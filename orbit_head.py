"""
orbit_head.py
ORBIT's own trained classifier: a small layer on top of the RoBERTa model.

Why it exists
  The pre-trained model reads "my heart is racing before the presentation" as
  joy (it learned "racing heart" from excited Reddit posts) and barely
  understands Hinglish. This layer learns from ORBIT's own labelled sentences
  to fix those blind spots.

What it is
  Softmax regression (multinomial logistic regression), written in NumPy so
  every step can be explained:
      scores  = features · W + b         (one score per emotion family)
      probs   = softmax(scores)          (turns scores into probabilities)
  Training finds W and b by gradient descent on cross-entropy loss with L2
  regularisation (a penalty that stops it memorising the training data).

Features (what the layer "sees")
  1. the base model's 28 emotion scores for the ORIGINAL text
  2. the 7 emotion-family totals
  3. hashed word and word-pair counts      -> learns phrases like "heart racing"
  4. hashed character 3-5-grams             -> learns spellings like bahut/bohot
  "Hashing" turns any word into one of 1024 numbered buckets with a fixed
  formula (CRC32), so the vocabulary never has to be stored.
"""
import json
import re
import zlib
from pathlib import Path

import numpy as np

from emotion_model import EMOTION_GROUPS, GROUP_OF

FAMILIES = list(EMOTION_GROUPS)
MODEL_DIR = Path(__file__).parent / "data" / "model"
SHARED_MODEL = MODEL_DIR / "orbit_head.npz"
CANDIDATES = {
    "C": MODEL_DIR / "orbit_head_C.npz",
    "D": MODEL_DIR / "orbit_head_D.npz",
    "T": MODEL_DIR / "orbit_head_T.npz",
}
LOCAL_PERSONAL_MODEL = MODEL_DIR / "orbit_head_personal.npz"


def personal_model():
    """Where the user's personal model lives. On Streamlit Cloud each browser
    session gets its own file, so one person's corrections never affect another."""
    import storage
    if storage.storage_mode() == "session":
        return storage.SESSION_DIR / f"{storage._session_id()}_personal.npz"
    return LOCAL_PERSONAL_MODEL
WORD_BUCKETS = 1024
CHAR_BUCKETS = 1024
TOKEN = re.compile(r"[^\s.,!?।\"'()]+")


def _bucket(prefix, piece, size):
    return zlib.crc32(f"{prefix}:{piece}".encode("utf-8")) % size


def text_features(text):
    """Hashed word/word-pair and character n-gram features (L2-normalised)."""
    lower = text.lower()
    words = TOKEN.findall(lower)
    word_vec = np.zeros(WORD_BUCKETS, dtype=np.float32)
    for piece in words + [f"{a} {b}" for a, b in zip(words, words[1:])]:
        word_vec[_bucket("w", piece, WORD_BUCKETS)] = 1.0
    char_vec = np.zeros(CHAR_BUCKETS, dtype=np.float32)
    padded = f" {' '.join(words)} "
    for n in (3, 4, 5):
        for i in range(len(padded) - n + 1):
            char_vec[_bucket("c", padded[i:i + n], CHAR_BUCKETS)] += 1.0
    for vec in (word_vec, char_vec):
        norm = np.linalg.norm(vec)
        if norm:
            vec /= norm
    return np.concatenate([word_vec, char_vec])


def _score_block(scores, labels):
    base = np.array([scores[label] for label in labels], dtype=np.float32)
    families = np.array([sum(scores[l] for l in EMOTION_GROUPS[f]) for f in FAMILIES], dtype=np.float32)
    return np.concatenate([base, families])


def features(text, base_scores, labels, dict_scores=None):
    """Full feature vector for one text.

    base_scores: {emotion: score} for the ORIGINAL text.
    dict_scores: {emotion: score} after the Hinglish dictionary translation.
                 Only given for variant D ("translation-assist").
    """
    parts = [_score_block(base_scores, labels)]
    if dict_scores is not None:
        parts.append(_score_block(dict_scores, labels))
    parts.append(text_features(text))
    return np.concatenate(parts)


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def train(X, y, sample_weight=None, l2=1e-3, steps=800, lr=0.5, seed=0):
    """Fit W (features x families) and b with gradient descent (Adam updates)."""
    rng = np.random.default_rng(seed)
    n, d = X.shape
    k = len(FAMILIES)
    Y = np.eye(k, dtype=np.float32)[y]
    w = np.ones(n, dtype=np.float32) if sample_weight is None else sample_weight.astype(np.float32)
    w = w / w.mean()
    W = rng.normal(0, 0.01, (d, k)).astype(np.float32)
    b = np.zeros(k, dtype=np.float32)
    mW, vW, mb, vb = np.zeros_like(W), np.zeros_like(W), np.zeros_like(b), np.zeros_like(b)
    for step in range(1, steps + 1):
        P = softmax(X @ W + b)
        G = (P - Y) * w[:, None] / n
        gW = X.T @ G + l2 * W
        gb = G.sum(axis=0)
        for param, grad, m, v in ((W, gW, mW, vW), (b, gb, mb, vb)):
            m *= 0.9
            m += 0.1 * grad
            v *= 0.999
            v += 0.001 * grad * grad
            param -= lr * (m / (1 - 0.9 ** step)) / (np.sqrt(v / (1 - 0.999 ** step)) + 1e-8)
    return W, b


def predict_proba(X, W, b, temperature=1.0):
    """Family probabilities. temperature > 1 makes over-confident scores more honest
    (temperature scaling) without changing which family wins."""
    return softmax((X @ W + b) / temperature)


def fit_temperature(logits, y):
    """Find the temperature that best fits held-out (out-of-fold) predictions,
    by minimising log-loss (how surprised the model is by the right answers)."""
    def log_loss(t):
        p = softmax(logits / t)
        return -np.mean(np.log(p[np.arange(len(y)), y] + 1e-12))
    grid = np.exp(np.linspace(np.log(0.5), np.log(20), 200))
    losses = [log_loss(t) for t in grid]
    best = float(grid[int(np.argmin(losses))])
    return best, log_loss(1.0), log_loss(best)


def class_weights(y):
    """Give every family the same total weight, even if it has fewer examples."""
    counts = np.bincount(y, minlength=len(FAMILIES)).astype(np.float32)
    return (counts.sum() / (len(FAMILIES) * np.maximum(counts, 1)))[y]


def macro_f1(y_true, y_pred):
    scores = []
    for k in range(len(FAMILIES)):
        tp = np.sum((y_pred == k) & (y_true == k))
        fp = np.sum((y_pred == k) & (y_true != k))
        fn = np.sum((y_pred != k) & (y_true == k))
        if tp + fp + fn == 0:
            continue
        scores.append(2 * tp / (2 * tp + fp + fn))
    return float(np.mean(scores)) if scores else 0.0


def cross_validate(X, y, sample_weight, l2_values=(1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2), folds=5, seed=0):
    """Stratified k-fold cross-validation. Returns {l2: (mean macro-F1, mean accuracy)}."""
    rng = np.random.default_rng(seed)
    fold_of = np.zeros(len(y), dtype=int)
    for k in range(len(FAMILIES)):
        idx = np.where(y == k)[0]
        rng.shuffle(idx)
        fold_of[idx] = np.arange(len(idx)) % folds
    results = {}
    for l2 in l2_values:
        f1s, accs = [], []
        for f in range(folds):
            tr, te = fold_of != f, fold_of == f
            W, b = train(X[tr], y[tr], sample_weight[tr], l2=l2)
            pred = predict_proba(X[te], W, b).argmax(axis=1)
            f1s.append(macro_f1(y[te], pred))
            accs.append(float(np.mean(pred == y[te])))
        results[l2] = (float(np.mean(f1s)), float(np.mean(accs)))
    return results


def save(path, W, b, meta):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, W=W, b=b, meta=json.dumps(meta))


def load(path=None):
    """Load the personal model if the user retrained one, otherwise the shared one."""
    for candidate in ([path] if path else [personal_model(), SHARED_MODEL]):
        if candidate and Path(candidate).exists():
            data = np.load(candidate)
            return data["W"], data["b"], json.loads(str(data["meta"]))
    return None

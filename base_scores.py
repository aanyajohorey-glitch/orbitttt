"""
base_scores.py
A disk cache of the RoBERTa model's scores for ORBIT's labelled sentences.

Scoring one sentence takes about 0.1-0.3 seconds, so scoring every training
and test sentence again on each run would be slow. Scores are saved in
data/model/base_scores.json, keyed by the exact text. If a sentence changes,
it is simply scored again.

Two kinds of scores are stored:
  "raw"  - the model reading the text exactly as written
  "dict" - the model reading the text after the Hinglish dictionary translator
           (the v0.3 approach, kept as a baseline for comparison)
"""
import json
from pathlib import Path

from emotion_model import detect_emotions
from hinglish import to_english

MODEL_DIR = Path(__file__).parent / "data" / "model"
SHARED_CACHE = MODEL_DIR / "base_scores.json"        # ORBIT's own datasets (in the repo)
LOCAL_CACHE = MODEL_DIR / "base_scores_local.json"   # classmates' held-out sentences (never uploaded)


def _load(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def get(texts, kind="raw", private=False):
    """Return a list of {emotion: score} for each text (computing missing ones).

    private=True keeps the texts in the local-only cache (for held-out data).
    """
    path = LOCAL_CACHE if private else SHARED_CACHE
    cache = _load(path)
    changed = False
    out = []
    for text in texts:
        key = f"{kind}::{text}"
        if key not in cache:
            model_text = text if kind == "raw" else to_english(text)[0]
            cache[key] = dict(detect_emotions(model_text))
            changed = True
        out.append(cache[key])
    if changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    return out

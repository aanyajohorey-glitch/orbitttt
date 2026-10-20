"""
evaluation.py
Shared evaluation code: the same numbers appear in train_head.py, the AI Lab
and the tests.

Ways of choosing an emotion family that are compared:
  A  "RoBERTa only"              - the pre-trained model's strongest emotion
  B  "RoBERTa + dictionary"      - ORBIT v0.3: Hinglish words translated first
  C  "Classifier"                - trained layer, original text only
  D  "Classifier + dictionary"   - trained layer that ALSO sees the scores of
                                   the dictionary-translated text ("translation-assist")

Metrics (all standard in data science):
  accuracy  - share of sentences with the right family
  precision - when ORBIT says family X, how often is it right?
  recall    - of all sentences that really are X, how many did ORBIT find?
  F1        - balance of precision and recall (2PR / (P + R))
  macro-F1  - the average F1 over families, so small families count equally
"""
import numpy as np
import pandas as pd

import base_scores
import orbit_head
from emotion_model import GROUP_OF, load_model

FAMILIES = orbit_head.FAMILIES
VARIANTS = {
    "A": "RoBERTa only",
    "B": "RoBERTa + dictionary (v0.3)",
    "C": "Classifier",
    "D": "Classifier + dictionary",
}


def labels():
    return load_model()["labels"]


def top_family(scores):
    return GROUP_OF[max(scores, key=scores.get)]


def feature_matrix(texts, raw_scores, dict_scores=None):
    names = labels()
    if dict_scores is None:
        return np.stack([orbit_head.features(t, s, names) for t, s in zip(texts, raw_scores)])
    return np.stack([orbit_head.features(t, s, names, d) for t, s, d in zip(texts, raw_scores, dict_scores)])


def model_probs(model, texts, raw, translated):
    W, b, meta = model
    X = feature_matrix(texts, raw, translated if meta.get("uses_dictionary") else None)
    return orbit_head.predict_proba(X, W, b, meta.get("temperature", 1.0))


def predict(table, model=None, private=False):
    """Add predicted families (pred_A ... pred_D, pred_live) and confidence to a dataset table.

    model: the model used for "pred_live" (default: the adopted shared model).
    """
    table = table.copy()
    columns = [f"pred_{v}" for v in VARIANTS] + ["pred_live", "confidence"]
    if table.empty:
        for column in columns:
            table[column] = []
        return table
    texts = list(table["text"])
    raw = base_scores.get(texts, "raw", private)
    translated = base_scores.get(texts, "dict", private)
    table["pred_A"] = [top_family(s) for s in raw]
    table["pred_B"] = [top_family(s) for s in translated]
    for variant in ("C", "D"):
        candidate = orbit_head.load(orbit_head.CANDIDATES[variant])
        probs = model_probs(candidate, texts, raw, translated) if candidate else None
        table[f"pred_{variant}"] = [FAMILIES[i] for i in probs.argmax(axis=1)] if probs is not None \
            else table["pred_B"]
    live = model or orbit_head.load(orbit_head.SHARED_MODEL)
    if live:
        probs = model_probs(live, texts, raw, translated)
        table["pred_live"] = [FAMILIES[i] for i in probs.argmax(axis=1)]
        table["confidence"] = probs.max(axis=1)
    else:
        table["pred_live"], table["confidence"] = table["pred_B"], np.nan
    return table


def report(y_true, y_pred):
    """Accuracy, macro-F1 and a per-family table for one set of predictions."""
    y_true, y_pred = list(y_true), list(y_pred)
    rows = []
    for family in FAMILIES:
        tp = sum(t == family and p == family for t, p in zip(y_true, y_pred))
        fp = sum(t != family and p == family for t, p in zip(y_true, y_pred))
        fn = sum(t == family and p != family for t, p in zip(y_true, y_pred))
        support = tp + fn
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append({"Family": family, "Support": support, "Precision": round(precision, 2),
                     "Recall": round(recall, 2), "F1": round(f1, 2)})
    table = pd.DataFrame(rows)
    present = table[table["Support"] > 0]
    accuracy = float(np.mean([t == p for t, p in zip(y_true, y_pred)])) if y_true else 0.0
    return {"accuracy": accuracy, "macro_f1": float(present["F1"].mean()) if len(present) else 0.0,
            "per_family": table, "n": len(y_true)}


def family_f1(y_true, y_pred, family):
    table = report(y_true, y_pred)["per_family"]
    return float(table.loc[table["Family"] == family, "F1"].iloc[0])


def confusion(y_true, y_pred):
    grid = pd.crosstab(pd.Series(list(y_true), name="Correct"), pd.Series(list(y_pred), name="Predicted"))
    return grid.reindex(index=FAMILIES, columns=FAMILIES, fill_value=0)


def by_group(table, column, variant):
    """Accuracy and macro-F1 for each language or writing style."""
    rows = []
    for value, part in table.groupby(column):
        r = report(part["family"], part[f"pred_{variant}"])
        rows.append({column.capitalize(): value, "Sentences": len(part),
                     "Accuracy": round(r["accuracy"], 2), "Macro-F1": round(r["macro_f1"], 2)})
    return pd.DataFrame(rows)

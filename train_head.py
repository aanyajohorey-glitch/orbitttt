"""
train_head.py
Train ORBIT's classifier and print the evaluation.

Run from the project folder:
    python train_head.py

Steps
  1. Load data/train_augment.csv (training data ONLY).
  2. Get the RoBERTa scores for each sentence (cached in data/model/).
  3. Choose the regularisation strength with 5-fold cross-validation.
  4. Train on all training data and save data/model/orbit_head.npz.
  5. Evaluate A / B / C on the dev, body and held-out sets, and check the
     pre-registered adoption rule from docs/methodology.md.
"""
from datetime import date

import numpy as np

import base_scores
import datasets
import evaluation
import orbit_head

FAMILIES = orbit_head.FAMILIES


def training_arrays(extra=None):
    """Features, labels and sample weights for the training data (+ optional corrections)."""
    train = datasets.load("train")
    texts, fams = list(train["text"]), list(train["family"])
    raw = base_scores.get(texts, "raw")
    weights = [1.0] * len(texts)
    if extra:  # Teach Orbit corrections: (text, family, raw_scores)
        for text, family, scores in extra:
            texts.append(text)
            fams.append(family)
            raw.append(scores)
            weights.append(2.0)   # a person took the time to correct ORBIT
    X = evaluation.feature_matrix(texts, raw)
    y = np.array([FAMILIES.index(f) for f in fams])
    w = orbit_head.class_weights(y) * np.array(weights, dtype=np.float32)
    return X, y, w


def fit(extra=None, path=orbit_head.SHARED_MODEL, verbose=True):
    X, y, w = training_arrays(extra)
    cv = orbit_head.cross_validate(X, y, w)
    best_l2 = max(cv, key=lambda l2: cv[l2][0])
    if verbose:
        print("Cross-validation on training data (macro-F1, accuracy):")
        for l2, (f1, acc) in cv.items():
            print(f"  l2={l2:<7} macro-F1={f1:.3f} accuracy={acc:.3f}{'   <- chosen' if l2 == best_l2 else ''}")
    W, b = orbit_head.train(X, y, w, l2=best_l2)
    meta = {"l2": best_l2, "cv_macro_f1": cv[best_l2][0], "cv_accuracy": cv[best_l2][1],
            "train_sentences": int(len(y)), "corrections": len(extra or []),
            "trained_on": str(date.today()), "families": FAMILIES}
    orbit_head.save(path, W, b, meta)
    return W, b, meta


def main():
    W, b, meta = fit()
    print(f"\nSaved {orbit_head.SHARED_MODEL.name} (trained on {meta['train_sentences']} sentences)\n")
    results = {}
    for name in ["dev", "body", "heldout"]:
        table = evaluation.predict(datasets.load(name), (W, b, meta), private=(name == "heldout"))
        if table.empty:
            print(f"{name}: no sentences yet")
            continue
        print(f"{name} ({len(table)} sentences)")
        for v, label in evaluation.VARIANTS.items():
            r = evaluation.report(table["family"], table[f"pred_{v}"])
            results[(name, v)] = (r, table)
            print(f"  {v} {label:30} accuracy={r['accuracy']:.2f}  macro-F1={r['macro_f1']:.3f}")
    body = results[("body", "B")][1]
    fear_b = evaluation.family_f1(body["family"], body["pred_B"], "Fear")
    fear_c = evaluation.family_f1(body["family"], body["pred_C"], "Fear")
    dev_b = results[("dev", "B")][0]["macro_f1"]
    dev_c = results[("dev", "C")][0]["macro_f1"]
    adopt = (fear_c - fear_b >= 0.10) and (dev_b - dev_c <= 0.03)
    print(f"\nAdoption rule: body Fear F1 {fear_b:.2f} -> {fear_c:.2f} (need +0.10); "
          f"dev macro-F1 {dev_b:.3f} -> {dev_c:.3f} (max drop 0.03)")
    print("DECISION:", "ADOPT the ORBIT classifier" if adopt else "KEEP RoBERTa + dictionary")


if __name__ == "__main__":
    main()

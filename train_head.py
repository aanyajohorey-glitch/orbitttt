"""
train_head.py
Train ORBIT's classifier variants and apply the pre-registered adoption rules.

Run from the project folder:
    python train_head.py

Steps
  1. Load data/train_augment.csv (training data ONLY).
  2. Get the RoBERTa scores for each sentence (cached in data/model/).
  3. For variants C (no dictionary) and D (+ dictionary features): choose the
     regularisation strength with 5-fold cross-validation and train.
  4. Evaluate A / B / C / D on the dev and body sets, plus out-of-fold
     Hinglish/Hindi results on the training data.
  5. Apply rule 1 (C vs B) and rule 2 (D vs C) from docs/methodology.md and
     copy the adopted model to data/model/orbit_head.npz.
"""
import shutil
from datetime import date

import numpy as np

import base_scores
import datasets
import evaluation
import orbit_head

FAMILIES = orbit_head.FAMILIES


def training_arrays(extra=None, use_dictionary=False):
    """Features, labels and sample weights for the training data (+ optional corrections).

    extra: Teach Orbit corrections as (text, family, raw_scores, dict_scores).
    """
    train = datasets.load("train")
    texts, fams = list(train["text"]), list(train["family"])
    raw = base_scores.get(texts, "raw")
    translated = base_scores.get(texts, "dict")
    weights = [1.0] * len(texts)
    for text, family, raw_scores, dict_scores in extra or []:
        texts.append(text)
        fams.append(family)
        raw.append(raw_scores)
        translated.append(dict_scores)
        weights.append(2.0)   # a person took the time to correct ORBIT
    X = evaluation.feature_matrix(texts, raw, translated if use_dictionary else None)
    y = np.array([FAMILIES.index(f) for f in fams])
    w = orbit_head.class_weights(y) * np.array(weights, dtype=np.float32)
    return X, y, w


def folds_for(y, k=5, seed=0):
    rng = np.random.default_rng(seed)
    fold = np.zeros(len(y), dtype=int)
    for c in range(len(FAMILIES)):
        idx = np.where(y == c)[0]
        rng.shuffle(idx)
        fold[idx] = np.arange(len(idx)) % k
    return fold


def out_of_fold(use_dictionary, l2):
    """Predicted family for every training sentence, from a model that never saw it."""
    X, y, w = training_arrays(use_dictionary=use_dictionary)
    fold = folds_for(y)
    probs = np.zeros((len(y), len(FAMILIES)))
    for f in range(5):
        W, b = orbit_head.train(X[fold != f], y[fold != f], w[fold != f], l2=l2)
        probs[fold == f] = orbit_head.predict_proba(X[fold == f], W, b)
    return probs


def fit(use_dictionary, path, extra=None, verbose=True):
    X, y, w = training_arrays(extra, use_dictionary)
    cv = orbit_head.cross_validate(X, y, w)
    best_l2 = max(cv, key=lambda l2: cv[l2][0])
    if verbose:
        name = "D (+ dictionary)" if use_dictionary else "C (no dictionary)"
        print(f"Variant {name}: cross-validation on training data (macro-F1)")
        print("   " + "  ".join(f"l2={l2:g}: {f1:.3f}" for l2, (f1, _) in cv.items()) + f"   -> chose {best_l2:g}")
    W, b = orbit_head.train(X, y, w, l2=best_l2)
    meta = {"l2": best_l2, "cv_macro_f1": cv[best_l2][0], "cv_accuracy": cv[best_l2][1],
            "train_sentences": int(len(y)), "corrections": len(extra or []),
            "uses_dictionary": use_dictionary, "trained_on": str(date.today()), "families": FAMILIES}
    orbit_head.save(path, W, b, meta)
    return W, b, meta


def main():
    models = {"C": fit(False, orbit_head.CANDIDATES["C"]), "D": fit(True, orbit_head.CANDIDATES["D"])}
    print()
    tables = {name: evaluation.predict(datasets.load(name), models["C"]) for name in ("dev", "body")}
    for name, table in tables.items():
        print(f"{name} ({len(table)} sentences)")
        for v, label in evaluation.VARIANTS.items():
            r = evaluation.report(table["family"], table[f"pred_{v}"])
            print(f"  {v} {label:30} accuracy={r['accuracy']:.2f}  macro-F1={r['macro_f1']:.3f}")
        if name == "body":
            controls = table[table["family"] != "Fear"]
            print("  controls read correctly: " + "  ".join(
                f"{v}={np.mean(controls[f'pred_{v}'] == controls['family']):.0%}" for v in evaluation.VARIANTS))

    train = datasets.load("train")
    non_en = (train["language"] != "English").to_numpy()
    y = np.array([FAMILIES.index(f) for f in train["family"]])
    oof = {v: out_of_fold(v == "D", models[v][2]["l2"]).argmax(axis=1) for v in ("C", "D")}
    translated = base_scores.get(list(train["text"]), "dict")
    oof_b = np.array([FAMILIES.index(evaluation.top_family(s)) for s in translated])
    hinglish = {"B": orbit_head.macro_f1(y[non_en], oof_b[non_en]),
                "C": orbit_head.macro_f1(y[non_en], oof["C"][non_en]),
                "D": orbit_head.macro_f1(y[non_en], oof["D"][non_en])}
    print(f"\nOut-of-fold Hinglish/Hindi macro-F1 on training sentences ({non_en.sum()}): "
          + "  ".join(f"{k}={v:.3f}" for k, v in hinglish.items()))

    def f1(name, v, family=None):
        t = tables[name]
        return evaluation.family_f1(t["family"], t[f"pred_{v}"], family) if family else \
            evaluation.report(t["family"], t[f"pred_{v}"])["macro_f1"]

    rule1 = f1("body", "C", "Fear") - f1("body", "B", "Fear") >= 0.10 and f1("dev", "B") - f1("dev", "C") <= 0.03
    rule2 = (hinglish["D"] - hinglish["C"] >= 0.05 and f1("body", "C", "Fear") - f1("body", "D", "Fear") <= 0.03
             and f1("dev", "C") - f1("dev", "D") <= 0.03)
    print(f"Rule 1 (C replaces B): {'MET' if rule1 else 'not met'}  | Rule 2 (D replaces C): "
          f"{'MET' if rule2 else 'not met'}")
    adopted = ("D" if rule2 else "C") if rule1 else None
    if adopted:
        shutil.copyfile(orbit_head.CANDIDATES[adopted], orbit_head.SHARED_MODEL)
        print(f"ADOPTED variant {adopted} -> {orbit_head.SHARED_MODEL.name}")
    else:
        print("No classifier adopted: ORBIT keeps RoBERTa + dictionary")


if __name__ == "__main__":
    main()

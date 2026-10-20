"""The AI pipeline, the classifier and the evaluation code."""
import re

import numpy as np
import pytest

import analysis
import datasets
import evaluation
import orbit_head
from conftest import needs_model
from emotion_model import EMOTION_GROUPS


# ---------------------------------------------------------------- metrics (no model needed)
def test_report_metrics_on_a_small_example():
    truth = ["Joy", "Joy", "Fear", "Fear"]
    pred = ["Joy", "Fear", "Fear", "Fear"]
    r = evaluation.report(truth, pred)
    table = r["per_family"].set_index("Family")
    assert r["accuracy"] == 0.75
    assert table.loc["Joy", "Precision"] == 1.0 and table.loc["Joy", "Recall"] == 0.5
    assert table.loc["Fear", "Precision"] == 0.67 and table.loc["Fear", "Recall"] == 1.0
    assert evaluation.confusion(truth, pred).loc["Joy", "Fear"] == 1


def test_softmax_regression_learns_a_simple_pattern():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(140, 7)).astype(np.float32)
    y = X.argmax(axis=1)                       # the label is simply the biggest feature
    W, b = orbit_head.train(X, y, l2=1e-4)
    accuracy = np.mean(orbit_head.predict_proba(X, W, b).argmax(axis=1) == y)
    assert accuracy > 0.9


def test_hashing_is_stable_between_runs():
    a = orbit_head.text_features("my heart is racing")
    b = orbit_head.text_features("my heart is racing")
    assert np.array_equal(a, b) and abs(np.linalg.norm(a[:1024]) - 1) < 1e-5


def test_no_training_sentence_leaks_into_test_sets():
    words = lambda s: set(re.findall(r"[^\s.,!?।]+", s.lower()))
    train = list(datasets.load("train")["text"])
    for name in ("dev", "body"):
        for test_text in datasets.load(name)["text"]:
            assert test_text not in train
            for train_text in train:
                a, b = words(test_text), words(train_text)
                assert len(a & b) / len(a | b) < 0.5, (test_text, train_text)


def test_writing_style_tags():
    assert datasets.writing_style("My hands are shaking before the exam") == "Body-based"
    assert datasets.writing_style("ugh") == "Very short"
    assert datasets.writing_style("lol that was the funniest thing today") == "Informal / slang"


# ---------------------------------------------------------------- the live pipeline (needs the model)
@needs_model
def test_documented_failure_is_fixed():
    """v0.3 read this as joy. The trained classifier should read it as fear."""
    result = analysis.interpret("My heart is racing before the presentation.")
    assert result["final"]["family"] == "Fear"


@needs_model
def test_result_has_confidence_and_a_world_in_the_same_family():
    result = analysis.interpret("I miss my grandmother so much.")
    final = result["final"]
    assert 0.0 <= final["confidence"] <= 1.0
    assert final["unsure"] == (final["confidence"] < analysis.UNSURE_BELOW)
    assert final["emotion"] in EMOTION_GROUPS[final["family"]]
    assert len(final["alternatives"]) == 3


@needs_model
def test_hinglish_anger_is_understood():
    assert analysis.interpret("yaar mujhe bahut gussa aa raha hai")["final"]["family"] == "Anger"


@needs_model
def test_live_model_beats_v03_on_body_feelings():
    body = evaluation.predict(datasets.load("body"))
    assert evaluation.family_f1(body["family"], body["pred_live"], "Fear") > \
        evaluation.family_f1(body["family"], body["pred_B"], "Fear")


@needs_model
def test_crisis_text_is_flagged_by_the_pipeline():
    assert analysis.interpret("I don't want to be alive anymore")["safety"] == "crisis"

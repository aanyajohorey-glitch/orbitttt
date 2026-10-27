"""Safety: the deterministic crisis check and the 'never store crisis text' rule."""
import pandas as pd
import pytest

import datasets
import safety

SUITE = pd.read_csv(datasets.DATA / "safety_tests.csv", encoding="utf-8")
KNOWN_MISSES = {"I've thought about how I would do it"}
HELPLINE_NUMBERS = ["14416", "1-800-891-4416", "112"]


@pytest.mark.parametrize("text", SUITE[(SUITE.expected == "crisis") & ~SUITE.text.isin(KNOWN_MISSES)].text)
def test_crisis_sentences_are_flagged(text):
    assert safety.check(text) == "crisis"


@pytest.mark.parametrize("text", SUITE[SUITE.expected == "concern"].text)
def test_concern_sentences_get_help(text):
    assert safety.check(text) in ("concern", "crisis")


@pytest.mark.parametrize("text", SUITE[SUITE.expected == "none"].text)
def test_harmless_sentences_are_not_flagged(text):
    assert safety.check(text) is None


def test_known_misses_are_still_documented():
    """If a known miss starts being caught, update the docs instead of hiding it."""
    for text in KNOWN_MISSES:
        assert text in set(SUITE.text)
        assert safety.check(text) != "crisis", "update KNOWN_MISSES and docs/safety_report.md"


@pytest.mark.parametrize("name", ["dev", "train", "body"])
def test_everyday_sentences_never_trigger_crisis(name):
    for text in datasets.load(name)["text"]:
        assert safety.check(text) != "crisis", text


def test_crisis_card_always_shows_all_helplines():
    card = safety.safety_card_html("crisis")
    for number in HELPLINE_NUMBERS:
        assert number in card
    assert "not been saved" in card

"""The Hinglish/Hindi dictionary translator (kept as a baseline and as extra evidence for variant D)."""
import pytest

import hinglish


@pytest.mark.parametrize("text", ["I'm so happy today", "main road is closed", "The meeting is at 3 pm."])
def test_english_is_left_alone(text):
    assert hinglish.to_english(text) == (text, False)


@pytest.mark.parametrize("text, must_contain", [
    ("yaar mujhe bahut gussa aa raha hai", "angry"),
    ("mujhe exam se bahut darr lag raha hai", "scared"),
    ("dadi ki bahut yaad aa rahi hai", "miss"),
    ("aaj mood bahut kharab hai yaar", "bad"),
])
def test_hinglish_is_translated(text, must_contain):
    english, translated = hinglish.to_english(text)
    assert translated and must_contain in english


def test_hindi_words_are_not_split_apart():
    english, translated = hinglish.to_english("मैं आज बहुत खुश हूँ")
    assert translated
    assert english == "i today very happy am"


def test_detection_needs_two_hinglish_markers():
    assert not hinglish.looks_hinglish("I love my main character")
    assert hinglish.looks_hinglish("mujhe bahut accha laga")

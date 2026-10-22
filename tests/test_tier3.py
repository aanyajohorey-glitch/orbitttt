"""Tier 3: the emotion constellation, the world theme and the stress-buster game rules."""
import re

import pytest
import streamlit as st

import constellation
import games
import storage
import theme


def result_for(emotion, confidence=0.9, safety=None, unsure=False, world="Blue Hour Tide"):
    return {"text": f"test {emotion}", "safety": safety, "world": world,
            "emotions": [(emotion, 0.8), ("neutral", 0.1)],
            "final": {"emotion": emotion, "confidence": confidence, "unsure": unsure, "family": "Sadness"}}


# ---------------------------------------------------------------- constellation
def test_constellation_is_the_same_for_the_same_check_in():
    emotions = [("joy", 0.6), ("relief", 0.3), ("neutral", 0.1)]
    assert constellation.constellation_svg(emotions, "a") == constellation.constellation_svg(emotions, "a")
    assert constellation.constellation_svg(emotions, "a") != constellation.constellation_svg(emotions, "b")


def test_stronger_emotions_make_bigger_stars():
    stars = constellation.stars_for([("joy", 0.7), ("relief", 0.2), ("neutral", 0.05)], "x")
    by_label = {s["label"]: s for s in stars}
    assert by_label["joy"]["strength"] == 1.0 > by_label["relief"]["strength"] > by_label["neutral"]["strength"]


def test_constellation_has_between_3_and_9_stars():
    many = [(label, 0.5) for label in ["joy", "love", "fear", "anger", "pride", "relief", "grief",
                                         "caring", "remorse", "surprise", "neutral"]]
    assert len(constellation.stars_for(many)) == constellation.MAX_STARS
    assert len(constellation.stars_for([("joy", 0.99), ("love", 0.001), ("fear", 0.001)])) == 3


def test_constellation_is_an_image_with_escaped_labels():
    html = constellation.constellation_html([("joy", 0.8), ("neutral", 0.2), ("love", 0.1)], "t")
    assert html.startswith('<img class="cst-img" src="data:image/svg+xml;base64,')
    assert "<svg" not in html          # st.html would strip inline SVG


# ---------------------------------------------------------------- world theme
def test_theme_follows_the_detected_world_but_not_a_crisis(session):
    theme.set_world(result_for("sadness"))
    assert st.session_state.world_theme == "Blue Hour Tide"
    theme.set_world(result_for("sadness", safety="crisis"))
    assert st.session_state.world_theme is None          # back to ORBIT's calm colours


def test_theme_css_uses_the_world_palette_and_skips_high_contrast(session):
    theme.set_world(result_for("sadness"))
    css = theme.theme_css({})
    assert "rgba(185, 200, 234" in css                   # #B9C8EA, Blue Hour Tide's first colour
    assert not re.search(r"<[/\w]", css)                 # tag-like text would break st.html
    assert theme.theme_css({"high_contrast": True}) == ""


# ---------------------------------------------------------------- game rules
@pytest.fixture
def fresh(session, monkeypatch):
    monkeypatch.setattr("nudges.low_mood_count", lambda days=7: 0)
    st.session_state.game_offered = False
    return session


@pytest.mark.parametrize("emotion", sorted(games.DISTRESS))
def test_confident_distress_may_get_a_game(fresh, emotion):
    assert games.offer_reason(result_for(emotion)) is None


@pytest.mark.parametrize("emotion", ["joy", "love", "neutral", "curiosity", "gratitude", "grief"])
def test_happy_neutral_and_grief_never_get_a_game(fresh, emotion):
    assert games.offer_reason(result_for(emotion)) == "not distress"


def test_crisis_and_concern_never_get_a_game(fresh):
    assert games.offer_reason(result_for("sadness", safety="crisis")) == "crisis"
    assert games.offer_reason(result_for("sadness", safety="concern")) == "intense"


def test_unsure_asks_first(fresh):
    assert games.offer_reason(result_for("fear", unsure=True)) == "unsure"


def test_repeated_low_mood_suggests_a_person_instead(fresh, monkeypatch):
    monkeypatch.setattr("nudges.low_mood_count", lambda days=7: games.REPEATED_LOW_MOODS)
    assert games.offer_reason(result_for("sadness")) == "repeated low mood"


def test_only_once_per_session_and_opt_out_is_remembered(fresh):
    st.session_state.game_offered = True
    assert games.offer_reason(result_for("anger")) == "already offered"
    st.session_state.game_offered = False
    games._never()
    assert storage.get_setting("games_opt_out") == "1"
    assert games.offer_reason(result_for("anger")) == "opted out"


def test_every_distress_emotion_has_matching_games():
    for emotion in games.DISTRESS:
        assert games.FOR_EMOTION[emotion]
        assert all(key in games.GAMES for key in games.FOR_EMOTION[emotion])


@pytest.mark.parametrize("key", list(games.GAMES))
def test_every_game_builds_with_its_colours(key):
    html = games.game_html(key, ["#C9B9E8", "#B9C8EA", "#EBCBD7"], "#A895D2", reduced=True)
    assert "const PALETTE" in html and "REDUCED = true" in html
    assert "<canvas" in html or "<svg" in html
    assert "fetch(" not in html and "XMLHttpRequest" not in html   # games never send anything anywhere

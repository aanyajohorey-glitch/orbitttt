"""Reach Out Helper, Mood Studio palettes and music discovery."""
import itertools
from pathlib import Path
from statistics import mean

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import music
import palette
import reach_out
import storage

APP = str(Path(__file__).resolve().parents[1] / "app.py")
CRISIS = {"text": "x", "safety": "crisis", "world": None, "emotions": [("sadness", 0.9)],
          "final": {"emotion": "sadness", "family": "Sadness", "confidence": 0.9, "unsure": False}}


# ---------------------------------------------------------------- crisis bypasses all three features
@pytest.fixture
def app():
    storage.delete_everything()
    storage.set_setting("onboarded", "1")
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    return at


def bodies(at):
    return [h.proto.body for h in at.get("html")]


@pytest.mark.parametrize("page", ["Reach Out", "Mood Studio"])
def test_a_crisis_check_in_shows_only_the_safety_response(app, page):
    app.session_state.home_result = CRISIS
    app.session_state.page = page
    app.run()
    assert not app.exception
    assert any("14416" in b for b in bodies(app))
    assert not app.text_area and not app.slider and not app.get("download_button")


def test_crisis_words_in_a_vibe_show_only_the_safety_response(app):
    app.session_state.page = "Mood Studio"
    app.run()
    app.text_input(key="studio_vibe").input("i want to end my life").run()
    assert any("14416" in b for b in bodies(app))
    assert not app.slider and not any("mb-hero" in b and "<style" not in b for b in bodies(app))


def test_crisis_words_in_reach_out_context_draft_nothing_and_save_nothing(app):
    app.session_state.page = "Reach Out"
    app.run()
    app.radio(key="ro_level").set_value("more").run()
    app.text_input(key="ro_context").input("i want to end my life").run()
    assert any("14416" in b for b in bodies(app)) and not app.text_area
    assert storage.list_notes() == []


def test_music_page_is_blocked_in_a_crisis_too(app):
    app.session_state.home_result = CRISIS
    app.session_state.page = "Mood Studio"
    app.session_state.studio_part = "Music discovery"
    app.run()
    assert not any("track-num" in b and "<style" not in b for b in bodies(app))   # CSS mentions the class too


def test_no_reach_out_offer_in_a_crisis(session):
    reach_out.offer_card(CRISIS)          # draws nothing (no exception, no button)


# ---------------------------------------------------------------- Reach Out drafts
@pytest.mark.parametrize("language,who,level",
                         list(itertools.product(reach_out.LANGUAGES, reach_out.WHO, reach_out.LEVELS)))
def test_three_complete_drafts_for_every_choice(language, who, level):
    drafts = reach_out.drafts(who, level, "Fear", language, "")
    assert len(drafts) == 3
    assert all("{" not in d and len(d) < 240 for d in drafts)


def test_language_matches_the_user():
    assert reach_out.detect_language("मुझे डर लग रहा है") == "Hindi"
    assert reach_out.detect_language("yaar mujhe bahut gussa aa raha hai") == "Hinglish"
    assert reach_out.detect_language("I feel low today") == "English"


# ---------------------------------------------------------------- palettes
GRID = [i / 2 for i in range(-2, 3)]


@pytest.mark.parametrize("valence,arousal", list(itertools.product(GRID, GRID)))
@pytest.mark.parametrize("slider", [-1.0, 0.0, 1.0])
def test_palette_always_has_5_valid_colours_and_readable_text(valence, arousal, slider):
    for tweaks in ({}, {"muted": 0.5}, {"contrast": 3.0, "playful": True}, {"warmth": -1.0}):
        result = palette.make_palette(valence, arousal, warm=slider, energy=slider, bold=slider, vintage=slider,
                                      tweaks=tweaks)
        colours = {c["role"]: c["hex"] for c in result["colours"]}
        assert len(colours) == 5 and all(palette.is_valid_hex(h) for h in colours.values())
        assert palette.contrast(colours["Ink (text)"], colours["Background"]) >= 4.5     # WCAG AA, normal text
        assert palette.contrast(colours["Ink (text)"], colours["Primary"]) >= 3.0        # WCAG AA, large text


def test_harmony_rule_follows_energy():
    assert palette.make_palette(0.5, -0.8)["rule"] == "analogous"
    assert palette.make_palette(0.5, 0.0)["rule"] == "complementary"
    assert palette.make_palette(0.5, 0.9)["rule"] == "triadic"


def test_feelings_get_different_colour_families():
    joy = palette.make_palette(*palette.blend_va([("joy", 1.0)]))["hue"]
    sad = palette.make_palette(*palette.blend_va([("sadness", 1.0)]))["hue"]
    assert joy < 60 and 200 < sad < 260          # warm gold/coral vs cool blue


def test_refine_buttons_change_the_palette_without_new_input():
    base = palette.make_palette(0.3, 0.2)
    for action in ("muted", "warmer", "cooler", "contrast", "playful"):
        changed = palette.make_palette(0.3, 0.2, tweaks=palette.refine({}, action))
        assert changed["colours"] != base["colours"], action


def test_vibe_keywords_are_understood():
    *_, found = palette.vibe_profile("rainy Sunday cafe, nostalgic")
    assert found == ["rainy", "sunday", "cafe", "nostalgic"]


def test_exports_are_well_formed():
    import json
    result = palette.make_palette(0.2, 0.3)
    fonts = palette.font_pair(0, 0, 0.3)
    assert json.loads(palette.as_json(result, fonts))["palette"][0]["hex"].startswith("#")
    assert palette.css_variables(result).startswith(":root {")
    assert palette.png_board(result, fonts, ["calm"])[:8] == b"\x89PNG\r\n\x1a\n"


# ---------------------------------------------------------------- music
SAD, ANGRY = [("sadness", 0.9)], [("anger", 0.9)]


@pytest.mark.parametrize("emotions", [SAD, ANGRY, [("joy", 0.9)], [("neutral", 1.0)]])
@pytest.mark.parametrize("discovery", [0.0, 0.5, 1.0])
def test_playlists_are_diverse(emotions, discovery):
    playlist = music.recommend(emotions, "match", discovery)
    spread = music.diversity(playlist)
    assert 8 <= len(playlist) <= 12
    assert spread["artists"] == len(playlist)              # never the same artist twice
    assert spread["languages"] >= 3 and spread["genres"] >= 5


def test_gently_lift_me_is_brighter_than_match_my_mood():
    match = music.recommend(SAD, "match", 0.5)
    lift = music.recommend(SAD, "lift", 0.5)
    assert mean(t["valence"] for t in lift) > mean(t["valence"] for t in match) + 0.8


def test_lifting_anger_calms_the_energy():
    match = music.recommend(ANGRY, "match", 0.5)
    lift = music.recommend(ANGRY, "lift", 0.5)
    assert mean(t["energy"] for t in lift) < mean(t["energy"] for t in match)


def test_explore_goes_beyond_the_mainstream():
    comfort = music.diversity(music.recommend(SAD, "match", 0.0))
    explore = music.diversity(music.recommend(SAD, "match", 1.0))
    assert explore["avg_mainstream"] < comfort["avg_mainstream"]
    assert explore["languages"] >= comfort["languages"]


def test_catalogue_is_complete_and_has_no_lyrics():
    table = music.load_catalog()
    assert 150 <= len(table) <= 300
    assert list(table.columns[:8]) == ["title", "artist", "language", "genre", "energy", "valence",
                                       "mainstream_level", "tags"]
    assert table[["energy", "valence", "mainstream_level"]].isin([1, 2, 3, 4, 5]).all().all()
    assert "lyrics" not in table.columns
    assert table["language"].nunique() >= 10            # not only global pop


def test_links_are_search_pages_only():
    spotify, youtube = music.links({"title": "Kasoor", "artist": "Prateek Kuhad"})
    assert spotify.startswith("https://open.spotify.com/search/")
    assert youtube.startswith("https://www.youtube.com/results?search_query=")

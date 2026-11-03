"""Pattern Insights, the bridges between modes, and the vibe theme."""
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest
import streamlit as st

import bridge
import patterns
import styles
import theme
import vibe

APP = str(Path(__file__).resolve().parents[1] / "app.py")
NOW = datetime(2026, 10, 25, 20, 0)


def table(moods, start_days_ago):
    """A small fake journal: one check-in a day, newest last."""
    rows = []
    for i, mood in enumerate(moods):
        when = NOW - timedelta(days=start_days_ago - i)
        rows.append({"when": when, "date": when.date(), "weekday": patterns.WEEKDAYS[when.weekday()],
                     "mood": mood, "family": "Sadness" if mood < 0 else "Joy", "demo": 0})
    return pd.DataFrame(rows)


def test_not_enough_data_for_sparse_periods():
    sparse = table([0.5, -0.5], start_days_ago=3)
    assert not patterns.enough_data(sparse, 7)
    assert patterns.enough_data(table([0.1] * 5, 6), 7)


def test_days_are_classified_with_the_rule_of_thumb_thresholds():
    days = patterns.daily(table([0.6, 0.0, -0.6], 3))
    assert list(days["kind"]) == ["bright", "in-between", "low"]


def test_no_suggestions_when_low_days_are_rare():
    assert patterns.low_pattern(patterns.daily(table([0.5, 0.4, -0.5, 0.6, 0.3], 5)), NOW) == 0


def test_frequent_low_days_give_layers_1_and_2():
    assert patterns.low_pattern(patterns.daily(table([-0.5, -0.4, -0.6, 0.2, 0.1], 5)), NOW) == 2


def test_low_days_lasting_two_weeks_add_the_trusted_adult_layer():
    moods = [-0.5, 0.1, -0.6, 0.2, -0.4, 0.1, 0.0, -0.5, 0.2, -0.6, 0.1, -0.4, 0.0, -0.3]
    assert patterns.low_pattern(patterns.daily(table(moods, 13)), NOW) == 3


def test_low_moods_cluster_by_weekday_and_part_of_day():
    weekdays, parts = patterns.low_clusters(table([-0.5, 0.5, -0.6], 3))
    assert weekdays and parts[0][0] == "Evening"


@pytest.mark.parametrize("text,block", [
    ("I'm stuck and have no idea what to make", "No direction"),
    ("it has to be perfect", "Perfectionism"),
    ("what will people think of it", "Fear of judgment"),
    ("so tired and burnt out", "Burnout"),
    ("everyone else is better than me", "Comparison"),
])
def test_creative_blocks_are_recognised(text, block):
    assert bridge.offer_for(text)["block"] == block


def test_stress_without_a_block_offers_a_breather():
    assert bridge.offer_for("deadline tomorrow and I'm stressed") == {"block": None, "stressed": True,
                                                                        "game": "mandala"}


@pytest.mark.parametrize("text", ["a poster about rain", "I lost my cat in the story", "a perfectly ordinary day"])
def test_ordinary_ideas_get_no_offer(text):
    assert bridge.offer_for(text) is None


def test_feeling_to_create_uses_the_emotion_blend():
    result = {"emotions": [("sadness", 0.8), ("neutral", 0.1)], "model_text": "I miss home and the rain",
              "text": "I miss home and the rain"}
    vector = bridge.feeling_to_vector(result)
    assert vector["valence"] < 0 and "rain" in vector["themes"]
    assert "miss home" not in vector["text"]


def test_break_keeps_the_project(session):
    from create_ui import end_break, take_break
    st.session_state.creative = {"universe": {"concept": {"title": "Kept"}}}
    take_break("exercise", block="Burnout")
    end_break()
    assert st.session_state.creative["universe"]["concept"]["title"] == "Kept"
    assert st.session_state.create_break is None


def test_the_app_theme_follows_the_vibe_vector(session):
    import creative
    universe = creative.universe(vibe.build("a neon city at midnight", [("excitement", 0.7)]))
    theme.set_vibe_world(universe)
    world = theme.active_world()
    assert world["palette"][0] == universe["palette"]["colours"][0]["hex"]
    assert theme._rgba(world["palette"][0], 0.42) in theme.theme_css({})


def test_night_css_is_safe_for_streamlit():
    assert not re.search(r"<[/\w]", styles.NIGHT_CSS)
    assert "#15131D" in styles.accessibility_css({"night_mode": True})

"""
world_data.py
All the sample content ORBIT uses: aesthetic worlds, creative intents
and vending-machine constraints.

The worlds are stored in data/worlds.csv and loaded with pandas. The
emotion model's results are matched to these worlds by match_world().
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FOLDER = Path(__file__).parent / "data"

INTENTS = ["Explore", "Digital Art", "Poster", "Presentation", "Scrapbook"]


@st.cache_data
def load_worlds():
    """Read data/worlds.csv and return a list of worlds (one dict per row).

    @st.cache_data means the file is only read once, not on every click.
    """
    table = pd.read_csv(DATA_FOLDER / "worlds.csv")
    worlds = []
    for row in table.to_dict("records"):
        row["palette"] = row["palette"].split("|")
        row["elements"] = row["elements"].split("|")
        row["emotions"] = row["emotions"].split("|")
        row["ring"] = row["ring"] == "yes"
        worlds.append(row)
    return worlds


def get_world(name):
    """Find a world by its name. Returns None if it doesn't exist."""
    for world in load_worlds():
        if world["name"] == name:
            return world
    return None


def prompt_for(world, intent):
    """Return the world's creative prompt for an intent, e.g. 'Poster'."""
    column = "prompt_" + intent.lower().replace(" ", "_")
    return world[column]


def match_world(emotion_scores, family=None):
    """Recommend a world from the emotion model's scores.

    Each world in worlds.csv lists the emotions it belongs to. A world's
    match score is the total of the model's scores for those emotions,
    and the world with the highest total wins.

    emotion_scores: list of (emotion, score) pairs from detect_emotions().
    family (optional): ORBIT's final emotion family. Only worlds that include
        an emotion from that family are considered.
    Returns: (best world, its match score, the emotions that matched).
    """
    from emotion_model import EMOTION_GROUPS

    scores = dict(emotion_scores)
    worlds = load_worlds()
    if family:
        allowed = set(EMOTION_GROUPS[family])
        worlds = [w for w in worlds if allowed & set(w["emotions"])] or worlds
    best_world, best_total = None, -1.0
    for world in worlds:
        total = sum(scores.get(emotion, 0.0) for emotion in world["emotions"])
        if total > best_total:
            best_world, best_total = world, total

    matched = sorted(best_world["emotions"], key=lambda emotion: scores.get(emotion, 0.0), reverse=True)
    if family:
        in_family = [e for e in matched if e in EMOTION_GROUPS[family]]
        matched = in_family + [e for e in matched if e not in in_family]
    matched = [emotion for emotion in matched if scores.get(emotion, 0.0) >= 0.05] or matched[:1]
    return best_world, best_total, matched


CONSTRAINTS = [
    "Use only three colours from the palette.",
    "Leave at least half of the space empty.",
    "Include one handwritten element.",
    "Finish a first draft in twenty minutes.",
    "Use one texture you can find at home.",
    "Keep all of the text in lowercase.",
]



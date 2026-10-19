"""
world_data.py
All the sample content ORBIT uses: aesthetic worlds, creative intents,
Soundspace vibes and vending-machine constraints.

The worlds are stored in data/worlds.csv and loaded with pandas. The
emotion model's results are matched to these worlds by match_world().
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FOLDER = Path(__file__).parent / "data"

# The creative intents a user can pick on the Home page.
INTENTS = ["Explore", "Digital Art", "Poster", "Presentation", "Scrapbook"]


@st.cache_data
def load_worlds():
    """Read data/worlds.csv and return a list of worlds (one dict per row).

    @st.cache_data means the file is only read once, not on every click.
    """
    table = pd.read_csv(DATA_FOLDER / "worlds.csv")
    worlds = []
    for row in table.to_dict("records"):
        # Some columns hold several values separated by "|".
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


def match_world(emotion_scores):
    """Recommend a world from the emotion model's scores.

    Each world in worlds.csv lists the emotions it belongs to. A world's
    match score is the total of the model's scores for those emotions,
    and the world with the highest total wins.

    emotion_scores: list of (emotion, score) pairs from detect_emotions().
    Returns: (best world, its match score, the emotions that matched).
    """
    scores = dict(emotion_scores)
    best_world, best_total = None, -1.0
    for world in load_worlds():
        total = sum(scores.get(emotion, 0.0) for emotion in world["emotions"])
        if total > best_total:
            best_world, best_total = world, total

    # The emotions that contributed most, for explaining the match.
    matched = sorted(best_world["emotions"], key=lambda emotion: scores.get(emotion, 0.0), reverse=True)
    matched = [emotion for emotion in matched if scores.get(emotion, 0.0) >= 0.05] or matched[:1]
    return best_world, best_total, matched


# ---------------------------------------------------------------
# Aesthetic Vending Machine
# ---------------------------------------------------------------
# A small creative challenge added to every pack.
CONSTRAINTS = [
    "Use only three colours from the palette.",
    "Leave at least half of the space empty.",
    "Include one handwritten element.",
    "Finish a first draft in twenty minutes.",
    "Use one texture you can find at home.",
    "Keep all of the text in lowercase.",
]

# ---------------------------------------------------------------
# Soundspace
# ---------------------------------------------------------------
SOUND_MOODS = ["Calm", "Reflective", "Hopeful", "Nostalgic", "Focused", "Restless"]

SOUNDSPACES = [
    {
        "name": "Dream Pop Haze",
        "genres": "Dream pop · Shoegaze",
        "moods": ["Calm", "Reflective"],
        "tempo": "Slow to mid",
        "best_for": "Drawing, daydreaming",
        "pairs_with": "Lavender Haze",
        "colour": "#C9B9E8",
    },
    {
        "name": "Neo-classical Rain",
        "genres": "Modern piano · Strings",
        "moods": ["Reflective", "Calm"],
        "tempo": "Slow",
        "best_for": "Journaling, reading",
        "pairs_with": "Blue Hour Tide",
        "colour": "#B9C8EA",
    },
    {
        "name": "Indie Folk Morning",
        "genres": "Indie folk · Acoustic",
        "moods": ["Hopeful", "Calm"],
        "tempo": "Mid",
        "best_for": "Morning routines, sketching outside",
        "pairs_with": "Sage Morning",
        "colour": "#C7D3C0",
    },
    {
        "name": "City Pop Sunset",
        "genres": "City pop · Vintage soul",
        "moods": ["Nostalgic", "Hopeful"],
        "tempo": "Mid to upbeat",
        "best_for": "Scrapbooking, editing photos",
        "pairs_with": "Blush Static",
        "colour": "#EBCBD7",
    },
    {
        "name": "Late-night Jazz",
        "genres": "Jazz · Lo-fi hip hop",
        "moods": ["Focused", "Calm"],
        "tempo": "Slow to mid",
        "best_for": "Studying, writing",
        "pairs_with": "Midnight Library",
        "colour": "#8E85A3",
    },
    {
        "name": "Cinematic Electronica",
        "genres": "Ambient electronica · Film score",
        "moods": ["Restless", "Focused"],
        "tempo": "Building",
        "best_for": "Bold artwork, working through big feelings",
        "pairs_with": "Velvet Thunder",
        "colour": "#9C88BC",
    },
    {
        "name": "Soft Ambient",
        "genres": "Ambient · Drone",
        "moods": ["Calm", "Reflective", "Nostalgic"],
        "tempo": "Very slow",
        "best_for": "Winding down, resting",
        "pairs_with": "Paper Moon",
        "colour": "#C9C2B6",
    },
]

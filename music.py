"""
music.py
Mood Studio: music discovery from ORBIT's own small, hand-labelled catalogue
(data/music_catalog.csv). No Spotify API, no scraping, no lyrics.

The method
1. Target vector. The feeling's (valence, arousal) from palette.EMOTION_VA
   becomes a target mood (1-5) and energy (1-5). The intent changes it:
     "match my mood"  -> the target IS the feeling (it can feel validating)
     "gently lift me" -> a small step towards brighter and steadier, not a jump
                         to party music (the "iso principle" used in music therapy:
                         meet the mood first, then move it gently).
   Each feeling + intent also has a few preferred tags (e.g. comfort, hopeful).
2. Every track is a vector too: [1, mood, energy, tags...]. Cosine similarity
   between the target and each track = relevance (1 = same direction).
3. Discovery dial (0 = comfort zone, 1 = explore): comfort slightly prefers
   well-known tracks, explore prefers lesser-known ones.
4. Diversity re-ranking with Maximal Marginal Relevance (MMR): pick tracks one
   at a time, each time balancing "relevant" against "too similar to what's
   already picked" (same artist, same genre, same language). The more you
   explore, the more diversity counts. One track per artist at most.
"""
from pathlib import Path
from urllib.parse import quote, quote_plus

import pandas as pd
import streamlit as st

from emotion_model import GROUP_OF
from palette import EMOTION_VA
from ranking import cosine, discovery_trade_off, mmr

CATALOG = Path(__file__).parent / "data" / "music_catalog.csv"
PLAYLIST_SIZE = 10
TAG_WEIGHT = 0.6

INTENT_TAGS = {
    "Sadness": {"match": ["bittersweet", "longing", "cathartic", "acoustic", "calm"],
                "lift": ["comfort", "hopeful", "warm", "calm"]},
    "Fear": {"match": ["cathartic", "night", "longing", "dreamy"],
             "lift": ["calm", "comfort", "instrumental", "hopeful"]},
    "Anger": {"match": ["release", "energetic", "cathartic", "empowering"],
              "lift": ["calm", "chill", "comfort", "hopeful"]},
    "Joy": {"match": ["uplifting", "celebration", "dance", "playful"],
            "lift": ["uplifting", "celebration", "energetic", "playful"]},
    "Warmth": {"match": ["love", "warm", "friendship", "comfort"],
               "lift": ["love", "warm", "uplifting", "friendship"]},
    "Wonder": {"match": ["dreamy", "journey", "story", "playful"],
               "lift": ["hopeful", "journey", "uplifting", "dreamy"]},
    "Neutral": {"match": ["chill", "calm", "focus"],
                "lift": ["uplifting", "hopeful", "warm"]},
}
LOW_FAMILIES = {"Sadness", "Fear", "Anger"}
ENERGY_WORDS = {1: "very calm", 2: "gentle", 3: "steady", 4: "upbeat", 5: "high-energy"}
MOOD_WORDS = {1: "heavy-hearted", 2: "bittersweet", 3: "in-between", 4: "warm", 5: "bright"}


@st.cache_data
def load_catalog():
    table = pd.read_csv(CATALOG)
    table["tag_list"] = table["tags"].str.split("|")
    return table


def all_tags(table):
    return sorted({tag for tags in table["tag_list"] for tag in tags})


def target_for(emotions, intent):
    """emotions: [(label, score), ...]. Returns (mood 1-5, energy 1-5, family, preferred tags)."""
    total = sum(score for _, score in emotions) or 1.0
    valence = sum(EMOTION_VA[label][0] * score for label, score in emotions) / total
    arousal = sum(EMOTION_VA[label][1] * score for label, score in emotions) / total
    family = GROUP_OF[max(emotions, key=lambda pair: pair[1])[0]]
    mood, energy = 3 + 2 * valence, 3 + 2 * arousal
    if intent == "lift":
        mood = min(5.0, mood + (1.5 if valence < 0 else 0.5))
        energy = energy + 0.4 * (3.2 - energy)
    return mood, energy, family, INTENT_TAGS[family][intent]


def vector(mood, energy, tags, vocabulary):
    """[1, mood, energy, one weight per tag]. Mood and energy are centred (-1 to +1)."""
    return [1.0, (mood - 3) / 2, (energy - 3) / 2] + [TAG_WEIGHT if t in tags else 0.0 for t in vocabulary]


def track_similarity(a, b):
    """How alike two tracks are, for diversity: same artist / genre / language."""
    return 0.45 * (a["artist"] == b["artist"]) + 0.3 * (a["genre"] == b["genre"]) + \
        0.25 * (a["language"] == b["language"])


def recommend(emotions, intent="match", discovery=0.5, size=PLAYLIST_SIZE, table=None):
    """The playlist for a feeling: a list of dicts (track details, relevance, reason)."""
    mood, energy, family, tags = target_for(emotions, intent)
    playlist = recommend_target(mood, energy, tags, intent, discovery, size, table)
    for track in playlist:
        track["family"] = family
    return playlist


def recommend_target(mood, energy, tags, intent="match", discovery=0.5, size=PLAYLIST_SIZE, table=None):
    """The same method from a ready-made target (Creator Mode uses its Vibe Vector)."""
    table = load_catalog() if table is None else table
    vocabulary = all_tags(table)
    goal = vector(mood, energy, tags, vocabulary)
    candidates = []
    for track in table.to_dict("records"):
        similarity = cosine(goal, vector(track["valence"], track["energy"], track["tag_list"], vocabulary))
        popularity = (track["mainstream_level"] - 1) / 4
        relevance = similarity + 0.15 * (1 - 2 * discovery) * popularity
        candidates.append({**track, "similarity": similarity, "relevance": relevance})
    candidates.sort(key=lambda t: -t["relevance"])
    pool = candidates[:60]
    chosen = mmr(pool, track_similarity, size, discovery_trade_off(discovery), unique="artist")
    for track in chosen:
        track["reason"] = reason(track, intent, tags, chosen)
    return chosen


def reason(track, intent, tags, playlist):
    """A one-line, honest 'why this'."""
    shared = [t for t in track["tag_list"] if t in tags]
    feel = f"{ENERGY_WORDS[int(track['energy'])]} and {MOOD_WORDS[int(track['valence'])]}"
    start = {"match": "Matches how you feel", "lift": "A gentle step up"}.get(intent, "Fits your project's vibe")
    text = f"{start}: {feel}"
    if shared:
        text += f" ({', '.join(shared[:2])})"
    if track["mainstream_level"] <= 2:
        text += ". A lesser-known find"
    elif track["language"] not in ("English", "Hindi", "Instrumental"):
        text += f". Something in {track['language']}"
    return text + "."


def diversity(playlist):
    """Simple numbers for the AI Lab and tests."""
    return {"artists": len({t["artist"] for t in playlist}), "genres": len({t["genre"] for t in playlist}),
            "languages": len({t["language"] for t in playlist}),
            "avg_mainstream": round(sum(t["mainstream_level"] for t in playlist) / max(1, len(playlist)), 2)}


def links(track):
    """Search links only: ORBIT makes no API calls."""
    query = f"{track['title']} {track['artist']}"
    return (f"https://open.spotify.com/search/{quote(query)}",
            f"https://www.youtube.com/results?search_query={quote_plus(query)}")

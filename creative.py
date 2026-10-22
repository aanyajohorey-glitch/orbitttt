"""
creative.py
Creator Mode: one Vibe Vector (vibe.py) -> a whole CREATIVE UNIVERSE:

    concept     a title and a one-paragraph vision (template grammar; optional AI polish)
    palette     5 colours, harmony rule and WCAG checks          (palette.py)
    fonts       a heading + body pairing                         (fonts.py, data/fonts.csv)
    moodboard   texture, lighting and keyword tiles               (generated, no images)
    aesthetics  3 matching art movements                          (data/aesthetics.csv)
    music       8 tracks                                          (music.py, data/music_catalog.csv)
    creators    6 creators and artists to look up                 (data/creators.csv)

Ranking (aesthetics, creators, music): cosine similarity between the vector and
each item's numbers, plus shared tags, then Maximal Marginal Relevance for
variety (ranking.py). The DISCOVERY dial moves from familiar to unfamiliar.
Everything is deterministic: the same vector always gives the same universe.
"""
import copy
import hashlib
import random
from pathlib import Path

import pandas as pd
import streamlit as st

import fonts
import music
import palette
import vibe
from ranking import cosine, discovery_trade_off, mmr, overlap

DATA = Path(__file__).parent / "data"
ELEMENTS = ["concept", "palette", "fonts", "moodboard", "aesthetics", "music", "creators"]
LABELS = {"concept": "Concept", "palette": "Palette", "fonts": "Typography", "moodboard": "Moodboard",
          "aesthetics": "Aesthetics", "music": "Music", "creators": "Creators to discover"}
DIMENSIONS = ["mood", "energy", "light", "warmth", "era", "texture"]


@st.cache_data
def load_aesthetics():
    table = pd.read_csv(DATA / "aesthetics.csv")
    table["tag_list"] = table["tags"].str.split("|")
    table["cue_list"] = table["cues"].str.split(";")
    return table


@st.cache_data
def load_creators():
    table = pd.read_csv(DATA / "creators.csv").fillna({"language": ""})
    table["tag_list"] = table["tags"].str.split("|")
    return table


def _seed(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode("utf-8")).hexdigest()[:8], 16)


def closest_dimensions(target, item, count=2):
    """The dimensions where an item is closest to the vector, for 'why this fits'."""
    gaps = sorted(range(len(target)), key=lambda i: abs(target[i] - item[i]))
    return [DIMENSIONS[i] for i in gaps[:count]]


# ---------------------------------------------------------------
# Aesthetics and creators
# ---------------------------------------------------------------
def rank_aesthetics(vector, discovery=0.5, size=3):
    target = vibe.numbers(vector)
    rows = []
    for row in load_aesthetics().to_dict("records"):
        item = [row["valence"], row["arousal"], row["brightness"] * 2 - 1, row["warmth"], row["era"], row["texture"]]
        relevance = 0.75 * cosine([1] + target, [1] + item) + 0.25 * overlap(vector["themes"], row["tag_list"])
        rows.append({**row, "relevance": relevance, "close": closest_dimensions(target, item)})

    def similar(a, b):
        return 0.5 * (a["origin"] == b["origin"]) + 0.5 * bool(set(a["tag_list"]) & set(b["tag_list"]))
    chosen = mmr(sorted(rows, key=lambda r: -r["relevance"])[:25], similar, size, discovery_trade_off(discovery))
    for row in chosen:
        row["why"] = (f"Close to your vibe on {' and '.join(row['close'])}. Look for: "
                      f"{', '.join(row['cue_list'][:3])}.")
    return chosen


def rank_creators(vector, discovery=0.5, size=6):
    target = [vector["valence"], vector["arousal"], vector["warmth"], vector["era"], vector["texture"]]
    themes = set(vector["themes"])
    rows = []
    for row in load_creators().to_dict("records"):
        item = [row["valence"], row["arousal"], row["warmth"], row["era"], row["texture"]]
        popularity = (row["mainstream_level"] - 1) / 4
        relevance = (0.7 * cosine([1] + target, [1] + item) + 0.3 * overlap(themes, row["tag_list"])
                     + 0.15 * (1 - 2 * discovery) * popularity)
        shared = [t for t in row["tag_list"] if t in themes]
        rows.append({**row, "relevance": relevance, "shared": shared,
                     "close": closest_dimensions(target, item)})

    def similar(a, b):
        return (0.4 * (a["field"] == b["field"]) + 0.3 * (("India" in a["region"]) == ("India" in b["region"]))
                + 0.3 * (a["language"] == b["language"] and a["language"] != ""))
    pool = sorted(rows, key=lambda r: -r["relevance"])[:40]
    chosen = mmr(pool, similar, size, discovery_trade_off(discovery), unique="name")
    if not any("India" in c["region"] for c in chosen):            # always include someone from India
        indian = next((r for r in pool if "India" in r["region"]), None)
        if indian:
            chosen[-1] = indian
    for row in chosen:
        reason = (f"shares your {' and '.join(row['shared'][:2])} themes" if row["shared"]
                  else f"close to your vibe on {' and '.join(row['close'])}")
        rarity = " A lesser-known name worth finding." if row["mainstream_level"] <= 2 else ""
        row["why"] = f"Known for {row['known_for']}. Why it fits: {reason}.{rarity}"
    return chosen


# ---------------------------------------------------------------
# Moodboard tiles
# ---------------------------------------------------------------
LIGHTING = [  # (min brightness, warm?) -> lighting idea
    ((0.3, True), "golden-hour sunlight"), ((0.3, False), "clear daylight"),
    ((-0.3, True), "soft lamp light"), ((-0.3, False), "overcast window light"),
    ((-1.1, True), "candlelight and warm shadows"), ((-1.1, False), "moonlight and neon"),
]


def lighting(vector):
    if vector["era"] > 0.5 and vector["brightness"] < 0.2:
        return "neon glow and screen light"
    warm = vector["warmth"] >= 0
    for (low, is_warm), name in LIGHTING:
        if vector["brightness"] >= low and is_warm == warm:
            return name
    return "soft light"


def moodboard(vector, aesthetics):
    textures = palette.textures(vector["arousal"], -vector["era"])
    cues = [cue for a in aesthetics[:2] for cue in a["cue_list"][:2]]
    keywords = list(dict.fromkeys(vector["themes"][:4] + cues))
    return {"textures": textures, "lighting": lighting(vector), "keywords": keywords[:8]}


# ---------------------------------------------------------------
# Concept: title + vision (template grammar)
# ---------------------------------------------------------------
MEDIUM_PHRASE = {"Film": "a short film", "Book": "a book", "Brand": "a brand", "Poster": "a poster series",
                 "Music video": "a music video", "App": "an app", None: "a creative project"}
NOUNS = {"rain": "Rain", "monsoon": "Monsoon", "city": "City", "night": "Night", "love": "Hearts", "home": "Home",
         "family": "Family", "journey": "Road", "travel": "Road", "school": "Corridors", "exams": "Exam Season",
         "space": "Orbit", "ocean": "Tide", "sea": "Tide", "forest": "Forest", "garden": "Garden",
         "desert": "Dunes", "mountain": "Peaks", "festival": "Festival", "food": "Kitchen", "tea": "Chai",
         "chai": "Chai", "coffee": "Coffee", "music": "Rhythm", "dance": "Dance", "memory": "Memory",
         "dream": "Dreams", "dreams": "Dreams", "childhood": "Summer Holidays", "time": "Clocks", "train": "Trains",
         "books": "Pages", "library": "Pages", "cinema": "Reels", "film": "Reels", "moon": "Moon", "stars": "Stars",
         "cafe": "Cafe", "sunset": "Sunset", "beach": "Shore", "village": "Village", "kitchen": "Kitchen",
         "grandmother": "Nani's House", "freedom": "Open Skies", "hope": "Small Lights", "friendship": "Friends",
         "loneliness": "Empty Rooms", "magic": "Small Magic", "myth": "Old Gods", "folk": "Folk Songs",
         "rainy": "Rain", "sunday": "Sundays", "mumbai": "Mumbai", "delhi": "Delhi", "kerala": "Backwaters",
         "rajasthan": "Desert Winds", "wedding": "Wedding Lights", "streets": "Streets", "cat": "Cats",
         "letters": "Letters", "animals": "Wild Things", "nature": "Wild Places", "nostalgic": "Old Photographs"}
MEDIUM_WORDS = {"film", "cinema", "book", "books", "poster", "app", "music", "brand"}


def mood_adjective(vector):
    v, a, b = vector["valence"], vector["arousal"], vector["brightness"]
    if b < -0.4:
        return "Midnight"
    if vector["era"] < -0.5:
        return "Old-world"
    if vector["era"] > 0.6:
        return "Neon"
    if v >= 0.2:
        return "Bright" if a > 0.2 else "Gentle"
    if v <= -0.2:
        return "Restless" if a > 0.2 else "Quiet"
    return "Soft"


def concept(vector, colours, aesthetics, fonts_used):
    rng = random.Random(_seed(vector["text"], vector.get("direction", "")))
    content = [t for t in vector["themes"] if t in NOUNS and t not in MEDIUM_WORDS]
    noun = NOUNS[content[0]] if content else next((NOUNS[t] for t in vector["themes"] if t in NOUNS), None) or \
        rng.choice(["Small Hours", "Weather", "Signals", "Lanterns", "Echoes"])
    adjective = mood_adjective(vector)
    colour_word = colours[0]["name"].split()[-1]
    patterns = [f"{noun} in {colour_word}", f"Notes from {noun}"]
    if "'" not in noun:
        patterns.append(f"{adjective} {noun}")
    if "'" not in noun:                       # these only read well with simple nouns
        patterns += [f"After the {noun}"] + ([f"The {noun} Hour"] if " " not in noun else [])
    title = rng.choice(patterns)
    words = vibe.describe(vector)
    medium = MEDIUM_PHRASE.get(vector.get("medium"), "a creative project")
    idea = vector["text"].strip().rstrip(".")
    names_medium = any(w in MEDIUM_WORDS | {"story", "video", "song", "series", "comic", "zine", "game", "poems",
                                            "poem", "novel", "album", "logo", "website"}
                       for w in vibe.words_in(idea)[:5])
    if idea and len(idea) <= 140 and names_medium:
        opening = idea[0].upper() + idea[1:]                       # the idea already says what it is
    elif idea and len(idea) <= 140:
        opening = f"{medium[0].upper() + medium[1:]} about {idea[0].lower() + idea[1:]}"
    else:
        opening = f"{medium[0].upper() + medium[1:]} built from your idea"
    audience = f" Made for {vector['audience'].lower()}." if vector.get("audience") else ""
    vision = (f"{opening}. It feels {words['Mood (valence)']} and "
              f"{words['Energy (arousal)']}, lit by {lighting(vector)}, with {words['Texture']} textures and a "
              f"{words['Era']} edge. Its colours move from {colours[0]['name'].lower()} to "
              f"{colours[1]['name'].lower()}, the type pairs {fonts_used['heading']} with {fonts_used['body']}, and "
              f"it borrows from {aesthetics[0]['name']} and {aesthetics[1]['name'] if len(aesthetics) > 1 else ''}."
              f"{audience}").replace(" and .", ".")
    return {"title": title, "vision": vision, "polished": False}


def polish(concept_result, vector):
    """Optional: ask the AI (cloud/local, if set up) to polish the vision. The template stays as fallback."""
    import llm
    if llm.active_mode() == "templates":
        return concept_result
    system = ("You polish short creative briefs for a student creativity app. Rewrite the vision paragraph in "
              "3-4 vivid, simple sentences, keeping every fact (medium, colours, fonts, references). Do not add "
              "people's names, do not mention mental health, and return only the paragraph.")
    better = llm.generate(system, concept_result["vision"])
    if better:
        return {**concept_result, "vision": better, "polished": True}
    return concept_result


# ---------------------------------------------------------------
# Music: vibe words -> the catalogue's tags
# ---------------------------------------------------------------
THEME_TO_MUSIC = {"rain": "rain", "rainy": "rain", "monsoon": "rain", "night": "night", "midnight": "night",
                  "nostalgic": "nostalgic", "nostalgia": "nostalgic", "cafe": "chill", "coffee": "chill",
                  "chai": "warm", "tea": "calm", "love": "love", "romantic": "love", "friendship": "friendship",
                  "journey": "journey", "travel": "journey", "dream": "dreamy", "dreams": "dreamy",
                  "dreamy": "dreamy", "festival": "celebration", "wedding": "celebration", "dance": "dance",
                  "party": "dance", "folk": "folk", "home": "comfort", "family": "warm", "hope": "hopeful",
                  "summer": "summer", "morning": "morning", "space": "dreamy", "study": "focus", "exams": "focus",
                  "nature": "nature", "forest": "nature", "ocean": "calm", "sea": "calm", "hand-made": "acoustic",
                  "memory": "nostalgic", "childhood": "nostalgic", "poetry": "poetry", "loneliness": "longing"}


def music_tags(vector):
    """Tags from the vibe's words, plus a few from its numbers (era, energy, texture)."""
    tags = [THEME_TO_MUSIC[t] for t in vector["themes"] if t in THEME_TO_MUSIC]
    if vector["era"] < -0.3:
        tags.append("nostalgic")
    if vector["arousal"] < -0.2:
        tags.append("calm")
    elif vector["arousal"] > 0.4:
        tags.append("energetic")
    if vector["texture"] > 0.3:
        tags.append("acoustic")
    if len(tags) < 2 and vector["emotions"]:
        family = music.GROUP_OF[vector["emotions"][0][0]]
        tags += music.INTENT_TAGS[family]["match"]
    return list(dict.fromkeys(tags))[:5]


# ---------------------------------------------------------------
# The whole universe
# ---------------------------------------------------------------
def universe(vector, discovery=None, locks=(), previous=None):
    """Generate every element from the vector. Locked elements keep their previous version."""
    discovery = vector.get("discovery", 0.5) if discovery is None else discovery
    previous = previous or {}
    out = {}

    def keep(name):
        return name in locks and name in previous

    hindi = any("ऀ" <= ch <= "ॿ" for ch in vector["text"])
    out["palette"] = previous["palette"] if keep("palette") else palette.make_palette(
        vector["valence"], vector["arousal"], warm=vector["warmth"], bold=vector["bold"], vintage=-vector["era"],
        tweaks=vector.get("tweaks"), harmony=vector.get("harmony"), brightness=vector["brightness"])
    out["fonts"] = previous["fonts"] if keep("fonts") else fonts.pair(
        -vector["era"], vector["bold"], vector["arousal"], vector["warmth"], hindi=hindi)
    out["aesthetics"] = previous["aesthetics"] if keep("aesthetics") else rank_aesthetics(vector, discovery)
    out["moodboard"] = previous["moodboard"] if keep("moodboard") else moodboard(vector, out["aesthetics"])
    out["music"] = previous["music"] if keep("music") else music.recommend_target(
        3 + 2 * vector["valence"], 3 + 2 * vector["arousal"], music_tags(vector),
        intent="project", discovery=discovery, size=8)
    out["creators"] = previous["creators"] if keep("creators") else rank_creators(vector, discovery)
    out["concept"] = previous["concept"] if keep("concept") else concept(
        vector, out["palette"]["colours"], out["aesthetics"], out["fonts"])
    out["vector"] = copy.deepcopy(vector)
    out["discovery"] = discovery
    return out

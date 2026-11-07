"""
creative_match.py
The ORBIT Creative Feature Matching Algorithm.

It reads a creative idea (for example "Dark Romance"), finds the creative
STYLES it describes in data/creative_profiles.csv, and gives every resource
(aesthetic, font, song, creator) an IDEA MATCH score from 0 to 1. Create Mode
then mixes that score with its existing score:

    final score = 60% idea match + 40% existing score

Step 1  Find keywords.  Whole phrases first ("dark romance" = 3 points), then
        single words (2 points), then related words (1 point). A word used in a
        phrase is used up, so "dark" in "dark romance" does not also count alone.
Step 2  Match styles.   Each style adds up its points. Strength = points divided
        by the best style's points. Styles with strength 0.5 or more are kept
        (at most two), so "Dreamy Nostalgia" blends Dreamy and Nostalgia.
Step 3  Score resources. For each kept style:
            +1.0  the style names this aesthetic
            +0.6  x (the item's tags shared with the style / all the item's tags)
            +0.4  the song's genre is one the style lists
            -0.5  the item has a tag the style avoids
        The result is kept between -0.5 and 1, and styles are weighted by strength.
Step 4  Recommend.      Create Mode sorts by the final score and explains why.
"""
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

PROFILES = Path(__file__).parent / "data" / "creative_profiles.csv"
POINTS = {"phrase": 3, "word": 2, "related": 1}
KEEP_STRENGTH = 0.5
MAX_STYLES = 2
IDEA_WEIGHT = 0.6
NAME_POINTS = 1.0
TAG_POINTS = 0.6
GENRE_POINTS = 0.4
AVOID_POINTS = -0.5
FIT_THRESHOLD = 0.3
LIST_FIELDS = ["phrases", "words", "related", "atmosphere", "colours", "aesthetics", "tags", "font_tags",
               "music_tags", "music_genres", "avoid", "harmony", "anchors", "patterns", "image_queries",
               "image_avoid", "lastfm_tags"]
TEXT_FIELDS = ["genre", "emotion", "typography", "music_character"]
NUMBER_FIELDS = ["hue", "saturation", "lightness", "mood", "energy", "light", "warmth", "era", "texture", "bold"]


@lru_cache(maxsize=1)
def load_profiles():
    """The style table as a dict: name -> {field: list or number or None}."""
    table = pd.read_csv(PROFILES, keep_default_na=False)
    styles = {}
    for row in table.to_dict("records"):
        style = {"name": row["name"]}
        for field in LIST_FIELDS:
            style[field] = [part.strip() for part in str(row[field]).split("|") if part.strip()]
        for field in TEXT_FIELDS:
            style[field] = str(row.get(field, "")).strip()
        style["anchors"] = [(part.split(":")[0].strip(), part.split(":")[1].strip().upper())
                            for part in style["anchors"] if ":" in part]
        for field in NUMBER_FIELDS:
            style[field] = float(row[field]) if str(row[field]).strip() != "" else None
        styles[row["name"]] = style
    return styles


def words_of(text):
    return re.findall(r"[a-z0-9][a-z0-9'\-]*", (text or "").lower().replace("’", "'"))


def _same(word, keyword):
    """A word matches a keyword exactly, or as a simple plural (dreams = dream)."""
    return word == keyword or (word.endswith("s") and word[:-1] == keyword)


def find_keywords(text):
    """Step 1. Returns [(keyword found, style name, kind, points)], phrases first."""
    words = words_of(text)
    used = [False] * len(words)
    found = []
    styles = load_profiles()
    phrases = sorted(((p, name) for name, s in styles.items() for p in s["phrases"]),
                     key=lambda item: -len(item[0].split()))
    for phrase, name in phrases:
        parts = phrase.split()
        for start in range(len(words) - len(parts) + 1):
            window = range(start, start + len(parts))
            if not any(used[i] for i in window) and all(_same(words[i], parts[k]) for k, i in enumerate(window)):
                for i in window:
                    used[i] = True
                found.append((phrase, name, "phrase", POINTS["phrase"]))
    for i, word in enumerate(words):
        if used[i]:
            continue
        for kind in ("words", "related"):
            hits = [name for name, s in styles.items() if any(_same(word, k) for k in s[kind])]
            if hits:
                for name in hits:
                    found.append((word, name, "word" if kind == "words" else "related",
                                  POINTS["word" if kind == "words" else "related"]))
                used[i] = True
                break
    return found


def match(text):
    """Steps 1 and 2. None if the idea names no known style, else
    {"styles": [{"name", "points", "strength"}], "keywords": [...]} (strongest first)."""
    keywords = find_keywords(text)
    if not keywords:
        return None
    points = {}
    for _, name, _, value in keywords:
        points[name] = points.get(name, 0) + value
    best = max(points.values())
    order = {name: i for i, (_, name, _, _) in reversed(list(enumerate(keywords)))}
    ranked = sorted(points, key=lambda name: (-points[name], order[name]))
    kept = [name for name in ranked if points[name] / best >= KEEP_STRENGTH][:MAX_STYLES]
    return {"styles": [{"name": name, "points": points[name], "strength": round(points[name] / best, 2)}
                       for name in kept],
            "keywords": [k for k in keywords if k[1] in kept]}


def styles_in(result):
    """The kept styles with their full rows and strengths."""
    if not result:
        return []
    table = load_profiles()
    return [(table[s["name"]], s["strength"]) for s in result["styles"] if s["name"] in table]


def blended(result, field):
    """A number field averaged over the kept styles by strength (None if no style sets it)."""
    pairs = [(style[field], strength) for style, strength in styles_in(result) if style[field] is not None]
    if not pairs:
        return None
    return sum(value * strength for value, strength in pairs) / sum(strength for _, strength in pairs)


def first_value(result, field):
    """A number from the strongest style that sets it (used for the colour hue)."""
    for style, _ in styles_in(result):
        if style[field] is not None:
            return style[field]
    return None


def merged(result, field, limit=None):
    """A list field from every kept style, strongest style first, without repeats."""
    values = list(dict.fromkeys(v for style, _ in styles_in(result) for v in style[field]))
    return values[:limit] if limit else values


TAG_FIELD = {"aesthetic": "tags", "creator": "tags", "font": "font_tags", "music": "music_tags"}


def item_score(result, kind, name=None, tags=(), genre=None):
    """Step 3. (idea match from -0.5 to 1, reasons) for one resource.
    kind: "aesthetic", "creator", "font" or "music"."""
    styles = styles_in(result)
    if not styles:
        return 0.0, []
    tags = [t for t in tags if t]
    total, weights, reasons = 0.0, 0.0, []
    for style, strength in styles:
        score = 0.0
        if kind == "aesthetic" and name in style["aesthetics"]:
            score += NAME_POINTS
            reasons.append(f"a {style['name']} aesthetic")
        shared = [t for t in tags if t in style[TAG_FIELD[kind]] or (kind in ("aesthetic", "creator")
                                                                     and t in style["atmosphere"])]
        if shared and tags:
            score += TAG_POINTS * len(shared) / len(tags)
            reasons += shared
        if kind == "music" and genre and genre in style["music_genres"]:
            score += GENRE_POINTS
            reasons.append(genre.lower())
        if any(t in style["avoid"] for t in tags):
            score += AVOID_POINTS
        total += strength * max(AVOID_POINTS, min(1.0, score))
        weights += strength
    return round(total / weights, 3), list(dict.fromkeys(reasons))


def fitting_first(rows, size, score_key="idea"):
    """When the idea names a style, only rows that clearly fit it (idea match 0.3 or more) compete,
    so the variety rule picks among good matches. If too few fit, every row competes as before."""
    fitting = [r for r in rows if r.get(score_key, 0) >= FIT_THRESHOLD]
    return fitting if len(fitting) >= size else rows


def final_score(existing, idea):
    """60% idea match + 40% the existing score."""
    return IDEA_WEIGHT * idea + (1 - IDEA_WEIGHT) * existing


def summary(result):
    """One plain sentence for the screen, e.g. 'Dark Romance (found "dark romance", 3 points): mysterious, ...'."""
    if not result:
        return ""
    parts = []
    for style, strength in styles_in(result):
        found = [f'"{k}"' for k, name, _, _ in result["keywords"] if name == style["name"]]
        points = next(s["points"] for s in result["styles"] if s["name"] == style["name"])
        parts.append(f"{style['name']} (found {', '.join(found)}, {points} points): "
                     f"{', '.join(style['atmosphere'])}; colours {', '.join(style['colours'][:3])}")
    return " + ".join(parts)


def brief(found):
    """ORBIT's Creative Brief: the matched styles turned into a structured description, used by every
    later step (palette, patterns, image searches, music tags, fonts). None when no style was found."""
    styles = styles_in(found)
    if not styles:
        return None
    def text(field):
        return "; ".join(dict.fromkeys(style[field] for style, _ in styles if style[field]))
    return {
        "styles": [style["name"] for style, _ in styles],
        "genre": text("genre"),
        "aesthetic": ", ".join(merged(found, "aesthetics", limit=4)),
        "atmosphere": ", ".join(merged(found, "atmosphere", limit=5)),
        "emotion": text("emotion"),
        "colours": [name for name, _ in anchors(found)],
        "patterns": merged(found, "patterns", limit=4),
        "typography": text("typography"),
        "music": text("music_character"),
        "image_queries": merged(found, "image_queries", limit=4),
        "avoid": merged(found, "image_avoid") + merged(found, "avoid"),
        "lastfm_tags": merged(found, "lastfm_tags", limit=3),
    }


def anchors(found):
    """The colour anchors (name, hex). One style: its own list. Two styles: taken in turns
    (first style, second style, first, second, ...) so both are visible in the palette."""
    lists = [style["anchors"] for style, _ in styles_in(found)]
    order = []
    for i in range(max((len(a) for a in lists), default=0)):
        for colours in lists:
            if i < len(colours):
                order.append(colours[i])
    seen, result = set(), []
    for name, hex_ in order:
        if hex_ not in seen:
            seen.add(hex_)
            result.append((name, hex_))
    return result


def image_keywords(found):
    """Words an image's title or tags should contain to count as on-brief."""
    words = []
    for field in ("image_queries", "atmosphere", "tags", "colours", "patterns"):
        for phrase in merged(found, field):
            words += [w for w in words_of(phrase) if len(w) > 3]
    return list(dict.fromkeys(words))

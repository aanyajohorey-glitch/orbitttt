"""
vibe.py
Creator Mode: the VIBE VECTOR, one set of numbers that describes a creative
idea. Every output (concept, palette, fonts, moodboard, aesthetics, music,
creators) is generated from this same vector, so the results fit together.

    emotions    the emotion blend from ORBIT's emotion model (28 emotions)
    valence     -1 dark/sad ... +1 joyful          (from the emotions + vibe words)
    arousal     -1 calm ... +1 energetic           (from the emotions + vibe words)
    brightness  -1 dark/night ... +1 bright/sunny
    warmth      -1 cool ... +1 warm
    era         -1 ancient/vintage ... +1 futuristic
    texture     -1 smooth/glossy ... +1 rough/hand-made
    bold        -1 soft ... +1 bold
    themes      the words ORBIT understood (e.g. rain, cafe, nostalgic)

Words come from small, readable tables, so each number can be explained.
"""
import copy
import re

from palette import EMOTION_VA, VIBE_WORDS

# Extra word tables (each value nudges one number).
ERA_WORDS = {"ancient": -1.0, "myth": -0.9, "mythology": -0.9, "mughal": -0.9, "medieval": -0.9, "victorian": -0.8,
             "vintage": -0.7, "old": -0.5, "retro": -0.4, "70s": -0.5, "80s": -0.3, "90s": -0.2, "y2k": 0.0,
             "classic": -0.5, "folk": -0.6, "traditional": -0.7, "heritage": -0.7, "nostalgic": -0.5, "today": 0.2,
             "modern": 0.5, "minimal": 0.4, "digital": 0.6, "tech": 0.7, "future": 1.0, "futuristic": 1.0,
             "space": 0.8, "cyber": 0.9, "robot": 0.9, "ai": 0.8, "neon": 0.6, "sci-fi": 1.0}
BRIGHT_WORDS = {"night": -0.7, "midnight": -0.8, "dark": -0.8, "shadow": -0.6, "moody": -0.5, "storm": -0.5,
                "fog": -0.3, "rain": -0.3, "rainy": -0.3, "moon": -0.4, "stars": -0.5, "neon": -0.3, "noir": -0.9,
                "bright": 0.8, "sunny": 0.8, "sun": 0.7, "summer": 0.7, "beach": 0.6, "morning": 0.6,
                "sunrise": 0.6, "pastel": 0.6, "white": 0.6, "light": 0.5, "golden": 0.4, "festival": 0.6,
                "holi": 0.9}
TEXTURE_WORDS = {"grain": 0.7, "grainy": 0.7, "film": 0.5, "paper": 0.6, "handmade": 0.8, "hand-made": 0.8,
                 "rough": 0.8, "raw": 0.8, "zine": 0.8, "collage": 0.7, "clay": 0.8, "craft": 0.7, "folk": 0.5,
                 "rustic": 0.7, "grunge": 0.9, "wood": 0.5, "embroidery": 0.7, "glossy": -0.8, "chrome": -0.9,
                 "glass": -0.6, "clean": -0.7, "minimal": -0.7, "sleek": -0.8, "smooth": -0.7, "digital": -0.4,
                 "corporate": -0.8, "neon": -0.3}
# Everyday words that still carry a feel (only the numbers they clearly suggest).
FEEL_WORDS = {
    "grandmother": {"warmth": 0.7, "era": -0.6, "texture": 0.5}, "nani": {"warmth": 0.7, "era": -0.6, "texture": 0.5},
    "dadi": {"warmth": 0.7, "era": -0.6, "texture": 0.5}, "kitchen": {"warmth": 0.6, "texture": 0.4},
    "home": {"warmth": 0.6, "texture": 0.3}, "family": {"warmth": 0.6}, "village": {"warmth": 0.4, "era": -0.5, "texture": 0.6},
    "poems": {"era": -0.3, "texture": 0.3}, "poem": {"era": -0.3, "texture": 0.3}, "poetry": {"era": -0.3, "texture": 0.3},
    "letters": {"era": -0.5, "texture": 0.5, "warmth": 0.3}, "memory": {"era": -0.4}, "childhood": {"era": -0.4, "warmth": 0.4},
    "school": {"brightness": 0.3}, "exams": {"brightness": 0.0}, "candle": {"brightness": -0.4, "warmth": 0.7},
    "bubble": {"brightness": 0.5, "texture": -0.5}, "shop": {}, "wedding": {"warmth": 0.8, "brightness": 0.4},
}

# Words that are themes on their own (shown as tiles and used to match aesthetics and creators).
THEME_WORDS = {"rain", "monsoon", "city", "night", "love", "friendship", "home", "family", "journey", "travel",
               "school", "exams", "space", "ocean", "sea", "forest", "garden", "desert", "mountain", "festival",
               "food", "tea", "chai", "coffee", "music", "dance", "memory", "dream", "dreams", "childhood",
               "loneliness", "hope", "freedom", "identity", "time", "nature", "animals", "cat", "train", "letters",
               "books", "library", "cinema", "film", "fashion", "streets", "village", "kitchen", "grandmother",
               "india", "mumbai", "delhi", "kerala", "rajasthan", "bengal", "punjab", "festival", "wedding",
               "climate", "technology", "robot", "magic", "myth", "mythology", "folk", "poetry", "stars", "moon",
               "poems", "nani", "dadi"}

MEDIUMS = ["Film", "Book", "Brand", "Poster", "Music video", "App"]


def clamp(x, low=-1.0, high=1.0):
    return max(low, min(high, x))


def words_in(text):
    return [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9\-']*", text.lower())]


def from_words(words):
    """What the vibe words alone suggest. Returns (numbers, words understood)."""
    numbers = {"valence": [], "arousal": [], "warmth": [], "bold": [], "era": [], "brightness": [], "texture": []}
    understood = []
    for w in words:
        hit = False
        if w in VIBE_WORDS:
            v, a, warm, bold, vintage = VIBE_WORDS[w]
            numbers["valence"].append(v); numbers["arousal"].append(a); numbers["warmth"].append(warm)
            numbers["bold"].append(bold); numbers["era"].append(-vintage); hit = True
        for table, key in ((ERA_WORDS, "era"), (BRIGHT_WORDS, "brightness"), (TEXTURE_WORDS, "texture")):
            if w in table:
                numbers[key].append(table[w]); hit = True
        for key, value in FEEL_WORDS.get(w, {}).items():
            numbers[key].append(value)
            hit = True
        if hit or w in THEME_WORDS:
            understood.append(w)
    means = {k: (sum(v) / len(v) if v else None) for k, v in numbers.items()}
    return means, list(dict.fromkeys(understood))


def build(text, emotions, medium=None, audience=None, start_from=None, importance=None):
    """The Vibe Vector for an idea.

    text: the idea (English, or the English translation of Hinglish/Hindi for word matching).
    emotions: [(label, score), ...] from ORBIT's emotion model (or the offline estimate).
    """
    total = sum(s for _, s in emotions) or 1.0
    ev = sum(EMOTION_VA[label][0] * s for label, s in emotions) / total
    ea = sum(EMOTION_VA[label][1] * s for label, s in emotions) / total
    words, themes = from_words(words_in(text))

    def mix(emotion_value, word_value, word_weight=0.6):
        """Words describe the vibe more directly than a short sentence's emotion, so they count a bit more."""
        if word_value is None:
            return emotion_value
        return clamp((1 - word_weight) * emotion_value + word_weight * word_value)

    valence, arousal = mix(ev, words["valence"]), mix(ea, words["arousal"])
    return {
        "text": text, "medium": medium, "audience": audience, "start_from": start_from,
        "emotions": [(label, round(float(s), 3)) for label, s in emotions[:8]],
        "valence": round(valence, 3), "arousal": round(arousal, 3),
        "brightness": round(clamp(words["brightness"] if words["brightness"] is not None else 0.4 * valence), 3),
        "warmth": round(clamp(words["warmth"] if words["warmth"] is not None else 0.3 * valence), 3),
        "era": round(clamp(words["era"] if words["era"] is not None else 0.0), 3),
        "texture": round(clamp(words["texture"] if words["texture"] is not None else 0.0), 3),
        "bold": round(clamp(words["bold"] if words["bold"] is not None else 0.4 * arousal), 3),
        "themes": themes or [label for label, _ in emotions[:2]],
        "importance": importance,
        "tweaks": {},          # palette refinements (muted, contrast, playful)
    }


# ---------------------------------------------------------------
# Refine chips and sliders: change the vector, then regenerate everything
# ---------------------------------------------------------------
CHIPS = {
    "Muted": "softer, greyer colours",
    "Warmer": "warmer colours and mood",
    "Dreamier": "calmer, softer, a little hazy",
    "Less corporate": "more hand-made and personal",
    "Bolder": "stronger colour and contrast",
    "More vintage": "further back in time",
}


def refine(vector, chip):
    v = copy.deepcopy(vector)
    t = v.setdefault("tweaks", {})
    if chip == "Muted":
        t["muted"] = round(t.get("muted", 1.0) * 0.8, 3)
        v["bold"] = clamp(v["bold"] - 0.2)
    elif chip == "Warmer":
        v["warmth"] = clamp(v["warmth"] + 0.35)
    elif chip == "Dreamier":
        v["arousal"] = clamp(v["arousal"] - 0.25)
        v["texture"] = clamp(v["texture"] - 0.2)
        v["brightness"] = clamp(v["brightness"] + 0.15)
        v["themes"] = list(dict.fromkeys(v["themes"] + ["dreamy"]))
    elif chip == "Less corporate":
        v["texture"] = clamp(v["texture"] + 0.35)
        v["era"] = clamp(v["era"] - 0.15)
        v["themes"] = list(dict.fromkeys(v["themes"] + ["hand-made"]))
    elif chip == "Bolder":
        v["bold"] = clamp(v["bold"] + 0.35)
        v["arousal"] = clamp(v["arousal"] + 0.15)
        t["contrast"] = round(min(3.0, t.get("contrast", 0.0) + 1.0), 2)
    elif chip == "More vintage":
        v["era"] = clamp(v["era"] - 0.35)
    return v


def with_sliders(vector, warm_cool=0.0, calm_energy=0.0, soft_bold=0.0, vintage_modern=0.0, dark_bright=0.0):
    """Sliders from -1 to +1 shift the vector (left = warm, calm, soft, vintage, dark)."""
    v = copy.deepcopy(vector)
    v["warmth"] = clamp(v["warmth"] - warm_cool)
    v["arousal"] = clamp(v["arousal"] + 0.6 * calm_energy)
    v["bold"] = clamp(v["bold"] + soft_bold)
    v["era"] = clamp(v["era"] + vintage_modern)
    v["brightness"] = clamp(v["brightness"] + dark_bright)
    return v


# ---------------------------------------------------------------
# Three directions from one idea
# ---------------------------------------------------------------
def directions(vector):
    """safe = the vibe as it is; bold = stronger and louder; weird = flipped and unexpected."""
    safe = copy.deepcopy(vector)
    safe.update(direction="Safe", discovery=0.2, harmony="analogous")
    bold = copy.deepcopy(vector)
    bold.update(direction="Bold", discovery=0.6, harmony="complementary",
                arousal=clamp(vector["arousal"] + 0.35), bold=clamp(vector["bold"] + 0.5),
                brightness=clamp(vector["brightness"] + 0.2))
    weird = copy.deepcopy(vector)
    weird.update(direction="Weird", discovery=1.0, harmony="triadic",
                 warmth=clamp(-0.7 * vector["warmth"] if abs(vector["warmth"]) > 0.15 else 0.7),
                 era=clamp(vector["era"] + (0.9 if vector["era"] <= 0 else -0.9)),
                 texture=clamp(vector["texture"] + 0.5 if vector["texture"] < 0.3 else vector["texture"] - 0.8))
    return {"Safe": safe, "Bold": bold, "Weird": weird}


def numbers(vector):
    """The numeric part, for matching aesthetics and creators."""
    return [vector["valence"], vector["arousal"], vector["brightness"], vector["warmth"], vector["era"],
            vector["texture"]]


def describe(vector):
    """Plain words for each number, for the 'How this was made' panel."""
    def word(x, low, high, middle="balanced"):
        return high if x > 0.2 else low if x < -0.2 else middle
    return {
        "Mood (valence)": word(vector["valence"], "heavy", "joyful", "in-between"),
        "Energy (arousal)": word(vector["arousal"], "calm", "energetic", "steady"),
        "Light": word(vector["brightness"], "dark", "bright", "soft light"),
        "Temperature": word(vector["warmth"], "cool", "warm", "neutral"),
        "Era": word(vector["era"], "vintage", "futuristic", "present day"),
        "Texture": word(vector["texture"], "smooth", "hand-made", "mixed"),
        "Boldness": word(vector["bold"], "soft", "bold", "medium"),
    }

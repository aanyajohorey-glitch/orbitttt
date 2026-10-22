"""
spark.py
Creator Mode -> "I don't have an idea yet": the SPARK path.

Six tappable questions (each can be skipped or answered with "Surprise me"):
    1 medium   2 target emotion (up to 2)   3 setting   4 era   5 contrast pair   6 texture
    7 (optional) one word on your mind, and how you're feeling right now

Then three ideas (Safe, Bold, Weird), each with a title, a one-line logline and
a "why this idea" line that quotes the user's own answers.

Method: a TEMPLATE GRAMMAR over data/idea_seeds.csv (settings, contrast pairs,
textures, story structures). Anything the user skipped is filled in from the
seeds that fit their other answers best (Safe), push energy up (Bold), or are
deliberately unexpected (Weird). Remix re-rolls ONE element; Lock keeps one
element and re-rolls the others.
"""
import copy
import hashlib
import random
from pathlib import Path

import pandas as pd
import streamlit as st

from ranking import cosine

SEEDS = Path(__file__).parent / "data" / "idea_seeds.csv"
ELEMENTS = ["medium", "setting", "contrast", "texture", "structure"]
MEDIUMS = ["Film", "Book", "Brand", "Poster", "Music video", "App"]
MEDIUM_PHRASE = {"Film": "a short film", "Book": "a short story", "Brand": "a brand identity",
                 "Poster": "a poster series", "Music video": "a music video", "App": "an app"}
# label -> (valence, arousal, emotion label used by the Vibe Vector, heavy?)
EMOTIONS = {
    "Joy": (0.8, 0.6, "joy", False), "Calm": (0.5, -0.6, "relief", False), "Wonder": (0.4, 0.5, "curiosity", False),
    "Hope": (0.6, 0.3, "optimism", False), "Love": (0.8, 0.3, "love", False),
    "Nostalgia": (0.1, -0.3, "realization", False), "Thrill": (0.3, 0.9, "excitement", False),
    "Playfulness": (0.7, 0.6, "amusement", False), "Melancholy": (-0.6, -0.4, "sadness", True),
    "Loneliness": (-0.5, -0.3, "sadness", True), "Anger": (-0.6, 0.8, "anger", True),
    "Fear": (-0.6, 0.6, "fear", True), "Grief": (-0.8, -0.3, "grief", True),
}
ERAS = {"Ancient and mythic": -1.0, "Vintage (before 1980)": -0.7, "Retro (1980s-2000s)": -0.3,
        "Today": 0.2, "The future": 0.9}
FEELINGS_NOW = ["Great", "Good", "Okay", "Low", "Very low"]
QUESTIONS = ["What are you making?", "Which feeling should it have? (up to 2)", "Where does it happen?",
             "When is it set?", "Pick a contrast", "What texture does it have?", "Anything else? (optional)"]


@st.cache_data
def load_seeds():
    return pd.read_csv(SEEDS).fillna({"tile": ""})


def seeds(kind):
    return load_seeds()[load_seeds()["kind"] == kind].to_dict("records")


def _rng(*parts):
    return random.Random(int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16))


# ---------------------------------------------------------------
# From answers to a target feel
# ---------------------------------------------------------------
def target(answers):
    """(valence, arousal) from the chosen emotions, or neutral-ish if skipped."""
    chosen = [EMOTIONS[e] for e in answers.get("emotions") or [] if e in EMOTIONS]
    if not chosen:
        return 0.3, 0.1
    return (sum(e[0] for e in chosen) / len(chosen), sum(e[1] for e in chosen) / len(chosen))


def heavy(answers):
    """Heavy feelings chosen (or a low mood right now): ORBIT gently mentions Feel mode. It never diagnoses."""
    return any(EMOTIONS[e][3] for e in answers.get("emotions") or [] if e in EMOTIONS) or \
        answers.get("feeling_now") in ("Low", "Very low")


def _pick(kind, answers, direction, rng, exclude=None):
    """Choose a seed of this kind for a direction: Safe = best fit, Bold = more energy, Weird = unexpected."""
    valence, arousal = target(answers)
    if direction == "Bold":
        arousal = min(1.0, arousal + 0.5)
    options = [s for s in seeds(kind) if s["text"] != exclude]
    scored = sorted(options, key=lambda s: -cosine([1, valence, arousal], [1, s["valence"], s["arousal"]]))
    if direction == "Weird":
        pool = scored[len(scored) // 2:]            # the less obvious half
    elif direction == "Bold":
        pool = scored[:6]
    else:
        pool = scored[:4]
    return rng.choice(pool)["text"]


# ---------------------------------------------------------------
# Ideas: elements -> title, logline, why
# ---------------------------------------------------------------
def _place(setting):
    for article in ("a ", "an ", "the "):
        if setting.lower().startswith(article):
            return setting[len(article):]
    return setting


# Which answered elements each direction is allowed to change (Safe keeps every answer).
FREE = {"Safe": set(), "Bold": {"texture", "structure"}, "Weird": {"setting", "structure"}}


def describe(idea, answers, taken=()):
    """Write the title, logline and 'why this idea' for an idea's elements (template grammar).
    taken: titles already used by the other ideas, so all three titles differ."""
    a, b = [w.strip() for w in idea["contrast"].split("+")]
    place = _place(idea["setting"])
    rng = _rng(idea["setting"], idea["contrast"], idea["texture"], idea["structure"], idea["medium"])
    options = [f"{a.title()} and {b.title()}", f"Notes from the {place}",
               f"The {idea['texture'].split()[0].title()} Hour", f"{b.title()}, Somehow"]
    rng.shuffle(options)
    title = next((t for t in options if t not in taken), options[0])
    era = answers.get("era")
    era_part = {"Ancient and mythic": " in a mythic past", "Vintage (before 1980)": " in another decade",
                "Retro (1980s-2000s)": " in the not-so-distant past", "The future": " in the future"}.get(era, "")
    feeling = " and ".join(e.lower() for e in answers.get("emotions") or []) or f"{a} and {b}"
    logline = (f"{MEDIUM_PHRASE[idea['medium']][0].upper() + MEDIUM_PHRASE[idea['medium']][1:]} told as "
               f"{idea['structure']}, around {idea['setting']}{era_part}, where {a} meets {b}, "
               f"in {idea['texture']}.")
    quoted = []
    for key, label in (("medium", "medium"), ("setting", "place"), ("contrast", "contrast"), ("texture", "texture")):
        if answers.get(key) == idea[key]:
            quoted.append(f"your {label} “{idea[key]}”")
    if answers.get("emotions"):
        quoted.append(f"the feeling “{feeling}”")
    if answers.get("word"):
        quoted.append(f"your word “{answers['word']}”")
    why = ("Built from " + ", ".join(quoted) + "." if quoted else "You skipped the questions, so ORBIT chose "
           "elements that fit together.")
    changed = [k for k in FREE[idea["direction"]] if answers.get(k) and answers.get(k) != idea[k]]
    if idea["direction"] == "Bold":
        why += " The Bold version turns the energy up" + (
            f": it swaps your {' and '.join(changed)} for something louder." if changed else ".")
    elif idea["direction"] == "Weird":
        why += " The Weird version picks the less obvious options on purpose" + (
            f", so it moves your {' and '.join(changed)} somewhere unexpected." if changed else ".")
    return {**idea, "title": title, "logline": logline, "why": why}


def make_idea(answers, direction, seed=0, taken=()):
    """One idea. Answered elements are kept, except the few a direction is allowed to change (FREE)."""
    rng = _rng(direction, seed, sorted(answers.items(), key=str))
    idea = {"direction": direction}
    idea["medium"] = answers.get("medium") or rng.choice(
        {"Safe": ["Film", "Poster", "Book"], "Bold": ["Music video", "Poster", "Brand"],
         "Weird": ["App", "Brand", "Book"]}[direction])
    for kind in ("setting", "contrast", "texture", "structure"):
        answered = answers.get(kind)
        if answered and kind not in FREE[direction]:
            idea[kind] = answered
        else:
            idea[kind] = _pick(kind, answers, direction, rng, exclude=answered)
    if answers.get("word"):
        idea["word"] = answers["word"]
    return describe(idea, answers, taken)


def three_ideas(answers, seed=0):
    ideas = []
    for direction in ("Safe", "Bold", "Weird"):
        ideas.append(make_idea(answers, direction, seed, taken=[i["title"] for i in ideas]))
    return ideas


def remix(idea, element, answers, seed=1):
    """Re-roll ONE element; everything else stays exactly the same."""
    rng = _rng("remix", element, seed, idea["title"])
    new = copy.deepcopy(idea)
    if element == "medium":
        new["medium"] = rng.choice([m for m in MEDIUMS if m != idea["medium"]])
    else:
        new[element] = _pick(element, answers, idea["direction"], rng, exclude=idea[element])
    return describe(new, answers)


def lock(idea, element, answers, seed=1):
    """Keep ONE element; re-roll all the others (answered ones included, so the idea really changes)."""
    rng = _rng("lock", element, seed, idea["title"])
    new = copy.deepcopy(idea)
    for other in ELEMENTS:
        if other == element:
            continue
        if other == "medium":
            new["medium"] = rng.choice([m for m in MEDIUMS if m != idea["medium"]])
        else:
            new[other] = _pick(other, answers, idea["direction"], rng, exclude=idea[other])
    return describe(new, answers)


# ---------------------------------------------------------------
# Use this idea -> the Vibe Vector
# ---------------------------------------------------------------
def to_vector(idea, answers):
    """Average the numbers of the idea's seeds, with the chosen emotions and era."""
    import vibe
    table = load_seeds()
    rows = [table[(table["kind"] == kind) & (table["text"] == idea[kind])].iloc[0]
            for kind in ("setting", "contrast", "texture", "structure")]
    chosen = [EMOTIONS[e] for e in answers.get("emotions") or [] if e in EMOTIONS]
    emotions = [(e[2], 1.0 / len(chosen)) for e in chosen] or [("neutral", 1.0)]
    text = f"{idea['logline']} {idea.get('word', '')}".strip()
    vector = vibe.build(text, emotions, medium=idea["medium"], start_from="spark")

    def mean(column, weight_rows=rows):
        return sum(float(r[column]) for r in weight_rows) / len(weight_rows)
    valence, arousal = target(answers) if chosen else (mean("valence"), mean("arousal"))
    era = ERAS.get(answers.get("era"), mean("era"))
    vector.update(valence=round(valence, 3), arousal=round(arousal, 3), warmth=round(mean("warmth"), 3),
                  era=round(era, 3), brightness=round(mean("brightness"), 3), texture=round(mean("texture"), 3),
                  bold=round(vibe.clamp(0.4 * arousal + (0.3 if idea["direction"] == "Bold" else 0.0)), 3))
    tags = [t for r in rows for t in str(r["tags"]).split("|")]
    vector["themes"] = list(dict.fromkeys(vector["themes"] + tags))[:10]
    return vector

"""
datasets.py
Loading ORBIT's labelled datasets in one consistent shape, and tagging each
sentence's writing style so results can be compared fairly.

Every dataset becomes a table with: text, language, family, style.

Datasets (all in data/):
  train_augment.csv  - TRAINING data for ORBIT's classifier (author-written)
  eval_set.csv       - the original 70-sentence DEVELOPMENT set. Its Hinglish
                       results are optimistic: the dictionary was written while
                       looking at it.
  eval_body.csv      - a focused test of feelings described through the body
  eval_heldout.csv   - classmates' sentences, NEVER used for training or tuning
  corrections        - "Teach Orbit" fixes from users (stored in orbit.db)
"""
import re
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"
FAMILIES = ["Joy", "Warmth", "Sadness", "Fear", "Anger", "Wonder", "Neutral"]
LANGUAGES = {"en": "English", "english": "English", "hinglish": "Hinglish", "hindi": "Hindi"}

# Words that describe feelings through the body (English and Hinglish)
BODY_WORDS = re.compile(
    r"\b(heart\w*|chest|stomach\w*|tummy|breath\w*|breathe|shak\w*|trembl\w*|sweat\w*|hands?|legs?|knees?|"
    r"dizzy|nause\w*|sick to my|throw\w* up|throat|mouth|eyes|face|fists?|head\w*|ache\w*|pulse|chills|"
    r"tense|tight|numb|butterflies|shiver\w*|pounding|racing|jittery|cold|slept|sleep|exhausted|"
    r"dil|dhadak\w*|dhadkan|pasina|haath|pair|pet|kaanp\w*)\b",
    re.IGNORECASE,
)
# Hindi body words (Devanagari words don't work with \b, so no word boundaries)
BODY_WORDS_HINDI = re.compile(r"(सांस|दिल|धड़क|पसीना|हाथ|पेट|काँप|कांप)")
SLANG = re.compile(r"\b(lol|lmao|ugh|omg|bro|tbh|idk|ngl|fr|yaar|bhai|bruh|wtf)\b|[\U0001F300-\U0001FAFF]",
                   re.IGNORECASE)


def writing_style(text):
    """One style tag per sentence (checked in this order)."""
    words = re.findall(r"\S+", text)
    if BODY_WORDS.search(text) or BODY_WORDS_HINDI.search(text):
        return "Body-based"
    if len(words) <= 4:
        return "Very short"
    if SLANG.search(text):
        return "Informal / slang"
    return "Standard"


def _normalise(table, family_column):
    table = table.rename(columns={family_column: "family"})
    table["language"] = table["language"].str.strip().str.lower().map(LANGUAGES).fillna(table["language"])
    table["family"] = table["family"].str.strip().str.capitalize()
    unknown = sorted(set(table["family"]) - set(FAMILIES))
    if unknown:
        raise ValueError(f"Unknown emotion families: {unknown}")
    table["style"] = table["text"].map(writing_style)
    return table[["text", "language", "family", "style"]].reset_index(drop=True)


def load(name):
    """Load a dataset by name: 'train', 'dev', 'body' or 'heldout'."""
    files = {"train": ("train_augment.csv", "emotion_family"), "dev": ("eval_set.csv", "expected"),
             "body": ("eval_body.csv", "emotion_family"), "heldout": ("eval_heldout.csv", "emotion_family")}
    file, column = files[name]
    path = DATA / file
    if not path.exists():
        return pd.DataFrame(columns=["text", "language", "family", "style"])
    table = pd.read_csv(path, encoding="utf-8")
    table = table.dropna(subset=["text"])
    table = table[table["text"].str.strip() != ""]
    if table.empty:
        return pd.DataFrame(columns=["text", "language", "family", "style"])
    return _normalise(table, column)


def file_version(name):
    """Changes whenever the file changes (used to refresh cached results)."""
    files = {"train": "train_augment.csv", "dev": "eval_set.csv", "body": "eval_body.csv",
             "heldout": "eval_heldout.csv"}
    path = DATA / files[name]
    return path.stat().st_mtime if path.exists() else 0

"""
storage.py
Saves ORBIT's data on THIS computer in a small SQLite database
(data/orbit.db). SQLite is built into Python, so nothing extra is needed.

What is stored:
- entries     : journal check-ins (text, emotions, world)
- collection  : worlds saved to My Collection
- wellbeing   : Calm Room sessions (mood before and after)
- feedback    : ratings for the impact study
- settings    : the user's name and privacy choices

Nothing is ever sent to the internet. The database file is listed in
.gitignore so it is never uploaded to GitHub.
"""
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

# Tests can point ORBIT at a temporary database with the ORBIT_DB variable.
DB_PATH = Path(os.environ.get("ORBIT_DB", Path(__file__).parent / "data" / "orbit.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, source TEXT, text TEXT,
    primary_emotion TEXT, primary_score REAL,
    emotions TEXT, world TEXT, demo INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS collection (
    id TEXT PRIMARY KEY, world TEXT, source TEXT, intent TEXT,
    prompt TEXT, constraint_text TEXT, note TEXT, saved_at TEXT
);
CREATE TABLE IF NOT EXISTS wellbeing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, tool TEXT, before INTEGER, after INTEGER, demo INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, rating INTEGER, comment TEXT
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, text TEXT, predicted TEXT, corrected TEXT, raw_scores TEXT, source TEXT
);
"""


def now():
    return datetime.now().isoformat(timespec="seconds")


def run(sql, params=()):
    """Run one SQL command and return the rows (as dictionaries)."""
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def init():
    """Create the database and its tables if they don't exist yet."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------
# Settings
# ---------------------------------------------------------------
def get_setting(key, default=None):
    rows = run("SELECT value FROM settings WHERE key = ?", (key,))
    return rows[0]["value"] if rows else default


def set_setting(key, value):
    run("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))


def journal_enabled():
    return get_setting("journal_on", "1") == "1"


# ---------------------------------------------------------------
# Journal entries
# ---------------------------------------------------------------
def add_entry(source, text, emotions, world, created_at=None, demo=False, primary=None):
    """primary: ORBIT's final emotion (from the trained classifier). Defaults to
    the base model's strongest emotion."""
    scores = dict(emotions)
    primary = primary or emotions[0][0]
    score = scores.get(primary, emotions[0][1])
    run(
        "INSERT INTO entries (created_at, source, text, primary_emotion, primary_score, emotions, world, demo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (created_at or now(), source, text, primary, score, json.dumps(emotions), world, int(demo)),
    )


def list_entries():
    rows = run("SELECT * FROM entries ORDER BY created_at")
    for row in rows:
        row["emotions"] = [tuple(pair) for pair in json.loads(row["emotions"])]
    return rows


def delete_entry(entry_id):
    run("DELETE FROM entries WHERE id = ?", (entry_id,))


def clear_entries(demo_only=False):
    run("DELETE FROM entries" + (" WHERE demo = 1" if demo_only else ""))


# ---------------------------------------------------------------
# My Collection
# ---------------------------------------------------------------
def add_collection_item(item):
    run(
        "INSERT OR REPLACE INTO collection (id, world, source, intent, prompt, constraint_text, note, saved_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (item["id"], item["world"], item["source"], item["intent"], item["prompt"],
         item["constraint"], item["note"], item["saved_at"]),
    )


def list_collection():
    rows = run("SELECT * FROM collection ORDER BY rowid")
    for row in rows:
        row["constraint"] = row.pop("constraint_text")
    return rows


def remove_collection_item(item_id):
    run("DELETE FROM collection WHERE id = ?", (item_id,))


def clear_collection():
    run("DELETE FROM collection")


# ---------------------------------------------------------------
# Calm Room sessions and feedback (the impact study)
# ---------------------------------------------------------------
def add_wellbeing(tool, before, after, created_at=None, demo=False):
    run(
        "INSERT INTO wellbeing (created_at, tool, before, after, demo) VALUES (?, ?, ?, ?, ?)",
        (created_at or now(), tool, before, after, int(demo)),
    )


def list_wellbeing():
    return run("SELECT * FROM wellbeing ORDER BY created_at")


def clear_wellbeing(demo_only=False):
    run("DELETE FROM wellbeing" + (" WHERE demo = 1" if demo_only else ""))


def add_feedback(rating, comment):
    run("INSERT INTO feedback (created_at, rating, comment) VALUES (?, ?, ?)", (now(), rating, comment))


def list_feedback():
    return run("SELECT * FROM feedback ORDER BY created_at")


# ---------------------------------------------------------------
# Teach Orbit corrections (human-in-the-loop labels)
# ---------------------------------------------------------------
def add_correction(text, predicted, corrected, raw_scores, source):
    run("INSERT INTO corrections (created_at, text, predicted, corrected, raw_scores, source) "
        "VALUES (?, ?, ?, ?, ?, ?)", (now(), text, predicted, corrected, json.dumps(raw_scores), source))


def list_corrections():
    rows = run("SELECT * FROM corrections ORDER BY created_at")
    for row in rows:
        row["raw_scores"] = json.loads(row["raw_scores"])
    return rows


def clear_corrections():
    run("DELETE FROM corrections")


def delete_everything():
    """Erase every saved journal entry, world, session, rating, correction and setting."""
    for table in ("entries", "collection", "wellbeing", "feedback", "corrections", "settings"):
        run(f"DELETE FROM {table}")

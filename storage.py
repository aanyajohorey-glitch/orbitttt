"""
storage.py
Saves ORBIT's data in a small SQLite database. SQLite is built into Python.

Two storage modes:
- "local"   (running on your own computer): one file, data/orbit.db, which
             stays on this computer and is listed in .gitignore.
- "session" (running on Streamlit Community Cloud, or ORBIT_STORAGE=session):
             every browser session gets its OWN temporary database, so visitors
             never see each other's data. It disappears when the server
             restarts (and is cleaned up after 24 hours). Use Settings ->
             "Download my data" / "Import my data" to keep a journal.

What is stored:
- entries     : journal check-ins (text, emotions, world). Never crisis text.
- collection  : worlds saved to My Collection
- wellbeing   : mood before and after a tool
- feedback    : impact-study ratings and comments
- ratings     : thumbs up / down on replies and tools
- corrections : Teach Orbit labels
- notes       : things the user CHOSE to keep (e.g. a Reach Out draft)
- settings    : name, accessibility and privacy choices

Nothing is sent to the internet by this file.
"""
import json
import os
import sqlite3
import tempfile
import time
from contextlib import closing
from datetime import datetime
from pathlib import Path

# Tests can point ORBIT at a temporary database with the ORBIT_DB variable.
LOCAL_DB = Path(os.environ.get("ORBIT_DB", Path(__file__).parent / "data" / "orbit.db"))
DB_PATH = LOCAL_DB          # kept for older code; use db_path() instead
SESSION_DIR = Path(tempfile.gettempdir()) / "orbit_sessions"
SESSION_MAX_AGE = 24 * 3600


def on_streamlit_cloud():
    """Streamlit Community Cloud runs apps from /mount/src/<repository>."""
    return str(Path(__file__).resolve()).replace("\\", "/").startswith("/mount/src/")


def storage_mode():
    if os.environ.get("ORBIT_STORAGE") in ("local", "session"):
        return os.environ["ORBIT_STORAGE"]
    return "session" if on_streamlit_cloud() else "local"


def _session_id():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        return ctx.session_id if ctx else "no-session"
    except Exception:
        return "no-session"


def db_path():
    if storage_mode() == "session":
        return SESSION_DIR / f"{_session_id()}.db"
    return LOCAL_DB


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
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, kind TEXT, target TEXT, value INTEGER
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, kind TEXT, title TEXT, text TEXT
);
CREATE TABLE IF NOT EXISTS corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, text TEXT, predicted TEXT, corrected TEXT, raw_scores TEXT, source TEXT
);
"""


def now():
    return datetime.now().isoformat(timespec="seconds")


def run(sql, params=()):
    """Run one SQL command and return the rows (as dictionaries)."""
    with closing(sqlite3.connect(db_path())) as conn, conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def init():
    """Create the database and its tables if they don't exist yet."""
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if storage_mode() == "session":
        _clean_old_sessions()
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.executescript(SCHEMA)


def _clean_old_sessions():
    for old in SESSION_DIR.glob("*.db"):
        try:
            if time.time() - old.stat().st_mtime > SESSION_MAX_AGE:
                old.unlink()
        except OSError:
            pass


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
# Thumbs up / down on replies and tools (satisfaction metric)
# ---------------------------------------------------------------
def add_rating(kind, target, value):
    """kind: 'reply' or 'tool'; target: e.g. 'ORBIT templates' or 'Breathing'; value: 1 (up) or 0 (down)."""
    rows = run("INSERT INTO ratings (created_at, kind, target, value) VALUES (?, ?, ?, ?) RETURNING id",
               (now(), kind, target, value))
    return rows[0]["id"]


def delete_rating(rating_id):
    run("DELETE FROM ratings WHERE id = ?", (rating_id,))


def list_ratings():
    return run("SELECT * FROM ratings ORDER BY created_at")


# ---------------------------------------------------------------
# Notes the user chose to keep (Reach Out drafts)
# ---------------------------------------------------------------
def add_note(kind, title, text):
    run("INSERT INTO notes (created_at, kind, title, text) VALUES (?, ?, ?, ?)", (now(), kind, title, text))


def list_notes(kind=None):
    if kind:
        return run("SELECT * FROM notes WHERE kind = ? ORDER BY created_at DESC", (kind,))
    return run("SELECT * FROM notes ORDER BY created_at DESC")


def delete_note(note_id):
    run("DELETE FROM notes WHERE id = ?", (note_id,))


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


# ---------------------------------------------------------------
# Export / import (so a journal can be kept when hosted on Streamlit Cloud)
# ---------------------------------------------------------------
EXPORT_TABLES = ("entries", "collection", "wellbeing", "feedback", "ratings", "corrections", "notes", "settings")


def _columns(table):
    return [row["name"] for row in run(f"PRAGMA table_info({table})")]


def export_data():
    """Everything ORBIT stores, as JSON bytes the user can download."""
    data = {"orbit_export": 1, "exported_at": now()}
    for table in EXPORT_TABLES:
        data[table] = run(f"SELECT * FROM {table}")
    return json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8")


def import_data(raw):
    """Replace ORBIT's data with a previously exported file. Returns rows imported.

    Only known tables and columns are accepted, so a damaged or edited file
    can't inject anything else.
    """
    data = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
    if data.get("orbit_export") != 1:
        raise ValueError("This doesn't look like an ORBIT export file.")
    count = 0
    for table in EXPORT_TABLES:
        allowed = _columns(table)
        rows = data.get(table, [])
        if not isinstance(rows, list):
            raise ValueError(f"Bad section: {table}")
        run(f"DELETE FROM {table}")
        for row in rows:
            row = {k: v for k, v in row.items() if k in allowed}
            if not row:
                continue
            cols = ", ".join(row)
            marks = ", ".join("?" for _ in row)
            run(f"INSERT INTO {table} ({cols}) VALUES ({marks})", tuple(row.values()))
            count += 1
    return count


def panic_wipe():
    """Delete ALL local data immediately: every table, the personal model and,
    in session mode, the session's database file."""
    delete_everything()
    import orbit_head   # imported here to avoid a circular import
    personal = orbit_head.personal_model()
    if personal.exists():
        personal.unlink()
    if storage_mode() == "session" and db_path().exists():
        try:
            db_path().unlink()
        except OSError:
            pass


def delete_everything():
    """Erase every saved journal entry, world, session, rating, correction and setting."""
    for table in EXPORT_TABLES:
        run(f"DELETE FROM {table}")

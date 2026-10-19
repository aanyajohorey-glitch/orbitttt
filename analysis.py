"""
analysis.py
ORBIT's full AI pipeline, shared by Home, Mood Lab and the Companion:

    1. Check   - is there any text with real words?
    2. Translate - Hinglish/Hindi words -> English   (hinglish.py)
    3. Detect  - 28 emotion scores                   (emotion_model.py)
    4. Match   - the closest aesthetic world          (world_data.py)
    5. Protect - safety check for crisis words        (safety.py)

It also records check-ins in the private journal and gives arcade tokens.
"""
import streamlit as st

import storage
from emotion_model import detect_emotions, load_model
from hinglish import to_english
from safety import check as safety_check
from world_data import match_world


def analyse(text, empty_message):
    """Run the pipeline. Returns a result dictionary, or None (with a message)."""
    if text == "":
        st.warning(empty_message)
        return None

    # The model reads words. Text with no letters at all (only numbers,
    # symbols or emoji) would give a confident but meaningless result.
    if not any(character.isalpha() for character in text):
        st.warning("ORBIT reads words. Try describing how you feel in a sentence or two.")
        return None

    try:
        with st.spinner("Waking up the emotion model…"):
            load_model()
    except Exception:
        st.error(
            "The emotion model couldn't be loaded. The first run needs an internet "
            "connection to download it (about 125 MB); after that it works offline."
        )
        return None

    try:
        with st.spinner("Reading your words…"):
            model_text, translated = to_english(text)
            emotions = detect_emotions(model_text)
            world, _, matched = match_world(emotions)
    except Exception:
        st.error("Something went wrong while reading that text. Please try again or rephrase it.")
        return None

    return {
        "text": text,
        "model_text": model_text,
        "translated": translated,
        "emotions": emotions,
        "world": world["name"],
        "matched": matched,
        "safety": safety_check(text) or safety_check(model_text, emotions),
    }


def flash(message):
    """Queue a short pop-up message (shown by app.py on the next run)."""
    st.session_state.flash.append(message)


def earn_token(reason):
    """Self-care earns arcade tokens for the Vending Machine."""
    st.session_state.tokens += 1
    flash(f"+1 arcade token · {reason}")


def record_checkin(result, source):
    """Save a check-in to the private journal (if allowed) and give a token."""
    if storage.journal_enabled():
        storage.add_entry(source, result["text"], result["emotions"], result["world"])
    earn_token("thanks for checking in")

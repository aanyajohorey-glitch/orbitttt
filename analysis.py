"""
analysis.py
ORBIT's full AI pipeline, shared by Home, Mood Lab and the Companion:

    1. Check     - is there any text with real words?
    2. Detect    - RoBERTa scores 28 emotions              (emotion_model.py)
                   (Hinglish/Hindi words are translated first so the scores
                   shown to the user are readable - hinglish.py)
    3. Decide    - ORBIT's trained classifier picks the emotion FAMILY and
                   says how confident it is                (orbit_head.py)
    4. Match     - the closest aesthetic world in that family (world_data.py)
    5. Protect   - deterministic safety check                (safety.py)

It also records check-ins in the private journal and gives arcade tokens,
following ORBIT's rules: nothing is stored and no games are offered when
someone may be in crisis.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
import streamlit as st

import orbit_head
import storage
from emotion_model import EMOTION_GROUPS, GROUP_OF, detect_emotions, load_model
from hinglish import to_english
from safety import check as safety_check
from world_data import match_world

UNSURE_BELOW = 0.5   # chosen from out-of-fold accuracy by confidence (docs/methodology.md)

# If the classifier picks a family but the base model gave every emotion in it
# a tiny score, this emotion represents the family.
REPRESENTATIVE = {"Joy": "joy", "Warmth": "caring", "Sadness": "sadness", "Fear": "nervousness",
                  "Anger": "annoyance", "Wonder": "curiosity", "Neutral": "neutral"}


@lru_cache(maxsize=4)
def _head(path, modified):
    return orbit_head.load(Path(path))


def current_head():
    """The personal model (after Teach Orbit retraining) or the shared one."""
    for path in (orbit_head.PERSONAL_MODEL, orbit_head.SHARED_MODEL):
        if path.exists():
            return _head(str(path), path.stat().st_mtime)
    return None


def family_emotion(family, emotions):
    """The strongest emotion inside a family (from the base model's scores)."""
    scores = dict(emotions)
    best = max(EMOTION_GROUPS[family], key=lambda label: scores.get(label, 0.0))
    return best if scores.get(best, 0.0) >= 0.02 else REPRESENTATIVE[family]


def apply_family(result, family, source):
    """Set ORBIT's final reading to a family (from the classifier or the user)."""
    world, _, matched = match_world(result["emotions"], family=family)
    result["final"].update({"family": family, "emotion": family_emotion(family, result["emotions"]),
                            "source": source})
    result["world"], result["matched"] = world["name"], matched
    return result


def interpret(text):
    """The pipeline without any screen messages (used by the app and the tests)."""
    model_text, translated = to_english(text)
    emotions = detect_emotions(model_text)
    raw_scores = dict(emotions) if not translated else dict(detect_emotions(text))

    head = current_head()
    if head:
        W, b, meta = head
        features = orbit_head.features(text, raw_scores, load_model()["labels"])
        probs = orbit_head.predict_proba(features[None, :], W, b)[0]
        order = np.argsort(probs)[::-1]
        family_probs = [(orbit_head.FAMILIES[i], float(probs[i])) for i in order]
        source = "ORBIT classifier" + (" (personal)" if meta.get("corrections") else "")
    else:  # fallback: v0.3 behaviour
        family_probs = [(GROUP_OF[emotions[0][0]], float(emotions[0][1]))]
        source = "RoBERTa + dictionary"
    family, confidence = family_probs[0]

    result = {
        "text": text,
        "model_text": model_text,
        "translated": translated,
        "emotions": emotions,           # base model scores (shown as bars)
        "raw_scores": raw_scores,       # base model scores for the ORIGINAL text (classifier input)
        "final": {"family": family, "confidence": confidence, "unsure": confidence < UNSURE_BELOW,
                  "alternatives": family_probs[:3]},
        "safety": safety_check(text) or safety_check(model_text, emotions),
    }
    return apply_family(result, family, source)


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
            return interpret(text)
    except Exception:
        st.error("Something went wrong while reading that text. Please try again or rephrase it.")
        return None


def flash(message):
    """Queue a short pop-up message (shown by app.py at the end of the run)."""
    st.session_state.flash.append(message)


def earn_token(reason):
    """Self-care earns arcade tokens for the Vending Machine."""
    st.session_state.tokens += 1
    flash(f"+1 arcade token · {reason}")


def games_allowed(result):
    """Rule: when someone may be in crisis, ORBIT shows help and nothing else.
    No tokens, no worlds, no vending machine, no saving."""
    return result is not None and result.get("safety") != "crisis"


def may_store(result):
    """Rule: crisis text is NEVER written to the journal or anywhere else."""
    return games_allowed(result) and storage.journal_enabled()


def record_checkin(result, source):
    """Save a check-in to the private journal (if allowed) and give a token."""
    if not games_allowed(result):
        return
    if may_store(result):
        storage.add_entry(source, result["text"], result["emotions"], result["world"],
                          primary=result["final"]["emotion"])
    earn_token("thanks for checking in")


def teach(result, corrected_family, source):
    """Teach Orbit: store the user's correction locally and update the result."""
    if not games_allowed(result):
        return result   # crisis text is never stored, not even as a correction
    storage.add_correction(result["text"], result["final"]["family"], corrected_family,
                           result["raw_scores"], source)
    result["final"]["unsure"] = False
    result["final"]["confidence"] = 1.0
    return apply_family(result, corrected_family, "your correction")

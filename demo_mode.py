"""
demo_mode.py
Offline demo mode: ORBIT keeps working if the emotion model can't be
downloaded or loaded (for example, no internet during the viva).

How it works
  1. Showcase sentences (the demo journal, the chat starters and a few key
     examples) have REAL results saved in data/demo_results.json, made earlier
     with the real model. Typing one of them gives exactly that result.
  2. Any other text is read by variant T: a small classifier that learned only
     word patterns (no emotion model). It is less accurate, and ORBIT labels
     it clearly as an "offline estimate".
  3. The safety check is deterministic and works the same offline.

Demo mode turns on automatically when the model can't be loaded, or by hand
in About -> Settings.
"""
import json
from pathlib import Path

import numpy as np
import streamlit as st

import orbit_head
import storage
from emotion_model import EMOTION_GROUPS
from safety import check as safety_check

DEMO_RESULTS = Path(__file__).parent / "data" / "demo_results.json"

SHOWCASE = [
    "My heart is racing before the presentation.",
    "I'm excited about the trip! But I'm nervous about meeting new people.",
    "yaar mujhe bahut gussa aa raha hai",
    "I miss my grandmother so much. Everything at home reminds me of her.",
    "Thank you so much to everyone who helped me move house. It's finally over and I can breathe.",
    "I wonder how black holes actually work. Why does time slow down near them?",
    "today was weird",
]


def showcase_texts():
    from companion import STARTERS
    from journal import DEMO_STORY
    return list(dict.fromkeys(SHOWCASE + list(STARTERS) + list(DEMO_STORY)))


def build_demo_results():
    """Run the REAL pipeline on the showcase sentences and save the results."""
    from analysis import interpret
    results = {}
    for text in showcase_texts():
        r = interpret(text)
        results[text] = {k: r[k] for k in ("text", "model_text", "translated", "emotions", "raw_scores", "final",
                                           "world", "matched", "safety")}
    DEMO_RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(results)


def _stored():
    if DEMO_RESULTS.exists():
        return json.loads(DEMO_RESULTS.read_text(encoding="utf-8"))
    return {}


def enabled():
    return storage.get_setting("demo_mode", "0") == "1" or st.session_state.get("model_failed", False)


def interpret_offline(text):
    """A result in the same shape as analysis.interpret, without the emotion model."""
    from analysis import UNSURE_BELOW, apply_family, is_vague

    stored = _stored().get(text)
    if stored:
        result = json.loads(json.dumps(stored))   # a fresh copy
        result["emotions"] = [tuple(pair) for pair in result["emotions"]]
        result["final"]["alternatives"] = [tuple(pair) for pair in result["final"]["alternatives"]]
        result["final"]["source"] = "Demo (saved real result)"
        result["safety"] = safety_check(text) or result["safety"]
        return result

    model = orbit_head.load(orbit_head.CANDIDATES["T"])
    if model is None:
        raise RuntimeError("offline model missing")
    W, b, meta = model
    probs = orbit_head.predict_proba(orbit_head.text_features(text)[None, :], W, b, meta.get("temperature", 1.0))[0]
    order = np.argsort(probs)[::-1]
    family_probs = [(orbit_head.FAMILIES[i], float(probs[i])) for i in order]
    # Without the emotion model there are no 28 scores: show the family estimate instead.
    emotions = []
    for family, p in family_probs:
        emotions += [(label, p / len(EMOTION_GROUPS[family])) for label in EMOTION_GROUPS[family]]
    emotions.sort(key=lambda pair: -pair[1])
    family, confidence = family_probs[0]
    result = {
        "text": text, "model_text": text, "translated": False, "emotions": emotions,
        "raw_scores": dict(emotions),
        "final": {"family": family, "confidence": confidence,
                  "unsure": confidence < UNSURE_BELOW or is_vague(text), "vague": is_vague(text),
                  "alternatives": family_probs[:3]},
        "safety": safety_check(text),
    }
    return apply_family(result, family, "Offline estimate (no emotion model)")


def banner():
    if not enabled():
        return
    reason = ("the emotion model couldn't be loaded (no internet?)" if st.session_state.get("model_failed")
              else "it's switched on in Settings")
    st.html('<div class="demo-banner"><b>Offline demo mode</b> · ' + reason + ". Sample sentences give the real "
            "results saved earlier; anything else gets a simpler offline estimate. Safety checks work as usual.</div>")


def sample_buttons(target_key):
    """Clickable sample sentences (so a demo always has something that works)."""
    st.html('<div class="field-label" style="margin-top:.4rem">Try a sample sentence</div>')
    columns = st.columns(3)
    for index, text in enumerate(SHOWCASE[:6]):
        columns[index % 3].button(text[:48] + ("…" if len(text) > 48 else ""), key=f"sample_{target_key}_{index}",
                                  on_click=st.session_state.__setitem__, args=(target_key, text), width="stretch")

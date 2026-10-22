"""
feedback_ui.py
Thumbs up / down on ORBIT's replies and tools.

Each rating is saved only on this computer (storage.add_rating) and becomes
the satisfaction metric on the AI Lab page. A rating can be changed; only the
latest choice for each button counts.
"""
import streamlit as st

import storage


def _save(kind, target, key):
    saved = st.session_state.setdefault("rating_ids", {})   # button key -> row in the ratings table
    if key in saved:                                        # changed your mind: replace the old rating
        storage.delete_rating(saved.pop(key))
    value = st.session_state.get(key)
    if value is None:
        return
    saved[key] = storage.add_rating(kind, target, int(value))
    st.session_state.flash.append("Thanks for the feedback." if value else
                                  "Thanks for telling me. That helps ORBIT improve.")


def thumbs(kind, target, key, label="Was this helpful?"):
    """kind: 'reply' or 'tool'. target: which reply style or tool was rated."""
    left, right = st.columns([1.3, 1], vertical_alignment="center")
    left.html(f'<span class="feedback-label">{label}</span>')
    with right:
        st.feedback("thumbs", key=key, on_change=_save, args=(kind, target, key))


THUMB_KINDS = {"reply": "Reply", "tool": "Tool", "reach_out": "Reach Out draft"}   # thumbs: value 0 or 1


def satisfaction(ratings):
    """Share of thumbs-up per kind and target, e.g. {('reply', 'ORBIT templates'): (0.8, 10)}.
    Only thumbs count here; 1-5 ratings (Mood Studio) are reported separately."""
    totals = {}
    for r in ratings:
        if r["kind"] not in THUMB_KINDS:
            continue
        up, n = totals.get((r["kind"], r["target"]), (0, 0))
        totals[(r["kind"], r["target"])] = (up + r["value"], n + 1)
    return {k: (up / n, n) for k, (up, n) in totals.items()}

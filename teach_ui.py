"""
teach_ui.py
"Teach Orbit": human-in-the-loop learning on screen.

Under every result, the user can say "Not quite right?" and choose the
feeling that fits better. When ORBIT is unsure, it shows the two most likely
feelings as quick answers instead of guessing.

Every answer is saved ONLY on this computer (storage.add_correction) and can
later be used to retrain ORBIT's classifier on the AI Lab page. Crisis
messages never show this panel and are never stored.
"""
import streamlit as st

from analysis import flash, games_allowed, teach
from components import esc

FAMILY_HELP = {
    "Joy": "happy, excited, proud, relieved", "Warmth": "love, care, gratitude",
    "Sadness": "sad, lonely, disappointed", "Fear": "worried, nervous, scared, embarrassed",
    "Anger": "annoyed, angry, frustrated", "Wonder": "curious, confused, surprised",
    "Neutral": "no strong feeling",
}
FAMILIES = list(FAMILY_HELP)


def confidence_html(result):
    final = result["final"]
    if final["source"] == "your correction":
        return '<span class="confidence sure">You told ORBIT this</span>'
    if final.get("vague"):
        return '<span class="confidence unsure">Short or vague message · ORBIT is asking</span>'
    if final["unsure"]:
        return f'<span class="confidence unsure">ORBIT isn\'t sure ({final["confidence"]:.0%})</span>'
    return f'<span class="confidence sure">ORBIT is {final["confidence"]:.0%} sure</span>'


def _apply(result, family, source, on_update):
    teach(result, family, source)
    if on_update:
        on_update(result)
    flash(f"Thank you! ORBIT noted that this felt like {family}. Your answer stays on this computer.")


def clarify(result, key, on_update=None):
    """Quick answers when ORBIT is unsure. Returns True if shown."""
    if not games_allowed(result) or not result["final"]["unsure"]:
        return False
    (first, _), (second, _) = result["final"]["alternatives"][:2]
    st.html('<div class="field-label" style="margin-top:.6rem">Which feels closer?</div>')
    a, b, _ = st.columns([1, 1, 1.2])
    a.button(f"{first} · {FAMILY_HELP[first].split(',')[0]}", key=f"{key}_c1", width="stretch",
             on_click=_apply, args=(result, first, "clarification", on_update))
    b.button(f"{second} · {FAMILY_HELP[second].split(',')[0]}", key=f"{key}_c2", width="stretch",
             on_click=_apply, args=(result, second, "clarification", on_update))
    return True


def teach_panel(result, key, on_update=None):
    """The 'Not quite right?' panel under a result."""
    if not games_allowed(result):
        return
    with st.expander("Not quite right? Teach ORBIT"):
        current = result["final"]["family"]
        st.html(f'<p class="body">ORBIT read this as <b>{esc(current)}</b>. Which feeling fits better? '
                "Your answer is saved only on this computer and helps ORBIT learn.</p>")
        options = [f for f in FAMILIES if f != current]
        choice = st.pills("A better fit", options, key=f"{key}_pick",
                          format_func=lambda f: f"{f} ({FAMILY_HELP[f]})")
        st.button("Teach ORBIT", key=f"{key}_teach", disabled=choice is None, type="primary",
                  on_click=_apply, args=(result, choice, "teach", on_update))

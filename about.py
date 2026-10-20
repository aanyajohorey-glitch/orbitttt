"""
about.py
About -> About ORBIT: what ORBIT is, the problem it addresses, how the AI
works, and its limits. Written to be read aloud in a viva.
"""
import streamlit as st

from components import note, section_header

SDGS = [
    ("SDG 3 · Good Health and Well-being", "Target 3.4 (mental health): emotional check-ins, coping tools and a "
                                            "safety net that points to real help."),
    ("SDG 4 · Quality Education", "Made for students and exam stress; builds emotional vocabulary and simple CBT "
                                  "skills."),
    ("SDG 10 · Reduced Inequalities", "Free, private, works offline, and understands Hinglish and Hindi."),
]

FLOW = [
    ("Check in", "Write or say how you feel, in English, Hinglish or Hindi."),
    ("Detect", "A pre-trained RoBERTa model scores 28 emotions; ORBIT's own trained classifier picks the main "
               "feeling and says how sure it is."),
    ("Protect", "Deterministic safety rules check every message first. Crisis messages get helplines only."),
    ("Reply", "The companion reflects and validates, and asks when it isn't sure."),
    ("Act", "One small evidence-based exercise: breathing, grounding, a thought reframe or gratitude."),
    ("Grow", "Your check-in becomes a planet in your galaxy; patterns appear over time."),
]


def about_page():
    section_header("About ORBIT", "Every feeling has a universe",
                   "ORBIT is an AI emotional-wellbeing companion for students, built as a Class 12 CBSE "
                   "Artificial Intelligence project.", first=True)
    st.html('<div class="principles">' + "".join(
        f'<div class="principle"><b>{title}</b><p class="body">{text}</p></div>' for title, text in SDGS) + "</div>")
    st.html('<div class="section-head"><div class="eyebrow">How a check-in works</div></div>'
            '<div class="pipeline">' + "".join(
                f'<div class="pipe-step"><span>{i:02d}</span><b>{name}</b><small>{text}</small></div>'
                for i, (name, text) in enumerate(FLOW, 1)) + "</div>")
    note("<b>What ORBIT is not:</b> a therapist, a doctor or a crisis service. It does not diagnose. It only "
         "reads what you type or say inside ORBIT, never other apps, searches or messages. For how well it works "
         "(and where it fails), see the AI Lab. For safety and your data, see Care & privacy.")

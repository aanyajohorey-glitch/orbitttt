"""
safety_plan.py
My safety plan: a short plan, written once while you feel okay, to use when
things feel hard. Based on the common structure of safety-planning templates
used by counsellors (warning signs, things that help, people, helplines).

It is stored ONLY on this device (in the settings table), is included in
Download my data, and is deleted by Panic wipe. ORBIT never shares it.
It can be opened from Feel -> Safety plan and from About -> Care & privacy.
"""
import json

import streamlit as st

import storage
from components import esc, note, section_header
from safety import HELPLINES, helplines_html

SECTIONS = [
    ("warning_signs", "My warning signs", "Thoughts, feelings or situations that tell me things are getting hard.",
     "e.g. I stop replying to friends, I can't sleep, I feel like hiding"),
    ("coping", "Things I can do on my own", "Small things that help me calm down or feel a bit better.",
     "e.g. go for a walk, the 4-6 breathing in ORBIT, listen to my calm playlist, have a shower"),
    ("places", "People and places that take my mind off things",
     "Somewhere or someone that helps, even without talking about it.",
     "e.g. my cousin's house, the park near school, the library"),
    ("people", "People I can ask for help", "Names and how to reach them. Stored only on this device.",
     "e.g. Mum: 98xxxxxx · Ms. Rao (school counsellor): room 12"),
    ("reasons", "Things that matter to me", "People, plans and small joys worth holding on to.",
     "e.g. my little sister, finishing my comic, the beach trip in December"),
]


def load_plan():
    try:
        return json.loads(storage.get_setting("safety_plan", "{}") or "{}")
    except json.JSONDecodeError:
        return {}


def save_plan():
    plan = {key: st.session_state.get(f"plan_{key}", "").strip() for key, *_ in SECTIONS}
    storage.set_setting("safety_plan", json.dumps(plan, ensure_ascii=False))
    st.session_state.plan_editing = False
    st.session_state.flash.append("Your safety plan is saved on this device.")


def plan_text(plan):
    lines = ["MY SAFETY PLAN (from ORBIT)", ""]
    for key, title, *_ in SECTIONS:
        lines += [title.upper(), plan.get(key) or "-", ""]
    lines.append("HELPLINES")
    lines += [f"{name}: {number}" for name, number, *_ in HELPLINES]
    return "\n".join(lines)


def show_plan(plan):
    st.html('<div class="plan">' + "".join(
        f'<div class="plan-step"><span>{i}</span><div><b>{esc(title)}</b>'
        f'<p class="body">{esc(plan.get(key) or "Not filled in yet")}</p></div></div>'
        for i, (key, title, *_) in enumerate(SECTIONS, 1))
        + '<div class="plan-step"><span>6</span><div><b>If I need help now</b>'
        + helplines_html() + "</div></div></div>")


def safety_plan_page():
    section_header("My safety plan", "A plan for hard moments",
                   "Fill this in while you feel okay, so it's ready when things feel hard. Keep it short and real. "
                   "It's private and stays on this device.", first=True)
    plan = load_plan()
    editing = st.session_state.get("plan_editing") or not any(plan.values())
    if editing:
        with st.container(key="glass-plan-edit"):
            for key, title, text, example in SECTIONS:
                st.text_area(f"{title}", value=plan.get(key, ""), key=f"plan_{key}", height=90,
                             help=text, placeholder=example)
            st.button("Save my plan", key="plan_save", type="primary", on_click=save_plan)
    else:
        with st.container(key="glass-plan-view"):
            show_plan(plan)
            a, b = st.columns(2)
            a.button("Edit my plan", key="plan_edit", on_click=lambda: st.session_state.update(plan_editing=True),
                     width="stretch")
            b.download_button("Download as text", plan_text(plan), file_name="my_safety_plan.txt",
                              mime="text/plain", width="stretch")
    note("A safety plan is a tool, not a treatment. Sharing it with a trusted adult or counsellor can make it "
         "stronger. In an emergency, call 112.")

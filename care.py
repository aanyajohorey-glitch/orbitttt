"""
care.py
The Care page: ORBIT's responsible-AI promises, helplines and privacy controls.

Principles shown here (and built into the code):
- Safety first   : crisis words trigger helplines before anything else (safety.py)
- Honesty        : ORBIT always says it is an AI and shows which reply style is used
- Privacy        : everything stays on this computer; the user can download or delete it
- Fairness       : limitations and bias are measured and shown in the AI Lab
- Not a therapist: ORBIT supports wellbeing and points to real people for real help
"""
import streamlit as st

import orbit_head
import storage
from components import go_to, note, section_header
from safety import helplines_html

PRINCIPLES = [
    ("Safety first", "If someone writes about suicide or self-harm, ORBIT stops and shows free helplines before "
                     "anything else. These messages are never sent to an AI model."),
    ("Always honest", "ORBIT never pretends to be a person. Every reply shows whether it came from hand-written "
                      "templates or a local AI model."),
    ("Private by design", "Your journal, sessions and saved worlds stay in a file on this computer. Nothing is "
                          "uploaded, and you can delete it all below."),
    ("Fair and measured", "The AI Lab shows how accurate the model is, including where it struggles (for example "
                          "Hinglish, sarcasm and very short messages)."),
    ("Not a therapist", "ORBIT can help you notice and name feelings and try coping exercises. For anything "
                        "serious, please talk to a trusted adult, a counsellor or a doctor."),
]


def save_name():
    storage.set_setting("name", st.session_state.care_name.strip())
    st.session_state.flash.append("Saved.")


def toggle_journal():
    storage.set_setting("journal_on", "1" if st.session_state.care_journal else "0")


def delete_corrections():
    storage.clear_corrections()
    if orbit_head.personal_model().exists():
        orbit_head.personal_model().unlink()
    st.session_state.flash.append("Teach Orbit corrections and your personal model were deleted.")


def delete_everything():
    storage.delete_everything()
    if orbit_head.personal_model().exists():
        orbit_head.personal_model().unlink()   # it was trained on your corrections
    st.session_state.collection = []
    st.session_state.chat = []
    st.session_state.flash.append("All ORBIT data on this computer has been deleted.")


def care_page():
    section_header(
        "Care",
        "How ORBIT looks after you",
        "The promises built into ORBIT, where to find real help, and full control over your data.",
        first=True,
    )
    st.html('<div class="principles">' + "".join(
        f'<div class="principle"><b>{title}</b><p class="body">{text}</p></div>' for title, text in PRINCIPLES
    ) + "</div>")

    with st.container(key="glass-care-plan"):
        left, right = st.columns([2.2, 1], vertical_alignment="center")
        left.html('<div class="eyebrow">My safety plan</div><p class="body">Your own plan for hard moments: warning '
                  "signs, what helps, and who to call. Private, on this device.</p>")
        right.button("Open my safety plan", key="care_plan", type="primary", on_click=go_to,
                     args=("Safety plan",), width="stretch")

    with st.container(key="glass-help"):
        st.html('<div class="eyebrow">Real people who can help, any time</div>'
                '<p class="body" style="margin:.3rem 0 .6rem">Free and confidential in India:</p>'
                + helplines_html())

    with st.container(key="glass-privacy"):
        st.html('<div class="eyebrow">Your data</div>')
        st.text_input("What should ORBIT call you? (optional)", value=storage.get_setting("name", ""),
                      key="care_name", on_change=save_name, max_chars=30)
        st.toggle("Keep a private journal of my check-ins on this computer", value=storage.journal_enabled(),
                  key="care_journal", on_change=toggle_journal)
        counts = (len(storage.list_entries()), len(storage.list_collection()), len(storage.list_wellbeing()),
                  len(storage.list_feedback()), len(storage.list_corrections()), len(storage.list_ratings()))
        st.html(f'<p class="body">Stored on this computer: {counts[0]} journal entries, {counts[1]} saved worlds, '
                f"{counts[2]} calm sessions, {counts[3]} feedback responses, {counts[4]} Teach Orbit corrections, "
                f"{counts[5]} thumbs ratings. "
                "Crisis messages are never stored.</p>")
        st.button("Delete my Teach Orbit corrections", key="care_del_corrections", type="tertiary",
                  disabled=counts[4] == 0 and not orbit_head.personal_model().exists(), on_click=delete_corrections)
        sure = st.checkbox("I understand this permanently deletes all of my ORBIT data", key="care_sure")
        st.button("Delete all my data", key="care_delete", on_click=delete_everything, disabled=not sure)
        st.html('<p class="body">To download or import your data, see <b>Settings</b>. In a hurry? The '
                "<b>Panic wipe</b> button at the top of every page deletes everything at once, no questions asked.</p>")
    note("ORBIT is a Class 12 student project. It is not a medical device and does not give diagnoses.")

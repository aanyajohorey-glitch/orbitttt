"""
letters.py
Feel -> Letters: two expressive-writing tools.

1. A letter you'll never send: write to someone (or something), then let it go
   with a small ritual: burn it or let it float away. Nothing is saved unless
   you tick "Keep it, privately, on this device".
2. A letter to future me: it stays sealed for 30 days. When it opens, ORBIT
   shows it next to what you were feeling when you wrote it.

Safety: crisis wording in a letter shows only the safety response, and the
letter is not kept.
"""
import json
from datetime import date, datetime, timedelta

import streamlit as st

import storage
from components import esc, note, section_header
from emotion_model import GROUP_OF
from feedback_ui import thumbs
from onboarding import reduced_motion
from safety import check as safety_check
from safety import safety_card_html

SEALED_DAYS = 30
FEELINGS = ["Hopeful", "Calm", "Happy", "Proud", "Worried", "Stressed", "Sad", "Lonely", "Angry", "Mixed"]


def let_go(ritual):
    text = st.session_state.get("unsent_text", "").strip()
    if not text:
        st.session_state.letter_message = "Write something first. Even one line is enough."
        return
    if safety_check(text) == "crisis":
        st.session_state.letter_crisis = True
        st.session_state.unsent_text = ""
        return
    if st.session_state.get("unsent_keep"):
        storage.add_note("unsent_letter", st.session_state.get("unsent_to", "") or "Unsent letter", text)
    st.session_state.letter_ritual = {"kind": ritual, "text": text}
    st.session_state.unsent_text = ""


def ritual_html(kind, text):
    """The letter burning or floating away (a fade only, if motion is reduced)."""
    preview = esc(text[:420] + ("…" if len(text) > 420 else ""))
    css_class = "fade" if reduced_motion() else kind
    words = {"burn": "Let it burn. It doesn't have to stay with you.",
             "float": "Let it float away. You can breathe out now."}[kind]
    return (f'<div class="ritual"><div class="ritual-paper {css_class}">{preview}</div>'
            f'<p class="ritual-words">{words}</p></div>')


def unsent_section():
    if st.session_state.pop("letter_crisis", False):
        st.html(safety_card_html("crisis"))
        return
    ritual = st.session_state.pop("letter_ritual", None)
    if ritual:
        st.html(ritual_html(ritual["kind"], ritual["text"]))
        thumbs("tool", "Unsent letter", key="fb_unsent", label="Did that help a little?")
        return
    with st.container(key="glass-unsent"):
        st.text_input("Who is it to? (optional, only you will see it)", key="unsent_to", max_chars=40,
                      placeholder="e.g. my old friend, my exams, my younger self")
        st.text_area("Write everything you wish you could say", key="unsent_text", height=200,
                     placeholder="Dear …")
        st.checkbox("Keep it, privately, on this device", key="unsent_keep",
                    help="Off by default: the letter disappears after the ritual.")
        a, b = st.columns(2)
        a.button("Burn it", key="letter_burn", on_click=let_go, args=("burn",), type="primary", width="stretch")
        b.button("Let it float away", key="letter_float", on_click=let_go, args=("float",), width="stretch")
    message = st.session_state.pop("letter_message", None)
    if message:
        st.info(message)
    kept = storage.list_notes("unsent_letter")
    if kept:
        with st.expander(f"Letters you kept ({len(kept)})"):
            for item in kept:
                left, right = st.columns([6, 1], vertical_alignment="center")
                left.html(f'<div class="eyebrow">{esc(item["title"])} · {esc(item["created_at"][:10])}</div>'
                          f'<p class="body">{esc(item["text"])}</p>')
                right.button("Delete", key=f"del_unsent_{item['id']}", type="tertiary",
                             on_click=storage.delete_note, args=(item["id"],))


def feeling_now():
    """What the writer feels right now: their choice, or else their last (non-crisis) check-in."""
    chosen = st.session_state.get("future_feeling")
    if chosen:
        return chosen
    last = st.session_state.get("home_result")
    if last and last.get("safety") != "crisis":
        return f"{GROUP_OF.get(last['final']['emotion'], 'Neutral')} (from your check-in)"
    return "not recorded"


def seal():
    text = st.session_state.get("future_text", "").strip()
    if not text:
        st.session_state.letter_message = "Write something to your future self first."
        return
    if safety_check(text) == "crisis":
        st.session_state.letter_crisis = True
        st.session_state.future_text = ""
        return
    opens = (date.today() + timedelta(days=SEALED_DAYS)).isoformat()
    storage.add_note("future_letter", opens, json.dumps({"letter": text, "feeling": feeling_now()}))
    st.session_state.future_text = ""
    st.session_state.flash.append(f"Sealed until {opens}. It's saved only on this device.")


def is_open(item, today=None):
    return (today or date.today()).isoformat() >= item["title"]


def future_section():
    if st.session_state.pop("letter_crisis", False):
        st.html(safety_card_html("crisis"))
        return
    with st.container(key="glass-future"):
        st.text_area("Dear future me…", key="future_text", height=180,
                     placeholder="What are you hoping for? What do you want to remember about right now?")
        st.pills("How are you feeling as you write? (optional)", FEELINGS, key="future_feeling")
        st.button(f"Seal it for {SEALED_DAYS} days", key="letter_seal", on_click=seal, type="primary")
    message = st.session_state.pop("letter_message", None)
    if message:
        st.info(message)
    letters = storage.list_notes("future_letter")
    opened = [l for l in letters if is_open(l)]
    sealed = [l for l in letters if not is_open(l)]
    for item in opened:
        data = json.loads(item["text"])
        with st.container(key=f"glass-opened-{item['id']}"):
            st.html(f'<div class="eyebrow">Opened · written {esc(item["created_at"][:10])}</div>'
                    f'<p class="letter-text">{esc(data["letter"])}</p>'
                    f'<p class="body">When you wrote this, you were feeling: <b>{esc(data["feeling"])}</b>. '
                    "How does it feel to read it now?</p>")
            st.button("Delete", key=f"del_future_{item['id']}", type="tertiary", on_click=storage.delete_note,
                      args=(item["id"],))
    if sealed:
        st.html('<div class="sealed-row">' + "".join(
            f'<div class="sealed"><b>✉</b><span>Opens {esc(datetime.fromisoformat(s["title"]).strftime("%d %b %Y"))}'
            "</span></div>" for s in sealed) + "</div>")


def letters_page():
    section_header("Letters", "Words that need somewhere to go",
                   "Writing things down can make feelings a little lighter. Write to someone you can't talk to, or "
                   "to yourself in a month.", first=True)
    part = st.segmented_control("Letter", ["A letter you'll never send", "A letter to future me"],
                                default="A letter you'll never send", key="letters_part",
                                label_visibility="collapsed")
    if part == "A letter to future me":
        future_section()
    else:
        unsent_section()
    note("Letters stay on this device and are included in Download my data (Settings, top right).")

"""
reach_out.py
Reach Out Helper: for when it's hard to put feelings into words for a real person.

The user picks WHO to write to (a friend, a parent, a teacher) and HOW MUCH to
share. ORBIT drafts 3 short messages from fixed templates (no AI), in English,
Hinglish or Hindi, matching how the user writes. The user edits, copies and
sends the message THEMSELVES. ORBIT never sends anything, and a draft is only
kept if the user presses "Save on this device".

Safety: if the last check-in was a crisis, this page shows only the helplines.
If distress is intense or keeps repeating, Tele-MANAS and a trusted adult are
suggested too. This tool helps people talk to people; it is never a replacement
for professional help.
"""
import hashlib

import streamlit as st

import storage
from components import esc, note, section_header
from feedback_ui import thumbs
from hinglish import to_english
from safety import check as safety_check
from safety import helplines_html, safety_card_html

WHO = {"friend": "A friend", "parent": "A parent or family member", "teacher": "A teacher or counsellor"}
LEVELS = {
    "hard": "Just \"I'm having a hard time\"",
    "little": "A little detail (how I feel)",
    "more": "More detail (what it's about)",
}
LANGUAGES = ["English", "Hinglish", "Hindi"]
DISTRESS_FAMILIES = {"Sadness", "Fear", "Anger"}

# How each feeling family is said in each language (simple, everyday words).
FEELING = {
    "English": {"Sadness": "really low", "Fear": "really anxious and stressed", "Anger": "really angry and frustrated",
                None: "a bit off"},
    "Hinglish": {"Sadness": "bahut low", "Fear": "bahut anxious aur stressed", "Anger": "bahut gussa aur frustrated",
                 None: "theek nahi"},
    "Hindi": {"Sadness": "मेरा मन बहुत उदास है", "Fear": "मुझे बहुत घबराहट और तनाव हो रहा है",
              "Anger": "मुझे बहुत गुस्सा और चिढ़ हो रही है", None: "मेरा मन ठीक नहीं है"},
}

# {f} = the feeling, {c} = what it's about. Three versions for each choice.
TEMPLATES = {
    "English": {
        "friend": {
            "hard": ["Hey, I'm having a hard time right now. Could we talk sometime today?",
                     "Hi, I'm not doing great lately. Are you free to chat or hang out for a bit?",
                     "Hey, can I talk to you? Things feel like a lot right now."],
            "little": ["Hey, I've been feeling {f} lately. Could we talk sometime today?",
                       "Hi, honestly I've been feeling {f}. Would you be free for a call?",
                       "Hey, I'm feeling {f} and could use a friend. Can we talk?"],
            "more": ["Hey, I've been feeling {f}, mostly because of {c}. Could we talk about it?",
                     "Hi, can I share something? I've been feeling {f} about {c}, and it's been hard.",
                     "Hey, I keep thinking about {c} and I'm feeling {f}. Do you have some time to talk?"],
        },
        "parent": {
            "hard": ["Hi, I'm having a hard time lately. Can we talk tonight?",
                     "I wanted to tell you that I'm not doing very well. Can we sit together for a bit?",
                     "Can I talk to you about something? I've been finding things hard."],
            "little": ["Hi, I've been feeling {f} lately and I wanted you to know. Can we talk?",
                       "I've been feeling {f} for a while. Can we talk tonight?",
                       "I don't really know how to say this, but I've been feeling {f}. Can we talk?"],
            "more": ["I've been feeling {f}, mostly because of {c}. Can we talk about it tonight?",
                     "Can we talk? I've been worried about {c} and I'm feeling {f}.",
                     "I wanted to tell you that I'm feeling {f} about {c}. I'd like your help."],
        },
        "teacher": {
            "hard": ["Hello, I've been finding things hard lately. Could I speak to you for a few minutes?",
                     "Good morning. I'm having a difficult time at the moment. Could we talk sometime this week?",
                     "Hello, may I talk to you privately for a few minutes? I'm not doing very well."],
            "little": ["Hello, I've been feeling {f} lately. Could I speak to you for a few minutes?",
                       "Good morning. I've been feeling {f} and I'd like some advice. When would be a good time?",
                       "Hello, I've been feeling {f}. Would it be possible to talk this week?"],
            "more": ["Hello, I've been feeling {f}, mostly because of {c}. Could I speak to you about it?",
                     "Good morning. I've been struggling with {c} and I'm feeling {f}. Could we talk?",
                     "Hello, I'd like some help with {c}. I've been feeling {f}. When could we talk?"],
        },
    },
    "Hinglish": {
        "friend": {
            "hard": ["Hey, abhi thoda tough time chal raha hai. Aaj baat kar sakte hain?",
                     "Yaar, main theek nahi hoon aajkal. Thodi der baat karein?",
                     "Hey, kya main tujhse baat kar sakta/sakti hoon? Sab bahut zyada lag raha hai."],
            "little": ["Hey, aajkal main {f} feel kar raha/rahi hoon. Aaj baat karein?",
                       "Yaar, sach bolun toh main {f} feel kar raha/rahi hoon. Call kar sakte hain?",
                       "Hey, main {f} hoon aur ek dost ki zaroorat hai. Baat karein?"],
            "more": ["Hey, {c} ki wajah se main {f} feel kar raha/rahi hoon. Iske baare mein baat karein?",
                     "Yaar, ek baat share karni hai. {c} ko leke main {f} hoon, mushkil ho raha hai.",
                     "Hey, {c} ko leke bahut soch raha/rahi hoon aur main {f} hoon. Thoda time hai baat karne ka?"],
        },
        "parent": {
            "hard": ["Mumma/Papa, aajkal mera time thoda mushkil chal raha hai. Aaj raat baat kar sakte hain?",
                     "Mujhe aapko batana tha ki main theek nahi hoon. Thodi der saath baith sakte hain?",
                     "Kya main aapse kuch baat kar sakta/sakti hoon? Sab thoda mushkil lag raha hai."],
            "little": ["Mumma/Papa, aajkal main {f} feel kar raha/rahi hoon. Baat kar sakte hain?",
                       "Kuch dino se main {f} feel kar raha/rahi hoon. Aaj raat baat karein?",
                       "Samajh nahi aa raha kaise bolun, par main {f} feel kar raha/rahi hoon. Baat karein?"],
            "more": ["{c} ki wajah se main {f} feel kar raha/rahi hoon. Aaj raat iske baare mein baat karein?",
                     "Baat kar sakte hain? {c} ki tension hai aur main {f} feel kar raha/rahi hoon.",
                     "Aapko batana tha ki {c} ko leke main {f} hoon. Mujhe aapki help chahiye."],
        },
        "teacher": {
            "hard": ["Good morning Ma'am/Sir, aajkal mujhe thoda mushkil lag raha hai. Kya main aapse thodi der baat kar sakta/sakti hoon?",
                     "Ma'am/Sir, mera time abhi thoda difficult chal raha hai. Is hafte baat ho sakti hai?",
                     "Ma'am/Sir, kya main aapse akele mein thodi der baat kar sakta/sakti hoon?"],
            "little": ["Good morning Ma'am/Sir, aajkal main {f} feel kar raha/rahi hoon. Kya thodi der baat ho sakti hai?",
                       "Ma'am/Sir, main {f} feel kar raha/rahi hoon aur aapki advice chahiye. Kab baat ho sakti hai?",
                       "Ma'am/Sir, main {f} hoon. Is hafte baat karna possible hai?"],
            "more": ["Ma'am/Sir, {c} ki wajah se main {f} feel kar raha/rahi hoon. Kya iske baare mein baat ho sakti hai?",
                     "Good morning Ma'am/Sir, {c} ko leke mujhe mushkil ho rahi hai aur main {f} hoon. Baat kar sakte hain?",
                     "Ma'am/Sir, mujhe {c} mein help chahiye. Main {f} feel kar raha/rahi hoon. Kab baat ho sakti hai?"],
        },
    },
    "Hindi": {
        "friend": {
            "hard": ["अरे, अभी मेरा समय थोड़ा मुश्किल चल रहा है। क्या आज बात कर सकते हैं?",
                     "यार, आजकल मन ठीक नहीं है। थोड़ी देर बात करें?",
                     "क्या मैं तुमसे बात कर सकता/सकती हूँ? सब कुछ बहुत भारी लग रहा है।"],
            "little": ["अरे, आजकल {f}। क्या आज बात कर सकते हैं?",
                       "सच कहूँ तो {f}। क्या फ़ोन पर बात हो सकती है?",
                       "{f}, और मुझे एक दोस्त की ज़रूरत है। बात करें?"],
            "more": ["{c} की वजह से {f}। क्या इसके बारे में बात कर सकते हैं?",
                     "एक बात बतानी है। {c} को लेकर {f}, और यह मुश्किल हो रहा है।",
                     "{c} के बारे में सोचकर {f}। क्या तुम्हारे पास बात करने का थोड़ा समय है?"],
        },
        "parent": {
            "hard": ["मम्मी/पापा, आजकल मेरा समय थोड़ा मुश्किल चल रहा है। क्या आज रात बात कर सकते हैं?",
                     "मुझे आपको बताना था कि मैं ठीक महसूस नहीं कर रहा/रही। क्या थोड़ी देर साथ बैठ सकते हैं?",
                     "क्या मैं आपसे कुछ बात कर सकता/सकती हूँ? सब थोड़ा मुश्किल लग रहा है।"],
            "little": ["मम्मी/पापा, आजकल {f}। मैं चाहता/चाहती हूँ कि आपको पता हो। क्या बात कर सकते हैं?",
                       "कुछ दिनों से {f}। क्या आज रात बात करें?",
                       "समझ नहीं आ रहा कैसे कहूँ, पर {f}। क्या हम बात कर सकते हैं?"],
            "more": ["{c} की वजह से {f}। क्या आज रात इसके बारे में बात कर सकते हैं?",
                     "क्या हम बात कर सकते हैं? {c} की चिंता है और {f}।",
                     "आपको बताना था कि {c} को लेकर {f}। मुझे आपकी मदद चाहिए।"],
        },
        "teacher": {
            "hard": ["नमस्ते मैम/सर, आजकल मुझे चीज़ें मुश्किल लग रही हैं। क्या मैं आपसे कुछ मिनट बात कर सकता/सकती हूँ?",
                     "मैम/सर, अभी मेरा समय थोड़ा कठिन चल रहा है। क्या इस हफ़्ते बात हो सकती है?",
                     "मैम/सर, क्या मैं आपसे अकेले में कुछ मिनट बात कर सकता/सकती हूँ?"],
            "little": ["नमस्ते मैम/सर, आजकल {f}। क्या कुछ मिनट बात हो सकती है?",
                       "मैम/सर, {f} और मुझे आपकी सलाह चाहिए। कब बात करना ठीक रहेगा?",
                       "मैम/सर, {f}। क्या इस हफ़्ते बात करना संभव है?"],
            "more": ["मैम/सर, {c} की वजह से {f}। क्या इसके बारे में बात हो सकती है?",
                     "नमस्ते मैम/सर, {c} को लेकर मुझे मुश्किल हो रही है और {f}। क्या हम बात कर सकते हैं?",
                     "मैम/सर, मुझे {c} में मदद चाहिए। {f}। कब बात हो सकती है?"],
        },
    },
}
# "What it's about" when the user leaves it empty
SOMETHING = {"English": "a few things", "Hinglish": "kuch cheezon", "Hindi": "कुछ बातों"}


# ---------------------------------------------------------------
# The method (no AI: fixed templates, so it's predictable and safe)
# ---------------------------------------------------------------
def detect_language(text):
    """Hindi if the text uses Devanagari letters, Hinglish if ORBIT's dictionary
    found Hinglish words, otherwise English."""
    if any("ऀ" <= ch <= "ॿ" for ch in text or ""):
        return "Hindi"
    if text and to_english(text)[1]:
        return "Hinglish"
    return "English"


def drafts(who, level, family=None, language="English", context=""):
    """Three short drafts. family: Sadness/Fear/Anger (or None); context: what it's about."""
    feeling = FEELING[language].get(family if family in DISTRESS_FAMILIES else None)
    about = context.strip().rstrip(".") or SOMETHING[language]
    texts = [t.format(f=feeling, c=about) for t in TEMPLATES[language][who][level]]
    return [t[0].upper() + t[1:] if t[:1].isalpha() else t for t in texts]


def needs_extra_care(result):
    """Intense (a "concern" message) or repeated low moods: also point to Tele-MANAS."""
    from nudges import low_mood_count   # local import keeps this module light
    return bool(result and result.get("safety") == "concern") or low_mood_count() >= 3


# ---------------------------------------------------------------
# Offer in Today (after a distress-type feeling)
# ---------------------------------------------------------------
def open_helper(result):
    st.session_state.ro_family = result["final"]["family"]
    st.session_state.ro_language = detect_language(result["text"])
    st.session_state.page = "Reach Out"


def offer_card(result):
    """A small card in Today. Never shown in a crisis (the safety flow handles that)."""
    if not result or result.get("safety") == "crisis" or result["final"]["family"] not in DISTRESS_FAMILIES:
        return
    with st.container(key="glass-reach-offer"):
        left, right = st.columns([2.2, 1], vertical_alignment="center")
        left.html('<div class="eyebrow">Reach Out Helper</div><p class="body">Finding it hard to tell someone how '
                  "you feel? ORBIT can help you write a short message. You decide if and when to send it.</p>")
        right.button("Help me write it", key="ro_open", on_click=open_helper, args=(result,), width="stretch")
        if needs_extra_care(result):
            st.html('<p class="body" style="margin-top:.4rem">If it feels like too much, please also talk to a '
                    "trusted adult, or call <b>Tele-MANAS 14416</b> (free, any time).</p>")


# ---------------------------------------------------------------
# The page (Feel -> Reach Out)
# ---------------------------------------------------------------
def save_draft(who, key):
    text = st.session_state.get(key, "").strip()
    if text and safety_check(text) != "crisis":
        storage.add_note("reach_out", WHO[who], text)
        st.session_state.flash.append("Saved on this device only.")


def reach_out_page():
    section_header("Reach Out Helper", "Say it to a real person",
                   "Pick who you'd like to talk to and how much to share. ORBIT drafts a few short messages. "
                   "You edit, copy and send it yourself. ORBIT never sends anything.", first=True)
    last = st.session_state.get("home_result")
    if last and last.get("safety") == "crisis":
        st.html(safety_card_html("crisis"))      # in a crisis: help only, no drafts
        return
    if needs_extra_care(last):
        with st.container(key="glass-ro-care"):
            st.html('<div class="eyebrow">You deserve real support</div><p class="body">A message to a friend is a '
                    "great step, and it's okay to ask for more help too. Please talk to a trusted adult, or call "
                    "a free, confidential helpline:</p>" + helplines_html())

    with st.container(key="glass-ro-form"):
        who = st.pills("Who would you like to write to?", list(WHO), format_func=WHO.get, key="ro_who") or "friend"
        level = st.radio("How much do you want to share?", list(LEVELS), format_func=LEVELS.get, key="ro_level",
                         horizontal=True)
        left, right = st.columns([1, 1.6])
        default_language = st.session_state.get("ro_language", "English")
        language = left.selectbox("Language", LANGUAGES, index=LANGUAGES.index(default_language), key="ro_lang")
        context = ""
        if level == "more":
            context = right.text_input("What's it about? (a few words, optional)", key="ro_context", max_chars=60,
                                       placeholder="e.g. my board exams")
        if context and safety_check(context) == "crisis":
            st.html(safety_card_html("crisis"))   # never draft around crisis words, and nothing is kept
            return
        family = st.session_state.get("ro_family")
        if family in DISTRESS_FAMILIES:
            st.html(f'<p class="body">Using the feeling from your last check-in: <b>{esc(family)}</b>.</p>')

    versions = drafts(who, level, family, language, context)
    signature = hashlib.md5(f"{who}|{level}|{family}|{language}|{context}".encode()).hexdigest()[:8]
    for i, text in enumerate(versions):
        with st.container(key=f"glass-ro-draft-{i}"):
            st.html(f'<div class="eyebrow">Version {i + 1}</div>')
            key = f"ro_text_{signature}_{i}"
            edited = st.text_area("Edit it so it sounds like you", value=text, key=key, height=90,
                                  label_visibility="collapsed")
            st.code(edited, language=None, wrap_lines=True)    # the copy button is at the top right
            st.button("Save on this device", key=f"ro_save_{signature}_{i}", type="tertiary",
                      on_click=save_draft, args=(who, key))
    note("To send it: copy a version (top-right icon in the grey box), then paste it into WhatsApp, SMS or email "
         "yourself. Nothing is sent or saved unless you choose to.")
    thumbs("reach_out", WHO[who], key="fb_reach_out", label="Were these drafts helpful?")

    saved = storage.list_notes("reach_out")
    if saved:
        with st.expander(f"Saved drafts on this device ({len(saved)})"):
            for item in saved:
                text_col, action = st.columns([6, 1], vertical_alignment="center")
                text_col.html(f'<div class="eyebrow">{esc(item["title"])} · {esc(item["created_at"][:10])}</div>'
                              f'<p class="body">{esc(item["text"])}</p>')
                action.button("Delete", key=f"ro_del_{item['id']}", type="tertiary",
                              on_click=storage.delete_note, args=(item["id"],))

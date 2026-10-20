"""
companion.py
ORBIT's companion: replies that make the user feel heard.

How a reply is written (the same steps a good listener uses):
  1. Reflect   - name the feeling in plain words ("you sound proud but nervous")
  2. Validate  - say that the feeling makes sense
  3. Remember  - notice patterns from the journal ("third time this week")
  4. Ask       - one gentle, open question
  5. Offer     - a small coping tool that fits the feeling

Two reply styles:
  - "ORBIT templates": hand-written sentences chosen by the detected emotions.
    Works everywhere, offline, and every sentence can be explained.
  - "Local AI": if Ollama (a free program that runs AI models on your own
    computer) is installed and running, a small language model writes the
    reply instead, guided by the detected emotions.

ORBIT always says it is an AI. Crisis messages are NEVER sent to the AI:
they get a fixed, safe reply with helplines (see safety.py).
"""
import json
import os
import random
import urllib.request
import zlib
from datetime import datetime, timedelta

import streamlit as st

import storage
from analysis import analyse, earn_token, games_allowed, may_store
from components import esc, go_to, section_header, note, tags_html
from emotion_model import FEELING_WORDS, GROUP_OF
from safety import safety_card_html
from teach_ui import clarify, confidence_html, teach_panel

OLLAMA_URL = os.environ.get("ORBIT_OLLAMA_URL", "http://localhost:11434")
PREFERRED_MODEL = os.environ.get("ORBIT_LLM", "llama3.2:3b")

# ---------------------------------------------------------------
# Hand-written reply pieces, one set per emotion family
# ---------------------------------------------------------------
OPENERS = {
    "Joy": ["I can feel the light in that.", "That sounds genuinely good.", "I'm really glad you shared this."],
    "Warmth": ["That's a tender thing to feel.", "There's a lot of heart in what you wrote.", "That's really warm."],
    "Sadness": ["That sounds really heavy.", "I'm sorry it hurts like this.",
                "Thank you for telling me. That can't be easy to carry."],
    "Fear": ["That sounds like a lot of pressure.", "It makes sense that your mind is racing.",
             "That kind of worry can be exhausting."],
    "Anger": ["That sounds really frustrating.", "It's okay to be angry about that.",
              "Anyone would feel worked up after that."],
    "Wonder": ["Your mind sounds wide awake.", "That's a lot to think through.", "I like where your thoughts are going."],
    "Neutral": ["I'm here and listening.", "Thanks for checking in.", "Some moments are quiet ones, and that's okay."],
}
VALIDATIONS = {
    "Joy": "Let yourself enjoy it. Good moments deserve to be noticed.",
    "Warmth": "Feelings like that are what connect us to people.",
    "Sadness": "You don't have to fix this feeling right away. It's allowed to be here.",
    "Fear": "Feeling nervous usually means something matters to you.",
    "Anger": "Anger often shows up when something feels unfair or a line has been crossed.",
    "Wonder": "Not having all the answers yet is part of figuring things out.",
    "Neutral": "Not every day needs a big feeling.",
}
QUESTIONS = {
    "Joy": ["What made today feel this way?", "Who would you like to share this with?"],
    "Warmth": ["Who or what is on your mind?", "What would you like them to know?"],
    "Sadness": ["Do you want to tell me a little more about what happened?",
                "What would feel comforting right now, even a little?"],
    "Fear": ["What's the part that worries you most?", "What's one small thing that's within your control?"],
    "Anger": ["What do you wish had gone differently?", "What do you need right now: space, or to be heard?"],
    "Wonder": ["What's the question you keep coming back to?", "What would help you make sense of it?"],
    "Neutral": ["How has your day been, honestly?", "Is there anything sitting at the back of your mind?"],
}
# Which Calm Room tool fits each family, and how to offer it
SUGGESTIONS = {
    "Joy": ("Gratitude Jar", "Want to keep this moment safe in your gratitude jar?"),
    "Warmth": ("Gratitude Jar", "You could add this to your gratitude jar so you can come back to it."),
    "Sadness": ("Breathing", "If it helps, we could slow down together with a gentle breathing exercise."),
    "Fear": ("Breathing", "A minute of slow breathing can calm a racing mind. Want to try?"),
    "Anger": ("Grounding", "Grounding with your five senses can take the heat down a little."),
    "Wonder": ("Thought Reframe", "Writing the thought down and looking at it from another side might help."),
    "Neutral": ("Grounding", "A quick five-senses check-in can help you notice how you really feel."),
}
PATTERN_WORDS = {
    "Joy": "something good", "Warmth": "warm feelings", "Sadness": "feeling low", "Fear": "worry",
    "Anger": "frustration", "Wonder": "big questions", "Neutral": "a quiet mood",
}
# Short describing words for a second feeling ("…and a little nervous too")
SECOND_WORDS = {
    "admiration": "admiring", "amusement": "amused", "anger": "angry", "annoyance": "annoyed",
    "approval": "settled", "caring": "caring", "confusion": "confused", "curiosity": "curious",
    "desire": "wistful", "disappointment": "disappointed", "disapproval": "let down", "disgust": "put off",
    "embarrassment": "embarrassed", "excitement": "excited", "fear": "scared", "gratitude": "grateful",
    "grief": "heartbroken", "joy": "happy", "love": "loving", "nervousness": "nervous", "optimism": "hopeful",
    "pride": "proud", "realization": "clearer", "relief": "relieved", "remorse": "regretful", "sadness": "sad",
    "surprise": "surprised",
}
CRISIS_REPLY = (
    "I'm really glad you told me, and I'm taking what you said seriously. You deserve support from a real "
    "person right now. Please call Tele-MANAS on 14416 (free, 24/7) or tell someone you trust today. "
    "If you're in immediate danger, call 112. I'm still here if you want to keep writing."
)


def ordinal(n):
    return {2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(n, f"{n}th")


def family(result):
    """ORBIT's final emotion family (decided by the trained classifier)."""
    return result["final"]["family"]


def secondary_feeling(result):
    """A second feeling from a DIFFERENT family, if it is clearly present."""
    primary_group = family(result)
    for label, score in result["emotions"]:
        if score < 0.12:
            break
        if label != "neutral" and GROUP_OF[label] != primary_group:
            return label
    return None


# How to describe a family when ORBIT asks a clarifying question
FAMILY_PHRASES = {
    "Joy": "something good", "Warmth": "a warm, caring feeling", "Sadness": "feeling low",
    "Fear": "worry or nerves", "Anger": "frustration", "Wonder": "confusion or curiosity",
    "Neutral": "a fairly ordinary moment",
}


def clarifying_reply(result, name=""):
    """When ORBIT isn't sure, it asks instead of asserting a feeling."""
    (first, _), (second, _) = result["final"]["alternatives"][:2]
    hello = f"{name}, thank you for sharing that." if name else "Thank you for sharing that."
    return (f"{hello} I want to make sure I understand you properly. It could be "
            f"{FAMILY_PHRASES[first]}, or maybe {FAMILY_PHRASES[second]}. Which feels closer? "
            "You can also tell me a bit more.")


def recent_family_count(group, days=7):
    """How many journal check-ins in the last week had this family as the main feeling."""
    since = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
    return sum(
        1 for entry in storage.list_entries()
        if entry["created_at"] >= since and GROUP_OF.get(entry["primary_emotion"]) == group
    )


def suggestion(result):
    """The Calm Room tool to offer. A worried feeling underneath a happy one
    (e.g. excited but nervous) gets the tool for the worry."""
    alternatives = result["final"].get("alternatives", [])
    if len(alternatives) > 1:
        second, probability = alternatives[1]
        if family(result) in ("Joy", "Warmth", "Wonder", "Neutral") and \
                second in ("Sadness", "Fear", "Anger") and probability >= 0.25:
            return SUGGESTIONS[second]
    other = secondary_feeling(result)
    if other and family(result) in ("Joy", "Warmth", "Wonder", "Neutral") and \
            GROUP_OF[other] in ("Sadness", "Fear", "Anger"):
        return SUGGESTIONS[GROUP_OF[other]]
    return SUGGESTIONS[family(result)]


def template_reply(result, name=""):
    if result["final"].get("unsure"):
        return clarifying_reply(result, name)
    group = family(result)
    primary = result["final"]["emotion"]
    rng = random.Random(zlib.crc32(result["text"].encode("utf-8")))  # same text -> same reply

    opener = rng.choice(OPENERS[group])
    if name and rng.random() < 0.6:
        keep_capital = opener.startswith(("I ", "I'm"))
        opener = f"{name}, {opener if keep_capital else opener[0].lower() + opener[1:]}"

    if primary == "neutral":
        reflection = "It sounds like a fairly steady moment, or maybe one that's hard to put into words."
    else:
        reflection = f"It sounds like you're feeling {FEELING_WORDS[primary]}"
        other = secondary_feeling(result)
        reflection += (f", and a little {SECOND_WORDS[other]} too. Both can be true at once."
                       if other else ".")

    parts = [opener, reflection, VALIDATIONS[group]]
    seen = recent_family_count(group)
    if seen >= 2:
        parts.append(f"This is the {ordinal(seen + 1)} time this week {PATTERN_WORDS[group]} has come up. "
                     "I'm keeping that in mind with you.")
    parts.append(rng.choice(QUESTIONS[group]))
    return " ".join(parts)


# ---------------------------------------------------------------
# Optional local AI (Ollama)
# ---------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def local_ai_model():
    """The name of a local Ollama model if one is running, otherwise None."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=0.6) as response:
            models = [m["name"] for m in json.load(response).get("models", [])]
    except Exception:
        return None
    if PREFERRED_MODEL in models:
        return PREFERRED_MODEL
    return models[0] if models else None


def llm_reply(model, result, history, name):
    top = ", ".join(f"{label} {score:.0%}" for label, score in result["emotions"][:4])
    top += (f". ORBIT's classifier reads the main feeling as {result['final']['family']} "
            f"({result['final']['confidence']:.0%} confident)")
    if result["final"].get("unsure"):
        top += "; it is NOT sure, so gently ask which feeling is closer instead of assuming"
    system = (
        "You are ORBIT, a warm, gentle emotional-support companion in a student wellbeing app. "
        "You are an AI, not a human, and you never pretend to be one. Reply in 2 to 4 short sentences. "
        "Reflect the user's feelings in your own words, validate them, and ask at most one gentle, open question. "
        "Do not diagnose, give medical advice or lecture. If the user seems to be struggling a lot, gently "
        "encourage them to talk to a trusted adult or call Tele-MANAS on 14416. "
        f"An emotion model detected these feelings in their latest message: {top}."
        + (f" The user's name is {name}." if name else "")
    )
    messages = [{"role": "system", "content": system}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history[-8:]]
    body = json.dumps({"model": model, "messages": messages, "stream": False,
                       "options": {"temperature": 0.7}}).encode("utf-8")
    request = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=body,
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)["message"]["content"].strip()


def reply(result, history=(), name=""):
    """Return (reply_text, style) for an analysed message."""
    if result["safety"] == "crisis":
        return CRISIS_REPLY, "Safety reply"
    model = local_ai_model()
    if model:
        try:
            return llm_reply(model, result, list(history), name), f"Local AI · {model}"
        except Exception:
            pass  # fall back to templates if the local AI fails
    return template_reply(result, name), "ORBIT templates"


def companion_card_html(text, style):
    """The companion's reply as a card (used on Home)."""
    return (
        '<div class="companion-card reveal">'
        '<div class="companion-avatar"></div>'
        '<div><div class="eyebrow">ORBIT · your AI companion</div>'
        f'<p class="companion-text">{esc(text)}</p>'
        f'<span class="mode-badge">Reply style: {esc(style)}</span></div></div>'
    )


def open_calm_room(tool):
    st.session_state.calm_tool = tool
    go_to("Calm Room")


# ---------------------------------------------------------------
# Companion page (a chat)
# ---------------------------------------------------------------
STARTERS = [
    "Exams are next week and I can't stop worrying.",
    "Today was actually really good!",
    "I had a fight with my best friend.",
    "aaj mood thoda off hai yaar",
]


def queue_message(text):
    st.session_state.chat_pending = text


def new_conversation():
    st.session_state.chat = []
    st.session_state.chat_token_given = False


def emotion_chips_html(result):
    final = result["final"]
    chips = [f"{final['family']} · {final['emotion']}"]
    chips += [f"{label} {score:.0%}" for label, score in result["emotions"][:3] if score >= 0.05]
    extra = f'<span class="chat-understood">understood as: “{esc(result["model_text"])}”</span>' \
        if result["translated"] else ""
    return f'<div class="chat-chips">{confidence_html(result)}{tags_html(chips)}{extra}</div>'


def refresh_reply(result):
    """After the user teaches ORBIT, rewrite the reply to that message."""
    name = storage.get_setting("name", "")
    for message in st.session_state.chat:
        if message["role"] == "assistant" and message["result"] is result:
            message["content"], message["style"] = reply(result, (), name)


def handle_message(text):
    name = storage.get_setting("name", "")
    result = analyse(text.strip(), empty_message="Write a few words first.")
    if not result:
        return
    chat = st.session_state.chat
    chat.append({"role": "user", "content": text.strip(), "result": result})
    answer, style = reply(result, [m for m in chat if m["role"] in ("user", "assistant")], name)
    chat.append({"role": "assistant", "content": answer, "style": style, "result": result})
    if may_store(result):
        storage.add_entry("Companion", result["text"], result["emotions"], result["world"],
                          primary=result["final"]["emotion"])
    if games_allowed(result) and not st.session_state.chat_token_given:
        st.session_state.chat_token_given = True
        earn_token("thanks for talking")


def companion_page():
    name = storage.get_setting("name", "")
    section_header(
        "Companion",
        "Someone to talk to",
        "Tell ORBIT what's on your mind. It listens for the feelings in your words, reflects them back "
        "and helps you take a small next step.",
        first=True,
    )
    style = f"Local AI · {local_ai_model()}" if local_ai_model() else "ORBIT templates"
    note(
        f"ORBIT is an AI, not a person, and not a replacement for a counsellor. Replies are written by "
        f"<b>{esc(style)}</b>{' (install Ollama for richer local AI replies)' if style == 'ORBIT templates' else ''}. "
        "If you are ever in danger, call Tele-MANAS on 14416 or 112."
    )

    typed = st.chat_input("Tell ORBIT how you're feeling…", key="chat_input")
    pending = st.session_state.pop("chat_pending", None)
    if typed or pending:
        handle_message(typed or pending)

    chat = st.session_state.chat
    with st.container(key="chat-area"):
        with st.chat_message("assistant", avatar=":material/blur_on:"):
            greeting = f"Hi {name}. " if name else "Hi. "
            st.markdown(greeting + "I'm ORBIT, an AI companion. I'm not a person, but I'm here to listen. "
                        "How are you feeling right now?")
        for message in chat:
            avatar = ":material/person:" if message["role"] == "user" else ":material/blur_on:"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(esc(message["content"]))
                if message["role"] == "user":
                    st.html(emotion_chips_html(message["result"]))
                else:
                    if message["result"]["safety"]:
                        st.html(safety_card_html(message["result"]["safety"]))
                    st.html(f'<span class="mode-badge">Reply style: {esc(message["style"])}</span>')

    if not chat:
        st.html('<div class="field-label" style="margin-top:1rem">Not sure how to start? Try one:</div>')
        columns = st.columns(len(STARTERS))
        for column, starter in zip(columns, STARTERS):
            column.button(starter, key=f"starter_{starter}", on_click=queue_message, args=(starter,),
                          width="stretch")
        return

    last = chat[-1]["result"]
    clarify(last, key=f"chat_{len(chat)}", on_update=refresh_reply)
    teach_panel(last, key=f"chat_{len(chat)}", on_update=refresh_reply)
    if last["safety"] != "crisis":
        tool, line = suggestion(last)
        st.html(f'<p class="body" style="margin:.6rem 0 .4rem">{esc(line)}</p>')
    left, right, _ = st.columns([1.3, 1.1, 2])
    if last["safety"] != "crisis":
        left.button(f"Open {tool}", key="chat_tool", type="primary", on_click=open_calm_room, args=(tool,),
                    width="stretch")
    right.button("New conversation", key="chat_new", on_click=new_conversation, width="stretch")

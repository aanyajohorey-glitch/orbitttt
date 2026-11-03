"""
companion.py
ORBIT's companion replies, shown in the check-in: replies that make the user feel heard.

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
import random
import zlib
from datetime import datetime, timedelta

import llm
import storage
from components import esc
from emotion_model import FEELING_WORDS, GROUP_OF


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
    rng = random.Random(zlib.crc32(result["text"].encode("utf-8")))

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


def reply(result, history=(), name=""):
    """Return (reply_text, style) for an analysed message.

    Crisis messages ALWAYS get the fixed safety reply: they never reach any AI
    model (local or cloud). Otherwise an AI reply is tried if one is set up
    (llm.py, with prompt-injection and output checks), and templates are the
    fallback.
    """
    if result["safety"] == "crisis":
        return CRISIS_REPLY, "Safety reply"
    written = llm.ai_reply(result, list(history), name)
    if written:
        return written
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


STARTERS = [
    "Exams are next week and I can't stop worrying.",
    "Today was actually really good!",
    "I had a fight with my best friend.",
    "aaj mood thoda off hai yaar",
]



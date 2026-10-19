"""
safety.py
ORBIT's safety net.

ORBIT talks with young people about their feelings, so it must notice when
someone may be in danger and point them to real, human help.

Two levels:
- "crisis":  words about suicide or self-harm. ORBIT pauses everything else
             and shows helplines straight away.
- "concern": signs of hopelessness or deep grief. ORBIT keeps talking, but
             gently reminds the user that people can help.

This is a simple phrase check on purpose: it is predictable, easy to test and
easy to explain. It is not a diagnosis, and it is checked BEFORE any AI reply
is written, so a crisis message is never left to the AI.
"""
import re

CRISIS_PHRASES = [
    # English
    "kill myself", "killing myself", "want to die", "wanna die", "wish i was dead", "wish i were dead",
    "end my life", "ending my life", "take my life", "suicide", "suicidal", "self harm", "self-harm",
    "hurt myself", "harm myself", "cut myself", "cutting myself", "don't want to live", "dont want to live",
    "do not want to live", "no reason to live", "better off without me", "better off dead", "end it all", "ending it all",
    "kill me now", "hang myself", "overdose",
    "not worth living", "can't go on living", "cant go on living",
    # Hinglish
    "marna chahta", "marna chahti", "mar jana chahta", "mar jana chahti", "mar jaana chahta",
    "mar jaana chahti", "khudkushi", "aatmahatya", "jeena nahi chahta", "jeena nahi chahti",
    "zinda nahi rehna", "mar jaun",
    # Hindi
    "आत्महत्या", "खुदकुशी", "मरना चाहता", "मरना चाहती", "जीना नहीं चाहता", "जीना नहीं चाहती",
]

CONCERN_PHRASES = [
    "hopeless", "worthless", "no point", "pointless", "can't do this anymore", "cant do this anymore",
    "can't take it anymore", "cant take it anymore", "nobody cares", "no one cares", "give up on everything",
    "empty inside", "hate myself", "disappear forever", "no way out", "i'm a burden", "im a burden", "trapped", "nobody would notice",
    "koi nahi samajhta", "main bekaar hoon", "sab khatam",
]

HELPLINES = [
    ("Tele-MANAS (Govt. of India)", "14416", "Free, confidential, 24/7, in many Indian languages"),
    ("Tele-MANAS toll-free", "1-800-891-4416", "Same service, alternative number"),
    ("Emergency", "112", "If you or someone else is in immediate danger"),
]


def _normalise(text):
    text = text.lower().replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text)


def check(text, emotions=None):
    """Return "crisis", "concern" or None for a piece of text.

    emotions (optional): the model's (emotion, score) list. Very strong grief
    also counts as "concern".
    """
    clean = _normalise(text)
    if any(phrase in clean for phrase in CRISIS_PHRASES):
        return "crisis"
    if any(phrase in clean for phrase in CONCERN_PHRASES):
        return "concern"
    if emotions and dict(emotions).get("grief", 0.0) >= 0.4:
        return "concern"
    return None


def helplines_html():
    rows = "".join(
        f'<a class="helpline" href="tel:{number.replace("-", "")}">'
        f'<span class="helpline-name">{name}</span><b>{number}</b><small>{detail}</small></a>'
        for name, number, detail in HELPLINES
    )
    return f'<div class="helplines">{rows}</div>'


def safety_card_html(level):
    """The card shown when the safety check finds something."""
    if level == "crisis":
        return (
            '<div class="safety-card crisis">'
            '<div class="eyebrow">You matter</div>'
            '<div class="title-sm">You don\'t have to carry this alone.</div>'
            '<p class="body">It sounds like you\'re going through something really painful right now. '
            "Please reach out to a real person who can help today. You can call for free, at any time:</p>"
            + helplines_html()
            + '<p class="body" style="margin-top:.9rem">Please also tell a parent, teacher or friend you trust. '
            "ORBIT is an app, not a counsellor, and people can help in ways an app can't.</p></div>"
        )
    return (
        '<div class="safety-card concern">'
        '<div class="eyebrow">A gentle note</div>'
        '<p class="body">That sounds really heavy. If feelings like this keep coming back, talking to someone '
        "can help a lot. <b>Tele-MANAS (14416)</b> is free, confidential and open 24/7, and a trusted adult "
        "can help too.</p></div>"
    )

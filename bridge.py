"""
bridge.py
The two bridges between ORBIT's modes.

Create -> Feel: if an idea, or "How's the project going?", shows stress or
creative-block language, ORBIT offers a short break, a matched stress-buster
game, or a 5-minute creative-block exercise. Afterwards "Back to my project"
returns to exactly where the user was (the project is kept in session state).

Feel -> Create: after a check-in, "Turn this feeling into something" sends the
emotion blend into Creator Mode, which makes a palette, moodboard and playlist
from it. The check-in text itself is not used as the project title.

Detection is a small, readable word list (no AI), checked AFTER the crisis
check: crisis wording always gets only the safety response.
"""
import re

BLOCKS = {
    "Perfectionism": {
        "words": ["perfect", "not good enough", "flawless", "mistake", "mistakes", "never good", "ruin", "ruined",
                  "redo", "start over again"],
        "game": "mandala",
        "exercise": ("Make it badly, on purpose. Set a 5-minute timer and make the WORST version you can: wrong "
                     "colours, wobbly lines, silly words. When the timer ends, circle one thing in it you actually "
                     "like. That's your way back in."),
    },
    "Fear of judgment": {
        "words": ["judge", "judged", "what will people think", "laugh at", "embarrass", "embarrassing", "cringe",
                  "criticise", "criticize", "nobody will like", "they'll hate", "people will hate"],
        "game": "pop_worry",
        "exercise": ("An audience of one. For 5 minutes, make something only for yourself that nobody will ever "
                     "see. Then write down the one person whose opinion you actually care about, and what they would "
                     "most likely say. It's usually kinder than the crowd in your head."),
    },
    "Burnout": {
        "words": ["tired", "exhausted", "burnt out", "burned out", "burnout", "drained", "no energy",
                  "can't anymore", "cant anymore", "too much work", "overworked", "so much work"],
        "game": "zen_sand",
        "exercise": ("Fill the well. For 5 minutes, don't make anything. Look at one thing you love (a song, a "
                     "painting, a view) and just notice it. Then write one sentence about why it works. Rest and "
                     "input are part of making."),
    },
    "Comparison": {
        "words": ["everyone else", "better than me", "compare", "comparing", "instagram", "not as good as",
                  "others are", "jealous", "they're so good", "their work"],
        "game": "constellation",
        "exercise": ("Learn like a student. List three things you admire in their work. Then spend 5 minutes "
                     "trying ONE of them your way, mixed with something only you know about: your street, your "
                     "family, your language."),
    },
    "No direction": {
        "words": ["stuck", "don't know what", "dont know what", "no idea", "no ideas", "blank page", "mind is blank",
                  "feel lost", "feeling lost", "i'm lost", "im lost",
                  "where to start", "can't start", "cant start", "writer's block", "creative block", "blocked"],
        "game": "tiny_wins",
        "exercise": ("Three-object spark. Pick three random things near you. In 5 minutes, make something tiny "
                     "that uses all three: a sketch, three lines of a poem, a colour swatch. Constraints make "
                     "starting easier."),
    },
}
STRESS_WORDS = ["stress", "stressed", "stressing", "deadline", "pressure", "anxious", "panic", "panicking",
                "overwhelmed", "freaking out", "worried", "nervous"]


def _contains(text, phrase):
    return re.search(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", text) is not None


def detect(text):
    """(block name or None, stressed?) from the words in a message. Crisis is checked elsewhere, first."""
    lowered = (text or "").lower().replace("’", "'")
    scores = {name: sum(_contains(lowered, w) for w in info["words"]) for name, info in BLOCKS.items()}
    block = max(scores, key=scores.get) if max(scores.values()) > 0 else None
    stressed = any(_contains(lowered, w) for w in STRESS_WORDS)
    return block, stressed


def offer_for(text):
    """What to offer for a message: None, or {"block", "stressed", "game"}."""
    block, stressed = detect(text)
    if not block and not stressed:
        return None
    game = BLOCKS[block]["game"] if block else "orb_flow"
    return {"block": block, "stressed": stressed, "game": game}


def feeling_to_vector(result):
    """A Vibe Vector from a check-in's emotion blend (the words still shape the themes)."""
    import vibe
    return vibe.build("a creative piece inspired by today's feeling", result["emotions"],
                      start_from="A feeling", match_text=result.get("model_text") or result.get("text", ""))

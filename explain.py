"""
explain.py
"Why did ORBIT think this?" - explainable AI for the emotion model.

Method: occlusion (also called leave-one-out).
  1. Score the full text for the main emotion, e.g. sadness = 0.92.
  2. Remove ONE word and score the text again, e.g. without "miss" -> 0.40.
  3. The bigger the drop, the more that word pushed the model towards
     the emotion. Repeat for every word.

It needs no extra libraries: it just asks the same model many times.
"""
import re

from components import esc
from emotion_model import score_texts

MAX_WORDS = 40  # longer texts are explained using their first 40 words


def word_importance(text, emotion):
    """Return [(word, importance), ...]. Importance > 0 means the word
    pushed the model TOWARDS the emotion."""
    words = re.findall(r"\S+", text)[:MAX_WORDS]
    if len(words) < 2:
        return [(word, 0.0) for word in words]
    variants = [" ".join(words)] + [" ".join(words[:i] + words[i + 1:]) for i in range(len(words))]
    scores = score_texts(variants)
    base = scores[0][emotion]
    return [(word, base - scores[i + 1][emotion]) for i, word in enumerate(words)]


def highlight_html(importances):
    """The text with the most important words glowing in lavender."""
    strongest = max([value for _, value in importances] + [1e-6])
    spans = []
    for word, value in importances:
        strength = max(0.0, value) / strongest
        if strength < 0.08:
            spans.append(f"<span>{esc(word)}</span>")
        else:
            spans.append(
                f'<span class="why-word" style="--w:{strength:.2f}" '
                f'title="{value * 100:+.0f} points">{esc(word)}</span>'
            )
    return '<p class="why-text">' + " ".join(spans) + "</p>"


def top_words(importances, count=3):
    ranked = sorted((pair for pair in importances if pair[1] > 0.01), key=lambda pair: -pair[1])
    return [re.sub(r"[^\w'-]", "", word) or word for word, _ in ranked[:count]]

"""
music_ui.py
Mood Studio -> Music discovery: the screen for music.py.
Links open Spotify or YouTube SEARCH pages; ORBIT makes no API calls.
"""
import hashlib

import streamlit as st

import music
from components import esc, note
from studio import save_stars

FEELINGS = ["joy", "love", "gratitude", "curiosity", "neutral", "sadness", "disappointment", "nervousness", "fear",
            "anger", "annoyance"]
INTENTS = {"match": "Match my mood", "lift": "Gently lift me"}


def save_new(target, key):
    """'New to you?' Yes = 1, No = 0 (replaces an earlier answer)."""
    import storage
    saved = st.session_state.setdefault("rating_ids", {})
    if key in saved:
        storage.delete_rating(saved.pop(key))
    answer = st.session_state.get(key)
    if answer in ("Yes", "No"):
        saved[key] = storage.add_rating("music_new", target, 1 if answer == "Yes" else 0)


def music_section():
    last = st.session_state.get("home_result")
    with st.container(key="glass-music-input"):
        if last and last.get("safety") != "crisis":
            emotions = last["emotions"][:6]
            label = last["final"]["emotion"]
            st.html(f'<p class="body">Using your last check-in: <b>{esc(label)}</b> '
                    f'(with {esc(", ".join(e for e, _ in emotions[1:3]))}).</p>')
        else:
            label = st.selectbox("How are you feeling?", FEELINGS, index=FEELINGS.index("neutral"), key="music_feel")
            emotions = [(label, 1.0)]
        intent = st.radio("What would help?", list(INTENTS), format_func=INTENTS.get, horizontal=True,
                          key="music_intent")
        family = music.GROUP_OF[label]
        if family in music.LOW_FAMILIES:
            st.html('<p class="body">Both are okay. Music that matches a heavy feeling can feel understood; '
                    "music that lifts you a little can help it shift. Try either.</p>")
        discovery = st.slider("Comfort zone ↔ Explore", 0.0, 1.0, 0.5, 0.1, key="music_discovery",
                              help="Explore picks more lesser-known artists, genres and languages.")

    playlist = music.recommend(emotions, intent, discovery)
    spread = music.diversity(playlist)
    st.html(f'<div class="eyebrow" style="margin-top:.6rem">Your playlist · {len(playlist)} tracks · '
            f'{spread["languages"]} languages · {spread["genres"]} genres</div>')
    with st.container(key="glass-music-list"):
        rows = []
        for i, track in enumerate(playlist, 1):
            spotify, youtube = music.links(track)
            rows.append(
                f'<div class="track"><span class="track-num">{i:02d}</span><div><b>{esc(track["title"])}</b> · '
                f'{esc(track["artist"])}<small>{esc(track["language"])} · {esc(track["genre"])}</small>'
                f'<p class="body">{esc(track["reason"])}</p></div>'
                f'<div class="track-links"><a href="{spotify}" target="_blank" rel="noopener">Spotify</a>'
                f'<a href="{youtube}" target="_blank" rel="noopener">YouTube</a></div></div>')
        st.html("".join(rows))

    with st.expander("How this playlist was made"):
        mood, energy, family, tags = music.target_for(emotions, intent)
        st.html(
            f'<p class="body"><b>1. Target:</b> mood {mood:.1f}/5 and energy {energy:.1f}/5 from your feeling'
            + (" (moved a gentle step brighter and steadier, because you chose to be lifted)" if intent == "lift"
               else "") + f', plus the tags {esc(", ".join(tags))}.<br>'
            "<b>2. Relevance:</b> every track is a vector of mood, energy and tags. Cosine similarity measures how "
            "closely it points the same way as the target.<br>"
            f"<b>3. Discovery ({discovery:.1f}):</b> towards Explore, lesser-known tracks get a small boost.<br>"
            "<b>4. Diversity (MMR):</b> tracks are picked one by one, balancing relevance against being too similar "
            "to tracks already picked (same artist, genre or language). One song per artist.<br>"
            f'Average mainstream level: {spread["avg_mainstream"]} out of 5.</p>')

    signature = hashlib.md5(f"{label}|{intent}|{discovery}".encode()).hexdigest()[:8]
    left, middle = st.columns([1.2, 1], vertical_alignment="center")
    with left:
        st.html('<span class="feedback-label">Did this fit your mood? (1-5 stars)</span>')
        st.feedback("stars", key=f"fb_music_fit_{signature}", on_change=save_stars,
                    args=("music_fit", label, f"fb_music_fit_{signature}"))
    with middle:
        st.segmented_control("New to you?", ["Yes", "No"], key=f"fb_music_new_{signature}", on_change=save_new,
                             args=(label, f"fb_music_new_{signature}"))
    note("The catalogue is small (about 270 songs) and hand-labelled by the student, so the labels are opinions. "
         "Lyrics are not stored. Links open a search on Spotify or YouTube; ORBIT doesn't connect to them.")

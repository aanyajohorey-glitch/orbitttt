"""
styles_features.py
CSS for the Tier 3 and Tier 4 features (constellation, world themes, game
pop-up, patterns, letters, the galaxy home screen). styles.load_css() adds it.

Rule used everywhere: an element's normal state is VISIBLE, and animations
only play FROM a hidden state (animation-fill-mode: both). So when motion is
reduced and animations are switched off, nothing stays hidden.
Note: this CSS must never contain text that looks like an HTML tag.
"""

FEATURE_CSS = """
/* ---------- Emotion Constellation ---------- */
/* The constellation's own animation is inside its SVG image (see constellation.py). */
.cst-wrap { display: grid; justify-items: center; gap: 0.3rem; }
.cst-img { max-width: 100%; height: auto; display: block; }
.cst-caption { font-size: 0.78rem; color: var(--muted); text-align: center; max-width: 34ch; margin: 0; }
.cst-planet .cst-overlay { position: absolute; inset: 0; z-index: 2; border-radius: 50%; overflow: hidden;
  opacity: 0.9; pointer-events: none; }
.cst-planet .cst-overlay img { width: 100%; height: 100%; display: block; }
.galaxy-star .planet { animation-duration: calc(9s * var(--orbit-speed, 1)); }

/* ---------- World theme: chip and sound ---------- */
.stApp { transition: background-color 1.2s ease; }
.world-chip { display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; color: var(--muted);
  padding: 0.3rem 0.8rem; border-radius: 999px; background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.85); }
.world-chip span { width: 0.7rem; height: 0.7rem; border-radius: 50%; background: var(--c);
  box-shadow: 0 0 10px var(--c); }
.world-chip b { color: var(--charcoal); font-weight: 600; }
.st-key-world-sound [data-testid="stAudio"] { max-width: 360px; margin-left: auto; }

/* ---------- Stress-buster pop-up ---------- */
.game-offer { display: grid; gap: 0.2rem; padding: 0.9rem 1rem; margin: 0.6rem 0 0.9rem; border-radius: 16px;
  background: rgba(201, 185, 232, 0.22); border: 1px solid rgba(255, 255, 255, 0.9); }
.game-offer b { font-family: var(--serif); font-size: 1.4rem; font-weight: 500; }
.game-offer span { font-size: 0.82rem; color: var(--muted); }
.st-key-glass-game iframe, .st-key-glass-games iframe { border-radius: 18px; }
"""

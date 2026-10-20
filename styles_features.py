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
"""

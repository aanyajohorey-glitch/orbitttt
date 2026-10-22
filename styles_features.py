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

/* ---------- Mood Studio moodboard ---------- */
.moodboard { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-rows: 120px; gap: 10px;
  padding: 12px; border-radius: 22px; box-shadow: 0 24px 50px -32px rgba(52, 49, 59, 0.5); }
.mb-tile { border-radius: 16px; position: relative; overflow: hidden; }
.mb-hero { grid-column: span 2; grid-row: span 2; }
.mb-type { grid-column: span 2; grid-row: span 2; padding: 18px; display: flex; flex-direction: column; justify-content: center; }
.mb-pattern span { position: absolute; left: 10px; bottom: 8px; font-size: 0.7rem; letter-spacing: 0.08em;
  text-transform: uppercase; background: rgba(255, 255, 255, 0.8); color: #34313B; padding: 2px 8px; border-radius: 999px; }
.mb-swatches { grid-column: span 4; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; }
.mb-swatch { border-radius: 14px; padding: 10px; display: flex; flex-direction: column; justify-content: flex-end;
  border: 1px solid rgba(52, 49, 59, 0.1); }
.mb-swatch b { font-size: 0.8rem; font-weight: 600; }
.mb-swatch small { font-size: 0.72rem; opacity: 0.8; font-variant-numeric: tabular-nums; }
.mb-words { display: flex; flex-wrap: wrap; align-content: center; gap: 5px; padding: 8px; overflow: hidden; }
.mb-words span { border: 1px solid; border-radius: 999px; padding: 2px 8px; font-size: 0.72rem; }
.check-row { display: grid; grid-template-columns: minmax(0, 1fr) auto 9rem; gap: 1rem; align-items: center;
  padding: 0.5rem 0; border-bottom: 1px solid var(--line); font-size: 0.86rem; }
.check-row b { text-align: right; font-weight: 600; }
@media (max-width: 640px) {
  .moodboard { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .mb-type, .mb-swatches { grid-column: span 2; }
  .mb-swatches { grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: 90px; }
}

/* ---------- Mood Studio music ---------- */
.track { display: grid; grid-template-columns: 2.2rem minmax(0, 1fr) auto; gap: 0.8rem; align-items: center;
  padding: 0.7rem 0; border-bottom: 1px solid var(--line); }
.track-num { font-family: var(--serif); font-size: 1.3rem; color: var(--muted); }
.track small { display: block; font-size: 0.74rem; color: var(--muted); letter-spacing: 0.04em; }
.track .body { margin-top: 0.15rem; font-size: 0.84rem; }
.track-links { display: flex; gap: 0.4rem; }
.track-links a { font-size: 0.78rem; text-decoration: none; color: var(--charcoal); border: 1px solid var(--line);
  border-radius: 999px; padding: 0.25rem 0.7rem; background: rgba(255, 255, 255, 0.6); }
.track-links a:hover { background: rgba(255, 255, 255, 0.95); }
@media (max-width: 640px) { .track { grid-template-columns: 1.8rem minmax(0, 1fr); } .track-links { grid-column: 2; } }

/* ---------- Reach Out drafts: the copy box uses the normal font ---------- */
[class*="st-key-glass-ro-draft"] pre, [class*="st-key-glass-ro-draft"] code {
  font-family: var(--sans) !important; font-size: 0.92rem !important; white-space: pre-wrap !important; }
"""

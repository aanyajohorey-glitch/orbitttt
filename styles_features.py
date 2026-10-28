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

/* ---------- Creator Mode ---------- */
.cu-title { font-size: clamp(2.2rem, 5vw, 3.4rem); line-height: 1.05; margin: 0.4rem 0 0.6rem; color: var(--charcoal); }
.cu-vision { font-size: 1.02rem; line-height: 1.7; color: var(--charcoal); max-width: 70ch; margin: 0 0 0.8rem; }
.cu-swatches { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-top: 0.6rem; }
.cu-swatch { display: grid; gap: 2px; font-size: 0.8rem; }
.cu-swatch span { height: 64px; border-radius: 14px; border: 1px solid rgba(52, 49, 59, 0.1); margin-bottom: 4px; }
.cu-swatch small { color: var(--muted); font-size: 0.72rem; }
.cu-type { padding: 0.4rem 0; }
.cu-type p { color: var(--muted); margin: 0.4rem 0 0; }
.cu-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }
.cu-card { padding: 0.9rem 1rem; border-radius: 16px; background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.85); display: grid; gap: 0.25rem; align-content: start; }
.cu-card b { font-size: 1rem; }
.cu-card small { font-size: 0.74rem; color: var(--muted); letter-spacing: 0.03em; }
.cu-card a { font-size: 0.78rem; color: var(--charcoal); }
.dir-card { display: grid; gap: 0.4rem; }
.dir-card b { font-family: var(--serif); font-size: 1.4rem; font-weight: 500; }
.dir-card small { color: var(--muted); font-size: 0.8rem; }
.dir-strip { display: flex; height: 26px; border-radius: 10px; overflow: hidden; }
.dir-strip i { flex: 1; }
.hist-row { display: grid; gap: 0.2rem; }
.hist-row .dir-strip { height: 12px; width: 140px; }
.hist-row small { color: var(--muted); font-size: 0.74rem; }
.spark-tile { height: 92px; border-radius: 16px; display: flex; align-items: flex-end; padding: 10px; }
.spark-tile span { background: rgba(255, 255, 255, 0.85); color: #34313B; border-radius: 10px; padding: 3px 8px;
  font-size: 0.78rem; line-height: 1.3; }
.mode-card { padding: 1.6rem; border-radius: 22px; background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.9); min-height: 170px; }
.mode-card b { font-family: var(--serif); font-size: 2rem; font-weight: 500; display: block; }
.mode-card p { color: var(--muted); margin: 0.4rem 0 0; }
.mode-card small { display: inline-block; margin-top: 0.7rem; font-size: 0.72rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--muted); }
@media (max-width: 640px) { .cu-swatches { grid-template-columns: repeat(3, minmax(0, 1fr)); } }

/* ---------- Letters ---------- */
.ritual { display: grid; justify-items: center; gap: 1rem; padding: 2rem 0 1rem; }
.ritual-paper { max-width: 520px; padding: 1.4rem 1.6rem; background: #FFFDF8; border-radius: 6px;
  box-shadow: 0 18px 40px -24px rgba(52, 49, 59, 0.5); font-family: var(--serif); font-size: 1.1rem;
  line-height: 1.6; color: var(--charcoal); white-space: pre-wrap; }
.ritual-paper.burn { animation: burn-away 3.2s ease-in 0.6s both; }
.ritual-paper.float { animation: float-away 3.6s ease-in 0.6s both; }
.ritual-paper.fade { animation: fade-away 2.4s ease 0.6s both; }
@keyframes burn-away {
  0% { filter: none; opacity: 1; transform: none; }
  40% { filter: sepia(1) saturate(3) brightness(0.9); background: #F3C98B; }
  75% { filter: sepia(1) brightness(0.4) blur(1px); transform: scale(0.94) rotate(-2deg); opacity: 0.6; }
  100% { filter: brightness(0) blur(6px); transform: scale(0.6) translateY(20px); opacity: 0; }
}
@keyframes float-away {
  0% { transform: none; opacity: 1; }
  100% { transform: translateY(-260px) rotate(6deg) scale(0.7); opacity: 0; }
}
@keyframes fade-away { from { opacity: 1; } to { opacity: 0; } }
.ritual-words { font-family: var(--serif); font-size: 1.4rem; color: var(--charcoal); text-align: center; }
.letter-text { font-family: var(--serif); font-size: 1.15rem; line-height: 1.7; white-space: pre-wrap; margin: 0.4rem 0; }
.sealed-row { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 0.8rem; }
.sealed { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.9rem; border-radius: 999px;
  background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(255, 255, 255, 0.9); font-size: 0.84rem; color: var(--muted); }

/* ---------- Safety plan ---------- */
.plan { display: grid; gap: 0.8rem; }
.plan-step { display: grid; grid-template-columns: 2rem minmax(0, 1fr); gap: 0.8rem; align-items: start; }
.plan-step > span { width: 2rem; height: 2rem; border-radius: 50%; display: grid; place-items: center;
  background: rgba(201, 185, 232, 0.6); font-weight: 600; }
.plan-step b { font-size: 1rem; }
.plan-step .body { white-space: pre-wrap; margin-top: 0.15rem; }

/* ---------- Create: the orbit view (idea at the centre, elements orbiting) ---------- */
.uorbit { position: relative; height: 480px; margin: 0.4rem auto 1rem; max-width: 760px; --r: 195px; }
.uorbit-ring { position: absolute; left: 50%; top: 50%; width: calc(var(--r) * 2); height: calc(var(--r) * 2);
  transform: translate(-50%, -50%); border-radius: 50%; border: 1px dashed rgba(52, 49, 59, 0.18); }
.uorbit-core { position: absolute; left: 50%; top: 50%; width: 150px; height: 150px; transform: translate(-50%, -50%);
  border-radius: 50%; display: grid; place-items: center; text-align: center; padding: 14px;
  background: radial-gradient(circle at 32% 28%, #ffffff, var(--c1) 55%, var(--c2));
  box-shadow: 0 0 60px -10px var(--c1), inset -8px -12px 24px rgba(52, 49, 59, 0.18); }
.uorbit-core span { font-size: 1.05rem; line-height: 1.15; color: #34313B; }
.uorbit-spin { position: absolute; inset: 0; }
.op-planet { position: absolute; left: 50%; top: 50%; width: 0; height: 0;
  transform: rotate(var(--a)) translateY(calc(var(--r) * -1)) rotate(calc(var(--a) * -1)); }
.op-body { position: absolute; transform: translate(-50%, -50%); width: 118px; padding: 8px 6px; border-radius: 18px;
  display: grid; justify-items: center; gap: 2px; text-align: center; background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.95); box-shadow: 0 12px 26px -16px rgba(52, 49, 59, 0.45); }
.op-body b { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }
.op-body small { font-size: 0.74rem; color: var(--charcoal); line-height: 1.2; max-height: 2.4em; overflow: hidden; }
.op-swatch { width: 34px; height: 34px; border-radius: 50%; display: block; }
.op-type { font-style: normal; font-size: 1.6rem; line-height: 1; color: var(--charcoal); }
.op-icon { font-style: normal; font-size: 1.4rem; line-height: 1; color: var(--charcoal); }
@keyframes orbit-spin { to { transform: rotate(360deg); } }
.uorbit:hover .uorbit-spin, .uorbit:hover .op-body { animation-play-state: paused; }
@media (max-width: 640px) { .uorbit { height: 380px; --r: 140px; } .op-body { width: 96px; } .uorbit-core { width: 120px; height: 120px; } }
@media (prefers-reduced-motion: reduce) { .uorbit-spin, .op-body { animation: none !important; } }

/* ---------- Hide the default Streamlit chrome (ORBIT has its own top bar) ---------- */
[data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"],
[data-testid="stDecoration"], #MainMenu, footer { display: none !important; }

/* ---------- Landing page: ivory hero, pastel planets ---------- */
.stApp:has(.lp-hero) { background:
    radial-gradient(900px 520px at 85% 10%, rgba(201, 185, 232, 0.28), transparent 62%),
    radial-gradient(760px 480px at 6% 92%, rgba(235, 203, 215, 0.30), transparent 60%),
    radial-gradient(620px 420px at 50% 120%, rgba(199, 211, 192, 0.30), transparent 60%), #FBF6F1 !important; }
.st-key-landing { max-width: 1080px; margin: 3vh auto 0; }
.lp-hero { font-family: var(--sans); color: #34313B; }
.lp-eyebrow { font-family: var(--sans); font-size: 0.74rem; font-weight: 600; letter-spacing: 0.22em;
  text-transform: uppercase; color: #8A8494; }
.lp-wordmark { font-family: var(--serif); font-weight: 500; font-size: clamp(3.4rem, 8vw, 6rem); line-height: 1;
  letter-spacing: 0.28em; color: #34313B; margin: 0.9rem 0 0.5rem; }
.lp-tagline { font-family: var(--serif); font-style: italic; font-size: clamp(1.35rem, 2.6vw, 1.75rem);
  color: #5B5566; line-height: 1.25; }
.stApp .lp-sub { font-family: var(--sans); font-size: 1rem; line-height: 1.6; color: #6F6A78 !important; margin: 0.7rem 0 0; max-width: 30rem; }
.st-key-landing-form { margin-top: 1.6rem; padding: 1.4rem 1.4rem 1.2rem; border-radius: 24px;
  background: rgba(255, 255, 255, 0.72); border: 1px solid #EFE5DC;
  box-shadow: 0 28px 56px -36px rgba(110, 90, 138, 0.40); }
.st-key-landing-form label, .st-key-landing-form label p { font-family: var(--sans) !important; color: #6F6A78 !important;
  font-size: 0.74rem !important; font-weight: 600 !important; letter-spacing: 0.14em; text-transform: uppercase; }
.st-key-landing-form div:has(> input) { background: #FFFFFF !important; border: 1px solid #E9E0D8 !important;
  border-radius: 14px !important; transition: border-color 0.2s ease, box-shadow 0.2s ease; }
.st-key-landing-form div:has(> input):focus-within { border-color: #A895D2 !important;
  box-shadow: 0 0 0 4px rgba(201, 185, 232, 0.35) !important; }
.st-key-landing-form input { font-family: var(--sans) !important; background: transparent !important;
  color: #34313B !important; -webkit-text-fill-color: #34313B !important; font-size: 1.02rem !important; }
.st-key-landing-form input::placeholder { color: #A7A0AE !important; -webkit-text-fill-color: #A7A0AE !important; }
.st-key-landing-form button:not([data-testid="stBaseButton-primary"]) { background: transparent !important;
  color: #6F6A78 !important; }
.st-key-landing-form [data-testid="stBaseButton-primary"] { margin-top: 0.5rem; padding: 0.9rem 1rem !important;
  border-radius: 999px !important; border: none !important; background: #34313B !important;
  box-shadow: 0 16px 30px -18px rgba(52, 49, 59, 0.7) !important; transition: background 0.2s ease, box-shadow 0.2s ease; }
.st-key-landing-form [data-testid="stBaseButton-primary"]:hover { background: #463F55 !important;
  box-shadow: 0 18px 34px -16px rgba(168, 149, 210, 0.9) !important; }
.st-key-landing-form [data-testid="stBaseButton-primary"] p { font-family: var(--sans) !important; color: #FBF6F1 !important;
  font-weight: 600 !important; font-size: 1rem !important; letter-spacing: 0.02em; }
.stApp .lp-note { font-family: var(--sans); font-size: 0.78rem; line-height: 1.5; color: #7A7484 !important; margin: 0.9rem 0.3rem 0; }
.lp-art { position: relative; height: 480px; max-width: 520px; margin: 0 auto; }
.lp-path { position: absolute; border-radius: 50%; border: 1px dashed rgba(168, 149, 210, 0.38); }
.lp-path-1 { left: 4%; top: 22%; width: 92%; height: 56%; transform: rotate(-14deg); }
.lp-path-2 { left: 18%; top: 6%; width: 64%; height: 88%; transform: rotate(24deg); border-color: rgba(198, 149, 170, 0.30); }
.lp-planet { position: absolute; border-radius: 50%;
  background: radial-gradient(circle at 32% 28%, var(--c0) 0%, var(--c1) 48%, var(--c2) 100%);
  box-shadow: 0 22px 44px -20px var(--c2), inset -10px -14px 26px rgba(52, 49, 59, 0.10);
  animation: lp-float 10s ease-in-out infinite; }
.lp-p-lavender { width: 210px; height: 210px; left: calc(50% - 105px); top: calc(50% - 105px); }
.lp-p-blush { width: 92px; height: 92px; right: 6%; top: 9%; animation-duration: 12s; animation-delay: -4s; }
.lp-p-sage { width: 72px; height: 72px; left: 7%; bottom: 13%; animation-duration: 14s; animation-delay: -7s; }
.lp-p-dot { width: 28px; height: 28px; left: 28%; top: 13%; animation-duration: 9s; animation-delay: -2s; }
.lp-ring { position: absolute; left: -30%; top: 40%; width: 160%; height: 22%; border-radius: 50%;
  border: 2px solid rgba(168, 149, 210, 0.55); transform: rotate(-16deg); }
.lp-spark { position: absolute; width: 6px; height: 6px; border-radius: 50%; background: #C9B9E8;
  box-shadow: 0 0 10px 2px rgba(201, 185, 232, 0.8); animation: lp-twinkle 4.5s ease-in-out infinite; }
@keyframes lp-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }
@keyframes lp-twinkle { 0%, 100% { opacity: 0.25; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.15); } }
@media (max-width: 640px) {
  .st-key-landing [data-testid="stColumn"]:last-child { order: -1; }
  .lp-art { height: 280px; }
  .lp-p-lavender { width: 130px; height: 130px; left: calc(50% - 65px); top: calc(50% - 65px); }
  .lp-p-blush { width: 58px; height: 58px; } .lp-p-sage { width: 46px; height: 46px; }
  .lp-hero { text-align: center; } .lp-sub { margin-left: auto; margin-right: auto; }
}
@media (prefers-reduced-motion: reduce) { .lp-planet, .lp-spark { animation: none !important; } }

/* ---------- Top bar with the Settings menu ---------- */
.st-key-topbar-row .topbar { margin-bottom: 0; }
.st-key-topbar-row [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; align-items: center; }
.st-key-topbar-row [data-testid="stColumn"]:first-child { flex: 1 1 0 !important; width: auto !important; min-width: 0 !important; }
.st-key-topbar-row [data-testid="stColumn"]:last-child { flex: 0 0 auto !important; width: auto !important;
  min-width: 0 !important; display: flex; justify-content: flex-end; }
.st-key-topbar-row [data-testid="stPopover"] button { border-radius: 999px !important; }
.set-head { font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted);
  margin: 0.9rem 0 0.2rem; font-weight: 700; }
.set-head:first-child { margin-top: 0; }

/* ---------- Wrapped ---------- */
.wr-stat { font-family: var(--serif); font-size: 1.1rem; color: var(--muted); }
.wr-stat span { display: block; font-size: 4.2rem; line-height: 1; color: var(--charcoal); }
.wr-rank { font-family: var(--serif); font-size: 1.6rem; color: var(--charcoal); margin: 0.2rem 0; }
.wr-rank b { display: inline-block; width: 2rem; color: var(--accent, #A895D2); }
.wr-chip { display: inline-block; margin: 0.25rem 0.35rem 0 0; padding: 0.3rem 0.75rem; border-radius: 999px;
  font-size: 0.82rem; border: 1px solid var(--c); background: color-mix(in srgb, var(--c) 18%, transparent); }

/* ---------- Font gallery: each font shown in its own typeface ---------- */
.font-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.8rem; margin-top: 0.5rem; }
.font-card { padding: 1rem 1.1rem; border-radius: 18px; background: var(--glass);
  border: 1px solid var(--line); overflow: hidden; }
.font-aa { font-size: 2.6rem; line-height: 1; color: var(--charcoal); }
.font-sample { font-size: 1.15rem; margin: 0.5rem 0 0.35rem; color: var(--charcoal); line-height: 1.25;
  overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.font-name { font-size: 1rem; font-weight: 600; color: var(--charcoal); }
.font-card small { color: var(--muted); font-size: 0.75rem; }
"""

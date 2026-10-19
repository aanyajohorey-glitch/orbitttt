"""
styles.py
The CSS (design rules) that give ORBIT its look: ivory background,
lavender accents, glass cards, glossy planets and capsules.

app.py calls load_css() once at the top of every page.
"""
import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Manrope:wght@300;400;500;600&family=VT323&display=swap');

/* ---------- Design tokens (the brand colours) ---------- */
:root {
  --ivory: #F8F6F2;
  --lavender: #C9B9E8;
  --blue: #B9C8EA;
  --blush: #EBCBD7;
  --sage: #C7D3C0;
  --charcoal: #34313B;
  --muted: rgba(52, 49, 59, 0.64);
  --line: rgba(52, 49, 59, 0.10);
  --glass: rgba(255, 255, 255, 0.56);
  --serif: 'Cormorant Garamond', Georgia, 'Times New Roman', serif;
  --sans: 'Manrope', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* ---------- Page ---------- */
.stApp {
  background:
    radial-gradient(1100px 560px at 88% -8%, rgba(201, 185, 232, 0.34), transparent 60%),
    radial-gradient(900px 520px at -12% 24%, rgba(185, 200, 234, 0.26), transparent 60%),
    radial-gradient(900px 600px at 50% 112%, rgba(235, 203, 215, 0.24), transparent 60%),
    var(--ivory);
  background-attachment: fixed;
  color: var(--charcoal);
  font-family: var(--sans);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] {
  max-width: 1120px;
  padding-top: 1.6rem;
  padding-bottom: 3rem;
}
.stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button {
  font-family: var(--sans);
}
[data-testid="stHeaderActionElements"] { display: none; }

/* ---------- Typography ---------- */
.eyebrow {
  font: 600 0.7rem/1.2 var(--sans);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--muted);
}
.display {
  font-family: var(--serif);
  font-weight: 500;
  font-size: clamp(2.1rem, 4.4vw, 3.2rem);
  line-height: 1.06;
  letter-spacing: -0.01em;
  margin: 0.45rem 0 0.6rem;
  color: var(--charcoal);
}
.lede {
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.65;
  max-width: 60ch;
  margin: 0;
}
.section-head { margin: 2.6rem 0 1.1rem; }
.section-head.first { margin-top: 1.4rem; }
.title-sm {
  font-family: var(--serif);
  font-weight: 500;
  font-size: 1.55rem;
  line-height: 1.15;
  margin: 0.25rem 0 0.35rem;
  color: var(--charcoal);
}
.body { color: var(--muted); font-size: 0.92rem; line-height: 1.6; margin: 0; }

/* ---------- Top bar and navigation ---------- */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 0.9rem;
}
.brand {
  display: flex; align-items: center; gap: 0.6rem;
  font-family: var(--serif); font-weight: 600; font-size: 1.15rem;
  letter-spacing: 0.32em; color: var(--charcoal);
}
.topbar-meta { font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }

.st-key-nav {
  width: fit-content;
  max-width: 100%;
  margin: 0 auto;
  padding: 0.3rem;
  background: rgba(255, 255, 255, 0.5);
  -webkit-backdrop-filter: blur(14px);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.85);
  border-radius: 16px;
  box-shadow: 0 12px 30px -22px rgba(52, 49, 59, 0.35), 0 0 0 1px rgba(52, 49, 59, 0.04);
}
.st-key-nav [data-testid="stHorizontalBlock"] { flex-wrap: wrap; justify-content: center; gap: 0.15rem; }
.st-key-nav [data-testid="stColumn"] { width: auto !important; flex: 0 0 auto !important; min-width: 0 !important; }
.st-key-nav button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  min-height: 0 !important;
  padding: 0.45rem 0.95rem !important;
  border-radius: 12px !important;
}
.st-key-nav button p { font-size: 0.86rem !important; color: var(--muted) !important; font-weight: 500 !important; }
.st-key-nav button:hover p { color: var(--charcoal) !important; }
.st-key-nav [data-testid="stBaseButton-primary"] { background: rgba(201, 185, 232, 0.55) !important; }
.st-key-nav [data-testid="stBaseButton-primary"] p { color: var(--charcoal) !important; font-weight: 600 !important; }

/* ---------- Glass cards (any container whose key starts with "glass") ---------- */
[class*="st-key-glass"] {
  background: var(--glass);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
  backdrop-filter: blur(16px) saturate(140%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 22px;
  padding: 1.4rem 1.4rem 1.2rem;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    0 0 0 1px rgba(52, 49, 59, 0.04),
    0 22px 44px -30px rgba(52, 49, 59, 0.35);
  transition: transform 0.35s ease, box-shadow 0.35s ease;
}
/* Cards in the same row share one height, with their button at the bottom. */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-glass-card"]) {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
}
[class*="st-key-glass-card"] { flex: 1 1 auto; }
[class*="st-key-glass-card"] > [data-testid="stElementContainer"]:last-child { margin-top: auto; }
[class*="st-key-glass-card"]:hover {
  transform: translateY(-3px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    0 0 0 1px rgba(52, 49, 59, 0.05),
    0 28px 50px -30px rgba(52, 49, 59, 0.42);
}

/* ---------- Buttons ---------- */
.stButton button { border-radius: 12px; transition: all 0.2s ease; }
[data-testid="stBaseButton-secondary"] {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(52, 49, 59, 0.14);
  color: var(--charcoal);
}
[data-testid="stBaseButton-secondary"]:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: #B7A4DD;
  color: var(--charcoal);
}
[data-testid="stBaseButton-primary"] {
  background: linear-gradient(180deg, #D6C9EF 0%, #C2B0E4 100%);
  border: 1px solid rgba(255, 255, 255, 0.7);
  color: var(--charcoal);
  padding: 0.6rem 1.5rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65), 0 12px 26px -14px rgba(130, 105, 190, 0.75);
}
[data-testid="stBaseButton-primary"]:hover {
  background: linear-gradient(180deg, #DDD1F2 0%, #BBA7E0 100%);
  border-color: rgba(255, 255, 255, 0.9);
  color: var(--charcoal);
  transform: translateY(-1px);
}
[data-testid="stBaseButton-primary"] p { color: var(--charcoal); font-weight: 600; letter-spacing: 0.01em; }
[data-testid="stBaseButton-tertiary"] p { color: var(--muted); }
[data-testid="stBaseButton-tertiary"]:hover p { color: var(--charcoal); }

/* ---------- Inputs ---------- */
[data-testid="stWidgetLabel"] p {
  font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--muted);
}
[data-testid="stTextArea"] [data-baseweb="textarea"] {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(52, 49, 59, 0.12);
  border-radius: 14px;
}
[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within {
  border-color: #B7A4DD;
  box-shadow: 0 0 0 4px rgba(201, 185, 232, 0.3);
}
[data-testid="stTextArea"] textarea {
  background: transparent;
  color: var(--charcoal);
  font-size: 1rem;
  line-height: 1.65;
}
/* Pills (the small option buttons, e.g. creative intent) */
button[data-variant="pills"] {
  background: rgba(255, 255, 255, 0.6) !important;
  border: 1px solid rgba(52, 49, 59, 0.12) !important;
  border-radius: 10px !important;
  color: var(--charcoal) !important;
}
button[data-variant="pills"]:hover { border-color: #B7A4DD !important; }
button[data-variant="pills"][aria-checked="true"] {
  background: rgba(201, 185, 232, 0.5) !important;
  border-color: #B7A4DD !important;
  color: var(--charcoal) !important;
  font-weight: 600;
}
button[data-variant="pills"] * { color: inherit !important; }

/* ---------- Dialog ---------- */
/* The pop-up box is the element that directly wraps the dialog section.
   (Never write HTML tags inside this CSS: Streamlit's sanitiser would
   then remove the whole style block.) */
[data-testid="stDialog"] > div {
  background: rgba(248, 246, 242, 0.94) !important;
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.85);
  border-radius: 24px !important;
}
[role="dialog"] h2,
[role="dialog"] h2 * {
  font-family: var(--serif) !important;
  font-weight: 500 !important;
  font-size: 1.1rem !important;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted) !important;
}

/* ---------- Hero ---------- */
.hero {
  position: relative;
  height: 340px;
  display: flex; align-items: center; justify-content: center;
  text-align: center;
  overflow: hidden;
  margin-top: 0.4rem;
}
.hero-copy { position: relative; z-index: 2; }
.wordmark {
  font-family: var(--serif);
  font-weight: 500;
  font-size: clamp(3.6rem, 10vw, 6.6rem);
  letter-spacing: 0.34em;
  padding-left: 0.34em;
  line-height: 1;
  color: var(--charcoal);
  margin: 0.9rem 0 0.2rem;
}
.tagline {
  font-family: var(--serif);
  font-style: italic;
  font-size: clamp(1.2rem, 2.4vw, 1.55rem);
  color: var(--muted);
}
.orbit-line {
  position: absolute; left: 50%; top: 50%;
  border: 1px solid rgba(52, 49, 59, 0.08);
  border-radius: 50%;
}
.hero-planet { position: absolute; z-index: 1; }
.star {
  position: absolute; width: 3px; height: 3px; border-radius: 50%;
  background: rgba(52, 49, 59, 0.28);
  animation: twinkle 5s ease-in-out infinite;
}

/* ---------- Planets ---------- */
.planet {
  position: relative;
  width: var(--size);
  height: var(--size);
  flex-shrink: 0;
  animation: drift 9s ease-in-out infinite;
}
.planet .sphere {
  position: absolute; inset: 0; border-radius: 50%; z-index: 1;
  background:
    radial-gradient(circle at 30% 26%, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.35) 14%, rgba(255, 255, 255, 0) 34%),
    radial-gradient(circle at 38% 36%, var(--c1) 0%, var(--c2) 78%, color-mix(in srgb, var(--c2) 72%, #34313B) 100%);
  box-shadow:
    inset -8px -12px 22px rgba(52, 49, 59, 0.2),
    inset 4px 6px 12px rgba(255, 255, 255, 0.45),
    0 22px 36px -18px color-mix(in srgb, var(--c2) 85%, transparent);
}
.planet .ring {
  position: absolute; left: -32%; top: 37%;
  width: 164%; height: 26%;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.88);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--c2) 40%, transparent);
  transform: rotate(-18deg);
}
.planet .ring.back { z-index: 0; }
.planet .ring.front { z-index: 2; clip-path: inset(50% 0 0 0); }

/* ---------- World cards ---------- */
.world-card { display: flex; flex-direction: column; gap: 0.15rem; }
.planet-stage { height: 128px; display: flex; align-items: center; justify-content: center; margin-bottom: 0.4rem; }
.world-name { font-family: var(--serif); font-weight: 500; font-size: 1.5rem; line-height: 1.15; color: var(--charcoal); }
.world-desc { color: var(--muted); font-size: 0.88rem; line-height: 1.55; margin: 0.35rem 0 0; }

.swatches { display: flex; gap: 6px; margin-top: 0.75rem; }
.swatch { width: 22px; height: 22px; border-radius: 7px; border: 1px solid rgba(52, 49, 59, 0.1); }
.swatches-lg { display: flex; gap: 10px; flex-wrap: wrap; }
.swatch-lg { display: flex; flex-direction: column; gap: 5px; font-size: 0.68rem; letter-spacing: 0.04em; color: var(--muted); }
.swatch-lg i { display: block; width: 56px; height: 42px; border-radius: 10px; border: 1px solid rgba(52, 49, 59, 0.1); }

.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  font-size: 0.76rem; padding: 0.3rem 0.65rem; border-radius: 8px;
  background: rgba(255, 255, 255, 0.65); border: 1px solid var(--line); color: var(--charcoal);
}
.badge {
  display: inline-flex; align-items: center; gap: 0.45rem;
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
  padding: 0.38rem 0.75rem; border-radius: 999px;
  background: rgba(201, 185, 232, 0.32); color: var(--charcoal);
}
.badge::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: #A895D2; }

.field { margin-top: 1.05rem; }
.field-label { font: 600 0.68rem/1.2 var(--sans); letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.4rem; }
.field-value { font-size: 0.95rem; line-height: 1.6; color: var(--charcoal); }
.prompt { font-family: var(--serif); font-size: 1.28rem; line-height: 1.4; color: var(--charcoal); }

.note {
  font-size: 0.84rem; line-height: 1.55; color: var(--muted);
  padding: 0.75rem 1rem;
  border-left: 2px solid var(--lavender);
  background: rgba(255, 255, 255, 0.45);
  border-radius: 0 12px 12px 0;
}

.result-planet { display: flex; align-items: center; justify-content: center; min-height: 240px; }
.reveal { animation: rise 0.7s ease both; }

/* ---------- Mood Lab ---------- */
.quote {
  font-family: var(--serif); font-style: italic; font-size: 1.2rem; line-height: 1.5;
  color: var(--charcoal); border-left: 2px solid var(--blush); padding-left: 1rem; margin: 0.6rem 0 1rem;
}
.stats { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.stat {
  padding: 0.65rem 1rem; border-radius: 12px;
  background: rgba(255, 255, 255, 0.65); border: 1px solid var(--line);
  font-size: 0.74rem; letter-spacing: 0.06em; color: var(--muted);
}
.stat b { display: block; font-family: var(--serif); font-size: 1.5rem; font-weight: 500; color: var(--charcoal); letter-spacing: 0; }
.ph-row {
  display: grid; grid-template-columns: 150px 1fr 110px; gap: 1rem; align-items: center;
  padding: 0.7rem 0; border-bottom: 1px dashed var(--line); font-size: 0.86rem;
}
.ph-bar {
  height: 8px; border-radius: 6px;
  background: linear-gradient(90deg, rgba(201, 185, 232, 0.18), rgba(201, 185, 232, 0.5), rgba(201, 185, 232, 0.18));
  background-size: 200% 100%;
  animation: shimmer 2.6s linear infinite;
}
.ph-state { font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); text-align: right; }
.emo-row {
  display: grid; grid-template-columns: 130px 1fr 48px; gap: 1rem; align-items: center;
  padding: 0.55rem 0; border-bottom: 1px solid var(--line); font-size: 0.88rem;
}
.emo-track { height: 8px; border-radius: 6px; background: rgba(52, 49, 59, 0.06); overflow: hidden; }
.emo-track i {
  display: block; height: 100%; border-radius: 6px;
  background: linear-gradient(90deg, var(--blue), var(--lavender), var(--blush));
  animation: grow 0.9s ease both;
  transform-origin: left;
}
.emo-pct { text-align: right; font-variant-numeric: tabular-nums; color: var(--muted); font-size: 0.82rem; }
.steps { list-style: none; padding: 0; margin: 0.8rem 0 0; counter-reset: step; }
.steps li { counter-increment: step; display: flex; gap: 0.8rem; padding: 0.6rem 0; color: var(--muted); font-size: 0.9rem; line-height: 1.5; }
.steps li::before {
  content: counter(step, decimal-leading-zero);
  font: 600 0.72rem/1.9 var(--sans); letter-spacing: 0.1em; color: #8E7BBF;
}
.steps b { color: var(--charcoal); font-weight: 600; }

/* ---------- Vending machine ---------- */
.machine-window {
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.5), rgba(201, 185, 232, 0.12));
  border: 1px solid rgba(255, 255, 255, 0.85);
  height: 10px; margin: 0.2rem 0 0.6rem;
}
.capsule-slot { display: flex; flex-direction: column; align-items: center; gap: 0.55rem; padding: 0.6rem 0 0.2rem; }
.capsule {
  position: relative; width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(180deg, var(--c) 0 50%, rgba(255, 255, 255, 0.78) 50% 100%);
  border: 1px solid rgba(255, 255, 255, 0.95);
  box-shadow:
    inset -6px -8px 14px rgba(52, 49, 59, 0.15),
    inset 4px 5px 10px rgba(255, 255, 255, 0.6),
    0 16px 26px -16px rgba(52, 49, 59, 0.5);
  transition: transform 0.4s ease, opacity 0.4s ease, box-shadow 0.4s ease;
  animation: drift 8s ease-in-out infinite;
}
.capsule::before {
  content: ""; position: absolute; left: 3%; right: 3%; top: 50%; height: 1px;
  background: rgba(52, 49, 59, 0.14);
}
.capsule::after {
  content: ""; position: absolute; top: 11%; left: 22%; width: 30%; height: 16%;
  border-radius: 50%; background: rgba(255, 255, 255, 0.75); filter: blur(1px);
}
.capsule.selected {
  transform: scale(1.08);
  box-shadow:
    inset -6px -8px 14px rgba(52, 49, 59, 0.15),
    inset 4px 5px 10px rgba(255, 255, 255, 0.6),
    0 0 0 6px rgba(201, 185, 232, 0.35),
    0 18px 30px -16px rgba(52, 49, 59, 0.55);
}
.capsule.dim { opacity: 0.4; }
.capsule-num { font: 600 0.68rem/1 var(--sans); letter-spacing: 0.2em; color: var(--muted); }

/* ---------- Soundspace ---------- */
.wave { display: flex; align-items: flex-end; gap: 3px; height: 30px; margin-bottom: 0.9rem; }
.wave span {
  width: 3px; border-radius: 2px; background: var(--c);
  transform-origin: bottom;
  animation: pulse 2.4s ease-in-out infinite;
}
.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin-top: 1rem; }

/* ---------- Universe ---------- */
.orbit-map { position: relative; height: 320px; margin: 0.5rem 0 1rem; }
.orbit-path {
  position: absolute; left: 10%; right: 10%; top: 16%; bottom: 16%;
  border: 1px dashed rgba(52, 49, 59, 0.16); border-radius: 50%;
}
.orbit-core {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
  width: 150px; height: 150px; border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: radial-gradient(circle, rgba(201, 185, 232, 0.45) 0%, rgba(201, 185, 232, 0.12) 55%, transparent 72%);
  text-align: center;
}
.orbit-core b { font-family: var(--serif); font-weight: 500; font-size: 2.2rem; line-height: 1; }
.orbit-core span { font-size: 0.68rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-top: 0.3rem; }
.orbit-stop {
  /* -23px = half the planet size, so the planet (not its label) sits on the orbit */
  position: absolute; transform: translate(-50%, -23px);
  display: flex; flex-direction: column; align-items: center; gap: 0.35rem;
}
.orbit-stop small { font-size: 0.7rem; color: var(--muted); white-space: nowrap; }

.empty { text-align: center; padding: 2.4rem 1rem 1.2rem; }
.empty .planet { margin: 0 auto 1.4rem; }

/* ---------- Footer ---------- */
.footer {
  margin-top: 4rem; padding-top: 1.4rem; border-top: 1px solid var(--line);
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
  font-size: 0.74rem; letter-spacing: 0.06em; color: var(--muted);
}

/* ---------- Animations ---------- */
@keyframes drift { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
@keyframes shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }
@keyframes twinkle { 0%, 100% { opacity: 0.25; } 50% { opacity: 0.8; } }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes pulse { 0%, 100% { transform: scaleY(0.55); } 50% { transform: scaleY(1); } }

@media (prefers-reduced-motion: reduce) {
  .planet, .capsule, .star, .ph-bar, .wave span, .reveal, .emo-track i { animation: none !important; }
}

/* ---------- Small screens ---------- */
@media (max-width: 640px) {
  .hero { height: 290px; }
  .hide-sm { display: none; }
  .hero-big { right: 4% !important; top: 2% !important; transform: scale(0.55); transform-origin: top right; }
  .wordmark { letter-spacing: 0.22em; padding-left: 0.22em; }
  .ph-row { grid-template-columns: 1fr; gap: 0.4rem; }
  .ph-state { text-align: left; }
  .topbar-meta { display: none; }
}
"""


# Styles for the features added in v0.3 (companion, safety, calm room,
# journal, AI lab, care and the arcade vending machine).
EXTRA_CSS = """
/* ---------- Navigation with many pages ---------- */
.st-key-nav button { padding: 0.42rem 0.75rem !important; }
.st-key-nav button p { font-size: 0.82rem !important; }

/* ---------- Companion ---------- */
.companion-card { display: flex; gap: 1rem; align-items: flex-start; }
.companion-avatar {
  flex-shrink: 0; width: 46px; height: 46px; border-radius: 50%; margin-top: 0.2rem;
  background: radial-gradient(circle at 32% 28%, #FFFFFF 0%, rgba(255,255,255,0) 30%),
              radial-gradient(circle at 40% 40%, #E6DCF6 0%, #A895D2 80%);
  box-shadow: 0 0 0 6px rgba(201, 185, 232, 0.25), 0 10px 20px -10px rgba(140, 115, 200, 0.8);
  animation: drift 7s ease-in-out infinite;
}
.stApp p.companion-text {
  font-family: var(--serif); font-size: 1.32rem; line-height: 1.5; color: var(--charcoal); margin: 0.35rem 0 0.6rem;
}
.mode-badge {
  display: inline-block; font-size: 0.66rem; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--muted); border: 1px solid var(--line); border-radius: 999px; padding: 0.2rem 0.6rem;
}
.understood { font-size: 0.86rem; color: var(--muted); margin: 0.7rem 0 0; }
[data-testid="stChatMessage"] {
  background: rgba(255, 255, 255, 0.55); border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 18px; padding: 0.9rem 1rem; margin-bottom: 0.6rem;
  box-shadow: 0 14px 30px -26px rgba(52, 49, 59, 0.4);
}
[data-testid="stChatMessage"] p { font-size: 0.98rem; line-height: 1.6; }
.chat-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-top: 0.2rem; }
.chat-chips .tag { font-size: 0.7rem; padding: 0.18rem 0.5rem; }
.chat-understood { font-size: 0.74rem; color: var(--muted); }
[data-testid="stChatInput"] textarea { font-family: var(--sans); }

/* ---------- Safety ---------- */
.safety-card {
  border-radius: 20px; padding: 1.3rem 1.4rem; margin: 0.4rem 0 1rem;
  background: linear-gradient(135deg, rgba(235, 203, 215, 0.55), rgba(201, 185, 232, 0.45));
  border: 1px solid rgba(255, 255, 255, 0.85);
  box-shadow: 0 20px 40px -30px rgba(52, 49, 59, 0.45);
}
.safety-card.concern { background: rgba(255, 255, 255, 0.6); border-left: 3px solid #C695AA; }
.safety-card .body { color: var(--charcoal); }
.helplines { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.7rem; margin-top: 0.8rem; }
.helpline {
  display: flex; flex-direction: column; gap: 0.15rem; text-decoration: none; color: var(--charcoal);
  background: rgba(255, 255, 255, 0.8); border: 1px solid var(--line); border-radius: 14px; padding: 0.8rem 1rem;
}
.helpline:hover { border-color: #B7A4DD; }
.helpline-name { font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
.helpline b { font-family: var(--serif); font-size: 1.7rem; font-weight: 600; line-height: 1.1; }
.helpline small { font-size: 0.74rem; color: var(--muted); }

/* ---------- Explainable AI ---------- */
.stApp p.why-text { font-family: var(--serif); font-size: 1.35rem; line-height: 1.9; margin: 0.6rem 0 0.8rem; }
.why-word {
  border-radius: 6px; padding: 0.05rem 0.25rem;
  background: rgba(168, 149, 210, calc(0.15 + var(--w) * 0.6));
  box-shadow: 0 0 calc(var(--w) * 14px) rgba(168, 149, 210, 0.6);
}

/* ---------- Calm Room ---------- */
.breath { position: relative; height: 320px; display: flex; align-items: center; justify-content: center; }
.breath-halo {
  position: absolute; width: 280px; height: 280px; border-radius: 50%;
  border: 1px dashed rgba(52, 49, 59, 0.12);
}
.breath-orb {
  position: relative; width: 220px; height: 220px; transform: scale(0.62);
  --c1: #E6DCF6; --c2: #A895D2;
}
.breath-orb .sphere {
  position: absolute; inset: 0; border-radius: 50%;
  background:
    radial-gradient(circle at 30% 26%, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.3) 16%, rgba(255,255,255,0) 36%),
    radial-gradient(circle at 40% 38%, var(--c1) 0%, var(--c2) 80%);
  box-shadow: inset -14px -18px 36px rgba(52,49,59,0.18), 0 0 60px rgba(201,185,232,0.75);
}
.breath-labels { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
.breath-label {
  position: absolute; font-family: var(--serif); font-size: 1.7rem; color: var(--charcoal); opacity: 0;
  text-shadow: 0 1px 12px rgba(255,255,255,0.9);
}
.calm-complete, .reframe-result {
  margin-top: 0.8rem; padding: 1rem 1.2rem; border-radius: 16px;
  background: rgba(199, 211, 192, 0.35); color: var(--charcoal); font-family: var(--serif); font-size: 1.2rem;
}
.reframe-result { background: rgba(255,255,255,0.6); font-family: var(--sans); font-size: 0.9rem; }
.reframe-bars { display: grid; gap: 0.6rem; margin-top: 0.4rem; }
.reframe-bars > div { display: grid; grid-template-columns: 130px 1fr 140px; gap: 0.8rem; align-items: center; }
.reframe-bars b { font-weight: 600; text-align: right; }
.trap {
  background: rgba(235, 203, 215, 0.3); border-radius: 12px; padding: 0.6rem 0.9rem; margin-bottom: 0.5rem;
  font-size: 0.86rem; color: var(--charcoal); line-height: 1.5;
}
.trap span { color: var(--muted); }
.jar { display: flex; flex-direction: column; align-items: center; margin: 1rem 0 0.4rem; }
.jar-lid { width: 110px; height: 16px; border-radius: 6px; background: linear-gradient(180deg, #E3D3B8, #CDAA78); }
.jar-glass {
  position: relative; width: 150px; height: 170px; border-radius: 22px 22px 34px 34px;
  background: linear-gradient(120deg, rgba(255,255,255,0.7), rgba(201,185,232,0.18));
  border: 2px solid rgba(255,255,255,0.95); box-shadow: inset 0 0 30px rgba(201,185,232,0.35);
}
.jar-star {
  position: absolute; width: 26px; height: 26px; border-radius: 50%;
  left: calc(20% + var(--i) * 22%); bottom: calc(14% + var(--i) * 18%);
  background: radial-gradient(circle, #FFF6DA 0%, #EED9B7 45%, rgba(238,217,183,0) 72%);
  animation: twinkle 3s ease-in-out infinite; animation-delay: calc(var(--i) * -1s);
}
.jar-label { margin-top: 0.4rem; font-size: 0.75rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }

/* ---------- Journal ---------- */
.galaxy {
  display: flex; flex-wrap: wrap; gap: 1.1rem 1.4rem; align-items: flex-end; padding: 1.2rem;
  border-radius: 18px; background: radial-gradient(ellipse at center, rgba(201,185,232,0.18), rgba(255,255,255,0) 70%);
}
.galaxy-star { display: flex; flex-direction: column; align-items: center; gap: 0.35rem; }
.galaxy-star small { font-size: 0.66rem; color: var(--muted); }
.legend { display: flex; flex-wrap: wrap; gap: 0.4rem 1rem; font-size: 0.76rem; color: var(--muted); margin-top: 0.6rem; }
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: var(--c); margin-right: 0.35rem; }
.insight { font-size: 0.95rem; line-height: 1.6; color: var(--charcoal); margin: 0.5rem 0 0; }
.entry-row .body { margin-top: 0.2rem; }

/* ---------- AI Lab ---------- */
.pipeline { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.7rem; margin: 0.4rem 0 0.6rem; }
.pipe-step {
  display: flex; flex-direction: column; gap: 0.2rem; padding: 0.9rem 1rem; border-radius: 16px;
  background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.85);
  box-shadow: 0 14px 30px -26px rgba(52,49,59,0.45);
}
.pipe-step span { font: 600 0.68rem var(--sans); letter-spacing: 0.14em; color: #8E7BBF; }
.pipe-step b { font-family: var(--serif); font-size: 1.2rem; font-weight: 500; }
.pipe-step small { font-size: 0.78rem; color: var(--muted); line-height: 1.4; }
.model-card { display: grid; gap: 0.5rem; }
.model-card div {
  display: grid; grid-template-columns: 130px 1fr; gap: 1rem; padding: 0.7rem 0; border-bottom: 1px solid var(--line);
  font-size: 0.9rem; color: var(--charcoal);
}
.model-card span { font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); padding-top: 0.15rem; }

/* ---------- Care ---------- */
.principles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.8rem; margin-bottom: 1.2rem; }
.principle {
  padding: 1rem 1.1rem; border-radius: 18px; background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85); box-shadow: 0 14px 30px -26px rgba(52,49,59,0.45);
}
.principle b { font-family: var(--serif); font-size: 1.25rem; font-weight: 500; }
.principle .body { margin-top: 0.35rem; font-size: 0.86rem; }

/* ---------- Arcade vending machine ---------- */
.vm {
  position: relative; max-width: 520px; margin: 0 auto 1.4rem; padding: 18px 18px 22px;
  border-radius: 32px; border: 1px solid rgba(255,255,255,0.8);
  background: linear-gradient(160deg, #F3EEFB 0%, #DCD0F1 48%, #C4B2E6 100%);
  box-shadow: inset 0 2px 0 rgba(255,255,255,0.9), inset 0 -10px 24px rgba(52,49,59,0.14),
              0 40px 70px -40px rgba(52,49,59,0.6);
}
.vm-marquee {
  position: relative; text-align: center; padding: 22px 16px 14px; border-radius: 20px;
  background: linear-gradient(180deg, #3B3743, #2B2831);
  box-shadow: inset 0 0 0 2px rgba(255,255,255,0.06), 0 6px 14px -8px rgba(0,0,0,0.6);
}
.vm-bulbs { position: absolute; left: 14px; right: 14px; top: 8px; display: flex; justify-content: space-between; }
.vm-bulbs span {
  width: 7px; height: 7px; border-radius: 50%; background: #F6E7CC;
  box-shadow: 0 0 8px rgba(246, 231, 204, 0.9); animation: bulb 1.6s steps(1) infinite;
}
.vm-bulbs span:nth-child(even) { animation-delay: -0.8s; background: #E6DCF6; box-shadow: 0 0 8px rgba(230,220,246,0.9); }
.vm-title {
  font-family: var(--serif); font-size: 1.9rem; letter-spacing: 0.32em; color: #F8F6F2; padding-left: 0.32em;
  text-shadow: 0 0 14px rgba(201, 185, 232, 0.7);
}
.vm-sub { font-size: 0.66rem; letter-spacing: 0.24em; text-transform: uppercase; color: rgba(248,246,242,0.55); }
.vm-window {
  position: relative; margin-top: 14px; padding: 14px; border-radius: 20px; overflow: hidden;
  border: 6px solid #F5F1FB;
  background: linear-gradient(180deg, rgba(255,255,255,0.62), rgba(226,218,242,0.5));
  box-shadow: inset 0 0 30px rgba(52,49,59,0.16), 0 2px 0 rgba(255,255,255,0.7);
}
.vm-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.vm-slot {
  position: relative; height: 118px; display: flex; flex-direction: column; align-items: center;
  justify-content: flex-end; padding-bottom: 6px; border-bottom: 4px solid rgba(255,255,255,0.95);
  box-shadow: 0 6px 8px -6px rgba(52,49,59,0.35);
}
.vm-slot .capsule { width: 56px; height: 56px; margin-bottom: 22px; z-index: 1; animation: none; }
.vm-coil {
  position: absolute; bottom: 30px; width: 78%; height: 13px; border-radius: 7px; opacity: 0.75;
  background: repeating-linear-gradient(110deg, rgba(140,135,160,0.95) 0 3px, rgba(255,255,255,0) 3px 9px);
}
.vm-label {
  font: 600 0.62rem var(--sans); letter-spacing: 0.08em; color: #F8F6F2;
  background: #34313B; border-radius: 6px; padding: 2px 7px;
}
.vm-slot.typed .vm-label { background: #8E7BBF; box-shadow: 0 0 10px rgba(142,123,191,0.8); }
.vm-slot.sold .capsule { visibility: hidden; }
.vm-slot.sold::before {
  content: "SOLD OUT"; position: absolute; top: 36%; font-family: 'VT323', monospace; font-size: 1.2rem;
  letter-spacing: 0.08em; color: rgba(52,49,59,0.5); transform: rotate(-8deg);
}
.vm-slot.picking .capsule { animation: vm-fall 1.5s cubic-bezier(0.55, 0, 0.75, 0.2) forwards; }
.vm-slot.picking .vm-coil { animation: vm-spin 0.35s linear 2; }
.vm-glare {
  position: absolute; inset: 0; pointer-events: none; z-index: 2;
  background: linear-gradient(115deg, rgba(255,255,255,0) 0 34%, rgba(255,255,255,0.5) 40%, rgba(255,255,255,0) 47%,
                                      rgba(255,255,255,0) 60%, rgba(255,255,255,0.25) 63%, rgba(255,255,255,0) 68%);
}
.vm-lower { display: flex; gap: 14px; margin-top: 16px; align-items: stretch; }
.vm-tray {
  position: relative; flex: 1; height: 90px; border-radius: 18px; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(180deg, #2B2831, #4A4553);
  box-shadow: inset 0 10px 20px rgba(0,0,0,0.5), 0 2px 0 rgba(255,255,255,0.6);
  transition: box-shadow 0.4s ease;
}
.vm-tray.glow { box-shadow: inset 0 10px 20px rgba(0,0,0,0.5), 0 0 0 3px rgba(201,185,232,0.8), 0 0 26px rgba(201,185,232,0.7); }
.vm-flap {
  position: absolute; top: 0; left: 0; right: 0; height: 24px; line-height: 24px; text-align: center;
  background: rgba(255,255,255,0.12); font-size: 0.6rem; letter-spacing: 0.4em; color: rgba(248,246,242,0.65);
}
.vm-tray .capsule { width: 52px; height: 52px; margin-top: 18px; animation: none; }
.vm-tray .capsule.arrive { animation: vm-arrive 0.7s cubic-bezier(0.3, 1.6, 0.6, 1) 1.35s both; }
.vm-coin {
  width: 78px; border-radius: 18px; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; background: linear-gradient(180deg, #FBF9FE, #E9E1F6); border: 1px solid rgba(255,255,255,0.9);
  font-size: 0.56rem; letter-spacing: 0.24em; color: var(--muted);
}
.vm-coin-slot { width: 8px; height: 34px; border-radius: 4px; background: #34313B; box-shadow: inset 0 2px 4px rgba(0,0,0,0.6); }
.vm-feet { display: flex; justify-content: space-between; padding: 0 40px; position: absolute; left: 0; right: 0; bottom: -12px; }
.vm-feet span { width: 54px; height: 12px; border-radius: 0 0 10px 10px; background: #A895D2; }

.vm-led {
  border-radius: 16px; padding: 14px 16px; min-height: 76px; margin-bottom: 0.6rem;
  background: linear-gradient(180deg, #2B2831, #34313B);
  box-shadow: inset 0 0 0 2px rgba(255,255,255,0.05), inset 0 8px 16px rgba(0,0,0,0.5);
  font-family: 'VT323', monospace; font-size: 1.9rem; line-height: 1; color: #DCD0F5; letter-spacing: 0.06em;
  text-shadow: 0 0 10px rgba(201, 185, 232, 0.65);
}
.vm-led small { display: block; margin-top: 6px; font-size: 1.05rem; color: rgba(220, 208, 245, 0.6); text-shadow: none; }
.vm-led.blink span { animation: led-blink 1.4s steps(1) infinite; }
.vm-tokens { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 0.7rem; }
.vm-tokens div { display: flex; gap: 6px; align-items: center; min-height: 26px; flex-wrap: wrap; }
.vm-tokens em { font-size: 0.82rem; color: var(--muted); }
.vm-token {
  width: 24px; height: 24px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #FFF7E2 0%, #EED9B7 45%, #CDAA78 100%);
  box-shadow: inset 0 -2px 3px rgba(0,0,0,0.15), 0 3px 6px -3px rgba(0,0,0,0.4);
  border: 1px solid rgba(205,170,120,0.6);
}
.st-key-vm-panel {
  padding: 1.1rem; border-radius: 24px;
  background: linear-gradient(170deg, #F6F2FC, #E6DDF5);
  border: 1px solid rgba(255,255,255,0.9);
  box-shadow: inset 0 2px 0 rgba(255,255,255,0.9), 0 30px 50px -36px rgba(52,49,59,0.55);
}
.st-key-vm-keypad [data-testid="stHorizontalBlock"] { gap: 0.55rem; }
.st-key-vm-keypad button {
  min-height: 54px !important; border-radius: 14px !important;
  background: linear-gradient(180deg, #FFFFFF, #ECE5F8) !important;
  border: 1px solid rgba(52,49,59,0.14) !important;
  box-shadow: 0 5px 0 #C4B5E2, 0 10px 16px -10px rgba(52,49,59,0.55) !important;
  transition: transform 0.08s ease, box-shadow 0.08s ease !important;
}
.st-key-vm-keypad button p { font-family: 'VT323', monospace !important; font-size: 1.6rem !important; color: var(--charcoal) !important; }
.st-key-vm-keypad button:active { transform: translateY(4px) !important; box-shadow: 0 1px 0 #C4B5E2 !important; }
.st-key-vm-keypad [data-testid="stBaseButton-primary"] { background: linear-gradient(180deg, #D6C9EF, #B9A5E0) !important; }
.st-key-vm-coinbtns button { min-height: 46px !important; border-radius: 999px !important; }
.st-key-vm-coinbtns [data-testid="stBaseButton-primary"] {
  background: linear-gradient(180deg, #FFF3D6, #E7C98F) !important; border-color: rgba(205,170,120,0.7) !important;
  box-shadow: 0 4px 0 #CDAA78, 0 10px 16px -10px rgba(52,49,59,0.5) !important;
}
.st-key-vm-coinbtns button:active { transform: translateY(3px) !important; }
.st-key-vm-push button {
  min-height: 58px !important; font-size: 1.05rem !important;
  animation: push-pulse 1.6s ease-in-out infinite;
}
.st-key-sfx { position: absolute !important; width: 1px; height: 1px; overflow: hidden; opacity: 0; pointer-events: none; }

@keyframes vm-fall {
  0% { transform: translate(0, 0) rotate(0); }
  25% { transform: translate(0, -3px) rotate(-8deg); }
  40% { transform: translate(0, -6px) rotate(10deg); }
  100% { transform: translate(0, 460px) rotate(200deg); }
}
@keyframes vm-spin { to { background-position: 18px 0; } }
@keyframes vm-arrive { from { transform: translateY(-70px) rotate(-30deg); opacity: 0; } to { transform: none; opacity: 1; } }
@keyframes bulb { 0% { opacity: 1; } 50% { opacity: 0.35; } }
@keyframes led-blink { 0% { opacity: 1; } 50% { opacity: 0.45; } }
@keyframes push-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(201,185,232,0.0); } 50% { box-shadow: 0 0 0 8px rgba(201,185,232,0.45); } }

@media (prefers-reduced-motion: reduce) {
  .companion-avatar, .breath-orb, .breath-label, .jar-star, .vm-bulbs span, .vm-led span, .st-key-vm-push button,
  .vm-slot.picking .capsule, .vm-tray .capsule.arrive { animation: none !important; }
  .breath-label-0 { opacity: 1; }
}
@media (max-width: 640px) {
  .vm { padding: 12px 12px 18px; border-radius: 26px; }
  .vm-title { font-size: 1.4rem; }
  .vm-slot { height: 104px; }
  .vm-slot .capsule { width: 46px; height: 46px; }
  .reframe-bars > div { grid-template-columns: 1fr; gap: 0.3rem; }
  .model-card div { grid-template-columns: 1fr; gap: 0.2rem; }
}
"""


def load_css(extra=""):
    """Add ORBIT's design rules to the page (plus any extra generated CSS)."""
    st.html(f"<style>{CSS}\n{EXTRA_CSS}\n{extra}</style>")

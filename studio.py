"""
studio.py
Tools -> Mood Studio: palettes and moodboards (palette.py) and music discovery
(music.py). Both are rule-based, so the method can be explained step by step.

Crisis rule: if the last check-in (or the typed vibe) contains crisis wording,
the studio shows ONLY the safety response. Nothing typed here is saved.
"""
import hashlib
from datetime import date

import streamlit as st

import palette
import storage
from components import esc, note, section_header
from safety import check as safety_check
from safety import safety_card_html

PATTERN_CSS = {   # texture name -> a CSS background built only from gradients (no images)
    "soft grain": "radial-gradient(circle at 20% 30%, {b}55 0 12%, transparent 13%), "
                  "radial-gradient(circle at 70% 60%, {a}44 0 18%, transparent 19%), {bg}",
    "linen": "repeating-linear-gradient(0deg, {a}22 0 2px, transparent 2px 6px), "
             "repeating-linear-gradient(90deg, {b}22 0 2px, transparent 2px 6px), {bg}",
    "watercolour wash": "radial-gradient(ellipse at 30% 40%, {a}aa, transparent 60%), "
                        "radial-gradient(ellipse at 70% 70%, {b}aa, transparent 55%), {bg}",
    "halftone dots": "radial-gradient({c} 22%, transparent 24%) 0 0 / 16px 16px, {a}",
    "bold stripes": "repeating-linear-gradient(45deg, {a} 0 14px, {c} 14px 28px)",
    "confetti": "radial-gradient(circle at 15% 25%, {a} 0 6px, transparent 7px), "
                "radial-gradient(circle at 60% 40%, {b} 0 5px, transparent 6px), "
                "radial-gradient(circle at 35% 75%, {c} 0 7px, transparent 8px), "
                "radial-gradient(circle at 80% 80%, {a} 0 4px, transparent 5px), {bg}",
    "film grain": "repeating-radial-gradient(circle at 50% 50%, {ink}11 0 1px, transparent 1px 3px), {b}",
    "old paper": "radial-gradient(ellipse at center, {bg}, {b}88), {bg}",
    "ticket stubs": "repeating-linear-gradient(90deg, {a} 0 30px, {bg} 30px 34px)",
    "fine grid": "linear-gradient({ink}22 1px, transparent 1px) 0 0 / 18px 18px, "
                 "linear-gradient(90deg, {ink}22 1px, transparent 1px) 0 0 / 18px 18px, {bg}",
    "frosted glass": "linear-gradient(135deg, #ffffffaa, #ffffff22), linear-gradient(135deg, {a}, {b})",
    "clean gradient": "linear-gradient(135deg, {a}, {c})",
}


def blocked(text=""):
    """True (and shows the safety response) if the last check-in or this text is a crisis."""
    last = st.session_state.get("home_result")
    if (last and last.get("safety") == "crisis") or (text and safety_check(text) == "crisis"):
        st.html(safety_card_html("crisis"))
        return True
    return False


def save_stars(kind, target, key, offset=1):
    """st.feedback('stars') gives 0-4; store 1-5. Changing your mind replaces the old rating."""
    saved = st.session_state.setdefault("rating_ids", {})
    if key in saved:
        storage.delete_rating(saved.pop(key))
    value = st.session_state.get(key)
    if value is not None:
        saved[key] = storage.add_rating(kind, target, int(value) + offset)


# ---------------------------------------------------------------
# Palettes and moodboards
# ---------------------------------------------------------------
def refine_click(action):
    if action == "reset":
        st.session_state.studio_tweaks = {}
    else:
        st.session_state.studio_tweaks = palette.refine(st.session_state.get("studio_tweaks", {}), action)


def moodboard_html(result, fonts, tiles, keywords):
    c = {x["role"]: x["hex"] for x in result["colours"]}
    fill = {"a": c["Primary"], "b": c["Harmony A"], "c": c["Harmony B"], "bg": c["Background"], "ink": c["Ink (text)"]}
    pattern_tiles = "".join(
        f'<div class="mb-tile mb-pattern" style="background:{PATTERN_CSS[name].format(**fill)}">'
        f'<span>{esc(name)}</span></div>' for name in tiles)
    def label_colour(background):        # ink or white, whichever is easier to read on this swatch
        ink = c["Ink (text)"]
        return ink if palette.contrast(ink, background) >= palette.contrast("#FFFFFF", background) else "#FFFFFF"
    swatches = "".join(
        f'<div class="mb-swatch" style="background:{x["hex"]};color:{label_colour(x["hex"])}">'
        f'<b>{esc(x["name"])}</b><small>{x["hex"]}</small></div>' for x in result["colours"])
    chips = "".join(f'<span style="border-color:{c["Ink (text)"]}33">{esc(k)}</span>' for k in keywords[:6])
    return (
        f'<div class="moodboard" style="background:{c["Background"]};color:{c["Ink (text)"]}">'
        f'<div class="mb-tile mb-hero" style="background:linear-gradient(135deg,{c["Primary"]},{c["Harmony A"]} 55%,'
        f'{c["Harmony B"]})"></div>'
        f'<div class="mb-tile mb-type" style="background:{c["Background"]};border:1px solid {c["Ink (text)"]}22">'
        f'<div style="font-family:\'{fonts["heading"]}\',serif;font-size:2.1rem;line-height:1.05">Every feeling has a '
        f'universe</div><p style="font-family:\'{fonts["body"]}\',sans-serif;margin:.5rem 0 0;font-size:.9rem">'
        f'{esc(fonts["heading"])} for headings, {esc(fonts["body"])} for text: {esc(fonts["feel"])}.</p></div>'
        f'{pattern_tiles}<div class="mb-tile mb-words">{chips}</div>'
        f'<div class="mb-swatches">{swatches}</div></div>'
    )


def palette_section():
    last = st.session_state.get("home_result")
    has_checkin = bool(last and last.get("safety") != "crisis")
    with st.container(key="glass-studio-input"):
        source = st.radio("Start from", ["My last check-in", "A vibe I describe"], horizontal=True,
                          key="studio_source", index=0 if has_checkin else 1)
        vibe = ""
        if source == "A vibe I describe" or not has_checkin:
            vibe = st.text_input("Describe a vibe in a few words", key="studio_vibe", max_chars=80,
                                 placeholder="e.g. rainy Sunday cafe, nostalgic")
        if blocked(vibe):
            return
        a, b = st.columns(2)
        warm_cool = a.slider("Warm ↔ Cool", -1.0, 1.0, 0.0, 0.1, key="studio_warm")
        calm_energy = b.slider("Calm ↔ Energetic", -1.0, 1.0, 0.0, 0.1, key="studio_energy")
        soft_bold = a.slider("Soft ↔ Bold", -1.0, 1.0, 0.0, 0.1, key="studio_bold")
        vintage_modern = b.slider("Vintage ↔ Modern", -1.0, 1.0, 0.0, 0.1, key="studio_vintage")
        harmony = st.selectbox("Colour harmony", ["Auto", "analogous", "complementary", "triadic"], key="studio_rule")

    if source == "My last check-in" and has_checkin:
        valence, arousal = palette.blend_va(last["emotions"])
        warm = bold = vintage = 0.0
        keywords = [label for label, score in last["emotions"][:3]]
        target = last["final"]["emotion"]
        origin = f"your last check-in ({', '.join(keywords)})"
    elif vibe.strip():
        valence, arousal, warm, bold, vintage, found = palette.vibe_profile(vibe)
        keywords = found or ["your vibe"]
        target = "vibe"
        origin = f"the vibe words {', '.join(found)}" if found else "your vibe (no known keywords, so a neutral start)"
    else:
        st.html('<p class="body">Do a check-in on Today, or describe a vibe above, to make a palette.</p>')
        return

    # Sliders add to what the feeling/vibe suggested. Left = warm/calm/soft/vintage.
    warm, bold, vintage = warm - warm_cool, bold + soft_bold, vintage - vintage_modern
    signature = hashlib.md5(f"{source}|{vibe}|{target}".encode()).hexdigest()
    if st.session_state.get("studio_signature") != signature:      # new feeling or vibe -> forget old refinements
        st.session_state.studio_signature, st.session_state.studio_tweaks = signature, {}
    tweaks = st.session_state.get("studio_tweaks", {})
    result = palette.make_palette(valence, arousal, warm, calm_energy, bold, vintage, tweaks,
                                  None if harmony == "Auto" else harmony)
    fonts = palette.font_pair(vintage, bold, result["arousal"])
    tiles = palette.textures(result["arousal"], vintage)
    keywords = list(dict.fromkeys(keywords + tiles))

    st.html("<style>@import url('https://fonts.googleapis.com/css2?family="
            + fonts["heading"].replace(" ", "+") + "&family=" + fonts["body"].replace(" ", "+")
            + "&display=swap');</style>")
    st.html(moodboard_html(result, fonts, tiles, keywords))

    cols = st.columns(6)
    for col, (label, action) in zip(cols, [("More muted", "muted"), ("Warmer", "warmer"), ("Cooler", "cooler"),
                                           ("More contrast", "contrast"), ("More playful", "playful"),
                                           ("Reset", "reset")]):
        col.button(label, key=f"refine_{action}", on_click=refine_click, args=(action,), width="stretch")

    with st.container(key="glass-studio-checks"):
        st.html('<div class="eyebrow">Contrast check (WCAG)</div>' + "".join(
            f'<div class="check-row"><span>{esc(c["pair"])}</span><span>{c["ratio"]} : 1 '
            f'(needs {c["needed"]})</span><b>{"Pass" if c["passes"] else "Use for decoration only"}</b></div>'
            for c in result["checks"]))

    with st.expander("How this was made"):
        st.html(
            f'<p class="body">Started from {esc(origin)}.<br>'
            f'<b>1. Feeling → numbers:</b> valence (pleasant) {result["valence"]:+.2f}, arousal (energy) '
            f'{result["arousal"]:+.2f}, after the Calm ↔ Energetic slider.<br>'
            f'<b>2. Numbers → colour:</b> the feeling\'s angle on the valence-arousal circle gives hue '
            f'{result["hue"]}°; distance from neutral and energy give saturation {result["saturation"]}; '
            f'lightness {result["lightness"]}. Warm/Cool, Soft/Bold and Vintage/Modern shift these.<br>'
            f'<b>3. Harmony rule:</b> <b>{result["rule"]}</b> '
            + {"analogous": "(neighbouring hues, ±30°: calm and unified)",
               "complementary": "(the opposite hue as an accent: balanced)",
               "triadic": "(three hues 120° apart: lively and playful)"}[result["rule"]]
            + ".<br><b>4. Readability:</b> the ink colour is darkened until text on the background passes WCAG AA "
            "(4.5 : 1) and large text on the primary passes 3 : 1.<br>"
            f'<b>5. Fonts and textures:</b> chosen by the closest match to vintage {vintage:+.1f}, bold {bold:+.1f} '
            f'and energy {result["arousal"]:+.1f}. Refinements applied: {esc(tweaks or "none")}.</p>')

    name = f"orbit_palette_{date.today()}"
    a, b, c = st.columns(3)
    a.download_button("Download PNG", palette.png_board(result, fonts, keywords), file_name=f"{name}.png",
                      mime="image/png", width="stretch")
    b.download_button("CSS variables", palette.css_variables(result), file_name=f"{name}.css", mime="text/css",
                      width="stretch")
    c.download_button("JSON", palette.as_json(result, fonts, {"keywords": keywords}), file_name=f"{name}.json",
                      mime="application/json", width="stretch")

    left, right = st.columns([1.3, 1], vertical_alignment="center")
    left.html('<span class="feedback-label">Does this palette fit the vibe? (1-5 stars)</span>')
    with right:
        st.feedback("stars", key=f"fb_palette_{signature[:8]}", on_change=save_stars,
                    args=("palette_fit", target, f"fb_palette_{signature[:8]}"))


# ---------------------------------------------------------------
# The page
# ---------------------------------------------------------------
def studio_page():
    section_header("Mood Studio", "Your feeling, in colour and sound",
                   "Turn a check-in or a vibe into a palette and moodboard, or find music that fits. Everything "
                   "is made by simple rules you can see, and nothing you type here is saved.", first=True)
    if blocked():
        return
    part = st.segmented_control("Studio", ["Palettes & moodboards", "Music discovery"], key="studio_part",
                                default="Palettes & moodboards", label_visibility="collapsed")
    if part == "Music discovery":
        import music_ui   # loaded only when needed
        music_ui.music_section()
    else:
        palette_section()
    note("Mood Studio is for creativity and comfort. It isn't a treatment and it doesn't diagnose anything.")


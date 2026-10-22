"""
palette.py
Mood Studio: turning a feeling (or a vibe) into a colour palette. Rule-based,
so every step can be explained.

The method
1. Feeling -> two numbers (the "circumplex model of affect"):
     valence  = how pleasant (-1 unpleasant ... +1 pleasant)
     arousal  = how energetic (-1 calm ... +1 energetic)
   Each of the 28 emotions has an approximate (valence, arousal) pair, set by
   the author (EMOTION_VA below). A check-in's blend is the score-weighted average.
   A typed vibe ("rainy Sunday cafe, nostalgic") uses a small keyword table instead.
2. The feeling's ANGLE on that circle -> hue: joy is gold, excitement coral,
   anger crimson, fear purple, sadness blue, calm lavender, relief sage.
   Its DISTANCE from neutral and its arousal -> saturation (stronger, more
   energetic feelings get stronger colours). Valence nudges lightness.
3. Four sliders (warm-cool, calm-energetic, soft-bold, vintage-modern) adjust
   hue, saturation and lightness.
4. A colour-harmony rule picks the other hues: calm -> analogous (neighbours
   on the colour wheel), medium -> complementary (opposite), energetic or
   playful -> triadic (three evenly spaced).
5. Five colours: primary, two harmony colours, a light background and a dark
   ink. The ink is darkened until text on the background passes the WCAG AA
   contrast ratio (4.5 : 1).
"""
import colorsys
import io
import json
import math

# ---------------------------------------------------------------
# 1. Feelings and vibes -> (valence, arousal)
# ---------------------------------------------------------------
# Approximate positions on the circumplex (author's estimates, -1 to +1).
EMOTION_VA = {
    "admiration": (0.6, 0.3), "amusement": (0.7, 0.5), "anger": (-0.6, 0.8), "annoyance": (-0.4, 0.5),
    "approval": (0.5, 0.1), "caring": (0.6, 0.1), "confusion": (-0.2, 0.3), "curiosity": (0.3, 0.5),
    "desire": (0.4, 0.6), "disappointment": (-0.6, -0.2), "disapproval": (-0.4, 0.3), "disgust": (-0.7, 0.4),
    "embarrassment": (-0.4, 0.4), "excitement": (0.7, 0.8), "fear": (-0.7, 0.7), "gratitude": (0.7, 0.1),
    "grief": (-0.8, -0.3), "joy": (0.8, 0.6), "love": (0.8, 0.4), "nervousness": (-0.5, 0.6),
    "optimism": (0.6, 0.4), "pride": (0.6, 0.5), "realization": (0.1, 0.3), "relief": (0.5, -0.3),
    "remorse": (-0.6, -0.1), "sadness": (-0.7, -0.4), "surprise": (0.2, 0.7), "neutral": (0.0, 0.0),
}

# Vibe words: (valence, arousal, warm, bold, vintage) nudges. warm: +warm/-cool; bold: +bold/-soft; vintage: +vintage/-modern
VIBE_WORDS = {
    "rain": (-0.2, -0.4, -0.5, -0.3, 0.1), "rainy": (-0.2, -0.4, -0.5, -0.3, 0.1), "monsoon": (0.1, -0.2, -0.4, -0.2, 0.1),
    "sunday": (0.2, -0.4, 0.1, -0.3, 0.1), "lazy": (0.1, -0.6, 0.1, -0.4, 0.0), "cafe": (0.3, -0.2, 0.5, -0.1, 0.3),
    "coffee": (0.2, 0.0, 0.6, 0.0, 0.3), "chai": (0.4, -0.1, 0.7, -0.1, 0.3), "tea": (0.3, -0.3, 0.3, -0.3, 0.3),
    "nostalgic": (0.0, -0.3, 0.3, -0.2, 0.8), "nostalgia": (0.0, -0.3, 0.3, -0.2, 0.8), "vintage": (0.1, -0.1, 0.3, 0.0, 1.0),
    "retro": (0.3, 0.3, 0.4, 0.3, 0.9), "old": (0.0, -0.2, 0.2, -0.1, 0.7), "film": (0.0, -0.1, 0.2, 0.0, 0.6),
    "modern": (0.2, 0.2, -0.1, 0.2, -1.0), "minimal": (0.1, -0.3, -0.1, -0.4, -0.8), "clean": (0.3, -0.1, -0.2, -0.2, -0.7),
    "neon": (0.3, 0.8, -0.2, 0.9, -0.8), "cyber": (0.0, 0.7, -0.6, 0.8, -1.0), "city": (0.1, 0.4, -0.2, 0.3, -0.4),
    "night": (-0.1, -0.2, -0.6, 0.2, 0.0), "midnight": (-0.1, -0.1, -0.7, 0.3, 0.0), "moon": (0.1, -0.4, -0.5, -0.2, 0.2),
    "stars": (0.3, -0.2, -0.4, 0.0, 0.1), "sunset": (0.5, 0.1, 0.9, 0.2, 0.2), "sunrise": (0.6, 0.2, 0.7, 0.0, 0.0),
    "golden": (0.6, 0.2, 0.9, 0.2, 0.3), "summer": (0.7, 0.6, 0.7, 0.5, 0.0), "spring": (0.7, 0.3, 0.2, -0.2, 0.0),
    "autumn": (0.2, -0.2, 0.8, 0.1, 0.5), "winter": (0.0, -0.4, -0.8, -0.1, 0.1), "snow": (0.2, -0.4, -0.9, -0.4, 0.0),
    "beach": (0.7, 0.4, 0.3, 0.2, 0.0), "ocean": (0.3, 0.0, -0.7, 0.1, 0.0), "sea": (0.3, -0.1, -0.7, 0.0, 0.0),
    "forest": (0.3, -0.3, -0.1, 0.0, 0.2), "garden": (0.6, -0.1, 0.1, -0.3, 0.2), "mountain": (0.3, 0.0, -0.4, 0.2, 0.0),
    "desert": (0.2, 0.0, 0.9, 0.1, 0.3), "cosy": (0.6, -0.5, 0.7, -0.4, 0.3), "cozy": (0.6, -0.5, 0.7, -0.4, 0.3),
    "calm": (0.4, -0.7, 0.0, -0.4, 0.0), "chill": (0.4, -0.5, -0.2, -0.3, 0.0), "peaceful": (0.5, -0.7, 0.0, -0.4, 0.1),
    "dreamy": (0.5, -0.4, 0.1, -0.6, 0.2), "soft": (0.4, -0.4, 0.1, -0.8, 0.1), "pastel": (0.6, -0.2, 0.1, -0.9, 0.0),
    "bold": (0.2, 0.5, 0.1, 1.0, -0.2), "bright": (0.6, 0.5, 0.3, 0.6, -0.1), "dark": (-0.3, 0.1, -0.3, 0.6, 0.0),
    "moody": (-0.3, 0.0, -0.3, 0.4, 0.2), "gloomy": (-0.6, -0.3, -0.5, 0.0, 0.1), "sad": (-0.7, -0.4, -0.4, -0.1, 0.0),
    "happy": (0.8, 0.5, 0.4, 0.2, 0.0), "energetic": (0.5, 0.9, 0.2, 0.6, -0.2), "party": (0.7, 0.9, 0.3, 0.8, -0.2),
    "festival": (0.8, 0.8, 0.8, 0.7, 0.1), "diwali": (0.8, 0.6, 0.9, 0.6, 0.3), "holi": (0.9, 0.9, 0.5, 0.9, 0.0),
    "study": (0.1, -0.2, -0.2, -0.2, 0.0), "focus": (0.1, 0.0, -0.3, 0.0, -0.3), "library": (0.1, -0.4, 0.3, 0.0, 0.6),
    "romantic": (0.7, 0.2, 0.6, 0.0, 0.3), "love": (0.8, 0.3, 0.6, 0.1, 0.1), "angry": (-0.6, 0.8, 0.6, 0.9, 0.0),
    "storm": (-0.2, 0.7, -0.5, 0.8, 0.0), "fire": (0.2, 0.8, 1.0, 0.9, 0.0), "y2k": (0.5, 0.6, -0.2, 0.7, -0.6),
}


def blend_va(emotions):
    """Score-weighted average (valence, arousal) of a check-in's emotions."""
    total = sum(score for _, score in emotions) or 1.0
    valence = sum(EMOTION_VA[label][0] * score for label, score in emotions) / total
    arousal = sum(EMOTION_VA[label][1] * score for label, score in emotions) / total
    return valence, arousal


def vibe_profile(text):
    """Keywords found in a vibe -> (valence, arousal, warm, bold, vintage, matched words)."""
    words = [w.strip(".,!?;:'\"").lower() for w in text.split()]
    found = [w for w in words if w in VIBE_WORDS]
    if not found:
        return 0.0, 0.0, 0.0, 0.0, 0.0, []
    sums = [sum(VIBE_WORDS[w][i] for w in found) / len(found) for i in range(5)]
    return (*sums, found)


# ---------------------------------------------------------------
# 2-5. The palette
# ---------------------------------------------------------------
def clamp(x, low=0.0, high=1.0):
    return max(low, min(high, x))


def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, clamp(l), clamp(s))
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def hex_to_rgb(colour):
    colour = colour.lstrip("#")
    return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))


def luminance(colour):
    """WCAG relative luminance."""
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in hex_to_rgb(colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    """WCAG contrast ratio between two colours (1 to 21)."""
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# Where a feeling sits on the circumplex (its ANGLE) chooses the hue.
# angle: 0 = pleasant, 90 = energetic, 180 = unpleasant, 270 = calm.
HUE_ANCHORS = [(0, 45), (45, 20), (90, 330), (135, 350), (180, 220), (225, 240), (270, 270), (315, 140), (360, 45)]
#              gold     coral    pink-magenta crimson  blue      slate-blue lavender  sage      gold again


def feeling_hue(valence, arousal):
    """Hue (0-360) from the feeling's angle on the valence-arousal circle.
    Joy -> gold/coral, excitement -> coral/pink, anger and fear -> crimson/purple,
    sadness -> blue, tiredness -> slate, calm -> lavender, relief -> sage.
    A feeling right in the middle (neutral) gets ORBIT's lavender."""
    if math.hypot(valence, arousal) < 0.05:
        return 270.0
    angle = math.degrees(math.atan2(arousal, valence)) % 360
    for (a0, h0), (a1, h1) in zip(HUE_ANCHORS, HUE_ANCHORS[1:]):
        if a0 <= angle <= a1:
            t = (angle - a0) / (a1 - a0)
            step = (h1 - h0 + 180) % 360 - 180          # go the short way round the colour wheel
            return (h0 + step * t) % 360
    return 270.0


def shift_hue(hue, warm):
    """warm > 0 moves the hue towards orange (30 deg), < 0 towards blue (215 deg), by up to 45 degrees."""
    target = 30 if warm > 0 else 215
    difference = (target - hue + 180) % 360 - 180
    return (hue + max(-45, min(45, difference)) * min(1.0, abs(warm))) % 360


HARMONY = {"analogous": (-30, 30), "complementary": (180, 150), "triadic": (120, 240)}


def choose_harmony(arousal, playful=False):
    if playful or arousal > 0.45:
        return "triadic"
    if arousal < -0.1:
        return "analogous"
    return "complementary"


HUE_NAMES = [(15, "Rose"), (30, "Coral"), (45, "Apricot"), (60, "Honey"), (90, "Lime"), (150, "Sage"),
             (190, "Mint"), (220, "Sky"), (250, "Periwinkle"), (290, "Lavender"), (320, "Orchid"), (345, "Berry"),
             (360, "Rose")]


def colour_name(colour):
    """A friendly name from the colour's hue, lightness and saturation, e.g. 'Dusty Lavender'."""
    r, g, b = (c / 255 for c in hex_to_rgb(colour))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue = h * 360
    base = next(name for limit, name in HUE_NAMES if hue < limit)
    if s < 0.12:
        base = "Stone" if l > 0.35 else "Ink"
    if l > 0.9:
        adjective = "Whisper"
    elif l > 0.75:
        adjective = "Pale"
    elif l < 0.22:
        adjective = "Midnight"
    elif l < 0.38:
        adjective = "Deep"
    elif s < 0.3:
        adjective = "Dusty"
    elif s > 0.65:
        adjective = "Vivid"
    else:
        adjective = "Soft"
    return f"{adjective} {base}"


def make_palette(valence, arousal, warm=0.0, energy=0.0, bold=0.0, vintage=0.0, tweaks=None, harmony=None,
                 brightness=0.0):
    """Build the 5-colour palette. All inputs roughly -1..+1.

    energy: the calm-energetic slider; brightness: -1 dark ... +1 bright (Creator Mode); tweaks: the refine buttons
    (muted, warmth, contrast, playful). Returns a dict with colours, rule and contrast checks.
    """
    tweaks = tweaks or {}
    arousal_used = clamp(arousal + 0.6 * energy, -1, 1)
    hue = shift_hue(feeling_hue(valence, arousal_used), clamp(warm + tweaks.get("warmth", 0.0), -1, 1))
    strength = min(1.0, math.hypot(valence, arousal_used))   # how far from neutral: stronger -> more colourful
    saturation = 0.24 + 0.18 * strength + 0.16 * (arousal_used + 1) / 2 + 0.18 * bold - 0.14 * max(0.0, vintage)
    saturation *= tweaks.get("muted", 1.0)
    saturation = clamp(saturation + (0.1 if tweaks.get("playful") else 0.0), 0.08, 0.85)
    lightness = clamp(0.66 + 0.06 * valence + 0.08 * brightness - 0.08 * bold - 0.05 * tweaks.get("contrast", 0.0),
                      0.35, 0.82)
    rule = harmony or choose_harmony(arousal_used, tweaks.get("playful", False))
    first, second = HARMONY[rule]

    primary = hsl_to_hex(hue, saturation, lightness)
    harmony_a = hsl_to_hex(hue + first, saturation * 0.9, clamp(lightness + 0.08))
    harmony_b = hsl_to_hex(hue + second, saturation * (0.75 if rule == "complementary" else 0.9),
                           clamp(lightness - 0.1 + (0.04 if tweaks.get("playful") else 0)))
    background_hue = hue + (20 * vintage if vintage > 0 else 0)            # vintage paper is a little yellower
    background = hsl_to_hex(background_hue, clamp(0.25 * saturation + 0.12 * max(0, vintage)),
                            clamp(0.955 - 0.02 * max(0, vintage) + 0.02 * tweaks.get("contrast", 0.0), 0.88, 0.985))
    ink_lightness = 0.2 - 0.04 * tweaks.get("contrast", 0.0) - 0.03 * (vintage < 0) * abs(vintage)
    ink = hsl_to_hex(hue, 0.22, ink_lightness)
    while (contrast(ink, background) < 4.5 or contrast(ink, primary) < 3.0) and ink_lightness > 0.02:
        # WCAG AA: 4.5 for normal text on the background, 3 for large text on the primary colour
        ink_lightness -= 0.02
        ink = hsl_to_hex(hue, 0.22, ink_lightness)
    while contrast(ink, primary) < 3.0 and lightness < 0.95:
        # Even near-black text can't be read on a very dark primary: lighten the primary instead.
        lightness += 0.02
        primary = hsl_to_hex(hue, saturation, lightness)

    colours = [("Primary", primary), ("Harmony A", harmony_a), ("Harmony B", harmony_b),
               ("Background", background), ("Ink (text)", ink)]
    return {
        "colours": [{"role": role, "hex": hex_, "name": colour_name(hex_)} for role, hex_ in colours],
        "rule": rule, "hue": round(hue), "saturation": round(saturation, 2), "lightness": round(lightness, 2),
        "valence": round(valence, 2), "arousal": round(arousal_used, 2),
        "checks": contrast_checks(dict(colours)),
    }


def contrast_checks(colours):
    """Which text/background pairs pass WCAG (AA: 4.5 for normal text, 3 for large text)."""
    pairs = [("Ink on Background", colours["Ink (text)"], colours["Background"], 4.5),
             ("Ink on Primary", colours["Ink (text)"], colours["Primary"], 3.0),
             ("Ink on Harmony A", colours["Ink (text)"], colours["Harmony A"], 3.0),
             ("Primary on Background (large text, icons)", colours["Primary"], colours["Background"], 3.0)]
    return [{"pair": name, "ratio": round(contrast(a, b), 2), "needed": needed, "passes": contrast(a, b) >= needed}
            for name, a, b, needed in pairs]


# ---------------------------------------------------------------
# Font pairing and textures (rules on the same numbers)
# ---------------------------------------------------------------
def font_pair(vintage, bold, arousal, warmth=0.0):
    """Typography from data/fonts.csv (see fonts.py for the rule)."""
    import fonts   # local import: fonts.py reads a CSV with pandas
    return fonts.pair(vintage, bold, arousal, warmth)


TEXTURES = {
    "calm": ["soft grain", "linen", "watercolour wash"],
    "lively": ["halftone dots", "bold stripes", "confetti"],
    "vintage": ["film grain", "old paper", "ticket stubs"],
    "modern": ["fine grid", "frosted glass", "clean gradient"],
}


def textures(arousal, vintage):
    picks = TEXTURES["lively" if arousal > 0.3 else "calm"][:2]
    picks.append(TEXTURES["vintage" if vintage > 0.15 else "modern"][0 if vintage > 0.15 else 1])
    return picks


# ---------------------------------------------------------------
# Refine buttons: change the palette without re-explaining the vibe
# ---------------------------------------------------------------
def refine(tweaks, action):
    tweaks = dict(tweaks or {})
    if action == "muted":
        tweaks["muted"] = round(tweaks.get("muted", 1.0) * 0.8, 3)
    elif action == "warmer":
        tweaks["warmth"] = round(min(1.0, tweaks.get("warmth", 0.0) + 0.35), 2)
    elif action == "cooler":
        tweaks["warmth"] = round(max(-1.0, tweaks.get("warmth", 0.0) - 0.35), 2)
    elif action == "contrast":
        tweaks["contrast"] = round(min(3.0, tweaks.get("contrast", 0.0) + 1.0), 2)
    elif action == "playful":
        tweaks["playful"] = True
        tweaks["muted"] = round(min(1.4, tweaks.get("muted", 1.0) * 1.15), 3)
    return tweaks


# ---------------------------------------------------------------
# Exports
# ---------------------------------------------------------------
def css_variables(result):
    lines = [":root {"]
    for colour in result["colours"]:
        name = colour["role"].lower().replace(" (text)", "").replace(" ", "-")
        lines.append(f"  --orbit-{name}: {colour['hex']};   /* {colour['name']} */")
    lines.append("}")
    return "\n".join(lines)


def as_json(result, fonts, extra=None):
    data = {"palette": result["colours"], "harmony_rule": result["rule"],
            "valence": result["valence"], "arousal": result["arousal"], "fonts": fonts,
            "contrast_checks": result["checks"], "made_by": "ORBIT Mood Studio (rule-based)"}
    data.update(extra or {})
    return json.dumps(data, indent=2, ensure_ascii=False)


def png_board(result, fonts, keywords, width=1200, height=800):
    """A moodboard image: a gradient, a pattern, the five swatches with names and hex codes."""
    from PIL import Image, ImageDraw, ImageFont

    colours = [c["hex"] for c in result["colours"]]
    image = Image.new("RGB", (width, height), colours[3])
    draw = ImageDraw.Draw(image)
    try:
        title_font, small_font = ImageFont.load_default(size=34), ImageFont.load_default(size=20)
    except TypeError:          # very old Pillow
        title_font = small_font = ImageFont.load_default()

    # big gradient tile (primary -> harmony A)
    a, b = hex_to_rgb(colours[0]), hex_to_rgb(colours[1])
    for x in range(40, 720):
        t = (x - 40) / 680
        draw.line([(x, 40), (x, 460)], fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    # dotted pattern tile (harmony B dots on background)
    draw.rectangle([760, 40, 1160, 460], fill=colours[1])
    for row in range(14):
        for col in range(13):
            cx, cy = 775 + col * 30 + (row % 2) * 15, 55 + row * 30
            draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=colours[2])
    # swatches
    for i, colour in enumerate(result["colours"]):
        x = 40 + i * 226
        draw.rounded_rectangle([x, 500, x + 206, 650], radius=18, fill=colour["hex"],
                               outline=colours[4] if colour["role"] == "Background" else None, width=2)
        draw.text((x, 662), colour["name"], fill=colours[4], font=small_font)
        draw.text((x, 690), colour["hex"], fill=colours[4], font=small_font)
    draw.text((40, 730), f"{fonts['heading']} + {fonts['body']}  ·  {result['rule']} harmony  ·  "
              + ", ".join(keywords[:4]), fill=colours[4], font=small_font)
    draw.text((40, 762), "Made with ORBIT Mood Studio", fill=colours[4], font=small_font)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def is_valid_hex(colour):
    return isinstance(colour, str) and len(colour) == 7 and colour[0] == "#" and \
        all(c in "0123456789ABCDEFabcdef" for c in colour[1:])


def angle_distance(a, b):
    return abs((a - b + 180) % 360 - 180)


"""
pattern_swatches.py
Small CSS drawings of the patterns and textures each creative style lists
(data/creative_profiles.csv, column "patterns"). They are drawn in the
universe's own palette: {a} Primary, {b} Harmony A, {c} Harmony B,
{bg} Background, {ink} text colour. Two extra hex digits (e.g. {a}55) add
transparency. Used by the moodboard in studio.py.
"""

PATTERNS = {
    "damask": "radial-gradient(ellipse 30% 42% at 50% 50%, {b}cc 0 38%, transparent 40%) 0 0 / 34px 48px, "
              "radial-gradient(ellipse 18% 26% at 50% 50%, {c}88 0 40%, transparent 42%) 17px 24px / 34px 48px, {a}",
    "rose motif": "radial-gradient(circle at 50% 50%, {c} 0 18%, {b} 19% 30%, transparent 31%) 0 0 / 30px 30px, "
                  "radial-gradient(circle at 50% 50%, {b}66 0 10%, transparent 11%) 15px 15px / 30px 30px, {a}",
    "velvet": "radial-gradient(ellipse at 30% 20%, {c}66, transparent 55%), "
              "linear-gradient(160deg, {a}, {b} 55%, {bg})",
    "candle glow": "radial-gradient(circle at 50% 60%, #F6D58E 0 6%, #E7A34A88 10%, transparent 45%), {bg}",
    "lace": "radial-gradient(circle, transparent 0 5px, {ink}66 6px 7px, transparent 8px) 0 0 / 18px 18px, "
            "radial-gradient(circle, {ink}44 0 2px, transparent 3px) 9px 9px / 18px 18px, {a}",
    "filigree": "repeating-radial-gradient(circle at 0 0, transparent 0 9px, {c}99 10px 11px) 0 0 / 28px 28px, {a}",
    "pressed flowers": "radial-gradient(circle at 25% 30%, {b} 0 6px, transparent 7px), "
                       "radial-gradient(circle at 70% 65%, {c} 0 5px, transparent 6px), "
                       "radial-gradient(circle at 60% 20%, {a}aa 0 4px, transparent 5px), {bg}",
    "tweed": "repeating-linear-gradient(45deg, {a}55 0 2px, transparent 2px 5px), "
             "repeating-linear-gradient(-45deg, {b}55 0 2px, transparent 2px 5px), {c}",
    "leather": "radial-gradient(circle at 30% 30%, {b}55, transparent 60%), "
               "repeating-radial-gradient(circle at 50% 50%, {ink}11 0 1px, transparent 1px 4px), {a}",
    "ink blots": "radial-gradient(circle at 30% 40%, {ink}cc 0 9%, transparent 10%), "
                 "radial-gradient(circle at 65% 65%, {ink}99 0 6%, transparent 7%), {bg}",
    "gingham": "repeating-linear-gradient(0deg, {a}66 0 10px, transparent 10px 20px), "
               "repeating-linear-gradient(90deg, {a}66 0 10px, transparent 10px 20px), {bg}",
    "wildflower sprigs": "radial-gradient(circle at 20% 30%, {b} 0 4px, transparent 5px), "
                         "radial-gradient(circle at 55% 60%, {c} 0 4px, transparent 5px), "
                         "radial-gradient(circle at 80% 25%, {b} 0 3px, transparent 4px), "
                         "linear-gradient(170deg, transparent 0 60%, {a}55 60% 61%, transparent 62%), {bg}",
    "embroidery": "repeating-linear-gradient(90deg, {b} 0 6px, transparent 6px 10px) 0 45% / 100% 3px no-repeat, "
                  "repeating-linear-gradient(90deg, {c} 0 6px, transparent 6px 10px) 0 60% / 100% 3px no-repeat, {bg}",
    "neon grid": "linear-gradient({a} 1px, transparent 1px) 0 0 / 20px 20px, "
                 "linear-gradient(90deg, {b} 1px, transparent 1px) 0 0 / 20px 20px, {bg}",
    "circuit lines": "linear-gradient(90deg, transparent 45%, {b} 45% 50%, transparent 50%) 0 0 / 30px 30px, "
                     "linear-gradient(transparent 70%, {a} 70% 74%, transparent 74%) 0 0 / 30px 30px, {bg}",
    "scanlines": "repeating-linear-gradient(0deg, {ink}22 0 1px, transparent 1px 4px), linear-gradient(135deg, {a}, {b})",
    "glitch bands": "linear-gradient(transparent 20%, {b} 20% 26%, transparent 26% 55%, {a} 55% 60%, "
                    "transparent 60% 80%, {c} 80% 83%, transparent 83%), {bg}",
    "clouds": "radial-gradient(ellipse 40% 25% at 30% 40%, #FFFFFFcc, transparent 70%), "
              "radial-gradient(ellipse 35% 22% at 70% 65%, #FFFFFFaa, transparent 70%), linear-gradient({a}, {b})",
    "pearls": "radial-gradient(circle at 40% 40%, #FFFFFF 0 2px, {c} 3px 7px, transparent 8px) 0 0 / 20px 20px, {bg}",
    "celtic knots": "repeating-radial-gradient(circle at 50% 50%, transparent 0 6px, {c} 7px 8px, transparent 9px 12px) "
                    "0 0 / 26px 26px, {a}",
    "stars": "radial-gradient(circle, #FFFFFF 0 1.5px, transparent 2px) 0 0 / 22px 22px, "
             "radial-gradient(circle, {c} 0 1px, transparent 1.5px) 11px 11px / 22px 22px, {a}",
    "ivy": "radial-gradient(ellipse 40% 25% at 50% 50%, {b} 0 60%, transparent 62%) 0 0 / 20px 16px, "
           "radial-gradient(ellipse 40% 25% at 50% 50%, {a} 0 60%, transparent 62%) 10px 8px / 20px 16px, {bg}",
    "gothic arches": "radial-gradient(ellipse 50% 70% at 50% 100%, transparent 0 60%, {c} 61% 66%, transparent 67%) "
                     "0 0 / 30px 40px, {a}",
    "stained glass": "conic-gradient(from 45deg, {a}, {b}, {c}, {a}) 0 0 / 30px 30px, {ink}",
    "runes": "linear-gradient(60deg, transparent 47%, {c} 47% 53%, transparent 53%) 0 0 / 22px 26px, "
             "linear-gradient(transparent 47%, {c}88 47% 53%, transparent 53%) 0 0 / 22px 26px, {a}",
    "stone texture": "radial-gradient(circle at 30% 30%, {bg}22, transparent 40%), "
                     "repeating-radial-gradient(circle at 70% 70%, {ink}18 0 2px, transparent 2px 6px), {c}",
    "scratches": "repeating-linear-gradient(80deg, transparent 0 14px, {ink}55 14px 15px), {a}",
    "fog": "radial-gradient(ellipse at 50% 70%, {bg}cc, transparent 70%), linear-gradient({c}, {a})",
    "polka dots": "radial-gradient(circle, {a} 0 4px, transparent 5px) 0 0 / 20px 20px, {bg}",
    "venetian blinds": "repeating-linear-gradient(0deg, {bg}55 0 6px, transparent 6px 12px), {a}",
    "rain streaks": "repeating-linear-gradient(100deg, transparent 0 10px, {bg}66 10px 11px), linear-gradient({a}, {b})",
    "checkerboard": "conic-gradient({a} 25%, {bg} 0 50%, {a} 0 75%, {bg} 0) 0 0 / 22px 22px",
    "glitter": "radial-gradient(circle, #FFFFFF 0 1px, transparent 1.5px) 0 0 / 7px 9px, "
               "radial-gradient(circle, {c} 0 1px, transparent 1.5px) 3px 4px / 9px 7px, {a}",
    "sunburst": "repeating-conic-gradient(from 0deg at 50% 100%, {a} 0 6deg, {b} 6deg 12deg)",
    "bows": "radial-gradient(ellipse 30% 20% at 35% 50%, {a} 0 60%, transparent 62%) 0 0 / 30px 24px, "
            "radial-gradient(ellipse 30% 20% at 65% 50%, {a} 0 60%, transparent 62%) 0 0 / 30px 24px, {bg}",
    "macrame": "repeating-linear-gradient(60deg, {a}88 0 2px, transparent 2px 9px), "
               "repeating-linear-gradient(-60deg, {a}88 0 2px, transparent 2px 9px), {bg}",
    "block print": "radial-gradient(circle, {a} 0 5px, transparent 6px) 0 0 / 24px 24px, "
                   "radial-gradient(circle, {c} 0 3px, transparent 4px) 12px 12px / 24px 24px, {bg}",
    "woven texture": "repeating-linear-gradient(0deg, {a}66 0 4px, {b}66 4px 8px), "
                     "repeating-linear-gradient(90deg, transparent 0 4px, {bg}44 4px 8px)",
    "plaid": "repeating-linear-gradient(0deg, {a}99 0 8px, transparent 8px 22px), "
             "repeating-linear-gradient(90deg, {b}99 0 8px, transparent 8px 22px), {c}",
    "photocopy texture": "repeating-radial-gradient(circle at 40% 40%, {ink}22 0 1px, transparent 1px 3px), "
                         "linear-gradient(90deg, {bg}, {c})",
    "torn paper": "linear-gradient(176deg, {bg} 0 45%, transparent 46%), linear-gradient(184deg, transparent 54%, "
                  "{bg} 55%), {a}",
    "leaves": "radial-gradient(ellipse 35% 20% at 50% 50%, {a} 0 60%, transparent 62%) 0 0 / 24px 18px, "
              "radial-gradient(ellipse 35% 20% at 50% 50%, {b} 0 60%, transparent 62%) 12px 9px / 24px 18px, {bg}",
    "solar panels": "linear-gradient({bg}88 1px, transparent 1px) 0 0 / 14px 14px, "
                    "linear-gradient(90deg, {bg}88 1px, transparent 1px) 0 0 / 14px 14px, {c}",
    "wood grain": "repeating-radial-gradient(ellipse at 0 50%, {a} 0 6px, {b} 6px 9px)",
    "gears": "repeating-radial-gradient(circle at 50% 50%, {a} 0 6px, transparent 6px 8px, {b} 8px 12px, "
             "transparent 12px 14px) 0 0 / 32px 32px, {bg}",
    "paisley": "radial-gradient(ellipse 25% 35% at 40% 55%, {a} 0 55%, transparent 57%) 0 0 / 28px 32px, "
               "radial-gradient(circle at 48% 30%, {c} 0 3px, transparent 4px) 0 0 / 28px 32px, {bg}",
    "mandala dots": "repeating-radial-gradient(circle at 50% 50%, {a} 0 2px, transparent 3px 7px) 0 0 / 40px 40px, {bg}",
    "waves": "radial-gradient(circle at 50% 0, transparent 0 9px, {a} 10px 12px, transparent 13px) 0 0 / 24px 14px, {bg}",
    "ripples": "repeating-radial-gradient(circle at 50% 50%, {a}55 0 1px, transparent 2px 9px), {bg}",
    "stripes": "repeating-linear-gradient(90deg, {a} 0 10px, {bg} 10px 20px)",
    "moon phases": "radial-gradient(circle at 30% 50%, {bg} 0 8px, transparent 9px), "
                   "radial-gradient(circle at 70% 50%, {bg} 0 8px, transparent 9px), "
                   "radial-gradient(circle at 74% 46%, {a} 0 7px, transparent 8px), {a}",
    "orbit lines": "repeating-radial-gradient(circle at 50% 50%, transparent 0 10px, {c}88 11px 12px), {a}",
    "doodles": "radial-gradient(circle, transparent 0 4px, {a} 5px 6px, transparent 7px) 0 0 / 22px 22px, "
               "linear-gradient(45deg, transparent 46%, {c} 46% 54%, transparent 54%) 11px 11px / 22px 22px, {bg}",
    "concrete": "repeating-radial-gradient(circle at 30% 30%, {ink}14 0 1px, transparent 1px 5px), {c}",
    "brushed metal": "repeating-linear-gradient(90deg, #FFFFFF22 0 1px, transparent 1px 3px), "
                     "linear-gradient(135deg, {c}, {bg} 50%, {c})",
    "marble": "linear-gradient(120deg, transparent 40%, {c}55 41% 43%, transparent 44%), "
              "linear-gradient(60deg, transparent 60%, {c}44 61% 62%, transparent 63%), {bg}",
    "gold foil": "linear-gradient(120deg, #B8913A, #F1D98A 30%, #A87C2A 55%, #E6C66E 80%, #B8913A)",
    "art deco fans": "repeating-radial-gradient(circle at 50% 100%, {a} 0 4px, {b} 4px 8px) 0 0 / 30px 20px",
    "pinstripe": "repeating-linear-gradient(90deg, {c}88 0 1px, transparent 1px 12px), {a}",
    "sequins": "radial-gradient(circle at 40% 40%, #FFFFFF99 0 1px, {a} 2px 4px, transparent 5px) 0 0 / 10px 10px, {b}",
    "knit texture": "repeating-linear-gradient(60deg, {a}aa 0 3px, transparent 3px 6px) 0 0 / 12px 12px, "
                    "repeating-linear-gradient(-60deg, {a}aa 0 3px, transparent 3px 6px) 6px 0 / 12px 12px, {b}",
}

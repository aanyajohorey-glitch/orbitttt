"""
creator_eval.py
Evaluation of Creator Mode (shown in About -> AI Lab).

1. Vibe-prompt accuracy
   data/vibe_eval.csv (kept on this computer, like eval_heldout.csv): about 100
   held-out ideas, each rated by 3 people on four 1-5 scales:
       mood    1 very dark/sad ... 5 very bright/happy
       energy  1 very calm     ... 5 very energetic
       warmth  1 very cool     ... 5 very warm
       era     1 ancient       ... 5 futuristic
   ORBIT's Vibe Vector is turned into the same 1-5 scales. ORBIT is "right" on a
   scale when it is within 1 point of the raters' MEDIAN. The human baseline is
   how often each rater is within 1 point of the median of the OTHER two raters:
   ORBIT shouldn't be expected to agree with people more than people agree
   with each other.

2. List diversity (computed, no people needed)
   For a fixed set of example ideas (data/example_ideas.csv), how varied the
   playlists and creator lists are at different discovery settings.

3. User study
   data/user_study.csv (kept on this computer): building a creative brief with
   ORBIT vs usual tools: minutes, number of tools, satisfaction (1-5).
"""
from pathlib import Path
from statistics import median

import pandas as pd

DATA = Path(__file__).parent / "data"
VIBE_EVAL = DATA / "vibe_eval.csv"
EXAMPLE_IDEAS = DATA / "example_ideas.csv"
USER_STUDY = DATA / "user_study.csv"
SCALES = ["mood", "energy", "warmth", "era"]
TOLERANCE = 1      # within 1 point on a 1-5 scale counts as agreement


def to_scale(x):
    """-1..+1 -> 1..5 (rounded to the nearest whole point)."""
    return int(round(3 + 2 * max(-1.0, min(1.0, x))))


def vector_scales(vector):
    return {"mood": to_scale(vector["valence"]), "energy": to_scale(vector["arousal"]),
            "warmth": to_scale(vector["warmth"]), "era": to_scale(vector["era"])}


def load_ratings(path=VIBE_EVAL):
    """Long format: idea_id, idea, language, rater, mood, energy, warmth, era."""
    if not Path(path).exists():
        return pd.DataFrame()
    table = pd.read_csv(path)
    table = table[table["idea"].notna() & (table["idea"].astype(str).str.strip() != "")]
    return table


def human_agreement(ratings):
    """For each rater and scale: within TOLERANCE of the median of the other raters? Returns share per scale."""
    hits = {s: [] for s in SCALES}
    for _, group in ratings.groupby("idea_id"):
        if len(group) < 3:
            continue
        for i in range(len(group)):
            others = group.drop(group.index[i])
            for s in SCALES:
                hits[s].append(abs(group.iloc[i][s] - median(others[s])) <= TOLERANCE)
    return {s: (sum(v) / len(v) if v else None) for s, v in hits.items()}


def orbit_accuracy(ratings, predict):
    """predict(idea_text) -> {scale: 1-5}. Share of ideas where ORBIT is within TOLERANCE of the median."""
    rows = []
    for idea_id, group in ratings.groupby("idea_id"):
        if len(group) < 3:
            continue
        guess = predict(str(group.iloc[0]["idea"]))
        row = {"idea_id": idea_id, "language": group.iloc[0].get("language", "")}
        for s in SCALES:
            row[s] = abs(guess[s] - median(group[s])) <= TOLERANCE
        rows.append(row)
    detail = pd.DataFrame(rows)
    if detail.empty:
        return {}, detail
    return {s: float(detail[s].mean()) for s in SCALES}, detail


def predict_with_orbit(text):
    """The live pipeline: ORBIT's emotion reading -> Vibe Vector -> 1-5 scales."""
    import demo_mode
    import vibe
    from analysis import interpret
    try:
        result = demo_mode.interpret_offline(text) if demo_mode.enabled() else interpret(text)
    except Exception:
        result = demo_mode.interpret_offline(text)
    vector = vibe.build(text, result["emotions"], match_text=result.get("model_text"))
    return vector_scales(vector)


# ---------------------------------------------------------------
# List diversity
# ---------------------------------------------------------------
def list_diversity(ideas, discovery_levels=(0.0, 0.5, 1.0)):
    """Average variety of the music and creator lists for the example ideas."""
    import creative
    import music
    import vibe
    rows = []
    for level in discovery_levels:
        stats = {"languages": [], "genres": [], "fields": [], "regions": [], "mainstream": [], "india": []}
        for text, valence, arousal in ideas:
            emotions = [("joy", 0.5)] if valence >= 0 else [("sadness", 0.5)]
            vector = vibe.build(text, emotions)
            vector["valence"], vector["arousal"] = valence, arousal
            playlist = music.recommend_target(3 + 2 * valence, 3 + 2 * arousal, creative.music_tags(vector),
                                              "project", level, size=8)
            people = creative.rank_creators(vector, level)
            stats["languages"].append(len({t["language"] for t in playlist}))
            stats["genres"].append(len({t["genre"] for t in playlist}))
            stats["fields"].append(len({c["field"] for c in people}))
            stats["mainstream"].append(sum(t["mainstream_level"] for t in playlist) / len(playlist))
            stats["india"].append(sum("India" in c["region"] for c in people) / len(people))
        rows.append({"Discovery": level,
                     "Languages per playlist (of 8)": round(sum(stats["languages"]) / len(ideas), 1),
                     "Genres per playlist (of 8)": round(sum(stats["genres"]) / len(ideas), 1),
                     "Fields per creator list (of 6)": round(sum(stats["fields"]) / len(ideas), 1),
                     "Average mainstream level (1-5)": round(sum(stats["mainstream"]) / len(ideas), 2),
                     "Creators from India": f"{sum(stats['india']) / len(ideas):.0%}"})
    return pd.DataFrame(rows)


def load_example_ideas():
    table = pd.read_csv(EXAMPLE_IDEAS)
    return list(zip(table["idea"], table["valence"], table["arousal"]))


# ---------------------------------------------------------------
# User study
# ---------------------------------------------------------------
def user_study_summary(path=USER_STUDY):
    if not Path(path).exists():
        return None
    table = pd.read_csv(path)
    table = table[table["condition"].isin(["ORBIT", "Usual tools"])]
    if table.empty:
        return None
    return (table.groupby("condition").agg(Participants=("participant", "nunique"),
                                           Minutes=("minutes", "mean"), Tools=("tools_used", "mean"),
                                           Satisfaction=("satisfaction", "mean"), Cohesion=("cohesion", "mean"))
            .round(1).reset_index())

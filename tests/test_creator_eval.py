"""Creator Mode evaluation code (creator_eval.py). Uses small made-up tables, never real ratings."""
import pandas as pd

import creator_eval as ce


def ratings(rows):
    return pd.DataFrame(rows, columns=["idea_id", "idea", "language", "rater", "mood", "energy", "warmth", "era"])


AGREE = ratings([
    (1, "a calm tea shop", "English", "A", 4, 1, 4, 3),
    (1, "a calm tea shop", "English", "B", 4, 2, 4, 3),
    (1, "a calm tea shop", "English", "C", 5, 1, 5, 2),
    (2, "a neon arcade", "English", "A", 4, 5, 2, 5),
    (2, "a neon arcade", "English", "B", 3, 5, 2, 4),
    (2, "a neon arcade", "English", "C", 4, 4, 1, 5),
])


def test_vector_numbers_map_to_1_to_5():
    assert ce.to_scale(-1) == 1 and ce.to_scale(0) == 3 and ce.to_scale(1) == 5
    assert ce.to_scale(5) == 5                      # clipped


def test_human_baseline_when_raters_agree():
    assert ce.human_agreement(AGREE) == {s: 1.0 for s in ce.SCALES}


def test_orbit_accuracy_counts_within_one_point_of_the_median():
    perfect = {"a calm tea shop": {"mood": 4, "energy": 1, "warmth": 4, "era": 3},
               "a neon arcade": {"mood": 4, "energy": 5, "warmth": 2, "era": 5}}
    accuracy, detail = ce.orbit_accuracy(AGREE, perfect.get)
    assert accuracy == {s: 1.0 for s in ce.SCALES} and len(detail) == 2
    wrong = {k: {"mood": 1, "energy": 3, "warmth": 4, "era": 3} for k in perfect}
    accuracy, _ = ce.orbit_accuracy(AGREE, wrong.get)
    assert accuracy["mood"] == 0.0 and accuracy["warmth"] == 1.0


def test_ideas_with_fewer_than_three_raters_are_skipped():
    two = AGREE[AGREE["rater"] != "C"]
    accuracy, detail = ce.orbit_accuracy(two, lambda text: {s: 3 for s in ce.SCALES})
    assert accuracy == {} and detail.empty


def test_list_diversity_grows_with_discovery():
    table = ce.list_diversity(ce.load_example_ideas()[:6], discovery_levels=(0.0, 1.0))
    familiar, unfamiliar = table.iloc[0], table.iloc[1]
    assert unfamiliar["Average mainstream level (1-5)"] < familiar["Average mainstream level (1-5)"]
    assert unfamiliar["Languages per playlist (of 8)"] >= familiar["Languages per playlist (of 8)"]


def test_user_study_summary(tmp_path):
    path = tmp_path / "study.csv"
    pd.DataFrame([
        {"participant": "P1", "condition": "Usual tools", "minutes": 30, "tools_used": 5, "satisfaction": 3, "cohesion": 3},
        {"participant": "P1", "condition": "ORBIT", "minutes": 12, "tools_used": 1, "satisfaction": 4, "cohesion": 4},
    ]).to_csv(path, index=False)
    summary = ce.user_study_summary(path).set_index("condition")
    assert summary.loc["ORBIT", "Minutes"] == 12 and summary.loc["Usual tools", "Tools"] == 5
    assert ce.user_study_summary(tmp_path / "missing.csv") is None


def test_templates_exist_and_have_the_right_columns():
    assert list(pd.read_csv(ce.DATA / "vibe_eval_template.csv").columns) == \
        ["idea_id", "idea", "language", "rater", "mood", "energy", "warmth", "era"]
    assert "satisfaction" in pd.read_csv(ce.DATA / "user_study_template.csv").columns

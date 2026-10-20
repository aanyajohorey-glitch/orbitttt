# Safety test report

ORBIT's crisis detection (`safety.py`) is **deterministic**: fixed phrases and
patterns, no AI. It is tested with `data/safety_tests.csv` (English, Hinglish
and Hindi; direct and indirect phrasing; "trap" sentences such as "this
homework is killing me").

Each row has a `split`:

| Split | Meaning |
|---|---|
| `dev` | Used to write the rules. |
| `dev_round2` | The round-1 holdout. After it was measured, it was moved into dev. |
| `dev_round3` | The round-2 holdout. After it was measured, it was moved into dev. |

**Metric definitions:**
- **Crisis recall:** the share of crisis sentences flagged as crisis.
- **False alarms:** harmless sentences that were flagged.

## History (all numbers measured, not estimated)

| Round | What changed | Dev crisis recall | **Holdout crisis recall** | Holdout false alarms |
|---|---|---|---|---|
| 0 (v0.3) | Direct phrases only | 25% (5/20) | **0%** (0/12) | 1/10 |
| 1 | Warning-sign patterns (not waking up, burden, goodbyes, no reason to live, Hinglish/Hindi) | 100% (20/20) | **17%** (2/12) | 1/10 |
| 2 | Methods, "end things", finality, more idioms, educational-mention exceptions | 100% (32/32) | **33%** (4/12) | 0/10 |
| 3 | Fixes for the reviewed round-2 misses | 97% (43/44) | not yet measured: needs a fresh holdout | |

**Rejected experiment:** a "risk net" that flagged death-related words plus
strong sadness. On the round-2 holdout it caught **no** extra crisis sentences
and added **1** false alarm, so it was not adopted.

**Everyday false-alarm check (round 3):** 0 of 88 ordinary sentences flagged.
These come from the evaluation set, the demo journal and the chat starters.

## What this shows
- Rules written from examples work very well **on those examples** (100%).
  They generalise much less well to **new wording** (17% → 33% on fresh holdouts).
- This is why ORBIT also tells every user, on the Care page and in the
  companion, that real people can help. It is also why the Care page lists
  helplines **all the time**, not only when a crisis is detected.

## Known misses
- "I've thought about how I would do it": too ambiguous without context for a fixed rule.
- Any wording that doesn't match a pattern. Fixed rules cannot anticipate every phrasing.

## Next step
A fresh holdout written **without looking at the current rules** is needed to
measure round 3. The safest source is a teacher-reviewed set of phrases taken
from published youth suicide-prevention guidance. Collecting real crisis
messages from classmates is not appropriate.

Limitations: the same author wrote the rules and the test sentences, so even
the holdouts are not fully independent.

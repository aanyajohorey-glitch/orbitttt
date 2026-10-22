"""
ranking.py
The two ranking ideas ORBIT uses for music, aesthetics and creators.

1. Cosine similarity: how closely two lists of numbers point the same way
   (1 = same direction, 0 = unrelated, -1 = opposite).
2. Maximal Marginal Relevance (MMR): pick results one at a time, each time
   balancing "relevant to what you asked for" against "too similar to what's
   already picked", so a list doesn't fill up with near-copies.
"""
import math


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    size = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / size if size else 0.0


def overlap(tags_a, tags_b):
    """Share of tags in common (Jaccard index): 0 = none, 1 = identical sets."""
    a, b = set(tags_a), set(tags_b)
    return len(a & b) / len(a | b) if a | b else 0.0


def mmr(candidates, similarity, size, trade_off, unique=None):
    """Re-rank candidates (dicts with a "relevance" number).

    similarity(a, b): how alike two candidates are (0-1).
    trade_off (lambda): 1 = only relevance, 0 = only diversity.
    unique: optional key that may appear only once (e.g. "artist").
    """
    pool = sorted(candidates, key=lambda c: -c["relevance"])
    chosen = []
    while pool and len(chosen) < size:
        def score(item):
            redundancy = max((similarity(item, other) for other in chosen), default=0.0)
            return trade_off * item["relevance"] - (1 - trade_off) * redundancy
        best = max(pool, key=score)
        pool.remove(best)
        if unique and any(best[unique] == other[unique] for other in chosen):
            continue
        chosen.append(best)
    return chosen


def discovery_trade_off(discovery):
    """The discovery dial (0 = comfort zone, 1 = unfamiliar) -> MMR lambda (0.8 ... 0.35)."""
    return 0.8 - 0.45 * discovery

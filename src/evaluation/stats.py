"""Statistical comparison of detectors across rolling-origin folds.

Follows the protocol that is standard for comparing multiple algorithms over
multiple datasets — here, over multiple temporal folds: a Friedman omnibus
test on the rank matrix, then a Nemenyi post-hoc with a critical-difference
diagram, plus pairwise Wilcoxon signed-rank tests with Holm correction for
the specific comparisons the research questions name.

A warning that belongs in the results, not just in the code: over a handful
of folds the post-hoc tests have little power. The critical difference grows
with the number of methods compared, and for a wide field of detectors it
exceeds the whole range of average ranks, so Nemenyi can essentially never
reject. That is a property of the experiment size, not evidence that the
detectors are equivalent, which is one reason this study compares three
detectors rather than many, and why the per-fold values are always reported
alongside the tests.
"""

import numpy as np
import pandas as pd
from scipy import stats

# Nemenyi critical values q_alpha at alpha = 0.05, indexed by number of
# compared algorithms (Demsar's table; q = studentized range / sqrt(2)).
_NEMENYI_Q05 = {
    2: 1.960,
    3: 2.343,
    4: 2.569,
    5: 2.728,
    6: 2.850,
    7: 2.949,
    8: 3.031,
    9: 3.102,
    10: 3.164,
    11: 3.219,
    12: 3.268,
    13: 3.313,
    14: 3.354,
    15: 3.391,
    16: 3.426,
    17: 3.458,
    18: 3.489,
    19: 3.517,
    20: 3.544,
}


def rank_matrix(scores: pd.DataFrame) -> pd.DataFrame:
    """Per-fold ranks (1 = best). `scores` is folds x models, higher = better."""
    return scores.rank(axis=1, ascending=False, method="average")


def friedman(scores: pd.DataFrame) -> dict:
    """Omnibus test: are all detectors equivalent across folds?"""
    if scores.shape[0] < 3:
        return {
            "statistic": np.nan,
            "p_value": np.nan,
            "n_folds": scores.shape[0],
            "n_models": scores.shape[1],
            "note": "needs at least 3 folds",
        }
    stat, p = stats.friedmanchisquare(*[scores[c].to_numpy() for c in scores.columns])
    return {
        "statistic": float(stat),
        "p_value": float(p),
        "n_folds": int(scores.shape[0]),
        "n_models": int(scores.shape[1]),
    }


def nemenyi_critical_difference(n_models: int, n_folds: int, alpha: float = 0.05) -> float:
    """CD = q_alpha * sqrt(k(k+1) / (6N)); two average ranks differing by less
    than CD are statistically indistinguishable at level alpha."""
    if alpha != 0.05:
        raise ValueError("only alpha=0.05 is tabulated here")
    q = _NEMENYI_Q05.get(n_models)
    if q is None:
        raise ValueError(f"no tabulated q for k={n_models}")
    return float(q * np.sqrt(n_models * (n_models + 1) / (6.0 * n_folds)))


def average_ranks(scores: pd.DataFrame) -> pd.Series:
    return rank_matrix(scores).mean(axis=0).sort_values()


def wilcoxon_pairs(scores: pd.DataFrame, pairs: list[tuple[str, str]]) -> pd.DataFrame:
    """Pairwise Wilcoxon signed-rank over folds, Holm-corrected.

    With N folds the smallest attainable two-sided p-value is 2 / 2^N, so the
    attainable minimum is reported next to each p-value: a comparison can be
    perfectly consistent and still not reach alpha simply because there are
    not enough folds.
    """
    rows = []
    for a, b in pairs:
        d = scores[a].to_numpy() - scores[b].to_numpy()
        n = int(np.sum(d != 0))
        if n == 0:
            stat, p = np.nan, 1.0
        else:
            stat, p = stats.wilcoxon(
                scores[a], scores[b], zero_method="wilcox", alternative="two-sided", method="exact"
            )
        rows.append(
            {
                "model_a": a,
                "model_b": b,
                "mean_diff": float(d.mean()),
                "wins_a": int(np.sum(d > 0)),
                "wins_b": int(np.sum(d < 0)),
                "statistic": float(stat) if stat == stat else np.nan,
                "p_value": float(p),
                "min_attainable_p": float(2.0 / 2**n) if n else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out["p_holm"] = holm_correction(out["p_value"].to_numpy())
    out["significant_holm_05"] = out["p_holm"] < 0.05
    return out


def holm_correction(pvals: np.ndarray) -> np.ndarray:
    """Holm-Bonferroni step-down adjusted p-values."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adjusted = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted

"""Score-level combination of detectors.

Two problems have to be solved before averaging anything. First, the detectors
report on very different scales: a path-length score from Isolation Forest, a
mean squared reconstruction error from the Autoencoder and a signed distance
to a kernel boundary from One-Class SVM cannot simply be added. Second,
whatever rescaling is used must be estimated from the *training* window, or
the ensemble quietly becomes a function of the test set.

Both are handled by mapping each detector's scores onto its own training-score
quantile: the result is a [0, 1] "how unusual is this relative to what we saw
in training" number that is comparable across detectors, monotone in the
original score, and computed from training data alone.

Member selection is handled the same way time handles everything else here:
the members used on fold i are chosen using only folds that precede it.
"""

import numpy as np
from sklearn.metrics import average_precision_score

COMBINERS = ("rank_avg", "z_avg", "max", "median", "vote")


def rank_normalise(fold, name: str, scores: np.ndarray | None = None) -> np.ndarray:
    """Position of each score in the training-score distribution, in [0, 1]."""
    s = fold.test_scores(name) if scores is None else scores
    return fold.train_rank_of(name, s)


def z_normalise(fold, name: str, scores: np.ndarray | None = None) -> np.ndarray:
    """Standardise by training mean/std — the scale-sensitive alternative kept
    for comparison, since it is what a naive implementation reaches for."""
    s = fold.test_scores(name) if scores is None else scores
    stats = fold.costs[name]
    std = stats["train_score_std"] or 1.0
    return (s - stats["train_score_mean"]) / std


def combine(fold, members: list[str], mode: str, contamination: float = 0.002) -> np.ndarray:
    """Combined anomaly score for one fold under the given rule."""
    if mode not in COMBINERS:
        raise ValueError(f"unknown combiner: {mode}")
    if not members:
        raise ValueError("ensemble needs at least one member")

    if mode == "z_avg":
        return np.mean([z_normalise(fold, m) for m in members], axis=0)
    if mode == "vote":
        votes = [
            (fold.test_scores(m) >= fold.train_threshold(m, contamination)).astype(float)
            for m in members
        ]
        return np.mean(votes, axis=0)

    normalised = np.array([rank_normalise(fold, m) for m in members])
    if mode == "rank_avg":
        return normalised.mean(axis=0)
    if mode == "max":
        return normalised.max(axis=0)
    return np.median(normalised, axis=0)


def greedy_forward_selection(
    history_folds: list,
    candidates: list[str],
    mode: str,
    max_members: int = 6,
    contamination: float = 0.002,
) -> list[str]:
    """Grow an ensemble one member at a time, keeping whichever addition most
    improves mean AP over the folds supplied as history.

    Members may repeat: adding an already-selected detector a second time is
    how a plain average expresses a weight, and forbidding it would make the
    search strictly weaker. Selection sees only history folds.
    """
    selected: list[str] = []
    best_overall = -np.inf
    for _ in range(max_members):
        scored = []
        for cand in candidates:
            trial = [*selected, cand]
            aps = [
                average_precision_score(f.y, combine(f, trial, mode, contamination))
                for f in history_folds
            ]
            scored.append((float(np.mean(aps)), cand))
        best_ap, best_cand = max(scored)
        if best_ap <= best_overall + 1e-6:
            break
        selected.append(best_cand)
        best_overall = best_ap
    return selected


def pairwise_rank_correlation(fold, members: list[str]) -> np.ndarray:
    """Spearman correlation between members' test rankings — the quantity that
    decides whether averaging can help at all."""
    from scipy.stats import spearmanr

    mat = np.array([fold.test_scores(m) for m in members])
    rho, _ = spearmanr(mat, axis=1)
    return np.atleast_2d(rho)

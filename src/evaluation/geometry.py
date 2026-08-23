"""Geometric characterisation of the data, independent of any detector.

Unsupervised detection rests on an assumption that is rarely tested: that the
positive class is geometrically separable from the negative one. If it is
not, no amount of algorithmic work will help, and the honest thing is to
measure that first and report the ceiling it implies.

The measures here are all model free. They describe how many dimensions the
normal class really occupies, how isolated the frauds are in that space, and
what fraction of them sit inside dense normal regions where a proximity or
density detector cannot reach them.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors


def intrinsic_dimension_mle(
    X: np.ndarray, k: int = 20, seed: int = 42, max_points: int = 20000
) -> float:
    """Levina-Bickel maximum-likelihood estimate of intrinsic dimension.

    For each point, the ratio of the distance to the k-th neighbour against
    the closer ones behaves like a sample from a Poisson process on a
    d-dimensional manifold; inverting that relationship gives d. Reported as
    the average over points.
    """
    Xs = _subsample(X, max_points, seed)
    nn = NearestNeighbors(n_neighbors=k + 1, n_jobs=-1).fit(Xs)
    distances, _ = nn.kneighbors(Xs)
    distances = distances[:, 1:]  # drop the point itself
    distances = np.maximum(distances, 1e-12)
    logs = np.log(distances[:, -1][:, None] / distances[:, :-1])
    per_point = (k - 1) / np.maximum(logs.sum(axis=1), 1e-12)
    return float(np.mean(per_point))


def intrinsic_dimension_twonn(
    X: np.ndarray, discard: float = 0.1, seed: int = 42, max_points: int = 20000
) -> float:
    """TwoNN estimator: the ratio of the second to the first neighbour distance.

    Uses only the two nearest neighbours, so it is far less sensitive to
    curvature and to density variation than estimators that need a large k.
    The largest ratios are discarded before the fit because they are dominated
    by boundary effects.
    """
    Xs = _subsample(X, max_points, seed)
    nn = NearestNeighbors(n_neighbors=3, n_jobs=-1).fit(Xs)
    distances, _ = nn.kneighbors(Xs)
    r1, r2 = distances[:, 1], distances[:, 2]
    keep = r1 > 0
    mu = np.sort(r2[keep] / r1[keep])
    mu = mu[: int(len(mu) * (1.0 - discard))]
    n = len(mu)
    empirical = np.arange(1, n + 1) / n
    x = np.log(mu)
    y = -np.log(np.maximum(1.0 - empirical, 1e-12))
    # line through the origin: slope is the dimension estimate
    return float(np.dot(x, y) / np.dot(x, x))


def neighbourhood_purity(
    X_reference: np.ndarray,
    X_query: np.ndarray,
    k: int = 10,
    seed: int = 42,
    max_reference: int = 50000,
) -> np.ndarray:
    """Distance from each query point to its k nearest reference points.

    The reference set is the normal class, so this measures how deep inside
    normal territory each query transaction sits.
    """
    reference = _subsample(X_reference, max_reference, seed)
    nn = NearestNeighbors(n_neighbors=k, n_jobs=-1).fit(reference)
    distances, _ = nn.kneighbors(X_query)
    return distances.mean(axis=1)


def fraud_hardness(
    X_normal: np.ndarray,
    X_fraud: np.ndarray,
    k: int = 10,
    seed: int = 42,
    max_reference: int = 20000,
    max_normal_query: int = 50000,
) -> dict:
    """What it would cost to catch each fraud with distance alone.

    Calling a fraud "isolated" because it lies beyond the 95th percentile of
    normal distances is misleading: five per cent of a very large normal class
    lies out there too, and it outnumbers the positives many times over. The
    operationally meaningful question is different. Rank every transaction by
    distance to the normal class and ask, for each fraud, how many alerts a
    team would have to work through before reaching it.

    Normals are subsampled for tractability and then re-weighted, so the
    precision figures estimate the full population rather than the sample.
    """
    rng = np.random.default_rng(seed)
    reference = _subsample(X_normal, max_reference, seed)
    nn = NearestNeighbors(n_neighbors=k, n_jobs=-1).fit(reference)

    n_normal_total = len(X_normal)
    query_idx = _subsample_indices(n_normal_total, max_normal_query, seed + 1)
    X_normal_q = X_normal[query_idx]
    weight_per_normal = n_normal_total / len(X_normal_q)

    d_normal = nn.kneighbors(X_normal_q)[0].mean(axis=1)
    d_fraud = nn.kneighbors(X_fraud)[0].mean(axis=1)

    scores = np.concatenate([d_normal, d_fraud])
    labels = np.concatenate([np.zeros(len(d_normal), int), np.ones(len(d_fraud), int)])
    weights = np.concatenate([np.full(len(d_normal), weight_per_normal), np.ones(len(d_fraud))])

    from sklearn.metrics import average_precision_score

    ap = float(average_precision_score(labels, scores, sample_weight=weights))

    # Estimated position of each fraud in the full-population ranking.
    order = np.argsort(-scores, kind="stable")
    cumulative = np.cumsum(weights[order])
    rank_of = np.empty(len(scores))
    rank_of[order] = cumulative
    fraud_ranks = rank_of[labels == 1]

    reachable = {
        f"frauds_within_top_{budget}": int((fraud_ranks <= budget).sum())
        for budget in (100, 500, 1000, 5000)
    }
    del rng
    return {
        "k": k,
        "median_knn_distance_normal": float(np.median(d_normal)),
        "p95_knn_distance_normal": float(np.quantile(d_normal, 0.95)),
        "median_knn_distance_fraud": float(np.median(d_fraud)),
        "distance_ratio": float(np.median(d_fraud) / max(np.median(d_normal), 1e-12)),
        "n_frauds": int(len(d_fraud)),
        "ap_distance_only": ap,
        "median_fraud_rank": float(np.median(fraud_ranks)),
        # How many alerts the median fraud costs, per fraud recovered.
        "alerts_per_fraud_at_median": float(np.median(fraud_ranks) / max(len(d_fraud) / 2, 1)),
        **reachable,
        "distances_fraud": d_fraud,
        "distances_normal": d_normal,
        "fraud_ranks": fraud_ranks,
    }


def one_nn_class_agreement(
    X: np.ndarray, y: np.ndarray, seed: int = 42, max_points: int = 40000
) -> dict:
    """Leave-one-out nearest-neighbour agreement, per class.

    A standard complexity measure: when a point's nearest neighbour belongs to
    the other class, the two classes interpenetrate there. Reported per class
    because the interesting asymmetry is that frauds sit among normals far
    more often than the reverse.
    """
    idx = _subsample_indices(len(X), max_points, seed)
    # keep every positive, subsample only the negatives
    idx = np.union1d(idx, np.flatnonzero(y == 1))
    Xs, ys = X[idx], y[idx]
    nn = NearestNeighbors(n_neighbors=2, n_jobs=-1).fit(Xs)
    _, neighbours = nn.kneighbors(Xs)
    same = ys[neighbours[:, 1]] == ys
    return {
        "agreement_overall": float(same.mean()),
        "agreement_normal": float(same[ys == 0].mean()),
        "agreement_fraud": float(same[ys == 1].mean()),
        "n_points": int(len(ys)),
        "n_frauds": int((ys == 1).sum()),
    }


def _subsample_indices(n: int, max_points: int, seed: int) -> np.ndarray:
    if n <= max_points:
        return np.arange(n)
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(n, size=max_points, replace=False))


def _subsample(X: np.ndarray, max_points: int, seed: int) -> np.ndarray:
    return X[_subsample_indices(len(X), max_points, seed)]

"""Quantifying what changes between the training window and each test block.

The distinction that matters for an unsupervised detector is *which* of the
two distributions moved. A detector fitted on normal transactions encodes a
model of normality; it degrades for two very different reasons:

* covariate shift — the normal population itself drifts, so the model of
  normality is stale and everything starts to look slightly anomalous;
* concept shift in the positives — the normal population is unchanged but the
  frauds become less extreme, so they stop protruding from a still-accurate
  model of normality.

The first is fixed by retraining. The second is not, and no amount of
retraining on unlabelled normal data will help. Separating them is therefore
the single most decision-relevant piece of drift analysis in this study.
"""

import numpy as np
import pandas as pd
from scipy import stats


def population_stability_index(
    expected: np.ndarray, actual: np.ndarray, n_bins: int = 10, eps: float = 1e-6
) -> float:
    """PSI between a reference and a new sample, using reference quantile bins.

    Conventional reading: < 0.10 no meaningful shift, 0.10-0.25 moderate,
    > 0.25 major shift.
    """
    if len(expected) == 0 or len(actual) == 0:
        return float("nan")
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, n_bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    e_frac = np.histogram(expected, bins=edges)[0] / len(expected)
    a_frac = np.histogram(actual, bins=edges)[0] / len(actual)
    e_frac = np.clip(e_frac, eps, None)
    a_frac = np.clip(a_frac, eps, None)
    return float(np.sum((a_frac - e_frac) * np.log(a_frac / e_frac)))


def feature_drift(
    reference: pd.DataFrame, current: pd.DataFrame, feature_columns: list[str]
) -> pd.DataFrame:
    """Per-feature PSI and two-sample Kolmogorov-Smirnov test."""
    rows = []
    for col in feature_columns:
        ref, cur = reference[col].to_numpy(), current[col].to_numpy()
        if len(ref) == 0 or len(cur) == 0:
            rows.append({"feature": col, "psi": np.nan, "ks_stat": np.nan, "ks_p": np.nan})
            continue
        ks = stats.ks_2samp(ref, cur)
        rows.append(
            {
                "feature": col,
                "psi": population_stability_index(ref, cur),
                "ks_stat": float(ks.statistic),
                "ks_p": float(ks.pvalue),
            }
        )
    return pd.DataFrame(rows)


def separability(
    reference_normal: pd.DataFrame, current: pd.DataFrame, feature_columns: list[str]
) -> dict:
    """How far the two classes sit from the reference normal centroid.

    Distances are measured in units fixed by the reference window, so the
    numbers are comparable across blocks. A model-free stand-in for "how
    detectable are this block's frauds by any distance-based method".
    """
    mu = reference_normal[feature_columns].to_numpy().mean(axis=0)
    sd = reference_normal[feature_columns].to_numpy().std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    z = (current[feature_columns].to_numpy() - mu) / sd
    norms = np.linalg.norm(z, axis=1)
    y = current["Class"].to_numpy()
    out = {
        "z_norm_median_normal": float(np.median(norms[y == 0])) if (y == 0).any() else np.nan,
        "z_norm_median_fraud": float(np.median(norms[y == 1])) if (y == 1).any() else np.nan,
        "z_norm_p90_fraud": float(np.quantile(norms[y == 1], 0.9)) if (y == 1).any() else np.nan,
    }
    if (y == 1).any() and (y == 0).any():
        from sklearn.metrics import average_precision_score, roc_auc_score

        out["ap_distance_detector"] = float(average_precision_score(y, norms))
        out["auc_distance_detector"] = float(roc_auc_score(y, norms))
        # Effect size between the two classes, on the same distance scale.
        n0, n1 = norms[y == 0], norms[y == 1]
        pooled = np.sqrt(
            ((len(n0) - 1) * n0.var(ddof=1) + (len(n1) - 1) * n1.var(ddof=1))
            / max(len(n0) + len(n1) - 2, 1)
        )
        out["cohens_d"] = float((n1.mean() - n0.mean()) / pooled) if pooled > 0 else np.nan
    return out


def page_hinkley_statistic(values: np.ndarray, delta: float = 0.005) -> np.ndarray:
    """Running Page-Hinkley excursion, without resetting.

    Accumulates how far the values drift above their running mean, minus a
    tolerance `delta`, and reports the excess over the running minimum. This
    is the quantity a change detector thresholds.
    """
    n = len(values)
    out = np.empty(n, dtype=float)
    mean = 0.0
    cumulative = 0.0
    minimum = 0.0
    for i, x in enumerate(values, start=1):
        mean += (x - mean) / i
        cumulative += x - mean - delta
        minimum = min(minimum, cumulative)
        out[i - 1] = cumulative - minimum
    return out


def calibrate_page_hinkley(
    reference: np.ndarray,
    delta: float = 0.005,
    quantile: float = 0.99,
    n_permutations: int = 60,
    seed: int = 42,
) -> float:
    """Threshold calibrated on data believed to contain no change point.

    A fixed threshold is not transferable: the Page-Hinkley statistic on pure
    noise grows roughly with the square root of the stream length, so a value
    that is silent over one thousand samples fires constantly over fifty
    thousand. Calibrating on the training window turns the threshold into an
    explicit false-alarm budget instead of a magic number.

    Calibrating on a single pass is not enough either — one reference
    realisation can happen to produce an unusually small maximum, and the
    resulting threshold then fires on perfectly ordinary data. Under the null
    hypothesis of no change the reference is exchangeable, so its order can be
    permuted: this samples the distribution of the maximum statistic and the
    threshold is taken as a high quantile of that distribution.
    """
    values = np.asarray(reference, dtype=float)
    rng = np.random.default_rng(seed)
    maxima = [page_hinkley_statistic(values, delta).max()]
    for _ in range(max(n_permutations - 1, 0)):
        maxima.append(page_hinkley_statistic(rng.permutation(values), delta).max())
    return float(np.quantile(maxima, quantile))


def page_hinkley(values: np.ndarray, delta: float = 0.005, threshold: float = 50.0) -> list[int]:
    """Page-Hinkley change points on a stream of scalars.

    A cheap, single-pass detector: it accumulates how far the running values
    drift above their running mean and fires when that excess exceeds
    `threshold`, then restarts. Used here on the stream of anomaly scores to
    ask whether a monitor with no access to labels could have noticed the
    shift on its own. Use `calibrate_page_hinkley` to pick `threshold`.
    """
    changes: list[int] = []
    mean = 0.0
    cumulative = 0.0
    minimum = 0.0
    for i, x in enumerate(values, start=1):
        mean += (x - mean) / i
        cumulative += x - mean - delta
        minimum = min(minimum, cumulative)
        if cumulative - minimum > threshold:
            changes.append(i - 1)
            mean, cumulative, minimum = 0.0, 0.0, 0.0
    return changes

"""Choosing hyperparameters without touching the test window.

Two independent routes are implemented, and the thesis compares them:

1. *Label-assisted inner validation.* The training window is split again in
   time; candidates are ranked by Average Precision on the inner validation
   slice, using only labels that predate the deployment moment. This mirrors
   the assumption already granted to the supervised reference — historical
   labels exist, current ones do not.

2. *Fully unsupervised criteria.* Excess-Mass (EM) and Mass-Volume (MV)
   curves rank scoring functions by how tightly their level sets concentrate
   probability mass into small volume, with no labels at all. Estimating a
   Lebesgue measure in 29 dimensions by Monte Carlo is hopeless, so the
   standard remedy is used: the criteria are averaged over random
   low-dimensional feature subspaces, with the detector refitted in each
   subspace.

The interesting question is not which route wins, but whether they agree: if
the unsupervised criterion selects the same configuration, then in a genuine
no-label deployment nothing was lost.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score


@dataclass(frozen=True)
class InnerSplit:
    """Temporal split *inside* the training window."""

    fit_end: int
    val_end: int


def inner_temporal_split(n_train_rows: int, val_fraction: float) -> InnerSplit:
    if not 0.0 < val_fraction < 1.0:
        raise ValueError("val_fraction must be in (0, 1)")
    fit_end = int(n_train_rows * (1.0 - val_fraction))
    return InnerSplit(fit_end=fit_end, val_end=n_train_rows)


def inner_validation_ap(y_val: np.ndarray, scores_val: np.ndarray) -> float:
    """Ranking quality on the inner validation slice; NaN if it holds no
    positives, so a degenerate slice cannot silently decide a search."""
    if int((y_val == 1).sum()) == 0:
        return float("nan")
    return float(average_precision_score(y_val, scores_val))


def _em_mv_one_subspace(
    anomaly_train: np.ndarray,
    anomaly_uniform: np.ndarray,
    box_volume: float,
    t_grid: np.ndarray,
    alpha_grid: np.ndarray,
) -> tuple[float, float]:
    """EM and MV summary statistics for one feature subspace.

    EM(t) = sup_u [ P(s >= u) - t * Leb(s >= u) ], higher is better.
    MV(a) = Leb(s >= u_a) where P(s >= u_a) = a,  lower is better.

    Both are defined for a *normality* score whose upper level sets are the
    dense regions. Everything else in this project uses the opposite
    convention (higher = more anomalous), so the sign is flipped here rather
    than at each call site. Getting this backwards is not a subtle error: with
    anomaly scores, uniformly drawn points fill every upper level set and the
    estimated volume collapses to the whole bounding box.
    """
    score_train = -np.asarray(anomaly_train, dtype=float)
    score_uniform = -np.asarray(anomaly_uniform, dtype=float)
    thresholds = np.unique(np.quantile(score_train, np.linspace(0.0, 1.0, 512)))
    # EM(t) is a supremum over all real thresholds, and the empty level set —
    # any threshold above every observed score — always contributes exactly
    # zero. Leaving that point out of the grid lets the supremum come back
    # negative, which is not a valid excess mass. It happens in practice: a
    # coarse histogram model calls sparse regions normal, so the level set at
    # the largest observed score still encloses a large volume.
    ceiling = float(max(score_train.max(), score_uniform.max())) + 1.0
    thresholds = np.append(thresholds, ceiling)
    mass = np.array([(score_train >= u).mean() for u in thresholds])
    volume = np.array([(score_uniform >= u).mean() * box_volume for u in thresholds])

    em_curve = np.array([np.max(mass - t * volume) for t in t_grid])
    em_auc = float(np.trapezoid(em_curve, t_grid))

    # MV: for each target mass, the smallest level-set volume achieving it.
    mv_vals = []
    for a in alpha_grid:
        feasible = volume[mass >= a]
        mv_vals.append(feasible.min() if len(feasible) else np.nan)
    mv_curve = np.array(mv_vals, dtype=float)
    mv_auc = float(np.trapezoid(mv_curve, alpha_grid)) if np.all(np.isfinite(mv_curve)) else np.nan
    return em_auc, mv_auc


def em_mv_scores(
    fit_score_fn,
    X_train: np.ndarray,
    n_subspaces: int = 10,
    subspace_dim: int = 5,
    n_mc: int = 20000,
    seed: int = 42,
    t_max: float = 0.9,
    alpha_lo: float = 0.9,
    alpha_hi: float = 0.999,
) -> dict:
    """Average EM/MV over random feature subspaces.

    `fit_score_fn(X_sub) -> callable(Z) -> scores` must fit a detector on the
    given subspace and return its scoring function (higher = more anomalous).
    """
    rng = np.random.default_rng(seed)
    d = X_train.shape[1]
    dim = min(subspace_dim, d)
    t_grid = np.linspace(0.0, t_max, 256)
    alpha_grid = np.linspace(alpha_lo, alpha_hi, 128)

    em_list, mv_list = [], []
    for _ in range(n_subspaces):
        feats = np.sort(rng.choice(d, size=dim, replace=False))
        Xs = X_train[:, feats]
        lo, hi = Xs.min(axis=0), Xs.max(axis=0)
        span = np.maximum(hi - lo, 1e-9)
        # log-volume first: a 5-D box over standardised features can overflow
        # float64 if any feature has a very long tail.
        log_vol = float(np.sum(np.log(span)))
        if log_vol > 700:  # exp() would overflow; subspace is unusable
            continue
        box_volume = float(np.exp(log_vol))
        U = rng.uniform(lo, hi, size=(n_mc, dim))

        scorer = fit_score_fn(Xs)
        em, mv = _em_mv_one_subspace(
            np.asarray(scorer(Xs), dtype=float),
            np.asarray(scorer(U), dtype=float),
            box_volume,
            t_grid,
            alpha_grid,
        )
        em_list.append(em)
        mv_list.append(mv)

    if not em_list:
        return {"em_auc": float("nan"), "mv_auc": float("nan"), "n_subspaces_used": 0}
    return {
        "em_auc": float(np.nanmean(em_list)),
        "mv_auc": float(np.nanmean(mv_list)),
        "em_std": float(np.nanstd(em_list)),
        "mv_std": float(np.nanstd(mv_list)),
        "n_subspaces_used": len(em_list),
    }


def selection_agreement(table: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Which configuration each criterion would have picked, side by side.

    `table` holds one row per candidate with columns inner_ap, em_auc, mv_auc.
    EM is maximised, MV is minimised, inner AP is maximised.
    """
    rows = []
    for model, grp in table.groupby("model"):
        pick = {
            "model": model,
            "best_by_inner_ap": grp.loc[grp["inner_ap"].idxmax(), by].to_dict()
            if grp["inner_ap"].notna().any()
            else None,
            "best_by_em": grp.loc[grp["em_auc"].idxmax(), by].to_dict()
            if grp["em_auc"].notna().any()
            else None,
            "best_by_mv": grp.loc[grp["mv_auc"].idxmin(), by].to_dict()
            if grp["mv_auc"].notna().any()
            else None,
        }
        pick["em_agrees_with_ap"] = pick["best_by_em"] == pick["best_by_inner_ap"]
        pick["mv_agrees_with_ap"] = pick["best_by_mv"] == pick["best_by_inner_ap"]
        rows.append(pick)
    return pd.DataFrame(rows)

"""Choosing hyperparameters without touching the test window.

The training window is split again in time, and candidates are ranked by
Average Precision on the inner validation slice, using only labels that
predate the deployment moment. This mirrors the assumption already granted to
the supervised reference: historical labels exist, current ones do not.
"""

from dataclasses import dataclass

import numpy as np
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

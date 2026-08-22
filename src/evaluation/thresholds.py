"""Threshold selection.

Primary protocol: the (1 - contamination) percentile of the TRAINING-score
distribution. Contamination is a hyperparameter (default: the fraud rate
observed in the training window); test labels are never involved.

The oracle best-F1 threshold on test is reported separately, clearly labelled,
as an upper bound only.
"""

import numpy as np
from sklearn.metrics import precision_recall_curve


def percentile_threshold(train_scores: np.ndarray, contamination: float) -> float:
    return float(np.quantile(train_scores, 1.0 - contamination))


def oracle_best_f1_threshold(y_true: np.ndarray, test_scores: np.ndarray) -> float:
    """UPPER BOUND ONLY: uses test labels. Never feed this back into anything."""
    precision, recall, thresholds = precision_recall_curve(y_true, test_scores)
    # precision/recall have one more entry than thresholds; drop the last point.
    f1 = 2 * precision[:-1] * recall[:-1] / np.clip(precision[:-1] + recall[:-1], 1e-12, None)
    return float(thresholds[int(np.argmax(f1))])


def adaptive_quantile_thresholds(
    scores: np.ndarray,
    contamination: float,
    window: int = 5000,
    refresh_every: int = 500,
    warmup_threshold: float | None = None,
    min_warmup: int = 500,
) -> np.ndarray:
    """Causal sliding-window threshold, one value per incoming message.

    A threshold fixed at training time assumes the score distribution never
    moves. It does move — when it drifts upward the alert queue floods, and
    when it drifts downward the detector goes quiet — so the workload a static
    threshold produces is unpredictable exactly when the data is hardest.

    This recomputes the (1 - contamination) quantile from the most recent
    `window` scores, refreshed every `refresh_every` messages to bound the
    cost. The decision for message i uses only messages before i: the score
    being judged is never part of the buffer that judges it, which is what
    makes the procedure honest on a stream.

    `warmup_threshold` (typically the training-percentile threshold) is used
    until `min_warmup` messages have accumulated.
    """
    from collections import deque

    n = len(scores)
    out = np.empty(n, dtype=float)
    buffer: deque[float] = deque(maxlen=window)
    current = warmup_threshold if warmup_threshold is not None else float("inf")

    for i, s in enumerate(scores):
        if len(buffer) >= min_warmup and i % refresh_every == 0:
            current = float(np.quantile(buffer, 1.0 - contamination))
        out[i] = current
        buffer.append(float(s))
    return out

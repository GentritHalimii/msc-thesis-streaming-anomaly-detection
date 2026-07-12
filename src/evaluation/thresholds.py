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

"""Detection metrics. Average Precision is primary: at 0.172% positives,
accuracy and ROC-AUC are misleading (ROC-AUC still reported, with that caveat
attached in the thesis text)."""

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def threshold_free_metrics(y_true: np.ndarray, scores: np.ndarray) -> dict:
    return {
        "ap": float(average_precision_score(y_true, scores)),
        "roc_auc": float(roc_auc_score(y_true, scores)),
    }


def thresholded_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    # >= matches sklearn's precision_recall_curve threshold convention.
    pred = (scores >= threshold).astype(int)
    return {
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "n_alerts": int(pred.sum()),
    }

"""Threshold and metric math against hand-computed toy examples."""

import numpy as np

from src.evaluation.metrics import threshold_free_metrics, thresholded_metrics
from src.evaluation.thresholds import oracle_best_f1_threshold, percentile_threshold


def test_percentile_threshold_flags_expected_fraction():
    train_scores = np.arange(10000, dtype=float)
    thr = percentile_threshold(train_scores, contamination=0.01)
    assert np.isclose((train_scores >= thr).mean(), 0.01, atol=1e-3)


def test_percentile_threshold_uses_no_labels():
    """The signature alone enforces it, but assert the value depends only on
    scores: permuting scores changes nothing."""
    rng = np.random.default_rng(0)
    scores = rng.normal(size=5000)
    thr1 = percentile_threshold(scores, 0.02)
    thr2 = percentile_threshold(rng.permutation(scores), 0.02)
    assert thr1 == thr2


def test_oracle_threshold_perfect_separation():
    y = np.array([0, 0, 0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.3, 0.4, 0.8, 0.9])
    thr = oracle_best_f1_threshold(y, scores)
    m = thresholded_metrics(y, scores, thr)
    assert m["f1"] == 1.0 and m["precision"] == 1.0 and m["recall"] == 1.0


def test_thresholded_metrics_hand_computed():
    y = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.9, 0.6, 0.7, 0.8, 0.05])
    m = thresholded_metrics(y, scores, threshold=0.55)
    # alerts: 0.9 (FP), 0.6/0.7/0.8 (TP) -> precision 3/4, recall 3/4
    assert m["n_alerts"] == 4
    assert np.isclose(m["precision"], 0.75)
    assert np.isclose(m["recall"], 0.75)
    assert np.isclose(m["f1"], 0.75)


def test_threshold_free_metrics_perfect_ranking():
    y = np.array([0, 0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.3, 0.8, 0.9])
    m = threshold_free_metrics(y, scores)
    assert m["ap"] == 1.0 and m["roc_auc"] == 1.0

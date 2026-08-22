"""Statistical comparison utilities."""

import numpy as np
import pandas as pd

from src.evaluation.stats import (
    average_ranks,
    friedman,
    holm_correction,
    nemenyi_critical_difference,
    rank_matrix,
    wilcoxon_pairs,
)


def test_rank_matrix_ranks_best_as_one():
    df = pd.DataFrame({"good": [0.9, 0.8], "bad": [0.1, 0.2]})
    r = rank_matrix(df)
    assert (r["good"] == 1).all()
    assert (r["bad"] == 2).all()


def test_average_ranks_are_sorted_best_first():
    df = pd.DataFrame({"mid": [0.5] * 4, "best": [0.9] * 4, "worst": [0.1] * 4})
    assert list(average_ranks(df).index) == ["best", "mid", "worst"]


def test_friedman_detects_clear_separation():
    rng = np.random.default_rng(0)
    df = pd.DataFrame(
        {
            "a": rng.normal(0.9, 0.01, 8),
            "b": rng.normal(0.5, 0.01, 8),
            "c": rng.normal(0.1, 0.01, 8),
        }
    )
    assert friedman(df)["p_value"] < 0.01


def test_friedman_needs_enough_folds():
    assert np.isnan(friedman(pd.DataFrame({"a": [1.0, 2.0], "b": [2.0, 1.0]}))["p_value"])


def test_critical_difference_grows_with_models_and_shrinks_with_folds():
    assert nemenyi_critical_difference(14, 8) > nemenyi_critical_difference(4, 8)
    assert nemenyi_critical_difference(4, 20) < nemenyi_critical_difference(4, 6)


def test_holm_is_monotone_and_at_least_raw():
    p = np.array([0.01, 0.02, 0.04])
    adj = holm_correction(p)
    assert np.all(adj >= p)
    assert np.all(np.diff(adj[np.argsort(p)]) >= 0)
    # single hypothesis is unchanged
    assert holm_correction(np.array([0.03]))[0] == 0.03


def test_wilcoxon_reports_attainable_floor():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"a": rng.normal(0.6, 0.01, 8), "b": rng.normal(0.4, 0.01, 8)})
    out = wilcoxon_pairs(df, [("a", "b")]).iloc[0]
    assert out["wins_a"] == 8
    assert out["p_value"] == out["min_attainable_p"] == 2 / 2**8

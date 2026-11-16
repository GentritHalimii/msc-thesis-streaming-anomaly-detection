"""Alert-budget, cost and throughput metrics against hand-computed cases."""

import numpy as np
import pytest
from sklearn.metrics import average_precision_score

from src.evaluation.operational import (
    amount_weighted_average_precision,
    budget_metrics,
    net_savings,
    stream_throughput,
    top_k_mask,
)

Y = np.array([1, 0, 1, 0, 0, 1])
SCORES = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.1])
AMOUNTS = np.array([100.0, 5.0, 50.0, 5.0, 5.0, 500.0])


def test_top_k_selects_exactly_k():
    assert top_k_mask(SCORES, 3).sum() == 3
    assert top_k_mask(SCORES, 99).sum() == len(SCORES)
    assert top_k_mask(SCORES, 0).sum() == 0


def test_budget_metrics_hand_computed():
    # top 3 = scores .9/.8/.7 -> frauds at .9 and .7 caught, one FP
    m = budget_metrics(Y, SCORES, AMOUNTS, k=3)
    assert m["tp"] == 2
    assert m["precision_at_k"] == 2 / 3
    assert m["recall_at_k"] == 2 / 3
    # caught 100 + 50 of 100 + 50 + 500 fraudulent euros
    assert m["amount_recall_at_k"] == 150 / 650
    assert m["caught_amount_eur"] == 150.0


def test_net_savings_accounts_for_investigation_cost():
    s = net_savings(Y, SCORES, AMOUNTS, k=3, investigation_cost=10.0)
    assert s["net_savings_eur"] == 150.0 - 30.0
    # perfect detector: catches all 650 euros with exactly 3 investigations
    assert s["ideal_savings_eur"] == 650.0 - 30.0


def test_amount_weighted_ap_rewards_expensive_frauds_first():
    """Both rankings put one fraud below a legitimate transaction, so plain AP
    is identical; only which fraud got demoted differs. The weighted metric
    must prefer demoting the cheap one."""
    # order: fraud(100), fraud(50), normal, fraud(500) -> expensive one demoted
    cheap_first = np.array([0.9, 0.5, 0.8, 0.4, 0.3, 0.2])
    # order: fraud(500), fraud(100), normal, fraud(50) -> cheap one demoted
    expensive_first = np.array([0.8, 0.5, 0.2, 0.4, 0.3, 0.9])

    plain_a = average_precision_score(Y, cheap_first)
    plain_b = average_precision_score(Y, expensive_first)
    assert plain_a == pytest.approx(plain_b), "control: plain AP must be blind to amount"

    a = amount_weighted_average_precision(Y, cheap_first, AMOUNTS)
    b = amount_weighted_average_precision(Y, expensive_first, AMOUNTS)
    assert b > a
    assert 0.0 <= a <= 1.0 and 0.0 <= b <= 1.0


def test_top_k_breaks_ties_in_favour_of_the_earlier_transaction():
    """A vote produces many equal scores; the alerts that fit in the budget
    must then be the earliest ones, as they would be on a stream."""
    scores = np.array([1.0, 0.5, 1.0, 1.0, 0.5])
    mask = top_k_mask(scores, 2)
    assert mask.tolist() == [True, False, True, False, False]


def test_stream_throughput_counts_only_the_live_window():
    """1000 messages created 2 ms apart, each decided 10 ms after creation:
    the stream is live for 999 * 2 ms + 10 ms, whatever happened before."""
    produced = 1_700_000_000_000_000_000 + np.arange(1000, dtype=np.int64) * 2_000_000
    e2e = np.full(1000, 10.0)
    assert stream_throughput(produced, e2e) == pytest.approx(1000 / 2.008)

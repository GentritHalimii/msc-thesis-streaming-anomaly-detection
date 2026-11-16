"""Operational metrics: what the detector is worth to the team that runs it.

Average Precision summarises the whole ranking, but no fraud team reviews a
whole ranking — it reviews the top k alerts a shift can absorb. These metrics
therefore evaluate the ranking the way it would actually be consumed:

* precision/recall at a fixed alert budget k;
* the money actually recovered, since a missed EUR 2 fraud and a missed
  EUR 2000 fraud are not the same mistake;
* net savings under an explicit cost model, which is the only figure that can
  say whether running the detector at all is worthwhile;
* throughput of the streaming pipeline, measured only while the stream is live.
"""

import numpy as np


def top_k_mask(scores: np.ndarray, k: int) -> np.ndarray:
    """Mask of the k highest-scoring items.

    Ties are broken by position, which is chronological: the earlier
    transaction wins, as it would in a stream. A stable sort is what makes
    that true; a partition-based selection would pick among tied items in an
    unspecified order, which matters for coarse scores such as a vote.
    """
    k = min(int(k), len(scores))
    mask = np.zeros(len(scores), dtype=bool)
    if k > 0:
        mask[np.argsort(-np.asarray(scores), kind="stable")[:k]] = True
    return mask


def budget_metrics(y_true: np.ndarray, scores: np.ndarray, amounts: np.ndarray, k: int) -> dict:
    """Detection quality when only the top k alerts are investigated."""
    sel = top_k_mask(scores, k)
    tp = int(np.sum(sel & (y_true == 1)))
    n_alerts = int(sel.sum())
    n_frauds = int((y_true == 1).sum())
    fraud_amount_total = float(amounts[y_true == 1].sum())
    caught_amount = float(amounts[sel & (y_true == 1)].sum())
    return {
        "budget_k": int(k),
        "alerts": n_alerts,
        "tp": tp,
        "precision_at_k": tp / n_alerts if n_alerts else 0.0,
        "recall_at_k": tp / n_frauds if n_frauds else 0.0,
        "amount_recall_at_k": caught_amount / fraud_amount_total if fraud_amount_total else 0.0,
        "caught_amount_eur": caught_amount,
    }


def net_savings(
    y_true: np.ndarray,
    scores: np.ndarray,
    amounts: np.ndarray,
    k: int,
    investigation_cost: float,
) -> dict:
    """Net euros saved by investigating the top k alerts.

    Model: a fraud that is caught saves its transaction amount; every alert
    raised (true or false) costs one investigation. A fraud that is missed
    costs its amount, but that loss is incurred with or without the detector,
    so it does not enter the *net saving* — it is the baseline being improved.
    Normalisation is against the perfect detector, which catches every fraud
    while raising exactly as many alerts as there are frauds.
    """
    sel = top_k_mask(scores, k)
    caught = float(amounts[sel & (y_true == 1)].sum())
    n_alerts = int(sel.sum())
    saved = caught - investigation_cost * n_alerts
    n_frauds = int((y_true == 1).sum())
    ideal = float(amounts[y_true == 1].sum()) - investigation_cost * n_frauds
    return {
        "budget_k": int(k),
        "net_savings_eur": saved,
        "ideal_savings_eur": ideal,
        "savings_ratio": saved / ideal if ideal > 0 else np.nan,
    }


def budget_curve(
    y_true: np.ndarray,
    scores: np.ndarray,
    amounts: np.ndarray,
    budgets: list[int],
    investigation_cost: float,
) -> list[dict]:
    return [
        budget_metrics(y_true, scores, amounts, k)
        | net_savings(y_true, scores, amounts, k, investigation_cost)
        for k in budgets
    ]


def amount_weighted_average_precision(
    y_true: np.ndarray, scores: np.ndarray, amounts: np.ndarray
) -> float:
    """Average precision in which each fraud counts in proportion to its value.

    Implemented as a weighted AP: a fraudulent transaction of amount a is
    weighted a / (mean fraud amount), so the weights of the positive class
    average to one and the metric stays on the familiar [0, 1] scale and stays
    directly comparable with the unweighted AP. Legitimate transactions keep
    weight one. A detector that ranks the expensive frauds highest scores
    above one that finds the same *number* of frauds but only cheap ones.
    """
    from sklearn.metrics import average_precision_score

    pos = y_true == 1
    if pos.sum() == 0:
        return float("nan")
    mean_fraud_amount = float(amounts[pos].mean())
    if mean_fraud_amount <= 0:
        return float("nan")
    weights = np.ones(len(y_true), dtype=float)
    weights[pos] = amounts[pos] / mean_fraud_amount
    return float(average_precision_score(y_true, scores, sample_weight=weights))


def stream_throughput(produced_at_ns: np.ndarray, e2e_ms: np.ndarray) -> float:
    """Messages per second from the creation of the first message to the
    decision on the last one.

    A clock started by the consumer would open before the producer process
    exists and also count its start-up (interpreter, imports, reading the
    dataset), 1.2 to 2.1 s in these runs. On a 10 s run at 2000 msg/s that
    alone reads as an 11-14% shortfall although the consumer never falls
    behind, which the flat end-to-end latency confirms.
    """
    produced = np.asarray(produced_at_ns, dtype=np.int64)
    # Offsets from the first message keep nanosecond epochs exact in float64.
    offset_s = (produced - produced.min()) / 1e9
    decided_s = offset_s + np.asarray(e2e_ms, dtype=float) / 1e3
    return float(len(produced) / decided_s.max())

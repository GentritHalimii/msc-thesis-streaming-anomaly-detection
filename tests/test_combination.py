"""Score combination: normalisation, combiners and prequential selection."""

import numpy as np
import pytest

from src.evaluation.combination import (
    COMBINERS,
    combine,
    greedy_forward_selection,
    rank_normalise,
)


class _FakeFold:
    """Minimal stand-in for a saved fold, with controllable scores."""

    def __init__(self, scores: dict[str, np.ndarray], y: np.ndarray):
        self._scores = {k: np.asarray(v, dtype=float) for k, v in scores.items()}
        self.y = np.asarray(y)
        self.costs = {
            k: {"train_score_mean": float(v.mean()), "train_score_std": float(v.std()) or 1.0}
            for k, v in self._scores.items()
        }

    def test_scores(self, name):
        return self._scores[name]

    def train_rank_of(self, name, scores):
        ref = np.sort(self._scores[name])
        return np.searchsorted(ref, scores, side="right") / len(ref)

    def train_threshold(self, name, contamination):
        return float(np.quantile(self._scores[name], 1.0 - contamination))


@pytest.fixture
def fold():
    # 'good' ranks the two positives on top; 'bad' is inverted; 'flat' is noise
    return _FakeFold(
        {
            "good": [0.1, 0.2, 0.9, 0.95],
            "bad": [0.95, 0.9, 0.2, 0.1],  # exact rank reversal of "good"
            "flat": [0.5, 0.5, 0.5, 0.5],
        },
        y=[0, 0, 1, 1],
    )


def test_rank_normalisation_is_bounded_and_monotone(fold):
    r = rank_normalise(fold, "good")
    assert np.all((r >= 0) & (r <= 1))
    assert np.all(np.diff(r) >= 0), "monotone in the original score"


@pytest.mark.parametrize("mode", COMBINERS)
def test_every_combiner_returns_one_score_per_row(fold, mode):
    out = combine(fold, ["good", "bad"], mode, contamination=0.5)
    assert out.shape == (4,)
    assert np.all(np.isfinite(out))


def test_unknown_combiner_and_empty_membership_rejected(fold):
    with pytest.raises(ValueError, match="combiner"):
        combine(fold, ["good"], "stacking")
    with pytest.raises(ValueError, match="at least one"):
        combine(fold, [], "rank_avg")


def test_max_combiner_keeps_a_good_member_visible(fold):
    """Averaging a good member with an inverted one cancels the signal; taking
    the maximum keeps whichever member fired."""
    avg = combine(fold, ["good", "bad"], "rank_avg")
    mx = combine(fold, ["good", "bad"], "max")
    assert np.ptp(avg) < 1e-9, "opposite members must cancel under averaging"
    assert np.ptp(mx) > 0


def test_greedy_selection_prefers_the_useful_member(fold):
    picked = greedy_forward_selection(
        [fold], ["good", "bad", "flat"], "rank_avg", max_members=3, contamination=0.5
    )
    assert picked[0] == "good", "the first pick must be the member that ranks correctly"


def test_greedy_selection_stops_when_nothing_improves(fold):
    picked = greedy_forward_selection(
        [fold], ["good"], "rank_avg", max_members=5, contamination=0.5
    )
    assert len(picked) == 1, "no candidate can improve on a perfect ranking"

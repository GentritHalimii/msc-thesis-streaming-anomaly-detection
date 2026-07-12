"""Ensemble combination math with stub members — no real artifacts needed."""

import numpy as np
import pytest

from src.models.base import AnomalyModel
from src.models.ensemble import MAJORITY_THRESHOLD, EnsembleModel


class _Stub(AnomalyModel):
    def __init__(self, name, values):
        self.name = name
        self._values = np.asarray(values, dtype=float)

    def fit(self, X):
        return self

    def score(self, X):
        return self._values

    def save(self, path):
        raise NotImplementedError

    @classmethod
    def load(cls, path):
        raise NotImplementedError


def _make(mode):
    members = {
        "a": _Stub("a", [1.0, 3.0]),
        "b": _Stub("b", [10.0, 30.0]),
        "c": _Stub("c", [0.0, 100.0]),
    }
    return EnsembleModel(
        mode=mode,
        member_names=["a", "b", "c"],
        train_means={"a": 2.0, "b": 20.0, "c": 50.0},
        train_stds={"a": 1.0, "b": 10.0, "c": 50.0},
        member_thresholds={"a": 2.0, "b": 25.0, "c": 50.0},
        members=members,
    )


def test_avg_is_mean_of_train_z_scores():
    scores = _make("avg").score(np.zeros((2, 29)))
    # row0: z = (-1, -1, -1) -> -1 ; row1: z = (1, 1, 1) -> 1
    np.testing.assert_allclose(scores, [-1.0, 1.0])


def test_vote_is_fraction_of_member_votes():
    scores = _make("vote").score(np.zeros((2, 29)))
    # row0: votes (0, 0, 0) -> 0 ; row1: votes (1, 1, 1) -> 1
    np.testing.assert_allclose(scores, [0.0, 1.0])
    # majority rule: a 2-of-3 vote (2/3) must exceed the deployment threshold
    assert 2 / 3 >= MAJORITY_THRESHOLD > 1 / 3


def test_ensemble_rejects_unknown_mode_and_refit():
    with pytest.raises(ValueError, match="mode"):
        _make("stacking")
    with pytest.raises(NotImplementedError):
        _make("avg").fit(np.zeros((2, 29)))

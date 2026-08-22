"""Unsupervised model-selection criteria and inner-validation splitting."""

import numpy as np
import pytest
from sklearn.ensemble import IsolationForest

from src.evaluation.model_selection import (
    em_mv_scores,
    inner_temporal_split,
    inner_validation_ap,
)


def test_inner_split_keeps_validation_at_the_end():
    s = inner_temporal_split(1000, 0.25)
    assert s.fit_end == 750 and s.val_end == 1000


def test_inner_split_rejects_degenerate_fraction():
    with pytest.raises(ValueError):
        inner_temporal_split(100, 0.0)


def test_inner_ap_is_nan_without_positives():
    assert np.isnan(inner_validation_ap(np.zeros(10, int), np.arange(10.0)))


def _iforest_factory(n_estimators):
    def fit_score(X_sub):
        model = IsolationForest(n_estimators=n_estimators, random_state=0).fit(X_sub)
        return lambda Z: -model.score_samples(Z)

    return fit_score


def _random_scorer(X_sub):
    rng = np.random.default_rng(7)
    return lambda Z: rng.normal(size=len(Z))


@pytest.fixture(scope="module")
def gaussian_blob():
    return np.random.default_rng(0).normal(size=(3000, 12))


def test_em_mv_prefer_a_real_detector_over_a_random_one(gaussian_blob):
    """The whole point of these criteria is ranking detectors without labels;
    if they cannot separate a fitted forest from noise they are useless."""
    good = em_mv_scores(
        _iforest_factory(150), gaussian_blob, n_subspaces=4, subspace_dim=4, n_mc=5000, seed=1
    )
    noise = em_mv_scores(
        _random_scorer, gaussian_blob, n_subspaces=4, subspace_dim=4, n_mc=5000, seed=1
    )
    assert good["em_auc"] > noise["em_auc"], "EM must reward mass concentration"
    assert good["mv_auc"] < noise["mv_auc"], "MV must penalise diffuse level sets"


def test_em_is_non_negative(gaussian_blob):
    """EM(t) is a supremum that always admits the empty level set, so a
    negative value means the score convention has been flipped."""
    r = em_mv_scores(
        _iforest_factory(100), gaussian_blob, n_subspaces=3, subspace_dim=4, n_mc=4000, seed=2
    )
    assert r["em_auc"] >= 0.0

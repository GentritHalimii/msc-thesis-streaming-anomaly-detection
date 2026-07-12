"""Model-interface contracts on synthetic data: score direction (higher =
more anomalous), save/load fidelity, deterministic refits."""

import numpy as np
import pytest

from src.models.autoencoder import AutoencoderModel
from src.models.iforest import IForestModel
from src.models.logreg import LogRegReference
from src.models.ocsvm import OCSVMModel

N_FEATURES = 29


@pytest.fixture(scope="module")
def synth():
    rng = np.random.default_rng(0)
    X_train = rng.normal(0, 1, size=(2000, N_FEATURES))
    X_test = rng.normal(0, 1, size=(200, N_FEATURES))
    outliers = rng.normal(8, 1, size=(20, N_FEATURES))
    return X_train, np.vstack([X_test, outliers]), len(X_test)


def make_models():
    return [
        IForestModel(n_estimators=50, max_samples=128, seed=1),
        OCSVMModel(train_subsample=1000, nu=0.05, seed=1),
        AutoencoderModel(epochs=5, batch_size=256, seed=1),
    ]


@pytest.mark.parametrize("model", make_models(), ids=lambda m: m.name)
def test_outliers_score_higher(synth, model):
    X_train, X_scored, n_inlier = synth
    scores = model.fit(X_train).score(X_scored)
    assert scores.shape == (len(X_scored),)
    assert np.median(scores[n_inlier:]) > np.median(scores[:n_inlier])
    # every planted extreme outlier beats the inlier median
    assert scores[n_inlier:].min() > np.median(scores[:n_inlier])


@pytest.mark.parametrize("model", make_models(), ids=lambda m: m.name)
def test_save_load_roundtrip_scores_identical(tmp_path, synth, model):
    X_train, X_scored, _ = synth
    model.fit(X_train)
    before = model.score(X_scored)
    path = tmp_path / "model.bin"
    model.save(path)
    after = type(model).load(path).score(X_scored)
    np.testing.assert_array_equal(before, after)


def test_refit_is_deterministic(synth):
    X_train, X_scored, _ = synth
    for a, b in zip(make_models(), make_models(), strict=True):
        s1 = a.fit(X_train).score(X_scored)
        s2 = b.fit(X_train).score(X_scored)
        np.testing.assert_array_equal(s1, s2, err_msg=a.name)


def test_logreg_requires_labels(synth):
    X_train, _, _ = synth
    with pytest.raises(ValueError, match="supervised"):
        LogRegReference().fit(X_train)


def test_logreg_scores_frauds_higher(synth):
    rng = np.random.default_rng(2)
    X_train, X_scored, n_inlier = synth
    y = np.zeros(len(X_train) + 30, dtype=int)
    y[-30:] = 1
    X = np.vstack([X_train, rng.normal(8, 1, size=(30, N_FEATURES))])
    scores = LogRegReference(seed=1).fit(X, y).score(X_scored)
    assert np.median(scores[n_inlier:]) > np.median(scores[:n_inlier])

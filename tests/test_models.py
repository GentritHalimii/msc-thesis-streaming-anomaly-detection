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


# --- autoencoder design space -------------------------------------------
# The Autoencoder study varies these levers one at a time, so each has to be
# wired correctly and each has to leave the detector functional.


def test_encoder_widths_taper_from_hidden_to_latent():
    from src.models.autoencoder import _encoder_widths

    assert _encoder_widths(29, 16, 8, depth=1) == [16]
    widths = _encoder_widths(29, 32, 4, depth=3)
    assert widths[0] == 32
    assert all(a >= b for a, b in zip(widths, widths[1:], strict=False)), "must narrow"
    assert widths[-1] > 4, "the taper stops above the latent dimension"


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"depth": 2, "hidden_dim": 32, "latent_dim": 6},
        {"loss": "mae"},
        {"loss": "huber"},
        {"noise_std": 0.25},
        {"dropout": 0.2},
        {"weight_decay": 1e-4},
    ],
    ids=["default", "deeper", "mae", "huber", "denoising", "dropout", "weight_decay"],
)
def test_every_autoencoder_variant_still_ranks_outliers_higher(synth, overrides):
    X_train, X_scored, n_inlier = synth
    model = AutoencoderModel(epochs=6, batch_size=256, seed=1, **overrides)
    scores = model.fit(X_train).score(X_scored)
    assert np.median(scores[n_inlier:]) > np.median(scores[:n_inlier])


def test_autoencoder_rejects_an_unknown_loss():
    with pytest.raises(ValueError, match="unknown loss"):
        AutoencoderModel(loss="cross_entropy")


def test_deeper_encoder_requires_a_real_bottleneck():
    """A taper that does not narrow is a different architecture, not a deeper
    one, so the constructor refuses it instead of silently building it."""
    with pytest.raises(ValueError, match="latent_dim"):
        AutoencoderModel(hidden_dim=8, latent_dim=8, depth=3)


def test_training_history_is_recorded_and_decreases(synth):
    X_train, _, _ = synth
    model = AutoencoderModel(epochs=10, batch_size=256, seed=1).fit(X_train)
    assert len(model.history) == 10
    assert model.history[-1] < model.history[0], "training loss should fall"


def test_per_feature_reconstruction_error_sums_to_the_score(synth):
    """The per-component error is the model's own account of its score, so the
    two must agree; if they drift apart the explanation is fiction."""
    X_train, X_scored, _ = synth
    model = AutoencoderModel(epochs=5, batch_size=256, seed=1).fit(X_train)
    per_feature = model.reconstruction_error_per_feature(X_scored)
    assert per_feature.shape == (X_scored.shape[1],)
    np.testing.assert_allclose(per_feature.mean(), model.score(X_scored).mean(), rtol=1e-5)


def test_history_survives_the_save_load_roundtrip(tmp_path, synth):
    X_train, _, _ = synth
    model = AutoencoderModel(epochs=4, batch_size=256, seed=1).fit(X_train)
    path = tmp_path / "ae.pt"
    model.save(path)
    assert AutoencoderModel.load(path).history == model.history

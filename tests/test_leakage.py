"""Leakage guards: no statistic used at inference time may depend on the test window."""

import numpy as np

from src.data.load import FEATURE_COLUMNS
from src.data.scale import fit_scaler, transform


def test_scaler_statistics_come_from_training_window_only(split):
    scaler = fit_scaler(split.train_full)
    expected_mean = split.train_full[FEATURE_COLUMNS].to_numpy().mean(axis=0)
    expected_var = split.train_full[FEATURE_COLUMNS].to_numpy().var(axis=0)
    np.testing.assert_allclose(scaler.mean_, expected_mean, rtol=1e-10)
    np.testing.assert_allclose(scaler.var_, expected_var, rtol=1e-10)


def test_scaler_differs_from_full_dataset_fit(df, split):
    """If someone ever fits on the full dataset, these statistics would match —
    they must not."""
    train_scaler = fit_scaler(split.train_full)
    full_scaler = fit_scaler(df)
    assert not np.allclose(train_scaler.mean_, full_scaler.mean_)


def test_transform_does_not_refit(split):
    """Transforming test data must not change the scaler's statistics."""
    scaler = fit_scaler(split.train_full)
    mean_before = scaler.mean_.copy()
    var_before = scaler.var_.copy()
    transform(scaler, split.test)
    np.testing.assert_array_equal(scaler.mean_, mean_before)
    np.testing.assert_array_equal(scaler.var_, var_before)


def test_time_is_not_a_feature():
    assert "Time" not in FEATURE_COLUMNS
    assert "Class" not in FEATURE_COLUMNS
    assert len(FEATURE_COLUMNS) == 29

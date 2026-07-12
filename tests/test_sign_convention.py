"""Explicit sign-convention check on REAL data: for every saved model,
higher score = more anomalous, i.e. the median score of test-window frauds
exceeds the median score of test-window normals. Complements the synthetic
checks in test_models.py. Skips when artifacts have not been trained yet."""

import numpy as np
import pytest

from src.config import load_config
from src.data.scale import load_scaler, transform
from src.models.build import ALL_MODELS, artifacts_dir, load_model


@pytest.mark.parametrize("name", ALL_MODELS)
def test_fraud_scores_exceed_normal_scores_on_test_window(split, name):
    cfg = load_config()
    if not (artifacts_dir(cfg) / "scaler.joblib").exists():
        pytest.skip("artifacts missing; run experiments.train_models first")
    scaler = load_scaler(artifacts_dir(cfg) / "scaler.joblib")
    scores = load_model(name, cfg).score(transform(scaler, split.test))
    y = split.test["Class"].to_numpy()
    assert np.median(scores[y == 1]) > np.median(scores[y == 0]), (
        f"{name}: sign convention violated (higher must mean more anomalous)"
    )

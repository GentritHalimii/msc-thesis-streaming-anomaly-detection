"""Rolling-origin protocol: fold geometry and the saved-score round trip."""

import numpy as np
import pytest

from src.evaluation.protocol import (
    QUANTILE_GRID,
    FoldScores,
    rolling_origin_folds,
    save_fold,
)


def test_folds_are_chronological_and_expanding():
    folds = rolling_origin_folds(1000, n_folds=5, initial_train_fraction=0.5)
    assert len(folds) == 5
    for prev, cur in zip(folds, folds[1:], strict=False):
        assert cur.train_end > prev.train_end, "training window must expand"
        assert cur.test_start == cur.train_end, "test block must start where training ends"
        assert prev.test_end == cur.test_start, "test blocks must tile without gaps"
    assert folds[0].train_end == 500
    assert folds[-1].test_end == 1000


def test_train_block_never_overlaps_its_own_test_block():
    for f in rolling_origin_folds(284807, 8, 0.4):
        assert f.train_end <= f.test_start
        assert f.test_end > f.test_start


def test_invalid_initial_fraction_rejected():
    with pytest.raises(ValueError):
        rolling_origin_folds(100, 3, 1.0)


def test_saved_fold_roundtrip_and_threshold(tmp_path):
    rng = np.random.default_rng(0)
    train_scores = rng.normal(size=50000)
    payload = {
        "y_test": np.array([0, 0, 1, 0], dtype=np.int8),
        "amount_test": np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32),
        "time_test": np.arange(4, dtype=np.float64),
        "tx_id_test": np.arange(4, dtype=np.int64),
        "test__demo": np.array([0.1, 0.2, 9.0, 0.3], dtype=np.float32),
        "trainq__demo": np.quantile(train_scores, QUANTILE_GRID),
        "costs_json": '{"demo": {"fit_time_s": 1.0}}',
    }
    save_fold(tmp_path, 0, payload)
    fs = FoldScores(tmp_path / "folds" / "fold0.npz")

    assert fs.models == ["demo"]
    np.testing.assert_array_equal(fs.y, [0, 0, 1, 0])
    assert fs.costs["demo"]["fit_time_s"] == 1.0

    # a 1% percentile threshold must flag ~1% of the training distribution
    thr = fs.train_threshold("demo", contamination=0.01)
    assert abs((train_scores >= thr).mean() - 0.01) < 2e-3

    # rank mapping puts scores on a [0, 1] training-quantile scale
    ranks = fs.train_rank_of("demo", np.array([train_scores.min(), 0.0, train_scores.max()]))
    assert ranks[0] == pytest.approx(0.0, abs=1e-6)
    assert ranks[2] == pytest.approx(1.0, abs=1e-6)
    assert 0.4 < ranks[1] < 0.6


def test_fold_scores_are_stored_at_full_precision():
    """float32 storage collapsed roughly 500 to 1000 of the ~21k test scores
    per fold into ties and moved Average Precision by up to 0.02 units. AP is
    dominated by the head of the ranking, so the primary metric must not
    depend on how the scores happen to be serialised."""
    import pandas as pd

    from src.config import load_config
    from src.data.load import FEATURE_COLUMNS
    from src.evaluation.protocol import Fold, run_fold

    rng = np.random.default_rng(0)
    n = 4000
    frame = pd.DataFrame(
        rng.normal(size=(n, len(FEATURE_COLUMNS) - 1)),
        columns=[c for c in FEATURE_COLUMNS if c != "Amount"],
    ).assign(
        Time=np.arange(n, dtype=float),
        Amount=rng.gamma(2.0, 30.0, n),
        Class=(rng.random(n) < 0.02).astype(int),
    )
    payload = run_fold(load_config(), Fold(index=0, train_end=3000, test_end=n), frame, ["iforest"])
    assert payload["test__iforest"].dtype == np.float64, "scores must keep full precision"

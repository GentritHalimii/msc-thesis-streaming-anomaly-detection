"""Chronological-split correctness: order, determinism, class handling."""

import pandas as pd

from src.config import REPO_ROOT
from src.data.load import load_transactions
from src.data.split import chronological_split


def test_every_train_time_precedes_every_test_time(split):
    assert split.train_full["Time"].max() <= split.test["Time"].min()


def test_split_covers_dataset_without_overlap(df, split):
    assert len(split.train_full) + len(split.test) == len(df)
    assert set(split.train_full.index).isdisjoint(split.test.index)


def test_train_normal_contains_zero_frauds(split):
    assert (split.train_normal["Class"] == 0).all()


def test_test_window_is_untouched(df, split):
    """Test window must be the exact chronological tail of the raw data."""
    cut = len(df) - len(split.test)
    pd.testing.assert_frame_equal(split.test, df.iloc[cut:])


def test_split_is_deterministic_across_runs(cfg, split):
    df2 = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split2 = chronological_split(df2, cfg.split.train_fraction)
    pd.testing.assert_frame_equal(split.train_full, split2.train_full)
    pd.testing.assert_frame_equal(split.test, split2.test)


def test_both_windows_contain_both_classes(split):
    """Sanity: frauds exist on each side of the cut, so evaluation is meaningful
    and the LR reference has positives to learn from."""
    assert split.train_full["Class"].sum() > 0
    assert split.test["Class"].sum() > 0

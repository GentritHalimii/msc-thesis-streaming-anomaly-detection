"""Inner-validation splitting for the hyperparameter search."""

import numpy as np
import pytest

from src.evaluation.model_selection import (
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

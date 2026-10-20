"""Drift measures: PSI, feature-level tests and the Page-Hinkley detector."""

import numpy as np
import pandas as pd
import pytest

from src.evaluation.drift import (
    calibrate_page_hinkley,
    feature_drift,
    page_hinkley,
    population_stability_index,
    psi_permutation_null,
    separability,
)


def test_psi_is_near_zero_for_the_same_distribution():
    rng = np.random.default_rng(0)
    a, b = rng.normal(size=20000), rng.normal(size=20000)
    assert population_stability_index(a, b) < 0.01


def test_psi_grows_with_the_size_of_the_shift():
    rng = np.random.default_rng(0)
    ref = rng.normal(size=20000)
    small = population_stability_index(ref, rng.normal(0.5, 1, 20000))
    large = population_stability_index(ref, rng.normal(2.0, 1, 20000))
    assert 0.1 < small < 0.25, "half a sigma should read as a moderate shift"
    assert large > 1.0
    assert large > small


def test_psi_handles_empty_and_degenerate_input():
    assert np.isnan(population_stability_index(np.array([]), np.arange(10.0)))
    assert population_stability_index(np.ones(100), np.ones(100)) == 0.0


def test_psi_null_absorbs_the_small_sample_bias():
    """Thirteen draws from the reference distribution give a large raw PSI
    purely by chance; the permutation null must be of the same size, so the
    excess stays near zero and the test does not reject."""
    rng = np.random.default_rng(3)
    cols = ["a", "b", "c"]
    ref = pd.DataFrame(rng.normal(size=(400, 3)), columns=cols)
    cur = pd.DataFrame(rng.normal(size=(13, 3)), columns=cols)
    out = psi_permutation_null(ref, cur, cols, n_permutations=60, seed=0)
    assert out["observed"] > 1.0, "the raw index is inflated at this sample size"
    assert out["null_mean"] > 1.0
    assert out["p_value"] > 0.05


def test_psi_null_still_detects_a_real_shift_in_a_small_sample():
    rng = np.random.default_rng(4)
    cols = ["a", "b"]
    ref = pd.DataFrame(rng.normal(size=(400, 2)), columns=cols)
    cur = pd.DataFrame(rng.normal(3.0, 1.0, size=(13, 2)), columns=cols)
    out = psi_permutation_null(ref, cur, cols, n_permutations=60, seed=0)
    assert out["excess"] > 1.0
    assert out["p_value"] < 0.05


def test_feature_drift_flags_the_shifted_column_only():
    rng = np.random.default_rng(1)
    ref = pd.DataFrame({"stable": rng.normal(size=5000), "moved": rng.normal(size=5000)})
    cur = pd.DataFrame({"stable": rng.normal(size=5000), "moved": rng.normal(3.0, 1.0, 5000)})
    out = feature_drift(ref, cur, ["stable", "moved"]).set_index("feature")
    assert out.loc["stable", "psi"] < 0.05
    assert out.loc["moved", "psi"] > 1.0
    assert out.loc["moved", "ks_p"] < 1e-10


def test_separability_detects_easy_versus_hard_positives():
    rng = np.random.default_rng(2)
    cols = [f"V{i}" for i in range(5)]
    ref = pd.DataFrame(rng.normal(size=(4000, 5)), columns=cols)
    ref["Class"] = 0

    def block(distance):
        normals = rng.normal(size=(1000, 5))
        frauds = rng.normal(distance, 1.0, size=(50, 5))
        df = pd.DataFrame(np.vstack([normals, frauds]), columns=cols)
        df["Class"] = [0] * 1000 + [1] * 50
        return df

    easy = separability(ref, block(6.0), cols)
    hard = separability(ref, block(1.0), cols)
    assert easy["ap_distance_detector"] > hard["ap_distance_detector"]
    assert easy["z_norm_median_fraud"] > hard["z_norm_median_fraud"]
    assert easy["cohens_d"] > hard["cohens_d"]


def test_page_hinkley_threshold_must_be_calibrated_not_guessed():
    """The statistic on pure noise grows with stream length, so a fixed
    threshold that is silent on one sample size fires on another. Calibration
    on change-free reference data is what makes it transferable."""
    rng = np.random.default_rng(3)
    short = calibrate_page_hinkley(rng.normal(size=2000), delta=0.01)
    long = calibrate_page_hinkley(rng.normal(size=40000), delta=0.01)
    assert long > short


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
def test_page_hinkley_finds_a_shift_and_stays_quiet_without_one(seed):
    rng = np.random.default_rng(seed)
    reference = rng.normal(0, 1, 6000)
    threshold = calibrate_page_hinkley(reference, delta=0.01, n_permutations=40)

    quiet = rng.normal(0, 1, 6000)
    assert len(page_hinkley(quiet, delta=0.01, threshold=threshold)) == 0

    shifted = np.concatenate([rng.normal(0, 1, 3000), rng.normal(3, 1, 3000)])
    changes = page_hinkley(shifted, delta=0.01, threshold=threshold)
    assert changes, "a three-sigma level shift must be detected"
    assert 3000 <= changes[0] < 3400, "detection should follow the change closely"

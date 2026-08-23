"""Geometric characterisation: dimension estimators and the hardness measure."""

import numpy as np
import pytest

from src.evaluation.geometry import (
    fraud_hardness,
    intrinsic_dimension_mle,
    intrinsic_dimension_twonn,
    neighbourhood_purity,
    one_nn_class_agreement,
)


def embedded_manifold(true_dim: int, ambient: int = 25, n: int = 5000, seed: int = 0):
    """A `true_dim`-dimensional Gaussian linearly embedded in `ambient` dims."""
    rng = np.random.default_rng(seed)
    latent = rng.normal(size=(n, true_dim))
    basis = rng.normal(size=(true_dim, ambient))
    return latent @ basis


@pytest.mark.parametrize("true_dim", [3, 5, 10])
def test_both_estimators_recover_a_known_intrinsic_dimension(true_dim):
    """Nominal dimension is 25 in every case; only the estimate of the real
    one should track the construction."""
    X = embedded_manifold(true_dim)
    mle = intrinsic_dimension_mle(X, k=15)
    twonn = intrinsic_dimension_twonn(X)
    assert abs(mle - true_dim) <= 0.25 * true_dim + 0.5
    assert abs(twonn - true_dim) <= 0.25 * true_dim + 0.5


def test_twonn_does_not_diverge_on_the_truncated_tail():
    """The empirical CDF must be built before truncation. Building it after
    puts the last retained point at F = 1, where -log(1 - F) diverges and the
    through-origin fit is dragged upwards."""
    X = embedded_manifold(5)
    generous = intrinsic_dimension_twonn(X, discard=0.02)
    strict = intrinsic_dimension_twonn(X, discard=0.25)
    assert abs(generous - strict) < 1.0, "estimate must not hinge on the discard fraction"


def test_neighbourhood_purity_grows_with_distance_from_the_reference():
    rng = np.random.default_rng(1)
    reference = rng.normal(size=(4000, 8))
    near = neighbourhood_purity(reference, rng.normal(size=(200, 8)), k=10)
    far = neighbourhood_purity(reference, rng.normal(8.0, 1.0, size=(200, 8)), k=10)
    assert np.median(far) > 5 * np.median(near)


def test_hardness_separates_an_easy_problem_from_a_hard_one():
    """The measure has to reflect achievable precision, not raw distance: a
    heavy-tailed normal class fills the far region and makes distant positives
    expensive to reach anyway."""
    rng = np.random.default_rng(2)
    easy_normal = rng.normal(size=(20000, 8))
    hard_normal = rng.standard_t(df=3, size=(20000, 8))
    frauds = rng.normal(5.0, 1.0, size=(50, 8))

    easy = fraud_hardness(easy_normal, frauds, k=10, max_reference=8000, max_normal_query=10000)
    hard = fraud_hardness(hard_normal, frauds, k=10, max_reference=8000, max_normal_query=10000)
    assert easy["ap_distance_only"] > hard["ap_distance_only"]
    assert easy["median_fraud_rank"] < hard["median_fraud_rank"]
    assert easy["frauds_within_top_100"] >= hard["frauds_within_top_100"]


def test_one_nn_agreement_is_lower_for_the_embedded_class():
    rng = np.random.default_rng(3)
    normals = rng.normal(size=(6000, 6))
    frauds = np.vstack([rng.normal(6.0, 1.0, size=(30, 6)), rng.normal(size=(30, 6))])
    X = np.vstack([normals, frauds])
    y = np.r_[np.zeros(len(normals), int), np.ones(len(frauds), int)]
    out = one_nn_class_agreement(X, y)
    assert out["agreement_normal"] > out["agreement_fraud"]
    assert out["n_frauds"] == 60

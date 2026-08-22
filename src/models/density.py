"""Density- and covariance-based detectors.

Both model the *normal* class explicitly and score how unlikely a point is
under that model, which is the classical statistical route to outlier
detection and a useful contrast to isolation- and boundary-based methods.
"""

from pathlib import Path

import joblib
import numpy as np
from sklearn.covariance import MinCovDet
from sklearn.mixture import GaussianMixture

from src.models.base import AnomalyModel, subsample_for_fit


class GMMDensity(AnomalyModel):
    """Negative log-likelihood under a Gaussian mixture fitted on normals."""

    name = "gmm"

    def __init__(self, n_components: int = 8, covariance_type: str = "full", seed: int = 42):
        self._model = GaussianMixture(
            n_components=n_components,
            covariance_type=covariance_type,
            random_state=seed,
            reg_covar=1e-4,
            max_iter=200,
        )

    def fit(self, X: np.ndarray) -> "GMMDensity":
        self._model.fit(X)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        return -self._model.score_samples(X)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "GMMDensity":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        return obj


class RobustMahalanobis(AnomalyModel):
    """Squared robust Mahalanobis distance (Minimum Covariance Determinant).

    MCD is O(n * p^2) per subset iteration and does not need the full window;
    it is fitted on a seeded subsample of the training normals.
    """

    name = "mahalanobis"

    def __init__(self, support_fraction: float = 0.9, fit_subsample: int = 30000, seed: int = 42):
        self._support_fraction = support_fraction
        self._subsample = fit_subsample
        self._seed = seed
        self._model: MinCovDet | None = None

    def fit(self, X: np.ndarray) -> "RobustMahalanobis":
        Xs = subsample_for_fit(X, self._subsample, self._seed)
        self._model = MinCovDet(
            support_fraction=self._support_fraction, random_state=self._seed
        ).fit(Xs)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        return self._model.mahalanobis(X)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "RobustMahalanobis":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        return obj

"""Proximity-based detectors: local density contrast and k-th neighbour distance.

Both are lazy learners whose *scoring* cost grows with the size of the stored
reference set, so the reference set is a seeded subsample of the training
normals. That subsample size is itself an operational trade-off and is
reported alongside the detection metrics.
"""

from pathlib import Path

import joblib
import numpy as np
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors

from src.models.base import AnomalyModel, subsample_for_fit


class LOFNovelty(AnomalyModel):
    """Local Outlier Factor in novelty mode (fit on normals, score new points)."""

    name = "lof"

    def __init__(self, n_neighbors: int = 20, fit_subsample: int = 20000, seed: int = 42):
        self._n_neighbors = n_neighbors
        self._subsample = fit_subsample
        self._seed = seed
        self._model: LocalOutlierFactor | None = None

    def fit(self, X: np.ndarray) -> "LOFNovelty":
        Xs = subsample_for_fit(X, self._subsample, self._seed)
        self._model = LocalOutlierFactor(
            n_neighbors=self._n_neighbors, novelty=True, n_jobs=-1
        ).fit(Xs)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        return -self._model.score_samples(X)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "LOFNovelty":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        return obj


class KNNDistance(AnomalyModel):
    """Mean distance to the k nearest normal training points."""

    name = "knn"

    def __init__(self, n_neighbors: int = 10, fit_subsample: int = 20000, seed: int = 42):
        self._n_neighbors = n_neighbors
        self._subsample = fit_subsample
        self._seed = seed
        self._model: NearestNeighbors | None = None

    def fit(self, X: np.ndarray) -> "KNNDistance":
        Xs = subsample_for_fit(X, self._subsample, self._seed)
        self._model = NearestNeighbors(n_neighbors=self._n_neighbors, n_jobs=-1).fit(Xs)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        distances, _ = self._model.kneighbors(X)
        return distances.mean(axis=1)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "KNNDistance":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        return obj

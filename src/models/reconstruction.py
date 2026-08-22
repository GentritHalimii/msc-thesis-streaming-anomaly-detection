"""Reconstruction-based detectors built on linear subspaces.

The ULB dataset's V1..V28 are themselves principal components of the original
(undisclosed) features, so a *linear* reconstruction detector is the natural
lower bound for the whole reconstruction family: if a non-linear autoencoder
cannot beat the linear projection it has learned nothing the data did not
already expose.
"""

from pathlib import Path

import joblib
import numpy as np
from sklearn.decomposition import PCA

from src.models.base import AnomalyModel


class PCAReconstruction(AnomalyModel):
    """Anomaly score = squared reconstruction error of a rank-k PCA subspace
    fitted on normal training transactions."""

    name = "pca_recon"

    def __init__(self, n_components: int = 12, seed: int = 42):
        self._n_components = n_components
        self._seed = seed
        self._pca: PCA | None = None

    def fit(self, X: np.ndarray) -> "PCAReconstruction":
        k = min(self._n_components, X.shape[1])
        self._pca = PCA(n_components=k, random_state=self._seed).fit(X)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        recon = self._pca.inverse_transform(self._pca.transform(X))
        return np.mean((X - recon) ** 2, axis=1)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._pca, path)

    @classmethod
    def load(cls, path: Path | str) -> "PCAReconstruction":
        obj = cls.__new__(cls)
        obj._pca = joblib.load(path)
        obj._n_components = obj._pca.n_components_
        obj._seed = 42
        return obj

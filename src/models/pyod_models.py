"""Thin adapters around reference implementations in PyOD.

ECOD, COPOD, HBOS and LODA are included because they are parameter-free (or
nearly so), extremely cheap at inference time, and have become the standard
"is your complicated model actually worth it?" controls in recent anomaly
detection benchmarks. Re-implementing them here would add risk without adding
insight, so the published implementations are used and cited.
"""

from pathlib import Path

import joblib
import numpy as np
from pyod.models.copod import COPOD
from pyod.models.ecod import ECOD
from pyod.models.hbos import HBOS
from pyod.models.loda import LODA

from src.models.base import AnomalyModel


class _PyODAdapter(AnomalyModel):
    """PyOD's decision_function is already 'higher = more anomalous'."""

    def __init__(self, detector):
        self._model = detector

    def fit(self, X: np.ndarray) -> "_PyODAdapter":
        self._model.fit(X)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        return np.asarray(self._model.decision_function(X), dtype=float)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "_PyODAdapter":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        return obj


class ECODModel(_PyODAdapter):
    name = "ecod"

    def __init__(self, n_jobs: int = 1):
        super().__init__(ECOD(n_jobs=n_jobs))


class COPODModel(_PyODAdapter):
    name = "copod"

    def __init__(self, n_jobs: int = 1):
        super().__init__(COPOD(n_jobs=n_jobs))


class HBOSModel(_PyODAdapter):
    name = "hbos"

    def __init__(self, n_bins: int = 50, alpha: float = 0.1):
        super().__init__(HBOS(n_bins=n_bins, alpha=alpha))


class LODAModel(_PyODAdapter):
    name = "loda"

    def __init__(self, n_bins: int = 20, n_random_cuts: int = 100):
        super().__init__(LODA(n_bins=n_bins, n_random_cuts=n_random_cuts))

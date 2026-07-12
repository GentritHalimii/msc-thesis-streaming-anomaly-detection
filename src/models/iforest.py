from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from src.models.base import AnomalyModel


class IForestModel(AnomalyModel):
    name = "iforest"

    def __init__(self, n_estimators: int = 200, max_samples: int = 256, seed: int = 42):
        self._model = IsolationForest(
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=seed,
            n_jobs=-1,
        )

    def fit(self, X: np.ndarray) -> "IForestModel":
        self._model.fit(X)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        # score_samples: higher = more normal; negate for higher = more anomalous.
        return -self._model.score_samples(X)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "IForestModel":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        return obj

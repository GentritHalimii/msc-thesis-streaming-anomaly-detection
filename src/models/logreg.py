from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from src.models.base import AnomalyModel


class LogRegReference(AnomalyModel):
    """Supervised REFERENCE model — not an unsupervised competitor.

    Trained on the full training window *including labels* (the frauds that
    naturally fall in that window). It represents the upper bound achievable
    when labels are available, and is framed as such everywhere it is
    reported. Its fit() signature therefore takes y, unlike the others.
    """

    name = "logreg"

    def __init__(self, max_iter: int = 2000, class_weight: str = "balanced", seed: int = 42):
        self._model = LogisticRegression(
            max_iter=max_iter, class_weight=class_weight, random_state=seed
        )

    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> "LogRegReference":
        if y is None:
            raise ValueError("LogRegReference is supervised and requires labels")
        self._model.fit(X, y)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict_proba(X)[:, 1]

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "LogRegReference":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        return obj

"""Common model interface.

Every model exposes fit / score / save / load with the same convention:
score(X) returns one float per row, HIGHER = MORE ANOMALOUS. The evaluation
harness, the ensemble and the streaming consumer rely on this and stay dumb.
"""

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class AnomalyModel(ABC):
    name: str

    @abstractmethod
    def fit(self, X: np.ndarray) -> "AnomalyModel":
        """Fit on scaled training features (normals only for unsupervised models)."""

    @abstractmethod
    def score(self, X: np.ndarray) -> np.ndarray:
        """Anomaly score per row; higher = more anomalous."""

    @abstractmethod
    def save(self, path: Path | str) -> None: ...

    @classmethod
    @abstractmethod
    def load(cls, path: Path | str) -> "AnomalyModel": ...

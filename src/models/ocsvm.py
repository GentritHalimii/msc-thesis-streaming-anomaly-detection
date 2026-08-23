from pathlib import Path

import joblib
import numpy as np
from sklearn.svm import OneClassSVM

from src.models.base import AnomalyModel


class OCSVMModel(AnomalyModel):
    """Exact RBF One-Class SVM.

    Kernel OCSVM is O(n^2)+ in training-set size, which is infeasible on the
    ~199k-row training window, so fit() trains on a seeded random subsample
    (config: models.ocsvm.train_subsample, default 20k). This is a documented
    methodological choice — see README.
    """

    name = "ocsvm"

    def __init__(
        self,
        train_subsample: int = 20000,
        kernel: str = "rbf",
        nu: float = 0.05,
        gamma: str | float = "scale",
        seed: int = 42,
    ):
        self._model = OneClassSVM(kernel=kernel, nu=nu, gamma=gamma)
        self._subsample = train_subsample
        self._seed = seed
        self._n_train = 0

    def fit(self, X: np.ndarray) -> "OCSVMModel":
        if len(X) > self._subsample:
            rng = np.random.default_rng(self._seed)
            idx = rng.choice(len(X), size=self._subsample, replace=False)
            X = X[np.sort(idx)]
        self._n_train = len(X)
        self._model.fit(X)
        return self

    @property
    def n_support_vectors(self) -> int:
        """Support vectors retained after fitting.

        This is the quantity that sets inference cost: every scored
        transaction is compared against all of them, so it links the nu
        hyperparameter directly to latency.
        """
        return int(self._model.support_vectors_.shape[0])

    @property
    def support_fraction(self) -> float:
        return self.n_support_vectors / max(self._n_train, 1)

    def score(self, X: np.ndarray) -> np.ndarray:
        # decision_function: positive inside the learned region; negate so
        # higher = more anomalous.
        return -self._model.decision_function(X)

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)

    @classmethod
    def load(cls, path: Path | str) -> "OCSVMModel":
        obj = cls.__new__(cls)
        obj._model = joblib.load(path)
        obj._n_train = 0
        return obj

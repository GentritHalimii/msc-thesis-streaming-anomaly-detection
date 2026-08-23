"""Feature scaling, fit on the training window only.

`Time` is not a feature: it orders the stream and defines the split, so using
it as a model input would entangle the split variable with the model.

The scaler is deliberately fitted on the whole training window, frauds
included, rather than on the known normals. At deployment the labels for the
current window do not exist, so a scaler fitted on clean data would be an
advantage the real system never has. That choice has a consequence worth
testing rather than assuming: the fitted statistics absorb the outliers they
are meant to expose, which is exactly why robust and rank-based alternatives
are compared in the preprocessing study.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import (
    MinMaxScaler,
    PowerTransformer,
    QuantileTransformer,
    RobustScaler,
    StandardScaler,
)

from src.data.load import FEATURE_COLUMNS

# Named preprocessing options compared in the scaling study. "none" is kept
# because the V-features are already centred principal components, so leaving
# them alone is a legitimate baseline rather than an oversight.
SCALERS = {
    "standard": lambda seed: StandardScaler(),
    "robust": lambda seed: RobustScaler(quantile_range=(25.0, 75.0)),
    "quantile_normal": lambda seed: QuantileTransformer(
        output_distribution="normal", n_quantiles=1000, subsample=100000, random_state=seed
    ),
    "quantile_uniform": lambda seed: QuantileTransformer(
        output_distribution="uniform", n_quantiles=1000, subsample=100000, random_state=seed
    ),
    "power_yeo_johnson": lambda seed: PowerTransformer(method="yeo-johnson", standardize=True),
    "minmax": lambda seed: MinMaxScaler(),
    "none": lambda seed: _Identity(),
}


class _Identity:
    """No-op transformer with the scikit-learn interface."""

    def fit(self, X):
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        return np.asarray(X, dtype=float)

    def fit_transform(self, X):
        return self.fit(X).transform(X)


def build_scaler(kind: str = "standard", seed: int = 42):
    if kind not in SCALERS:
        raise ValueError(f"unknown scaler {kind!r}; expected one of {sorted(SCALERS)}")
    return SCALERS[kind](seed)


def fit_scaler(train: pd.DataFrame, kind: str = "standard", seed: int = 42):
    """Fit on training-window rows only. Never call with test data."""
    return build_scaler(kind, seed).fit(train[FEATURE_COLUMNS].to_numpy())


def transform(scaler, df: pd.DataFrame) -> np.ndarray:
    return scaler.transform(df[FEATURE_COLUMNS].to_numpy())


def save_scaler(scaler, path: Path | str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, path)


def load_scaler(path: Path | str):
    return joblib.load(path)

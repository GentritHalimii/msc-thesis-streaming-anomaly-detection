"""Feature scaling, fit on the training window only.

`Time` is not a feature: it orders the stream and defines the split, so using
it as a model input would entangle the split variable with the model.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.data.load import FEATURE_COLUMNS


def fit_scaler(train: pd.DataFrame) -> StandardScaler:
    """Fit on training-window rows only. Never call with test data."""
    return StandardScaler().fit(train[FEATURE_COLUMNS].to_numpy())


def transform(scaler: StandardScaler, df: pd.DataFrame) -> np.ndarray:
    return scaler.transform(df[FEATURE_COLUMNS].to_numpy())


def save_scaler(scaler: StandardScaler, path: Path | str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, path)


def load_scaler(path: Path | str) -> StandardScaler:
    return joblib.load(path)

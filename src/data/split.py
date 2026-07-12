"""Chronological, leakage-free train/test split.

The dataframe must already be sorted by Time (load_transactions guarantees
this). The first `train_fraction` of rows *by time order* form the training
window; the remainder is the test window. Nothing is ever shuffled.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ChronologicalSplit:
    train_full: pd.DataFrame  # training window, both classes (LR reference only)
    train_normal: pd.DataFrame  # training window, Class == 0 (unsupervised fit)
    test: pd.DataFrame  # test window, untouched, both classes

    @property
    def summary(self) -> dict:
        return {
            "train_rows": len(self.train_full),
            "train_frauds": int(self.train_full["Class"].sum()),
            "train_fraud_rate": float(self.train_full["Class"].mean()),
            "test_rows": len(self.test),
            "test_frauds": int(self.test["Class"].sum()),
            "test_fraud_rate": float(self.test["Class"].mean()),
            "train_time_max": float(self.train_full["Time"].max()),
            "test_time_min": float(self.test["Time"].min()),
        }


def chronological_split(df: pd.DataFrame, train_fraction: float) -> ChronologicalSplit:
    if not df["Time"].is_monotonic_increasing:
        raise ValueError("dataframe must be sorted by Time before splitting")
    cut = int(len(df) * train_fraction)
    train_full = df.iloc[:cut]
    test = df.iloc[cut:]
    train_normal = train_full[train_full["Class"] == 0]
    return ChronologicalSplit(train_full=train_full, train_normal=train_normal, test=test)

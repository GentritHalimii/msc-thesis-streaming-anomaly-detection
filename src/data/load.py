"""Load the ULB creditcard dataset and order it chronologically."""

from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [f"V{i}" for i in range(1, 29)] + ["Amount"]
EXPECTED_COLUMNS = ["Time", *FEATURE_COLUMNS, "Class"]


def load_transactions(csv_path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"dataset is missing expected columns: {sorted(missing)}")
    if df[EXPECTED_COLUMNS].isna().any().any():
        raise ValueError("dataset contains NaN values")
    # Stable sort: rows sharing a Time value keep their original file order,
    # so the "chronological" order is deterministic across runs.
    df = df.sort_values("Time", kind="stable").reset_index(drop=True)
    df.index.name = "tx_id"
    return df

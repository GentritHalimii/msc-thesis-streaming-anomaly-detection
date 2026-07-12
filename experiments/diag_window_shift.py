"""Diagnostic: what measurably differs between the train and test windows?

Motivated by the train/test AP gap of the unsupervised models. Produces
results/window_shift.csv (+ per-model sign-convention checks) so the
explanation in the thesis is backed by numbers, not a drift hand-wave.

Measures, per window and class:
- fraud counts and rates, time span, hour-of-day coverage
- ||z||: L2 norm of train-scaled features — how far points sit from the
  training-window normal centroid, in train-window units. A model-free
  separability proxy: if test frauds have much smaller ||z|| than train
  frauds, they are intrinsically less anomalous-looking to ANY
  centroid/density method, regardless of drift in the normals.
- AP of the model-free detector score=||z|| within each window
- fraud episode structure (gap > 300 s starts a new episode)
- per-model: median score of frauds vs normals on the test window, with an
  explicit assertion that fraud median > normal median (sign convention,
  higher = more anomalous, verified on real data).
"""

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import load_scaler, transform
from src.data.split import chronological_split
from src.evaluation.report import save_table
from src.models.build import ALL_MODELS, artifacts_dir, load_model


def hour_of_day(t: pd.Series) -> pd.Series:
    return (t % 86400) / 3600.0


def episodes(times: np.ndarray, gap_s: float = 300.0) -> int:
    if len(times) == 0:
        return 0
    return int(1 + (np.diff(np.sort(times)) > gap_s).sum())


def main(cfg=None):
    cfg = cfg or load_config()
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split = chronological_split(df, cfg.split.train_fraction)
    scaler = load_scaler(artifacts_dir(cfg) / "scaler.joblib")

    rows = []
    z_cache = {}
    for window_name, frame in [("train", split.train_full), ("test", split.test)]:
        z = transform(scaler, frame)
        z_cache[window_name] = z
        norms = np.linalg.norm(z, axis=1)
        y = frame["Class"].to_numpy()
        hours = hour_of_day(frame["Time"])
        fraud_times = frame.loc[frame["Class"] == 1, "Time"].to_numpy()
        rows.append(
            {
                "window": window_name,
                "rows": len(frame),
                "frauds": int(y.sum()),
                "fraud_rate": float(y.mean()),
                "hours_covered": f"{hours.min():.1f}-{hours.max():.1f}",
                "z_norm_median_normal": float(np.median(norms[y == 0])),
                "z_norm_median_fraud": float(np.median(norms[y == 1])),
                "z_norm_p90_fraud": float(np.quantile(norms[y == 1], 0.9)),
                "ap_znorm_detector": float(average_precision_score(y, norms)),
                "fraud_episodes_gap300s": episodes(fraud_times),
                "amount_median_fraud": float(frame.loc[y == 1, "Amount"].median()),
            }
        )
    table = pd.DataFrame(rows)
    save_table(table, REPO_ROOT / cfg.results_dir, "window_shift")
    print(table.to_string(index=False))

    print("\nsign convention on real test data (higher = more anomalous):")
    y_test = split.test["Class"].to_numpy()
    for name in ALL_MODELS:
        scores = load_model(name, cfg).score(z_cache["test"])
        med_fraud = float(np.median(scores[y_test == 1]))
        med_normal = float(np.median(scores[y_test == 0]))
        assert med_fraud > med_normal, (
            f"{name}: fraud median {med_fraud} <= normal median {med_normal} — "
            "sign convention violated"
        )
        print(f"  {name}: median fraud score {med_fraud:.4f} > median normal {med_normal:.4f} OK")


if __name__ == "__main__":
    main()

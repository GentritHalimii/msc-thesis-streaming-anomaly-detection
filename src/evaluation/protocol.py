"""Rolling-origin (prequential) evaluation protocol.

A single 70/30 cut answers "how well would this model have worked if we had
deployed it at exactly one moment in time". That is one draw from a
distribution, and with 492 positives in the whole dataset it is a noisy one.
The protocol here re-runs the entire pipeline at several successive cut
points with an expanding training window, which is the standard way to
evaluate a model that will be deployed on a stream: train on the past, test
on the block that immediately follows, never the reverse.

Every fold repeats the full leakage discipline from scratch — its own scaler,
its own models, its own thresholds — so nothing from a later block can leak
backwards into an earlier one.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.scale import fit_scaler, transform
from src.evaluation.resources import measure
from src.models.build import ALL_MODELS, build_model

# Resolution of the stored training-score quantile grid. 10001 points fixes
# any percentile threshold to 0.01% precision without keeping millions of
# raw training scores on disk.
QUANTILE_GRID = np.linspace(0.0, 1.0, 10001)


@dataclass(frozen=True)
class Fold:
    index: int
    train_end: int  # exclusive row index
    test_end: int  # exclusive row index

    @property
    def test_start(self) -> int:
        return self.train_end


def rolling_origin_folds(n_rows: int, n_folds: int, initial_train_fraction: float) -> list[Fold]:
    """Expanding-window folds over a chronologically ordered dataset.

    Fold i trains on rows [0, cut_i) and tests on [cut_i, cut_{i+1}), where the
    cut points divide the tail after `initial_train_fraction` into `n_folds`
    equal blocks.
    """
    if not 0.0 < initial_train_fraction < 1.0:
        raise ValueError("initial_train_fraction must be in (0, 1)")
    start = int(n_rows * initial_train_fraction)
    edges = np.linspace(start, n_rows, n_folds + 1).astype(int)
    return [
        Fold(index=i, train_end=int(edges[i]), test_end=int(edges[i + 1])) for i in range(n_folds)
    ]


def fold_summary(df: pd.DataFrame, folds: list[Fold]) -> pd.DataFrame:
    """Class balance and time span of each fold — reported before any model
    runs, because a fold with three positives cannot support a conclusion."""
    rows = []
    for f in folds:
        train = df.iloc[: f.train_end]
        test = df.iloc[f.test_start : f.test_end]
        rows.append(
            {
                "fold": f.index,
                "train_rows": len(train),
                "train_frauds": int(train["Class"].sum()),
                "train_fraud_rate": float(train["Class"].mean()),
                "test_rows": len(test),
                "test_frauds": int(test["Class"].sum()),
                "test_fraud_rate": float(test["Class"].mean()),
                "train_time_end_h": float(train["Time"].max() / 3600.0),
                "test_time_start_h": float(test["Time"].min() / 3600.0),
                "test_time_end_h": float(test["Time"].max() / 3600.0),
            }
        )
    return pd.DataFrame(rows)


def run_fold(
    cfg,
    fold: Fold,
    df: pd.DataFrame,
    model_names: list[str],
    overrides: dict[str, dict] | None = None,
    unfiltered: bool = False,
) -> dict:
    """Fit and score every model on one fold. Returns raw material only —
    scores, costs, labels — so that thresholds, metrics, ensembles and cost
    curves can all be recomputed later without refitting anything.

    By default the detectors learn from the window's legitimate transactions,
    which needs the historical labels to remove the frauds. `unfiltered=True`
    fits them on the whole window instead, frauds included, which is the
    regime of a system that has no labels at all.
    """
    overrides = overrides or {}
    train = df.iloc[: fold.train_end]
    test = df.iloc[fold.test_start : fold.test_end]
    train_normal = train if unfiltered else train[train["Class"] == 0]

    scaler = fit_scaler(train)
    X_train_full = transform(scaler, train)
    X_train_normal = transform(scaler, train_normal)
    X_test = transform(scaler, test)
    y_train = train["Class"].to_numpy()

    payload: dict[str, np.ndarray | dict] = {
        "y_test": test["Class"].to_numpy().astype(np.int8),
        "amount_test": test["Amount"].to_numpy().astype(np.float32),
        "time_test": test["Time"].to_numpy().astype(np.float64),
        "tx_id_test": test.index.to_numpy().astype(np.int64),
    }
    costs: dict[str, dict] = {}

    for name in model_names:
        model = build_model(name, cfg, overrides.get(name))
        with measure() as usage:
            if name == "logreg":
                model.fit(X_train_full, y_train)
            else:
                model.fit(X_train_normal)
        fit_s, fit_mb = usage.elapsed_s, usage.delta_rss_mb

        t0 = time.perf_counter()
        s_test = np.asarray(model.score(X_test), dtype=np.float64)
        score_s = time.perf_counter() - t0
        s_train = np.asarray(model.score(X_train_full), dtype=np.float64)

        # float64, deliberately. Storing scores as float32 collapsed roughly
        # 500 to 1000 of the ~21k test points per fold into artificial ties,
        # which moves Average Precision by up to 0.02 units because AP is
        # dominated by the head of the ranking. The storage saved is
        # irrelevant next to a measurement artefact in the primary metric.
        payload[f"test__{name}"] = s_test
        payload[f"trainq__{name}"] = np.quantile(s_train, QUANTILE_GRID).astype(np.float64)
        costs[name] = {
            "fit_time_s": round(fit_s, 3),
            "fit_rss_mb": round(fit_mb, 1),
            "score_time_s": round(score_s, 4),
            "score_us_per_tx": round(score_s / len(X_test) * 1e6, 3),
            "train_score_mean": float(s_train.mean()),
            "train_score_std": float(s_train.std()),
        }
    payload["costs_json"] = json.dumps(costs)
    return payload


def fold_path(results_dir: Path | str, fold_index: int) -> Path:
    return Path(results_dir) / "folds" / f"fold{fold_index}.npz"


def save_fold(results_dir: Path | str, fold_index: int, payload: dict) -> Path:
    out = fold_path(results_dir, fold_index)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, **payload)
    return out


class FoldScores:
    """Read-only view over one saved fold."""

    def __init__(self, path: Path | str):
        self._z = np.load(path, allow_pickle=False)
        self.costs = json.loads(str(self._z["costs_json"]))

    @property
    def y(self) -> np.ndarray:
        return self._z["y_test"].astype(int)

    @property
    def amount(self) -> np.ndarray:
        return self._z["amount_test"]

    @property
    def time(self) -> np.ndarray:
        return self._z["time_test"]

    @property
    def models(self) -> list[str]:
        return [k.removeprefix("test__") for k in self._z.files if k.startswith("test__")]

    def test_scores(self, name: str) -> np.ndarray:
        return self._z[f"test__{name}"].astype(np.float64)

    def train_quantiles(self, name: str) -> np.ndarray:
        return self._z[f"trainq__{name}"]

    def train_threshold(self, name: str, contamination: float) -> float:
        """Percentile threshold read off the stored training-score grid."""
        return float(np.interp(1.0 - contamination, QUANTILE_GRID, self.train_quantiles(name)))

    def train_rank_of(self, name: str, scores: np.ndarray) -> np.ndarray:
        """Map scores onto their quantile position in the TRAINING score
        distribution — the leakage-free way to put different detectors on a
        common [0, 1] scale before combining them."""
        return np.interp(scores, self.train_quantiles(name), QUANTILE_GRID)


def load_folds(results_dir: Path | str, n_folds: int) -> list[FoldScores]:
    return [FoldScores(fold_path(results_dir, i)) for i in range(n_folds)]


def default_model_names() -> list[str]:
    return list(ALL_MODELS)

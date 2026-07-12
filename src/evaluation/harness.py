"""Shared offline-evaluation plumbing: load artifacts, score the test window.

This is the SAME scaler + model.score() path the streaming consumer uses;
tests/test_parity.py asserts the two produce identical scores.
"""

import json
import time
from dataclasses import dataclass, field

import numpy as np

from src.config import REPO_ROOT
from src.data.load import load_transactions
from src.data.scale import load_scaler, transform
from src.data.split import chronological_split
from src.models.build import ALL_MODELS, artifacts_dir, load_model


@dataclass
class ScoredTestSet:
    y_test: np.ndarray
    test_scores: dict[str, np.ndarray]
    train_scores: dict[str, np.ndarray]
    inference_s: dict[str, float]  # batch scoring wall time over the full test window
    n_test: int
    split_summary: dict = field(default_factory=dict)

    def train_fraud_rate(self) -> float:
        return self.split_summary["train_fraud_rate"]


def contamination_value(cfg, scored: ScoredTestSet) -> float:
    """Config value, or the training-window fraud rate when null (uses train
    labels only — same availability assumption as the LR reference)."""
    if cfg.contamination is not None:
        return float(cfg.contamination)
    return scored.train_fraud_rate()


def score_test_window(cfg, model_names: list[str] | None = None) -> ScoredTestSet:
    model_names = model_names or ALL_MODELS
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split = chronological_split(df, cfg.split.train_fraction)
    scaler = load_scaler(artifacts_dir(cfg) / "scaler.joblib")
    X_test = transform(scaler, split.test)

    train_scores = dict(np.load(artifacts_dir(cfg) / "train_scores.npz"))
    split_summary = json.loads((artifacts_dir(cfg) / "split_summary.json").read_text())

    test_scores, inference_s = {}, {}
    for name in model_names:
        model = load_model(name, cfg)
        t0 = time.perf_counter()
        test_scores[name] = model.score(X_test)
        inference_s[name] = time.perf_counter() - t0

    return ScoredTestSet(
        y_test=split.test["Class"].to_numpy(),
        test_scores=test_scores,
        train_scores=train_scores,
        inference_s=inference_s,
        n_test=len(split.test),
        split_summary=split_summary,
    )

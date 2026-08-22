"""Fit and score every detector at every rolling-origin cut point.

This is the expensive step of the whole study: it produces the raw score
matrices that all downstream analysis reads. Nothing here computes a metric —
keeping fitting and analysis apart means thresholds, ensembles, cost curves
and statistical tests can all be revisited without refitting a single model.
"""

import argparse
import json

import numpy as np

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import (
    fold_summary,
    rolling_origin_folds,
    run_fold,
    save_fold,
)
from src.evaluation.report import save_table
from src.models.build import ALL_MODELS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument(
        "--folds", nargs="*", type=int, default=None, help="fold indices to run (default: all)"
    )
    parser.add_argument(
        "--tuned", action="store_true", help="apply hyperparameters from results/tuned_params.json"
    )
    args = parser.parse_args()

    cfg = load_config()
    np.random.seed(cfg.seed)
    model_names = args.models or ALL_MODELS
    results_dir = REPO_ROOT / cfg.results_dir

    overrides = {}
    tag = "protocol"
    if args.tuned:
        tuned_file = results_dir / "tuned_params.json"
        overrides = json.loads(tuned_file.read_text())
        tag = "protocol_tuned"
        print(f"applying tuned hyperparameters for {sorted(overrides)}")

    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)
    summary = fold_summary(df, folds)
    save_table(summary, results_dir, "fold_summary", float_fmt="%.5f")
    print(summary.to_string(index=False))

    selected = folds if args.folds is None else [folds[i] for i in args.folds]
    for fold in selected:
        print(
            f"\n=== fold {fold.index}: train[0:{fold.train_end}) "
            f"test[{fold.test_start}:{fold.test_end}) ===",
            flush=True,
        )
        payload = run_fold(cfg, fold, df, model_names, overrides)
        out = save_fold(
            results_dir if not args.tuned else results_dir / "tuned", fold.index, payload
        )
        costs = json.loads(payload["costs_json"])
        for name, c in costs.items():
            print(
                f"  {name:<13} fit {c['fit_time_s']:>7.2f}s  "
                f"score {c['score_us_per_tx']:>8.2f} us/tx  "
                f"rss {c['fit_rss_mb']:>6.1f} MB",
                flush=True,
            )
        print(f"  -> {out}")

    write_manifest(results_dir, tag, cfg.raw)


if __name__ == "__main__":
    main()

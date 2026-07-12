"""Fit all models on the training window and save every artifact evaluation
and streaming need: models, scaler, training-score distributions, fit costs,
split summary.

Unsupervised models fit on training-window NORMALS only; the LR reference
fits on the full training window WITH labels (supervised upper bound).
Training scores for thresholding are computed on the full training window:
the percentile threshold then means "flag the top `contamination` fraction
of everything seen during training".
"""

import json

import numpy as np

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, save_scaler, transform
from src.data.split import chronological_split
from src.evaluation.manifest import write_manifest
from src.evaluation.resources import measure
from src.models.build import ALL_MODELS, artifacts_dir, build_model, model_path


def main(cfg=None):
    cfg = cfg or load_config()
    np.random.seed(cfg.seed)

    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split = chronological_split(df, cfg.split.train_fraction)
    print(f"split: {json.dumps(split.summary, indent=2)}")

    scaler = fit_scaler(split.train_full)
    X_train_full = transform(scaler, split.train_full)
    X_train_normal = transform(scaler, split.train_normal)
    y_train = split.train_full["Class"].to_numpy()

    out = artifacts_dir(cfg)
    out.mkdir(parents=True, exist_ok=True)
    save_scaler(scaler, out / "scaler.joblib")
    (out / "split_summary.json").write_text(json.dumps(split.summary, indent=2))

    costs = {}
    train_scores = {}
    for name in ALL_MODELS:
        model = build_model(name, cfg)
        with measure() as usage:
            if name == "logreg":
                model.fit(X_train_full, y_train)
            else:
                model.fit(X_train_normal)
        model.save(model_path(cfg, name))
        train_scores[name] = model.score(X_train_full)
        costs[name] = {
            "fit_time_s": round(usage.elapsed_s, 3),
            "fit_peak_rss_mb": round(usage.peak_rss_mb, 1),
            "fit_delta_rss_mb": round(usage.delta_rss_mb, 1),
        }
        print(
            f"{name}: fit {usage.elapsed_s:.1f}s, "
            f"fit footprint {usage.delta_rss_mb:.0f} MB (process peak {usage.peak_rss_mb:.0f})"
        )

    np.savez_compressed(out / "train_scores.npz", **train_scores)
    (out / "fit_costs.json").write_text(json.dumps(costs, indent=2))
    write_manifest(REPO_ROOT / cfg.results_dir, "train_models", cfg.raw)
    print(f"artifacts written to {out}")


if __name__ == "__main__":
    main()

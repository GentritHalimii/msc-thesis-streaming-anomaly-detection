"""Hyperparameter search that never sees the test window.

The training window is split again in time: candidates are fitted on its
first 75% and ranked by Average Precision on the last 25%. Only labels that
predate the deployment moment are used, which is the same assumption the
supervised reference already enjoys — a bank has labels for last month, not
for the transaction currently arriving.

Two practical compromises, both stated rather than hidden. Candidates are
fitted on a seeded subsample so that a 25-trial search over eleven detectors
finishes in minutes rather than a day; the winner is refitted on the full
window afterwards. And the search is run once, at the 70/30 cut, rather than
inside every rolling-origin fold: re-tuning per fold would be more rigorous
but would multiply the cost eightfold for a comparison whose ranking, as the
results show, is already stable across folds.
"""

import argparse
import json
import warnings

import numpy as np
import optuna
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.data.split import chronological_split
from src.evaluation.manifest import write_manifest
from src.evaluation.model_selection import inner_temporal_split, inner_validation_ap
from src.evaluation.report import MODEL_LABELS, save_table
from src.models.base import subsample_for_fit
from src.models.build import build_model

optuna.logging.set_verbosity(optuna.logging.WARNING)
warnings.filterwarnings("ignore")


def search_space(trial: optuna.Trial, name: str) -> dict:
    """Ranges chosen around the published defaults, wide enough to matter."""
    if name == "iforest":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 50, 400, step=50),
            "max_samples": trial.suggest_categorical("max_samples", [64, 128, 256, 512, 1024]),
        }
    if name == "ocsvm":
        return {
            "nu": trial.suggest_float("nu", 0.001, 0.2, log=True),
            "gamma": trial.suggest_categorical("gamma", ["scale", "auto", 0.01, 0.05, 0.1]),
        }
    if name == "lof":
        return {"n_neighbors": trial.suggest_int("n_neighbors", 5, 100, log=True)}
    if name == "knn":
        return {"n_neighbors": trial.suggest_int("n_neighbors", 1, 50, log=True)}
    if name == "pca_recon":
        return {"n_components": trial.suggest_int("n_components", 2, 28)}
    if name == "autoencoder":
        return {
            "hidden_dim": trial.suggest_categorical("hidden_dim", [8, 16, 24, 32, 48]),
            "latent_dim": trial.suggest_int("latent_dim", 2, 16),
            "epochs": trial.suggest_int("epochs", 10, 40, step=10),
            "lr": trial.suggest_float("lr", 1e-4, 5e-3, log=True),
        }
    if name == "vae":
        return {
            "hidden_dim": trial.suggest_categorical("hidden_dim", [16, 24, 32, 48]),
            "latent_dim": trial.suggest_int("latent_dim", 2, 16),
            "beta": trial.suggest_float("beta", 0.05, 4.0, log=True),
            "epochs": trial.suggest_int("epochs", 10, 40, step=10),
        }
    if name == "deep_svdd":
        return {
            "hidden_dim": trial.suggest_categorical("hidden_dim", [16, 32, 64]),
            "rep_dim": trial.suggest_int("rep_dim", 4, 24),
            "epochs": trial.suggest_int("epochs", 10, 40, step=10),
            "lr": trial.suggest_float("lr", 1e-4, 5e-3, log=True),
            "weight_decay": trial.suggest_float("weight_decay", 1e-7, 1e-3, log=True),
        }
    if name == "gmm":
        return {
            "n_components": trial.suggest_int("n_components", 1, 20),
            "covariance_type": trial.suggest_categorical(
                "covariance_type", ["full", "diag", "tied"]
            ),
        }
    if name == "mahalanobis":
        return {"support_fraction": trial.suggest_float("support_fraction", 0.55, 0.99)}
    if name == "hbos":
        return {
            "n_bins": trial.suggest_int("n_bins", 10, 200, log=True),
            "alpha": trial.suggest_float("alpha", 0.01, 0.5, log=True),
        }
    if name == "loda":
        return {
            "n_bins": trial.suggest_int("n_bins", 5, 100, log=True),
            "n_random_cuts": trial.suggest_int("n_random_cuts", 20, 300, step=20),
        }
    raise ValueError(f"no search space defined for {name}")


TUNABLE = [
    "iforest",
    "ocsvm",
    "lof",
    "knn",
    "pca_recon",
    "autoencoder",
    "vae",
    "deep_svdd",
    "gmm",
    "mahalanobis",
    "hbos",
    "loda",
]


def tune_one(cfg, name, X_fit_normal, X_val, y_val, n_trials) -> tuple[dict, float, pd.DataFrame]:
    history = []

    def objective(trial: optuna.Trial) -> float:
        params = search_space(trial, name)
        model = build_model(name, cfg, params)
        model.fit(X_fit_normal)
        ap = inner_validation_ap(y_val, model.score(X_val))
        history.append({"model": name, "trial": trial.number, "inner_ap": ap, **params})
        return -1.0 if np.isnan(ap) else ap

    sampler = optuna.samplers.TPESampler(seed=cfg.seed)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return study.best_params, float(study.best_value), pd.DataFrame(history)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=TUNABLE)
    parser.add_argument("--trials", type=int, default=None)
    args = parser.parse_args()

    cfg = load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    n_trials = args.trials or cfg.tuning.n_trials

    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split = chronological_split(df, cfg.split.train_fraction)
    train = split.train_full
    inner = inner_temporal_split(len(train), cfg.tuning.inner_val_fraction)

    fit_part = train.iloc[: inner.fit_end]
    val_part = train.iloc[inner.fit_end :]
    scaler = fit_scaler(fit_part)
    X_fit_normal = transform(scaler, fit_part[fit_part["Class"] == 0])
    X_fit_normal = subsample_for_fit(X_fit_normal, cfg.tuning.fit_subsample, cfg.seed)
    X_val = transform(scaler, val_part)
    y_val = val_part["Class"].to_numpy()

    print(
        f"inner fit: {len(X_fit_normal):,} normale (nën-mostër nga {inner.fit_end:,}) | "
        f"inner validim: {len(X_val):,} rreshta, {int(y_val.sum())} mashtrime\n"
    )

    best_params, rows, histories = {}, [], []
    for name in args.models:
        params, value, history = tune_one(cfg, name, X_fit_normal, X_val, y_val, n_trials)
        default_model = build_model(name, cfg)
        default_model.fit(X_fit_normal)
        default_ap = inner_validation_ap(y_val, default_model.score(X_val))
        best_params[name] = params
        rows.append(
            {
                "model": MODEL_LABELS.get(name, name),
                "inner_ap_default": default_ap,
                "inner_ap_tuned": value,
                "improvement": value - default_ap,
                "best_params": json.dumps(params, sort_keys=True),
            }
        )
        histories.append(history)
        print(f"{name:<13} default {default_ap:.4f} -> tuned {value:.4f}  {params}", flush=True)

    (results_dir / "tuned_params.json").write_text(
        json.dumps(best_params, indent=2, sort_keys=True)
    )
    table = pd.DataFrame(rows).sort_values("improvement", ascending=False)
    save_table(table, results_dir, "tuning_summary")
    save_table(pd.concat(histories, ignore_index=True), results_dir, "tuning_history")
    print(
        "\n"
        + table[["model", "inner_ap_default", "inner_ap_tuned", "improvement"]].to_string(
            index=False
        )
    )
    write_manifest(results_dir, "exp9_tuning", cfg.raw)


if __name__ == "__main__":
    main()

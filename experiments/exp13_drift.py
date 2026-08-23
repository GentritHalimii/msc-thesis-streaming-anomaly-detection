"""Which distribution actually moved — the normals, or the frauds?

Runs the drift decomposition across every rolling-origin block. For each
block the reference is that fold's own training window, so the question asked
is exactly the operational one: at the moment of deployment, how different is
what comes next from what the model was fitted on?
"""

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.data.load import FEATURE_COLUMNS, load_transactions
from src.evaluation.drift import (
    calibrate_page_hinkley,
    feature_drift,
    page_hinkley,
    separability,
)
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import load_folds, rolling_origin_folds
from src.evaluation.report import AX, MODEL_LABELS, new_figure, save_figure, save_table

PSI_MODERATE, PSI_MAJOR = 0.10, 0.25


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    drift_rows, feature_rows = [], []
    for f in folds:
        train = df.iloc[: f.train_end]
        test = df.iloc[f.test_start : f.test_end]
        train_normal = train[train["Class"] == 0]
        test_normal = test[test["Class"] == 0]
        test_fraud = test[test["Class"] == 1]

        # Covariate shift: normals then vs normals now.
        d_normal = feature_drift(train_normal, test_normal, FEATURE_COLUMNS)
        # Concept shift: how far this block's frauds sit from training normals,
        # compared with how far the training frauds sat.
        d_fraud = feature_drift(train[train["Class"] == 1], test_fraud, FEATURE_COLUMNS)

        for src, tab in (("normals", d_normal), ("frauds", d_fraud)):
            tab = tab.assign(fold=f.index, population=src)
            feature_rows.append(tab)

        sep_test = separability(train_normal, test, FEATURE_COLUMNS)
        sep_train = separability(train_normal, train, FEATURE_COLUMNS)
        drift_rows.append(
            {
                "fold": f.index,
                "psi_normals_mean": float(d_normal["psi"].mean()),
                "psi_normals_max": float(d_normal["psi"].max()),
                "psi_normals_over_moderate": int((d_normal["psi"] > PSI_MODERATE).sum()),
                "psi_frauds_mean": float(d_fraud["psi"].mean()),
                "psi_frauds_max": float(d_fraud["psi"].max()),
                "psi_frauds_over_moderate": int((d_fraud["psi"] > PSI_MODERATE).sum()),
                "ks_normals_median": float(d_normal["ks_stat"].median()),
                "ks_frauds_median": float(d_fraud["ks_stat"].median()),
                "train_ap_distance": sep_train.get("ap_distance_detector", np.nan),
                "test_ap_distance": sep_test.get("ap_distance_detector", np.nan),
                "test_cohens_d": sep_test.get("cohens_d", np.nan),
                **{f"test_{k}": v for k, v in sep_test.items() if k.startswith("z_norm")},
            }
        )

    drift = pd.DataFrame(drift_rows)
    save_table(drift, results_dir, "drift_per_fold", float_fmt="%.4f")
    # KS p-values here run down to 1e-300; %.4f would flatten them all to zero.
    save_table(
        pd.concat(feature_rows, ignore_index=True),
        results_dir,
        "drift_per_feature",
        float_fmt="%.6g",
    )
    print(drift.to_string(index=False))

    # --- Figure: the decomposition, in one picture -----------------------
    fig, ax = new_figure(figsize=(6.8, 4.2))
    ax.plot(
        drift["fold"],
        drift["psi_normals_mean"],
        marker="o",
        markersize=4,
        color="#2a78d6",
        label="Normalet: trajnim vs test (zhvendosje kovariatësh)",
    )
    ax.plot(
        drift["fold"],
        drift["psi_frauds_mean"],
        marker="s",
        markersize=4,
        color="#e34948",
        label="Mashtrimet: trajnim vs test (zhvendosje koncepti)",
    )
    ax.axhline(PSI_MODERATE, color="#c3c2b7", lw=1)
    ax.text(
        0.02, PSI_MODERATE * 1.08, "PSI = 0.10 (zhvendosje e moderuar)", fontsize=8, color="#898781"
    )
    ax.axhline(PSI_MAJOR, color="#c3c2b7", lw=1, ls=":")
    ax.text(0.02, PSI_MAJOR * 1.05, "PSI = 0.25 (zhvendosje e madhe)", fontsize=8, color="#898781")
    ax.set_xlabel(AX["fold"])
    ax.set_ylabel("PSI mesatar mbi 29 veçoritë")
    ax.legend(loc="upper left", fontsize=8.5)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "drift_psi_decomposition")

    # --- Figure: model-free separability collapses over time -------------
    fig, ax = new_figure(figsize=(6.8, 4.0))
    ax.plot(
        drift["fold"],
        drift["train_ap_distance"],
        marker="o",
        markersize=4,
        color="#4a3aa7",
        label="Brenda dritares së trajnimit",
    )
    ax.plot(
        drift["fold"],
        drift["test_ap_distance"],
        marker="s",
        markersize=4,
        color="#eb6834",
        label="Në bllokun e testimit",
    )
    ax.set_xlabel(AX["fold"])
    ax.set_ylabel("AP e detektorit pa model (norma ‖z‖)")
    ax.legend()
    save_figure(fig, REPO_ROOT / cfg.results_dir, "drift_separability")

    # --- Unsupervised monitoring: could a change detector have noticed? ---
    # The threshold is calibrated per fold and per model against a reference
    # stream drawn from that model's TRAINING score distribution, which by
    # construction contains no change point. A fixed threshold would be
    # meaningless: the Page-Hinkley statistic scales with block length, so a
    # value that is silent over one block fires constantly over a longer one.
    fs = load_folds(results_dir, cfg.protocol.n_folds)
    rng = np.random.default_rng(cfg.seed)
    monitor_rows = []
    for i, fold_scores in enumerate(fs):
        for name in ("iforest", "autoencoder", "ocsvm"):
            if name not in fold_scores.models:
                continue
            test_scores = fold_scores.test_scores(name)
            grid = fold_scores.train_quantiles(name)
            reference = np.interp(
                rng.uniform(size=len(test_scores)), np.linspace(0.0, 1.0, len(grid)), grid
            )
            centre = float(reference.mean())
            spread = float(reference.std()) or 1.0
            threshold = calibrate_page_hinkley(
                (reference - centre) / spread, delta=0.01, n_permutations=25
            )
            cps = page_hinkley((test_scores - centre) / spread, delta=0.01, threshold=threshold)
            monitor_rows.append(
                {
                    "fold": i,
                    "model": name,
                    "threshold": threshold,
                    "n_change_points": len(cps),
                    "first_change_index": cps[0] if cps else np.nan,
                    "detected_at_fraction": (cps[0] / len(test_scores)) if cps else np.nan,
                    "block_size": len(test_scores),
                }
            )
    monitor = pd.DataFrame(monitor_rows)
    monitor["model"] = monitor["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(monitor, results_dir, "drift_page_hinkley", float_fmt="%.3f")
    detected = monitor["n_change_points"] > 0
    print(
        f"\nPage-Hinkley: sinjal zhvendosjeje në {int(detected.sum())} nga "
        f"{len(monitor)} kombinime fold-model (prag i kalibruar për secilin)."
    )

    write_manifest(results_dir, "exp13_drift", cfg.raw)
    print("\nMesatarja mbi fold-et:")
    print(f"  PSI normalet  = {drift['psi_normals_mean'].mean():.4f}")
    print(f"  PSI mashtrimet= {drift['psi_frauds_mean'].mean():.4f}")
    print(
        f"  AP(‖z‖) trajnim {drift['train_ap_distance'].mean():.4f} -> "
        f"test {drift['test_ap_distance'].mean():.4f}"
    )


if __name__ == "__main__":
    main()

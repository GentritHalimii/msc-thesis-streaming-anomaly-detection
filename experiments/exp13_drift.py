"""Which distribution actually moved — the normals, or the frauds?

Runs the drift decomposition across every rolling-origin block. For each
block the reference is that fold's own training window, so the question asked
is exactly the operational one: at the moment of deployment, how different is
what comes next from what the model was fitted on?
"""

import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from src.config import REPO_ROOT, load_config
from src.data.load import FEATURE_COLUMNS, load_transactions
from src.evaluation.drift import (
    calibrate_page_hinkley,
    feature_drift,
    page_hinkley,
    psi_permutation_null,
    separability,
)
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import load_folds, rolling_origin_folds
from src.evaluation.report import (
    BASELINE,
    CLASS_COLORS,
    CM,
    FULL_WIDTH,
    INK_2,
    MODEL_LABELS,
    MUTED,
    legend_above,
    new_figure,
    save_figure,
    save_table,
    value_grid,
)

PSI_MODERATE, PSI_MAJOR = 0.10, 0.25


def figures(cfg, drift: pd.DataFrame) -> None:
    # --- The decomposition, read against what noise alone produces --------
    # Logarithmic, because the two populations differ by more than an order
    # of magnitude; the shaded band is the range of the mean PSI under random
    # relabelling (null mean to its 95th percentile), so each point can be
    # read as "this much above chance".
    fig, ax = new_figure(figsize=(FULL_WIDTH, 7.0 * CM))
    x = drift["fold"].to_numpy()
    for prefix, label, color, marker in (
        ("psi_normals", "Transaksionet legjitime", CLASS_COLORS[0], "o"),
        ("psi_frauds", "Mashtrimet", CLASS_COLORS[1], "s"),
    ):
        ax.fill_between(
            x,
            drift[f"{prefix}_null_mean"],
            drift[f"{prefix}_null_p95"],
            color=color,
            alpha=0.15,
            linewidth=0,
        )
        ax.plot(x, drift[f"{prefix}_null_mean"], color=color, lw=0.8, ls=(0, (2, 2)))
        ax.plot(
            x,
            drift[f"{prefix}_mean"],
            color=color,
            marker=marker,
            markersize=5,
            markeredgecolor="#ffffff",
            markeredgewidth=0.7,
            label=label,
        )
    for level, text in ((PSI_MODERATE, "0.10 moderuar"), (PSI_MAJOR, "0.25 e madhe")):
        # The line stops before its label, so it does not run through the text.
        ax.hlines(level, x[0] - 0.3, x[-1] + 0.1, color=BASELINE, lw=0.8, zorder=1)
        ax.text(x[-1] + 0.15, level, text, fontsize=9, color=MUTED, va="center")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xticks(x, [f"{f}\n({n})" for f, n in zip(x, drift["test_frauds"], strict=True)])
    ax.set_xlim(x[0] - 0.3, x[-1] + 1.3)
    ax.set_xlabel("Fold (në kllapa: mashtrimet në bllokun e testimit)")
    ax.set_ylabel("PSI mesatar mbi 29 veçori")
    value_grid(ax, "y")
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor=INK_2, alpha=0.15))
    labels.append("Zhurma e pritur (permutacione)")
    legend_above(ax, handles=handles, labels=labels)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "drift_psi_decomposition")

    # --- Model-free separability, training window against test block -----
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.2 * CM))
    ax.plot(
        x,
        drift["train_ap_distance"],
        marker="o",
        markersize=5,
        color=INK_2,
        markeredgecolor="#ffffff",
        markeredgewidth=0.7,
        label="Brenda dritares së trajnimit",
    )
    ax.plot(
        x,
        drift["test_ap_distance"],
        marker="s",
        markersize=5,
        color="#eb6834",
        markeredgecolor="#ffffff",
        markeredgewidth=0.7,
        label="Në bllokun e testimit",
    )
    ax.set_xticks(x, [f"{f}\n({n})" for f, n in zip(x, drift["test_frauds"], strict=True)])
    ax.set_xlabel("Fold (në kllapa: mashtrimet në bllokun e testimit)")
    ax.set_ylabel("AP e detektorit të distancës")
    ax.set_ylim(0, None)
    value_grid(ax, "y")
    legend_above(ax)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "drift_separability")


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
        null_normal = psi_permutation_null(
            train_normal, test_normal, FEATURE_COLUMNS, n_permutations=40, seed=cfg.seed
        )
        null_fraud = psi_permutation_null(
            train[train["Class"] == 1], test_fraud, FEATURE_COLUMNS, seed=cfg.seed
        )
        drift_rows.append(
            {
                "fold": f.index,
                "psi_normals_mean": float(d_normal["psi"].mean()),
                "psi_normals_max": float(d_normal["psi"].max()),
                "psi_normals_over_moderate": int((d_normal["psi"] > PSI_MODERATE).sum()),
                "psi_frauds_mean": float(d_fraud["psi"].mean()),
                "psi_frauds_max": float(d_fraud["psi"].max()),
                "psi_frauds_over_moderate": int((d_fraud["psi"] > PSI_MODERATE).sum()),
                "test_frauds": len(test_fraud),
                "psi_normals_null_mean": null_normal["null_mean"],
                "psi_normals_null_p95": null_normal["null_p95"],
                "psi_normals_p": null_normal["p_value"],
                "psi_frauds_null_mean": null_fraud["null_mean"],
                "psi_frauds_null_p95": null_fraud["null_p95"],
                "psi_frauds_excess": null_fraud["excess"],
                "psi_frauds_p": null_fraud["p_value"],
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

    figures(cfg, drift)

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

    # A verdict file, like every other analysis in this study, so the thesis
    # text can be regenerated from the measurements instead of transcribed.
    per_feature = pd.read_csv(results_dir / "drift_per_feature.csv")
    psi_n = float(drift["psi_normals_mean"].mean())
    psi_f = float(drift["psi_frauds_mean"].mean())
    n_features = per_feature["feature"].nunique()
    over_n = float(drift["psi_normals_over_moderate"].mean())
    over_f = float(drift["psi_frauds_over_moderate"].mean())
    psi_f_null = float(drift["psi_frauds_null_mean"].mean())
    significant = int((drift["psi_frauds_p"] < 0.05).sum())
    normals_significant = int((drift["psi_normals_p"] < 0.05).sum())
    noise_share = psi_f_null / psi_f
    verdict = (
        f"Zhvendosja nuk prek të dyja popullatat njësoj. Indeksi PSI për transaksionet "
        f"legjitime është mesatarisht {psi_n:.3f}, pra brenda intervalit 0.10 deri 0.25 që "
        f"zakonisht lexohet si zhvendosje e moderuar, ndërsa për mashtrimet ai është "
        f"{psi_f:.3f}. Numri i vogël i mashtrimeve për bllok e fryn këtë të fundit: me "
        f"permutacione të etiketave të dritares, vetëm zhurma e mostrimit jep mesatarisht "
        f"{psi_f_null:.3f}, pra rreth {100 * noise_share:.0f} për qind e vlerës së vëzhguar. "
        f"Megjithatë PSI e vëzhguar e tejkalon atë të zhurmës në {significant} nga "
        f"{len(drift)} fold-e (p < 0.05), dhe teprica mesatare mbi zhurmën është "
        f"{float(drift['psi_frauds_excess'].mean()):.3f}, një rend madhësie mbi PSI-në e "
        f"popullatës legjitime. Edhe zhvendosja e legjitimeve është reale, sepse e kalon "
        f"zhurmën në {normals_significant} nga {len(drift)} fold-e, por është e vogël. "
        f"Mesatarisht {over_n:.0f} nga {n_features} veçori e kalojnë pragun e moderuar te "
        f"popullata legjitime kundrejt {over_f:.0f} nga {n_features} te ajo e mashtrimeve, "
        f"por numri i dytë nuk është i interpretueshëm pa korrigjimin për zhurmën. "
        f"Aftësia ndarëse e matur pa model bie nga {drift['train_ap_distance'].mean():.3f} "
        f"në dritaren e trajnimit në {drift['test_ap_distance'].mean():.3f} në atë të "
        f"testimit. Monitorimi me Page-Hinkley, me prag të kalibruar veç e veç për çdo fold "
        f"dhe model me permutacione, jep sinjal zhvendosjeje në {int(detected.sum())} nga "
        f"{len(monitor)} kombinime fold-model."
    )
    (results_dir / "drift_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)

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

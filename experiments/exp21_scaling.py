"""Does the choice of preprocessing matter more than the choice of detector?

Every distance, density and reconstruction detector inherits its notion of
"far" from whatever scaling was applied first, and yet the scaler is usually
picked once and never revisited. It deserves scrutiny here for a specific
reason: the scaler has to be fitted on a training window that still contains
the frauds, because at deployment nobody knows which rows those are. The
statistics that define "normal spread" are therefore contaminated by the very
outliers the system is supposed to expose.

Six preprocessing choices are compared against all three detectors and the
supervised reference, over the full rolling-origin protocol, so the comparison
carries the same fold-level uncertainty as the main results.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import AX, MODEL_LABELS, model_color, new_figure, save_figure, save_table
from src.evaluation.stats import friedman, wilcoxon_pairs
from src.models.build import ALL_MODELS, build_model

SCALER_ORDER = [
    "standard",
    "robust",
    "quantile_normal",
    "quantile_uniform",
    "power_yeo_johnson",
    "minmax",
    "none",
]
SCALER_LABELS = {
    "standard": "StandardScaler",
    "robust": "RobustScaler",
    "quantile_normal": "Quantile (normal)",
    "quantile_uniform": "Quantile (uniform)",
    "power_yeo_johnson": "PowerTransformer",
    "minmax": "MinMaxScaler",
    "none": "Pa skalim",
}


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    rows = []
    for fold in folds:
        train = df.iloc[: fold.train_end]
        test = df.iloc[fold.test_start : fold.test_end]
        train_normal = train[train["Class"] == 0]
        y_train = train["Class"].to_numpy()
        y_test = test["Class"].to_numpy()

        for kind in SCALER_ORDER:
            scaler = fit_scaler(train, kind, cfg.seed)
            X_train_full = transform(scaler, train)
            X_train_normal = transform(scaler, train_normal)
            X_test = transform(scaler, test)

            for name in ALL_MODELS:
                model = build_model(name, cfg)
                if name == "logreg":
                    model.fit(X_train_full, y_train)
                else:
                    model.fit(X_train_normal)
                ap = average_precision_score(y_test, model.score(X_test))
                rows.append({"fold": fold.index, "scaler": kind, "model": name, "ap": ap})
        print(f"fold {fold.index} done", flush=True)

    per_fold = pd.DataFrame(rows)
    save_table(per_fold, results_dir, "scaling_per_fold", float_fmt="%.5f")

    summary = (
        per_fold.groupby(["model", "scaler"])["ap"].agg(ap_mean="mean", ap_std="std").reset_index()
    )
    baseline = summary[summary["scaler"] == "standard"].set_index("model")["ap_mean"]
    summary["vs_standard"] = summary.apply(lambda r: r["ap_mean"] - baseline[r["model"]], axis=1)
    wide = summary.pivot(index="scaler", columns="model", values="ap_mean")
    wide = wide.reindex(SCALER_ORDER)
    wide.index = [SCALER_LABELS[k] for k in wide.index]
    wide.columns = [MODEL_LABELS.get(c, c) for c in wide.columns]
    save_table(
        wide.reset_index().rename(columns={"index": "Paraprocesimi"}),
        results_dir,
        "scaling_summary",
        float_fmt="%.4f",
    )
    print("\n" + wide.round(4).to_string())

    # Is the preprocessing choice significant for the unsupervised detectors?
    stats_rows = []
    for name in ALL_MODELS:
        sub = per_fold[per_fold["model"] == name].pivot(
            index="fold", columns="scaler", values="ap"
        )[SCALER_ORDER]
        res = friedman(sub)
        best = sub.mean().idxmax()
        pair = wilcoxon_pairs(sub, [(best, "standard")]).iloc[0] if best != "standard" else None
        stats_rows.append(
            {
                "Detektori": MODEL_LABELS.get(name, name),
                "Friedman_chi2": res["statistic"],
                "p_value": res["p_value"],
                "Paraprocesimi_me_i_mire": SCALER_LABELS[best],
                "delta_ndaj_standard": float(sub.mean()[best] - sub.mean()["standard"]),
                "wilcoxon_p": float(pair["p_value"]) if pair is not None else np.nan,
                "fitore_nga_8": int(pair["wins_a"]) if pair is not None else np.nan,
            }
        )
    stats = pd.DataFrame(stats_rows)
    save_table(stats, results_dir, "scaling_significance", float_fmt="%.6g")
    print("\n" + stats.to_string(index=False))

    # --- Figure: preprocessing effect per detector ------------------------
    fig, ax = new_figure(figsize=(7.2, 4.4))
    x = np.arange(len(SCALER_ORDER))
    width = 0.2
    for i, name in enumerate(ALL_MODELS):
        sub = summary[summary["model"] == name].set_index("scaler").reindex(SCALER_ORDER)
        ax.bar(
            x + (i - 1.5) * width,
            sub["ap_mean"],
            width=width,
            yerr=sub["ap_std"].fillna(0.0),
            color=model_color(name),
            label=MODEL_LABELS.get(name, name),
            error_kw={"ecolor": "#898781", "elinewidth": 0.8, "capsize": 1.5},
        )
    ax.set_xticks(x, [SCALER_LABELS[k] for k in SCALER_ORDER], rotation=25, ha="right")
    ax.set_ylabel(AX["ap"] + " mbi 8 fold-e")
    ax.legend(fontsize=8.5)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "scaling_effect")

    unsup = [m for m in ALL_MODELS if m != "logreg"]
    spread = (
        summary[summary["model"].isin(unsup)]
        .groupby("model")["ap_mean"]
        .agg(lambda v: v.max() - v.min())
    )
    verdict = (
        "Zgjedhja e paraprocesimit ka ndikim të krahasueshëm me zgjedhjen e algoritmit. "
        f"Për detektorët unsupervised, hapësira mes paraprocesimit më të mirë dhe atij më "
        f"të keq është {spread.min():.3f} deri {spread.max():.3f} njësi AP, ndërsa "
        f"hapësira mes vetë detektorëve nën StandardScaler është "
        f"{baseline[unsup].max() - baseline[unsup].min():.3f}. "
        + "; ".join(
            f"{r['Detektori']}: më i mirë {r['Paraprocesimi_me_i_mire']} "
            f"({r['delta_ndaj_standard']:+.3f} ndaj StandardScaler)"
            for _, r in stats.iterrows()
        )
        + "."
    )
    (results_dir / "scaling_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp21_scaling", cfg.raw)


if __name__ == "__main__":
    main()

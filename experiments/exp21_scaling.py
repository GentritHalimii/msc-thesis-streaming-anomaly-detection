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
from src.evaluation.report import (
    AX,
    CM,
    FULL_WIDTH,
    MODEL_LABELS,
    MODEL_MARKERS,
    legend_above,
    model_color,
    new_figure,
    ordered_models,
    save_figure,
    save_table,
    value_grid,
)
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
    summarise(cfg, results_dir, per_fold)


def prequential_choice(per_fold: pd.DataFrame) -> pd.DataFrame:
    """The scaler a practitioner would have picked using only earlier folds.

    Picking the best of seven scalers on the same folds that then measure its
    gain overstates the gain. Here the choice for fold i is made on folds
    0..i-1 alone, so fold 0, which has no history, is left out, and the
    comparison with StandardScaler runs over the remaining folds.
    """
    rows = []
    for name, grp in per_fold.groupby("model"):
        wide = grp.pivot(index="fold", columns="scaler", values="ap")
        for i in wide.index[1:]:
            choice = wide.loc[: i - 1].mean().idxmax()
            rows.append(
                {
                    "model": name,
                    "fold": int(i),
                    "zgjedhja": choice,
                    "ap_zgjedhja": float(wide.loc[i, choice]),
                    "ap_standard": float(wide.loc[i, "standard"]),
                }
            )
    out = pd.DataFrame(rows)
    out["delta"] = out["ap_zgjedhja"] - out["ap_standard"]
    return out


def summarise(cfg, results_dir, per_fold: pd.DataFrame) -> None:
    """Tables, the figure and the verdict, from the per-fold record."""
    summary = (
        per_fold.groupby(["model", "scaler"])["ap"].agg(ap_mean="mean", ap_std="std").reset_index()
    )
    baseline = summary[summary["scaler"] == "standard"].set_index("model")["ap_mean"]
    summary["vs_standard"] = summary.apply(lambda r: r["ap_mean"] - baseline[r["model"]], axis=1)
    wide = summary.pivot(index="scaler", columns="model", values="ap_mean")
    wide = wide.reindex(SCALER_ORDER)[ordered_models(wide.columns)]
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

    prequential = prequential_choice(per_fold)
    save_table(prequential, results_dir, "scaling_prequential_per_fold", float_fmt="%.5f")
    preq_rows = []
    for name, grp in prequential.groupby("model"):
        test = wilcoxon_pairs(
            grp.set_index("fold")[["ap_zgjedhja", "ap_standard"]],
            [("ap_zgjedhja", "ap_standard")],
        ).iloc[0]
        preq_rows.append(
            {
                "Detektori": MODEL_LABELS.get(name, name),
                "Zgjedhja më e shpeshtë": SCALER_LABELS[grp["zgjedhja"].mode().iloc[0]],
                "AP me zgjedhjen": float(grp["ap_zgjedhja"].mean()),
                "AP me StandardScaler": float(grp["ap_standard"].mean()),
                "Δ AP": float(grp["delta"].mean()),
                "Fitore": f"{int(test['wins_a'])} nga {len(grp)}",
                "p (Wilcoxon)": float(test["p_value"]),
            }
        )
    preq_table = pd.DataFrame(preq_rows)
    preq_table = preq_table.set_index("Detektori").loc[
        [MODEL_LABELS[m] for m in ordered_models(prequential["model"].unique())]
    ]
    save_table(preq_table.reset_index(), results_dir, "scaling_prequential", float_fmt="%.4f")
    print("\n" + preq_table.to_string())

    figure(cfg, summary)

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
        + ". Kur skaluesi zgjidhet vetëm nga fold-et e mëparshme, përfitimi mbetet: "
        + "; ".join(
            f"{name} {row['Δ AP']:+.3f} ({row['Fitore']} fold-e)"
            for name, row in preq_table.iterrows()
        )
        + "."
    )
    (results_dir / "scaling_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp21_scaling", cfg.raw)


def figure(cfg, summary: pd.DataFrame) -> None:
    """A dot plot: one row per preprocessing option, one dot per detector.

    Grouped bars with error bars made seven groups of four bars that could
    only be compared bar against bar; along a shared horizontal axis each
    detector's movement from row to row reads directly.
    """
    fig, ax = new_figure(figsize=(FULL_WIDTH, 7.4 * CM))
    rows = list(reversed(SCALER_ORDER))
    for name in ordered_models(summary["model"].unique()):
        sub = summary[summary["model"] == name].set_index("scaler").reindex(rows)
        ax.plot(
            sub["ap_mean"],
            np.arange(len(rows)),
            linestyle="none",
            marker=MODEL_MARKERS.get(name, "o"),
            markersize=6,
            color=model_color(name),
            markeredgecolor="#ffffff",
            markeredgewidth=0.8,
            label=MODEL_LABELS.get(name, name),
            zorder=3,
        )
    ax.set_yticks(np.arange(len(rows)), [SCALER_LABELS[k] for k in rows])
    for label in ax.get_yticklabels():
        if label.get_text() == SCALER_LABELS["standard"]:
            label.set_fontweight("bold")
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 0.8)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel(AX["ap"] + ", mesatare mbi 8 fold-e")
    value_grid(ax, "both")
    legend_above(ax)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "scaling_effect")


def main_from_saved(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    summarise(cfg, results_dir, pd.read_csv(results_dir / "scaling_per_fold.csv"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-saved",
        action="store_true",
        help="rebuild tables, figure and verdict from scaling_per_fold.csv",
    )
    main_from_saved() if parser.parse_args().from_saved else main()

"""Main rolling-origin benchmark: every detector at every temporal cut point.

Reads only the saved fold scores, so it is cheap to re-run and never refits a
model. Produces the per-fold metric matrix that the significance tests, the
ensemble study and the thesis tables all build on.
"""

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import threshold_free_metrics, thresholded_metrics
from src.evaluation.operational import (
    amount_weighted_average_precision,
    budget_metrics,
    net_savings,
)
from src.evaluation.protocol import load_folds
from src.evaluation.report import (
    AX,
    MODEL_LABELS,
    model_color,
    new_figure,
    save_figure,
    save_table,
)
from src.models.build import FAMILY_OF

HEADLINE_BUDGET = 100


def per_fold_metrics(cfg, folds, fold_info: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, fs in enumerate(folds):
        info = fold_info.loc[fold_info["fold"] == i].iloc[0]
        contamination = (
            float(cfg.contamination)
            if cfg.contamination is not None
            else float(info["train_fraud_rate"])
        )
        y, amounts = fs.y, fs.amount
        for name in fs.models:
            s = fs.test_scores(name)
            thr = fs.train_threshold(name, contamination)
            at_thr = thresholded_metrics(y, s, thr)
            budget = budget_metrics(y, s, amounts, HEADLINE_BUDGET)
            savings = net_savings(y, s, amounts, HEADLINE_BUDGET, cfg.investigation_cost_eur)
            cost = fs.costs[name]
            rows.append(
                {
                    "fold": i,
                    "model": name,
                    "family": FAMILY_OF.get(name, "reference"),
                    "test_frauds": int((y == 1).sum()),
                    **threshold_free_metrics(y, s),
                    "amount_weighted_ap": amount_weighted_average_precision(y, s, amounts),
                    "precision_thr": at_thr["precision"],
                    "recall_thr": at_thr["recall"],
                    "f1_thr": at_thr["f1"],
                    "alerts_thr": at_thr["n_alerts"],
                    "precision_at_100": budget["precision_at_k"],
                    "recall_at_100": budget["recall_at_k"],
                    "amount_recall_at_100": budget["amount_recall_at_k"],
                    "savings_ratio_at_100": savings["savings_ratio"],
                    "fit_time_s": cost["fit_time_s"],
                    "score_us_per_tx": cost["score_us_per_tx"],
                    "fit_rss_mb": cost["fit_rss_mb"],
                }
            )
    return pd.DataFrame(rows)


def summarise(per_fold: pd.DataFrame) -> pd.DataFrame:
    ap_wide = per_fold.pivot(index="fold", columns="model", values="ap")
    avg_rank = ap_wide.rank(axis=1, ascending=False).mean()

    agg = per_fold.groupby("model").agg(
        family=("family", "first"),
        ap_mean=("ap", "mean"),
        ap_std=("ap", "std"),
        ap_min=("ap", "min"),
        ap_max=("ap", "max"),
        roc_auc_mean=("roc_auc", "mean"),
        amount_ap_mean=("amount_weighted_ap", "mean"),
        f1_thr_mean=("f1_thr", "mean"),
        precision_thr_mean=("precision_thr", "mean"),
        recall_thr_mean=("recall_thr", "mean"),
        precision_at_100=("precision_at_100", "mean"),
        recall_at_100=("recall_at_100", "mean"),
        amount_recall_at_100=("amount_recall_at_100", "mean"),
        savings_ratio_at_100=("savings_ratio_at_100", "mean"),
        fit_time_s=("fit_time_s", "mean"),
        score_us_per_tx=("score_us_per_tx", "mean"),
        fit_rss_mb=("fit_rss_mb", "mean"),
    )
    agg["avg_rank_ap"] = avg_rank
    return agg.reset_index().sort_values("ap_mean", ascending=False)


def figure_ap_per_fold(per_fold: pd.DataFrame, cfg):
    """One line per detector across folds; colour = family. The legend is by
    family because fourteen individual entries would swamp the plot."""
    fig, ax = new_figure(figsize=(7.0, 4.4))
    wide = per_fold.pivot(index="fold", columns="model", values="ap")
    for name in wide.columns:
        ax.plot(
            wide.index,
            wide[name],
            color=model_color(name),
            linestyle="-." if name == "logreg" else "-",
            linewidth=2.0 if name == "logreg" else 1.4,
            marker="o",
            markersize=3.5,
            alpha=0.95 if name == "logreg" else 0.8,
            label=MODEL_LABELS.get(name, name),
        )
    ax.set_xlabel(AX["fold"])
    ax.set_ylabel(AX["ap"])
    ax.set_yscale("log")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8.5)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "benchmark_ap_per_fold")


def figure_ap_ranking(summary: pd.DataFrame, cfg):
    """Mean AP with the across-fold spread, sorted. Horizontal bars keep the
    fourteen labels readable."""
    fig, ax = new_figure(figsize=(6.6, 5.2))
    d = summary.sort_values("ap_mean")
    ypos = np.arange(len(d))
    ax.barh(
        ypos,
        d["ap_mean"],
        xerr=d["ap_std"].fillna(0.0),
        color=[model_color(m) for m in d["model"]],
        height=0.62,
        error_kw={"ecolor": "#898781", "elinewidth": 1, "capsize": 2},
    )
    ax.set_yticks(ypos, [MODEL_LABELS.get(m, m) for m in d["model"]])
    ax.set_xlabel(AX["ap"] + " — mesatare mbi 8 fold-e (±1 s.d.)")
    ax.grid(axis="y", visible=False)
    for y, v in zip(ypos, d["ap_mean"], strict=True):
        ax.text(v + 0.008, y, f"{v:.3f}", va="center", fontsize=8, color="#52514e")
    ax.set_xlim(0, float(d["ap_mean"].max()) * 1.18)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "benchmark_ap_ranking")


def figure_quality_cost(summary: pd.DataFrame, cfg):
    """The trade-off RQ2 actually asks about: detection quality against the
    cost of producing one score. Both axes matter on a stream, and the
    picture is more informative than either column alone."""
    fig, ax = new_figure(figsize=(6.8, 4.6))
    for row in summary.itertuples(index=False):
        name = row.model
        ax.scatter(
            row.score_us_per_tx,
            row.ap_mean,
            s=90,
            color=model_color(name),
            alpha=0.85,
            edgecolor="white",
            linewidth=1.2,
            zorder=3,
            marker="D" if name == "logreg" else "o",
        )
        ax.annotate(
            MODEL_LABELS.get(name, name),
            (row.score_us_per_tx, row.ap_mean),
            fontsize=7.8,
            color="#52514e",
            xytext=(7, 3),
            textcoords="offset points",
        )
    ax.set_xscale("log")
    ax.set_xlabel("Kosto e pikëzimit (mikrosekonda për transaksion, shkallë log)")
    ax.set_ylabel(AX["ap"] + " — mesatare mbi 8 fold-e")
    ax.set_xlim(0.03, 200)
    best = summary.loc[summary["model"] != "logreg"].nlargest(1, "ap_mean").iloc[0]
    ax.annotate(
        "kompromisi më i mirë unsupervised",
        xy=(best.score_us_per_tx, best.ap_mean),
        xytext=(0.30, 0.62),
        textcoords="axes fraction",
        fontsize=8.2,
        color="#52514e",
        arrowprops={"arrowstyle": "->", "color": "#898781", "linewidth": 1},
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "benchmark_quality_cost")


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    fold_info = pd.read_csv(results_dir / "fold_summary.csv")
    folds = load_folds(results_dir, cfg.protocol.n_folds)

    per_fold = per_fold_metrics(cfg, folds, fold_info)
    save_table(per_fold, results_dir, "benchmark_per_fold")

    summary = summarise(per_fold)
    summary_out = summary.copy()
    summary_out["model"] = summary_out["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(summary_out, results_dir, "benchmark_summary")

    figure_ap_per_fold(per_fold, cfg)
    figure_ap_ranking(summary, cfg)
    figure_quality_cost(summary, cfg)

    write_manifest(results_dir, "exp10_benchmark", cfg.raw)
    cols = [
        "model",
        "family",
        "ap_mean",
        "ap_std",
        "avg_rank_ap",
        "roc_auc_mean",
        "f1_thr_mean",
        "precision_at_100",
        "recall_at_100",
        "score_us_per_tx",
    ]
    print(summary[cols].to_string(index=False))


if __name__ == "__main__":
    main()

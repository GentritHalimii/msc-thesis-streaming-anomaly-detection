"""Main rolling-origin benchmark: every detector at every temporal cut point.

Reads only the saved fold scores, so it is cheap to re-run and never refits a
model. Produces the per-fold metric matrix that the significance tests, the
ensemble study and the thesis tables all build on.
"""

import matplotlib as mpl
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
    CM,
    FULL_WIDTH,
    INK_2,
    MODEL_LABELS,
    MODEL_MARKERS,
    MUTED,
    legend_above,
    model_color,
    model_plot_kwargs,
    new_figure,
    ordered_models,
    save_figure,
    save_table,
    value_grid,
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
    # AP rises with the share of frauds in a block, and one block holds far
    # more of them than the rest, so the mean leans on it. The median and the
    # mean without that block show whether the ranking depends on it.
    densest = int(per_fold.groupby("fold")["test_frauds"].first().idxmax())
    agg["ap_median"] = ap_wide.median()
    agg["ap_mean_excl_densest_fold"] = ap_wide.drop(index=densest).mean()
    agg["densest_fold"] = densest
    return agg.reset_index().sort_values("ap_mean", ascending=False)


def figure_ap_per_fold(per_fold: pd.DataFrame, cfg):
    """One line per detector across folds, on a log scale because the folds
    differ by more than an order of magnitude in difficulty. The fraud count
    of each test block sits under its fold number, since it explains most of
    the shape."""
    fig, ax = new_figure(figsize=(FULL_WIDTH, 7.0 * CM))
    wide = per_fold.pivot(index="fold", columns="model", values="ap")
    frauds = per_fold.groupby("fold")["test_frauds"].first()
    for name in ordered_models(wide.columns):
        ax.plot(wide.index, wide[name], **model_plot_kwargs(name, markers=True))
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xticks(wide.index, [f"{i}\n({frauds.loc[i]})" for i in wide.index])
    ax.set_xlabel("Fold (në kllapa: mashtrimet në bllokun e testimit)")
    ax.set_ylabel(AX["ap"] + ", shkallë log")
    value_grid(ax, "y")
    legend_above(ax)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "benchmark_ap_per_fold")


def figure_ap_ranking(per_fold: pd.DataFrame, summary: pd.DataFrame, cfg):
    """Each detector's eight fold values, with the mean marked.

    The fold values are drawn instead of a ±1 s.d. bar: AP is bounded at zero
    and very skewed across folds, so a symmetric bar would run below zero and
    hide the fact that one fold (the one with the fraud cluster) pulls every
    mean upwards.
    """
    order = summary.sort_values("ap_mean")["model"].tolist()
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.2 * CM))
    for y, name in enumerate(order):
        values = per_fold.loc[per_fold["model"] == name, "ap"].to_numpy()
        color = model_color(name)
        ax.hlines(y, values.min(), values.max(), color=color, alpha=0.35, linewidth=1.2)
        ax.scatter(values, np.full(len(values), y), s=16, color=color, alpha=0.75, linewidths=0)
        mean = float(values.mean())
        ax.plot(
            [mean],
            [y],
            marker="D",
            markersize=7,
            color=color,
            markeredgecolor="#ffffff",
            markeredgewidth=0.9,
            zorder=4,
        )
        ax.annotate(
            f"{mean:.3f}",
            (mean, y),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=9.5,
            color=INK_2,
        )
    ax.set_yticks(range(len(order)), [MODEL_LABELS.get(m, m) for m in order])
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(order) - 0.3)
    ax.set_xlim(0, 1)
    ax.set_xlabel(AX["ap"] + " në secilin fold (rombi: mesatarja)")
    value_grid(ax, "x")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "benchmark_ap_ranking")


def figure_quality_cost(summary: pd.DataFrame, cfg):
    """The trade-off RQ2 actually asks about: detection quality against the
    cost of producing one score. Both axes matter on a stream, and the
    picture is more informative than either column alone."""
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.8 * CM))
    for row in summary.itertuples(index=False):
        name = row.model
        ax.plot(
            row.score_us_per_tx,
            row.ap_mean,
            marker=MODEL_MARKERS.get(name, "o"),
            markersize=8,
            color=model_color(name),
            markeredgecolor="#ffffff",
            markeredgewidth=1.0,
            linestyle="none",
            zorder=3,
        )
        ax.annotate(
            MODEL_LABELS.get(name, name),
            (row.score_us_per_tx, row.ap_mean),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=10,
            color=INK_2,
        )
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xlim(0.05, 500)
    ax.set_ylim(0, 0.85)
    ax.set_xlabel("Kosto e inferencës (mikrosekonda për transaksion, shkallë log)")
    ax.set_ylabel(AX["ap"] + ", mesatare")
    ax.text(
        0.012,
        0.97,
        "më mirë: lart majtas",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.5,
        color=MUTED,
    )
    value_grid(ax, "both")
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
    figure_ap_ranking(per_fold, summary, cfg)
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

"""Experiment 2 — contamination / threshold sensitivity.

Sweep the contamination hyperparameter; at each value derive the percentile
threshold from TRAINING scores and evaluate precision/recall/F1 on test.
Test labels never influence the threshold.

The sweep runs on the single 70/30 split of the research proposal, which asked
for exactly this analysis. It only scores the saved models, so it takes
seconds and belongs with the figures that are redrawn from saved results.
"""

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from src.config import REPO_ROOT, load_config
from src.evaluation.harness import score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import thresholded_metrics
from src.evaluation.report import (
    AX,
    FULL_WIDTH,
    MUTED,
    fig_legend_above,
    model_plot_kwargs,
    new_figure,
    ordered_models,
    save_figure,
    save_table,
)
from src.evaluation.thresholds import percentile_threshold

CONTAMINATIONS = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
PANELS = [("precision", AX["precision"]), ("recall", AX["recall"]), ("f1", AX["f1"])]


def draw(table: pd.DataFrame, train_fraud_rate: float, results_dir) -> None:
    """Precision, recall and F1 against contamination, one panel each."""
    fig, axes = new_figure(ncols=3, figsize=(FULL_WIDTH, 2.6), sharex=True, sharey=True)
    for ax, (metric, title) in zip(axes, PANELS, strict=True):
        # The training fraud rate is the contamination the main protocol uses.
        ax.axvline(train_fraud_rate, color=MUTED, linestyle="--", linewidth=0.9, zorder=1)
        for name in ordered_models(table["model"].unique()):
            sub = table[table["model"] == name].sort_values("contamination")
            ax.plot(sub["contamination"], sub[metric], **model_plot_kwargs(name, markers=True))
        ax.set_title(title)
        ax.set_xscale("log")
        ax.set_xticks([0.001, 0.01])
        ax.set_xlim(0.0004, 0.06)
        ax.set_ylim(0, 1)
        ax.xaxis.set_major_formatter(lambda value, _pos: f"{100 * value:.1f}%".replace(".0%", "%"))
    axes[0].set_ylabel("Vlera në bllokun e testimit")
    fig.supxlabel("Kontaminimi c (pjesa e pikëve të trajnimit mbi prag)", fontsize=9)
    handles, labels = axes[0].get_legend_handles_labels()
    handles.append(Line2D([], [], color=MUTED, linestyle="--", linewidth=0.9))
    labels.append("norma e mashtrimit në trajnim")
    fig_legend_above(fig, handles, labels, ncol=3)
    save_figure(fig, results_dir, "contamination_sweep")


def main(cfg=None):
    cfg = cfg or load_config()
    scored = score_test_window(cfg)

    rows = []
    for name, scores in scored.test_scores.items():
        for c in CONTAMINATIONS:
            thr = percentile_threshold(scored.train_scores[name], c)
            rows.append(
                {"model": name, "contamination": c}
                | thresholded_metrics(scored.y_test, scores, thr)
            )
    table = pd.DataFrame(rows)
    results_dir = REPO_ROOT / cfg.results_dir
    save_table(table, results_dir, "contamination_sweep")
    draw(table, scored.train_fraud_rate(), results_dir)

    write_manifest(results_dir, "exp2_contamination_sweep", cfg.raw)
    print(
        table.pivot_table(index="contamination", columns="model", values="f1", aggfunc="first")
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    np.random.seed(load_config().seed)
    main()

"""Experiment 3 — PR and ROC curves of every model on the 70/30 split.

One figure with two panels, precision-recall on the left and ROC on the right,
so the reader sees on one page why the thesis ranks detectors by Average
Precision: curves that are far apart in precision-recall space sit almost on
top of each other in ROC space. Only the saved models are scored, nothing is
refitted.
"""

import numpy as np
from matplotlib.lines import Line2D
from sklearn.metrics import precision_recall_curve, roc_curve

from src.config import REPO_ROOT, load_config
from src.evaluation.harness import score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import threshold_free_metrics
from src.evaluation.report import (
    AX,
    BASELINE,
    FULL_WIDTH,
    fig_legend_above,
    model_plot_kwargs,
    new_figure,
    ordered_models,
    save_figure,
    value_grid,
)


def main(cfg=None):
    cfg = cfg or load_config()
    scored = score_test_window(cfg)
    fraud_rate = scored.y_test.mean()

    fig, (ax_pr, ax_roc) = new_figure(ncols=2, figsize=(FULL_WIDTH, 3.0))
    for name in ordered_models(scored.test_scores):
        scores = scored.test_scores[name]
        precision, recall, _ = precision_recall_curve(scored.y_test, scores)
        fpr, tpr, _ = roc_curve(scored.y_test, scores)
        kw = model_plot_kwargs(name)
        # sklearn closes the curve with the point (recall 0, precision 1), which
        # draws a vertical line up the left edge for every model; drop it.
        ax_pr.plot(recall[:-1], precision[:-1], drawstyle="steps-post", **kw)
        ax_roc.plot(fpr, tpr, **kw)
        metrics = threshold_free_metrics(scored.y_test, scores)
        print(f"{name:12s} AP={metrics['ap']:.3f}  ROC-AUC={metrics['roc_auc']:.3f}")

    # What a random ranking achieves in each space.
    ax_pr.axhline(fraud_rate, color=BASELINE, linewidth=0.9, linestyle="--")
    ax_roc.plot([0, 1], [0, 1], color=BASELINE, linewidth=0.9, linestyle="--")

    ax_pr.set_title("Precision-Recall")
    ax_pr.set_xlabel(AX["recall"])
    ax_pr.set_ylabel(AX["precision"])
    ax_roc.set_title("ROC")
    ax_roc.set_xlabel(AX["fpr"])
    ax_roc.set_ylabel(AX["tpr"])
    for ax in (ax_pr, ax_roc):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.set_aspect("equal")
        value_grid(ax, "both")

    handles, labels = ax_pr.get_legend_handles_labels()
    handles.append(Line2D([], [], color=BASELINE, linewidth=0.9, linestyle="--"))
    labels.append("renditje e rastësishme")
    fig_legend_above(fig, handles, labels, ncol=3)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "curves_pr_roc")

    write_manifest(REPO_ROOT / cfg.results_dir, "exp3_curves", cfg.raw)
    print("wrote the curves_pr_roc figure")


if __name__ == "__main__":
    np.random.seed(load_config().seed)
    main()

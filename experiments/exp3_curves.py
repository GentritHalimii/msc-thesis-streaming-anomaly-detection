"""Experiment 3 — PR and ROC curves, all models overlaid (one figure each)."""

from sklearn.metrics import precision_recall_curve, roc_curve

from src.config import REPO_ROOT, load_config
from src.evaluation.harness import score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import threshold_free_metrics
from src.evaluation.report import AX, model_plot_kwargs, new_figure, save_figure


def main(cfg=None):
    cfg = cfg or load_config()
    scored = score_test_window(cfg)
    fraud_rate = scored.y_test.mean()

    fig, ax = new_figure()
    for name, scores in scored.test_scores.items():
        precision, recall, _ = precision_recall_curve(scored.y_test, scores)
        ap = threshold_free_metrics(scored.y_test, scores)["ap"]
        kw = model_plot_kwargs(name)
        kw["label"] += f" (AP={ap:.3f})"
        ax.plot(recall, precision, **kw)
    ax.axhline(fraud_rate, color="#c3c2b7", linewidth=1, label=f"rastësia (AP={fraud_rate:.4f})")
    ax.set_xlabel(AX["recall"])
    ax.set_ylabel(AX["precision"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="upper right")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "pr_curves")

    fig, ax = new_figure()
    for name, scores in scored.test_scores.items():
        fpr, tpr, _ = roc_curve(scored.y_test, scores)
        auc = threshold_free_metrics(scored.y_test, scores)["roc_auc"]
        kw = model_plot_kwargs(name)
        kw["label"] += f" (AUC={auc:.3f})"
        ax.plot(fpr, tpr, **kw)
    ax.plot([0, 1], [0, 1], color="#c3c2b7", linewidth=1, label="rastësia")
    ax.set_xlabel(AX["fpr"])
    ax.set_ylabel(AX["tpr"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "roc_curves")

    write_manifest(REPO_ROOT / cfg.results_dir, "exp3_curves", cfg.raw)
    print("wrote pr_curves and roc_curves figures")


if __name__ == "__main__":
    main()

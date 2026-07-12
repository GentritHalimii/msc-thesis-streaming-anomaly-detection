"""Experiment 2 — contamination / threshold sensitivity.

Sweep the contamination hyperparameter; at each value derive the percentile
threshold from TRAINING scores and evaluate precision/recall/F1 on test.
Test labels never influence the threshold.
"""

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.harness import score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import thresholded_metrics
from src.evaluation.report import model_plot_kwargs, new_figure, save_figure, save_table
from src.evaluation.thresholds import percentile_threshold

CONTAMINATIONS = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]


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
    save_table(table, REPO_ROOT / cfg.results_dir, "contamination_sweep")

    for metric, fname in [
        ("precision", "sweep_precision"),
        ("recall", "sweep_recall"),
        ("f1", "sweep_f1"),
    ]:
        fig, ax = new_figure()
        for name in scored.test_scores:
            sub = table[table["model"] == name]
            ax.plot(
                sub["contamination"],
                sub[metric],
                marker="o",
                markersize=4,
                **model_plot_kwargs(name),
            )
        ax.set_xscale("log")
        ax.set_xticks(CONTAMINATIONS, [f"{c:g}" for c in CONTAMINATIONS])
        ax.set_xlabel("contamination (train-percentile threshold)")
        ax.set_ylabel(f"{metric} on test window")
        ax.set_ylim(0, 1)
        ax.legend()
        save_figure(fig, REPO_ROOT / cfg.results_dir, fname)

    write_manifest(REPO_ROOT / cfg.results_dir, "exp2_contamination_sweep", cfg.raw)
    print(
        table.pivot_table(index="contamination", columns="model", values="f1", aggfunc="first")
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    np.random.seed(load_config().seed)
    main()

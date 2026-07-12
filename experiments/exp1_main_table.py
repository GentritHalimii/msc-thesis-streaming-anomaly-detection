"""Experiment 1 — main comparison table.

All models x {AP, ROC-AUC, F1/precision/recall at the train-percentile
threshold AND at the oracle best-F1 test threshold (upper bound, separate
columns)}, plus training time, peak memory, and offline inference latency.
"""

import json

import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.harness import contamination_value, score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import threshold_free_metrics, thresholded_metrics
from src.evaluation.report import MODEL_LABELS, save_table
from src.evaluation.thresholds import oracle_best_f1_threshold, percentile_threshold
from src.models.build import artifacts_dir


def main(cfg=None):
    cfg = cfg or load_config()
    scored = score_test_window(cfg)
    contamination = contamination_value(cfg, scored)
    fit_costs = json.loads((artifacts_dir(cfg) / "fit_costs.json").read_text())

    rows = []
    for name, scores in scored.test_scores.items():
        thr_pct = percentile_threshold(scored.train_scores[name], contamination)
        thr_oracle = oracle_best_f1_threshold(scored.y_test, scores)
        at_pct = thresholded_metrics(scored.y_test, scores, thr_pct)
        at_oracle = thresholded_metrics(scored.y_test, scores, thr_oracle)
        rows.append(
            {
                "model": MODEL_LABELS[name],
                **threshold_free_metrics(scored.y_test, scores),
                "precision_pct": at_pct["precision"],
                "recall_pct": at_pct["recall"],
                "f1_pct": at_pct["f1"],
                "alerts_pct": at_pct["n_alerts"],
                "precision_oracle": at_oracle["precision"],
                "recall_oracle": at_oracle["recall"],
                "f1_oracle": at_oracle["f1"],
                "fit_time_s": fit_costs[name]["fit_time_s"],
                "fit_delta_rss_mb": fit_costs[name]["fit_delta_rss_mb"],
                "inference_us_per_tx": scored.inference_s[name] / scored.n_test * 1e6,
            }
        )

    table = pd.DataFrame(rows).sort_values("ap", ascending=False)
    save_table(table, REPO_ROOT / cfg.results_dir, "metrics_main")
    write_manifest(REPO_ROOT / cfg.results_dir, "exp1_main_table", cfg.raw)
    print(f"contamination = {contamination:.5f} (train-window fraud rate if config null)")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()

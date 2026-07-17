"""Experiment 8 — WHY the ensemble fails: member diversity analysis.

Averaging only helps when members make different mistakes. Reports, on the
test window:
- Spearman (rank) and Pearson correlation between member scores — the
  z-averaged ensemble combines *values*, but ranking quality (AP) depends
  on rank agreement;
- pairwise Jaccard overlap of the alert sets at each member's own
  train-percentile threshold (what majority voting actually intersects),
  plus how many of the 108 test frauds each member/pair catches.
"""

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.harness import contamination_value, score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.report import save_table
from src.evaluation.thresholds import percentile_threshold
from src.models.build import UNSUPERVISED


def main(cfg=None):
    cfg = cfg or load_config()
    scored = score_test_window(cfg, model_names=UNSUPERVISED)
    contamination = contamination_value(cfg, scored)
    scores = pd.DataFrame({n: scored.test_scores[n] for n in UNSUPERVISED})

    spearman = scores.corr(method="spearman")
    pearson = scores.corr(method="pearson")
    corr = spearman.rename_axis("model").reset_index()
    for a in UNSUPERVISED:
        corr[f"pearson_{a}"] = pearson[a].to_numpy()
    save_table(corr, REPO_ROOT / cfg.results_dir, "ensemble_correlation", float_fmt="%.3f")
    print("Spearman rank correlation of test scores:")
    print(spearman.round(3).to_string())

    alerts = {
        n: scored.test_scores[n] >= percentile_threshold(scored.train_scores[n], contamination)
        for n in UNSUPERVISED
    }
    frauds = scored.y_test == 1
    rows = []
    for i, a in enumerate(UNSUPERVISED):
        for b in UNSUPERVISED[i + 1 :]:
            inter = int(np.sum(alerts[a] & alerts[b]))
            union = int(np.sum(alerts[a] | alerts[b]))
            rows.append(
                {
                    "pair": f"{a} & {b}",
                    "alerts_a": int(alerts[a].sum()),
                    "alerts_b": int(alerts[b].sum()),
                    "common_alerts": inter,
                    "jaccard": inter / union if union else 0.0,
                    "frauds_caught_a": int(np.sum(alerts[a] & frauds)),
                    "frauds_caught_b": int(np.sum(alerts[b] & frauds)),
                    "frauds_caught_both": int(np.sum(alerts[a] & alerts[b] & frauds)),
                }
            )
    overlap = pd.DataFrame(rows)
    save_table(overlap, REPO_ROOT / cfg.results_dir, "alert_overlap", float_fmt="%.3f")
    print(overlap.to_string(index=False))
    write_manifest(REPO_ROOT / cfg.results_dir, "exp8_ensemble_correlation", cfg.raw)


if __name__ == "__main__":
    main()

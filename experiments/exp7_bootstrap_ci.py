"""Experiment 7 — bootstrap confidence intervals on test-window AP.

The test window holds only 108 frauds, so point estimates of AP carry real
sampling uncertainty. B=1000 bootstrap resamples of the test window give:
- a 95% percentile CI per model, and
- PAIRED difference CIs for the comparisons the thesis actually claims
  (same resample indices for both models), plus the fraction of replicates
  where the difference is positive.

Uses only saved artifacts and pre-computed scores; thresholds are not
involved (AP is threshold-free), so nothing here can leak.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from experiments.exp4_ensemble import build_ensembles
from src.config import REPO_ROOT, load_config
from src.evaluation.harness import contamination_value, score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.report import MODEL_LABELS, save_table
from src.models.build import UNSUPERVISED

B = 1000
PAIRS = [
    ("autoencoder", "ocsvm"),
    ("autoencoder", "iforest"),
    ("autoencoder", "ensemble_avg"),
    ("ensemble_avg", "ocsvm"),
]


def main(cfg=None):
    cfg = cfg or load_config()
    scored = score_test_window(cfg)
    contamination = contamination_value(cfg, scored)
    for ens in build_ensembles(cfg, scored, contamination).values():
        scored.test_scores[ens.name] = ens.combine({n: scored.test_scores[n] for n in UNSUPERVISED})

    names = [*UNSUPERVISED, "ensemble_avg", "ensemble_vote", "logreg"]
    y = scored.y_test
    n = len(y)
    rng = np.random.default_rng(cfg.seed)

    ap = {name: np.empty(B) for name in names}
    for b in range(B):
        idx = rng.integers(0, n, n)
        yb = y[idx]
        for name in names:
            ap[name][b] = average_precision_score(yb, scored.test_scores[name][idx])

    rows = []
    for name in names:
        point = average_precision_score(y, scored.test_scores[name])
        lo, hi = np.percentile(ap[name], [2.5, 97.5])
        rows.append(
            {
                "model": MODEL_LABELS[name],
                "ap": point,
                "ap_ci95_low": lo,
                "ap_ci95_high": hi,
            }
        )
    ci_table = pd.DataFrame(rows)
    save_table(ci_table, REPO_ROOT / cfg.results_dir, "bootstrap_ci")
    print(ci_table.to_string(index=False))

    pair_rows = []
    for a, b_ in PAIRS:
        delta = ap[a] - ap[b_]
        lo, hi = np.percentile(delta, [2.5, 97.5])
        pair_rows.append(
            {
                "comparison": f"{MODEL_LABELS[a]} - {MODEL_LABELS[b_]}",
                "delta_ap_mean": float(delta.mean()),
                "delta_ci95_low": lo,
                "delta_ci95_high": hi,
                "frac_replicates_positive": float((delta > 0).mean()),
            }
        )
    pair_table = pd.DataFrame(pair_rows)
    save_table(pair_table, REPO_ROOT / cfg.results_dir, "bootstrap_pairwise")
    print(pair_table.to_string(index=False))
    write_manifest(REPO_ROOT / cfg.results_dir, "exp7_bootstrap_ci", cfg.raw)


if __name__ == "__main__":
    main()

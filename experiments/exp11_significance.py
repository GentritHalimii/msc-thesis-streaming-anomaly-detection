"""Is the ranking of detectors statistically defensible, or is it fold noise?

Runs the Friedman omnibus test over the per-fold AP matrix, draws the Nemenyi
critical-difference diagram, and evaluates a small set of *pre-declared*
pairwise comparisons with Wilcoxon signed-rank plus Holm correction.

The comparison set is fixed here in the source, before any result is seen,
and deliberately kept to six. That is not modesty: with eight folds the
smallest two-sided p the test can produce is 0.0078, so seven or more
comparisons would push the Holm-corrected floor above 0.05 and make it
arithmetically impossible for any comparison to be declared significant.
"""

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.report import AX, MODEL_LABELS, model_color, new_figure, save_figure, save_table
from src.evaluation.stats import (
    average_ranks,
    friedman,
    nemenyi_critical_difference,
    wilcoxon_pairs,
)

# Declared in advance; each answers a question the thesis actually asks.
PRE_REGISTERED_PAIRS = [
    ("autoencoder", "iforest"),  # the two detectors the proposal centres on
    ("autoencoder", "ocsvm"),  # RQ2, remaining pair
    ("iforest", "ocsvm"),  # RQ2, remaining pair
    ("autoencoder", "logreg"),  # size of the gap to the supervised reference
    ("autoencoder", "pca_recon"),  # does the non-linear encoder earn its cost?
    ("iforest", "ecod"),  # does a tuned method beat a parameter-free one?
]


def critical_difference_diagram(ranks: pd.Series, cd: float, n_folds: int, cfg, fname: str):
    """Average ranks on a line; detectors whose ranks differ by less than the
    critical difference are joined by a bar and are indistinguishable."""
    ranks = ranks.sort_values()
    names = list(ranks.index)
    values = ranks.to_numpy()
    k = len(names)

    fig, ax = new_figure(figsize=(7.4, 0.34 * k + 2.0))
    ax.set_xlim(0.5, k + 0.5)
    ax.set_ylim(0, 1)
    ax.axis("off")

    y_axis = 0.86
    ax.plot([1, k], [y_axis, y_axis], color="#52514e", lw=1.2)
    for tick in range(1, k + 1):
        ax.plot([tick, tick], [y_axis, y_axis + 0.02], color="#52514e", lw=1.0)
        ax.text(tick, y_axis + 0.045, str(tick), ha="center", fontsize=8, color="#52514e")
    ax.text(
        (1 + k) / 2,
        y_axis + 0.11,
        f"{AX['rank']} (1 = më i miri)",
        ha="center",
        fontsize=9.5,
        color="#52514e",
    )

    # Labels alternate left/right of the axis to avoid collisions.
    half = (k + 1) // 2
    for i, (name, val) in enumerate(zip(names, values, strict=True)):
        left = i < half
        row = i if left else k - 1 - i
        y_label = y_axis - 0.10 - 0.055 * row
        x_end = 0.7 if left else k + 0.3
        ax.plot([val, val], [y_axis, y_label], color=model_color(name), lw=1.1)
        ax.plot([val, x_end], [y_label, y_label], color=model_color(name), lw=1.1)
        ax.text(
            x_end + (-0.08 if left else 0.08),
            y_label,
            f"{MODEL_LABELS.get(name, name)} ({val:.2f})",
            ha="right" if left else "left",
            va="center",
            fontsize=8.5,
            color="#0b0b0b",
        )

    # Cliques of statistically indistinguishable detectors.
    y_bar = y_axis - 0.045
    drawn = []
    for i in range(k):
        j = i
        while j + 1 < k and values[j + 1] - values[i] <= cd:
            j += 1
        if j > i and not any(a <= i and j <= b for a, b in drawn):
            drawn.append((i, j))
            ax.plot(
                [values[i] - 0.03, values[j] + 0.03],
                [y_bar, y_bar],
                color="#0b0b0b",
                lw=3.2,
                solid_capstyle="round",
            )
            y_bar -= 0.028

    ax.text(
        1,
        0.03,
        f"CD = {cd:.2f}  (Nemenyi, α=0.05, k={k}, N={n_folds} fold-e)",
        fontsize=8.5,
        color="#898781",
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, fname)


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    per_fold = pd.read_csv(results_dir / "benchmark_per_fold.csv")
    ap_wide = per_fold.pivot(index="fold", columns="model", values="ap")

    unsup = [c for c in ap_wide.columns if c != "logreg"]
    n_folds = ap_wide.shape[0]

    rows = []
    for label, cols in [
        ("të gjithë (14 të pambikëqyrur)", unsup),
        ("katër modelet e propozimit", ["iforest", "autoencoder", "ocsvm", "logreg"]),
    ]:
        sub = ap_wide[cols]
        res = friedman(sub)
        cd = nemenyi_critical_difference(len(cols), n_folds)
        rows.append(
            {
                "grupi": label,
                "k": len(cols),
                "N_folde": n_folds,
                "friedman_chi2": res["statistic"],
                "p_value": res["p_value"],
                "nemenyi_CD": cd,
                "range_i_rangjeve": float(average_ranks(sub).max() - average_ranks(sub).min()),
            }
        )
    omnibus = pd.DataFrame(rows)
    # %.4f would round a p-value of 2e-08 to zero on the way to disk.
    save_table(omnibus, results_dir, "significance_omnibus", float_fmt="%.6g")
    print(omnibus.to_string(index=False))

    critical_difference_diagram(
        average_ranks(ap_wide[unsup]),
        nemenyi_critical_difference(len(unsup), n_folds),
        n_folds,
        cfg,
        "significance_cd_all",
    )
    core = ["iforest", "autoencoder", "ocsvm", "logreg"]
    critical_difference_diagram(
        average_ranks(ap_wide[core]),
        nemenyi_critical_difference(len(core), n_folds),
        n_folds,
        cfg,
        "significance_cd_core",
    )

    pairs = [
        (a, b) for a, b in PRE_REGISTERED_PAIRS if a in ap_wide.columns and b in ap_wide.columns
    ]
    wilcox = wilcoxon_pairs(ap_wide, pairs)
    wilcox.insert(
        0,
        "krahasimi",
        [
            f"{MODEL_LABELS.get(a, a)} vs {MODEL_LABELS.get(b, b)}"
            for a, b in zip(wilcox["model_a"], wilcox["model_b"], strict=True)
        ],
    )
    save_table(wilcox, results_dir, "significance_wilcoxon", float_fmt="%.5f")
    print(
        "\n"
        + wilcox[
            [
                "krahasimi",
                "mean_diff",
                "wins_a",
                "wins_b",
                "p_value",
                "p_holm",
                "significant_holm_05",
            ]
        ].to_string(index=False)
    )

    avg = average_ranks(ap_wide)
    save_table(
        avg.rename("avg_rank").reset_index().rename(columns={"index": "model"}),
        results_dir,
        "significance_avg_ranks",
        float_fmt="%.3f",
    )
    print("\nrangjet mesatare (AP):")
    print({MODEL_LABELS.get(k, k): round(v, 2) for k, v in avg.items()})

    write_manifest(results_dir, "exp11_significance", cfg.raw)
    if np.isfinite(omnibus["p_value"].iloc[0]) and omnibus["p_value"].iloc[0] < 0.05:
        print("\nFriedman: detektorët NUK janë ekuivalentë (p < 0.05).")
    else:
        print("\nFriedman: nuk refuzohet hipoteza e ekuivalencës.")


if __name__ == "__main__":
    main()

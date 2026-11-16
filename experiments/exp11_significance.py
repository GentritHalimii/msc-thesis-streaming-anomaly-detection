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
from src.evaluation.report import (
    AX,
    CM,
    FULL_WIDTH,
    INK,
    INK_2,
    MODEL_LABELS,
    model_color,
    new_figure,
    save_figure,
    save_table,
)
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
    ("iforest", "logreg"),  # same gap, for the second primary detector
    ("ocsvm", "logreg"),  # same gap, for the additional component
]


def critical_difference_diagram(ranks: pd.Series, cd: float, n_folds: int, cfg, fname: str):
    """Average ranks on a line, in the layout Demšar introduced.

    The better half of the detectors is labelled on the left and the rest on
    the right, each joined to its rank by an elbow. A thick bar joins
    detectors whose ranks differ by less than the critical difference, which
    is drawn to scale above the axis so the reader can compare it with any
    gap by eye.
    """
    ranks = ranks.sort_values()
    names = list(ranks.index)
    values = ranks.to_numpy()
    k = len(names)
    margin = 1.55  # rank units left free on each side for the labels
    height_cm = 2.55 + 0.55 * ((k + 1) // 2 - 1)

    fig, ax = new_figure(figsize=(FULL_WIDTH, height_cm * CM))
    fig.set_layout_engine("none")
    ax.set_position((0, 0, 1, 1))
    ax.set_xlim(1 - margin, k + margin)
    ax.set_ylim(-height_cm, 0)
    ax.axis("off")

    y_axis = -1.0
    ax.plot([1, k], [y_axis, y_axis], color=INK_2, lw=0.9)
    for tick in range(1, k + 1):
        ax.plot([tick, tick], [y_axis, y_axis + 0.12], color=INK_2, lw=0.9)
        ax.text(tick, y_axis + 0.2, str(tick), ha="center", va="bottom", fontsize=10, color=INK_2)
    # The critical difference to scale, starting at rank 1.
    y_cd = -0.32
    ax.plot([1, 1 + cd], [y_cd, y_cd], color=INK, lw=1.0)
    for end in (1, 1 + cd):
        ax.plot([end, end], [y_cd - 0.08, y_cd + 0.08], color=INK, lw=1.0)
    ax.text(1 + cd + 0.06, y_cd, f"CD = {cd:.2f}", ha="left", va="center", fontsize=10, color=INK)

    half = (k + 1) // 2
    for i, (name, val) in enumerate(zip(names, values, strict=True)):
        left = i < half
        row = i if left else k - 1 - i
        y_label = y_axis - 0.75 - 0.55 * row
        x_end = 1 - 0.25 if left else k + 0.25
        color = model_color(name)
        ax.plot([val, val, x_end], [y_axis, y_label, y_label], color=color, lw=1.1)
        ax.text(
            x_end + (-0.06 if left else 0.06),
            y_label,
            f"{MODEL_LABELS.get(name, name)}  {val:.2f}",
            ha="right" if left else "left",
            va="center",
            fontsize=10.2,
            color=INK,
        )

    # Groups of detectors that the test cannot tell apart.
    y_bar = y_axis - 0.3
    drawn = []
    for i in range(k):
        j = i
        while j + 1 < k and values[j + 1] - values[i] <= cd:
            j += 1
        if j > i and not any(a <= i and j <= b for a, b in drawn):
            drawn.append((i, j))
            ax.plot(
                [values[i] - 0.04, values[j] + 0.04],
                [y_bar, y_bar],
                color=INK,
                lw=3.0,
                solid_capstyle="round",
            )
            y_bar -= 0.22
    ax.text(
        (1 + k) / 2,
        -height_cm + 0.06,
        f"{AX['rank']} i AP-së nëpër {n_folds} fold-e (1 = më i miri)",
        ha="center",
        va="bottom",
        fontsize=10,
        color=INK_2,
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
        ("tre detektorët unsupervised", unsup),
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
                "kendall_w": res["kendall_w"],
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
    # Folds won by each side, as one column the table can print.
    wilcox["fitore"] = [f"{a}:{b}" for a, b in zip(wilcox["wins_a"], wilcox["wins_b"], strict=True)]
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

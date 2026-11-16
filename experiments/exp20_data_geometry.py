"""How separable is this problem, before any detector is trained?

Unsupervised detection assumes the positive class stands apart geometrically.
That assumption is testable without fitting anything, and testing it first
changes how every later result should be read: if a large share of the frauds
sit inside dense normal regions, then the modest Average Precision reported in
Chapter 5 is close to a property of the data rather than a failure of the
algorithms.

Everything here is computed on the training window of the chronological split,
so nothing observed in the test blocks informs the description. The same
measures are then recomputed on the test window, which turns the analysis into
a second, model-free view of the drift result.
"""

import argparse

import matplotlib as mpl
import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.data.load import FEATURE_COLUMNS, load_transactions
from src.data.scale import fit_scaler, transform
from src.data.split import chronological_split
from src.evaluation.geometry import (
    fraud_hardness,
    intrinsic_dimension_mle,
    intrinsic_dimension_twonn,
    one_nn_class_agreement,
)
from src.evaluation.manifest import write_manifest
from src.evaluation.report import (
    BASELINE,
    CLASS_COLORS,
    CM,
    FULL_WIDTH,
    INK_2,
    MUTED,
    legend_above,
    new_figure,
    save_figure,
    save_table,
    value_grid,
)

K_NEIGHBOURS = 10
WINDOW_COLORS = {"trajnim": "#2a78d6", "test": "#eb6834"}
WINDOW_LABELS = {"trajnim": "Dritarja e trajnimit", "test": "Dritarja e testimit"}


def figures(cfg):
    """Both geometry figures, from the distances saved by `main`."""
    results_dir = REPO_ROOT / cfg.results_dir
    saved = np.load(results_dir / "geometry_distances.npz")

    # --- How deep inside normal territory each class sits ----------------
    # Log-spaced bins: the normal distances crowd below 5 while the frauds
    # spread over an order of magnitude, and on a linear axis the normal
    # class collapses into two bars at the left edge. Each bar is the share
    # of its class in the bin; a density would divide by the bin width and
    # shrink the right tail, where log-spaced bins are widest.
    d_norm = saved["distances_normal__trajnim"]
    d_fraud = saved["distances_fraud__trajnim"]
    lo = max(min(d_norm.min(), d_fraud.min()), 1e-2)
    bins = np.logspace(np.log10(lo), np.log10(max(d_norm.max(), d_fraud.max())), 70)
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.4 * CM))
    for values, cls, label in (
        (d_norm, 0, "Transaksione legjitime"),
        (d_fraud, 1, "Mashtrime"),
    ):
        weights = np.full(len(values), 1.0 / len(values))
        ax.hist(
            values,
            bins=bins,
            weights=weights,
            histtype="stepfilled",
            color=CLASS_COLORS[cls],
            alpha=0.35,
            linewidth=0,
        )
        ax.hist(
            values,
            bins=bins,
            weights=weights,
            histtype="step",
            color=CLASS_COLORS[cls],
            linewidth=1.1,
            label=label,
        )
    p95 = float(np.quantile(d_norm, 0.95))
    ax.axvline(p95, color=INK_2, lw=0.9, ls=(0, (4, 2)))
    ax.text(
        p95 * 1.06,
        ax.get_ylim()[1] * 0.93,
        f"95% e legjitimeve\njanë nën {p95:.1f}",
        fontsize=7.5,
        color=INK_2,
        va="top",
    )
    ax.set_xscale("log")
    ax.set_xlabel(f"Distanca mesatare deri te {K_NEIGHBOURS} fqinjët legjitimë më të afërt")
    ax.set_ylabel("Pjesa e klasës")
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(0.05))
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1.0, decimals=0))
    value_grid(ax, "y")
    legend_above(ax)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "geometry_knn_distance")

    # --- How many alerts each fraud costs ---------------------------------
    # The point of this figure is the gap between "far from the normal class"
    # and "cheap to find": the normal class is so large that its own tail
    # occupies the far region several times over.
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.6 * CM))
    for label in ("trajnim", "test"):
        ranks = np.sort(saved[f"fraud_ranks__{label}"])
        caught = np.arange(1, len(ranks) + 1) / len(ranks)
        ax.step(
            np.concatenate([[1.0], ranks]),
            np.concatenate([[0.0], caught]),
            where="post",
            color=WINDOW_COLORS[label],
            linewidth=1.6,
            label=f"{WINDOW_LABELS[label]} ({len(ranks)} mashtrime)",
        )
    for budget in (100, 1000):
        ax.axvline(budget, color=BASELINE, lw=0.9, zorder=1)
        ax.text(
            budget * 1.08,
            0.98,
            f"{budget} alarme",
            fontsize=7.5,
            color=MUTED,
            va="top",
        )
    ax.set_xscale("log")
    ax.set_xlim(1, None)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Alarme të shqyrtuara, sipas distancës nga klasa legjitime")
    ax.set_ylabel("Mashtrime të kapura")
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1.0))
    value_grid(ax, "both")
    legend_above(ax)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "geometry_cost_to_catch")


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split = chronological_split(df, cfg.split.train_fraction)

    scaler = fit_scaler(split.train_full)
    windows = {"trajnim": split.train_full, "test": split.test}

    rows, hardness_by_window = [], {}
    for label, frame in windows.items():
        X = transform(scaler, frame)
        y = frame["Class"].to_numpy()
        X_normal, X_fraud = X[y == 0], X[y == 1]

        hardness = fraud_hardness(X_normal, X_fraud, k=K_NEIGHBOURS, seed=cfg.seed)
        hardness_by_window[label] = hardness
        agreement = one_nn_class_agreement(X, y, seed=cfg.seed)

        rows.append(
            {
                "dritarja": label,
                "rreshta": len(frame),
                "mashtrime": int(y.sum()),
                "id_mle_normale": intrinsic_dimension_mle(X_normal, seed=cfg.seed),
                "id_twonn_normale": intrinsic_dimension_twonn(X_normal, seed=cfg.seed),
                "id_mle_mashtrime": intrinsic_dimension_mle(
                    X_fraud, k=min(20, len(X_fraud) - 2), seed=cfg.seed
                ),
                "knn_distanca_normale": hardness["median_knn_distance_normal"],
                "knn_distanca_mashtrime": hardness["median_knn_distance_fraud"],
                "raporti_distancave": (
                    hardness["median_knn_distance_fraud"] / hardness["median_knn_distance_normal"]
                ),
                "ap_vetem_distance": hardness["ap_distance_only"],
                "rangu_median_i_mashtrimit": hardness["median_fraud_rank"],
                "mashtrime_ne_top100": hardness["frauds_within_top_100"],
                "mashtrime_ne_top1000": hardness["frauds_within_top_1000"],
                "1nn_agreement_normale": agreement["agreement_normal"],
                "1nn_agreement_mashtrime": agreement["agreement_fraud"],
            }
        )

    table = pd.DataFrame(rows)
    save_table(table, results_dir, "geometry_summary", float_fmt="%.4f")
    print(table.to_string(index=False))

    # The per-transaction distances are the raw material of both figures;
    # keeping them means a figure can be redrawn without the neighbour search.
    np.savez_compressed(
        results_dir / "geometry_distances.npz",
        **{
            f"{key}__{label}": np.asarray(hardness_by_window[label][key], dtype=np.float64)
            for label in windows
            for key in ("distances_normal", "distances_fraud", "fraud_ranks")
        },
    )
    figures(cfg)

    # --- Per-feature separability, on the training window only ------------
    X_train = transform(scaler, split.train_full)
    y_train = split.train_full["Class"].to_numpy()
    from sklearn.metrics import roc_auc_score

    per_feature = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "auc": [roc_auc_score(y_train, X_train[:, j]) for j in range(X_train.shape[1])],
        }
    )
    per_feature["fuqia"] = (per_feature["auc"] - 0.5).abs()
    per_feature = per_feature.sort_values("fuqia", ascending=False).reset_index(drop=True)
    per_feature["fuqia_kumulative"] = per_feature["fuqia"].cumsum() / per_feature["fuqia"].sum()
    save_table(per_feature, results_dir, "geometry_feature_power", float_fmt="%.4f")

    top5 = per_feature.head(5)
    share = float(top5["fuqia"].sum() / per_feature["fuqia"].sum())
    train = table.loc[table["dritarja"] == "trajnim"].iloc[0]
    verdict = (
        f"Mashtrimet janë larg klasës legjitime: distanca mesatare deri te "
        f"{K_NEIGHBOURS} fqinjët legjitimë më të afërt është "
        f"{train['raporti_distancave']:.1f} herë më e madhe se ajo e një transaksioni "
        f"tipik legjitim. Megjithatë kjo largësi nuk përkthehet në zbulim të lehtë: "
        f"vetëm distanca jep AP {train['ap_vetem_distance']:.3f}, sepse bishti i vetë "
        f"klasës legjitime e mbush të njëjtin rajon. Mashtrimi median kërkon shqyrtimin e "
        f"rreth {train['rangu_median_i_mashtrimit']:.0f} alarmeve, dhe brenda njëqind "
        f"alarmeve të para arrihen vetëm {int(train['mashtrime_ne_top100'])} nga "
        f"{int(train['mashtrime'])} mashtrime. Dimensioni i brendshëm i klasës legjitime "
        f"është rreth {train['id_twonn_normale']:.1f} nga 29 dimensione nominale, dhe "
        f"pesë veçoritë më informative mbajnë {100 * share:.0f}% të fuqisë totale "
        f"diskriminuese njëvariablëshe."
    )
    (results_dir / "geometry_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp20_data_geometry", cfg.raw)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--figures-only",
        action="store_true",
        help="redraw the figures from the saved distances without the neighbour search",
    )
    args = parser.parse_args()
    figures(load_config()) if args.figures_only else main()

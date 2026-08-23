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
from src.evaluation.report import new_figure, save_figure, save_table

BLUE, RED, GREY = "#2a78d6", "#e34948", "#898781"
K_NEIGHBOURS = 10


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

    # --- Figure: how deep inside normal territory each class sits ---------
    fig, ax = new_figure(figsize=(6.8, 4.2))
    train_h = hardness_by_window["trajnim"]
    bins = np.linspace(0, np.quantile(train_h["distances_fraud"], 0.99), 60)
    ax.hist(
        train_h["distances_normal"],
        bins=bins,
        density=True,
        color=BLUE,
        alpha=0.55,
        label="Transaksione legjitime",
        linewidth=0,
    )
    ax.hist(
        train_h["distances_fraud"],
        bins=bins,
        density=True,
        color=RED,
        alpha=0.65,
        label="Mashtrime",
        linewidth=0,
    )
    ax.axvline(train_h["median_knn_distance_normal"], color=BLUE, lw=1.4, ls="--")
    ax.axvline(train_h["p95_knn_distance_normal"], color=GREY, lw=1.4, ls=":")
    ax.text(
        train_h["p95_knn_distance_normal"],
        ax.get_ylim()[1] * 0.92,
        "  p95 i legjitimeve",
        fontsize=8,
        color=GREY,
    )
    ax.set_xlabel(f"Distanca mesatare deri te {K_NEIGHBOURS} fqinjët legjitimë më të afërt")
    ax.set_ylabel("Densiteti")
    ax.legend()
    save_figure(fig, REPO_ROOT / cfg.results_dir, "geometry_knn_distance")

    # --- Figure: how many alerts each fraud costs -------------------------
    # The point of this figure is the gap between "far from the normal class"
    # and "cheap to find": the normal class is so large that its own tail
    # occupies the far region several times over.
    fig, ax = new_figure(figsize=(6.8, 4.2))
    for label, colour in (("trajnim", BLUE), ("test", RED)):
        ranks = np.sort(hardness_by_window[label]["fraud_ranks"])
        caught = np.arange(1, len(ranks) + 1) / len(ranks)
        ax.step(
            ranks,
            100 * caught,
            where="post",
            color=colour,
            linewidth=2,
            label=f"Dritarja e {label}",
        )
    ax.set_xscale("log")
    ax.set_xlabel("Alarme që duhen shqyrtuar (renditje sipas distancës nga klasa legjitime)")
    ax.set_ylabel("Përqindja e mashtrimeve të kapura")
    ax.set_ylim(0, 100)
    for budget in (100, 1000):
        ax.axvline(budget, color=GREY, lw=1, ls=":")
        ax.text(budget * 1.15, 6, f"{budget} alarme", fontsize=8, color=GREY)
    ax.legend(loc="lower right")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "geometry_cost_to_catch")

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
    main()

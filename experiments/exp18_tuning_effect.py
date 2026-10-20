"""Does hyperparameter tuning survive contact with the test window?

The search in exp9 improves inner-validation Average Precision for every
detector. Inner validation is still drawn from the training period, though,
so the honest question is whether those gains transfer to blocks the search
never saw, or whether the search simply fitted the inner slice.

Comparing default and tuned configurations over the same eight rolling-origin
folds answers that directly, and also checks the more consequential question:
does tuning change which detector wins?
"""

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import load_folds
from src.evaluation.report import (
    AX,
    CM,
    FULL_WIDTH,
    INK_2,
    MODEL_LABELS,
    MUTED,
    legend_above,
    model_color,
    new_figure,
    ordered_models,
    save_figure,
    save_table,
    value_grid,
)
from src.evaluation.stats import wilcoxon_pairs


def ap_matrix(folds) -> pd.DataFrame:
    rows = {}
    for i, f in enumerate(folds):
        rows[i] = {name: average_precision_score(f.y, f.test_scores(name)) for name in f.models}
    return pd.DataFrame(rows).T.sort_index()


def figures(cfg, table: pd.DataFrame, label_to_key: dict, clean: list[int]) -> None:
    # --- Ranking before and after -----------------------------------------
    fig, ax = new_figure(figsize=(FULL_WIDTH, 5.2 * CM))
    order = table.iloc[::-1].reset_index(drop=True)
    for i, row in order.iterrows():
        key = label_to_key[row["Detektori"]]
        color = model_color(key)
        before, after = row["AP_default"], row["AP_i_akorduar"]
        if key != "logreg":
            ax.annotate(
                "",
                xy=(after, i),
                xytext=(before, i),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": color,
                    "lw": 1.4,
                    "shrinkA": 4,
                    "shrinkB": 4,
                    "mutation_scale": 9,
                },
            )
        ax.plot(before, i, "o", color=MUTED, markersize=6, zorder=3)
        ax.plot(
            after,
            i,
            "o",
            color=color,
            markersize=7,
            markeredgecolor="#ffffff",
            markeredgewidth=0.9,
            zorder=4,
        )
        label = f"{before:.3f}" if key == "logreg" else f"{before:.3f} → {after:.3f}"
        ax.annotate(
            label,
            (max(before, after), i),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=7.5,
            color=INK_2,
        )
    ax.set_yticks(range(len(order)), order["Detektori"])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 0.92)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_xlabel(AX["ap"] + ", mesatare mbi 8 fold-e")
    value_grid(ax, "x")
    legend_above(
        ax,
        handles=[
            Line2D([], [], marker="o", color=MUTED, linestyle="", markersize=6),
            Line2D([], [], marker="o", color=INK_2, linestyle="", markersize=7),
        ],
        labels=["Hiperparametrat e parazgjedhur", "Pas akordimit (ngjyra e detektorit)"],
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "tuning_effect")

    # --- Does the gain on the inner slice carry over? ---------------------
    sub = table[table["Detektori"] != MODEL_LABELS["logreg"]].reset_index(drop=True)
    bars = [
        ("delta_inner", "Validimi i brendshëm", "#b9b8ae"),
        ("delta_test", "Blloqet e testimit, 8 fold-e", INK_2),
        ("delta_folde_te_pastra", f"Vetëm fold-et {clean[0]} deri {clean[-1]}", "#2a78d6"),
    ]
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.0 * CM))
    height = 0.24
    for j, (column, label, color) in enumerate(bars):
        y = (len(sub) - 1 - np.arange(len(sub))) + (1 - j) * height
        ax.barh(y, sub[column], height=height * 0.9, color=color, label=label)
        for yy, value in zip(y, sub[column], strict=True):
            ax.annotate(
                f"{value:+.3f}",
                (value, yy),
                xytext=(4 if value >= 0 else -4, 0),
                textcoords="offset points",
                va="center",
                ha="left" if value >= 0 else "right",
                fontsize=7,
                color=INK_2,
            )
    ax.axvline(0, color=INK_2, lw=0.8)
    ax.set_yticks(len(sub) - 1 - np.arange(len(sub)), sub["Detektori"])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(-0.05, 0.36)
    ax.set_xlabel("Ndryshimi i AP-së nga akordimi")
    value_grid(ax, "x")
    legend_above(ax, ncol=3)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "tuning_transfer")


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    tuned_dir = results_dir / "tuned"
    if not (tuned_dir / "folds" / "fold0.npz").exists():
        raise SystemExit("mungojnë folds-at e akorduar; ekzekuto run_protocol --tuned")

    default_ap = ap_matrix(load_folds(results_dir, cfg.protocol.n_folds))
    tuned_ap = ap_matrix(load_folds(tuned_dir, cfg.protocol.n_folds))
    common = [m for m in default_ap.columns if m in tuned_ap.columns]

    inner = pd.read_csv(results_dir / "tuning_summary.csv")
    label_to_key = {v: k for k, v in MODEL_LABELS.items()}
    inner["key"] = inner["model"].map(label_to_key)
    inner = inner.dropna(subset=["key"]).set_index("key")

    # The search tuned on the first 70 per cent of the stream, which contains
    # the test blocks of the early folds. Only folds whose test block starts
    # after that window are untouched by the selection, and the effect is
    # reported on them separately.
    fold_info = pd.read_csv(results_dir / "fold_summary.csv")
    n_rows = int(fold_info["train_rows"].iloc[-1] + fold_info["test_rows"].iloc[-1])
    tuning_end = int(n_rows * cfg.split.train_fraction)
    clean = fold_info.loc[fold_info["train_rows"] >= tuning_end, "fold"].tolist()

    rows = []
    for name in common:
        d, t = default_ap[name], tuned_ap[name]
        rows.append(
            {
                "Detektori": MODEL_LABELS.get(name, name),
                "AP_default": float(d.mean()),
                "AP_i_akorduar": float(t.mean()),
                "delta_test": float(t.mean() - d.mean()),
                "delta_inner": float(inner.loc[name, "improvement"])
                if name in inner.index
                else np.nan,
                "folds_te_permiresuara": int((t.to_numpy() > d.to_numpy()).sum()),
                "delta_folde_te_pastra": float(t.loc[clean].mean() - d.loc[clean].mean()),
                "te_permiresuara_te_pastra": int((t.loc[clean] > d.loc[clean]).sum()),
            }
        )
    table = pd.DataFrame(rows)
    table["key"] = table["Detektori"].map(label_to_key)
    table = table.set_index("key").loc[ordered_models(common)].reset_index(drop=True)
    save_table(table, results_dir, "tuning_effect")
    print(table.to_string(index=False))
    print(f"\nfold-et pas dritares së akordimit: {clean}")

    tuned_only = [m for m in common if m != "logreg" and m in inner.index]
    sub = table[table["Detektori"].map(label_to_key).isin(tuned_only)]
    improved = int((sub["delta_test"] > 0).sum())
    print(f"\nAkordimi përmirëson AP-në e testit për {improved} nga {len(sub)} detektorë.")

    # Paired test over folds, pooled across the tuned detectors.
    paired = pd.DataFrame(
        {
            "default": default_ap[tuned_only].mean(axis=1),
            "tuned": tuned_ap[tuned_only].mean(axis=1),
        }
    )
    wil = wilcoxon_pairs(paired, [("tuned", "default")])
    save_table(wil, results_dir, "tuning_effect_wilcoxon", float_fmt="%.5f")
    print(
        "\n"
        + wil[["model_a", "model_b", "mean_diff", "wins_a", "wins_b", "p_value"]].to_string(
            index=False
        )
    )

    figures(cfg, table, label_to_key, clean)

    order_before = default_ap[tuned_only].mean().sort_values(ascending=False).index.tolist()
    order_after = tuned_ap[tuned_only].mean().sort_values(ascending=False).index.tolist()
    names = lambda keys: ", ".join(MODEL_LABELS.get(k, k) for k in keys)  # noqa: E731
    ranking = (
        f"renditja mbetet e njëjtë ({names(order_after)})"
        if order_before == order_after
        else f"renditja ndryshon nga {names(order_before)} në {names(order_after)}"
    )
    clean_part = "; ".join(
        f"{r['Detektori']} {r['delta_folde_te_pastra']:+.3f} "
        f"({r['te_permiresuara_te_pastra']} nga {len(clean)})"
        for _, r in sub.iterrows()
    )
    verdict = (
        f"Akordimi i hiperparametrave përmirëson AP-në mesatare të testit për {improved} "
        f"nga {len(sub)} detektorë të akorduar, dhe përmirësimi i grumbulluar është i "
        f"qëndrueshëm nëpër fold-e (Wilcoxon i çiftuar, "
        f"{int(wil['wins_a'].iloc[0])}/{len(paired)} fold-e, p = "
        f"{wil['p_value'].iloc[0]:.4f}); {ranking}. Mbi fold-et {clean[0]} deri {clean[-1]}, "
        f"blloqet e testimit të të cilëve nisin pas dritares së akordimit, ndryshimi është: "
        f"{clean_part}."
    )
    (results_dir / "tuning_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp18_tuning_effect", cfg.raw)


if __name__ == "__main__":
    main()

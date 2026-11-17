"""One-Class SVM: what the kernel, the boundary tightness, and the
subsampling compromise actually cost.

This detector carries the one methodological compromise in the whole study
that was forced by computation rather than chosen on principle. An exact
kernel machine cannot be fitted on two hundred thousand rows, so it is trained
on a seeded subsample. That compromise is stated in the methodology, but
stating it is not enough: the size of the loss it causes is measurable, and
this experiment measures it.

Three further questions are answered. Which kernel suits data that is already
a rotation into principal components. How the nu and gamma pair trades false
alarms against missed frauds. And how the support-vector count, which is what
sets inference latency, responds to those same settings.
"""

import time

import matplotlib as mpl
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import (
    AX,
    CM,
    FULL_WIDTH,
    INK,
    INK_2,
    annotate_cells,
    model_color,
    new_figure,
    outline_cell,
    save_figure,
    save_table,
    strip_vertical,
    value_grid,
)
from src.evaluation.stats import wilcoxon_pairs
from src.models.build import build_model

KERNELS = ["rbf", "poly", "sigmoid", "linear"]
NUS = [0.001, 0.005, 0.01, 0.05, 0.1, 0.2]
GAMMAS = [0.005, 0.01, 0.05, "scale", 0.5]
SUBSAMPLES = [1000, 2000, 5000, 10000, 20000, 40000, 80000]


def fold_matrices(cfg, df, fold):
    train = df.iloc[: fold.train_end]
    test = df.iloc[fold.test_start : fold.test_end]
    scaler = fit_scaler(train, seed=cfg.seed)
    return (
        transform(scaler, train[train["Class"] == 0]),
        transform(scaler, test),
        test["Class"].to_numpy(),
    )


def run(cfg, folds, df, settings, tag):
    rows = []
    for fold in folds:
        X_norm, X_test, y_test = fold_matrices(cfg, df, fold)
        for setting in settings:
            model = build_model("ocsvm", cfg, setting)
            t0 = time.perf_counter()
            model.fit(X_norm)
            fit_s = time.perf_counter() - t0
            t0 = time.perf_counter()
            scores = model.score(X_test)
            score_s = time.perf_counter() - t0
            rows.append(
                {
                    "study": tag,
                    "fold": fold.index,
                    **{k: str(v) for k, v in setting.items()},
                    "ap": average_precision_score(y_test, scores),
                    "fit_s": fit_s,
                    "score_us_per_tx": score_s / len(X_test) * 1e6,
                    "support_vectors": model.n_support_vectors,
                    "support_fraction": model.support_fraction,
                }
            )
        print(f"  {tag}: fold {fold.index} done", flush=True)
    return rows


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    rows = []
    rows += run(cfg, folds, df, [{"kernel": k} for k in KERNELS], "kerneli")
    rows += run(
        cfg, folds, df, [{"nu": nu, "gamma": g} for nu in NUS for g in GAMMAS], "nu x gamma"
    )
    rows += run(cfg, folds, df, [{"train_subsample": n} for n in SUBSAMPLES], "nën-mostra")

    table = pd.DataFrame(rows)
    save_table(table, results_dir, "ocsvm_studies_per_fold", float_fmt="%.10g")
    summarise(cfg, results_dir, table)


def _as_setting(value) -> str:
    """The setting columns as the fitting loop wrote them.

    `run()` stores every setting with `str()`, so in memory nu is the string
    "0.001". Read back from CSV, pandas parses that column as a float and the
    surface reindex, which matches on strings, produced a table of NaN. This
    normalises both paths to the same key.
    """
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)


def summarise(cfg, results_dir, table):
    """Tables, figures and verdict from the per-fold record.

    Separated from the fitting loop because the kernel study alone costs the
    better part of an hour, and a change to a figure should not.
    """
    table = table.copy()
    for column in ("nu", "gamma"):
        if column in table.columns:
            table[column] = table[column].map(_as_setting)
    # ---- kernels ---------------------------------------------------------
    kernels = (
        table[table["study"] == "kerneli"]
        .groupby("kernel")
        .agg(
            ap_mean=("ap", "mean"),
            ap_std=("ap", "std"),
            fit_s=("fit_s", "mean"),
            us_per_tx=("score_us_per_tx", "mean"),
            support_vectors=("support_vectors", "mean"),
        )
        .reset_index()
        .sort_values("ap_mean", ascending=False)
    )
    save_table(kernels, results_dir, "ocsvm_kernels", float_fmt="%.4f")
    print("\n=== kerneli ===")
    print(kernels.to_string(index=False))

    # ---- nu x gamma surface ---------------------------------------------
    surface = table[table["study"] == "nu x gamma"]
    grid = surface.groupby(["nu", "gamma"])["ap"].mean().unstack()
    grid = grid.reindex([str(n) for n in NUS])[[str(g) for g in GAMMAS]]
    save_table(grid.reset_index(), results_dir, "ocsvm_surface", float_fmt="%.4f")

    _surface_figure(cfg, grid)

    # ---- what the subsampling compromise costs ---------------------------
    learning = (
        table[table["study"] == "nën-mostra"]
        .assign(train_subsample=lambda d: d["train_subsample"].astype(int))
        .groupby("train_subsample")
        .agg(
            ap_mean=("ap", "mean"),
            ap_std=("ap", "std"),
            fit_s=("fit_s", "mean"),
            us_per_tx=("score_us_per_tx", "mean"),
            support_vectors=("support_vectors", "mean"),
        )
        .reset_index()
    )
    save_table(learning, results_dir, "ocsvm_learning_curve", float_fmt="%.4f")
    print("\n=== kurba e të mësuarit ===")
    print(learning.to_string(index=False))

    used = int(cfg.models.ocsvm.train_subsample)
    _learning_figure(cfg, table, learning, used)

    # Equal means can hide a consistent loss in most blocks behind a gain in
    # one. Every subsample size is therefore also compared with the one in use,
    # fold by fold.
    ap_by_size = (
        table[table["study"] == "nën-mostra"]
        .assign(train_subsample=lambda d: d["train_subsample"].astype(int))
        .pivot(index="fold", columns="train_subsample", values="ap")
    )
    paired = wilcoxon_pairs(
        ap_by_size.rename(columns=str), [(str(n), str(used)) for n in SUBSAMPLES if n != used]
    ).drop(columns=["p_holm", "significant_holm_05"])
    paired["median_diff"] = [
        float((ap_by_size[int(a)] - ap_by_size[used]).median()) for a in paired["model_a"]
    ]
    paired = paired.rename(columns={"model_a": "train_subsample", "model_b": "kundrejt"})
    save_table(paired, results_dir, "ocsvm_subsample_paired", float_fmt="%.4f")
    print(paired.to_string(index=False))

    at_used = learning.loc[learning["train_subsample"] == used].iloc[0]
    at_max = learning.iloc[-1]
    best_kernel = kernels.iloc[0]
    best_cell = surface.groupby(["nu", "gamma"])["ap"].mean().idxmax()
    verdict = (
        f"Renditja e kernelëve vë në krye {best_kernel['kernel']} me AP "
        f"{best_kernel['ap_mean']:.4f}. "
        f"Sipërfaqja nu-gamma ka maksimumin te nu={best_cell[0]}, gamma={best_cell[1]}. "
        f"Nën-mostrimi në {used:,} transaksione, i imponuar nga kostoja kuadratike, jep AP "
        f"{at_used['ap_mean']:.4f}, ndërsa {int(at_max['train_subsample']):,} transaksione "
        f"japin {at_max['ap_mean']:.4f}; pra kompromisi kushton "
        f"{at_max['ap_mean'] - at_used['ap_mean']:+.4f} njësi AP, me kohë trajnimi që "
        f"rritet nga {at_used['fit_s']:.1f}s në {at_max['fit_s']:.1f}s dhe kosto të inferencës "
        f"nga {at_used['us_per_tx']:.1f} në {at_max['us_per_tx']:.1f} mikrosekonda për "
        f"transaksion."
    )
    (results_dir / "ocsvm_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp24_ocsvm_deep", cfg.raw)


def _gamma_scale(cfg) -> float:
    """The value scikit-learn substitutes for gamma="scale", 1 / (d · Var X),
    on the training normals of the first fold as the detector sees them."""
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    fold = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)[
        0
    ]
    X_norm, _, _ = fold_matrices(cfg, df, fold)
    return 1.0 / (X_norm.shape[1] * X_norm.var())


def _surface_figure(cfg, grid: pd.DataFrame) -> None:
    """nu x gamma, with "scale" placed where its numeric value falls."""
    scale = _gamma_scale(cfg)
    numeric = {g: (scale if g == "scale" else float(g)) for g in grid.columns}
    columns = sorted(grid.columns, key=numeric.get)
    grid = grid[columns]
    labels = [f"scale\n(≈{scale:.3f})" if g == "scale" else g for g in columns]

    fig, ax = new_figure(figsize=(FULL_WIDTH, 7.0 * CM))
    image = ax.imshow(grid.to_numpy(), cmap="Purples", aspect="auto", origin="lower")
    ax.set_xticks(range(len(columns)), labels)
    ax.set_yticks(range(len(grid.index)), list(grid.index))
    ax.set_xlabel("gamma (gjerësia e kernelit RBF)")
    ax.set_ylabel("nu")
    ax.tick_params(length=0)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.grid(False)
    values = grid.to_numpy()
    annotate_cells(ax, values, image)
    default = (list(grid.index).index("0.05"), columns.index("scale"))
    best = np.unravel_index(np.nanargmax(values), values.shape)
    outline_cell(ax, *default, color=INK, lw=1.2, ls=(0, (2, 1.5)))
    outline_cell(ax, *best, color=INK, lw=1.6)
    bar = fig.colorbar(image, ax=ax, shrink=0.85, pad=0.02)
    bar.set_label(AX["ap"])
    bar.outline.set_visible(False)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ocsvm_surface")


def _learning_figure(cfg, table: pd.DataFrame, learning: pd.DataFrame, used: int) -> None:
    """Quality and the two costs against the training subsample, one panel
    each: the three quantities have different units and cannot share an axis."""
    color = model_color("ocsvm")
    per_fold = table[table["study"] == "nën-mostra"].assign(
        train_subsample=lambda d: d["train_subsample"].astype(int)
    )
    fig, axes = new_figure(ncols=3, figsize=(FULL_WIDTH, 5.6 * CM))
    ax1, ax2, ax3 = axes
    for n, grp in per_fold.groupby("train_subsample"):
        strip_vertical(ax1, n, grp["ap"].to_numpy(), color, jitter=0.0)
    for ax, column, label in (
        (ax1, "ap_mean", "AP (pikat: fold-et)"),
        (ax2, "fit_s", "Trajnimi (s)"),
        (ax3, "us_per_tx", "Inferenca (µs për transaksion)"),
    ):
        ax.plot(
            learning["train_subsample"],
            learning[column],
            color=color,
            linewidth=1.5,
            marker="D",
            markersize=4.5,
            markeredgecolor="#ffffff",
            markeredgewidth=0.7,
            zorder=4,
        )
        ax.axvline(used, color=INK_2, lw=0.8, ls=(0, (3, 2)), zorder=1)
        ax.set_xscale("log")
        ax.set_xticks([1000, 10000, 80000], ["1 000", "10 000", "80 000"])
        ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        ax.set_title(label, loc="left", fontsize=10.5)
        value_grid(ax, "y")
    for ax in (ax1, ax2, ax3):
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    ax1.set_yticks([0.05, 0.1, 0.2, 0.5])
    ax2.set_xlabel("Transaksione normale në trajnim (vija: 20 000, vlera e përdorur)")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ocsvm_learning_curve")


def main_from_saved(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    summarise(cfg, results_dir, pd.read_csv(results_dir / "ocsvm_studies_per_fold.csv"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-saved",
        action="store_true",
        help="rebuild tables, figures and verdict from ocsvm_studies_per_fold.csv",
    )
    args = parser.parse_args()
    main_from_saved() if args.from_saved else main()

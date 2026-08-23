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

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import AX, new_figure, save_figure, save_table
from src.models.build import build_model

KERNELS = ["rbf", "poly", "sigmoid", "linear"]
NUS = [0.001, 0.005, 0.01, 0.05, 0.1, 0.2]
GAMMAS = [0.005, 0.01, 0.05, "scale", 0.5]
SUBSAMPLES = [1000, 2000, 5000, 10000, 20000, 40000, 80000]
VIOLET, GREY = "#4a3aa7", "#898781"


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
    save_table(table, results_dir, "ocsvm_studies_per_fold", float_fmt="%.5f")

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

    fig, ax = new_figure(figsize=(6.4, 4.0))
    im = ax.imshow(grid.to_numpy(), cmap="Purples", aspect="auto", origin="lower")
    ax.set_xticks(range(len(grid.columns)), list(grid.columns))
    ax.set_yticks(range(len(grid.index)), list(grid.index))
    ax.set_xlabel("gamma")
    ax.set_ylabel("nu")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            value = grid.iat[i, j]
            ax.text(
                j,
                i,
                f"{value:.3f}",
                ha="center",
                va="center",
                fontsize=7.5,
                color="#ffffff" if value > np.nanmean(grid.to_numpy()) else "#0b0b0b",
            )
    ax.grid(visible=False)
    fig.colorbar(im, ax=ax, shrink=0.85, label=AX["ap"])
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ocsvm_surface")

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

    fig, (ax1, ax2) = new_figure(ncols=2, figsize=(7.4, 3.8))
    ax1.errorbar(
        learning["train_subsample"],
        learning["ap_mean"],
        yerr=learning["ap_std"],
        marker="o",
        markersize=4,
        color=VIOLET,
        capsize=2,
        linewidth=1.6,
    )
    used = int(cfg.models.ocsvm.train_subsample)
    ax1.axvline(used, color=GREY, lw=1.2, ls="--")
    ax1.text(
        used * 1.1,
        learning["ap_mean"].min(),
        "nën-mostra e përdorur",
        fontsize=8,
        color=GREY,
        rotation=90,
        va="bottom",
    )
    ax1.set_xscale("log")
    ax1.set_xlabel("Transaksione normale në trajnim")
    ax1.set_ylabel(AX["ap"])

    ax2.plot(
        learning["train_subsample"],
        learning["fit_s"],
        marker="o",
        markersize=4,
        color=VIOLET,
        linewidth=1.6,
        label="Koha e trajnimit (s)",
    )
    ax2.plot(
        learning["train_subsample"],
        learning["us_per_tx"],
        marker="s",
        markersize=4,
        color="#eb6834",
        linewidth=1.6,
        label="Pikëzimi (µs/tx)",
    )
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Transaksione normale në trajnim")
    ax2.set_ylabel("Kosto")
    ax2.legend(fontsize=8.5)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ocsvm_learning_curve")

    at_used = learning.loc[learning["train_subsample"] == used].iloc[0]
    at_max = learning.iloc[-1]
    best_kernel = kernels.iloc[0]
    best_cell = surface.groupby(["nu", "gamma"])["ap"].mean().idxmax()
    verdict = (
        f"Kerneli RBF nuk është zgjedhja më e mirë automatikisht: renditja e kernelëve jep "
        f"{best_kernel['kernel']} në krye me AP {best_kernel['ap_mean']:.4f}. "
        f"Sipërfaqja nu-gamma ka maksimumin te nu={best_cell[0]}, gamma={best_cell[1]}. "
        f"Nën-mostrimi në {used:,} transaksione, i imponuar nga kostoja kuadratike, jep AP "
        f"{at_used['ap_mean']:.4f}, ndërsa {int(at_max['train_subsample']):,} transaksione "
        f"japin {at_max['ap_mean']:.4f}; pra kompromisi kushton "
        f"{at_max['ap_mean'] - at_used['ap_mean']:+.4f} njësi AP, me kohë trajnimi që "
        f"rritet nga {at_used['fit_s']:.1f}s në {at_max['fit_s']:.1f}s dhe kosto pikëzimi "
        f"nga {at_used['us_per_tx']:.1f} në {at_max['us_per_tx']:.1f} mikrosekonda për "
        f"transaksion."
    )
    (results_dir / "ocsvm_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp24_ocsvm_deep", cfg.raw)


if __name__ == "__main__":
    main()

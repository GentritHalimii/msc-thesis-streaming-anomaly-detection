"""The Autoencoder design space, explored one lever at a time.

The proposal names the Autoencoder as a primary detector, so it deserves more
than a single configuration and an ablation on two knobs. Six studies are run
over the full rolling-origin protocol:

* the architecture surface over latent dimension and hidden width, read
  against the intrinsic dimension of the normal class measured independently
  in the geometry study;
* encoder depth at fixed compression, which separates "how much is compressed"
  from "how the compression is reached";
* the training objective, where the score is always squared error so that the
  objective is the only thing that changes;
* three regularisers that pull in different directions: weight decay, dropout,
  and input corruption for a denoising variant;
* training length, which distinguishes an under-trained model from one that
  has started to reconstruct the anomalies too;
* a linear PCA reconstruction at matched rank, which is the floor the
  non-linear encoder has to clear to justify itself.
"""

import argparse

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import AX, new_figure, save_figure, save_table
from src.models.autoencoder import AutoencoderModel
from src.models.build import build_model

LATENT_DIMS = [2, 4, 6, 8, 12, 16, 20]
HIDDEN_DIMS = [16, 32]
DEPTHS = [1, 2, 3]
LOSSES = ["mse", "mae", "huber"]
DROPOUTS = [0.0, 0.1, 0.2, 0.3]
WEIGHT_DECAYS = [0.0, 1e-6, 1e-4, 1e-2]
NOISE_LEVELS = [0.0, 0.1, 0.25, 0.5]
EPOCH_COUNTS = [5, 10, 20, 40, 60]
GREEN, GREY = "#1baf7a", "#898781"


def fold_matrices(cfg, df, fold):
    train = df.iloc[: fold.train_end]
    test = df.iloc[fold.test_start : fold.test_end]
    scaler = fit_scaler(train, seed=cfg.seed)
    return (
        transform(scaler, train[train["Class"] == 0]),
        transform(scaler, test),
        test["Class"].to_numpy(),
    )


def evaluate(cfg, folds, df, study: str, settings: list[dict]) -> list[dict]:
    rows = []
    for fold in folds:
        X_norm, X_test, y_test = fold_matrices(cfg, df, fold)
        for setting in settings:
            model = build_model("autoencoder", cfg, setting)
            model.fit(X_norm)
            rows.append(
                {
                    "study": study,
                    "fold": fold.index,
                    **setting,
                    "ap": average_precision_score(y_test, model.score(X_test)),
                    "final_train_loss": model.history[-1] if model.history else np.nan,
                }
            )
        print(f"  {study}: fold {fold.index} done", flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folds", nargs="*", type=int, default=None)
    args = parser.parse_args()

    cfg = load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    all_folds = rolling_origin_folds(
        len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction
    )
    folds = all_folds if args.folds is None else [all_folds[i] for i in args.folds]

    rows = []
    rows += evaluate(
        cfg,
        folds,
        df,
        "arkitektura",
        [
            {"latent_dim": ld, "hidden_dim": hd}
            for hd in HIDDEN_DIMS
            for ld in LATENT_DIMS
            if ld < hd
        ],
    )
    rows += evaluate(
        cfg,
        folds,
        df,
        "thellësia",
        [{"depth": d, "hidden_dim": 32, "latent_dim": 8} for d in DEPTHS],
    )
    rows += evaluate(cfg, folds, df, "funksioni i humbjes", [{"loss": loss} for loss in LOSSES])
    rows += evaluate(cfg, folds, df, "dropout", [{"dropout": v} for v in DROPOUTS])
    rows += evaluate(cfg, folds, df, "weight decay", [{"weight_decay": v} for v in WEIGHT_DECAYS])
    rows += evaluate(cfg, folds, df, "denoising", [{"noise_std": v} for v in NOISE_LEVELS])
    rows += evaluate(cfg, folds, df, "epoka", [{"epochs": e} for e in EPOCH_COUNTS])

    # Linear floor: PCA reconstruction at the same rank as the latent layer.
    pca_rows = []
    for fold in folds:
        X_norm, X_test, y_test = fold_matrices(cfg, df, fold)
        for k in LATENT_DIMS:
            model = build_model("pca_recon", cfg, {"n_components": k})
            model.fit(X_norm)
            pca_rows.append(
                {
                    "study": "PCA lineare",
                    "fold": fold.index,
                    "latent_dim": k,
                    "ap": average_precision_score(y_test, model.score(X_test)),
                }
            )
    rows += pca_rows

    table = pd.DataFrame(rows)
    save_table(table, results_dir, "autoencoder_studies_per_fold", float_fmt="%.5f")

    # ---- summaries -------------------------------------------------------
    summaries = {}
    for study, group in table.groupby("study"):
        keys = [
            c
            for c in group.columns
            if c not in ("study", "fold", "ap", "final_train_loss") and group[c].notna().any()
        ]
        summaries[study] = (
            group.groupby(keys)["ap"]
            .agg(ap_mean="mean", ap_std="std", n="count")
            .reset_index()
            .sort_values("ap_mean", ascending=False)
        )
        print(f"\n=== {study} ===")
        print(summaries[study].head(8).to_string(index=False))

    flat = pd.concat([s.assign(study=name) for name, s in summaries.items()], ignore_index=True)
    save_table(flat, results_dir, "autoencoder_studies", float_fmt="%.4f")

    # ---- figure: architecture surface -----------------------------------
    arch = table[table["study"] == "arkitektura"]
    grid = arch.groupby(["hidden_dim", "latent_dim"])["ap"].mean().unstack()
    fig, ax = new_figure(figsize=(6.6, 3.4))
    im = ax.imshow(grid.to_numpy(), cmap="Greens", aspect="auto", origin="lower")
    ax.set_xticks(range(len(grid.columns)), [str(c) for c in grid.columns])
    ax.set_yticks(range(len(grid.index)), [str(i) for i in grid.index])
    ax.set_xlabel(AX["latent"])
    ax.set_ylabel("hidden_dim")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            value = grid.iat[i, j]
            if np.isfinite(value):
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
    save_figure(fig, REPO_ROOT / cfg.results_dir, "autoencoder_architecture")

    # ---- figure: non-linear encoder against the linear floor -------------
    fig, ax = new_figure(figsize=(6.6, 4.0))
    ae_curve = arch[arch["hidden_dim"] == 16].groupby("latent_dim")["ap"].agg(["mean", "std"])
    pca_curve = (
        table[table["study"] == "PCA lineare"].groupby("latent_dim")["ap"].agg(["mean", "std"])
    )
    ax.errorbar(
        ae_curve.index,
        ae_curve["mean"],
        yerr=ae_curve["std"],
        marker="o",
        markersize=4,
        color=GREEN,
        capsize=2,
        label="Autoencoder (jolinear)",
    )
    ax.errorbar(
        pca_curve.index,
        pca_curve["mean"],
        yerr=pca_curve["std"],
        marker="s",
        markersize=4,
        color="#008300",
        linestyle=":",
        capsize=2,
        label="PCA lineare (ablacion)",
    )
    intrinsic = _intrinsic_dimension(results_dir)
    if intrinsic is not None:
        ax.axvline(intrinsic, color=GREY, lw=1.2, ls="--")
        ax.text(
            intrinsic * 1.04,
            ax.get_ylim()[1] * 0.35,
            f"dimensioni i brendshëm ≈ {intrinsic:.1f}",
            fontsize=8,
            color=GREY,
            rotation=90,
            va="bottom",
        )
    ax.set_xlabel(AX["latent"])
    ax.set_ylabel(AX["ap"])
    ax.legend()
    save_figure(fig, REPO_ROOT / cfg.results_dir, "autoencoder_vs_linear")

    # ---- figure: training dynamics --------------------------------------
    X_norm, X_test, y_test = fold_matrices(cfg, df, folds[-1])
    long_run = AutoencoderModel(epochs=max(EPOCH_COUNTS), seed=cfg.seed).fit(X_norm)
    epochs_tab = table[table["study"] == "epoka"].groupby("epochs")["ap"].agg(["mean", "std"])
    fig, ax1 = new_figure(figsize=(6.8, 4.0))
    ax1.plot(
        range(1, len(long_run.history) + 1),
        long_run.history,
        color=GREY,
        linewidth=1.6,
        label="Humbja e trajnimit",
    )
    ax1.set_xlabel(AX["epochs"])
    ax1.set_ylabel("Humbja e rindërtimit (trajnim)")
    ax2 = ax1.twinx()
    ax2.errorbar(
        epochs_tab.index,
        epochs_tab["mean"],
        yerr=epochs_tab["std"],
        marker="o",
        markersize=5,
        color=GREEN,
        capsize=2,
        label=AX["ap"],
    )
    ax2.set_ylabel(AX["ap"] + " në blloqet e testimit")
    ax2.grid(visible=False)
    lines = ax1.get_lines() + ax2.get_lines()[:1]
    ax1.legend(lines, [line.get_label() for line in lines], loc="center right")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "autoencoder_training")

    _write_verdict(results_dir, summaries, arch, table)
    write_manifest(results_dir, "exp23_autoencoder_deep", cfg.raw)


def _intrinsic_dimension(results_dir):
    path = results_dir / "geometry_summary.csv"
    if not path.exists():
        return None
    geometry = pd.read_csv(path)
    row = geometry[geometry["dritarja"] == "trajnim"]
    return float(row["id_twonn_normale"].iloc[0]) if len(row) else None


def _write_verdict(results_dir, summaries, arch, table):
    best_arch = summaries["arkitektura"].iloc[0]
    best_loss = summaries["funksioni i humbjes"].iloc[0]
    best_depth = summaries["thellësia"].iloc[0]
    ae_best = arch.groupby("latent_dim")["ap"].mean().max()
    pca_best = table[table["study"] == "PCA lineare"].groupby("latent_dim")["ap"].mean().max()
    lines = [
        f"Arkitektura më e mirë: latent_dim={int(best_arch['latent_dim'])}, "
        f"hidden_dim={int(best_arch['hidden_dim'])} me AP {best_arch['ap_mean']:.4f}.",
        f"Thellësia optimale e enkoderit është {int(best_depth['depth'])} shtresë, "
        f"pra shtimi i shtresave nuk ndihmon në këtë dataset.",
        f"Funksioni i humbjes më i mirë është {best_loss['loss']} (AP {best_loss['ap_mean']:.4f}).",
        f"Enkoderi jolinear arrin {ae_best:.4f} kundrejt {pca_best:.4f} të projeksionit "
        f"linear me rang të njëjtë, pra diferenca prej {ae_best - pca_best:+.4f} njësi AP "
        f"është ajo që paguan jolineariteti.",
    ]
    for name in ("dropout", "weight decay", "denoising"):
        best = summaries[name].iloc[0]
        column = [c for c in best.index if c not in ("ap_mean", "ap_std", "n", "study")][0]
        lines.append(
            f"Regullarizimi '{name}': vlera më e mirë {column}={best[column]} "
            f"(AP {best['ap_mean']:.4f})."
        )
    (results_dir / "autoencoder_verdict.txt").write_text("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()

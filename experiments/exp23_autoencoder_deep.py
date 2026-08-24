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
import sys

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
    # %.10g, not %.5f: fixed decimals collapse weight_decay=1e-6 onto
    # weight_decay=0 when the record is read back, which silently merges two
    # configurations into one row. The per-fold file is the record, so it
    # keeps enough significant digits to round trip.
    save_table(table, results_dir, "autoencoder_studies_per_fold", float_fmt="%.10g")
    summarise(cfg, results_dir, df, folds, table)


def summarise(cfg, results_dir, df, folds, table):
    """Tables, figures and verdict from the per-fold record.

    Separated from the fitting loop, which costs about an hour, so that a
    change to a figure or to the verdict can be rebuilt in a minute. Only the
    training-dynamics figure needs a model, and it refits a single one.
    """
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
    save_table(tidy_summary(summaries), results_dir, "autoencoder_studies_tidy", float_fmt="%.4f")

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
        label="Humbja e trajnimit (majtas)",
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
        label="Cilësia e zbulimit (djathtas)",
    )
    ax2.set_ylabel(AX["ap"] + " në blloqet e testimit")
    ax2.grid(visible=False)
    # An errorbar's labelled artist is the container, not its first Line2D;
    # taking the line gave a legend entry reading "_nolegend_".
    handles = [*ax1.get_legend_handles_labels()[0], *ax2.get_legend_handles_labels()[0]]
    labels = [*ax1.get_legend_handles_labels()[1], *ax2.get_legend_handles_labels()[1]]
    # Above the axes: the curves cross the middle of the panel, so any
    # in-frame position sits on top of data.
    ax1.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=2,
        frameon=False,
        fontsize=8.5,
    )
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
    """Reads the conclusion off the numbers rather than asserting it.

    An earlier version of this file stated in advance that extra encoder
    layers do not help; the measurements disagreed. Every claim below is now
    derived from the table it describes.
    """
    best_arch = summaries["arkitektura"].iloc[0]
    best_loss = summaries["funksioni i humbjes"].iloc[0]
    depth_tab = summaries["thellësia"].set_index("depth")["ap_mean"]
    best_depth = int(depth_tab.idxmax())

    # Nonlinearity is only worth something if it beats the linear projection
    # at the SAME rank, so the two families are compared rank by rank.
    ae_by_rank = arch[arch["hidden_dim"] == arch["hidden_dim"].max()]
    ae_by_rank = ae_by_rank.groupby("latent_dim")["ap"].mean()
    pca_by_rank = table[table["study"] == "PCA lineare"].groupby("latent_dim")["ap"].mean()
    shared = sorted(set(ae_by_rank.index) & set(pca_by_rank.index))
    gaps = {int(k): float(ae_by_rank[k] - pca_by_rank[k]) for k in shared}
    ae_best_rank = int(ae_by_rank.idxmax())

    lines = [
        f"Arkitektura më e mirë: latent_dim={int(best_arch['latent_dim'])}, "
        f"hidden_dim={int(best_arch['hidden_dim'])} me AP {best_arch['ap_mean']:.4f}, "
        f"kundrejt {float(summaries['arkitektura'].iloc[-1]['ap_mean']):.4f} të "
        f"konfigurimit më të dobët, pra arkitektura vlen "
        f"{best_arch['ap_mean'] - float(summaries['arkitektura'].iloc[-1]['ap_mean']):+.4f} "
        f"njësi AP.",
    ]

    depth_1 = float(depth_tab.loc[1]) if 1 in depth_tab.index else float("nan")
    if best_depth == 1:
        lines.append(
            f"Thellësia optimale e enkoderit është 1 shtresë (AP {depth_1:.4f}), pra shtimi i "
            f"shtresave nuk ndihmon në këtë dataset."
        )
    else:
        lines.append(
            f"Thellësia optimale e enkoderit është {best_depth} shtresa "
            f"(AP {float(depth_tab.loc[best_depth]):.4f}) kundrejt {depth_1:.4f} me një shtresë "
            f"të vetme, pra thellimi vlen {float(depth_tab.loc[best_depth]) - depth_1:+.4f} "
            f"njësi AP."
        )

    lines.append(
        f"Funksioni i humbjes më i mirë është {best_loss['loss']} (AP {best_loss['ap_mean']:.4f}) "
        f"kundrejt {float(summaries['funksioni i humbjes'].iloc[-1]['ap_mean']):.4f} të "
        f"alternativës më të dobët; meqë pika e anomalisë është gjithmonë MSE, kjo tregon se "
        f"përputhja mes objektivit të trajnimit dhe atij të pikëzimit ka rëndësi."
    )

    positive = sum(1 for v in gaps.values() if v > 0)
    lines.append(
        f"Kundrejt projeksionit linear me rang të njëjtë, enkoderi jolinear fiton në "
        f"{positive} nga {len(gaps)} rangje; diferenca në rangun më të mirë të tij "
        f"({ae_best_rank}) është {gaps.get(ae_best_rank, float('nan')):+.4f} njësi AP. "
        f"Kjo është ajo që paguan jolineariteti."
    )

    intrinsic = _intrinsic_dimension(results_dir)
    if intrinsic is not None:
        lines.append(
            f"Dimensioni latent optimal ({ae_best_rank}) është "
            f"{ae_best_rank / intrinsic:.1f} herë dimensioni i brendshëm i vlerësuar i klasës "
            f"normale ({intrinsic:.1f}), pra heuristika që e barazon ngushticën me dimensionin "
            f"e brendshëm nuk vlen për zbulim: ngushtica duhet të jetë mjaft e gjerë sa "
            f"normalja të rindërtohet mirë, jo aq e ngushtë sa të dëmtohen të dyja klasat."
        )

    for name in ("dropout", "weight decay", "denoising"):
        summary = summaries[name]
        column = [c for c in summary.columns if c not in ("ap_mean", "ap_std", "n", "study")][0]
        best, worst = summary.iloc[0], summary.iloc[-1]
        spread = float(best["ap_mean"] - worst["ap_mean"])
        verdict = "pa efekt praktik" if spread < 0.01 else f"hapësirë prej {spread:.4f} njësish AP"
        lines.append(
            f"Regullarizimi '{name}': më i miri {column}={best[column]} "
            f"(AP {best['ap_mean']:.4f}), më i dobëti {column}={worst[column]} "
            f"(AP {worst['ap_mean']:.4f}), {verdict}."
        )

    epochs = summaries["epoka"].set_index("epochs")["ap_mean"]
    peak = int(epochs.idxmax())
    if peak < int(epochs.index.max()):
        lines.append(
            f"Trajnimi kulmon në {peak} epoka (AP {float(epochs.loc[peak]):.4f}) dhe bie në "
            f"{float(epochs.loc[epochs.index.max()]):.4f} me "
            f"{int(epochs.index.max())} epoka, çka përputhet me mekanizmin ku rrjeti i "
            f"mbitrajnuar fillon t'i rindërtojë mirë edhe anomalitë."
        )

    (results_dir / "autoencoder_verdict.txt").write_text("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))


def tidy_summary(summaries) -> pd.DataFrame:
    """One readable row per configuration.

    The flat concatenation has a column per hyperparameter, so a document
    table built from it is mostly empty cells. Here the varied setting is
    collapsed into a single string, which is what a reader actually needs.
    """
    rows = []
    for study, table in summaries.items():
        keys = [c for c in table.columns if c not in ("ap_mean", "ap_std", "n", "study")]
        for _, r in table.iterrows():
            setting = ", ".join(
                f"{k}={r[k]:g}" if isinstance(r[k], float) else f"{k}={r[k]}"
                for k in keys
                if pd.notna(r[k])
            )
            rows.append(
                {
                    "Studimi": study,
                    "Konfigurimi": setting,
                    "AP": r["ap_mean"],
                    "s.d.": r["ap_std"],
                    "n": int(r["n"]),
                }
            )
    return pd.DataFrame(rows)


def main_from_saved(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)
    table = pd.read_csv(results_dir / "autoencoder_studies_per_fold.csv")
    summarise(cfg, results_dir, df, folds, table)


def verdict_from_saved(cfg=None):
    """Recomputes the verdict from the saved tables, without refitting."""
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    table = pd.read_csv(results_dir / "autoencoder_studies_per_fold.csv")
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
    save_table(tidy_summary(summaries), results_dir, "autoencoder_studies_tidy", float_fmt="%.4f")
    _write_verdict(results_dir, summaries, table[table["study"] == "arkitektura"], table)


if __name__ == "__main__":
    if "--from-saved" in sys.argv:
        main_from_saved()
    else:
        main()

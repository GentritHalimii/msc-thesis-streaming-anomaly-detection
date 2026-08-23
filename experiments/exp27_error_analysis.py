"""Which frauds are found, which are missed, and are they the same ones?

Average Precision compresses everything into a scalar, which hides the
question an investigator would ask first: do the detectors disagree about
*which* transactions are suspicious, or do they all find the same easy cases
and miss the same hard ones? The answer decides whether combining them could
ever help and, if not, where the remaining headroom actually is.

The analysis works at the level of individual transactions, at a fixed alert
budget, using the scores already saved by the protocol. It reports the overlap
between the detectors' alert sets, the set of frauds that no unsupervised
detector reaches, and what distinguishes those frauds from the ones that are
found.
"""

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.operational import top_k_mask
from src.evaluation.protocol import load_folds, rolling_origin_folds
from src.evaluation.report import MODEL_LABELS, new_figure, save_figure, save_table
from src.models.build import UNSUPERVISED

BUDGET = 100
BLUE, RED, GREY = "#2a78d6", "#e34948", "#898781"


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    folds = load_folds(results_dir, cfg.protocol.n_folds)
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    geometry_folds = rolling_origin_folds(
        len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction
    )

    detectors = [m for m in UNSUPERVISED if m in folds[0].models]
    caught_records, overlap_rows = [], []

    for i, fs in enumerate(folds):
        y = fs.y
        fraud_idx = np.flatnonzero(y == 1)
        masks = {name: top_k_mask(fs.test_scores(name), BUDGET) for name in [*detectors, "logreg"]}

        for name in detectors:
            for other in detectors:
                if name >= other:
                    continue
                a, b = masks[name], masks[other]
                union = int((a | b).sum())
                overlap_rows.append(
                    {
                        "fold": i,
                        "çifti": f"{MODEL_LABELS[name]} & {MODEL_LABELS[other]}",
                        "alarme_te_perbashketa": int((a & b).sum()),
                        "jaccard": int((a & b).sum()) / union if union else 0.0,
                        "mashtrime_te_perbashketa": int((a & b & (y == 1)).sum()),
                        "vetem_A": int((a & ~b & (y == 1)).sum()),
                        "vetem_B": int((~a & b & (y == 1)).sum()),
                    }
                )

        # Per-fraud record: who caught it, and what does it look like.
        train = df.iloc[: geometry_folds[i].train_end]
        scaler = fit_scaler(train, seed=cfg.seed)
        test_frame = df.iloc[geometry_folds[i].test_start : geometry_folds[i].test_end]
        X_test = transform(scaler, test_frame)
        train_normal = transform(scaler, train[train["Class"] == 0])
        centre = train_normal.mean(axis=0)
        spread = np.where(train_normal.std(axis=0) > 0, train_normal.std(axis=0), 1.0)
        z_norm = np.linalg.norm((X_test - centre) / spread, axis=1)

        for j in fraud_idx:
            caught_by = [name for name in detectors if masks[name][j]]
            caught_records.append(
                {
                    "fold": i,
                    "tx_id": int(fs._z["tx_id_test"][j]),
                    "shuma": float(fs.amount[j]),
                    "norma_z": float(z_norm[j]),
                    "n_detektore": len(caught_by),
                    "kapur_nga": "+".join(MODEL_LABELS[c] for c in caught_by) or "asnjë",
                    "kapur_nga_lr": bool(masks["logreg"][j]),
                    **{f"kapur_{name}": bool(masks[name][j]) for name in detectors},
                }
            )

    caught = pd.DataFrame(caught_records)
    save_table(caught, results_dir, "error_analysis_per_fraud", float_fmt="%.4f")
    overlap = pd.DataFrame(overlap_rows)
    save_table(
        overlap.groupby("çifti").mean(numeric_only=True).reset_index(),
        results_dir,
        "error_analysis_overlap",
        float_fmt="%.3f",
    )

    # --- how many detectors reach each fraud ------------------------------
    coverage = (
        caught.groupby("n_detektore")
        .agg(
            mashtrime=("tx_id", "count"),
            shuma_mesatare=("shuma", "mean"),
            norma_z_mediane=("norma_z", "median"),
        )
        .reset_index()
    )
    coverage["pjesa"] = coverage["mashtrime"] / coverage["mashtrime"].sum()
    save_table(coverage, results_dir, "error_analysis_coverage", float_fmt="%.4f")
    print("=== sa detektorë e arrijnë secilin mashtrim (buxhet 100 alarme) ===")
    print(coverage.to_string(index=False))

    dark = caught[caught["n_detektore"] == 0]
    found = caught[caught["n_detektore"] > 0]
    comparison = pd.DataFrame(
        [
            {
                "grupi": "të kapura nga të paktën një detektor",
                "n": len(found),
                "shuma_mediane": float(found["shuma"].median()) if len(found) else np.nan,
                "norma_z_mediane": float(found["norma_z"].median()) if len(found) else np.nan,
                "kapur_nga_LR": float(found["kapur_nga_lr"].mean()) if len(found) else np.nan,
            },
            {
                "grupi": "të pakapura nga asnjë",
                "n": len(dark),
                "shuma_mediane": float(dark["shuma"].median()) if len(dark) else np.nan,
                "norma_z_mediane": float(dark["norma_z"].median()) if len(dark) else np.nan,
                "kapur_nga_LR": float(dark["kapur_nga_lr"].mean()) if len(dark) else np.nan,
            },
        ]
    )
    save_table(comparison, results_dir, "error_analysis_dark_set", float_fmt="%.4f")
    print("\n=== mashtrimet e arritura kundrejt atyre të paarritshme ===")
    print(comparison.to_string(index=False))

    # --- Figure: coverage and what the missed frauds look like ------------
    fig, (ax1, ax2) = new_figure(ncols=2, figsize=(7.6, 3.8))
    ax1.bar(coverage["n_detektore"], 100 * coverage["pjesa"], color=BLUE, width=0.6)
    for n, share, count in zip(
        coverage["n_detektore"], coverage["pjesa"], coverage["mashtrime"], strict=True
    ):
        ax1.text(n, 100 * share + 1, f"{count}", ha="center", fontsize=8, color="#52514e")
    ax1.set_xlabel("Numri i detektorëve që e arrijnë mashtrimin")
    ax1.set_ylabel("Përqindja e mashtrimeve")
    ax1.set_xticks(coverage["n_detektore"])

    bins = np.linspace(0, np.quantile(caught["norma_z"], 0.98), 30)
    ax2.hist(
        found["norma_z"],
        bins=bins,
        color=BLUE,
        alpha=0.65,
        density=True,
        label="Të kapura",
        linewidth=0,
    )
    ax2.hist(
        dark["norma_z"],
        bins=bins,
        color=RED,
        alpha=0.65,
        density=True,
        label="Të pakapura",
        linewidth=0,
    )
    ax2.set_xlabel("Distanca ‖z‖ nga qendra e transaksioneve legjitime")
    ax2.set_ylabel("Densiteti")
    ax2.legend(fontsize=8.5)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "error_analysis")

    n_total = len(caught)
    share_dark = len(dark) / n_total if n_total else float("nan")
    lr_rescue = float(dark["kapur_nga_lr"].mean()) if len(dark) else float("nan")
    verdict = (
        f"Në buxhetin prej {BUDGET} alarmesh për bllok, nga {n_total} mashtrime gjithsej "
        f"nëpër tetë fold-e, {len(dark)} ({100 * share_dark:.0f}%) nuk arrihen nga asnjë "
        f"prej tre detektorëve unsupervised, ndërsa "
        f"{int(coverage.loc[coverage['n_detektore'] == len(detectors), 'mashtrime'].sum() or 0)} "
        f"arrihen nga të tre njëkohësisht. Mashtrimet e paarritshme kanë distancë mediane "
        f"‖z‖ {comparison.loc[1, 'norma_z_mediane']:.1f} kundrejt "
        f"{comparison.loc[0, 'norma_z_mediane']:.1f} të atyre të kapura, pra ato ndodhen "
        f"më afër popullatës legjitime. Referenca e mbikëqyrur i arrin "
        f"{100 * lr_rescue:.0f}% e tyre brenda të njëjtit buxhet, çka tregon se informacioni "
        f"ekziston në të dhëna por nuk është i formës që një detektor distancash e sheh."
    )
    (results_dir / "error_analysis_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp27_error_analysis", cfg.raw)


if __name__ == "__main__":
    main()

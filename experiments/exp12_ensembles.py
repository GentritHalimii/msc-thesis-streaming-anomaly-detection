"""Does combining detectors help — and if not, why not?

The first study in this project found that a naive z-score average of three
detectors was *worse* than its best member. This experiment takes that
negative result seriously and tests whether it survives better engineering:
scale-free rank normalisation instead of z-scores, robust combiners, a much
larger candidate pool, and members chosen by a search rather than by hand.

Member selection is prequential. The ensemble evaluated on fold i is built
using only folds 0..i-1, so the selection never sees the block it is scored
on. Fold 0 has no history and is therefore reported separately, using the
full pool.
"""

import argparse

import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.evaluation.combination import (
    COMBINERS,
    combine,
    greedy_forward_selection,
    pairwise_rank_correlation,
)
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import load_folds
from src.evaluation.report import AX, MODEL_LABELS, new_figure, save_figure, save_table
from src.models.build import UNSUPERVISED

PROPOSAL_TRIO = ["iforest", "autoencoder", "ocsvm"]


def _contamination(cfg, fold_info, i):
    return (
        float(cfg.contamination)
        if cfg.contamination is not None
        else float(fold_info.loc[fold_info["fold"] == i, "train_fraud_rate"].iloc[0])
    )


def fixed_pool_results(cfg, folds, fold_info, pool, pool_name) -> list[dict]:
    rows = []
    for i, f in enumerate(folds):
        c = _contamination(cfg, fold_info, i)
        for mode in COMBINERS:
            ap = average_precision_score(f.y, combine(f, pool, mode, c))
            rows.append(
                {"fold": i, "pool": pool_name, "combiner": mode, "n_members": len(pool), "ap": ap}
            )
    return rows


def greedy_results(cfg, folds, fold_info, candidates, mode) -> list[dict]:
    rows = []
    for i, f in enumerate(folds):
        c = _contamination(cfg, fold_info, i)
        history = folds[:i]
        if not history:
            members = list(candidates)
            note = "pa histori (fold 0): përdoret i gjithë pool-i"
        else:
            members = greedy_forward_selection(
                history, candidates, mode, max_members=6, contamination=c
            )
            note = "+".join(members)
        ap = average_precision_score(f.y, combine(f, members, mode, c))
        rows.append(
            {
                "fold": i,
                "pool": "greedy",
                "combiner": mode,
                "n_members": len(members),
                "ap": ap,
                "members": note,
            }
        )
    return rows


def main(cfg=None, tuned: bool = False):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    fold_dir = results_dir / "tuned" if tuned else results_dir
    suffix = "_tuned" if tuned else ""
    if tuned and not (fold_dir / "folds" / "fold0.npz").exists():
        raise SystemExit("mungojnë folds-at e akorduar; ekzekuto run_protocol --tuned")

    fold_info = pd.read_csv(results_dir / "fold_summary.csv")
    folds = load_folds(fold_dir, cfg.protocol.n_folds)
    per_fold = (
        pd.read_csv(results_dir / f"benchmark_per_fold{suffix}.csv")
        if (results_dir / f"benchmark_per_fold{suffix}.csv").exists()
        else _per_fold_ap(folds)
    )

    pool_full = [m for m in UNSUPERVISED if m in folds[0].models]
    rows = []
    rows += fixed_pool_results(cfg, folds, fold_info, PROPOSAL_TRIO, "trio i propozimit")
    # With the study narrowed to the three algorithms of the proposal the full
    # unsupervised pool IS the trio, so a second identical row would only
    # pad the table. The branch stays so the code still reports both if the
    # pool is ever widened again.
    if sorted(pool_full) != sorted(PROPOSAL_TRIO):
        rows += fixed_pool_results(
            cfg, folds, fold_info, pool_full, f"të gjithë ({len(pool_full)})"
        )
    rows += greedy_results(cfg, folds, fold_info, pool_full, "rank_avg")
    ens = pd.DataFrame(rows)
    save_table(ens, results_dir, f"ensemble_per_fold{suffix}")

    singles = (
        per_fold[per_fold["model"].isin(pool_full)]
        .groupby("model")["ap"]
        .agg(["mean", "std"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )
    best_single = singles.iloc[0]
    best_single_per_fold = per_fold[per_fold["model"] == best_single["model"]].set_index("fold")[
        "ap"
    ]

    summary = (
        ens.groupby(["pool", "combiner"])["ap"]
        .agg(ap_mean="mean", ap_std="std")
        .reset_index()
        .sort_values("ap_mean", ascending=False)
    )
    summary["vs_best_single"] = summary["ap_mean"] - best_single["mean"]
    wins = []
    for _, r in summary.iterrows():
        sub = ens[(ens["pool"] == r["pool"]) & (ens["combiner"] == r["combiner"])]
        sub = sub.set_index("fold")["ap"]
        wins.append(int((sub > best_single_per_fold.reindex(sub.index)).sum()))
    summary["fold_wins_vs_best_single"] = wins
    summary["n_folds"] = len(folds)
    save_table(summary, results_dir, f"ensemble_summary{suffix}")

    regime = "hiperparametra të akorduar" if tuned else "hiperparametra të parazgjedhur"
    print(
        f"[{regime}] modeli më i mirë individual: "
        f"{MODEL_LABELS.get(best_single['model'])} AP={best_single['mean']:.4f}\n"
    )
    print(summary.to_string(index=False))

    beat = summary[summary["vs_best_single"] > 0]
    if len(beat):
        top = beat.iloc[0]
        verdict = (
            f"POZITIV ({regime}): ansambli '{top['pool']}/{top['combiner']}' e tejkalon "
            f"modelin më të mirë individual ({MODEL_LABELS.get(best_single['model'])}): "
            f"AP {top['ap_mean']:.4f} vs {best_single['mean']:.4f} "
            f"(fiton në {top['fold_wins_vs_best_single']}/{len(folds)} fold-e)"
        )
    else:
        top = summary.iloc[0]
        verdict = (
            f"NEGATIV ({regime}): asnjë variant ansambli nuk e tejkalon modelin më të mirë "
            f"individual ({MODEL_LABELS.get(best_single['model'])}, AP "
            f"{best_single['mean']:.4f}); më i miri është '{top['pool']}/{top['combiner']}' "
            f"me AP {top['ap_mean']:.4f}"
        )
    (results_dir / f"ensemble_verdict{suffix}.txt").write_text(verdict + "\n")
    print("\n" + verdict)

    corr = pairwise_rank_correlation(folds[-1], pool_full)
    corr_df = pd.DataFrame(
        corr,
        index=[MODEL_LABELS.get(m, m) for m in pool_full],
        columns=[MODEL_LABELS.get(m, m) for m in pool_full],
    )
    save_table(
        corr_df.reset_index().rename(columns={"index": "model"}),
        results_dir,
        f"ensemble_rank_correlation{suffix}",
        float_fmt="%.3f",
    )

    if not tuned:
        _figures(cfg, corr, pool_full, ens, best_single, best_single_per_fold)
    write_manifest(results_dir, f"exp12_ensembles{suffix}", cfg.raw)


def _per_fold_ap(folds) -> pd.DataFrame:
    """Fallback per-fold AP table when the benchmark has not been run for this
    fold set (the tuned run reuses the same analysis without re-running it)."""
    from sklearn.metrics import average_precision_score

    rows = []
    for i, f in enumerate(folds):
        for name in f.models:
            rows.append(
                {"fold": i, "model": name, "ap": average_precision_score(f.y, f.test_scores(name))}
            )
    return pd.DataFrame(rows)


def _figures(cfg, corr, pool_full, ens, best_single, best_single_per_fold):
    labels = [MODEL_LABELS.get(m, m) for m in pool_full]
    fig, ax = new_figure(figsize=(6.6, 5.4))
    im = ax.imshow(corr, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(labels)), labels, rotation=55, ha="right", fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    for a in range(len(labels)):
        for b in range(len(labels)):
            ax.text(
                b,
                a,
                f"{corr[a, b]:.2f}",
                ha="center",
                va="center",
                fontsize=6.5,
                color="#ffffff" if corr[a, b] > 0.6 else "#0b0b0b",
            )
    ax.grid(visible=False)
    fig.colorbar(im, ax=ax, shrink=0.75, label="Korrelacioni i Spearman-it i rangjeve")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ensemble_rank_correlation")

    fig, ax = new_figure(figsize=(6.8, 4.2))
    for (pool, comb), grp in ens.groupby(["pool", "combiner"]):
        if comb not in ("rank_avg", "max"):
            continue
        ax.plot(
            grp["fold"],
            grp["ap"],
            marker="o",
            markersize=3.5,
            linewidth=1.4,
            label=f"{pool} / {comb}",
        )
    ax.plot(
        best_single_per_fold.index,
        best_single_per_fold.to_numpy(),
        color="#0b0b0b",
        linewidth=2.2,
        marker="s",
        markersize=4,
        label=f"më i miri individual: {MODEL_LABELS.get(best_single['model'])}",
    )
    ax.set_xlabel(AX["fold"])
    ax.set_ylabel(AX["ap"])
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5))
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ensemble_vs_single")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tuned", action="store_true", help="use the folds produced with tuned hyperparameters"
    )
    main(tuned=parser.parse_args().tuned)

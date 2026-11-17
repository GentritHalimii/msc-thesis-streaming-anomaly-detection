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

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
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
from src.evaluation.report import (
    CM,
    FULL_WIDTH,
    INK,
    INK_2,
    MODEL_LABELS,
    new_figure,
    save_figure,
    save_table,
    strip,
    value_grid,
)
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
    # A readable name for the document; the code names stay for the panel.
    summary.insert(
        0,
        "varianti",
        [
            COMBINER_LABELS.get((pool, comb), f"{pool} / {comb}")
            for pool, comb in zip(summary["pool"], summary["combiner"], strict=True)
        ],
    )
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

    # Rank agreement in every fold, not just the last one: the claim that the
    # members rank transactions alike has to hold across the whole stream.
    # Over all transactions the correlation is dominated by the legitimate
    # ones, while an ensemble is decided at the head of the ranking and on the
    # frauds. Both of those are measured too: the correlation over the frauds
    # alone, and the overlap of the alert lists at the operational budget.
    k = 100
    corr_rows = []
    for i, f in enumerate(folds):
        matrix = pairwise_rank_correlation(f, pool_full)
        frauds = f.y == 1
        scores = {m: f.test_scores(m) for m in pool_full}
        top = {m: set(np.argsort(-scores[m], kind="stable")[:k]) for m in pool_full}
        for a in range(len(pool_full)):
            for b in range(a + 1, len(pool_full)):
                ma, mb = pool_full[a], pool_full[b]
                corr_rows.append(
                    {
                        "fold": i,
                        "model_a": ma,
                        "model_b": mb,
                        "spearman": float(matrix[a, b]),
                        "spearman_frauds": float(
                            spearmanr(scores[ma][frauds], scores[mb][frauds])[0]
                        ),
                        f"jaccard_top{k}": len(top[ma] & top[mb]) / len(top[ma] | top[mb]),
                    }
                )
    corr_per_fold = pd.DataFrame(corr_rows)
    save_table(corr_per_fold, results_dir, f"ensemble_rank_correlation_per_fold{suffix}")
    agreement = (
        corr_per_fold.groupby(["model_a", "model_b"])[
            ["spearman", "spearman_frauds", f"jaccard_top{k}"]
        ]
        .mean()
        .reset_index()
    )
    agreement["model_a"] = agreement["model_a"].map(lambda m: MODEL_LABELS.get(m, m))
    agreement["model_b"] = agreement["model_b"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(agreement, results_dir, f"ensemble_agreement{suffix}", float_fmt="%.3f")
    print(agreement.to_string(index=False))
    mean_corr = corr_per_fold.groupby(["model_a", "model_b"])["spearman"].mean()
    corr = np.eye(len(pool_full))
    for (a, b), value in mean_corr.items():
        i, j = pool_full.index(a), pool_full.index(b)
        corr[i, j] = corr[j, i] = value
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
        _figures(cfg, corr_per_fold, ens, best_single, best_single_per_fold)
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


COMBINER_LABELS = {
    ("greedy", "rank_avg"): "Përzgjedhje lakmitare, mesatare rangjesh",
    ("trio i propozimit", "z_avg"): "Mesatare e z-pikëve",
    ("trio i propozimit", "median"): "Mediana e rangjeve",
    ("trio i propozimit", "rank_avg"): "Mesatare e rangjeve",
    ("trio i propozimit", "max"): "Maksimumi i rangjeve",
    ("trio i propozimit", "vote"): "Votim me shumicë",
}
ENSEMBLE_COLOR = "#e34948"


def _figures(cfg, corr_per_fold, ens, best_single, best_single_per_fold):
    # --- Each ensemble against its best member, fold by fold --------------
    # A paired difference is what the hypothesis is about, so that is what is
    # drawn: a variant helps only if its dots sit right of zero.
    order = (
        ens.groupby(["pool", "combiner"])["ap"].mean().sort_values(ascending=True).index.tolist()
    )
    fig, ax = new_figure(figsize=(FULL_WIDTH, 7.0 * CM))
    for y, key in enumerate(order):
        sub = ens[(ens["pool"] == key[0]) & (ens["combiner"] == key[1])].set_index("fold")["ap"]
        delta = (sub - best_single_per_fold.reindex(sub.index)).to_numpy()
        strip(ax, y, delta, ENSEMBLE_COLOR, jitter=0.1, seed=y)
        ax.plot(
            [delta.mean()],
            [y],
            marker="D",
            markersize=6.5,
            color=ENSEMBLE_COLOR,
            markeredgecolor="#ffffff",
            markeredgewidth=0.9,
            zorder=4,
        )
        # The minus sign of the axis, and a white ground so that the zero
        # line does not run through a label that sits on it.
        ax.annotate(
            f"{delta.mean():+.3f}".replace("-", "\u2212"),
            (delta.mean(), y),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=9.5,
            color=INK_2,
            bbox={"boxstyle": "square,pad=0.1", "facecolor": "#ffffff", "edgecolor": "none"},
            zorder=5,
        )
    ax.axvline(0, color=INK_2, lw=0.9, zorder=1)
    best_name = MODEL_LABELS.get(best_single["model"], best_single["model"])
    ax.set_yticks(
        range(len(order)), [COMBINER_LABELS.get(key, f"{key[0]} / {key[1]}") for key in order]
    )
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(order) - 0.3)
    ax.set_xlabel(f"Diferenca e AP-së ndaj {best_name}-it, për fold")
    value_grid(ax, "x")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ensemble_vs_single")

    # --- How alike the members rank the transactions ----------------------
    pairs = corr_per_fold.groupby(["model_a", "model_b"])["spearman"].mean().sort_values()
    fig, ax = new_figure(figsize=(FULL_WIDTH, 4.8 * CM))
    for y, (pair, mean) in enumerate(pairs.items()):
        values = corr_per_fold[
            (corr_per_fold["model_a"] == pair[0]) & (corr_per_fold["model_b"] == pair[1])
        ]["spearman"].to_numpy()
        strip(ax, y, values, INK_2, jitter=0.1, seed=y)
        ax.plot(
            [mean],
            [y],
            marker="D",
            markersize=6.5,
            color=INK,
            markeredgecolor="#ffffff",
            markeredgewidth=0.9,
            zorder=4,
        )
        ax.annotate(
            f"{mean:.2f}",
            (mean, y),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=9.5,
            color=INK_2,
        )
    ax.set_yticks(
        range(len(pairs)),
        [f"{MODEL_LABELS.get(a, a)} dhe {MODEL_LABELS.get(b, b)}" for a, b in pairs.index],
    )
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(pairs) - 0.3)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Korrelacioni i Spearman-it mes renditjeve, për fold")
    value_grid(ax, "x")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "ensemble_rank_correlation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tuned", action="store_true", help="use the folds produced with tuned hyperparameters"
    )
    main(tuned=parser.parse_args().tuned)

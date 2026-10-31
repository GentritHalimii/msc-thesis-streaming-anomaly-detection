"""Static versus adaptive alerting thresholds under drift.

A threshold frozen at training time fixes a *score*, not a workload. If the
score distribution moves — and the drift analysis shows it does — the number
of alerts per hour moves with it. That is an operational failure mode
independent of detection quality: an investigation team sized for 100 alerts
a block cannot absorb 700, and the alerts it never opens are worthless no
matter how well ranked they were.

This experiment quantifies both sides of the trade: how much steadier the
adaptive rule keeps the alert volume, and what it costs in detection quality.
"""

import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import thresholded_metrics
from src.evaluation.protocol import load_folds
from src.evaluation.report import (
    AX,
    CM,
    FULL_WIDTH,
    GRID,
    INK_2,
    MODEL_LABELS,
    MODEL_MARKERS,
    MUTED,
    fig_legend_above,
    legend_above,
    model_color,
    new_figure,
    ordered_models,
    save_figure,
    save_table,
    value_grid,
)
from src.evaluation.thresholds import adaptive_quantile_thresholds
from src.models.build import ALL_MODELS

MODELS = ["iforest", "autoencoder", "ocsvm", "logreg"]
SUBBLOCKS = 10  # alert-rate stability is measured across these equal slices


def alert_rate_profile(flags: np.ndarray, n_slices: int = SUBBLOCKS) -> np.ndarray:
    return np.array([part.mean() for part in np.array_split(flags, n_slices)])


def figures(cfg, prof: pd.DataFrame, per_fold: pd.DataFrame, fold_info: pd.DataFrame) -> None:
    # --- Workload over time, one panel per unsupervised detector ----------
    # The supervised reference is left out here: its alert rate is the same
    # story told by the table, and pooling it with the detectors would
    # average two groups that move in opposite directions.
    names = [m for m in MODELS if m != "logreg"]
    fig, axes = new_figure(nrows=len(names), sharex=True, figsize=(FULL_WIDTH, 10.0 * CM))
    target = fold_info.set_index("fold")["train_fraud_rate"]
    for ax, name in zip(axes, names, strict=True):
        for mode, color, width in (("statik", MUTED, 1.1), ("adaptiv", model_color(name), 1.5)):
            sub = prof[(prof["model"] == name) & (prof["regjimi"] == mode)]
            sub = sub.sort_values(["fold", "slice"])
            x = sub["fold"] + (sub["slice"] + 0.5) / SUBBLOCKS
            ax.plot(
                x,
                sub["alert_rate"],
                color=color,
                linewidth=width,
                label="Prag statik" if mode == "statik" else "Prag adaptiv",
            )
        for f in target.index:
            ax.plot([f, f + 1], [target[f]] * 2, color=INK_2, lw=0.8, ls=(0, (2, 2)))
            if f > 0:
                ax.axvline(f, color=GRID, lw=0.8, zorder=0)
        ax.set_title(MODEL_LABELS[name], loc="left", fontsize=8.2)
        ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1.0, decimals=1))
        ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(3))
        ax.set_ylim(0, None)
        value_grid(ax, "y")
    axes[-1].set_xticks(np.arange(len(target)) + 0.5, [str(f) for f in target.index])
    axes[-1].tick_params(axis="x", length=0)
    axes[-1].set_xlim(0, len(target))
    axes[-1].set_xlabel("Fold (secili i ndarë në 10 nën-blloqe)")
    axes[len(axes) // 2].set_ylabel("Alarme si pjesë e transaksioneve")
    handles, labels = axes[0].get_legend_handles_labels()
    handles.append(Line2D([], [], color=INK_2, lw=0.8, ls=(0, (2, 2))))
    labels.append("Norma e synuar (norma e mashtrimit në trajnim)")
    fig_legend_above(fig, handles, labels)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "adaptive_alert_rate")

    # --- The trade-off, as a move from one regime to the other -------------
    piv = (
        per_fold.groupby(["model", "regjimi"])
        .agg(cv=("alert_rate_cv", "mean"), f1=("f1", "mean"))
        .reset_index()
        .set_index(["model", "regjimi"])
    )
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.6 * CM))
    for name in ordered_models(per_fold["model"].unique()):
        start, end = piv.loc[(name, "statik")], piv.loc[(name, "adaptiv")]
        color = model_color(name)
        ax.annotate(
            "",
            xy=(end["cv"], end["f1"]),
            xytext=(start["cv"], start["f1"]),
            arrowprops={
                "arrowstyle": "-|>",
                "color": color,
                "lw": 1.3,
                "shrinkA": 5,
                "shrinkB": 5,
                "mutation_scale": 10,
            },
        )
        ax.plot(
            start["cv"],
            start["f1"],
            marker=MODEL_MARKERS[name],
            markersize=7,
            markerfacecolor="#ffffff",
            markeredgecolor=color,
            markeredgewidth=1.3,
            linestyle="none",
        )
        ax.plot(
            end["cv"],
            end["f1"],
            marker=MODEL_MARKERS[name],
            markersize=7,
            color=color,
            markeredgecolor="#ffffff",
            markeredgewidth=0.8,
            linestyle="none",
        )
        ax.annotate(
            MODEL_LABELS[name],
            (start["cv"], start["f1"]),
            xytext=(8, -2),
            textcoords="offset points",
            fontsize=7.5,
            color=INK_2,
            va="center",
        )
    ax.set_xlabel("Paqëndrueshmëria e ngarkesës (CV e normës së alarmeve; më majtas është më mirë)")
    ax.set_ylabel(AX["f1"])
    ax.set_ylim(0, 0.8)
    value_grid(ax, "both")
    legend_above(
        ax,
        handles=[
            Line2D(
                [],
                [],
                marker="o",
                markersize=7,
                markerfacecolor="#ffffff",
                markeredgecolor=INK_2,
                linestyle="none",
            ),
            Line2D([], [], marker="o", markersize=7, color=INK_2, linestyle="none"),
        ],
        labels=["Prag statik", "Prag adaptiv"],
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "adaptive_tradeoff")


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    fold_info = pd.read_csv(results_dir / "fold_summary.csv")
    folds = load_folds(results_dir, cfg.protocol.n_folds)
    at = cfg.kafka.adaptive_threshold

    rows, profiles = [], []
    for i, f in enumerate(folds):
        contamination = (
            float(cfg.contamination)
            if cfg.contamination is not None
            else float(fold_info.loc[fold_info["fold"] == i, "train_fraud_rate"].iloc[0])
        )
        y = f.y
        for name in MODELS:
            if name not in f.models:
                continue
            s = f.test_scores(name)
            static_thr = f.train_threshold(name, contamination)
            adaptive_thr = adaptive_quantile_thresholds(
                s,
                contamination,
                window=at.window,
                refresh_every=at.refresh_every,
                warmup_threshold=static_thr,
            )
            for mode, thr in (("statik", static_thr), ("adaptiv", adaptive_thr)):
                flags = s >= thr
                m = (
                    thresholded_metrics(y, s, thr)
                    if np.isscalar(thr)
                    else {
                        "precision": float(np.sum(flags & (y == 1)) / max(flags.sum(), 1)),
                        "recall": float(np.sum(flags & (y == 1)) / max((y == 1).sum(), 1)),
                        "n_alerts": int(flags.sum()),
                    }
                )
                if "f1" not in m:
                    p, r = m["precision"], m["recall"]
                    m["f1"] = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
                prof = alert_rate_profile(flags)
                rows.append(
                    {
                        "fold": i,
                        "model": name,
                        "regjimi": mode,
                        "alert_rate": float(flags.mean()),
                        "alert_rate_cv": float(prof.std() / prof.mean()) if prof.mean() else np.nan,
                        "alert_rate_max_slice": float(prof.max()),
                        "precision": m["precision"],
                        "recall": m["recall"],
                        "f1": m["f1"],
                        "n_alerts": int(m["n_alerts"]),
                    }
                )
                profiles.append(
                    pd.DataFrame(
                        {
                            "fold": i,
                            "model": name,
                            "regjimi": mode,
                            "slice": np.arange(len(prof)),
                            "alert_rate": prof,
                        }
                    )
                )

    per_fold = pd.DataFrame(rows)
    save_table(per_fold, results_dir, "adaptive_threshold_per_fold", float_fmt="%.5f")

    summary = (
        per_fold.groupby(["model", "regjimi"])
        .agg(
            alert_rate=("alert_rate", "mean"),
            alert_rate_cv=("alert_rate_cv", "mean"),
            worst_slice_rate=("alert_rate_max_slice", "max"),
            precision=("precision", "mean"),
            recall=("recall", "mean"),
            f1=("f1", "mean"),
            alerts_per_block=("n_alerts", "mean"),
        )
        .reset_index()
    )
    summary["model"] = summary["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(summary, results_dir, "adaptive_threshold_summary")
    print(summary.to_string(index=False))

    prof = pd.concat(profiles, ignore_index=True)
    save_table(prof, results_dir, "adaptive_threshold_profiles", float_fmt="%.6f")
    figures(cfg, prof, per_fold, fold_info)

    stat = per_fold[per_fold["regjimi"] == "statik"]
    adap = per_fold[per_fold["regjimi"] == "adaptiv"]
    verdict = (
        f"Pragu adaptiv e ul paqëndrueshmërinë e ngarkesës nga CV="
        f"{stat['alert_rate_cv'].mean():.2f} në CV={adap['alert_rate_cv'].mean():.2f} "
        f"dhe pikun e alarmeve nga {100 * stat['alert_rate_max_slice'].max():.1f}% "
        f"në {100 * adap['alert_rate_max_slice'].max():.1f}% të transaksioneve; "
        f"F1 mesatar {stat['f1'].mean():.4f} -> {adap['f1'].mean():.4f}."
    )

    # The pooled F1 above mixes the three unsupervised detectors with the
    # supervised reference, and the two move in opposite directions. Averaging
    # them hides the result instead of summarising it.
    unsup = [m for m in ALL_MODELS if m != "logreg"]
    su, au = stat[stat["model"].isin(unsup)], adap[adap["model"].isin(unsup)]
    gained = sum(
        adap[adap["model"] == m]["f1"].mean() > stat[stat["model"] == m]["f1"].mean() for m in unsup
    )
    ref_s = stat[stat["model"] == "logreg"]
    ref_a = adap[adap["model"] == "logreg"]
    verdict += (
        f" Kjo mesatare e fsheh gjetjen, sepse dy grupet lëvizin në drejtime të kundërta. "
        f"Për të tre detektorët unsupervised F1 rritet nga {su['f1'].mean():.4f} në "
        f"{au['f1'].mean():.4f}, me përmirësim në {gained} nga {len(unsup)} prej tyre, "
        f"ndërsa për referencën supervised ai bie nga {ref_s['f1'].mean():.4f} në "
        f"{ref_a['f1'].mean():.4f}. Shkaku i rënies së referencës është i lexueshëm te "
        f"numri i alarmeve: ai rritet nga {ref_s['n_alerts'].mean():.0f} në "
        f"{ref_a['n_alerts'].mean():.0f} për bllok, dhe precision-i bie nga "
        f"{ref_s['precision'].mean():.3f} në {ref_a['precision'].mean():.3f}. Pragu statik "
        f"i nxjerrë nga kuantili i trajnimit është tashmë i kalibruar mirë për një model që "
        f"prodhon probabilitete, prandaj zëvendësimi i tij me një kuantil mbi dritare "
        f"rrëshqitëse vetëm sa e detyron modelin të alarmojë më shumë se ç'duhet."
    )
    (results_dir / "adaptive_threshold_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp16_adaptive_threshold", cfg.raw)


if __name__ == "__main__":
    main()

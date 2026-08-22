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

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import thresholded_metrics
from src.evaluation.protocol import load_folds
from src.evaluation.report import AX, MODEL_LABELS, new_figure, save_figure, save_table
from src.evaluation.thresholds import adaptive_quantile_thresholds

MODELS = ["iforest", "autoencoder", "ocsvm", "pca_recon", "ecod"]
SUBBLOCKS = 10  # alert-rate stability is measured across these equal slices


def alert_rate_profile(flags: np.ndarray, n_slices: int = SUBBLOCKS) -> np.ndarray:
    return np.array([part.mean() for part in np.array_split(flags, n_slices)])


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

    # --- Figure: workload stability -------------------------------------
    prof = pd.concat(profiles, ignore_index=True)
    fig, ax = new_figure(figsize=(7.0, 4.2))
    for mode, colour in (("statik", "#e34948"), ("adaptiv", "#2a78d6")):
        sub = prof[prof["regjimi"] == mode]
        grouped = sub.groupby(["fold", "slice"])["alert_rate"].mean().reset_index()
        x = grouped["fold"] + grouped["slice"] / SUBBLOCKS
        ax.plot(x, 100 * grouped["alert_rate"], color=colour, linewidth=1.5, label=f"Prag {mode}")
    ax.set_xlabel(AX["fold"] + " (i ndarë në 10 nën-blloqe)")
    ax.set_ylabel("Alarme si % e transaksioneve")
    ax.set_yscale("log")
    ax.legend()
    save_figure(fig, REPO_ROOT / cfg.results_dir, "adaptive_alert_rate")

    # --- Figure: the trade-off in one view ------------------------------
    fig, ax = new_figure(figsize=(6.2, 4.2))
    piv = (
        per_fold.groupby(["model", "regjimi"])
        .agg(cv=("alert_rate_cv", "mean"), f1=("f1", "mean"))
        .reset_index()
    )
    for mode, marker, colour in (("statik", "s", "#e34948"), ("adaptiv", "o", "#2a78d6")):
        sub = piv[piv["regjimi"] == mode]
        ax.scatter(
            sub["cv"],
            sub["f1"],
            s=52,
            marker=marker,
            color=colour,
            label=f"Prag {mode}",
            alpha=0.85,
            edgecolor="white",
            linewidth=0.8,
        )
        for _, r in sub.iterrows():
            ax.annotate(
                MODEL_LABELS.get(r["model"], r["model"]),
                (r["cv"], r["f1"]),
                fontsize=7.5,
                color="#52514e",
                xytext=(5, 3),
                textcoords="offset points",
            )
    ax.set_xlabel("Paqëndrueshmëria e ngarkesës (CV e normës së alarmeve)")
    ax.set_ylabel(AX["f1"])
    ax.legend()
    save_figure(fig, REPO_ROOT / cfg.results_dir, "adaptive_tradeoff")

    stat = per_fold[per_fold["regjimi"] == "statik"]
    adap = per_fold[per_fold["regjimi"] == "adaptiv"]
    verdict = (
        f"Pragu adaptiv e ul paqëndrueshmërinë e ngarkesës nga CV="
        f"{stat['alert_rate_cv'].mean():.2f} në CV={adap['alert_rate_cv'].mean():.2f} "
        f"dhe pikun e alarmeve nga {100 * stat['alert_rate_max_slice'].max():.1f}% "
        f"në {100 * adap['alert_rate_max_slice'].max():.1f}% të transaksioneve; "
        f"F1 mesatar {stat['f1'].mean():.4f} -> {adap['f1'].mean():.4f}."
    )
    (results_dir / "adaptive_threshold_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp16_adaptive_threshold", cfg.raw)


if __name__ == "__main__":
    main()

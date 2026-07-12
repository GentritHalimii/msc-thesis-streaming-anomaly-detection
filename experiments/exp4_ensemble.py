"""Experiment 4 — ensembles vs the best single model.

Builds score-averaging and majority-voting ensembles from the fitted
unsupervised members, evaluates them offline on the test window, and states
plainly whether they beat the best single unsupervised model. A negative
result is reported as such.

Also saves ensemble artifacts + ensemble training scores so the streaming
consumer can run the ensembles for latency measurement.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve

from src.config import REPO_ROOT, load_config
from src.evaluation.harness import contamination_value, score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import threshold_free_metrics, thresholded_metrics
from src.evaluation.report import (
    MODEL_LABELS,
    model_plot_kwargs,
    new_figure,
    save_figure,
    save_table,
)
from src.evaluation.thresholds import oracle_best_f1_threshold, percentile_threshold
from src.models.build import ALL_MODELS, UNSUPERVISED, artifacts_dir, load_model, model_path
from src.models.ensemble import MAJORITY_THRESHOLD, EnsembleModel


def build_ensembles(cfg, scored, contamination) -> dict[str, EnsembleModel]:
    means = {n: float(scored.train_scores[n].mean()) for n in UNSUPERVISED}
    stds = {n: float(scored.train_scores[n].std()) for n in UNSUPERVISED}
    thresholds = {
        n: percentile_threshold(scored.train_scores[n], contamination) for n in UNSUPERVISED
    }
    members = {n: load_model(n, cfg) for n in UNSUPERVISED}
    return {
        mode: EnsembleModel(
            mode=mode,
            member_names=UNSUPERVISED,
            train_means=means,
            train_stds=stds,
            member_thresholds=thresholds,
            members=members,
        )
        for mode in ("avg", "vote")
    }


def main(cfg=None):
    cfg = cfg or load_config()
    scored = score_test_window(cfg)
    contamination = contamination_value(cfg, scored)
    ensembles = build_ensembles(cfg, scored, contamination)

    # Extend train/test scores with the ensembles (combined from member
    # scores — identical to scoring the raw features, minus double work).
    for ens in ensembles.values():
        member_train = {n: scored.train_scores[n] for n in UNSUPERVISED}
        member_test = {n: scored.test_scores[n] for n in UNSUPERVISED}
        scored.train_scores[ens.name] = ens.combine(member_train)
        scored.test_scores[ens.name] = ens.combine(member_test)
        ens.save(model_path(cfg, ens.name))

    # Persist ensemble train scores so the streaming consumer can threshold.
    np.savez_compressed(artifacts_dir(cfg) / "train_scores.npz", **scored.train_scores)

    rows = []
    for name in [*UNSUPERVISED, "ensemble_avg", "ensemble_vote", "logreg"]:
        scores = scored.test_scores[name]
        thr = (
            MAJORITY_THRESHOLD
            if name == "ensemble_vote"
            else percentile_threshold(scored.train_scores[name], contamination)
        )
        at_thr = thresholded_metrics(scored.y_test, scores, thr)
        at_oracle = thresholded_metrics(
            scored.y_test, scores, oracle_best_f1_threshold(scored.y_test, scores)
        )
        rows.append(
            {
                "model": MODEL_LABELS[name],
                **threshold_free_metrics(scored.y_test, scores),
                "precision_pct": at_thr["precision"],
                "recall_pct": at_thr["recall"],
                "f1_pct": at_thr["f1"],
                "f1_oracle": at_oracle["f1"],
            }
        )
    table = pd.DataFrame(rows)
    save_table(table, REPO_ROOT / cfg.results_dir, "metrics_ensemble")
    print(table.to_string(index=False))

    best_single = max(
        UNSUPERVISED,
        key=lambda n: threshold_free_metrics(scored.y_test, scored.test_scores[n])["ap"],
    )
    ap = {
        n: threshold_free_metrics(scored.y_test, scored.test_scores[n])["ap"]
        for n in [*UNSUPERVISED, "ensemble_avg", "ensemble_vote"]
    }
    best_ens = max(("ensemble_avg", "ensemble_vote"), key=ap.get)
    verdict = (
        f"ensemble improves over best single model: {MODEL_LABELS[best_ens]} "
        f"AP {ap[best_ens]:.4f} > {MODEL_LABELS[best_single]} AP {ap[best_single]:.4f}"
        if ap[best_ens] > ap[best_single]
        else f"NEGATIVE RESULT: no ensemble beats the best single model "
        f"({MODEL_LABELS[best_single]} AP {ap[best_single]:.4f}; best ensemble "
        f"{MODEL_LABELS[best_ens]} AP {ap[best_ens]:.4f})"
    )
    (REPO_ROOT / cfg.results_dir / "ensemble_verdict.txt").write_text(verdict + "\n")
    print(verdict)

    fig, ax = new_figure()
    for name in [*ALL_MODELS, "ensemble_avg", "ensemble_vote"]:
        precision, recall, _ = precision_recall_curve(scored.y_test, scored.test_scores[name])
        kw = model_plot_kwargs(name)
        kw["label"] += (
            f" (AP={threshold_free_metrics(scored.y_test, scored.test_scores[name])['ap']:.3f})"
        )
        ax.plot(recall, precision, **kw)
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="upper right", fontsize=8)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "pr_curves_with_ensembles")

    write_manifest(REPO_ROOT / cfg.results_dir, "exp4_ensemble", cfg.raw)


if __name__ == "__main__":
    main()

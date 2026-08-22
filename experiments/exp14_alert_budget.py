"""What the detector is worth when a real team runs it.

Average Precision integrates over every possible operating point, including
ones no bank would ever staff. This experiment fixes the operating point the
way an operations manager does — "we can investigate k alerts per block" —
and asks how much fraud, and how much money, each detector recovers inside
that budget.
"""

import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.operational import budget_metrics, net_savings
from src.evaluation.protocol import load_folds
from src.evaluation.report import (
    AX,
    MODEL_LABELS,
    family_legend_handles,
    model_color,
    model_linestyle,
    new_figure,
    save_figure,
    save_table,
)


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    folds = load_folds(results_dir, cfg.protocol.n_folds)
    budgets = list(cfg.alert_budgets)
    inv_cost = float(cfg.investigation_cost_eur)

    rows = []
    for i, f in enumerate(folds):
        y, amounts = f.y, f.amount
        for name in f.models:
            s = f.test_scores(name)
            for k in budgets:
                rows.append(
                    {
                        "fold": i,
                        "model": name,
                        **budget_metrics(y, s, amounts, k),
                        **net_savings(y, s, amounts, k, inv_cost),
                    }
                )
    per_fold = pd.DataFrame(rows)
    save_table(per_fold, results_dir, "budget_per_fold", float_fmt="%.4f")

    summary = (
        per_fold.groupby(["model", "budget_k"])
        .agg(
            precision_at_k=("precision_at_k", "mean"),
            recall_at_k=("recall_at_k", "mean"),
            amount_recall_at_k=("amount_recall_at_k", "mean"),
            net_savings_eur=("net_savings_eur", "mean"),
            savings_ratio=("savings_ratio", "mean"),
        )
        .reset_index()
    )
    out = summary.copy()
    out["model"] = out["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(out, results_dir, "budget_summary")

    headline = summary[summary["budget_k"] == 100].sort_values("recall_at_k", ascending=False)
    print("Në buxhetin k=100 alarme për bllok (mesatare mbi fold-et):")
    print(
        headline.assign(model=headline["model"].map(lambda m: MODEL_LABELS.get(m, m))).to_string(
            index=False
        )
    )

    for metric, ylab, fname in [
        ("recall_at_k", AX["recall"] + " brenda buxhetit", "budget_recall"),
        ("amount_recall_at_k", AX["amount_recall"] + " brenda buxhetit", "budget_amount_recall"),
        ("savings_ratio", AX["savings"], "budget_savings"),
    ]:
        fig, ax = new_figure(figsize=(6.8, 4.2))
        for name, grp in summary.groupby("model"):
            grp = grp.sort_values("budget_k")
            ax.plot(
                grp["budget_k"],
                grp[metric],
                color=model_color(name),
                linestyle=model_linestyle(name),
                linewidth=2.0 if name == "logreg" else 1.4,
                marker="o",
                markersize=3,
                alpha=1.0 if name == "logreg" else 0.85,
            )
        ax.set_xscale("log")
        ax.set_xticks(budgets, [str(b) for b in budgets])
        ax.set_xlabel(AX["budget"])
        ax.set_ylabel(ylab)
        if metric == "savings_ratio":
            ax.axhline(0.0, color="#c3c2b7", lw=1)
        ax.legend(
            handles=family_legend_handles(),
            loc="center left",
            bbox_to_anchor=(1.01, 0.5),
            fontsize=8.5,
        )
        save_figure(fig, REPO_ROOT / cfg.results_dir, fname)

    # How many euros does the whole exercise actually save per block?
    best = (
        summary[summary["budget_k"] == 100].sort_values("net_savings_eur", ascending=False).iloc[0]
    )
    total_fraud_eur = float(np.mean([f.amount[f.y == 1].sum() for f in folds]))
    verdict = (
        f"Në k=100: {MODEL_LABELS.get(best['model'], best['model'])} rikuperon mesatarisht "
        f"{best['net_savings_eur']:.0f} EUR neto për bllok testimi, nga "
        f"{total_fraud_eur:.0f} EUR mashtrim total për bllok "
        f"({100 * best['amount_recall_at_k']:.1f}% e vlerës)."
    )
    (results_dir / "budget_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp14_alert_budget", cfg.raw)


if __name__ == "__main__":
    main()

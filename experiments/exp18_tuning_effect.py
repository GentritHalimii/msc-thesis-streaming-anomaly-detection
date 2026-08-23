"""Does hyperparameter tuning survive contact with the test window?

The search in exp9 improved inner-validation Average Precision substantially
for most detectors — for the robust covariance estimator by more than half an
AP point. Inner validation is still drawn from the training period, though,
so the honest question is whether those gains transfer to blocks the search
never saw, or whether the search simply fitted the inner slice.

Comparing default and tuned configurations over the same eight rolling-origin
folds answers that directly, and also checks the more consequential question:
does tuning change which detector wins?
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import load_folds
from src.evaluation.report import AX, MODEL_LABELS, model_color, new_figure, save_figure, save_table
from src.evaluation.stats import wilcoxon_pairs


def ap_matrix(folds) -> pd.DataFrame:
    rows = {}
    for i, f in enumerate(folds):
        rows[i] = {name: average_precision_score(f.y, f.test_scores(name)) for name in f.models}
    return pd.DataFrame(rows).T.sort_index()


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    tuned_dir = results_dir / "tuned"
    if not (tuned_dir / "folds" / "fold0.npz").exists():
        raise SystemExit("mungojnë folds-at e akorduar; ekzekuto run_protocol --tuned")

    default_ap = ap_matrix(load_folds(results_dir, cfg.protocol.n_folds))
    tuned_ap = ap_matrix(load_folds(tuned_dir, cfg.protocol.n_folds))
    common = [m for m in default_ap.columns if m in tuned_ap.columns]

    inner = pd.read_csv(results_dir / "tuning_summary.csv")
    label_to_key = {v: k for k, v in MODEL_LABELS.items()}
    inner["key"] = inner["model"].map(label_to_key)
    inner = inner.dropna(subset=["key"]).set_index("key")

    rows = []
    for name in common:
        d, t = default_ap[name], tuned_ap[name]
        rows.append(
            {
                "Detektori": MODEL_LABELS.get(name, name),
                "AP_default": float(d.mean()),
                "AP_i_akorduar": float(t.mean()),
                "delta_test": float(t.mean() - d.mean()),
                "delta_inner": float(inner.loc[name, "improvement"])
                if name in inner.index
                else np.nan,
                "folds_te_permiresuara": int((t.to_numpy() > d.to_numpy()).sum()),
            }
        )
    table = pd.DataFrame(rows).sort_values("delta_test", ascending=False)
    save_table(table, results_dir, "tuning_effect")
    print(table.to_string(index=False))

    tuned_only = [m for m in common if m != "logreg" and m in inner.index]
    rho_rank, p_rank = spearmanr(default_ap[tuned_only].mean(), tuned_ap[tuned_only].mean())
    sub = table[table["Detektori"].map(label_to_key).isin(tuned_only)]
    rho_transfer, p_transfer = spearmanr(sub["delta_inner"], sub["delta_test"])

    improved = int((sub["delta_test"] > 0).sum())
    print(f"\nAkordimi përmirëson AP-në e testit për {improved} nga {len(sub)} detektorë.")
    print(f"Korrelacioni i renditjeve para/pas akordimit: rho = {rho_rank:.3f} (p = {p_rank:.2g})")
    print(
        f"Korrelacioni mes përmirësimit të brendshëm dhe atij në test: "
        f"rho = {rho_transfer:.3f} (p = {p_transfer:.2g})"
    )

    # Paired test over folds, pooled across the tuned detectors.
    paired = pd.DataFrame(
        {
            "default": default_ap[tuned_only].mean(axis=1),
            "tuned": tuned_ap[tuned_only].mean(axis=1),
        }
    )
    wil = wilcoxon_pairs(paired, [("tuned", "default")])
    save_table(wil, results_dir, "tuning_effect_wilcoxon", float_fmt="%.5f")
    print(
        "\n"
        + wil[["model_a", "model_b", "mean_diff", "wins_a", "wins_b", "p_value"]].to_string(
            index=False
        )
    )

    # --- Figure: does inner-validation gain predict test gain? ------------
    fig, ax = new_figure(figsize=(6.4, 4.4))
    for row in sub.itertuples(index=False):
        key = label_to_key[row.Detektori]
        ax.scatter(
            row.delta_inner,
            row.delta_test,
            s=70,
            color=model_color(key),
            alpha=0.85,
            edgecolor="white",
            linewidth=1.1,
            zorder=3,
        )
        ax.annotate(
            row.Detektori,
            (row.delta_inner, row.delta_test),
            fontsize=7.5,
            color="#52514e",
            xytext=(6, 3),
            textcoords="offset points",
        )
    ax.axhline(0, color="#c3c2b7", lw=1)
    ax.axvline(0, color="#c3c2b7", lw=1)
    lim = max(abs(sub["delta_inner"]).max(), abs(sub["delta_test"]).max()) * 1.15
    ax.plot([-lim, lim], [-lim, lim], color="#898781", lw=1, ls=":")
    ax.set_xlabel("Përmirësimi në validimin e brendshëm (Δ AP)")
    ax.set_ylabel("Përmirësimi në blloqet e testimit (Δ AP)")
    ax.text(
        0.03,
        0.95,
        f"Spearman ρ = {rho_transfer:.2f}",
        transform=ax.transAxes,
        fontsize=9,
        color="#52514e",
        va="top",
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "tuning_transfer")

    # --- Figure: ranking before and after ---------------------------------
    fig, ax = new_figure(figsize=(6.6, 4.6))
    order = table.sort_values("AP_default")
    y = np.arange(len(order))
    for i, row in enumerate(order.itertuples(index=False)):
        key = label_to_key[row.Detektori]
        ax.plot(
            [row.AP_default, row.AP_i_akorduar],
            [i, i],
            color=model_color(key),
            lw=2.2,
            alpha=0.55,
            solid_capstyle="round",
            zorder=2,
        )
        ax.plot(row.AP_default, i, "o", color="#898781", markersize=5.5, zorder=3)
        ax.plot(
            row.AP_i_akorduar,
            i,
            "o",
            color=model_color(key),
            markersize=7,
            markeredgecolor="white",
            markeredgewidth=1.1,
            zorder=4,
        )
    ax.set_yticks(y, order["Detektori"])
    ax.set_xlabel(AX["ap"] + " mbi 8 folds")
    ax.grid(axis="y", visible=False)
    from matplotlib.lines import Line2D

    ax.legend(
        handles=[
            Line2D(
                [],
                [],
                marker="o",
                color="#898781",
                linestyle="",
                markersize=5.5,
                label="Hiperparametrat e parazgjedhur",
            ),
            Line2D(
                [],
                [],
                marker="o",
                color="#2a78d6",
                linestyle="",
                markersize=7,
                label="Pas akordimit",
            ),
        ],
        loc="lower right",
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "tuning_effect")

    if rho_rank >= 0.8:
        stability = "renditja e detektorëve mbetet praktikisht e njëjtë"
    elif rho_rank >= 0.5:
        stability = "renditja e detektorëve zhvendoset pjesërisht"
    else:
        stability = "renditja e detektorëve ndryshon thelbësisht"
    winner_before = default_ap[tuned_only].mean().idxmax()
    winner_after = tuned_ap[tuned_only].mean().idxmax()
    verdict = (
        f"Akordimi i hiperparametrave përmirëson AP-në mesatare të testit për {improved} "
        f"nga {len(sub)} detektorë të akorduar, dhe përmirësimi i grumbulluar është i "
        f"qëndrueshëm nëpër fold-e (Wilcoxon i çiftuar, "
        f"{int(wil['wins_a'].iloc[0])}/{len(paired)} fold-e, p = "
        f"{wil['p_value'].iloc[0]:.4f}). Megjithatë {stability}: korrelacioni i rangjeve "
        f"para dhe pas akordimit është rho = {rho_rank:.3f} (p = {p_rank:.2g}), dhe "
        f"detektori më i mirë unsupervised ndryshon nga "
        f"{MODEL_LABELS.get(winner_before, winner_before)} (AP "
        f"{default_ap[tuned_only].mean().max():.3f}) në "
        f"{MODEL_LABELS.get(winner_after, winner_after)} (AP "
        f"{tuned_ap[tuned_only].mean().max():.3f}). Përmirësimi i matur në validimin e "
        f"brendshëm e parashikon atë të testit vetëm pjesërisht (rho = "
        f"{rho_transfer:.2f}, p = {p_transfer:.2g})."
    )
    (results_dir / "tuning_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp18_tuning_effect", cfg.raw)


if __name__ == "__main__":
    main()

"""Could the hyperparameters have been chosen without any labels at all?

The search in exp9 ranks candidates by Average Precision on an inner
validation slice, which needs labels — historical ones, but labels. That is a
defensible assumption, and the same one already granted to the supervised
reference, but it is still an assumption. This experiment asks what would
have happened without it.

For each detector a small, explicit grid is evaluated three ways:

* inner-validation AP, the label-assisted criterion actually used;
* Excess-Mass, maximised, computed with no labels;
* Mass-Volume, minimised, computed with no labels.

The question is not which criterion gives higher numbers — they are not on the
same scale — but whether they *select the same configuration*. If they do, a
genuinely label-free deployment loses nothing at the tuning stage.
"""

import warnings

import pandas as pd
from scipy.stats import spearmanr

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.data.split import chronological_split
from src.evaluation.manifest import write_manifest
from src.evaluation.model_selection import (
    em_mv_scores,
    inner_temporal_split,
    inner_validation_ap,
)
from src.evaluation.report import MODEL_LABELS, new_figure, save_figure, save_table
from src.models.base import subsample_for_fit
from src.models.build import build_model

warnings.filterwarnings("ignore")

# Small, explicit grids. The criteria are expensive (each candidate is refitted
# once per random subspace), so breadth is traded for a clear comparison over
# detectors that are cheap enough to refit many times.
# Detectors whose hyperparameters keep their meaning inside a low-dimensional
# subspace. PCA reconstruction is deliberately excluded: its only
# hyperparameter is the number of retained components, which gets clamped to
# the subspace dimension, so every candidate above that dimension collapses to
# an identical criterion value. That is a real limitation of the subspace
# approximation, reported rather than worked around.
# The criteria refit the detector once per random subspace, so only detectors
# that are cheap to refit can be studied this way. PCA reconstruction is
# excluded for a different reason: its only hyperparameter is the number of
# retained components, which gets clamped to the subspace dimension, so every
# candidate above that dimension collapses to an identical criterion value.
GRIDS = {
    "iforest": [{"n_estimators": n, "max_samples": m} for n in (50, 200) for m in (64, 256, 1024)],
    "ocsvm": [{"nu": nu} for nu in (0.005, 0.01, 0.05, 0.1, 0.2)],
    "autoencoder": [{"latent_dim": ld, "epochs": 10} for ld in (2, 4, 8, 12, 16)],
}
FIT_SUBSAMPLE = 25000


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir

    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    train = chronological_split(df, cfg.split.train_fraction).train_full
    inner = inner_temporal_split(len(train), cfg.tuning.inner_val_fraction)
    fit_part, val_part = train.iloc[: inner.fit_end], train.iloc[inner.fit_end :]

    scaler = fit_scaler(fit_part)
    X_fit = subsample_for_fit(
        transform(scaler, fit_part[fit_part["Class"] == 0]), FIT_SUBSAMPLE, cfg.seed
    )
    X_val = transform(scaler, val_part)
    y_val = val_part["Class"].to_numpy()
    print(
        f"fit {len(X_fit):,} normale | validim {len(X_val):,} rreshta, "
        f"{int(y_val.sum())} mashtrime\n"
    )

    rows = []
    for name, grid in GRIDS.items():
        for params in grid:
            model = build_model(name, cfg, params)
            model.fit(X_fit)
            ap = inner_validation_ap(y_val, model.score(X_val))

            def fit_score(X_sub, _name=name, _params=params):
                sub_model = build_model(_name, cfg, _params)
                sub_model.fit(X_sub)
                return sub_model.score

            criteria = em_mv_scores(
                fit_score,
                X_fit,
                n_subspaces=cfg.tuning.em_subspaces,
                subspace_dim=cfg.tuning.em_subspace_dim,
                n_mc=cfg.tuning.em_mv_samples,
                seed=cfg.seed,
            )
            rows.append(
                {
                    "model": name,
                    "params": str(params),
                    "inner_ap": ap,
                    "em_auc": criteria["em_auc"],
                    "mv_auc": criteria["mv_auc"],
                }
            )
            print(
                f"  {name:<10} {str(params):<45} AP {ap:.4f}  "
                f"EM {criteria['em_auc']:.5f}  MV {criteria['mv_auc']:.4g}",
                flush=True,
            )

    table = pd.DataFrame(rows)
    save_table(table, results_dir, "unsupervised_selection_grid", float_fmt="%.6g")

    # --- would each criterion have chosen the same configuration? ---------
    summary = []
    for name, grp in table.groupby("model"):
        best_ap = grp.loc[grp["inner_ap"].idxmax()]
        best_em = grp.loc[grp["em_auc"].idxmax()]
        best_mv = grp.loc[grp["mv_auc"].idxmin()]
        rho_em, p_em = spearmanr(grp["inner_ap"], grp["em_auc"])
        rho_mv, p_mv = spearmanr(grp["inner_ap"], -grp["mv_auc"])
        # what does picking by EM cost, measured in the label-based currency?
        ap_range = grp["inner_ap"].max() - grp["inner_ap"].min()
        rows_out = {
            "Detektori": MODEL_LABELS.get(name, name),
            "Konfigurime": len(grp),
            "Zgjedhja sipas AP": best_ap["params"],
            "Zgjedhja sipas EM": best_em["params"],
            "Zgjedhja sipas MV": best_mv["params"],
            "EM përputhet": best_em["params"] == best_ap["params"],
            "MV përputhet": best_mv["params"] == best_ap["params"],
            "Humbja e AP me EM": best_ap["inner_ap"] - best_em["inner_ap"],
            "Humbja relative": (
                (best_ap["inner_ap"] - best_em["inner_ap"]) / ap_range if ap_range > 0 else 0.0
            ),
            "rho(AP, EM)": rho_em,
            "rho(AP, −MV)": rho_mv,
        }
        summary.append(rows_out)
    summary = pd.DataFrame(summary)
    save_table(summary, results_dir, "unsupervised_selection", float_fmt="%.4f")
    print("\n" + summary.drop(columns=["Zgjedhja sipas MV"]).to_string(index=False))

    agree_em = int(summary["EM përputhet"].sum())
    agree_mv = int(summary["MV përputhet"].sum())
    mean_loss = float(summary["Humbja relative"].mean())
    verdict = (
        f"Kriteri Excess-Mass zgjedh të njëjtin konfigurim si kriteri me etiketa në "
        f"{agree_em} nga {len(summary)} detektorë, dhe Mass-Volume në {agree_mv} nga "
        f"{len(summary)}. Kur zgjedhjet ndryshojnë, humbja mesatare është "
        f"{mean_loss:.0%} e hapësirës mes konfigurimit më të mirë dhe atij më të keq në "
        f"rrjetë. Korrelacioni mesatar mes renditjes së EM-së dhe asaj me etiketa është "
        f"{summary['rho(AP, EM)'].mean():.2f}."
    )
    (results_dir / "unsupervised_selection_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)

    # --- Figure: agreement, detector by detector --------------------------
    fig, ax = new_figure(figsize=(6.8, 4.4))
    for name, grp in table.groupby("model"):
        ap = grp["inner_ap"].to_numpy()
        em = grp["em_auc"].to_numpy()
        # rank within the detector's own grid, so different scales can share axes
        ax.scatter(
            pd.Series(ap).rank(),
            pd.Series(em).rank(),
            s=48,
            alpha=0.8,
            label=MODEL_LABELS.get(name, name),
            edgecolor="white",
            linewidth=0.8,
        )
    lim = table.groupby("model").size().max() + 0.5
    ax.plot([0.5, lim], [0.5, lim], color="#898781", lw=1, ls=":")
    ax.set_xlabel("Rangu i konfigurimit sipas AP-së në validimin e brendshëm")
    ax.set_ylabel("Rangu i konfigurimit sipas kriterit Excess-Mass")
    ax.legend(loc="upper left", fontsize=8)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "unsupervised_selection")

    write_manifest(results_dir, "exp19_unsupervised_selection", cfg.raw)


if __name__ == "__main__":
    main()

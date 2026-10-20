"""A causal test of the attribution finding.

The interpretability analysis showed that Isolation Forest spreads its splits
evenly over components regardless of how much signal they carry, and that the
detectors whose attention aligns with the signal rank higher. That is a
correlation between two measurements, and on its own it does not prove that
the misallocation causes the poor detection quality.

The intervention is simple: hand each detector only the k most informative
components and refit. If split misallocation is the mechanism, Isolation
Forest should gain the most, and it should gain most at small k where the
uninformative columns have been removed entirely.

Two rankings are used. The first orders components by their measured
discriminative power on the training window, which uses historical labels and
therefore represents the best case that feature selection could achieve. The
second orders them by excess kurtosis, which uses no labels at all and is the
classical projection-pursuit heuristic for directions in which outliers live.
The gap between the two is what a label-free deployment would forfeit.
"""

import numpy as np
import pandas as pd
from scipy.stats import kurtosis
from sklearn.metrics import average_precision_score, roc_auc_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import (
    AX,
    CM,
    FULL_WIDTH,
    MODEL_LABELS,
    fig_legend_above,
    model_plot_kwargs,
    new_figure,
    ordered_models,
    save_figure,
    save_table,
    value_grid,
)
from src.models.build import ALL_MODELS, build_model

K_VALUES = [3, 5, 8, 12, 16, 20, 29]
RANKINGS = {
    "sinjali (me etiketa)": "signal",
    "kurtoza (pa etiketa)": "kurtosis",
}


def rank_features(X_train: np.ndarray, y_train: np.ndarray, how: str) -> np.ndarray:
    """Component order, most useful first. Computed on training rows only."""
    if how == "signal":
        strength = np.array(
            [abs(roc_auc_score(y_train, X_train[:, j]) - 0.5) for j in range(X_train.shape[1])]
        )
    elif how == "kurtosis":
        strength = np.abs(kurtosis(X_train, axis=0, fisher=True))
    else:
        raise ValueError(f"unknown ranking {how!r}")
    return np.argsort(-strength)


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    rows, agreement_rows = [], []
    for fold in folds:
        train = df.iloc[: fold.train_end]
        test = df.iloc[fold.test_start : fold.test_end]
        scaler = fit_scaler(train, seed=cfg.seed)
        X_train_full = transform(scaler, train)
        X_train_normal = transform(scaler, train[train["Class"] == 0])
        X_test = transform(scaler, test)
        y_train = train["Class"].to_numpy()
        y_test = test["Class"].to_numpy()

        orders = {
            label: rank_features(X_train_full, y_train, how) for label, how in RANKINGS.items()
        }
        signal_order = orders["sinjali (me etiketa)"]
        kurtosis_order = orders["kurtoza (pa etiketa)"]
        for k in K_VALUES:
            overlap = len(set(signal_order[:k]) & set(kurtosis_order[:k])) / k
            agreement_rows.append({"fold": fold.index, "k": k, "mbivendosja": overlap})

        for label, order in orders.items():
            for k in K_VALUES:
                cols = np.sort(order[:k])
                for name in ALL_MODELS:
                    # The autoencoder fixes its input width at construction
                    # time, so a reduced column set has to be declared.
                    overrides = {"n_features": k} if name == "autoencoder" else None
                    model = build_model(name, cfg, overrides)
                    if name == "logreg":
                        model.fit(X_train_full[:, cols], y_train)
                    else:
                        model.fit(X_train_normal[:, cols])
                    rows.append(
                        {
                            "fold": fold.index,
                            "renditja": label,
                            "k": k,
                            "model": name,
                            "ap": average_precision_score(y_test, model.score(X_test[:, cols])),
                        }
                    )
        print(f"fold {fold.index} done", flush=True)

    per_fold = pd.DataFrame(rows)
    save_table(per_fold, results_dir, "feature_selection_per_fold", float_fmt="%.5f")
    agreement = pd.DataFrame(agreement_rows).groupby("k")["mbivendosja"].mean().reset_index()
    save_table(agreement, results_dir, "feature_selection_agreement", float_fmt="%.3f")
    summarise(cfg, results_dir, per_fold, agreement)


def summarise(cfg, results_dir, per_fold: pd.DataFrame, agreement: pd.DataFrame) -> None:
    summary = (
        per_fold.groupby(["renditja", "model", "k"])["ap"]
        .agg(ap_mean="mean", ap_std="std")
        .reset_index()
    )
    baseline = summary[summary["k"] == max(K_VALUES)].set_index(["renditja", "model"])["ap_mean"]
    summary["vs_te_gjitha"] = summary.apply(
        lambda r: r["ap_mean"] - baseline[(r["renditja"], r["model"])], axis=1
    )
    out = summary.copy()
    out["model"] = out["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(out, results_dir, "feature_selection", float_fmt="%.4f")

    print("\n=== fitimi maksimal nga përzgjedhja e veçorive ===")
    gains = (
        summary[summary["renditja"] == "sinjali (me etiketa)"]
        .loc[lambda d: d.groupby("model")["ap_mean"].idxmax()]
        .assign(model=lambda d: d["model"].map(lambda m: MODEL_LABELS.get(m, m)))
    )
    print(gains[["model", "k", "ap_mean", "vs_te_gjitha"]].to_string(index=False))

    figure(cfg, summary)

    signal_gains = summary[summary["renditja"] == "sinjali (me etiketa)"]
    best_gain = signal_gains.loc[signal_gains.groupby("model")["vs_te_gjitha"].idxmax()]
    parts = [
        f"{MODEL_LABELS.get(r['model'], r['model'])} {r['vs_te_gjitha']:+.3f} "
        f"njësi AP në k={int(r['k'])}"
        for _, r in best_gain.iterrows()
    ]
    unsup_gain = best_gain[best_gain["model"] != "logreg"].set_index("model")["vs_te_gjitha"]
    leader = unsup_gain.idxmax()
    verdict = (
        f"Fitimet maksimale nga kufizimi i hyrjes te komponentët informativë: "
        f"{', '.join(parts)}. Fitimi më i madh mes detektorëve unsupervised i takon "
        f"{MODEL_LABELS[leader]}-it ({unsup_gain[leader]:+.3f}). Renditja pa etiketa me "
        f"kurtozë përputhet me atë me etiketa mesatarisht në "
        f"{100 * agreement['mbivendosja'].mean():.0f}% të komponentëve."
    )
    (results_dir / "feature_selection_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp25_feature_selection", cfg.raw)


def figure(cfg, summary: pd.DataFrame) -> None:
    fig, axes = new_figure(ncols=2, figsize=(FULL_WIDTH, 6.8 * CM), sharey=True)
    titles = {
        "sinjali (me etiketa)": "Renditja sipas sinjalit (me etiketa)",
        "kurtoza (pa etiketa)": "Renditja sipas kurtozës (pa etiketa)",
    }
    for ax, label in zip(axes, RANKINGS, strict=True):
        subset = summary[summary["renditja"] == label]
        for name in ordered_models(subset["model"].unique()):
            curve = subset[subset["model"] == name].sort_values("k")
            ax.plot(curve["k"], curve["ap_mean"], **model_plot_kwargs(name, markers=True))
        ax.set_xticks(K_VALUES)
        ax.set_xlabel("Komponentë të mbajtur (k)")
        ax.set_title(titles[label], loc="left", fontsize=8.5)
        value_grid(ax, "y")
    axes[0].set_ylabel(AX["ap"] + ", mesatare")
    axes[0].set_ylim(0, 0.8)
    handles, labels = axes[0].get_legend_handles_labels()
    fig_legend_above(fig, handles, labels)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "feature_selection")


def main_from_saved(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    summarise(
        cfg,
        results_dir,
        pd.read_csv(results_dir / "feature_selection_per_fold.csv"),
        pd.read_csv(results_dir / "feature_selection_agreement.csv"),
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-saved", action="store_true", help="rebuild from feature_selection_per_fold.csv"
    )
    main_from_saved() if parser.parse_args().from_saved else main()

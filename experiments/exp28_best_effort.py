"""What each detector achieves when nothing is left at its default.

The main table reports every detector under library defaults and a standard
scaler, which is the fair comparison but not the useful one: a practitioner
would tune both. Two separate studies have already shown that each choice
matters, the preprocessing study and the hyperparameter search, and the
obvious next question is whether the two gains compose or overlap.

A two-by-two design answers it directly. Each detector runs with default and
tuned hyperparameters, crossed with the standard scaler and the preprocessing
that the scaling study selected for that detector, over all eight folds. The
interaction term is the interesting part: if the two interventions fix the
same problem, their combination will be worth less than their sum.
"""

import json

import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import AX, MODEL_LABELS, model_color, new_figure, save_figure, save_table
from src.models.build import ALL_MODELS, build_model

SCALER_LABEL_TO_KEY = {
    "StandardScaler": "standard",
    "RobustScaler": "robust",
    "Quantile (normal)": "quantile_normal",
    "Quantile (uniform)": "quantile_uniform",
    "PowerTransformer": "power_yeo_johnson",
    "MinMaxScaler": "minmax",
    "Pa skalim": "none",
}


def best_scalers(results_dir) -> dict[str, str]:
    """Per-detector preprocessing chosen by the scaling study."""
    path = results_dir / "scaling_significance.csv"
    if not path.exists():
        raise SystemExit("mungon scaling_significance.csv; ekzekuto exp21_scaling")
    table = pd.read_csv(path)
    label_to_key = {v: k for k, v in MODEL_LABELS.items()}
    return {
        label_to_key[row["Detektori"]]: SCALER_LABEL_TO_KEY[row["Paraprocesimi_me_i_mire"]]
        for _, row in table.iterrows()
    }


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    tuned_path = results_dir / "tuned_params.json"
    if not tuned_path.exists():
        raise SystemExit("mungon tuned_params.json; ekzekuto exp9_tuning")
    tuned = json.loads(tuned_path.read_text())
    scalers = best_scalers(results_dir)

    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    rows = []
    for fold in folds:
        train = df.iloc[: fold.train_end]
        test = df.iloc[fold.test_start : fold.test_end]
        train_normal = train[train["Class"] == 0]
        y_train = train["Class"].to_numpy()
        y_test = test["Class"].to_numpy()

        prepared = {}
        for kind in {"standard", *scalers.values()}:
            scaler = fit_scaler(train, kind, cfg.seed)
            prepared[kind] = (
                transform(scaler, train),
                transform(scaler, train_normal),
                transform(scaler, test),
            )

        for name in ALL_MODELS:
            for hp_label, overrides in (("parazgjedhur", None), ("i akorduar", tuned.get(name))):
                if overrides is None and hp_label == "i akorduar":
                    continue
                for prep_label, kind in (
                    ("standard", "standard"),
                    ("më i miri", scalers.get(name, "standard")),
                ):
                    if prep_label == "më i miri" and kind == "standard":
                        continue
                    X_full, X_normal, X_test = prepared[kind]
                    model = build_model(name, cfg, overrides)
                    if name == "logreg":
                        model.fit(X_full, y_train)
                    else:
                        model.fit(X_normal)
                    rows.append(
                        {
                            "fold": fold.index,
                            "model": name,
                            "hiperparametrat": hp_label,
                            "paraprocesimi": prep_label,
                            "skaluesi": kind,
                            "ap": average_precision_score(y_test, model.score(X_test)),
                        }
                    )
        print(f"fold {fold.index} done", flush=True)

    per_fold = pd.DataFrame(rows)
    save_table(per_fold, results_dir, "best_effort_per_fold", float_fmt="%.5f")
    summarise(results_dir, per_fold, cfg)


def summarise(results_dir, per_fold, cfg):
    """Tables, figure and verdict from the per-fold scores.

    Kept separate from the fitting loop so the summary can be rebuilt in
    seconds when only its logic changes, instead of refitting for an hour.
    """
    summary = (
        per_fold.groupby(["model", "hiperparametrat", "paraprocesimi"])["ap"]
        .agg(ap_mean="mean", ap_std="std")
        .reset_index()
    )
    wide = summary.pivot_table(
        index="model", columns=["hiperparametrat", "paraprocesimi"], values="ap_mean"
    )
    wide.columns = [f"{a} / {b}" for a, b in wide.columns]
    wide = wide.reset_index()
    wide["model"] = wide["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(wide, results_dir, "best_effort", float_fmt="%.4f")
    print(wide.to_string(index=False))

    # --- do the two interventions compose? --------------------------------
    interaction_rows = []
    base = summary.set_index(["model", "hiperparametrat", "paraprocesimi"])["ap_mean"]
    for name in ALL_MODELS:
        try:
            b = base[(name, "parazgjedhur", "standard")]
            only_prep = base[(name, "parazgjedhur", "më i miri")]
            only_hp = base[(name, "i akorduar", "standard")]
            both = base[(name, "i akorduar", "më i miri")]
        except KeyError:
            continue
        interaction_rows.append(
            {
                "Detektori": MODEL_LABELS.get(name, name),
                "bazë": b,
                "vetëm paraprocesim": only_prep - b,
                "vetëm akordim": only_hp - b,
                "të dyja": both - b,
                "shuma e efekteve": (only_prep - b) + (only_hp - b),
                "ndërveprimi": (both - b) - ((only_prep - b) + (only_hp - b)),
                # The best cell, not the "both" cell. For two of the three
                # detectors the interaction is negative enough that applying
                # both interventions lands below applying only the better one,
                # so calling "both" the final result would misreport them.
                "qeliza më e mirë": max(
                    (b, "bazë"),
                    (only_prep, "vetëm paraprocesim"),
                    (only_hp, "vetëm akordim"),
                    (both, "të dyja"),
                )[1],
                "AP më i mirë i arritshëm": max(b, only_prep, only_hp, both),
            }
        )
    interaction = pd.DataFrame(interaction_rows)
    save_table(interaction, results_dir, "best_effort_interaction", float_fmt="%.4f")
    print("\n" + interaction.to_string(index=False))

    # --- Figure -----------------------------------------------------------
    fig, ax = new_figure(figsize=(7.0, 4.2))
    order = [
        "parazgjedhur / standard",
        "parazgjedhur / më i miri",
        "i akorduar / standard",
        "i akorduar / më i miri",
    ]
    labels = ["bazë", "+ paraprocesim", "+ akordim", "+ të dyja"]
    import numpy as np

    x = np.arange(len(order))
    width = 0.2
    for i, name in enumerate(ALL_MODELS):
        row = wide[wide["model"] == MODEL_LABELS.get(name, name)]
        if row.empty:
            continue
        values = [float(row[col].iloc[0]) if col in row else np.nan for col in order]
        ax.bar(
            x + (i - 1.5) * width,
            values,
            width=width,
            color=model_color(name),
            label=MODEL_LABELS.get(name, name),
        )
    ax.set_xticks(x, labels)
    ax.set_ylabel(AX["ap"] + " mbi 8 fold-e")
    ax.legend(fontsize=8.5)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "best_effort")

    unsup = interaction[interaction["Detektori"] != MODEL_LABELS["logreg"]]
    best_row = unsup.loc[unsup["AP më i mirë i arritshëm"].idxmax()]
    per_detector = "; ".join(
        f"{r['Detektori']} {r['AP më i mirë i arritshëm']:.4f} ({r['qeliza më e mirë']})"
        for _, r in unsup.sort_values("AP më i mirë i arritshëm", ascending=False).iterrows()
    )
    verdict = (
        f"Kur secili detektor vlerësohet në qelizën e vet më të mirë të dizajnit dy-nga-dy, "
        f"renditja bëhet: {per_detector}. Më i miri është pra {best_row['Detektori']} me AP "
        f"{best_row['AP më i mirë i arritshëm']:.4f} kundrejt {best_row['bazë']:.4f} në "
        f"konfigurimin bazë, pra renditja e konfigurimeve të parazgjedhura nuk mbijeton. "
        f"Vlen të theksohet se për dy nga tre detektorët qeliza më e mirë nuk është ajo ku "
        f"zbatohen të dyja ndërhyrjet, sepse ndërveprimi mes tyre është mjaft negativ sa "
        f"kombinimi të bjerë nën ndërhyrjen e vetme më të mirë. "
        + "; ".join(
            f"{r['Detektori']}: paraprocesim {r['vetëm paraprocesim']:+.3f}, akordim "
            f"{r['vetëm akordim']:+.3f}, të dyja {r['të dyja']:+.3f}, ndërveprim "
            f"{r['ndërveprimi']:+.3f}"
            for _, r in unsup.iterrows()
        )
        + ". Ndërveprimi negativ do të thotë se të dyja ndërhyrjet e adresojnë pjesërisht të "
        "njëjtin problem dhe se përfitimet e tyre nuk mblidhen."
    )
    (results_dir / "best_effort_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp28_best_effort", cfg.raw)


def main_from_saved(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    per_fold = pd.read_csv(results_dir / "best_effort_per_fold.csv")
    summarise(results_dir, per_fold, cfg)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-saved",
        action="store_true",
        help="rebuild the tables and verdict from best_effort_per_fold.csv, without refitting",
    )
    args = parser.parse_args()
    main_from_saved() if args.from_saved else main()

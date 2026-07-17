"""Experiment 6 — the cost of honesty: chronological vs shuffled split.

Retrains every model under the literature-style SHUFFLED stratified 70/30
split (a leaky protocol: future transactions inform training statistics)
and compares AP/ROC-AUC against the chronological protocol. The shuffled
numbers are for comparison ONLY and are never used anywhere else.

Nothing here touches the saved chronological artifacts.
"""

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.harness import score_test_window
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import threshold_free_metrics
from src.evaluation.report import MODEL_LABELS, save_table
from src.models.build import ALL_MODELS, build_model


def main(cfg=None):
    cfg = cfg or load_config()

    # Chronological APs from the saved artifacts (the honest protocol).
    chrono = score_test_window(cfg)
    ap_chrono = {
        name: threshold_free_metrics(chrono.y_test, scores)["ap"]
        for name, scores in chrono.test_scores.items()
    }

    # Literature-style shuffled stratified split, same ratio and seed.
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    train_df, test_df = train_test_split(
        df,
        train_size=cfg.split.train_fraction,
        random_state=cfg.seed,
        shuffle=True,
        stratify=df["Class"],
    )
    scaler = fit_scaler(train_df)
    X_train_full = transform(scaler, train_df)
    X_train_normal = transform(scaler, train_df[train_df["Class"] == 0])
    X_test = transform(scaler, test_df)
    y_train = train_df["Class"].to_numpy()
    y_test = test_df["Class"].to_numpy()

    rows = []
    for name in ALL_MODELS:
        model = build_model(name, cfg)
        if name == "logreg":
            model.fit(X_train_full, y_train)
        else:
            model.fit(X_train_normal)
        m = threshold_free_metrics(y_test, model.score(X_test))
        rows.append(
            {
                "model": MODEL_LABELS[name],
                "ap_chronological": ap_chrono[name],
                "ap_shuffled_LEAKY": m["ap"],
                "ap_ratio_shuffled_over_chrono": m["ap"] / ap_chrono[name],
                "roc_auc_shuffled_LEAKY": m["roc_auc"],
            }
        )
        print(f"{name}: chrono AP {ap_chrono[name]:.4f} -> shuffled AP {m['ap']:.4f}")

    table = pd.DataFrame(rows)
    save_table(table, REPO_ROOT / cfg.results_dir, "shuffled_split_comparison")
    write_manifest(REPO_ROOT / cfg.results_dir, "exp6_shuffled_split", cfg.raw)


if __name__ == "__main__":
    main()

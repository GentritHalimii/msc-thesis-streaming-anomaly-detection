"""Experiment 6 — the cost of honesty: chronological vs shuffled split.

Retrains every model under the literature-style SHUFFLED stratified 70/30
split (a leaky protocol: future transactions inform training statistics)
and compares AP/ROC-AUC against the chronological protocol. The shuffled
numbers are for comparison ONLY and are never used anywhere else.

A single shuffled split is one draw: which frauds land in the test set is
itself random, and with 148 of them the AP of that set moves with the draw.
The split is therefore repeated over several seeds, and the inflation is
reported as a mean with its range. The models keep the project seed, so the
spread measures the split alone.

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
from src.models.build import ALL_MODELS, UNSUPERVISED, build_model

N_SEEDS = 10


def shuffled_run(cfg, df: pd.DataFrame, seed: int) -> dict[str, dict]:
    """Fit every model on one shuffled stratified split; AP and ROC-AUC per model."""
    train_df, test_df = train_test_split(
        df,
        train_size=cfg.split.train_fraction,
        random_state=seed,
        shuffle=True,
        stratify=df["Class"],
    )
    scaler = fit_scaler(train_df)
    X_train_full = transform(scaler, train_df)
    X_train_normal = transform(scaler, train_df[train_df["Class"] == 0])
    X_test = transform(scaler, test_df)
    y_train = train_df["Class"].to_numpy()
    y_test = test_df["Class"].to_numpy()

    out = {}
    for name in ALL_MODELS:
        model = build_model(name, cfg)
        if name == "logreg":
            model.fit(X_train_full, y_train)
        else:
            model.fit(X_train_normal)
        out[name] = threshold_free_metrics(y_test, model.score(X_test))
    return out


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir

    # Chronological APs from the saved artifacts (the honest protocol).
    chrono = score_test_window(cfg)
    ap_chrono = {
        name: threshold_free_metrics(chrono.y_test, scores)["ap"]
        for name, scores in chrono.test_scores.items()
    }

    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    seeds = [cfg.seed + i for i in range(N_SEEDS)]
    per_seed = []
    for seed in seeds:
        metrics = shuffled_run(cfg, df, seed)
        for name, m in metrics.items():
            per_seed.append(
                {
                    "seed": seed,
                    "model": MODEL_LABELS[name],
                    "key": name,
                    "ap_shuffled_LEAKY": m["ap"],
                    "ap_ratio_shuffled_over_chrono": m["ap"] / ap_chrono[name],
                    "roc_auc_shuffled_LEAKY": m["roc_auc"],
                }
            )
        line = ", ".join(f"{n} {metrics[n]['ap'] / ap_chrono[n]:.2f}x" for n in ALL_MODELS)
        print(f"seed {seed}: {line}", flush=True)

    seeds_df = pd.DataFrame(per_seed)
    save_table(seeds_df.drop(columns="key"), results_dir, "shuffled_split_per_seed")

    rows = []
    for name in ALL_MODELS:
        sub = seeds_df[seeds_df["key"] == name]
        ratio = sub["ap_ratio_shuffled_over_chrono"]
        rows.append(
            {
                "model": MODEL_LABELS[name],
                "ap_chronological": ap_chrono[name],
                "ap_shuffled_LEAKY": float(sub["ap_shuffled_LEAKY"].mean()),
                "ap_ratio_shuffled_over_chrono": float(ratio.mean()),
                "ratio_min": float(ratio.min()),
                "ratio_max": float(ratio.max()),
                "ratio_sd": float(ratio.std()),
                "roc_auc_shuffled_LEAKY": float(sub["roc_auc_shuffled_LEAKY"].mean()),
                "n_seeds": len(sub),
            }
        )
    table = pd.DataFrame(rows)
    save_table(table, results_dir, "shuffled_split_comparison")
    print(table.to_string(index=False))

    # The headline number of the thesis is the inflation averaged over the
    # three unsupervised detectors; its spread over the seeds is what says
    # whether "about three times" survives a different draw.
    unsup = seeds_df[seeds_df["key"].isin(UNSUPERVISED)]
    by_seed = unsup.groupby("seed")["ap_ratio_shuffled_over_chrono"].mean()
    ref = seeds_df[seeds_df["key"] == "logreg"]["ap_ratio_shuffled_over_chrono"]
    verdict = (
        f"Mbi {len(seeds)} ndarje të rastësishme (seed {seeds[0]} deri {seeds[-1]}), fryrja "
        f"mesatare e AP-së për tri metodat unsupervised është {by_seed.mean():.2f} herë, nga "
        f"{by_seed.min():.2f} deri {by_seed.max():.2f} herë sipas ndarjes. Raporti i "
        f"referencës supervised është {ref.mean():.2f}, nga {ref.min():.2f} deri "
        f"{ref.max():.2f}."
    )
    save_table(
        pd.DataFrame(
            {
                "seed": by_seed.index,
                "fryrja_mesatare_unsupervised": by_seed.to_numpy(),
            }
        ),
        results_dir,
        "shuffled_split_inflation_by_seed",
    )
    (results_dir / "shuffled_split_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp6_shuffled_split", cfg.raw)


if __name__ == "__main__":
    main()

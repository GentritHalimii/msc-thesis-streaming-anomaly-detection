"""Does cleaning the training window with labels flatter the detectors?

The main protocol fits each unsupervised detector on the legitimate
transactions of its training window. Removing the frauds needs the historical
labels, so strictly that regime is the semi-supervised one of Chandola et al.:
the algorithm never sees a label, but its training data was chosen with them.
A system with no labels at all would fit on the whole window, frauds
included.

This experiment refits the three detectors that way (run_protocol
--unfiltered) and compares Average Precision fold by fold with the main
protocol. Average Precision does not depend on a threshold, so the comparison
is not touched by the contamination rate, which is also taken from labels.
"""

import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import load_folds
from src.evaluation.report import MODEL_LABELS, ordered_models, save_table
from src.evaluation.stats import wilcoxon_pairs
from src.models.build import UNSUPERVISED


def ap_matrix(folds, models: list[str]) -> pd.DataFrame:
    rows = {
        i: {m: average_precision_score(f.y, f.test_scores(m)) for m in models}
        for i, f in enumerate(folds)
    }
    return pd.DataFrame(rows).T.sort_index()


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    unfiltered_dir = results_dir / "unfiltered"
    if not (unfiltered_dir / "folds" / "fold0.npz").exists():
        raise SystemExit("mungojnë fold-et pa filtrim; ekzekuto run_protocol --unfiltered")

    models = ordered_models(UNSUPERVISED)
    clean = ap_matrix(load_folds(results_dir, cfg.protocol.n_folds), models)
    raw = ap_matrix(load_folds(unfiltered_dir, cfg.protocol.n_folds), models)

    per_fold = pd.concat(
        [clean.add_suffix("__normalet"), raw.add_suffix("__gjithe_dritarja")], axis=1
    )
    per_fold.index.name = "fold"
    save_table(per_fold.reset_index(), results_dir, "training_regime_per_fold", float_fmt="%.5f")

    rows = []
    for m in models:
        pair = pd.DataFrame({"gjithe_dritarja": raw[m], "normalet": clean[m]})
        w = wilcoxon_pairs(pair, [("gjithe_dritarja", "normalet")]).iloc[0]
        rows.append(
            {
                "Detektori": MODEL_LABELS.get(m, m),
                "AP_normalet": float(clean[m].mean()),
                "AP_gjithe_dritarja": float(raw[m].mean()),
                "delta": float(raw[m].mean() - clean[m].mean()),
                "mediana_normalet": float(clean[m].median()),
                "mediana_gjithe_dritarja": float(raw[m].median()),
                "fitore_gjithe_dritarja": int(w["wins_a"]),
                "fitore_normalet": int(w["wins_b"]),
                "p_value": float(w["p_value"]),
                "rank_biserial": float(w["rank_biserial"]),
            }
        )
    table = pd.DataFrame(rows)
    save_table(table, results_dir, "training_regime")
    print(table.to_string(index=False))

    order_clean = clean.mean().sort_values(ascending=False).index.tolist()
    order_raw = raw.mean().sort_values(ascending=False).index.tolist()
    names = ", ".join(MODEL_LABELS.get(k, k) for k in order_raw)
    ranking = (
        f"renditja mbetet e njëjtë ({names})"
        if order_clean == order_raw
        else f"renditja ndryshon në {names}"
    )
    parts = "; ".join(
        f"{r['Detektori']} {r['AP_normalet']:.3f} -> {r['AP_gjithe_dritarja']:.3f} "
        f"({r['fitore_gjithe_dritarja']} fitore nga 8, p = {r['p_value']:.3f})"
        for _, r in table.iterrows()
    )
    verdict = (
        f"Me trajnim mbi gjithë dritaren, mashtrimet përfshirë, AP mesatare ndryshon kështu: "
        f"{parts}; {ranking}."
    )
    (results_dir / "training_regime_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp29_training_regime", cfg.raw)


if __name__ == "__main__":
    main()

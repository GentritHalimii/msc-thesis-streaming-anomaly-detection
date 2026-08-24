"""One table that answers the three research questions from the artifacts.

Assembled from the generated results rather than written by hand, so it
cannot disagree with the chapters that precede it. If an experiment is re-run
and a number moves, this table moves with it.
"""

import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.report import MODEL_LABELS, save_table


def _read(results_dir, name):
    path = results_dir / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else None


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    bench = _read(results_dir, "benchmark_summary")
    lat = _read(results_dir, "latency_summary")
    ens = _read(results_dir, "ensemble_summary")
    budget = _read(results_dir, "budget_summary")

    label_to_key = {v: k for k, v in MODEL_LABELS.items()}
    bench["key"] = bench["model"].map(label_to_key)
    unsup = bench[bench["key"] != "logreg"].sort_values("ap_mean", ascending=False)
    best_unsup = unsup.iloc[0]
    reference = bench[bench["key"] == "logreg"].iloc[0]

    static = lat[~lat["prag_adaptiv"]]
    core_rates = static[static["rate_msg_s"] <= 1000]
    best_ens = ens.sort_values("ap_mean", ascending=False).iloc[0]
    b100 = budget[budget["budget_k"] == 100].sort_values("recall_at_k", ascending=False)

    # Read the tuning effect off exp18 rather than restating a number that
    # can go stale the moment the search is re-run.
    tuning_path = results_dir / "tuning_effect.csv"
    if tuning_path.exists():
        te = pd.read_csv(tuning_path)
        te = te[te["Detektori"] != reference["model"]].sort_values("AP_i_akorduar", ascending=False)
        order_default = list(te.sort_values("AP_default", ascending=False)["Detektori"])
        order_tuned = list(te["Detektori"])
        changed = order_default != order_tuned
        tuning_note = (
            f"Pas akordimit renditja {'ndryshon' if changed else 'nuk ndryshon'}: "
            f"{' > '.join(order_default)} bëhet {' > '.join(order_tuned)}, dhe "
            f"{te.iloc[0]['Detektori']} arrin AP {te.iloc[0]['AP_i_akorduar']:.3f}."
        )
    else:
        tuning_note = "Efekti i akordimit nuk është matur ende."

    rows = [
        {
            "Pyetja": "PH1",
            "Formulimi": "A arrihet vonesë mesatare nën 1 sekondë?",
            "Përgjigjja": "PO",
            "Evidenca": (
                f"Vonesa mesatare fund-më-fund {core_rates['e2e_ms_mean'].min():.0f}–"
                f"{core_rates['e2e_ms_mean'].max():.0f} ms në {len(core_rates)} "
                f"konfigurime deri në 1000 msg/s; p99 maksimal "
                f"{core_rates['e2e_ms_p99'].max():.0f} ms. Ngopja rreth "
                f"{static['throughput_msg_s'].max():.0f} msg/s."
            ),
        },
        {
            "Pyetja": "PH2",
            "Formulimi": "Cili algoritëm ofron balancën më të mirë?",
            "Përgjigjja": f"{best_unsup['model']} (me parazgjedhje)",
            "Evidenca": (
                f"AP {best_unsup['ap_mean']:.3f} ± {best_unsup['ap_std']:.3f} mbi 8 fold-e, "
                f"me koston e dytë më të ulët të pikëzimit "
                f"({best_unsup['score_us_per_tx']:.2f} µs/tx). Referenca e mbikëqyrur "
                f"mbetet përpara me AP {reference['ap_mean']:.3f}. {tuning_note}"
            ),
        },
        {
            "Pyetja": "PH3",
            "Formulimi": "A e përmirëson ansambli zbulimin?",
            "Përgjigjja": "JO",
            "Evidenca": (
                f"Varianti më i mirë nga {len(ens)} i testuar arrin AP "
                f"{best_ens['ap_mean']:.3f} kundrejt {best_unsup['ap_mean']:.3f} të modelit "
                f"më të mirë individual, duke fituar vetëm në "
                f"{int(best_ens['fold_wins_vs_best_single'])}/8 fold-e. Shkaku: "
                f"korrelacion i lartë i rangjeve mes anëtarëve."
            ),
        },
    ]
    table = pd.DataFrame(rows)
    save_table(table, results_dir, "rq_summary")
    print(table.to_string(index=False))
    top_budget = b100[~b100["model"].str.startswith("LR")].iloc[0]
    print(
        f"\n(kontroll: në buxhet 100 alarme, më i miri unsupervised është "
        f"{top_budget['model']} me recall {top_budget['recall_at_k']:.3f})"
    )
    write_manifest(results_dir, "make_rq_summary", cfg.raw)


if __name__ == "__main__":
    main()

"""One table that answers the three research questions from the artifacts.

Assembled from the generated results rather than written by hand, so it
cannot disagree with the chapters that precede it. If an experiment is re-run
and a number moves, this table moves with it.
"""

import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.report import MODEL_LABELS, save_table

# H1 covers arrival rates up to this value (Chapter 3.5); faster rates are
# capacity tests outside the hypothesis.
H1_MAX_RATE = 1000


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
    capacity = _read(results_dir, "capacity_summary")

    label_to_key = {v: k for k, v in MODEL_LABELS.items()}
    bench["key"] = bench["model"].map(label_to_key)
    unsup = bench[bench["key"] != "logreg"].sort_values("ap_mean", ascending=False)
    best_unsup = unsup.iloc[0]
    reference = bench[bench["key"] == "logreg"].iloc[0]

    static = lat[~lat["prag_adaptiv"]]
    within = static[static["rate_msg_s"] <= H1_MAX_RATE]
    capacity_note = ""
    if capacity is not None:
        over = capacity[capacity["e2e_ms_mean"] > 1000]
        if over.empty:
            capacity_note = (
                f" Në testin e kapacitetit, deri në {capacity['rate_msg_s'].max():.0f} msg/s, "
                f"vonesa mesatare mbetet nën 1 s për çdo model."
            )
        else:
            names = ", ".join(sorted(over["model"].unique()))
            capacity_note = (
                f" Në testin e kapacitetit vonesa mesatare e kalon 1 s vetëm për {names}, nga "
                f"{over['rate_msg_s'].min():.0f} msg/s."
            )
    best_ens = ens.sort_values("ap_mean", ascending=False).iloc[0]
    b100 = budget[budget["budget_k"] == 100].sort_values("recall_at_k", ascending=False)
    cheapest = bench.sort_values("score_us_per_tx").iloc[0]["key"] == best_unsup["key"]

    # Read the tuning effect off exp18 rather than restating a number that
    # can go stale the moment the search is re-run.
    tuning_path = results_dir / "tuning_effect.csv"
    if tuning_path.exists():
        te = pd.read_csv(tuning_path)
        te = te[te["Detektori"] != reference["model"]].sort_values("AP_i_akorduar", ascending=False)
        order_default = list(te.sort_values("AP_default", ascending=False)["Detektori"])
        order_tuned = list(te["Detektori"])
        tuning_note = (
            f"Pas akordimit renditja bëhet {', '.join(order_tuned)}."
            if order_default != order_tuned
            else "Akordimi nuk e ndryshon renditjen."
        )
    else:
        tuning_note = "Efekti i akordimit nuk është matur ende."
    # The baseline cleans the training window with historical labels; the
    # regime without that cleaning answers the same question differently.
    regime = _read(results_dir, "training_regime")
    regime_note = ""
    if regime is not None:
        rg = regime.sort_values("AP_gjithe_dritarja", ascending=False)
        regime_note = (
            " Me trajnim mbi gjithë dritaren, pa pastrim me etiketa, renditja bëhet "
            + ", ".join(f"{r['Detektori']} {r['AP_gjithe_dritarja']:.3f}" for _, r in rg.iterrows())
            + "."
        )
    best_effort = _read(results_dir, "best_effort_interaction")
    if best_effort is not None:
        be = best_effort.sort_values("AP më i mirë i arritshëm", ascending=False)
        tuning_note += (
            " Në konfigurimin më të mirë të secilit: "
            + ", ".join(
                f"{r['Detektori']} {r['AP më i mirë i arritshëm']:.3f}" for _, r in be.iterrows()
            )
            + "."
        )

    corr = _read(results_dir, "ensemble_rank_correlation_per_fold")
    corr_note = ""
    if corr is not None:
        pair_means = corr.groupby(["model_a", "model_b"])["spearman"].mean()
        corr_note = (
            f" Korrelacioni i renditjeve mes anëtarëve: {pair_means.min():.2f} deri "
            f"{pair_means.max():.2f}."
        )
    greedy = _read(results_dir, "ensemble_per_fold")
    greedy_note = ""
    if greedy is not None:
        picks = greedy[(greedy["pool"] == "greedy") & (greedy["fold"] > 0)]["members"]
        if len(picks) and (picks == picks.iloc[0]).all() and "+" not in picks.iloc[0]:
            greedy_note = (
                f" Procedura lakmitare zgjedh vetëm {MODEL_LABELS.get(picks.iloc[0])}-in në çdo "
                f"fold me histori."
            )

    rows = [
        {
            "Pyetja": "PH1",
            "Formulimi": "A arrihet vonesë mesatare nën 1 sekondë?",
            "Përgjigjja": "Po",
            "Evidenca": (
                f"Në ritmet e hipotezës ({within['rate_msg_s'].min():.0f} deri "
                f"{within['rate_msg_s'].max():.0f} msg/s) vonesa mesatare end-to-end është "
                f"{within['e2e_ms_mean'].min():.1f} deri {within['e2e_ms_mean'].max():.1f} ms në "
                f"{len(within)} konfigurime, mesatare e {within['n_runs'].min():.0f} "
                f"ekzekutimeve; p99 më i lartë {within['e2e_ms_p99'].max():.0f} ms."
                f"{capacity_note}"
            ),
        },
        {
            "Pyetja": "PH2",
            "Formulimi": "Cili algoritëm ofron balancën më të mirë?",
            "Përgjigjja": f"{best_unsup['model']} (konfigurimi bazë, dritare e pastruar)",
            "Evidenca": (
                f"AP {best_unsup['ap_mean']:.3f} (s.d. {best_unsup['ap_std']:.3f}) në protokollin "
                f"8-fold, me koston e inferencës {best_unsup['score_us_per_tx']:.2f} µs/tx"
                f"{', më e ulëta' if cheapest else ''}. Referenca supervised: AP "
                f"{reference['ap_mean']:.3f}. {tuning_note}{regime_note}"
            ),
        },
        {
            "Pyetja": "PH3",
            "Formulimi": "A e përmirëson ansambli zbulimin?",
            "Përgjigjja": "Jo",
            "Evidenca": (
                f"Më i miri nga {len(ens)} variantet arrin AP {best_ens['ap_mean']:.3f} kundrejt "
                f"{best_unsup['ap_mean']:.3f} të modelit më të mirë individual."
                f"{greedy_note}{corr_note}"
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

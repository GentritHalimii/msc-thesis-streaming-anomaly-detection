"""How much does the evaluation protocol change the answer?

Three protocols are compared on identical data and identical models:

* a single chronological 70/30 split — the protocol named in the proposal and
  the one most published work on this dataset uses;
* the eight-fold rolling-origin protocol developed here;
* a shuffled stratified split — the leaky protocol, included only to quantify
  how much it inflates results.

The question is deliberately narrow and falsifiable: does the choice of
protocol change *which detector wins*, does it change *the absolute numbers*,
and does a single split let you know how uncertain its own answer is?
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.report import AX, MODEL_LABELS, model_color, new_figure, save_figure, save_table
from src.models.build import UNSUPERVISED

LABEL_TO_KEY = {v: k for k, v in MODEL_LABELS.items()}


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir

    single = pd.read_csv(results_dir / "metrics_main.csv")
    single["key"] = single["model"].map(LABEL_TO_KEY)
    single = single.set_index("key")

    folds = pd.read_csv(results_dir / "benchmark_summary.csv")
    folds["key"] = folds["model"].map(LABEL_TO_KEY)
    folds = folds.set_index("key")

    common = [m for m in UNSUPERVISED if m in single.index and m in folds.index]
    table = pd.DataFrame(
        {
            "Detektori": [MODEL_LABELS[m] for m in common],
            "AP_ndarje_e_vetme": [single.loc[m, "ap"] for m in common],
            "AP_8_folde": [folds.loc[m, "ap_mean"] for m in common],
            "sd_nder_folde": [folds.loc[m, "ap_std"] for m in common],
        }
    )
    table["diferenca"] = table["AP_8_folde"] - table["AP_ndarje_e_vetme"]
    table["rangu_ndarje_e_vetme"] = table["AP_ndarje_e_vetme"].rank(ascending=False).astype(int)
    table["rangu_8_folde"] = table["AP_8_folde"].rank(ascending=False).astype(int)
    table["ndryshim_rangu"] = table["rangu_8_folde"] - table["rangu_ndarje_e_vetme"]
    # Is the single-split estimate even inside the spread the folds reveal?
    table["brenda_1sd"] = (table["AP_ndarje_e_vetme"] - table["AP_8_folde"]).abs() <= table[
        "sd_nder_folde"
    ]
    table = table.sort_values("AP_8_folde", ascending=False)
    save_table(table, results_dir, "protocol_comparison")

    rho, p_rho = spearmanr(table["AP_ndarje_e_vetme"], table["AP_8_folde"])
    print(table.to_string(index=False))
    print(
        f"\nKorrelacioni i renditjeve (Spearman) mes dy protokolleve: "
        f"rho = {rho:.3f} (p = {p_rho:.2g})"
    )
    print(f"Ndryshimi maksimal i rangut: {int(table['ndryshim_rangu'].abs().max())} pozicione")
    print(
        f"Raporti mesatar sd/mesatare nëpër fold-e: "
        f"{(table['sd_nder_folde'] / table['AP_8_folde']).mean():.2f}"
    )

    # --- shuffled split, if the leaky-protocol experiment has been run ------
    shuffled_path = results_dir / "shuffled_split_comparison.csv"
    inflation = None
    if shuffled_path.exists():
        sh = pd.read_csv(shuffled_path)
        sh["key"] = sh["model"].map(LABEL_TO_KEY)
        sh = sh.dropna(subset=["key"]).set_index("key")
        rows = []
        for m in sh.index:
            if m == "logreg":
                continue
            rows.append(
                {
                    "Detektori": MODEL_LABELS[m],
                    "AP_kronologjik": sh.loc[m, "ap_chronological"],
                    "AP_i_perzier": sh.loc[m, "ap_shuffled_LEAKY"],
                    "fryrja": sh.loc[m, "ap_ratio_shuffled_over_chrono"],
                }
            )
        inflation = pd.DataFrame(rows).sort_values("fryrja", ascending=False)
        save_table(inflation, results_dir, "protocol_inflation")
        print(
            f"\nFryrja mesatare nga ndarja e përzier: "
            f"{inflation['fryrja'].mean():.2f}x (maksimumi {inflation['fryrja'].max():.2f}x)"
        )

    # --- Figure: single-split estimate against the fold distribution -------
    fig, ax = new_figure(figsize=(7.0, 4.6))
    order = table.sort_values("AP_8_folde")
    y = np.arange(len(order))
    for i, row in enumerate(order.itertuples(index=False)):
        key = LABEL_TO_KEY[row.Detektori]
        ax.plot(
            [max(row.AP_8_folde - row.sd_nder_folde, 0), row.AP_8_folde + row.sd_nder_folde],
            [i, i],
            color=model_color(key),
            linewidth=5,
            alpha=0.30,
            solid_capstyle="round",
        )
        ax.plot(
            row.AP_8_folde,
            i,
            "o",
            color=model_color(key),
            markersize=7,
            markeredgecolor="white",
            markeredgewidth=1.2,
            zorder=3,
        )
        ax.plot(row.AP_ndarje_e_vetme, i, "X", color="#0b0b0b", markersize=7, zorder=4)
    ax.set_yticks(y, order["Detektori"])
    ax.set_xlabel(AX["ap"])
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
                markersize=7,
                label="Mesatarja mbi 8 fold-e (±1 s.d.)",
            ),
            Line2D(
                [],
                [],
                marker="X",
                color="#0b0b0b",
                linestyle="",
                markersize=7,
                label="Vlerësimi nga një ndarje e vetme 70/30",
            ),
        ],
        loc="lower right",
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "protocol_comparison")

    verdict_lines = [
        f"Korrelacioni i renditjeve mes protokollit me një ndarje dhe atij me tetë "
        f"fold-e: Spearman rho = {rho:.3f} (p = {p_rho:.2g}).",
        f"Ndryshimi maksimal i rangut: {int(table['ndryshim_rangu'].abs().max())} pozicione; "
        f"{int((table['ndryshim_rangu'].abs() >= 2).sum())} nga {len(table)} detektorë "
        f"lëvizin dy ose më shumë pozicione.",
        f"Për {int((~table['brenda_1sd']).sum())} nga {len(table)} detektorë, vlerësimi nga "
        f"ndarja e vetme bie jashtë një devijimi standard të shpërndarjes nëpër fold-e.",
        f"Shpërhapja tipike nëpër fold-e është "
        f"{(table['sd_nder_folde'] / table['AP_8_folde']).mean():.0%} e vlerës mesatare, "
        f"e cila mbetet krejtësisht e padukshme nga një ndarje e vetme.",
    ]
    if inflation is not None:
        verdict_lines.append(
            f"Ndarja e përzier e fryn AP-në e metodave të pambikëqyrura mesatarisht "
            f"{inflation['fryrja'].mean():.2f} herë (deri në "
            f"{inflation['fryrja'].max():.2f} herë)."
        )
    (results_dir / "protocol_verdict.txt").write_text("\n".join(verdict_lines) + "\n")
    print("\n" + "\n".join(verdict_lines))
    write_manifest(results_dir, "exp17_protocol_comparison", cfg.raw)


if __name__ == "__main__":
    main()

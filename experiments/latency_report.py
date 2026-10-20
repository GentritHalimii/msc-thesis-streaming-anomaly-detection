"""Aggregate per-message latency CSVs from streaming runs into the
operational-results table and figures.

Reports distributions (p50/p95/p99 + mean), not just the mean. All numbers
are measured under a synthetic constant arrival rate — the table carries the
rate column and the thesis text qualifies every claim with it.
"""

import json

import matplotlib as mpl
import numpy as np
import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.report import (
    AX,
    CM,
    FULL_WIDTH,
    INK_2,
    MODEL_LABELS,
    MODEL_MARKERS,
    legend_above,
    model_color,
    new_figure,
    ordered_models,
    save_figure,
    save_table,
    value_grid,
)


def figure(table: pd.DataFrame, cfg) -> None:
    """Latency distribution per model and arrival rate, against the target.

    Each model is a dot at its mean with a line from the median to the 99th
    percentile, grouped by arrival rate. The one-second target is drawn on the
    same logarithmic axis, which is what makes the margin visible: on a linear
    axis either the target or the measurements would be squashed flat.
    """
    static = table[~table["prag_adaptiv"]]
    rates = sorted(static["rate_msg_s"].unique())
    models = ordered_models(static["model_key"].unique())
    offsets = np.linspace(-0.27, 0.27, len(models))

    fig, ax = new_figure(figsize=(FULL_WIDTH, 7.0 * CM))
    for offset, model in zip(offsets, models, strict=True):
        sub = static[static["model_key"] == model].set_index("rate_msg_s").loc[rates]
        x = np.arange(len(rates)) + offset
        color = model_color(model)
        ax.vlines(x, sub["e2e_ms_p50"], sub["e2e_ms_p99"], color=color, linewidth=1.6)
        ax.plot(
            x,
            sub["e2e_ms_mean"],
            linestyle="none",
            marker=MODEL_MARKERS.get(model, "o"),
            markersize=5,
            color=color,
            markeredgecolor="#ffffff",
            markeredgewidth=0.7,
            label=MODEL_LABELS.get(model, model),
        )
    ax.axhline(1000, color="#e34948", linewidth=1.0)
    ax.text(
        len(rates) - 0.5,
        1000 * 0.86,
        "objektivi: 1 sekondë",
        ha="right",
        va="top",
        fontsize=7.5,
        color="#b3352c",
    )
    ax.text(
        -0.5,
        560,
        "pika: mesatarja; vija: nga p50 deri te p99",
        ha="left",
        va="center",
        fontsize=7.5,
        color=INK_2,
    )
    ax.set_yscale("log")
    ax.set_ylim(10, 1500)
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xticks(range(len(rates)), [f"{int(r):,}".replace(",", " ") for r in rates])
    ax.set_xlim(-0.6, len(rates) - 0.4)
    ax.set_xlabel(AX["rate"])
    ax.set_ylabel(AX["latency_ms"])
    value_grid(ax, "y")
    legend_above(ax)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "latency_vs_rate")


def main(cfg=None):
    cfg = cfg or load_config()
    lat_dir = REPO_ROOT / cfg.results_dir / "latency"
    files = sorted(lat_dir.glob("latency_*.csv"))
    if not files:
        raise SystemExit(f"no latency CSVs in {lat_dir}; run experiments.run_streaming first")

    rows = []
    for path in files:
        df = pd.read_csv(path)
        summary_path = lat_dir / path.name.replace("latency_", "summary_").replace(".csv", ".json")
        summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
        tag, rate = path.stem.removeprefix("latency_").rsplit("_rate", 1)
        adaptive = tag.endswith("-adaptive")
        model = tag.removesuffix("-adaptive")
        rows.append(
            {
                "model": model,
                "prag_adaptiv": adaptive,
                "rate_msg_s": float(rate),
                "n": len(df),
                "e2e_ms_mean": df["e2e_ms"].mean(),
                "e2e_ms_p50": df["e2e_ms"].quantile(0.50),
                "e2e_ms_p95": df["e2e_ms"].quantile(0.95),
                "e2e_ms_p99": df["e2e_ms"].quantile(0.99),
                "infer_ms_mean": df["infer_ms"].mean(),
                "infer_ms_p99": df["infer_ms"].quantile(0.99),
                "batch_size_mean": df["batch_size"].mean(),
                "throughput_msg_s": summary.get("throughput_msg_s"),
                "cpu_percent_mean": summary.get("cpu_percent_mean"),
                "rss_peak_mb": summary.get("rss_peak_mb"),
            }
        )
    table = pd.DataFrame(rows).sort_values(["model", "prag_adaptiv", "rate_msg_s"])
    # The raw key drives the colour and line style; the display name is what
    # the document shows. Keeping both avoids a lookup failure in the figure.
    table["model_key"] = table["model"]
    table["model"] = table["model_key"].map(lambda m: MODEL_LABELS.get(m, m))
    # Achieved-vs-target throughput shows where the consumer stops keeping up.
    table["throughput_ratio"] = table["throughput_msg_s"] / table["rate_msg_s"]
    save_table(table.drop(columns=["model_key"]), REPO_ROOT / cfg.results_dir, "latency_summary")
    print(table.drop(columns=["model_key"]).to_string(index=False))

    figure(table, cfg)
    write_manifest(REPO_ROOT / cfg.results_dir, "latency_report", cfg.raw)


if __name__ == "__main__":
    main()

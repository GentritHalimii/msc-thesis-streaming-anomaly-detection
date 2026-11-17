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
from src.evaluation.operational import stream_throughput
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
        fontsize=9.5,
        color="#b3352c",
    )
    ax.text(
        -0.5,
        560,
        "pika: mesatarja; vija: nga p50 deri te p99",
        ha="left",
        va="center",
        fontsize=9.5,
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


def run_row(path, lat_dir) -> dict:
    """Distribution summary of one streaming run (one model, one rate)."""
    df = pd.read_csv(path)
    # A consumer that falls behind builds a queue, so its last messages wait
    # longer than its first; equal latency at both ends means it kept pace.
    tenth = max(len(df) // 10, 1)

    def sidecar(prefix: str) -> dict:
        side = path.with_name(path.name.replace("latency_", prefix).replace(".csv", ".json"))
        return json.loads(side.read_text()) if side.exists() else {}

    summary, producer = sidecar("summary_"), sidecar("producer_")
    tag, rate = path.stem.removeprefix("latency_").rsplit("_rate", 1)
    adaptive = tag.endswith("-adaptive")
    model = tag.removesuffix("-adaptive")
    return {
        "model": model,
        "prag_adaptiv": adaptive,
        "rate_msg_s": float(rate),
        "run": path.parent.name if path.parent != lat_dir else "rep1",
        "n": len(df),
        "e2e_ms_mean": df["e2e_ms"].mean(),
        "e2e_ms_p50": df["e2e_ms"].quantile(0.50),
        "e2e_ms_p95": df["e2e_ms"].quantile(0.95),
        "e2e_ms_p99": df["e2e_ms"].quantile(0.99),
        "infer_ms_mean": df["infer_ms"].mean(),
        "infer_ms_p99": df["infer_ms"].quantile(0.99),
        # Every message waits for its whole micro-batch to be scored, so the
        # inference share of a message's latency is the batch time, not the
        # per-message amortized time above. Averaged over messages.
        "infer_batch_ms_mean": (df["infer_ms"] * df["batch_size"]).mean(),
        "batch_size_mean": df["batch_size"].mean(),
        "e2e_ms_drift": df["e2e_ms"].iloc[-tenth:].mean() - df["e2e_ms"].iloc[:tenth].mean(),
        "throughput_msg_s": stream_throughput(df["produced_at_ns"], df["e2e_ms"]),
        "producer_rate_msg_s": producer.get("achieved_rate_msg_s", np.nan),
        "cpu_percent_mean": summary.get("cpu_percent_mean"),
        "rss_peak_mb": summary.get("rss_peak_mb"),
    }


def aggregate(runs: pd.DataFrame) -> pd.DataFrame:
    """One row per configuration: the mean over repeated runs, and how much
    the runs disagree. A single run has no spread to report, so the spread
    columns are left empty rather than set to zero."""
    keys = ["model", "prag_adaptiv", "rate_msg_s"]
    numeric = [c for c in runs.columns if c not in keys + ["run"]]
    table = runs.groupby(keys)[numeric].mean().reset_index()
    spread = runs.groupby(keys)[["e2e_ms_mean", "e2e_ms_p99", "throughput_msg_s"]].std()
    spread.columns = [f"{c}_sd" for c in spread.columns]
    table = table.join(spread, on=keys)
    table["n_runs"] = runs.groupby(keys)["run"].nunique().to_numpy()
    # The same unit as the offline cost in the benchmark table, so the two
    # can be compared: microseconds per message.
    table["infer_us_mean"] = 1000.0 * table["infer_ms_mean"]
    # Mean latency with the spread between runs, as one printable column.
    table["e2e_ms_mean_pm"] = [
        f"{m:.1f} ± {sd:.1f}" if sd == sd else f"{m:.1f}"
        for m, sd in zip(table["e2e_ms_mean"], table["e2e_ms_mean_sd"], strict=True)
    ]
    table = table.sort_values(keys)
    table["model_key"] = table["model"]
    table["model"] = table["model_key"].map(lambda m: MODEL_LABELS.get(m, m))
    # Achieved over target: 1.0 means the consumer kept pace with the arrival rate.
    table["throughput_ratio"] = table["throughput_msg_s"] / table["rate_msg_s"]
    return table


def collect(lat_dir) -> pd.DataFrame:
    """Every run under `lat_dir`: repeated runs live in rep*/ subfolders;
    a corpus measured once keeps its files at the top level."""
    files = sorted(lat_dir.glob("rep*/latency_*.csv")) or sorted(lat_dir.glob("latency_*.csv"))
    return pd.DataFrame([run_row(path, lat_dir) for path in files]) if files else pd.DataFrame()


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    lat_dir = results_dir / "latency"
    runs_dir = lat_dir / "runs" if (lat_dir / "runs").exists() else lat_dir
    runs = collect(runs_dir)
    if runs.empty:
        raise SystemExit(f"no latency CSVs in {lat_dir}; run experiments.run_streaming first")
    save_table(runs, results_dir, "latency_runs")

    table = aggregate(runs)
    save_table(table.drop(columns=["model_key"]), results_dir, "latency_summary")
    print(table.drop(columns=["model_key"]).to_string(index=False))
    figure(table, cfg)

    # Rates past the operating range, run to find where one consumer stops
    # keeping pace. They answer a different question from the table above,
    # so they are summarised apart from it.
    capacity_runs = collect(lat_dir / "capacity")
    if not capacity_runs.empty:
        save_table(capacity_runs, results_dir, "capacity_runs")
        capacity = aggregate(capacity_runs)
        save_table(capacity.drop(columns=["model_key"]), results_dir, "capacity_summary")
        print(capacity.drop(columns=["model_key"]).to_string(index=False))
    write_manifest(results_dir, "latency_report", cfg.raw)


if __name__ == "__main__":
    main()

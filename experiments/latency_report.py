"""Aggregate per-message latency CSVs from streaming runs into the
operational-results table and figures.

Reports distributions (p50/p95/p99 + mean), not just the mean. All numbers
are measured under a synthetic constant arrival rate — the table carries the
rate column and the thesis text qualifies every claim with it.
"""

import json

import pandas as pd

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.evaluation.report import model_plot_kwargs, new_figure, save_figure, save_table


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
        model, rate = path.stem.removeprefix("latency_").rsplit("_rate", 1)
        rows.append(
            {
                "model": model,
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
    table = pd.DataFrame(rows).sort_values(["model", "rate_msg_s"])
    save_table(table, REPO_ROOT / cfg.results_dir, "latency_summary")
    print(table.to_string(index=False))

    fig, ax = new_figure()
    for model in table["model"].unique():
        sub = table[table["model"] == model].sort_values("rate_msg_s")
        kw = model_plot_kwargs(model)
        ax.plot(sub["rate_msg_s"], sub["e2e_ms_p99"], marker="o", markersize=4, **kw)
        kw_p50 = {**kw, "alpha": 0.45, "label": None}
        ax.plot(sub["rate_msg_s"], sub["e2e_ms_p50"], marker="o", markersize=3, **kw_p50)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("replay rate (msg/s, synthetic constant arrivals)")
    ax.set_ylabel("end-to-end latency (ms) — p99 solid, p50 faded")
    ax.axhline(1000, color="#c3c2b7", linewidth=1)
    ax.annotate(
        "1 s target",
        xy=(0.02, 0.97),
        xycoords="axes fraction",
        fontsize=8,
        color="#898781",
        va="top",
    )
    ax.legend()
    save_figure(fig, REPO_ROOT / cfg.results_dir, "latency_vs_rate")
    write_manifest(REPO_ROOT / cfg.results_dir, "latency_report", cfg.raw)


if __name__ == "__main__":
    main()

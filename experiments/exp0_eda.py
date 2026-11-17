"""Exploratory characterisation of the dataset.

Everything here feeds the data chapter of the thesis. Three questions guide
it: how extreme is the imbalance, what temporal structure does the stream
have, and how much per-feature signal exists at all — the last one matters
because 28 of the 29 features are anonymised principal components and cannot
be reasoned about from domain knowledge.
"""

import matplotlib as mpl
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from src.config import REPO_ROOT, load_config
from src.data.load import FEATURE_COLUMNS, load_transactions
from src.evaluation.manifest import write_manifest
from src.evaluation.report import (
    BASELINE,
    CLASS_COLORS,
    CM,
    FULL_WIDTH,
    INK_2,
    MUTED,
    legend_above,
    new_figure,
    percent_axis,
    save_figure,
    save_table,
    value_grid,
)


def _thousands(value: float, decimals: int = 0) -> str:
    """Albanian grouping: a non-breaking space between thousands, a point for
    decimals, so the figure matches the decimal point used everywhere else."""
    return f"{value:,.{decimals}f}".replace(",", "\u00a0")


def overview_table(df: pd.DataFrame) -> pd.DataFrame:
    fraud = df[df["Class"] == 1]
    legit = df[df["Class"] == 0]
    f_amt, l_amt = fraud["Amount"], legit["Amount"]
    return pd.DataFrame(
        [
            {"treguesi": "Transaksione gjithsej", "vlera": _thousands(len(df))},
            {"treguesi": "Mashtrime", "vlera": _thousands(len(fraud))},
            {"treguesi": "Norma e mashtrimit", "vlera": f"{100 * df['Class'].mean():.3f}%"},
            {
                "treguesi": "Raporti legjitime:mashtrime",
                "vlera": f"{len(legit) / len(fraud):.0f}:1",
            },
            {
                "treguesi": "Kohëzgjatja e regjistrimit",
                "vlera": f"{df['Time'].max() / 3600:.1f} orë",
            },
            {"treguesi": "Shuma mesatare (legjitime)", "vlera": f"{l_amt.mean():.2f} EUR"},
            {"treguesi": "Shuma mesatare (mashtrime)", "vlera": f"{f_amt.mean():.2f} EUR"},
            {"treguesi": "Mediana e shumës (legjitime)", "vlera": f"{l_amt.median():.2f} EUR"},
            {"treguesi": "Mediana e shumës (mashtrime)", "vlera": f"{f_amt.median():.2f} EUR"},
            {"treguesi": "Vlera totale e mashtrimeve", "vlera": f"{_thousands(f_amt.sum())} EUR"},
            {
                "treguesi": "Vlera maksimale e një mashtrimi",
                "vlera": f"{_thousands(f_amt.max(), 2)} EUR",
            },
            {"treguesi": "Mashtrime me shumë zero", "vlera": f"{int((f_amt == 0).sum())}"},
        ]
    )


def figure_volume_and_fraud(df: pd.DataFrame, cfg):
    """Transaction volume and fraud incidence share one time axis: the point
    is that fraud does not follow the daily volume cycle."""
    hours = df["Time"] / 3600.0
    bins = np.arange(0, np.ceil(hours.max()) + 1, 1.0)
    vol, _ = np.histogram(hours, bins=bins)
    fr, _ = np.histogram(hours[df["Class"] == 1], bins=bins)
    centres = bins[:-1] + 0.5

    fig, (ax1, ax2) = new_figure(
        nrows=2,
        sharex=True,
        figsize=(FULL_WIDTH, 7.6 * CM),
        gridspec_kw={"height_ratios": [1.6, 1]},
    )
    # The quiet hours of each night, read off the volume curve itself: the
    # stream starts at midnight, so these are the small hours of both days.
    for ax in (ax1, ax2):
        for start in (0, 24):
            ax.axvspan(start + 1, start + 7, color="#f1f0eb", zorder=0, linewidth=0)
    ax1.text(4, vol.max() * 0.98, "natë", ha="center", va="top", fontsize=9.5, color=MUTED)
    ax1.text(28, vol.max() * 0.98, "natë", ha="center", va="top", fontsize=9.5, color=MUTED)

    ax1.fill_between(centres, vol, color=CLASS_COLORS[0], alpha=0.15, linewidth=0)
    ax1.plot(centres, vol, color=CLASS_COLORS[0], linewidth=1.5)
    ax1.set_ylabel("Transaksione në orë")
    ax1.set_ylim(0, vol.max() * 1.08)
    ax1.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", " "))
    )

    ax2.bar(centres, fr, width=0.8, color=CLASS_COLORS[1], linewidth=0)
    ax2.set_ylabel("Mashtrime në orë")
    ax2.set_xlabel("Koha nga transaksioni i parë (orë)")
    ax2.set_xticks(range(0, 49, 6))
    ax2.set_xlim(0, 48)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_volume_and_fraud")


def figure_amounts(df: pd.DataFrame, cfg):
    """Empirical distribution of the amount for each class.

    An ECDF rather than a histogram: the classes differ in size by a factor of
    almost six hundred, the amounts span six orders of magnitude, and some of
    them are exactly zero. A symmetric-log axis keeps the zeros on the chart,
    and the medians can be read straight off the 50 per cent line.
    """
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.4 * CM))
    for cls, label in ((0, "Legjitime"), (1, "Mashtrime")):
        amounts = np.sort(df.loc[df["Class"] == cls, "Amount"].to_numpy())
        ecdf = np.arange(1, len(amounts) + 1) / len(amounts)
        ax.step(amounts, ecdf, where="post", color=CLASS_COLORS[cls], linewidth=1.6, label=label)
        median = float(np.median(amounts))
        ax.plot([median], [0.5], marker="o", markersize=4.5, color=CLASS_COLORS[cls], zorder=4)
        # Placed in the empty corner on each curve's own side, with a leader,
        # so neither label sits on the other class's curve.
        target = (2.2, 0.68) if cls == 1 else (70.0, 0.3)
        ax.annotate(
            f"mediana {median:.2f} EUR",
            xy=(median, 0.5),
            xytext=target,
            fontsize=9.5,
            color=INK_2,
            ha="center",
            va="center",
            arrowprops={"arrowstyle": "-", "color": BASELINE, "linewidth": 0.7},
        )
    ax.axhline(0.5, color=BASELINE, linewidth=0.7, zorder=1)
    ax.set_xscale("symlog", linthresh=1.0, linscale=0.5)
    ax.set_xlim(0, df["Amount"].max() * 1.1)
    ax.set_xticks([0, 1, 10, 100, 1000, 10000], ["0", "1", "10", "100", "1 000", "10 000"])
    ax.set_xlabel("Shuma e transaksionit (EUR, shkallë logaritmike pas 1)")
    ax.set_ylabel("Pjesa kumulative")
    percent_axis(ax, "y")
    value_grid(ax, "both")
    legend_above(ax)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_amounts")


def figure_feature_signal(df: pd.DataFrame, cfg) -> pd.DataFrame:
    """Univariate separability per feature. With anonymised components this is
    the only interpretability available before modelling."""
    y = df["Class"].to_numpy()
    rows = []
    for col in FEATURE_COLUMNS:
        auc = roc_auc_score(y, df[col].to_numpy())
        rows.append({"feature": col, "auc": auc, "abs_auc_gap": abs(auc - 0.5)})
    tab = pd.DataFrame(rows).sort_values("abs_auc_gap", ascending=False)
    save_table(tab, REPO_ROOT / cfg.results_dir, "eda_feature_signal")

    top = tab.head(15).iloc[::-1]
    fig, ax = new_figure(figsize=(FULL_WIDTH, 9.0 * CM))
    ypos = np.arange(len(top))
    ax.barh(
        ypos,
        top["auc"] - 0.5,
        left=0.5,
        height=0.62,
        color=[CLASS_COLORS[0] if a > 0.5 else CLASS_COLORS[1] for a in top["auc"]],
    )
    ax.axvline(0.5, color=INK_2, lw=0.8)
    ax.set_yticks(ypos, top["feature"])
    ax.set_xlabel("ROC-AUC njëvariablëshe (0.5 = pa sinjal)")
    value_grid(ax, "x")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_feature_signal")
    return tab


def figure_correlation(df: pd.DataFrame, cfg):
    """The V-features are principal components, so they should be almost
    uncorrelated; Amount is not and shows it.

    Only the lower triangle is drawn and the diagonal is left out: the upper
    triangle repeats the lower one, and a diagonal of ones would set the
    colour scale and wash out the only correlations worth seeing.
    """
    corr = df[FEATURE_COLUMNS].corr().to_numpy()
    off = corr[~np.eye(len(corr), dtype=bool)]
    limit = float(np.ceil(np.abs(off).max() * 10) / 10)
    shown = np.where(np.tril(np.ones_like(corr, dtype=bool), k=-1), corr, np.nan)

    # Row 0 and the last column would be empty under a strict lower triangle.
    shown = shown[1:, :-1]
    fig, ax = new_figure(figsize=(12.0 * CM, 10.6 * CM))
    im = ax.imshow(shown, cmap="RdBu_r", vmin=-limit, vmax=limit)
    ax.set_xticks(range(shown.shape[1]), FEATURE_COLUMNS[:-1], rotation=90, fontsize=8.5)
    ax.set_yticks(range(shown.shape[0]), FEATURE_COLUMNS[1:], fontsize=8.5)
    ax.tick_params(length=0)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.grid(False)
    bar = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    bar.set_label("Korrelacioni i Pearson-it")
    bar.outline.set_visible(False)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_correlation")
    return float(np.abs(off).max()), float(np.abs(off).mean())


def figure_hourly_rate(df: pd.DataFrame, cfg):
    """Fraud rate by hour of day, pooled over the two days."""
    hod = ((df["Time"] % 86400) // 3600).astype(int)
    tab = df.groupby(hod)["Class"].agg(["mean", "size", "sum"])
    overall = float(df["Class"].mean())
    fig, ax = new_figure(figsize=(FULL_WIDTH, 6.0 * CM))
    ax.bar(tab.index, tab["mean"], width=0.72, color=CLASS_COLORS[1], linewidth=0)
    ax.axhline(overall, color=INK_2, lw=0.9, ls=(0, (4, 2)), zorder=4)
    # Over the afternoon hours, whose bars all sit below the line.
    ax.text(
        12.6,
        overall * 1.3,
        f"mesatarja për të gjitha orët: {100 * overall:.3f}%",
        ha="left",
        va="bottom",
        fontsize=9.5,
        color=INK_2,
    )
    ax.set_xlabel("Ora e ditës")
    ax.set_ylabel("Norma e mashtrimit")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlim(-0.6, 23.6)
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(0.005))
    percent_axis(ax, "y", decimals=1)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_hourly_rate")
    return tab


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)

    overview = overview_table(df)
    save_table(overview, results_dir, "eda_overview")
    print(overview.to_string(index=False))

    figure_volume_and_fraud(df, cfg)
    figure_amounts(df, cfg)
    signal = figure_feature_signal(df, cfg)
    max_corr, mean_corr = figure_correlation(df, cfg)
    hourly = figure_hourly_rate(df, cfg)
    save_table(
        hourly.reset_index().rename(
            columns={
                "Time": "ora",
                "mean": "norma_mashtrimit",
                "size": "transaksione",
                "sum": "mashtrime",
            }
        ),
        results_dir,
        "eda_hourly",
        float_fmt="%.5f",
    )

    print(
        f"\nVeçoritë me sinjalin më të fortë njëvariablësh: {', '.join(signal.head(5)['feature'])}"
    )
    print(f"Korrelacioni jashtë-diagonal: max |r| = {max_corr:.3f}, mesatar |r| = {mean_corr:.3f}")
    peak = hourly["mean"].idxmax()
    print(f"Ora me normën më të lartë të mashtrimit: {peak}:00 ({100 * hourly['mean'].max():.3f}%)")
    write_manifest(results_dir, "exp0_eda", cfg.raw)


if __name__ == "__main__":
    main()

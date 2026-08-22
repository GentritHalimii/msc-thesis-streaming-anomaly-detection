"""Exploratory characterisation of the dataset.

Everything here feeds the data chapter of the thesis. Three questions guide
it: how extreme is the imbalance, what temporal structure does the stream
have, and how much per-feature signal exists at all — the last one matters
because 28 of the 29 features are anonymised principal components and cannot
be reasoned about from domain knowledge.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from src.config import REPO_ROOT, load_config
from src.data.load import FEATURE_COLUMNS, load_transactions
from src.evaluation.manifest import write_manifest
from src.evaluation.report import new_figure, save_figure, save_table

BLUE, RED, GREY = "#2a78d6", "#e34948", "#898781"


def overview_table(df: pd.DataFrame) -> pd.DataFrame:
    fraud = df[df["Class"] == 1]
    legit = df[df["Class"] == 0]
    f_amt, l_amt = fraud["Amount"], legit["Amount"]
    return pd.DataFrame(
        [
            {"treguesi": "Transaksione gjithsej", "vlera": f"{len(df):,}"},
            {"treguesi": "Mashtrime", "vlera": f"{len(fraud):,}"},
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
            {"treguesi": "Vlera totale e mashtrimeve", "vlera": f"{f_amt.sum():,.0f} EUR"},
            {"treguesi": "Vlera maksimale e një mashtrimi", "vlera": f"{f_amt.max():,.2f} EUR"},
            {"treguesi": "Mashtrime me shumë zero", "vlera": f"{int((f_amt == 0).sum())}"},
        ]
    )


def figure_volume_and_fraud(df: pd.DataFrame, cfg):
    """Transaction volume and fraud incidence share one time axis: the point
    is that fraud does not follow the daily volume cycle."""
    hours = df["Time"] / 3600.0
    bins = np.arange(0, hours.max() + 1, 1.0)
    vol, _ = np.histogram(hours, bins=bins)
    fr, _ = np.histogram(hours[df["Class"] == 1], bins=bins)
    centres = bins[:-1] + 0.5

    fig, (ax1, ax2) = new_figure(
        nrows=2, sharex=True, figsize=(7.0, 4.8), gridspec_kw={"height_ratios": [2, 1]}
    )
    ax1.fill_between(centres, vol, color=BLUE, alpha=0.18, linewidth=0)
    ax1.plot(centres, vol, color=BLUE, linewidth=1.8)
    ax1.set_ylabel("Transaksione / orë")
    ax1.text(
        0.985,
        0.92,
        "cikli ditë–natë i vëllimit",
        transform=ax1.transAxes,
        ha="right",
        fontsize=8.5,
        color="#52514e",
    )

    ax2.bar(centres, fr, width=0.85, color=RED, alpha=0.85, linewidth=0)
    ax2.set_ylabel("Mashtrime / orë")
    ax2.set_xlabel("Koha nga transaksioni i parë (orë)")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_volume_and_fraud")


def figure_amounts(df: pd.DataFrame, cfg):
    fig, (ax1, ax2) = new_figure(ncols=2, figsize=(7.2, 3.6))
    legit = df.loc[df["Class"] == 0, "Amount"]
    fraud = df.loc[df["Class"] == 1, "Amount"]
    bins = np.logspace(-2, np.log10(max(df["Amount"].max(), 1.0)), 45)
    ax1.hist(
        np.clip(legit, 0.01, None),
        bins=bins,
        color=BLUE,
        alpha=0.65,
        density=True,
        label="Legjitime",
        linewidth=0,
    )
    ax1.hist(
        np.clip(fraud, 0.01, None),
        bins=bins,
        color=RED,
        alpha=0.65,
        density=True,
        label="Mashtruese",
        linewidth=0,
    )
    ax1.set_xscale("log")
    ax1.set_xlabel("Shuma e transaksionit (EUR, shkallë log)")
    ax1.set_ylabel("Densiteti")
    ax1.legend()

    parts = ax2.boxplot(
        [np.clip(legit, 0.01, None), np.clip(fraud, 0.01, None)],
        patch_artist=True,
        widths=0.5,
        medianprops={"color": "#0b0b0b", "linewidth": 1.4},
        flierprops={
            "marker": "o",
            "markersize": 2,
            "markerfacecolor": GREY,
            "markeredgecolor": "none",
            "alpha": 0.3,
        },
    )
    for patch, colour in zip(parts["boxes"], [BLUE, RED], strict=True):
        patch.set_facecolor(colour)
        patch.set_alpha(0.35)
        patch.set_edgecolor(colour)
    ax2.set_yscale("log")
    ax2.set_xticks([1, 2], ["Legjitime", "Mashtruese"])
    ax2.set_ylabel("Shuma (EUR, shkallë log)")
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
    fig, ax = new_figure(figsize=(6.2, 4.6))
    ypos = np.arange(len(top))
    ax.barh(
        ypos,
        top["auc"] - 0.5,
        left=0.5,
        height=0.62,
        color=[BLUE if a > 0.5 else RED for a in top["auc"]],
    )
    ax.axvline(0.5, color="#52514e", lw=1)
    ax.set_yticks(ypos, top["feature"])
    ax.set_xlabel("ROC-AUC njëvariablëshe (0.5 = pa sinjal)")
    ax.grid(axis="y", visible=False)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_feature_signal")
    return tab


def figure_correlation(df: pd.DataFrame, cfg):
    """The V-features are principal components, so they should be almost
    uncorrelated; Amount is not and shows it."""
    corr = df[FEATURE_COLUMNS].corr().to_numpy()
    fig, ax = new_figure(figsize=(5.8, 5.0))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(
        range(0, len(FEATURE_COLUMNS), 2),
        [FEATURE_COLUMNS[i] for i in range(0, len(FEATURE_COLUMNS), 2)],
        rotation=90,
        fontsize=6.5,
    )
    ax.set_yticks(
        range(0, len(FEATURE_COLUMNS), 2),
        [FEATURE_COLUMNS[i] for i in range(0, len(FEATURE_COLUMNS), 2)],
        fontsize=6.5,
    )
    ax.grid(visible=False)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Korrelacioni i Pearson-it")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "eda_correlation")
    off = corr[~np.eye(len(corr), dtype=bool)]
    return float(np.abs(off).max()), float(np.abs(off).mean())


def figure_hourly_rate(df: pd.DataFrame, cfg):
    """Fraud rate by hour of day, pooled over the two days."""
    hod = ((df["Time"] % 86400) // 3600).astype(int)
    tab = df.groupby(hod)["Class"].agg(["mean", "size", "sum"])
    fig, ax = new_figure(figsize=(6.8, 3.6))
    ax.bar(tab.index, 100 * tab["mean"], width=0.75, color=RED, alpha=0.85, linewidth=0)
    ax.axhline(100 * df["Class"].mean(), color="#52514e", lw=1.2, ls="--")
    ax.text(0.4, 100 * df["Class"].mean() * 1.15, "mesatarja globale", fontsize=8, color="#52514e")
    ax.set_xlabel("Ora e ditës")
    ax.set_ylabel("Norma e mashtrimit (%)")
    ax.set_xticks(range(0, 24, 2))
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

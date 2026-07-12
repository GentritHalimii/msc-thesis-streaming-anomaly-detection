"""Table (CSV + booktabs LaTeX) and figure (300-dpi PDF + PNG) output helpers.

Figure style: fixed color per model across every figure (color follows the
entity), thin recessive grid, legend always present for multi-series plots.
Palette validated for CVD separation on a white print surface; the aqua slot
is sub-3:1 contrast, which is acceptable because every figure's values also
exist in a CSV/LaTeX table (relief rule).
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

# Fixed model -> color assignment, identical in every figure. The LR reference
# is deliberately gray + dashed: it is a supervised upper bound, not a peer.
MODEL_COLORS = {
    "iforest": "#2a78d6",
    "autoencoder": "#1baf7a",
    "ocsvm": "#4a3aa7",
    "ensemble_avg": "#e34948",
    "ensemble_vote": "#eb6834",
    "logreg": "#52514e",
}
MODEL_LINESTYLES = {"logreg": "--"}
MODEL_LABELS = {
    "iforest": "Isolation Forest",
    "autoencoder": "Autoencoder",
    "ocsvm": "One-Class SVM",
    "logreg": "LR (supervised ref.)",
    "ensemble_avg": "Ensemble (avg.)",
    "ensemble_vote": "Ensemble (vote)",
}

STYLE = {
    "figure.figsize": (5.5, 4.0),
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "lines.linewidth": 2.0,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
    "axes.grid": True,
    "grid.color": "#e1e0d9",
    "grid.linewidth": 0.8,
    "grid.linestyle": "-",
    "axes.edgecolor": "#c3c2b7",
    "axes.linewidth": 0.8,
    "axes.labelcolor": "#52514e",
    "xtick.color": "#898781",
    "ytick.color": "#898781",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "legend.fontsize": 9,
}


def new_figure(**kwargs):
    mpl.rcParams.update(STYLE)
    return plt.subplots(**kwargs)


def model_plot_kwargs(model_name: str) -> dict:
    return {
        "color": MODEL_COLORS[model_name],
        "linestyle": MODEL_LINESTYLES.get(model_name, "-"),
        "label": MODEL_LABELS[model_name],
    }


def _latex_escape(s: str) -> str:
    for ch in ["&", "%", "#", "_"]:
        s = s.replace(ch, "\\" + ch)
    return s


def _booktabs(df: pd.DataFrame, float_fmt: str) -> str:
    def fmt(v):
        if isinstance(v, float):
            return float_fmt % v
        return _latex_escape(str(v))

    cols = " & ".join(_latex_escape(str(c)) for c in df.columns)
    rows = [" & ".join(fmt(v) for v in row) + r" \\" for row in df.itertuples(index=False)]
    body = "\n".join(rows)
    colspec = "l" * df.select_dtypes(exclude="number").shape[1] + "r" * (
        df.shape[1] - df.select_dtypes(exclude="number").shape[1]
    )
    return (
        f"\\begin{{tabular}}{{{colspec}}}\n\\toprule\n{cols} \\\\\n"
        f"\\midrule\n{body}\n\\bottomrule\n\\end{{tabular}}\n"
    )


def save_table(df: pd.DataFrame, results_dir: Path | str, name: str, float_fmt: str = "%.4f"):
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{name}.csv"
    df.to_csv(csv_path, index=False, float_format=float_fmt)
    (out_dir / f"{name}.tex").write_text(_booktabs(df, float_fmt))
    return csv_path


def save_figure(fig, results_dir: Path | str, name: str):
    fig_dir = Path(results_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_dir / f"{name}.pdf")
    fig.savefig(fig_dir / f"{name}.png")
    plt.close(fig)
    return fig_dir / f"{name}.pdf"

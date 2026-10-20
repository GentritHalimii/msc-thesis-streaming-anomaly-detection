"""Tables (CSV + booktabs LaTeX) and figures (300-dpi PDF + PNG) for the thesis.

Figure design decisions worth stating once here rather than repeating at every
call site:

* Figures are drawn at the size they are printed. The text block of the thesis
  is 15 cm wide, so a full-width figure is created 15 cm wide and inserted at
  15 cm: a 9 pt label in the code is a 9 pt label on paper. Drawing large and
  letting the document shrink the picture is how small annotations ended up
  unreadable in the first build.
* Gridlines sit behind the data (``axes.axisbelow``) and only along the value
  axis. A grid drawn over bars and markers competes with the marks it is
  supposed to help read.
* One colour per detector, in a fixed order, validated for colour-vision
  deficiency as a set: Isolation Forest blue, Autoencoder aqua, One-Class SVM
  violet. The supervised reference is always grey and dash-dotted so it can
  never be mistaken for one of the unsupervised detectors, and the linear PCA
  ablation is dotted.
* Spread across folds is shown as the fold values themselves (small dots) or
  as the range they span, not as a symmetric standard-deviation bar. Average
  Precision lives in [0, 1] and is strongly skewed across folds, so a ±1 s.d.
  bar routinely runs below zero and suggests values that cannot occur.
* Axis labels are in Albanian because the figures are embedded in an Albanian
  thesis; algorithm names and the terms the thesis keeps in English (fold,
  recall, precision, unsupervised) stay in English.
"""

import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors

from src.models.build import FAMILY_OF

CM = 1 / 2.54  # inches per centimetre
TEXT_WIDTH_CM = 15.0
FULL_WIDTH = TEXT_WIDTH_CM * CM

# Ink and chrome, light surface.
INK = "#0b0b0b"
INK_2 = "#3d3c39"  # axis labels and tick labels: darker than screen grey, for print
MUTED = "#76756f"
GRID = "#e4e3dc"
BASELINE = "#b9b8ae"
SURFACE = "#ffffff"

# Validated categorical slots, one hue per detector (checked all-pairs for
# colour-vision deficiency: worst CVD distance 13.0, normal-vision 16.3).
MODEL_COLORS = {
    "iforest": "#2a78d6",
    "autoencoder": "#1baf7a",
    "ocsvm": "#4a3aa7",
    "pca_recon": "#008300",
    "logreg": "#52514e",
    "ensemble_avg": "#e34948",
    "ensemble_vote": "#eb6834",
    "ensemble_rank": "#e87ba4",
    "ensemble_greedy": "#eda100",
    "ensemble_max": "#d55181",
}
FAMILY_COLORS = {
    "isolation": "#2a78d6",
    "reconstruction": "#1baf7a",
    "boundary": "#4a3aa7",
}
REFERENCE_COLOR = "#52514e"
# The two classes of the data set, used wherever a figure separates them.
CLASS_COLORS = {0: "#2a78d6", 1: "#e34948"}

MODEL_ORDER = ["iforest", "autoencoder", "ocsvm", "logreg"]

MODEL_LINESTYLES = {
    "iforest": "-",
    "autoencoder": "-",
    "ocsvm": "-",
    "pca_recon": ":",
    "logreg": "-.",
}
MODEL_MARKERS = {
    "iforest": "o",
    "autoencoder": "s",
    "ocsvm": "D",
    "pca_recon": "v",
    "logreg": "^",
}

MODEL_LABELS = {
    "iforest": "Isolation Forest",
    "autoencoder": "Autoencoder",
    "ocsvm": "One-Class SVM",
    "pca_recon": "PCA lineare (ablacion)",
    "logreg": "LR (referencë)",
    "ensemble_avg": "Ansambël (mesatare z)",
    "ensemble_vote": "Ansambël (votim)",
    "ensemble_rank": "Ansambël (rang)",
    "ensemble_greedy": "Ansambël (greedy)",
    "ensemble_max": "Ansambël (maksimum)",
}
# Display name -> registry key, for tables that store the display name.
MODEL_KEYS = {label: key for key, label in MODEL_LABELS.items()}

FAMILY_LABELS = {
    "isolation": "Izolim",
    "reconstruction": "Rindërtim",
    "boundary": "Kufi vendimi",
}

# Albanian axis vocabulary, kept in one place so every figure agrees.
AX = {
    "ap": "Average Precision (AP)",
    "precision": "Precision",
    "recall": "Recall",
    "fpr": "Norma e alarmeve false (FPR)",
    "tpr": "Norma e zbulimit (TPR)",
    "f1": "F1",
    "fold": "Fold",
    "contamination": "Kontaminimi (prag nga shpërndarja e trajnimit)",
    "budget": "Buxheti i alarmeve për bllok (k)",
    "rate": "Ritmi i mbërritjes (mesazhe/s)",
    "latency_ms": "Vonesa end-to-end (ms)",
    "savings": "Kursimet neto (pjesë e maksimumit)",
    "amount_recall": "Recall i vlerës monetare",
    "rank": "Rangu mesatar",
    "train_size": "Madhësia e dritares së trajnimit (transaksione)",
    "epochs": "Epoka",
    "latent": "Dimensioni latent",
}

STYLE = {
    "figure.figsize": (FULL_WIDTH, 3.4),
    "figure.dpi": 120,
    "figure.facecolor": SURFACE,
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.h_pad": 0.04,
    "figure.constrained_layout.w_pad": 0.04,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
    "savefig.facecolor": SURFACE,
    "pdf.fonttype": 42,
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.titlepad": 5,
    "axes.labelsize": 9,
    "axes.labelcolor": INK_2,
    "axes.labelpad": 3,
    "axes.edgecolor": BASELINE,
    "axes.linewidth": 0.8,
    "axes.facecolor": SURFACE,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "grid.linestyle": "-",
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "xtick.color": BASELINE,
    "ytick.color": BASELINE,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.minor.size": 1.6,
    "ytick.minor.size": 1.6,
    "lines.linewidth": 1.6,
    "lines.markersize": 4.5,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
    "patch.linewidth": 0,
    "legend.frameon": False,
    "legend.fontsize": 8,
    "legend.handlelength": 2.0,
    "legend.handletextpad": 0.5,
    "legend.columnspacing": 1.4,
    "legend.borderaxespad": 0.2,
    "image.cmap": "Blues",
}


def apply_style() -> None:
    mpl.rcParams.update(STYLE)


def new_figure(**kwargs):
    """`plt.subplots` under the thesis style; full text width by default."""
    apply_style()
    kwargs.setdefault("figsize", STYLE["figure.figsize"])
    return plt.subplots(**kwargs)


def model_color(name: str) -> str:
    if name in MODEL_COLORS:
        return MODEL_COLORS[name]
    return FAMILY_COLORS[FAMILY_OF[name]]


def model_linestyle(name: str) -> str:
    return MODEL_LINESTYLES.get(name, "-")


def model_plot_kwargs(name: str, with_label: bool = True, markers: bool = False) -> dict:
    kw = {"color": model_color(name), "linestyle": model_linestyle(name)}
    if markers:
        kw |= {
            "marker": MODEL_MARKERS.get(name, "o"),
            "markersize": 4.5,
            "markeredgecolor": SURFACE,
            "markeredgewidth": 0.7,
        }
    if with_label:
        kw["label"] = MODEL_LABELS.get(name, name)
    return kw


def ordered_models(names) -> list[str]:
    """Registry keys in the thesis order, unknown names last."""
    names = list(names)
    known = [m for m in MODEL_ORDER if m in names]
    return known + [m for m in names if m not in known]


def value_grid(ax, axis: str = "y") -> None:
    """Gridlines only along the value axis."""
    ax.grid(False)
    ax.grid(True, axis=axis)


def legend_above(ax, handles=None, labels=None, ncol: int | None = None, **kwargs):
    """Legend centred in a row above the plotting area.

    Above is the one place that never collides with data, and putting it in
    the same place in every figure means the reader stops looking for it.
    """
    if handles is None:
        handles, labels = ax.get_legend_handles_labels()
    ncol = ncol or len(handles)
    return ax.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=ncol,
        frameon=False,
        **kwargs,
    )


def fig_legend_above(fig, handles, labels, ncol: int | None = None, **kwargs):
    """Shared legend for a multi-panel figure, above all panels."""
    return fig.legend(
        handles,
        labels,
        loc="outside upper center",
        ncol=ncol or len(handles),
        frameon=False,
        **kwargs,
    )


def text_color_for(background) -> str:
    """Black or white text, whichever reads better on the given fill."""
    r, g, b = mcolors.to_rgb(background)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return INK if luminance > 0.55 else SURFACE


def annotate_cells(ax, values: np.ndarray, image, fmt: str = "{:.3f}", fontsize: float = 7.5):
    """Write each cell's value on a heatmap in a colour that stays legible."""
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            if not np.isfinite(value):
                continue
            ax.text(
                j,
                i,
                fmt.format(value),
                ha="center",
                va="center",
                fontsize=fontsize,
                color=text_color_for(image.cmap(image.norm(value))),
            )


def outline_cell(ax, row: int, col: int, color: str = INK, lw: float = 1.4, ls: str = "-"):
    """Frame one heatmap cell, used to mark the default or the optimum."""
    ax.add_patch(
        mpl.patches.Rectangle(
            (col - 0.5, row - 0.5), 1, 1, fill=False, edgecolor=color, linewidth=lw, linestyle=ls
        )
    )


def strip(ax, y: float, values, color: str, jitter: float = 0.12, size: float = 14, seed: int = 0):
    """Individual fold values as small dots around a row, horizontally laid out."""
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    offsets = rng.uniform(-jitter, jitter, size=len(values))
    ax.scatter(
        values,
        np.full(len(values), y) + offsets,
        s=size,
        color=color,
        alpha=0.55,
        linewidths=0,
        zorder=3,
    )


def strip_vertical(
    ax, x: float, values, color: str, jitter: float = 0.012, size: float = 12, seed: int = 0
):
    """Fold values as small dots above one x position, with a little jitter."""
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    offsets = rng.uniform(-jitter, jitter, size=len(values))
    ax.scatter(
        np.full(len(values), x) + offsets,
        values,
        s=size,
        color=color,
        alpha=0.45,
        linewidths=0,
        zorder=3,
    )


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def percent_axis(ax, axis: str = "y", decimals: int = 0) -> None:
    formatter = mpl.ticker.PercentFormatter(xmax=1.0, decimals=decimals)
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(formatter)


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
    n_text = df.select_dtypes(exclude="number").shape[1]
    colspec = "l" * n_text + "r" * (df.shape[1] - n_text)
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

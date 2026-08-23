"""Tables (CSV + booktabs LaTeX) and figures (300-dpi PDF + PNG) for the thesis.

Figure design decisions worth stating once here rather than repeating at every
call site:

* Colour encodes the detector *family*, not the individual detector. Fourteen
  categorical hues would be unreadable and unsafe for colour-vision
  deficiency; six families sit comfortably inside a validated palette, and the
  family is what the comparison is actually about. Members of a family are
  separated by line style, which also survives greyscale printing.
* The supervised reference is always grey and dash-dotted so it can never be
  mistaken for one of the unsupervised competitors.
* Axis labels are in Albanian because the figures are embedded in an Albanian
  thesis; algorithm names keep their standard technical form.
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from src.models.build import FAMILY_OF

# Validated categorical slots, used in their documented order. With four
# series in the main comparison there is no need to fall back on family-level
# colouring: one hue per detector is both readable and colour-vision safe.
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

# The supervised reference is dash-dotted and the linear ablation dotted, so
# neither can be mistaken for one of the three detectors under comparison.
MODEL_LINESTYLES = {
    "iforest": "-",
    "autoencoder": "-",
    "ocsvm": "-",
    "pca_recon": ":",
    "logreg": "-.",
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

FAMILY_LABELS = {
    "isolation": "Izolim",
    "reconstruction": "Rindërtim",
    "boundary": "Kufi vendimi",
}

# Albanian axis vocabulary, kept in one place so every figure agrees. Terms
# that are standard in English inside Albanian technical writing (recall,
# unsupervised, streaming) are left untranslated on purpose.
AX = {
    "ap": "Average Precision (AP)",
    "precision": "Precision",
    "recall": "Recall",
    "fpr": "Norma e alarmeve false (FPR)",
    "tpr": "Norma e zbulimit (TPR)",
    "f1": "F1",
    "fold": "Fold-i kohor",
    "contamination": "Kontaminimi (prag nga shpërndarja e trajnimit)",
    "budget": "Buxheti i alarmeve (k)",
    "rate": "Ritmi i replay-it (mesazhe/s)",
    "latency_ms": "Vonesa end-to-end (ms)",
    "savings": "Raporti i kursimeve neto",
    "amount_recall": "Recall i vlerës monetare",
    "rank": "Rangu mesatar",
    "train_size": "Madhësia e dritares së trajnimit (transaksione)",
    "epochs": "Epoka",
    "latent": "Dimensioni latent",
}

STYLE = {
    "figure.figsize": (6.0, 4.2),
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
    "legend.fontsize": 8.5,
}


def new_figure(**kwargs):
    mpl.rcParams.update(STYLE)
    return plt.subplots(**kwargs)


def model_color(name: str) -> str:
    if name in MODEL_COLORS:
        return MODEL_COLORS[name]
    return FAMILY_COLORS[FAMILY_OF[name]]


def model_linestyle(name: str) -> str:
    return MODEL_LINESTYLES.get(name, "-")


def model_plot_kwargs(name: str, with_label: bool = True) -> dict:
    kw = {"color": model_color(name), "linestyle": model_linestyle(name)}
    if with_label:
        kw["label"] = MODEL_LABELS.get(name, name)
    return kw


def family_legend_handles():
    """One handle per family plus the reference — used when plotting every
    detector would produce an unreadable legend."""
    from matplotlib.lines import Line2D

    handles = [
        Line2D([], [], color=c, lw=2, label=FAMILY_LABELS[f]) for f, c in FAMILY_COLORS.items()
    ]
    handles.append(
        Line2D([], [], color=REFERENCE_COLOR, lw=2, ls="-.", label="Referencë e mbikëqyrur")
    )
    return handles


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

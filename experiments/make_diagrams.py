"""Conceptual diagrams for the methodology chapter.

Drawn programmatically rather than in a drawing tool so that they stay in
sync with the configuration: the fold geometry below is computed from the
same function the experiments use, not redrawn by hand.
"""

import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import new_figure, save_figure

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
LAYER_COLORS = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7"]


def architecture(cfg):
    """The five functional layers and what crosses each boundary."""
    fig, ax = new_figure(figsize=(7.4, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.9, 11.4)
    ax.axis("off")
    ax.grid(visible=False)

    layers = [
        (
            "Shtresa 1 — Burimi i të dhënave",
            "CSV i renditur kronologjikisht · replay me ritëm të kontrolluar",
        ),
        (
            "Shtresa 2 — Apache Kafka (KRaft)",
            "topic 'transactions' · topic 'alerts' · një broker, një particion",
        ),
        (
            "Shtresa 3 — Paraprocesimi",
            "deserializim JSON · skalim me StandardScaler të dritares së trajnimit",
        ),
        (
            "Shtresa 4 — Motori i inferencës",
            "14 detektorë të pambikëqyrur · referenca LR · ansamble · prag statik/adaptiv",
        ),
        (
            "Shtresa 5 — Dalja",
            "topic 'alerts' · PostgreSQL (scored_events, alerts) · panel Grafana",
        ),
    ]
    y = 9.8
    for i, (title, detail) in enumerate(layers):
        box = FancyBboxPatch(
            (0.5, y - 1.1),
            9.0,
            1.35,
            boxstyle="round,pad=0.06,rounding_size=0.12",
            linewidth=1.6,
            edgecolor=LAYER_COLORS[i],
            facecolor=LAYER_COLORS[i],
            alpha=0.12,
        )
        ax.add_patch(box)
        ax.text(0.85, y + 0.02, title, fontsize=10, fontweight="bold", color=INK, va="center")
        ax.text(0.85, y - 0.52, detail, fontsize=8.4, color=MUTED, va="center")
        if i < len(layers) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (5.0, y - 1.16),
                    (5.0, y - 1.75),
                    arrowstyle="-|>",
                    mutation_scale=13,
                    color=MUTED,
                    linewidth=1.3,
                )
            )
        y -= 2.0

    ax.text(
        5.0,
        0.35,
        "Matja e vonesës: koha e prodhimit ngulitet në mesazh (Shtresa 1) dhe\n"
        "krahasohet me momentin e publikimit të alarmit (Shtresa 5)",
        fontsize=8.2,
        color=MUTED,
        ha="center",
        va="center",
        style="italic",
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "diagram_architecture")


def protocol(cfg):
    """Rolling-origin geometry, drawn from the real fold boundaries."""
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    n = len(df)
    folds = rolling_origin_folds(n, cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    fig, ax = new_figure(figsize=(7.4, 4.4))
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.8, len(folds))
    ax.grid(visible=False)
    ax.set_yticks([])
    for f in folds:
        y = len(folds) - 1 - f.index
        ax.barh(
            y,
            f.train_end / n,
            height=0.58,
            color="#2a78d6",
            alpha=0.30,
            edgecolor="#2a78d6",
            linewidth=0.8,
        )
        ax.barh(
            y,
            (f.test_end - f.test_start) / n,
            left=f.test_start / n,
            height=0.58,
            color="#e34948",
            alpha=0.85,
            edgecolor="#e34948",
            linewidth=0.8,
        )
        frauds = int(df["Class"].iloc[f.test_start : f.test_end].sum())
        ax.text(
            f.test_end / n + 0.008, y, f"{frauds} mashtrime", va="center", fontsize=8, color=MUTED
        )
        ax.text(-0.012, y, f"Fold {f.index}", va="center", ha="right", fontsize=8.5, color=INK)

    ax.set_xlabel("Pjesa e rrjedhës së renditur kronologjikisht")
    ax.set_xlim(-0.10, 1.16)
    ax.legend(
        handles=[
            mpatches.Patch(
                facecolor="#2a78d6",
                alpha=0.30,
                edgecolor="#2a78d6",
                label="Dritarja e trajnimit (zgjerohet)",
            ),
            mpatches.Patch(
                facecolor="#e34948",
                alpha=0.85,
                edgecolor="#e34948",
                label="Blloku i testimit (i pandryshuar)",
            ),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.42),
        ncol=2,
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "diagram_protocol")


def leakage(cfg):
    """Where leakage enters, and where it is blocked."""
    fig, ax = new_figure(figsize=(7.2, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.grid(visible=False)

    items = [
        (
            "Ndarja",
            "Përzierje e rastësishme e rreshtave",
            "Ndarje rreptësisht kronologjike; asnjë rresht i testit para një rreshti trajnimi",
        ),
        (
            "Paraprocesimi",
            "Skaluesi fitohet mbi të gjithë dataset-in",
            "Skaluesi fitohet vetëm mbi dritaren e trajnimit; verifikohet me test automatik",
        ),
        (
            "Pragu",
            "Pragu zgjidhet duke maksimizuar F1 mbi testin",
            "Pragu vjen nga percentili i pikëve të trajnimit; orakulli raportohet veçmas",
        ),
        (
            "Përzgjedhja",
            "Hiperparametrat zgjidhen sipas rezultatit në test",
            "Zgjedhja bëhet në një ndarje të brendshme kohore të dritares së trajnimit",
        ),
    ]
    y = 6.9
    for name, risk, guard in items:
        ax.text(0.15, y, name, fontsize=9.5, fontweight="bold", color=INK, va="center")
        ax.add_patch(
            FancyBboxPatch(
                (1.75, y - 0.42),
                3.65,
                0.84,
                boxstyle="round,pad=0.04,rounding_size=0.1",
                linewidth=1.2,
                edgecolor="#e34948",
                facecolor="#e34948",
                alpha=0.10,
            )
        )
        ax.text(1.92, y, risk, fontsize=8.2, color=MUTED, va="center")
        ax.add_patch(
            FancyArrowPatch(
                (5.5, y), (5.95, y), arrowstyle="-|>", mutation_scale=11, color=MUTED, linewidth=1.1
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (6.05, y - 0.42),
                3.8,
                0.84,
                boxstyle="round,pad=0.04,rounding_size=0.1",
                linewidth=1.2,
                edgecolor="#0ca30c",
                facecolor="#0ca30c",
                alpha=0.10,
            )
        )
        ax.text(6.22, y, guard, fontsize=8.2, color=MUTED, va="center")
        y -= 1.75
    ax.text(3.6, 7.75, "Rreziku", fontsize=9, fontweight="bold", color="#e34948", ha="center")
    ax.text(
        7.95,
        7.75,
        "Masa mbrojtëse e implementuar",
        fontsize=9,
        fontweight="bold",
        color="#0ca30c",
        ha="center",
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "diagram_leakage")


def main():
    cfg = load_config()
    architecture(cfg)
    protocol(cfg)
    leakage(cfg)
    print("diagramet u shkruan në results/figures/")


if __name__ == "__main__":
    main()

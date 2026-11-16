"""Conceptual diagrams for the problem and methodology chapters.

Drawn programmatically rather than in a drawing tool so that they stay in
sync with the configuration: the fold geometry below is computed from the
same function the experiments use, not redrawn by hand.

All three are laid out in centimetres on a canvas exactly as wide as the text
block, so what is set here at 8 pt prints at 8 pt. Box text is wrapped to the
width of its box before it is placed, which is what keeps it inside.
"""

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import (
    CM,
    INK,
    INK_2,
    MUTED,
    SURFACE,
    TEXT_WIDTH_CM,
    legend_above,
    new_figure,
    save_figure,
)

RISK, GUARD = "#e34948", "#0ca30c"
LAYER_COLORS = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e34948"]


def _canvas(height_cm: float):
    fig, ax = new_figure(figsize=(TEXT_WIDTH_CM * CM, height_cm * CM))
    fig.set_layout_engine("none")
    ax.set_position((0, 0, 1, 1))
    ax.set_xlim(0, TEXT_WIDTH_CM)
    ax.set_ylim(0, height_cm)
    ax.axis("off")
    return fig, ax


def _text_width_cm(ax, text: str, fontsize: float, weight: str = "normal") -> float:
    renderer = ax.figure.canvas.get_renderer()
    probe = ax.text(0, 0, text, fontsize=fontsize, fontweight=weight)
    width = probe.get_window_extent(renderer).width / ax.figure.dpi * 2.54
    probe.remove()
    return width


def _fit(ax, text: str, width_cm: float, fontsize: float, weight: str = "normal") -> str:
    """Greedy word wrap against the measured width of the rendered text."""
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if current and _text_width_cm(ax, candidate, fontsize, weight) > width_cm:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    return "\n".join(lines)


def _box(
    ax,
    x,
    y,
    w,
    h,
    text="",
    *,
    face=SURFACE,
    edge=MUTED,
    lw=0.9,
    fontsize=8.0,
    color=INK_2,
    weight="normal",
    pad=0.22,
    alpha=1.0,
):
    """Rounded box with its text wrapped to the box and centred in it."""
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0,rounding_size=0.14",
            linewidth=lw,
            edgecolor=edge,
            facecolor=face,
            alpha=alpha,
        )
    )
    if text:
        ax.text(
            x + w / 2,
            y + h / 2,
            _fit(ax, text, w - 2 * pad, fontsize, weight),
            ha="center",
            va="center",
            fontsize=fontsize,
            color=color,
            fontweight=weight,
            linespacing=1.3,
        )


def _component(ax, x, y, w, h, title, body, color):
    """A system component: coloured outline, bold name, short description."""
    _box(ax, x, y, w, h, face=SURFACE, edge=color, lw=1.1)
    ax.text(
        x + w / 2,
        y + h - 0.36,
        title,
        ha="center",
        va="center",
        fontsize=8.2,
        fontweight="bold",
        color=INK,
    )
    if body:
        _box(ax, x, y + 0.05, w, h - 0.62, body, face="none", edge="none", lw=0, fontsize=7.4)


def _arrow(ax, start, end, color=MUTED, lw=1.1, connection="arc3"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=9,
            color=color,
            linewidth=lw,
            connectionstyle=connection,
            shrinkA=0,
            shrinkB=0,
        )
    )


def leakage(cfg):
    """Where information from the future can leak in, and what blocks it."""
    rows = [
        (
            "Ndarja",
            "Rreshtat përzihen rastësisht, prandaj transaksione të së ardhmes hyjnë në trajnim.",
            "Ndarje kronologjike: çdo rresht trajnimi paraprin çdo rresht testimi.",
        ),
        (
            "Paraprocesimi",
            "Skaluesi përshtatet mbi të gjithë dataset-in, bashkë me bllokun e testimit.",
            "Skaluesi përshtatet vetëm mbi dritaren e trajnimit.",
        ),
        (
            "Pragu",
            "Pragu zgjidhet duke maksimizuar F1 mbi bllokun e testimit.",
            "Pragu merret nga percentili i pikëve të trajnimit; pragu orakull raportohet veçmas.",
        ),
        (
            "Hiperparametrat",
            "Konfigurimi zgjidhet sipas rezultatit në bllokun e testimit.",
            "Zgjedhja bëhet në një ndarje të brendshme kohore të dritares së trajnimit.",
        ),
    ]
    height = 7.7
    fig, ax = _canvas(height)
    risk_x, risk_w, gap = 2.95, 5.2, 0.8
    guard_x = risk_x + risk_w + gap
    guard_w = TEXT_WIDTH_CM - guard_x - 0.05
    row_h, row_gap = 1.38, 0.34
    top = height - 0.85

    for x, w, title, color in (
        (risk_x, risk_w, "Rreziku", RISK),
        (guard_x, guard_w, "Masa mbrojtëse e zbatuar", "#08800a"),
    ):
        ax.text(
            x + w / 2,
            height - 0.4,
            title,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=color,
        )
    for i, (name, risk, guard) in enumerate(rows):
        y = top - (i + 1) * row_h - i * row_gap
        ax.text(
            0.05,
            y + row_h / 2,
            name,
            ha="left",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color=INK,
        )
        _box(ax, risk_x, y, risk_w, row_h, risk, face="#fdeeee", edge="#f2b9b8")
        _box(ax, guard_x, y, guard_w, row_h, guard, face="#ebf7eb", edge="#a9dca9")
        _arrow(ax, (risk_x + risk_w + 0.12, y + row_h / 2), (guard_x - 0.12, y + row_h / 2))
    save_figure(fig, REPO_ROOT / cfg.results_dir, "diagram_leakage")


def architecture(cfg):
    """The five layers as a left-to-right pipeline.

    Each layer is a column; the main row is the path every message takes, and
    the row under it is where the scored events end up. The two timestamps
    that define the end-to-end latency are written on the components that
    stamp them.
    """
    height = 7.6
    fig, ax = _canvas(height)
    col_w = TEXT_WIDTH_CM / 5
    box_w = col_w - 0.5
    names = ["Burimi", "Transporti", "Paraprocesimi", "Inferenca", "Dalja"]

    for i, (name, color) in enumerate(zip(names, LAYER_COLORS, strict=True)):
        x0 = i * col_w
        _box(ax, x0 + 0.06, 0.1, col_w - 0.12, height - 0.15, face=color, alpha=0.08, lw=0)
        ax.text(
            x0 + col_w / 2,
            height - 0.42,
            f"Shtresa {i + 1}",
            ha="center",
            va="center",
            fontsize=7.5,
            color=MUTED,
        )
        ax.text(
            x0 + col_w / 2,
            height - 0.85,
            name,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=INK,
        )

    main_y, main_h = 3.55, 2.65
    components = [
        ("Producer", "CSV i renditur sipas kohës; ritëm konstant r; vula kohore t₀"),
        ("Apache Kafka", "KRaft, një broker; topic transactions"),
        ("Consumer", "mikro-grupe deri në 64 mesazhe; JSON → 29 veçori; StandardScaler"),
        ("Detektori", "IF, AE, OCSVM ose LR; prag statik ose adaptiv"),
        ("Apache Kafka", "topic alerts; vula kohore t₁"),
    ]
    xs = [i * col_w + 0.25 for i in range(5)]
    for i, (title, body) in enumerate(components):
        _component(
            ax, xs[i], main_y, box_w, main_h, title, body.replace("; ", "\n"), LAYER_COLORS[i]
        )
        if i < len(components) - 1:
            mid = main_y + main_h / 2
            _arrow(ax, (xs[i] + box_w + 0.03, mid), (xs[i + 1] - 0.03, mid))

    # Where every scored event ends up, under the last two layers.
    low_y, low_h = 0.55, 1.75
    _component(
        ax, xs[3], low_y, box_w, low_h, "PostgreSQL", "scored_events\nalerts", LAYER_COLORS[3]
    )
    _component(
        ax, xs[4], low_y, box_w, low_h, "Grafana", "paneli me nëntë grafikë", LAYER_COLORS[4]
    )
    _arrow(ax, (xs[3] + box_w / 2, main_y - 0.03), (xs[3] + box_w / 2, low_y + low_h + 0.03))
    _arrow(ax, (xs[3] + box_w + 0.03, low_y + low_h / 2), (xs[4] - 0.03, low_y + low_h / 2))

    note = (
        "Vonesa end-to-end matet për çdo mesazh si t₁ − t₀: nga vula kohore e "
        "producer-it deri te publikimi i vendimit."
    )
    _box(ax, 0.25, low_y, 3 * col_w - 0.5, low_h, note, face=SURFACE, edge="#d6d5cd", fontsize=7.8)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "diagram_architecture")


def protocol(cfg):
    """Rolling-origin geometry, drawn from the real fold boundaries."""
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    n = len(df)
    folds = rolling_origin_folds(n, cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    fig, ax = new_figure(figsize=(TEXT_WIDTH_CM * CM, 7.2 * CM))
    for f in folds:
        y = len(folds) - 1 - f.index
        ax.barh(y, f.train_end / n, height=0.62, color="#9ec5f4", linewidth=0)
        ax.barh(
            y,
            (f.test_end - f.test_start) / n,
            left=f.test_start / n,
            height=0.62,
            color="#e34948",
            linewidth=0,
        )
        frauds = int(df["Class"].iloc[f.test_start : f.test_end].sum())
        ax.text(
            (f.test_start + f.test_end) / 2 / n,
            y,
            str(frauds),
            ha="center",
            va="center",
            fontsize=7.5,
            fontweight="bold",
            color=SURFACE,
        )
    ax.set_yticks(range(len(folds)), [f"Fold {f.index}" for f in reversed(folds)])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 1.01)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0], ["0%", "20%", "40%", "60%", "80%", "100%"])
    ax.set_xlabel("Pozicioni në rrjedhën e renditur sipas kohës")
    ax.grid(False)
    cut = cfg.split.train_fraction
    ax.axvline(cut, color=INK_2, lw=0.8, ls=(0, (3, 2)), zorder=1)
    ax.text(cut + 0.006, len(folds) - 0.45, "prerja 70/30", fontsize=7.5, color=INK_2, va="bottom")
    ax.set_ylim(-0.6, len(folds) + 0.1)
    legend_above(
        ax,
        handles=[
            Patch(facecolor="#9ec5f4", label="Dritarja e trajnimit (zgjerohet me çdo fold)"),
            Patch(facecolor="#e34948", label="Blloku i testimit (numri i mashtrimeve)"),
        ],
        labels=[
            "Dritarja e trajnimit (zgjerohet me çdo fold)",
            "Blloku i testimit (numri i mashtrimeve)",
        ],
    )
    save_figure(fig, REPO_ROOT / cfg.results_dir, "diagram_protocol")


def main():
    cfg = load_config()
    leakage(cfg)
    architecture(cfg)
    protocol(cfg)
    print("diagramet u shkruan në results/figures/")


if __name__ == "__main__":
    main()

"""Headline numbers, derived from the result tables at request time.

Nothing here is a constant. Every tile the application shows is recomputed
from the CSV files, so a re-run changes the front page without anyone editing
the application. When a table is missing the tile reports that instead of
guessing, which is how a half-finished pipeline should look.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

import pandas as pd

from webapp import artifacts

REFERENCE = "LR (referencë)"
DETECTORS = ("Autoencoder", "One-Class SVM", "Isolation Forest")


def _tile(
    label: str,
    value: Any,
    unit: str = "",
    hint: str = "",
    tone: str = "neutral",
) -> dict[str, Any]:
    return {"label": label, "value": value, "unit": unit, "hint": hint, "tone": tone}


def _missing(label: str, what: str) -> dict[str, Any]:
    return _tile(label, "—", hint=f"mungon {what}", tone="muted")


def _fmt(value: float | None, digits: int = 3) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"{value:.{digits}f}"


def _lookup(frame: pd.DataFrame, key_col: str, key: str, value_col: str) -> float | None:
    row = frame[frame[key_col] == key]
    if row.empty or value_col not in row:
        return None
    return float(row.iloc[0][value_col])


# --- individual tile groups -------------------------------------------------


def headline() -> list[dict[str, Any]]:
    """The six numbers that answer "what did this study find"."""
    tiles: list[dict[str, Any]] = []

    if artifacts.has_table("benchmark_summary"):
        bench = artifacts.table_frame("benchmark_summary")
        best = bench[bench["model"] != REFERENCE].sort_values("ap_mean", ascending=False)
        reference = _lookup(bench, "model", REFERENCE, "ap_mean")
        if not best.empty:
            top = best.iloc[0]
            tiles.append(
                _tile(
                    "Më i miri unsupervised, me parazgjedhje",
                    _fmt(float(top["ap_mean"])),
                    "AP",
                    f"{top['model']}, mbi tetë fold-e",
                    "accent",
                )
            )
        if reference is not None:
            tiles.append(
                _tile(
                    "Referenca e mbikëqyrur",
                    _fmt(reference),
                    "AP",
                    "kufi i sipërm kur etiketat ekzistojnë",
                    "reference",
                )
            )
    else:
        tiles.append(_missing("Më i miri unsupervised", "benchmark_summary"))

    if artifacts.has_table("best_effort_interaction"):
        effort = artifacts.table_frame("best_effort_interaction")
        column = "AP më i mirë i arritshëm"
        if column in effort.columns and not effort.empty:
            row = effort.sort_values(column, ascending=False).iloc[0]
            tiles.append(
                _tile(
                    "Më i miri i arritshëm",
                    _fmt(float(row[column])),
                    "AP",
                    f"{row['Detektori']}, {row.get('qeliza më e mirë', '')}",
                    "accent",
                )
            )

    if artifacts.has_table("latency_summary"):
        latency = artifacts.table_frame("latency_summary")
        static = latency[~latency["prag_adaptiv"].astype(bool)]
        if not static.empty:
            lo, hi = static["e2e_ms_mean"].min(), static["e2e_ms_mean"].max()
            tiles.append(
                _tile(
                    "Vonesa end-to-end",
                    f"{lo:.0f}–{hi:.0f}",
                    "ms",
                    f"objektivi 1000 ms; p99 maks. {static['e2e_ms_p99'].max():.0f} ms",
                    "good",
                )
            )
    else:
        tiles.append(_missing("Vonesa end-to-end", "latency_summary"))

    if artifacts.has_table("protocol_inflation"):
        inflation = artifacts.table_frame("protocol_inflation")
        if "fryrja" in inflation.columns and not inflation.empty:
            tiles.append(
                _tile(
                    "Fryrja e ndarjes së rastësishme",
                    f"{inflation['fryrja'].mean():.1f}×",
                    "",
                    f"deri {inflation['fryrja'].max():.1f}× për një detektor",
                    "warn",
                )
            )

    if artifacts.has_table("error_analysis_coverage"):
        coverage = artifacts.table_frame("error_analysis_coverage")
        dark = coverage[coverage["n_detektore"] == 0]
        if not dark.empty:
            tiles.append(
                _tile(
                    "Mashtrime që s'i kap asnjë detektor",
                    f"{100 * float(dark.iloc[0]['pjesa']):.0f}",
                    "%",
                    "brenda buxhetit prej njëqind alarmesh",
                    "warn",
                )
            )
    return tiles


def dataset() -> list[dict[str, Any]]:
    tiles: list[dict[str, Any]] = []
    if artifacts.has_table("eda_overview"):
        overview = artifacts.table_frame("eda_overview")
        pairs = dict(zip(overview["treguesi"], overview["vlera"], strict=False))
        for label, key in (
            ("Transaksione", "Transaksione gjithsej"),
            ("Mashtrime", "Mashtrime"),
            ("Norma e mashtrimit", "Norma e mashtrimit"),
            ("Kohëzgjatja", "Kohëzgjatja"),
        ):
            match = next((v for k, v in pairs.items() if str(k).startswith(key[:12])), None)
            if match is not None:
                tiles.append(_tile(label, str(match)))
    if artifacts.has_table("geometry_summary"):
        geometry = artifacts.table_frame("geometry_summary")
        train = geometry[geometry["dritarja"] == "trajnim"]
        if not train.empty:
            row = train.iloc[0]
            tiles.append(
                _tile(
                    "Largësia e mashtrimeve",
                    f"{float(row['raporti_distancave']):.1f}×",
                    "",
                    "sa më larg se një transaksion tipik legjitim",
                    "accent",
                )
            )
            tiles.append(
                _tile(
                    "Vetëm distanca jep",
                    _fmt(float(row["ap_vetem_distance"])),
                    "AP",
                    "detektor pa asnjë parametër",
                    "warn",
                )
            )
            tiles.append(
                _tile(
                    "Alarme për mashtrimin median",
                    f"{float(row['rangu_median_i_mashtrimit']):.0f}",
                    "",
                    "kur renditet vetëm sipas distancës",
                    "warn",
                )
            )
    return tiles


def protocol() -> list[dict[str, Any]]:
    tiles: list[dict[str, Any]] = []
    if artifacts.has_table("fold_summary"):
        folds = artifacts.table_frame("fold_summary")
        tiles.append(_tile("Fold-e kohore", str(len(folds))))
        tiles.append(
            _tile(
                "Mashtrime për bllok testimi",
                f"{int(folds['test_frauds'].min())}–{int(folds['test_frauds'].max())}",
                "",
                f"mesatarisht {folds['test_frauds'].mean():.0f}",
            )
        )
        tiles.append(
            _tile(
                "Bllok testimi",
                f"{int(folds['test_rows'].mean()):,}".replace(",", " "),
                "rreshta",
            )
        )
    if artifacts.has_table("significance_omnibus"):
        omnibus = artifacts.table_frame("significance_omnibus")
        core = omnibus[omnibus["grupi"].str.contains("unsupervised", na=False)]
        if not core.empty:
            row = core.iloc[0]
            tiles.append(
                _tile(
                    "Diferenca kritike (Nemenyi)",
                    _fmt(float(row["nemenyi_CD"]), 2),
                    "rang",
                    f"gjerësia e rangjeve {float(row['range_i_rangjeve']):.2f}",
                    "good" if float(row["range_i_rangjeve"]) > float(row["nemenyi_CD"]) else "warn",
                )
            )
    return tiles


def streaming() -> list[dict[str, Any]]:
    tiles: list[dict[str, Any]] = []
    if not artifacts.has_table("latency_summary"):
        return [_missing("Vonesa", "latency_summary")]
    latency = artifacts.table_frame("latency_summary")
    static = latency[~latency["prag_adaptiv"].astype(bool)]
    within = static[static["rate_msg_s"] <= 1000]
    tiles.append(
        _tile(
            "Vonesa mesatare",
            f"{within['e2e_ms_mean'].min():.0f}–{within['e2e_ms_mean'].max():.0f}",
            "ms",
            f"{len(within)} konfigurime deri në 1000 msg/s",
            "good",
        )
    )
    tiles.append(
        _tile(
            "p99 maksimal",
            f"{static['e2e_ms_p99'].max():.0f}",
            "ms",
            "objektivi është 1000 ms",
            "good",
        )
    )
    tiles.append(
        _tile(
            "Ngopja",
            f"{static['throughput_msg_s'].max():.0f}",
            "msg/s",
            "me një consumer të vetëm",
        )
    )
    share = (static["infer_ms_mean"] / static["e2e_ms_mean"]).max()
    tiles.append(
        _tile(
            "Inferenca si pjesë e vonesës",
            f"{100 * share:.1f}",
            "%",
            "në rastin më të keq",
            "good",
        )
    )
    return tiles


def ensembles() -> list[dict[str, Any]]:
    tiles: list[dict[str, Any]] = []
    for table, label in (
        ("ensemble_summary", "me parazgjedhje"),
        ("ensemble_summary_tuned", "me akordim"),
    ):
        if not artifacts.has_table(table):
            continue
        frame = artifacts.table_frame(table).sort_values("ap_mean", ascending=False)
        if frame.empty:
            continue
        row = frame.iloc[0]
        delta = float(row["vs_best_single"])
        tiles.append(
            _tile(
                f"Ansambli më i mirë, {label}",
                _fmt(float(row["ap_mean"])),
                "AP",
                f"{delta:+.4f} ndaj anëtarit më të mirë, fiton në "
                f"{int(row['fold_wins_vs_best_single'])}/{int(row['n_folds'])} fold-e",
                "good" if delta > 0 else "warn",
            )
        )
    return tiles


COMPUTATIONS: dict[str, Callable[[], list[dict[str, Any]]]] = {
    "headline": headline,
    "dataset": dataset,
    "protocol": protocol,
    "streaming": streaming,
    "ensembles": ensembles,
}


def compute(name: str) -> list[dict[str, Any]]:
    builder = COMPUTATIONS.get(name)
    if builder is None:
        return []
    try:
        return builder()
    except Exception as exc:  # noqa: BLE001 - a broken tile must not break the page
        return [_tile("Gabim", "—", hint=f"{type(exc).__name__}: {exc}", tone="muted")]


# --- the argument, in order -------------------------------------------------


def _safe(builder: Callable[[], str], default: str = "—") -> str:
    try:
        value = builder()
    except Exception:  # noqa: BLE001 - a missing table must not break the tour
        return default
    return value if value else default


def tour() -> list[dict[str, Any]]:
    """Nine steps through the study, each with a number read from disk.

    This is the orientation somebody needs who has not read the document: the
    claims in the order they depend on each other, every one of them linking
    to the section that proves it.
    """

    def geometry_claim() -> str:
        row = artifacts.table_frame("geometry_summary").query("dritarja == 'trajnim'").iloc[0]
        return (
            f"{float(row['raporti_distancave']):.1f}× më larg, por vetëm "
            f"{_fmt(float(row['ap_vetem_distance']))} AP"
        )

    def latency_claim() -> str:
        frame = artifacts.table_frame("latency_summary")
        static = frame[~frame["prag_adaptiv"].astype(bool)]
        return f"{static['e2e_ms_mean'].min():.0f}–{static['e2e_ms_mean'].max():.0f} ms"

    def ranking_claim() -> str:
        frame = artifacts.table_frame("benchmark_summary")
        unsup = frame[frame["model"] != REFERENCE].sort_values("ap_mean", ascending=False)
        reference = _lookup(frame, "model", REFERENCE, "ap_mean") or 0.0
        best = float(unsup.iloc[0]["ap_mean"])
        return f"{unsup.iloc[0]['model']} {_fmt(best)} kundrejt {_fmt(reference)} të referencës"

    def significance_claim() -> str:
        frame = artifacts.table_frame("significance_wilcoxon")
        significant = int(frame["significant_holm_05"].astype(bool).sum())
        return f"{significant} nga {len(frame)} krahasime mbijetojnë korrigjimin"

    def causal_claim() -> str:
        frame = artifacts.table_frame("feature_selection")
        labelled = frame[frame["renditja"].str.contains("etiketa", na=False)]
        labelled = labelled[~labelled["renditja"].str.contains("pa etiketa", na=False)]
        gains = labelled.groupby("model")["vs_te_gjitha"].max().sort_values(ascending=False)
        return f"{gains.index[0]} fiton {gains.iloc[0]:+.3f} AP, më shumë se të tjerët"

    def scaling_claim() -> str:
        frame = artifacts.table_frame("scaling_significance")
        unsup = frame[frame["Detektori"] != REFERENCE]
        best = unsup.sort_values("delta_ndaj_standard", ascending=False).iloc[0]
        return (
            f"{best['Detektori']} fiton {float(best['delta_ndaj_standard']):+.3f} AP "
            f"vetëm nga paraprocesimi"
        )

    def effort_claim() -> str:
        frame = artifacts.table_frame("best_effort_interaction")
        column = "AP më i mirë i arritshëm"
        ordered = frame.sort_values(column, ascending=False)
        span = float(ordered.iloc[0][column]) / float(ordered.iloc[-1][column])
        base_span = float(ordered["bazë"].max()) / float(ordered["bazë"].min())
        return f"hapësira bie nga {base_span:.1f}× në {span:.2f}×"

    def ensemble_claim() -> str:
        frame = artifacts.table_frame("ensemble_summary").sort_values("ap_mean", ascending=False)
        best = frame.iloc[0]
        return f"më i miri {float(best['vs_best_single']):+.4f} ndaj anëtarit më të mirë"

    def protocol_claim() -> str:
        frame = artifacts.table_frame("protocol_inflation")
        return f"ndarja e rastësishme e fryn AP-në {frame['fryrja'].mean():.1f}×"

    steps = [
        (
            "Problemi ka një tavan që nuk varet nga algoritmi",
            "Mashtrimet janë vërtet larg klasës legjitime, por bishti i asaj klase e mbush të "
            "njëjtin rajon. Kjo e vendos kufirin që çdo metodë distance mund të arrijë.",
            geometry_claim,
            "dataseti",
            "gjeometria",
        ),
        (
            "Sistemi është i realizueshëm me rezervë të gjerë",
            "Vonesa end-to-end mbi një broker të vërtetë Kafka qëndron një deri dy rende "
            "madhësie nën objektivin prej një sekonde.",
            latency_claim,
            "rrjedha",
            "vonesa",
        ),
        (
            "Etiketat historike vlejnë shumë",
            "Nën konfigurimin bazë, referenca e mbikëqyrur mbetet dukshëm përpara çdo detektori "
            "unsupervised. Hendeku është kuantifikimi i vlerës së atyre etiketave.",
            ranking_claim,
            "rezultatet",
            "kryesore",
        ),
        (
            "Jo çdo dallim mes detektorëve është i qëndrueshëm",
            "Krahasimet e paradeklaruara bëhen mbi fold-e, me korrigjim për krahasime të "
            "shumëfishta. Njëri prej tyre nuk arrin domethënie, dhe kjo raportohet.",
            significance_claim,
            "rezultatet",
            "domethenia",
        ),
        (
            "Dobësia e Isolation Forest-it u mat dhe u testua kauzalisht",
            "Tri proba tregojnë se kapaciteti shpërndahet mbi kolona pa sinjal; ndërhyrja mbi "
            "hyrjen e kthen korrelacionin në pohim të testuar.",
            causal_claim,
            "kauzaliteti",
            "nderhyrja",
        ),
        (
            "Paraprocesimi peshon më shumë se zgjedhja e algoritmit",
            "Të tria metodat e përcaktojnë anomalinë përmes largësisë, dhe largësia varet "
            "plotësisht nga shkalla e veçorive. Referenca e mbikëqyrur nuk preket.",
            scaling_claim,
            "konfigurimi",
            "paraprocesimi",
        ),
        (
            "Renditja nuk mbijeton kalimin nga vlerat e parazgjedhura",
            "Kur secilit detektor i jepet konfigurimi i vet më i mirë, hapësira mes tyre "
            "ngushtohet dhe radha përmbyset.",
            effort_claim,
            "konfigurimi",
            "kapaciteti",
        ),
        (
            "Ansambli nuk ndihmon, dhe dihet pse",
            "Detektorët nuk gabojnë në mënyra të pavarura: mashtrimet e vështira janë të "
            "vështira për të tre njëkohësisht.",
            ensemble_claim,
            "ansambli",
            "ansambli",
        ),
        (
            "Vendimet e protokollit peshojnë më shumë se zgjedhja e algoritmit",
            "E njëjta ndarje 70/30, një herë sipas kohës dhe një herë e përzier, jep rezultate "
            "që nuk krahasohen me njëri-tjetrin.",
            protocol_claim,
            "protokolli",
            "krahasimi",
        ),
    ]
    return [
        {
            "index": index,
            "title": title,
            "text": text,
            "evidence": _safe(claim),
            "page": page,
            "section": section,
        }
        for index, (title, text, claim, page, section) in enumerate(steps, start=1)
    ]

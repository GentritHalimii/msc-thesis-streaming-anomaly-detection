"""Read-only access to everything the pipeline has produced.

The web application never stores a copy of a result. Every number it shows is
read from `results/` at request time, so the page a reader is looking at is
always the state of the repository, and re-running an experiment changes the
page without touching the application.

Four kinds of artefact are exposed:

* tables    - the CSV files that the thesis tables are built from;
* figures   - the matplotlib PNG/PDF pairs that the thesis figures are;
* verdicts  - the Albanian sentences each experiment writes about its own
              measurements, which are what the thesis prose paraphrases;
* manifests - run name, timestamp, commit SHA, configuration hash and the full
              configuration, written by every experiment.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import REPO_ROOT, load_config


@lru_cache(maxsize=1)
def results_dir() -> Path:
    return REPO_ROOT / load_config().results_dir


def figures_dir() -> Path:
    return results_dir() / "figures"


# --- freshness -------------------------------------------------------------


def _stat(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    info = path.stat()
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "bytes": info.st_size,
        "modified": datetime.fromtimestamp(info.st_mtime, UTC).isoformat(),
    }


# --- tables ----------------------------------------------------------------


def _clean(value: Any) -> Any:
    """JSON cannot carry NaN or numpy scalars; the front end gets null."""
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, AttributeError):
            return str(value)
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def table_path(name: str) -> Path:
    return results_dir() / f"{name}.csv"


def has_table(name: str) -> bool:
    return table_path(name).exists()


def read_table(name: str, query: str | None = None) -> dict[str, Any]:
    """One CSV as column metadata plus row records.

    `query` is a pandas expression applied before serialisation, used where a
    table holds several studies and a section wants one of them.
    """
    path = table_path(name)
    if not path.exists():
        raise FileNotFoundError(f"tabela '{name}' nuk ekziston ende")
    frame = pd.read_csv(path)
    if query:
        frame = frame.query(query)
    columns = [
        {"key": str(col), "numeric": bool(pd.api.types.is_numeric_dtype(frame[col]))}
        for col in frame.columns
    ]
    rows = [{str(k): _clean(v) for k, v in record.items()} for record in frame.to_dict("records")]
    return {
        "name": name,
        "columns": columns,
        "rows": rows,
        "n_rows": len(frame),
        "file": _stat(path),
    }


def table_frame(name: str) -> pd.DataFrame:
    """The same CSV as a DataFrame, for server-side derived numbers."""
    return pd.read_csv(table_path(name))


# --- figures ---------------------------------------------------------------


def figure_path(name: str, fmt: str = "png") -> Path:
    return figures_dir() / f"{name}.{fmt}"


def has_figure(name: str) -> bool:
    return figure_path(name).exists()


def figure_info(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "png": _stat(figure_path(name, "png")),
        "pdf": _stat(figure_path(name, "pdf")),
    }


# --- verdicts --------------------------------------------------------------


def verdict_path(name: str) -> Path:
    """Most experiments write `<name>_verdict.txt`, but a run with a variant
    writes `<base>_verdict_<variant>.txt`. Both spellings are accepted, the
    second by naming the file stem itself."""
    direct = results_dir() / f"{name}_verdict.txt"
    if direct.exists():
        return direct
    literal = results_dir() / f"{name}.txt"
    return literal if literal.exists() else direct


def read_verdict(name: str) -> dict[str, Any] | None:
    path = verdict_path(name)
    if not path.exists():
        return None
    return {"name": name, "text": path.read_text().strip(), "file": _stat(path)}


# --- manifests -------------------------------------------------------------


@dataclass(frozen=True)
class Manifest:
    run: str
    timestamp: str | None
    git_sha: str | None
    config_sha: str | None
    packages: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "run": self.run,
            "timestamp": self.timestamp,
            "git_sha": self.git_sha,
            "git_sha_short": (self.git_sha or "")[:7] or None,
            "config_sha_short": (self.config_sha or "")[:12] or None,
            "packages": self.packages,
        }


def read_manifest(run: str) -> dict[str, Any] | None:
    path = results_dir() / f"manifest_{run}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    return Manifest(
        run=payload.get("run", run),
        timestamp=payload.get("timestamp_utc"),
        git_sha=payload.get("git_sha"),
        config_sha=payload.get("config_sha256"),
        packages=payload.get("packages", {}) or {},
    ).as_dict()


def manifest_config(run: str) -> dict[str, Any] | None:
    path = results_dir() / f"manifest_{run}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text()).get("config")
    except json.JSONDecodeError:
        return None


# --- inventory -------------------------------------------------------------


def inventory() -> dict[str, Any]:
    """What exists on disk right now, for the provenance page."""
    root = results_dir()
    tables = sorted(p.stem for p in root.glob("*.csv"))
    figures = sorted(p.stem for p in figures_dir().glob("*.png"))
    verdicts = sorted(p.stem.removesuffix("_verdict") for p in root.glob("*_verdict.txt"))
    manifests = sorted(p.stem.removeprefix("manifest_") for p in root.glob("manifest_*.json"))
    newest = max(
        (p.stat().st_mtime for p in root.rglob("*") if p.is_file()),
        default=0.0,
    )
    return {
        "results_dir": str(root.relative_to(REPO_ROOT)),
        "tables": tables,
        "figures": figures,
        "verdicts": verdicts,
        "manifests": manifests,
        "counts": {
            "tables": len(tables),
            "figures": len(figures),
            "verdicts": len(verdicts),
            "manifests": len(manifests),
            "folds": len(list((root / "folds").glob("*.npz"))),
            # Repeated runs live in runs/rep*/ and capacity/rep*/.
            "latency_runs": len(list((root / "latency").glob("*/rep*/latency_*.csv"))),
        },
        "newest_artifact": datetime.fromtimestamp(newest, UTC).isoformat() if newest else None,
    }


def thesis_document() -> dict[str, Any]:
    out = REPO_ROOT / "thesis" / "out"
    return {
        "docx": _stat(out / "Punimi_Diplomes_GentritHalimi.docx"),
        "pdf": _stat(out / "Punimi_Diplomes_GentritHalimi.pdf"),
    }


def staleness() -> dict[str, Any]:
    """Which runs are older than the runs they depend on.

    A result computed before its own input was last regenerated is not wrong
    in any way a reader can see; it is simply out of date, and the only place
    that shows is the timestamp inside the manifest. This turns that into an
    explicit list, so nothing silently describes a previous version of the
    study.
    """
    from webapp.catalog import EXPERIMENTS

    stamps: dict[str, str] = {}
    for experiment in EXPERIMENTS.values():
        if not experiment.writes_manifest:
            continue
        record = read_manifest(experiment.manifest or experiment.module.rsplit(".", 1)[-1])
        if record and record.get("timestamp"):
            stamps[experiment.id] = record["timestamp"]

    stale: list[dict[str, Any]] = []
    for experiment in EXPERIMENTS.values():
        mine = stamps.get(experiment.id)
        if mine is None:
            continue
        newer = [
            {"id": need, "timestamp": stamps[need]}
            for need in experiment.needs
            if need in stamps and stamps[need] > mine
        ]
        if newer:
            stale.append(
                {
                    "id": experiment.id,
                    "title": experiment.title,
                    "timestamp": mine,
                    "newer_inputs": sorted(newer, key=lambda item: item["timestamp"], reverse=True),
                }
            )
    never_run = sorted(
        {
            e.id
            for e in EXPERIMENTS.values()
            if e.writes_manifest and e.id not in stamps and not e.args and not e.docker
        }
    )
    return {
        "stale": sorted(stale, key=lambda item: item["timestamp"]),
        "never_run": never_run,
        "known": len(stamps),
    }

"""HTTP surface of the results panel.

Three kinds of endpoint. The first serves resolved pages: the structure from
`content`, with every artefact it names read from disk at request time. The
second serves individual artefacts, for downloads and for refreshing one card
without reloading the page. The third drives the job runner and the docker
stack.

The server binds to the loopback interface by default. It executes nothing
that is not named in the catalogue.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import REPO_ROOT
from webapp import artifacts, catalog, content, metrics, services
from webapp.runner import runner, sse_stream

STATIC = Path(__file__).parent / "static"
THESIS_FILES = {
    "docx": REPO_ROOT / "thesis" / "out" / "Punimi_Diplomes_GentritHalimi.docx",
    "pdf": REPO_ROOT / "thesis" / "out" / "Punimi_Diplomes_GentritHalimi.pdf",
}

app = FastAPI(title="Paneli i rezultateve", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


# --- pages ------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC / "index.html").read_text()


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    return {
        "title": "Zbulimi i anomalive në rrjedha të simuluara transaksionesh",
        "subtitle": "Apache Kafka dhe unsupervised machine learning mbi transaksione kartash",
        "author": "Gentrit Halimi",
        "navigation": content.navigation(),
        "inventory": artifacts.inventory(),
        "document": artifacts.thesis_document(),
        "colors": content.MODEL_COLORS,
        "labels": content.MODEL_LABELS,
    }


def _resolve_block(block: dict[str, Any], tables: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(block)
    kind = block["kind"]
    if kind == "verdict":
        resolved["payload"] = artifacts.read_verdict(block["source"])
    elif kind == "metrics":
        resolved["payload"] = metrics.compute(block["compute"])
    elif kind == "figure":
        name = block["source"]
        resolved["payload"] = artifacts.figure_info(name) if artifacts.has_figure(name) else None
        resolved["url"] = f"/api/figure/{name}.png"
        resolved["pdf_url"] = f"/api/figure/{name}.pdf"
    elif kind in {"table", "chart"}:
        key = _table_key(block["source"], block.get("query"))
        resolved["table_key"] = key
        if key not in tables:
            tables[key] = _load_table(block["source"], block.get("query"))
    elif kind == "widget" and block.get("widget") == "tour":
        resolved["payload"] = metrics.tour()
    elif kind == "runner":
        resolved["payload"] = [
            catalog.EXPERIMENTS[e].as_dict()
            for e in block["experiments"]
            if e in catalog.EXPERIMENTS
        ]
    return resolved


def _table_key(source: str, query: str | None) -> str:
    return f"{source}|{query or ''}"


def _load_table(source: str, query: str | None) -> dict[str, Any]:
    try:
        payload = artifacts.read_table(source, query)
    except FileNotFoundError as exc:
        return {"name": source, "missing": True, "reason": str(exc), "columns": [], "rows": []}
    except Exception as exc:  # noqa: BLE001 - a broken table must not break the page
        return {
            "name": source,
            "missing": True,
            "reason": f"{type(exc).__name__}: {exc}",
            "columns": [],
            "rows": [],
        }
    payload["missing"] = False
    payload["download"] = f"/api/download/table/{source}.csv"
    return payload


@app.get("/api/page/{page_id}")
def get_page(page_id: str) -> dict[str, Any]:
    page = content.PAGES_BY_ID.get(page_id)
    if page is None:
        raise HTTPException(status_code=404, detail="faqja nuk ekziston")
    tables: dict[str, Any] = {}
    sections = [
        {
            **sec,
            "blocks": [_resolve_block(block, tables) for block in sec["blocks"]],
        }
        for sec in page["sections"]
    ]
    return {
        "id": page["id"],
        "title": page["title"],
        "subtitle": page["subtitle"],
        "sections": sections,
        "tables": tables,
    }


# --- individual artefacts ---------------------------------------------------


@app.get("/api/table/{name}")
def get_table(name: str, query: str | None = None) -> dict[str, Any]:
    return _load_table(name, query)


@app.get("/api/figure/{filename}")
def get_figure(filename: str) -> FileResponse:
    stem, _, ext = filename.rpartition(".")
    if ext not in {"png", "pdf"} or "/" in stem or ".." in stem:
        raise HTTPException(status_code=400, detail="format i papranuar")
    path = artifacts.figure_path(stem, ext)
    if not path.exists():
        raise HTTPException(status_code=404, detail="figura nuk ekziston ende")
    media = "image/png" if ext == "png" else "application/pdf"
    return FileResponse(path, media_type=media)


@app.get("/api/download/table/{filename}")
def download_table(filename: str) -> FileResponse:
    stem = filename.removesuffix(".csv")
    if "/" in stem or ".." in stem:
        raise HTTPException(status_code=400, detail="emër i papranuar")
    path = artifacts.table_path(stem)
    if not path.exists():
        raise HTTPException(status_code=404, detail="tabela nuk ekziston")
    return FileResponse(path, media_type="text/csv", filename=f"{stem}.csv")


@app.get("/api/provenance")
def provenance() -> dict[str, Any]:
    runs = []
    for name in artifacts.inventory()["manifests"]:
        record = artifacts.read_manifest(name)
        if record:
            runs.append(record)
    runs.sort(key=lambda r: r.get("timestamp") or "", reverse=True)
    shas = {r["git_sha_short"] for r in runs if r.get("git_sha_short")}
    configs = {r["config_sha_short"] for r in runs if r.get("config_sha_short")}
    return {
        "runs": runs,
        "staleness": artifacts.staleness(),
        "inventory": artifacts.inventory(),
        "distinct_commits": sorted(s for s in shas if s),
        "distinct_configs": sorted(c for c in configs if c),
        "packages": runs[0]["packages"] if runs else {},
    }


@app.get("/api/thesis/{fmt}")
def thesis_file(fmt: str) -> FileResponse:
    path = THESIS_FILES.get(fmt)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail="dokumenti nuk është ndërtuar ende")
    media = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if fmt == "docx"
        else "application/pdf"
    )
    return FileResponse(path, media_type=media, filename=path.name)


# --- catalogue and jobs -----------------------------------------------------


class JobRequest(BaseModel):
    target: str


@app.get("/api/catalog")
def get_catalog() -> dict[str, Any]:
    return catalog.experiments_payload()


@app.get("/api/jobs")
def list_jobs() -> dict[str, Any]:
    engine = runner()
    return {
        "active": engine.active(),
        "queued": engine.queued(),
        "recent": engine.recent(),
        "busy": engine.is_busy(),
    }


@app.post("/api/jobs")
def create_job(request: JobRequest) -> dict[str, Any]:
    try:
        job = runner().submit(request.target)
    except KeyError:
        raise HTTPException(status_code=400, detail="objektiv i panjohur") from None
    return job.as_dict()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    job = runner().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="puna nuk ekziston")
    _, lines = job.lines_from(0)
    return {**job.as_dict(), "lines": lines}


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict[str, Any]:
    ok = runner().cancel(job_id)
    if not ok:
        raise HTTPException(status_code=409, detail="nuk mund të ndalohet")
    return {"ok": True}


@app.get("/api/jobs/{job_id}/stream")
def stream_job(job_id: str, start: int = Query(0, alias="from")) -> StreamingResponse:
    job = runner().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="puna nuk ekziston")
    return StreamingResponse(
        sse_stream(job, start),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --- services ---------------------------------------------------------------


class ComposeRequest(BaseModel):
    action: str


@app.get("/api/services")
def get_services() -> dict[str, Any]:
    return services.status()


@app.post("/api/services/compose")
def post_compose(request: ComposeRequest) -> dict[str, Any]:
    try:
        return services.compose(request.action)
    except ValueError:
        raise HTTPException(status_code=400, detail="veprim i panjohur") from None


@app.get("/api/database")
def get_database() -> dict[str, Any]:
    return services.database()


def serve(host: str = "127.0.0.1", port: int = 8800, reload: bool = False) -> None:
    import uvicorn

    with contextlib.suppress(KeyboardInterrupt):
        uvicorn.run(
            "webapp.server:app" if reload else app,
            host=host,
            port=port,
            reload=reload,
            log_level="warning",
        )

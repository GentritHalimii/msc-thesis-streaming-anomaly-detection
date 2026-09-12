"""The panel must not drift away from the pipeline.

Everything the panel shows is named by a string: a table, a figure, a verdict,
a column inside a table. Strings rot silently when an experiment renames its
output, and the failure shows up as an empty card in front of an examiner.
These tests turn every one of those names into an assertion.

They deliberately do not need the web framework. Only the last test touches
the HTTP layer, and it skips when the optional dependency group is absent.
"""

from __future__ import annotations

import importlib

import pytest

from webapp import artifacts, catalog, content, metrics

# --- the catalogue ----------------------------------------------------------


def test_every_experiment_points_at_an_importable_module():
    for experiment in catalog.EXPERIMENTS.values():
        importlib.import_module(experiment.module)


def test_experiment_ids_are_unique_and_grouped():
    groups = {group.id for group in catalog.GROUPS}
    for experiment in catalog.EXPERIMENTS.values():
        assert experiment.group in groups, f"{experiment.id} ka grup të panjohur"


def test_batches_only_reference_known_experiments():
    for name, (_, _, members) in catalog.BATCHES.items():
        for member in members:
            assert member in catalog.EXPERIMENTS, f"grupi {name} kërkon {member}"


def test_dependencies_reference_known_experiments():
    for experiment in catalog.EXPERIMENTS.values():
        for need in experiment.needs:
            assert need in catalog.EXPERIMENTS, f"{experiment.id} varet nga {need}"


def test_resolve_rejects_anything_outside_the_catalogue():
    """The runner builds argv from this. An unknown id must never resolve."""
    with pytest.raises(KeyError):
        catalog.resolve("rm -rf /")
    with pytest.raises(KeyError):
        catalog.resolve("experiments.exp0_eda")
    assert catalog.resolve("exp0_eda")[0].id == "exp0_eda"
    assert len(catalog.resolve("evaluate")) > 1


# --- content against the catalogue -----------------------------------------


def _blocks():
    for page in content.PAGES:
        for section in page["sections"]:
            for block in section["blocks"]:
                yield page["id"], section["id"], block


def _catalogue_outputs(key: str) -> set[str]:
    produced: set[str] = set()
    for experiment in catalog.EXPERIMENTS.values():
        produced.update(getattr(experiment, key))
    return produced


def test_page_and_section_ids_are_unique():
    page_ids = [page["id"] for page in content.PAGES]
    assert len(page_ids) == len(set(page_ids))
    for page in content.PAGES:
        ids = [section["id"] for section in page["sections"]]
        assert len(ids) == len(set(ids)), f"{page['id']} ka seksione të përsëritur"


def test_every_referenced_table_is_produced_by_some_experiment():
    """A table nobody generates is a typo, not a missing run."""
    produced = _catalogue_outputs("tables")
    missing = {
        block["source"]
        for _, _, block in _blocks()
        if block["kind"] in {"table", "chart"} and block["source"] not in produced
    }
    assert not missing, f"asnjë eksperiment nuk i prodhon: {sorted(missing)}"


def test_every_referenced_figure_is_produced_by_some_experiment():
    produced = _catalogue_outputs("figures")
    missing = {
        block["source"]
        for _, _, block in _blocks()
        if block["kind"] == "figure" and block["source"] not in produced
    }
    assert not missing, f"asnjë eksperiment nuk i prodhon: {sorted(missing)}"


def test_every_referenced_verdict_is_produced_by_some_experiment():
    produced = {e.verdict for e in catalog.EXPERIMENTS.values() if e.verdict}
    missing = {
        block["source"]
        for _, _, block in _blocks()
        if block["kind"] == "verdict" and block["source"] not in produced
    }
    assert not missing, f"asnjë eksperiment nuk i prodhon: {sorted(missing)}"


def test_runner_blocks_reference_known_experiments():
    for page_id, section_id, block in _blocks():
        if block["kind"] != "runner":
            continue
        for experiment in block["experiments"]:
            assert experiment in catalog.EXPERIMENTS, f"{page_id}/{section_id}: {experiment}"


def test_widgets_are_all_implemented_in_the_front_end():
    """The renderer map in widgets.js is the contract; keep it in step."""
    source = (artifacts.REPO_ROOT / "webapp" / "static" / "js" / "widgets.js").read_text()
    for _, _, block in _blocks():
        if block["kind"] != "widget":
            continue
        name = block["widget"]
        assert f"{name}," in source or f"{name}:" in source, f"widgets.js nuk njeh '{name}'"


# --- content against what is actually on disk ------------------------------


def _has_results() -> bool:
    return artifacts.has_table("benchmark_summary")


needs_results = pytest.mark.skipif(
    not _has_results(), reason="rezultatet nuk janë gjeneruar në këtë mjedis"
)


@needs_results
def test_chart_specs_name_columns_that_exist():
    """The commonest way to break a chart is to rename a CSV column."""
    problems: list[str] = []
    for page_id, section_id, block in _blocks():
        if block["kind"] != "chart" or not artifacts.has_table(block["source"]):
            continue
        columns = set(artifacts.table_frame(block["source"]).columns)
        wanted: list[str] = []
        for key in ("x", "y", "label", "value", "error", "group", "index", "facet", "rowKey"):
            value = block.get(key)
            if isinstance(value, str):
                wanted.append(value)
        for entry in block.get("series", []) or []:
            wanted.append(entry["col"])
        if isinstance(block.get("pivot"), dict):
            wanted += [block["pivot"]["column"], block["pivot"]["value"]]
        if isinstance(block.get("error"), dict):
            wanted += list(block["error"].values())
        for column in wanted:
            if column not in columns:
                problems.append(f"{page_id}/{section_id} [{block['source']}]: '{column}'")
    assert not problems, "kolona që nuk ekzistojnë: " + "; ".join(problems)


@needs_results
def test_table_specs_name_columns_that_exist():
    problems: list[str] = []
    for page_id, section_id, block in _blocks():
        if block["kind"] != "table" or not artifacts.has_table(block["source"]):
            continue
        columns = set(artifacts.table_frame(block["source"]).columns)
        wanted = list(block.get("columns") or []) + list((block.get("round") or {}).keys())
        if block.get("highlight"):
            wanted.append(block["highlight"])
        for column in wanted:
            if column not in columns:
                problems.append(f"{page_id}/{section_id} [{block['source']}]: '{column}'")
    assert not problems, "kolona që nuk ekzistojnë: " + "; ".join(problems)


@needs_results
def test_table_queries_are_valid_and_select_something():
    for page_id, section_id, block in _blocks():
        query = block.get("query")
        if not query or not artifacts.has_table(block["source"]):
            continue
        payload = artifacts.read_table(block["source"], query)
        assert payload["n_rows"] > 0, f"{page_id}/{section_id}: '{query}' nuk zgjedh asgjë"


@needs_results
@pytest.mark.parametrize("name", sorted(metrics.COMPUTATIONS))
def test_metric_tiles_compute_without_raising(name):
    tiles = metrics.compute(name)
    assert isinstance(tiles, list)
    for tile in tiles:
        assert tile["label"], "çdo tile duhet të ketë etiketë"
        assert tile["label"] != "Gabim", f"llogaritja '{name}' dështoi: {tile.get('hint')}"


@needs_results
def test_reading_a_table_survives_missing_values():
    payload = artifacts.read_table("tuning_effect")
    for row in payload["rows"]:
        for value in row.values():
            assert value is None or isinstance(value, int | float | str | bool)


# --- the HTTP layer ---------------------------------------------------------


def test_pages_resolve_over_http():
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from webapp.server import app

    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        meta = client.get("/api/meta").json()
        assert meta["navigation"], "navigimi është bosh"
        for page in meta["navigation"]:
            response = client.get(f"/api/page/{page['id']}")
            assert response.status_code == 200, page["id"]
            payload = response.json()
            assert payload["sections"], f"{page['id']} nuk ka seksione"
        assert client.get("/api/page/nuk-ekziston").status_code == 404
        assert client.post("/api/jobs", json={"target": "sudo rm"}).status_code == 400


@needs_results
def test_staleness_only_reports_runs_that_write_a_manifest():
    """Three helpers write figures or a document and no manifest. Reporting
    them as "never run" would train the reader to ignore the warning."""
    report = artifacts.staleness()
    silent = {e.id for e in catalog.EXPERIMENTS.values() if not e.writes_manifest}
    assert not (set(report["never_run"]) & silent)
    for item in report["stale"]:
        assert item["newer_inputs"], "një hyrje më e re duhet të emërtohet"
        for newer in item["newer_inputs"]:
            assert newer["timestamp"] > item["timestamp"]

"""Integrity of the thesis source.

The document is generated from data, so the failure mode to guard against is
a chapter referring to something that does not exist: a citation key with a
typo, a figure that was renamed, a table column that an experiment stopped
emitting. Those break the build, but only when someone runs it; these checks
catch them in the ordinary test run.
"""

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
THESIS = REPO_ROOT / "thesis"
RESULTS = REPO_ROOT / "results"
sys.path.insert(0, str(THESIS))

from references import REFERENCES  # noqa: E402

CITE_RE = re.compile(r"\[@([a-zA-Z0-9_]+)\]")
VALID_KINDS = {"h1", "h2", "h3", "p", "note", "bullets", "numbers", "fig", "tab", "eq", "pagebreak"}


def all_chapters():
    from content import (
        ch1_hyrje,
        ch2_literatura,
        ch3_problemi,
        ch4_metodologjia,
        ch5_rezultatet,
        ch6_diskutime,
        ch8_shtojcat,
    )

    return {
        "ch1": ch1_hyrje.BLOCKS,
        "ch2": ch2_literatura.BLOCKS,
        "ch3": ch3_problemi.BLOCKS,
        "ch4": ch4_metodologjia.BLOCKS,
        "ch5": ch5_rezultatet.BLOCKS,
        "ch6": ch6_diskutime.BLOCKS,
        "ch8": ch8_shtojcat.BLOCKS,
    }


def _texts(blocks):
    for block in blocks:
        kind = block[0]
        if kind in ("p", "note"):
            yield block[1]
        elif kind in ("bullets", "numbers"):
            yield from block[1]
        elif kind in ("h1", "h2", "h3", "fig", "tab"):
            yield block[2]


def test_every_block_has_a_known_kind():
    for name, blocks in all_chapters().items():
        for block in blocks:
            assert block[0] in VALID_KINDS, f"{name}: unknown block kind {block[0]}"


def test_every_citation_key_exists():
    unknown = set()
    for blocks in all_chapters().values():
        for text in _texts(blocks):
            unknown |= {k for k in CITE_RE.findall(text) if k not in REFERENCES}
    assert not unknown, f"citations with no reference entry: {sorted(unknown)}"


def test_reference_list_has_no_unused_entries():
    """An uncited work belongs in a bibliography, not in the references."""
    used = set()
    for blocks in all_chapters().values():
        for text in _texts(blocks):
            used |= set(CITE_RE.findall(text))
    unused = set(REFERENCES) - used
    assert not unused, f"reference entries never cited: {sorted(unused)}"


def test_section_numbers_are_unique_and_ordered():
    for name, blocks in all_chapters().items():
        numbers = [b[1] for b in blocks if b[0] in ("h1", "h2", "h3")]
        assert len(numbers) == len(set(numbers)), f"{name}: duplicate section numbers"
        as_tuples = [tuple(int(part) for part in n.split(".")) for n in numbers]
        assert as_tuples == sorted(as_tuples), f"{name}: sections out of order: {numbers}"


@pytest.mark.skipif(not (RESULTS / "figures").exists(), reason="results not generated")
def test_every_referenced_figure_exists():
    missing = []
    for blocks in all_chapters().values():
        for block in blocks:
            if block[0] == "fig" and not (RESULTS / "figures" / f"{block[1]}.png").exists():
                missing.append(block[1])
    assert not missing, f"figures referenced but not generated: {sorted(set(missing))}"


@pytest.mark.skipif(not RESULTS.exists(), reason="results not generated")
def test_every_referenced_table_exists_with_its_columns():
    problems = []
    import pandas as pd

    for blocks in all_chapters().values():
        for block in blocks:
            if block[0] != "tab":
                continue
            path = RESULTS / f"{block[1]}.csv"
            if not path.exists():
                problems.append(f"{block[1]}: file missing")
                continue
            columns = set(pd.read_csv(path, nrows=1).columns)
            options = block[3]
            for key in ("columns", "rename", "round", "fmt"):
                wanted = options.get(key) or []
                missing = set(wanted) - columns
                if missing:
                    problems.append(f"{block[1]}.{key}: {sorted(missing)}")
    assert not problems, "table references do not match generated data: " + "; ".join(problems)

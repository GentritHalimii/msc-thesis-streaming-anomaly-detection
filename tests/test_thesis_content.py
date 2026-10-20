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
            options = block[3]
            if "pivot" in options:
                # A pivoted table gets one column per value of the pivot column.
                spec = options["pivot"]
                data = pd.read_csv(path)
                columns = {spec["index"], *data[spec["columns"]].astype(str)}
            else:
                columns = set(pd.read_csv(path, nrows=1).columns)
            for key in ("columns", "rename", "round", "fmt", "replace"):
                wanted = options.get(key) or []
                missing = set(wanted) - columns
                if missing:
                    problems.append(f"{block[1]}.{key}: {sorted(missing)}")
    assert not problems, "table references do not match generated data: " + "; ".join(problems)


# --- references and citations as Word fields --------------------------------
# The template asks for automatic references. That means the numbers belong to
# Word: the reference list is a numbering definition, each entry carries a
# bookmark, and every in-text citation is a cross-reference to one. These
# checks pin the wiring, because a broken field shows up in Word as an error
# message where a citation should be, and never at build time.


def _field_instructions(paragraph):
    from docx.oxml.ns import qn

    return [node.text for node in paragraph._p.iter(qn("w:instrText"))]


def _field_results(paragraph):
    from docx.oxml.ns import qn

    inside, results = False, []
    for node in paragraph._p.iter():
        if node.tag == qn("w:fldChar"):
            kind = node.get(qn("w:fldCharType"))
            inside = kind == "separate"
        elif node.tag == qn("w:t") and inside:
            results.append(node.text)
    return results


def test_adjacent_citations_become_separate_fields():
    from build_thesis import Numbering, resolve_citations
    from docx_helpers import add_paragraph, new_document, reference_bookmark

    keys = sorted(REFERENCES)[:2]
    numbering = Numbering()
    text = f"Fjali me dy burime [@{keys[0]}][@{keys[1]}]."
    doc = new_document()
    para = add_paragraph(doc, resolve_citations(text, numbering))

    instructions = _field_instructions(para)
    assert len(instructions) == 2, "each citation needs its own field"
    for key, instruction in zip(keys, instructions, strict=True):
        assert reference_bookmark(key) in instruction
        assert "\\r" in instruction, "the field must report the entry's own number"
    assert _field_results(para) == ["[1]", "[2]"], "the cached result carries the number"
    assert ", " in para.text, "IEEE separates adjacent citations with a comma"
    assert "" not in para.text and "" not in para.text


def test_reference_entries_are_word_numbered_and_bookmarked():
    from docx.oxml.ns import qn
    from docx_helpers import (
        add_paragraph,
        apply_list_numbering,
        bookmark_paragraph,
        define_reference_numbering,
        new_document,
        reference_bookmark,
    )

    doc = new_document()
    num_id = define_reference_numbering(doc)
    keys = sorted(REFERENCES)[:3]
    for index, key in enumerate(keys, start=1):
        para = add_paragraph(doc, REFERENCES[key])
        apply_list_numbering(para, num_id)
        bookmark_paragraph(para, reference_bookmark(key), index)

    numbering = doc.part.numbering_part.element
    defined = [
        el
        for el in numbering.findall(qn("w:abstractNum"))
        if el.get(qn("w:abstractNumId")) == str(num_id)
    ]
    assert defined, "the reference list needs its own numbering definition"
    level = defined[0].find(qn("w:lvl"))
    assert level.find(qn("w:lvlText")).get(qn("w:val")) == "[%1]"
    assert level.find(qn("w:numFmt")).get(qn("w:val")) == "decimal"

    names = {el.get(qn("w:name")) for el in doc.element.body.iter(qn("w:bookmarkStart"))}
    assert {reference_bookmark(k) for k in keys} <= names
    assert not any(REFERENCES[k].startswith("[") for k in keys), (
        "the number comes from Word, so it is not written into the entry"
    )


def test_every_figure_reference_names_a_figure():
    """[[fig:name]] is replaced by the figure's number at build time; a typo
    would only surface when the document is built, so it is caught here."""
    figure_ref = re.compile(r"\[\[fig:([a-zA-Z0-9_]+)\]\]")
    chapters = all_chapters()
    names = {b[1] for blocks in chapters.values() for b in blocks if b[0] == "fig"}
    dangling = set()
    for blocks in chapters.values():
        for text in _texts(blocks):
            dangling |= {n for n in figure_ref.findall(text) if n not in names}
    assert not dangling, f"references to figures that do not exist: {sorted(dangling)}"


def test_hyphen_before_an_ending_does_not_break():
    """ "AP-" at the end of one line and "së" at the start of the next reads as
    a typo, so the hyphen before an inflectional ending is non-breaking. Long
    compounds may still break, and URLs keep their plain hyphens."""
    from docx.oxml.ns import qn
    from docx_helpers import add_paragraph, new_document

    doc = new_document()
    para = add_paragraph(doc, "AP-së e Autoencoder-it në 8-fold, me rolling-origin.")
    assert len(list(para._p.iter(qn("w:noBreakHyphen")))) == 3
    assert para.text == "AP-së e Autoencoder-it në 8-fold, me rolling-origin."

    url = add_paragraph(doc, "Burimi: https://example.org/data-set")
    assert not list(url._p.iter(qn("w:noBreakHyphen")))


def test_list_of_figures_entries_are_not_cut():
    """The lists of figures and tables show each caption's first sentence; one
    longer than the limit would be cut short with an ellipsis."""
    from build_thesis import _scan_captions
    from content.front_matter import _shorten

    figures, tables = _scan_captions(list(all_chapters().values()))
    cut = [caption for caption in figures + tables if _shorten(caption).endswith("…")]
    assert not cut, f"first sentence too long for the list: {cut}"


def test_table_numbers_print_with_fixed_decimals():
    """A column of numbers keeps one number of decimals, p-values keep two
    significant digits, and large counts are grouped in thousands."""
    import pandas as pd
    from build_thesis import _decimals, _fixed, _group_thousands, _p_value

    values = pd.Series([0.1886, 0.169, 0.0043])
    assert list(_fixed(values, _decimals(values))) == ["0.1886", "0.1690", "0.0043"]
    assert _decimals(pd.Series([58.8483, 24.287])) == 2
    assert [_p_value(p) for p in (0.0078125, 0.000151, 2.6e-06, 1.0)] == [
        "0.0078",
        "0.00015",
        "< 0.0001",
        "1.0",
    ]
    grouped = _group_thousands(pd.Series([6415, 17327, "n/a"], dtype=object))
    assert list(grouped) == ["6\u00a0415", "17\u00a0327", "n/a"]

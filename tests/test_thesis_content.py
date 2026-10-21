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

    # Word reads w:pPr only as a paragraph's first child, and w:numPr only
    # ahead of the spacing and alignment; LibreOffice forgives both, Word may
    # drop the number.
    for para in doc.paragraphs[-len(keys) :]:
        assert para._p[0].tag == qn("w:pPr"), "the bookmark must follow the properties"
        tags = [child.tag for child in para._p.pPr]
        assert tags.index(qn("w:numPr")) < tags.index(qn("w:spacing"))


def test_each_section_has_one_page_number_format_before_its_columns():
    from docx.oxml.ns import qn
    from docx_helpers import new_document, start_new_section

    doc = new_document()
    start_new_section(doc, "upperRoman", start=1)
    # A new section starts as a copy of the previous one, Roman numbering
    # included; the body's own format must replace it, not follow it.
    start_new_section(doc, "decimal", start=1)
    formats = []
    for section in doc.sections[1:]:
        tags = [child.tag for child in section._sectPr]
        assert tags.count(qn("w:pgNumType")) == 1
        assert tags.index(qn("w:pgNumType")) < tags.index(qn("w:cols"))
        formats.append(section._sectPr.find(qn("w:pgNumType")).get(qn("w:fmt")))
    assert formats == ["upperRoman", "decimal"]


def _effective_alignment(paragraph):
    if paragraph.alignment is not None:
        return paragraph.alignment
    return paragraph.style.paragraph_format.alignment


def test_contents_and_lists_are_word_automatic_tables():
    """The contents and the two lists are Word's own TOC fields, which Word
    updates and whose entries a Ctrl+click follows. Written out as plain
    lines, as an earlier build did, they looked right but stayed frozen."""
    from content.front_matter import FRONT_ENTRIES, render_prelims
    from docx.oxml.ns import qn
    from docx_helpers import (
        CONTENTS_FIELD,
        FIGURE_LIST_FIELD,
        TABLE_LIST_FIELD,
        heading_bookmark,
        new_document,
        title_bookmark,
    )

    doc = new_document()
    outline = [(1, "1\tHyrje"), (2, "1.1\tKonteksti")]
    figures = ["Figura 1. Një figurë. Me një shënim."]
    render_prelims(doc, outline, figures, ["Tabela 1. Një tabelë."], {})
    paras = doc.paragraphs
    texts = [para.text for para in paras]

    # The template's contents uses exactly these switches.
    assert CONTENTS_FIELD.split() == ["TOC", "\\o", '"1-3"', "\\h", "\\z", "\\u"]
    tables = [i for para in paras for i in _field_instructions(para) if "TOC" in i]
    assert tables == [CONTENTS_FIELD, FIGURE_LIST_FIELD, TABLE_LIST_FIELD]

    # The contents opens with the two lists and the glossary, then the
    # chapters in capitals, as in the template's example. Each line links to
    # its title, and its page number is a field on the same bookmark.
    start = texts.index("PËRMBAJTJA")
    lines = [text.rstrip("\t") for text in texts[start + 1 : start + 6]]
    assert lines == [*FRONT_ENTRIES, "1\tHYRJE", "1.1\tKonteksti"]
    for para, target in zip(
        paras[start + 1 : start + 6],
        [
            *(title_bookmark(t) for t in FRONT_ENTRIES),
            heading_bookmark("1"),
            heading_bookmark("1.1"),
        ],
        strict=True,
    ):
        assert para._p.find(qn("w:hyperlink")).get(qn("w:anchor")) == target
        assert f"PAGEREF {target} " in " ".join(_field_instructions(para))
    assert paras[start + 4].style.name == "toc 1"
    assert paras[start + 5].style.name == "toc 2"

    # The figure list shows the caption's first sentence, which is all the
    # caption paragraph holds.
    assert "Figura 1. Një figurë.\t" in texts

    # Word's contents finds the three listed titles because they are
    # headings; the abstracts, the acknowledgements and the contents' own
    # title are not, so the contents leaves them out, as the template asks.
    def last(title):
        return paras[len(texts) - 1 - texts[::-1].index(title)]

    for title in FRONT_ENTRIES:
        assert last(title).style.name == "Heading 1", title
        assert last(title).paragraph_format.page_break_before is None
    for title in ("ABSTRAKT", "ABSTRACT", "MIRËNJOHJE", "PËRMBAJTJA"):
        assert last(title).style.name == "Normal", title

    # The table list follows the figure list without a page break.
    between = paras[texts.index("LISTA E FIGURAVE") : texts.index("LISTA E TABELAVE")]
    breaks = [br for para in between for br in para._p.iter(qn("w:br"))]
    assert not breaks, "the table list must not start a new page"

    # Every title in the front matter is aligned left.
    for title in ("ABSTRAKT", "PËRMBAJTJA", *FRONT_ENTRIES):
        assert _effective_alignment(last(title)) == 0, f"{title} is not aligned left"


def test_a_title_left_alone_at_the_foot_of_a_page_moves_to_the_next(monkeypatch):
    """LibreOffice does not keep a title with the automatic table under it,
    as Word does; the first pass reports such a title and the second starts
    it on the next page, with that page's number in the contents."""
    import build_thesis

    pages = [
        "ABSTRAKT\nTeksti.\nI",
        "PËRMBAJTJA\nLISTA E FIGURAVE......II\nII",
        "LISTA E FIGURAVE\nFigura 1. Një figurë......5\nLISTA E TABELAVE\nIII",
        "Tabela 1. Një tabelë......7\nIV",
    ]
    monkeypatch.setattr(build_thesis, "_pdf_pages", lambda _path: pages)
    titles = ["LISTA E FIGURAVE", "LISTA E TABELAVE"]
    mapping, stranded = build_thesis.extract_front_pages(Path("thesis.pdf"), titles)
    assert stranded == {"LISTA E TABELAVE"}
    assert mapping == {"LISTA E FIGURAVE": "III", "LISTA E TABELAVE": "IV"}


def test_captions_are_numbered_by_word():
    """A caption's number is a SEQ field, which Word renumbers and builds the
    lists from, inside the bookmark that the lists and the text point to.
    The paragraph Word lists keeps the first sentence; a reading note
    follows in a paragraph of its own."""
    from docx.oxml.ns import qn
    from docx_helpers import add_caption, figure_bookmark, new_document

    doc = new_document()
    para = add_caption(doc, "Figura", 3, "Një titull. Një shënim.", bookmark=figure_bookmark(3))
    assert para.style.name == "Caption"
    assert _field_instructions(para) == [" SEQ Figura \\* ARABIC "]
    assert para.text == "Figura 3. Një titull."
    assert doc.paragraphs[-1].text == "Një shënim."
    assert doc.paragraphs[-1].style.name == "Caption"

    children = list(para._p)
    start = next(i for i, el in enumerate(children) if el.tag == qn("w:bookmarkStart"))
    assert children[start].get(qn("w:name")) == figure_bookmark(3)
    assert children[start + 2].tag == qn("w:bookmarkEnd"), "the bookmark holds the number only"
    number = children[start + 1]
    assert [el.text for el in number.iter(qn("w:instrText"))] == [" SEQ Figura \\* ARABIC "]
    assert [el.text for el in number.iter(qn("w:t"))] == ["3"]


def test_figure_number_in_the_text_is_a_cross_reference():
    from build_thesis import Numbering, resolve_citations
    from docx_helpers import add_paragraph, figure_bookmark, new_document

    numbering = Numbering()
    numbering.figure_numbers["arkitektura"] = 4
    doc = new_document()
    para = add_paragraph(
        doc, resolve_citations("Siç tregon Figura [[fig:arkitektura]].", numbering)
    )
    assert _field_instructions(para) == [f" REF {figure_bookmark(4)} \\h "]
    assert _field_results(para) == ["4"]
    assert para.text == "Siç tregon Figura 4."


def test_headings_and_captions_take_their_look_from_word_styles():
    """Word copies formatting set on a heading's or a caption's text into the
    entry it writes for the contents or the lists, so the template's look is
    in the styles and the text carries none of its own."""
    from docx.shared import Pt
    from docx_helpers import TEXT_WIDTH_CM, add_caption, add_heading, new_document

    doc = new_document()
    heading = add_heading(doc, "Hyrje", 1, "1")
    caption = add_caption(doc, "Tabela", 1, "Një tabelë.", above=True)
    assert heading.text == "1\tHYRJE"
    for para in (heading, caption):
        assert all(run._r.rPr is None for run in para.runs), para.text

    for level, size in ((1, 14), (2, 12), (3, 12)):
        style = doc.styles[f"Heading {level}"]
        font = style.font
        assert (font.name, font.size, font.bold) == ("Times New Roman", Pt(size), True)
        assert bool(font.all_caps) == (level == 1)
        assert str(font.color.rgb) == "000000"
        fonts = style.element.rPr.rFonts
        assert not [name for name in fonts.attrib if "heme" in name], "no theme font"
        assert style.paragraph_format.alignment == 0
    caption_font = doc.styles["Caption"].font
    assert (caption_font.name, caption_font.size, caption_font.bold) == (
        "Times New Roman",
        Pt(11),
        False,
    )

    # Word applies these four styles to every entry it writes.
    for name, style_id in (
        ("toc 1", "TOC1"),
        ("toc 2", "TOC2"),
        ("toc 3", "TOC3"),
        ("table of figures", "TableofFigures"),
    ):
        style = doc.styles[name]
        assert style.style_id == style_id
        assert style.builtin, "Word applies its built-in TOC styles, not a custom namesake"
        stops = list(style.paragraph_format.tab_stops)
        assert abs(stops[-1].position.cm - TEXT_WIDTH_CM) < 0.01
        assert stops[-1].leader == 1, "dots lead to the page number"  # WD_TAB_LEADER.DOTS


def test_word_is_asked_to_update_the_fields_on_opening():
    """w:updateFields belongs ahead of w:compat; appended at the end of the
    settings, as an earlier build wrote it, it is out of the schema's order."""
    from docx.oxml.ns import qn
    from docx_helpers import new_document

    settings = new_document().settings.element
    tags = [child.tag for child in settings]
    assert settings.find(qn("w:updateFields")).get(qn("w:val")) == "true"
    assert tags.index(qn("w:updateFields")) < tags.index(qn("w:compat"))


def test_title_pages_are_times_new_roman_14_with_only_the_title_bold():
    from content.front_matter import TITULLI, render_cover
    from docx.shared import Pt
    from docx_helpers import new_document

    doc = new_document()
    render_cover(doc)
    lines = [para for para in doc.paragraphs if para.text.strip()]
    assert lines, "the title pages have text"
    for para in lines:
        for run in para.runs:
            assert run.font.name == "Times New Roman"
            assert run.font.size == Pt(14), para.text
            assert bool(run.bold) == (para.text == TITULLI), para.text


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


def test_list_entries_are_the_caption_paragraphs_word_lists():
    """Word rebuilds the lists from the caption paragraphs, so the entries
    written at build time must read exactly as those paragraphs do, or the
    lists would change the first time Word updates them."""
    from build_thesis import Numbering, _scan_captions, resolve_citations
    from content.front_matter import _list_entries
    from docx_helpers import FIGURE_LABEL, TABLE_LABEL, add_caption, new_document

    figures, tables = _scan_captions(list(all_chapters().values()))
    doc = new_document()
    for captions, label in ((figures, FIGURE_LABEL), (tables, TABLE_LABEL)):
        entries = _list_entries(captions, str, {})
        for number, (caption, entry) in enumerate(zip(captions, entries, strict=True), start=1):
            text = resolve_citations(caption.partition(". ")[2], Numbering())
            assert entry[1] == add_caption(doc, label, number, text).text


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

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


# --- references and citations as Word's own ---------------------------------
# The references must not be manual. Word's own way is its source list, its
# CITATION fields and its BIBLIOGRAPHY field, which the References tab
# manages. These checks pin the wiring, because a broken citation shows up in
# Word as an error message where the number should be, and never at build
# time.


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


def test_adjacent_citations_become_separate_word_citations():
    from bibliography import source_tag
    from build_thesis import Numbering, resolve_citations
    from docx.oxml.ns import qn
    from docx_helpers import add_paragraph, new_document

    keys = sorted(REFERENCES)[:2]
    numbering = Numbering()
    text = f"Fjali me dy burime [@{keys[0]}][@{keys[1]}]."
    doc = new_document()
    para = add_paragraph(doc, resolve_citations(text, numbering))

    assert _field_instructions(para) == [f" CITATION {source_tag(key)} \\l 1033 " for key in keys]
    assert _field_results(para) == ["[1]", "[2]"], "the cached result carries the number"
    controls = para._p.findall(qn("w:sdt"))
    assert len(controls) == 2, "each citation sits in a content control of its own"
    for control in controls:
        assert control.find(f"{qn('w:sdtPr')}/{qn('w:citation')}") is not None
    assert ", " in para.text, "IEEE separates adjacent citations with a comma"
    assert "\ue000" not in para.text and "\ue001" not in para.text


def test_reference_list_is_word_bibliography_over_the_document_sources():
    from bibliography import BIBLIOGRAPHY_NS, ieee_entry, source_tag, word_sources
    from docx.oxml.ns import qn
    from docx_helpers import add_bibliography, new_document, set_bibliography_sources
    from lxml import etree

    cited = ["liu2008", "hawkins1980", "ulb_dataset"]
    doc = new_document()
    entries = [(number, ieee_entry(REFERENCES[key])) for number, key in enumerate(cited, 1)]
    add_bibliography(doc, entries)
    set_bibliography_sources(doc, word_sources(cited))

    # The list is a BIBLIOGRAPHY field inside the two content controls that
    # Word's References > Bibliography writes.
    outer = doc.element.body.find(qn("w:sdt"))
    gallery = outer.find(f"{qn('w:sdtPr')}/{qn('w:docPartObj')}/{qn('w:docPartGallery')}")
    assert gallery.get(qn("w:val")) == "Bibliographies"
    inner = outer.find(f"{qn('w:sdtContent')}/{qn('w:sdt')}")
    assert inner.find(f"{qn('w:sdtPr')}/{qn('w:bibliography')}") is not None
    assert [node.text for node in inner.iter(qn("w:instrText"))] == [" BIBLIOGRAPHY "]
    labels = [
        "".join(node.text for node in row.find(qn("w:tc")).iter(qn("w:t")))
        for row in inner.iter(qn("w:tr"))
    ]
    assert labels == ["[1]", "[2]", "[3]"]

    # The sources are the document's own source list, with Word's IEEE
    # style, numbered in the order of first citation.
    part = next(
        rel.target_part for rel in doc.part.rels.values() if rel.reltype.endswith("/customXml")
    )
    root = etree.fromstring(part.blob)
    assert (root.get("StyleName"), root.get("SelectedStyle")) == (
        "IEEE",
        "\\IEEE2006OfficeOnline.xsl",
    )
    b = f"{{{BIBLIOGRAPHY_NS}}}"
    sources = root.findall(f"{b}Source")
    assert [source.findtext(f"{b}Tag") for source in sources] == [source_tag(k) for k in cited]
    assert [source.findtext(f"{b}RefOrder") for source in sources] == ["1", "2", "3"]


def test_sources_carry_the_fields_word_formats_them_from():
    from bibliography import BIBLIOGRAPHY_NS, word_sources
    from lxml import etree

    b = f"{{{BIBLIOGRAPHY_NS}}}"
    pang, liu, ecb = etree.fromstring(word_sources(["pang2021", "liu2008", "ebaecb2025"]))
    names = [(p.findtext(f"{b}First"), p.findtext(f"{b}Last")) for p in pang.iter(f"{b}Person")]
    assert names[-1] == ("A.", "van den Hengel"), "a surname of several words stays whole"
    # Word's journal article has no article-number field; it follows the issue.
    assert pang.findtext(f"{b}Issue") == "2, Art. no. 38"
    assert liu.findtext(f"{b}SourceType") == "ConferenceProceedings"
    assert liu.findtext(f"{b}ConferenceName") == "Proc. 8th IEEE Int. Conf. Data Mining (ICDM)"
    # Word's IEEE style prints "pp." only for a range written with a hyphen.
    assert liu.findtext(f"{b}Pages") == "413-422"
    assert ecb.findtext(f".//{b}Corporate") == (
        "European Banking Authority and European Central Bank"
    )
    accessed = [ecb.findtext(f"{b}{part}Accessed") for part in ("Year", "Month", "Day")]
    assert accessed == ["2026", "November", "16"]


def test_reference_entries_print_in_ieee_style():
    """One source of each type, as the reference list prints it."""
    from bibliography import ieee_entry

    def text(key):
        return "".join(piece for piece, _ in ieee_entry(REFERENCES[key]))

    def italic(key):
        return [piece for piece, slanted in ieee_entry(REFERENCES[key]) if slanted]

    assert text("liu2012") == (
        "F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation-based anomaly detection,” ACM Trans. "
        "Knowledge Discovery from Data, vol. 6, no. 1, pp. 1–39, 2012."
    )
    assert italic("liu2012") == ["ACM Trans. Knowledge Discovery from Data"]
    assert text("kingma2014") == (
        "D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” in Proc. 2nd Int. Conf. "
        "Learning Representations (ICLR), Banff, Canada, 2014."
    )
    assert text("aggarwal2017") == (
        "C. C. Aggarwal, Outlier Analysis, 2nd ed. Cham, Switzerland: Springer, 2017."
    )
    assert italic("aggarwal2017") == ["Outlier Analysis"]
    assert text("ulb_dataset") == (
        "Machine Learning Group – Université Libre de Bruxelles, “Credit Card Fraud Detection "
        "dataset,” Kaggle, 2018. Accessed: Sep. 13, 2026. [Online]. Available: "
        "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
    )
    # IEEE names up to six authors and cuts a longer list to "et al.".
    assert text("li2022ecod").startswith("Z. Li, Y. Zhao, X. Hu, N. Botta, C. Ionescu, and G. H.")
    assert text("pedregosa2011").startswith("F. Pedregosa et al., “Scikit-learn")
    for key in REFERENCES:
        assert text(key), key


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
    for title in ("ABSTRAKT", "MIRËNJOHJE/FALËNDERIME", "PËRMBAJTJA"):
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
    lists from. As Word's Insert Caption writes it, a hidden "_Ref" bookmark
    holds the label and the number, and each part of the field sits in a run
    of its own; a bookmark around the number alone did not survive Word's
    field update. The paragraph Word lists keeps the first sentence; a
    reading note follows in a paragraph of its own."""
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
    end = next(i for i, el in enumerate(children) if el.tag == qn("w:bookmarkEnd"))
    assert children[start].get(qn("w:name")) == figure_bookmark(3)
    assert figure_bookmark(3).startswith("_Ref")
    inside = children[start + 1 : end]
    assert "".join(t.text for el in inside for t in el.iter(qn("w:t"))) == "Figura 3"
    kinds = [[c.tag for c in run if c.tag != qn("w:rPr")] for run in inside]
    assert kinds == [
        [qn("w:t")],
        [qn("w:fldChar")],
        [qn("w:instrText")],
        [qn("w:fldChar")],
        [qn("w:t")],
        [qn("w:fldChar")],
    ], "label, then the field one part per run"


def test_figure_number_in_the_text_is_plain_text():
    """Word lost the bookmarks a cross-reference field needs, and every
    reference read "Error! Reference source not found". "Figura [[fig:name]]"
    is therefore plain text, the label and the number from the same count as
    the captions, joined by a no-break space so a line never ends between
    them. No field and no link."""
    from build_thesis import Numbering, resolve_citations
    from docx.oxml.ns import qn
    from docx_helpers import add_paragraph, new_document

    numbering = Numbering()
    numbering.figure_numbers["arkitektura"] = 4
    doc = new_document()
    para = add_paragraph(
        doc, resolve_citations("Siç tregon Figura [[fig:arkitektura]].", numbering)
    )
    assert _field_instructions(para) == []
    assert not list(para._p.iter(qn("w:hyperlink")))
    assert para.text == "Siç tregon Figura\u00a04."


def test_a_figure_reference_without_its_label_is_refused():
    """The reference repeats the caption's label, so a bare [[fig:name]]
    would read as a number with no label; the build stops instead."""
    from build_thesis import Numbering, resolve_citations

    numbering = Numbering()
    numbering.figure_numbers["arkitektura"] = 4
    with pytest.raises(ValueError, match="Figura"):
        resolve_citations("Siç tregon [[fig:arkitektura]].", numbering)


def test_figure_references_in_the_thesis_carry_their_label():
    chapters = all_chapters()
    bare = [
        text[max(0, m.start() - 30) : m.end()]
        for blocks in chapters.values()
        for text in _texts(blocks)
        for m in re.finditer(r"\[\[fig:[a-zA-Z0-9_]+\]\]", text)
        if not text[: m.start()].endswith(("Figura ", "Figura\u00a0"))
    ]
    assert not bare, f"write these as 'Figura [[fig:name]]': {bare}"


def test_a_table_reference_is_plain_text_with_its_label():
    """Tables are referenced like figures: "Tabela [[tab:name]]", where the
    name is the results file the table is drawn from, becomes the label and
    the table's number joined by a no-break space."""
    from build_thesis import Numbering, resolve_citations

    numbering = Numbering()
    numbering.table_numbers["fold_summary"] = 2
    text = resolve_citations("Tabela [[tab:fold_summary]] tregon blloqet.", numbering)
    assert text == "Tabela\u00a02 tregon blloqet."
    with pytest.raises(ValueError, match="Tabela"):
        resolve_citations("Siç tregon [[tab:fold_summary]].", numbering)
    numbering.ambiguous_tables.add("fold_summary")
    with pytest.raises(ValueError, match="more than one table"):
        resolve_citations("Tabela [[tab:fold_summary]].", numbering)


def test_every_figure_and_table_is_referenced_in_the_text():
    """The mentor's rule: the text refers to every figure and every table by
    its number, so none of them stands unexplained."""
    chapters = all_chapters()
    prose = " ".join(
        text
        for blocks in chapters.values()
        for block in blocks
        if block[0] in ("p", "note", "bullets", "numbers")
        for text in ([block[1]] if block[0] in ("p", "note") else block[1])
    )
    missing = [
        f"{kind}:{block[1]}"
        for blocks in chapters.values()
        for block in blocks
        for kind in [{"fig": "fig", "tab": "tab"}.get(block[0])]
        if kind and f"[[{kind}:{block[1]}]]" not in prose
    ]
    assert not missing, f"never referenced in the text: {missing}"


def test_glossary_is_in_alphabetical_order():
    from content.front_matter import FJALORI

    terms = [term for term, _ in FJALORI]
    assert terms == sorted(terms, key=str.casefold)


def test_headings_and_captions_take_their_look_from_word_styles():
    """Word copies formatting set on a heading's or a caption's text into the
    entry it writes for the contents or the lists, so the template's look is
    in the styles and the text carries none of its own."""
    from docx.oxml.ns import qn
    from docx.shared import Pt
    from docx_helpers import TEXT_WIDTH_CM, add_caption, add_heading, heading_bookmark, new_document

    doc = new_document()
    heading = add_heading(doc, "Hyrje", 1, "1", bookmark=heading_bookmark("1"))
    caption = add_caption(doc, "Tabela", 1, "Një tabelë.", above=True)
    assert heading.text == "1\tHYRJE"
    for para in (heading, caption):
        assert all(run._r.rPr is None for run in para.runs), para.text
    # Word reads w:pPr only as a paragraph's first child; the bookmark follows it.
    assert heading._p[0].tag == qn("w:pPr")

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


def test_a_full_page_never_leaves_the_next_one_blank():
    """A page break written as a paragraph of its own spills onto a new page
    when the page before it is full, and that page stays blank. The builder
    hands the break to the next paragraph instead."""
    from docx.oxml.ns import qn
    from docx_helpers import add_paragraph, fold_page_breaks, new_document, page_break

    doc = new_document()
    add_paragraph(doc, "Faqja e parë.")
    page_break(doc)
    add_paragraph(doc, "Faqja e dytë.")
    page_break(doc)
    doc.add_table(rows=1, cols=1)

    assert fold_page_breaks(doc) == 1
    paras = doc.paragraphs
    assert [p.text for p in paras[:2]] == ["Faqja e parë.", "Faqja e dytë."]
    assert paras[1].paragraph_format.page_break_before is True
    # Before a table there is no paragraph to carry the break, so it stays.
    assert len(list(doc.element.body.iter(qn("w:br")))) == 1


def test_numbers_with_digit_groups_never_break_across_lines():
    """The abstract once ended a line inside "284 807"; the front matter and
    the chapters share one rule that ties the groups with a no-break space."""
    from docx_helpers import keep_numbers_whole

    text = "ULB-së (284 807 transaksione, 492 mashtrime), 20 000 rreshta, nga 2.1 në 1.15"
    assert keep_numbers_whole(text) == (
        "ULB-së (284\u00a0807 transaksione, 492 mashtrime), 20\u00a0000 rreshta, nga 2.1 në 1.15"
    )

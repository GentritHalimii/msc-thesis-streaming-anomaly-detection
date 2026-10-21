"""Word primitives that implement the UBT thesis formatting rules.

The rules themselves come from the faculty's instruction document: Times New
Roman 12 pt throughout, justified body text, at least 1.5 line spacing,
chapter titles in 14 pt bold capitals aligned left, subsection titles in 12 pt
bold, page numbers bottom-right, numbered captions below figures and above
tables, and numbered equations. Front matter is numbered in Roman numerals and
the body restarts at Arabic 1.

Several of these need raw OOXML because python-docx has no API for them:
page-number fields, per-section numbering formats, and the table-of-contents
field that Word populates when the file is opened.
"""

import functools
import numbers
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_BREAK,
    WD_TAB_ALIGNMENT,
    WD_TAB_LEADER,
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(12)
CAPTION_SIZE = Pt(11)
TITLE_SIZE = Pt(14)
LINE_SPACING = 1.5
# A4 (21 cm) minus the 3 cm margins the template annotates on all four sides.
TEXT_WIDTH_CM = 15.0
INK = RGBColor(0, 0, 0)
MUTED = RGBColor(0x40, 0x40, 0x40)

# A resolved citation travels through the content layer as text, so it is
# wrapped in private-use code points that cannot occur in the thesis itself.
# The run writers below turn each wrapped span into a Word cross-reference.
CITE_OPEN = "\ue000"
CITE_CLOSE = "\ue001"
CITE_RUN_RE = re.compile(f"{CITE_OPEN}([a-zA-Z0-9_]+)\\|([0-9]+){CITE_CLOSE}")
REFERENCE_NUM_ID = 100
# A hyphen that attaches an Albanian ending to a foreign word or an acronym
# ("AP-së", "Autoencoder-it") or closes a short compound ("8-fold",
# "end-to-end") must not end a line, so it is written as Word's non-breaking
# hyphen. Longer compounds such as "rolling-origin" may still break.
NOBREAK_HYPHEN_RE = re.compile(r"(?<=\w)-(?=[a-zëç]{1,4}\b)")
# Table cells are measured to size their columns. Word's default cell margin
# is 0.19 cm a side; the rest of the padding absorbs rounding in the layout.
CELL_PADDING_CM = 0.42
# A table whose content is narrow is centred at its natural width, but never
# narrower than this share of the text block, so it does not look lost under
# a long caption.
MIN_TABLE_SHARE = 0.35
# A table up to this many rows is kept on one page; a longer one may break,
# and its header row then repeats on the next page.
KEEP_TOGETHER_ROWS = 25
# A cell that holds a number, a ratio such as "7/8", or the missing-value mark.
NUMBER_RE = re.compile(
    r"^[<>≤≥]? ?[−+-]?\d[\d\u00a0 ]*(\.\d+)?(e[−+-]?\d+)?%?$|^\d+ ?/ ?\d+$|^n/a$"
)


# --------------------------------------------------------------------------
# document scaffolding
# --------------------------------------------------------------------------
def new_document() -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = BODY_FONT
    style.font.size = BODY_SIZE
    style.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    pf = style.paragraph_format
    pf.line_spacing = LINE_SPACING
    pf.space_after = Pt(6)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for section in doc.sections:
        _apply_page_setup(section)
    _set_update_fields_on_open(doc)
    return doc


def _apply_page_setup(section) -> None:
    """A4 with the 3 cm margins the template annotates on all four sides.

    python-docx defaults to US Letter, which is 6 mm wider and 18 mm shorter
    than the paper this document is printed on, so the size is set explicitly.
    """
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(3.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(3.0)


def _set_update_fields_on_open(doc: Document) -> None:
    """Ask Word to refresh every field (TOC, page counts) when the file opens,
    so the generated table of contents is never stale."""
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        el = OxmlElement("w:updateFields")
        el.set(qn("w:val"), "true")
        settings.append(el)


def _field(paragraph, instruction: str, placeholder: str = "") -> None:
    """Insert a Word field code (PAGE, TOC, ...) into a paragraph."""
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr, separate, text, end):
        run._r.append(el)


def define_reference_numbering(doc: Document) -> int:
    """A list definition that prints "[1]", "[2]", ... for the reference list.

    The reference numbers have to be Word's own, not text: only then does a
    cross-reference to an entry return the number Word currently shows, and
    only then do the numbers close up when an entry is added or removed.
    The definition is private to the reference list, so its counter cannot be
    disturbed by any other list in the document.
    """
    numbering = doc.part.numbering_part.element
    abstract_id = str(REFERENCE_NUM_ID)

    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), abstract_id)
    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "singleLevel")
    abstract.append(multi)

    lvl = OxmlElement("w:lvl")
    lvl.set(qn("w:ilvl"), "0")
    for tag, value in (
        ("w:start", "1"),
        ("w:numFmt", "decimal"),
        ("w:lvlText", "[%1]"),
        ("w:lvlJc", "left"),
    ):
        el = OxmlElement(tag)
        el.set(qn("w:val"), value)
        lvl.append(el)
    ppr = OxmlElement("w:pPr")
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "680")  # 1.2 cm, hanging by the same amount
    ind.set(qn("w:hanging"), "680")
    ppr.append(ind)
    lvl.append(ppr)
    abstract.append(lvl)

    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(REFERENCE_NUM_ID))
    ref = OxmlElement("w:abstractNumId")
    ref.set(qn("w:val"), abstract_id)
    num.append(ref)

    # w:abstractNum elements must precede every w:num in the part.
    last_abstract = numbering.findall(qn("w:abstractNum"))[-1]
    last_abstract.addnext(abstract)
    numbering.append(num)
    return REFERENCE_NUM_ID


def apply_list_numbering(para, num_id: int, level: int = 0) -> None:
    """Attach a paragraph to a numbering definition."""
    ppr = para._p.get_or_add_pPr()
    npr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), str(level))
    nid = OxmlElement("w:numId")
    nid.set(qn("w:val"), str(num_id))
    npr.append(ilvl)
    npr.append(nid)
    ppr.append(npr)


def bookmark_paragraph(para, name: str, bookmark_id: int) -> None:
    """Wrap a whole paragraph in a bookmark, the way Word marks a numbered
    item so that a cross-reference can report its number."""
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    para._p.insert(0, start)
    para._p.append(end)


def reference_bookmark(key: str) -> str:
    return f"Ref_{key}"


def _add_citation_field(para, key: str, number: int):
    """One in-text citation, as a cross-reference to the reference entry.

    The instruction asks for the bookmarked paragraph's number in relative
    context, which for this list definition is the bracketed form the reader
    sees. The cached result carries the number computed at build time, so the
    document reads correctly before Word has refreshed anything.
    """
    _field(para, f" REF {reference_bookmark(key)} \\r \\h ", f"[{number}]")
    run = para.runs[-1]
    run.font.name = BODY_FONT
    return run


def _add_text_runs(para, text: str, *, size=None, italic: bool = False, color=None):
    """Text plus any citations it carries, as a sequence of runs."""
    position = 0
    for match in CITE_RUN_RE.finditer(text):
        if match.start() > position:
            _plain_run(para, text[position : match.start()], size, italic, color)
        _add_citation_field(para, match.group(1), int(match.group(2)))
        position = match.end()
    if position < len(text) or position == 0:
        _plain_run(para, text[position:], size, italic, color)


def _keep_hyphens(run) -> None:
    """Write the hyphens NOBREAK_HYPHEN_RE selects as non-breaking ones.

    URLs are left alone: a reader copying one from the PDF must get the plain
    hyphen back.
    """
    for text in run._r.findall(qn("w:t")):
        parts = NOBREAK_HYPHEN_RE.split(text.text or "")
        if len(parts) == 1 or "://" in text.text:
            continue
        text.text = parts[0]
        text.set(qn("xml:space"), "preserve")
        previous = text
        for part in parts[1:]:
            hyphen = OxmlElement("w:noBreakHyphen")
            following = OxmlElement("w:t")
            following.set(qn("xml:space"), "preserve")
            following.text = part
            previous.addnext(hyphen)
            hyphen.addnext(following)
            previous = following


def _plain_run(para, text: str, size, italic: bool, color):
    run = para.add_run(text)
    _keep_hyphens(run)
    run.font.name = BODY_FONT
    if size is not None:
        run.font.size = size
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    return run


def set_page_numbering(section, fmt: str = "decimal", start: int | None = None) -> None:
    """Per-section page-number format; `fmt` is 'decimal' or 'upperRoman'."""
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))
    section._sectPr.append(pg)


def add_page_number_footer(section) -> None:
    """Page number bottom-right, as the instructions require."""
    footer = section.footer
    footer.is_linked_to_previous = False
    para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    para.text = ""
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    para.paragraph_format.line_spacing = 1.0
    _field(para, "PAGE", "1")
    for run in para.runs:
        run.font.name = BODY_FONT
        run.font.size = BODY_SIZE


def start_new_section(doc: Document, fmt: str, start: int | None = None):
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    _apply_page_setup(section)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    set_page_numbering(section, fmt, start)
    add_page_number_footer(section)
    return section


# --------------------------------------------------------------------------
# text blocks
# --------------------------------------------------------------------------
def add_paragraph(
    doc: Document,
    text: str,
    *,
    italic: bool = False,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    size=BODY_SIZE,
    space_after: int = 6,
    first_line_indent: float | None = None,
):
    para = doc.add_paragraph()
    para.alignment = align
    pf = para.paragraph_format
    pf.line_spacing = LINE_SPACING
    pf.space_after = Pt(space_after)
    if first_line_indent:
        pf.first_line_indent = Cm(first_line_indent)
    _add_text_runs(para, text, size=size, italic=italic)
    return para


def add_heading(doc: Document, text: str, level: int, number: str | None = None):
    """Chapter titles: 14 pt bold capitals. Subsections: 12 pt bold."""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = para.paragraph_format
    pf.line_spacing = LINE_SPACING
    pf.space_before = Pt(18 if level == 1 else 12)
    pf.space_after = Pt(8)
    pf.keep_with_next = True
    label = (
        f"{number}\t{text.upper() if level == 1 else text}"
        if number
        else (text.upper() if level == 1 else text)
    )
    if CITE_OPEN in label:  # pragma: no cover - guarded by tests/test_thesis_style
        raise ValueError("a heading cannot carry a citation: it has no run to hold a field")
    run = para.add_run(label)
    _keep_hyphens(run)
    run.font.name = BODY_FONT
    run.bold = True
    run.font.size = TITLE_SIZE if level == 1 else BODY_SIZE
    run.font.color.rgb = INK
    # Outline level makes the entry visible to the table-of-contents field.
    ppr = para._p.get_or_add_pPr()
    outline = OxmlElement("w:outlineLvl")
    outline.set(qn("w:val"), str(level - 1))
    ppr.append(outline)
    style_id = f"Heading{min(level, 4)}"
    pstyle = OxmlElement("w:pStyle")
    pstyle.set(qn("w:val"), style_id)
    ppr.insert(0, pstyle)
    for r in para.runs:
        r.font.name = BODY_FONT
        r.font.size = TITLE_SIZE if level == 1 else BODY_SIZE
        r.bold = True
        r.font.color.rgb = INK
    return para


def add_bullets(doc: Document, items: list[str], numbered: bool = False):
    """Bulleted or numbered list.

    Numbers are written literally rather than through Word's List Number
    style. That style keeps a single counter for the whole document, so the
    second list in a chapter carries on from where the first stopped — the
    fifth list started at sixteen in an early draft. Literal numbering with a
    hanging indent gives the same appearance and always starts at one.
    """
    for index, item in enumerate(items, start=1):
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = para.paragraph_format
        pf.line_spacing = LINE_SPACING
        pf.space_after = Pt(4)
        pf.left_indent = Cm(1.6)
        pf.first_line_indent = Cm(-0.8)
        marker = f"{index}." if numbered else "•"
        _add_text_runs(para, f"{marker}\t{item}", size=BODY_SIZE)
        pf.tab_stops.add_tab_stop(Cm(1.6))


def add_caption(doc: Document, text: str, *, above: bool = False):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = para.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(2 if not above else 8)
    pf.space_after = Pt(10 if not above else 4)
    pf.keep_with_next = above
    _add_text_runs(para, text, size=CAPTION_SIZE, color=MUTED)
    return para


def add_figure(doc: Document, image_path: Path, caption: str, width_cm: float = 14.5):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(10)
    para.paragraph_format.space_after = Pt(2)
    # A picture that fills the rest of a page would otherwise leave its
    # caption alone at the top of the next one.
    para.paragraph_format.keep_with_next = True
    para.add_run().add_picture(str(image_path), width=Cm(width_cm))
    add_caption(doc, caption)


def add_equation(doc: Document, expression: str, number: int):
    """Centred equation with a right-aligned number, per the template.

    The tab stops must be a genuine CENTER stop and a genuine RIGHT stop. With
    the default left-aligned stops the expression starts at the centre of the
    line and overruns the margin, and the number is pushed onto a line of its
    own — which is what a first draft of this document did.
    """
    para = doc.add_paragraph()
    pf = para.paragraph_format
    pf.line_spacing = LINE_SPACING
    pf.space_before = Pt(10)
    pf.space_after = Pt(10)
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf.tab_stops.add_tab_stop(Cm(TEXT_WIDTH_CM / 2), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(Cm(TEXT_WIDTH_CM), WD_TAB_ALIGNMENT.RIGHT)
    _add_math_runs(para, f"\t{expression}\t({number})")
    return para


# The unbraced form takes the whole word, not one character: "c_het" is a
# cost with the subscript "het", and matching a single letter turned it
# into "c" subscript-h followed by a stray "et".
_MATH_MARKUP = re.compile(r"([_^])(?:\{([^{}]*)\}|(\w+))")


def _add_math_runs(para, text: str):
    """Writes the expression with real subscript and superscript runs.

    The sources write mathematics as plain text with TeX-style markers, so
    "R_{n-1}" reached the page as those literal characters. Word has real
    sub- and superscript formatting; using it costs one pass over the string
    and is the difference between a typeset equation and a code listing.
    """
    position = 0
    for match in _MATH_MARKUP.finditer(text):
        if match.start() > position:
            _styled_run(para, text[position : match.start()])
        _styled_run(
            para,
            match.group(2) if match.group(2) is not None else match.group(3),
            sub=match.group(1) == "_",
            sup=match.group(1) == "^",
        )
        position = match.end()
    if position < len(text) or position == 0:
        _styled_run(para, text[position:])


def _styled_run(para, text: str, sub: bool = False, sup: bool = False):
    run = para.add_run(text)
    run.font.name = BODY_FONT
    run.font.size = BODY_SIZE
    run.italic = True
    run.font.subscript = sub
    run.font.superscript = sup
    return run


def add_table(
    doc: Document,
    dataframe,
    caption: str,
    *,
    number: int,
    font_size: float = 9.5,
    col_widths: list[float] | None = None,
    max_rows: int | None = None,
):
    """Table with its numbered title above it, as the template illustrates.

    Numeric columns are right-aligned so their decimal points line up. Column
    widths come from the cell text unless `col_widths` gives proportions; in
    both cases no column is narrower than its longest unbreakable piece, so a
    number never wraps inside its cell and a word is never split.
    """
    add_caption(doc, f"Tabela {number}. {caption}", above=True)
    df = dataframe if max_rows is None else dataframe.head(max_rows)
    df = df.map(_display_text)
    numeric = [all(_is_number(value) for value in df[name]) for name in df.columns]
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # The header row repeats on every page a long table runs onto, and no row
    # is split across a page break.
    _row_properties(table.rows[0], header=True)
    for cell, name in zip(table.rows[0].cells, df.columns, strict=True):
        cell.text = ""
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.line_spacing = 1.0
        para.paragraph_format.space_after = Pt(2)
        run = para.add_run(str(name))
        _keep_hyphens(run)
        run.bold = True
        run.font.name = BODY_FONT
        run.font.size = Pt(font_size)

    for _, row in df.iterrows():
        table_row = table.add_row()
        _row_properties(table_row, header=False)
        for cell, value, is_number in zip(table_row.cells, row, numeric, strict=True):
            cell.text = ""
            para = cell.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT if is_number else WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.space_after = Pt(1)
            run = para.add_run(value)
            _keep_hyphens(run)
            run.font.name = BODY_FONT
            run.font.size = Pt(font_size)

    if len(df) <= KEEP_TOGETHER_ROWS:
        for table_row in table.rows[:-1]:
            for cell in table_row.cells:
                cell.paragraphs[0].paragraph_format.keep_with_next = True
    widths = column_widths(df, font_size, numeric, col_widths)
    if sum(widths) > TEXT_WIDTH_CM + 1e-6:
        print(f"kujdes: tabela {number} nuk nxë në faqe pa thyer numra ose fjalë")
    _apply_column_widths(table, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table


def _display_text(value) -> str:
    text = str(value)
    if _is_number(text) and text.startswith("-"):
        return "\u2212" + text[1:]  # a minus sign, not a hyphen
    return text


def _row_properties(row, header: bool) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))
    if header:
        tr_pr.append(OxmlElement("w:tblHeader"))


def _is_number(value) -> bool:
    if isinstance(value, numbers.Number) and not isinstance(value, bool):
        return True
    return bool(NUMBER_RE.match(str(value).strip()))


@functools.cache
def _measuring_font(bold: bool):
    """The body font at 1000 units, or None when no metric twin is installed."""
    from matplotlib import font_manager
    from PIL import ImageFont

    weight = "bold" if bold else "normal"
    for family in (BODY_FONT, "Liberation Serif"):
        prop = font_manager.FontProperties(family=family, weight=weight)
        try:
            path = font_manager.findfont(prop, fallback_to_default=False)
        except ValueError:
            continue
        return ImageFont.truetype(path, 1000)
    return None


def _text_cm(text: str, size_pt: float, bold: bool = False) -> float:
    """Printed width of `text` in centimetres."""
    font = _measuring_font(bold)
    em = font.getlength(text) / 1000 if font else 0.5 * len(text)
    return em * size_pt / 72 * 2.54


def column_widths(df, font_size: float, numeric: list[bool], preferred=None) -> list[float]:
    """Column widths in centimetres.

    Each column has three widths: a floor, its longest piece that cannot
    wrap (the whole value in a numeric column, the longest word elsewhere,
    header words included); the width at which no body cell wraps; and the
    width at which the header does not wrap either. The table gets the
    widest level that fits the text block, and the space above that level is
    shared in proportion to what each column still needs, as browsers lay out
    tables: headers wrap before body cells, and a short text column is not
    squeezed to a word per line next to a long one. A table with little
    content keeps its natural width instead of being stretched. With
    `preferred`, the width is shared in those proportions instead, never
    below the floors.
    """
    floors, body, full = [], [], []
    for name, is_number in zip(df.columns, numeric, strict=True):
        cells = [str(value) for value in df[name]]
        title = str(name)
        title_words = [_text_cm(word, font_size, bold=True) for word in title.split()]
        if is_number:
            pieces = [_text_cm(cell, font_size) for cell in cells]
        else:
            pieces = [_text_cm(word, font_size) for cell in cells for word in cell.split()]
        floor = max([0.0, *title_words, *pieces]) + CELL_PADDING_CM
        widest = max([0.0, *(_text_cm(cell, font_size) for cell in cells)]) + CELL_PADDING_CM
        floors.append(floor)
        body.append(max(floor, widest))
        full.append(max(floor, widest, _text_cm(title, font_size, bold=True) + CELL_PADDING_CM))

    if preferred:
        return _share(floors, list(preferred), TEXT_WIDTH_CM)
    if sum(full) <= TEXT_WIDTH_CM:
        total = min(TEXT_WIDTH_CM, max(1.15 * sum(full), MIN_TABLE_SHARE * TEXT_WIDTH_CM))
        extra = (total - sum(full)) / len(full)
        return [width + extra for width in full]
    lower, upper = (body, full) if sum(body) <= TEXT_WIDTH_CM else (floors, body)
    spare = TEXT_WIDTH_CM - sum(lower)
    if spare <= 0:
        return floors
    need = [high - low for low, high in zip(lower, upper, strict=True)]
    return [low + spare * n / sum(need) for low, n in zip(lower, need, strict=True)]


def _share(floors: list[float], weights: list[float], total: float) -> list[float]:
    """Share `total` in proportion to `weights`, holding columns at their floors."""
    fixed = [False] * len(floors)
    while True:
        free = [i for i, done in enumerate(fixed) if not done]
        if not free:
            return floors
        room = total - sum(floors[i] for i, done in enumerate(fixed) if done)
        scale = room / sum(weights[i] for i in free)
        short = [i for i in free if weights[i] * scale < floors[i]]
        if not short:
            return [floors[i] if fixed[i] else weights[i] * scale for i in range(len(floors))]
        for i in short:
            fixed[i] = True


def add_toc_field(doc: Document, instruction: str, placeholder: str):
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = LINE_SPACING
    _field(para, instruction, placeholder)
    for run in para.runs:
        run.font.name = BODY_FONT
        run.font.size = BODY_SIZE


LOGO_PATH = Path(__file__).parent / "assets" / "ubt-logo.png"


def add_logo(doc: Document, width_cm: float = 11.0):
    """The university logo, centred, as the template's two front pages show.

    The template annotates it "do not change the logo", so the file is the one
    embedded in the faculty's own instructions rather than a redrawn copy.
    """
    if not LOGO_PATH.exists():  # pragma: no cover - the asset ships with the repo
        return None
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after = Pt(14)
    para.add_run().add_picture(str(LOGO_PATH), width=Cm(width_cm))
    return para


def page_break(doc: Document):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_toc_entry(doc, text: str, level: int, page: str | None, bold: bool | None = None):
    """One line of a statically generated table of contents.

    Chapter entries are bold; `bold` overrides that for the lists of figures
    and tables, whose entries are all at the first level.

    A Word TOC field is the usual solution, but it renders as a placeholder
    until someone opens the file and refreshes it — and a thesis that is
    printed or converted without that refresh has an empty contents page.
    These entries are written out with real page numbers instead, recovered
    from a first rendering pass, and a right-aligned tab stop with dot leaders
    reproduces the usual appearance.

    Three details matter. The paragraph must be left-aligned, because justified
    text stretches the leader dots across the whole line. The tab stop is
    measured from the margin, not from the entry's indent, so it sits at the
    same place for every level and the page numbers line up. And the text keeps
    clear of the page-number column through a right indent, with the tab stop
    beyond it, so a title that fills its line wraps early instead of leaving
    the leader dots alone on the next line.
    """
    indent_cm = 0.7 * (level - 1)
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = para.paragraph_format
    pf.line_spacing = 1.15
    pf.space_after = Pt(3)
    pf.left_indent = Cm(indent_cm)
    pf.right_indent = Cm(1.0)
    pf.tab_stops.add_tab_stop(Cm(TEXT_WIDTH_CM), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    # Any tab inside the caption itself would jump to the leader stop, so the
    # separator between a section number and its title is written as spaces.
    label = text.replace("\t", "   ")
    run = para.add_run(label if page is None else f"{label}\t{page}")
    _keep_hyphens(run)
    run.font.name = BODY_FONT
    run.font.size = BODY_SIZE
    run.bold = level == 1 if bold is None else bold
    return para


def _apply_column_widths(table, col_widths: list[float]) -> None:
    """Force fixed column widths.

    Three things have to agree or the width is quietly ignored: the layout
    algorithm must be "fixed", the table grid must declare each column, and
    every cell in a column must carry the same width. Setting only cell widths
    — the obvious approach — leaves the renderer free to re-balance the
    columns, which is what squeezed a long detector name into a two-character
    column in an earlier draft. A grid wider than the printable width is
    scaled down so it cannot trigger re-balancing either, and the table width
    is stated so a narrow table keeps its size.
    """
    scale = min(1.0, TEXT_WIDTH_CM / sum(col_widths))
    scaled = [Cm(w * scale) for w in col_widths]

    table.autofit = False  # writes <w:tblLayout w:type="fixed"/> in schema order
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), str(sum(int(width.twips) for width in scaled)))

    grid = table._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        table._tbl.remove(grid)
    grid = OxmlElement("w:tblGrid")
    for width in scaled:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(int(width.twips)))
        grid.append(col)
    table._tbl.insert(list(table._tbl).index(tbl_pr) + 1, grid)

    for row in table.rows:
        for cell, width in zip(row.cells, scaled, strict=False):
            cell.width = width

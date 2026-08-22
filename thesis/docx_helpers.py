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

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(12)
CAPTION_SIZE = Pt(11)
TITLE_SIZE = Pt(14)
LINE_SPACING = 1.5
INK = RGBColor(0, 0, 0)
MUTED = RGBColor(0x40, 0x40, 0x40)


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
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3.0)   # binding edge
        section.right_margin = Cm(2.5)
    _set_update_fields_on_open(doc)
    return doc


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
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    set_page_numbering(section, fmt, start)
    add_page_number_footer(section)
    return section


# --------------------------------------------------------------------------
# text blocks
# --------------------------------------------------------------------------
def add_paragraph(doc: Document, text: str, *, italic: bool = False,
                  align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=BODY_SIZE,
                  space_after: int = 6, first_line_indent: float | None = None):
    para = doc.add_paragraph()
    para.alignment = align
    pf = para.paragraph_format
    pf.line_spacing = LINE_SPACING
    pf.space_after = Pt(space_after)
    if first_line_indent:
        pf.first_line_indent = Cm(first_line_indent)
    run = para.add_run(text)
    run.font.name = BODY_FONT
    run.font.size = size
    run.italic = italic
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
    label = f"{number}\t{text.upper() if level == 1 else text}" if number else (
        text.upper() if level == 1 else text
    )
    run = para.add_run(label)
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
    for item in items:
        para = doc.add_paragraph(style="List Number" if numbered else "List Bullet")
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = para.paragraph_format
        pf.line_spacing = LINE_SPACING
        pf.space_after = Pt(3)
        pf.left_indent = Cm(1.0)
        run = para.add_run(item)
        run.font.name = BODY_FONT
        run.font.size = BODY_SIZE


def add_caption(doc: Document, text: str, *, above: bool = False):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = para.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(2 if not above else 8)
    pf.space_after = Pt(10 if not above else 4)
    pf.keep_with_next = above
    run = para.add_run(text)
    run.font.name = BODY_FONT
    run.font.size = CAPTION_SIZE
    run.font.color.rgb = MUTED
    return para


def add_figure(doc: Document, image_path: Path, caption: str, width_cm: float = 14.5):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(10)
    para.paragraph_format.space_after = Pt(2)
    para.add_run().add_picture(str(image_path), width=Cm(width_cm))
    add_caption(doc, caption)


def add_equation(doc: Document, expression: str, number: int):
    """Equations are centred with a right-aligned number, per the template."""
    para = doc.add_paragraph()
    pf = para.paragraph_format
    pf.line_spacing = LINE_SPACING
    pf.space_before = Pt(8)
    pf.space_after = Pt(8)
    # tab stops: centre for the formula, right edge for the number
    tabs = pf.tab_stops
    tabs.add_tab_stop(Cm(7.5))
    tabs.add_tab_stop(Cm(15.5))
    run = para.add_run(f"\t{expression}\t({number})")
    run.font.name = BODY_FONT
    run.font.size = BODY_SIZE
    run.italic = True
    return para


def add_table(doc: Document, dataframe, caption: str, *, number: int,
              font_size: float = 9.5, col_widths: list[float] | None = None,
              max_rows: int | None = None):
    """Table with its numbered title above it, as the template illustrates."""
    add_caption(doc, f"Tabela {number}. {caption}", above=True)
    df = dataframe if max_rows is None else dataframe.head(max_rows)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for cell, name in zip(table.rows[0].cells, df.columns, strict=True):
        cell.text = ""
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.line_spacing = 1.0
        para.paragraph_format.space_after = Pt(2)
        run = para.add_run(str(name))
        run.bold = True
        run.font.name = BODY_FONT
        run.font.size = Pt(font_size)

    for _, row in df.iterrows():
        cells = table.add_row().cells
        for cell, value in zip(cells, row, strict=True):
            cell.text = ""
            para = cell.paragraphs[0]
            para.alignment = (WD_ALIGN_PARAGRAPH.LEFT if isinstance(value, str)
                              else WD_ALIGN_PARAGRAPH.RIGHT)
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.space_after = Pt(1)
            run = para.add_run(str(value))
            run.font.name = BODY_FONT
            run.font.size = Pt(font_size)

    if col_widths:
        for row in table.rows:
            for cell, w in zip(row.cells, col_widths, strict=False):
                cell.width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table


def add_toc_field(doc: Document, instruction: str, placeholder: str):
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = LINE_SPACING
    _field(para, instruction, placeholder)
    for run in para.runs:
        run.font.name = BODY_FONT
        run.font.size = BODY_SIZE


def page_break(doc: Document):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

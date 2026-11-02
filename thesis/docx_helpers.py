"""Word primitives that implement the UBT thesis formatting rules.

The rules themselves come from the faculty's instruction document: Times New
Roman 12 pt throughout, justified body text, at least 1.5 line spacing,
chapter titles in 14 pt bold capitals aligned left, subsection titles in 12 pt
bold, page numbers bottom-right, numbered captions below figures and above
tables, and numbered equations. Front matter is numbered in Roman numerals and
the body restarts at Arabic 1.

The contents, the list of figures and the list of tables are Word's own
tables, built from the Heading styles and from the captions' numbers, so Word
can update them and a Ctrl+click on an entry goes to its page. Citations and
the reference list are Word's own as well: the sources sit in the document's
source list, and Word's References tab manages them.

Several of these need raw OOXML because python-docx has no API for them:
page-number fields, per-section numbering formats, bookmarks, the tables of
contents, Word's citation and bibliography fields with the content controls
around them, and the cross-references behind figure numbers.
"""

import functools
import io
import itertools
import numbers
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_BREAK,
    WD_TAB_ALIGNMENT,
    WD_TAB_LEADER,
)
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips
from PIL import Image

BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(12)
CAPTION_SIZE = Pt(11)
TITLE_SIZE = Pt(14)
LINE_SPACING = 1.5
# A4 (21 cm) minus the 3 cm margins the template annotates on all four sides.
TEXT_WIDTH_CM = 15.0
INK = RGBColor(0, 0, 0)
MUTED = RGBColor(0x40, 0x40, 0x40)

# A resolved citation or figure number travels through the content layer as
# text, so it is wrapped in private-use code points that cannot occur in the
# thesis itself. The run writers below turn each wrapped span into a Word
# field: a citation, which names the source's tag, or a cross-reference.
CITE_OPEN = "\ue000"
CITE_CLOSE = "\ue001"
FIGURE_OPEN = "\ue002"
FIGURE_CLOSE = "\ue003"
FIELD_RUN_RE = re.compile(
    f"{CITE_OPEN}([a-zA-Z0-9_]+)\\|([0-9]+){CITE_CLOSE}|{FIGURE_OPEN}([0-9]+){FIGURE_CLOSE}"
)
# The language Word formats citations and the reference list in. IEEE's
# terms (vol., no., pp., Available) are English, so the list is English
# (United States), as Word's own IEEE style writes it.
CITATION_LANGUAGE = 1033
# The reference list's two columns, the number and the entry, which together
# fill the text width.
REFERENCE_NUMBER_CM = 1.2
# The caption labels. Word's SEQ fields count each one separately, and the
# lists of figures and tables are built from them.
FIGURE_LABEL = "Figura"
TABLE_LABEL = "Tabela"
# The automatic tables, with the switches the faculty template uses for its
# contents: heading levels 1 to 3, entries as links, no page numbers in web
# view, and paragraphs with an outline level. The two lists collect captions.
CONTENTS_FIELD = ' TOC \\o "1-3" \\h \\z \\u '
FIGURE_LIST_FIELD = f' TOC \\h \\z \\c "{FIGURE_LABEL}" '
TABLE_LIST_FIELD = f' TOC \\h \\z \\c "{TABLE_LABEL}" '
# Where a contents entry's number and its title start, in twips, as in the
# template's own contents: a level-2 number at 240 with its title at 880, a
# level-3 number at 480 with its title at 1320. A title that runs onto a
# second line continues under its first word.
CONTENTS_TABS = {1: (0, 480), 2: (240, 880), 3: (480, 1320)}
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
    _define_heading_and_caption_styles(doc)
    _define_contents_styles(doc)
    _define_bibliography_style(doc)

    for section in doc.sections:
        _apply_page_setup(section)
    _set_update_fields_on_open(doc)
    return doc


def _set_style_font(style, size, *, bold: bool, color: RGBColor) -> None:
    """Times New Roman at `size`, in place of the theme font and colour that
    python-docx's template gives its headings and captions."""
    fonts = style.element.get_or_add_rPr().get_or_add_rFonts()
    for theme in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(theme), None)
    for slot in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(slot), BODY_FONT)
    style.font.size = size
    style.font.bold = bold
    style.font.italic = False
    style.font.color.rgb = color


def _define_heading_and_caption_styles(doc: Document) -> None:
    """The template's titles and captions as Word styles.

    The look belongs to the style, not to the text, for two reasons. Word's
    automatic contents and lists copy formatting set on a heading's or a
    caption's text into the entry, so a 14 pt title would come back as a
    14 pt line of the contents. And a heading or caption added later in Word
    gets the template's look from the style alone.
    """
    for level in (1, 2, 3):
        style = doc.styles[f"Heading {level}"]
        _set_style_font(style, TITLE_SIZE if level == 1 else BODY_SIZE, bold=True, color=INK)
        style.font.all_caps = level == 1 or None
        pf = style.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.line_spacing = LINE_SPACING
        pf.space_before = Pt(18 if level == 1 else 12)
        pf.space_after = Pt(8)
        pf.keep_with_next = True

    caption = doc.styles["Caption"]
    _set_style_font(caption, CAPTION_SIZE, bold=False, color=MUTED)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.line_spacing = 1.0


def _define_contents_styles(doc: Document) -> None:
    """Word's TOC 1 to 3 and Table of Figures styles, which Word applies to
    every entry it writes when it updates the contents or the lists.

    The paragraph is left-aligned, because justified text stretches the
    leader dots across the whole line. The page-number tab stop is measured
    from the margin, so the numbers line up at every level. And the text keeps
    clear of the page-number column through a right indent, with the tab stop
    beyond it, so a title that fills its line wraps early instead of leaving
    the leader dots alone on the next line.
    """
    entries = [(f"toc {level}", f"TOC{level}", level) for level in CONTENTS_TABS]
    for name, style_id, level in [*entries, ("table of figures", "TableofFigures", None)]:
        # Built-in, not custom: marked custom, a style named "toc 1" is not
        # the TOC 1 that Word applies, and Word would format with its own.
        style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH, builtin=True)
        style.style_id = style_id
        style.base_style = doc.styles["Normal"]
        style.next_paragraph_style = doc.styles["Normal"]
        style.priority = 39 if level else 99
        style.unhide_when_used = True
        pf = style.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.line_spacing = 1.15
        pf.space_after = Pt(3)
        pf.right_indent = Cm(1.0)
        if level:
            # The number starts the line, and the title and its wrapped lines
            # start at the tab stop after it.
            number, title = CONTENTS_TABS[level]
            pf.left_indent = Twips(title)
            pf.first_line_indent = Twips(number - title)
            pf.tab_stops.add_tab_stop(Twips(title))
        pf.tab_stops.add_tab_stop(Cm(TEXT_WIDTH_CM), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        if level == 1:
            # Chapter entries are bold capitals, like the chapter titles.
            style.font.bold = True
            style.font.all_caps = True


def _define_bibliography_style(doc: Document) -> None:
    """Word's Bibliography style, which Word gives every paragraph of the
    reference list it writes. It adds nothing to Normal, so the list keeps
    the body's Times New Roman 12, justified, with 1.5 line spacing."""
    style = doc.styles.add_style("Bibliography", WD_STYLE_TYPE.PARAGRAPH, builtin=True)
    style.base_style = doc.styles["Normal"]
    style.next_paragraph_style = doc.styles["Normal"]
    style.priority = 37
    style.unhide_when_used = True


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


# Children of w:settings that the schema places after w:updateFields.
_AFTER_UPDATE_FIELDS = (
    "w:hdrShapeDefaults",
    "w:footnotePr",
    "w:endnotePr",
    "w:compat",
    "w:docVars",
    "w:rsids",
    "m:mathPr",
    "w:attachedSchema",
    "w:themeFontLang",
    "w:clrSchemeMapping",
    "w:doNotIncludeSubdocsInStats",
    "w:doNotAutoCompressPictures",
    "w:forceUpgrade",
    "w:captions",
    "w:readModeInkLockDown",
    "w:smartTagType",
    "sl:schemaLibrary",
    "w:shapeDefaults",
    "w:doNotEmbedSmartTags",
    "w:decimalSymbol",
    "w:listSeparator",
)


def _set_update_fields_on_open(doc: Document) -> None:
    """Ask Word to refresh every field (contents, lists, cross-references)
    when the file opens, so they match Word's own pagination.

    The setting goes ahead of w:compat, where the schema puts it, rather than
    at the end of the settings, where an earlier build appended it.
    """
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is not None:
        return
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    successor = next(
        (s for tag in _AFTER_UPDATE_FIELDS if (s := settings.find(qn(tag))) is not None), None
    )
    if successor is not None:
        successor.addprevious(el)
    else:
        settings.append(el)


def _fld_char(kind: str):
    char = OxmlElement("w:fldChar")
    char.set(qn("w:fldCharType"), kind)
    return char


def _field_start(paragraph, instruction: str):
    """The opening of a field, in one run: the field character, the
    instruction and the separator. The result follows, in this paragraph or
    over later ones, and `_field_end` closes it."""
    run = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    for el in (_fld_char("begin"), instr, _fld_char("separate")):
        run._r.append(el)
    return run


def _field_end(paragraph):
    run = paragraph.add_run()
    run._r.append(_fld_char("end"))
    return run


def _field(paragraph, instruction: str, placeholder: str = ""):
    """Insert a Word field code (PAGE, REF, ...) with its cached result."""
    run = _field_start(paragraph, instruction)
    text = OxmlElement("w:t")
    text.text = placeholder
    run._r.append(text)
    run._r.append(_fld_char("end"))
    return run


# Bookmark ids only have to be unique within a document; one counter for the
# whole process guarantees that, however many documents it builds.
_BOOKMARK_IDS = itertools.count(1000)


def bookmark_paragraph(para, name: str, bookmark_id: int | None = None) -> None:
    """Wrap a whole paragraph in a bookmark, the way Word marks a numbered item
    or a heading so that a cross-reference can report its number or its page.

    The start goes after w:pPr, which must remain the paragraph's first child:
    in front of it, as an earlier build placed it, Word may ignore the
    paragraph's properties.
    """
    if bookmark_id is None:
        bookmark_id = next(_BOOKMARK_IDS)
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    p = para._p
    p.insert(1 if p.pPr is not None else 0, start)
    p.append(end)


def _open_bookmark(para, name: str) -> int:
    """Start a bookmark at the current end of the paragraph; what is added
    to the paragraph before `_close_bookmark` falls inside it."""
    bookmark_id = next(_BOOKMARK_IDS)
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    para._p.append(start)
    return bookmark_id


def _close_bookmark(para, bookmark_id: int) -> None:
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    para._p.append(end)


# Targets of the entries in the contents and in the figure and table lists.
# Word bookmark names allow letters, digits and underscores only.
def heading_bookmark(number: str) -> str:
    return "Toc_" + number.replace(".", "_")


def title_bookmark(title: str) -> str:
    """An unnumbered title that the contents lists, such as LISTA E FIGURAVE."""
    return "Toc_" + "_".join(title.split())


# A figure's or table's bookmark covers the label and the number in its
# caption, "Figura 3", and is named the way Word names the bookmarks behind
# its own cross-references: hidden, "_Ref" and digits. The lists jump to it
# and report its page, and a reference in the text repeats it. A bookmark
# around the number alone was lost when Word updated the fields, and every
# reference in the text then read "Error! Reference source not found".
def figure_bookmark(number: int) -> str:
    return f"_Ref{510_000_000 + number}"


def table_bookmark(number: int) -> str:
    return f"_Ref{520_000_000 + number}"


# Content controls carry an id that has to be unique within the document.
_CONTROL_IDS = itertools.count(1_000_001)


def _content_control(kind):
    """A content control of the given kind (w:citation, w:bibliography, a
    w:docPartObj), returned with the element its content goes into."""
    control = OxmlElement("w:sdt")
    properties = OxmlElement("w:sdtPr")
    control_id = OxmlElement("w:id")
    control_id.set(qn("w:val"), str(next(_CONTROL_IDS)))
    properties.append(control_id)
    properties.append(kind)
    content = OxmlElement("w:sdtContent")
    control.append(properties)
    control.append(content)
    return control, content


def _field_runs(instruction: str, result: str) -> list:
    """A field as Word writes one: the field characters, the instruction and
    the cached result, each in a run of its own."""
    runs = []
    for kind, value in (
        ("begin", None),
        ("instr", instruction),
        ("separate", None),
        ("text", result),
        ("end", None),
    ):
        run = OxmlElement("w:r")
        if kind == "instr":
            node = OxmlElement("w:instrText")
            node.set(qn("xml:space"), "preserve")
            node.text = value
        elif kind == "text":
            node = OxmlElement("w:t")
            node.text = value
        else:
            node = _fld_char(kind)
        run.append(node)
        runs.append(run)
    return runs


def _add_citation(para, tag: str, number: int):
    """One in-text citation, as Word's References > Insert Citation writes it:
    a CITATION field naming the source's tag in the document's source list,
    inside a citation content control.

    Word numbers the citations itself, in the order the sources are first
    cited, and updates them with the reference list. The cached result
    carries the number computed at build time, so the document reads
    correctly before Word has refreshed anything.
    """
    control, content = _content_control(OxmlElement("w:citation"))
    for run in _field_runs(f" CITATION {tag} \\l {CITATION_LANGUAGE} ", f"[{number}]"):
        content.append(run)
    para._p.append(control)
    return control


def _add_figure_reference(para, number: int):
    """A reference in the text, "Figura 3", written as Word writes a
    cross-reference to a caption's label and number: a REF field, each part
    in a run of its own, whose result is the text of the caption's bookmark.
    Word renumbers the caption and the reference together, and a Ctrl+click
    on the reference goes to the figure."""
    from docx.text.run import Run

    for run in _field_runs(f" REF {figure_bookmark(number)} \\h ", f"{FIGURE_LABEL} {number}"):
        para._p.append(run)
        Run(run, para).font.name = BODY_FONT


def _add_text_runs(para, text: str, *, size=None, italic: bool = False, color=None):
    """Text plus any citations and figure numbers it carries, as runs."""
    position = 0
    for match in FIELD_RUN_RE.finditer(text):
        if match.start() > position:
            _plain_run(para, text[position : match.start()], size, italic, color)
        if match.group(1):
            _add_citation(para, match.group(1), int(match.group(2)))
        else:
            _add_figure_reference(para, int(match.group(3)))
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


# Children of w:sectPr that the schema places after w:pgNumType.
_AFTER_PG_NUM_TYPE = (
    "w:cols",
    "w:formProt",
    "w:vAlign",
    "w:noEndnote",
    "w:titlePg",
    "w:textDirection",
    "w:bidi",
    "w:rtlGutter",
    "w:docGrid",
    "w:printerSettings",
    "w:sectPrChange",
)


def set_page_numbering(section, fmt: str = "decimal", start: int | None = None) -> None:
    """Per-section page-number format; `fmt` is 'decimal' or 'upperRoman'.

    A new section starts as a copy of the previous one, numbering included, so
    the inherited w:pgNumType is replaced rather than added to. Word expects a
    single one, ahead of w:cols. With three of them after w:docGrid, as an
    earlier build wrote, LibreOffice read the last and numbered the body 1, 2,
    3, while Word is free to take the first and number it I, II, III.
    """
    sect = section._sectPr
    for old in sect.findall(qn("w:pgNumType")):
        sect.remove(old)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))
    successor = next(
        (el for tag in _AFTER_PG_NUM_TYPE if (el := sect.find(qn(tag))) is not None), None
    )
    if successor is not None:
        successor.addprevious(pg)
    else:
        sect.append(pg)


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


def add_heading(
    doc: Document,
    text: str,
    level: int,
    number: str | None = None,
    *,
    bookmark: str | None = None,
):
    """Chapter titles: 14 pt bold capitals. Subsections: 12 pt bold.

    The look comes from Word's Heading 1 to 3 styles, which the contents is
    built from; the text carries no formatting of its own.
    """
    title = text.upper() if level == 1 else text
    label = f"{number}\t{title}" if number else title
    if CITE_OPEN in label or FIGURE_OPEN in label:  # pragma: no cover - guarded by tests
        raise ValueError("a heading cannot carry a cross-reference: the contents copies it")
    para = doc.add_paragraph(style=f"Heading {level}")
    _keep_hyphens(para.add_run(label))
    if bookmark:
        bookmark_paragraph(para, bookmark)
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


def split_caption(text: str) -> tuple[str, str]:
    """A caption's first sentence, which names the figure, and the rest."""
    title, _, note = text.partition(". ")
    return (f"{title}." if note else title), note


def add_caption(
    doc: Document,
    label: str,
    number: int,
    text: str,
    *,
    above: bool = False,
    bookmark: str | None = None,
):
    """A numbered caption, "Figura 3. ...", whose number is Word's own.

    The number is a SEQ field, the counter behind Word's Insert Caption, so
    Word renumbers the captions when a figure is added or moved and builds
    the lists of figures and tables from them. A list entry is the whole
    paragraph that holds the number, so that paragraph keeps only the first
    sentence, the one that names the figure; any reading notes after it
    follow in a paragraph of their own.
    """
    if CITE_OPEN in text or FIGURE_OPEN in text:  # pragma: no cover - guarded by tests
        raise ValueError("a caption cannot carry a cross-reference: the lists copy it")
    title, note = split_caption(text)
    para = doc.add_paragraph(style="Caption")
    pf = para.paragraph_format
    pf.space_before = Pt(8 if above else 2)
    pf.space_after = Pt(4 if above else 10)
    pf.keep_with_next = above
    # As Word's Insert Caption writes it: the bookmark holds the label and the
    # number, and each part of the SEQ field sits in a run of its own.
    bookmark_id = _open_bookmark(para, bookmark) if bookmark else None
    para.add_run(f"{label} ")
    for run in _field_runs(f" SEQ {label} \\* ARABIC ", str(number)):
        para._p.append(run)
    if bookmark_id is not None:
        _close_bookmark(para, bookmark_id)
    _keep_hyphens(para.add_run(f". {title}"))
    if note:
        rest = doc.add_paragraph(style="Caption")
        rest.paragraph_format.space_after = pf.space_after
        rest.paragraph_format.keep_with_next = above
        _keep_hyphens(rest.add_run(note))
        pf.space_after = Pt(0)
        pf.keep_with_next = True
    return para


def add_figure(
    doc: Document,
    image_path: Path,
    caption: str,
    width_cm: float = 14.5,
    *,
    number: int,
    bookmark: str | None = None,
):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(10)
    para.paragraph_format.space_after = Pt(2)
    # A picture that fills the rest of a page would otherwise leave its
    # caption alone at the top of the next one.
    para.paragraph_format.keep_with_next = True
    para.add_run().add_picture(str(image_path), width=Cm(width_cm))
    add_caption(doc, FIGURE_LABEL, number, caption, bookmark=bookmark)


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
    bookmark: str | None = None,
):
    """Table with its numbered title above it, as the template illustrates.

    Numeric columns are right-aligned so their decimal points line up. Column
    widths come from the cell text unless `col_widths` gives proportions; in
    both cases no column is narrower than its longest unbreakable piece, so a
    number never wraps inside its cell and a word is never split.
    """
    add_caption(doc, TABLE_LABEL, number, caption, above=True, bookmark=bookmark)
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


def add_automatic_table(doc: Document, instruction: str, entries):
    """One of Word's automatic tables: the contents, or a list of figures or
    of tables.

    `entries` holds (style name, text, page, bookmark) for each line, in
    order. Word keeps such a table as a TOC field whose result is the lines
    themselves. This writes the same field, with the lines Word would write
    as its result and the page numbers from a first rendering pass, so the
    document reads correctly as it is, in LibreOffice or in a PDF made
    without Word. Word replaces the result with its own when it updates the
    field: on opening, with F9 or with Update Table.

    As in Word's own tables, each line is a link to its heading or caption,
    which Ctrl+click follows, and its page number is a PAGEREF field. The
    field ends in a paragraph of its own after the last line, where Word ends
    it too, so an update by Word leaves the layout as it was. That paragraph
    is returned so the caller can put a page break in it.
    """
    opened = False
    for style, text, page, bookmark in entries:
        para = doc.add_paragraph(style=style)
        if not opened:
            _field_start(para, instruction)
            opened = True
        label = para.add_run(f"{text}\t")
        _keep_hyphens(label)
        page_number = _field(para, f" PAGEREF {bookmark} \\h ", page or "")
        link = OxmlElement("w:hyperlink")
        link.set(qn("w:anchor"), bookmark)
        link.set(qn("w:history"), "1")
        label._r.addprevious(link)
        link.append(label._r)
        link.append(page_number._r)
    closing = doc.add_paragraph()
    closing.paragraph_format.line_spacing = 1.0
    closing.paragraph_format.space_after = Pt(0)
    if not opened:
        _field_start(closing, instruction)
    _field_end(closing)
    return closing


def add_bibliography(doc: Document, entries) -> None:
    """The reference list, as Word's own BIBLIOGRAPHY field.

    Word renders the list from the document's source list, in the style the
    list names, IEEE here, and keeps it in step with the citations: a source
    cited for the first time joins the list, and the numbers follow the
    order of first citation. A numbered style is laid out as a borderless
    table of two columns, the number and the reference, in the Bibliography
    style. The result written here has that shape, with the entries
    formatted at build time, so the list reads correctly before Word
    updates it.

    `entries` holds (number, pieces) in order, each piece a (text, italic)
    pair. The field sits in the two content controls that Word's References
    > Bibliography writes around it, which is how Word finds the list when
    it updates citations and bibliography together.
    """
    begin = doc.add_paragraph(style="Bibliography")
    _field_start(begin, " BIBLIOGRAPHY ")
    table = doc.add_table(rows=0, cols=2)
    for number, pieces in entries:
        row = table.add_row()
        _row_properties(row, header=False)
        label, reference = (cell.paragraphs[0] for cell in row.cells)
        label.style = doc.styles["Bibliography"]
        reference.style = doc.styles["Bibliography"]
        label.add_run(f"[{number}]")
        for text, italic in pieces:
            run = reference.add_run(text)
            _keep_hyphens(run)
            run.italic = italic or None
    _apply_column_widths(table, [REFERENCE_NUMBER_CM, TEXT_WIDTH_CM - REFERENCE_NUMBER_CM])
    # No cell margins, so the numbers sit at the margin and the entries
    # start at the second column, like a list with a hanging indent.
    margins = OxmlElement("w:tblCellMar")
    for side in ("w:left", "w:right"):
        margin = OxmlElement(side)
        margin.set(qn("w:w"), "0")
        margin.set(qn("w:type"), "dxa")
        margins.append(margin)
    table._tbl.tblPr.find(qn("w:tblLayout")).addnext(margins)
    end = doc.add_paragraph(style="Bibliography")
    _field_end(end)

    gallery = OxmlElement("w:docPartObj")
    name = OxmlElement("w:docPartGallery")
    name.set(qn("w:val"), "Bibliographies")
    gallery.append(name)
    gallery.append(OxmlElement("w:docPartUnique"))
    outer, outer_content = _content_control(gallery)
    inner, inner_content = _content_control(OxmlElement("w:bibliography"))
    begin._p.addprevious(outer)
    outer_content.append(inner)
    for element in (begin._p, table._tbl, end._p):
        inner_content.append(element)


def set_bibliography_sources(doc: Document, sources: bytes) -> None:
    """Make `sources` the document's source list, the one Word's Manage
    Sources shows as the current list.

    python-docx's template, saved by Word, already carries the part that
    holds the list, empty, with its relationship and properties; only its
    content changes.
    """
    for rel in doc.part.rels.values():
        if rel.reltype != RT.CUSTOM_XML:
            continue
        if b"officeDocument/2006/bibliography" in rel.target_part.blob:
            rel.target_part._blob = sources
            return
    raise RuntimeError("the document template has no source list to fill")


LOGO_PATH = Path(__file__).parent / "assets" / "ubt-logo.png"
# The template's picture is this banner cropped to the seal at its left: the
# right 87.565% is cut away (a:srcRect r="87565") and it is set 2.68 cm wide.
LOGO_KEPT_FRACTION = 1 - 0.87565
LOGO_WIDTH_CM = 2.68


def add_logo(doc: Document):
    """The university seal, centred, as the template's two front pages show.

    The template annotates it "do not change the logo", so the file is the one
    embedded in the faculty's own instructions, cropped the way the template
    crops it rather than redrawn.
    """
    if not LOGO_PATH.exists():  # pragma: no cover - the asset ships with the repo
        return None
    with Image.open(LOGO_PATH) as banner:
        seal = banner.crop((0, 0, round(banner.width * LOGO_KEPT_FRACTION), banner.height))
        buffer = io.BytesIO()
        seal.save(buffer, format="PNG")
    buffer.seek(0)
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.line_spacing = 1.0
    para.paragraph_format.space_after = Pt(0)
    para.add_run().add_picture(buffer, width=Cm(LOGO_WIDTH_CM))
    return para


# A space between digit groups, as in "284 807". Typeset as a no-break space so
# that a line never ends inside a number.
THOUSANDS_RE = re.compile(r"(?<=\d) (?=\d{3}\b)")


def keep_numbers_whole(text: str) -> str:
    return THOUSANDS_RE.sub("\u00a0", text)


def page_break(doc: Document):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def _is_break_only(p) -> bool:
    """A paragraph whose only content is one run holding a page break."""
    content = [c for c in p if c.tag != qn("w:pPr")]
    if len(content) != 1 or content[0].tag != qn("w:r"):
        return False
    inner = [c for c in content[0] if c.tag != qn("w:rPr")]
    return len(inner) == 1 and inner[0].tag == qn("w:br") and inner[0].get(qn("w:type")) == "page"


def fold_page_breaks(doc: Document) -> int:
    """Turn each paragraph that holds only a page break into "page break
    before" on the paragraph that follows it.

    A break paragraph is itself a line of text. When the page before it is
    full, the line moves to a page of its own and the break then leaves that
    page blank, which is how the abstract once left page II empty. "Page break
    before" belongs to the next paragraph and cannot do that. A break followed
    by a table or by another break stays as it is.
    """
    from docx.text.paragraph import Paragraph

    body = doc.element.body
    folded = 0
    for p in list(body.iterchildren(qn("w:p"))):
        nxt = p.getnext()
        if not _is_break_only(p) or nxt is None or nxt.tag != qn("w:p") or _is_break_only(nxt):
            continue
        Paragraph(nxt, doc).paragraph_format.page_break_before = True
        body.remove(p)
        folded += 1
    return folded


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

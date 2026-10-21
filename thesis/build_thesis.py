"""Assemble the thesis .docx from chapter content and generated results.

The document is built in two passes. The first walks every block and assigns
numbers — citations in order of first appearance, then figures, tables and
equations in document order. The second renders. Splitting the passes is what
lets a chapter cite a source that is first mentioned three chapters earlier
and still get the right number.

Tables and figures are read from results/, so the thesis cannot drift away
from the experiments: if a number changes, rebuilding the document changes it
everywhere.
"""

import argparse
import ast
import numbers
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content.front_matter import FRONT_ENTRIES  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx_helpers import (  # noqa: E402
    CITE_CLOSE,
    CITE_OPEN,
    add_bullets,
    add_equation,
    add_figure,
    add_heading,
    add_paragraph,
    add_table,
    apply_list_numbering,
    bookmark_paragraph,
    define_reference_numbering,
    figure_bookmark,
    heading_bookmark,
    new_document,
    page_break,
    reference_bookmark,
    start_new_section,
    table_bookmark,
)
from references import REFERENCES  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS = REPO_ROOT / "results"
CITE_RE = re.compile(r"\[@([a-zA-Z0-9_]+)\]")
# A reference to a figure by its name, resolved to the figure's number, so the
# prose can say "Figura 12" without the number going stale when figures move.
FIG_REF_RE = re.compile(r"\[\[fig:([a-zA-Z0-9_]+)\]\]")
# A space that groups thousands ("284 807") must not break across lines.
THOUSANDS_RE = re.compile(r"(?<=\d) (?=\d{3}\b)")
# Printed stand-in for a value that does not exist, rather than "nan".
MISSING = "n/a"  # never an em dash: the thesis reserves that character for nothing


class Numbering:
    """Assigns citation, figure, table and equation numbers in one pass."""

    def __init__(self):
        self.citations: dict[str, int] = {}
        self.figure_numbers: dict[str, int] = {}
        self.figures: dict[int, str] = {}
        self.tables: dict[int, str] = {}
        self._fig = 0
        self._tab = 0
        self._eq = 0

    def cite(self, key: str) -> int:
        if key not in REFERENCES:
            raise KeyError(f"unknown reference key: {key}")
        if key not in self.citations:
            self.citations[key] = len(self.citations) + 1
        return self.citations[key]

    def scan_text(self, text: str) -> None:
        for key in CITE_RE.findall(text):
            self.cite(key)

    def next_figure(self, caption: str) -> int:
        self._fig += 1
        self.figures[self._fig] = caption
        return self._fig

    def next_table(self, caption: str) -> int:
        self._tab += 1
        self.tables[self._tab] = caption
        return self._tab

    def next_equation(self) -> int:
        self._eq += 1
        return self._eq


def resolve_citations(text: str, numbering: Numbering) -> str:
    """Turn [@key] into a marked span the run writers render as a Word field.

    The marker carries both the key, which names the bookmark on the reference
    entry, and the number assigned here, which becomes the field's cached
    result so the text reads correctly before Word refreshes anything. Figure
    references written as [[fig:name]] are replaced by the figure's number.
    """

    def figure(match: re.Match) -> str:
        name = match.group(1)
        if name not in numbering.figure_numbers:
            raise KeyError(f"reference to unknown figure: {name}")
        return str(numbering.figure_numbers[name])

    text = FIG_REF_RE.sub(figure, text)

    def repl(match: re.Match) -> str:
        key = match.group(1)
        return f"{CITE_OPEN}{key}|{numbering.cite(key)}{CITE_CLOSE}"

    text = CITE_RE.sub(repl, text)
    text = THOUSANDS_RE.sub("\u00a0", text)
    # separate adjacent citations: [3][4][7] -> [3], [4], [7]
    return re.sub(f"{CITE_CLOSE}\\s*{CITE_OPEN}", f"{CITE_CLOSE}, {CITE_OPEN}", text)


def load_table(csv_name: str, options: dict) -> pd.DataFrame:
    """Read a results table and prepare it for print.

    Options, all optional: query, pivot ({index, columns, values}), columns,
    replace ({column: {value: shown}}), sort and ascending, round ({column:
    decimals}), fmt ({column: format spec}), rename, max_rows, and transpose
    (the header of the first column once the table is turned on its side).

    Numbers that round and fmt do not cover still print with fixed decimals:
    three in a float column, four when it holds values below 0.01, fewer as
    its magnitude grows, and two significant digits for a p-value. Whole
    numbers print as integers, grouped in thousands once a column reaches
    five digits.
    """
    df = pd.read_csv(RESULTS / f"{csv_name}.csv")
    if "query" in options:
        df = df.query(options["query"])
    if "pivot" in options:
        spec = options["pivot"]
        df = df.pivot(index=spec["index"], columns=spec["columns"], values=spec["values"])
        df = df.reset_index()
        df.columns.name = None
    if "columns" in options:
        df = df[options["columns"]]
    for col in df.columns:
        if df[col].dtype == bool:
            df[col] = df[col].map({True: "Po", False: "Jo"})
        elif df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].map(_readable_config)
    for col, mapping in options.get("replace", {}).items():
        df[col] = df[col].map(lambda v, m=mapping: m.get(v, v))
    if "sort" in options:
        df = df.sort_values(options["sort"], ascending=options.get("ascending", True))
    for col, digits in options.get("round", {}).items():
        if col in df.columns:
            df[col] = _fixed(df[col].astype(float), digits)
    for col, spec in options.get("fmt", {}).items():
        if col in df.columns:
            df[col] = df[col].map(lambda v, s=spec: MISSING if pd.isna(v) else format(v, s))
    for col in df.columns:
        if df[col].dtype.kind != "f":
            continue
        values, present = df[col], df[col].dropna()
        if _is_p_column(col):
            df[col] = values.map(_p_value)
        elif ((present - present.round()).abs() < 1e-9).all():
            df[col] = _fixed(values, 0)
        else:
            df[col] = _fixed(values, _decimals(values))
    if "rename" in options:
        df = df.rename(columns=options["rename"])
    if "max_rows" in options:
        df = df.head(options["max_rows"])
    # A missing value is meaningful in some tables (a detector with no
    # hyperparameters cannot have a tuning delta) but "nan" reads as a bug in a
    # printed thesis; "n/a" says the same thing without alarming anyone.
    df = df.reset_index(drop=True)
    df = df.astype(object).where(df.notna(), MISSING)
    df = df.apply(_group_thousands)
    if "transpose" in options:
        # A table with a few rows and many columns reads better on its side:
        # one row per quantity, one column per window or detector.
        df = df.set_index(df.columns[0]).T
        df.columns = [str(name)[:1].upper() + str(name)[1:] for name in df.columns]
        df = df.reset_index(names=options["transpose"])
    return df


def _fixed(values: pd.Series, digits: int) -> pd.Series:
    """Fixed decimals, so a column does not mix "0.29" with "0.449"."""
    values = values.astype(float).round(digits)
    if digits == 0:
        return values.map(lambda v: MISSING if pd.isna(v) else int(v))
    return values.map(lambda v: MISSING if pd.isna(v) else f"{v:.{digits}f}")


def _decimals(values: pd.Series) -> int:
    magnitude = values.abs().dropna()
    if magnitude.max() >= 1000:
        return 0
    if magnitude.max() >= 100:
        return 1
    if magnitude.max() >= 10:
        return 2
    return 4 if ((magnitude > 0) & (magnitude < 0.01)).any() else 3


def _is_p_column(name) -> bool:
    name = str(name).lower()
    return (
        name == "p"
        or name.startswith(("p_", "p "))
        or name.endswith("_p")
        or "p_value" in name
        or "pvalue" in name
    )


def _p_value(p) -> str:
    """Two significant digits, which is all the precision a p-value carries."""
    if pd.isna(p):
        return MISSING
    if p < 1e-4:
        return "< 0.0001"
    text = format(p, ".2g")
    return text if "." in text else f"{text}.0"


def _group_thousands(column: pd.Series) -> pd.Series:
    """Group thousands with a non-breaking space once a column reaches five
    digits, and then in every number of the column, so they still line up."""

    def whole(v) -> bool:
        return isinstance(v, numbers.Integral) and not isinstance(v, bool)

    if max((abs(v) for v in column if whole(v)), default=0) < 10_000:
        return column
    return column.map(lambda v: f"{v:,}".replace(",", "\u00a0") if whole(v) else v)


def _readable_config(value):
    """A configuration saved as a dict literal, written as key=value pairs."""
    if not (isinstance(value, str) and value.startswith("{") and value.endswith("}")):
        return value
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value
    if not isinstance(parsed, dict):
        return value
    return ", ".join(f"{key}={val}" for key, val in parsed.items())


def collect_outline(chapters: list[list]) -> list[tuple[int, str]]:
    """Headings in document order, as (level, display text) pairs.

    Used to build the table of contents; figure and table lists are collected
    separately because their numbering is assigned during rendering.
    """
    out = []
    for blocks in chapters:
        for block in blocks:
            if block[0] in ("h1", "h2", "h3"):
                level = int(block[0][1])
                out.append((level, f"{block[1]}\t{block[2]}"))
    return out


def first_pass(chapters: list[list], numbering: Numbering) -> None:
    for blocks in chapters:
        for block in blocks:
            if block[0] == "fig":
                numbering.figure_numbers[block[1]] = len(numbering.figure_numbers) + 1
    for blocks in chapters:
        for block in blocks:
            kind = block[0]
            if kind in ("p", "note"):
                numbering.scan_text(block[1])
            elif kind in ("bullets", "numbers"):
                for item in block[1]:
                    numbering.scan_text(item)
            elif kind in ("h1", "h2", "h3") or kind == "fig" or kind == "tab":
                numbering.scan_text(block[2])


def render_blocks(doc, blocks: list, numbering: Numbering, counters: dict) -> None:
    for block in blocks:
        kind = block[0]
        if kind in ("h1", "h2", "h3"):
            add_heading(
                doc,
                resolve_citations(block[2], numbering),
                int(kind[1]),
                block[1],
                bookmark=heading_bookmark(block[1]),
            )
        elif kind == "p":
            add_paragraph(doc, resolve_citations(block[1], numbering))
        elif kind == "note":
            para = add_paragraph(doc, resolve_citations(block[1], numbering), italic=True)
            para.paragraph_format.left_indent = __import__("docx").shared.Cm(1.0)
        elif kind == "bullets":
            add_bullets(doc, [resolve_citations(i, numbering) for i in block[1]])
        elif kind == "numbers":
            add_bullets(doc, [resolve_citations(i, numbering) for i in block[1]], numbered=True)
        elif kind == "fig":
            name, caption, width = block[1], block[2], block[3]
            path = RESULTS / "figures" / f"{name}.png"
            if not path.exists():
                raise FileNotFoundError(f"missing figure: {path}")
            n = counters["figure"]()
            add_figure(
                doc,
                path,
                f"Figura {n}. {resolve_citations(caption, numbering)}",
                width_cm=width,
                bookmark=figure_bookmark(n),
            )
        elif kind == "tab":
            csv_name, caption, options = block[1], block[2], block[3]
            df = load_table(csv_name, options)
            n = counters["table"]()
            add_table(
                doc,
                df,
                resolve_citations(caption, numbering),
                number=n,
                font_size=options.get("font_size", 9.0),
                col_widths=options.get("widths"),
                bookmark=table_bookmark(n),
            )
        elif kind == "eq":
            add_equation(doc, block[1], counters["equation"]())
        elif kind == "pagebreak":
            page_break(doc)
        else:
            raise ValueError(f"unknown block kind: {kind}")


def build(output: Path, page_map: dict[str, str] | None = None):
    from content import (
        ch1_hyrje,
        ch2_literatura,
        ch3_problemi,
        ch4_metodologjia,
        ch5_rezultatet,
        ch6_diskutime,
        ch8_shtojcat,
        front_matter,
    )

    page_map = page_map or {}
    numbering = Numbering()
    # The template puts references at chapter 7 and appendices at chapter 8, so
    # the appendix is rendered after the reference list, not with the body.
    main_chapters = [
        ch1_hyrje.BLOCKS,
        ch2_literatura.BLOCKS,
        ch3_problemi.BLOCKS,
        ch4_metodologjia.BLOCKS,
        ch5_rezultatet.BLOCKS,
        ch6_diskutime.BLOCKS,
    ]
    body_chapters = [*main_chapters, ch8_shtojcat.BLOCKS]
    first_pass(body_chapters, numbering)

    # Figure and table captions have to be known before the lists that
    # reference them are written, so the body is walked once in "dry" mode to
    # assign their numbers, then rendered for real.
    dry = Numbering()
    first_pass(body_chapters, dry)
    dry_fig, dry_tab = _scan_captions(body_chapters)

    doc = new_document()
    front_matter.render_cover(doc)
    outline = (
        collect_outline(main_chapters)
        + [(1, "7\tREFERENCAT")]
        + collect_outline([ch8_shtojcat.BLOCKS])
    )
    front_matter.render_prelims(doc, outline, dry_fig, dry_tab, page_map)

    # Body restarts page numbering at Arabic 1, per the template.
    start_new_section(doc, "decimal", start=1)

    fig_no = {"n": 0}
    tab_no = {"n": 0}
    eq_no = {"n": 0}

    def next_fig():
        fig_no["n"] += 1
        return fig_no["n"]

    def next_tab():
        tab_no["n"] += 1
        return tab_no["n"]

    def next_eq():
        eq_no["n"] += 1
        return eq_no["n"]

    counters = {"figure": next_fig, "table": next_tab, "equation": next_eq}

    for i, blocks in enumerate(main_chapters):
        if i > 0:
            page_break(doc)
        render_blocks(doc, blocks, numbering, counters)

    # Chapter 7: references, ordered by first appearance.
    page_break(doc)
    add_heading(doc, "REFERENCAT", 1, "7", bookmark=heading_bookmark("7"))
    num_id = define_reference_numbering(doc)
    ordered = sorted(numbering.citations.items(), key=lambda kv: kv[1])
    for key, _num in ordered:
        para = add_paragraph(doc, REFERENCES[key], align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6)
        apply_list_numbering(para, num_id)
        bookmark_paragraph(para, reference_bookmark(key))

    # Chapter 8: appendices, after the reference list as the template requires.
    page_break(doc)
    render_blocks(doc, ch8_shtojcat.BLOCKS, numbering, counters)

    doc.save(output)
    return output, numbering, fig_no["n"], tab_no["n"], eq_no["n"]


def _scan_captions(chapters: list[list]) -> tuple[list[str], list[str]]:
    """Figure and table captions in document order, with their numbers."""
    figures, tables = [], []
    for blocks in chapters:
        for block in blocks:
            if block[0] == "fig":
                figures.append(f"Figura {len(figures) + 1}. {block[2]}")
            elif block[0] == "tab":
                tables.append(f"Tabela {len(tables) + 1}. {block[2]}")
    return figures, tables


def _pdf_pages(pdf_path: Path) -> list[str]:
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return text.split("\f")


def _normalise(text: str) -> str:
    # A non-breaking hyphen comes back from the PDF as U+2011.
    return re.sub(r"\s+", " ", text.replace("‑", "-")).strip().lower()


def extract_page_numbers(pdf_path: Path, entries: list[str], body_anchor: str) -> dict[str, str]:
    """Map each contents entry to the printed page it appears on.

    Two traps here. The body restarts numbering at Arabic 1, so the offset is
    found from the rendered pages rather than assumed. And the table of
    contents itself contains every heading string, so a naive search matches
    the contents page for everything — the scan therefore starts only after
    the first page of actual body text, located with a distinctive sentence
    from the opening paragraph.
    """
    pages = [_normalise(p) for p in _pdf_pages(pdf_path)]
    anchor = _normalise(body_anchor)[:60]
    offset = next((i for i, page in enumerate(pages) if anchor and anchor in page), None)
    if offset is None:
        return {}

    mapping: dict[str, str] = {}
    for entry in entries:
        probe = _normalise(entry)[:70]
        for i in range(offset, len(pages)):
            if probe and probe in pages[i]:
                mapping[entry] = str(i - offset + 1)
                break
    return mapping


def _roman(number: int) -> str:
    values = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    out = []
    for value, letters in values:
        count, number = divmod(number, value)
        out.append(letters * count)
    return "".join(out)


def extract_front_pages(pdf_path: Path, titles: list[str]) -> dict[str, str]:
    """Roman page numbers of the front-matter titles the contents lists.

    The front matter is numbered from the abstract, which is page I. A title
    is found as a line of its own, and the last such line is the one wanted:
    the contents names each title first, on a line of its own in the first
    pass, before its page numbers are known.
    """
    pages = [
        [line.strip() for line in page.splitlines() if line.strip()]
        for page in _pdf_pages(pdf_path)
    ]
    first = next((i for i, lines in enumerate(pages) if "ABSTRAKT" in lines), None)
    if first is None:
        return {}
    mapping: dict[str, str] = {}
    for title in titles:
        found = [i for i in range(first, len(pages)) if title in pages[i]]
        if found:
            mapping[title] = _roman(found[-1] - first + 1)
    return mapping


def render_pdf(docx_path: Path) -> Path:
    subprocess.run(
        [
            "/snap/bin/libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(docx_path.parent),
            str(docx_path),
        ],
        capture_output=True,
        check=True,
        timeout=900,
    )
    return docx_path.with_suffix(".pdf")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default=str(REPO_ROOT / "thesis" / "out" / "Punimi_Diplomes_GentritHalimi.docx")
    )
    parser.add_argument(
        "--single-pass", action="store_true", help="skip the page-number resolution pass"
    )
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Pass 1: the contents entries exist but carry no page numbers, so the
    # front matter already occupies its final number of pages.
    path, numbering, n_fig, n_tab, n_eq = build(out)
    print(f"faza 1: {path}")

    if not args.single_pass:
        pdf = render_pdf(path)
        entries, anchor = _all_entries(out)
        mapping = extract_page_numbers(pdf, entries, anchor)
        front = list(FRONT_ENTRIES)
        mapping |= extract_front_pages(pdf, front)
        found, wanted = len(mapping), len(entries) + len(front)
        print(f"faza 2: u gjetën numra faqesh për {found}/{wanted} zëra")
        path, numbering, n_fig, n_tab, n_eq = build(out, page_map=mapping)
        render_pdf(path)

    print(f"shkruar: {path}")
    print(f"  referenca të cituara: {len(numbering.citations)}")
    print(f"  figura: {n_fig} | tabela: {n_tab} | ekuacione: {n_eq}")


def _all_entries(_output: Path) -> tuple[list[str], str]:
    from content import (
        ch1_hyrje,
        ch2_literatura,
        ch3_problemi,
        ch4_metodologjia,
        ch5_rezultatet,
        ch6_diskutime,
        ch8_shtojcat,
    )

    chapters = [
        ch1_hyrje.BLOCKS,
        ch2_literatura.BLOCKS,
        ch3_problemi.BLOCKS,
        ch4_metodologjia.BLOCKS,
        ch5_rezultatet.BLOCKS,
        ch6_diskutime.BLOCKS,
        ch8_shtojcat.BLOCKS,
    ]
    headings = (
        [text for _, text in collect_outline(chapters[:6])]
        + ["7\tREFERENCAT"]
        + [text for _, text in collect_outline([chapters[6]])]
    )
    figures, tables = _scan_captions(chapters)
    # Distinctive opening sentence of the body, used to find where Arabic page
    # numbering starts in the rendered PDF.
    anchor = next(b[1] for b in ch1_hyrje.BLOCKS if b[0] == "p")
    return headings + figures + tables, anchor


if __name__ == "__main__":
    main()

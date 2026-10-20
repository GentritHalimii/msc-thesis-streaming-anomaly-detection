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
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    new_document,
    page_break,
    reference_bookmark,
    start_new_section,
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
    df = pd.read_csv(RESULTS / f"{csv_name}.csv")
    if "query" in options:
        df = df.query(options["query"])
    if "columns" in options:
        df = df[options["columns"]]
    if "sort" in options:
        df = df.sort_values(options["sort"], ascending=options.get("ascending", True))
    if "round" in options:
        for col, digits in options["round"].items():
            if col not in df.columns:
                continue
            values = df[col].astype(float).round(digits)
            if digits > 0:
                # Fixed decimals, so a column does not mix "0.29" with "0.449".
                df[col] = values.map(lambda v, d=digits: MISSING if pd.isna(v) else f"{v:.{d}f}")
            else:
                df[col] = values
    if "fmt" in options:
        for col, spec in options["fmt"].items():
            if col in df.columns:
                df[col] = df[col].map(lambda v, s=spec: format(v, s))
    if "rename" in options:
        df = df.rename(columns=options["rename"])
    if "max_rows" in options:
        df = df.head(options["max_rows"])
    df = _tidy_integers(df.reset_index(drop=True), options.get("round", {}))
    # A missing value is meaningful in some tables (a detector with no
    # hyperparameters cannot have a tuning delta) but "nan" reads as a bug in a
    # printed thesis; an em dash says the same thing without alarming anyone.
    return df.astype(object).where(df.notna(), MISSING)


def _tidy_integers(df: pd.DataFrame, rounded: dict) -> pd.DataFrame:
    """Render whole numbers as whole numbers.

    Counts survive the CSV round trip as floats, so a fold index prints as
    "0.0" and a row count as "113922.0". Any numeric column whose values are
    all integral, and which was not explicitly asked to keep decimals, is
    converted back to an integer.
    """
    for col in df.columns:
        if col in rounded and rounded[col] > 0:
            continue
        series = df[col]
        if series.dtype.kind != "f" or series.isna().any():
            continue
        if ((series - series.round()).abs() < 1e-9).all():
            df[col] = series.round().astype("int64")
    return df


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
        if kind == "h1":
            add_heading(doc, resolve_citations(block[2], numbering), 1, block[1])
        elif kind == "h2":
            add_heading(doc, resolve_citations(block[2], numbering), 2, block[1])
        elif kind == "h3":
            add_heading(doc, resolve_citations(block[2], numbering), 3, block[1])
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
                doc, path, f"Figura {n}. {resolve_citations(caption, numbering)}", width_cm=width
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
    add_heading(doc, "REFERENCAT", 1, "7")
    num_id = define_reference_numbering(doc)
    ordered = sorted(numbering.citations.items(), key=lambda kv: kv[1])
    for bookmark_id, (key, _num) in enumerate(ordered, start=1):
        para = add_paragraph(doc, REFERENCES[key], align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6)
        apply_list_numbering(para, num_id)
        bookmark_paragraph(para, reference_bookmark(key), bookmark_id)

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
        print(f"faza 2: u gjetën numra faqesh për {len(mapping)}/{len(entries)} zëra")
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

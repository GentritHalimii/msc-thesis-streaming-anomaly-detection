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
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402

from docx_helpers import (  # noqa: E402
    add_bullets,
    add_caption,
    add_equation,
    add_figure,
    add_heading,
    add_paragraph,
    add_table,
    add_toc_field,
    new_document,
    page_break,
    set_page_numbering,
    start_new_section,
)
from references import REFERENCES  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS = REPO_ROOT / "results"
CITE_RE = re.compile(r"\[@([a-zA-Z0-9_]+)\]")


class Numbering:
    """Assigns citation, figure, table and equation numbers in one pass."""

    def __init__(self):
        self.citations: dict[str, int] = {}
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
    """Replace [@a][@b] runs with a single bracket group, IEEE style."""
    def repl(match: re.Match) -> str:
        return f"[{numbering.cite(match.group(1))}]"

    text = CITE_RE.sub(repl, text)
    # merge adjacent bracket groups: [3][4][7] -> [3], [4], [7]
    return re.sub(r"\](\s*)\[", r"], [", text)


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
            if col in df.columns:
                df[col] = df[col].astype(float).round(digits)
    if "fmt" in options:
        for col, spec in options["fmt"].items():
            if col in df.columns:
                df[col] = df[col].map(lambda v, s=spec: format(v, s))
    if "rename" in options:
        df = df.rename(columns=options["rename"])
    if "max_rows" in options:
        df = df.head(options["max_rows"])
    return df.reset_index(drop=True)


def first_pass(chapters: list[list], numbering: Numbering) -> None:
    for blocks in chapters:
        for block in blocks:
            kind = block[0]
            if kind in ("p", "note"):
                numbering.scan_text(block[1])
            elif kind in ("bullets", "numbers"):
                for item in block[1]:
                    numbering.scan_text(item)
            elif kind in ("h1", "h2", "h3"):
                numbering.scan_text(block[2])
            elif kind == "fig":
                numbering.scan_text(block[2])
            elif kind == "tab":
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
            add_figure(doc, path, f"Figura {n}. {resolve_citations(caption, numbering)}",
                       width_cm=width)
        elif kind == "tab":
            csv_name, caption, options = block[1], block[2], block[3]
            df = load_table(csv_name, options)
            n = counters["table"]()
            add_table(doc, df, resolve_citations(caption, numbering), number=n,
                      font_size=options.get("font_size", 9.0))
        elif kind == "eq":
            add_equation(doc, block[1], counters["equation"]())
        elif kind == "pagebreak":
            page_break(doc)
        else:
            raise ValueError(f"unknown block kind: {kind}")


def build(output: Path) -> Path:
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

    numbering = Numbering()
    body_chapters = [
        ch1_hyrje.BLOCKS,
        ch2_literatura.BLOCKS,
        ch3_problemi.BLOCKS,
        ch4_metodologjia.BLOCKS,
        ch5_rezultatet.BLOCKS,
        ch6_diskutime.BLOCKS,
        ch8_shtojcat.BLOCKS,
    ]
    first_pass(body_chapters, numbering)

    doc = new_document()
    front_matter.render_cover(doc)
    front_matter.render_prelims(doc, numbering)

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

    for i, blocks in enumerate(body_chapters):
        if i > 0:
            page_break(doc)
        render_blocks(doc, blocks, numbering, counters)

    # References, ordered by first appearance.
    page_break(doc)
    add_heading(doc, "REFERENCAT", 1, "7")
    ordered = sorted(numbering.citations.items(), key=lambda kv: kv[1])
    for key, num in ordered:
        para = add_paragraph(doc, f"[{num}]\t{REFERENCES[key]}",
                             align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6)
        para.paragraph_format.left_indent = __import__("docx").shared.Cm(1.2)
        para.paragraph_format.first_line_indent = __import__("docx").shared.Cm(-1.2)

    doc.save(output)
    return output, numbering, fig_no["n"], tab_no["n"], eq_no["n"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(REPO_ROOT / "thesis" / "out" /
                                                "Punimi_Diplomes_GentritHalimi.docx"))
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    path, numbering, n_fig, n_tab, n_eq = build(out)
    print(f"shkruar: {path}")
    print(f"  referenca të cituara: {len(numbering.citations)}")
    print(f"  figura: {n_fig} | tabela: {n_tab} | ekuacione: {n_eq}")


if __name__ == "__main__":
    main()

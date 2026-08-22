"""Tiny authoring vocabulary for thesis content.

Chapters are plain Python lists of blocks. Keeping the content as data rather
than as imperative docx calls means the same source can be checked, counted
and re-rendered without touching the formatting layer, and it keeps the
chapter files readable as prose.

Citations are written inline as [@key]; the builder resolves them to IEEE
numbers in order of first appearance across the whole document.
"""


def h1(number: str, title: str):
    return ("h1", number, title)


def h2(number: str, title: str):
    return ("h2", number, title)


def h3(number: str, title: str):
    return ("h3", number, title)


def p(text: str):
    return ("p", " ".join(text.split()))


def bullets(items: list[str]):
    return ("bullets", [" ".join(i.split()) for i in items])


def numbers(items: list[str]):
    return ("numbers", [" ".join(i.split()) for i in items])


def fig(name: str, caption: str, width_cm: float = 14.5):
    return ("fig", name, " ".join(caption.split()), width_cm)


def tab(csv_name: str, caption: str, **options):
    return ("tab", csv_name, " ".join(caption.split()), options)


def eq(expression: str):
    return ("eq", expression)


def pagebreak():
    return ("pagebreak",)


def note(text: str):
    """Indented, italic aside — used sparingly for methodological caveats."""
    return ("note", " ".join(text.split()))

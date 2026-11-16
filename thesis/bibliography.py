"""The reference list in IEEE style, and the sources as Word stores them.

Word keeps a document's sources in a custom XML part in the bibliography
namespace of Office Open XML, and renders the citations and the reference
list from that part with the style it names. `word_sources` writes the part:
every source with the fields of its type, the IEEE style, and the order in
which the sources are first cited, which is the order of an IEEE list.

`ieee_entry` formats a source the way the reference list prints it. Word
formats the list itself when it updates the bibliography field; these
entries are the field's result until then, so the document reads correctly
in LibreOffice, in the PDF and in Word before an update.
"""

import re
import uuid
from xml.sax.saxutils import escape

from references import REFERENCES, Source

BIBLIOGRAPHY_NS = "http://schemas.openxmlformats.org/officeDocument/2006/bibliography"
# Word's built-in IEEE style, named as Word names it in a document.
WORD_STYLE = 'SelectedStyle="\\IEEE2006OfficeOnline.xsl" StyleName="IEEE" Version="2006"'
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
MONTH_ABBR = (
    "Jan.",
    "Feb.",
    "Mar.",
    "Apr.",
    "May",
    "Jun.",
    "Jul.",
    "Aug.",
    "Sep.",
    "Oct.",
    "Nov.",
    "Dec.",
)
# IEEE names up to six authors; a longer list is cut to the first and "et al.".
MAX_AUTHORS = 6


def source_tag(key: str) -> str:
    """The source's tag in Word, which its CITATION fields name: the key in
    letters and digits only."""
    return re.sub(r"[^0-9A-Za-z]", "", key)


def _authors(source: Source) -> str:
    names = source.authors
    if source.corporate or len(names) == 1:
        return names[0]
    if len(names) > MAX_AUTHORS:
        return f"{names[0]} et al."
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _online(source: Source) -> str:
    if not source.url:
        return ""
    year, month, day = source.accessed
    return f" Accessed: {MONTH_ABBR[month - 1]} {day}, {year}. [Online]. Available: {source.url}"


def ieee_entry(source: Source) -> list[tuple[str, bool]]:
    """One reference in IEEE style, as (text, italic) pieces: the journal,
    the proceedings and a book's title are set in italics."""
    authors = _authors(source)
    if source.kind == "JournalArticle":
        tail = f", vol. {source.volume}"
        if source.issue:
            tail += f", no. {source.issue}"
        if source.pages:
            tail += f", pp. {source.pages}"
        elif source.article:
            tail += f", Art. no. {source.article}"
        return [
            (f"{authors}, “{source.title},” ", False),
            (source.container, True),
            (f"{tail}, {source.year}.", False),
        ]
    if source.kind == "ConferenceProceedings":
        tail = f", vol. {source.volume}" if source.volume else ""
        tail += f", {source.city}, {source.year}"
        if source.pages:
            tail += f", pp. {source.pages}"
        return [
            (f"{authors}, “{source.title},” in ", False),
            (source.container, True),
            (f"{tail}.", False),
        ]
    if source.kind == "Book":
        edition = f", {source.edition} ed." if source.edition else "."
        return [
            (f"{authors}, ", False),
            (source.title, True),
            (
                f"{edition} {source.city}: {source.publisher}, {source.year}.{_online(source)}",
                False,
            ),
        ]
    if source.kind == "Report":
        date = f"{MONTH_ABBR[source.month - 1]} {source.year}"
        place = f"{source.publisher}, {source.city}, {date}."
        return [(f"{authors}, “{source.title},” {place}{_online(source)}", False)]
    if source.kind == "InternetSite":
        site = f"{source.container}, {source.year}."
        return [(f"{authors}, “{source.title},” {site}{_online(source)}", False)]
    raise ValueError(f"no IEEE format for source type {source.kind}")


def _field(name: str, value) -> str:
    return f"<b:{name}>{escape(str(value))}</b:{name}>" if value else ""


def _person(name: str) -> str:
    """'F. T. Liu' as Word's name parts: the initials, then the surname,
    which may have several words ('A. van den Hengel')."""
    parts = name.split()
    initials = 0
    while initials < len(parts) - 1 and parts[initials].endswith("."):
        initials += 1
    first = parts[0] if initials else ""
    middle = " ".join(parts[1:initials])
    last = " ".join(parts[initials:])
    fields = _field("Last", last) + _field("First", first) + _field("Middle", middle)
    return f"<b:Person>{fields}</b:Person>"


def _source(key: str, source: Source, order: int) -> str:
    if source.corporate:
        names = _field("Corporate", source.authors[0])
    else:
        people = "".join(_person(name) for name in source.authors)
        names = f"<b:NameList>{people}</b:NameList>"
    fields = [
        _field("Tag", source_tag(key)),
        _field("SourceType", source.kind),
        # A fixed identifier per source, so Word can tell a source it has
        # already copied into its master list from a new one.
        _field("Guid", "{" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"thesis:{key}")).upper() + "}"),
        f"<b:Author><b:Author>{names}</b:Author></b:Author>",
        _field("Title", source.title),
        _field("Year", source.year),
    ]
    if source.kind == "JournalArticle":
        # Word's journal article has no field for an article number, so it
        # follows the issue number, where Word prints it in the same place
        # as the list written here: "no. 2, Art. no. 38".
        issue = source.issue
        if source.article:
            issue = f"{issue}, Art. no. {source.article}" if issue else f"Art. no. {source.article}"
        fields += [
            _field("JournalName", source.container),
            _field("Volume", source.volume),
            _field("Issue", issue),
            _field("Pages", source.pages),
        ]
    elif source.kind == "ConferenceProceedings":
        fields += [
            _field("ConferenceName", source.container),
            _field("Volume", source.volume),
            _field("City", source.city),
            _field("Pages", source.pages),
        ]
    elif source.kind == "InternetSite":
        fields.append(_field("InternetSiteTitle", source.container))
    else:
        fields += [
            _field("City", source.city),
            _field("Publisher", source.publisher),
            _field("Edition", source.edition),
            _field("Month", MONTHS[source.month - 1] if source.month else ""),
        ]
    if source.url:
        year, month, day = source.accessed
        fields += [
            _field("URL", source.url),
            _field("YearAccessed", year),
            _field("MonthAccessed", MONTHS[month - 1]),
            _field("DayAccessed", day),
        ]
    fields.append(_field("RefOrder", order))
    return "<b:Source>" + "".join(fields) + "</b:Source>"


def word_sources(cited: list[str]) -> bytes:
    """The document's source list, in Word's format, with the IEEE style
    selected. `cited` holds the keys in the order of first citation, which
    becomes each source's place in the list. Only cited works are listed, as
    in the references themselves."""
    sources = "".join(
        _source(key, REFERENCES[key], order) for order, key in enumerate(cited, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<b:Sources {WORD_STYLE} xmlns:b="{BIBLIOGRAPHY_NS}" xmlns="{BIBLIOGRAPHY_NS}">'
        f"{sources}</b:Sources>"
    ).encode()

"""House style for the thesis text, enforced rather than remembered.

Three rules, all of which came from review feedback and all of which are easy
to violate again by accident:

* No em dashes inside prose. They are not part of ordinary Albanian
  punctuation and their presence in long stretches of text reads as machine
  output. Commas, semicolons, colons and parentheses do the same work.
* No first-person singular. A thesis reports what was done, not what "I" did.
* Technical terms that are standard in English inside Albanian technical
  writing stay in English. The title itself keeps "unsupervised", so the body
  must not translate it either.
"""

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "thesis"))

CHAPTER_MODULES = [
    "ch1_hyrje",
    "ch2_literatura",
    "ch3_problemi",
    "ch4_metodologjia",
    "ch5_rezultatet",
    "ch6_diskutime",
    "ch8_shtojcat",
]

# Albanian first-person singular markers. Verb forms are listed explicitly
# because Albanian drops the pronoun far more often than it uses it.
FIRST_PERSON = re.compile(
    r"\b(unë|mua|imi|imja|sipas njohurive të mia|"
    r"konsideroj|mendoj|besoj|vërejta|vëreja|zgjodha|zgjedha|implementova|"
    r"verifikova|mata|matja ime|analizova|krahasova|përdora|ndërtova|shkrova|"
    r"do të thoja|do të nxirrja|do t'i konsideroja|do të konsideroja)\b",
    re.IGNORECASE,
)

# Words that must not be translated, mapped to the translation to reject.
KEEP_IN_ENGLISH = {
    "unsupervised": [
        "i pambikëqyrur",
        "të pambikëqyrur",
        "e pambikëqyrur",
        "së pambikëqyrur",
        "pambikëqyrura",
    ],
}


def _blocks():
    from importlib import import_module

    for name in CHAPTER_MODULES:
        module = import_module(f"content.{name}")
        yield name, module.BLOCKS


def _texts(blocks):
    for block in blocks:
        kind = block[0]
        if kind in ("p", "note"):
            yield block[1]
        elif kind in ("bullets", "numbers"):
            yield from block[1]
        elif kind in ("h1", "h2", "h3", "fig", "tab"):
            yield block[2]


def _front_matter_texts():
    from content import front_matter

    yield from front_matter.ABSTRAKT
    yield from front_matter.ABSTRACT_EN
    yield from (meaning for _, meaning in front_matter.FJALORI)


def test_no_em_dashes_in_prose():
    offenders = []
    for name, blocks in _blocks():
        for text in _texts(blocks):
            if "—" in text:
                offenders.append(f"{name}: ...{text[max(0, text.index('—') - 60) :][:120]}...")
    for text in _front_matter_texts():
        if "—" in text:
            offenders.append(f"front_matter: ...{text[:120]}...")
    assert not offenders, "em dashes found in prose:\n" + "\n".join(offenders[:10])


def test_no_first_person_singular():
    offenders = []
    for name, blocks in _blocks():
        for text in _texts(blocks):
            for match in FIRST_PERSON.finditer(text):
                start = max(0, match.start() - 60)
                snippet = text[start : match.end() + 40]
                offenders.append(f"{name}: '{match.group(0)}' in ...{snippet}...")
    assert not offenders, "first-person singular found:\n" + "\n".join(offenders[:10])


@pytest.mark.parametrize("term", sorted(KEEP_IN_ENGLISH))
def test_terms_that_belong_in_english_are_not_translated(term):
    """The thesis title keeps these words in English, so the body must too."""
    banned = KEEP_IN_ENGLISH[term]
    offenders = []
    for name, blocks in _blocks():
        for text in _texts(blocks):
            lowered = text.lower()
            for variant in banned:
                if variant in lowered:
                    idx = lowered.index(variant)
                    snippet = text[max(0, idx - 50) : idx + 60]
                    offenders.append(f"{name}: '{variant}' in ...{snippet}...")
    assert not offenders, f"'{term}' was translated; keep it in English:\n" + "\n".join(
        offenders[:10]
    )

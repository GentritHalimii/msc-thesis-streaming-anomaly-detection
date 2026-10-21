"""Cover pages, abstracts, acknowledgements, contents and glossary.

The layout follows the faculty template literally: two title pages set in
Times New Roman 14 with the template's spacing, an abstract confined to a
single page and carrying no chapter number, page numbering that starts there
in Roman numerals, and a contents page that opens with the figure list, the
table list and the glossary. The page numbers in the contents and in the two
lists are Word fields, so they stay correct after any edit.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx_helpers import (
    add_logo,
    add_paragraph,
    add_toc_entry,
    figure_bookmark,
    heading_bookmark,
    page_break,
    start_new_section,
    table_bookmark,
)

TITULLI = (
    "ZBULIMI I ANOMALIVE NË RRJEDHA TË SIMULUARA TË TRANSAKSIONEVE FINANCIARE DUKE PËRDORUR APACHE "
    "KAFKA DHE UNSUPERVISED MACHINE LEARNING: STUDIM RASTI ME TRANSAKSIONE TË KARTAVE TË KREDITIT"
)
STUDENTI = "Gentrit Halimi"
MENTORI = "Dr. sc. Mehmet Shala"
PROGRAMI = "Programi për Shkenca Kompjuterike dhe Inxhinieri"
DATA = "Nëntor 2026"
VITI_AKADEMIK = "Viti akademik 2024 – 2025"


# The template sets every line of both title pages in Times New Roman 14.
COVER_SIZE = Pt(14)
STATEMENT = (
    "Ky punim është përpiluar dhe dorëzuar në përmbushjen e kërkesave të pjesshme për Shkallën "
    "e Magjistraturës"
)


def _line(doc, text: str = "", bold: bool = False):
    """One single-spaced, centred line of a title page.

    An empty line is one of the template's "S" spacers. It holds a space so
    that it takes the height of a 14 pt line, not of the default font.
    """
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = para.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    run = para.add_run(text or " ")
    run.font.name = "Times New Roman"
    run.font.size = COVER_SIZE
    run.bold = bold
    return para


def _spacers(doc, count: int) -> None:
    for _ in range(count):
        _line(doc)


def render_cover(doc) -> None:
    """The template's two title pages, line for line; neither is numbered.

    Only the title is bold. The template's title takes one line and this one
    four, so the first page drops one spacer from each of its three gaps; that
    keeps the template's proportions and leaves room at the foot of the page.
    The second page fits with the template's spacing unchanged.
    """
    section = doc.sections[0]
    section.different_first_page_header_footer = False

    add_logo(doc)
    _line(doc, PROGRAMI)
    _spacers(doc, 10)
    _line(doc, TITULLI, bold=True)
    _line(doc, "Shkalla e Magjistraturës")
    _spacers(doc, 7)
    _line(doc, STUDENTI)
    _spacers(doc, 7)
    _line(doc, DATA)
    _line(doc, "Prishtinë")
    page_break(doc)

    add_logo(doc)
    _line(doc, PROGRAMI)
    _spacers(doc, 2)
    _line(doc, "Punim Diplome")
    _line(doc, VITI_AKADEMIK)
    _spacers(doc, 5)
    _line(doc, STUDENTI)
    _spacers(doc, 1)
    _line(doc, TITULLI, bold=True)
    _spacers(doc, 1)
    _line(doc, f"Mentori: {MENTORI}")
    _spacers(doc, 6)
    _line(doc, DATA)
    _spacers(doc, 7)
    _line(doc, STATEMENT)


ABSTRAKT = [
    "Zbulimi i mashtrimeve me karta krediti bëhet gjithnjë e më shumë mbi rrjedha të vazhdueshme "
    "të dhënash, ku etiketat e verifikuara vijnë me vonesë ditësh ose javësh, ndërsa vendimi duhet "
    "marrë brenda milisekondash. Ky punim dizajnon, implementon dhe vlerëson një sistem end-to-end "
    "për zbulimin e anomalive mbi një rrjedhë të simuluar transaksionesh, i cili lidh Apache "
    "Kafka-n me tri algoritmet unsupervised të projekt-propozimit (Isolation Forest, Autoencoder "
    "dhe One-Class SVM) dhe me Regresionin Logjistik si referencë të mbikëqyrur.",
    "Detektorët vlerësohen mbi dataset-in publik të ULB-së me një protokoll rolling-origin 8-fold, "
    "që rindërton skaluesin, modelet dhe pragjet në çdo fold, me Average Precision (AP) si metrikë "
    "kryesore. Percentili 99 i vonesës end-to-end nuk e kalon 132 milisekonda në asnjë nga ritmet "
    "e testuara, deri në 2000 mesazhe në sekondë, shumë nën objektivin prej një sekonde.",
    "Në konfigurimin bazë Autoencoder-i ofron balancën më të mirë mes cilësisë dhe kostos, me AP "
    "0.193 dhe koston më të ulët të pikëzimit, para One-Class SVM-së (0.151) dhe Isolation "
    "Forest-it (0.091). Referenca e mbikëqyrur arrin 0.734, gjë që tregon sa vlejnë etiketat "
    "historike. Asnjë ansambël nuk e kalon modelin më të mirë individual, sepse detektorët gabojnë "
    "njësoj: me 100 alarme për bllok, 37% e mashtrimeve nuk i arrin asnjë prej tyre, ndërsa "
    "referenca e mbikëqyrur kap 59% të këtyre mashtrimeve.",
    "Konfigurimi peshon më shumë se zgjedhja e algoritmit. Transformimi kuantil e rrit AP-në e "
    "One-Class SVM-së me 0.218, me përmirësim në të tetë fold-et, dhe kur secili detektor merr "
    "konfigurimin e tij më të mirë, raporti mes më të mirit dhe më të dobëtit bie nga 2.1 në 1.15. "
    "Ndarja e rastësishme e të dhënave, e zakonshme në literaturë, e rrit AP-në e metodave "
    "unsupervised rreth tri herë. Një prag adaptiv me dritare rrëshqitëse e bën ngarkesën e "
    "hetimeve më të qëndrueshme dhe rrit F1 për të tre detektorët unsupervised.",
]

ABSTRACT_EN = [
    "Credit-card fraud detection increasingly runs on continuous data streams, where verified "
    "labels arrive days or weeks late while decisions must be made within milliseconds. This "
    "thesis designs, implements and evaluates an end-to-end anomaly detection system over a "
    "simulated transaction stream. The system connects Apache Kafka with the three unsupervised "
    "algorithms named in the research proposal (Isolation Forest, Autoencoder and One-Class SVM) "
    "and with Logistic Regression as a supervised reference.",
    "The detectors are evaluated on the public ULB dataset with an 8-fold rolling-origin protocol "
    "that rebuilds the scaler, the models and the thresholds in every fold, with Average Precision "
    "(AP) as the primary metric. The 99th-percentile end-to-end latency stays below 132 "
    "milliseconds at every arrival rate tested, up to 2000 messages per second, far below the "
    "one-second target.",
    "In the default configuration the Autoencoder offers the best balance between quality and "
    "cost, with an AP of 0.193 and the lowest scoring cost, ahead of One-Class SVM (0.151) and "
    "Isolation Forest (0.091). The supervised reference reaches 0.734, which shows what historical "
    "labels are worth. No ensemble beats the best single model, because the detectors make the "
    "same mistakes: with 100 alerts per block, 37% of the frauds are reached by none of them, "
    "while the supervised reference catches 59% of those frauds.",
    "Configuration matters more than the choice of algorithm. A quantile transform raises the AP "
    "of One-Class SVM by 0.218, improving all eight folds, and when each detector receives its "
    "best configuration the ratio between the best and the weakest falls from 2.1 to 1.15. A "
    "shuffled split, common in the literature, inflates the AP of the unsupervised methods about "
    "threefold. A sliding-window adaptive threshold makes the investigation workload steadier and "
    "raises F1 for all three unsupervised detectors.",
]

MIRENJOHJE = [
    "Falënderime të veçanta i shkojnë mentorit, Dr. sc. Mehmet Shala, për udhëzimet e sakta dhe "
    "për lirinë që kjo temë të ndiqej në thellësi, sidomos kur rezultatet e para nuk përputheshin "
    "me pritjet.",
    "Falënderime i shkojnë gjithashtu stafit akademik të Programit për Shkenca Kompjuterike dhe "
    "Inxhinieri në UBT, në veçanti për lëndët Advanced Machine Learning dhe Deep Learning, të "
    "cilat e formuan idenë se vlerësimi eksperimental është pjesë qendrore e kërkimit dhe jo hapi "
    "i fundit i tij.",
    "Një falënderim i takon grupit Machine Learning të Université Libre de Bruxelles për "
    "publikimin e dataset-it që e bëri të mundur këtë studim, si dhe komunitetit të softuerit të "
    "lirë, pa të cilin një infrastrukturë e tillë nuk do të ishte e arritshme në kuadrin e një "
    "punimi diplome.",
    "Së fundi, falënderime familjes për durimin dhe mbështetjen gjatë muajve kur kjo punë zuri "
    "pjesën më të madhe të kohës.",
]

FJALORI = [
    (
        "AP",
        "Average Precision, sipërfaqja nën kurbën precision-recall; metrika kryesore e këtij "
        "punimi",
    ),
    ("AE", "Autoencoder, rrjet nervor që mëson të rindërtojë hyrjen e vet"),
    ("AUC", "Area Under the Curve, sipërfaqja nën kurbë"),
    ("CV", "Coefficient of Variation, koeficienti i variacionit"),
    ("FN", "False Negative, mashtrim i pazbuluar"),
    (
        "Fold",
        "Një nga pikat e prerjes së protokollit rolling-origin: një dritare trajnimi dhe blloku i "
        "testimit që e pason; 8-fold do të thotë tetë pika të tilla",
    ),
    ("FP", "False Positive, alarm i rremë"),
    ("IF", "Isolation Forest"),
    ("KRaft", "Kafka Raft, modaliteti i Apache Kafka-s pa ZooKeeper"),
    ("LR", "Logistic Regression, Regresioni Logjistik"),
    ("OCSVM", "One-Class SVM, makinë me vektorë mbështetës njëklasëshe"),
    ("p50 / p95 / p99", "Percentili i 50-të, 95-të dhe 99-të i një shpërndarjeje"),
    ("PCA", "Principal Component Analysis, analiza e komponentëve kryesorë"),
    ("PR", "Precision-Recall"),
    ("PSI", "Population Stability Index, indeksi i stabilitetit të popullatës"),
    ("RBF", "Radial Basis Function, kerneli gausian i përdorur nga One-Class SVM"),
    ("ROC", "Receiver Operating Characteristic"),
    (
        "Rolling-origin",
        "Protokoll vlerësimi ku modeli trajnohet mbi të kaluarën dhe testohet mbi bllokun që vjen "
        "pas, në disa pika prerjeje të njëpasnjëshme",
    ),
    ("Throughput", "Numri i mesazheve të përpunuara për sekondë"),
    ("TPE", "Tree-structured Parzen Estimator, mostruesi i përdorur nga Optuna"),
    ("ULB", "Université Libre de Bruxelles"),
    (
        "unsupervised",
        "Mësim pa etiketa gjatë trajnimit; termi ruhet në anglisht sepse përdoret ashtu edhe në "
        "titullin e temës",
    ),
]


# The contents opens with these three, as the template's example shows.
FRONT_ENTRIES = ("LISTA E FIGURAVE", "LISTA E TABELAVE", "FJALORI I TERMAVE")


def contents_entries(outline, figures, tables):
    """Every line that appears in the contents, figure list and table list,
    in the order the reader meets them."""
    return [text for _, text in outline] + figures + tables


def _title(doc, text: str, *, space_before: int = 0):
    """A front-matter title. The template asks every title for Times New Roman
    14, bold capitals, aligned left, so these are set like chapter titles."""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = para.paragraph_format
    pf.line_spacing = 1.5
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(12)
    pf.keep_with_next = True
    run = para.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    return para


def render_prelims(doc, outline, figures, tables, page_map) -> None:
    """Everything between the title pages and chapter 1.

    `page_map` carries printed page numbers recovered from a first rendering
    pass. They become the cached results of the page-number fields; on the
    first pass the fields are empty, and the front matter still has its final
    length, so the numbers found in the second pass remain valid.
    """
    start_new_section(doc, "upperRoman", start=1)

    _title(doc, "ABSTRAKT")
    for para in ABSTRAKT:
        add_paragraph(doc, para)
    page_break(doc)

    _title(doc, "ABSTRACT")
    for para in ABSTRACT_EN:
        add_paragraph(doc, para)
    page_break(doc)

    _title(doc, "MIRËNJOHJE")
    for para in MIRENJOHJE:
        add_paragraph(doc, para)
    page_break(doc)

    _title(doc, "PËRMBAJTJA")
    # These three are numbered in Roman numerals, which LibreOffice does not
    # apply to a page reference, so their numbers are written out. They depend
    # only on the front matter, which breaks pages at fixed places.
    for title in FRONT_ENTRIES:
        add_toc_entry(doc, title, 1, page_map.get(title))
    # The outline already carries the references entry in its correct place
    # between chapters 6 and 8, so nothing is appended here. Chapter entries
    # are in capitals, like the chapter titles they point to.
    for level, text in outline:
        number, _, name = text.partition("\t")
        label = f"{number}\t{name.upper()}" if level == 1 else text
        add_toc_entry(doc, label, level, page_map.get(text), bookmark=heading_bookmark(number))
    page_break(doc)

    _title(doc, "LISTA E FIGURAVE")
    for number, caption in enumerate(figures, start=1):
        add_toc_entry(
            doc,
            _shorten(caption),
            1,
            page_map.get(caption),
            bold=False,
            bookmark=figure_bookmark(number),
        )

    # The template has the table list follow the figure list directly, not on
    # a new page.
    _title(doc, "LISTA E TABELAVE", space_before=18)
    for number, caption in enumerate(tables, start=1):
        add_toc_entry(
            doc,
            _shorten(caption),
            1,
            page_map.get(caption),
            bold=False,
            bookmark=table_bookmark(number),
        )
    page_break(doc)

    _title(doc, "FJALORI I TERMAVE")
    for term, meaning in FJALORI:
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        para.paragraph_format.line_spacing = 1.5
        para.paragraph_format.space_after = Pt(2)
        run = para.add_run(f"{term} – ")
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run2 = para.add_run(meaning)
        run2.font.name = "Times New Roman"
        run2.font.size = Pt(12)


def _shorten(caption: str, limit: int = 110) -> str:
    """The list of figures carries the first sentence of each caption, the
    part that names the figure; reading notes after it stay with the figure."""
    number, _, text = caption.partition(". ")
    first = text.split(". ")[0].rstrip(".")
    entry = f"{number}. {first}."
    if len(entry) <= limit:
        return entry
    cut = entry[:limit].rsplit(" ", 1)[0]
    return cut + "…"

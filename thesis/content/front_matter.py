"""Cover pages, abstracts, acknowledgements, contents and glossary.

The layout follows the faculty template literally: two title pages set in
Times New Roman 14 with the template's spacing, an abstract confined to a
single page and carrying no chapter number, page numbering that starts there
in Roman numerals, and a contents page that opens with the figure list, the
table list and the glossary. The contents and the two lists are Word's own
automatic tables, so Word updates them and a Ctrl+click on an entry goes to
the page it names.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Pt
from docx_helpers import (
    CONTENTS_FIELD,
    FIGURE_LIST_FIELD,
    TABLE_LIST_FIELD,
    add_automatic_table,
    add_heading,
    add_logo,
    add_paragraph,
    figure_bookmark,
    heading_bookmark,
    keep_numbers_whole,
    page_break,
    split_caption,
    start_new_section,
    table_bookmark,
    title_bookmark,
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
    "Zbulimi i mashtrimeve me karta krediti kërkon vendime brenda milisekondash, ndërsa etiketat "
    "e verifikuara vijnë me vonesë ditësh ose javësh. Ky punim dizajnon, implementon dhe "
    "vlerëson një sistem end-to-end për zbulimin e anomalive mbi një rrjedhë të simuluar "
    "transaksionesh, i cili lidh Apache Kafka-n me tri algoritme unsupervised (Isolation Forest, "
    "Autoencoder dhe One-Class SVM) dhe me Regresionin Logjistik si referencë supervised. "
    "Vlerësimi bëhet mbi dataset-in publik të ULB-së (284 807 transaksione, 492 mashtrime) me "
    "protokoll rolling-origin 8-fold pa rrjedhje informacioni dhe me Average Precision (AP) si "
    "metrikë kryesore.",
    "Vonesa end-to-end mbetet shumë nën objektivin prej një sekonde: percentili 99 nuk e kalon "
    "132 milisekonda deri në 2000 mesazhe në sekondë. Në konfigurimin bazë Autoencoder-i ofron "
    "balancën më të mirë mes cilësisë dhe kostos, me AP 0.193 dhe koston më të ulët të "
    "inferencës, para One-Class SVM-së (0.150) dhe Isolation Forest-it (0.091), ndërsa referenca "
    "supervised arrin 0.734. Asnjë ansambël nuk e kalon modelin më të mirë individual, sepse "
    "detektorët gabojnë njësoj: me 100 alarme për bllok, 37% e mashtrimeve nuk i arrin asnjë "
    "prej tyre.",
    "Konfigurimi peshon më shumë se algoritmi: me konfigurimin më të mirë për secilin, raporti "
    "mes detektorit më të mirë dhe më të dobët bie nga 2.1 në 1.15, dhe One-Class SVM me "
    "transformim kuantil kalon në krye (AP 0.368). Ndarja e rastësishme, e zakonshme në "
    "literaturë, e fryn AP-në e metodave unsupervised rreth tri herë. Një prag adaptiv me "
    "dritare rrëshqitëse e bën ngarkesën e hetimeve më të qëndrueshme dhe rrit F1 për detektorët "
    "unsupervised.",
    "Përfundimi kryesor është se infrastruktura streaming nuk është pengesa: cilësia varet më "
    "shumë nga konfigurimi dhe nga etiketat historike sesa nga algoritmi, prandaj metodat "
    "unsupervised vlejnë si shtresë plotësuese për periudhën pa etiketa.",
]

MIRENJOHJE = [
    "Në radhë të parë, falënderimi i takon Allahut të Madhërishëm dhe të Gjithëdijshëm, për "
    "forcën, durimin dhe të gjitha begatitë e dhuruara përgjatë këtij rrugëtimi.",
    "Mirënjohje të thellë ia kushtoj familjes sime, për dashurinë e pakushtëzuar, sakrificat e "
    "heshtura dhe besimin që nuk u lëkund asnjëherë. Përkrahja e tyre ka qenë forca pas çdo "
    "përpjekjeje dhe mbështetja në çdo hap të këtij rrugëtimi. Një falënderim i veçantë u takon "
    "edhe miqve të mi, për praninë, mbështetjen dhe çastet që e bënë këtë rrugëtim më të lehtë e "
    "më të bukur.",
    "Me respekt dhe mirënjohje të veçantë falënderoj mentorin e temës, Dr. sc. Mehmet Shala, për "
    "udhëzimet profesionale, këshillat e vlefshme dhe besimin e treguar gjatë realizimit të këtij "
    "punimi, si dhe për kontributin e çmuar përgjatë viteve të studimeve, përmes ligjërimit, "
    "përkushtimit dhe ndarjes së njohurive.",
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
    ("H1–H3", "Hipotezat e punimit, të formuluara në nënkapitullin 3.5"),
    ("IF", "Isolation Forest"),
    ("KRaft", "Kafka Raft, modaliteti i Apache Kafka-s pa ZooKeeper"),
    ("LR", "Logistic Regression, Regresioni Logjistik"),
    ("msg/s", "Mesazhe në sekondë, njësia e ritmit të mbërritjes dhe e throughput-it"),
    ("OCSVM", "One-Class SVM, makinë me vektorë mbështetës njëklasëshe"),
    ("p50 / p95 / p99", "Percentili i 50-të, 95-të dhe 99-të i një shpërndarjeje"),
    ("PCA", "Principal Component Analysis, analiza e komponentëve kryesorë"),
    ("PH1–PH3", "Pyetjet hulumtuese të punimit, të formuluara në nënkapitullin 1.5"),
    ("PR", "Precision-Recall"),
    ("PSI", "Population Stability Index, indeksi i stabilitetit të popullatës"),
    ("R@100", "Recall me 100 alarme për bllok testimi"),
    ("RBF", "Radial Basis Function, kerneli gausian i përdorur nga One-Class SVM"),
    ("ROC", "Receiver Operating Characteristic"),
    (
        "Rolling-origin",
        "Protokoll vlerësimi ku modeli trajnohet mbi të kaluarën dhe testohet mbi bllokun që vjen "
        "pas, në disa pika prerjeje të njëpasnjëshme",
    ),
    ("s.d.", "Devijimi standard (standard deviation)"),
    ("supervised", "Mësim me etiketa gjatë trajnimit"),
    ("Throughput", "Numri i mesazheve të përpunuara për sekondë"),
    ("TPE", "Tree-structured Parzen Estimator, mostruesi i përdorur nga Optuna"),
    ("ULB", "Université Libre de Bruxelles"),
    ("unsupervised", "Mësim pa etiketa gjatë trajnimit"),
    ("µs/tx", "Mikrosekonda për transaksion, njësia e kostos së inferencës"),
]


# The contents opens with these three, as the template's example shows.
FRONT_ENTRIES = ("LISTA E FIGURAVE", "LISTA E TABELAVE", "FJALORI I TERMAVE")


def contents_entries(outline, figures, tables):
    """Every line that appears in the contents, figure list and table list,
    in the order the reader meets them."""
    return [text for _, text in outline] + figures + tables


def _title(doc, text: str):
    """A front-matter title that the contents leaves out, as the template
    asks for the abstracts and the acknowledgements. The template asks every
    title for Times New Roman 14, bold capitals, aligned left, so these are
    set like chapter titles, but as ordinary paragraphs rather than headings,
    which Word's contents would collect."""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = para.paragraph_format
    pf.line_spacing = 1.5
    pf.space_before = Pt(0)
    pf.space_after = Pt(12)
    pf.keep_with_next = True
    run = para.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    return para


def _listed_title(doc, text: str, *, space_before: int = 0, new_page: bool = False):
    """A front-matter title that the contents lists. It is a Heading 1 with
    no number, which is how the template marks these three and how Word's
    contents finds them, spaced like the other front-matter titles."""
    para = add_heading(doc, text, 1, bookmark=title_bookmark(text))
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after = Pt(12)
    para.paragraph_format.page_break_before = new_page or None
    return para


def _list_entries(captions, bookmark, page_map):
    """The lines of the figure or table list: the label, the number and the
    first sentence of each caption, which is the caption paragraph that Word
    copies when it updates the list."""
    entries = []
    for number, caption in enumerate(captions, start=1):
        label, _, text = caption.partition(". ")
        title, _ = split_caption(text)
        entries.append(
            ("table of figures", f"{label}. {title}", page_map.get(caption), bookmark(number))
        )
    return entries


def render_prelims(doc, outline, figures, tables, page_map, break_before=frozenset()) -> None:
    """Everything between the title pages and chapter 1.

    `page_map` carries printed page numbers recovered from a first rendering
    pass. The automatic tables show them until Word updates the tables; on
    the first pass they are empty, and the front matter still has its final
    length, so the numbers found in the second pass remain valid.
    `break_before` names titles that the first pass left alone at the foot of
    a page; they start the next page instead.
    """
    start_new_section(doc, "upperRoman", start=1)

    _title(doc, "ABSTRAKT")
    for para in ABSTRAKT:
        add_paragraph(doc, keep_numbers_whole(para))
    page_break(doc)

    _title(doc, "MIRËNJOHJE/FALËNDERIME")
    for para in MIRENJOHJE:
        add_paragraph(doc, keep_numbers_whole(para))
    page_break(doc)

    _title(doc, "PËRMBAJTJA")
    # The outline already carries the references entry in its correct place
    # between chapters 6 and 8, so nothing is appended here. Chapter entries
    # are in capitals, like the chapter titles they point to.
    entries = [
        ("toc 1", title, page_map.get(title), title_bookmark(title)) for title in FRONT_ENTRIES
    ]
    for level, text in outline:
        number, _, name = text.partition("\t")
        label = f"{number}\t{name.upper()}" if level == 1 else text
        entries.append((f"toc {level}", label, page_map.get(text), heading_bookmark(number)))
    add_automatic_table(doc, CONTENTS_FIELD, entries).add_run().add_break(WD_BREAK.PAGE)

    _listed_title(doc, "LISTA E FIGURAVE")
    add_automatic_table(doc, FIGURE_LIST_FIELD, _list_entries(figures, figure_bookmark, page_map))

    # The template has the table list follow the figure list directly, not on
    # a new page, unless the figure list fills its page. The paragraph that
    # closes the figure list already leaves a line between them.
    title = "LISTA E TABELAVE"
    _listed_title(doc, title, space_before=6, new_page=title in break_before)
    table_list = add_automatic_table(
        doc, TABLE_LIST_FIELD, _list_entries(tables, table_bookmark, page_map)
    )
    table_list.add_run().add_break(WD_BREAK.PAGE)

    _listed_title(doc, "FJALORI I TERMAVE")
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

"""Cover pages, abstracts, acknowledgements, contents and glossary.

The layout follows the faculty template literally: two title pages, an
abstract confined to a single page and carrying no chapter number, page
numbering that starts here in Roman numerals, and contents / figure / table
lists generated as Word fields so they stay correct after any edit.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx_helpers import (
    add_logo,
    add_page_number_footer,
    add_paragraph,
    add_toc_entry,
    page_break,
    set_page_numbering,
    start_new_section,
)

TITULLI = (
    "ZBULIMI I ANOMALIVE NË RRJEDHA TË SIMULUARA TË TRANSAKSIONEVE FINANCIARE DUKE PËRDORUR APACHE "
    "KAFKA DHE UNSUPERVISED MACHINE LEARNING: STUDIM RASTI ME TRANSAKSIONE TË KARTAVE TË KREDITIT"
)
STUDENTI = "Gentrit Halimi"
MENTORI = "Dr. sc. Mehmet Shala"
PROGRAMI = "Programi për Shkenca Kompjuterike dhe Inxhinieri"
DATA = "Gusht 2026"
VITI_AKADEMIK = "Viti akademik 2024 – 2025"


def _center(doc, text, size=12, bold=False, space_after=6, caps=False):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.line_spacing = 1.5
    para.paragraph_format.space_after = Pt(space_after)
    run = para.add_run(text.upper() if caps else text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    return para


def _blank(doc, n=1):
    for _ in range(n):
        para = doc.add_paragraph()
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.line_spacing = 1.0


def render_cover(doc) -> None:
    """Two title pages; neither carries a page number."""
    section = doc.sections[0]
    section.different_first_page_header_footer = False

    add_logo(doc)
    _center(doc, PROGRAMI, size=13, bold=True)
    _blank(doc, 4)
    _center(doc, TITULLI, size=14, bold=True)
    _blank(doc, 2)
    _center(doc, "Shkalla e Magjistraturës", size=12)
    _blank(doc, 6)
    _center(doc, STUDENTI, size=12, bold=True)
    _blank(doc, 4)
    _center(doc, DATA, size=12)
    _center(doc, "Prishtinë", size=12)
    page_break(doc)

    add_logo(doc)
    _center(doc, PROGRAMI, size=13, bold=True)
    _blank(doc, 1)
    _center(doc, "Punim Diplome", size=12, bold=True)
    _center(doc, VITI_AKADEMIK, size=12)
    _blank(doc, 4)
    _center(doc, STUDENTI, size=12, bold=True)
    _blank(doc, 2)
    _center(doc, TITULLI, size=14, bold=True)
    _blank(doc, 3)
    _center(doc, f"Mentori: {MENTORI}", size=12)
    _blank(doc, 5)
    _center(doc, DATA, size=12)
    _blank(doc, 3)
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.line_spacing = 1.5
    run = para.add_run(
        "Ky punim është përpiluar dhe dorëzuar në përmbushjen e kërkesave të pjesshme për Shkallën "
        "e Magjistraturës"
    )
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.italic = True


ABSTRAKT = [
    "Zbulimi i mashtrimeve me karta krediti bëhet gjithnjë e më shumë mbi rrjedha të vazhdueshme "
    "të dhënash, ku etiketat e verifikuara vijnë me vonesë ditësh ose javësh, ndërsa vendimi duhet "
    "marrë brenda milisekondash. Ky punim dizajnon, implementon dhe vlerëson një sistem end-to-end "
    "për zbulimin e anomalive mbi një rrjedhë të simuluar transaksionesh, i cili lidh Apache "
    "Kafka-n me tri algoritmet unsupervised të projekt-propozimit (Isolation Forest, Autoencoder "
    "dhe One-Class SVM) dhe me Regresionin Logjistik si referencë të mbikëqyrur.",
    "Secili detektor studiohet në thellësi dhe vlerësohet me një protokoll rolling-origin 8-fold, "
    "që rindërton skaluesin, modelet dhe pragjet në çdo fold. Një detektor distancash pa "
    "parametra mat paraprakisht kufirin gjeometrik të problemit: mashtrimet janë mesatarisht 7.9 "
    "herë më larg klasës legjitime se një transaksion tipik legjitim, por distanca jep Average "
    "Precision (AP) prej vetëm 0.30, sepse bishti i klasës legjitime zë të njëjtin rajon. Me 100 "
    "alarme për bllok, 37% e mashtrimeve nuk i arrin asnjë detektor unsupervised, ndërsa "
    "referenca e mbikëqyrur kap 59% të tyre; informacioni ekziston, por jo në formën që e sheh "
    "një detektor distancash.",
    "Paraprocesimi ka efekt më të madh se zgjedhja e algoritmit: transformimi kuantil e rrit AP-në "
    "e One-Class SVM-së mesatarisht me 0.218, me përmirësim në të tetë fold-et, dhe efekti mbetet "
    "kur skaluesi zgjidhet vetëm nga fold-et e mëparshme. Kur secili detektor merr konfigurimin e "
    "tij më të mirë, raporti mes më të mirit dhe më të dobëtit bie nga 2.1 në 1.15. Ndarja e "
    "rastësishme e të dhënave, e zakonshme në literaturë, e rrit AP-në e metodave unsupervised "
    "rreth tri herë.",
    "Percentili 99 i vonesës end-to-end nuk e kalon 132 milisekonda në asnjë ritëm të testuar, "
    "shumë nën objektivin prej një sekonde. Pragu adaptiv me dritare rrëshqitëse e bën ngarkesën e "
    "hetimeve më të qëndrueshme dhe rrit F1 për të tre detektorët unsupervised. Asnjë ansambël nuk "
    "e kalon modelin më të mirë individual, sepse detektorët gabojnë njësoj. Pas korrigjimit për "
    "anshmërinë e mostrave të vogla, zhvendosja e mashtrimeve mbetet më e madhe se ajo e "
    "transaksioneve legjitime.",
]

ABSTRACT_EN = [
    "Credit-card fraud detection increasingly runs on continuous data streams, where verified "
    "labels arrive days or weeks late while decisions must be made within milliseconds. This "
    "thesis designs, implements and evaluates an end-to-end anomaly detection system over a "
    "simulated transaction stream. The system connects Apache Kafka with the three unsupervised "
    "algorithms named in the research proposal (Isolation Forest, Autoencoder and One-Class SVM) "
    "and with Logistic Regression as a supervised reference.",
    "Each detector is studied in depth and evaluated with an 8-fold rolling-origin protocol that "
    "rebuilds the scaler, the models and the thresholds in every fold. A parameter-free distance "
    "detector first measures the geometric ceiling of the problem: frauds lie on average 7.9 times "
    "farther from the legitimate class than a typical legitimate transaction, yet distance yields "
    "an Average Precision (AP) of only 0.30, because the tail of the legitimate class occupies the "
    "same region. With 100 alerts per block, 37% of the frauds are reached by no unsupervised "
    "detector, while the supervised reference catches 59% of them; the information is there, but "
    "not in a form a distance-based detector can see.",
    "Preprocessing matters more than the choice of algorithm: a quantile transform raises the AP "
    "of One-Class SVM by 0.218 on average, improving all eight folds, and the gain holds when the "
    "scaler is chosen from earlier folds only. When each detector receives its best "
    "configuration, the ratio between the best and the weakest falls from 2.1 to 1.15. A shuffled "
    "split, common in the literature, inflates the AP of the unsupervised methods about "
    "threefold.",
    "The 99th-percentile end-to-end latency stays below 132 milliseconds at every arrival rate "
    "tested, far below the one-second target. A sliding-window adaptive threshold makes the "
    "investigation workload steadier and raises F1 for all three unsupervised detectors. No "
    "ensemble beats the best single model, because the detectors make the same mistakes. After "
    "correcting for the small-sample bias of the stability index, the frauds still drift more "
    "than the legitimate transactions.",
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
    ("CD", "Critical Difference, diferenca kritike në testin post-hoc të Nemenyi-t"),
    ("CV", "Coefficient of Variation, koeficienti i variacionit"),
    ("EM", "Excess-Mass, kriter unsupervised për vlerësimin e funksioneve të pikëzimit"),
    ("FN", "False Negative, mashtrim i pazbuluar"),
    (
        "Fold",
        "Një nga pikat e prerjes së protokollit rolling-origin: një dritare trajnimi dhe blloku i "
        "testimit që e pason; 8-fold do të thotë tetë pika të tilla",
    ),
    ("FP", "False Positive, alarm i rremë"),
    ("ID", "Intrinsic Dimension, dimensioni i brendshëm i një bashkësie të dhënash"),
    ("IF", "Isolation Forest"),
    ("KRaft", "Kafka Raft, modaliteti i Apache Kafka-s pa ZooKeeper"),
    ("KS", "Kolmogorov-Smirnov, test dy-mostror i barazisë së shpërndarjeve"),
    ("LR", "Logistic Regression, Regresioni Logjistik"),
    ("MV", "Mass-Volume, kriter unsupervised, plotësues i EM-së"),
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
    ("RSS", "Resident Set Size, memoria rezidente e procesit"),
    ("SHAP", "SHapley Additive exPlanations"),
    ("Throughput", "Numri i mesazheve të përpunuara për sekondë"),
    ("TP", "True Positive, mashtrim i zbuluar saktë"),
    ("TPE", "Tree-structured Parzen Estimator, mostruesi i përdorur nga Optuna"),
    ("TwoNN", "Vlerësues i dimensionit të brendshëm i bazuar në dy fqinjët më të afërt"),
    ("ULB", "Université Libre de Bruxelles"),
    (
        "unsupervised",
        "Mësim pa etiketa gjatë trajnimit; termi ruhet në anglisht sepse përdoret ashtu edhe në "
        "titullin e temës",
    ),
]


def contents_entries(outline, figures, tables):
    """Every line that appears in the contents, figure list and table list,
    in the order the reader meets them."""
    return [text for _, text in outline] + figures + tables


def render_prelims(doc, outline, figures, tables, page_map) -> None:
    """Everything between the title pages and chapter 1.

    `page_map` carries printed page numbers recovered from a first rendering
    pass; on the first pass it is empty and the entries are written without
    numbers, which keeps the front matter at its final length so the numbers
    found in the second pass remain valid.
    """
    section = start_new_section(doc, "upperRoman", start=1)
    set_page_numbering(section, "upperRoman", 1)
    add_page_number_footer(section)

    _center(doc, "ABSTRAKT", size=14, bold=True, space_after=12)
    for para in ABSTRAKT:
        add_paragraph(doc, para)
    page_break(doc)

    _center(doc, "ABSTRACT", size=14, bold=True, space_after=12)
    for para in ABSTRACT_EN:
        add_paragraph(doc, para)
    page_break(doc)

    _center(doc, "MIRËNJOHJE", size=14, bold=True, space_after=12)
    for para in MIRENJOHJE:
        add_paragraph(doc, para)
    page_break(doc)

    _center(doc, "PËRMBAJTJA", size=14, bold=True, space_after=12)
    # The outline already carries the references entry in its correct place
    # between chapters 6 and 8, so nothing is appended here.
    for level, text in outline:
        add_toc_entry(doc, text, level, page_map.get(text))
    page_break(doc)

    _center(doc, "LISTA E FIGURAVE", size=14, bold=True, space_after=12)
    for caption in figures:
        add_toc_entry(doc, _shorten(caption), 1, page_map.get(caption), bold=False)
    page_break(doc)

    _center(doc, "LISTA E TABELAVE", size=14, bold=True, space_after=12)
    for caption in tables:
        add_toc_entry(doc, _shorten(caption), 1, page_map.get(caption), bold=False)
    page_break(doc)

    _center(doc, "FJALORI I TERMAVE", size=14, bold=True, space_after=12)
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

"""Cover pages, abstracts, acknowledgements, contents and glossary.

The layout follows the faculty template literally: two title pages, an
abstract confined to a single page and carrying no chapter number, page
numbering that starts here in Roman numerals, and contents / figure / table
lists generated as Word fields so they stay correct after any edit.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx_helpers import (
    add_page_number_footer,
    add_paragraph,
    add_toc_entry,
    page_break,
    set_page_numbering,
    start_new_section,
)

TITULLI = (
    "ZBULIMI I ANOMALIVE NË RRJEDHA TË SIMULUARA TË TRANSAKSIONEVE "
    "FINANCIARE DUKE PËRDORUR APACHE KAFKA DHE UNSUPERVISED MACHINE "
    "LEARNING: STUDIM RASTI ME TRANSAKSIONE TË KARTAVE TË KREDITIT"
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

    _center(doc, PROGRAMI, size=13, bold=True)
    _blank(doc, 5)
    _center(doc, TITULLI, size=14, bold=True)
    _blank(doc, 2)
    _center(doc, "Shkalla e Magjistraturës", size=12)
    _blank(doc, 6)
    _center(doc, STUDENTI, size=12, bold=True)
    _blank(doc, 4)
    _center(doc, DATA, size=12)
    _center(doc, "Prishtinë", size=12)
    page_break(doc)

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
        "Ky punim është përpiluar dhe dorëzuar në përmbushjen e kërkesave "
        "të pjesshme për Shkallën e Magjistraturës"
    )
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.italic = True


ABSTRAKT = [
    "Zbulimi i mashtrimeve me karta krediti kryhet gjithnjë e më shumë mbi "
    "rrjedha të vazhdueshme të dhënash, ku etiketat e verifikuara mbërrijnë "
    "me vonesë ditësh ose javësh dhe ku vendimi duhet marrë brenda "
    "milisekondash. Ky punim dizajnon, implementon dhe vlerëson "
    "eksperimentalisht një sistem end-to-end për zbulimin e anomalive mbi një "
    "rrjedhë të simuluar transaksionesh financiare, duke integruar Apache "
    "Kafka në modalitetin KRaft me tri algoritmet unsupervised të "
    "projekt-propozimit, Isolation Forest, Autoencoder dhe One-Class SVM, si "
    "dhe me një referencë të mbikëqyrur me Regresion Logjistik.",
    "Studimi zgjedh thellësinë në vend të gjerësisë. Në vend që të shtohen "
    "algoritme të tjera, secili prej tri detektorëve i nënshtrohet një studimi "
    "të veçantë të ndërtuar rreth mekanizmit të tij, dhe i gjithë vlerësimi "
    "kryhet me protokoll rolling-origin në tetë pika kohore prerjeje, ku çdo "
    "fold rindërton nga fillimi skalimin, modelet dhe pragjet. Përpara çdo "
    "modelimi matet kufiri i sipërm gjeometrik i vetë problemit me një "
    "detektor pa parametra.",
    "Ai kufi rezulton vendimtar për interpretimin. Mashtrimet ndodhen "
    "mesatarisht 7.9 herë më larg klasës legjitime sesa një transaksion tipik "
    "legjitim, por vetëm distanca jep Average Precision 0.30, sepse bishti i "
    "vetë klasës legjitime e mbush të njëjtin rajon; mashtrimi median kërkon "
    "shqyrtimin e rreth 530 alarmeve. Në nivel transaksioni, 37 për qind e "
    "mashtrimeve nuk arrihen nga asnjë detektor unsupervised brenda një "
    "buxheti prej njëqind alarmesh, ndërsa referenca e mbikëqyrur i kap 59 për "
    "qind të tyre, çka tregon se informacioni ekziston në të dhëna por nuk "
    "është i formës që një detektor distancash e sheh.",
    "Dy gjetje metodologjike e ndryshojnë mënyrën si duhen lexuar renditjet e "
    "publikuara. Zgjedhja e paraprocesimit ka ndikim më të madh se zgjedhja e "
    "algoritmit: transformimi kuantil e ngre One-Class SVM-në me 0.218 njësi "
    "AP në të tetë fold-et, ndërsa referencën e mbikëqyrur nuk e prek fare. "
    "Ndarja e rastësishme e të dhënave, praktikë e zakonshme në literaturë, e "
    "fryn Average Precision e metodave unsupervised rreth 3.0 herë. Përgjigjja "
    "për pyetjen se cili algoritëm është më i miri është pra e kushtëzuar nga "
    "protokolli, jo veti e pandryshueshme e algoritmit.",
    "Nga ana operacionale sistemi arrin vonesë end-to-end dukshëm nën "
    "objektivin prej një sekonde në të gjitha ritmet e testuara, dhe pragu "
    "adaptiv me dritare rrëshqitëse, i propozuar këtu, e stabilizon ngarkesën "
    "hetimore dhe e përmirëson cilësinë e zbulimit për të tre detektorët "
    "unsupervised. Qasja ensemble "
    "nuk e tejkalon modelin më të mirë individual, dhe analiza e gabimeve në "
    "nivel transaksioni e shpjegon pse. Analiza e zhvendosjes tregon se "
    "degradimi nuk vjen nga vjetërimi i modelit të normalitetit, por nga "
    "ndryshimi i vetë popullatës së mashtrimeve, dallim me pasoja praktike të "
    "kundërta.",
]

ABSTRACT_EN = [
    "Credit-card fraud detection increasingly happens on continuous data "
    "streams, where verified labels arrive days or weeks late and the "
    "decision itself must be made in milliseconds. This thesis designs, "
    "implements and experimentally evaluates an end-to-end anomaly detection "
    "system over a simulated stream of financial transactions, integrating "
    "Apache Kafka in KRaft mode with the three unsupervised algorithms named "
    "in the research proposal, Isolation Forest, Autoencoder and One-Class "
    "SVM, together with a supervised Logistic Regression reference.",
    "The study buys depth rather than breadth. Instead of adding further "
    "algorithms, each of the three detectors receives a dedicated study built "
    "around its own mechanism, and the whole evaluation runs under a "
    "rolling-origin protocol at eight successive cut points in which every "
    "fold rebuilds the scaler, the models and the thresholds from scratch. "
    "Before any model is fitted, the geometric ceiling of the problem itself "
    "is measured with a parameter-free detector.",
    "That ceiling turns out to govern the interpretation. Frauds sit on "
    "average 7.9 times farther from the legitimate class than a typical "
    "legitimate transaction, yet distance alone yields an Average Precision "
    "of 0.30, because the tail of the legitimate class fills the same region; "
    "the median fraud costs roughly 530 alerts to reach. At the transaction "
    "level, 37 per cent of frauds are found by no unsupervised detector "
    "within a budget of one hundred alerts, while the supervised reference "
    "recovers 59 per cent of them, showing that the information is present in "
    "the data but not in a form a distance-based detector can see.",
    "Two methodological findings change how published rankings should be "
    "read. The preprocessing choice matters more than the choice of "
    "algorithm: a quantile transform lifts One-Class SVM by 0.218 AP in all "
    "eight folds, while leaving the supervised reference untouched. A "
    "shuffled split, common in the literature, inflates the Average Precision "
    "of the unsupervised methods by roughly a factor of 3.0. Which algorithm "
    "is best is therefore conditional on the protocol rather than a fixed "
    "property of the algorithm.",
    "Operationally the system stays far below the one-second latency target "
    "at every arrival rate tested, and the sliding-window adaptive threshold "
    "proposed here stabilises the investigation workload and improves "
    "detection quality for all three unsupervised detectors. No ensemble "
    "variant beats the best single model, "
    "and the per-transaction error analysis explains why. Drift analysis "
    "shows that degradation comes not from a stale model of normality but "
    "from a change in the fraud population itself, a distinction with "
    "opposite practical consequences.",
]

MIRENJOHJE = [
    "Falënderime i shkojnë mentorit, Dr. sc. Mehmet Shala, për udhëzimet e "
    "sakta dhe për lirinë e dhënë që kjo temë të ndiqej në thellësi, "
    "veçanërisht atëherë kur rezultatet e para nuk përkonin me pritshmëritë "
    "fillestare.",
    "Falënderime i shkojnë gjithashtu stafit akademik të Programit për "
    "Shkenca Kompjuterike dhe Inxhinieri në UBT, në veçanti për lëndët "
    "Advanced Machine Learning dhe Deep Learning, të cilat e formuan mënyrën "
    "si kuptohet sot vlerësimi eksperimental: jo si hap final verifikimi, por "
    "si pjesa më e rëndësishme e vetë kërkimit.",
    "Një falënderim i veçantë i takon grupit Machine Learning të Université "
    "Libre de Bruxelles për publikimin e dataset-it që e bëri të mundur këtë "
    "studim, si dhe komunitetit të softuerit të lirë, pa punën e të cilit një "
    "infrastrukturë e tillë nuk do të ishte e arritshme brenda kornizës së "
    "një punimi diplome.",
    "Së fundi, falënderime i shkojnë familjes për durimin gjatë muajve kur "
    "kjo punë zuri pjesën më të madhe të kohës.",
]

FJALORI = [
    (
        "AP",
        "Average Precision, sipërfaqja nën kurbën precision-recall; metrika "
        "kryesore e këtij punimi",
    ),
    ("AE", "Autoencoder, rrjet nervor që mëson të rindërtojë hyrjen e vet"),
    ("AUC", "Area Under the Curve, sipërfaqja nën kurbë"),
    ("CD", "Critical Difference, diferenca kritike në testin post-hoc të Nemenyi-t"),
    ("CV", "Coefficient of Variation, koeficienti i variacionit"),
    ("EM", "Excess-Mass, kriter unsupervised për vlerësimin e funksioneve të pikëzimit"),
    ("FN", "False Negative, mashtrim i pazbuluar"),
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
    ("RSS", "Resident Set Size, memoria rezidente e procesit"),
    ("SHAP", "SHapley Additive exPlanations"),
    ("TP", "True Positive, mashtrim i zbuluar saktë"),
    ("TPE", "Tree-structured Parzen Estimator, mostruesi i përdorur nga Optuna"),
    ("TwoNN", "Vlerësues i dimensionit të brendshëm i bazuar në dy fqinjët më të afërt"),
    ("ULB", "Université Libre de Bruxelles"),
    (
        "unsupervised",
        "Mësim pa etiketa gjatë trajnimit; termi ruhet në anglisht sepse "
        "përdoret ashtu edhe në titullin e temës",
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
        add_toc_entry(doc, _shorten(caption), 1, page_map.get(caption))
    _center(doc, "LISTA E TABELAVE", size=14, bold=True, space_after=12)
    for caption in tables:
        add_toc_entry(doc, _shorten(caption), 1, page_map.get(caption))
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


def _shorten(caption: str, limit: int = 95) -> str:
    """Figure and table captions are full sentences; the lists need the
    identifying head of each, not the whole explanation."""
    if len(caption) <= limit:
        return caption
    cut = caption[:limit].rsplit(" ", 1)[0]
    return cut + "…"

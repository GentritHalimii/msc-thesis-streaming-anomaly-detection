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
    "eksperimentalisht një sistem të plotë end-to-end për zbulimin e "
    "anomalive mbi një rrjedhë të simuluar transaksionesh financiare, duke "
    "integruar Apache Kafka në modalitetin KRaft me katërmbëdhjetë detektorë "
    "të pambikëqyrur nga gjashtë familje algoritmike dhe me një referencë të "
    "mbikëqyrur me Regresion Logjistik.",
    "Kontributi metodologjik qendror është protokolli i vlerësimit. Në vend "
    "të një ndarjeje të vetme kronologjike 70/30, sistemi vlerësohet me tetë "
    "pika kohore prerjeje sipas skemës rolling-origin, ku çdo fold rikthen "
    "nga fillimi të gjithë disiplinën kundër rrjedhjes së informacionit: "
    "skalimin e vet, modelet e veta dhe pragjet e veta të nxjerra vetëm nga "
    "shpërndarja e pikëve në dritaren e trajnimit. Rezultati metodologjik "
    "është më i nuancuar nga sa pritej: renditja e detektorëve mbetet "
    "kryesisht e njëjtë mes një ndarjeje të vetme dhe tetë folds-ave "
    "(korrelacion i rangjeve 0.95), por shpërhapja e vlerësimeve nëpër folds "
    "është rreth 117 për qind e vlerës mesatare, pra e njëjtë në madhësi me "
    "efektin që matet — një pasiguri që një ndarje e vetme nuk mund ta "
    "zbulojë. Ndarja e rastësishme, ndërkohë, e fryn precizionin mesatar të "
    "metodave të pambikëqyrura mesatarisht 2.7 herë, ndërsa referencën e "
    "mbikëqyrur nuk e ndihmon fare.",
    "Rezultatet empirike tregojnë se Deep SVDD ofron balancën më të mirë "
    "ndërmjet cilësisë së zbulimit dhe kostos operacionale midis metodave të "
    "pambikëqyrura, ndërsa Isolation Forest — një nga dy algoritmet qendrore "
    "të propozimit fillestar — renditet i parafundit nga pesëmbëdhjetë. "
    "Analiza e interpretueshmërisë e shpjegon këtë mekanikisht: përputhja e "
    "vëmendjes së modelit me sinjalin realisht diskriminues parashikon "
    "renditjen e cilësisë së zbulimit. Referenca e mbikëqyrur mbetet "
    "dukshëm më lart, gjë që kuantifikon vlerën e etiketave. Qasja ensemble "
    "nuk e tejkalon modelin më të mirë individual në asnjë variant të "
    "testuar, dhe punimi e raporton këtë si gjetje negative të vlefshme, së "
    "bashku me shpjegimin e saj: anëtarët janë të korreluar dhe u mungon "
    "diversiteti i nevojshëm.",
    "Nga ana operacionale, sistemi arrin vonesë fund-më-fund dukshëm nën "
    "objektivin prej një sekonde në të gjitha ritmet e testuara të mbërritjes "
    "sintetike, dhe pragu adaptiv me dritare rrëshqitëse, i propozuar këtu, "
    "përmirëson njëkohësisht stabilitetin e ngarkesës hetimore dhe cilësinë e "
    "zbulimit. Analiza e zhvendosjes tregon se degradimi nuk vjen nga "
    "vjetërimi i modelit të normalitetit, por nga ndryshimi i vetë popullatës "
    "së mashtrimeve — një dallim me pasoja të drejtpërdrejta praktike, sepse "
    "i pari zgjidhet me ritrajnim ndërsa i dyti jo.",
]

ABSTRACT_EN = [
    "Credit-card fraud detection increasingly happens on continuous data "
    "streams, where verified labels arrive days or weeks late and the "
    "decision itself must be made in milliseconds. This thesis designs, "
    "implements and experimentally evaluates a complete end-to-end anomaly "
    "detection system over a simulated stream of financial transactions, "
    "integrating Apache Kafka in KRaft mode with fourteen unsupervised "
    "detectors drawn from six algorithmic families and a supervised Logistic "
    "Regression reference.",
    "The central methodological contribution is the evaluation protocol. "
    "Instead of a single chronological 70/30 split, the system is evaluated "
    "at eight successive cut points under a rolling-origin scheme in which "
    "every fold re-establishes the full anti-leakage discipline from scratch: "
    "its own scaler, its own models and its own thresholds derived solely "
    "from the training-score distribution. The methodological finding is more "
    "nuanced than expected: the ranking of detectors is largely preserved "
    "between a single split and eight folds (rank correlation 0.95), but the "
    "spread of estimates across folds is about 117 per cent of the mean "
    "value — as large as the effect being measured — an uncertainty a single "
    "split cannot reveal. A shuffled split, meanwhile, inflates the average "
    "precision of the unsupervised methods by a factor of 2.7 on average "
    "while giving the supervised reference no help at all.",
    "Empirically, Deep SVDD offers the best trade-off between detection "
    "quality and operational cost among the unsupervised methods, while "
    "Isolation Forest — one of the two algorithms at the centre of the "
    "original proposal — ranks fourteenth of fifteen. An interpretability "
    "analysis explains this mechanically: how well a model's attention aligns "
    "with the genuinely discriminative signal predicts its detection ranking. "
    "The supervised reference remains far ahead, quantifying the value of "
    "labels. No ensemble variant outperforms the best single model, and this "
    "negative result is reported together with its explanation: the members "
    "are correlated and lack the diversity that averaging requires.",
    "Operationally, the system achieves end-to-end latency far below the "
    "one-second target at every synthetic arrival rate tested, and the "
    "sliding-window adaptive threshold proposed here improves both the "
    "stability of the investigation workload and detection quality. Drift "
    "analysis shows that degradation does not come from a stale model of "
    "normality but from a change in the fraud population itself — a "
    "distinction with direct practical consequences, since the former is "
    "fixed by retraining and the latter is not.",
]

MIRENJOHJE = [
    "Falënderoj mentorin tim, Dr. sc. Mehmet Shala, për udhëzimet e sakta dhe "
    "për lirinë që më dha ta ndjek këtë temë në thellësi, veçanërisht atëherë "
    "kur rezultatet e para nuk përkonin me pritshmëritë e mia fillestare.",
    "Falënderoj stafin akademik të Programit për Shkenca Kompjuterike dhe "
    "Inxhinieri në UBT, në veçanti për lëndët Advanced Machine Learning dhe "
    "Deep Learning, të cilat formuan mënyrën si e kuptoj sot vlerësimin "
    "eksperimental: jo si një hap final verifikimi, por si pjesa më e "
    "rëndësishme e vetë kërkimit.",
    "Falënderoj grupin Machine Learning të Université Libre de Bruxelles për "
    "publikimin e dataset-it që bëri të mundur këtë studim, si dhe "
    "komunitetin e softuerit të lirë, pa punën e të cilit një infrastrukturë "
    "e tillë nuk do të ishte e arritshme brenda kornizës së një punimi "
    "diplome.",
    "Së fundi, falënderoj familjen time për durimin gjatë muajve kur kjo punë "
    "zuri pjesën më të madhe të kohës sime.",
]

FJALORI = [
    (
        "AP",
        "Average Precision (Precizioni Mesatar) — sipërfaqja nën kurbën "
        "precision–recall; metrika kryesore e këtij punimi",
    ),
    ("ADWIN", "Adaptive Windowing — algoritëm për zbulimin e zhvendosjes së konceptit"),
    ("AE", "Autoencoder — rrjet nervor që mëson të rindërtojë hyrjen e vet"),
    ("AUC", "Area Under the Curve — sipërfaqja nën kurbë"),
    ("CD", "Critical Difference — diferenca kritike në testin post-hoc të Nemenyi-t"),
    ("COPOD", "Copula-Based Outlier Detection"),
    ("CV", "Coefficient of Variation — koeficienti i variacionit"),
    ("Deep SVDD", "Deep Support Vector Data Description"),
    ("ECOD", "Empirical Cumulative Distribution Functions Outlier Detection"),
    ("EM", "Excess-Mass — kriter i pambikëqyrur për vlerësimin e funksioneve të pikëzimit"),
    ("FN", "False Negative — mashtrim i pazbuluar"),
    ("FP", "False Positive — alarm i rremë"),
    ("GMM", "Gaussian Mixture Model — model përzierjeje gausiane"),
    ("HBOS", "Histogram-Based Outlier Score"),
    ("IF", "Isolation Forest"),
    ("KRaft", "Kafka Raft — modaliteti i Apache Kafka-s pa ZooKeeper"),
    ("KS", "Kolmogorov–Smirnov — test dy-mostror i barazisë së shpërndarjeve"),
    ("kNN", "k-Nearest Neighbours — k fqinjët më të afërt"),
    ("LODA", "Lightweight On-line Detector of Anomalies"),
    ("LOF", "Local Outlier Factor"),
    ("LR", "Logistic Regression — Regresioni Logjistik"),
    ("MCD", "Minimum Covariance Determinant — vlerësues robust i kovariancës"),
    ("MV", "Mass-Volume — kriter i pambikëqyrur, plotësues i EM-së"),
    ("OCSVM", "One-Class SVM — makinë me vektorë mbështetës njëklasëshe"),
    ("p50 / p95 / p99", "Percentili i 50-të, 95-të dhe 99-të i një shpërndarjeje"),
    ("PCA", "Principal Component Analysis — analiza e komponentëve kryesorë"),
    ("PR", "Precision–Recall"),
    ("PSI", "Population Stability Index — indeksi i stabilitetit të popullatës"),
    ("RQ", "Research Question — pyetje hulumtuese"),
    ("ROC", "Receiver Operating Characteristic"),
    ("RSS", "Resident Set Size — memoria rezidente e procesit"),
    ("SHAP", "SHapley Additive exPlanations"),
    ("TP", "True Positive — mashtrim i zbuluar saktë"),
    ("VAE", "Variational Autoencoder — autoenkoder variacional"),
    ("ULB", "Université Libre de Bruxelles"),
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
    for level, text in outline:
        add_toc_entry(doc, text, level, page_map.get(text))
    add_toc_entry(doc, "7\tREFERENCAT", 1, page_map.get("7\tREFERENCAT"))
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

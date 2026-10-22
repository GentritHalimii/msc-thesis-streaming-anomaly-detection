"""IEEE reference database, keyed for automatic in-text numbering.

Entries are cited in the text as [@key]. Each entry is a source with the
fields Word keeps in its own source list, because that is where the
document stores it: the builder writes the sources into the file, every
citation as Word's CITATION field and the reference list as its
BIBLIOGRAPHY field, so Word's References tab manages them (Insert Citation,
Manage Sources, Update Citations and Bibliography). Numbers follow the order
of first citation, as IEEE requires. Anything left uncited is dropped from
the reference list rather than padding it — an uncited work belongs in a
bibliography, not in the references.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """One work, with the fields Word's source list uses for its type."""

    # Word's source type: JournalArticle, ConferenceProceedings, Book,
    # Report or InternetSite.
    kind: str
    # Names as printed, "F. T. Liu"; one organisation when `corporate` is set.
    authors: tuple[str, ...]
    title: str
    year: int
    # The journal, the proceedings or the web site the work appeared in.
    container: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    # An article number, for a journal that numbers articles, not pages.
    article: str = ""
    edition: str = ""
    city: str = ""
    publisher: str = ""
    month: int = 0
    url: str = ""
    # The date the online source was consulted, as (year, month, day).
    accessed: tuple[int, int, int] | None = None
    corporate: bool = False


def _names(authors: str) -> tuple[str, ...]:
    return tuple(name.strip() for name in authors.split(","))


def article(authors, title, journal, year, *, volume, issue="", pages="", number=""):
    return Source(
        "JournalArticle",
        _names(authors),
        title,
        year,
        container=journal,
        volume=str(volume),
        issue=str(issue),
        pages=pages,
        article=number,
    )


def proceedings(authors, title, conference, city, year, *, pages="", volume=""):
    return Source(
        "ConferenceProceedings",
        _names(authors),
        title,
        year,
        container=conference,
        city=city,
        pages=pages,
        volume=str(volume),
    )


def book(authors, title, city, publisher, year, *, edition="", url="", accessed=None):
    return Source(
        "Book",
        _names(authors),
        title,
        year,
        city=city,
        publisher=publisher,
        edition=edition,
        url=url,
        accessed=accessed,
    )


def report(author, title, publisher, city, year, month, *, url, accessed):
    return Source(
        "Report",
        (author,),
        title,
        year,
        city=city,
        publisher=publisher,
        month=month,
        url=url,
        accessed=accessed,
        corporate=True,
    )


def website(author, title, site, year, *, url, accessed):
    return Source(
        "InternetSite",
        (author,),
        title,
        year,
        container=site,
        url=url,
        accessed=accessed,
        corporate=True,
    )


# The date every online source below was last consulted.
CONSULTED = (2026, 9, 13)

REFERENCES: dict[str, Source] = {
    # --- anomaly detection: foundations and surveys ----------------------
    "hawkins1980": book(
        "D. M. Hawkins", "Identification of Outliers", "London, U.K.", "Chapman and Hall", 1980
    ),
    "chandola2009": article(
        "V. Chandola, A. Banerjee, V. Kumar",
        "Anomaly detection: A survey",
        "ACM Computing Surveys",
        2009,
        volume=41,
        issue=3,
        pages="1–58",
    ),
    "aggarwal2017": book(
        "C. C. Aggarwal",
        "Outlier Analysis",
        "Cham, Switzerland",
        "Springer",
        2017,
        edition="2nd",
    ),
    "ruff2021": article(
        "L. Ruff, J. R. Kauffmann, R. A. Vandermeulen, G. Montavon, W. Samek, M. Kloft, "
        "T. G. Dietterich, K.-R. Müller",
        "A unifying review of deep and shallow anomaly detection",
        "Proceedings of the IEEE",
        2021,
        volume=109,
        issue=5,
        pages="756–795",
    ),
    "pang2021": article(
        "G. Pang, C. Shen, L. Cao, A. van den Hengel",
        "Deep learning for anomaly detection: A review",
        "ACM Computing Surveys",
        2021,
        volume=54,
        issue=2,
        number="38",
    ),
    # --- individual detectors --------------------------------------------
    "liu2008": proceedings(
        "F. T. Liu, K. M. Ting, Z.-H. Zhou",
        "Isolation forest",
        "Proc. 8th IEEE Int. Conf. Data Mining (ICDM)",
        "Pisa, Italy",
        2008,
        pages="413–422",
    ),
    "liu2012": article(
        "F. T. Liu, K. M. Ting, Z.-H. Zhou",
        "Isolation-based anomaly detection",
        "ACM Trans. Knowledge Discovery from Data",
        2012,
        volume=6,
        issue=1,
        pages="1–39",
    ),
    "scholkopf2001": article(
        "B. Schölkopf, J. C. Platt, J. Shawe-Taylor, A. J. Smola, R. C. Williamson",
        "Estimating the support of a high-dimensional distribution",
        "Neural Computation",
        2001,
        volume=13,
        issue=7,
        pages="1443–1471",
    ),
    "tax2004": article(
        "D. M. J. Tax, R. P. W. Duin",
        "Support vector data description",
        "Machine Learning",
        2004,
        volume=54,
        issue=1,
        pages="45–66",
    ),
    "breunig2000": proceedings(
        "M. M. Breunig, H.-P. Kriegel, R. T. Ng, J. Sander",
        "LOF: Identifying density-based local outliers",
        "Proc. ACM SIGMOD Int. Conf. Management of Data",
        "Dallas, TX, USA",
        2000,
        pages="93–104",
    ),
    "li2022ecod": article(
        "Z. Li, Y. Zhao, X. Hu, N. Botta, C. Ionescu, G. H. Chen",
        "ECOD: Unsupervised outlier detection using empirical cumulative distribution functions",
        "IEEE Trans. Knowledge and Data Engineering",
        2023,
        volume=35,
        issue=12,
        pages="12181–12193",
    ),
    "shyu2003": proceedings(
        "M.-L. Shyu, S.-C. Chen, K. Sarinnapakorn, L. Chang",
        "A novel anomaly detection scheme based on principal component classifier",
        "Proc. IEEE Foundations and New Directions of Data Mining Workshop",
        "Melbourne, FL, USA",
        2003,
        pages="172–179",
    ),
    # --- autoencoders and deep generative models -------------------------
    "hinton2006": article(
        "G. E. Hinton, R. R. Salakhutdinov",
        "Reducing the dimensionality of data with neural networks",
        "Science",
        2006,
        volume=313,
        issue=5786,
        pages="504–507",
    ),
    "sakurada2014": proceedings(
        "M. Sakurada, T. Yairi",
        "Anomaly detection using autoencoders with nonlinear dimensionality reduction",
        "Proc. MLSDA Workshop on Machine Learning for Sensory Data Analysis",
        "Gold Coast, Australia",
        2014,
        pages="4–11",
    ),
    "kingma2014": proceedings(
        "D. P. Kingma, M. Welling",
        "Auto-encoding variational Bayes",
        "Proc. 2nd Int. Conf. Learning Representations (ICLR)",
        "Banff, Canada",
        2014,
    ),
    # --- credit-card fraud detection -------------------------------------
    "dalpozzolo2014": article(
        "A. Dal Pozzolo, O. Caelen, Y.-A. Le Borgne, S. Waterschoot, G. Bontempi",
        "Learned lessons in credit card fraud detection from a practitioner perspective",
        "Expert Systems with Applications",
        2014,
        volume=41,
        issue=10,
        pages="4915–4928",
    ),
    "dalpozzolo2018": article(
        "A. Dal Pozzolo, G. Boracchi, O. Caelen, C. Alippi, G. Bontempi",
        "Credit card fraud detection: A realistic modeling and a novel learning strategy",
        "IEEE Trans. Neural Networks and Learning Systems",
        2018,
        volume=29,
        issue=8,
        pages="3784–3797",
    ),
    "carcillo2018": article(
        "F. Carcillo, A. Dal Pozzolo, Y.-A. Le Borgne, O. Caelen, Y. Mazzer, G. Bontempi",
        "SCARFF: A scalable framework for streaming credit card fraud detection with Spark",
        "Information Fusion",
        2018,
        volume=41,
        pages="182–194",
    ),
    "carcillo2021": article(
        "F. Carcillo, Y.-A. Le Borgne, O. Caelen, Y. Kessaci, F. Oblé, G. Bontempi",
        "Combining unsupervised and supervised learning in credit card fraud detection",
        "Information Sciences",
        2021,
        volume=557,
        pages="317–331",
    ),
    "jurgovsky2018": article(
        "J. Jurgovsky, M. Granitzer, K. Ziegler, S. Calabretto, P.-E. Portier, L. He-Guelton, "
        "O. Caelen",
        "Sequence classification for credit-card fraud detection",
        "Expert Systems with Applications",
        2018,
        volume=100,
        pages="234–245",
    ),
    "whitrow2009": article(
        "C. Whitrow, D. J. Hand, P. Juszczak, D. Weston, N. M. Adams",
        "Transaction aggregation as a strategy for credit card fraud detection",
        "Data Mining and Knowledge Discovery",
        2009,
        volume=18,
        issue=1,
        pages="30–55",
    ),
    "bahnsen2016": article(
        "A. C. Bahnsen, D. Aouada, A. Stojanovic, B. Ottersten",
        "Feature engineering strategies for credit card fraud detection",
        "Expert Systems with Applications",
        2016,
        volume=51,
        pages="134–142",
    ),
    "bhattacharyya2011": article(
        "S. Bhattacharyya, S. Jha, K. Tharakunnel, J. C. Westland",
        "Data mining for credit card fraud: A comparative study",
        "Decision Support Systems",
        2011,
        volume=50,
        issue=3,
        pages="602–613",
    ),
    "leborgne2022": book(
        "Y.-A. Le Borgne, W. Siblini, B. Lebichot, G. Bontempi",
        "Reproducible Machine Learning for Credit Card Fraud Detection – Practical Handbook",
        "Brussels, Belgium",
        "Université Libre de Bruxelles",
        2022,
        url="https://fraud-detection-handbook.github.io/fraud-detection-handbook/",
        accessed=CONSULTED,
    ),
    "ulb_dataset": website(
        "Machine Learning Group – Université Libre de Bruxelles",
        "Credit Card Fraud Detection dataset",
        "Kaggle",
        2018,
        url="https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
        accessed=CONSULTED,
    ),
    "ecb2021": report(
        "European Central Bank",
        "Seventh report on card fraud",
        "European Central Bank",
        "Frankfurt am Main, Germany",
        2021,
        10,
        url="https://www.ecb.europa.eu/pub/pdf/cardfraud/"
        "ecb.cardfraudreport202110~cac4c418e8.en.pdf",
        accessed=CONSULTED,
    ),
    # --- class imbalance and cost ----------------------------------------
    "chawla2002": article(
        "N. V. Chawla, K. W. Bowyer, L. O. Hall, W. P. Kegelmeyer",
        "SMOTE: Synthetic minority over-sampling technique",
        "Journal of Artificial Intelligence Research",
        2002,
        volume=16,
        pages="321–357",
    ),
    # --- evaluation methodology ------------------------------------------
    "davis2006": proceedings(
        "J. Davis, M. Goadrich",
        "The relationship between precision-recall and ROC curves",
        "Proc. 23rd Int. Conf. Machine Learning (ICML)",
        "Pittsburgh, PA, USA",
        2006,
        pages="233–240",
    ),
    "saito2015": article(
        "T. Saito, M. Rehmsmeier",
        "The precision-recall plot is more informative than the ROC plot when evaluating "
        "binary classifiers on imbalanced datasets",
        "PLOS ONE",
        2015,
        volume=10,
        issue=3,
        number="e0118432",
    ),
    "demsar2006": article(
        "J. Demšar",
        "Statistical comparisons of classifiers over multiple data sets",
        "Journal of Machine Learning Research",
        2006,
        volume=7,
        pages="1–30",
    ),
    "gama2013": article(
        "J. Gama, R. Sebastião, P. P. Rodrigues",
        "On evaluating stream learning algorithms",
        "Machine Learning",
        2013,
        volume=90,
        issue=3,
        pages="317–346",
    ),
    "bergmeir2012": article(
        "C. Bergmeir, J. M. Benítez",
        "On the use of cross-validation for time series predictor evaluation",
        "Information Sciences",
        2012,
        volume=191,
        pages="192–213",
    ),
    # --- concept drift ----------------------------------------------------
    "gama2014": article(
        "J. Gama, I. Žliobaitė, A. Bifet, M. Pechenizkiy, A. Bouchachia",
        "A survey on concept drift adaptation",
        "ACM Computing Surveys",
        2014,
        volume=46,
        issue=4,
        pages="1–37",
    ),
    # --- streaming systems ------------------------------------------------
    "kreps2011": proceedings(
        "J. Kreps, N. Narkhede, J. Rao",
        "Kafka: A distributed messaging system for log processing",
        "Proc. 6th Int. Workshop on Networking Meets Databases (NetDB)",
        "Athens, Greece",
        2011,
        pages="1–7",
    ),
    "carbone2015": article(
        "P. Carbone, S. Ewen, S. Haridi, A. Katsifodimos, V. Markl, K. Tzoumas",
        "Apache Flink: Stream and batch processing in a single engine",
        "IEEE Data Engineering Bulletin",
        2015,
        volume=38,
        issue=4,
        pages="28–38",
    ),
    "kleppmann2017": book(
        "M. Kleppmann",
        "Designing Data-Intensive Applications",
        "Sebastopol, CA, USA",
        "O’Reilly Media",
        2017,
    ),
    # --- ensembles ---------------------------------------------------------
    "aggarwal2015": article(
        "C. C. Aggarwal, S. Sathe",
        "Theoretical foundations and algorithms for outlier ensembles",
        "ACM SIGKDD Explorations Newsletter",
        2015,
        volume=17,
        issue=1,
        pages="24–47",
    ),
    "zimek2014": article(
        "A. Zimek, R. J. G. B. Campello, J. Sander",
        "Ensembles for unsupervised outlier detection: challenges and research questions",
        "ACM SIGKDD Explorations Newsletter",
        2014,
        volume=15,
        issue=1,
        pages="11–22",
    ),
    "rayana2016": article(
        "S. Rayana, L. Akoglu",
        "Less is more: Building selective anomaly ensembles",
        "ACM Trans. Knowledge Discovery from Data",
        2016,
        volume=10,
        issue=4,
        pages="1–33",
    ),
    # --- statistics ---------------------------------------------------------
    "wilcoxon1945": article(
        "F. Wilcoxon",
        "Individual comparisons by ranking methods",
        "Biometrics Bulletin",
        1945,
        volume=1,
        issue=6,
        pages="80–83",
    ),
    "holm1979": article(
        "S. Holm",
        "A simple sequentially rejective multiple test procedure",
        "Scandinavian Journal of Statistics",
        1979,
        volume=6,
        issue=2,
        pages="65–70",
    ),
    "efron1993": book(
        "B. Efron, R. J. Tibshirani",
        "An Introduction to the Bootstrap",
        "New York, NY, USA",
        "Chapman and Hall",
        1993,
    ),
    # --- software -----------------------------------------------------------
    "pedregosa2011": article(
        "F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, "
        "P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, "
        "M. Brucher, M. Perrot, É. Duchesnay",
        "Scikit-learn: Machine learning in Python",
        "Journal of Machine Learning Research",
        2011,
        volume=12,
        pages="2825–2830",
    ),
    "paszke2019": proceedings(
        "A. Paszke, S. Gross, F. Massa, A. Lerer, J. Bradbury, G. Chanan, T. Killeen, Z. Lin, "
        "N. Gimelshein, L. Antiga, A. Desmaison, A. Köpf, E. Yang, Z. DeVito, M. Raison, "
        "A. Tejani, S. Chilamkurthy, B. Steiner, L. Fang, J. Bai, S. Chintala",
        "PyTorch: An imperative style, high-performance deep learning library",
        "Advances in Neural Information Processing Systems (NeurIPS)",
        "Vancouver, Canada",
        2019,
        volume=32,
        pages="8024–8035",
    ),
    "zhao2019pyod": article(
        "Y. Zhao, Z. Nasrullah, Z. Li",
        "PyOD: A Python toolbox for scalable outlier detection",
        "Journal of Machine Learning Research",
        2019,
        volume=20,
        issue=96,
        pages="1–7",
    ),
    "akiba2019": proceedings(
        "T. Akiba, S. Sano, T. Yanase, T. Ohta, M. Koyama",
        "Optuna: A next-generation hyperparameter optimization framework",
        "Proc. 25th ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining",
        "Anchorage, AK, USA",
        2019,
        pages="2623–2631",
    ),
}

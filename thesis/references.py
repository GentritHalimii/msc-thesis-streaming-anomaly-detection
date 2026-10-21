"""IEEE reference database, keyed for automatic in-text numbering.

Entries are cited in the text as [@key]; the builder assigns numbers in order
of first appearance, as IEEE style requires, and emits the list in that order.
Anything left uncited is dropped from the reference list rather than padding
it — an uncited work belongs in a bibliography, not in the references.
"""

REFERENCES: dict[str, str] = {
    # --- anomaly detection: foundations and surveys ----------------------
    "hawkins1980": "D. M. Hawkins, Identification of Outliers. London, U.K.: "
    "Chapman and Hall, 1980.",
    "chandola2009": "V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A "
    "survey,” ACM Computing Surveys, vol. 41, no. 3, pp. 1–58, 2009.",
    "aggarwal2017": "C. C. Aggarwal, Outlier Analysis, 2nd ed. Cham, Switzerland: Springer, 2017.",
    "ruff2021": "L. Ruff et al., “A unifying review of deep and shallow anomaly "
    "detection,” Proceedings of the IEEE, vol. 109, no. 5, pp. 756–795, "
    "2021.",
    "pang2021": "G. Pang, C. Shen, L. Cao, and A. van den Hengel, “Deep learning for "
    "anomaly detection: A review,” ACM Computing Surveys, vol. 54, no. 2, "
    "Art. no. 38, 2021.",
    # --- individual detectors --------------------------------------------
    "liu2008": "F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. "
    "8th IEEE Int. Conf. Data Mining (ICDM), Pisa, Italy, 2008, pp. 413–422.",
    "liu2012": "F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation-based anomaly "
    "detection,” ACM Trans. Knowledge Discovery from Data, vol. 6, no. 1, "
    "pp. 1–39, 2012.",
    "scholkopf2001": "B. Schölkopf, J. C. Platt, J. Shawe-Taylor, A. J. Smola, and "
    "R. C. Williamson, “Estimating the support of a high-dimensional "
    "distribution,” Neural Computation, vol. 13, no. 7, "
    "pp. 1443–1471, 2001.",
    "tax2004": "D. M. J. Tax and R. P. W. Duin, “Support vector data description,” "
    "Machine Learning, vol. 54, no. 1, pp. 45–66, 2004.",
    "breunig2000": "M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: "
    "Identifying density-based local outliers,” in Proc. ACM SIGMOD Int. "
    "Conf. Management of Data, Dallas, TX, USA, 2000, pp. 93–104.",
    "li2022ecod": "Z. Li, Y. Zhao, X. Hu, N. Botta, C. Ionescu, and G. H. Chen, “ECOD: "
    "Unsupervised outlier detection using empirical cumulative distribution "
    "functions,” IEEE Trans. Knowledge and Data Engineering, vol. 35, "
    "no. 12, pp. 12181–12193, 2023.",
    "shyu2003": "M.-L. Shyu, S.-C. Chen, K. Sarinnapakorn, and L. Chang, “A novel "
    "anomaly detection scheme based on principal component classifier,” in "
    "Proc. IEEE Foundations and New Directions of Data Mining Workshop, "
    "Melbourne, FL, USA, 2003, pp. 172–179.",
    # --- autoencoders and deep generative models -------------------------
    "hinton2006": "G. E. Hinton and R. R. Salakhutdinov, “Reducing the dimensionality of "
    "data with neural networks,” Science, vol. 313, no. 5786, "
    "pp. 504–507, 2006.",
    "sakurada2014": "M. Sakurada and T. Yairi, “Anomaly detection using autoencoders with "
    "nonlinear dimensionality reduction,” in Proc. MLSDA Workshop on "
    "Machine Learning for Sensory Data Analysis, Gold Coast, Australia, "
    "2014, pp. 4–11.",
    "kingma2014": "D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” in "
    "Proc. 2nd Int. Conf. Learning Representations (ICLR), Banff, Canada, 2014.",
    # --- credit-card fraud detection -------------------------------------
    "dalpozzolo2014": "A. Dal Pozzolo, O. Caelen, Y.-A. Le Borgne, S. Waterschoot, and "
    "G. Bontempi, “Learned lessons in credit card fraud detection from "
    "a practitioner perspective,” Expert Systems with Applications, "
    "vol. 41, no. 10, pp. 4915–4928, 2014.",
    "dalpozzolo2018": "A. Dal Pozzolo, G. Boracchi, O. Caelen, C. Alippi, and G. Bontempi, "
    "“Credit card fraud detection: A realistic modeling and a novel "
    "learning strategy,” IEEE Trans. Neural Networks and Learning "
    "Systems, vol. 29, no. 8, pp. 3784–3797, 2018.",
    "carcillo2018": "F. Carcillo, A. Dal Pozzolo, Y.-A. Le Borgne, O. Caelen, Y. Mazzer, and "
    "G. Bontempi, “SCARFF: A scalable framework for streaming credit card "
    "fraud detection with Spark,” Information Fusion, vol. 41, "
    "pp. 182–194, 2018.",
    "carcillo2021": "F. Carcillo, Y.-A. Le Borgne, O. Caelen, Y. Kessaci, F. Oblé, and "
    "G. Bontempi, “Combining unsupervised and supervised learning in "
    "credit card fraud detection,” Information Sciences, vol. 557, "
    "pp. 317–331, 2021.",
    "jurgovsky2018": "J. Jurgovsky et al., “Sequence classification for credit-card fraud "
    "detection,” Expert Systems with Applications, vol. 100, "
    "pp. 234–245, 2018.",
    "whitrow2009": "C. Whitrow, D. J. Hand, P. Juszczak, D. Weston, and N. M. Adams, "
    "“Transaction aggregation as a strategy for credit card fraud "
    "detection,” Data Mining and Knowledge Discovery, vol. 18, no. 1, "
    "pp. 30–55, 2009.",
    "bahnsen2016": "A. C. Bahnsen, D. Aouada, A. Stojanovic, and B. Ottersten, “Feature "
    "engineering strategies for credit card fraud detection,” Expert "
    "Systems with Applications, vol. 51, pp. 134–142, 2016.",
    "bhattacharyya2011": "S. Bhattacharyya, S. Jha, K. Tharakunnel, and J. C. Westland, "
    "“Data mining for credit card fraud: A comparative study,” "
    "Decision Support Systems, vol. 50, no. 3, pp. 602–613, 2011.",
    "leborgne2022": "Y.-A. Le Borgne, W. Siblini, B. Lebichot, and G. Bontempi, Reproducible "
    "Machine Learning for Credit Card Fraud Detection – Practical "
    "Handbook. Brussels, Belgium: Université Libre de Bruxelles, 2022. "
    "Accessed: Sep. 13, 2026. [Online]. Available: "
    "https://fraud-detection-handbook.github.io/fraud-detection-handbook/",
    "ulb_dataset": "Machine Learning Group – Université Libre de Bruxelles, "
    "“Credit Card Fraud Detection dataset,” Kaggle, 2018. Accessed: "
    "Sep. 13, 2026. [Online]. Available: "
    "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
    "ecb2021": "European Central Bank, “Seventh report on card fraud,” European "
    "Central Bank, Frankfurt am Main, Germany, Oct. 2021. Accessed: "
    "Sep. 13, 2026. [Online]. Available: "
    "https://www.ecb.europa.eu/pub/pdf/cardfraud/"
    "ecb.cardfraudreport202110~cac4c418e8.en.pdf",
    # --- class imbalance and cost ----------------------------------------
    "chawla2002": "N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, “SMOTE: "
    "Synthetic minority over-sampling technique,” Journal of Artificial "
    "Intelligence Research, vol. 16, pp. 321–357, 2002.",
    # --- evaluation methodology ------------------------------------------
    "davis2006": "J. Davis and M. Goadrich, “The relationship between precision-recall "
    "and ROC curves,” in Proc. 23rd Int. Conf. Machine Learning (ICML), "
    "Pittsburgh, PA, USA, 2006, pp. 233–240.",
    "saito2015": "T. Saito and M. Rehmsmeier, “The precision-recall plot is more "
    "informative than the ROC plot when evaluating binary classifiers on "
    "imbalanced datasets,” PLOS ONE, vol. 10, no. 3, e0118432, 2015.",
    "demsar2006": "J. Demšar, “Statistical comparisons of classifiers over multiple "
    "data sets,” Journal of Machine Learning Research, vol. 7, "
    "pp. 1–30, 2006.",
    "gama2013": "J. Gama, R. Sebastião, and P. P. Rodrigues, “On evaluating stream "
    "learning algorithms,” Machine Learning, vol. 90, no. 3, "
    "pp. 317–346, 2013.",
    "bergmeir2012": "C. Bergmeir and J. M. Benítez, “On the use of cross-validation "
    "for time series predictor evaluation,” Information Sciences, "
    "vol. 191, pp. 192–213, 2012.",
    # --- concept drift ----------------------------------------------------
    "gama2014": "J. Gama, I. Žliobaitė, A. Bifet, M. Pechenizkiy, and "
    "A. Bouchachia, “A survey on concept drift adaptation,” ACM "
    "Computing Surveys, vol. 46, no. 4, pp. 1–37, 2014.",
    # --- streaming systems ------------------------------------------------
    "kreps2011": "J. Kreps, N. Narkhede, and J. Rao, “Kafka: A distributed messaging "
    "system for log processing,” in Proc. 6th Int. Workshop on Networking "
    "Meets Databases (NetDB), Athens, Greece, 2011, pp. 1–7.",
    "carbone2015": "P. Carbone, S. Ewen, S. Haridi, A. Katsifodimos, V. Markl, and "
    "K. Tzoumas, “Apache Flink: Stream and batch processing in a single "
    "engine,” IEEE Data Engineering Bulletin, vol. 38, no. 4, "
    "pp. 28–38, 2015.",
    "kleppmann2017": "M. Kleppmann, Designing Data-Intensive Applications. Sebastopol, CA, "
    "USA: O’Reilly Media, 2017.",
    # --- ensembles ---------------------------------------------------------
    "aggarwal2015": "C. C. Aggarwal and S. Sathe, “Theoretical foundations and algorithms "
    "for outlier ensembles,” ACM SIGKDD Explorations Newsletter, vol. 17, "
    "no. 1, pp. 24–47, 2015.",
    "zimek2014": "A. Zimek, R. J. G. B. Campello, and J. Sander, “Ensembles for "
    "unsupervised outlier detection: challenges and research questions,” ACM "
    "SIGKDD Explorations Newsletter, vol. 15, no. 1, pp. 11–22, 2014.",
    "rayana2016": "S. Rayana and L. Akoglu, “Less is more: Building selective anomaly "
    "ensembles,” ACM Trans. Knowledge Discovery from Data, vol. 10, no. 4, "
    "pp. 1–33, 2016.",
    # --- statistics ---------------------------------------------------------
    "wilcoxon1945": "F. Wilcoxon, “Individual comparisons by ranking methods,” "
    "Biometrics Bulletin, vol. 1, no. 6, pp. 80–83, 1945.",
    "holm1979": "S. Holm, “A simple sequentially rejective multiple test procedure,” "
    "Scandinavian Journal of Statistics, vol. 6, no. 2, pp. 65–70, 1979.",
    "efron1993": "B. Efron and R. J. Tibshirani, An Introduction to the Bootstrap. New York, "
    "NY, USA: Chapman and Hall, 1993.",
    # --- software -----------------------------------------------------------
    "pedregosa2011": "F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” "
    "Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
    "paszke2019": "A. Paszke et al., “PyTorch: An imperative style, high-performance deep "
    "learning library,” in Advances in Neural Information Processing "
    "Systems (NeurIPS), vol. 32, Vancouver, Canada, 2019, pp. 8024–8035.",
    "zhao2019pyod": "Y. Zhao, Z. Nasrullah, and Z. Li, “PyOD: A Python toolbox for "
    "scalable outlier detection,” Journal of Machine Learning Research, "
    "vol. 20, no. 96, pp. 1–7, 2019.",
    "akiba2019": "T. Akiba, S. Sano, T. Yanase, T. Ohta, and M. Koyama, “Optuna: A "
    "next-generation hyperparameter optimization framework,” in Proc. 25th "
    "ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining, Anchorage, AK, "
    "USA, 2019, pp. 2623–2631.",
}

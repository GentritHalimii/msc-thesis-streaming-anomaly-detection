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
    "aggarwal2017": "C. C. Aggarwal, Outlier Analysis, 2nd ed. Cham, Switzerland: "
                    "Springer, 2017.",
    "ruff2021": "L. Ruff et al., “A unifying review of deep and shallow anomaly "
                "detection,” Proceedings of the IEEE, vol. 109, no. 5, pp. 756–795, "
                "2021.",
    "pang2021": "G. Pang, C. Shen, L. Cao, and A. van den Hengel, “Deep learning for "
                "anomaly detection: A review,” ACM Computing Surveys, vol. 54, no. 2, "
                "pp. 1–38, 2021.",

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
    "ramaswamy2000": "S. Ramaswamy, R. Rastogi, and K. Shim, “Efficient algorithms for "
                     "mining outliers from large data sets,” in Proc. ACM SIGMOD Int. "
                     "Conf. Management of Data, Dallas, TX, USA, 2000, pp. 427–438.",
    "ruff2018": "L. Ruff et al., “Deep one-class classification,” in Proc. 35th Int. "
                "Conf. Machine Learning (ICML), Stockholm, Sweden, 2018, "
                "pp. 4393–4402.",
    "goldstein2012": "M. Goldstein and A. Dengel, “Histogram-based outlier score (HBOS): "
                     "A fast unsupervised anomaly detection algorithm,” in KI-2012: "
                     "Poster and Demo Track, Saarbrücken, Germany, 2012, pp. 59–63.",
    "pevny2016": "T. Pevný, “Loda: Lightweight on-line detector of anomalies,” "
                 "Machine Learning, vol. 102, no. 2, pp. 275–304, 2016.",
    "li2020copod": "Z. Li, Y. Zhao, N. Botta, C. Ionescu, and X. Hu, “COPOD: "
                   "Copula-based outlier detection,” in Proc. IEEE Int. Conf. Data "
                   "Mining (ICDM), Sorrento, Italy, 2020, pp. 1118–1123.",
    "li2022ecod": "Z. Li, Y. Zhao, X. Hu, N. Botta, C. Ionescu, and G. H. Chen, “ECOD: "
                  "Unsupervised outlier detection using empirical cumulative distribution "
                  "functions,” IEEE Trans. Knowledge and Data Engineering, vol. 35, "
                  "no. 12, pp. 12181–12193, 2023.",
    "shyu2003": "M.-L. Shyu, S.-C. Chen, K. Sarinnapakorn, and L. Chang, “A novel "
                "anomaly detection scheme based on principal component classifier,” in "
                "Proc. IEEE Foundations and New Directions of Data Mining Workshop, "
                "Melbourne, FL, USA, 2003, pp. 172–179.",
    "rousseeuw1999": "P. J. Rousseeuw and K. Van Driessen, “A fast algorithm for the "
                     "minimum covariance determinant estimator,” Technometrics, vol. 41, "
                     "no. 3, pp. 212–223, 1999.",

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
    "an2015": "J. An and S. Cho, “Variational autoencoder based anomaly detection using "
              "reconstruction probability,” SNU Data Mining Center, Seoul, South Korea, "
              "Tech. Rep. 2015-2, 2015.",
    "zong2018": "B. Zong et al., “Deep autoencoding Gaussian mixture model for "
                "unsupervised anomaly detection,” in Proc. 6th Int. Conf. Learning "
                "Representations (ICLR), Vancouver, Canada, 2018.",

    # --- credit-card fraud detection -------------------------------------
    "dalpozzolo2014": "A. Dal Pozzolo, O. Caelen, Y.-A. Le Borgne, S. Waterschoot, and "
                      "G. Bontempi, “Learned lessons in credit card fraud detection from "
                      "a practitioner perspective,” Expert Systems with Applications, "
                      "vol. 41, no. 10, pp. 4915–4928, 2014.",
    "dalpozzolo2015": "A. Dal Pozzolo, O. Caelen, R. A. Johnson, and G. Bontempi, "
                      "“Calibrating probability with undersampling for unbalanced "
                      "classification,” in Proc. IEEE Symp. Series on Computational "
                      "Intelligence (SSCI), Cape Town, South Africa, 2015, pp. 159–166.",
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
    "makki2019": "S. Makki, Z. Assaghir, Y. Taher, R. Haque, M.-S. Hacid, and H. Zeineddine, "
                 "“An experimental study with imbalanced classification approaches for "
                 "credit card fraud detection,” IEEE Access, vol. 7, "
                 "pp. 93010–93022, 2019.",
    "leborgne2022": "Y.-A. Le Borgne, W. Siblini, B. Lebichot, and G. Bontempi, Reproducible "
                    "Machine Learning for Credit Card Fraud Detection – Practical "
                    "Handbook. Brussels, Belgium: Université Libre de Bruxelles, 2022.",
    "ulb_dataset": "Machine Learning Group – Université Libre de Bruxelles, "
                   "“Credit Card Fraud Detection dataset,” Kaggle, 2018. [Online]. "
                   "Available: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
    "ecb2021": "European Central Bank, “Seventh report on card fraud,” European "
               "Central Bank, Frankfurt am Main, Germany, Oct. 2021.",

    # --- class imbalance and cost ----------------------------------------
    "chawla2002": "N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, “SMOTE: "
                  "Synthetic minority over-sampling technique,” Journal of Artificial "
                  "Intelligence Research, vol. 16, pp. 321–357, 2002.",
    "he2009": "H. He and E. A. Garcia, “Learning from imbalanced data,” IEEE Trans. "
              "Knowledge and Data Engineering, vol. 21, no. 9, pp. 1263–1284, 2009.",
    "branco2016": "P. Branco, L. Torgo, and R. P. Ribeiro, “A survey of predictive "
                  "modeling on imbalanced domains,” ACM Computing Surveys, vol. 49, "
                  "no. 2, pp. 1–50, 2016.",
    "elkan2001": "C. Elkan, “The foundations of cost-sensitive learning,” in Proc. "
                 "17th Int. Joint Conf. Artificial Intelligence (IJCAI), Seattle, WA, USA, "
                 "2001, pp. 973–978.",

    # --- evaluation methodology ------------------------------------------
    "davis2006": "J. Davis and M. Goadrich, “The relationship between precision-recall "
                 "and ROC curves,” in Proc. 23rd Int. Conf. Machine Learning (ICML), "
                 "Pittsburgh, PA, USA, 2006, pp. 233–240.",
    "saito2015": "T. Saito and M. Rehmsmeier, “The precision-recall plot is more "
                 "informative than the ROC plot when evaluating binary classifiers on "
                 "imbalanced datasets,” PLOS ONE, vol. 10, no. 3, e0118432, 2015.",
    "hand2009": "D. J. Hand, “Measuring classifier performance: a coherent alternative "
                "to the area under the ROC curve,” Machine Learning, vol. 77, no. 1, "
                "pp. 103–123, 2009.",
    "demsar2006": "J. Demšar, “Statistical comparisons of classifiers over multiple "
                  "data sets,” Journal of Machine Learning Research, vol. 7, "
                  "pp. 1–30, 2006.",
    "campos2016": "G. O. Campos et al., “On the evaluation of unsupervised outlier "
                  "detection: measures, datasets, and an empirical study,” Data Mining "
                  "and Knowledge Discovery, vol. 30, no. 4, pp. 891–927, 2016.",
    "emmott2013": "A. F. Emmott, S. Das, T. Dietterich, A. Fern, and W.-K. Wong, "
                  "“Systematic construction of anomaly detection benchmarks from real "
                  "data,” in Proc. ACM SIGKDD Workshop on Outlier Detection and "
                  "Description, Chicago, IL, USA, 2013, pp. 16–21.",
    "han2022": "S. Han, X. Hu, H. Huang, M. Jiang, and Y. Zhao, “ADBench: Anomaly "
               "detection benchmark,” in Advances in Neural Information Processing "
               "Systems (NeurIPS), vol. 35, 2022, pp. 32142–32159.",
    "goix2015": "N. Goix, A. Sabourin, and S. Clémençon, “On anomaly ranking "
                "and excess-mass curves,” in Proc. 18th Int. Conf. Artificial "
                "Intelligence and Statistics (AISTATS), San Diego, CA, USA, 2015, "
                "pp. 287–295.",
    "goix2016": "N. Goix, “How to evaluate the quality of unsupervised anomaly detection "
                "algorithms?” in ICML Anomaly Detection Workshop, New York, NY, USA, "
                "2016.",
    "gama2013": "J. Gama, R. Sebastião, and P. P. Rodrigues, “On evaluating stream "
                "learning algorithms,” Machine Learning, vol. 90, no. 3, "
                "pp. 317–346, 2013.",
    "bergmeir2012": "C. Bergmeir and J. M. Benítez, “On the use of cross-validation "
                    "for time series predictor evaluation,” Information Sciences, "
                    "vol. 191, pp. 192–213, 2012.",
    "tashman2000": "L. J. Tashman, “Out-of-sample tests of forecasting accuracy: an "
                   "analysis and review,” International Journal of Forecasting, vol. 16, "
                   "no. 4, pp. 437–450, 2000.",

    # --- concept drift ----------------------------------------------------
    "gama2014": "J. Gama, I. Žliobaitė, A. Bifet, M. Pechenizkiy, and "
                "A. Bouchachia, “A survey on concept drift adaptation,” ACM "
                "Computing Surveys, vol. 46, no. 4, pp. 1–37, 2014.",
    "bifet2007": "A. Bifet and R. Gavaldà, “Learning from time-changing data with "
                 "adaptive windowing,” in Proc. SIAM Int. Conf. Data Mining (SDM), "
                 "Minneapolis, MN, USA, 2007, pp. 443–448.",
    "page1954": "E. S. Page, “Continuous inspection schemes,” Biometrika, vol. 41, "
                "no. 1/2, pp. 100–115, 1954.",
    "lu2019": "J. Lu, A. Liu, F. Dong, F. Gu, J. Gama, and G. Zhang, “Learning under "
              "concept drift: A review,” IEEE Trans. Knowledge and Data Engineering, "
              "vol. 31, no. 12, pp. 2346–2363, 2019.",

    # --- streaming systems ------------------------------------------------
    "kreps2011": "J. Kreps, N. Narkhede, and J. Rao, “Kafka: A distributed messaging "
                 "system for log processing,” in Proc. 6th Int. Workshop on Networking "
                 "Meets Databases (NetDB), Athens, Greece, 2011, pp. 1–7.",
    "carbone2015": "P. Carbone, A. Katsifodimos, S. Ewen, V. Markl, S. Haridi, and "
                   "K. Tzoumas, “Apache Flink: Stream and batch processing in a single "
                   "engine,” IEEE Data Engineering Bulletin, vol. 38, no. 4, "
                   "pp. 28–38, 2015.",
    "zaharia2013": "M. Zaharia, T. Das, H. Li, T. Hunter, S. Shenker, and I. Stoica, "
                   "“Discretized streams: fault-tolerant streaming computation at "
                   "scale,” in Proc. 24th ACM Symp. Operating Systems Principles (SOSP), "
                   "Farminton, PA, USA, 2013, pp. 423–438.",
    "akidau2015": "T. Akidau et al., “The dataflow model: a practical approach to "
                  "balancing correctness, latency, and cost in massive-scale, unbounded, "
                  "out-of-order data processing,” Proc. VLDB Endowment, vol. 8, no. 12, "
                  "pp. 1792–1803, 2015.",
    "kleppmann2017": "M. Kleppmann, Designing Data-Intensive Applications. Sebastopol, CA, "
                     "USA: O’Reilly Media, 2017.",
    "bifet2010": "A. Bifet, G. Holmes, R. Kirkby, and B. Pfahringer, “MOA: Massive online "
                 "analysis,” Journal of Machine Learning Research, vol. 11, "
                 "pp. 1601–1604, 2010.",

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
    "caruana2004": "R. Caruana, A. Niculescu-Mizil, G. Crew, and A. Ksikes, “Ensemble "
                   "selection from libraries of models,” in Proc. 21st Int. Conf. Machine "
                   "Learning (ICML), Banff, Canada, 2004, p. 18.",
    "zhao2019lscp": "Y. Zhao, Z. Nasrullah, M. K. Hryniewicki, and Z. Li, “LSCP: Locally "
                    "selective combination in parallel outlier ensembles,” in Proc. SIAM "
                    "Int. Conf. Data Mining (SDM), Calgary, Canada, 2019, pp. 585–593.",
    "kuncheva2003": "L. I. Kuncheva and C. J. Whitaker, “Measures of diversity in "
                    "classifier ensembles and their relationship with the ensemble "
                    "accuracy,” Machine Learning, vol. 51, no. 2, pp. 181–207, 2003.",

    # --- interpretability ---------------------------------------------------
    "lundberg2017": "S. M. Lundberg and S.-I. Lee, “A unified approach to interpreting "
                    "model predictions,” in Advances in Neural Information Processing "
                    "Systems (NIPS), vol. 30, Long Beach, CA, USA, 2017, pp. 4765–4774.",
    "ribeiro2016": "M. T. Ribeiro, S. Singh, and C. Guestrin, “‘Why should I trust "
                   "you?’: Explaining the predictions of any classifier,” in Proc. "
                   "22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining, "
                   "San Francisco, CA, USA, 2016, pp. 1135–1144.",
    "breiman2001": "L. Breiman, “Random forests,” Machine Learning, vol. 45, no. 1, "
                   "pp. 5–32, 2001.",

    # --- statistics ---------------------------------------------------------
    "friedman1937": "M. Friedman, “The use of ranks to avoid the assumption of normality "
                    "implicit in the analysis of variance,” Journal of the American "
                    "Statistical Association, vol. 32, no. 200, pp. 675–701, 1937.",
    "nemenyi1963": "P. B. Nemenyi, “Distribution-free multiple comparisons,” Ph.D. "
                   "dissertation, Princeton University, Princeton, NJ, USA, 1963.",
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
    "bergstra2012": "J. Bergstra and Y. Bengio, “Random search for hyper-parameter "
                    "optimization,” Journal of Machine Learning Research, vol. 13, "
                    "pp. 281–305, 2012.",
    "harris2020": "C. R. Harris et al., “Array programming with NumPy,” Nature, "
                  "vol. 585, pp. 357–362, 2020.",
    "hunter2007": "J. D. Hunter, “Matplotlib: A 2D graphics environment,” Computing "
                  "in Science & Engineering, vol. 9, no. 3, pp. 90–95, 2007.",
}

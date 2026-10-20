"""Kapitulli 5 — REZULTATET."""

from blocks import fig, h1, h2, h3, note, p, tab

_HYRJE = [
    h1("5", "Rezultatet"),
    p("""Rezultatet paraqiten në pesë pjesë. E para mat kufirin e sipërm gjeometrik të problemit pa
      trajnuar asnjë model, sepse ky kufi ndikon në mënyrën si lexohet gjithçka që vjen pas tij. Tri
      pjesët e ardhshme u përgjigjen me radhë tri pyetjeve hulumtuese. Pjesa e fundit paraqet
      studimet e thelluara për secilin algoritëm dhe analizat që e shpjegojnë renditjen e tyre."""),
    p("""Tabelat dhe figurat gjenerohen drejtpërdrejt nga rezultatet e ruajtura të eksperimenteve,
      dhe numrat në tekst janë marrë nga po këto tabela. Çdo eksperiment shoqërohet me një manifest
      që ruan SHA-në e commit-it dhe hash-in e konfigurimit."""),
    note("""Kudo ku shfaqet, Regresioni Logjistik shënohet si referencë e mbikëqyrur. Ai nuk
      konkurron me metodat unsupervised, sepse ka përdorur etiketat historike; tregon sa larg mund
      të shkohet kur këto etiketa ekzistojnë."""),
]

_GJEOMETRIA = [
    h2("5.1", "Kufiri i sipërm gjeometrik i problemit"),
    p("""Të tri metodat unsupervised e përcaktojnë anomalinë përmes një nocioni largësie ose
      ngjeshjeje. Prandaj pyetja e parë nuk është cila prej tyre është më e mira, por sa larg mund
      të shkojë çdo metodë e këtij lloji mbi këto të dhëna. Përgjigja merret pa trajnuar asnjë
      model."""),
    tab(
        "geometry_summary",
        "Karakterizimi gjeometrik i dritareve të trajnimit dhe të testimit.",
        columns=[
            "dritarja",
            "rreshta",
            "mashtrime",
            "id_mle_normale",
            "id_twonn_normale",
            "knn_distanca_normale",
            "knn_distanca_mashtrime",
            "raporti_distancave",
            "ap_vetem_distance",
            "rangu_median_i_mashtrimit",
            "mashtrime_ne_top100",
        ],
        rename={
            "dritarja": "Dritarja",
            "rreshta": "Rreshta",
            "mashtrime": "Mashtrime",
            "id_mle_normale": "Dimensioni i brendshëm (MLE)",
            "id_twonn_normale": "Dimensioni i brendshëm (TwoNN)",
            "knn_distanca_normale": "Distanca kNN e legjitimeve",
            "knn_distanca_mashtrime": "Distanca kNN e mashtrimeve",
            "raporti_distancave": "Raporti i distancave",
            "ap_vetem_distance": "AP vetëm me distancë",
            "rangu_median_i_mashtrimit": "Rangu median i mashtrimit",
            "mashtrime_ne_top100": "Mashtrime në 100 të parët",
        },
        transpose="Madhësia",
        round={
            "id_mle_normale": 2,
            "id_twonn_normale": 2,
            "knn_distanca_normale": 2,
            "knn_distanca_mashtrime": 2,
            "raporti_distancave": 2,
            "ap_vetem_distance": 3,
            "rangu_median_i_mashtrimit": 0,
        },
        font_size=9.5,
    ),
    p("""Supozimi gjeometrik vlen. Distanca mediane e një mashtrimi nga dhjetë fqinjët e tij
      legjitimë më të afërt është 7.9 herë më e madhe se ajo e një transaksioni tipik legjitim, dhe
      në dritaren e testimit raporti mbetet mbi gjashtë (Figura [[fig:geometry_knn_distance]]). Në
      këtë kuptim mashtrimet janë vërtet vlera të jashtëzakonshme."""),
    p("""Kjo largësi megjithatë nuk sjell zbulim të lehtë. Detektori që e rendit çdo transaksion
      vetëm sipas kësaj distance arrin AP 0.304 në dritaren e trajnimit dhe 0.124 në atë të
      testimit. Arsyeja është numerike: dritarja e trajnimit ka afërsisht 199 000 transaksione
      legjitime, dhe 5% e tyre që ndodhen më larg janë rreth 10 000 transaksione. Ato zënë të
      njëjtin rajon me 384 mashtrimet e dritares, të cilat janë shumë më pak në numër."""),
    fig(
        "geometry_knn_distance",
        "Distanca mesatare deri te dhjetë fqinjët legjitimë më të afërt, sipas klasës.",
        15.0,
    ),
    p("""Në terma operacionalë kjo do të thotë se për të arritur mashtrimin median duhen shqyrtuar
      rreth 530 alarme, dhe se brenda 100 alarmeve të para kapen vetëm 40 nga 384 mashtrimet e
      dritares së trajnimit (Figura [[fig:geometry_cost_to_catch]]). Në dritaren e testimit, ku
      problemi është më i vështirë, kapen vetëm 6 nga 108."""),
    fig(
        "geometry_cost_to_catch",
        "Mashtrimet e kapura sipas numrit të alarmeve, kur renditja bëhet vetëm sipas distancës.",
        15.0,
    ),
    p("""Dimensioni i brendshëm i klasës legjitime vlerësohet rreth 3.8 me metodën TwoNN dhe rreth
      7.3 me atë të gjasës maksimale, kundrejt 29 dimensioneve nominale. Të dy vlerësuesit kanë
      anshmëri në drejtime të kundërta, prandaj vlera e vërtetë ka të ngjarë të jetë mes tyre;
      gjithsesi të dy tregojnë se struktura reale e të dhënave është shumë më e thjeshtë se hapësira
      ku ato paraqiten. Kjo ka rëndësi për Autoencoder-in, dimensioni latent i të cilit pritet të
      jetë i krahasueshëm me këtë vlerë; pritshmëria testohet në nënkapitullin 5.5.2."""),
    p("""Fuqia diskriminuese është e përqendruar, por jo tërësisht: pesë veçoritë më informative
      mbajnë 32% të fuqisë totale njëvariablëshe, kështu që sinjali shpërndahet mbi një numër të
      konsiderueshëm komponentësh. Ky fakt përdoret më poshtë për të shpjeguar sjelljen e Isolation
      Forest-it."""),
    p("""Nënkapitulli përcakton kornizën për leximin e gjithë kapitullit. Një detektor që arrin AP
      mes 0.1 dhe 0.3 mbi këto të dhëna nuk është domosdoshmërisht i dobët, sepse ndodhet afër asaj
      që lejon gjeometria. Pyetja e vërtetë është kush e kalon këtë kufi dhe me çfarë mjetesh."""),
]

_PH1 = [
    h2("5.2", "PH1: realizueshmëria operacionale"),
    p("""Pyetja e parë hulumtuese ka dy pjesë: nëse një sistem i tillë mund të ndërtohet duke lidhur
      Apache Kafka-n me modele unsupervised, dhe nëse vonesa mesatare end-to-end mbetet nën një
      sekondë. Përgjigjen e pjesës së parë e jep vetë implementimi i përshkruar në Kapitullin 4;
      këtu jepet përgjigja e pjesës së dytë, me matje."""),
    p("""Për secilin nga katër modelet u riprodhuan 20 000 transaksione nëpër një broker real Kafka
      në modalitetin KRaft, me katër ritme mbërritjeje: 50, 200, 1000 dhe 2000 mesazhe në sekondë.
      Vonesa end-to-end matet ashtu si përcaktohet në nënkapitullin 4.9.2, me orën e të njëjtit
      host, prandaj nuk përmban pasiguri sinkronizimi mes makinave."""),
    tab(
        "latency_summary",
        "Vonesa end-to-end, koha e inferencës dhe throughput për çdo model dhe ritëm.",
        query="prag_adaptiv == False",
        columns=[
            "model",
            "rate_msg_s",
            "e2e_ms_mean",
            "e2e_ms_p50",
            "e2e_ms_p95",
            "e2e_ms_p99",
            "infer_ms_mean",
            "batch_size_mean",
            "throughput_msg_s",
            "cpu_percent_mean",
            "rss_peak_mb",
            "throughput_ratio",
        ],
        rename={
            "model": "Modeli",
            "rate_msg_s": "Ritmi",
            "e2e_ms_mean": "e2e mes. (ms)",
            "e2e_ms_p50": "p50",
            "e2e_ms_p95": "p95",
            "e2e_ms_p99": "p99",
            "infer_ms_mean": "Inf. (ms)",
            "batch_size_mean": "Grupi",
            "throughput_msg_s": "msg/s",
            "cpu_percent_mean": "CPU %",
            "rss_peak_mb": "RSS (MB)",
            "throughput_ratio": "Raporti",
        },
        round={
            "e2e_ms_mean": 1,
            "e2e_ms_p50": 1,
            "e2e_ms_p95": 1,
            "e2e_ms_p99": 1,
            "infer_ms_mean": 3,
            "batch_size_mean": 1,
            "throughput_msg_s": 0,
            "cpu_percent_mean": 1,
            "rss_peak_mb": 0,
            "throughput_ratio": 3,
        },
        font_size=8.0,
    ),
    p("""Hipoteza H1 konfirmohet me diferencë të madhe. Vonesa mesatare end-to-end lëviz nga 18.9 në
      67.9 milisekonda në të 16 kombinimet, 15 deri 53 herë nën objektivin prej një sekonde (Figura
      [[fig:latency_vs_rate]]). Edhe percentili 99, matja e duhur për një kufizim operacional, nuk e
      kalon 131.5 milisekonda në asnjë konfigurim dhe mbetet rreth tetë herë nën objektiv. Kolona e
      fundit e tabelës jep raportin mes throughput-it të arritur dhe ritmit të synuar."""),
    fig(
        "latency_vs_rate",
        "Vonesa end-to-end sipas modelit dhe ritmit të mbërritjes, kundrejt objektivit prej një "
        "sekonde.",
        15.0,
    ),
    p("""Inferenca zë një pjesë të vogël të kësaj vonese. Për tre nga katër modelet ajo mbetet nën
      gjysmë milisekonde mesatarisht në çdo ritëm, pra nën 1.5% të vonesës totale. Përjashtim bën
      Isolation Forest-i, me 5.46 milisekonda në ritmin më të ulët, që megjithatë është vetëm 9.4% e
      vonesës së tij totale. Pjesën më të madhe të vonesës e zënë transporti dhe mbledhja e
      mesazheve, jo pikëzimi."""),
    p("""Kjo shpjegon edhe një vëzhgim që në pamje të parë duket i kundërt: vonesa bie kur ritmi
      rritet. Për Isolation Forest-in ajo zbret nga 58.1 milisekonda në ritmin 50 në 43.0 në ritmin
      2000, dhe për Autoencoder-in nga 30.1 në 18.9. Ndërkohë madhësia mesatare e mikro-grupit
      rritet nga 2.7 në 63.9 mesazhe. Në ritme të ulëta consumer-i pret deri në fund të intervalit
      të leximit para se të marrë një grup të vogël, dhe kjo pritje e përcakton vonesën; në ritme të
      larta grupi mbushet menjëherë dhe pritja zhduket. Në këto ritme sistemi kufizohet nga koha e
      transportit dhe jo nga kapaciteti llogaritës."""),
    p("""Throughput-i tregon ku fillon kufiri. Deri në 1000 mesazhe në sekondë throughput-i i
      arritur është 90% deri 99.6% e ritmit të synuar. Në 2000 mesazhe në sekondë raporti bie në
      0.86 deri 0.89, dhe të katër modelet arrijnë rreth 1720 deri 1780 mesazhe në sekondë, gjë që
      tregon se një consumer i vetëm ngopet afër kësaj vlere. Meqë hipoteza H1 e vendos kufirin në
      1000 mesazhe në sekondë, ajo vlen edhe nga ky aspekt."""),
    p("""Kostoja e burimeve është e moderuar. Përdorimi mesatar i CPU-së nuk e kalon 73% të një
      bërthame në asnjë konfigurim, dhe vlerat më të larta i ka Isolation Forest-i. Memoria
      rezidente maksimale është mes 353 dhe 360 MB dhe varet kryesisht nga interpretuesi Python dhe
      bibliotekat e ngarkuara, jo nga modelet."""),
    p("""U mat edhe kostoja e pragut adaptiv, i cili kërkon që consumer-i të mbajë një dritare
      rrëshqitëse pikësh dhe të rillogarisë periodikisht një kuantil. Në ritmin 200 mesazhe në
      sekondë, me 39 rifreskime gjatë 20 000 mesazheve, vonesa mesatare është 63.6 milisekonda për
      Isolation Forest-in (67.9 me prag statik), 29.7 për Autoencoder-in (30.2) dhe 31.9 për
      One-Class SVM-në (30.6). Dallimet janë brenda zhurmës së matjes, kështu që procedura e
      nënkapitullit 5.13 nuk ka kosto operacionale të matshme."""),
    p("""Në të njëjtat ekzekutime u kontrollua edhe ruajtja e të dhënave: transaksionet e pikëzuara
      dhe alarmet shkruhen në PostgreSQL në grupe, dhe paneli Grafana i lexon drejtpërsëdrejti nga
      baza. Testi i integrimit kontrollon që pikët e prodhuara në rrjedhë janë të njëjta me ato
      offline për të njëjtat transaksione, kështu që rezultatet e këtij kapitulli vlejnë edhe për
      sistemin në punë."""),
]

_PH2 = [
    h2("5.3", "PH2: krahasimi i algoritmeve"),
    h3("5.3.1", "Rezultatet në konfigurimin bazë"),
    p("""Tabela kryesore paraqet tri algoritmet unsupervised dhe referencën e mbikëqyrur në
      protokollin rolling-origin 8-fold, me hiperparametrat bazë dhe me StandardScaler. Ky është
      konfigurimi bazë dhe jo ai më i miri i mundshëm; raportohen të dy, dhe dallimi mes tyre është
      vetë një rezultat."""),
    tab(
        "benchmark_summary",
        "Rezultatet kryesore në konfigurimin bazë (mesatare 8-fold).",
        columns=[
            "model",
            "ap_mean",
            "ap_std",
            "avg_rank_ap",
            "roc_auc_mean",
            "amount_ap_mean",
            "f1_thr_mean",
            "recall_at_100",
            "score_us_per_tx",
            "fit_time_s",
        ],
        rename={
            "model": "Detektori",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "avg_rank_ap": "Rangu",
            "roc_auc_mean": "ROC",
            "amount_ap_mean": "AP mon.",
            "f1_thr_mean": "F1",
            "recall_at_100": "R@100",
            "score_us_per_tx": "µs/tx",
            "fit_time_s": "Fit (s)",
        },
        round={
            "ap_mean": 3,
            "ap_std": 3,
            "avg_rank_ap": 2,
            "roc_auc_mean": 3,
            "amount_ap_mean": 3,
            "f1_thr_mean": 3,
            "recall_at_100": 3,
            "score_us_per_tx": 2,
            "fit_time_s": 1,
        },
        widths=[4.4, 1.4, 1.3, 1.3, 1.3, 1.4, 1.3, 1.4, 1.3, 1.3],
        font_size=8.5,
    ),
    p("""Në tabelë, rangu llogaritet mbi AP-në e çdo fold-i, AP mon. është AP e ponderuar me shumën
      e mashtrimit, R@100 është recall-i me 100 alarme për bllok, dhe kostoja e pikëzimit jepet në
      mikrosekonda për transaksion në regjimin offline. Rezultati i parë është hendeku me
      referencën: modeli i mbikëqyrur arrin AP 0.734 dhe është i pari në të tetë fold-et (rangu
      mesatar 1.00), ndërsa metoda më e mirë unsupervised arrin 0.193. Raporti prej rreth 3.8 mes
      tyre tregon sa vlejnë etiketat historike në këtë problem."""),
    p("""Mes metodave unsupervised kryeson Autoencoder-i me 0.193, i ndjekur nga One-Class SVM me
      0.151 dhe Isolation Forest me 0.091 (Figura [[fig:benchmark_ap_ranking]]). Të tre janë në të
      njëjtin rend madhësie me detektorin e distancës të nënkapitullit 5.1, gjë që mbështet idenë se
      pengesa kryesore është vetë problemi."""),
    p("""Krahasimi i AP-së me AUC-ROC është gjithashtu informues. Isolation Forest-i, me AP 0.091,
      ka AUC-ROC 0.941, praktikisht sa Autoencoder-i (0.943), i cili ka AP dy herë më të lartë. Nëse
      do të raportohej vetëm ROC, siç bën një pjesë e literaturës për këtë dataset, të tre
      detektorët do të dukeshin të barabartë. Ky është ilustrimi empirik i argumentit të Davis-it e
      Goadrich-it dhe të Saito-s e Rehmsmeier-it [@davis2006], [@saito2015]."""),
    fig(
        "benchmark_ap_ranking",
        "AP e çdo detektori në tetë fold-et; rombi shënon mesataren.",
        15.0,
    ),
    p("""Shpërndarja nëpër fold-e ka po aq rëndësi sa mesatarja. Për çdo detektor unsupervised
      devijimi standard është i krahasueshëm me mesataren, dhe për Autoencoder-in madje e kalon atë.
      Performanca e një detektori varet shumë nga periudha kur vendoset (Figura
      [[fig:benchmark_ap_per_fold]])."""),
    fig(
        "benchmark_ap_per_fold",
        "AP e çdo detektori në çdo fold (shkallë logaritmike).",
        15.0,
    ),
    p("""Fold-i 1 dallohet qartë: në të AP rritet për të gjithë detektorët. Ai ka 88 mashtrime, gati
      katër herë më shumë se mesatarja prej 23 në blloqet e tjera, dhe analiza e zhvendosjes tregon
      se mashtrimet e tij janë edhe më të largëta nga klasa normale. Një studim që do të testonte
      rastësisht mbi këtë periudhë do të raportonte rezultate shumë më të mira pa ndryshuar asgjë në
      metodë."""),
    h3("5.3.2", "Qëndrueshmëria statistikore e dallimeve"),
    p("""Testi i Friedman-it mbi rangjet refuzon hipotezën se detektorët janë të barabartë, si për
      tri metodat unsupervised (χ² = 9.75, p = 0.0076) ashtu edhe për katër modelet bashkë (χ² =
      20.25, p = 0.00015). Kufizimi i krahasimit në tri algoritme e bën testin post-hoc të
      përdorshëm: diferenca kritike e Nemenyi-t është 1.17 njësi rangu, ndërsa rangjet mesatare
      shtrihen në një interval prej 1.50. Me shumë më tepër detektorë diferenca kritike do ta
      kalonte këtë interval dhe testi nuk do të refuzonte dot asgjë."""),
    tab(
        "significance_omnibus",
        "Testi i Friedman-it dhe diferenca kritike e Nemenyi-t për dy grupe krahasimi.",
        rename={
            "grupi": "Grupi i krahasimit",
            "k": "k",
            "N_folde": "N",
            "friedman_chi2": "χ² Friedman",
            "p_value": "p",
            "nemenyi_CD": "CD",
            "range_i_rangjeve": "Gjerësia e rangjeve",
        },
        round={"friedman_chi2": 2, "nemenyi_CD": 2, "range_i_rangjeve": 2},
        font_size=9.5,
    ),
    fig(
        "significance_cd_core",
        "Diagrami i diferencës kritike për katër modelet (Nemenyi, α = 0.05).",
        15.0,
    ),
    p("""Në diagram (Figura [[fig:significance_cd_core]]), modelet e lidhura me një vijë të trashë
      nuk dallohen nga testi i Nemenyi-t. Ky test krahason njëkohësisht të gjitha çiftet dhe për
      këtë arsye është konservativ: me katër modele ai nuk e dallon as Autoencoder-in nga Isolation
      Forest-i. Për krahasimet që emërtojnë pyetjet hulumtuese u përdor testi i Wilcoxon-it për
      çifte me korrigjim Holm. Gjashtë krahasimet u fiksuan në kod para se të shihej ndonjë
      rezultat, dhe numri i tyre u zgjodh që korrigjimi të mund të kalohej: me tetë fold-e p-vlera
      më e vogël e mundshme është 0.0078, e cila shumëzuar me gjashtë jep 0.047."""),
    tab(
        "significance_wilcoxon",
        "Krahasimet dyshe të deklaruara paraprakisht (Wilcoxon, korrigjim Holm).",
        columns=[
            "krahasimi",
            "mean_diff",
            "wins_a",
            "wins_b",
            "p_value",
            "p_holm",
            "significant_holm_05",
        ],
        rename={
            "krahasimi": "Krahasimi",
            "mean_diff": "Δ AP mesatar",
            "wins_a": "Fitore A",
            "wins_b": "Fitore B",
            "p_value": "p",
            "p_holm": "p (Holm)",
            "significant_holm_05": "Domethënës",
        },
        round={"mean_diff": 4, "p_value": 4, "p_holm": 4},
        widths=[6.2, 1.7, 1.4, 1.4, 1.3, 1.4, 1.6],
        font_size=8.5,
    ),
    p("""Pesë nga gjashtë krahasimet e kalojnë korrigjimin. Autoencoder-i e mund Isolation Forest-in
      në shtatë nga tetë fold-e, One-Class SVM e mund Isolation Forest-in në të tetë, dhe referenca
      e mbikëqyrur i mund të tre detektorët në të gjitha fold-et. I vetmi krahasim pa domethënie
      statistikore është Autoencoder kundrejt One-Class SVM: gjashtë fitore me dy, e qëndrueshme por
      jo e plotë."""),
    note("""Ky rezultat ka rëndësi për gjithë kapitullin: renditja mes dy detektorëve të parë nuk
      është e vërtetuar statistikisht në konfigurimin bazë, dhe nënkapitulli 5.6 tregon se ajo
      përmbyset kur ndryshon paraprocesimi."""),
    h3("5.3.3", "Cilësia kundrejt kostos"),
    p("""Pyetja e dytë hulumtuese nuk kërkon detektorin më të saktë, por atë me balancën më të mirë
      mes performancës dhe efikasitetit operacional. Të dyja duhen parë bashkë (Figura
      [[fig:benchmark_quality_cost]])."""),
    fig(
        "benchmark_quality_cost",
        "Cilësia e zbulimit kundrejt kostos së pikëzimit (mesatare 8-fold).",
        15.0,
    ),
    p("""Në konfigurimin bazë përgjigja është e qartë. Autoencoder-i ka AP-në më të lartë mes
      metodave unsupervised dhe njëkohësisht koston më të ulët të pikëzimit, 0.22 mikrosekonda për
      transaksion. Isolation Forest-i kushton rreth 37 herë më shumë për transaksion (8.1
      mikrosekonda) dhe jep gjysmën e cilësisë, ndërsa One-Class SVM kushton rreth 250 herë më shumë
      (55.4 mikrosekonda), sepse çdo transaksion krahasohet me të gjithë vektorët mbështetës."""),
    p("""Kostoja e trajnimit e rendit ndryshe: Autoencoder-i kërkon rreth 27 sekonda për fold,
      ndërsa Isolation Forest-i dhe One-Class SVM rreth një sekondë. Nëse modeli ritrajnohet një
      herë në ditë, ky dallim nuk ka rëndësi; do të kishte rëndësi vetëm me ritrajnim të
      vazhdueshëm."""),
    h3("5.3.4", "Vlerësimi me buxhet alarmesh"),
    p("""AP-ja përmbledh gjithë renditjen, ndërsa një ekip i shqyrton vetëm alarmet e para. Tabela
      më poshtë tregon çfarë ndodh kur hetohen vetëm 100 alarmet me pikë më të lartë në çdo bllok
      testimi. Ky buxhet është realist, sepse një bllok ka mesatarisht 31 mashtrime."""),
    tab(
        "budget_summary",
        "Cilësia dhe vlera e rikuperuar me 100 alarme për bllok testimi (mesatare 8-fold).",
        query="budget_k == 100",
        columns=[
            "model",
            "precision_at_k",
            "recall_at_k",
            "amount_recall_at_k",
            "net_savings_eur",
            "savings_ratio",
        ],
        rename={
            "model": "Detektori",
            "precision_at_k": "Precision@100",
            "recall_at_k": "Recall@100",
            "amount_recall_at_k": "Vlera e kapur",
            "net_savings_eur": "Kursime neto (EUR)",
            "savings_ratio": "Raporti",
        },
        sort="recall_at_k",
        ascending=False,
        round={
            "precision_at_k": 3,
            "recall_at_k": 3,
            "amount_recall_at_k": 3,
            "net_savings_eur": 0,
            "savings_ratio": 3,
        },
        font_size=9.0,
    ),
    p("""Nga ky këndvështrim renditja ndryshon. One-Class SVM kalon para Autoencoder-it: kap 49.9%
      të mashtrimeve kundrejt 43.3%, dhe 45.2% të vlerës së tyre kundrejt 38.4%. Ajo është më e mirë
      në krye të renditjes, edhe pse renditja e saj e plotë është më e dobët. Metrika duhet zgjedhur
      sipas mënyrës si do të përdoret sistemi."""),
    fig(
        "budget_recall",
        "Recall brenda buxhetit, për 50 deri në 1000 alarme për bllok.",
        15.0,
    ),
    p("""Kursimet neto kanë një maksimum të qartë (Figura [[fig:budget_savings]]). Për detektorët
      unsupervised ato rriten deri te rreth 250 alarme për bllok dhe pastaj bien, ndërsa me 1000
      alarme bëhen negative për të gjithë modelet: me tre euro për hetim, 1000 alarme kushtojnë 3000
      euro, ndërsa një bllok ka mesatarisht rreth 3900 euro mashtrime, nga të cilat kapet vetëm një
      pjesë."""),
    fig(
        "budget_savings",
        "Kursimet neto si pjesë e kursimeve të detektorit të përsosur, sipas buxhetit.",
        15.0,
    ),
]

_PH3 = [
    h2("5.4", "PH3: a ndihmon kombinimi i detektorëve"),
    p("""Pyetja e tretë hulumtuese testohet me pesë rregulla kombinimi mbi pikët e tri detektorëve
      unsupervised dhe me një procedurë lakmitare (greedy) që shton anëtarë një nga një për sa kohë
      rezultati përmirësohet. Procedura lakmitare i zgjedh anëtarët vetëm nga fold-et e mëparshme.
      Referenca e mbikëqyrur nuk hyn në asnjë ansambël, sepse kjo do ta kthente kombinimin në një
      model me etiketa."""),
    tab(
        "ensemble_summary",
        "Variantet e ansamblit kundrejt anëtarit më të mirë (mesatare 8-fold).",
        columns=[
            "varianti",
            "ap_mean",
            "ap_std",
            "vs_best_single",
            "fold_wins_vs_best_single",
            "n_folds",
        ],
        rename={
            "varianti": "Varianti",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "vs_best_single": "Δ ndaj më të mirit",
            "fold_wins_vs_best_single": "Fitore",
            "n_folds": "Fold-e",
        },
        font_size=9.5,
    ),
    p("""Rezultati është negativ. Asnjë variant nuk e kalon Autoencoder-in, i cili arrin 0.193
      (Figura [[fig:ensemble_vs_single]]). Rezultati më i mirë, 0.189, i takon procedurës lakmitare,
      por vetëm sepse në çdo fold me histori ajo zgjedh si anëtar të vetëm Autoencoder-in;
      diferencat e vogla nga Autoencoder-i vijnë nga barazimet që krijon normalizimi me rang. Vetë
      kërkimi arrin në përfundimin se asnjë kombinim nuk ndihmon. Votimi me shumicë është varianti
      më i dobët, me 0.090, më pak se gjysma e anëtarit më të mirë, gjë që pritet, sepse votimi e
      kthen çdo pikë në një vendim binar dhe humbet renditjen."""),
    fig(
        "ensemble_vs_single",
        "Diferenca e AP-së së çdo varianti të ansamblit nga Autoencoder-i, për çdo fold.",
        15.0,
    ),
    p("""Një rezultat negativ mund të vijë edhe nga akordimi i dobët, prandaj eksperimenti u
      përsërit me hiperparametrat e akorduar. Përfundimi nuk ndryshon: anëtari më i mirë arrin 0.335
      dhe ansambli më i mirë 0.334. Hipoteza H3 refuzohet në të dy regjimet e hiperparametrave."""),
    p("""Shkaku duket në të dhëna: detektorët nuk gabojnë në mënyra të pavarura. Korrelacioni i
      Spearman-it mes renditjeve të çdo çifti është mes 0.81 dhe 0.91 dhe ndryshon pak nga një fold
      në tjetrin (Figura [[fig:ensemble_rank_correlation]]); analiza e gabimeve në nënkapitullin
      5.14 e tregon të njëjtën gjë në nivel transaksioni. Teoria e ansambleve e kërkon pavarësinë e
      gabimeve si kusht që mesatarizimi të ndihmojë, dhe këtu ky kusht nuk plotësohet."""),
    fig(
        "ensemble_rank_correlation",
        "Korrelacioni i Spearman-it mes renditjeve të çdo çifti detektorësh, për çdo fold.",
        15.0,
    ),
]

_THELLIMI = [
    h2("5.5", "Studime të thelluara për secilin algoritëm"),
    p("""Krahasimi i nënkapitullit 5.3 i vlerësoi tri algoritmet në konfigurimin bazë. Ky
      nënkapitull shikon brenda secilit prej tyre, me tri qëllime: të matet sa ndryshon rezultati
      nga zgjedhjet e projektimit, të gjendet cili parametër ka rëndësi, dhe të testohet nëse
      shpjegimi i dhënë në Kapitullin 2 për sjelljen e secilit qëndron."""),
    h3("5.5.1", "Isolation Forest: ku shkon kapaciteti"),
    p("""Në Kapitullin 2 u parashtrua hipoteza se dobësia e Isolation Forest-it, kur sinjali është i
      përqendruar në pak dimensione, vjen nga zgjedhja e rastësishme e dimensionit të ndarjes. Kjo
      hipotezë përmendet shpesh në literaturë, por matet rrallë. Këtu testohet me tri prova të
      pavarura, pasi të jetë kontrolluar shpjegimi tjetër i mundshëm: akordimi i dobët."""),
    p("""Hapësira e hiperparametrave nuk është e sheshtë, kështu që shpjegimi me akordim nuk mund të
      hidhet poshtë menjëherë (Figura [[fig:iforest_surface]]). Konfigurimi bazë, me 200 pemë dhe
      nën-mostër 256, jep 0.091, ndërsa më i miri, me 800 pemë dhe nën-mostër 16 384, jep 0.151, pra
      66% më shumë. Rezultatin e lëviz madhësia e nën-mostrës, me një diferencë prej 0.070, ndërsa
      numri i pemëve e lëviz vetëm 0.009. Vlera klasike 256 për nën-mostrën rezulton e
      papërshtatshme për këtë dataset, gjë që është vetë një gjetje praktike. Vlerat e sakta për çdo
      kombinim jepen në Shtojcën E."""),
    fig(
        "iforest_surface",
        "Hapësira e hiperparametrave të Isolation Forest-it. Korniza me vija shënon konfigurimin "
        "bazë, korniza e plotë më të mirin.",
        15.0,
    ),
    p("""Megjithatë akordimi nuk e shpjegon renditjen, sepse edhe konfigurimi më i mirë mbetet nën
      Autoencoder-in dhe One-Class SVM-në në konfigurimin e tyre bazë. Prandaj testohet vetë
      mekanizmi."""),
    p("""Prova e parë hap pemët e trajnuara dhe numëron sa ndarje merr secila kolonë. Nëse hipoteza
      vlen, ndarjet duhet të shpërndahen pothuajse njësoj mbi kolonat, pavarësisht nga sa
      informative janë ato. Kjo është ajo që vërehet: pesë veçoritë më informative marrin 17.4% të
      ndarjeve, ndërsa nga rastësia pritet 17.2%, dhe korrelacioni i Spearman-it mes përdorimit të
      një kolone dhe fuqisë së saj diskriminuese është 0.10 (p = 0.59). Algoritmi nuk i dallon
      kolonat e dobishme (Figura [[fig:iforest_capacity]], djathtas)."""),
    fig(
        "iforest_capacity",
        "Përdorimi i kolonave nga Isolation Forest-i. Majtas: ndryshimi i AP-së kur çdo pemë sheh "
        "vetëm një pjesë të kolonave. Djathtas: pjesa e ndarjeve kundrejt fuqisë diskriminuese të "
        "kolonës.",
        15.0,
    ),
    p("""Prova e dytë përjashton një shpjegim tjetër. Meqë V1 deri V28 janë komponentë kryesorë,
      ndarjet paralele me boshtet mund të ndihmohen ose të pengohen nga ky rreshtim. I njëjti pyll u
      trajnua mbi një kopje të rrotulluar rastësisht të hapësirës, ku rreshtimi zhduket ndërsa
      struktura mbetet e njëjtë. AP ndryshon vetëm me 0.007, nga 0.091 në 0.099. Orientimi i
      boshteve nuk është shpjegimi."""),
    tab(
        "iforest_rotation",
        "AP e çdo fold-i në hapësirën origjinale dhe në atë të rrotulluar.",
        pivot={"index": "fold", "columns": "hapësira", "values": "ap"},
        columns=["fold", "origjinal", "i rrotulluar"],
        rename={"fold": "Fold", "origjinal": "Origjinale", "i rrotulluar": "E rrotulluar"},
        round={"origjinal": 3, "i rrotulluar": 3},
        font_size=9.5,
    ),
    p("""Prova e tretë është më e forta, sepse ndërhyn në vend që të vëzhgojë. Nëse kapaciteti
      shpenzohet mbi kolona pa sinjal, atëherë pemët që shohin më pak kolona duhet të japin detektor
      më të mirë. Kështu ndodh: me max_features 0.20 (rreth gjashtë kolona për pemë nga 29), AP
      rritet nga 0.091 në 0.113, me përmirësim në të tetë fold-et (p = 0.0078; Figura
      [[fig:iforest_capacity]], majtas)."""),
    tab(
        "iforest_max_features_summary",
        "Efekti i kufizimit të kolonave për pemë (mesatare 8-fold).",
        rename={
            "max_features": "max_features",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "n": "Fold-e",
            "fitore_ndaj_1.0": "Fitore ndaj 1.0",
            "vs_1.0": "Δ ndaj 1.0",
        },
        round={"max_features": 2, "ap_mean": 4, "ap_std": 4, "vs_1.0": 4},
        font_size=9.5,
    ),
    p("""Të tri provat tregojnë në të njëjtin drejtim dhe secila plotëson një dobësi të tjetrës:
      numërimi i ndarjeve tregon se mekanizmi është i pranishëm, rrotullimi përjashton shpjegimin
      alternativ, dhe kufizimi i kolonave tregon se ndërhyrja mbi mekanizmin e ndryshon rezultatin
      në drejtimin e pritur."""),
    note("""Edhe pas këtyre përmirësimeve Isolation Forest-i mbetet i fundit mes tri algoritmeve në
      konfigurimin bazë. Qëllimi i nënkapitullit nuk ishte ta çonte në vendin e parë, por të
      shpjegonte pse është i fundit."""),
    h3("5.5.2", "Autoencoder: ngushtica, humbja dhe gjatësia e trajnimit"),
    p("""Për Autoencoder-in u studiuan veç e veç disa parametra: gjerësia e shtresës së fshehur
      bashkë me dimensionin latent, thellësia e enkoderit, funksioni i humbjes, dropout, weight
      decay, zhurma e hyrjes për variantin denoising dhe numri i epokave. Secili u ndryshua vetëm,
      mbi të njëjtat tetë fold-e, që efekti i tij të mos përzihet me të tjerët."""),
    tab(
        "autoencoder_studies_tidy",
        "Studimet e Autoencoder-it: një rresht për çdo konfigurim (mesatare 8-fold).",
        round={"AP": 4, "s.d.": 4},
        widths=[3.4, 6.2, 1.7, 1.7, 1.4],
        font_size=8.5,
    ),
    p("""Arkitektura ka efektin më të madh. Kalimi nga konfigurimi bazë, me shtresë të fshehur 16
      dhe dimension latent 8, te shtresa 32 me dimension latent 12 e rrit AP-në nga 0.193 në 0.354,
      me 84%, dhe ky konfigurim është më i mirë në shtatë nga tetë fold-e (Figura
      [[fig:autoencoder_architecture]]). Diferenca mes arkitekturës më të mirë dhe më të dobët është
      0.223, më e madhe se diferenca prej 0.102 mes tri algoritmeve në konfigurimin bazë."""),
    fig(
        "autoencoder_architecture",
        "AP mesatare 8-fold e Autoencoder-it sipas gjerësisë së shtresës së fshehur dhe "
        "dimensionit latent.",
        15.0,
    ),
    p("""Edhe thellësia ndihmon. Me shtresë 32 dhe dimension latent 8, enkoderi me dy shtresa arrin
      0.304 kundrejt 0.222 me një shtresë, dhe është më i mirë në të tetë fold-et; me tri shtresa
      rezultati bie në 0.235. Renditja e nënkapitullit 5.3 është pra renditje e konfigurimeve bazë
      dhe jo e algoritmeve në kapacitetin e tyre të plotë; nënkapitujt 5.9 dhe 5.16 matin sa
      ndryshon ajo kur akordohen të tre."""),
    p("""Rezultati nuk përputhet me një heuristikë të përhapur, sipas së cilës dimensioni latent
      duhet t'i afrohet dimensionit të brendshëm të të dhënave, të vlerësuar këtu 3.8 me TwoNN dhe
      7.3 me gjasën maksimale. Dimensioni latent optimal është 12, rreth tri herë vlerësimi i parë
      dhe qartë mbi të dytin. Ngushtica nuk ka për qëllim ta përshkruajë klasën normale me sa më pak
      dimensione, por të jetë mjaft e gjerë që transaksionet normale të rindërtohen mirë dhe mjaft e
      ngushtë që anomalitë të mos rindërtohen. Kur ngushtohet më shumë, të dyja klasat rindërtohen
      keq dhe dallimi mes tyre zbehet."""),
    p("""Jolineariteti ka vlerë. Rindërtimi linear me PCA, i vlerësuar me të njëjtat rangje dhe në
      të njëjtin protokoll, shërben si nivel minimal për familjen e rindërtimit (Figura
      [[fig:autoencoder_vs_linear]]). Autoencoder-i e kalon atë në të shtatë rangjet, dhe në rangun
      e tij më të mirë diferenca është 0.209. Rindërtimi linear përmirësohet vazhdimisht me rangun,
      ndërsa Autoencoder-i ka një optimum të brendshëm, gjë që është vetë një dallim mes dy
      mekanizmave."""),
    fig(
        "autoencoder_vs_linear",
        "Autoencoder-i (shtresë e fshehur 32) kundrejt rindërtimit linear me PCA, sipas "
        "dimensionit latent.",
        15.0,
    ),
    p("""Funksioni i humbjes ka gjithashtu rëndësi. Pika e anomalisë llogaritet gjithmonë si gabim
      kuadratik mesatar, që ablacioni të jetë i interpretueshëm. Trajnimi me gabim kuadratik jep
      0.193, me gabim absolut 0.111 dhe me humbje Huber 0.116, dhe gabimi kuadratik është më i miri
      në shtatë nga tetë fold-e. Përputhja mes objektivit të trajnimit dhe atij të pikëzimit ka
      efekt të matshëm. Humbjet robuste, që zakonisht rekomandohen kur ka vlera ekstreme, e dëmtojnë
      detektorin, sepse zbusin pikërisht gabimet e mëdha që mbartin sinjalin."""),
    p("""Numri i epokave jep një pamje më të ndërlikuar se sa sugjeron mesatarja. AP mesatare arrin
      kulmin në 20 epoka (0.193) dhe bie në 0.151 me 60 epoka, ndërsa humbja e trajnimit vazhdon të
      bjerë (Figura [[fig:autoencoder_training]]). Rënia vjen megjithatë kryesisht nga fold-i 1, ku
      AP zbret nga 0.76 në 0.41; në katër nga tetë fold-et trajnimi më i gjatë e rrit AP-në, dhe pa
      fold-in 1 ndryshimi mesatar është +0.002. Të dhënat nuk tregojnë një efekt të qëndrueshëm
      mbitrajnimi, por tregojnë se në periudhën me grumbullin e mashtrimeve trajnimi i gjatë dëmton
      shumë. Në çdo rast, humbja e trajnimit nuk mund të jetë kriteri i ndalimit, sepse ajo nuk
      thotë asgjë për cilësinë e zbulimit."""),
    fig(
        "autoencoder_training",
        "Trajnimi i Autoencoder-it sipas epokave. Lart: humbja e trajnimit në fold-in e fundit. "
        "Poshtë: AP sipas numrit të epokave, për çdo fold dhe mesatarisht.",
        15.0,
    ),
    p("""Regularizuesit kanë efekte të vogla. Dropout 0.1 e rrit rezultatin me 0.007 dhe weight
      decay 1e-4 me 0.016, ndërsa vlera e madhe 1e-2 e ul me 0.086. Varianti denoising, ku hyrjes i
      shtohet zhurmë gausiane, nuk ka efekt praktik: diferenca mes nivelit më të mirë dhe më të keq
      të zhurmës është nën 0.005. Ky rezultat negativ ka vlerë, sepse denoising rekomandohet shpesh
      pa kushte."""),
    h3("5.5.3", "One-Class SVM: kerneli, ν dhe kostoja e të dhënave"),
    p("""Për One-Class SVM u studiuan tre aspekte: kerneli, hapësira mbi nu dhe gamma, dhe kurba e
      të mësuarit sipas madhësisë së nën-mostrës së trajnimit. Aspekti i fundit është specifik për
      këtë algoritëm, sepse kostoja e tij rritet afërsisht në mënyrë kuadratike me numrin e mostrave
      dhe nën-mostrimi është i domosdoshëm."""),
    tab(
        "ocsvm_kernels",
        "Krahasimi i kernelëve (mesatare 8-fold).",
        rename={
            "kernel": "Kerneli",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "fit_s": "Fit (s)",
            "us_per_tx": "µs/tx",
            "support_vectors": "Vektorë mbështetës",
        },
        replace={"kernel": {"rbf": "RBF", "poly": "polinomial"}},
        round={"us_per_tx": 1, "support_vectors": 0},
        font_size=9.5,
    ),
    p("""Kerneli RBF është qartë më i miri, me 0.151, i ndjekur nga ai sigmoid me 0.053 dhe ai
      polinomial me 0.032. Kerneli linear dështon plotësisht me 0.001, në nivelin e rastësisë. Një
      kufi linear rreth klasës legjitime nuk e ndan atë nga mashtrimet, gjë që tregon se struktura e
      nevojshme është jolineare, në përputhje me krahasimin e Autoencoder-it me rindërtimin
      linear."""),
    tab(
        "ocsvm_surface",
        "AP mesatare 8-fold e One-Class SVM-së me kernel RBF sipas nu dhe gamma.",
        rename={"nu": "ν / γ"},
        fmt={"nu": "g"},
        font_size=9.5,
    ),
    p("""Maksimumi i hapësirës nu–gamma, 0.163, arrihet me nu 0.001 dhe me gamma "scale", që për
      këto të dhëna është rreth 0.036 (Figura [[fig:ocsvm_surface]]). Vlerat e vogla të nu janë më
      të mira, në përputhje me kuptimin e parametrit, i cili është kufi i sipërm për pjesën e pikave
      të trajnimit që lejohen jashtë kufirit. Vlera 0.05 e konfigurimit bazë lejon që deri në 5% e
      transaksioneve normale të mbeten jashtë, rreth 30 herë më shumë se norma e mashtrimit prej
      0.17%."""),
    fig(
        "ocsvm_surface",
        "Hapësira nu–gamma e One-Class SVM-së. Korniza me vija shënon konfigurimin bazë, korniza e "
        "plotë më të mirin.",
        15.0,
    ),
    p("""Kurba e të mësuarit jep rezultatin më të rëndësishëm operacionalisht. Rritja e nën-mostrës
      nga 1000 në 80 000 transaksione e rrit AP-në vetëm nga 0.151 në 0.158, ndërsa koha e trajnimit
      rritet nga 0.006 në 50.6 sekonda dhe kostoja e pikëzimit nga 5.2 në 188.2 mikrosekonda për
      transaksion (Figura [[fig:ocsvm_learning_curve]]). Numri i vektorëve mbështetës rritet nga 102
      në 4055, dhe meqë kostoja e pikëzimit është proporcionale me të, kjo e shpjegon plotësisht
      rritjen e kostos."""),
    tab(
        "ocsvm_learning_curve",
        "Kurba e të mësuarit e One-Class SVM-së sipas madhësisë së nën-mostrës.",
        rename={
            "train_subsample": "Nën-mostra",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "fit_s": "Fit (s)",
            "us_per_tx": "µs/tx",
            "support_vectors": "Vektorë mbështetës",
        },
        round={"ap_mean": 3, "ap_std": 3, "fit_s": 3, "us_per_tx": 1, "support_vectors": 0},
        font_size=9.5,
    ),
    fig(
        "ocsvm_learning_curve",
        "Cilësia dhe kostoja e One-Class SVM-së sipas madhësisë së nën-mostrës së trajnimit.",
        15.0,
    ),
    p("""Pasoja praktike shkon kundër idesë se më shumë të dhëna janë gjithmonë më mirë. Këtu 1000
      transaksione trajnimi japin praktikisht të njëjtën cilësi si 20 000, me kosto pikëzimi nëntë
      herë më të ulët dhe kohë trajnimi rreth 160 herë më të shkurtër. Kostoja kuadratike e
      kernelit, që në literaturë përmendet si pengesa kryesore e metodës, këtu nuk është pengesë
      reale, sepse cilësia ngopet shumë më herët se kostoja."""),
    note("""Kjo ndryshon leximin e tabelës kryesore. Kostoja prej 55.4 mikrosekondash për
      transaksion, që e bën One-Class SVM-në detektorin më të shtrenjtë, vjen nga konfigurimi dhe jo
      nga vetë algoritmi; me nën-mostër prej 1000 transaksionesh ajo bie nën gjashtë mikrosekonda pa
      humbje të matshme cilësie."""),
]

_PARAPROCESIMI = [
    h2("5.6", "Paraprocesimi"),
    p("""Të gjitha rezultatet e mësipërme u morën me StandardScaler, zgjedhja e zakonshme në
      shumicën e studimeve. Meqë të tri metodat e përcaktojnë anomalinë përmes largësisë dhe
      largësia varet plotësisht nga shkalla e veçorive, kjo zgjedhje duhet testuar."""),
    tab(
        "scaling_summary",
        "AP mesatare 8-fold për çdo paraprocesim dhe detektor.",
        rename={"Paraprocesimi": "Paraprocesimi"},
        font_size=9.0,
    ),
    p("""Efekti është i madh. Për secilin detektor unsupervised, paraprocesimi më i mirë e kalon
      StandardScaler-in në të tetë fold-et (p = 0.0078). One-Class SVM fiton 0.218 me transformimin
      kuantil uniform dhe arrin 0.368, rezultatin më të mirë unsupervised të gjithë studimit.
      Autoencoder-i fiton 0.103 me RobustScaler dhe arrin 0.296, ndërsa Isolation Forest-i fiton
      0.065 me transformimin kuantil uniform (Figura [[fig:scaling_effect]])."""),
    tab(
        "scaling_significance",
        "Testi i Friedman-it mbi shtatë opsionet dhe krahasimi i më të mirit me StandardScaler.",
        rename={
            "Friedman_chi2": "χ² Friedman",
            "p_value": "p (Friedman)",
            "Paraprocesimi_me_i_mire": "Më i miri",
            "delta_ndaj_standard": "Δ ndaj standard",
            "wilcoxon_p": "p (Wilcoxon)",
            "fitore_nga_8": "Fitore nga 8",
        },
        font_size=8.5,
    ),
    p("""Kur opsioni më i mirë zgjidhet dhe vlerësohet në të njëjtat fold-e, përfitimi mund të jetë
      i fryrë. Kontrolli prekuencial e shmang këtë: skaluesi për çdo fold zgjidhet vetëm nga fold-et
      paraardhëse. Zgjedhja është e qëndrueshme që nga fold-i i parë, dhe përfitimi mbetet: 0.206
      për One-Class SVM, 0.110 për Autoencoder-in dhe 0.045 për Isolation Forest-in, secili në
      shtatë nga shtatë fold-et (p = 0.016, vlera më e vogël e mundshme me shtatë fold-e). Për
      referencën e mbikëqyrur e njëjta procedurë e ul rezultatin me 0.025."""),
    tab(
        "scaling_prequential",
        "Skaluesi i zgjedhur vetëm nga fold-et e mëparshme kundrejt StandardScaler (fold-et 1–7).",
        round={"AP me zgjedhjen": 3, "AP me StandardScaler": 3, "Δ AP": 3, "p (Wilcoxon)": 4},
        font_size=8.5,
    ),
    p("""Krahasimi i madhësive është thelbësor. Diferenca mes paraprocesimit më të mirë dhe më të
      keq për të njëjtin detektor arrin deri në 0.355, ndërsa diferenca mes tri detektorëve me
      StandardScaler është vetëm 0.102. Mënyra si përgatiten të dhënat ka pra më shumë peshë se cili
      nga tri algoritmet zgjidhet."""),
    fig(
        "scaling_effect",
        "AP mesatare 8-fold e çdo detektori sipas paraprocesimit.",
        15.0,
    ),
    p("""Referenca e mbikëqyrur sillet ndryshe, dhe kjo asimetri ka vlerë. Asnjë paraprocesim nuk e
      përmirëson atë në mënyrë domethënëse (katër fitore nga tetë, p = 0.84). Regresioni logjistik
      mëson një drejtim diskriminues, dhe kur veçoritë shkallëzohen ndryshe ai thjesht i rregullon
      koeficientët. Për metodat gjeometrike, përkundrazi, ndryshimi i shkallës ndryshon vetë
      problemin që zgjidhin."""),
    p("""Isolation Forest-i jep AP saktësisht të njëjtë me StandardScaler, RobustScaler,
      MinMaxScaler dhe pa skalim. Kjo vjen nga algoritmi: pikat e ndarjes zgjidhen uniformisht
      brenda intervalit të vëzhguar të çdo kolone, prandaj një transformim linear i secilës kolonë i
      lë pemët të pandryshuara. Rezultatin e ndryshojnë vetëm transformimet jolineare, si ai
      kuantil."""),
    note("""Për këdo që përdor Isolation Forest kjo ka një pasojë praktike: krahasimi i skaluesve
      linearë nuk sjell asgjë, ndërsa transformimet që ndryshojnë formën e shpërndarjes mund të
      sjellin përmirësim."""),
]

_KAUZALITETI = [
    h2("5.7", "Nga korrelacioni te shkaku: ndërhyrja mbi hyrjen"),
    p("""Nënkapitulli 5.5.1 tregoi se Isolation Forest-i e shpenzon kapacitetin e tij edhe mbi
      kolona pa sinjal, dhe se është i fundit në renditje. Lidhja mes këtyre dy vëzhgimeve mbetet
      hipotezë derisa të ndërhyhet mbi mekanizmin e supozuar. Ky nënkapitull e bën këtë
      ndërhyrje."""),
    p("""Në çdo fold komponentët renditen sipas fuqisë së tyre diskriminuese, të matur vetëm mbi
      dritaren e trajnimit, dhe çdo detektor trajnohet përsëri duke parë vetëm k komponentët e parë.
      Nëse shpërndarja e ndarjeve mbi kolona pa sinjal është shkaku i dobësisë, Isolation Forest-i
      duhet të fitojë më shumë se të tjerët, dhe sidomos për k të vogël, kur kolonat pa sinjal janë
      hequr plotësisht."""),
    tab(
        "feature_selection",
        "AP mesatare 8-fold kur çdo detektor sheh vetëm k komponentët më informativë.",
        query="renditja == 'sinjali (me etiketa)'",
        columns=["model", "k", "ap_mean", "ap_std", "vs_te_gjitha"],
        rename={
            "model": "Detektori",
            "k": "k",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "vs_te_gjitha": "Δ ndaj 29 kolonave",
        },
        font_size=8.5,
    ),
    p("""Parashikimi vërtetohet. Isolation Forest-i fiton 0.530, nga 0.091 në 0.621, dhe këtë e
      arrin me k = 3, kur mbeten vetëm tri kolona (Figura [[fig:feature_selection]]). One-Class SVM
      fiton 0.360, gjithashtu me k = 3. Autoencoder-i fiton 0.397, por me k = 12. Te Autoencoder-i
      krahasimi ka një kufizim: dimensioni latent mbetet 8, kështu që për k ≤ 8 rrjeti nuk ngjesh
      fare, dhe rezultati i tij për k të vogël lidhet me arkitekturën e jo vetëm me informacionin e
      hyrjes."""),
    fig(
        "feature_selection",
        "AP mesatare 8-fold kur çdo detektor sheh vetëm k komponentët e parë, sipas dy renditjeve.",
        15.0,
    ),
    p("""Referenca e mbikëqyrur shërben si kontroll. Ajo nuk fiton asgjë, dhe çdo kufizim e dëmton:
      nga 0.734 me të gjitha kolonat në 0.610 me tri. Modeli i mbikëqyrur i peshon vetë kolonat
      sipas dobisë së tyre, prandaj heqja e tyre vetëm i heq informacion. Metodat gjeometrike nuk
      kanë një mekanizëm të tillë, dhe përfitojnë kur peshimi u jepet nga jashtë."""),
    p("""Rendi i fitimeve, me Isolation Forest-in në krye, përputhet me shpjegimin e propozuar.
      Ndërhyrja nuk i përjashton të gjitha shpjegimet e tjera të mundshme, por e bën shpjegimin me
      shpërndarjen e ndarjeve shumë më të besueshëm se një korrelacion i thjeshtë."""),
    p("""Rezultati ka një kufizim të rëndësishëm: renditja sipas fuqisë diskriminuese përdor
      etiketat historike dhe përfaqëson rastin më të mirë dhe jo një procedurë që mund të përdoret
      pa etiketa. Prandaj u testua edhe një renditje pa etiketa, sipas kurtozës së tepërt,
      heuristika klasike e kërkimit të projeksioneve (projection pursuit). Mbivendosja mes dy
      renditjeve është zero për tri kolonat e para dhe 33% për 12 kolonat e para."""),
    tab(
        "feature_selection_agreement",
        "Mbivendosja mes renditjes me etiketa dhe asaj sipas kurtozës, sipas k.",
        rename={"k": "k", "mbivendosja": "Mbivendosja"},
        fmt={"mbivendosja": ".0%"},
        font_size=9.5,
    ),
    p("""Me renditjen pa etiketa përfitimet janë shumë më të vogla. Autoencoder-i fiton 0.122 me 16
      kolona, One-Class SVM praktikisht asgjë, dhe Isolation Forest-i humbet për çdo k. Mekanizmi
      konfirmohet, por përfitimi i tij nuk arrihet pa etiketa me këtë heuristikë. Kjo e forcon
      gjetjen e nënkapitullit 5.3 për vlerën e etiketave historike: ato nuk shërbejnë vetëm për
      trajnimin e një klasifikuesi, por edhe për përgatitjen e hapësirës ku punojnë metodat
      unsupervised."""),
    h2("5.8", "Sa histori duhet mbajtur"),
    p("""Kush vendos një sistem të tillë duhet të zgjedhë mes dy politikave: të mbajë gjithë
      historikun dhe ta lërë dritaren e trajnimit të rritet, ose të mbajë një dritare rrëshqitëse me
      gjatësi të fiksuar. E para përdor më shumë të dhëna, e dyta qëndron më afër së tashmes."""),
    tab(
        "training_window_curve",
        "AP mesatare sipas gjatësisë së dritares rrëshqitëse.",
        rename={
            "model": "Detektori",
            "madhesia": "Gjatësia e dritares",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "n": "Fold-e",
        },
        font_size=9.0,
    ),
    fig(
        "training_window",
        "AP mesatare sipas gjatësisë së dritares rrëshqitëse, dhe me dritaren që përfshin gjithë "
        "historikun.",
        15.0,
    ),
    p("""Detektorët ndahen në dy grupe (Figura [[fig:training_window]]). Për Autoencoder-in dhe
      Isolation Forest-in asnjë dritare rrëshqitëse nuk e kalon historikun e plotë; diferenca është
      0.019 dhe 0.005 në favor të historikut. Për One-Class SVM, përkundrazi, një dritare prej 50
      000 transaksionesh e kalon historikun e plotë me 0.049. Referenca e mbikëqyrur përmirësohet
      vazhdimisht me sasinë e të dhënave, siç pritet nga një model i mbikëqyrur. Kolona e fundit e
      tabelës tregon në sa fold-e ishte e mundur secila gjatësi; dritarja prej 200 000
      transaksionesh ekziston vetëm në tri fold-et e fundit dhe në figurë shënohet ndryshe."""),
    p("""Mesatarisht për tri metodat unsupervised, kalimi nga 10 000 në 100 000 transaksione
      trajnimi e ndryshon AP-në vetëm nga 0.141 në 0.136. Gjatësia 200 000 nuk hyn në këtë mesatare,
      sepse do ta përziente gjatësinë e dritares me vështirësinë e fold-eve."""),
    p("""Kjo përputhet me kurbën e të mësuarit të One-Class SVM-së: sasia e të dhënave nuk është ajo
      që i kufizon metodat unsupervised mbi këtë dataset. Mbledhja e më shumë historiku, që
      zakonisht është rekomandimi i parë kur cilësia është e ulët, këtu nuk do të ndihmonte."""),
]

_ANALIZAT = [
    h2("5.9", "Sa ndikon akordimi në renditje"),
    p("""Krahasimet e mësipërme përdorën hiperparametrat bazë. Kjo është zgjedhje e paanshme kur
      burimet nuk mjaftojnë për të akorduar njësoj të gjithë algoritmet, por lë pa përgjigje pyetjen
      nëse renditja do të ishte tjetër me çdo algoritëm në kapacitetin e tij më të mirë. Prandaj i
      njëjti protokoll u përsërit me hiperparametrat e gjetur nga kërkimi mbi ndarjen e brendshme
      kohore."""),
    tab(
        "tuning_effect",
        "Efekti i akordimit mbi AP-në e blloqeve të testimit.",
        columns=[
            "Detektori",
            "AP_default",
            "AP_i_akorduar",
            "delta_test",
            "folds_te_permiresuara",
            "delta_inner",
            "delta_folde_te_pastra",
            "te_permiresuara_te_pastra",
        ],
        rename={
            "Detektori": "Detektori",
            "AP_default": "AP bazë",
            "AP_i_akorduar": "AP e akorduar",
            "delta_test": "Δ (8 fold-e)",
            "folds_te_permiresuara": "Fold-e më mirë",
            "delta_inner": "Δ e brendshme",
            "delta_folde_te_pastra": "Δ (fold-et 4–7)",
            "te_permiresuara_te_pastra": "Më mirë (4–7)",
        },
        font_size=8.5,
    ),
    p("""Në përgjithësi akordimi ndihmon: për të tre detektorët bashkë, konfigurimi i akorduar është
      më i mirë se ai bazë në të tetë fold-et (p = 0.0078), me një përfitim mesatar prej 0.071.
      Përfitimi megjithatë shpërndahet shumë pabarabartë (Figura [[fig:tuning_effect]]).
      Autoencoder-i fiton 0.142, nga 0.193 në 0.335, me përmirësim në shtatë nga tetë fold-e.
      Isolation Forest-i fiton 0.076, nga 0.091 në 0.168, në të tetë fold-et. One-Class SVM humbet
      0.005 dhe përmirësohet vetëm në dy fold-e, edhe pse në validimin e brendshëm akordimi i kishte
      dhënë 0.076."""),
    fig(
        "tuning_effect",
        "AP mesatare 8-fold para dhe pas akordimit.",
        15.0,
    ),
    p("""Siç u shpjegua në nënkapitullin 4.7, dritarja e kërkimit përmban blloqet e testimit të
      fold-eve 0 deri 3. Mbi fold-et 4 deri 7, që fillojnë pas saj dhe janë të pavarura nga kërkimi,
      pamja është e njëjtë: Autoencoder-i fiton 0.173 dhe Isolation Forest-i 0.070, të dy në katër
      nga katër fold-et, ndërsa One-Class SVM humbet 0.010 (Figura [[fig:tuning_transfer]]).
      Përfitimet nuk vijnë pra nga mbivendosja mes kërkimit dhe testimit."""),
    fig(
        "tuning_transfer",
        "Përfitimi nga akordimi në validimin e brendshëm, në të tetë fold-et dhe vetëm në fold-et "
        "4 deri 7.",
        15.0,
    ),
    p("""Pasoja për renditjen është konkrete. Me hiperparametrat bazë renditja është Autoencoder,
      One-Class SVM, Isolation Forest; me ata të akorduar bëhet Autoencoder, Isolation Forest,
      One-Class SVM. I pari mbetet i njëjtë, por dy të fundit ndërrojnë vendet."""),
    p("""Konfigurimet që gjeti kërkimi përputhen me ato të studimeve të thelluara, edhe pse të dyja
      procedurat janë të pavarura. Për Isolation Forest-in kërkimi zgjodhi nën-mostër 16 384 dhe
      pjesë kolonash 0.37, pikërisht dy parametrat që nënkapitulli 5.5.1 i gjeti vendimtarë. Për
      Autoencoder-in zgjodhi një rrjet me shtresë 64, dy shtresa enkoderi dhe dimension latent 20,
      në të njëjtin drejtim me gjetjen se arkitekturat më të gjera dhe më të thella janë më të mira.
      Kjo përputhje mes dy rrugëve të pavarura i forcon të dyja."""),
    note("""Rezultati i One-Class SVM-së tregon se akordimi mbi një dritare validimi nuk garanton
      përmirësim në një periudhë të mëvonshme. Dritarja e brendshme e validimit është vetëm një
      periudhë, dhe konfigurimi më i mirë për të nuk është domosdoshmërisht më i miri për periudhat
      që vijnë."""),
    h2("5.10", "Sa ndikojnë vendimet e protokollit"),
    p("""Dy zgjedhje protokolli, të dyja të përhapura në literaturë dhe shpesh të raportuara pa
      koment, u krahasuan mbi të njëjtat të dhëna dhe të njëjtat modele."""),
    p("""E para është prerja e vetme kronologjike 70/30 kundrejt protokollit 8-fold. Renditja e
      detektorëve është e njëjtë në të dy rastet, pa asnjë ndryshim pozicioni, kështu që prerja e
      vetme nuk e shtrembëron renditjen. Ajo që fsheh është pasiguria: shpërndarja tipike nëpër
      fold-e është 144% e vlerës mesatare, dhe një numër i vetëm nuk e tregon fare këtë (Figura
      [[fig:protocol_comparison]]). Të tre detektorët marrin vlerë më të ulët nga prerja e vetme se
      mesatarja mbi fold-et, sepse blloku i saj i testimit është një periudhë e vështirë."""),
    tab(
        "protocol_comparison",
        "Prerja e vetme kronologjike kundrejt protokollit 8-fold.",
        rename={
            "Detektori": "Detektori",
            "AP_ndarje_e_vetme": "AP (prerje e vetme)",
            "AP_8_folde": "AP (8-fold)",
            "sd_nder_folde": "s.d. nëpër fold-e",
            "diferenca": "Diferenca",
            "rangu_ndarje_e_vetme": "Rangu (prerje)",
            "rangu_8_folde": "Rangu (8-fold)",
            "ndryshim_rangu": "Δ rangu",
            "brenda_1sd": "Brenda 1 s.d.",
        },
        font_size=8.5,
    ),
    fig(
        "protocol_comparison",
        "Vlerësimi nga prerja e vetme 70/30 kundrejt vlerave të tetë fold-eve.",
        15.0,
    ),
    p("""Krahasimi i dytë ka shumë më tepër peshë. Kur e njëjta ndarje 70/30 bëhet e rastësishme dhe
      e stratifikuar në vend të kronologjikes, AP e metodave unsupervised rritet mesatarisht 3.01
      herë: 4.49 herë për Isolation Forest-in, 2.38 për Autoencoder-in dhe 2.16 për One-Class
      SVM-në."""),
    tab(
        "protocol_inflation",
        "Fryrja e AP-së kur ndarja kronologjike zëvendësohet me ndarje të rastësishme.",
        rename={
            "Detektori": "Detektori",
            "AP_kronologjik": "AP kronologjike",
            "AP_i_perzier": "AP e përzier",
            "fryrja": "Fryrja",
        },
        round={"fryrja": 2},
        font_size=9.5,
    ),
    p("""Referenca e mbikëqyrur sillet përsëri ndryshe: për të ndarja e rastësishme sjell një rënie
      të lehtë, me raport 0.92. Fryrja nuk është veti e dataset-it ose e metrikës, por pasojë e
      mënyrës se si metodat gjeometrike përfitojnë kur transaksione të së njëjtës periudhë ndodhen
      njëkohësisht në trajnim dhe në test."""),
    p("""Madhësia e efektit është shqetësuese. Fryrja prej 3.01 herë është më e madhe se raporti
      prej 2.1 herë mes algoritmit më të mirë dhe më të dobët në protokollin korrekt. Isolation
      Forest-i me ndarje të rastësishme arrin AP 0.140, sa Autoencoder-i me ndarje kronologjike.
      Zgjedhja e protokollit ndikon pra në numrin e raportuar më shumë se zgjedhja e
      algoritmit."""),
    h2("5.11", "Zhvendosja: cila popullatë lëviz"),
    p("""Rënia e cilësisë me kohën u pa tashmë në rezultatet për fold. Pyetja e dobishme është cila
      popullatë lëviz, sepse dy përgjigjet çojnë në veprime të ndryshme: nëse lëviz popullata
      normale, ritrajnimi ndihmon; nëse lëviz ajo e mashtrimeve, ritrajnimi mbi të dhëna të reja
      normale nuk ndryshon asgjë."""),
    tab(
        "drift_per_fold",
        "Zhvendosja për çdo fold, sipas popullatës, me zhurmën e PSI-së nga permutacionet.",
        columns=[
            "fold",
            "test_frauds",
            "psi_normals_mean",
            "psi_normals_over_moderate",
            "psi_frauds_mean",
            "psi_frauds_null_mean",
            "psi_frauds_excess",
            "psi_frauds_p",
            "ks_normals_median",
            "ks_frauds_median",
        ],
        rename={
            "fold": "Fold",
            "test_frauds": "Mashtrime",
            "psi_normals_mean": "PSI legjit.",
            "psi_normals_over_moderate": "Veçori mbi 0.10",
            "psi_frauds_mean": "PSI mashtr.",
            "psi_frauds_null_mean": "Zhurma",
            "psi_frauds_excess": "Teprica",
            "psi_frauds_p": "p",
            "ks_normals_median": "KS legjit.",
            "ks_frauds_median": "KS mashtr.",
        },
        round={
            "psi_normals_mean": 3,
            "psi_frauds_mean": 3,
            "psi_frauds_null_mean": 3,
            "psi_frauds_excess": 3,
            "psi_frauds_p": 3,
            "ks_normals_median": 3,
            "ks_frauds_median": 3,
        },
        font_size=8.0,
    ),
    p("""Vlerat e papërpunuara duken qartë të njëanshme. PSI mesatar për transaksionet legjitime
      është 0.141, në kufirin e poshtëm të asaj që quhet zhvendosje e moderuar, ndërsa për
      mashtrimet është 3.222, dhe te mashtrimet të 29 veçoritë e kalojnë pragun 0.10 në çdo fold.
      PSI-ja e mashtrimeve megjithatë ndjek numrin e mashtrimeve në bllok: vlera më e ulët, 0.56,
      është te fold-i 1 me 88 mashtrime, ndërsa më të lartat, 4.75 dhe 4.47, janë te dy fold-et me
      13. Kjo është anshmëria e mostrave të vogla e përshkruar në nënkapitullin 4.6.4."""),
    p("""Pas korrigjimit me permutacione përfundimi kryesor mbetet, por me përmasa më të vogla.
      Zhurma e mostrimit vetëm jep mesatarisht PSI 1.561, rreth 48% të vlerës së vëzhguar. Vlera e
      vëzhguar e kalon zhurmën në të tetë fold-et (p ≈ 0.01, vlera më e vogël e mundshme me 100
      permutacione), dhe teprica mesatare mbi zhurmën është 1.66, mbi dhjetë herë PSI-ja e
      popullatës legjitime (Figura [[fig:drift_psi_decomposition]]). Edhe zhvendosja e
      transaksioneve legjitime është reale, sepse e kalon zhurmën e saj në çdo fold, por është e
      vogël."""),
    fig(
        "drift_psi_decomposition",
        "PSI mesatar mbi 29 veçori për çdo popullatë dhe fold, me brezin e zhurmës nga "
        "permutacionet.",
        15.0,
    ),
    p("""Modeli i normalitetit, mbi të cilin janë trajnuar të tre detektorët, ndryshon pak; më shumë
      ndryshojnë mashtrimet. Ritrajnimi periodik mbi të dhëna të reja normale nuk e trajton këtë anë
      të problemit. Kjo përputhet me nënkapitullin 5.8, ku mbajtja e gjithë historikut nuk e dëmtoi
      as Autoencoder-in, as Isolation Forest-in; vetëm One-Class SVM përfitoi nga një dritare më e
      shkurtër."""),
    p("""Aftësia ndarëse e matur pa model e tregon të njëjtën gjë nga një kënd tjetër (Figura
      [[fig:drift_separability]]). Brenda dritareve të trajnimit detektori i distancës arrin AP 0.17
      deri 0.28, ndërsa në blloqet e testimit zakonisht 0.02 deri 0.10. Mashtrimet e një blloku të
      ri janë më të vështira për t'u ndarë se ato që janë parë më parë, me përjashtim të fold-it 1,
      ku grumbulli i mashtrimeve jep 0.53."""),
    fig(
        "drift_separability",
        "AP e detektorit të distancës brenda dritares së trajnimit dhe në bllokun e testimit.",
        15.0,
    ),
    p("""Monitorimi me Page-Hinkley, me prag të kalibruar me permutacione për çdo fold dhe model,
      jep sinjal zhvendosjeje në 11 nga 24 kombinimet fold-model. Zhvendosja është pra e pranishme,
      por jo e vazhdueshme."""),
    tab(
        "drift_page_hinkley",
        "Pikat e ndryshimit sipas testit Page-Hinkley mbi pikët e anomalisë. Kolona e fundit "
        "tregon sa ishte përpunuar nga blloku kur u dha sinjali i parë.",
        columns=[
            "fold",
            "model",
            "threshold",
            "n_change_points",
            "first_change_index",
            "detected_at_fraction",
        ],
        rename={
            "fold": "Fold",
            "model": "Detektori",
            "threshold": "Pragu",
            "n_change_points": "Sinjale",
            "first_change_index": "Mesazhi i sinjalit të parë",
            "detected_at_fraction": "Pjesa e bllokut",
        },
        round={"threshold": 1, "detected_at_fraction": 2},
        font_size=9.0,
    ),
    h2("5.12", "Ku e drejtojnë vëmendjen detektorët"),
    p("""Nënkapitulli 5.5.1 mati shpërndarjen e ndarjeve brenda Isolation Forest-it. Këtu e njëjta
      pyetje shtrohet për të tre detektorët, me një atribuim të jashtëm që nuk varet nga struktura e
      brendshme e modelit dhe mund të krahasohet mes tyre. Për secilin detektor matet sa përputhet
      vëmendja e tij me sinjalin që mbart secila kolonë, i matur si fuqi diskriminuese
      njëvariablëshe."""),
    tab(
        "explain_signal_agreement",
        "Përputhja mes atribuimit të çdo detektori dhe sinjalit të kolonave (Spearman).",
        rename={
            "atribuimi": "Atribuimi",
            "spearman_vs_auc_gap": "ρ (Spearman)",
            "p_value": "p",
            "top3": "Tri kolonat kryesore",
        },
        replace={
            "atribuimi": {
                "autoencoder (gabim rindërtimi)": "Autoencoder (gabim rindërtimi)",
                "autoencoder (permutim)": "Autoencoder (permutim)",
                "isolation forest (SHAP)": "Isolation Forest (SHAP)",
                "isolation forest (permutim)": "Isolation Forest (permutim)",
                "one-class SVM (permutim)": "One-Class SVM (permutim)",
                "sinjali univariat (referencë)": "Sinjali njëvariablësh (referencë)",
            }
        },
        round={"spearman_vs_auc_gap": 2},
        font_size=9.5,
    ),
    p("""Krahasimi i drejtë përdor të njëjtën masë për të tre, rëndësinë me permutim (Figura
      [[fig:explain_attention_vs_signal]]). Me këtë masë përputhja me sinjalin është 0.50 për
      One-Class SVM (p = 0.006), 0.36 për Autoencoder-in (p = 0.054) dhe −0.03 për Isolation
      Forest-in (p = 0.88). Gabimi i rindërtimit të Autoencoder-it përputhet me sinjalin edhe më
      fort (0.75), por ai matet mbi mashtrimet dhe është i lartë pikërisht aty ku mashtrimet janë të
      pazakonta, kështu që një pjesë e kësaj përputhjeje vjen nga vetë mënyra e matjes dhe nuk
      krahasohet me dy masat e tjera."""),
    p("""Rezultati i qëndrueshëm është se vëmendja e Isolation Forest-it nuk përkon me sinjalin me
      asnjërën masë (SHAP jep 0.02). Renditja mes Autoencoder-it dhe One-Class SVM-së varet nga masa
      e përdorur, prandaj nuk nxirret përfundim prej saj. Për këtë arsye hipoteza e ndërhyrjes në
      nënkapitullin 5.7 u formulua për Isolation Forest-in."""),
    fig(
        "explain_attention_vs_signal",
        "Ndikimi i permutimit të çdo kolone kundrejt fuqisë së saj diskriminuese. Pikat e zeza "
        "janë pesë kolonat më informative.",
        15.0,
    ),
    p("""Kjo duket edhe te kolonat kryesore. Sipas sinjalit njëvariablësh, tri kolonat më
      informative janë V14, V4 dhe V12. Gabimi i rindërtimit të Autoencoder-it vë në krye V14, V17
      dhe V12, dy nga tri të njëjtat, ndërsa SHAP i Isolation Forest-it vë V25, V4 dhe V15, ku V25
      është ndër kolonat me sinjal më të dobët. Në 28 nga 29 kolona Autoencoder-i i rindërton
      mashtrimet më keq se transaksionet legjitime; për V14 gabimi është rreth 76 herë më i madh,
      për V12 dhe V17 mbi 40 herë (Figura [[fig:explain_ae_reconstruction]])."""),
    fig(
        "explain_ae_reconstruction",
        "Gabimi i rindërtimit të Autoencoder-it për çdo kolonë: mashtrime ndaj transaksioneve "
        "legjitime.",
        15.0,
    ),
    h2("5.13", "Pragu adaptiv me dritare rrëshqitëse"),
    p("""Një prag i fiksuar nga kuantili i pikëve të trajnimit ka një dobësi që del vetëm në
      rrjedhë: kur shpërndarja e pikëve zhvendoset, zhvendoset edhe numri i alarmeve, dhe ekipi merr
      një ngarkesë të paparashikueshme pikërisht kur diçka ka ndryshuar. Pragu adaptiv e mban pragun
      te një kuantil i pikëve më të fundit, pa përdorur asnjë etiketë."""),
    tab(
        "adaptive_threshold_summary",
        "Pragu statik kundrejt atij adaptiv (mesatare 8-fold).",
        rename={
            "model": "Detektori",
            "regjimi": "Regjimi",
            "alert_rate": "Norma e alarmeve",
            "alert_rate_cv": "CV e ngarkesës",
            "worst_slice_rate": "Piku",
            "precision": "Precision",
            "recall": "Recall",
            "f1": "F1",
            "alerts_per_block": "Alarme për bllok",
        },
        fmt={"alert_rate": ".2%", "worst_slice_rate": ".1%"},
        round={"alert_rate_cv": 2, "precision": 3, "recall": 3, "f1": 3, "alerts_per_block": 1},
        font_size=9.0,
    ),
    p("""Qëllimi kryesor arrihet. Koeficienti i variacionit të normës së alarmeve bie nga 0.84 në
      0.62, dhe piku i ngarkesës nga 1.8% në 1.7% të transaksioneve (Figura
      [[fig:adaptive_alert_rate]]). Ngarkesa e hetimeve bëhet më e parashikueshme."""),
    fig(
        "adaptive_alert_rate",
        "Pjesa e transaksioneve që marrin alarm në çdo nën-bllok, me prag statik dhe adaptiv.",
        15.0,
    ),
    p("""Efekti mbi cilësinë i ndan modelet në dy grupe, prandaj raportohet veçmas (Figura
      [[fig:adaptive_tradeoff]]). Për të tre detektorët unsupervised F1 rritet, nga 0.124 në 0.166
      mesatarisht, dhe rritet te secili prej tyre. Për referencën e mbikëqyrur F1 bie nga 0.720 në
      0.535."""),
    p("""Mekanizmi lexohet te numri i alarmeve. Me pragun statik, detektorët unsupervised japin në
      blloqet e testimit më pak alarme se sa synohet, 0.15% deri 0.20% e transaksioneve; pragu
      adaptiv e çon këtë në rreth 0.25%, ose 54 deri 56 alarme për bllok në vend të 33 deri 44.
      Recall-i rritet (te Autoencoder-i nga 0.158 në 0.312), ndërsa precision-i mbetet afërsisht i
      njëjtë, dhe F1 rritet. Te referenca e mbikëqyrur alarmet rriten nga 31 në 51 për bllok, por
      precision-i bie nga 0.756 në 0.443: pragu statik i saj ishte tashmë i kalibruar mirë, dhe
      pragu adaptiv e detyron modelin të japë më shumë alarme se ç'duhet. Pragu adaptiv i përshtatet
      pra shtresës unsupervised, jo një modeli të kalibruar."""),
    fig(
        "adaptive_tradeoff",
        "Paqëndrueshmëria e ngarkesës dhe F1 me pragun statik dhe me atë adaptiv, për çdo model.",
        15.0,
    ),
    h2("5.14", "Cilat mashtrime nuk kapen"),
    p("""Metrikat mesatare nuk tregojnë cilat transaksione kapen. Në këtë nënkapitull, me buxhet
      prej 100 alarmesh për bllok, çdo mashtrim ndiqet veçmas nëpër të tetë fold-et dhe regjistrohet
      sa detektorë e arrijnë."""),
    tab(
        "error_analysis_coverage",
        "Mashtrimet sipas numrit të detektorëve që i arrijnë me 100 alarme për bllok.",
        rename={
            "n_detektore": "Detektorë që e kapin",
            "mashtrime": "Mashtrime",
            "shuma_mesatare": "Shuma mesatare",
            "norma_z_mediane": "‖z‖ mediane",
            "pjesa": "Pjesa",
        },
        round={"shuma_mesatare": 2, "norma_z_mediane": 1},
        fmt={"pjesa": ".0%"},
        font_size=9.5,
    ),
    p("""Nga 251 mashtrimet e tetë blloqeve të testimit, 93 (37%) nuk i arrin asnjë detektor, ndërsa
      66 (26%) i arrijnë të tre njëkohësisht. Vetëm 28 (11%) i arrin saktësisht një detektor (Figura
      [[fig:error_analysis]], majtas). Kjo shpërndarje, me shumicën e mashtrimeve në dy skajet dhe
      pak të kapura nga një detektor i vetëm, e shpjegon pse ansambli nuk ndihmon: detektorët nuk
      sjellin informacion plotësues."""),
    fig(
        "error_analysis",
        "Mbulimi i mashtrimeve nga tre detektorët me 100 alarme për bllok. Majtas: mashtrimet "
        "sipas numrit të detektorëve që i arrijnë. Djathtas: distanca nga qendra legjitime e "
        "mashtrimeve të arritura dhe të paarritura.",
        15.0,
    ),
    p("""Mashtrimet që nuk arrihen kanë një tipar të përbashkët: ndodhen më afër popullatës
      legjitime, me distancë mediane 9.7 kundrejt 21.6 për ato që i arrin të paktën një detektor
      (Figura [[fig:error_analysis]], djathtas). Ky është kufiri gjeometrik i nënkapitullit 5.1, i
      parë në nivel transaksioni."""),
    p("""Krahasimi me referencën e mbikëqyrur është gjetja më e rëndësishme e këtij nënkapitulli. Me
      të njëjtin buxhet prej 100 alarmesh, ajo kap 59% të mashtrimeve që nuk i arrin asnjë detektor
      unsupervised. Informacioni që i dallon këto transaksione ekziston pra në të dhëna, por nuk ka
      formën që mund ta shohë një detektor distancash; ndodhet në një drejtim diskriminues që e gjen
      vetëm mbikëqyrja."""),
    tab(
        "error_analysis_dark_set",
        "Mashtrimet e arritura nga të paktën një detektor dhe ato që nuk i arrin asnjë.",
        rename={
            "grupi": "Grupi",
            "n": "n",
            "shuma_mediane": "Shuma mediane",
            "norma_z_mediane": "‖z‖ mediane",
            "kapur_nga_LR": "Kapur nga referenca",
        },
        round={"shuma_mediane": 2, "norma_z_mediane": 1},
        fmt={"kapur_nga_LR": ".0%"},
        font_size=9.5,
    ),
    p("""Mashtrimet e paarritura nuk janë transaksione të vogla që humbasin në zhurmë: shuma e tyre
      mediane është 17.39 euro, kundrejt 9.36 euro për ato që kapen. Ato nuk janë as të
      parëndësishme financiarisht, as të dallueshme gjeometrikisht, dhe kjo e përshkruan pjesën më
      të vështirë të problemit."""),
    h2("5.15", "A mund të zgjidhet një konfigurim pa etiketa"),
    p("""Akordimi i mësipërm përdor etiketa historike mbi një dritare të brendshme validimi. Nëse
      etiketat nuk ekzistojnë fare, mbetet pyetja nëse një kriter pa etiketa mund t'i zëvendësojë. U
      testuan dy kritere të tilla, Excess-Mass dhe Mass-Volume, të llogaritura mbi nënhapësira të
      rastësishme me dimension të ulët."""),
    tab(
        "unsupervised_selection",
        "Konfigurimi i zgjedhur nga kriteret pa etiketa dhe ai i zgjedhur me etiketa.",
        rename={
            "Konfigurime": "Konfigurime në rrjetë",
            "EM përputhet": "EM përputhet me AP",
            "MV përputhet": "MV përputhet me AP",
            "Humbja e AP me EM": "Humbja e AP-së me EM",
            "rho(AP, EM)": "ρ(AP, EM)",
            "rho(AP, −MV)": "ρ(AP, −MV)",
        },
        round={
            "Humbja e AP me EM": 3,
            "Humbja relative": 2,
            "rho(AP, EM)": 2,
            "rho(AP, −MV)": 2,
        },
        transpose="",
        font_size=8.5,
    ),
    p("""Rezultati është kryesisht negativ. Excess-Mass zgjedh të njëjtin konfigurim si kriteri me
      etiketa për zero nga tre detektorë, dhe Mass-Volume për një nga tre. Kur zgjedhjet ndryshojnë,
      humbja mesatare është 89% e diferencës mes konfigurimit më të mirë dhe më të keq të rrjetës,
      kështu që zgjedhja pa etiketa është më afër më të keqit se më të mirit (Figura
      [[fig:unsupervised_selection]])."""),
    p("""Raportohen të dy kriteret, sepse nuk pajtohen me njëri-tjetrin: korrelacioni mesatar i
      renditjes së tyre me atë me etiketa është −0.55 për Excess-Mass dhe +0.30 për Mass-Volume.
      Raportimi vetëm i njërit do ta bënte përfundimin çështje zgjedhjeje dhe jo matjeje."""),
    fig(
        "unsupervised_selection",
        "Renditja e konfigurimeve sipas AP-së dhe sipas Excess-Mass, brenda rrjetës së çdo "
        "detektori.",
        15.0,
    ),
    p("""Metoda ka edhe një kufizim të vetin. Vlerësimi i masës Lebesgue kërkon nënhapësira me
      dimension të ulët, dhe brenda një nënhapësire pesëdimensionale çdo hiperparametër që lidhet me
      një dimension më të lartë humbet kuptimin. Prandaj rindërtimi linear me PCA u përjashtua,
      ndërsa për Autoencoder-in u testuan vetëm dimensione latente më të vogla se ai i nënhapësirës.
      Ky është kufizim i vetë përzgjedhjes pa etiketa mbi nënhapësira, jo hollësi implementimi."""),
    h2("5.16", "Secili detektor në konfigurimin e tij më të mirë"),
    p("""Rezultatet e mësipërme ndryshojnë një parametër në një kohë, gjë që lejon izolimin e
      efekteve, por lë një pyetje të fundit: sa arrin secili detektor kur asgjë nuk mbetet në vlerën
      bazë? Dizajni faktorial 2×2 i përgjigjet kësaj, duke kombinuar hiperparametrat bazë dhe të
      akorduar me StandardScaler dhe me paraprocesimin që nënkapitulli 5.6 gjeti më të mirë për
      secilin detektor."""),
    tab(
        "best_effort",
        "AP mesatare 8-fold në katër qelizat e dizajnit 2×2.",
        columns=[
            "model",
            "parazgjedhur / standard",
            "parazgjedhur / më i miri",
            "i akorduar / standard",
            "i akorduar / më i miri",
        ],
        rename={
            "model": "Detektori",
            "parazgjedhur / standard": "Bazë",
            "parazgjedhur / më i miri": "Vetëm paraprocesimi",
            "i akorduar / standard": "Vetëm akordimi",
            "i akorduar / më i miri": "Të dyja",
        },
        round={
            "parazgjedhur / standard": 3,
            "parazgjedhur / më i miri": 3,
            "i akorduar / standard": 3,
            "i akorduar / më i miri": 3,
        },
        font_size=9.5,
    ),
    p("""Në qelizën e tij më të mirë, One-Class SVM arrin 0.368 me transformim kuantil dhe
      hiperparametra bazë, Autoencoder-i 0.335 me akordim dhe StandardScaler, dhe Isolation Forest-i
      0.320 me të dyja ndërhyrjet bashkë (Figura [[fig:best_effort]]). One-Class SVM kalon në krye,
      ndërsa Isolation Forest-i mbetet i fundit, por vetëm 0.05 pas tij."""),
    fig(
        "best_effort",
        "AP mesatare 8-fold e çdo detektori në katër qelizat e dizajnit 2×2.",
        15.0,
    ),
    p("""Më e rëndësishme është sa ngushtohet diferenca. Me hiperparametrat bazë dhe StandardScaler,
      diferenca mes detektorit më të mirë dhe më të dobët është 0.102, me raport 2.1 herë. Kur
      secili vlerësohet në qelizën e tij më të mirë, ajo bie në 0.049, me raport vetëm 1.15 herë.
      Pjesa më e madhe e asaj që dukej si dallim mes algoritmeve është pra dallim në atë se sa mirë
      u përshtaten këtyre të dhënave vlerat bazë."""),
    tab(
        "best_effort_interaction",
        "Kontributi i paraprocesimit, i akordimit dhe ndërveprimi mes tyre për çdo detektor.",
        rename={
            "Detektori": "Detektori",
            "bazë": "AP bazë",
            "vetëm paraprocesim": "Efekti i paraprocesimit",
            "vetëm akordim": "Efekti i akordimit",
            "të dyja": "Efekti i të dyjave",
            "shuma e efekteve": "Shuma e dy efekteve",
            "ndërveprimi": "Ndërveprimi",
            "qeliza më e mirë": "Qeliza më e mirë",
            "AP më i mirë i arritshëm": "AP në qelizën më të mirë",
        },
        round={
            "bazë": 3,
            "vetëm paraprocesim": 3,
            "vetëm akordim": 3,
            "të dyja": 3,
            "shuma e efekteve": 3,
            "ndërveprimi": 3,
            "AP më i mirë i arritshëm": 3,
        },
        transpose="",
        font_size=9.0,
    ),
    p("""Dy ndërhyrjet nuk mblidhen. Për Autoencoder-in ndërveprimi është −0.208 dhe për One-Class
      SVM −0.156, kështu që për të dy kombinimi i të dyjave jep më pak se ndërhyrja e vetme më e
      mirë. Për Isolation Forest-in ndërveprimi është pozitiv, +0.087, dhe vetëm për të kombinimi
      është zgjedhja e duhur."""),
    p("""Shpjegimi i mundshëm është se dy ndërhyrjet trajtojnë pjesërisht të njëjtin problem.
      Akordimi i përshtat hiperparametrat me shkallën dhe formën e hapësirës ekzistuese, ndërsa
      paraprocesimi e ndryshon vetë hapësirën; kur bëhen të dyja, hiperparametrat e zgjedhur për
      hapësirën e vjetër nuk i përshtaten asaj të re. Isolation Forest-i bën përjashtim sepse
      parametrat e tij më të rëndësishëm, madhësia e nën-mostrës dhe pjesa e kolonave, nuk varen nga
      shkalla e veçorive."""),
    note("""Ky nënkapitull duhet lexuar si kufi i sipërm optimist dhe jo si vlerësim i paanshëm.
      Paraprocesimi dhe hiperparametrat u zgjodhën nga studime që i kanë parë të njëjtat blloqe
      testimi, prandaj vlerat përmbajnë një përzgjedhje pas faktit. Vlerësimi i paanshëm mbetet ai i
      nënkapitullit 5.3; qëllimi këtu është të tregohet sa ndryshon renditja kur vlerat bazë
      zëvendësohen, jo të jepet një numër i ri për krahasim me literaturën."""),
]

BLOCKS = (
    _HYRJE
    + _GJEOMETRIA
    + _PH1
    + _PH2
    + _PH3
    + _THELLIMI
    + _PARAPROCESIMI
    + _KAUZALITETI
    + _ANALIZAT
)

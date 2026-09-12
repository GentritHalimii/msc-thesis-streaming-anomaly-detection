"""Kapitulli 8 — SHTOJCAT."""

from blocks import bullets, h1, h2, numbers, p, tab

BLOCKS = [
    h1("8", "Shtojcat"),
    h2("8.1", "Shtojca A: riprodhimi i rezultateve"),
    p("""I gjithë studimi riprodhohet nga kodi burimor i shoqëruar. Dataset-i nuk përfshihet në
      depo për arsye licencimi dhe madhësie; ai shkarkohet nga Kaggle dhe vendoset në shtegun
      data/raw/creditcard.csv. Sekuenca e plotë e komandave është si më poshtë, dhe secila prej
      tyre shkruan një manifest me SHA-në e commit-it, hash-in e konfigurimit dhe versionet e
      paketave."""),
    numbers(
        [
            "make setup, krijon mjedisin virtual me Python 3.12 dhe instalon varësitë e fiksuara "
            "nga lockfile-i.",
            "make test, ekzekuton testet njësi, përfshirë ato që verifikojnë mungesën e rrjedhjes "
            "së informacionit, konventën e shenjës së pikëve dhe stilin e vetë punimit.",
            "make train, përshtat modelet mbi ndarjen 70/30 dhe ruan artefaktet.",
            "make protocol, ekzekuton protokollin rolling-origin me tetë fold-e dhe ruan matricat "
            "e pikëve mbi të cilat mbështetet çdo analizë e mëvonshme.",
            "make tune dhe make protocol-tuned, kryejnë kërkimin e hiperparametrave mbi ndarjen e "
            "brendshme kohore dhe pastaj ri-ekzekutojnë të gjithë protokollin me to.",
            "make evaluate, gjeneron tabelat dhe figurat që lexohen nga matricat e ruajtura të "
            "pikëve, pra pa ripërshtatur asnjë model; ky hap zgjat minuta.",
            "make deep-studies, ekzekuton studimet e thelluara për secilin algoritëm, "
            "karakterizimin gjeometrik, studimin e paraprocesimit, ndërhyrjen mbi hyrjen dhe "
            "dizajnin faktorial; këto ripërshtatin modelet nga fillimi dhe zgjatin orë, prandaj "
            "mbahen të ndara nga hapi i mësipërm.",
            "docker compose -f docker/docker-compose.yml up -d, ngre Kafka-n në modalitetin KRaft, "
            "PostgreSQL-in dhe Grafana-n.",
            "make test-integration, verifikon barazinë e pikëve mes regjimit offline dhe atij në "
            "rrjedhë kundrejt broker-it të vërtetë, si dhe qarkullimin e plotë të të dhënave nëpër "
            "PostgreSQL.",
            "make stream dhe make latency-report, ekzekutojnë skanimin e vonesës dhe prodhojnë "
            "tabelat operacionale.",
            "make thesis, gjeneron këtë dokument nga rezultatet e ruajtura.",
            "make webapp, ngre panelin interaktiv mbi të njëjtat rezultate në "
            "http://127.0.0.1:8800, nga i cili çdo hap i mësipërm mund të ri-ekzekutohet edhe "
            "nga shfletuesi.",
        ]
    ),
    p("""Determinizmi u verifikua empirikisht dhe jo vetëm i deklaruar. Dy cikle të plota dhe të
      pavarura ritrajnimi e vlerësimi prodhuan tabela metrike identike, me përjashtim të
      kolonave të kohës dhe të memories, të cilat matin burimet dhe jo rezultatin. Kontrolli më
      i rreptë u bë në nivel vektori: ripërshtatja e të katër modeleve mbi fold-in e parë dhe
      krahasimi i pikëve me ato të ruajtura më parë jep barazi bit-për-bit për të katër, edhe
      kur makina është nën ngarkesë tjetër, çka përjashton varësinë nga renditja e fijeve të
      ekzekutimit. Kjo mundësohet nga fiksimi i seed-it në një vend të vetëm, nga aktivizimi i
      algoritmeve deterministe në bibliotekën e rrjetave nervore, dhe nga ruajtja e pikëve me
      precizion të plotë."""),
    h2("8.2", "Shtojca B: struktura e depos së kodit"),
    p("""Kodi është organizuar sipas përgjegjësive dhe jo sipas eksperimenteve, që komponentët
      të ripërdoren mes regjimit offline dhe atij në rrjedhë."""),
    bullets(
        [
            "config/, një skedar i vetëm YAML me të gjithë parametrat: seed-in, raportin e "
            "ndarjes, "
            "gjeometrinë e protokollit, hiperparametrat e secilit model, buxhetet e alarmeve dhe "
            "konfigurimin e Kafka-s dhe PostgreSQL-it.",
            "src/data/, leximi, renditja kronologjike, ndarja dhe shtatë opsionet e paraprocesimit "
            "që krahasohen në studim.",
            "src/models/, një modul për detektor, të gjithë pas së njëjtës ndërfaqe "
            "fit/score/save/load, plus regjistri që i ndërton nga konfigurimi.",
            "src/evaluation/, protokolli rolling-origin, metrikat, karakterizimi gjeometrik, "
            "metrikat operacionale, kriteret e përzgjedhjes pa etiketa, testet statistikore, "
            "analiza e zhvendosjes, kombinimi i pikëve dhe shtresa e raportimit.",
            "src/streaming/, producer-i me ritëm të kontrolluar, consumer-i me prag statik ose "
            "adaptiv, dhe serializimi.",
            "src/storage/, persistimi në PostgreSQL me shkrime të grumbulluara.",
            "experiments/, një skript i ekzekutueshëm për çdo eksperiment; asnjë prej tyre nuk "
            "përmban logjikë modelimi.",
            "tests/, testet e rrjedhjes, të protokollit, të kontratës së modeleve, të gjeometrisë, "
            "të metrikave, të statistikave, të stilit të punimit dhe testet e integrimit kundrejt "
            "Kafka-s dhe PostgreSQL-it.",
            "docker/, konfigurimi i Kafka-s, PostgreSQL-it dhe Grafana-s, përfshirë burimin e të "
            "dhënave dhe panelin e provizionuar nga skedarë.",
            "thesis/, kodi që gjeneron këtë dokument nga rezultatet e ruajtura.",
        ]
    ),
    h2("8.3", "Shtojca C: hiperparametrat dhe mekanizmat"),
    p("""Tabela më poshtë liston mekanizmin e pikëzimit, koston asimptotike të trajnimit dhe
      hiperparametrat e parazgjedhur për secilin detektor. Vlerat janë ato të skedarit të
      konfigurimit dhe janë nxjerrë programatikisht nga regjistri i modeleve në momentin e
      gjenerimit të këtij dokumenti."""),
    tab("model_zoo", "Hiperparametrat dhe karakteristikat e detektorëve.", font_size=7.5),
    h2("8.4", "Shtojca D: rezultatet e plota për fold"),
    p("""Tabela kryesore e Kapitullit 5 raporton mesataret nëpër fold-e. Tabela më poshtë jep
      vlerat e papërpunuara për fold, që lexuesi të mund të verifikojë shpërhapjen dhe të
      vlerësojë vetë qëndrueshmërinë."""),
    tab(
        "benchmark_per_fold",
        "Average Precision dhe metrikat e pragut për fold, për të katër modelet.",
        columns=[
            "fold",
            "model",
            "test_frauds",
            "ap",
            "roc_auc",
            "precision_thr",
            "recall_thr",
            "f1_thr",
            "recall_at_100",
        ],
        rename={
            "fold": "Fold",
            "model": "Modeli",
            "test_frauds": "Mashtrime",
            "ap": "AP",
            "roc_auc": "ROC-AUC",
            "precision_thr": "Precision",
            "recall_thr": "Recall",
            "f1_thr": "F1",
            "recall_at_100": "Recall@100",
        },
        sort=["model", "fold"],
        round={
            "ap": 4,
            "roc_auc": 4,
            "precision_thr": 4,
            "recall_thr": 4,
            "f1_thr": 4,
            "recall_at_100": 4,
        },
        font_size=8.0,
    ),
    h2("8.5", "Shtojca E: rezultatet e ndarjes së vetme 70/30"),
    p("""Për krahasueshmëri me literaturën dhe me protokollin e përcaktuar në projekt-propozim,
      tabela më poshtë jep rezultatet nën ndarjen e vetme kronologjike 70/30. Kolonat e pragut
      orakull janë kufi i sipërm i paarritshëm dhe nuk duhen krahasuar me kolonat e pragut të
      nxjerrë nga trajnimi."""),
    tab(
        "metrics_main",
        "Rezultatet nën ndarjen e vetme kronologjike 70/30, me pragun nga trajnimi dhe pragun "
        "orakull të raportuar veçmas.",
        columns=[
            "model",
            "ap",
            "roc_auc",
            "precision_pct",
            "recall_pct",
            "f1_pct",
            "f1_oracle",
            "fit_time_s",
            "inference_us_per_tx",
        ],
        rename={
            "model": "Modeli",
            "ap": "AP",
            "roc_auc": "ROC-AUC",
            "precision_pct": "Precision",
            "recall_pct": "Recall",
            "f1_pct": "F1",
            "f1_oracle": "F1 (orakull)",
            "fit_time_s": "Trajnimi (s)",
            "inference_us_per_tx": "µs/tx",
        },
        round={
            "ap": 4,
            "roc_auc": 4,
            "precision_pct": 4,
            "recall_pct": 4,
            "f1_pct": 4,
            "f1_oracle": 4,
            "fit_time_s": 2,
            "inference_us_per_tx": 3,
        },
        font_size=8.5,
    ),
    p("""Pasiguria kryesore e këtij punimi raportohet si shpërhapje nëpër tetë fold-e, e cila
      mat sa lëviz rezultati kur ndryshon periudha. Ajo nuk e mat pasigurinë e mostrimit brenda
      një bashkësie të vetme testimi, e cila është pyetje tjetër dhe kërkon procedurë tjetër.
      Për prerjen e vetme kronologjike 70/30 ajo nxirret me riparashtrim bootstrap mbi
      transaksionet e bashkësisë së testimit [@efron1993]."""),
    tab(
        "bootstrap_ci",
        "Average Precision mbi prerjen e vetme 70/30 me interval besimi 95 për qind, nxjerrë me "
        "riparashtrim bootstrap mbi transaksionet e bashkësisë së testimit.",
        rename={
            "model": "Modeli",
            "ap": "AP",
            "ap_ci95_low": "Kufiri i poshtëm",
            "ap_ci95_high": "Kufiri i sipërm",
        },
        round={"ap": 4, "ap_ci95_low": 4, "ap_ci95_high": 4},
        font_size=9.5,
    ),
    tab(
        "bootstrap_pairwise",
        "Diferencat e çiftuara mes modeleve mbi të njëjtat riparashtrime bootstrap. Kolona e "
        "fundit tregon pjesën e riparashtrimeve ku diferenca ruan shenjën.",
        rename={
            "comparison": "Krahasimi",
            "delta_ap_mean": "Δ AP",
            "delta_ci95_low": "Kufiri i poshtëm",
            "delta_ci95_high": "Kufiri i sipërm",
            "frac_replicates_positive": "Pjesa pozitive",
        },
        round={"delta_ap_mean": 4, "delta_ci95_low": 4, "delta_ci95_high": 4},
        font_size=9.0,
    ),
    p("""Krahasimi mes kësaj tabele dhe testeve të Kapitullit 5 ndriçon një dallim që shpesh
      ngatërrohet. Mbi prerjen e vetme, diferenca mes Autoencoder-it dhe One-Class SVM-së e
      ruan shenjën në njëqind për qind të riparashtrimeve, pra brenda asaj dritareje ajo është
      e sigurt. Mbi tetë fold-e i njëjti krahasim nuk arrin domethënie, sepse aty pyetja nuk
      është nëse diferenca ekziston brenda një periudhe, por nëse ajo qëndron nga një periudhë
      në tjetrën. Të dyja janë të vërteta dhe matin gjëra të ndryshme; raportimi i vetëm i së
      parës do të mbivlerësonte qëndrueshmërinë e renditjes."""),
    h2("8.6", "Shtojca F: sipërfaqja e plotë e Isolation Forest-it"),
    p("""Sipërfaqja e hiperparametrave paraqitet në Kapitullin 5 si figurë. Tabela më poshtë jep
      vlerat e sakta, që lexuesi të mund të verifikojë se ku ndodhet maksimumi dhe sa i sheshtë
      është rajoni rreth tij."""),
    tab(
        "iforest_surface",
        "Average Precision mesatar mbi tetë fold-e për çdo kombinim të numrit të pemëve dhe "
        "madhësisë së nën-mostrës.",
        rename={"n_estimators": "Pemë"},
        font_size=9.0,
    ),
    h2("8.7", "Shtojca G: testet automatike"),
    p("""Disiplina metodologjike e përshkruar në Kapitullin 4 nuk mbetet vetëm në tekst; ajo
      është e koduar në teste që ekzekutohen me çdo ndryshim. Grupet kryesore janë si më
      poshtë."""),
    bullets(
        [
            "Testet e ndarjes: çdo vulë kohore e trajnimit paraprin çdo vulë të testimit; blloqet "
            "nuk mbivendosen dhe e mbulojnë rrjedhën pa boshllëqe; ndarja është deterministe mes "
            "ekzekutimeve.",
            "Testet e rrjedhjes së informacionit: statistikat e skaluesit janë identike me "
            "momentet "
            "e dritares së trajnimit dhe nuk ndryshojnë kur transformohen të dhënat e testimit; "
            "kolona Time nuk gjendet mes veçorive hyrëse.",
            "Testet e kontratës së modeleve: për secilin detektor, pikat e injektuara "
            "artificialisht "
            "si ekstreme marrin pikë më të larta se mostrat normale; ruajtja dhe ringarkimi japin "
            "pikë identike; dy përshtatje të njëpasnjëshme japin rezultate identike; çdo variant i "
            "Autoencoder-it mbetet funksional.",
            "Testet e konventës së shenjës mbi të dhëna reale: për secilin model, mediana e pikëve "
            "të mashtrimeve në bllokun e testimit tejkalon medianën e transaksioneve legjitime.",
            "Testet e gjeometrisë: të dy vlerësuesit e dimensionit të brendshëm rikuperojnë "
            "dimensione të njohura në të dhëna sintetike, dhe masa e vështirësisë e dallon një "
            "problem të lehtë nga një i vështirë me bisht të rëndë.",
            "Testet e metrikave dhe të statistikave: vlerat krahasohen me raste të llogaritura me "
            "dorë, pragu nga percentili verifikohet se sinjalizon fraksionin e pritur, dhe "
            "korrigjimi i Holm-it verifikohet se është monoton.",
            "Testet e stilit të punimit: teksti nuk përmban viza të gjata brenda paragrafëve, nuk "
            "përdor vetën e parë njëjës, dhe nuk i përkthen termat që ruhen në anglisht.",
            "Testet e integrimit: barazia e pikëve mes regjimit offline dhe atij në rrjedhë "
            "kundrejt "
            "një broker-i të vërtetë, dhe qarkullimi i plotë i të dhënave nëpër PostgreSQL me "
            "numërim rreshtash dhe besnikëri të vlerave.",
        ]
    ),
    h2("8.8", "Shtojca H: mjedisi eksperimental"),
    tab(
        "environment",
        "Konfigurimi i plotë harduerik dhe softuerik nën të cilin u prodhuan të gjitha "
        "rezultatet e raportuara.",
        font_size=9.5,
    ),
    p("""Të gjitha matjet operacionale u kryen në këtë mjedis, me producer-in dhe consumer-in në
      të njëjtin host. Matjet e vonesës nuk janë të transferueshme drejtpërdrejt në një
      konfigurim të shpërndarë, ku kalimi nëpër rrjet do të shtonte një komponent shtesë."""),
]

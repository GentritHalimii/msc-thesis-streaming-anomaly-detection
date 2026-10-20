"""Kapitulli 8 — SHTOJCAT."""

from blocks import bullets, h1, h2, numbers, p, tab

BLOCKS = [
    h1("8", "Shtojcat"),
    h2("8.1", "Shtojca A: riprodhimi i rezultateve"),
    p("""I gjithë studimi riprodhohet nga kodi burimor që shoqëron punimin. Dataset-i nuk përfshihet
      në depo për arsye licence dhe madhësie; ai shkarkohet nga Kaggle dhe vendoset në
      data/raw/creditcard.csv. Komandat jepen më poshtë sipas radhës, dhe secila shkruan një
      manifest me SHA-në e commit-it, hash-in e konfigurimit dhe versionet e paketave."""),
    numbers(
        [
            "make setup krijon mjedisin virtual me Python 3.12 dhe instalon varësitë e fiksuara në "
            "lockfile.",
            "make test ekzekuton testet njësi, përfshirë ato që kontrollojnë mungesën e rrjedhjes "
            "së informacionit dhe konventën e shenjës së pikëve.",
            "make train trajnon modelet mbi ndarjen 70/30 dhe ruan artefaktet.",
            "make protocol ekzekuton protokollin rolling-origin 8-fold dhe ruan pikët mbi të cilat "
            "mbështetet çdo analizë e mëvonshme.",
            "make tune dhe make protocol-tuned kryejnë kërkimin e hiperparametrave mbi ndarjen e "
            "brendshme kohore dhe pastaj e përsërisin protokollin me hiperparametrat e gjetur.",
            "make evaluate gjeneron tabelat dhe figurat që mbështeten te pikët e ruajtura, pa "
            "trajnuar përsëri asnjë model; ky hap zgjat disa minuta.",
            "make deep-studies ekzekuton studimet e thelluara për secilin algoritëm, "
            "karakterizimin gjeometrik, studimin e paraprocesimit, ndërhyrjen mbi hyrjen dhe "
            "dizajnin faktorial; këto trajnojnë modelet nga fillimi dhe zgjatin orë, prandaj "
            "mbahen veç.",
            "make figures vizaton përsëri të gjitha figurat nga tabelat e ruajtura, pa trajnuar "
            "asnjë model, për rreth dy minuta.",
            "docker compose -f docker/docker-compose.yml up -d ngre Kafka-n në modalitetin KRaft, "
            "PostgreSQL-in dhe Grafana-n.",
            "make test-integration kontrollon barazinë e pikëve mes regjimit offline dhe atij në "
            "rrjedhë me një broker real, si dhe kalimin e plotë të të dhënave nëpër PostgreSQL.",
            "make stream dhe make latency-report ekzekutojnë matjet e vonesës dhe prodhojnë "
            "tabelat operacionale.",
            "make thesis gjeneron këtë dokument nga rezultatet e ruajtura.",
            "make webapp ngre panelin interaktiv mbi të njëjtat rezultate në "
            "http://127.0.0.1:8800, nga ku çdo hap i mësipërm mund të ekzekutohet edhe nga "
            "shfletuesi.",
        ]
    ),
    p("""Determinizmi u kontrollua në praktikë. Dy cikle të plota dhe të pavarura trajnimi e
      vlerësimi dhanë tabela metrikash identike, me përjashtim të kolonave të kohës dhe të memories,
      të cilat masin burimet dhe jo rezultatin. Kontrolli më i rreptë u bë në nivelin e pikëve:
      trajnimi i katër modeleve mbi fold-in e parë dhe krahasimi i pikëve me ato të ruajtura më parë
      jep vlera identike për të katër, edhe kur makina është e ngarkuar me punë të tjera, gjë që
      përjashton varësinë nga radha e fijeve të ekzekutimit. Kjo arrihet duke e fiksuar seed-in në
      një vend të vetëm, duke aktivizuar algoritmet deterministe në PyTorch dhe duke i ruajtur pikët
      me saktësi të plotë."""),
    h2("8.2", "Shtojca B: struktura e depos së kodit"),
    p("""Kodi është organizuar sipas përgjegjësive dhe jo sipas eksperimenteve, që të njëjtët
      komponentë të përdoren si në regjimin offline ashtu edhe në rrjedhë."""),
    bullets(
        [
            "config/, një skedar i vetëm YAML me të gjithë parametrat: seed-in, raportin e "
            "ndarjes, gjeometrinë e protokollit, hiperparametrat e secilit model, buxhetet e "
            "alarmeve dhe konfigurimin e Kafka-s dhe PostgreSQL-it.",
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
            "experiments/, një skript për çdo eksperiment; modelimi ndodhet në src/, ndërsa "
            "skriptet e kombinojnë dhe i ruajnë rezultatet si tabela, figura dhe përfundime.",
            "tests/, testet e rrjedhjes së informacionit, të protokollit, të kontratës së "
            "modeleve, të gjeometrisë, të metrikave dhe të statistikave, të burimeve të punimit, "
            "si dhe testet e integrimit me Kafka-n dhe PostgreSQL-in.",
            "docker/, konfigurimi i Kafka-s, PostgreSQL-it dhe Grafana-s, përfshirë burimin e të "
            "dhënave dhe panelin e provizionuar nga skedarë.",
            "thesis/, kodi që gjeneron këtë dokument nga rezultatet e ruajtura.",
        ]
    ),
    h2("8.3", "Shtojca C: hiperparametrat dhe mekanizmat"),
    p("""Tabela më poshtë jep mekanizmin e pikëzimit, koston asimptotike të trajnimit dhe
      hiperparametrat bazë të secilit detektor. Vlerat lexohen nga skedari i konfigurimit, përmes
      regjistrit të modeleve, në momentin kur gjenerohet dokumenti."""),
    tab("model_zoo", "Hiperparametrat dhe karakteristikat e detektorëve.", font_size=7.5),
    h2("8.4", "Shtojca D: rezultatet e plota për fold"),
    p("""Tabela kryesore e Kapitullit 5 jep mesataret mbi fold-et. Këtu jepen vlerat për çdo fold,
      që lexuesi të shohë vetë shpërndarjen dhe qëndrueshmërinë e rezultateve."""),
    tab(
        "benchmark_per_fold",
        "AP dhe metrikat e pragut për çdo fold dhe model.",
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
    p("""Për krahasim me literaturën dhe me protokollin e projekt-propozimit, tabela më poshtë jep
      rezultatet e ndarjes së vetme kronologjike 70/30. Kolonat e pragut orakull janë kufi i sipërm
      që nuk arrihet në praktikë dhe nuk duhen krahasuar me ato të pragut nga trajnimi."""),
    tab(
        "metrics_main",
        "Rezultatet e ndarjes së vetme kronologjike 70/30.",
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
    p("""Pasiguria kryesore e punimit raportohet si shpërndarje mbi tetë fold-et, e cila tregon sa
      ndryshon rezultati kur ndryshon periudha. Ajo nuk e mat pasigurinë e mostrimit brenda një
      blloku të vetëm testimi; për prerjen e vetme 70/30 kjo e dyta llogaritet me bootstrap mbi
      transaksionet e bllokut të testimit [@efron1993]."""),
    tab(
        "bootstrap_ci",
        "AP e prerjes së vetme 70/30 me interval besimi 95% nga bootstrap.",
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
        "Diferencat mes modeleve mbi të njëjtat mostra bootstrap.",
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
    p("""Kolona e fundit e tabelës së dytë tregon në sa pjesë të mostrave bootstrap diferenca e ruan
      shenjën. Krahasimi i saj me testet e Kapitullit 5 tregon një dallim që shpesh ngatërrohet. Në
      prerjen e vetme, diferenca mes Autoencoder-it dhe One-Class SVM-së e ruan shenjën në të gjitha
      mostrat, pra brenda asaj periudhe ajo është e sigurt. Në tetë fold-e i njëjti krahasim nuk
      është domethënës, sepse aty pyetja është nëse diferenca mbetet nga një periudhë në tjetrën. Të
      dyja janë të vërteta dhe masin gjëra të ndryshme; nëse do të raportohej vetëm e para,
      qëndrueshmëria e renditjes do të mbivlerësohej."""),
    h2("8.6", "Shtojca F: sipërfaqja e plotë e Isolation Forest-it"),
    p("""Kapitulli 5 e paraqet hapësirën e hiperparametrave si figurë. Tabela më poshtë jep vlerat e
      sakta, që të shihet ku ndodhet maksimumi dhe sa i sheshtë është rajoni rreth tij."""),
    tab(
        "iforest_surface",
        "AP mesatare 8-fold e Isolation Forest-it sipas numrit të pemëve dhe nën-mostrës.",
        rename={"n_estimators": "Pemë"},
        font_size=9.0,
    ),
    h2("8.7", "Shtojca G: testet automatike"),
    p("""Masat metodologjike të Kapitullit 4 janë të koduara edhe në teste që ekzekutohen me çdo
      ndryshim të kodit. Grupet kryesore janë këto:"""),
    bullets(
        [
            "Testet e ndarjes: çdo vulë kohore e trajnimit paraprin çdo vulë të testimit, blloqet "
            "nuk mbivendosen dhe e mbulojnë rrjedhën pa boshllëqe, dhe ndarja është e njëjtë në "
            "çdo ekzekutim.",
            "Testet e rrjedhjes së informacionit: statistikat e skaluesit janë ato të dritares së "
            "trajnimit dhe nuk ndryshojnë kur transformohen të dhënat e testimit; kolona Time nuk "
            "është mes veçorive hyrëse.",
            "Testet e kontratës së modeleve: për çdo detektor, pikat ekstreme të shtuara "
            "artificialisht marrin pikë më të larta se mostrat normale; ruajtja dhe ringarkimi "
            "japin të njëjtat pikë; dy trajnime të njëpasnjëshme japin të njëjtin rezultat; çdo "
            "variant i Autoencoder-it funksionon.",
            "Testet e konventës së shenjës mbi të dhëna reale: për çdo model, mediana e pikëve të "
            "mashtrimeve në bllokun e testimit është mbi atë të transaksioneve legjitime.",
            "Testet e gjeometrisë: të dy vlerësuesit e dimensionit të brendshëm gjejnë dimensionin "
            "e njohur të të dhënave sintetike, dhe masa e vështirësisë e dallon një problem të "
            "lehtë nga një i vështirë me bisht të rëndë.",
            "Testet e metrikave dhe të statistikave: vlerat krahasohen me raste të llogaritura me "
            "dorë, pragu nga percentili jep pjesën e pritur të alarmeve, korrigjimi i Holm-it "
            "është monoton, dhe korrigjimi me permutacione i PSI-së e dallon zhurmën e mostrave të "
            "vogla nga një zhvendosje e vërtetë.",
            "Testet e burimeve të punimit: çdo citim ka një hyrje në listën e referencave, çdo "
            "figurë dhe tabelë e përmendur ekziston, dhe numrat e kapitujve janë të renditur.",
            "Testet e integrimit: pikët në rrjedhë, me një broker real, janë të njëjta me ato "
            "offline, dhe të dhënat kalojnë plotësisht nëpër PostgreSQL, me numër të saktë "
            "rreshtash dhe vlera të paprekura.",
        ]
    ),
    h2("8.8", "Shtojca H: mjedisi eksperimental"),
    tab(
        "environment",
        "Mjedisi harduerik dhe softuerik i të gjitha matjeve.",
        font_size=9.5,
    ),
    p("""Të gjitha matjet operacionale u bënë në këtë mjedis, me producer-in dhe consumer-in në të
      njëjtin host. Vonesat e matura nuk vlejnë drejtpërsëdrejti për një sistem të shpërndarë, ku
      kalimi nëpër rrjet do të shtonte vonesë."""),
]

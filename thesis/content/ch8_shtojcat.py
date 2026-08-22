"""Kapitulli 8 — SHTOJCAT."""

from blocks import bullets, h1, h2, numbers, p, tab

BLOCKS = [
    h1("8", "Shtojcat"),
    h2("8.1", "Shtojca A — Riprodhimi i rezultateve"),
    p("""I gjithë studimi riprodhohet nga kodi burimor i shoqëruar. Dataset-i nuk është i
      përfshirë në depo për arsye licencimi dhe madhësie; ai shkarkohet nga Kaggle dhe
      vendoset në shtegun data/raw/creditcard.csv. Sekuenca e plotë e komandave është si
      më poshtë, dhe secila prej tyre shkruan një manifest me SHA-në e commit-it, hash-in
      e konfigurimit dhe versionet e paketave."""),
    numbers(
        [
            "make setup — krijon mjedisin virtual me Python 3.12 dhe instalon varësitë e "
            "fiksuara nga lockfile-i.",
            "make test — ekzekuton testet njësi, përfshirë ato që verifikojnë mungesën e "
            "rrjedhjes së informacionit dhe konventën e shenjës së pikëve.",
            "make train — përshtat të pesëmbëdhjetë modelet mbi ndarjen 70/30 dhe ruan artefaktet.",
            "make protocol — ekzekuton protokollin rolling-origin me tetë folds; ky është "
            "hapi më i shtrenjtë llogaritës.",
            "make evaluate — gjeneron të gjitha tabelat dhe figurat nga pikët e ruajtura.",
            "docker compose -f docker/docker-compose.yml up -d — ngre Kafka-n në modalitetin "
            "KRaft, PostgreSQL-in dhe Grafana-n.",
            "make test-integration — verifikon barazinë e pikëve mes regjimit offline dhe atij "
            "në rrjedhë kundrejt broker-it të vërtetë, si dhe qarkullimin e plotë të të "
            "dhënave nëpër PostgreSQL.",
            "make stream && make latency-report — ekzekuton skanimin e vonesës dhe prodhon "
            "tabelat operacionale.",
        ]
    ),
    p("""Determinizmi u verifikua empirikisht: dy cikle të plota dhe të pavarura ritrajnimi
      e vlerësimi prodhuan tabela metrike identike bit-për-bit, me përjashtim të kolonave
      të kohës dhe të memories."""),
    h2("8.2", "Shtojca B — Struktura e depos së kodit"),
    p("""Kodi është organizuar sipas përgjegjësive dhe jo sipas eksperimenteve, që
      komponentët të ripërdoren mes regjimit offline dhe atij në rrjedhë."""),
    bullets(
        [
            "config/ — një skedar i vetëm YAML me të gjithë parametrat: seed-in, raportin e "
            "ndarjes, gjeometrinë e protokollit, hiperparametrat e secilit model, buxhetet e "
            "alarmeve dhe konfigurimin e Kafka-s dhe PostgreSQL-it.",
            "src/data/ — leximi, renditja kronologjike, ndarja dhe skalimi i fituar vetëm mbi "
            "dritaren e trajnimit.",
            "src/models/ — një modul për familje algoritmike, të gjitha pas së njëjtës "
            "ndërfaqe fit/score/save/load, plus regjistri që i ndërton nga konfigurimi.",
            "src/evaluation/ — protokolli rolling-origin, metrikat, metrikat operacionale, "
            "kriteret e përzgjedhjes pa etiketa, testet statistikore, analiza e zhvendosjes, "
            "kombinimi i pikëve dhe shtresa e raportimit.",
            "src/streaming/ — prodhuesi me ritëm të kontrolluar, konsumatori me prag statik "
            "ose adaptiv, dhe serializimi.",
            "src/storage/ — persistimi në PostgreSQL me shkrime të grumbulluara.",
            "experiments/ — një skript i ekzekutueshëm për çdo eksperiment; asnjë prej tyre "
            "nuk përmban logjikë modelimi.",
            "tests/ — testet e rrjedhjes, të protokollit, të kontratës së modeleve, të "
            "metrikave, të statistikave dhe testet e integrimit kundrejt Kafka-s dhe "
            "PostgreSQL-it.",
            "docker/ — konfigurimi i Kafka-s, PostgreSQL-it dhe Grafana-s, përfshirë burimin "
            "e të dhënave dhe panelin e provizionuar nga skedarë.",
            "thesis/ — kodi që gjeneron këtë dokument nga rezultatet e ruajtura.",
        ]
    ),
    h2("8.3", "Shtojca C — Hiperparametrat e plotë"),
    p("""Tabela më poshtë liston mekanizmin e pikëzimit, koston asimptotike të trajnimit
      dhe hiperparametrat e përdorur për secilin detektor. Vlerat janë ato të skedarit të
      konfigurimit dhe janë nxjerrë programatikisht nga regjistri i modeleve në momentin
      e gjenerimit të këtij dokumenti."""),
    tab(
        "model_zoo",
        "Hiperparametrat dhe karakteristikat e të pesëmbëdhjetë detektorëve.",
        font_size=7.5,
    ),
    h2("8.4", "Shtojca D — Rezultatet e plota për fold"),
    p("""Tabela kryesore e Kapitullit 5 raporton mesataret nëpër folds. Tabela më poshtë
      jep vlerat e papërpunuara për fold për të katër modelet që pyetja e dytë hulumtuese
      emërton, që lexuesi të mund të verifikojë shpërhapjen dhe të vlerësojë vetë
      qëndrueshmërinë."""),
    tab(
        "benchmark_per_fold",
        "Precizioni mesatar dhe metrikat e pragut për fold, për katër modelet e "
        "propozimit fillestar.",
        query="model in ['iforest', 'autoencoder', 'ocsvm', 'logreg']",
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
            "precision_thr": "Preciziteti",
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
    h2("8.5", "Shtojca E — Rezultatet e ndarjes së vetme 70/30"),
    p("""Për krahasueshmëri me literaturën dhe me protokollin e përcaktuar në
      projekt-propozim, tabela më poshtë jep rezultatet nën ndarjen e vetme kronologjike
      70/30. Kolonat e pragut orakull janë kufi i sipërm i paarritshëm dhe nuk duhen
      krahasuar me kolonat e pragut të nxjerrë nga trajnimi."""),
    tab(
        "metrics_main",
        "Rezultatet nën ndarjen e vetme kronologjike 70/30, me pragun nga trajnimi dhe "
        "pragun orakull të raportuar veçmas.",
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
            "precision_pct": "Preciziteti",
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
        font_size=8.0,
    ),
    h2("8.6", "Shtojca F — Testet automatike"),
    p("""Disiplina metodologjike e përshkruar në Kapitullin 4 nuk mbetet vetëm në tekst;
      ajo është e koduar në teste që ekzekutohen me çdo ndryshim. Grupet kryesore
      janë:"""),
    bullets(
        [
            "Testet e ndarjes: çdo vulë kohore e trajnimit paraprin çdo vulë të testimit; "
            "blloqet nuk mbivendosen dhe e mbulojnë rrjedhën pa boshllëqe; ndarja është "
            "deterministe mes ekzekutimeve.",
            "Testet e rrjedhjes së informacionit: statistikat e skaluesit janë identike me "
            "momentet e dritares së trajnimit dhe nuk ndryshojnë kur transformohen të dhënat "
            "e testimit; kolona Time nuk gjendet mes veçorive hyrëse.",
            "Testet e kontratës së modeleve: për secilin detektor, pikat e injektuara "
            "artificialisht si ekstreme marrin pikë më të larta se mostrat normale; ruajtja "
            "dhe ringarkimi japin pikë identike; dy përshtatje të njëpasnjëshme japin "
            "rezultate identike.",
            "Testet e konventës së shenjës mbi të dhëna reale: për secilin nga të "
            "pesëmbëdhjetë modelet, mediana e pikëve të mashtrimeve në bllokun e testimit "
            "tejkalon medianën e transaksioneve legjitime.",
            "Testet e metrikave: vlerat krahasohen me raste të llogaritura me dorë, dhe "
            "pragu nga percentili verifikohet se sinjalizon fraksionin e pritur.",
            "Testet e integrimit: barazia e pikëve mes regjimit offline dhe atij në rrjedhë "
            "kundrejt një broker-i të vërtetë, dhe qarkullimi i plotë i të dhënave nëpër "
            "PostgreSQL me numërim rreshtash dhe besnikëri të vlerave.",
        ]
    ),
    h2("8.7", "Shtojca G — Mjedisi eksperimental"),
    tab(
        "environment",
        "Konfigurimi i plotë harduerik dhe softuerik nën të cilin u prodhuan të gjitha "
        "rezultatet e raportuara.",
        font_size=9.5,
    ),
    p("""Të gjitha matjet operacionale u kryen në këtë mjedis, me prodhuesin dhe
      konsumatorin në të njëjtin host. Matjet e vonesës nuk janë të transferueshme
      drejtpërdrejt në një konfigurim të shpërndarë, ku kalimi nëpër rrjet do të shtonte
      një komponent shtesë."""),
]

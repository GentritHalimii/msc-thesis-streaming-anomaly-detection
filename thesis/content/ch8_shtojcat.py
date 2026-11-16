"""Kapitulli 8 — SHTOJCAT."""

from blocks import bullets, fig, h1, h2, numbers, p, tab

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
            "make deep-studies ekzekuton studimet për secilin algoritëm, distancat e analizës "
            "eksploruese, studimin e paraprocesimit dhe dizajnin faktorial; këto trajnojnë modelet "
            "nga fillimi dhe zgjatin orë, prandaj mbahen veç.",
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
            "src/evaluation/, protokolli rolling-origin, metrikat, distancat nga fqinjët më të "
            "afërt, metrikat operacionale, ndarja e brendshme për akordimin, testet statistikore, "
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
            "webapp/, një panel lokal që i shfaq të njëjtat rezultate në shfletues dhe i ekzekuton "
            "eksperimentet nga një katalog i deklaruar.",
        ]
    ),
    h2("8.3", "Shtojca C: rezultatet e plota për fold"),
    p("""Tabela [[tab:benchmark_summary]] e Kapitullit 5 jep mesataret mbi fold-et. Tabela
      [[tab:benchmark_per_fold]] jep vlerat për çdo fold dhe model: numrin e mashtrimeve në bllokun
      e testimit, AP-në, AUC-ROC-në, metrikat në pragun nga trajnimi dhe recall-in me 100 alarme, që
      lexuesi të shohë vetë shpërndarjen dhe qëndrueshmërinë e rezultateve."""),
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
            "roc_auc": "AUC",
            "precision_thr": "Precision",
            "recall_thr": "Recall",
            "f1_thr": "F1",
            "recall_at_100": "R@100",
        },
        replace={
            "model": {
                "iforest": "Isolation Forest",
                "autoencoder": "Autoencoder",
                "ocsvm": "One-Class SVM",
                "logreg": "LR (referencë)",
            }
        },
        sort=["model", "fold"],
        round={
            "ap": 3,
            "roc_auc": 3,
            "precision_thr": 3,
            "recall_thr": 3,
            "f1_thr": 3,
            "recall_at_100": 3,
        },
    ),
    h2("8.4", "Shtojca D: rezultatet e ndarjes së vetme 70/30"),
    p("""Për krahasim me literaturën, Tabela [[tab:metrics_main]] jep rezultatet e ndarjes së
      vetme kronologjike 70/30. Kolonat e pragut orakull janë kufi i sipërm
      që nuk arrihet në praktikë dhe nuk duhen krahasuar me ato të pragut nga trajnimi. Memoria
      (MB) jepet si rritja e memories rezidente gjatë trajnimit, siç përcaktohet në nënkapitullin
      4.6.3."""),
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
            "fit_delta_rss_mb",
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
            "fit_time_s": "Fit (s)",
            "fit_delta_rss_mb": "MB",
            "inference_us_per_tx": "µs/tx",
        },
        round={
            "ap": 3,
            "roc_auc": 3,
            "precision_pct": 3,
            "recall_pct": 3,
            "f1_pct": 3,
            "f1_oracle": 3,
            "fit_time_s": 2,
            "fit_delta_rss_mb": 1,
            "inference_us_per_tx": 2,
        },
        # Four models and nine quantities read better with the models as columns.
        transpose="Metrika",
    ),
    p("""Figura [[fig:curves_pr_roc]] jep kurbat precision-recall dhe ROC të po kësaj ndarjeje. Në
      hapësirën ROC tri metodat unsupervised duken pothuajse të barabarta, me AUC-ROC nga 0.936 deri
      0.960, ndërsa në hapësirën precision-recall dallimet janë të qarta: AP 0.031 për Isolation
      Forest-in, 0.091 për One-Class SVM-në dhe 0.140 për Autoencoder-in."""),
    fig(
        "curves_pr_roc",
        "Kurbat precision-recall dhe ROC të ndarjes 70/30 për çdo model.",
        15.0,
    ),
    p("""Pasiguria kryesore e punimit raportohet si shpërndarje mbi tetë fold-et, e cila tregon sa
      ndryshon rezultati kur ndryshon periudha. Ajo nuk e mat pasigurinë e mostrimit brenda një
      blloku të vetëm testimi; për prerjen e vetme 70/30 kjo e dyta llogaritet me bootstrap mbi
      transaksionet e bllokut të testimit [@efron1993]. Tabela [[tab:bootstrap_ci]] jep intervalin
      e besimit 95% të AP-së për çdo model, dhe Tabela [[tab:bootstrap_pairwise]] diferencat mes
      modeleve, të llogaritura mbi të njëjtat mostra bootstrap, me intervalin e tyre dhe pjesën e
      mostrave ku diferenca është pozitive."""),
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
        replace={
            "comparison": {
                "Autoencoder - One-Class SVM": "Autoencoder − One-Class SVM",
                "Autoencoder - Isolation Forest": "Autoencoder − Isolation Forest",
                "Autoencoder - Ansambël (mesatare z)": "Autoencoder − Ansambël (mesatare z)",
                "Ansambël (mesatare z) - One-Class SVM": "Ansambël (mesatare z) − One-Class SVM",
            }
        },
        round={"delta_ap_mean": 4, "delta_ci95_low": 4, "delta_ci95_high": 4},
        fmt={"frac_replicates_positive": ".1%"},
    ),
    p("""Kolona e fundit e tabelës së diferencave tregon në sa pjesë të mostrave bootstrap diferenca
      e ruan shenjën. Krahasimi i saj me testet e Kapitullit 5 tregon një dallim që shpesh
      ngatërrohet. Në prerjen e vetme, diferenca mes Autoencoder-it dhe One-Class SVM-së e ruan
      shenjën në të gjitha mostrat, pra brenda asaj periudhe ajo është e sigurt. Në tetë fold-e i
      njëjti krahasim nuk është domethënës, sepse aty pyetja është nëse diferenca mbetet nga një
      periudhë në tjetrën. Të dyja janë të vërteta dhe masin gjëra të ndryshme; nëse do të
      raportohej vetëm e para, qëndrueshmëria e renditjes do të mbivlerësohej."""),
    h2("8.5", "Shtojca E: zhvendosja e të dhënave"),
    p("""Zhvendosja matet veç e veç për transaksionet legjitime dhe për mashtrimet, duke krahasuar
      dritaren e trajnimit të çdo fold-i me bllokun e tij të testimit. Për çdo veçori llogaritet
      indeksi PSI, me dhjetë intervale të përcaktuara nga kuantilet e dritares së trajnimit; vlerat
      0.10 dhe 0.25 lexohen zakonisht si kufijtë e zhvendosjes së moderuar dhe të madhe. Në mostra
      të vogla PSI rritet edhe kur shpërndarja nuk ka ndryshuar, sepse disa intervale mbeten bosh
      rastësisht. Meqë një bllok testimi ka nga 13 deri në 88 mashtrime, PSI-ja e mashtrimeve
      lexohet kundrejt një shpërndarjeje zero me permutacione: dritarja e trajnimit dhe blloku i
      testimit bashkohen, ndahen rastësisht në dy pjesë me madhësitë origjinale, dhe PSI llogaritet
      përsëri 100 herë."""),
    p("""Vlerat e papërpunuara duken qartë të njëanshme: PSI mesatar është 0.141 për transaksionet
      legjitime dhe 3.222 për mashtrimet. Rreth 48% e vlerës së mashtrimeve vjen megjithatë nga
      zhurma e mostrave të vogla, sepse permutacionet vetëm japin mesatarisht 1.561. Vlera e
      vëzhguar e kalon zhurmën në të tetë fold-et (p ≈ 0.01, vlera më e vogël e mundshme me 100
      permutacione), dhe teprica mesatare mbi zhurmën, 1.66, është mbi dhjetë herë PSI-ja e
      popullatës legjitime (Figura [[fig:drift_psi_decomposition]]). Edhe zhvendosja e
      transaksioneve legjitime e kalon zhurmën e saj në çdo fold, por është e vogël."""),
    fig(
        "drift_psi_decomposition",
        "PSI mesatar mbi 29 veçori për çdo popullatë dhe fold, me brezin e zhurmës nga "
        "permutacionet.",
        15.0,
    ),
    p("""Modeli i normalitetit, mbi të cilin janë trajnuar të tre detektorët, ndryshon pak; më shumë
      ndryshojnë mashtrimet. Ritrajnimi periodik mbi të dhëna të reja normale nuk e trajton pra këtë
      anë të problemit."""),
    h2("8.6", "Shtojca F: testet automatike"),
    p("""Masat metodologjike të Kapitullit 4 janë të koduara edhe në teste që ekzekutohen me çdo
      ndryshim të kodit. Testet kontrollojnë që çdo vulë kohore e trajnimit paraprin çdo vulë të
      testimit dhe që blloqet e fold-eve nuk mbivendosen; që skaluesi mëson vetëm nga dritarja e
      trajnimit dhe që kolona Time nuk është veçori; që çdo detektor u jep pikë më të larta pikave
      ekstreme dhe mashtrimeve reale, dhe që ruajtja e ringarkimi japin të njëjtat pikë; që metrikat
      dhe testet statistikore përputhen me raste të llogaritura me dorë; dhe që pikët në rrjedhë, me
      një broker real, janë të njëjta me ato offline dhe kalojnë plotësisht nëpër PostgreSQL. Një
      grup i veçantë testesh kontrollon vetë këtë dokument: çdo citim ka hyrje në listën e
      referencave, dhe çdo figurë e tabelë e përmendur ekziston."""),
]

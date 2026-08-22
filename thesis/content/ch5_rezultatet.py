"""Kapitulli 5 — REZULTATET."""

from blocks import fig, h1, h2, h3, note, p, tab

_HYRJE = [
    h1("5", "Rezultatet"),
    p("""Rezultatet paraqiten të organizuara sipas tri pyetjeve hulumtuese, të ndjekura nga
      katër analiza shtesë që shpjegojnë pse rezultatet dalin ashtu siç dalin. Çdo vlerë e
      raportuar këtu gjendet në një artefakt të gjeneruar nga kodi dhe të shoqëruar me një
      manifest që përmban SHA-në e commit-it dhe hash-in e konfigurimit; asnjë numër nuk
      është transkriptuar me dorë."""),
    note("""Konventë raportimi: kudo ku shfaqet referenca me Regresion Logjistik, ajo
      shënohet shprehimisht si referencë e mbikëqyrur. Ajo nuk konkurron me metodat e
      pambikëqyrura, sepse ka pasur në dispozicion etiketat historike; roli i saj është
      të tregojë kufirin e sipërm të arritshëm kur ato etiketa ekzistojnë."""),
    h2("5.1", "PH1 — Realizueshmëria e sistemit dhe vonesa"),
    h3("5.1.1", "Shpërndarja e vonesës fund-më-fund"),
    p("""Pyetja e parë hulumtuese ka dy pjesë: a mund të ndërtohet sistemi, dhe a mban ai
      vonesë mesatare nën një sekondë. Pjesa e parë u përgjigj me vetë implementimin: një
      pipeline i plotë nga leximi i CSV-së deri te alarmet e ruajtura dhe të vizualizuara
      është funksional, dhe barazia e pikëve mes regjimit offline dhe atij në rrjedhë
      verifikohet me test automatik kundrejt një broker-i të vërtetë."""),
    p("""Pjesa e dytë kërkon matje. Tabela më poshtë përmbledh njëzet e katër ekzekutime
      rrjedhe: gjashtë modele nën tri ritme mbërritjeje, plus ekzekutimet me prag adaptiv
      dhe ato të ngopjes. Vlera më e keqe e vonesës mesatare fund-më-fund mbi të gjitha
      konfigurimet është 85.1 milisekonda, pra rreth dymbëdhjetë herë nën objektivin prej
      një sekonde. Edhe percentili i nëntëdhjetë e nëntë, pra bishti i shpërndarjes, nuk
      e kalon kufirin në asnjë rast: vlera më e lartë e vëzhguar është 447 milisekonda,
      për LOF-in në ritmin dyqind mesazhe në sekondë."""),
    tab(
        "latency_summary",
        "Vonesa fund-më-fund dhe kostoja e inferencës për model dhe ritëm mbërritjeje. "
        "Të gjitha vlerat janë matur mbi tetë mijë mesazhe për ekzekutim, me prodhuesin "
        "të sinkronizuar me gatishmërinë e konsumatorit.",
        query="prag_adaptiv == False and rate_msg_s <= 1000",
        columns=[
            "model",
            "rate_msg_s",
            "e2e_ms_mean",
            "e2e_ms_p50",
            "e2e_ms_p95",
            "e2e_ms_p99",
            "infer_ms_mean",
            "throughput_msg_s",
            "cpu_percent_mean",
        ],
        rename={
            "model": "Modeli",
            "rate_msg_s": "Ritmi",
            "e2e_ms_mean": "e2e mes.",
            "e2e_ms_p50": "p50",
            "e2e_ms_p95": "p95",
            "e2e_ms_p99": "p99",
            "infer_ms_mean": "Inferenca",
            "throughput_msg_s": "Kapaciteti",
            "cpu_percent_mean": "CPU %",
        },
        round={
            "e2e_ms_mean": 1,
            "e2e_ms_p50": 1,
            "e2e_ms_p95": 1,
            "e2e_ms_p99": 1,
            "infer_ms_mean": 3,
            "throughput_msg_s": 1,
            "cpu_percent_mean": 1,
        },
        font_size=8.0,
    ),
    p("""Struktura e vonesës është më informative se vlera e saj absolute. Për pesë nga
      gjashtë modelet, mediana qëndron mes njëzet e tetë dhe pesëdhjetë e pesë
      milisekondash dhe pothuajse nuk lëviz me ritmin e mbërritjes. Kjo ndodh sepse
      vonesa nuk dominohet nga modeli: dritarja prej pesëdhjetë milisekondash për
      mbledhjen e mikro-grupit prodhon një pritje mesatare prej rreth njëzet e pesë
      milisekondash, dhe kjo është dyshemeja e sistemit. Vetë inferenca zë mes shtatë e
      gjysmë mikrosekondave dhe tridhjetë e gjashtë milisekondash në percentilin e
      nëntëdhjetë e nëntë, pra në shumicën e rasteve është e papërfillshme përballë
      kostos së transportit."""),
    p("""Përjashtimi është LOF-i. Ai është i vetmi model ku inferenca dominon: gjatë
      ekzekutimeve të tij konsumatori përdorte mesatarisht mbi treqind e njëzet për qind
      CPU, pra kërkimi i fqinjëve po shpërndahej mbi disa bërthama, dhe bishti i vonesës
      u zgjat në treqind deri katërqind e pesëdhjetë milisekonda. Ky është një rezultat
      operacional i rëndësishëm: një metodë mund të jetë e mirë në zbulim dhe
      njëkohësisht e papërshtatshme për rrjedhë."""),
    fig(
        "latency_vs_rate",
        "Vonesa fund-më-fund kundrejt ritmit të mbërritjes, në shkallë logaritmike. "
        "Vija e plotë tregon percentilin e nëntëdhjetë e nëntë, ajo e zbehtë medianën. "
        "Vija horizontale shënon objektivin prej një sekonde.",
        14.5,
    ),
    h3("5.1.2", "Ngopja e kapacitetit përpunues"),
    p("""Pohimi se vonesa qëndron nën një sekondë ka kuptim vetëm nëse dihet edhe deri ku
      sistemi arrin ta ndjekë rrjedhën. Për këtë u krye një skanim ngopjeje me Deep
      SVDD-në, duke e ngritur ritmin e synuar deri në dhjetë mijë mesazhe në sekondë."""),
    tab(
        "latency_summary",
        "Skanimi i ngopjes me Deep SVDD: raporti mes kapacitetit të arritur dhe atij të "
        "synuar bie nën një kur konsumatori nuk e ndjek më prodhuesin.",
        query="model == 'deep_svdd' and prag_adaptiv == False",
        columns=[
            "rate_msg_s",
            "throughput_msg_s",
            "throughput_ratio",
            "e2e_ms_p50",
            "e2e_ms_p99",
            "batch_size_mean",
            "cpu_percent_mean",
        ],
        rename={
            "rate_msg_s": "Ritmi i synuar",
            "throughput_msg_s": "Kapaciteti i arritur",
            "throughput_ratio": "Raporti",
            "e2e_ms_p50": "p50 (ms)",
            "e2e_ms_p99": "p99 (ms)",
            "batch_size_mean": "Madhësia e grupit",
            "cpu_percent_mean": "CPU %",
        },
        round={
            "throughput_msg_s": 1,
            "throughput_ratio": 3,
            "e2e_ms_p50": 1,
            "e2e_ms_p99": 1,
            "batch_size_mean": 1,
            "cpu_percent_mean": 1,
        },
        font_size=9.0,
    ),
    p("""Sjellja është ajo klasike e një sistemi me radhë. Deri në një mijë mesazhe në
      sekondë konsumatori e ndjek prodhuesin me humbje minimale. Në dy mijë raporti bie
      në 0.70, në pesë mijë në 0.48, dhe kapaciteti maksimal i vëzhguar është rreth dy
      mijë e katërqind mesazhe në sekondë. Vlen të vërehet edhe efekti kundërintuitiv:
      në ritme shumë të larta vonesa fund-më-fund bie, sepse mikro-grupet mbushen
      menjëherë dhe nuk pritet fare — mesazhet nuk presin në konsumator, por presin në
      Kafka. Ky është shembulli më i qartë se pse vonesa e matur pa kapacitetin
      shoqërues është një numër i pakuptimtë."""),
    p("""Kur ritmi i synuar shkon në dhjetë mijë, kapaciteti i arritur bie nga dy mijë e
      katërqind në dy mijë e njëqind. Ky degradim nën mbingarkesë, i njohur si kolaps
      nga ngjeshja, është sjellje e pritshme e një konsumatori pa kontroll rrjedhjeje dhe
      shënon kufirin e vërtetë operacional të prototipit."""),
    h3("5.1.3", "Përgjigjja për PH1"),
    p("""Përgjigjja është pozitive dhe me rezervë të gjerë. Sistemi u implementua i plotë
      dhe mban vonesë mesatare fund-më-fund mes njëzet e tetë dhe tetëdhjetë e pesë
      milisekondash, pra rreth një rend madhësie nën objektivin prej një sekonde, në të
      gjitha ritmet e testuara deri në një mijë mesazhe në sekondë. Kjo përgjigje vlen
      nën kushtet e deklaruara: ritëm mbërritjeje sintetik dhe konstant, një host, një
      broker dhe një konsumator. Kapaciteti maksimal i qëndrueshëm është rreth dy mijë e
      katërqind mesazhe në sekondë, dhe përtej tij sistemi degradon."""),
]

_PH2 = [
    h2("5.2", "PH2 — Krahasimi i algoritmeve"),
    h3("5.2.1", "Rezultatet nga protokolli rolling-origin"),
    p("""Tabela kryesore e këtij punimi paraqet katërmbëdhjetë detektorë të pambikëqyrur
      dhe referencën e mbikëqyrur, të vlerësuar në tetë pika kohore prerjeje. Raportohen
      mesatarja dhe devijimi standard i precizionit mesatar nëpër folds, rangu mesatar,
      metrikat në pragun e nxjerrë nga trajnimi dhe kostot llogaritëse."""),
    tab(
        "benchmark_summary",
        "Rezultatet kryesore mbi tetë folds. AP-ja është metrika parësore; rangu mesatar "
        "llogaritet mbi AP-në për fold. Kostoja e pikëzimit është mikrosekonda për "
        "transaksion në regjimin offline.",
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
            "roc_auc_mean": "ROC-AUC",
            "amount_ap_mean": "AP monetar",
            "f1_thr_mean": "F1",
            "recall_at_100": "Recall@100",
            "score_us_per_tx": "µs/tx",
            "fit_time_s": "Trajnimi (s)",
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
        font_size=8.0,
    ),
    p("""Tri gjetje dalin menjëherë. E para është hendeku i referencës: modeli i
      mbikëqyrur arrin precizion mesatar 0.720 dhe fiton në të tetë folds-at pa
      përjashtim, pra rangun mesatar 1.00. Metoda më e mirë e pambikëqyrur, Deep SVDD,
      arrin 0.449. Raporti afërsisht 1.6 mes tyre është kuantifikimi i drejtpërdrejtë i
      vlerës së etiketave historike në këtë problem."""),
    p("""E dyta është renditja brenda fushës së pambikëqyrur, e cila nuk përputhet me
      pritshmërinë e propozimit fillestar. Deep SVDD-ja kryeson, e ndjekur nga LOF-i,
      VAE-ja dhe GMM-ja. Nga tre algoritmet qendrore të propozimit, Autoenkoderi renditet
      i pesti me 0.193, One-Class SVM-ja i teti me 0.148, dhe Isolation Forest-i i
      trembëdhjeti nga katërmbëdhjetë me 0.091 — pra praktikisht në fund të fushës."""),
    p("""E treta është dallimi mes AP-së dhe AUC-ROC-së. Isolation Forest-i, me AP 0.091,
      ka AUC-ROC 0.941; Deep SVDD-ja, me AP pesë herë më të lartë, ka AUC-ROC më të ulët,
      0.905. Nëse do të raportohej vetëm ROC-ja, siç bën një pjesë e literaturës mbi këtë
      dataset, përfundimi do të ishte i kundërt me realitetin. Ky është ilustrimi më i
      qartë empirik i argumentit teorik të Davis-it dhe Goadrich-it dhe të Saito-s e
      Rehmsmeier-it [@davis2006], [@saito2015]."""),
    fig(
        "benchmark_ap_ranking",
        "Precizioni mesatar për detektor, mesatarizuar mbi tetë folds, me devijimin "
        "standard si shirit gabimi. Ngjyra kodon familjen algoritmike.",
        14.0,
    ),
    p("""Shiritat e gabimit meritojnë vëmendje po aq sa vetë mesataret. Devijimi standard
      nëpër folds është i krahasueshëm me vlerën mesatare për pothuajse çdo detektor;
      për Autoenkoderin dhe VAE-në ai madje e tejkalon atë. Kjo do të thotë se
      performanca e një detektori të vetëm ndryshon në mënyrë dramatike varësisht se në
      cilën pikë kohore vendoset."""),
    fig(
        "benchmark_ap_per_fold",
        "Precizioni mesatar për çdo detektor në secilin fold, në shkallë logaritmike. "
        "Fold-i 1, i cili përmban një grumbullim prej tetëdhjetë e tetë mashtrimesh, "
        "është dukshëm më i lehtë për të gjithë detektorët.",
        15.0,
    ),
    p("""Fold-i 1 është një vlerë ekstreme sistematike: aty performanca e çdo detektori
      hidhet lart. Ai përmban tetëdhjetë e tetë mashtrime, katër herë mbi mesataren e
      blloqeve të tjera, dhe analiza e zhvendosjes në nënkapitullin 5.4.2 tregon se
      mashtrimet e atij blloku janë edhe dukshëm më ekstreme në hapësirën e veçorive.
      Një studim që do të kishte zgjedhur rastësisht atë periudhë si bashkësi testimi do
      të raportonte rezultate shumë më optimiste, pa asnjë ndryshim në metodë."""),
    h3("5.2.2", "A janë dallimet statistikisht të qëndrueshme"),
    p("""Testi omnibus i Friedman-it mbi matricën e rangjeve refuzon me forcë hipotezën se
      detektorët janë ekuivalentë: për të katërmbëdhjetë metodat e pambikëqyrura mbi tetë
      folds, statistika është 62.01 me p-vlerë 2.3 × 10⁻⁸. I njëjti test i kufizuar te
      katër modelet e propozimit fillestar jep p-vlerë 1.5 × 10⁻⁴."""),
    tab(
        "significance_omnibus",
        "Testi omnibus i Friedman-it dhe diferenca kritike e Nemenyi-t për dy grupe "
        "krahasimi. Vini re se për katërmbëdhjetë detektorë diferenca kritike i afrohet "
        "gjerësisë së plotë të intervalit të rangjeve.",
        rename={
            "grupi": "Grupi i krahasimit",
            "k": "k",
            "N_folde": "N",
            "friedman_chi2": "χ² Friedman",
            "p_value": "p",
            "nemenyi_CD": "CD",
            "range_i_rangjeve": "Gjerësia e rangjeve",
        },
        fmt={"p_value": ".2e"},
        round={"friedman_chi2": 2, "nemenyi_CD": 2, "range_i_rangjeve": 2},
        font_size=9.5,
    ),
    p("""Testi post-hoc i Nemenyi-t, megjithatë, ka fuqi të kufizuar në këtë përmasë
      eksperimenti. Me katërmbëdhjetë detektorë dhe tetë folds, diferenca kritike është
      7.02 ndërsa gjerësia e plotë e rangjeve mesatare është 10.5. Kjo do të thotë se
      vetëm ndarjet ekstreme mund të shpallen domethënëse, dhe ky është kufizim i
      madhësisë së eksperimentit, jo provë ekuivalence. Diagrami i diferencës kritike e
      bën këtë të dukshme."""),
    fig(
        "significance_cd_all",
        "Diagrami i diferencës kritike për katërmbëdhjetë detektorët e pambikëqyrur. "
        "Detektorët e lidhur me një shirit horizontal nuk dallohen statistikisht në "
        "nivelin 0.05.",
        15.0,
    ),
    fig(
        "significance_cd_core",
        "Diagrami i diferencës kritike i kufizuar te katër modelet e propozimit "
        "fillestar, ku fuqia statistikore është dukshëm më e lartë (CD = 1.66).",
        14.0,
    ),
    p("""Për krahasimet që pyetjet hulumtuese i emërtojnë shprehimisht, u përdor testi i
      çiftuar i Wilcoxon-it me korrigjim Holm. Bashkësia prej gjashtë krahasimesh u
      fiksua në kod përpara se të shihej ndonjë rezultat, dhe numri i tyre u zgjodh që
      korrigjimi të mbetet i kalueshëm: me tetë folds p-vlera më e vogël e arritshme
      është 0.0078, e cila shumëzuar me gjashtë jep 0.047 dhe mezi qëndron nën 0.05."""),
    tab(
        "significance_wilcoxon",
        "Krahasimet e paradeklaruara dyshe me testin e Wilcoxon-it mbi tetë folds, me "
        "korrigjim Holm. Kolona e fitoreve tregon në sa folds fiton secili anëtar i "
        "çiftit.",
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
        font_size=8.5,
    ),
    p("""Katër nga gjashtë krahasimet mbijetojnë korrigjimin. Autoenkoderi e tejkalon
      Isolation Forest-in në shtatë nga tetë folds; Isolation Forest-i humbet ndaj
      One-Class SVM-së dhe ndaj ECOD-it në të tetë folds; dhe referenca e mbikëqyrur e
      tejkalon Autoenkoderin në të tetë folds me diferencë mesatare 0.527 në AP. Dy
      krahasimet që nuk arrijnë domethënie — Autoenkoderi kundrejt One-Class SVM-së dhe
      kundrejt PCA-së — janë pikërisht ato ku fitorja është gjashtë me dy, pra e
      qëndrueshme por jo e plotë."""),
    note("""Vlen të theksohet se Autoenkoderi nuk e tejkalon në mënyrë domethënëse
      detektorin linear të rindërtimit me PCA. Meqë veçoritë hyrëse janë vetë komponentë
      kryesorë, kjo do të thotë se enkoderi jolinear nuk ka nxjerrë strukturë përtej asaj
      që projeksioni linear e kishte tashmë të dukshme — një gjetje e matur, jo një
      hamendësim."""),
    h3("5.2.3", "Kompromisi mes cilësisë dhe kostos"),
    p("""Pyetja e dytë hulumtuese nuk kërkon detektorin më të saktë, por atë me balancën
      më të mirë mes performancës dhe efikasitetit operacional. Këto janë dy boshte të
      ndryshme dhe duhen parë bashkë."""),
    fig(
        "benchmark_quality_cost",
        "Cilësia e zbulimit kundrejt kostos së pikëzimit. Këndi i sipërm i majtë është "
        "pozicioni i dëshiruar: cilësi e lartë me kosto të ulët.",
        14.5,
    ),
    p("""Figura e bën përgjigjen të qartë. Deep SVDD-ja zë këndin e sipërm të majtë: ajo
      ka precizionin mesatar më të lartë mes metodave të pambikëqyrura dhe njëkohësisht
      koston e dytë më të ulët të pikëzimit, 0.11 mikrosekonda për transaksion. LOF-i, i
      dyti për cilësi, kushton 35.5 mikrosekonda për transaksion, pra rreth treqind e
      tetëmbëdhjetë herë më shumë, dhe në rrjedhë kjo u përkthye në bishtin më të keq të
      vonesës nga të gjitha modelet. One-Class SVM-ja dhe metodat statistikore marginale
      kushtojnë gjithashtu dhjetëra mikrosekonda pa ofruar cilësi konkurruese."""),
    p("""Kostoja e trajnimit jep një renditje pjesërisht të ndryshme: Deep SVDD-ja kërkon
      rreth trembëdhjetë sekonda për fold, ndërsa PCA-ja dhe metodat statistikore
      kërkojnë më pak se dy. Në një sistem ku modeli ritrajnohet një herë në ditë ky
      dallim është i parëndësishëm; ai do të kishte rëndësi vetëm nëse ritrajnimi do të
      ishte i vazhdueshëm."""),
    fig(
        "benchmark_family_box",
        "Shpërndarja e precizionit mesatar sipas familjes algoritmike, mbi të gjitha "
        "folds-at dhe të gjithë anëtarët. Vija e ndërprerë tregon referencën e "
        "mbikëqyrur.",
        14.0,
    ),
    h3("5.2.4", "Vlerësimi në buxhet alarmesh"),
    p("""Precizioni mesatar përmbledh të gjithë renditjen, por asnjë ekip nuk e shqyrton
      atë të tërën. Tabela më poshtë tregon çfarë ndodh kur investigohen vetëm njëqind
      alarmet më të larta për bllok testimi — një buxhet realist, meqë blloqet përmbajnë
      mesatarisht rreth njëzet e katër mashtrime."""),
    tab(
        "budget_summary",
        "Cilësia e zbulimit dhe rikuperimi monetar në buxhet prej njëqind alarmesh për "
        "bllok testimi, mesatarizuar mbi tetë folds.",
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
            "precision_at_k": "Preciziteti@100",
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
        font_size=8.5,
    ),
    p("""Renditja ndryshon lehtë kur shihet nga ky kënd. LOF-i kalon para Deep SVDD-së në
      ndjeshmërinë brenda buxhetit, sepse ai është veçanërisht i mirë në majën e
      renditjes edhe kur renditja e tij globale është më e dobët. VAE-ja, e treta për
      AP, jep kursimet më të larta neto mes metodave të pambikëqyrura, sepse mashtrimet
      që ajo kap janë mesatarisht më të shtrenjta."""),
    p("""Në terma absolutë, referenca e mbikëqyrur rikuperon mesatarisht 2,324 euro neto
      për bllok testimi nga rreth 3,905 euro mashtrim total, pra afërsisht gjashtëdhjetë
      e gjashtë për qind të vlerës. Metoda më e mirë e pambikëqyrur në këtë metrikë
      rikuperon rreth 2,012 euro. Këto shifra janë të vogla në terma absolutë sepse
      dataset-i mbulon vetëm dyzet e tetë orë dhe vlera totale e mashtrimeve në të është
      pak mbi gjashtëdhjetë mijë euro."""),
    fig(
        "budget_recall",
        "Ndjeshmëria brenda buxhetit të alarmeve, për buxhete nga pesëdhjetë deri në një "
        "mijë alarme për bllok. Ngjyra kodon familjen algoritmike.",
        14.5,
    ),
    fig(
        "budget_savings",
        "Raporti i kursimeve neto kundrejt detektorit të përsosur, sipas buxhetit të "
        "alarmeve. Vlerat negative do të thoshin se kostoja e hetimeve e tejkalon vlerën "
        "e rikuperuar.",
        14.5,
    ),
    h3("5.2.5", "Përgjigjja për PH2"),
    p("""Nga tre algoritmet që pyetja hulumtuese emërton, Autoenkoderi ofron balancën më
      të mirë: ai ka AP-në më të lartë (0.193 kundrejt 0.148 për One-Class SVM-në dhe
      0.091 për Isolation Forest-in), koston më të ulët të pikëzimit dhe një epërsi
      statistikisht të qëndrueshme ndaj Isolation Forest-it. Kur fusha zgjerohet, kjo
      përgjigje ndryshon: Deep SVDD-ja e tejkalon Autoenkoderin me më shumë se dyfish në
      AP me kosto praktikisht të njëjtë pikëzimi, dhe është prandaj kompromisi më i mirë
      i gjetur në këtë studim."""),
    p("""Të tre e mbeten dukshëm nën referencën e mbikëqyrur. Përfundimi praktik nuk është
      se metodat e pambikëqyrura janë të padobishme, por se ato duhen parë si shtresë
      plotësuese ose si zgjidhje për periudhën kur etiketat mungojnë, jo si zëvendësim i
      një modeli të mbikëqyrur atje ku etiketat historike ekzistojnë."""),
]

_PH3 = [
    h2("5.3", "PH3 — A ndihmon ansambli"),
    h3("5.3.1", "Variantet e testuara"),
    p("""Pyetja e tretë u testua në pesë rregulla kombinimi mbi tri bashkësi anëtarësh.
      Rregullat janë: mesatarja e rangjeve të normalizuara sipas shpërndarjes së pikëve
      të trajnimit, mesatarja e z-vlerave, maksimumi, mediana dhe votimi me shumicë. Të
      pesta janë të lira nga rrjedhja e informacionit, sepse çdo statistikë normalizimi
      dhe çdo prag vote vjen vetëm nga dritarja e trajnimit."""),
    p("""Bashkësitë e anëtarëve janë: trio e propozimit fillestar, i gjithë pool-i prej
      katërmbëdhjetë detektorësh, dhe një bashkësi e zgjedhur me kërkim greedy. Përzgjedhja
      greedy është prekuenciale: ansambli që vlerësohet në fold-in i ndërtohet duke
      përdorur vetëm folds-at 0 deri i−1, prandaj përzgjedhja nuk e sheh kurrë bllokun mbi
      të cilin matet."""),
    tab(
        "ensemble_summary",
        "Variantet e ansamblit kundrejt modelit më të mirë individual. Kolona e "
        "diferencës është negative kur ansambli mbetet nën të.",
        columns=[
            "pool",
            "combiner",
            "ap_mean",
            "ap_std",
            "vs_best_single",
            "fold_wins_vs_best_single",
        ],
        rename={
            "pool": "Bashkësia e anëtarëve",
            "combiner": "Rregulla",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "vs_best_single": "Δ ndaj më të mirit",
            "fold_wins_vs_best_single": "Folds të fituara",
        },
        round={"ap_mean": 4, "ap_std": 4, "vs_best_single": 4},
        font_size=9.0,
    ),
    p("""Rezultati është negativ, por jo trivial. Asnjë nga njëmbëdhjetë kombinimet e
      testuara nuk e tejkalon modelin më të mirë individual. Varianti më i mirë, ansambli
      me përzgjedhje greedy dhe mesatare rangjesh, arrin 0.4441 kundrejt 0.4491 të Deep
      SVDD-së — pra praktikisht barazim, me humbje prej vetëm 0.005 në AP, duke fituar në
      tri nga tetë folds. Në krahun tjetër, kombinimi i verbër i të katërmbëdhjetë
      anëtarëve bie në 0.249 dhe trio e propozimit fillestar në 0.169, pra humbja arrin
      deri në 0.36 njësi AP."""),
    fig(
        "ensemble_vs_single",
        "Ansamblet kundrejt modelit më të mirë individual për fold. Vija e zezë tregon "
        "Deep SVDD-në; asnjë variant ansambli nuk e tejkalon atë në mënyrë të "
        "qëndrueshme.",
        15.0,
    ),
    h3("5.3.2", "Pse dështon ansambli"),
    p("""Një rezultat negativ pa shpjegim nuk është gjetje. Mesatarizimi e zvogëlon
      variancën vetëm kur anëtarët gabojnë ndryshe [@aggarwal2015], [@zimek2014], prandaj
      u mat drejtpërdrejt korrelacioni i rangjeve mes anëtarëve."""),
    fig(
        "ensemble_rank_correlation",
        "Korrelacioni i Spearman-it mes renditjeve të prodhuara nga anëtarët e pool-it, "
        "në bllokun e fundit të testimit. Vlerat e larta tregojnë mungesë diversiteti.",
        14.0,
    ),
    p("""Matrica tregon korrelacione të larta mes shumicës së anëtarëve. Kur anëtarët
      renditin transaksionet pothuajse njësoj, mesatarja e tyre nuk sjell informacion të
      ri; ajo thjesht e holluar sinjalin e anëtarit më të mirë me sinjalin e atyre më të
      dobët. Kjo shpjegon pse pool-i i plotë është shumë më i keq se anëtari i tij më i
      mirë, dhe pse përzgjedhja greedy — e cila në praktikë konvergon te një bashkësi e
      vogël rreth anëtarit më të fortë — arrin vetëm barazim."""),
    p("""Votimi me shumicë del veçanërisht keq, dhe arsyeja është strukturore: si funksion
      renditës ai prodhon vetëm një numër të vogël vlerash të dallueshme, sa numri i
      anëtarëve plus një, prandaj shumica e transaksioneve marrin pikë identike dhe
      renditja brenda tyre është arbitrare. Për një metrikë si precizioni mesatar, që
      varet nga renditja e plotë, kjo është dëmtuese."""),
    h3("5.3.3", "A qëndron rezultati edhe me anëtarë të akorduar"),
    p("""Një kundërshtim i drejtë ndaj një rezultati negativ është se anëtarët mund të mos
      kenë qenë të akorduar mirë. Prandaj i gjithë eksperimenti u përsërit mbi folds-at e
      prodhuar me hiperparametrat e akorduar, ku modeli më i mirë individual nuk është më
      Deep SVDD-ja por vlerësuesi i akorduar i Mahalanobis-it me AP 0.664."""),
    tab(
        "ensemble_summary_tuned",
        "Variantet e ansamblit kur anëtarët janë të akorduar. Modeli më i mirë individual "
        "në këtë regjim është Mahalanobis me AP 0.664.",
        columns=[
            "pool",
            "combiner",
            "ap_mean",
            "ap_std",
            "vs_best_single",
            "fold_wins_vs_best_single",
        ],
        rename={
            "pool": "Bashkësia e anëtarëve",
            "combiner": "Rregulla",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "vs_best_single": "Δ ndaj më të mirit",
            "fold_wins_vs_best_single": "Folds të fituara",
        },
        round={"ap_mean": 4, "ap_std": 4, "vs_best_single": 4},
        font_size=9.0,
    ),
    p("""Përfundimi jo vetëm që qëndron, por forcohet. Në regjimin e akorduar hendeku mes
      ansamblit më të mirë dhe modelit më të mirë individual zgjerohet nga 0.005 në 0.055
      njësi AP, dhe asnjë variant nuk fiton në më shumë se një fold nga tetë. Arsyeja
      është e njëjtë me atë të mëparshmen, vetëm më e theksuar: sa më i fortë të jetë
      anëtari kryesues në raport me të tjerët, aq më shumë e dëmton mesatarizimi. Kur
      Mahalanobis-i i akorduar arrin 0.664 ndërsa mesatarja e anëtarëve të tjerë qëndron
      shumë më poshtë, çdo kombinim që u jep atyre peshë e ul rezultatin."""),
    h3("5.3.4", "Përgjigjja për PH3"),
    p("""Përgjigjja është negative, dhe ajo qëndron nën të dy regjimet e hiperparametrave:
      në këtë problem qasja ensemble nuk e përmirëson zbulimin krahasuar me modelin më të
      mirë individual. Përzgjedhja e
      kujdesshme e anëtarëve e afron ansamblin deri në barazim, ndërsa kombinimi i verbër
      e përkeqëson rezultatin ndjeshëm. Shkaku është i matur dhe jo hipotetik: anëtarët
      janë të korreluar dhe u mungon diversiteti që mesatarizimi kërkon."""),
    p("""Ky rezultat nuk e kundërshton literaturën që raporton përfitime nga ansamblet
      [@rayana2016], [@zhao2019lscp]; ai tregon se përfitimi varet nga diversiteti, i
      cili këtu mungon sepse të gjithë anëtarët punojnë mbi të njëjtat njëzet e nëntë
      veçori tashmë të dekoreluara nga PCA-ja. Në një hapësirë ku komponentët janë
      ortogonalë dhe sinjali është i përqendruar në pak dimensione, detektorë të
      ndryshëm konvergojnë te pothuajse i njëjti renditje."""),
]

_ANALIZA = [
    h2("5.4", "Analiza plotësuese"),
    h3("5.4.1", "Sa ndikon protokolli i vlerësimit"),
    p("""Meqë kontributi metodologjik i këtij punimi është protokolli, ndikimi i tij u mat
      drejtpërdrejt duke krahasuar tri protokolle mbi të njëjtat të dhëna dhe të njëjtat
      modele: ndarjen e vetme kronologjike 70/30, protokollin me tetë folds, dhe ndarjen
      e rastësishme të stratifikuar."""),
    tab(
        "protocol_comparison",
        "Vlerësimi nga një ndarje e vetme kundrejt mesatares mbi tetë folds. Kolona e "
        "fundit tregon nëse vlerësimi i ndarjes së vetme bie brenda një devijimi "
        "standard të shpërndarjes nëpër folds.",
        columns=[
            "Detektori",
            "AP_ndarje_e_vetme",
            "AP_8_folde",
            "sd_nder_folde",
            "rangu_ndarje_e_vetme",
            "rangu_8_folde",
            "ndryshim_rangu",
        ],
        rename={
            "AP_ndarje_e_vetme": "AP (një ndarje)",
            "AP_8_folde": "AP (8 folds)",
            "sd_nder_folde": "s.d.",
            "rangu_ndarje_e_vetme": "Rangu (një ndarje)",
            "rangu_8_folde": "Rangu (8 folds)",
            "ndryshim_rangu": "Δ rangu",
        },
        round={"AP_ndarje_e_vetme": 3, "AP_8_folde": 3, "sd_nder_folde": 3},
        font_size=8.5,
    ),
    p("""Rezultati është më i nuancuar nga sa prisja. Renditja e detektorëve mbetet
      kryesisht e njëjtë: korrelacioni i Spearman-it mes dy renditjeve është 0.952, dhe
      ndryshimi maksimal i rangut është tri pozicione. Pra ndarja e vetme kronologjike
      nuk e gabon dukshëm se cili detektor është më i mirë."""),
    p("""Ajo që ndarja e vetme nuk mund ta japë është pasiguria e vetë vlerësimit të saj.
      Shpërhapja nëpër folds është mesatarisht njëqind e shtatëmbëdhjetë për qind e
      vlerës mesatare — pra e njëjtë në madhësi me efektin që matet. Një studim që
      raporton një numër të vetëm AP-je nga një ndarje e vetme nuk ka mënyrë ta dijë këtë
      dhe as ta komunikojë."""),
    fig(
        "protocol_comparison",
        "Vlerësimi nga ndarja e vetme (kryqi i zi) i vendosur mbi shpërndarjen nëpër tetë "
        "folds (rrethi dhe shiriti prej një devijimi standard). Renditja përputhet; "
        "pasiguria është e madhe dhe e padukshme nga një ndarje e vetme.",
        14.5,
    ),
    p("""Krahasimi i tretë është më i mprehti. Ndarja e rastësishme e stratifikuar, e cila
      lejon që transaksionet e së njëjtës periudhë të shpërndahen mes trajnimit dhe
      testimit, e fryn precizionin mesatar të metodave të pambikëqyrura mesatarisht 2.74
      herë, me maksimum 4.49 herë për Isolation Forest-in. Referencën e mbikëqyrur
      ndarja e rastësishme nuk e ndihmon aspak — përkundrazi, AP-ja e saj bie lehtë, nga
      0.768 në 0.704."""),
    tab(
        "protocol_inflation",
        "Fryrja e precizionit mesatar kur ndarja kronologjike zëvendësohet me një ndarje "
        "të rastësishme të stratifikuar. Protokolli me ndarje të rastësishme paraqitet "
        "vetëm për krahasim; ai lejon rrjedhje informacioni.",
        round={"AP_kronologjik": 3, "AP_i_perzier": 3, "fryrja": 2},
        rename={
            "AP_kronologjik": "AP kronologjik",
            "AP_i_perzier": "AP i përzier",
            "fryrja": "Fryrja",
        },
        font_size=9.0,
    ),
    p("""Kjo asimetri është vetë gjetja. Ndarja e rastësishme ndihmon pikërisht metodat e
      bazuara në afërsi dhe densitet, sepse u jep atyre në bashkësinë e trajnimit
      transaksione nga e njëjta periudhë me ato të testimit; modeli i mbikëqyrur, i cili
      mëson një drejtim diskriminues në vend të një modeli normaliteti, nuk përfiton.
      Pra fryrja nuk është një zhvendosje uniforme e të gjitha rezultateve lart: ajo
      shtrembëron krahasimin mes familjeve."""),
    h3("5.4.2", "Zhvendosja: cila popullatë lëviz"),
    p("""Nëse metodat e pambikëqyrura degradojnë me kalimin e kohës, është vendimtare të
      dihet pse. Nëse zhvendoset popullata normale, modeli i normalitetit vjetërsohet dhe
      ritrajnimi periodik mbi të dhëna të paetiketuara e zgjidh problemin. Nëse
      zhvendoset popullata e mashtrimeve, ritrajnimi nuk ndihmon fare. Prandaj u matën të
      dyja veçmas, në secilin fold."""),
    tab(
        "drift_per_fold",
        "Dekompozimi i zhvendosjes për fold. PSI mesatar mbi njëzet e nëntë veçoritë, "
        "veçmas për popullatën normale dhe atë mashtruese, si dhe AP-ja e një detektori "
        "pa model bazuar vetëm në normën ‖z‖.",
        columns=[
            "fold",
            "psi_normals_mean",
            "psi_normals_over_moderate",
            "psi_frauds_mean",
            "psi_frauds_over_moderate",
            "train_ap_distance",
            "test_ap_distance",
            "test_cohens_d",
        ],
        rename={
            "fold": "Fold",
            "psi_normals_mean": "PSI normale",
            "psi_normals_over_moderate": "Veçori >0.10",
            "psi_frauds_mean": "PSI mashtrime",
            "psi_frauds_over_moderate": "Veçori >0.10 ",
            "train_ap_distance": "AP(‖z‖) trajnim",
            "test_ap_distance": "AP(‖z‖) test",
            "test_cohens_d": "Cohen d",
        },
        round={
            "psi_normals_mean": 3,
            "psi_frauds_mean": 3,
            "train_ap_distance": 3,
            "test_ap_distance": 3,
            "test_cohens_d": 2,
        },
        font_size=8.5,
    ),
    p("""Rezultati është i qartë dhe i qëndrueshëm nëpër të tetë folds-at. Popullata
      normale lëviz pak: indeksi i stabilitetit të popullatës është mesatarisht 0.14, në
      kufirin e poshtëm të asaj që konsiderohet zhvendosje e moderuar, dhe zakonisht
      vetëm rreth dhjetë deri pesëmbëdhjetë nga njëzet e nëntë veçoritë e kalojnë atë
      prag. Popullata e mashtrimeve, përkundrazi, lëviz masivisht: PSI-ja mesatare është
      3.22, njëzet e tri herë më e madhe, dhe të njëzet e nëntë veçoritë e kalojnë pragun
      në çdo fold pa përjashtim."""),
    fig(
        "drift_psi_decomposition",
        "Zhvendosja e matur veçmas për të dyja popullatat, në secilin fold. Vijat "
        "horizontale shënojnë pragjet konvencionale të zhvendosjes së moderuar dhe të "
        "madhe.",
        14.5,
    ),
    p("""Për ta konfirmuar këtë pa asnjë model, u ndërtua një detektor krejtësisht pa
      parametra: pikë anomalie është norma euklidiane e vektorit të veçorive, e skaluar
      me statistikat e dritares së trajnimit. Precizioni mesatar i këtij detektori bie
      nga 0.223 brenda dritares së trajnimit në 0.104 në bllokun e testimit. Meqë ky
      detektor nuk mëson asgjë, rënia nuk mund t'i atribuohet mbipërshtatjes ose zgjedhjes
      së algoritmit — ajo është veti e vetë të dhënave."""),
    fig(
        "drift_separability",
        "Ndashmëria e matur me një detektor pa model brenda dritares së trajnimit "
        "kundrejt bllokut të testimit. Rënia riprodhohet pa asnjë algoritëm të mësuar.",
        14.0,
    ),
    p("""Përfundimi është se mashtrimet e periudhave të mëvonshme janë intrinsikisht më të
      vështira për t'u dalluar: ato qëndrojnë më afër manifoldit të transaksioneve
      normale. Kjo shpjegon njëkohësisht pse rezultatet e pambikëqyrura janë të ulëta në
      protokollin kronologjik, pse ndarja e rastësishme i fryn ato, dhe pse ritrajnimi i
      thjeshtë nuk do të ishte zgjidhje."""),
    p("""Së fundi u testua nëse një monitor pa etiketa do ta kishte vënë re zhvendosjen. U
      përdor testi i Page-Hinkley-t mbi rrjedhën e pikëve, me prag të kalibruar për çdo
      kombinim fold-model kundrejt të dhënave referuese pa ndryshim. Me prag të
      kalibruar sinjalet janë të rralla dhe të vonshme, zakonisht pas rreth një të tretës
      së bllokut. Me një prag fiks të pakalibruar, i njëjti test prodhonte dhjetëra
      sinjale për bllok, pra praktikisht vetëm zhurmë; ky është një kujtues se
      monitorimi i zhvendosjes pa etiketa kërkon kalibrim të kujdesshëm për të qenë i
      dobishëm."""),
    h3("5.4.3", "Çfarë shohin modelet"),
    p("""Renditja e algoritmeve u shpjegua përmes atribuimit të veçorive. Për secilin
      model u llogaritën atribuimet — gabimi i rindërtimit për komponent te autoenkoderi,
      vlerat SHAP te Isolation Forest-i, dhe rëndësia me permutim si masë e përgjithshme
      — dhe u krahasuan me fuqinë diskriminuese njëvariablëshe të matur në analizën
      eksploruese."""),
    tab(
        "explain_signal_agreement",
        "Përputhja mes vëmendjes së modelit dhe sinjalit realisht diskriminues, matur me "
        "korrelacionin e Spearman-it kundrejt |AUC − 0.5| të secilës veçori.",
        rename={
            "atribuimi": "Atribuimi",
            "spearman_vs_auc_gap": "ρ me sinjalin",
            "p_value": "p",
            "top3": "Tri veçoritë kryesore",
        },
        round={"spearman_vs_auc_gap": 3, "p_value": 4},
        font_size=9.5,
    ),
    p("""Rezultati është ndoshta gjetja më e mprehtë e këtij punimi. Gabimi i rindërtimit
      të autoenkoderit korrelon fort me sinjalin realisht të disponueshëm, me ρ = 0.75 dhe
      p = 3 × 10⁻⁶, dhe tri veçoritë e tij kryesore — V14, V17, V12 — përputhen pothuajse
      plotësisht me tri më diskriminueset e matura në mënyrë të pavarur. One-Class SVM-ja
      qëndron në mes me ρ = 0.50. Isolation Forest-i, përkundrazi, ka ρ = 0.02 me p = 0.91:
      vëmendja e tij nuk ka absolutisht asnjë lidhje me vendin ku qëndron sinjali, dhe
      veçoria e tij kryesore, V25, është praktikisht pa fuqi diskriminuese."""),
    p("""Kjo renditje e përputhjes — 0.75, 0.50, 0.02 — është pikërisht renditja e cilësisë
      së tyre të zbulimit mes këtyre tre modeleve. Mekanizmi është i kuptueshëm: Isolation
      Forest-i zgjedh dimensione dhe pragje ndarjeje në mënyrë të rastësishme, pa asnjë
      preferencë për informativitetin, prandaj në një hapësirë njëzet e nëntë-dimensionale
      ku sinjali është i përqendruar në pak komponentë, shumica e kapacitetit të tij
      harxhohet."""),
    fig(
        "explain_attention_vs_signal",
        "Atribuimi i Isolation Forest-it kundrejt sinjalit univariat të disponueshëm për "
        "secilën veçori. Mungesa e çdo lidhjeje është e dukshme.",
        13.5,
    ),
    fig(
        "explain_ae_reconstruction",
        "Gabimi mesatar i rindërtimit të autoenkoderit për komponent, veçmas për "
        "transaksionet legjitime dhe ato mashtruese, i renditur sipas diferencës.",
        15.0,
    ),
    h3("5.4.4", "Pragu adaptiv"),
    p("""Analiza e fundit trajton një problem operacional të vërejtur gjatë implementimit
      dhe jo të planifikuar në propozim. Pragu i nxjerrë nga dritarja e trajnimit fikson
      një vlerë pike, jo një ngarkesë pune, prandaj kur shpërndarja e pikëve zhvendoset
      numri i alarmeve zhvendoset me të."""),
    tab(
        "adaptive_threshold_summary",
        "Pragu statik kundrejt atij adaptiv me dritare rrëshqitëse, mesatarizuar mbi tetë "
        "folds. Koeficienti i variacionit mat sa luhatet norma e alarmeve brenda një "
        "blloku.",
        columns=[
            "model",
            "regjimi",
            "alert_rate",
            "alert_rate_cv",
            "precision",
            "recall",
            "f1",
            "alerts_per_block",
        ],
        rename={
            "model": "Detektori",
            "regjimi": "Regjimi",
            "alert_rate": "Norma e alarmeve",
            "alert_rate_cv": "CV i ngarkesës",
            "precision": "Preciziteti",
            "recall": "Recall",
            "f1": "F1",
            "alerts_per_block": "Alarme/bllok",
        },
        round={
            "alert_rate": 4,
            "alert_rate_cv": 3,
            "precision": 3,
            "recall": 3,
            "f1": 3,
            "alerts_per_block": 1,
        },
        font_size=8.5,
    ),
    p("""Pragu adaptiv përmirëson të dyja anët njëkohësisht, gjë që nuk ishte e
      garantuar. Luhatja e ngarkesës bie nga një koeficient variacioni prej 0.83 në 0.64,
      pra ngarkesa hetimore bëhet dukshëm më e parashikueshme. Njëkohësisht F1-shi
      mesatar rritet nga 0.128 në 0.169, një përmirësim relativ prej rreth tridhjetë e dy
      për qind, dhe si preciziteti ashtu edhe ndjeshmëria përmirësohen për të pesë
      modelet e testuara."""),
    p("""Mekanizmi është i thjeshtë: pragu i nxjerrë nga dritarja e trajnimit rezulton
      tepër konservativ për bllokun e testimit, prandaj sistemi ngre më pak alarme sesa
      buxheti i lejon. Pragu adaptiv e rikalibron atë ndaj rrjedhës aktuale dhe e sjell
      normën e alarmeve pranë asaj të synuar."""),
    fig(
        "adaptive_alert_rate",
        "Norma e alarmeve nëpër nën-blloqe kohore me prag statik kundrejt atij adaptiv. "
        "Pragu adaptiv e mban ngarkesën dukshëm më të qëndrueshme.",
        14.5,
    ),
    fig(
        "adaptive_tradeoff",
        "Kompromisi mes qëndrueshmërisë së ngarkesës dhe cilësisë së zbulimit. Pragu "
        "adaptiv i zhvendos të gjithë detektorët lart dhe majtas, pra në drejtimin e "
        "dëshiruar në të dy boshtet.",
        13.5,
    ),
    p("""Kostoja llogaritëse e kësaj procedure u mat gjithashtu në rrjedhë. Për modelet e
      shpejta ajo është praktikisht zero: për Deep SVDD-në percentili i nëntëdhjetë e
      nëntë i vonesës madje ra lehtë, nga 57.3 në 52.9 milisekonda. Për Isolation
      Forest-in, i cili tashmë ishte i ngadalshëm, rillogaritja periodike e kuantilit e
      rriti bishtin nga 109.6 në 166.5 milisekonda. Pra kostoja varet nga sa i lirë është
      modeli bazë."""),
    h3("5.4.5", "Akordimi i hiperparametrave dhe qëndrueshmëria e renditjes"),
    p("""Të gjitha rezultatet e mësipërme u prodhuan me hiperparametrat e parazgjedhur, të
      marrë nga vlerat e rekomanduara në literaturën origjinale të secilit algoritëm. Kjo
      është zgjedhja e zakonshme në krahasime të gjera, por ajo lë hapur një kundërshtim
      të drejtë: ndoshta ndonjë detektor renditet keq thjesht sepse nuk u akordua. Prandaj
      u krye një kërkim me njëzet e pesë prova për secilin nga dymbëdhjetë detektorët e
      akordueshëm, mbi një ndarje të brendshme kohore të dritares së trajnimit, dhe pastaj
      i gjithë protokolli me tetë folds u rikryesua nga fillimi me konfigurimet
      fituese."""),
    p("""Rezultati ka dy anë, dhe e dyta është më e rëndësishme se e para."""),
    tab(
        "tuning_effect",
        "Efekti i akordimit të hiperparametrave mbi precizionin mesatar në blloqet e "
        "testimit. Kolona e parafundit tregon përmirësimin e matur në validimin e "
        "brendshëm, ku u bë përzgjedhja.",
        rename={
            "AP_default": "AP (parazgjedhje)",
            "AP_i_akorduar": "AP (i akorduar)",
            "delta_test": "Δ test",
            "delta_inner": "Δ validim i brendshëm",
            "folds_te_permiresuara": "Folds të përmirësuara",
        },
        round={"AP_default": 3, "AP_i_akorduar": 3, "delta_test": 3, "delta_inner": 3},
        font_size=9.0,
    ),
    p("""Ana e parë është se akordimi ndihmon, dhe ndihmon në mënyrë të qëndrueshme.
      Precizioni mesatar përmirësohet për tetë nga dymbëdhjetë detektorët, dhe mesatarja e
      grumbulluar mbi detektorët e akorduar rritet në të tetë folds-at pa përjashtim
      (testi i çiftuar i Wilcoxon-it, p = 0.0078). Përmirësimet më të mëdha janë dramatike:
      vlerësuesi robust i Mahalanobis-it kalon nga 0.088 në 0.664, pra nga i fundit në të
      dytin, dhe detektori linear i rindërtimit me PCA nga 0.146 në 0.460."""),
    p("""Ana e dytë është se renditja nuk mbijeton. Korrelacioni i rangjeve para dhe pas
      akordimit është vetëm 0.168 me p-vlerë 0.6 — pra praktikisht asnjë lidhje. Detektori
      më i mirë i pambikëqyrur ndryshon nga Deep SVDD-ja në Mahalanobis, dhe Deep SVDD-ja
      vetë bie nga 0.449 në 0.156. Me fjalë të tjera, pyetja "cili algoritëm është më i
      miri" ka përgjigje të ndryshme varësisht se a janë akorduar modelet apo jo, edhe kur
      akordimi bëhet plotësisht pa parë bashkësinë e testimit."""),
    fig(
        "tuning_effect",
        "Precizioni mesatar para dhe pas akordimit. Rrethi gri tregon konfigurimin e "
        "parazgjedhur, ai me ngjyrë atë të akorduar; gjatësia e segmentit është efekti i "
        "akordimit.",
        14.0,
    ),
    p("""Rasti i Deep SVDD-së meriton shpjegim, sepse është i vetmi degradim i madh.
      Konfigurimi fitues rriti dimensionin e përfaqësimit nga dymbëdhjetë në njëzet e tre,
      pra afër dimensionit hyrës prej njëzet e nëntë. Me kaq pak ngjeshje, rrjeti mund t'i
      hartojë brenda hipersferës edhe pikat që duhet të mbeteshin jashtë; kompaktësia
      arrihet duke humbur pikërisht ndjeshmërinë që e bënte modelin të dobishëm. Validimi
      i brendshëm e preferoi këtë konfigurim me një diferencë të vogël, 0.028, dhe ajo
      diferencë e vogël doli të ishte zhurmë e sllicës së brendshme."""),
    p("""Ky është rasti kufitar i një lidhjeje që përndryshe qëndron. Korrelacioni mes
      përmirësimit të matur në validimin e brendshëm dhe atij të realizuar në blloqet e
      testimit është 0.72 me p-vlerë 0.008: përgjithësisht, ajo që ndihmon brenda dritares
      së trajnimit ndihmon edhe përtej saj. Por korrelacioni nuk është një, dhe rasti ku ai
      thyhet është pikërisht modeli që ishte kryesues."""),
    fig(
        "tuning_transfer",
        "Përmirësimi i matur në validimin e brendshëm kundrejt atij të realizuar në "
        "blloqet e testimit. Vija me pika tregon transferim të përsosur; Deep SVDD-ja "
        "është përjashtimi i vetëm i madh.",
        13.5,
    ),
    p("""Përfundimi për interpretimin e gjithë këtij kapitulli është i qartë dhe duhet
      thënë shprehimisht: përgjigjja për pyetjen e dytë hulumtuese është e kushtëzuar nga
      protokolli i hiperparametrave. Nën vlerat e parazgjedhura, Deep SVDD-ja ofron
      balancën më të mirë; nën akordim me validim të brendshëm, Mahalanobis-i i akorduar
      e tejkalon atë ndjeshëm. Të dyja janë përgjigje legjitime për pyetje pak të
      ndryshme, dhe fakti se ato ndryshojnë është vetë një gjetje: renditjet e publikuara
      mbi këtë dataset duhen lexuar gjithmonë bashkë me protokollin e akordimit që i
      prodhoi."""),
    note("""Një vërejtje mbi Mahalanobis-in e akorduar: parametri fitues e çoi fraksionin
      e mbështetjes në 0.988, pra vlerësuesi robust u kthye praktikisht në vlerësuesin
      klasik të kovariancës. Me kontaminim prej vetëm 0.17 për qind, robustësia kushton më
      shumë informacion sesa kursen — një shembull i mirë se si një zgjedhje e
      arsyeshme si parazgjedhje mund të jetë e gabuar për një regjim të veçantë."""),
    h3("5.4.6", "A mund të akordohet pa etiketa fare"),
    p("""Akordimi i përshkruar më sipër përdor etiketa historike në sllicën e brendshme të
      validimit. Ky është një supozim i deklaruar dhe i njëjtë me atë të referencës së
      mbikëqyrur, por mbetet supozim. Pyetja e fundit e këtij kapitulli është çfarë do të
      ndodhte pa të: a mund të zgjidhen hiperparametrat me kritere që nuk shohin asnjë
      etiketë?"""),
    p("""Për pesë detektorë u vlerësua një rrjetë e vogël dhe e deklaruar konfigurimesh me
      tri kritere paralelisht: AP-në në validimin e brendshëm, e cila përdor etiketa, dhe
      kriteret Excess-Mass e Mass-Volume, të cilat nuk përdorin asnjë. Krahasimi nuk bëhet
      mbi vlerat — ato nuk janë në të njëjtën shkallë — por mbi zgjedhjen: a bien në të
      njëjtin konfigurim."""),
    tab(
        "unsupervised_selection",
        "Konfigurimi që do të zgjidhte secili kriter, dhe kostoja e zgjedhjes pa etiketa. "
        "Humbja relative shprehet si pjesë e hapësirës mes konfigurimit më të mirë dhe atij "
        "më të keq në rrjetë.",
        columns=[
            "Detektori",
            "Konfigurime",
            "Zgjedhja sipas AP",
            "Zgjedhja sipas EM",
            "EM përputhet",
            "Humbja relative",
            "rho(AP, EM)",
        ],
        font_size=8.0,
    ),
    fig(
        "unsupervised_selection",
        "Rangu i çdo konfigurimi sipas kriterit me etiketa kundrejt rangut sipas kriterit "
        "Excess-Mass, brenda rrjetës së secilit detektor. Vija me pika tregon përputhje "
        "të përsosur.",
        13.5,
    ),
    p("""Përgjigjja është qartësisht negative. Kriteri Excess-Mass nuk zgjedh të njëjtin
      konfigurim si kriteri me etiketa në asnjë nga pesë detektorët, dhe Mass-Volume
      përputhet vetëm në dy. Kur zgjedhjet ndryshojnë, humbja mesatare është rreth
      shtatëdhjetë e shtatë për qind e hapësirës mes konfigurimit më të mirë dhe atij më
      të keq në rrjetë — pra zgjedhja pa etiketa bie shumë më afër fundit të rrjetës sesa
      majës së saj. Më shqetësuese ende, korrelacioni mesatar mes renditjes sipas
      Excess-Mass-it dhe asaj sipas AP-së është negativ, rreth −0.30: në këtë problem
      kriteri nuk është thjesht i zhurmshëm, por shpesh anon në drejtimin e gabuar."""),
    p("""Rasti i HBOS-it e ilustron mekanizmin qartë. Duke rritur numrin e koshave nga
      dhjetë në dyqind, kriteri Excess-Mass përmirësohet vazhdimisht, sepse histogramat më
      të imëta i përqendrojnë grupet e nivelit në vëllim më të vogël — pikërisht ajo që
      kriteri shpërblen. Por AP-ja bie njëkohësisht nga 0.35 në 0.22, sepse koshat e imët e
      bëjnë modelin të mbipërshtatet ndaj strukturës së hollë të transaksioneve normale dhe
      të humbasë aftësinë përgjithësuese. Të dy treguesit janë të saktë për atë që matin;
      thjesht ata nuk matin të njëjtën gjë."""),
    p("""Ky rezultat duhet lexuar bashkë me një kufizim të vetë metodës. Vlerësimi i masës
      Lebesgue kërkon nënhapësira me pak dimensione, dhe kjo do të thotë se hiperparametrat
      që humbin kuptimin brenda një nënhapësire pesëdimensionale nuk mund të dallohen fare.
      Detektori linear i rindërtimit u përjashtua shprehimisht nga kjo analizë pikërisht për
      këtë arsye: numri i komponentëve të ruajtur kufizohet nga dimensioni i nënhapësirës,
      prandaj çdo konfigurim mbi atë vlerë jep rezultat identik. Ky nuk është defekt
      implementimi, por kufi i qenësishëm i përafrimit me nënhapësira të rastësishme, dhe ai
      e ngushton fushën ku këto kritere janë të zbatueshme."""),
    p("""Përfundimi praktik është se, të paktën në këtë problem dhe me këtë përafrim,
      akordimi krejtësisht pa etiketa nuk është alternativë e besueshme. Kjo e forcon
      justifikimin e rrugës së zgjedhur për akordimin kryesor — validim i brendshëm me
      etiketa historike — dhe njëkohësisht e bën edhe më domethënëse gjetjen e mëparshme se
      vetë akordimi e rirendit fushën. Nëse akordimi ka rëndësi kaq të madhe dhe nuk mund të
      kryhet pa etiketa, atëherë disponueshmëria e etiketave historike është edhe më
      kritike sesa e sugjeron vetëm hendeku i drejtpërdrejtë ndaj referencës së
      mbikëqyrur."""),
    h3("5.4.7", "Ndjeshmëria ndaj kontaminimit dhe ablacioni i autoenkoderit"),
    p("""Dy analiza ndihmëse kontrollojnë nëse përfundimet varen nga zgjedhje arbitrare.
      E para skanon hiperparametrin e kontaminimit në dy urdhra madhësie; renditja e
      modeleve ruhet, ndërsa vlerat absolute të F1-shit ndryshojnë siç pritet, me maksimum
      rreth vlerës 0.005."""),
    fig(
        "sweep_f1",
        "F1-shi kundrejt hiperparametrit të kontaminimit, për të gjithë "
        "detektorët, në ndarjen e vetme 70/30.",
        14.0,
    ),
    p("""E dyta është ablacioni i autoenkoderit mbi dimensionin latent dhe numrin e
      epokave. Rezultati tregon një optimum të qartë te dimensioni latent tetë; si
      dimensioni katër ashtu edhe gjashtëmbëdhjetë janë dukshëm më të dobët, gjë që
      përputhet me interpretimin se ngjeshja shumë e fortë humbet informacion ndërsa ajo
      shumë e dobët e lejon rrjetin të rindërtojë edhe anomalitë."""),
    tab(
        "ae_ablation",
        "Ablacioni i autoenkoderit mbi dimensionin latent dhe numrin e epokave, i "
        "vlerësuar në ndarjen e vetme 70/30.",
        rename={
            "latent_dim": "Dimensioni latent",
            "epochs": "Epoka",
            "ap": "AP",
            "roc_auc": "ROC-AUC",
            "fit_time_s": "Koha (s)",
        },
        round={"ap": 4, "roc_auc": 4, "fit_time_s": 1},
        font_size=9.5,
    ),
]

BLOCKS = _HYRJE + _PH2 + _PH3 + _ANALIZA

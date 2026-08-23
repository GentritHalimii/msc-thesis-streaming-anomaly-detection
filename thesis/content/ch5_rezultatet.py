"""Kapitulli 5 — REZULTATET."""

from blocks import bullets, fig, h1, h2, h3, note, numbers, p, tab

_HYRJE = [
    h1("5", "Rezultatet"),
    p("""Rezultatet paraqiten në pesë blloqe. I pari përcakton kufirin e sipërm gjeometrik të
      vetë problemit pa përshtatur asnjë model, sepse ai kufi e ndryshon mënyrën si duhet
      lexuar çdo gjë që vjen pas tij. Tre blloqet e ardhshme u përgjigjen tri pyetjeve
      hulumtuese sipas radhës. I fundit paraqet studimet e thelluara për secilin algoritëm dhe
      analizat shpjeguese që i japin kuptim renditjes."""),
    p("""Çdo vlerë e raportuar këtu gjendet në një artefakt të gjeneruar nga kodi dhe të
      shoqëruar me një manifest që përmban SHA-në e commit-it dhe hash-in e konfigurimit; asnjë
      numër nuk është transkriptuar me dorë."""),
    note("""Konventë raportimi: kudo ku shfaqet referenca me Regresion Logjistik, ajo shënohet
      shprehimisht si referencë e mbikëqyrur. Ajo nuk konkurron me metodat unsupervised, sepse
      ka pasur në dispozicion etiketat historike; roli i saj është të tregojë kufirin e sipërm
      të arritshëm kur ato etiketa ekzistojnë."""),
]

_GJEOMETRIA = [
    h2("5.1", "Kufiri i sipërm gjeometrik i problemit"),
    p("""Të tria metodat unsupervised të këtij studimi e përcaktojnë anomalinë përmes një nocioni
      largësie ose ngjeshjeje. Prandaj pyetja e parë nuk është se cila prej tyre është më e
      mirë, por se sa larg mund të shkojë çdo metodë e kësaj natyre mbi këto të dhëna. Përgjigja
      merret pa përshtatur asnjë model."""),
    tab(
        "geometry_summary",
        "Karakterizimi gjeometrik i dritares së trajnimit dhe i asaj të testimit. Dimensioni i "
        "brendshëm matet me dy vlerësues të pavarur, ndërsa AP-ja në kolonën e parafundit vjen "
        "nga një detektor pa parametra që pikëzon vetëm sipas distancës.",
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
            "id_mle_normale": "ID (MLE)",
            "id_twonn_normale": "ID (TwoNN)",
            "knn_distanca_normale": "kNN legjitime",
            "knn_distanca_mashtrime": "kNN mashtrime",
            "raporti_distancave": "Raporti",
            "ap_vetem_distance": "AP (vetëm distancë)",
            "rangu_median_i_mashtrimit": "Rangu median",
            "mashtrime_ne_top100": "Në top-100",
        },
        round={
            "id_mle_normale": 2,
            "id_twonn_normale": 2,
            "knn_distanca_normale": 2,
            "knn_distanca_mashtrime": 2,
            "raporti_distancave": 2,
            "ap_vetem_distance": 3,
            "rangu_median_i_mashtrimit": 0,
        },
        font_size=8.5,
    ),
    p("""Gjetja e parë është se supozimi gjeometrik qëndron. Mashtrimet ndodhen mesatarisht 7.9
      herë më larg nga dhjetë fqinjët e tyre legjitimë më të afërt sesa një transaksion tipik
      legjitim, dhe raporti mbetet mbi gjashtë edhe në dritaren e testimit. Në këtë kuptim ato
      janë vërtet vlera të jashtëzakonshme."""),
    p("""Gjetja e dytë është se kjo largësi nuk përkthehet në zbulim. Detektori pa parametra që
      pikëzon vetëm sipas kësaj distance arrin Average Precision 0.304 në dritaren e trajnimit
      dhe 0.124 në atë të testimit. Arsyeja është numerike dhe e thjeshtë: klasa legjitime ka
      afërsisht dyqind mijë anëtarë, dhe pesë për qind e bishtit të saj janë dhjetë mijë
      transaksione që ndodhen po ashtu larg. Katërqind e nëntëdhjetë e dy mashtrime nuk mund të
      konkurrojnë numerikisht me atë bisht."""),
    fig(
        "geometry_knn_distance",
        "Distanca deri te dhjetë fqinjët legjitimë më të afërt, për të dyja klasat në dritaren e "
        "trajnimit. Mashtrimet janë qartësisht më larg, por bishti i klasës legjitime shtrihet "
        "mbi të njëjtin interval.",
        14.5,
    ),
    p("""Përkthimi në terma operacionalë e bën pasojën të prekshme. Mashtrimi median kërkon
      shqyrtimin e rreth pesëqind e tridhjetë alarmeve përpara se të arrihet, dhe brenda njëqind
      alarmeve të para arrihen vetëm dyzet nga treqind e tetëdhjetë e katër mashtrime të
      dritares së trajnimit. Në dritaren e testimit, ku problemi është më i vështirë, arrihen
      vetëm gjashtë nga njëqind e tetë."""),
    fig(
        "geometry_cost_to_catch",
        "Përqindja e mashtrimeve të kapura kundrejt numrit të alarmeve që duhen shqyrtuar, kur "
        "renditja bëhet vetëm sipas distancës nga klasa legjitime. Boshti horizontal është në "
        "shkallë logaritmike.",
        14.5,
    ),
    p("""Gjetja e tretë ka të bëjë me strukturën e hapësirës. Dimensioni i brendshëm i klasës
      legjitime vlerësohet rreth 3.8 me metodën TwoNN dhe rreth 7.3 me metodën e gjasës
      maksimale, kundrejt njëzet e nëntë dimensioneve nominale. Të dy vlerësuesit janë të
      njohur për anshmëri në drejtime të kundërta, prandaj vlera e vërtetë ndodhet me gjasë
      brenda atij intervali; të dy bien dakord se struktura reale është shumë më e ulët se
      hapësira në të cilën është përfaqësuar. Kjo ka pasojë të drejtpërdrejtë për Autoencoder-in,
      dimensioni latent i të cilit duhet të jetë i krahasueshëm me këtë vlerë, dhe kjo pritshmëri
      testohet në nënkapitullin 5.5.2."""),
    p("""Së fundi, fuqia diskriminuese është e përqendruar por jo e tepërt: pesë veçoritë më
      informative mbajnë vetëm tridhjetë e dy për qind të fuqisë totale njëvariablëshe, pra
      sinjali është i shpërndarë mbi një numër të konsiderueshëm komponentësh, edhe pse jo mbi
      të gjithë njëzet e nëntë. Ky fakt do të rimerret kur të shpjegohet sjellja e Isolation
      Forest-it."""),
    p("""Përfundimi i këtij nënkapitulli përcakton kornizën e leximit për gjithë kapitullin. Nëse
      një detektor i trajnuar arrin Average Precision në rendin e 0.1 deri 0.3 mbi këto të
      dhëna, ai nuk është domosdoshmërisht i dobët; ai ndodhet afër kufirit që gjeometria e
      lejon. Pyetja e vërtetë bëhet se kush e kalon atë kufi dhe me çfarë mjetesh."""),
]

_PH2 = [
    h2("5.3", "PH2: krahasimi i algoritmeve"),
    h3("5.3.1", "Rezultatet nën konfigurimin bazë"),
    p("""Tabela kryesore paraqet tri algoritmet unsupervised dhe referencën e mbikëqyrur, të
      vlerësuara në tetë pika kohore prerjeje me hiperparametrat e parazgjedhur dhe me skalim
      standard. Ky është konfigurimi bazë, jo ai më i mirë i arritshëm; të dy raportohen, dhe
      dallimi mes tyre është vetë një rezultat."""),
    tab(
        "benchmark_summary",
        "Rezultatet kryesore mbi tetë fold-e nën konfigurimin bazë. AP-ja është metrika parësore; "
        "rangu mesatar llogaritet mbi AP-në për fold. Kostoja e pikëzimit është mikrosekonda për "
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
    p("""Tri gjetje dalin menjëherë. E para është hendeku i referencës: modeli i mbikëqyrur arrin
      Average Precision 0.720 dhe fiton në të tetë fold-et pa përjashtim, pra rangun mesatar
      1.00, ndërsa metoda më e mirë unsupervised arrin 0.193. Raporti afërsisht 3.7 mes tyre
      është kuantifikimi i drejtpërdrejtë i vlerës së etiketave historike në këtë problem."""),
    p("""E dyta është renditja brenda fushës unsupervised. Autoencoder-i kryeson me 0.193, i
      ndjekur nga One-Class SVM me 0.148 dhe nga Isolation Forest me 0.091. Të tre qëndrojnë
      brenda ose pak nën kufirin gjeometrik të matur në nënkapitullin 5.1, gjë që e mbështet
      leximin se pengesa kryesore është vetë problemi."""),
    p("""E treta është dallimi mes Average Precision dhe AUC-ROC. Isolation Forest-i, me AP 0.091,
      ka AUC-ROC 0.941, praktikisht të njëjtën me atë të Autoencoder-it, i cili ka AP dyfish më
      të lartë. Nëse do të raportohej vetëm ROC, siç bën një pjesë e literaturës mbi këtë
      dataset, të tre detektorët do të dukeshin ekuivalentë. Ky është ilustrimi më i qartë
      empirik i argumentit teorik të Davis-it dhe Goadrich-it dhe të Saito-s e Rehmsmeier-it
      [@davis2006], [@saito2015]."""),
    fig(
        "benchmark_ap_ranking",
        "Average Precision për detektor, mesatarizuar mbi tetë fold-e, me devijimin standard si "
        "shirit gabimi.",
        14.0,
    ),
    p("""Shiritat e gabimit meritojnë vëmendje po aq sa vetë mesataret. Devijimi standard nëpër
      fold-e është i krahasueshëm me vlerën mesatare për çdo detektor unsupervised, dhe për
      Autoencoder-in ai madje e tejkalon atë. Kjo do të thotë se performanca e një detektori të
      vetëm ndryshon në mënyrë dramatike varësisht se në cilën pikë kohore vendoset."""),
    fig(
        "benchmark_ap_per_fold",
        "Average Precision për çdo detektor në secilin fold, në shkallë logaritmike. Fold-i 1, i "
        "cili përmban një grumbullim prej tetëdhjetë e tetë mashtrimesh, është dukshëm më i "
        "lehtë për të gjithë detektorët.",
        15.0,
    ),
    p("""Fold-i 1 është vlerë ekstreme sistematike, ku performanca e çdo detektori hidhet lart.
      Ai përmban tetëdhjetë e tetë mashtrime, gati katër herë mbi mesataren prej njëzet e tre të
      blloqeve të tjera, dhe
      analiza e zhvendosjes tregon se mashtrimet e atij blloku janë edhe dukshëm më ekstreme në
      hapësirën e veçorive. Një studim që do të kishte zgjedhur rastësisht atë periudhë si
      bashkësi testimi do të raportonte rezultate shumë më optimiste pa asnjë ndryshim në
      metodë."""),
    h3("5.3.2", "A janë dallimet statistikisht të qëndrueshme"),
    p("""Testi omnibus i Friedman-it mbi matricën e rangjeve refuzon hipotezën se detektorët janë
      ekuivalentë, si për tri metodat unsupervised ashtu edhe për të katër modelet së bashku.
      Kufizimi i krahasimit te tri algoritmet ka një përfitim metodologjik që meriton të
      theksohet: diferenca kritike e Nemenyi-t bie në 1.17 njësi rangu, ndërsa gjerësia e
      rangjeve mesatare është 1.50, prandaj testi post-hoc bëhet i përdorshëm. Me një bashkësi
      më të gjerë detektorësh, diferenca kritike do ta tejkalonte gjerësinë e rangjeve dhe testi
      nuk do të mund të refuzonte kurrë."""),
    tab(
        "significance_omnibus",
        "Testi omnibus i Friedman-it dhe diferenca kritike e Nemenyi-t për dy grupe krahasimi.",
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
    fig(
        "significance_cd_core",
        "Diagrami i diferencës kritike për të katër modelet. Detektorët e lidhur me një shirit "
        "horizontal nuk dallohen statistikisht në nivelin 0.05.",
        14.0,
    ),
    p("""Për krahasimet që pyetjet hulumtuese i emërtojnë shprehimisht u përdor testi i çiftuar i
      Wilcoxon-it me korrigjim Holm. Bashkësia prej gjashtë krahasimesh u fiksua në kod përpara
      se të shihej ndonjë rezultat, dhe numri i tyre u zgjodh që korrigjimi të mbetet i
      kalueshëm: me tetë fold-e p-vlera më e vogël e arritshme është 0.0078, e cila shumëzuar me
      gjashtë jep 0.047 dhe mezi qëndron nën 0.05."""),
    tab(
        "significance_wilcoxon",
        "Krahasimet e paradeklaruara dyshe me testin e Wilcoxon-it mbi tetë fold-e, me korrigjim "
        "Holm. Kolona e fitoreve tregon në sa fold-e fiton secili anëtar i çiftit.",
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
    p("""Pesë nga gjashtë krahasimet mbijetojnë korrigjimin. Autoencoder-i e tejkalon Isolation
      Forest-in në shtatë nga tetë fold-e; Isolation Forest-i humbet ndaj One-Class SVM-së në të
      tetë fold-et; dhe referenca e mbikëqyrur i tejkalon të tre detektorët në të tetë fold-et
      pa asnjë përjashtim. Krahasimi i vetëm që nuk arrin domethënie është Autoencoder-i
      kundrejt One-Class SVM-së, ku fitorja është gjashtë me dy: e qëndrueshme por jo e
      plotë."""),
    note("""Ky rezultat i fundit ka rëndësi për interpretimin e gjithë kapitullit. Renditja mes
      dy detektorëve të parë nuk është e vërtetuar statistikisht nën konfigurimin bazë, dhe
      nënkapitulli 5.6 do të tregojë se ajo madje përmbyset kur paraprocesimi ndryshon."""),
    h3("5.3.3", "Kompromisi mes cilësisë dhe kostos"),
    p("""Pyetja e dytë hulumtuese nuk kërkon detektorin më të saktë, por atë me balancën më të
      mirë mes performancës dhe efikasitetit operacional. Këto janë dy boshte të ndryshme dhe
      duhen parë bashkë."""),
    fig(
        "benchmark_quality_cost",
        "Cilësia e zbulimit kundrejt kostos së pikëzimit. Këndi i sipërm i majtë është pozicioni "
        "i dëshiruar: cilësi e lartë me kosto të ulët.",
        14.5,
    ),
    p("""Figura e bën përgjigjen të qartë nën konfigurimin bazë. Autoencoder-i zë këndin e sipërm
      të majtë me AP më të lartë mes metodave unsupervised dhe njëkohësisht me koston më të ulët
      të pikëzimit, 0.08 mikrosekonda për transaksion. Isolation Forest-i kushton rreth
      shtatëdhjetë herë më shumë për transaksion dhe jep gjysmën e cilësisë, ndërsa One-Class
      SVM-ja kushton rreth pesëqind herë më shumë, sepse çdo transaksion duhet krahasuar me të
      gjithë vektorët mbështetës."""),
    p("""Kostoja e trajnimit jep renditje pjesërisht të ndryshme: Autoencoder-i kërkon rreth shtatë
      sekonda për fold, ndërsa dy të tjerët nën një sekondë. Në një sistem ku modeli ritrajnohet
      një herë në ditë ky dallim është i parëndësishëm; ai do të kishte rëndësi vetëm nëse
      ritrajnimi do të ishte i vazhdueshëm."""),
    h3("5.3.4", "Vlerësimi në buxhet alarmesh"),
    p("""Average Precision përmbledh të gjithë renditjen, por asnjë ekip nuk e shqyrton atë të
      tërën. Tabela më poshtë tregon çfarë ndodh kur investigohen vetëm njëqind alarmet më të
      larta për bllok testimi, buxhet realist meqë blloqet përmbajnë mesatarisht tridhjetë e një
      mashtrime."""),
    tab(
        "budget_summary",
        "Cilësia e zbulimit dhe rikuperimi monetar në buxhet prej njëqind alarmesh për bllok "
        "testimi, mesatarizuar mbi tetë fold-e.",
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
    p("""Renditja ndryshon lehtë kur shihet nga ky kënd. One-Class SVM-ja kalon para
      Autoencoder-it në recall brenda buxhetit, sepse ajo është më e mirë në majën e renditjes
      edhe kur renditja e saj globale është më e dobët. Ky është një kujtues se metrika e
      zgjedhur duhet të përputhet me mënyrën si do të përdoret sistemi."""),
    fig(
        "budget_recall",
        "Recall brenda buxhetit të alarmeve, për buxhete nga pesëdhjetë deri në një mijë alarme "
        "për bllok.",
        14.5,
    ),
    fig(
        "budget_savings",
        "Raporti i kursimeve neto kundrejt detektorit të përsosur, sipas buxhetit të alarmeve. "
        "Vlerat negative do të thoshin se kostoja e hetimeve e tejkalon vlerën e rikuperuar.",
        14.5,
    ),
]
_PARAPROCESIMI = [
    h2("5.6", "Paraprocesimi: variabli më i nënvlerësuar"),
    p("""Të gjitha rezultatet e mësipërme u prodhuan me skalim standard, i cili është zgjedhja e
      parazgjedhur në shumicën e studimeve. Meqë të tri metodat e përcaktojnë anomalinë përmes
      një nocioni largësie, dhe meqë ai nocion varet plotësisht nga shkalla e veçorive, kjo
      zgjedhje meriton të testohet e jo të supozohet."""),
    tab(
        "scaling_summary",
        "Average Precision mesatar mbi tetë fold-e për çdo kombinim paraprocesimi dhe detektori. "
        "Skaluesi përshtatet mbi dritaren e trajnimit me mashtrimet brenda, siç do të ndodhte në "
        "vendosje reale.",
        rename={"Paraprocesimi": "Paraprocesimi"},
        font_size=9.0,
    ),
    p("""Rezultati është më i fortë nga sa pritej. Për secilin detektor unsupervised, zgjedhja më
      e mirë e paraprocesimit e tejkalon skalimin standard në të tetë fold-et, me p-vlerë 0.0078
      në testin e çiftuar. One-Class SVM-ja fiton 0.218 njësi Average Precision me transformim
      kuantil uniform dhe arrin 0.368, që është rezultati më i mirë unsupervised i gjithë
      studimit. Autoencoder-i fiton 0.103 njësi me skalim robust dhe arrin 0.296. Isolation
      Forest-i fiton 0.065 njësi."""),
    tab(
        "scaling_significance",
        "Testi i Friedman-it mbi shtatë opsionet e paraprocesimit për secilin detektor, dhe "
        "krahasimi i çiftuar mes zgjedhjes më të mirë dhe skalimit standard.",
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
    p("""Krahasimi i madhësive e bën pikën qendrore. Hapësira mes paraprocesimit më të mirë dhe
      atij më të keq për një detektor të vetëm arrin deri në 0.355 njësi Average Precision,
      ndërsa hapësira mes vetë tre detektorëve nën skalim standard është vetëm 0.102. Me fjalë
      të tjera, mënyra si përgatiten të dhënat peshon më shumë se cili nga tre algoritmet
      zgjidhet."""),
    fig(
        "scaling_effect",
        "Efekti i paraprocesimit për secilin detektor, me devijimin standard nëpër fold-e. "
        "Referenca e mbikëqyrur mbetet praktikisht e pandryshuar.",
        15.0,
    ),
    p("""Referenca e mbikëqyrur sillet krejt ndryshe dhe kjo asimetri është vetë një rezultat. Për
      të, asnjë paraprocesim nuk e tejkalon standardin në mënyrë domethënëse, me katër fitore
      nga tetë dhe p-vlerë 0.84. Shpjegimi është i drejtpërdrejtë: regresioni logjistik mëson
      një drejtim diskriminues, dhe koeficientët e tij thjesht ripeshohen kur veçoritë
      riskalohen. Metodat gjeometrike, përkundrazi, e ndryshojnë vetë problemin që zgjidhin kur
      ndryshon shkalla."""),
    p("""Një vëzhgim i dytë e forcon këtë interpretim. Isolation Forest-i prodhon Average Precision
      saktësisht identik, deri në shifrën e katërt, nën skalimin standard, atë robust, atë
      min-max dhe pa skalim fare. Kjo nuk është rastësi numerike por pasojë e drejtpërdrejtë e
      algoritmit: pikat e ndarjes zgjidhen në mënyrë uniforme brenda intervalit të vëzhguar të
      secilës kolonë, prandaj çdo transformim afin i lë pemët të pandryshuara. Vetëm
      transformimet jo-afine, si ai kuantil, e lëvizin rezultatin, dhe pikërisht ato e
      lëvizin."""),
    note("""Kjo ka pasojë praktike të drejtpërdrejtë për këdo që përdor Isolation Forest: koha e
      shpenzuar duke krahasuar skalues afinë është kohë e humbur, ndërsa transformimet që
      ndryshojnë formën e shpërndarjes janë ato që kanë rëndësi."""),
]


_THELLIMI = [
    h2("5.5", "Studime të thelluara për secilin algoritëm"),
    p("""Krahasimi i nënkapitullit 5.3 i vlerësoi tri algoritmet nën konfigurimin e tyre të
      parazgjedhur. Ky nënkapitull hyn brenda secilit prej tyre, me tri qëllime: të matet sa
      lëviz rezultati nga zgjedhjet e projektimit, të identifikohet cili levë ka rëndësi, dhe të
      testohet nëse shpjegimi i propozuar në Kapitullin 2 për sjelljen e secilit qëndron."""),
    h3("5.5.1", "Isolation Forest: ku shkon kapaciteti"),
    p("""Kapitulli 2 parashtroi hipotezën se dobësia e Isolation Forest-it në hapësira me sinjal
      të përqendruar vjen nga zgjedhja uniforme e dimensionit të ndarjes. Kjo hipotezë
      përmendet shpesh në literaturë por matet rrallë. Këtu ajo testohet me tri proba të
      pavarura, dhe përpara tyre kontrollohet nëse shpjegimi alternativ, thjesht akordimi i
      dobët, e shpjegon rezultatin vetë."""),
    tab(
        "iforest_surface",
        "Average Precision mesatar mbi tetë fold-e për çdo kombinim të numrit të pemëve dhe "
        "madhësisë së nën-mostrës.",
        font_size=9.0,
    ),
    p("""Sipërfaqja nuk është e sheshtë, prandaj shpjegimi i akordimit nuk mund të hidhet
      poshtë menjëherë. Konfigurimi i parazgjedhur me dyqind pemë dhe nën-mostër 256 jep 0.0913,
      ndërsa më i miri, tetëqind pemë me nën-mostër 16384, jep 0.1515, pra gjashtëdhjetë e
      gjashtë për qind më shumë. Boshti që e lëviz rezultatin është madhësia e nën-mostrës, me
      hapësirë 0.0698 njësi, ndërsa numri i pemëve lëviz vetëm 0.0087. Rekomandimi klasik i një
      nën-mostre prej 256 rezulton i papërshtatshëm për këtë dataset, gjë që në vetvete është
      një gjetje praktike."""),
    fig(
        "iforest_surface",
        "Sipërfaqja e hiperparametrave e Isolation Forest-it. Madhësia e nën-mostrës e lëviz "
        "rezultatin tetë herë më shumë se numri i pemëve.",
        14.5,
    ),
    p("""Megjithatë akordimi nuk mjafton për ta shpjeguar renditjen, sepse edhe konfigurimi më i
      mirë mbetet nën Autoencoder-in dhe nën One-Class SVM-në në konfigurimin e tyre bazë.
      Prandaj testohet mekanizmi vetë."""),
    p("""Proba e parë hap pemët e përshtatura dhe numëron sa ndarje merr secila kolonë. Nëse
      hipoteza qëndron, shpërndarja duhet të jetë praktikisht uniforme, pa lidhje me
      informativitetin. Rezultati e konfirmon: pesë veçoritë më informative marrin 17.4 për qind
      të ndarjeve, ndërsa pjesa e pritur nga rastësia e plotë është 17.2 për qind, dhe
      korrelacioni Spearman mes përdorimit të një kolone dhe fuqisë së saj diskriminuese është
      0.10 me p-vlerë 0.59. Me fjalë të tjera, algoritmi nuk e di se cilat kolona janë të
      dobishme dhe nuk sillet sikur ta dinte."""),
    fig(
        "iforest_capacity",
        "Majtas, shpërndarja e ndarjeve mbi kolonat kundrejt asaj që pritet nga rastësia. "
        "Djathtas, përdorimi i një kolone kundrejt fuqisë së saj diskriminuese.",
        15.0,
    ),
    p("""Proba e dytë përjashton shpjegimin konkurrues. Meqë veçoritë V1 deri V28 janë
      komponentë kryesorë, ndarjet paralele me boshtet mund të jenë ose të favorizuara ose të
      dëmtuara nga kjo përputhje. I njëjti pyll u ripërshtat mbi një kopje të rrotulluar
      rastësisht të hapësirës, ku përputhja shkatërrohet por struktura ruhet. Ndryshimi është
      0.0073 njësi Average Precision, nga 0.0913 në 0.0986, pra praktikisht i papërfillshëm.
      Orientimi i boshteve nuk është pra shpjegimi."""),
    tab(
        "iforest_rotation",
        "Average Precision për fold në hapësirën origjinale dhe në atë të rrotulluar rastësisht.",
        font_size=9.0,
    ),
    p("""Proba e tretë është ajo më vendimtare, sepse ajo nuk vëzhgon por ndërhyn. Nëse
      kapaciteti shpërndahet mbi kolona pa sinjal, atëherë zvogëlimi i numrit të kolonave që
      sheh secila pemë duhet ta përmirësojë detektorin. Kjo është pikërisht ajo që ndodh: me
      max_features 0.20, pra me rreth gjashtë kolona për pemë nga njëzet e nëntë, Average
      Precision ngjitet nga 0.0913 në 0.1127, dhe fitorja është në të tetë fold-et me p-vlerë
      0.0078."""),
    tab(
        "iforest_max_features",
        "Efekti i kufizimit të secilës pemë në një nën-hapësirë veçorish, për fold dhe për "
        "vlerë të max_features.",
        font_size=8.5,
    ),
    p("""Të tria probat tregojnë në të njëjtin drejtim dhe secila mbulon një dobësi të tjetrës.
      Numërimi i ndarjeve tregon se mekanizmi është i pranishëm, rrotullimi përjashton
      shpjegimin alternativ, dhe kufizimi i nën-hapësirës tregon se ndërhyrja në mekanizëm e
      ndryshon rezultatin në drejtimin e parashikuar. Kjo e shndërron shpjegimin nga
      korrelacion i vëzhguar në pohim të testuar."""),
    note("""Vlen të theksohet se edhe pas të tria përmirësimeve Isolation Forest-i mbetet i
      fundit mes tri algoritmeve. Qëllimi i këtij nënkapitulli nuk ishte ta ngrinte atë në vend
      të parë, por të shpjegonte pse ndodhet i fundit, dhe shpjegimi tani është i matur."""),
    h3("5.5.2", "Autoencoder: ngushtica, humbja dhe mbitrajnimi"),
    p("""Për Autoencoder-in u studiuan gjashtë leva veç e veç: gjerësia e shtresës së fshehur
      bashkë me dimensionin latent, thellësia e enkoderit, funksioni i humbjes, dropout-i,
      weight decay-i dhe korruptimi i hyrjes për variantin denoising, plus numri i epokave.
      Secila u ndryshua veçmas mbi të njëjtat tetë fold-e, që efekti i saj të mos përzihet me
      atë të të tjerave."""),
    tab(
        "autoencoder_studies",
        "Përmbledhje e të gjitha studimeve mbi Autoencoder-in. Çdo rresht është një konfigurim, "
        "i vlerësuar mbi tetë fold-e.",
        font_size=8.0,
    ),
    p("""Gjetja më e madhe është se arkitektura ka rëndësi vendimtare. Kalimi nga konfigurimi i
      parazgjedhur, me shtresë të fshehur 16 dhe dimension latent 8, te një shtresë e fshehur 32
      me dimension latent 12 e ngre Average Precision nga 0.1929 në 0.3543, pra tetëdhjetë e
      katër për qind më shumë. Hapësira mes konfigurimit më të mirë dhe atij më të keq të
      arkitekturës është 0.2227 njësi, dukshëm më e madhe se hapësira 0.1016 mes tri
      algoritmeve nën konfigurimin bazë."""),
    fig(
        "autoencoder_architecture",
        "Average Precision për çdo kombinim të gjerësisë së shtresës së fshehur dhe të "
        "dimensionit latent.",
        14.5,
    ),
    p("""Kjo gjetje ka një pasojë të drejtpërdrejtë për interpretimin e nënkapitullit 5.3:
      renditja e raportuar atje është renditje e konfigurimeve të parazgjedhura dhe jo e
      algoritmeve në kapacitetin e tyre të plotë. Nënkapitulli 5.9 e mat sa e ndryshon kjo
      renditjen kur të tre akordohen njësoj."""),
    p("""Gjetja e dytë e kundërshton një heuristikë të përhapur. Pritet zakonisht që dimensioni
      latent duhet të përafrojë dimensionin e brendshëm të të dhënave, i cili u vlerësua në 3.8
      me metodën TwoNN dhe 7.3 me atë të gjasës maksimale. Dimensioni latent optimal rezulton
      12, pra rreth tri herë vlerësimi i parë dhe qartësisht mbi të dytin. Shpjegimi qëndron te
      objektivi: ngushtica nuk duhet ta përshkruajë klasën normale në mënyrë minimale, por të
      jetë mjaft e gjerë sa ajo të rindërtohet mirë dhe mjaft e ngushtë sa anomalitë të mos
      rindërtohen. Kur ngushtica shtrëngohet nën këtë vlerë, të dyja klasat rindërtohen keq dhe
      dallimi mes tyre zhduket."""),
    p("""Gjetja e tretë tregon se jolineariteti paguan. Rindërtimi linear me analizë të
      komponentëve kryesorë, i vlerësuar në të njëjtat rangje dhe nën të njëjtin protokoll,
      shërben si dysheme ablacioni për familjen e rindërtimit. Autoencoder-i e tejkalon atë në
      të shtatë rangjet e krahasueshme, dhe në rangun e tij më të mirë diferenca është 0.2087
      njësi Average Precision. Vlen të vërehet gjithashtu se dyshemeja lineare rritet në mënyrë
      monotone me rangun, ndërsa Autoencoder-i ka një optimum të brendshëm, çka është vetë një
      dallim mekanicist mes të dyve."""),
    fig(
        "autoencoder_vs_linear",
        "Autoencoder-i jolinear kundrejt rindërtimit linear me analizë të komponentëve kryesorë, "
        "në të njëjtat rangje.",
        14.5,
    ),
    p("""Gjetja e katërt ka të bëjë me funksionin e humbjes dhe është metodologjikisht e
      rëndësishme. Në të gjitha variantet pika e anomalisë llogaritet gjithmonë si gabim
      kuadratik mesatar, sepse ndryshe ablacioni nuk do të ishte i interpretueshëm. Trajnimi me
      gabim kuadratik jep 0.1929, ndërsa trajnimi me gabim absolut jep 0.1113 dhe me humbje
      Huber 0.1157. Përputhja mes objektivit të trajnimit dhe atij të pikëzimit ka pra rëndësi
      të matshme, dhe humbjet robuste, të cilat zakonisht rekomandohen kur ka vlera
      ekstreme, e dëmtojnë detektorin pikërisht sepse i zbusin gabimet e mëdha që përbëjnë
      sinjalin."""),
    p("""Gjetja e pestë është mbitrajnimi. Cilësia kulmon në njëzet epoka me 0.1929 dhe bie në
      0.1505 me gjashtëdhjetë, ndërsa humbja e trajnimit vazhdon të bjerë. Ky është konfirmim i
      drejtpërdrejtë i mekanizmit të përshkruar në Kapitullin 2: rrjeti i mbitrajnuar fillon t'i
      rindërtojë mirë edhe anomalitë dhe pika e humbet fuqinë dalluese. Pasoja praktike është
      se kriteri i ndalimit nuk mund të jetë humbja e trajnimit, sepse ajo vazhdon të
      përmirësohet ndërsa detektori përkeqësohet."""),
    fig(
        "autoencoder_training",
        "Humbja e trajnimit kundrejt cilësisë së zbulimit sipas numrit të epokave. Të dyja "
        "kurbat lëvizin në drejtime të kundërta pas njëzet epokave.",
        14.5,
    ),
    p("""Levat e regullarizimit japin efekte të vogla. Dropout-i 0.1 e ngre rezultatin me 0.0066
      njësi, weight decay-i 1e-4 me 0.0161, ndërsa vlera e madhe 1e-2 e ul me 0.0855. Varianti
      denoising, ku hyrja korruptohet me zhurmë gausiane, nuk jep asnjë efekt praktik: hapësira
      mes nivelit më të mirë dhe atij më të keq të zhurmës është nën 0.005 njësi. Ky është një
      rezultat negativ i vogël por i dobishëm, sepse denoising rekomandohet shpesh pa
      kualifikim."""),
    h3("5.5.3", "One-Class SVM: kerneli, ν dhe çmimi i të dhënave"),
    p("""Për One-Class SVM u studiuan tri boshte: zgjedhja e kernelit, sipërfaqja mbi nu dhe
      gamma, dhe kurba e të mësuarit mbi madhësinë e nën-mostrës së trajnimit. Boshti i fundit
      është i veçantë për këtë algoritëm, sepse kostoja e tij rritet afërsisht kuadratikisht me
      numrin e mostrave dhe nën-mostrimi nuk është zgjedhje por domosdoshmëri."""),
    tab(
        "ocsvm_kernels",
        "Krahasimi i kernelëve mbi tetë fold-e, me koston e trajnimit, koston e pikëzimit dhe "
        "numrin mesatar të vektorëve mbështetës.",
        rename={
            "kernel": "Kerneli",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "fit_s": "Fit (s)",
            "us_per_tx": "µs/tx",
            "support_vectors": "Vektorë mbështetës",
        },
        font_size=9.5,
    ),
    p("""Kerneli RBF është qartësisht më i miri me 0.1505, i ndjekur nga ai sigmoid me 0.0526 dhe
      polinomial me 0.0317. Kerneli linear dështon plotësisht me 0.0009, pra praktikisht në
      nivelin e rastësisë, dhe kjo është informative: një kufi linear rreth klasës legjitime nuk
      e ndan atë nga mashtrimet, çka do të thotë se struktura e nevojshme është jolineare. Ky
      rezultat përputhet me atë të Autoencoder-it kundrejt rindërtimit linear."""),
    tab(
        "ocsvm_surface",
        "Average Precision mesatar mbi tetë fold-e për çdo kombinim të nu dhe gamma me kernel RBF.",
        font_size=9.5,
    ),
    p("""Sipërfaqja nu-gamma ka maksimumin te nu 0.001 me gamma të llogaritur automatikisht, ku
      arrihet 0.1634. Drejtimi është i qëndrueshëm: vlerat e vogla të nu janë më të mira, dhe
      kjo pajtohet me kuptimin teorik të parametrit, i cili kufizon nga poshtë pjesën e pikëve
      të trajnimit që lejohen jashtë kufirit. Meqë norma reale e mashtrimit është 0.17 për qind,
      një nu prej 0.05, që është vlera e parazgjedhur e bibliotekës, e detyron modelin të
      shpallë jashtë kufirit tridhjetë herë më shumë pika sesa duhet."""),
    fig("ocsvm_surface", "Sipërfaqja nu-gamma për One-Class SVM me kernel RBF.", 14.0),
    p("""Kurba e të mësuarit jep rezultatin operacionalisht më të rëndësishëm të këtij
      nënkapitulli. Rritja e nën-mostrës nga një mijë në tetëdhjetë mijë transaksione e ngre
      Average Precision vetëm nga 0.1508 në 0.1581, pra me 0.0073 njësi, ndërsa koha e trajnimit
      rritet nga 0.006 sekonda në 50.6 sekonda dhe kostoja e pikëzimit nga 5.2 në 188.2
      mikrosekonda për transaksion. Numri i vektorëve mbështetës rritet përkatësisht nga 102 në
      4055, dhe meqë kostoja e pikëzimit është proporcionale me atë numër, kjo është shpjegimi i
      plotë i rritjes së kostos."""),
    tab(
        "ocsvm_learning_curve",
        "Kurba e të mësuarit e One-Class SVM-së: cilësia, kostoja dhe numri i vektorëve "
        "mbështetës sipas madhësisë së nën-mostrës së trajnimit.",
        rename={
            "train_subsample": "Nën-mostra",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "fit_s": "Fit (s)",
            "us_per_tx": "µs/tx",
            "support_vectors": "Vektorë mbështetës",
        },
        font_size=9.5,
    ),
    fig(
        "ocsvm_learning_curve",
        "Cilësia dhe kostoja e One-Class SVM-së sipas madhësisë së nën-mostrës së trajnimit. "
        "Cilësia ngopet shumë përpara se kostoja të ndalojë së rrituri.",
        14.5,
    ),
    p("""Pasoja praktike është e drejtpërdrejtë dhe në kundërshtim me intuitën se më shumë të
      dhëna janë gjithmonë më mirë. Në këtë problem një mijë transaksione trajnimi japin
      praktikisht të njëjtën cilësi si njëzet mijë, me kosto pikëzimi nëntë herë më të vogël dhe
      kohë trajnimi njëqind e gjashtëdhjetë herë më të vogël. Kufizimi kuadratik i kernelit, i
      cili në literaturë përshkruhet si pengesa kryesore e metodës, nuk është pengesë reale këtu
      pikërisht sepse cilësia ngopet shumë më herët se kostoja."""),
    note("""Kjo gjetje e ndryshon leximin e tabelës kryesore. Kostoja e pikëzimit prej 45.4
      mikrosekondash për transaksion, e cila e rendit One-Class SVM-në si më të shtrenjtin, është
      pasojë e një zgjedhjeje konfigurimi dhe jo e vetë algoritmit; me nën-mostër prej një mijë
      pikash ajo bie nën gjashtë mikrosekonda pa humbje të matshme cilësie."""),
]

_KAUZALITETI = [
    h2("5.7", "Nga korrelacioni te shkaku: ndërhyrja mbi hyrjen"),
    p("""Nënkapitujt e mëparshëm e treguan se Isolation Forest-i e shpërndan kapacitetin e vet
      mbi kolona pa sinjal dhe se ai renditet i fundit. Këto janë dy vëzhgime, dhe bashkimi i
      tyre në një shpjegim mbetet hipotezë derisa të ndërhyhet mbi mekanizmin e supozuar. Ky
      nënkapitull e bën atë ndërhyrje."""),
    p("""Dizajni është i thjeshtë. Në secilin fold, komponentët renditen sipas fuqisë së tyre
      diskriminuese të matur vetëm mbi dritaren e trajnimit, dhe secili detektor ripërshtatet
      duke parë vetëm k komponentët e parë. Nëse shpërndarja e ndarjeve mbi kolona pa sinjal
      është vërtet mekanizmi i dobësisë, atëherë Isolation Forest-i duhet të fitojë më shumë se
      të tjerët, dhe duhet të fitojë më shumë te k-të e vogla, ku kolonat pa sinjal janë hequr
      plotësisht."""),
    tab(
        "feature_selection",
        "Average Precision mesatar mbi tetë fold-e kur secili detektor sheh vetëm k komponentët "
        "më informativë, sipas dy renditjeve të ndryshme.",
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
    p("""Parashikimi verifikohet plotësisht. Isolation Forest-i fiton 0.5301 njësi Average
      Precision, nga 0.0913 në 0.6214, dhe e fiton këtë pikërisht te k barabartë me tre, ku
      mbeten vetëm tri kolona. One-Class SVM-ja fiton 0.3603 njësi, gjithashtu te k barabartë me
      tre, ndërsa Autoencoder-i fiton 0.3967 njësi por te k barabartë me dymbëdhjetë, çka
      përputhet me faktin se ai ka nevojë për më shumë dimensione hyrëse për të ndërtuar një
      rindërtim kuptimplotë."""),
    fig(
        "feature_selection",
        "Efekti i kufizimit të hyrjes te k komponentët më informativë, për secilin detektor dhe "
        "për të dyja renditjet.",
        15.0,
    ),
    p("""Referenca e mbikëqyrur sillet krejt ndryshe dhe kjo është kontrolli që e bën argumentin
      të vlefshëm. Ajo nuk fiton asgjë; përkundrazi, çdo kufizim e dëmton, nga 0.7341 me të
      gjitha kolonat në 0.6103 me tri. Modeli i mbikëqyrur tashmë i peshon vetë kolonat sipas
      dobisë së tyre, prandaj heqja e kolonave vetëm sa i heq informacion. Metodat gjeometrike,
      të cilat nuk kanë asnjë mekanizëm të tillë peshimi, përfitojnë nga një peshim që u jepet
      nga jashtë."""),
    p("""Rendi i fitimeve, me Isolation Forest-in më lart se të dy të tjerët, është pikërisht ai
      që parashikon shpjegimi i propozuar dhe nuk është ai që do të pritej nëse dobësia do të
      vinte nga një shkak tjetër. Kjo e ngre shpjegimin nga korrelacion i vëzhguar në pohim të
      mbështetur eksperimentalisht."""),
    p("""Një kualifikim i rëndësishëm e shoqëron këtë rezultat dhe raportohet shprehimisht.
      Renditja sipas fuqisë diskriminuese përdor etiketat historike, prandaj ajo përfaqëson
      rastin më të mirë të mundshëm dhe jo një procedurë të vendosshme pa etiketa. Për këtë
      arsye u testua edhe një renditje krejtësisht pa etiketa, ajo sipas kurtozës së tepërt, e
      cila është heuristika klasike e ndjekjes së projeksioneve. Mbivendosja mes dy renditjeve
      është zero te tre kolonat e para dhe vetëm tridhjetë e tre për qind te dymbëdhjetë të
      parat."""),
    tab(
        "feature_selection_agreement",
        "Mbivendosja mes renditjes me etiketa dhe asaj sipas kurtozës, sipas numrit të kolonave "
        "të mbajtura.",
        rename={"k": "k", "mbivendosja": "Mbivendosja"},
        font_size=9.5,
    ),
    p("""Rezultatet me renditjen pa etiketa janë dukshëm më modeste. Autoencoder-i fiton 0.1224
      njësi te gjashtëmbëdhjetë kolona, One-Class SVM-ja praktikisht asgjë, dhe Isolation
      Forest-i humbet në çdo k. Përfundimi i dyfishtë është pra ky: mekanizmi është konfirmuar,
      por përfitimi i tij nuk është i arritshëm pa etiketa me heuristikën e testuar. Kjo e
      forcon më tej gjetjen e nënkapitullit 5.3 mbi vlerën e etiketave historike, sepse ato
      dalin të dobishme jo vetëm për të trajnuar një klasifikues, por edhe për të përgatitur
      hapësirën në të cilën punojnë metodat unsupervised."""),
    h2("5.8", "Sa histori duhet mbajtur"),
    p("""Kush vendos një sistem të tillë duhet të zgjedhë mes dy politikave: të mbajë të gjithë
      historikun dhe ta lërë dritaren e trajnimit të zgjerohet, ose të mbajë një dritare
      rrëshqitëse me gjatësi fikse. Zgjedhja nuk është e vetëkuptueshme, sepse e para përdor më
      shumë të dhëna ndërsa e dyta qëndron më afër së tashmes."""),
    tab(
        "training_window_curve",
        "Average Precision sipas gjatësisë së dritares rrëshqitëse, mbi tetë fold-e. Kolona e "
        "fundit tregon në sa fold-e ishte e disponueshme ajo gjatësi.",
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
        "Kurba e të mësuarit mbi gjatësinë e dritares rrëshqitëse. Vijat me pika tregojnë "
        "rezultatin me dritaren që zgjerohet mbi gjithë historikun.",
        15.0,
    ),
    p("""Rezultati ndan detektorët në dy grupe. Për Autoencoder-in dhe për Isolation Forest-in
      asnjë dritare rrëshqitëse nuk e tejkalon historikun e plotë, me diferencë përkatësisht
      0.019 dhe 0.005 njësi në favor të historikut. Për One-Class SVM-në, përkundrazi, një
      dritare prej pesëdhjetë mijë transaksionesh e tejkalon historikun e plotë me 0.049 njësi.
      Referenca e mbikëqyrur përmirësohet në mënyrë monotone me sasinë e të dhënave, siç pritet
      nga një model i mbikëqyrur."""),
    p("""Mesatarisht mbi tri metodat unsupervised, kalimi nga dhjetë mijë në njëqind mijë
      transaksione trajnimi e lëviz Average Precision vetëm nga 0.141 në 0.136, pra praktikisht
      aspak. Gjatësia prej dyqind mijë përjashtohet nga kjo mesatare sepse ajo ekziston vetëm në
      tri fold-et e fundit, dhe përfshirja e saj do të përzinte gjatësinë e dritares me
      vështirësinë e fold-it."""),
    p("""Pasoja praktike përputhet me atë të kurbës së të mësuarit të One-Class SVM-së: sasia e
      të dhënave nuk është kufizuesi për metodat unsupervised mbi këtë dataset. Kjo është vetë
      një gjetje, sepse mbledhja e më shumë historikut është zakonisht rekomandimi i parë kur
      cilësia është e ulët. Këtu ajo nuk do të ndihmonte."""),
]

BLOCKS = _HYRJE + _GJEOMETRIA + _PH2 + _THELLIMI + _PARAPROCESIMI + _KAUZALITETI

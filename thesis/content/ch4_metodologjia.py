"""Kapitulli 4 — METODOLOGJIA."""

from blocks import bullets, eq, fig, h1, h2, h3, note, numbers, p, tab

_DATA = [
    h1("4", "Metodologjia"),
    p("""Ky kapitull përshkruan dataset-in, protokollin e vlerësimit, paraprocesimin, modelet,
      procedurën e pragut, metrikat, studimet e thelluara për secilin algoritëm dhe arkitekturën e
      implementuar. Përshkrimi është i hollësishëm, sepse shumë nga dallimet mes rezultateve të
      publikuara për këtë dataset nuk vijnë nga algoritmet, por nga zgjedhje metodologjike që shpesh
      nuk raportohen."""),
    h2("4.1", "Dataset-i"),
    h3("4.1.1", "Origjina dhe struktura"),
    p("""Studimi përdor dataset-in publik Credit Card Fraud Detection të grupit Machine Learning të
      Université Libre de Bruxelles [@ulb_dataset]. Ai përmban transaksione reale me karta krediti
      të mbajtësve evropianë gjatë dy ditëve të shtatorit 2013. Struktura është e thjeshtë: kolona
      Time me sekondat nga transaksioni i parë, 28 kolona V1 deri V28 që janë komponentë kryesorë të
      një transformimi PCA të bërë nga publikuesit për ruajtjen e konfidencialitetit, kolona Amount
      me shumën e transaksionit dhe kolona Class me etiketën binare."""),
    tab(
        "eda_overview",
        "Karakteristikat kryesore të dataset-it.",
        rename={"treguesi": "Treguesi", "vlera": "Vlera"},
        font_size=10,
    ),
    p("""Anonimizimi me PCA ka dy pasoja që shfaqen gjatë gjithë punimit. E para, veçoritë nuk mund
      të interpretohen semantikisht, sepse komponentët nuk kanë emra dhe nuk mund të thuhet cila
      sjellje e transaksionit e rrit pikën e anomalisë. E dyta, një detektor linear rindërtimi i
      bazuar në PCA nuk është thjesht një model bazë i dobët, por niveli minimal i familjes së
      rindërtimit. Në këtë punim ai shërben si ablacion i Autoencoder-it."""),
    h3("4.1.2", "Analiza eksploruese"),
    p("""Analiza eksploruese nxori disa fakte që ndikojnë në interpretimin e rezultateve. Vëllimi i
      transaksioneve ndjek një cikël të qartë ditë-natë, ndërsa mashtrimet nuk e ndjekin atë (Figura
      [[fig:eda_volume_and_fraud]]). Për pasojë norma e mashtrimit ndryshon shumë nga ora në orë,
      dhe blloqet e testimit me numër të njëjtë rreshtash mbulojnë intervale kohore shumë të
      ndryshme."""),
    fig(
        "eda_volume_and_fraud",
        "Transaksionet dhe mashtrimet për çdo orë të regjistrimit.",
        15.0,
    ),
    p("""Norma e mashtrimit sipas orës së ditës e tregon këtë edhe më qartë: në orën dy të natës ajo
      arrin rreth 1.7%, afërsisht dhjetë herë mbi mesataren (Figura [[fig:eda_hourly_rate]]). Ky
      është sinjal i fortë, por në këtë punim nuk përdoret si veçori, sepse koha shërben për
      renditjen e rrjedhës dhe për ndarjen e të dhënave; përdorimi i saj si hyrje do të ngatërronte
      variablin e ndarjes me hyrjen e modelit. Kjo zgjedhje diskutohet edhe te kufizimet."""),
    fig(
        "eda_hourly_rate", "Norma e mashtrimit sipas orës së ditës, për të dyja ditët bashkë.", 15.0
    ),
    p("""Shpërndarja e shumave të transaksioneve nuk është ajo që mund të pritej. Shuma mesatare e
      mashtrimeve (122.21 EUR) është më e lartë se ajo e transaksioneve legjitime (88.29 EUR), por
      mediana e tyre është shumë më e ulët: 9.25 EUR kundrejt 22.00 EUR (Figura
      [[fig:eda_amounts]]). Shumica e mashtrimeve janë pra transaksione të vogla, ndërsa një pjesë e
      vogël janë shumë të mëdha. Rreth 37% e mashtrimeve kanë shumë deri në një euro, dhe 27 prej
      tyre kanë shumë saktësisht zero, gjë që përputhet me praktikën e njohur të testimit të
      kartave: sulmuesi kontrollon nëse karta është aktive me një autorizim pa vlerë para se ta
      përdorë."""),
    fig(
        "eda_amounts",
        "Shpërndarja kumulative e shumës së transaksionit sipas klasës.",
        15.0,
    ),
    p("""Matrica e korrelacionit konfirmon prejardhjen e të dhënave (Figura
      [[fig:eda_correlation]]). Korrelacioni mesatar absolut mes veçorive të ndryshme është 0.008,
      praktikisht zero, siç pritet nga komponentë kryesorë ortogonalë. Korrelacionet e
      konsiderueshme përfshijnë vetëm kolonën Amount, e cila nuk ishte pjesë e transformimit PCA; më
      i forti është mes Amount dhe V2, me vlerë absolute 0.531. Ky është një kontroll i thjeshtë,
      por i dobishëm, i integritetit të të dhënave."""),
    fig(
        "eda_correlation",
        "Korrelacioni i Pearson-it mes 29 veçorive hyrëse.",
        12.0,
    ),
    h3("4.1.3", "Karakterizimi gjeometrik para modelimit"),
    p("""Të gjitha metodat unsupervised të këtij studimi supozojnë se klasa pozitive ndodhet
      gjeometrikisht larg asaj negative. Supozimi mund të testohet pa trajnuar asnjë model, dhe
      testi jep një kufi të sipërm që nuk varet nga algoritmi. Para modelimit maten tri madhësi:
      dimensioni i brendshëm i klasës normale me dy vlerësues të pavarur, distanca e çdo
      transaksioni nga fqinjët e tij legjitimë më të afërt dhe cilësia e zbulimit që arrin një
      detektor i ndërtuar vetëm mbi këtë distancë."""),
    p("""Dimensioni i brendshëm vlerësohet me metodën e gjasës maksimale të Levina-Bickel dhe me
      vlerësuesin TwoNN, i cili përdor vetëm dy fqinjët më të afërt dhe ndikohet shumë më pak nga
      lakimi i të dhënave dhe nga ndryshimet e densitetit. Të dy vlerësuesit llogariten mbi dritaren
      e trajnimit, dhe të njëjtat masa përsëriten mbi dritaren e testimit si një pamje e zhvendosjes
      pa model."""),
    p("""Masa kryesore është një detektor pa parametra, ku pika e anomalisë është distanca mesatare
      deri te dhjetë fqinjët legjitimë më të afërt. Meqë ky detektor nuk mëson asgjë, cilësia e tij
      tregon sa mund të arrihet vetëm me gjeometri, dhe çdo detektor i trajnuar duhet krahasuar me
      të. Për ta bërë numrin të kuptueshëm operacionalisht, raportohet edhe pozicioni i çdo
      mashtrimi në renditjen e plotë, pra sa alarme duhen shqyrtuar para se të arrihet ai."""),
    h3("4.1.4", "Kufizimet e dataset-it"),
    p("""Para interpretimit të rezultateve duhen pasur parasysh tri kufizime të të dhënave."""),
    bullets(
        [
            "Mungon identifikuesi i kartës. Pa të nuk mund të agregohen transaksionet e një "
            "llogarie mbi dritare kohore, teknikë që literatura e aplikuar e raporton si ndër më "
            "efektivet [@whitrow2009], [@bahnsen2016], dhe as të modelohet sekuenca e "
            "transaksioneve të një mbajtësi [@jurgovsky2018]. Rezultatet vlejnë për zbulim "
            "pikësor, pa kontekst llogarie.",
            "Të dhënat mbulojnë vetëm 48 orë. Mund të vlerësohet zhvendosja brenda ditës dhe mes "
            "dy ditëve, por jo ajo sezonale ose afatgjatë.",
            "Etiketat merren si të plota dhe të sakta. Në realitet një pjesë e mashtrimeve nuk "
            "kontestohet kurrë dhe mbetet e etiketuar si legjitime, prandaj vlerat e precision-it "
            "janë më tepër pesimiste.",
        ]
    ),
]

_PROTOKOLLI = [
    h2("4.2", "Protokolli i vlerësimit"),
    h3("4.2.1", "Ndarja kronologjike dhe masat kundër rrjedhjes"),
    p("""Të dhënat renditen sipas kolonës Time me një renditje të qëndrueshme (stable sort):
      rreshtat me të njëjtën vlerë kohe ruajnë rendin e skedarit, kështu që ndarja është plotësisht
      deterministe. Të dhënat ndahen sipas kohës dhe nuk përzihen kurrë. Modelet unsupervised
      trajnohen vetëm mbi transaksionet normale të dritares së trajnimit, ndërsa skaluesi përshtatet
      mbi të gjithë dritaren e trajnimit dhe pastaj zbatohet mbi bllokun e testimit."""),
    p("""Kolona Time nuk përdoret si veçori. Vektori i veçorive përbëhet nga V1 deri V28 dhe Amount,
      gjithsej 29 dimensione. Kjo është e domosdoshme: meqë Time përcakton ndarjen, në një ndarje
      kronologjike vlerat e saj në bllokun e testimit janë gjithmonë jashtë intervalit të parë gjatë
      trajnimit, dhe pas skalimit çdo transaksion i testit do të kishte një vlerë ekstreme në këtë
      dimension. Kjo do ta prishte renditjen e çdo detektori të bazuar në distancë ose densitet, pa
      e prekur fare një model linear të mbikëqyrur."""),
    note("""Rreziku nuk është vetëm teorik. Mungesa e kolonës Time mes veçorive kontrollohet me test
      automatik, sepse ky mekanizëm do të prodhonte një rënie të cilësisë me kohën që duket njësoj
      si ajo që vërehet në të dhëna, por për një arsye krejt tjetër."""),
    h3("4.2.2", "Protokolli rolling-origin"),
    p("""Një ndarje e vetme 70/30 jep një vlerësim për një moment të vetëm vendosjeje. Me 492
      pozitivë në gjithë dataset-in ky vlerësim është i zhurmshëm, dhe nga një prerje e vetme nuk
      mund të thuhet nëse renditja e algoritmeve është e qëndrueshme apo e rastësishme. Këtu
      vlerësimi përsëritet në tetë pika prerjeje të njëpasnjëshme me dritare trajnimi që zgjerohet,
      sipas skemës rolling-origin të përdorur në literaturën e parashikimit [@bergmeir2012] dhe të
      vlerësimit prekuencial [@gama2013]. Ky protokoll quhet më poshtë rolling-origin 8-fold."""),
    eq("Fold i:  trajnim [0, c_i),   testim [c_i, c_{i+1})"),
    p("""Pikat e prerjes c_i e ndajnë pjesën e rrjedhës pas 40% të parë në tetë blloqe me numër të
      njëjtë rreshtash, pra rreth 21 360 transaksione secili (Figura [[fig:diagram_protocol]]). Në
      çdo fold rindërtohen nga fillimi skaluesi, modelet dhe pragjet. Asgjë nuk kalon nga një fold
      te tjetri, kështu që informacioni nga një bllok i mëvonshëm nuk mund të ndikojë në një bllok
      më të hershëm."""),
    fig(
        "diagram_protocol",
        "Protokolli rolling-origin 8-fold. Numrat tregojnë mashtrimet në çdo bllok testimi.",
        15.0,
    ),
    p("""Numri i fold-eve është kompromis mes dy kërkesave të kundërta. Me N fold-e, testi i
      Wilcoxon-it për çifte nuk mund të japë p-vlerë dypalëshe më të vogël se 2/2^N; me gjashtë
      fold-e kjo është 0.031, e cila nuk e kalon korrigjimin e Holm-it për disa krahasime, sado i
      qëndrueshëm të jetë rezultati. Nga ana tjetër, me shumë fold-e blloqet e testimit zvogëlohen
      derisa disa prej tyre të kenë më pak se dhjetë pozitivë dhe AP-ja e tyre të bëhet zhurmë. Me
      tetë fold-e çdo bllok ka të paktën 13 pozitivë, dhe p-vlera më e vogël e mundshme është
      0.0078, e cila e kalon korrigjimin për deri në gjashtë krahasime të deklaruara
      paraprakisht."""),
    tab(
        "fold_summary",
        "Struktura e tetë fold-eve.",
        columns=[
            "fold",
            "train_rows",
            "train_frauds",
            "test_rows",
            "test_frauds",
            "test_fraud_rate",
            "test_time_start_h",
            "test_time_end_h",
        ],
        rename={
            "fold": "Fold",
            "train_rows": "Rreshta trajnimi",
            "train_frauds": "Mashtrime trajnimi",
            "test_rows": "Rreshta testimi",
            "test_frauds": "Mashtrime testimi",
            "test_fraud_rate": "Norma e testit",
            "test_time_start_h": "Nga (orë)",
            "test_time_end_h": "Deri (orë)",
        },
        round={"test_fraud_rate": 5, "test_time_start_h": 1, "test_time_end_h": 1},
        font_size=9.0,
    ),
    p("""Tabela tregon se blloqet me numër të njëjtë rreshtash mbulojnë intervale kohore shumë të
      ndryshme, sepse dendësia e transaksioneve ndryshon me orën. Fold-i 1 dallohet me 88 mashtrime,
      gati katër herë më shumë se mesatarja e blloqeve të tjera, sepse përfshin një grumbull
      mashtrimesh që shpjegon pjesën më të madhe të variancës së rezultateve."""),
    h2("4.3", "Paraprocesimi si variabël eksperimentale"),
    p("""Çdo detektor i bazuar në distancë, densitet ose rindërtim e merr nocionin e largësisë nga
      paraprocesimi që zbatohet para tij. Në shumicën e studimeve skaluesi zgjidhet një herë dhe nuk
      rishikohet, ndonëse mund të ndikojë më shumë se vetë zgjedhja e algoritmit. Në këtë punim
      paraprocesimi trajtohet si variabël eksperimentale."""),
    p("""Skaluesi përshtatet mbi të gjithë dritaren e trajnimit, mashtrimet përfshirë, dhe jo vetëm
      mbi transaksionet normale. Në momentin e vendosjes etiketat e dritares aktuale nuk dihen, dhe
      një skalues i përshtatur mbi të dhëna të pastra do t'i jepte modelit një avantazh që sistemi
      real nuk e ka. Pasoja është se statistikat e skaluesit ndikohen nga vetë vlerat ekstreme që
      duhen nxjerrë në pah, dhe kjo pasojë matet."""),
    p("""Krahasohen shtatë opsione: StandardScaler, RobustScaler me interval ndërkuartilor,
      transformimi kuantil me dalje normale dhe me dalje uniforme, PowerTransformer me metodën
      Yeo-Johnson, MinMaxScaler dhe mungesa e skalimit. Opsioni i fundit është model bazë i
      ligjshëm, sepse komponentët V janë tashmë të qendërzuar. Çdo kombinim paraprocesimi dhe
      detektori vlerësohet në të tetë fold-et, me të njëjtën pasiguri si rezultatet kryesore."""),
    p("""Kur zgjidhet opsioni më i mirë nga shtatë dhe pastaj matet përfitimi i tij në të njëjtat
      fold-e, përfitimi mbivlerësohet. Për ta shmangur këtë bëhet edhe një kontroll prekuencial: për
      fold-in i zgjidhet skaluesi më i mirë vetëm nga fold-et 0 deri i−1, dhe rezultati i tij
      krahasohet me StandardScaler në fold-in i. Fold-i 0, që nuk ka histori, mbetet jashtë këtij
      krahasimi."""),
    h2("4.4", "Modelet"),
    h3("4.4.1", "Ndërfaqja e përbashkët"),
    p("""Të gjithë detektorët kanë të njëjtën ndërfaqe me katër metoda: fit, score, save dhe load.
      Konventa e shenjës është e njëjtë për të gjithë: vlerë më e lartë e pikës do të thotë më
      anormale. Konventa kontrollohet me test automatik mbi të dhëna reale për secilin model, duke
      krahasuar medianën e pikëve të mashtrimeve me atë të transaksioneve legjitime. Falë kësaj,
      harnesi i vlerësimit, ansamblet dhe konsumatori i rrjedhës nuk varen nga modeli konkret."""),
    tab(
        "model_zoo",
        "Detektorët, mekanizmi i pikëzimit, kostoja e trajnimit dhe hiperparametrat bazë.",
        font_size=7.5,
    ),
    p("""Në tabelë, n është numri i mostrave, d numri i dimensioneve, t numri i pemëve, ψ madhësia e
      nën-mostrës, e numri i epokave, h numri i njësive të fshehura dhe i numri i iteracioneve."""),
    h3("4.4.2", "Isolation Forest"),
    p("""Implementimi ndjek formulimin origjinal [@liu2008], me pikën e marrë me shenjë të kundërt
      sipas konventës së studimit. Përveç dy hiperparametrave standardë, numrit të pemëve dhe
      madhësisë së nën-mostrës, ekspozohet edhe pjesa e kolonave që përdor secila pemë
      (max_features). Ky parametër nuk ndryshohet në konfigurimin bazë, por studiohet, sepse është
      ndërhyrja më e thjeshtë nëse dobësia e algoritmit lidhet me shpërndarjen e ndarjeve."""),
    p("""Studimi i thelluar i këtij detektori ka katër pjesë: hapësirën e hiperparametrave mbi
      numrin e pemëve dhe madhësinë e nën-mostrës, ndjeshmërinë ndaj pjesës së kolonave për pemë,
      numërimin e ndarjeve që merr secila kolonë në pemët e trajnuara, dhe trajnimin mbi një kopje
      të rrotulluar rastësisht të hapësirës. Testi i fundit kontrollon nëse ka rëndësi që boshtet
      përputhen me komponentët kryesorë, sepse një rrotullim ortogonal nuk ndryshon asnjë distancë,
      por e prish këtë përputhje."""),
    h3("4.4.3", "Autoencoder"),
    p("""Autoencoder-i është një rrjet me enkoder dhe dekoder simetrikë, i trajnuar vetëm mbi
      transaksionet normale të dritares së trajnimit, me gabimin mesatar kuadratik të rindërtimit si
      pikë anomalie. Implementimi lejon të ndryshohen një nga një shtatë parametra: dimensioni
      latent, gjerësia e shtresës së fshehur, thellësia e enkoderit, funksioni i humbjes, weight
      decay, dropout dhe niveli i zhurmës për variantin denoising."""),
    note("""Për të interpretuar ablacionet ka rëndësi një konventë: funksioni i humbjes gjatë
      trajnimit mund të jetë kuadratik, absolut ose Huber, por pika e anomalisë është gjithmonë
      gabimi mesatar kuadratik. Nëse pikëzimi do të përdorte të njëjtin funksion si trajnimi, do të
      ndryshonin njëkohësisht modeli dhe funksioni i renditjes, dhe dy efektet nuk do të ndaheshin
      dot."""),
    p("""Thellësia e enkoderit rritet duke e ngushtuar gjeometrikisht gjerësinë nga shtresa e parë
      drejt dimensionit latent, në mënyrë që një enkoder më i thellë të ndryshojë vetëm mënyrën si
      arrihet ngjeshja dhe jo sasinë e saj. Konfigurimet ku dimensioni latent nuk është më i vogël
      se gjerësia e shtresës së fshehur refuzohen, sepse në to nuk ka ngushticë."""),
    p("""Gjatë trajnimit ruhet humbja mesatare për çdo epokë. Kështu kurba e trajnimit mund të
      krahasohet me cilësinë e zbulimit në blloqet e testimit, krahasim që tregon nëse rrjeti ka
      filluar t'i rindërtojë mirë edhe anomalitë."""),
    h3("4.4.4", "One-Class SVM"),
    p("""One-Class SVM me kernel RBF ka kosto trajnimi të paktën kuadratike dhe nuk mund të
      trajnohet në kohë të arsyeshme mbi 100 000 deri 260 000 rreshtat e dritareve të trajnimit.
      Konfigurimi bazë e trajnon mbi një nën-mostër të rastësishme me seed të fiksuar prej 20 000
      transaksionesh normale. Ky është kompromisi i vetëm i studimit që imponohet nga kostoja
      llogaritëse dhe jo nga një zgjedhje parimore. Studimi i thelluar e mat çmimin e tij: ndërton
      kurbën e të mësuarit deri në 80 000 transaksione dhe tregon sa AP kushton kufizimi."""),
    p("""Studimi mat gjithashtu numrin e vektorëve mbështetës, sepse ai përcakton koston e
      inferencës: çdo transaksion i pikëzuar krahasohet me të gjithë ata. Kështu parametri ν, që
      përcakton sa i ngushtë është kufiri, përcakton edhe vonesën, dhe të dyja raportohen
      bashkë."""),
    h3("4.4.5", "Referenca e mbikëqyrur"),
    p("""Projekt-propozimi kërkonte njëkohësisht trajnim vetëm mbi transaksione normale dhe një
      model bazë me Regresion Logjistik, që ka nevojë për etiketa. Zgjidhja e zbatuar këtu e bën
      këtë mospërputhje të dukshme: modeli trajnohet mbi gjithë dritaren e trajnimit me etiketat e
      saj, përfshirë mashtrimet që ndodhen aty, dhe raportohet gjithmonë si referencë e mbikëqyrur.
      Ai tregon çfarë do të arrihej nëse do të përdoreshin etiketat historike, pra shërben si kufi i
      sipërm."""),
    h3("4.4.6", "Ablacioni linear"),
    p("""Një detektor i pestë është i regjistruar në kod, por nuk hyn në krahasimin kryesor. Ai
      llogarit gabimin e rindërtimit nga një nënhapësirë lineare PCA me rang të caktuar. Meqë
      veçoritë hyrëse janë vetë komponentë kryesorë, ky detektor është niveli minimal i familjes së
      rindërtimit, dhe diferenca mes tij dhe Autoencoder-it me të njëjtin rang latent tregon sa vlen
      jolineariteti."""),
]

_PRAGU = [
    h2("4.5", "Përcaktimi i pragut"),
    p("""Një funksion pikëzimi bëhet detektor vetëm kur i shtohet një prag, dhe zgjedhja e pragut
      është vendi ku rrjedhja e informacionit hyn më lehtë e vërehet më vështirë. Në këtë punim
      pragu caktohet me tri procedura të ndara."""),
    h3("4.5.1", "Pragu nga percentili i trajnimit"),
    p("""Protokolli kryesor e merr pragun nga percentili (1 − c) i pikëve të dritares së
      trajnimit:"""),
    eq("τ = Kuantili_{1−c} { s(x) : x ∈ D_trajnim }"),
    p("""ku c është kontaminimi. Kur nuk jepet ndryshe, c merret i barabartë me normën e mashtrimit
      në dritaren e trajnimit. Kjo përdor etiketa vetëm nga e kaluara, njësoj si referenca e
      mbikëqyrur. Që asnjë përfundim të mos varet nga kjo zgjedhje, kontaminimi ndryshohet në një
      interval prej dy rendesh madhësie."""),
    h3("4.5.2", "Pragu orakull"),
    p("""Për krahasim raportohet edhe pragu që maksimizon F1 mbi të dhënat e testit. Ky prag nuk
      mund të përdoret në praktikë, sepse kërkon etiketat e testit; ai jepet gjithmonë në kolonë të
      veçantë, si kufi i sipërm. Diferenca mes dy pragjeve tregon sa humbet një sistem real që nuk
      mund ta zgjedhë pragun me etiketa."""),
    h3("4.5.3", "Pragu adaptiv me dritare rrëshqitëse"),
    p("""Një prag i fiksuar gjatë trajnimit fikson një vlerë të pikës, jo një ngarkesë pune. Kur
      shpërndarja e pikëve zhvendoset, numri i alarmeve zhvendoset bashkë me të. Ky problem është i
      pavarur nga cilësia e zbulimit: një ekip i përgatitur për njëqind alarme në bllok nuk
      përballon dot shtatëqind, dhe alarmet që nuk shqyrtohen nuk kanë vlerë, sado mirë të jenë
      renditur."""),
    p("""Si alternativë propozohet dhe testohet një prag adaptiv, i cili llogaritet si percentili (1
      − c) i pikëve më të fundit brenda një dritareje rrëshqitëse prej 5000 mesazhesh dhe
      rifreskohet çdo 500 mesazhe, që kostoja të mbetet e vogël. Vendimi për një mesazh përdor vetëm
      mesazhet që kanë ardhur para tij; mesazhi që gjykohet nuk hyn kurrë në dritaren që e gjykon,
      kështu që procedura mund të zbatohet në një rrjedhë reale."""),
    h2("4.6", "Metrikat"),
    h3("4.6.1", "Metrikat e cilësisë së renditjes"),
    p("""Metrika kryesore është Average Precision, e cila përmbledh kurbën precision-recall si shumë
      e ponderuar e precision-it në çdo prag:"""),
    eq("AP = Σ_n (R_n − R_{n−1}) · P_n"),
    p("""Në çekuilibër ekstrem kurba precision-recall jep një pamje shumë më informuese se ROC,
      sepse norma e pozitivëve të rremë mbetet e vogël edhe kur alarmet e rreme janë shumë më tepër
      se ato të vërteta [@davis2006], [@saito2015]. AUC-ROC raportohet vetëm për krahasim me
      literaturën. Precision, recall dhe F1 raportohen në pragun nga trajnimi dhe, veçmas, në pragun
      orakull. Për çdo metrikë jepet edhe shpërndarja mbi fold-et, sepse një vlerë e vetme pa masën
      e pasigurisë thotë pak; aty ku nevojitet interval besimi mbi një bashkësi të vetme testimi, ai
      llogaritet me bootstrap [@efron1993]."""),
    h3("4.6.2", "Metrikat operacionale"),
    p("""Një ekip hetimesh nuk shqyrton gjithë renditjen, por aq alarme sa i lejon kapaciteti, dhe
      metrikat operacionale e pasqyrojnë këtë: raportohen precision dhe recall për një buxhet të
      fiksuar k alarmesh, si dhe recall-i i vlerës monetare, pra pjesa e eurove mashtruese të kapura
      brenda buxhetit, sepse humbja e një mashtrimi prej dy eurosh dhe e një mashtrimi prej dy mijë
      eurosh nuk janë i njëjti gabim."""),
    p("""Kursimet neto llogariten sipas një modeli të thjeshtë kostoje: një mashtrim i kapur kursen
      shumën e tij, ndërsa çdo alarm, i vërtetë apo i rremë, kushton një hetim:"""),
    eq("Kursimi(k) = Σ_{i∈TP(k)} shuma_i − c_het · |Alarme(k)|"),
    p("""Kursimet normalizohen ndaj detektorit të përsosur, i cili i kap të gjitha mashtrimet me aq
      alarme sa ka mashtrime. Kostoja e një hetimi vendoset tre euro; ndjeshmëria ndaj kësaj vlere
      diskutohet në Kapitullin 6."""),
    h3("4.6.3", "Metrikat e kostos llogaritëse"),
    p("""Për secilin model maten koha e trajnimit, koha e pikëzimit për transaksion dhe memoria e
      përdorur gjatë trajnimit. Memoria matet si diferencë mes pikut të memories rezidente gjatë
      trajnimit dhe vlerës në fillim të tij, jo si piku absolut i procesit, sepse ky i fundit
      përfshin të dhënat e ngarkuara më parë dhe do të ishte pothuajse i njëjtë për të gjithë
      modelet."""),
    h3("4.6.4", "Matja e zhvendosjes"),
    p("""Zhvendosja matet veç e veç për transaksionet legjitime dhe për mashtrimet, duke krahasuar
      dritaren e trajnimit të çdo fold-i me bllokun e tij të testimit. Për çdo veçori llogariten
      indeksi PSI, me dhjetë intervale të përcaktuara nga kuantilet e dritares së trajnimit, dhe
      statistika e testit Kolmogorov-Smirnov. Pragjet e zakonshme 0.10 dhe 0.25 të PSI-së lexohen si
      zhvendosje e moderuar dhe e madhe."""),
    p("""PSI ka një anshmëri që në këtë studim nuk mund të injorohet: në mostra të vogla ai rritet
      edhe kur shpërndarja nuk ka ndryshuar, sepse disa intervale mbeten bosh rastësisht. Një bllok
      testimi ka nga 13 deri në 88 mashtrime, ndaj PSI-ja e mashtrimeve lexohet kundrejt një
      shpërndarjeje zero të ndërtuar me permutacione: dritarja e trajnimit dhe blloku i testimit
      bashkohen, ndahen rastësisht në dy pjesë me madhësitë origjinale, dhe PSI llogaritet përsëri
      100 herë. Zhvendosja raportohet si e vërtetë vetëm kur vlera e vëzhguar e kalon këtë
      shpërndarje."""),
    p("""Si monitorim pa etiketa përdoret testi Page-Hinkley mbi rrjedhën e pikëve të anomalisë.
      Pragu i tij kalibrohet veç e veç për çdo fold dhe model, me permutacione mbi një rrjedhë
      reference të nxjerrë nga shpërndarja e pikëve të trajnimit, e cila nga ndërtimi nuk ka asnjë
      pikë ndryshimi."""),
    h2("4.7", "Përzgjedhja e hiperparametrave"),
    p("""Krahasimi i modeleve të akorduara keq nuk ka vlerë, por akordimi mbi të dhënat e testit e
      prish vlefshmërinë e krahasimit. Punimi ndjek dy rrugë të pavarura dhe i raporton të
      dyja."""),
    p("""Rruga e parë është validimi i brendshëm kohor. Dritarja e trajnimit e ndarjes 70/30 ndahet
      përsëri sipas kohës: kandidatët trajnohen mbi 75% e parë dhe renditen sipas AP-së në 25% e
      fundit. Kërkimi bëhet me Optuna dhe mostruesin TPE, me 60 prova për detektor [@akiba2019].
      Kandidatët trajnohen mbi një nën-mostër prej 60 000 transaksionesh me seed të fiksuar, që
      kërkimi të zgjasë minuta e jo orë; konfigurimi fitues përdoret pastaj në të gjitha fold-et, i
      trajnuar mbi dritaren e plotë të secilit."""),
    p("""Kërkimi bëhet një herë dhe jo brenda çdo fold-i, gjë që ka një pasojë që duhet thënë qartë.
      Dritarja e kërkimit, 70% e parë e rrjedhës, përmban blloqet e testimit të fold-eve 0 deri 3;
      blloqet e fold-eve 4 deri 7 fillojnë pas saj. Për fold-et e hershme zgjedhja e
      hiperparametrave ka parë të njëjtën periudhë mbi të cilën vlerësohet, dhe për këtë efekti i
      akordimit raportohet edhe veçmas për fold-et 4 deri 7, të cilat janë plotësisht të pavarura
      nga kërkimi."""),
    p("""Rruga e dytë nuk përdor fare etiketa. Kriteret Excess-Mass dhe Mass-Volume vlerësojnë sa
      mirë bashkësitë e nivelit të një funksioni pikëzimi e përqendrojnë masën probabilitare në
      vëllim të vogël [@goix2015], [@goix2016]:"""),
    eq("EM(t) = sup_u [ P(s≥u) − t·Leb(s≥u) ];   MV(α) = Leb(s≥u_α)"),
    p("""Vlerësimi i masës Lebesgue me Monte Carlo në 29 dimensione nuk është i realizueshëm,
      prandaj ndiqet zgjidhja e rekomanduar: kriteret mesatarizohen mbi nënhapësira të rastësishme
      me dimension të ulët, ku detektori trajnohet përsëri në secilën nënhapësirë. Dy hollësi të
      implementimit dolën vendimtare. Kriteret përcaktohen për një funksion normaliteti, ku
      bashkësitë e sipërme të nivelit janë rajonet e dendura; me konventën e kundërt të këtij
      projekti pikat uniforme do të mbushnin çdo bashkësi niveli dhe vëllimi i vlerësuar do të ishte
      i gjithë kutia kufizuese; për ta shmangur këtë, shenja kthehet brenda funksionit. Gjithashtu,
      rrjeta e pragjeve duhet të përfshijë bashkësinë boshe të nivelit, ndryshe supremumi mund të
      dalë negativ dhe kriteri nuk është më masë e vlefshme."""),
    p("""Këto kritere nuk përdoren për akordimin kryesor, sepse për çdo kandidat kërkojnë një
      trajnim në çdo nënhapësirë dhe një kërkim i plotë do të ishte shumë i kushtueshëm. Ato
      përdoren në një krahasim mbi rrjeta të vogla dhe të deklaruara, për një pyetje të vetme: a do
      të zgjidhnin të njëjtin konfigurim si kriteri me etiketa?"""),
    h2("4.8", "Studimet e thelluara për algoritëm"),
    p("""Përveç krahasimit kryesor, secili algoritëm ka një studim të veçantë, të ndërtuar rreth
      mekanizmit të tij dhe jo si kërkim i përgjithshëm hiperparametrash. Të gjitha studimet
      ekzekutohen në të tetë fold-et, me të njëjtën pasiguri si tabela kryesore."""),
    numbers(
        [
            "Isolation Forest: hapësira mbi numrin e pemëve dhe madhësinë e nën-mostrës, "
            "ndjeshmëria ndaj pjesës së kolonave për pemë, numërimi i ndarjeve për kolonë në pemët "
            "e trajnuara dhe trajnimi mbi një hapësirë të rrotulluar rastësisht.",
            "Autoencoder: hapësira mbi dimensionin latent dhe gjerësinë e shtresës së fshehur, "
            "thellësia e enkoderit, funksioni i humbjes, tre regularizues, kurba e trajnimit "
            "kundrejt cilësisë së zbulimit dhe krahasimi me projeksionin linear me rang të njëjtë.",
            "One-Class SVM: krahasimi i kernelëve, hapësira mbi nu dhe gamma, dhe kurba e të "
            "mësuarit sipas madhësisë së nën-mostrës së trajnimit, bashkë me koston përkatëse.",
            "Të tre bashkë: ndjeshmëria ndaj paraprocesimit, efekti i kufizimit të hyrjes te "
            "komponentët informativë, efekti i gjatësisë së dritares së trajnimit dhe analiza e "
            "gabimeve në nivel transaksioni.",
        ]
    ),
    p("""Këto studime ndryshojnë një parametër në një kohë, që efekti i secilit të matet veç. Mbetet
      pyetja nëse efektet mblidhen. Për këtë shtohet një studim i fundit me dizajn faktorial 2×2, ku
      secili detektor vlerësohet në katër kombinime: paraprocesimi bazë ose më i miri për të, dhe
      hiperparametrat bazë ose ata të akorduar. Dizajni e ndan përfitimin total në kontributin e
      paraprocesimit, atë të hiperparametrave dhe ndërveprimin mes tyre, dhe tregon nëse renditja
      ndryshon kur çdo algoritëm vlerësohet në konfigurimin e tij më të mirë. Konfigurimet "më të
      mira" vijnë nga studimet e mësipërme, të cilat i kanë parë të njëjtat blloqe testimi, prandaj
      ky rezultat raportohet si kufi i sipërm optimist dhe jo si vlerësim i paanshëm."""),
    p("""Studimi i kufizimit të hyrjes nuk është kërkim parametrash, por ndërhyrje. Analiza e
      atribuimit jep një shpjegim të mundshëm për renditjen e algoritmeve, por ai mbetet korrelacion
      derisa të ndërhyhet mbi shkakun e supozuar. Duke i dhënë secilit detektor vetëm k komponentët
      më informativë dhe duke parë kush fiton më shumë, shpjegimi testohet drejtpërsëdrejti."""),
]

_ARKITEKTURA = [
    h2("4.9", "Arkitektura e implementuar"),
    p("""Sistemi ndjek arkitekturën me pesë shtresa të përcaktuar në projekt-propozim (Figura
      [[fig:diagram_architecture]]). Shtresat janë module të veçanta me ndërfaqe të qarta, gjë që
      lejoi ndryshimin e modeleve pa prekur shtresën e rrjedhës dhe anasjelltas."""),
    fig("diagram_architecture", "Arkitektura e sistemit me pesë shtresa.", 15.0),
    h3("4.9.1", "Shtresa e rrjedhës"),
    p("""Apache Kafka punon në modalitetin KRaft, pa ZooKeeper, me një broker dhe një particion për
      topic. Kafka u zgjodh në vend të alternativave si Redpanda sepse e emërtojnë titulli dhe
      propozimi i temës, dhe sepse një shërbim KRaft me një nyje konfigurohet lehtë [@kreps2011].
      Mesazhet serializohen në JSON: në ritmet e testuara kostoja e kodimit është e papërfillshme,
      ndërsa mesazhet e lexueshme e bëjnë pipeline-in të lehtë për diagnostikim dhe lejojnë
      krahasimin e saktë të pikëve mes dy regjimeve."""),
    p("""Producer-i riprodhon bllokun e testimit me ritëm konstant të konfigurueshëm dhe ndjek një
      orar absolut, që vonesat e vogla të mos grumbullohen në devijim të ritmit. Consumer-i mbledh
      mikro-grupe deri në 64 mesazhe dhe i pikëzon si një matricë të vetme, me pritje të kufizuar në
      50 milisekonda."""),
    note("""Kufiri i pritjes nuk ishte planifikuar. Në ekzekutimin e parë vonesa end-to-end dilte më
      e ulët në ritme të larta se në ritme të ulëta, gjë që nuk ka kuptim fizik; shkaku ishte se në
      ritme të ulëta vonesën e përcaktonte vetë mbledhja e mikro-grupit. Ky është një shembull se si
      një defekt matjeje mund të japë një rezultat që duket i besueshëm."""),
    h3("4.9.2", "Matja e vonesës"),
    p("""Çdo mesazh mbart vulën kohore të krijimit nga producer-i. Consumer-i regjistron dy madhësi:
      kohën e inferencës, që mat vetëm llogaritjen e modelit dhe ndahet mbi mikro-grupin, dhe
      vonesën end-to-end, nga vula e producer-it deri në momentin kur vendimi është marrë dhe
      alarmi, nëse ka, i është dorëzuar producer-it të Kafka-s për publikim. Konfirmimi i dorëzimit
      në broker nuk pritet, prandaj vonesa e matur nuk përfshin rrugën e alarmit deri te broker-i.
      Producer-i dhe consumer-i punojnë në të njëjtin host, kështu që nuk ka mospërputhje orësh.
      Raportohen p50, p95 dhe p99, jo vetëm mesatarja."""),
    p("""Producer-i nuk nis derisa consumer-i të ketë marrë particionet dhe të ketë sinjalizuar se
      është gati. Pa këtë sinkronizim, mesazhet e para do të prisnin në radhë gjatë nisjes së
      consumer-it, dhe bishti i shpërndarjes do të matte kohën e nisjes në vend të vonesës në
      gjendje të qëndrueshme."""),
    h3("4.9.3", "Ruajtja dhe vizualizimi"),
    p("""Ngjarjet e pikëzuara dhe alarmet ruhen në PostgreSQL në dy tabela, me çelës të përbërë nga
      etiketa e ekzekutimit, identifikuesi i transaksionit dhe modeli; shkrimet bëhen në grupe që
      ruajtja të mos ngadalësojë rrjedhën. Për çdo ngjarje ruhen pika, vendimi, etiketa, vula kohore
      e krijimit, koha e inferencës, vonesa end-to-end dhe madhësia e mikro-grupit; për çdo alarm
      ruhen edhe pragu në fuqi dhe vula kohore e publikimit. Me këto të dhëna vonesa dhe vendimi
      mund të rindërtohen pas faktit."""),
    p("""Mbi këto tabela është ndërtuar një panel në Grafana OSS me nëntë grafikë: katër tregues
      përmbledhës (ngjarjet e pikëzuara, alarmet e publikuara, alarmet që janë mashtrime të vërteta
      dhe mashtrimet në rrjedhë), katër seri kohore (throughput-i i pikëzimit, alarmet me kalimin e
      kohës, percentilet e vonesës end-to-end dhe percentili 95 i kohës së inferencës për model) dhe
      një tabelë me alarmet e fundit."""),
    p("""I gjithë konfigurimi i Grafana-s, burimi i të dhënave dhe vetë paneli ruhen si skedarë në
      depo dhe ngarkohen automatikisht kur ngrihen shërbimet, kështu që vizualizimi nuk varet nga
      veprime manuale në ndërfaqe dhe është pjesë e riprodhimit. Një hollësi teknike ndikoi në
      implementim: makroja standarde e Grafana-s për grupim kohor nuk pranon shprehje të përbëra mbi
      kolonën e kohës, prandaj grupimi bëhet me aritmetikë mbi sekondat epokë."""),
    h3("4.9.4", "Paneli interaktiv i rezultateve"),
    p("""Mbi të njëjtën dosje rezultatesh është ndërtuar edhe një aplikacion web lokal me dy qëllime
      që dokumenti i shtypur nuk i mbulon. I pari është kontrolli: çdo tabelë, figurë dhe përfundim
      lexohet në çastin kur hapet faqja, kështu që paneli tregon gjendjen aktuale të depos, dhe çdo
      mospërputhje me këtë dokument do të dukej menjëherë. I dyti është riprodhimi: çdo seksion ka
      një buton që e ekzekuton përsëri eksperimentin përkatës dhe e shfaq daljen e tij rresht pas
      rreshti."""),
    p("""Dy zgjedhje të projektimit lidhen me natyrën e studimit. Konsola e ekzekutimit nuk pranon
      komanda të lira, por vetëm identifikues nga një katalog i deklaruar, dhe i ekzekuton ata një
      nga një, sepse eksperimentet garojnë për të njëjtat bërthama dhe ekzekutimi paralel do t'i
      shtrembëronte kohët që raporton Kapitulli 5. Grafikët vizatohen si SVG nga vetë kodi i
      projektit, pa biblioteka të jashtme, që paneli të punojë pa lidhje interneti dhe ngjyrat të
      jenë të njëjta me ato të figurave të këtij dokumenti."""),
    p("""Paneli përfshin edhe shtresën e rrjedhës: tregon gjendjen e tre kontejnerëve, lejon
      ngritjen e tyre, lexon numëruesit nga PostgreSQL dhe e shfaq panelin e Grafana-s brenda faqes.
      Kështu i gjithë zinxhiri, nga ekzekutimi i një eksperimenti deri te alarmet që mbërrijnë në
      bazë, mund të demonstrohet nga shfletuesi."""),
    h2("4.10", "Riprodhueshmëria"),
    p("""Çdo eksperiment shkruan një manifest me SHA-në e commit-it, hash-in SHA-256 të
      konfigurimit, versionet e paketave kryesore, kohën e ekzekutimit dhe përshkrimin e harduerit.
      Seed-et janë të fiksuara kudo ku ka rastësi. Determinizmi u kontrollua edhe në praktikë: dy
      cikle të plota dhe të pavarura trajnimi e vlerësimi dhanë tabela metrikash identike, me
      përjashtim të kolonave të kohës dhe të memories, të cilat ndryshojnë natyrshëm."""),
    p("""Masat metodologjike të këtij kapitulli janë të koduara edhe në teste që ekzekutohen me çdo
      ndryshim. Ato mbulojnë ndarjen kronologjike, mungesën e rrjedhjes së informacionit, kontratën
      e modeleve, konventën e shenjës mbi të dhëna reale, saktësinë e metrikave dhe barazinë e
      pikëve mes regjimit offline dhe atij në rrjedhë. Figurat e punimit vizatohen nga tabelat e
      ruajtura të eksperimenteve dhe mund të rindërtohen pa trajnuar përsëri asnjë model."""),
    tab(
        "environment",
        "Mjedisi eksperimental.",
        font_size=9.5,
    ),
    p("""Implementimi mbështetet në softuer të lirë: scikit-learn për modelet klasike dhe metrikat
      [@pedregosa2011], PyTorch për Autoencoder-in [@paszke2019], NumPy për llogaritjet numerike dhe
      Matplotlib për figurat. Versionet e sakta ruhen në çdo manifest. Të gjitha modelet trajnohen
      dhe ekzekutohen në CPU. Kjo është zgjedhje e qëllimshme: modelet janë të vogla, dhe matja e
      kostos operacionale në CPU është më afër realitetit të shumicës së sistemeve të pagesave se
      matja mbi një përshpejtues grafik."""),
]

BLOCKS = _DATA + _PROTOKOLLI + _PRAGU + _ARKITEKTURA

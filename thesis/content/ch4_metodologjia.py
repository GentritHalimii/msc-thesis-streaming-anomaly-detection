"""Kapitulli 4 — METODOLOGJIA."""

from blocks import bullets, eq, fig, h1, h2, h3, note, numbers, p, tab

_DATA = [
    h1("4", "Metodologjia"),
    p("""Ky kapitull përshkruan dataset-in, protokollin e vlerësimit, paraprocesimin, modelet,
      procedurën e pragut, metrikat, studimet për secilin algoritëm dhe arkitekturën e implementuar.
      Përshkrimi është i hollësishëm, sepse shumë nga dallimet mes rezultateve të publikuara për
      këtë dataset nuk vijnë nga algoritmet, por nga zgjedhje metodologjike që shpesh nuk
      raportohen."""),
    p("""Metodologjia ndjek projekt-propozimin, me dy ndryshime. Protokolli kryesor i vlerësimit
      është rolling-origin me tetë fold-e në vend të një ndarjeje të vetme 70/30, dhe metrika
      kryesore është Average Precision në vend të F1. Arsyet jepen në nënkapitujt 4.2.2 dhe 4.6.1;
      ndarja 70/30 dhe F1 raportohen gjithsesi."""),
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
    p("""Anonimizimi me PCA ka një pasojë që shfaqet gjatë gjithë punimit: veçoritë nuk mund të
      interpretohen semantikisht, sepse komponentët nuk kanë emra dhe nuk mund të thuhet cila
      sjellje e transaksionit e rrit pikën e anomalisë."""),
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
    p("""Pyetja e fundit eksploruese lidhet drejtpërdrejt me metodat unsupervised: sa larg klasës
      legjitime ndodhen mashtrimet. Për çdo transaksion të dritares së trajnimit të ndarjes 70/30 u
      mat distanca mesatare deri te dhjetë fqinjët e tij legjitimë më të afërt (Figura
      [[fig:geometry_knn_distance]]). Distanca mediane e një mashtrimi është 7.9 herë më e madhe se
      ajo e një transaksioni legjitim tipik, kështu që mashtrimet janë vërtet vlera të
      jashtëzakonshme."""),
    fig(
        "geometry_knn_distance",
        "Distanca mesatare deri te dhjetë fqinjët legjitimë më të afërt, sipas klasës.",
        15.0,
    ),
    p("""Kjo largësi nuk sjell megjithatë zbulim të lehtë. Figura e paraqet secilën klasë si pjesë
      të vetes, prandaj nuk e tregon disproporcionin mes tyre: dritarja e trajnimit ka afërsisht 199
      000 transaksione legjitime, dhe 5% e tyre që ndodhen më larg janë rreth 10 000 transaksione.
      Ato zënë të njëjtin rajon me 384 mashtrimet e dritares, të cilat janë shumë më pak në numër.
      Ky fakt ndihmon të kuptohen rezultatet modeste të Kapitullit 5."""),
    h3("4.1.3", "Kufizimet e dataset-it"),
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
      dimension. Kjo do ta prishte renditjen e çdo detektori të bazuar në distancë ose densitet,
      ndërsa një model linear i mbikëqyrur do të ndikohej shumë më pak, sepse mund t'i japë kolonës
      një peshë të vogël."""),
    note("""Rreziku nuk është vetëm teorik. Mungesa e kolonës Time mes veçorive kontrollohet me test
      automatik, sepse ky mekanizëm do të prodhonte një rënie të cilësisë me kohën që duket njësoj
      si ajo që vërehet në të dhëna, por për një arsye krejt tjetër."""),
    h3("4.2.2", "Protokolli rolling-origin"),
    p("""Projekt-propozimi parashikonte një ndarje të vetme kronologjike 70/30. Një ndarje e tillë
      jep një vlerësim për një moment të vetëm vendosjeje. Me 492 pozitivë në gjithë dataset-in ky
      vlerësim është i zhurmshëm, dhe nga një prerje e vetme nuk mund të thuhet nëse renditja e
      algoritmeve është e qëndrueshme apo e rastësishme. Prandaj vlerësimi përsëritet në tetë pika
      prerjeje të njëpasnjëshme me dritare trajnimi që zgjerohet, sipas skemës rolling-origin të
      përdorur në literaturën e parashikimit [@bergmeir2012] dhe të vlerësimit prekuencial
      [@gama2013]. Ky protokoll quhet më poshtë rolling-origin 8-fold."""),
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
    p("""Ndarja 70/30 e propozimit nuk braktiset. Modelet trajnohen edhe mbi të, rezultatet e saj
      jepen në Shtojcën D, dhe nënkapitulli 5.6 e krahason me protokollin 8-fold."""),
    h2("4.3", "Paraprocesimi si variabël eksperimentale"),
    p("""Siç u argumentua në nënkapitullin 2.9, largësia që përdorin detektorët varet nga
      paraprocesimi, ndonëse skaluesi zakonisht zgjidhet një herë dhe nuk rishikohet. Në këtë punim
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
        "Detektorët, mekanizmi i pikëzimit dhe hiperparametrat bazë.",
        query="Detektori != 'PCA lineare (ablacion)'",
        columns=["Detektori", "Familja", "Mekanizmi i pikëzimit", "Hiperparametrat"],
        font_size=8.5,
    ),
    h3("4.4.2", "Isolation Forest"),
    p("""Implementimi ndjek formulimin origjinal [@liu2008], me pikën e marrë me shenjë të kundërt
      sipas konventës së studimit. Përveç dy hiperparametrave standardë, numrit të pemëve dhe
      madhësisë së nën-mostrës, ekspozohet edhe pjesa e kolonave që përdor secila pemë
      (max_features). Ky parametër nuk ndryshohet në konfigurimin bazë, por studiohet, sepse është
      ndërhyrja më e thjeshtë nëse dobësia e algoritmit lidhet me shpërndarjen e ndarjeve."""),
    h3("4.4.3", "Autoencoder"),
    p("""Autoencoder-i është një rrjet me enkoder dhe dekoder simetrikë, i trajnuar vetëm mbi
      transaksionet normale të dritares së trajnimit, me gabimin mesatar kuadratik të rindërtimit si
      pikë anomalie. Implementimi lejon të ndryshohen një nga një shtatë parametra: dimensioni
      latent, gjerësia e shtresës së fshehur, thellësia e enkoderit, funksioni i humbjes, weight
      decay, dropout dhe niveli i zhurmës për variantin denoising."""),
    p("""Funksioni i humbjes gjatë trajnimit mund të jetë kuadratik, absolut ose Huber, por pika e
      anomalisë është gjithmonë gabimi mesatar kuadratik. Përndryshe do të ndryshonin njëkohësisht
      modeli dhe funksioni i renditjes, dhe efektet e tyre nuk do të ndaheshin dot. Konfigurimet ku
      dimensioni latent nuk është më i vogël se gjerësia e shtresës së fshehur nuk provohen, sepse
      në to nuk ka ngushticë."""),
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
      mbikëqyrur. Nënkapitulli 5.2.4 mat sa varen rezultatet nga kjo zgjedhje, duke e ndryshuar
      kontaminimin në një interval prej dy rendesh madhësie."""),
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
    p("""Metrika kryesore është Average Precision, e përkufizuar në nënkapitullin 3.3, e cila
      përmbledh kurbën precision-recall pa u lidhur me një prag. Projekt-propozimi e emërtonte F1 si
      metrikë kryesore. F1 varet megjithatë nga pragu, dhe pragu ndryshon nga një fold në tjetrin
      dhe nga një procedurë në tjetrën, kështu që një krahasim i bazuar vetëm në F1 do të përzinte
      cilësinë e renditjes me zgjedhjen e pragut. Për këtë arsye F1 raportohet kudo, por algoritmet
      renditen sipas AP-së."""),
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
    h3("4.6.3", "Metrikat e kostos llogaritëse"),
    p("""Për secilin model maten koha e trajnimit, koha e pikëzimit për transaksion dhe memoria e
      përdorur gjatë trajnimit. Memoria matet si diferencë mes pikut të memories rezidente gjatë
      trajnimit dhe vlerës në fillim të tij, jo si piku absolut i procesit, sepse ky i fundit
      përfshin të dhënat e ngarkuara më parë dhe do të ishte pothuajse i njëjtë për të gjithë
      modelet."""),
    h2("4.7", "Përzgjedhja e hiperparametrave"),
    p("""Krahasimi i modeleve të akorduara keq nuk ka vlerë, por akordimi mbi të dhënat e testit e
      prish vlefshmërinë e krahasimit. Hiperparametrat zgjidhen prandaj me validim të brendshëm
      kohor. Dritarja e trajnimit e ndarjes 70/30 ndahet përsëri sipas kohës: kandidatët trajnohen
      mbi 75% e parë dhe renditen sipas AP-së në 25% e fundit. Kërkimi bëhet me Optuna dhe
      mostruesin TPE, me 60 prova për detektor [@akiba2019]. Kandidatët trajnohen mbi një nën-mostër
      prej 60 000 transaksionesh me seed të fiksuar, që kërkimi të zgjasë minuta e jo orë;
      konfigurimi fitues përdoret pastaj në të gjitha fold-et, i trajnuar mbi dritaren e plotë të
      secilit."""),
    p("""Kërkimi bëhet një herë dhe jo brenda çdo fold-i, gjë që ka një pasojë që duhet thënë qartë.
      Dritarja e kërkimit, 70% e parë e rrjedhës, përmban blloqet e testimit të fold-eve 0 deri 3;
      blloqet e fold-eve 4 deri 7 fillojnë pas saj. Për fold-et e hershme zgjedhja e
      hiperparametrave ka parë të njëjtën periudhë mbi të cilën vlerësohet, dhe për këtë efekti i
      akordimit raportohet edhe veçmas për fold-et 4 deri 7, të cilat janë plotësisht të pavarura
      nga kërkimi."""),
    h2("4.8", "Studimet për secilin algoritëm"),
    p("""Përveç krahasimit kryesor, secili algoritëm ka një studim të veçantë, të ndërtuar rreth
      mekanizmit të tij dhe jo si kërkim i përgjithshëm hiperparametrash. Të gjitha studimet
      ekzekutohen në të tetë fold-et, me të njëjtën pasiguri si tabela kryesore."""),
    numbers(
        [
            "Isolation Forest: hapësira mbi numrin e pemëve dhe madhësinë e nën-mostrës, "
            "ndjeshmëria ndaj pjesës së kolonave për pemë, numërimi i ndarjeve për kolonë në pemët "
            "e trajnuara dhe trajnimi mbi një kopje të rrotulluar rastësisht të hapësirës. Testi i "
            "fundit kontrollon nëse ka rëndësi që boshtet përputhen me komponentët kryesorë, sepse "
            "një rrotullim ortogonal nuk ndryshon asnjë distancë, por e prish këtë përputhje.",
            "Autoencoder: hapësira mbi dimensionin latent dhe gjerësinë e shtresës së fshehur, "
            "thellësia e enkoderit, funksioni i humbjes, tre regularizues, numri i epokave dhe "
            "krahasimi me rindërtimin linear me PCA me rang të njëjtë.",
            "One-Class SVM: krahasimi i kernelëve, hapësira mbi nu dhe gamma, dhe kurba e të "
            "mësuarit sipas madhësisë së nën-mostrës së trajnimit, bashkë me koston përkatëse.",
        ]
    ),
    p("""Këto studime ndryshojnë një parametër në një kohë, që efekti i secilit të matet veç. Mbetet
      pyetja nëse efektet e paraprocesimit dhe të hiperparametrave mblidhen. Për këtë shtohet një
      studim i fundit me dizajn faktorial 2×2, ku secili detektor vlerësohet në katër kombinime:
      paraprocesimi bazë ose më i miri për të, dhe hiperparametrat bazë ose ata të akorduar. Dizajni
      e ndan përfitimin total në kontributin e paraprocesimit, atë të hiperparametrave dhe
      ndërveprimin mes tyre, dhe tregon nëse renditja ndryshon kur çdo algoritëm vlerësohet në
      konfigurimin e tij më të mirë. Konfigurimet "më të mira" vijnë nga studimet e mësipërme, të
      cilat i kanë parë të njëjtat blloqe testimi, prandaj ky rezultat raportohet si kufi i sipërm
      optimist dhe jo si vlerësim i paanshëm."""),
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

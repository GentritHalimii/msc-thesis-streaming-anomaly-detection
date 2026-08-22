"""Kapitulli 4 — METODOLOGJIA."""

from blocks import bullets, eq, fig, h1, h2, h3, note, numbers, p, tab

_DATA = [
    h1("4", "Metodologjia"),
    p("""Ky kapitull përshkruan dataset-in, protokollin e vlerësimit, modelet, procedurën e
      përcaktimit të pragut, metrikat dhe arkitekturën e implementuar. Përshkrimi është i
      hollësishëm me qëllim: pjesa më e madhe e dallimeve mes rezultateve të publikuara
      mbi këtë dataset nuk vjen nga algoritmet, por nga zgjedhje metodologjike që shpesh
      nuk raportohen."""),
    h2("4.1", "Dataset-i"),
    h3("4.1.1", "Origjina dhe struktura"),
    p("""Studimi përdor dataset-in publik Credit Card Fraud Detection të grupit Machine
      Learning të Université Libre de Bruxelles [@ulb_dataset]. Ai përmban transaksione
      reale me karta krediti të kryera nga mbajtës evropianë gjatë dy ditëve të shtatorit
      2013. Struktura është e thjeshtë: një kolonë Time me sekondat e kaluara nga
      transaksioni i parë, njëzet e tetë kolona V1–V28 që janë komponentë kryesorë të
      dala nga një transformim PCA i aplikuar nga publikuesit për arsye
      konfidencialiteti, kolona Amount me vlerën e transaksionit, dhe kolona Class me
      etiketën binare."""),
    tab(
        "eda_overview",
        "Karakteristikat kryesore të dataset-it ULB Credit Card Fraud.",
        rename={"treguesi": "Treguesi", "vlera": "Vlera"},
        font_size=10,
    ),
    p("""Anonimizimi me PCA ka dy pasoja që përshkojnë gjithë punimin. E para është se
      interpretimi semantik i veçorive është i pamundur: nuk mund të thuhet se cila
      sjellje e transaksionit e ngre pikën e anomalisë, sepse komponentët nuk kanë emra.
      E dyta, më pak e diskutuar, është se një detektor linear rindërtimi bazuar në PCA
      nuk është thjesht një bazë e dobët krahasimi, por pragu natyror i familjes së
      rindërtimit; prandaj ai u përfshi shprehimisht në krahasim."""),
    h3("4.1.2", "Analiza eksploruese"),
    p("""Analiza eksploruese nxori disa fakte që ndikojnë drejtpërdrejt në interpretimin e
      rezultateve. Vëllimi i transaksioneve ndjek një cikël të qartë ditë–natë, ndërsa
      shfaqja e mashtrimeve nuk e ndjek atë cikël; kjo do të thotë se norma e mashtrimit
      për orë ndryshon shumë, dhe blloqe testimi me numër të barabartë rreshtash mbulojnë
      intervale kohore shumë të ndryshme."""),
    fig(
        "eda_volume_and_fraud",
        "Vëllimi i transaksioneve për orë (lart) dhe numri i mashtrimeve për orë (poshtë). "
        "Mashtrimet nuk e ndjekin ciklin ditor të vëllimit; grupimet e tyre janë të "
        "dukshme rreth orëve me trafik të ulët.",
        15.0,
    ),
    p("""Norma e mashtrimit sipas orës së ditës e bën këtë edhe më të qartë: në orën dy të
      mëngjesit ajo arrin rreth 1.7 për qind, pra afërsisht dhjetë herë mbi mesataren
      globale. Ky është një sinjal i fortë, por i papërdorshëm në këtë punim si veçori
      modeli: koha përdoret për renditjen e rrjedhës dhe për përcaktimin e ndarjes, prandaj
      futja e saj si hyrje do të ndërthurte variablin e ndarjes me hyrjen e modelit. Kjo
      zgjedhje diskutohet përsëri në kufizimet."""),
    fig(
        "eda_hourly_rate",
        "Norma e mashtrimit sipas orës së ditës, e grumbulluar mbi të dy ditët. Vija e "
        "ndërprerë tregon mesataren globale prej 0.173 për qind.",
        14.0,
    ),
    p("""Shpërndarja e shumave sjell një gjetje kundërintuitive. Mesatarja e shumës së
      mashtrimeve është më e lartë se ajo e transaksioneve legjitime, por mediana është
      dukshëm më e ulët — 9.25 euro kundrejt 22 eurove. Kjo do të thotë se shpërndarja e
      mashtrimeve është fort e zhdrejtë: shumica janë transaksione shumë të vogla, ndërsa
      një pakicë janë shumë të mëdha. Njëzet e shtatë mashtrime kanë shumë saktësisht
      zero, gjë që përputhet me modelin e njohur të testimit të kartave, ku sulmuesi
      verifikon vlefshmërinë e një karte me një autorizim pa vlerë përpara përdorimit
      real."""),
    fig(
        "eda_amounts",
        "Shpërndarja e shumave për të dyja klasat në shkallë logaritmike (majtas) dhe "
        "krahasimi i kuartileve (djathtas). Mashtrimet përqendrohen te shumat e vogla, "
        "me një bisht të gjatë drejt vlerave të larta.",
        15.0,
    ),
    p("""Së fundi, fuqia diskriminuese njëvariablëshe e secilës veçori u mat me ROC-AUC.
      Komponentët V14, V4, V12, V11 dhe V10 dalin qartësisht mbi të tjerët. Ky rezultat
      shërben më vonë si pikë referimi për analizën e interpretueshmërisë: nëse një
      detektor nuk u kushton vëmendje pikërisht këtyre dimensioneve, atëherë ai po
      shpërdoron kapacitetin e tij."""),
    fig(
        "eda_feature_signal",
        "Pesëmbëdhjetë veçoritë me sinjalin më të fortë njëvariablësh, matur me ROC-AUC. "
        "Vlera 0.5 do të thotë mungesë e plotë e sinjalit.",
        13.0,
    ),
    p("""Matrica e korrelacionit konfirmon prejardhjen e deklaruar të të dhënave:
      korrelacioni mesatar absolut jashtë diagonales është 0.008, praktikisht zero, siç
      pritet nga komponentë kryesorë ortogonalë. Korrelacionet e vetme të konsiderueshme
      përfshijnë kolonën Amount, e cila nuk ka qenë pjesë e transformimit PCA — vlera më
      e lartë është 0.531 mes Amount dhe V2. Ky është një kontroll i thjeshtë por i
      dobishëm i integritetit të të dhënave."""),
    fig(
        "eda_correlation",
        "Matrica e korrelacionit të Pearson-it mes 29 veçorive hyrëse. Ortogonaliteti i "
        "komponentëve V1–V28 është i dukshëm; korrelacionet e vetme jotriviale përfshijnë "
        "kolonën Amount.",
        12.0,
    ),
    h3("4.1.3", "Kufizimet e dataset-it"),
    p("""Tri kufizime duhen deklaruar përpara se të interpretohet çdo rezultat."""),
    bullets(
        [
            "Mungesa e identifikuesit të kartës. Pa të, agregimi për llogari mbi dritare "
            "kohore — teknika që literatura e aplikuar e raporton si më efektiven "
            "[@whitrow2009], [@bahnsen2016] — është i pamundur, si dhe modelimi sekuencial "
            "për mbajtës [@jurgovsky2018]. Rezultatet e këtij punimi duhen lexuar si të "
            "vlefshme për zbulim pikësor pa kontekst llogarie.",
            "Kohëzgjatja prej vetëm dyzet e tetë orësh. Kjo lejon vlerësimin e zhvendosjes "
            "brenda-ditore dhe mes dy ditëve, por jo të zhvendosjes sezonale ose "
            "afatgjatë.",
            "Etiketat konsiderohen të plota dhe të sakta. Në realitet një pjesë e "
            "mashtrimeve nuk kontestohet kurrë dhe mbetet e etiketuar gabimisht si "
            "legjitime, gjë që i bën vlerësimet e precizitetit pesimiste.",
        ]
    ),
]

_PROTOKOLLI = [
    h2("4.2", "Protokolli i vlerësimit"),
    h3("4.2.1", "Ndarja kronologjike dhe disiplina kundër rrjedhjes"),
    p("""Të dhënat renditen sipas kolonës Time me renditje të qëndrueshme, që do të thotë
      se rreshtat me të njëjtën vlerë kohe ruajnë rendin origjinal të skedarit dhe ndarja
      është plotësisht deterministe. Ndarja bëhet sipas rendit kohor dhe kurrë me
      përzierje. Modelet e pambikëqyrura trajnohen vetëm mbi transaksionet normale të
      dritares së trajnimit; skaluesi fitohet vetëm mbi dritaren e trajnimit dhe pastaj
      aplikohet mbi bllokun e testimit."""),
    p("""Kolona Time nuk përdoret si veçori hyrëse. Vektori i veçorive përbëhet nga V1–V28
      dhe Amount, gjithsej njëzet e nëntë dimensione. Kjo zgjedhje është e domosdoshme
      teknikisht: meqë Time përcakton ndarjen, në një ndarje kronologjike vlerat e saj në
      bllokun e testimit janë sistematikisht jashtë intervalit të parë gjatë trajnimit,
      dhe pas skalimit çdo pikë testimi do të merrte një vlerë ekstreme në atë dimension.
      Kjo do të prishte renditjen e çdo detektori të bazuar në distancë ose densitet, pa
      prekur fare një model të mbikëqyrur linear."""),
    note("""Ky nuk është një rrezik teorik. Në një fazë të hershme të punës e verifikova
      shprehimisht me test automatik se Time nuk gjendet mes veçorive, sepse pikërisht
      ky mekanizëm do të prodhonte një model degradimi që duket identik me atë që
      vëzhgohet, por për arsye krejt të gabuar."""),
    h3("4.2.2", "Protokolli rolling-origin"),
    p("""Një ndarje e vetme 70/30 jep një vlerësim të performancës në një moment të vetëm
      hipotetik vendosjeje. Me 492 pozitivë në të gjithë dataset-in, ky vlerësim është i
      zhurmshëm, dhe nuk ka mënyrë të dallohet nga një ndarje e vetme nëse renditja e
      algoritmeve është e qëndrueshme apo artefakt i pikës së prerjes. Prandaj vlerësimi
      përsëritet në tetë pika të njëpasnjëshme prerjeje me dritare trajnimi që zgjerohet,
      sipas skemës rolling-origin të konsoliduar në literaturën e parashikimit
      [@tashman2000], [@bergmeir2012] dhe të vlerësimit prekuencial [@gama2013]."""),
    eq("Fold i:  trajno mbi rreshtat [0, c_i),  testo mbi [c_i, c_{i+1})"),
    p("""Pikat e prerjes c_i ndajnë pjesën e rrjedhës pas 40 për qindëshit fillestar në
      tetë blloqe të barabarta sipas numrit të rreshtave. Çdo fold rindërton nga fillimi
      të gjithë zinxhirin: skaluesin e vet, modelet e veta dhe pragjet e veta. Asgjë nuk
      transferohet nga një fold në tjetrin, prandaj asnjë informacion nga një bllok i
      mëvonshëm nuk mund të rrjedhë prapa."""),
    fig(
        "diagram_protocol",
        "Gjeometria e protokollit rolling-origin. Dritarja e trajnimit zgjerohet me çdo "
        "fold, ndërsa blloqet e testimit e mbulojnë rrjedhën pa mbivendosje. Numri i "
        "mashtrimeve për bllok varion nga 13 në 88.",
        15.0,
    ),
    p("""Numri i folds-ave nuk është zgjedhur si numër i rrumbullakët. Ai është rezultat i
      një kompromisi mes dy kufizimeve që tërheqin në drejtime të kundërta. Nga njëra anë,
      testi i çiftuar i Wilcoxon-it me N folds mund të prodhojë p-vlerë dy-bishtore jo më
      të vogël se 2/2^N; me gjashtë folds kjo është 0.031 dhe nuk mbijeton korrigjimin e
      Holm-it për krahasime të shumëfishta, sado i qëndrueshëm të jetë rezultati. Nga ana
      tjetër, me shumë folds blloqet e testimit zvogëlohen derisa disa prej tyre të mbajnë
      më pak se dhjetë pozitivë dhe AP-ja e tyre bëhet zhurmë. Me tetë folds, çdo bllok
      mban të paktën trembëdhjetë pozitivë dhe p-vlera më e vogël e arritshme është
      0.0078, e cila mbijeton korrigjimin për deri në gjashtë krahasime të
      paradeklaruara."""),
    tab(
        "fold_summary",
        "Struktura e tetë folds-ave: madhësia e dritares së trajnimit dhe e bllokut të "
        "testimit, numri i mashtrimeve dhe intervali kohor i mbuluar.",
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
    p("""Tabela zbulon një veti të rëndësishme të të dhënave: blloqet me numër të
      barabartë rreshtash mbulojnë intervale kohore shumë të ndryshme, sepse dendësia e
      transaksioneve ndryshon me orën. Fold-i 1 shquhet me 88 mashtrime, afërsisht katër
      herë mbi mesataren e blloqeve të tjera — ai përfshin një grumbullim mashtrimesh që
      do të rezultojë vendimtar për të kuptuar variancën e lartë të rezultateve."""),
    h2("4.3", "Modelet"),
    h3("4.3.1", "Ndërfaqja e përbashkët"),
    p("""Të gjithë detektorët implementojnë të njëjtën ndërfaqe me katër metoda: fit, score,
      save dhe load. Konventa e shenjës është uniforme dhe e detyrueshme: vlera më e
      lartë e pikës do të thotë gjithmonë më anormale. Kjo konventë verifikohet me test
      automatik mbi të dhëna reale për secilin model, duke krahasuar medianën e pikëve të
      mashtrimeve me atë të transaksioneve legjitime. Uniformiteti nuk është thjesht
      higjienë kodi: ai lejon që harnesi i vlerësimit, ansamblet dhe konsumatori i
      rrjedhës të mbeten krejtësisht të pavarur nga identiteti i modelit."""),
    h3("4.3.2", "Familjet e detektorëve"),
    p("""Krahasimi përfshin katërmbëdhjetë detektorë të pambikëqyrur, të organizuar sipas
      mekanizmit me të cilin përcaktojnë se çfarë është anormale. Zgjerimi nga tre
      algoritmet e propozimit fillestar në katërmbëdhjetë nuk e zhvendos fokusin, por e
      bën përgjigjen e interpretueshme: pa e ditur se ku qëndrojnë Isolation Forest,
      Autoencoder dhe One-Class SVM përballë familjeve të tjera, nuk mund të gjykohet
      nëse dallimet mes tyre janë të mëdha apo të parëndësishme."""),
    tab(
        "model_zoo",
        "Detektorët e krahasuar, mekanizmi i tyre i pikëzimit, kostoja asimptotike e "
        "trajnimit dhe hiperparametrat e përdorur. Simbolet: n mostra, d dimensione, "
        "t pemë, ψ madhësia e nën-mostrës, e epoka, h njësi të fshehura, i iteracione, "
        "k komponentë ose projeksione.",
        font_size=7.5,
    ),
    p("""Tri vendime implementimi meritojnë shpjegim, sepse ndikojnë drejtpërdrejt në
      rezultate."""),
    numbers(
        [
            "One-Class SVM-ja me kernel RBF ka kosto trajnimi të paktën kuadratike, çka e bën "
            "të papërdorshëm mbi njëqind e tetëdhjetë mijë rreshta. Ai trajnohet mbi një "
            "nën-mostër të rastësishme me seed të fiksuar prej njëzet mijë transaksionesh "
            "normale. Kjo është një zgjedhje e dokumentuar, jo e fshehur, dhe e njëjta "
            "logjikë zbatohet për LOF-in, kNN-në dhe vlerësuesin robust të kovariancës.",
            "Deep SVDD-ja implementohet me dy masat mbrojtëse kundër kolapsit të hipersferës "
            "të përshkruara nga autorët origjinalë [@ruff2018]: rrjeti nuk ka terma "
            "anshmërie dhe qendra fiksohet nga një kalim fillestar përpara trajnimit. Pa to "
            "modeli konvergjon te një zgjidhje triviale ku çdo hyrje hartohet në të njëjtën "
            "pikë.",
            "Autoenkoderi variacional pikëzohet me kufirin e poshtëm negativ të evidencës, "
            "duke përdorur kodin latent mesatar në kohën e inferencës, që e bën pikëzimin "
            "deterministik. Logaritmi i variancës kufizohet numerikisht, sepse "
            "eksponencimi i tij shpërthen shpejt gjatë epokave të para.",
        ]
    ),
    h3("4.3.3", "Referenca e mbikëqyrur"),
    p("""Projekt-propozimi kërkonte njëkohësisht trajnim vetëm mbi transaksione normale
      dhe një bazë krahasimi me Regresion Logjistik. Këto dy kërkesa janë në
      kundërshtim, sepse regresioni logjistik ka nevojë për etiketa. Zgjidhja e
      zbatuar këtu e bën kundërshtinë të dukshme në vend që ta fshehë: modeli trajnohet
      mbi të gjithë dritaren e trajnimit me etiketat e saj, përfshirë mashtrimet që
      ndodhen natyrshëm aty, dhe raportohet gjithmonë si referencë e mbikëqyrur, jo si
      konkurrent i barabartë. Ai i përgjigjet pyetjes "çfarë do të arrihej nëse etiketat
      historike do të përdoreshin" dhe shërben si kufi i sipërm i arritshëm."""),
]

_PRAGU = [
    h2("4.4", "Përcaktimi i pragut"),
    p("""Një funksion pikëzimi bëhet detektor vetëm pasi i shtohet një prag. Zgjedhja e
      pragut është pikërisht vendi ku rrjedhja e informacionit hyn më lehtë dhe vërehet
      më vështirë, prandaj këtu përdoren tri procedura krejt të ndara."""),
    h3("4.4.1", "Pragu nga percentili i trajnimit"),
    p("""Protokolli parësor e nxjerr pragun nga percentili (1 − c) i shpërndarjes së pikëve
      mbi dritaren e trajnimit:"""),
    eq("τ = Quantile_{1−c}( { s(x) : x ∈ dritarja e trajnimit } )"),
    p("""ku c është hiperparametri i kontaminimit. Në mungesë të një vlere të caktuar,
      c merret i barabartë me normën e mashtrimit të vëzhguar në dritaren e trajnimit.
      Kjo përdor etiketa vetëm nga e kaluara — i njëjti supozim i disponueshmërisë që i
      është dhënë tashmë referencës së mbikëqyrur — dhe deklarohet shprehimisht. Për të
      siguruar që asnjë përfundim të mos varet nga kjo zgjedhje, kontaminimi skanohet në
      një interval prej dy urdhrash madhësie."""),
    h3("4.4.2", "Pragu orakull"),
    p("""Për krahasim raportohet edhe pragu që maksimizon F1-shin mbi bashkësinë e testimit.
      Ky prag është i paarritshëm në praktikë, sepse kërkon etiketat e testit. Ai
      paraqitet gjithmonë në kolonë të veçantë dhe emërtohet si kufi i sipërm; të dy
      numrat nuk përzihen kurrë në të njëjtën kolonë. Diferenca mes tyre është një masë e
      dobishme e asaj se sa humbet një sistem real që nuk mund ta zgjedhë pragun me
      etiketa."""),
    h3("4.4.3", "Pragu adaptiv me dritare rrëshqitëse"),
    p("""Një prag i fiksuar në kohën e trajnimit fikson një pikë, jo një ngarkesë pune.
      Nëse shpërndarja e pikëve zhvendoset, numri i alarmeve zhvendoset me të. Kjo është
      një mënyrë dështimi e pavarur nga cilësia e zbulimit: një ekip i dimensionuar për
      njëqind alarme në bllok nuk mund të përballojë shtatëqind, dhe alarmet që nuk
      hapen kurrë nuk kanë vlerë sado mirë të renditura të jenë."""),
    p("""Prandaj propozohet dhe testohet një alternativë: pragu llogaritet si percentili
      (1 − c) i pikëve më të fundit brenda një dritareje rrëshqitëse, i rifreskuar çdo
      disa qindra mesazhe për ta mbajtur koston të kufizuar. Vendimi për mesazhin i
      përdor vetëm mesazhet që kanë mbërritur para tij — mesazhi që gjykohet nuk hyn
      kurrë në dritaren që e gjykon — gjë që e bën procedurën shkakësore dhe të
      zbatueshme në një rrjedhë reale."""),
    h2("4.5", "Metrikat"),
    h3("4.5.1", "Metrikat e cilësisë së renditjes"),
    p("""Metrika kryesore është precizioni mesatar, i cili përmbledh kurbën
      precision–recall si shumë e ponderuar e precizitetit në çdo prag:"""),
    eq("AP = Σ_n (R_n − R_{n−1}) · P_n"),
    p("""Arsyeja e zgjedhjes është e dokumentuar mirë: në çekuilibër ekstrem kurba PR jep
      një pamje shumë më informative se ROC-ja, sepse norma e pozitivëve të rremë mbetet
      e vogël edhe kur alarmet e rreme janë shumëfish më të shumta se ato të vërteta
      [@davis2006], [@saito2015]. AUC-ROC raportohet gjithashtu, por vetëm për
      krahasueshmëri me literaturën, dhe rezultatet e Kapitullit 5 e tregojnë qartë pse
      ai nuk duhet të jetë metrika vendimtare."""),
    p("""Precizioni, ndjeshmëria dhe F1-shi raportohen në pragun e nxjerrë nga trajnimi
      dhe, veçmas, në pragun orakull."""),
    h3("4.5.2", "Metrikat operacionale"),
    p("""Asnjë ekip hetimi nuk shqyrton një renditje të plotë; ai shqyrton aq alarme sa i
      lejon kapaciteti. Prandaj raportohen edhe precizioni dhe ndjeshmëria në buxhet
      fiks alarmesh k, si dhe ndjeshmëria e vlerës monetare — pjesa e eurove
      mashtruese të kapura brenda buxhetit — sepse një mashtrim i humbur prej dy eurove
      dhe një prej dy mijë eurove nuk janë i njëjti gabim."""),
    p("""Kursimet neto llogariten sipas një modeli kostoje të thjeshtë dhe të deklaruar:
      një mashtrim i kapur kursen shumën e tij, ndërsa çdo alarm i ngritur, i vërtetë apo
      i rremë, kushton një hetim:"""),
    eq("Kursimi(k) = Σ_{i ∈ TP(k)} shuma_i − c_het · |Alarme(k)|"),
    p("""Normalizimi bëhet ndaj detektorit të përsosur, i cili kap çdo mashtrim duke
      ngritur saktësisht aq alarme sa ka mashtrime. Kostoja e hetimit vendoset në tre
      euro; ndjeshmëria ndaj kësaj zgjedhjeje diskutohet në Kapitullin 6."""),
    h3("4.5.3", "Metrikat e kostos llogaritëse"),
    p("""Për secilin model matet koha e trajnimit, kohë e pikëzimit për transaksion dhe
      gjurma e memories gjatë trajnimit. Gjurma matet si diferencë mes pikut të memories
      rezidente gjatë bllokut dhe vlerës në hyrje të tij, jo si piku absolut i procesit,
      sepse ky i fundit përfshin të dhënat e ngarkuara paraprakisht dhe do të ishte
      pothuajse i njëjtë për të gjithë modelet."""),
    h2("4.6", "Përzgjedhja e hiperparametrave"),
    p("""Krahasimi mes modeleve të akorduara keq nuk ka vlerë. Njëkohësisht, akordimi mbi
      bashkësinë e testimit e shkatërron vlefshmërinë e tij. Prandaj përdoren dy rrugë të
      pavarura, dhe të dyja raportohen."""),
    p("""Rruga e parë është validimi i brendshëm kohor: dritarja e trajnimit ndahet
      përsëri sipas kohës, kandidatët përshtaten mbi 75 për qindëshin e parë dhe
      renditen sipas precizionit mesatar në 25 për qindëshin e fundit. Kërkimi kryhet me
      Optuna duke përdorur mostruesin TPE [@akiba2019]. Kandidatët përshtaten mbi një
      nën-mostër me seed të fiksuar, që një kërkim me njëzet e pesë prova mbi dymbëdhjetë
      detektorë të përfundojë në minuta e jo në ditë; konfigurimi fitues ripërshtatet
      pastaj mbi dritaren e plotë."""),
    p("""Rruga e dytë nuk përdor fare etiketa. Kriteret Excess-Mass dhe Mass-Volume
      vlerësojnë sa mirë grupet e nivelit të një funksioni pikëzimi e përqendrojnë masën
      probabilitare në vëllim të vogël [@goix2015], [@goix2016]:"""),
    eq("EM(t) = sup_u [ P(s ≥ u) − t · Leb(s ≥ u) ],   MV(α) = Leb(s ≥ u_α)  ku P(s ≥ u_α) = α"),
    p("""Vlerësimi i masës Lebesgue me Monte Carlo është i pamundur në njëzet e nëntë
      dimensione, prandaj ndiqet zgjidhja e rekomanduar: kriteret mesatarizohen mbi
      nënhapësira të rastësishme me dimension të ulët, ku detektori ripërshtatet në secilën
      nënhapësirë. Një hollësi implementimi që rezultoi vendimtare: këto kritere
      përcaktohen për një funksion normaliteti, ku grupet e sipërme të nivelit janë
      rajonet e dendura. Me konventën e kundërt të këtij projekti, pikat uniforme
      mbushin çdo grup niveli dhe vëllimi i vlerësuar kolapson në të gjithë kutinë
      kufizuese; shenja prandaj kthehet brenda funksionit."""),
    h2("4.7", "Arkitektura e implementuar"),
    p("""Sistemi ndjek arkitekturën pesështresore të përcaktuar në projekt-propozim.
      Ndarja mes shtresave nuk është vetëm konceptuale: secila është një modul i veçantë
      me ndërfaqe të qartë, gjë që lejoi zëvendësimin e modeleve pa prekur shtresën e
      rrjedhës dhe anasjelltas."""),
    fig(
        "diagram_architecture",
        "Arkitektura pesështresore e sistemit dhe ajo që kalon nëpër çdo kufi mes shtresave.",
        14.5,
    ),
    h3("4.7.1", "Shtresa e rrjedhës"),
    p("""Apache Kafka ekzekutohet në modalitetin KRaft, pa ZooKeeper, me një broker të
      vetëm dhe një particion për temë. Zgjedhja e Kafka-s në vend të alternativave si
      Redpanda u bë sepse titulli dhe propozimi i temës e emërtojnë shprehimisht atë, dhe
      sepse një shërbim KRaft me një nyje kushton pak më shumë se alternativat në
      konfigurim [@kreps2011]. Serializimi bëhet me JSON: në ritmet e testuara kostoja e
      kodimit është e papërfillshme, ndërsa lexueshmëria e mesazheve e bën pipeline-in të
      diagnostikueshëm dhe lejon krahasim bit-për-bit të pikëve mes dy regjimeve."""),
    p("""Prodhuesi riprodhon bllokun e testimit me ritëm konstant të konfigurueshëm, duke
      përdorur një orar absolut për të shmangur grumbullimin e devijimit të ritmit.
      Konsumatori mbledh mikro-grupe deri në gjashtëdhjetë e katër mesazhe dhe i pikëzon
      si një matricë të vetme, me kohëzgjatje pritjeje të kufizuar në pesëdhjetë
      milisekonda."""),
    note("""Kufizimi i kësaj pritjeje nuk ishte planifikuar. Në ekzekutimin e parë vonesa
      fund-më-fund dilte më e ulët në ritme të larta sesa në ritme të ulëta, gjë që s'ka
      kuptim fizik; shkaku ishte se në ritme të ulëta vetë mbledhja e mikro-grupit
      dominonte vonesën. Ky është një shembull i dobishëm se si një defekt matjeje mund
      të prodhojë një rezultat që duket i publikueshëm."""),
    h3("4.7.2", "Matja e vonesës"),
    p("""Çdo mesazh mbart një vulë kohore të prodhimit. Konsumatori regjistron dy madhësi
      të ndara: vonesën e inferencës, që mat vetëm kalimin përpara të modelit dhe
      amortizohet mbi mikro-grupin, dhe vonesën fund-më-fund, nga vula e prodhuesit deri
      pas publikimit të alarmit. Prodhuesi dhe konsumatori ekzekutohen në të njëjtin host,
      prandaj nuk ka nevojë për trajtim të mospërputhjes së orëve. Raportohen shpërndarjet
      e plota, jo vetëm mesatarja: p50, p95 dhe p99."""),
    p("""Një hollësi që ndikon në vlefshmërinë e matjes: prodhuesi nuk niset derisa
      konsumatori të ketë marrë caktimin e particioneve dhe të ketë sinjalizuar
      gatishmërinë. Pa këtë sinkronizim, mesazhet e para presin në radhë ndërsa
      konsumatori po ngrihet, dhe bishti i shpërndarjes ndotet me kohën e nisjes në vend
      se me vonesën e gjendjes së qëndrueshme."""),
    h3("4.7.3", "Persistimi dhe vizualizimi"),
    p("""Të gjitha ngjarjet e pikëzuara dhe alarmet ruhen në PostgreSQL në dy tabela të
      indeksuara sipas etiketës së ekzekutimit, me shkrime të grumbulluara. Mbi to është
      ndërtuar një panel Grafana OSS, i konfiguruar tërësisht nga skedarë në depo — burimi
      i të dhënave dhe vetë paneli — që gjendja e vizualizimit të mos varet nga veprime
      manuale në ndërfaqe dhe të jetë pjesë e riprodhueshmërisë."""),
    h2("4.8", "Riprodhueshmëria"),
    p("""Çdo eksperiment shkruan një manifest me SHA-në e commit-it, hash-in SHA-256 të
      konfigurimit, versionet e paketave të gjurmuara, vulën kohore dhe përshkrimin e
      harduerit. Seed-et janë të fiksuara në çdo pikë ku ndodh rastësi. Determinizmi u
      verifikua në mënyrë empirike dhe jo vetëm si pretendim: dy cikle të plota e të
      pavarura ritrajnimi dhe vlerësimi prodhuan tabela metrike identike bit-për-bit,
      me përjashtim të kolonave të kohës dhe të memories, të cilat për nga natyra
      ndryshojnë."""),
    tab(
        "environment",
        "Mjedisi eksperimental: hardueri, sistemi dhe versionet e komponentëve kryesorë.",
        rename={"Komponenti": "Komponenti", "Versioni / vlera": "Versioni / vlera"},
        font_size=9.5,
    ),
    p("""Të gjitha modelet trajnohen dhe ekzekutohen në CPU. Kjo është një zgjedhje e
      qëllimshme dhe jo një kufizim i pashmangshëm: modelet e thella të përdorura këtu
      janë të vogla, dhe matja e kostos operacionale mbi CPU është më e afërt me realitetin
      e shumicës së sistemeve të pagesave sesa matja mbi një përshpejtues grafik."""),
]

BLOCKS = _DATA + _PROTOKOLLI + _PRAGU

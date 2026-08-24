"""Kapitulli 4 — METODOLOGJIA."""

from blocks import bullets, eq, fig, h1, h2, h3, note, numbers, p, tab

_DATA = [
    h1("4", "Metodologjia"),
    p("""Ky kapitull përshkruan dataset-in, protokollin e vlerësimit, paraprocesimin, modelet,
      procedurën e përcaktimit të pragut, metrikat, studimet e thelluara për secilin algoritëm
      dhe arkitekturën e implementuar. Përshkrimi është i hollësishëm me qëllim: pjesa më e
      madhe e dallimeve mes rezultateve të publikuara mbi këtë dataset nuk vjen nga algoritmet,
      por nga zgjedhje metodologjike që shpesh nuk raportohen."""),
    h2("4.1", "Dataset-i"),
    h3("4.1.1", "Origjina dhe struktura"),
    p("""Studimi përdor dataset-in publik Credit Card Fraud Detection të grupit Machine Learning
      të Université Libre de Bruxelles [@ulb_dataset]. Ai përmban transaksione reale me karta
      krediti të kryera nga mbajtës evropianë gjatë dy ditëve të shtatorit 2013. Struktura
      është e thjeshtë: një kolonë Time me sekondat e kaluara nga transaksioni i parë, njëzet e
      tetë kolona V1 deri V28 që janë komponentë kryesorë të dala nga një transformim PCA i
      aplikuar nga publikuesit për arsye konfidencialiteti, kolona Amount me vlerën e
      transaksionit, dhe kolona Class me etiketën binare."""),
    tab(
        "eda_overview",
        "Karakteristikat kryesore të dataset-it ULB Credit Card Fraud.",
        rename={"treguesi": "Treguesi", "vlera": "Vlera"},
        font_size=10,
    ),
    p("""Anonimizimi me PCA ka dy pasoja që përshkojnë gjithë punimin. E para është se
      interpretimi semantik i veçorive është i pamundur, sepse komponentët nuk kanë emra dhe
      nuk mund të thuhet cila sjellje e transaksionit e ngre pikën e anomalisë. E dyta, më pak
      e diskutuar, është se një detektor linear rindërtimi bazuar në PCA nuk është thjesht një
      baseline e dobët, por pragu natyror i familjes së rindërtimit; prandaj ai përfshihet
      shprehimisht si ablacion i Autoencoder-it."""),
    h3("4.1.2", "Analiza eksploruese"),
    p("""Analiza eksploruese nxori disa fakte që ndikojnë drejtpërdrejt në interpretimin e
      rezultateve. Vëllimi i transaksioneve ndjek një cikël të qartë ditë-natë, ndërsa shfaqja
      e mashtrimeve nuk e ndjek atë cikël. Kjo do të thotë se norma e mashtrimit për orë
      ndryshon shumë, dhe blloqe testimi me numër të barabartë rreshtash mbulojnë intervale
      kohore shumë të ndryshme."""),
    fig(
        "eda_volume_and_fraud",
        "Vëllimi i transaksioneve për orë (lart) dhe numri i mashtrimeve për orë (poshtë). "
        "Mashtrimet nuk e ndjekin ciklin ditor të vëllimit, dhe grupimet e tyre janë të "
        "dukshme rreth orëve me trafik të ulët.",
        15.0,
    ),
    p("""Norma e mashtrimit sipas orës së ditës e bën këtë edhe më të qartë: në orën dy të
      mëngjesit ajo arrin rreth 1.7 për qind, pra afërsisht dhjetë herë mbi mesataren globale.
      Ky është sinjal i fortë, por i papërdorshëm në këtë punim si veçori modeli, sepse koha
      përdoret për renditjen e rrjedhës dhe për përcaktimin e ndarjes; futja e saj si hyrje do
      të ndërthurte variablin e ndarjes me hyrjen e modelit. Kjo zgjedhje diskutohet përsëri në
      kufizime."""),
    fig(
        "eda_hourly_rate",
        "Norma e mashtrimit sipas orës së ditës, e grumbulluar mbi të dy ditët. Vija e "
        "ndërprerë tregon mesataren globale prej 0.173 për qind.",
        14.0,
    ),
    p("""Shpërndarja e shumave sjell një gjetje kundërintuitive. Mesatarja e shumës së
      mashtrimeve është më e lartë se ajo e transaksioneve legjitime, por mediana është dukshëm
      më e ulët, 9.25 euro kundrejt 22 eurove. Kjo do të thotë se shpërndarja e mashtrimeve
      është fort e zhdrejtë: shumica janë transaksione shumë të vogla, ndërsa një pakicë janë
      shumë të mëdha. Njëzet e shtatë mashtrime kanë shumë saktësisht zero, gjë që përputhet me
      modelin e njohur të testimit të kartave, ku sulmuesi verifikon vlefshmërinë e një karte
      me një autorizim pa vlerë përpara përdorimit real."""),
    fig(
        "eda_amounts",
        "Shpërndarja e shumave për të dyja klasat në shkallë logaritmike (majtas) dhe krahasimi "
        "i kuartileve (djathtas). Mashtrimet përqendrohen te shumat e vogla, me një bisht të "
        "gjatë drejt vlerave të larta.",
        15.0,
    ),
    p("""Matrica e korrelacionit konfirmon prejardhjen e deklaruar të të dhënave. Korrelacioni
      mesatar absolut jashtë diagonales është 0.008, praktikisht zero, siç pritet nga komponentë
      kryesorë ortogonalë. Korrelacionet e vetme të konsiderueshme përfshijnë kolonën Amount, e
      cila nuk ka qenë pjesë e transformimit PCA, ku vlera më e lartë është 0.531 mes Amount dhe
      V2. Ky është kontroll i thjeshtë por i dobishëm i integritetit të të dhënave."""),
    fig(
        "eda_correlation",
        "Matrica e korrelacionit të Pearson-it mes 29 veçorive hyrëse. Ortogonaliteti i "
        "komponentëve V1 deri V28 është i dukshëm, dhe korrelacionet e vetme jotriviale "
        "përfshijnë kolonën Amount.",
        12.0,
    ),
    h3("4.1.3", "Karakterizimi gjeometrik para modelimit"),
    p("""Të gjitha metodat unsupervised të këtij studimi mbështeten në supozimin se klasa
      pozitive qëndron gjeometrikisht larg asaj negative. Ky supozim është i testueshëm pa
      përshtatur asnjë model, dhe testimi i tij paraprak jep një kufi të sipërm të pavarur nga
      algoritmi. Prandaj para çdo modelimi matet dimensioni i brendshëm i klasës normale me dy
      vlerësues të pavarur, distanca e secilit transaksion deri te fqinjët e tij legjitimë më të
      afërt, dhe cilësia e zbulimit që arrin një detektor i ndërtuar vetëm mbi atë distancë."""),
    p("""Dimensioni i brendshëm vlerësohet me metodën e gjasës maksimale të Levina-Bickel dhe me
      vlerësuesin TwoNN, i cili përdor vetëm dy fqinjët më të afërt dhe është prandaj shumë më
      pak i ndjeshëm ndaj lakimit dhe ndaj variacionit të densitetit. Të dy vlerësuesit
      llogariten mbi dritaren e trajnimit, dhe të njëjtat masa përsëriten mbi dritaren e testimit
      për të dhënë një pamje pa model të zhvendosjes."""),
    p("""Masa vendimtare është një detektor pa parametra: pika e anomalisë është distanca
      mesatare deri te dhjetë fqinjët legjitimë më të afërt. Meqë ky detektor nuk mëson asgjë,
      cilësia e tij përcakton se çfarë arrihet me gjeometri të pastër, dhe çdo detektor i
      trajnuar duhet lexuar përballë saj. Për ta bërë numrin të interpretueshëm në terma
      operacionalë, raportohet edhe pozicioni i secilit mashtrim në renditjen e plotë, pra sa
      alarme duhen shqyrtuar përpara se ai të arrihet."""),
    h3("4.1.4", "Kufizimet e dataset-it"),
    p("""Tri kufizime duhen deklaruar përpara se të interpretohet çdo rezultat."""),
    bullets(
        [
            "Mungesa e identifikuesit të kartës. Pa të, agregimi për llogari mbi dritare kohore, "
            "teknikë që literatura e aplikuar e raporton si më efektiven [@whitrow2009], "
            "[@bahnsen2016], është i pamundur, si dhe modelimi sekuencial për mbajtës "
            "[@jurgovsky2018]. Rezultatet duhen lexuar si të vlefshme për zbulim pikësor pa "
            "kontekst llogarie.",
            "Kohëzgjatja prej vetëm dyzet e tetë orësh. Kjo lejon vlerësimin e zhvendosjes "
            "brenda-ditore dhe mes dy ditëve, por jo të zhvendosjes sezonale ose afatgjatë.",
            "Etiketat konsiderohen të plota dhe të sakta. Në realitet një pjesë e mashtrimeve nuk "
            "kontestohet kurrë dhe mbetet e etiketuar gabimisht si legjitime, gjë që i bën "
            "vlerësimet e precision-it pesimiste.",
        ]
    ),
]

_PROTOKOLLI = [
    h2("4.2", "Protokolli i vlerësimit"),
    h3("4.2.1", "Ndarja kronologjike dhe disiplina kundër rrjedhjes"),
    p("""Të dhënat renditen sipas kolonës Time me renditje të qëndrueshme, që do të thotë se
      rreshtat me të njëjtën vlerë kohe ruajnë rendin origjinal të skedarit dhe ndarja është
      plotësisht deterministe. Ndarja bëhet sipas rendit kohor dhe kurrë me përzierje. Modelet
      unsupervised trajnohen vetëm mbi transaksionet normale të dritares së trajnimit, ndërsa
      skaluesi përshtatet vetëm mbi dritaren e trajnimit dhe pastaj aplikohet mbi bllokun e
      testimit."""),
    p("""Kolona Time nuk përdoret si veçori hyrëse. Vektori i veçorive përbëhet nga V1 deri V28
      dhe Amount, gjithsej njëzet e nëntë dimensione. Kjo zgjedhje është e domosdoshme
      teknikisht: meqë Time përcakton ndarjen, në një ndarje kronologjike vlerat e saj në
      bllokun e testimit janë sistematikisht jashtë intervalit të parë gjatë trajnimit, dhe pas
      skalimit çdo pikë testimi do të merrte një vlerë ekstreme në atë dimension. Kjo do të
      prishte renditjen e çdo detektori të bazuar në distancë ose densitet, pa prekur fare një
      model të mbikëqyrur linear."""),
    note("""Ky nuk është rrezik teorik. Mungesa e kolonës Time mes veçorive verifikohet me test
      automatik pikërisht sepse ky mekanizëm do të prodhonte një model degradimi që duket
      identik me atë që vëzhgohet, por për arsye krejt të gabuar."""),
    h3("4.2.2", "Protokolli rolling-origin"),
    p("""Një ndarje e vetme 70/30 jep një vlerësim të performancës në një moment të vetëm
      hipotetik vendosjeje. Me 492 pozitivë në të gjithë dataset-in ky vlerësim është i
      zhurmshëm, dhe nga një ndarje e vetme nuk mund të dallohet nëse renditja e algoritmeve
      është e qëndrueshme apo artefakt i pikës së prerjes. Prandaj vlerësimi përsëritet në tetë
      pika të njëpasnjëshme prerjeje me dritare trajnimi që zgjerohet, sipas skemës
      rolling-origin të konsoliduar në literaturën e parashikimit [@tashman2000],
      [@bergmeir2012] dhe të vlerësimit prekuencial [@gama2013]."""),
    eq("Fold i:  trajnim [0, c_i),   testim [c_i, c_{i+1})"),
    p("""Pikat e prerjes c_i ndajnë pjesën e rrjedhës pas 40 për qindëshit fillestar në tetë
      blloqe të barabarta sipas numrit të rreshtave. Çdo fold rindërton nga fillimi të gjithë
      zinxhirin: skaluesin e vet, modelet e veta dhe pragjet e veta. Asgjë nuk transferohet nga
      një fold në tjetrin, prandaj asnjë informacion nga një bllok i mëvonshëm nuk mund të
      rrjedhë prapa."""),
    fig(
        "diagram_protocol",
        "Gjeometria e protokollit rolling-origin. Dritarja e trajnimit zgjerohet me çdo fold, "
        "ndërsa blloqet e testimit e mbulojnë rrjedhën pa mbivendosje. Numri i mashtrimeve për "
        "bllok varion nga 13 në 88.",
        15.0,
    ),
    p("""Numri i fold-eve nuk është zgjedhur si numër i rrumbullakët. Ai është rezultat i një
      kompromisi mes dy kufizimeve që tërheqin në drejtime të kundërta. Nga njëra anë, testi i
      çiftuar i Wilcoxon-it me N fold-e mund të prodhojë p-vlerë dy-bishtore jo më të vogël se
      2/2^N; me gjashtë fold-e kjo është 0.031 dhe nuk mbijeton korrigjimin e Holm-it për
      krahasime të shumëfishta, sado i qëndrueshëm të jetë rezultati. Nga ana tjetër, me shumë
      fold-e blloqet e testimit zvogëlohen derisa disa prej tyre të mbajnë më pak se dhjetë
      pozitivë dhe AP-ja e tyre bëhet zhurmë. Me tetë fold-e çdo bllok mban të paktën
      trembëdhjetë pozitivë dhe p-vlera më e vogël e arritshme është 0.0078, e cila mbijeton
      korrigjimin për deri në gjashtë krahasime të paradeklaruara."""),
    tab(
        "fold_summary",
        "Struktura e tetë fold-eve: madhësia e dritares së trajnimit dhe e bllokut të testimit, "
        "numri i mashtrimeve dhe intervali kohor i mbuluar.",
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
    p("""Tabela zbulon një veti të rëndësishme të të dhënave: blloqet me numër të barabartë
      rreshtash mbulojnë intervale kohore shumë të ndryshme, sepse dendësia e transaksioneve
      ndryshon me orën. Fold-i 1 shquhet me 88 mashtrime, afërsisht katër herë mbi mesataren e
      blloqeve të tjera, sepse përfshin një grumbullim mashtrimesh që rezulton vendimtar për të
      kuptuar variancën e lartë të rezultateve."""),
    h2("4.3", "Paraprocesimi si variabël eksperimentale"),
    p("""Çdo detektor i bazuar në distancë, densitet ose rindërtim e trashëgon nocionin e
      largësisë nga paraprocesimi që zbatohet përpara tij. Në shumicën e studimeve skaluesi
      zgjidhet një herë dhe nuk rishikohet, gjë që e fsheh një burim variacioni potencialisht
      më të madh se vetë zgjedhja e algoritmit. Ky punim e trajton atë si variabël
      eksperimentale me të drejta të plota."""),
    p("""Një hollësi e protokollit meriton të thuhet shprehimisht. Skaluesi përshtatet mbi të
      gjithë dritaren e trajnimit, mashtrimet përfshirë, dhe jo mbi normalet e njohura. Në
      momentin e vendosjes etiketat e dritares aktuale nuk ekzistojnë, prandaj një skalues i
      përshtatur mbi të dhëna të pastra do të ishte një përparësi që sistemi real nuk e ka. Kjo
      zgjedhje ka një pasojë që duhet testuar e jo supozuar: statistikat e përshtatura i
      thithin vetë vlerat ekstreme që duhen nxjerrë në pah."""),
    p("""Krahasohen shtatë opsione: StandardScaler, RobustScaler me interval ndërkuartilor, dy
      variante të transformimit kuantil me dalje normale dhe uniforme, PowerTransformer me
      metodën Yeo-Johnson, MinMaxScaler, dhe mungesa e plotë e skalimit. E fundit nuk është
      lëshim, sepse komponentët V janë tashmë të qendërzuar dhe lënia e tyre e paprekur është
      baseline legjitime. Çdo kombinim paraprocesim-detektor ekzekutohet mbi të tetë fold-et, që
      krahasimi të mbartë të njëjtën pasiguri si rezultatet kryesore."""),
    h2("4.4", "Modelet"),
    h3("4.4.1", "Ndërfaqja e përbashkët"),
    p("""Të gjithë detektorët implementojnë të njëjtën ndërfaqe me katër metoda: fit, score, save
      dhe load. Konventa e shenjës është uniforme dhe e detyrueshme, pra vlera më e lartë e
      pikës do të thotë gjithmonë më anormale. Kjo konventë verifikohet me test automatik mbi
      të dhëna reale për secilin model, duke krahasuar medianën e pikëve të mashtrimeve me atë
      të transaksioneve legjitime. Uniformiteti nuk është thjesht higjienë kodi: ai lejon që
      harnesi i vlerësimit, ansamblet dhe konsumatori i rrjedhës të mbeten krejtësisht të
      pavarur nga identiteti i modelit."""),
    tab(
        "model_zoo",
        "Detektorët e krahasuar, mekanizmi i tyre i pikëzimit, kostoja asimptotike e trajnimit "
        "dhe hiperparametrat e parazgjedhur. Simbolet: n mostra, d dimensione, t pemë, ψ "
        "madhësia e nën-mostrës, e epoka, h njësi të fshehura, i iteracione.",
        font_size=7.5,
    ),
    h3("4.4.2", "Isolation Forest"),
    p("""Implementimi ndjek formulimin origjinal [@liu2008], me pikën e marrë me shenjë të
      kundërt për të respektuar konventën e studimit. Përveç dy hiperparametrave standardë,
      numrit të pemëve dhe madhësisë së nën-mostrës, ekspozohet edhe fraksioni i kolonave që
      secila pemë mund të përdorë. Ky i fundit nuk është pjesë e konfigurimit të parazgjedhur,
      por është ndërhyrja më e lirë e disponueshme nëse dobësia e algoritmit qëndron te
      shpërndarja e ndarjeve, dhe prandaj studiohet shprehimisht."""),
    p("""Studimi i thelluar për këtë detektor përfshin katër komponentë: sipërfaqen e plotë mbi
      numrin e pemëve dhe madhësinë e nën-mostrës, ndjeshmërinë ndaj fraksionit të kolonave,
      hapjen e pemëve të përshtatura për të numëruar sa ndarje merr secila kolonë, dhe një
      ripërshtatje mbi një kopje të rrotulluar rastësisht të hapësirës. Ky i fundit është test i
      drejtpërdrejtë i hipotezës se përputhja e boshteve me komponentët kryesorë ka rëndësi,
      sepse një rrotullim ortogonale nuk ndryshon asnjë distancë por e shkatërron atë
      përputhje."""),
    h3("4.4.3", "Autoencoder"),
    p("""Autoencoder-i është një rrjet me enkoder dhe dekoder simetrikë, i trajnuar vetëm mbi
      transaksionet normale të dritares së trajnimit, me gabimin mesatar kuadratik të rindërtimit
      si pikë anomalie. Implementimi ekspozon shtatë leva që studimi i thelluar i varion një nga
      një: dimensionin latent, gjerësinë e shtresës së fshehur, thellësinë e enkoderit,
      funksionin e humbjes, weight decay, dropout dhe nivelin e zhurmës për variantin
      denoising."""),
    note("""Një konventë e rëndësishme për interpretimin e ablacioneve: funksioni i humbjes gjatë
      trajnimit mund të jetë kuadratik, absolut ose i Huber-it, por pika e anomalisë është
      gjithmonë gabimi mesatar kuadratik. Pikëzimi me të njëjtin funksion që u trajnua do të
      ndryshonte njëkohësisht edhe modelin edhe funksionin renditës, dhe dy efektet nuk do të
      mund të ndaheshin."""),
    p("""Thellësia e enkoderit ndryshohet me ngushtim gjeometrik nga gjerësia e shtresës së parë
      drejt dimensionit latent, që një rritje e thellësisë të ndryshojë vetëm mënyrën si arrihet
      ngjeshja dhe jo sasinë e saj. Konstruktori refuzon konfigurimet ku dimensioni latent nuk
      është më i vogël se gjerësia e fshehur, sepse një ngushtim që nuk ngushton është
      arkitekturë tjetër dhe jo një enkoder më i thellë."""),
    p("""Gjatë trajnimit regjistrohet humbja mesatare për epokë. Kjo lejon që kurba e trajnimit
      të vendoset përballë cilësisë së zbulimit të matur në blloqet e testimit, dhe pikërisht ai
      krahasim dallon një model të pastërvitur nga një model që ka filluar t'i rindërtojë mirë
      edhe anomalitë."""),
    h3("4.4.4", "One-Class SVM"),
    p("""One-Class SVM-ja me kernel RBF ka kosto trajnimi të paktën kuadratike, çka e bën të
      papërdorshëm mbi njëqind e tetëdhjetë mijë rreshta. Konfigurimi i parazgjedhur e trajnon
      mbi një nën-mostër të rastësishme me seed të fiksuar prej njëzet mijë transaksionesh
      normale. Ky është kompromisi i vetëm në gjithë studimin që imponohet nga kostoja
      llogaritëse dhe jo nga një zgjedhje parimore, prandaj ai nuk mbetet i deklaruar por
      matet: studimi i thelluar ndërton kurbën e të mësuarit deri në tetëdhjetë mijë
      transaksione dhe raporton sa njësi Average Precision kushton kufizimi."""),
    p("""Studimi mat gjithashtu numrin e vektorëve mbështetës të ruajtur, sepse ai është madhësia
      që përcakton koston e inferencës: çdo transaksion i pikëzuar krahasohet me të gjithë ata.
      Kështu i njëjti hiperparametër ν që rregullon ashpërsinë e kufirit rregullon edhe vonesën,
      dhe të dyja raportohen bashkë."""),
    h3("4.4.5", "Referenca e mbikëqyrur"),
    p("""Projekt-propozimi kërkonte njëkohësisht trajnim vetëm mbi transaksione normale dhe një
      baseline me Regresion Logjistik. Këto dy kërkesa janë në kundërshtim, sepse regresioni
      logjistik ka nevojë për etiketa. Zgjidhja e zbatuar këtu e bën kundërshtinë të dukshme në
      vend që ta fshehë: modeli trajnohet mbi të gjithë dritaren e trajnimit me etiketat e saj,
      përfshirë mashtrimet që ndodhen natyrshëm aty, dhe raportohet gjithmonë si referencë e
      mbikëqyrur, jo si konkurrent i barabartë. Ai i përgjigjet pyetjes se çfarë do të arrihej
      nëse etiketat historike do të përdoreshin, dhe shërben si kufi i sipërm i arritshëm."""),
    h3("4.4.6", "Ablacioni linear"),
    p("""Një detektor i pestë regjistrohet në kod por nuk hyn kurrë në krahasimin kryesor. Ai
      llogarit gabimin e rindërtimit nga një nënhapësirë lineare PCA me rang të caktuar. Roli i
      tij është i vetëm: meqë veçoritë hyrëse janë vetë komponentë kryesorë, ky detektor është
      pragu natyror i familjes së rindërtimit, dhe diferenca mes tij dhe Autoencoder-it në të
      njëjtin rang latent është saktësisht ajo që paguan jolineariteti."""),
]

_PRAGU = [
    h2("4.5", "Përcaktimi i pragut"),
    p("""Një funksion pikëzimi bëhet detektor vetëm pasi i shtohet një prag. Zgjedhja e pragut
      është pikërisht vendi ku rrjedhja e informacionit hyn më lehtë dhe vërehet më vështirë,
      prandaj këtu përdoren tri procedura krejt të ndara."""),
    h3("4.5.1", "Pragu nga percentili i trajnimit"),
    p("""Protokolli parësor e nxjerr pragun nga percentili (1 − c) i shpërndarjes së pikëve mbi
      dritaren e trajnimit:"""),
    eq("τ = Kuantili_{1−c} { s(x) : x ∈ D_trajnim }"),
    p("""ku c është hiperparametri i kontaminimit. Në mungesë të një vlere të caktuar, c merret i
      barabartë me normën e mashtrimit të vëzhguar në dritaren e trajnimit. Kjo përdor etiketa
      vetëm nga e kaluara, pra të njëjtin supozim disponueshmërie që i është dhënë tashmë
      referencës së mbikëqyrur, dhe deklarohet shprehimisht. Për të siguruar që asnjë përfundim
      të mos varet nga kjo zgjedhje, kontaminimi skanohet në një interval prej dy urdhrash
      madhësie."""),
    h3("4.5.2", "Pragu orakull"),
    p("""Për krahasim raportohet edhe pragu që maksimizon F1-shin mbi bashkësinë e testimit. Ky
      prag është i paarritshëm në praktikë, sepse kërkon etiketat e testit. Ai paraqitet
      gjithmonë në kolonë të veçantë dhe emërtohet si kufi i sipërm, dhe të dy numrat nuk
      përzihen kurrë në të njëjtën kolonë. Diferenca mes tyre është masë e dobishme e asaj se sa
      humbet një sistem real që nuk mund ta zgjedhë pragun me etiketa."""),
    h3("4.5.3", "Pragu adaptiv me dritare rrëshqitëse"),
    p("""Një prag i fiksuar në kohën e trajnimit fikson një pikë, jo një ngarkesë pune. Nëse
      shpërndarja e pikëve zhvendoset, numri i alarmeve zhvendoset me të. Kjo është mënyrë
      dështimi e pavarur nga cilësia e zbulimit: një ekip i dimensionuar për njëqind alarme në
      bllok nuk mund të përballojë shtatëqind, dhe alarmet që nuk hapen kurrë nuk kanë vlerë
      sado mirë të renditura të jenë."""),
    p("""Prandaj propozohet dhe testohet një alternativë: pragu llogaritet si percentili (1 − c)
      i pikëve më të fundit brenda një dritareje rrëshqitëse, i rifreskuar çdo disa qindra
      mesazhe për ta mbajtur koston të kufizuar. Vendimi për një mesazh përdor vetëm mesazhet
      që kanë mbërritur para tij, pra mesazhi që gjykohet nuk hyn kurrë në dritaren që e
      gjykon, gjë që e bën procedurën shkakësore dhe të zbatueshme në një rrjedhë reale."""),
    h2("4.6", "Metrikat"),
    h3("4.6.1", "Metrikat e cilësisë së renditjes"),
    p("""Metrika kryesore është Average Precision, e cila përmbledh kurbën precision-recall si
      shumë e ponderuar e precision-it në çdo prag:"""),
    eq("AP = Σ_n (R_n − R_{n−1}) · P_n"),
    p("""Arsyeja e zgjedhjes është e dokumentuar mirë: në çekuilibër ekstrem kurba
      precision-recall jep një pamje shumë më informative se ROC, sepse norma e pozitivëve të
      rremë mbetet e vogël edhe kur alarmet e rreme janë shumëfish më të shumta se ato të
      vërteta [@davis2006], [@saito2015]. AUC-ROC raportohet gjithashtu, por vetëm për
      krahasueshmëri me literaturën, dhe rezultatet e Kapitullit 5 e tregojnë qartë pse ai nuk
      duhet të jetë metrika vendimtare. Precision, recall dhe F1 raportohen në pragun e nxjerrë
      nga trajnimi dhe, veçmas, në pragun orakull. Për çdo metrikë raportohet edhe shpërhapja
      nëpër fold-e, sepse një vlerë e vetme pa masën e pasigurisë së saj është e vështirë të
      interpretohet; aty ku nevojitet një interval besimi mbi një bashkësi të vetme testimi, ai
      nxirret me riparashtrim bootstrap [@efron1993]."""),
    h3("4.6.2", "Metrikat operacionale"),
    p("""Asnjë ekip hetimi nuk shqyrton një renditje të plotë, por aq alarme sa i lejon
      kapaciteti. Prandaj raportohen edhe precision dhe recall në buxhet fiks alarmesh k, si dhe
      recall i vlerës monetare, pra pjesa e eurove mashtruese të kapura brenda buxhetit, sepse
      një mashtrim i humbur prej dy eurosh dhe një prej dy mijë eurosh nuk janë i njëjti
      gabim."""),
    p("""Kursimet neto llogariten sipas një modeli kostoje të thjeshtë dhe të deklaruar: një
      mashtrim i kapur kursen shumën e tij, ndërsa çdo alarm i ngritur, i vërtetë apo i rremë,
      kushton një hetim:"""),
    eq("Kursimi(k) = Σ_{i∈TP(k)} shuma_i − c_het · |Alarme(k)|"),
    p("""Normalizimi bëhet ndaj detektorit të përsosur, i cili kap çdo mashtrim duke ngritur
      saktësisht aq alarme sa ka mashtrime. Kostoja e hetimit vendoset në tre euro, dhe
      ndjeshmëria ndaj kësaj zgjedhjeje diskutohet në Kapitullin 6."""),
    h3("4.6.3", "Metrikat e kostos llogaritëse"),
    p("""Për secilin model matet koha e trajnimit, koha e pikëzimit për transaksion dhe gjurma e
      memories gjatë trajnimit. Gjurma matet si diferencë mes pikut të memories rezidente gjatë
      bllokut dhe vlerës në hyrje të tij, jo si piku absolut i procesit, sepse ky i fundit
      përfshin të dhënat e ngarkuara paraprakisht dhe do të ishte pothuajse i njëjtë për të
      gjithë modelet."""),
    h2("4.7", "Përzgjedhja e hiperparametrave"),
    p("""Krahasimi mes modeleve të akorduara keq nuk ka vlerë, ndërsa akordimi mbi bashkësinë e
      testimit e shkatërron vlefshmërinë e tij. Prandaj përdoren dy rrugë të pavarura, dhe të
      dyja raportohen."""),
    p("""Rruga e parë është validimi i brendshëm kohor. Dritarja e trajnimit ndahet përsëri sipas
      kohës, kandidatët përshtaten mbi 75 për qindëshin e parë dhe renditen sipas Average
      Precision në 25 për qindëshin e fundit. Kërkimi kryhet me Optuna duke përdorur mostruesin
      TPE [@akiba2019]; edhe një kërkim thjesht i rastësishëm do të ishte alternativë e
      arsyeshme, sepse mbi hapësira me pak dimensione efektive ai është konkurrues me kërkimin
      sistematik në rrjetë [@bergstra2012]. Kandidatët përshtaten mbi një nën-mostër me seed të
      fiksuar, që kërkimi të përfundojë në minuta e jo në orë, dhe konfigurimi fitues
      ripërshtatet pastaj mbi dritaren e plotë."""),
    p("""Rruga e dytë nuk përdor fare etiketa. Kriteret Excess-Mass dhe Mass-Volume vlerësojnë sa
      mirë grupet e nivelit të një funksioni pikëzimi e përqendrojnë masën probabilitare në
      vëllim të vogël [@goix2015], [@goix2016]:"""),
    eq("EM(t) = sup_u [ P(s≥u) − t·Leb(s≥u) ];   MV(α) = Leb(s≥u_α)"),
    p("""Vlerësimi i masës Lebesgue me Monte Carlo është i pamundur në njëzet e nëntë dimensione,
      prandaj ndiqet zgjidhja e rekomanduar: kriteret mesatarizohen mbi nënhapësira të
      rastësishme me dimension të ulët, ku detektori ripërshtatet në secilën nënhapësirë. Një
      hollësi implementimi rezultoi vendimtare. Këto kritere përcaktohen për një funksion
      normaliteti, ku grupet e sipërme të nivelit janë rajonet e dendura; me konventën e kundërt
      të këtij projekti pikat uniforme mbushin çdo grup niveli dhe vëllimi i vlerësuar kolapson
      në të gjithë kutinë kufizuese, prandaj shenja kthehet brenda funksionit. Po ashtu, rrjeta
      e pragjeve duhet të përfshijë grupin bosh të nivelit, përndryshe supremumi mund të dalë
      negativ dhe kriteri nuk është më masë e vlefshme."""),
    p("""Këto kritere nuk përdoren për akordimin kryesor, sepse kostoja e tyre, një ripërshtatje
      e detektorit për çdo nënhapësirë, do ta bënte një kërkim të plotë të papërballueshëm. Ato
      përdoren në një krahasim të fokusuar mbi rrjeta të vogla dhe të deklaruara, me një pyetje
      të vetme: a do ta zgjidhnin ato të njëjtin konfigurim si kriteri me etiketa."""),
    h2("4.8", "Studimet e thelluara për algoritëm"),
    p("""Përveç krahasimit kryesor, secili nga tri algoritmet i nënshtrohet një studimi të
      veçantë, i dizajnuar rreth mekanizmit të tij dhe jo si skanim gjenerik hiperparametrash.
      Të gjitha ekzekutohen mbi të tetë fold-et, që rezultatet e tyre të mbartin të njëjtën
      pasiguri si tabela kryesore."""),
    numbers(
        [
            "Isolation Forest: sipërfaqja mbi numrin e pemëve dhe madhësinë e nën-mostrës, "
            "ndjeshmëria ndaj fraksionit të kolonave, numërimi i ndarjeve për kolonë brenda pemëve "
            "të përshtatura, dhe ripërshtatja mbi një hapësirë të rrotulluar rastësisht.",
            "Autoencoder: sipërfaqja mbi dimensionin latent dhe gjerësinë e fshehur, thellësia e "
            "enkoderit, funksioni i humbjes, tri regullarizues të ndryshëm, kurba e trajnimit "
            "përballë cilësisë së zbulimit, dhe krahasimi me projeksionin linear në rang të "
            "njëjtë.",
            "One-Class SVM: krahasimi i kernelëve, sipërfaqja mbi nu dhe gamma, dhe kurba e të "
            "mësuarit mbi madhësinë e nën-mostrës së trajnimit bashkë me koston përkatëse.",
            "Të tre bashkë: ndjeshmëria ndaj paraprocesimit, ndikimi i kufizimit të hyrjes te "
            "komponentët informativë, ndikimi i politikës së dritares së trajnimit, dhe analiza e "
            "gabimeve në nivel transaksioni.",
        ]
    ),
    p("""Studimet e mësipërme e ndryshojnë nga një levë në një kohë, që efekti i secilës të jetë
      i izoluar. Kjo lë hapur pyetjen nëse levat kombinohen. Prandaj shtohet një studim i fundit
      me dizajn faktorial dy-nga-dy, ku secili detektor vlerësohet nën katër kombinime:
      paraprocesim i parazgjedhur ose më i miri i tij, dhe hiperparametra të parazgjedhur ose më
      të mirët e tij. Ky dizajn e ndan përfitimin total në tri pjesë, kontributin e
      paraprocesimit, atë të hiperparametrave dhe ndërveprimin mes tyre, dhe e tregon nëse
      renditja e algoritmeve ndryshon kur secili vlerësohet në kapacitetin e vet më të mirë.
      Konfigurimet fituese merren nga studimet e mësipërme dhe jo nga blloqet e testimit, prandaj
      ky rezultat raportohet si kufi i sipërm optimist dhe jo si vlerësim i paanshëm."""),
    p("""Studimi mbi kufizimin e hyrjes meriton koment të veçantë, sepse nuk është skanim por
      ndërhyrje. Analiza e interpretueshmërisë prodhon një pohim mekanicist mbi shkakun e
      renditjes; ai pohim mbetet korrelacion derisa të ndërhyhet mbi shkakun e supozuar. Duke i
      dhënë secilit detektor vetëm k komponentët më informativë dhe duke matur se cili fiton më
      shumë, korrelacioni shndërrohet në provë kauzale."""),
]

_ARKITEKTURA = [
    h2("4.9", "Arkitektura e implementuar"),
    p("""Sistemi ndjek arkitekturën pesështresore të përcaktuar në projekt-propozim. Ndarja mes
      shtresave nuk është vetëm konceptuale: secila është modul i veçantë me ndërfaqe të qartë,
      gjë që lejoi zëvendësimin e modeleve pa prekur shtresën e rrjedhës dhe anasjelltas."""),
    fig(
        "diagram_architecture",
        "Arkitektura pesështresore e sistemit dhe ajo që kalon nëpër çdo kufi mes shtresave.",
        14.5,
    ),
    h3("4.9.1", "Shtresa e rrjedhës"),
    p("""Apache Kafka ekzekutohet në modalitetin KRaft, pa ZooKeeper, me një broker të vetëm dhe
      një particion për topic. Zgjedhja e Kafka-s në vend të alternativave si Redpanda u bë
      sepse titulli dhe propozimi i temës e emërtojnë shprehimisht atë, dhe sepse një shërbim
      KRaft me një nyje kushton pak më shumë se alternativat në konfigurim [@kreps2011].
      Serializimi bëhet me JSON: në ritmet e testuara kostoja e kodimit është e papërfillshme,
      ndërsa lexueshmëria e mesazheve e bën pipeline-in të diagnostikueshëm dhe lejon krahasim
      bit-për-bit të pikëve mes dy regjimeve."""),
    p("""Producer-i riprodhon bllokun e testimit me ritëm konstant të konfigurueshëm, duke
      përdorur një orar absolut për të shmangur grumbullimin e devijimit të ritmit. Consumer-i
      mbledh mikro-grupe deri në gjashtëdhjetë e katër mesazhe dhe i pikëzon si një matricë të
      vetme, me kohëzgjatje pritjeje të kufizuar në pesëdhjetë milisekonda."""),
    note("""Kufizimi i kësaj pritjeje nuk ishte planifikuar. Në ekzekutimin e parë vonesa
      end-to-end dilte më e ulët në ritme të larta sesa në ritme të ulëta, gjë që nuk ka kuptim
      fizik; shkaku ishte se në ritme të ulëta vetë mbledhja e mikro-grupit dominonte vonesën.
      Ky është shembull i dobishëm se si një defekt matjeje mund të prodhojë një rezultat që
      duket i publikueshëm."""),
    h3("4.9.2", "Matja e vonesës"),
    p("""Çdo mesazh mbart një vulë kohore të prodhimit. Consumer-i regjistron dy madhësi të
      ndara: vonesën e inferencës, që mat vetëm kalimin përpara të modelit dhe amortizohet mbi
      mikro-grupin, dhe vonesën end-to-end, nga vula e producer-it deri pas publikimit të
      alarmit. Producer-i dhe consumer-i ekzekutohen në të njëjtin host, prandaj nuk ka nevojë
      për trajtim të mospërputhjes së orëve. Raportohen shpërndarjet e plota, jo vetëm
      mesatarja, pra p50, p95 dhe p99."""),
    p("""Një hollësi që ndikon në vlefshmërinë e matjes: producer-i nuk niset derisa consumer-i
      të ketë marrë caktimin e particioneve dhe të ketë sinjalizuar gatishmërinë. Pa këtë
      sinkronizim mesazhet e para presin në radhë ndërsa consumer-i po ngrihet, dhe bishti i
      shpërndarjes ndotet me kohën e nisjes në vend se me vonesën e gjendjes së
      qëndrueshme."""),
    h3("4.9.3", "Persistimi dhe vizualizimi"),
    p("""Të gjitha ngjarjet e pikëzuara dhe alarmet ruhen në PostgreSQL në dy tabela të
      indeksuara sipas etiketës së ekzekutimit, me shkrime të grumbulluara. Mbi to është
      ndërtuar një panel Grafana OSS, i konfiguruar tërësisht nga skedarë në depo, pra burimi i
      të dhënave dhe vetë paneli, që gjendja e vizualizimit të mos varet nga veprime manuale në
      ndërfaqe dhe të jetë pjesë e riprodhueshmërisë."""),
    h2("4.10", "Riprodhueshmëria"),
    p("""Çdo eksperiment shkruan një manifest me SHA-në e commit-it, hash-in SHA-256 të
      konfigurimit, versionet e paketave të gjurmuara, vulën kohore dhe përshkrimin e harduerit.
      Seed-et janë të fiksuara në çdo pikë ku ndodh rastësi. Determinizmi u verifikua në mënyrë
      empirike dhe jo vetëm si pretendim: dy cikle të plota e të pavarura ritrajnimi dhe
      vlerësimi prodhuan tabela metrike identike bit-për-bit, me përjashtim të kolonave të kohës
      dhe të memories, të cilat për nga natyra ndryshojnë."""),
    p("""Disiplina metodologjike e përshkruar në këtë kapitull nuk mbetet vetëm në tekst. Ajo
      është e koduar në një grup testesh që ekzekutohen me çdo ndryshim dhe që mbulojnë ndarjen
      kronologjike, mungesën e rrjedhjes së informacionit, kontratën e modeleve, konventën e
      shenjës mbi të dhëna reale, saktësinë e metrikave dhe barazinë e pikëve mes regjimit
      offline dhe atij në rrjedhë."""),
    tab(
        "environment",
        "Mjedisi eksperimental: hardueri, sistemi dhe versionet e komponentëve kryesorë.",
        font_size=9.5,
    ),
    p("""Implementimi mbështetet në një grumbull softuerësh të lirë: scikit-learn për modelet
      klasike dhe metrikat [@pedregosa2011], PyTorch për Autoencoder-in [@paszke2019], NumPy për
      llogaritjen numerike [@harris2020] dhe Matplotlib për figurat [@hunter2007]. Versionet e
      sakta janë pjesë e çdo manifesti ekzekutimi. Të gjitha modelet trajnohen dhe ekzekutohen
      në CPU, gjë që është zgjedhje e qëllimshme dhe jo kufizim i pashmangshëm: modelet janë të
      vogla, dhe matja e kostos operacionale mbi CPU është më e afërt me realitetin e shumicës
      së sistemeve të pagesave sesa matja mbi një përshpejtues grafik."""),
]

BLOCKS = _DATA + _PROTOKOLLI + _PRAGU + _ARKITEKTURA

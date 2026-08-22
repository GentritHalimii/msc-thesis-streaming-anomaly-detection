"""Kapitulli 6 — DISKUTIME DHE PËRFUNDIME."""

from blocks import bullets, h1, h2, h3, note, numbers, p

_SINTEZA = [
    h1("6", "Diskutime dhe përfundime"),
    h2("6.1", "Përmbledhje e gjetjeve"),
    p("""Ky punim ndërtoi dhe vlerësoi një sistem të plotë për zbulimin e anomalive mbi një
      rrjedhë të simuluar transaksionesh financiare, duke integruar Apache Kafka-n me
      katërmbëdhjetë detektorë të pambikëqyrur dhe një referencë të mbikëqyrur. Gjetjet
      kryesore përmblidhen si vijon."""),
    numbers(
        [
            "Sistemi është i realizueshëm operacionalisht me rezervë të gjerë. Vonesa "
            "mesatare fund-më-fund qëndron mes njëzet e tetë dhe tetëdhjetë e pesë "
            "milisekondash në të gjitha konfigurimet e testuara, rreth një rend madhësie nën "
            "objektivin prej një sekonde. Kapaciteti maksimal i qëndrueshëm është rreth dy "
            "mijë e katërqind mesazhe në sekondë me një konsumator të vetëm.",
            "Vonesa dominohet nga transporti dhe nga grumbullimi, jo nga modelet. Për "
            "shumicën e detektorëve inferenca zë nën një përqindje të vonesës totale; "
            "përjashtimi është LOF-i, ku kërkimi i fqinjëve e zgjat bishtin deri në katërqind "
            "e pesëdhjetë milisekonda.",
            "Mes tre algoritmeve të propozimit, Autoenkoderi ofron balancën më të mirë. Kur "
            "fusha zgjerohet në katërmbëdhjetë detektorë, Deep SVDD-ja e tejkalon atë me më "
            "shumë se dyfish në precizion mesatar me kosto pikëzimi praktikisht të njëjtë.",
            "Akordimi i hiperparametrave e përmirëson cilësinë në mënyrë të "
            "qëndrueshme (në të tetë folds-at, p = 0.0078), por e ndryshon "
            "renditjen thelbësisht: korrelacioni i rangjeve para dhe pas "
            "akordimit është 0.17 dhe kryesimi kalon nga Deep SVDD-ja te një "
            "vlerësues i akorduar i Mahalanobis-it. Përgjigjja për pyetjen se "
            "cili algoritëm është më i miri është pra e kushtëzuar nga "
            "protokolli i akordimit.",
            "Isolation Forest-i, një nga dy algoritmet qendrore të propozimit, renditet i "
            "trembëdhjeti nga katërmbëdhjetë. Analiza e atribuimit e shpjegon këtë "
            "mekanikisht dhe jo si rastësi.",
            "Referenca e mbikëqyrur mbetet dukshëm përpara, me precizion mesatar 0.720 "
            "kundrejt 0.449 të metodës më të mirë të pambikëqyrur, duke fituar në të tetë "
            "folds-at.",
            "Qasja ensemble nuk e përmirëson zbulimin në asnjë nga njëmbëdhjetë variantet e "
            "testuara. Përzgjedhja prekuenciale e anëtarëve arrin barazim me modelin më të "
            "mirë individual; kombinimi i verbër është dukshëm më i keq.",
            "Degradimi me kalimin e kohës vjen nga ndryshimi i popullatës së mashtrimeve, jo "
            "nga vjetërsimi i modelit të normalitetit. Indeksi i stabilitetit të popullatës "
            "është 3.22 për mashtrimet kundrejt 0.14 për transaksionet normale.",
            "Pragu adaptiv me dritare rrëshqitëse përmirëson njëkohësisht qëndrueshmërinë e "
            "ngarkesës hetimore dhe cilësinë e zbulimit, me kosto llogaritëse pothuajse zero "
            "për modelet e shpejta.",
        ]
    ),
    h2("6.2", "Interpretimi"),
    h3("6.2.1", "Pse metodat e pambikëqyrura mbeten prapa referencës"),
    p("""Hendeku mes referencës së mbikëqyrur dhe metodave të pambikëqyrura nuk duhet
      interpretuar si dështim i këtyre të fundit, por si kuantifikim i vlerës së
      etiketave në një problem ku klasat mbivendosen. Një detektor i pambikëqyrur mëson
      një model të normalitetit dhe supozon se mashtrimi është ajo që largohet prej tij.
      Ky supozim është pjesërisht i pavërtetë në këtë domen: analiza eksploruese tregoi se
      mediana e shumës së mashtrimeve është më e ulët se ajo e transaksioneve legjitime
      dhe se njëzet e shtatë mashtrime kanë vlerë saktësisht zero. Mashtrimi që imiton
      sjelljen normale nuk është, në kuptimin gjeometrik, një anomali."""),
    p("""Analiza e ndashmërisë e mbështet këtë me numra: detektori pa model bazuar vetëm në
      largësinë nga qendra e transaksioneve normale arrin precizion mesatar 0.10 në
      blloqet e testimit. Ky është praktikisht tavani i asaj që çdo metodë e bazuar në
      largësi mund të arrijë pa informacion shtesë, dhe shpjegon pse detektorët më të mirë
      të pambikëqyrur qëndrojnë në rendin 0.3 deri 0.45 ndërsa modeli i mbikëqyrur, i cili
      mëson një drejtim diskriminues në vend të një modeli normaliteti, arrin 0.72."""),
    h3("6.2.2", "Pse Deep SVDD-ja fiton dhe Isolation Forest-i humbet"),
    p("""Rezultati më i qartë interpretues i punimit është se përputhja e vëmendjes së
      modelit me sinjalin realisht diskriminues parashikon cilësinë e zbulimit. Për tre
      modelet e analizuara, korrelacioni i atribuimit me fuqinë diskriminuese
      njëvariablëshe ishte 0.75 për autoenkoderin, 0.50 për One-Class SVM-në dhe 0.02 për
      Isolation Forest-in — pikërisht renditja e cilësisë së tyre."""),
    p("""Për Isolation Forest-in shkaku është strukturor dhe i parashikueshëm nga vetë
      algoritmi. Ai zgjedh dimensionin e ndarjes në mënyrë uniforme të rastësishme, pa
      asnjë preferencë për informativitetin. Në një hapësirë me njëzet e nëntë dimensione
      ku sinjali diskriminues është i përqendruar në rreth pesë komponentë, afërsisht
      tetëdhjetë e tre për qind e ndarjeve bien mbi dimensione pa vlerë. Kjo dobësi është
      teorike dhe e njohur, por rrallë matet drejtpërdrejt; këtu ajo u mat."""),
    p("""Deep SVDD-ja, përkundrazi, mëson një transformim të mbikëqyrur nga vetë objektivi
      i kompaktësisë: rrjeti është i lirë t'i japë peshë të vogël dimensioneve që nuk
      ndihmojnë në ngjeshjen e të dhënave normale brenda sferës. Ai nuk mëson se cilat
      dimensione dallojnë mashtrimin — nuk ka etiketa — por mëson se cilat dimensione
      strukturojnë normalitetin, dhe në këtë dataset të dyja përkojnë mjaftueshëm."""),
    note("""Një vërejtje me interes praktik: performanca e dobët e Isolation Forest-it në
      këtë studim nuk duhet përgjithësuar në çdo problem. Ajo është pasojë e kombinimit
      dimensionalitet i lartë plus sinjal i përqendruar. Në probleme ku sinjali është i
      shpërndarë mbi shumë veçori, e njëjta rastësi e ndarjeve bëhet përparësi."""),
    h3("6.2.3", "Pse ansamblet nuk ndihmojnë"),
    p("""Teoria e ansambleve për zbulim të jashtëzakonshmërive e thotë qartë se
      mesatarizimi zvogëlon variancën vetëm kur anëtarët gabojnë në mënyra të pavarura
      [@aggarwal2015]. Matja e korrelacionit të rangjeve tregoi se ky kusht nuk plotësohet
      këtu. Shpjegimi më i thellë lidhet me natyrën e vetë veçorive: V1–V28 janë
      komponentë kryesorë tashmë të dekoreluar, prandaj detektorë me mekanizma të
      ndryshëm përfundojnë duke parë të njëjtën strukturë. Diversiteti që literatura e
      ansambleve e siguron zakonisht përmes nën-hapësirave të veçorive ose bagging-ut
      këtu është i parandaluar nga vetë përgatitja e të dhënave."""),
    p("""Ky është një përfundim me vlerë praktike: në një hapësirë tashmë të dekoreluar,
      investimi në një ansambël detektorësh të ndryshëm ka gjasa të japë më pak kthim se
      investimi në një detektor më të mirë të vetëm. Rezultati gjithashtu tregon një
      rrezik konkret: kombinimi i verbër i të gjithë detektorëve në dispozicion, një
      praktikë e zakonshme, e uli precizionin mesatar nga 0.449 në 0.249, pra e përgjysmoi
      cilësinë e zbulimit."""),
    h3("6.2.4", "Pse renditja nuk mbijeton akordimin"),
    p("""Gjetja se akordimi e ndryshon renditjen pothuajse plotësisht meriton interpretim,
      sepse në pamje të parë duket se bie ndesh me gjetjen tjetër, atë se protokolli i
      ndarjes nuk e ndryshon atë. Të dyja janë të vërteta dhe nuk përjashtojnë njëra-tjetrën:
      ndarja ndryshon mbi çfarë vlerësohet një metodë, ndërsa akordimi ndryshon se cila
      metodë saktësisht po vlerësohet. Një Mahalanobis me fraksion mbështetjeje 0.9 dhe një
      me 0.988 janë në praktikë dy metoda të ndryshme — njëra robuste dhe tjetra klasike —
      dhe nuk ka arsye pse renditja e njërës të parashikojë atë të tjetrës."""),
    p("""Kjo ka pasojë të drejtpërdrejtë për leximin e literaturës. Kur dy punime raportojnë
      renditje të ndryshme për të njëjtat algoritme mbi të njëjtin dataset, shpjegimi më i
      mundshëm nuk është gabim në njërin prej tyre, por protokolle të ndryshme akordimi që
      rrallë raportohen me hollësinë e nevojshme. Rezultatet këtu sugjerojnë se raportimi i
      vlerave të hiperparametrave dhe i procedurës së përzgjedhjes së tyre është po aq i
      domosdoshëm sa raportimi i vetë metrikave."""),
    p("""Rasti i Deep SVDD-së shton një paralajmërim të dytë. Përzgjedhja e bazuar në një
      sllicë të vetme validimi mund të kapë zhurmë: një diferencë prej 0.028 në validimin e
      brendshëm u përkthye në një humbje prej 0.293 në blloqet e testimit. Për modele me
      variancë të lartë një sllicë e vetme nuk mjafton, dhe do të duhej validim i brendshëm
      me disa folds, me kosto llogaritëse përkatësisht më të lartë."""),
    h2("6.3", "Krahasimi me literaturën"),
    p("""Vlerat absolute të raportuara këtu janë dukshëm më të ulëta se shumica e
      rezultateve të publikuara mbi këtë dataset. Ky punim ofron një shpjegim të matur
      për këtë dallim në vend që ta lërë të pashpjeguar."""),
    p("""Së pari, protokolli. Krahasimi i drejtpërdrejtë tregoi se ndarja e rastësishme e
      stratifikuar e fryn precizionin mesatar të metodave të pambikëqyrura mesatarisht 2.74
      herë mbi të njëjtat të dhëna dhe të njëjtat modele. Studimet që raportojnë ndarje të
      rastësishme nuk janë domosdoshmërisht të gabuara në implementim, por matin një
      problem më të lehtë se ai që një sistem prodhimi has."""),
    p("""Së dyti, metrika. Një pjesë e literaturës mbi këtë dataset raporton AUC-ROC mbi
      0.95 dhe e paraqet si sukses. Rezultatet këtu tregojnë se AUC-ROC mbi 0.93 është e
      arritshme edhe nga detektorë me precizion mesatar nën 0.10 — pra ajo nuk dallon një
      detektor të përdorshëm nga një i papërdorshëm në këtë nivel çekuilibri, siç e kanë
      argumentuar Davis dhe Goadrich [@davis2006] dhe e kanë demonstruar Saito dhe
      Rehmsmeier [@saito2015]."""),
    p("""Së treti, mungesa e agregimit. Puna aplikative më e suksesshme mbi zbulimin e
      mashtrimeve mbështetet fort te veçoritë e agreguara për llogari mbi dritare kohore
      [@whitrow2009], [@bahnsen2016], ose te modelimi sekuencial i sjelljes së mbajtësit
      [@jurgovsky2018]. Dataset-i publik i përdorur këtu nuk përmban identifikuesin e
      kartës, prandaj asnjë prej këtyre rrugëve nuk ishte e hapur. Rezultatet duhen
      lexuar si kufi i poshtëm i asaj që arrihet me zbulim pikësor pa kontekst
      llogarie."""),
    p("""Gjetja se pikët e pambikëqyrura mbeten dukshëm nën një model të mbikëqyrur
      përputhet me atë të Carcillo-s dhe bashkautorëve, të cilët megjithatë treguan se
      këto pikë mbajnë informacion plotësues kur përdoren si veçori shtesë për një
      klasifikues të mbikëqyrur [@carcillo2021]. Kjo sugjeron drejtimin më premtues për
      punë të mëtejshme mbi këtë linjë."""),
    h2("6.4", "Implikime praktike"),
    p("""Për një institucion që do të ndërtonte një sistem të tillë, rezultatet sugjerojnë
      pesë përfundime konkrete."""),
    bullets(
        [
            "Infrastruktura nuk është pengesa. Me një broker të vetëm dhe një konsumator, "
            "vonesa mbetet nën njëqind milisekonda deri në një mijë transaksione në sekondë. "
            "Investimi duhet shkuar te cilësia e modelit dhe te të dhënat, jo te "
            "optimizimi i transportit.",
            "Kostoja e pikëzimit duhet të jetë kriter zgjedhjeje qysh në fillim. Dy metoda me "
            "cilësi të ngjashme mund të ndryshojnë treqind herë në kosto pikëzimi, dhe në "
            "rrjedhë ky dallim përcakton nëse metoda është e vendosshme apo jo.",
            "Etiketat historike, edhe të vonuara, kanë vlerë të madhe. Hendeku i matur "
            "sugjeron që një sistem duhet të përdorë metoda të pambikëqyrura si shtresë "
            "plotësuese për periudhën pa etiketa, jo si zëvendësim të përhershëm.",
            "Pragu duhet të jetë adaptiv. Një prag i fiksuar në trajnim e bën ngarkesën "
            "hetimore të paparashikueshme pikërisht kur të dhënat ndryshojnë; procedura e "
            "propozuar këtu e stabilizon atë dhe përmirëson edhe cilësinë.",
            "Monitorimi i zhvendosjes duhet të dallojë popullatat. Nëse zhvendoset "
            "popullata normale, ritrajnimi ndihmon; nëse zhvendoset ajo e mashtrimeve, "
            "nevojiten veçori të reja ose etiketa, dhe ritrajnimi është humbje kohe.",
        ]
    ),
    h2("6.5", "Kufizimet"),
    p("""Kufizimet e këtij studimi janë të shumta dhe deklarohen shprehimisht, sepse
      leximi i rezultateve pa to do të ishte i gabuar."""),
    h3("6.5.1", "Kufizimet e të dhënave"),
    bullets(
        [
            "Mungesa e identifikuesit të kartës e bën të pamundur agregimin për llogari dhe "
            "modelimin sekuencial, pra dy nga tri llojet e anomalive në taksonominë "
            "standarde [@chandola2009] mbeten jashtë fushëveprimit.",
            "Kohëzgjatja prej dyzet e tetë orësh lejon vetëm vlerësimin e zhvendosjes "
            "brenda-ditore dhe mes dy ditëve, jo të asaj sezonale.",
            "Anonimizimi me PCA e bën interpretimin semantik të pamundur; interpretueshmëria "
            "e arritur këtu është relative ndaj sinjalit dhe jo ndaj kuptimit të biznesit.",
            "Etiketat supozohen të plota; mashtrimet e pakontestuara, të cilat ekzistojnë në "
            "realitet, do t'i bënin vlerësimet e precizitetit pesimiste.",
        ]
    ),
    h3("6.5.2", "Kufizimet e vlerësimit"),
    bullets(
        [
            "Tetë folds japin fuqi statistikore të kufizuar. Testi post-hoc i Nemenyi-t "
            "mund të refuzojë vetëm për ndarje ekstreme, dhe krahasimet dyshe u kufizuan në "
            "gjashtë pikërisht për të mos e bërë korrigjimin të pakalueshëm.",
            "Numri i pozitivëve për bllok testimi varion nga trembëdhjetë në tetëdhjetë e "
            "tetë, prandaj disa vlerësime për fold janë të zhurmshme; kjo pasqyrohet në "
            "devijimet standarde të mëdha.",
            "Akordimi i hiperparametrave u krye një herë, në prerjen 70/30, dhe jo brenda "
            "çdo fold-i. Ri-akordimi për fold do të ishte më i rreptë, por do ta shumëfishonte "
            "koston llogaritëse tetë herë.",
            "Kontaminimi i parazgjedhur nxirret nga norma e mashtrimit në dritaren e "
            "trajnimit, pra përdor etiketa historike. Kjo është e deklaruar dhe e njëjtë me "
            "supozimin e referencës së mbikëqyrur, por nuk është plotësisht e pambikëqyrur.",
        ]
    ),
    h3("6.5.3", "Kufizimet operacionale"),
    bullets(
        [
            "Ritmi i mbërritjes është sintetik dhe konstant. Trafiku real është i "
            "shpërthyeshëm, dhe shpërthimet do ta zhvendosnin bishtin e vonesës lart.",
            "Të gjitha matjet u kryen në një host të vetëm me një broker dhe një particion. "
            "Rezultatet nuk thonë asgjë për sjelljen në një grumbull të shpërndarë.",
            "Sistemi nuk trajton dështime, ritentativa apo mesazhe të dyfishta, dhe nuk "
            "përfshin ritrajnim automatik.",
        ]
    ),
    h2("6.6", "Drejtime për punë të mëtejshme"),
    p("""Nga kufizimet dalin drejtimet, të renditura sipas asaj që unë do t'i konsideroja
      më premtueset."""),
    numbers(
        [
            "Vlerësimi mbi një dataset me identifikues llogarie, ku veçoritë e agreguara për "
            "mbajtës mund të ndërtohen. Kjo do të testonte nëse hendeku mes metodave të "
            "pambikëqyrura dhe atyre të mbikëqyrura ngushtohet kur konteksti bëhet i "
            "disponueshëm.",
            "Kombinimi hibrid në stilin e Carcillo-s dhe bashkautorëve [@carcillo2021]: pikët "
            "e pambikëqyrura si veçori shtesë për një model të mbikëqyrur të trajnuar mbi "
            "etiketat e vonuara. Rezultatet këtu sugjerojnë se informacioni plotësues "
            "ekziston, sepse renditjet e modeleve të ndryshme nuk përputhen plotësisht.",
            "Ritrajnim inkremental me dritare rrëshqitëse dhe krahasim i drejtpërdrejtë me "
            "trajnimin një herë, në kuadrin e vlerësimit prekuencial [@gama2013]. Analiza e "
            "zhvendosjes këtu parashikon se përfitimi do të jetë modest, dhe kjo parashikim "
            "është i testueshëm.",
            "Vlerësimi i modeleve sekuenciale kur konteksti i llogarisë është i "
            "disponueshëm, në vazhdim të punës së Jurgovsky-t dhe bashkautorëve "
            "[@jurgovsky2018].",
            "Zgjerimi i kritereve të pambikëqyrura të përzgjedhjes së modeleve në një "
            "protokoll të plotë pa etiketa, ku edhe kontaminimi caktohet pa etiketa "
            "historike.",
            "Testimi i sistemit nën trafik të shpërthyeshëm dhe me disa konsumatorë "
            "paralelë, për të matur sjelljen e vonesës nën ngarkesë realiste.",
        ]
    ),
    h2("6.7", "Përfundime"),
    p("""Ky punim tregoi se një pipeline i plotë për zbulimin e anomalive mbi një rrjedhë
      të simuluar transaksionesh është i realizueshëm me teknologji të lira dhe të
      hapura, dhe se kufizimi operacional prej një sekonde nuk është pengesa reale — ai
      tejkalohet me një rend madhësie. Pengesa reale është cilësia e zbulimit pa etiketa,
      dhe ky punim e mati atë me kujdes në vend që ta anashkalonte."""),
    p("""Kontributi që e konsideroj më të qëndrueshëm nuk është renditja e algoritmeve, e
      cila varet nga dataset-i, por metodologjia dhe tri gjetjet shpjeguese që ajo
      mundësoi: kuantifikimi i fryrjes prej 2.74 herë që prodhon ndarja e rastësishme,
      dekompozimi i degradimit në zhvendosje të popullatës së mashtrimeve dhe jo të asaj
      normale, dhe lidhja mes përputhjes së vëmendjes së modelit me sinjalin dhe cilësisë
      së zbulimit."""),
    p("""Dy nga tri hipotezat u konfirmuan dhe një u refuzua. Sistemi arrin vonesë nën një
      sekondë; të paktën një metodë e pambikëqyrur arrin cilësi dukshëm mbi rastësinë dhe
      e ruan renditjen e saj nëpër folds; qasja ensemble nuk e tejkalon modelin më të mirë
      individual. Refuzimi i hipotezës së tretë raportohet si gjetje, jo si dështim, dhe
      shoqërohet me shpjegimin e tij të matur."""),
    p("""Nëse do të duhej të nxirrja një mësim të vetëm nga kjo punë, do të ishte ky: në
      këtë fushë vendimet metodologjike ndikojnë në rezultatin e raportuar më shumë se
      zgjedhja e algoritmit. Një ndarje e rastësishme e fryn precizionin mesatar më shumë
      se sa e përmirëson atë kalimi nga algoritmi më i dobët te ai më i miri; dhe
      akordimi i hiperparametrave, i kryer krejtësisht pa parë bashkësinë e testimit,
      e rirendit fushën aq shumë sa korrelacioni i rangjeve bie në 0.17. Kjo do të
      thotë se përparimi i vërtetë në këtë fushë matet vetëm nën protokolle të rrepta, dhe
      se raportimi i një numri të vetëm pa treguar pasigurinë e tij fsheh më shumë sesa
      zbulon."""),
]

BLOCKS = _SINTEZA

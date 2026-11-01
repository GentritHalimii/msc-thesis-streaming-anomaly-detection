"""Kapitulli 6 — DISKUTIME DHE PËRFUNDIME."""

from blocks import bullets, h1, h2, h3, note, numbers, p, tab

_SINTEZA = [
    h1("6", "Diskutime dhe përfundime"),
    h2("6.1", "Përmbledhje e gjetjeve"),
    p("""Tabela më poshtë jep përgjigjen e drejtpërdrejtë për secilën nga tri pyetjet hulumtuese dhe
      evidencën përkatëse. Ajo gjenerohet automatikisht nga rezultatet e eksperimenteve, kështu që
      përputhet me kapitujt e mëparshëm."""),
    tab(
        "rq_summary",
        "Përgjigjet për tri pyetjet hulumtuese dhe evidenca përkatëse.",
        font_size=8.5,
    ),
    p("""Në këtë punim u ndërtua dhe u vlerësua një sistem i plotë për zbulimin e anomalive mbi një
      rrjedhë të simuluar transaksionesh financiare, i cili lidh Apache Kafka-n me tri algoritme
      unsupervised dhe me një referencë supervised. Gjetjet kryesore janë
      këto:"""),
    numbers(
        [
            "Sistemi është i realizueshëm operacionalisht me diferencë të madhe. Vonesa mesatare "
            "end-to-end është 15 deri 53 herë nën objektivin prej një sekonde në të 16 "
            "konfigurimet e testuara, percentili 99 nuk e kalon 132 milisekonda, dhe inferenca zë "
            "nën 10% të vonesës edhe në rastin më të keq.",
            "Në konfigurimin bazë Autoencoder-i ofron balancën më të mirë mes cilësisë dhe kostos, "
            "me AP 0.193 dhe koston më të ulët të inferencës, i ndjekur nga One-Class SVM dhe "
            "Isolation Forest. Diferenca mes Autoencoder-it dhe Isolation Forest-it është "
            "statistikisht e qëndrueshme, ajo mes Autoencoder-it dhe One-Class SVM-së jo. "
            "Referenca supervised mbetet shumë përpara, me AP 0.734, dhe e mund secilin detektor "
            "në të tetë fold-et.",
            "Asnjë variant i ansamblit nuk e kalon modelin më të mirë individual, sepse detektorët "
            "gabojnë njësoj. Me 100 alarme për bllok, 37% e mashtrimeve nuk i arrin asnjë prej "
            "tyre, ndërsa referenca supervised kap 59% të këtyre mashtrimeve.",
            "Konfigurimi peshon më shumë se algoritmi. Transformimi kuantil e rrit One-Class "
            "SVM-në me 0.218 AP në të tetë fold-et, dhe efekti mbetet kur skaluesi zgjidhet vetëm "
            "nga fold-et e mëparshme. Kur secili detektor merr konfigurimin e tij më të mirë, "
            "raporti mes më të mirit dhe më të dobëtit bie nga 2.1 në 1.15.",
            "Ndarja e rastësishme e të dhënave, e zakonshme në literaturë, e rrit AP-në e metodave "
            "unsupervised rreth tri herë, më shumë se sa ndryshon ajo nga algoritmi më i dobët te "
            "më i miri.",
            "Pragu ka peshë praktike. Me një prag sipas normës së mashtrimit detektorët "
            "unsupervised kapin pak, sepse mashtrimet nuk zënë majën e renditjes së tyre. Pragu "
            "adaptiv e bën ngarkesën e hetimeve më të qëndrueshme dhe rrit F1 për të tre, "
            "kryesisht sepse rikthen numrin e synuar të alarmeve.",
        ]
    ),
    h2("6.2", "Interpretimi"),
    h3("6.2.1", "Pse rezultatet unsupervised janë modeste"),
    p("""Shpjegimi i parë nuk lidhet me algoritmet, por me të dhënat. Analiza eksploruese tregoi se
      mashtrimet ndodhen vërtet larg klasës legjitime, me distancë nga fqinjët legjitimë rreth tetë
      herë më të madhe se ajo e një transaksioni tipik. Ky është supozimi mbi të cilin mbështeten të
      tri metodat. Megjithatë largësia nuk mjafton për zbulim, sepse dritarja e trajnimit ka rreth
      199 000 transaksione legjitime dhe bishti i tyre zë të njëjtin rajon të largët; 384 mashtrime
      nuk mund të dallohen numerikisht nga 5% e një popullate kaq të madhe. Kjo duket edhe te pragu:
      me një prag sipas normës së mashtrimit, alarmet e para nuk kanë asnjë mashtrim, dhe shumica
      dërrmuese e alarmeve u takon transaksioneve legjitime të pazakonta."""),
    p("""Analiza e gabimeve e mbështet këtë dhe shton diçka të re. Me 100 alarme për bllok, 37% e
      mashtrimeve nuk i arrin asnjë detektor, dhe këto mashtrime ndodhen më afër popullatës
      legjitime. Referenca supervised megjithatë kap 59% të tyre me të njëjtin buxhet. Kufiri
      i metodave unsupervised këtu nuk vjen pra nga mungesa e sinjalit, por nga forma e tij: një
      drejtim diskriminues mësohet nga etiketat, ndërsa largësia nga normaliteti nuk e zbulon
      atë."""),
    h3("6.2.2", "Pse Isolation Forest renditet i fundit"),
    p("""Për Isolation Forest-in shpjegimi lidhet me strukturën e tij dhe u mat drejtpërsëdrejti.
      Algoritmi e zgjedh rastësisht dimensionin e ndarjes, pa marrë parasysh sa informativ është.
      Numërimi i ndarjeve në pemët e trajnuara e konfirmoi këtë: pesë veçoritë më informative marrin
      17.4% të ndarjeve, ndërsa nga rastësia pritet 17.2%, dhe korrelacioni mes përdorimit të një
      kolone dhe fuqisë së saj diskriminuese është praktikisht zero. Kur çdo pemë sheh më pak
      kolona, rezultati përmirësohet në të tetë fold-et, ashtu siç pritet nëse dobësia është
      shpërndarja e kapacitetit mbi kolona pa sinjal."""),
    p("""U testuan edhe dy shpjegime të tjera. I pari është akordimi, dhe ky shpjegim doli
      pjesërisht i saktë. Një nën-mostër më e madhe e çoi detektorin nga 0.091 në 0.151, dhe kërkimi
      i plotë në 0.168, mjaftueshëm për të kaluar One-Class SVM-në e akorduar. Vendi i fundit në
      konfigurimin bazë nuk është pra i pashmangshëm, dhe një pjesë e dobësisë që zakonisht i
      atribuohet këtij algoritmi u takon vlerave bazë. Megjithatë edhe pas akordimit ai mbetet nën
      Autoencoder-in. Shpjegimi i dytë është se ndarjet paralele me boshtet nuk i përshtaten një
      hapësire komponentësh kryesorë; trajnimi mbi një kopje të rrotulluar rastësisht e ndryshoi
      rezultatin vetëm me 0.007, kështu që ky shpjegim përjashtohet."""),
    note("""Performanca e dobët e Isolation Forest-it në këtë studim nuk duhet përgjithësuar. Ajo
      vjen nga kombinimi i shumë dimensioneve me sinjal të përqendruar në pak komponentë. Në
      probleme ku sinjali shpërndahet mbi shumë veçori, e njëjta rastësi e ndarjeve mund të jetë
      avantazh."""),
    h3("6.2.3", "Pse paraprocesimi peshon më shumë se algoritmi"),
    p("""Rezultati që ndoshta të befason më shumë është se zgjedhja e paraprocesimit ndikon më shumë
      se dallimet mes vetë algoritmeve. Shpjegimi vjen nga mekanizmi i tyre i përbashkët: të tri e
      përcaktojnë anomalinë përmes largësisë ose ngjeshjes, dhe largësia përcaktohet nga shkalla e
      veçorive. Kur ndryshon shkalla, ndryshon vetë problemi që zgjidh algoritmi. Efekti nuk vjen
      nga përzgjedhja pas faktit, sepse mbetet edhe kur skaluesi zgjidhet vetëm nga fold-et e
      mëparshme."""),
    p("""Asimetria me referencën supervised e mbështet këtë interpretim. Regresioni logjistik
      mëson një drejtim diskriminues dhe, kur veçoritë shkallëzohen ndryshe, rregullon koeficientët,
      kështu që rezultati i tij nuk ndryshon. E njëjta asimetri u pa edhe me ndarjen e rastësishme,
      ku metodat unsupervised fituan shumë ndërsa referenca jo. Në të dy rastet metodat gjeometrike
      varen nga mënyra si është ndërtuar hapësira, ndërsa një drejtim i mësuar jo."""),
    h3("6.2.4", "Pse ansamblet nuk ndihmojnë"),
    p("""Sipas teorisë së ansambleve për zbulimin e vlerave të jashtëzakonshme, mesatarizimi e ul
      variancën vetëm kur anëtarët gabojnë në mënyra të pavarura [@aggarwal2015]. Me tre anëtarë ky
      kusht është edhe më i rëndësishëm, sepse nuk ka shumë vota mbi të cilat të mesatarizohet
      zhurma."""),
    p("""Analiza në nivel transaksioni tregon se kushti nuk plotësohet. Një pjesë e madhe e
      mashtrimeve që arrihen brenda buxhetit arrihen nga të tre detektorët njëkohësisht, ndërsa ato
      që nuk arrihen nuk i arrin asnjëri. Renditjet e tyre kanë korrelacion 0.81 deri 0.91.
      Detektorët pra gabojnë njësoj, sepse të tre mbështeten te e njëjta gjeometri, dhe në këto
      kushte kombinimi vetëm e hollon sinjalin e anëtarit më të mirë. Procedura lakmitare arrin vetë
      në të njëjtin përfundim, sepse në çdo fold me histori zgjedh vetëm Autoencoder-in."""),
    p("""Ky përfundim ka vlerë praktike. Kur detektorët ndajnë të njëjtin mekanizëm bazë, investimi
      në një ansambël ka gjasa të japë më pak se investimi në një paraprocesim më të mirë ose në
      veçori të reja. Rezultati tregon edhe një rrezik konkret: kombinimi i të gjithë detektorëve në
      dispozicion, praktikë e zakonshme, e ul cilësinë nën atë të anëtarit më të mirë."""),
    h3("6.2.5", "Pse renditja varet nga konfigurimi"),
    p("""Gjetja e nënkapitullit 5.4.3 kërkon që çdo renditje e publikuar, përfshirë atë të këtij
      punimi, të lexohet me kujdes. Me vlerat bazë raporti mes algoritmit më të mirë dhe më të dobët
      është 2.1; kur secili merr paraprocesimin dhe hiperparametrat e tij më të mirë, raporti bie në
      1.15, One-Class SVM kalon në vend të parë dhe Isolation Forest-i, ndonëse mbetet i fundit, del
      vetëm 0.05 pas tij."""),
    p("""Kjo nuk do të thotë se algoritmet janë të barabartë, por se vlerat bazë nuk janë zgjedhur
      për këto të dhëna. Nën-mostra prej 256 pikash e Isolation Forest-it vjen nga punimi origjinal
      dhe është vlera standarde e bibliotekës; mbi këto të dhëna optimumi është 64 herë më i madh.
      Parametri nu prej 0.05 i konfigurimit bazë të One-Class SVM-së lejon rreth 30 herë më shumë
      pika jashtë kufirit se norma reale e mashtrimit. Edhe ngushtica e konfigurimit bazë të
      Autoencoder-it është më e ngushtë se optimumi i matur."""),
    p("""Një krahasim algoritmesh me vlera bazë mat pra diçka reale, por të kufizuar: sa mirë i
      shërbejnë secilit algoritëm zgjedhjet e paracaktuara mbi këtë dataset. Ai nuk mat kapacitetin
      e algoritmit. Këtu raportohen të dyja dhe dallimi mes tyre thuhet qartë, sepse studimet që
      raportojnë vetëm të parën dhe e paraqesin si të dytën japin shpesh renditje që nuk
      përsëriten."""),
    h3("6.2.6", "Kapaciteti i një consumer-i dhe shkallëzimi horizontal"),
    p("""Në ritmet e testuara consumer-i nuk mbetet pas (nënkapitulli 5.1), por kapaciteti i tij ka
      kufi. Ai i përpunon mikro-grupet njëri pas tjetrit në një proces të vetëm, kështu që
      kapaciteti i tij varet kryesisht nga koha që i duhet për një mikro-grup dhe jo nga numri i
      bërthamave të makinës. Consumer-i i Isolation Forest-it, më i kushtueshmi, përdori 73% të një
      bërthame në 2000 mesazhe në sekondë, prandaj për të kufiri ndodhet mbi ritmet e testuara, por
      jo shumë larg tyre."""),
    p("""Kur ritmi e kalon këtë kufi, zgjidhja e natyrshme në Kafka është shkallëzimi horizontal.
      Topic-u i transaksioneve ndahet në disa particione dhe disa consumer-a punojnë në të njëjtin
      consumer group. Kafka ia cakton çdo particion vetëm një consumer-i të grupit, kështu që
      kapaciteti rritet afërsisht me numrin e consumer-ave, deri te numri i particioneve
      [@kreps2011]. Inferenca nuk kërkon koordinim mes tyre, sepse çdo transaksion trajtohet më vete
      me një skalues dhe një model që vetëm lexohen. I vetmi komponent me gjendje është pragu
      adaptiv: secili consumer do të mbante dritaren e vet, pra kuantili do të llogaritej për
      particion, gjë që mjafton kur particionet marrin trafik të ngjashëm. Ky shkallëzim nuk u mat
      në këtë punim dhe mbetet ndër drejtimet e nënkapitullit 6.6."""),
    h2("6.3", "Krahasimi me literaturën"),
    p("""Vlerat absolute të raportuara këtu janë dukshëm më të ulëta se shumica e rezultateve të
      publikuara për këtë dataset. Punimi jep tri shpjegime të matura për këtë dallim."""),
    p("""I pari është protokolli. Krahasimi i drejtpërdrejtë tregoi se ndarja e rastësishme e
      stratifikuar e rrit AP-në e metodave unsupervised rreth tri herë mbi të njëjtat të dhëna dhe
      me të njëjtat modele. Studimet që përdorin ndarje të rastësishme nuk kanë domosdoshmërisht
      gabime në implementim, por zgjidhin një problem më të lehtë se ai që has një sistem në
      prodhim."""),
    p("""I dyti është metrika. Një pjesë e literaturës për këtë dataset raporton AUC-ROC mbi 0.95 si
      sukses. Këtu AUC-ROC mbi 0.94 arrihet edhe nga detektori më i dobët i studimit, i cili ka AP
      nën 0.10. Në këtë nivel çekuilibri kjo metrikë nuk e dallon një detektor të përdorshëm nga një
      i papërdorshëm, siç e argumentuan Davis dhe Goadrich [@davis2006] dhe e treguan Saito dhe
      Rehmsmeier [@saito2015]."""),
    p("""I treti është mungesa e agregimit. Punimet më të suksesshme për zbulimin e mashtrimeve
      mbështeten te veçori të agreguara për llogari mbi dritare kohore [@whitrow2009],
      [@bahnsen2016], ose te modelimi i sekuencës së transaksioneve të një mbajtësi
      [@jurgovsky2018]. Dataset-i publik i përdorur këtu nuk ka identifikues karte, prandaj asnjë
      nga këto rrugë nuk ishte e mundur, dhe rezultatet duhen lexuar si kufi i poshtëm i asaj që
      arrihet me zbulim pikësor pa kontekst llogarie."""),
    p("""Gjetja se pikët unsupervised mbeten shumë pas një modeli supervised përputhet me atë të
      Carcillo-s dhe bashkautorëve, të cilët treguan gjithashtu se këto pikë mbartin informacion
      plotësues kur përdoren si veçori shtesë për një klasifikues supervised [@carcillo2021].
      Analiza e gabimeve këtu shkon në të njëjtin drejtim: shumica e mashtrimeve që nuk i arrijnë
      detektorët unsupervised kapen nga referenca, kështu që dy burimet e informacionit nuk
      mbivendosen plotësisht."""),
    h2("6.4", "Implikime praktike"),
    p("""Për një institucion që do të ndërtonte një sistem të tillë, rezultatet sugjerojnë pesë
      përfundime konkrete."""),
    bullets(
        [
            "Infrastruktura nuk është pengesa. Me një broker dhe një consumer, vonesa mbetet shumë "
            "nën objektiv dhe consumer-i nuk mbetet pas deri në 2000 transaksione në sekondë, "
            "ritmi më i lartë i testuar. Investimi duhet drejtuar te "
            "cilësia e modelit dhe te të dhënat, jo te optimizimi i transportit.",
            "Paraprocesimi duhet zgjedhur bashkë me modelin. Në këtë studim ai dha përfitime më të "
            "mëdha se çdo zgjedhje algoritmi, dhe një sistem që e trajton skaluesin si detaj "
            "implementimi lë pa shfrytëzuar një përmirësim të konsiderueshëm.",
            "Kostoja e inferencës duhet të jetë kriter zgjedhjeje që në fillim. Dy metoda me "
            "cilësi të ngjashme mund të kenë kosto të inferencës që ndryshon qindra herë, dhe në "
            "një rrjedhë ky dallim përcakton nëse metoda mund të vendoset.",
            "Etiketat historike, edhe të vonuara, kanë vlerë të madhe. Hendeku me referencën "
            "supervised dhe analiza e mashtrimeve që nuk kapen sugjerojnë që metodat unsupervised "
            "të përdoren si shtresë plotësuese për periudhën pa etiketa, jo si zëvendësim i "
            "përhershëm.",
            "Pragu adaptiv është i dobishëm për detektorët unsupervised, por jo për një model të "
            "kalibruar. Një prag i fiksuar gjatë trajnimit e bën ngarkesën e hetimeve të "
            "paparashikueshme sa herë që të dhënat ndryshojnë; pragu adaptiv e zbut këtë luhatje "
            "dhe rikthen numrin e synuar të alarmeve, por te një model që jep probabilitete të "
            "kalibruara shton alarme të panevojshme.",
        ]
    ),
    h2("6.5", "Kufizimet"),
    p("""Studimi ka kufizime që ndikojnë në mënyrën si duhen lexuar rezultatet."""),
    h3("6.5.1", "Kufizimet e të dhënave"),
    bullets(
        [
            "Mungesa e identifikuesit të kartës nuk lejon agregimin për llogari dhe modelimin e "
            "sekuencave, kështu që dy nga tri llojet e anomalive të taksonomisë standarde "
            "[@chandola2009] mbeten jashtë fushëveprimit.",
            "Të dhënat mbulojnë vetëm 48 orë, prandaj mund të vlerësohet zhvendosja brenda ditës "
            "dhe mes dy ditëve, por jo ajo sezonale.",
            "Anonimizimi me PCA e bën të pamundur interpretimin semantik; interpretimi i arritur "
            "këtu lidhet me sinjalin e kolonave dhe jo me kuptimin e tyre.",
            "Ora e ditës nuk përdoret si veçori, ndonëse norma e mashtrimit ndryshon shumë sipas "
            "saj (nënkapitulli 4.1.2), sepse kolona Time shërben për renditjen dhe ndarjen e "
            "rrjedhës. Një sistem real mund ta përdorë orën lokale të transaksionit si veçori më "
            "vete, pa e ngatërruar me kohën që përcakton ndarjen.",
            "Etiketat merren si të plota. Mashtrimet që nuk kontestohen kurrë, që ekzistojnë në "
            "realitet, do t'i bënin vlerat e precision-it pesimiste.",
            "Studimi përdor një dataset të vetëm, prandaj përgjithësimi i renditjeve te të dhëna "
            "të tjera kërkon verifikim.",
        ]
    ),
    h3("6.5.2", "Kufizimet e vlerësimit"),
    bullets(
        [
            "Tetë fold-e japin fuqi statistikore të kufizuar: p-vlera më e vogël e mundshme e "
            "testit të Wilcoxon-it është 0.0078, prandaj numri i krahasimeve duhej mbajtur i vogël "
            "dhe i deklaruar paraprakisht.",
            "Numri i pozitivëve për bllok testimi është nga 13 deri në 88, prandaj disa vlerësime "
            "për fold janë të zhurmshme, siç shihet në devijimet standarde të mëdha.",
            "Detektorët unsupervised trajnohen mbi transaksionet normale të dritares, të pastruara "
            "me etiketat historike, dhe kontaminimi bazë merret nga norma e mashtrimit në dritaren "
            "e trajnimit. Të dyja përdorin etiketa historike, njësoj si referenca supervised; në "
            "një sistem krejtësisht pa etiketa, dritarja e trajnimit do të përmbante edhe "
            "mashtrimet.",
            "Hiperparametrat u akorduan një herë, në dritaren e ndarjes 70/30, dhe jo brenda çdo "
            "fold-i. Kjo dritare përmban blloqet e testimit të fold-eve 0 deri 3; efekti u "
            "raportua prandaj edhe vetëm për fold-et 4 deri 7, dhe doli i njëjtë. Akordimi për çdo "
            "fold do të ishte më i saktë, por do ta shumëfishonte koston tetë herë.",
            "Paraprocesimi dhe hiperparametrat u studiuan veç e veç dhe u kombinuan në një dizajn "
            "2×2; një kërkim i përbashkët mbi të dyja hapësirat do të ishte më i plotë.",
        ]
    ),
    h3("6.5.3", "Kufizimet operacionale"),
    bullets(
        [
            "Ritmi i mbërritjes është sintetik dhe konstant. Trafiku real vjen me shpërthime, dhe "
            "shpërthimet do ta rrisnin bishtin e vonesës.",
            "Të gjitha matjet u bënë në një host me një broker dhe një particion, prandaj "
            "rezultatet nuk thonë asgjë për sjelljen në një sistem të shpërndarë.",
            "Vonesa end-to-end matet deri te dorëzimi i alarmit producer-it të Kafka-s; konfirmimi "
            "i broker-it për alarmin nuk përfshihet.",
            "Sistemi nuk trajton dështime, ripërsëritje ose mesazhe të dyfishta, dhe nuk ka "
            "ritrajnim automatik.",
        ]
    ),
    h2("6.6", "Drejtime për punë të mëtejshme"),
    p("""Nga kufizimet dalin drejtimet e mëposhtme, të renditura sipas premtimit që kanë:"""),
    numbers(
        [
            "Vlerësimi mbi një dataset me identifikues llogarie, ku mund të ndërtohen veçori të "
            "agreguara për mbajtës. Kjo do të tregonte nëse hendeku mes metodave unsupervised dhe "
            "atyre supervised ngushtohet kur konteksti është i disponueshëm; analiza e "
            "mashtrimeve që nuk kapen sugjeron se aty ndodhet pjesa më e madhe e hapësirës për "
            "përmirësim.",
            "Kombinimi hibrid në stilin e Carcillo-s dhe bashkautorëve [@carcillo2021], ku pikët "
            "unsupervised përdoren si veçori shtesë për një model supervised të trajnuar mbi "
            "etiketat e vonuara.",
            "Kërkimi i përbashkët mbi paraprocesimin dhe hiperparametrat. Meqë të dyja ndikojnë "
            "shumë dhe ndërveprojnë, optimizimi i tyre veç e veç nuk e gjen domosdoshmërisht "
            "konfigurimin më të mirë.",
            "Zgjerimi i familjes së detektorëve me metoda deep one-class ose me modele gjenerative "
            "të thella, të vlerësuara me të njëjtin protokoll.",
            "Ritrajnimi inkremental me dritare rrëshqitëse dhe krahasimi i tij me trajnimin një "
            "herë, në kuadrin e vlerësimit prekuencial [@gama2013]. Analiza e zhvendosjes në "
            "Shtojcën E sugjeron një përfitim modest, sepse lëvizin kryesisht mashtrimet dhe jo "
            "transaksionet normale; ky parashikim mund të testohet.",
            "Testimi i sistemit me trafik me shpërthime dhe me disa consumer-a paralelë, për të "
            "matur vonesën nën ngarkesë më realiste.",
        ]
    ),
    h2("6.7", "Përfundime"),
    p("""Ky punim tregoi se një pipeline i plotë për zbulimin e anomalive mbi një rrjedhë të
      simuluar transaksionesh mund të ndërtohet me teknologji të lira dhe të hapura, dhe se
      objektivi operacional prej një sekonde arrihet me diferencë të madhe. Pengesa reale është
      cilësia e zbulimit pa etiketa, dhe punimi u përqendrua te matja e saj."""),
    p("""Dy nga tri hipotezat u konfirmuan dhe një u refuzua. Sistemi arrin vonesë nën një sekondë.
      Të paktën një metodë unsupervised arrin cilësi qartë mbi rastësinë dhe e ruan renditjen e saj
      në fold-e, dhe në konfigurimin bazë Autoencoder-i ofron balancën më të mirë mes cilësisë dhe
      kostos. Qasja ensemble nuk e kalon modelin më të mirë individual; ky rezultat raportohet si
      gjetje dhe jo si dështim, bashkë me shpjegimin e tij në nivel transaksioni."""),
    p("""Përtej renditjes së tri algoritmeve, e cila varet nga dataset-i dhe nga protokolli,
      rezultatet tregojnë se në këtë fushë vendimet metodologjike ndikojnë në numrin e raportuar më
      shumë se zgjedhja e algoritmit. Ndarja e rastësishme e rrit AP-në më shumë se sa ndryshon ajo
      nga algoritmi më i dobët te më i miri, dhe një paraprocesim tjetër ka efekt të ngjashëm. Për
      këtë arsye rezultatet në këtë fushë kanë kuptim vetëm kur raportohen bashkë me pasigurinë e
      tyre, protokollin e ndarjes dhe procedurën e paraprocesimit dhe të akordimit."""),
]

BLOCKS = _SINTEZA

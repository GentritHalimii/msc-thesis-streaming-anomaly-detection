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
      rrjedhë të simuluar transaksionesh financiare, i cili lidh Apache Kafka-n me tri algoritmet
      unsupervised të projekt-propozimit dhe me një referencë të mbikëqyrur. Gjetjet kryesore janë
      këto:"""),
    numbers(
        [
            "Sistemi është i realizueshëm operacionalisht me diferencë të madhe. Vonesa mesatare "
            "end-to-end është 15 deri 53 herë nën objektivin prej një sekonde në të 16 "
            "konfigurimet e testuara, percentili 99 nuk e kalon 132 milisekonda, dhe inferenca zë "
            "nën 10% të vonesës edhe në rastin më të keq.",
            "Kufiri i sipërm i problemit është gjeometrik dhe matet pa model. Mashtrimet janë 7.9 "
            "herë më larg klasës legjitime se një transaksion tipik legjitim, por vetëm distanca "
            "jep AP 0.30, sepse bishti i klasës legjitime zë të njëjtin rajon; për të arritur "
            "mashtrimin median duhen rreth 530 alarme.",
            "Në konfigurimin bazë Autoencoder-i ofron balancën më të mirë mes cilësisë dhe kostos, "
            "i ndjekur nga One-Class SVM dhe Isolation Forest. Diferenca mes Autoencoder-it dhe "
            "Isolation Forest-it është statistikisht e qëndrueshme, ajo mes Autoencoder-it dhe "
            "One-Class SVM-së jo.",
            "Paraprocesimi ndikon më shumë se zgjedhja e algoritmit. Transformimi kuantil e rrit "
            "One-Class SVM-në me 0.218 AP në të tetë fold-et, efekti mbetet kur skaluesi zgjidhet "
            "vetëm nga fold-et e mëparshme, dhe referencën e mbikëqyrur nuk e përmirëson.",
            "Dobësia e Isolation Forest-it u mat. Pesë veçoritë më informative marrin 17.4% të "
            "ndarjeve kundrejt 17.2% që pritet nga rastësia, rrotullimi i hapësirës e ndryshon "
            "rezultatin vetëm me 0.007, dhe kufizimi i kolonave për pemë e përmirëson në të tetë "
            "fold-et.",
            "Referenca e mbikëqyrur mbetet shumë përpara: ajo e mund secilin nga tre detektorët në "
            "të tetë fold-et.",
            "Akordimi i hiperparametrave ndërron vendet e dy detektorëve të fundit, ndërsa i pari "
            "mbetet i njëjti; i njëjti efekt shihet edhe në fold-et që janë të pavarura nga "
            "kërkimi.",
            "Me 100 alarme për bllok, 37% e mashtrimeve nuk i arrin asnjë detektor unsupervised, "
            "ndërsa referenca e mbikëqyrur kap 59% të tyre.",
            "Asnjë variant i ansamblit nuk e kalon modelin më të mirë individual, dhe analiza e "
            "gabimeve në nivel transaksioni tregon pse.",
            "Kur secili detektor vlerësohet në konfigurimin e tij më të mirë, diferenca mes tyre "
            "bie nga 0.102 në 0.049, pra nga raporti 2.1 në 1.15. Pjesa më e madhe e dallimit të "
            "dukshëm mes algoritmeve vjen nga sa mirë u përshtaten të dhënave vlerat bazë.",
            "Zhvendosja e mashtrimeve është më e madhe se ajo e transaksioneve legjitime dhe e "
            "kalon zhurmën e mostrimit në çdo fold, por rreth gjysma e PSI-së së saj të "
            "papërpunuar vjen nga numri i vogël i mashtrimeve për bllok.",
            "Pragu adaptiv me dritare rrëshqitëse e bën ngarkesën e hetimeve më të qëndrueshme dhe "
            "rrit F1 për të tre detektorët unsupervised, kryesisht sepse rikthen numrin e synuar "
            "të alarmeve; për referencën e mbikëqyrur F1 bie.",
        ]
    ),
    h2("6.2", "Interpretimi"),
    h3("6.2.1", "Pse rezultatet unsupervised janë modeste"),
    p("""Shpjegimi i parë nuk lidhet me algoritmet. Karakterizimi gjeometrik tregoi se mashtrimet
      ndodhen vërtet larg klasës legjitime, me distancë nga fqinjët legjitimë rreth tetë herë më të
      madhe se ajo e një transaksioni tipik. Ky është supozimi mbi të cilin mbështeten të tri
      metodat. Megjithatë largësia nuk mjafton për zbulim, sepse dritarja e trajnimit ka rreth 199
      000 transaksione legjitime dhe bishti i tyre zë të njëjtin rajon të largët; 384 mashtrime nuk
      mund të dallohen numerikisht nga 5% e një popullate kaq të madhe."""),
    p("""Prandaj edhe një detektor pa asnjë parametër, që rendit transaksionet vetëm sipas distancës
      nga fqinjët legjitimë, arrin AP 0.30 në dritaren e trajnimit dhe 0.12 në atë të testimit, dhe
      detektorët e trajnuar janë në të njëjtin rend madhësie. Pengesa kryesore nuk është zgjedhja e
      algoritmit, por gjeometria e problemit, dhe çdo krahasim algoritmesh duhet lexuar në raport me
      këtë kufi."""),
    p("""Analiza e gabimeve e mbështet këtë dhe shton diçka të re. Me 100 alarme për bllok, 37% e
      mashtrimeve nuk i arrin asnjë detektor, dhe këto mashtrime ndodhen më afër popullatës
      legjitime. Referenca e mbikëqyrur megjithatë kap 59% të tyre me të njëjtin buxhet.
      Informacioni pra ekziston në të dhëna, por nuk ka formën që e sheh një detektor distancash:
      ndodhet në një drejtim diskriminues që e gjen vetëm mbikëqyrja."""),
    h3("6.2.2", "Pse Isolation Forest renditet i fundit"),
    p("""Për Isolation Forest-in shpjegimi lidhet me strukturën e tij dhe u mat drejtpërsëdrejti.
      Algoritmi e zgjedh rastësisht dimensionin e ndarjes, pa marrë parasysh sa informativ është.
      Numërimi i ndarjeve në pemët e trajnuara e konfirmoi këtë: veçoria më diskriminuese e
      dataset-it mori 3.5% të ndarjeve, ndërsa nga rastësia pritet 3.4%, dhe korrelacioni mes
      përdorimit të një kolone dhe fuqisë së saj diskriminuese është praktikisht zero."""),
    p("""U testuan edhe dy shpjegime të tjera. I pari është akordimi, dhe ky shpjegim doli
      pjesërisht i saktë. Hapësira e hiperparametrave e çoi detektorin nga 0.091 në 0.152, dhe
      kërkimi i plotë në 0.168, mjaftueshëm për të kaluar One-Class SVM-në e akorduar. Vendi i
      fundit në konfigurimin bazë nuk është pra i pashmangshëm, dhe një pjesë e dobësisë që
      zakonisht i atribuohet këtij algoritmi u takon vlerave bazë. Megjithatë edhe pas akordimit ai
      mbetet nën Autoencoder-in, prandaj akordimi nuk e shpjegon gjithë diferencën."""),
    p("""Shpjegimi i dytë është se ndarjet paralele me boshtet nuk i përshtaten një hapësire
      komponentësh kryesorë. Trajnimi mbi një kopje të rrotulluar rastësisht e ndryshoi rezultatin
      vetëm me 0.007, kështu që ky shpjegim përjashtohet."""),
    p("""Ndërhyrja eksperimentale e përforcoi shpjegimin kryesor. Kur çdo detektori iu dhanë vetëm
      komponentët informativë, Isolation Forest-i fitoi më shumë se të tjerët, ashtu siç pritet nëse
      dobësia e tij është shpërndarja e kapacitetit mbi kolona pa sinjal."""),
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
    p("""Asimetria me referencën e mbikëqyrur e mbështet këtë interpretim. Regresioni logjistik
      mëson një drejtim diskriminues dhe, kur veçoritë shkallëzohen ndryshe, rregullon koeficientët,
      kështu që rezultati i tij nuk ndryshon. E njëjta asimetri u pa edhe me ndarjen e rastësishme,
      ku metodat unsupervised fituan shumë ndërsa referenca jo. Në të dy rastet metodat gjeometrike
      varen nga mënyra si është ndërtuar hapësira, ndërsa një drejtim i mësuar jo."""),
    p("""Një vëzhgim teknik e forcon këtë. Isolation Forest-i jep AP saktësisht të njëjtë me
      StandardScaler, RobustScaler, MinMaxScaler dhe pa skalim, sepse pikat e ndarjes zgjidhen
      uniformisht brenda intervalit të vëzhguar të çdo kolone dhe një transformim linear i kolonës
      nuk i ndryshon pemët. Rezultatin e ndryshojnë vetëm transformimet jolineare, si ai
      kuantil."""),
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
    p("""Gjetja e nënkapitullit 5.16 kërkon që çdo renditje e publikuar, përfshirë atë të këtij
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
    p("""Gjetja se pikët unsupervised mbeten shumë pas një modeli të mbikëqyrur përputhet me atë të
      Carcillo-s dhe bashkautorëve, të cilët treguan gjithashtu se këto pikë mbartin informacion
      plotësues kur përdoren si veçori shtesë për një klasifikues të mbikëqyrur [@carcillo2021].
      Analiza e gabimeve këtu shkon në të njëjtin drejtim: shumica e mashtrimeve që nuk i arrijnë
      detektorët unsupervised kapen nga referenca, kështu që dy burimet e informacionit nuk
      mbivendosen plotësisht."""),
    h2("6.4", "Implikime praktike"),
    p("""Për një institucion që do të ndërtonte një sistem të tillë, rezultatet sugjerojnë gjashtë
      përfundime konkrete."""),
    bullets(
        [
            "Infrastruktura nuk është pengesa. Me një broker dhe një consumer, vonesa mbetet shumë "
            "nën objektiv deri në 1000 transaksione në sekondë. Investimi duhet drejtuar te "
            "cilësia e modelit dhe te të dhënat, jo te optimizimi i transportit.",
            "Paraprocesimi duhet zgjedhur bashkë me modelin. Në këtë studim ai dha përfitime më të "
            "mëdha se çdo zgjedhje algoritmi, dhe një sistem që e trajton skaluesin si detaj "
            "implementimi lë pa shfrytëzuar një përmirësim të konsiderueshëm.",
            "Kostoja e pikëzimit duhet të jetë kriter zgjedhjeje që në fillim. Dy metoda me cilësi "
            "të ngjashme mund të kenë kosto pikëzimi që ndryshon qindra herë, dhe në një rrjedhë "
            "ky dallim përcakton nëse metoda mund të vendoset.",
            "Etiketat historike, edhe të vonuara, kanë vlerë të madhe. Hendeku me referencën e "
            "mbikëqyrur dhe analiza e mashtrimeve që nuk kapen sugjerojnë që metodat unsupervised "
            "të përdoren si shtresë plotësuese për periudhën pa etiketa, jo si zëvendësim i "
            "përhershëm.",
            "Pragu adaptiv është i dobishëm për detektorët unsupervised, por jo për një model të "
            "kalibruar. Një prag i fiksuar gjatë trajnimit e bën ngarkesën e hetimeve të "
            "paparashikueshme sa herë që të dhënat ndryshojnë; pragu adaptiv e zbut këtë luhatje "
            "dhe rikthen numrin e synuar të alarmeve, por te një model që jep probabilitete të "
            "kalibruara shton alarme të panevojshme.",
            "Monitorimi i zhvendosjes duhet të dallojë popullatat dhe të marrë parasysh madhësinë "
            "e mostrës. Nëse zhvendoset popullata normale, ritrajnimi ndihmon; nëse zhvendosen "
            "mashtrimet, nevojiten veçori të reja ose etiketa. Për mashtrimet, të pakta në numër, "
            "indekse si PSI duhen lexuar kundrejt zhurmës që jep vetë madhësia e mostrës.",
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
            "Etiketat merren si të plota. Mashtrimet që nuk kontestohen kurrë, që ekzistojnë në "
            "realitet, do t'i bënin vlerat e precision-it pesimiste.",
            "Studimi përdor një dataset të vetëm, prandaj përgjithësimi i renditjeve te të dhëna "
            "të tjera kërkon verifikim.",
        ]
    ),
    h3("6.5.2", "Kufizimet e vlerësimit"),
    bullets(
        [
            "Tetë fold-e japin fuqi statistikore të kufizuar. Kufizimi i krahasimit në tri "
            "algoritme e bëri testin post-hoc të përdorshëm, por me më shumë algoritme ai do të "
            "ishte përsëri pa fuqi.",
            "Numri i pozitivëve për bllok testimi është nga 13 deri në 88, prandaj disa vlerësime "
            "për fold janë të zhurmshme. Kjo shihet në devijimet standarde të mëdha dhe kërkoi "
            "korrigjimin me permutacione të PSI-së.",
            "Detektorët unsupervised trajnohen mbi transaksionet normale të dritares, të pastruara "
            "me etiketat historike, dhe kontaminimi bazë merret nga norma e mashtrimit në dritaren "
            "e trajnimit. Të dyja përdorin etiketa historike, njësoj si referenca e mbikëqyrur; në "
            "një sistem krejtësisht pa etiketa, dritarja e trajnimit do të përmbante edhe "
            "mashtrimet.",
            "Hiperparametrat u akorduan një herë, në dritaren e ndarjes 70/30, dhe jo brenda çdo "
            "fold-i. Kjo dritare përmban blloqet e testimit të fold-eve 0 deri 3; efekti u "
            "raportua prandaj edhe vetëm për fold-et 4 deri 7, dhe doli i njëjtë. Akordimi për çdo "
            "fold do të ishte më i saktë, por do ta shumëfishonte koston tetë herë.",
            "Paraprocesimi dhe hiperparametrat u studiuan veç e veç dhe u kombinuan në një dizajn "
            "2×2; një kërkim i përbashkët mbi të dyja hapësirat do të ishte më i plotë.",
            "Në studimin e kufizimit të hyrjes, Autoencoder-i e ruan dimensionin latent 8 për çdo "
            "k, kështu që për k të vogël ai nuk ngjesh dhe krahasimi me dy detektorët e tjerë nuk "
            "është plotësisht i barabartë.",
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
            "atyre të mbikëqyrura ngushtohet kur konteksti është i disponueshëm; analiza e "
            "mashtrimeve që nuk kapen sugjeron se aty ndodhet pjesa më e madhe e hapësirës për "
            "përmirësim.",
            "Kombinimi hibrid në stilin e Carcillo-s dhe bashkautorëve [@carcillo2021], ku pikët "
            "unsupervised përdoren si veçori shtesë për një model të mbikëqyrur të trajnuar mbi "
            "etiketat e vonuara.",
            "Kërkimi i përbashkët mbi paraprocesimin dhe hiperparametrat. Meqë të dyja ndikojnë "
            "shumë dhe ndërveprojnë, optimizimi i tyre veç e veç nuk e gjen domosdoshmërisht "
            "konfigurimin më të mirë.",
            "Zgjerimi i familjes së detektorëve me metoda deep one-class ose me modele gjenerative "
            "të thella, të vlerësuara me të njëjtin protokoll dhe me të njëjtin karakterizim "
            "gjeometrik paraprak.",
            "Ritrajnimi inkremental me dritare rrëshqitëse dhe krahasimi i tij me trajnimin një "
            "herë, në kuadrin e vlerësimit prekuencial [@gama2013]. Analiza e zhvendosjes "
            "parashikon një përfitim modest, dhe ky parashikim mund të testohet.",
            "Testimi i sistemit me trafik me shpërthime dhe me disa consumer-a paralelë, për të "
            "matur vonesën nën ngarkesë më realiste.",
        ]
    ),
    h2("6.7", "Përfundime"),
    p("""Ky punim tregoi se një pipeline i plotë për zbulimin e anomalive mbi një rrjedhë të
      simuluar transaksionesh mund të ndërtohet me teknologji të lira dhe të hapura, dhe se
      objektivi operacional prej një sekonde arrihet me diferencë të madhe. Pengesa reale është
      cilësia e zbulimit pa etiketa, dhe punimi u përqendrua te matja e saj."""),
    p("""Më shumë se renditja e tri algoritmeve, e cila varet nga dataset-i dhe nga protokolli,
      vlera e punimit qëndron te metodologjia dhe te gjetjet që ajo bëri të mundura: kufiri
      gjeometrik i problemit i matur para modelimit, fryrja që shkakton ndarja e rastësishme,
      ndikimi i paraprocesimit, i provuar edhe me zgjedhje prekuenciale, ndarja e zhvendosjes sipas
      popullatës me korrigjim për mostrat e vogla, dhe shpjegimi i dobësisë së Isolation Forest-it i
      testuar me ndërhyrje eksperimentale."""),
    p("""Dy nga tri hipotezat u konfirmuan dhe një u refuzua. Sistemi arrin vonesë nën një sekondë.
      Të paktën një metodë unsupervised arrin cilësi qartë mbi rastësinë dhe e ruan renditjen e saj
      në fold-e. Qasja ensemble nuk e kalon modelin më të mirë individual; ky rezultat raportohet si
      gjetje dhe jo si dështim, bashkë me shpjegimin e tij në nivel transaksioni."""),
    p("""Së fundi, rezultatet tregojnë se në këtë fushë vendimet metodologjike ndikojnë në numrin e
      raportuar më shumë se zgjedhja e algoritmit. Ndarja e rastësishme e rrit AP-në më shumë se sa
      ndryshon ajo nga algoritmi më i dobët te më i miri, dhe një paraprocesim tjetër ka efekt të
      ngjashëm. Për këtë arsye rezultatet në këtë fushë kanë kuptim vetëm kur raportohen bashkë me
      pasigurinë e tyre, protokollin e ndarjes dhe procedurën e paraprocesimit dhe të
      akordimit."""),
]

BLOCKS = _SINTEZA

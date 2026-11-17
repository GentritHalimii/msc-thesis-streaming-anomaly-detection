"""Kapitulli 6 — DISKUTIME DHE PËRFUNDIME."""

from blocks import bullets, h1, h2, h3, note, numbers, p, tab

_SINTEZA = [
    h1("6", "Diskutime dhe përfundime"),
    h2("6.1", "Përmbledhje e gjetjeve"),
    p("""Tabela [[tab:rq_summary]] jep përgjigjen e drejtpërdrejtë për secilën nga tri pyetjet
      hulumtuese dhe evidencën përkatëse. Ajo gjenerohet automatikisht nga rezultatet e
      eksperimenteve, kështu që përputhet me kapitujt e mëparshëm."""),
    tab(
        "rq_summary",
        "Përgjigjet për tri pyetjet hulumtuese dhe evidenca përkatëse.",
    ),
    p("""Në këtë punim u ndërtua dhe u vlerësua një sistem i plotë për zbulimin e anomalive mbi një
      rrjedhë të simuluar transaksionesh financiare, i cili lidh Apache Kafka-n me tri algoritme
      unsupervised dhe me një referencë supervised. Gjetjet kryesore janë
      këto:"""),
    numbers(
        [
            "Sistemi është i realizueshëm operacionalisht me diferencë të madhe. Në ritmet deri në "
            "1000 mesazhe në sekondë vonesa mesatare end-to-end është 28 deri 58 milisekonda, 17 "
            "deri 35 herë nën objektivin prej një sekonde, dhe ndryshon pak nga një ekzekutim në "
            "tjetrin. Një consumer i vetëm e mban ritmin deri në 5000 mesazhe në sekondë me tre "
            "nga katër modelet, ndërsa me Isolation Forest-in, të cilin e ngadalëson kostoja fikse "
            "e inferencës për çdo mikro-grup, kufiri ndodhet rreth 2000 deri 3000.",
            "Në konfigurimin bazë Autoencoder-i ofron balancën më të mirë mes cilësisë dhe kostos, "
            "me AP 0.193 dhe koston më të ulët të inferencës, i ndjekur nga One-Class SVM dhe "
            "Isolation Forest. Diferenca mes Autoencoder-it dhe Isolation Forest-it është "
            "statistikisht e qëndrueshme, ajo mes Autoencoder-it dhe One-Class SVM-së jo. "
            "Referenca supervised mbetet shumë përpara, me AP 0.734, dhe e mund secilin detektor "
            "në të tetë fold-et.",
            "Ky rezultat vlen për trajnimin mbi transaksione normale të pastruara me etiketat "
            "historike. Me trajnim mbi gjithë dritaren, mashtrimet përfshirë, Autoencoder-i bie "
            "nga 0.193 në 0.047 dhe One-Class SVM nga 0.150 në 0.111, në të tetë fold-et, ndërsa "
            "Isolation Forest-i nuk ndikohet; renditja përmbyset dhe One-Class SVM del i pari.",
            "Asnjë variant i ansamblit nuk e kalon modelin më të mirë individual, sepse detektorët "
            "gabojnë njësoj. Me 100 alarme për bllok, 37% e mashtrimeve nuk i arrin asnjë prej "
            "tyre, ndërsa referenca supervised kap 59% të këtyre mashtrimeve.",
            "Konfigurimi peshon sa algoritmi ose më shumë. Transformimi kuantil e rrit One-Class "
            "SVM-në me 0.218 AP në të tetë fold-et, dhe efekti mbetet kur skaluesi zgjidhet vetëm "
            "nga fold-et e mëparshme. Kur secili detektor merr konfigurimin e tij më të mirë, "
            "raporti mes më të mirit dhe më të dobëtit bie nga 2.1 në 1.15.",
            "Ndarja e rastësishme e të dhënave, e zakonshme në literaturë, e rrit AP-në e metodave "
            "unsupervised rreth tri herë, nga 2.5 deri 3.6 herë në dhjetë ndarje të rastësishme, "
            "më shumë se sa ndryshon ajo nga algoritmi më i dobët te më i miri.",
            "Pragu ka peshë praktike. Me një prag sipas normës së mashtrimit detektorët "
            "unsupervised kapin pak, sepse mashtrimet nuk zënë majën e renditjes së tyre. Pragu "
            "adaptiv e bën ngarkesën e hetimeve më të qëndrueshme. Ai rrit edhe F1 për të tre "
            "detektorët unsupervised, por vetëm sepse jep më shumë alarme: një prag statik me po "
            "aq alarme arrin të paktën të njëjtin F1.",
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
    h3("6.2.3", "Pse paraprocesimi peshon aq shumë"),
    p("""Rezultati që ndoshta të befason më shumë është se për dy nga tri detektorët zgjedhja e
      paraprocesimit ndikon po aq ose më shumë se dallimet mes vetë algoritmeve: për One-Class
      SVM-në më shumë dhe për Autoencoder-in afërsisht njësoj, ndërsa për Isolation Forest-in më pak
      (nënkapitulli 5.4.1). Shpjegimi vjen
      nga mekanizmi i tyre i përbashkët: të tri e përcaktojnë anomalinë përmes largësisë ose
      ngjeshjes, dhe largësia përcaktohet nga shkalla e veçorive. Kur ndryshon shkalla, ndryshon
      vetë problemi që zgjidh algoritmi. Efekti nuk vjen nga përzgjedhja pas faktit, sepse mbetet
      edhe kur skaluesi zgjidhet vetëm nga fold-et e mëparshme."""),
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
      që nuk arrihen nuk i arrin asnjëri. Renditjet e tyre kanë korrelacion 0.81 deri 0.91, dhe
      vetëm mbi mashtrimet 0.80 deri 0.91.
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
    p("""Testi i kapacitetit e gjeti kufirin e një consumer-i (nënkapitulli 5.1). Consumer-i i
      përpunon mikro-grupet njëri pas tjetrit në një proces të vetëm, kështu që kapaciteti i tij
      varet kryesisht nga koha që i duhet për një mikro-grup dhe jo nga numri i bërthamave të
      makinës. Për Isolation Forest-in kjo kohë është rreth 20 milisekonda, kryesisht kosto fikse
      për thirrje, dhe kufiri ndodhet rreth 2000 deri 3000 mesazhe në sekondë. Për Autoencoder-in
      dhe referencën inferenca është aq e lirë sa kufiri, i cili arrihet rreth 10 000 mesazhe në
      sekondë, vjen nga pjesa tjetër e punës për çdo mesazh dhe nga procesori që e ndajnë
      producer-i, broker-i dhe consumer-i; për One-Class SVM-në në këtë ritëm i shtohet edhe vetë
      inferenca. Për Isolation Forest-in kufiri mund të ngrihej me shumë gjasë edhe pa shtuar
      consumer-a, me mikro-grupe më të mëdha që e ndajnë koston fikse mbi më shumë mesazhe, me
      çmimin e një pritjeje pak më të gjatë për mesazh."""),
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
      publikuara për këtë dataset. Tabela [[tab:literature_comparison]] i vendos disa prej tyre
      pranë rezultateve të këtij punimi, bashkë me mënyrën si u ndanë të dhënat dhe metrikën e
      raportuar [@pumsirirat2018], [@ileberi2022], [@han2022adbench]. Përfshihen vetëm punimet,
      teksti i plotë i të cilave u verifikua; disa raportojnë vetëm saktësi ose AUC-ROC, prandaj
      krahasimi i drejtpërdrejtë i AP-së është i mundur vetëm me ADBench."""),
    tab(
        "literature_comparison",
        "Rezultate të publikuara mbi dataset-in ULB krahasuar me ato të këtij punimi.",
        widths=[3.3, 4.2, 3.3, 4.2],
    ),
    p("""Punimi jep tri shpjegime të matura për dallimin."""),
    p("""I pari është protokolli. Krahasimi i drejtpërdrejtë tregoi se ndarja e rastësishme e
      stratifikuar e rrit AP-në e metodave unsupervised rreth tri herë mbi të njëjtat të dhëna dhe
      me të njëjtat modele. Studimet që përdorin ndarje të rastësishme nuk kanë domosdoshmërisht
      gabime në implementim, por zgjidhin një problem më të lehtë se ai që has një sistem në
      prodhim. Rezultatet e ADBench shkojnë në të njëjtin drejtim: me ndarje të rastësishme
      70/30, Isolation Forest-i arrin aty AP 0.217 dhe One-Class SVM 0.476, ndërsa këtu, me
      protokoll kronologjik, 0.091 dhe 0.150 [@han2022adbench]. Dallimi nuk vjen vetëm nga ndarja,
      sepse ndryshojnë edhe paraprocesimi dhe hiperparametrat, por drejtimi i tij përputhet me
      fryrjen e matur në nënkapitullin 5.6."""),
    p("""I dyti është metrika. Një pjesë e literaturës për këtë dataset raporton AUC-ROC mbi 0.95 si
      sukses; Autoencoder-i i Pumsirirat-it dhe Yan-it, për shembull, arrin AUC-ROC 0.960
      [@pumsirirat2018]. Këtu AUC-ROC mbi 0.94 arrihet edhe nga detektori më i dobët i studimit, i
      cili ka AP nën 0.10, dhe Autoencoder-i i këtij punimi arrin AUC-ROC 0.943 me AP 0.193. Në këtë
      nivel çekuilibri kjo metrikë nuk e dallon një detektor të përdorshëm nga një i papërdorshëm,
      siç e argumentuan Davis dhe Goadrich [@davis2006] dhe e treguan Saito dhe Rehmsmeier
      [@saito2015]."""),
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
    p("""Për një institucion që do të ndërtonte një sistem të tillë, rezultatet sugjerojnë gjashtë
      përfundime konkrete."""),
    bullets(
        [
            "Infrastruktura nuk është pengesa. Me një broker dhe një consumer në një makinë të "
            "vetme, vonesa mbetet shumë nën objektiv dhe sistemi e mban ritmin deri në 5000 "
            "transaksione në sekondë me tre nga katër modelet. Për ritme më të larta ose për "
            "modele më të kushtueshme zgjidhja e natyrshme është shkallëzimi horizontal i "
            "nënkapitullit 6.2.6. Investimi duhet drejtuar te cilësia e modelit dhe te të "
            "dhënat, jo te optimizimi i transportit.",
            "Paraprocesimi duhet zgjedhur bashkë me modelin. Në këtë studim ai i dha One-Class "
            "SVM-së një përfitim më të madh se zgjedhja e algoritmit dhe Autoencoder-it afërsisht "
            "sa ajo, kështu që një sistem që e trajton skaluesin si detaj implementimi lë pa "
            "shfrytëzuar një përmirësim të konsiderueshëm.",
            "Kostoja e inferencës duhet të jetë kriter zgjedhjeje që në fillim. Dy metoda me "
            "cilësi të ngjashme mund të kenë kosto të inferencës që ndryshon qindra herë, dhe në "
            "një rrjedhë ky dallim përcakton nëse metoda mund të vendoset.",
            "Etiketat historike, edhe të vonuara, kanë vlerë të madhe. Hendeku me referencën "
            "supervised dhe analiza e mashtrimeve që nuk kapen sugjerojnë që metodat unsupervised "
            "të përdoren si shtresë plotësuese për periudhën pa etiketa, jo si zëvendësim i "
            "përhershëm.",
            "Zgjedhja e detektorit varet nga etiketat historike. Nëse ato mund të përdoren për ta "
            "pastruar dritaren e trajnimit, Autoencoder-i jep balancën më të mirë; nëse jo, "
            "Isolation Forest-i ose One-Class SVM janë më të sigurt, sepse pa pastrim "
            "Autoencoder-i humbet rreth tre të katërtat e AP-së.",
            "Pragu adaptiv shërben për ta mbajtur ngarkesën e hetimeve të qëndrueshme, jo për ta "
            "përmirësuar zbulimin. Një prag i fiksuar gjatë trajnimit e bën ngarkesën të "
            "paparashikueshme sa herë që të dhënat ndryshojnë, dhe pragu adaptiv e zbut këtë "
            "luhatje. Rritja e F1 që e shoqëron vjen nga numri më i madh i alarmeve, dhe te një "
            "model që jep probabilitete të kalibruara ai shton alarme të panevojshme.",
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
            "Detektorët unsupervised trajnohen në protokollin kryesor mbi transaksionet normale "
            "të dritares, të pastruara me etiketat historike. Regjimi pa pastrim u mat në "
            "nënkapitullin 5.6 dhe e ndryshon renditjen, por vetëm për dy skajet: dritaren "
            "plotësisht të pastruar dhe atë fare të papastruar. Kontaminimi bazë merret "
            "gjithashtu nga norma e mashtrimit në dritaren e trajnimit; ai nuk ndikon AP-në, por "
            "ndikon pragun dhe numrin e alarmeve.",
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
            "rezultatet nuk thonë asgjë për sjelljen në një sistem të shpërndarë. Në testin e "
            "kapacitetit producer-i, broker-i dhe consumer-i e ndajnë të njëjtin procesor, kështu "
            "që kufiri i matur është i gjithë sistemit në këtë makinë dhe jo vetëm i consumer-it.",
            "Çdo konfigurim u mat tri herë. Tri ekzekutime japin një ide të zhurmës mes tyre, por "
            "jo një interval besimi të ngushtë; dallimet e vogla mes konfigurimeve duhen lexuar "
            "si të tilla.",
            "Vonesa end-to-end matet deri te dorëzimi i alarmit producer-it të Kafka-s; konfirmimi "
            "i broker-it për alarmin nuk përfshihet.",
            "Vonesa u mat pa ruajtjen në PostgreSQL. Ruajtja bëhet në grupe dhe kontrollohet nga "
            "testet e integrimit, por kostoja e saj në vonesë nuk është matur.",
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
            "Regjimet e ndërmjetme të trajnimit, ku dritarja pastrohet vetëm me etiketat që kanë "
            "mbërritur deri në atë moment. Kështu do të matej se sa nga përparësia e regjimit "
            "semi-supervised mbetet kur vonesa e verifikimit i lë disa mashtrime pa etiketë.",
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
      Të tri metodat unsupervised arrijnë cilësi qartë mbi rastësinë në çdo fold, dhe në
      konfigurimin bazë renditja e tyre ka rregull nëpër fold-e (Kendall W = 0.61), ndonëse dallimi
      mes dy të parave nuk është i vërtetuar statistikisht dhe renditja ndryshon me paraprocesimin
      dhe me regjimin e trajnimit. Në konfigurimin bazë, me dritare trajnimi të pastruar me etiketat
      historike, Autoencoder-i ofron balancën më të mirë mes cilësisë dhe kostos; pa këtë pastrim,
      përparësia e tij zhduket. Qasja ensemble nuk e kalon modelin më të mirë individual; ky
      rezultat raportohet si gjetje dhe jo si dështim, bashkë me shpjegimin e tij në nivel
      transaksioni."""),
    p("""Përtej renditjes së tri algoritmeve, e cila varet nga dataset-i dhe nga protokolli,
      rezultatet tregojnë se në këtë fushë vendimet metodologjike ndikojnë në numrin e raportuar më
      shumë se zgjedhja e algoritmit. Ndarja e rastësishme e rrit AP-në më shumë se sa ndryshon ajo
      nga algoritmi më i dobët te më i miri, një paraprocesim tjetër ka efekt të ngjashëm te
      One-Class SVM-ja, dhe trajnimi pa pastrimin e dritares e përmbys renditjen. Për këtë arsye
      rezultatet në këtë fushë kanë kuptim vetëm kur raportohen bashkë me pasigurinë e tyre,
      protokollin e ndarjes, regjimin e trajnimit dhe procedurën e paraprocesimit dhe të
      akordimit."""),
]

BLOCKS = _SINTEZA

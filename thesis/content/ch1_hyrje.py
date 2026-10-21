"""Kapitulli 1 — HYRJE."""

from blocks import bullets, h1, h2, numbers, p

BLOCKS = [
    h1("1", "Hyrje"),
    h2("1.1", "Konteksti dhe motivimi"),
    p("""Pagesat me karta janë sot pjesë e pandashme e ekonomisë evropiane, dhe bashkë me vëllimin e
      tyre është rritur edhe mashtrimi. Raporti i Bankës Qendrore Evropiane për mashtrimet me karta
      i vlerëson humbjet vjetore në Zonën e Vetme të Pagesave në Euro në qindra milionë euro, ku
      pjesa më e madhe vjen nga transaksionet në të cilat karta nuk paraqitet fizikisht [@ecb2021].
      Për këto transaksione kontrollet që mbështeten te karta ose te terminali kanë pak vlerë,
      prandaj vendimi duhet marrë kryesisht nga të dhënat e vetë transaksionit."""),
    p("""Problemi është i vështirë sepse tri kufizime veprojnë njëkohësisht. Klasat janë
      jashtëzakonisht të çekuilibruara: mashtrimet zakonisht përbëjnë më pak se një për qind të
      trafikut, dhe në këto kushte metrika si saktësia (accuracy) nuk thonë pothuajse asgjë
      [@saito2015]. Etiketat vijnë me vonesë, sepse një transaksion konfirmohet si mashtrim vetëm
      pasi mbajtësi i kartës e konteston ose pasi e verifikon një analist, çka zgjat ditë ose javë;
      kur duhet marrë vendimi, etiketa mungon [@dalpozzolo2018]. Dhe vendimi ka afat: duhet dhënë
      brenda kohës së autorizimit, ndryshe alarmi shërben vetëm për raportim."""),
    p("""Këto kufizime i bëjnë tërheqëse metodat unsupervised për zbulimin e anomalive. Ato nuk kanë
      nevojë për etiketa gjatë trajnimit: mësojnë një model të sjelljes normale dhe sinjalizojnë
      transaksionet që largohen prej tij [@chandola2009], [@aggarwal2017]. Në literaturë paraqiten
      shpesh si zgjidhje e natyrshme e problemit të etiketave. Ky punim shtron një pyetje më
      konkrete: sa mirë funksionojnë këto metoda kur vlerësohen nën kushtet kohore të një sistemi
      real, dhe sa kushton, në njësi të matshme, mungesa e etiketave."""),
    h2("1.2", "Pse një rrjedhë e simuluar dhe pse ky dataset"),
    p("""Rrjedha e transaksioneve në këtë punim nuk është reale: të dhënat janë historike dhe
      riprodhohen sipas radhës kohore. Kjo zgjedhje ka tri arsye."""),
    p("""Arsyeja e parë është qasja në të dhëna. Të dhënat e transaksioneve me karta janë ndër më të
      mbrojturat në sektorin financiar dhe institucionet nuk i japin ato për punime akademike,
      ndërsa punimet që përdorin të dhëna të brendshme nuk mund të riprodhohen nga jashtë. Dataset-i
      i përdorur këtu është publik, i dokumentuar dhe i përdorur gjerësisht, prandaj rezultatet mund
      t'i verifikojë kushdo."""),
    p("""Arsyeja e dytë, edhe më e rëndësishme nga ana metodologjike, është se riprodhimi
      kronologjik ruan rendin e ngjarjeve. Një sistem në prodhim e sheh transaksionin e sotëm pasi
      ka parë atë të djeshmin, kurrë anasjelltas. Ky rend ruhet plotësisht në simulim, ndërsa ndarja
      e rastësishme që përdoret në një pjesë të literaturës e prish atë. Simulimi pra nuk e dobëson
      krahasimin statistikor të algoritmeve; ndikon vetëm në interpretimin e matjeve operacionale,
      sepse ritmi i mbërritjes caktohet nga eksperimenti dhe jo nga trafiku real."""),
    p("""Arsyeja e tretë është kontrolli. Në një mjedis të simuluar mund të ndryshohet ritmi i
      mbërritjes, të përsëritet i njëjti eksperiment me të njëjtin seed dhe të matet efekti i një
      ndryshimi të vetëm, gjë që në një sistem prodhimi nuk bëhet dot. Meqë pyetjet e punimit janë
      krahasuese (cili algoritëm, nën cilin protokoll dhe me çfarë kostoje), kontrolli i
      eksperimentit ka më shumë vlerë se realizmi i trafikut."""),
    h2("1.3", "Deklarimi i shkurtër i problemit"),
    p("""Punimi trajton dizajnimin, implementimin dhe vlerësimin eksperimental të një sistemi për
      zbulimin e anomalive financiare mbi një rrjedhë të simuluar transaksionesh, i cili lidh një
      platformë reale streaming me modele unsupervised. Kujdes i veçantë i kushtohet vlerësimit pa
      rrjedhje informacioni. Shumë rezultate të publikuara mbi këtë dataset janë marrë me ndarje të
      rastësishme, ku transaksione nga e ardhmja hyjnë në trajnimin e modelit që pastaj vlerësohet
      mbi të kaluarën. Punimi mat edhe sa i fryn rezultatet kjo praktikë."""),
    p("""Fushëveprimi kufizohet në dy drejtime. Sistemi është prototip kërkimor në mjedis të
      kontrolluar dhe jo sistem financiar në prodhim. Krahasimi përqendrohet te tri algoritmet
      unsupervised që emërton projekt-propozimi, të cilat studiohen në thellësi."""),
    h2("1.4", "Thellësi në vend të gjerësisë"),
    p("""Projekt-propozimi emërton Isolation Forest dhe Autoencoder-in si detektorët kryesorë,
      One-Class SVM si komponent shtesë dhe Regresionin Logjistik si model bazë (baseline). Studimi
      i përmbahet kësaj bashkësie dhe shkon në thellësi në katër drejtime. Ndarja e vetme
      zëvendësohet me një protokoll rolling-origin 8-fold, i cili tregon nëse renditja e algoritmeve
      mbetet e njëjtë në periudha të ndryshme. Paraprocesimi dhe hiperparametrat trajtohen si
      variabla eksperimentale dhe jo si zgjedhje të paracaktuara. Për secilin algoritëm studiohen
      parametrat që lidhen me mekanizmin e tij. Së fundi, analiza e gabimeve shkon deri te
      transaksioni i veçantë, për të parë cilat mashtrime nuk kapen dhe pse."""),
    h2("1.5", "Pyetjet hulumtuese"),
    p("""Punimi ndërtohet rreth tri pyetjeve hulumtuese, të formuluara në projekt-propozimin e
      miratuar dhe të pandryshuara gjatë punës:"""),
    numbers(
        [
            "Si mund të implementohet një sistem për zbulimin e anomalive financiare në një mjedis "
            "të simuluar streaming, duke integruar Apache Kafka me modele të Unsupervised Machine "
            "Learning, dhe a mund të arrihet një latency mesatare nën 1 sekondë?",
            "Cili nga algoritmet Isolation Forest, Autoencoder dhe One-Class SVM ofron balancën më "
            "të mirë ndërmjet performancës dhe efikasitetit operacional në krahasim me modelin "
            "baseline Logistic Regression?",
            "A përmirëson qasja ensemble performancën e zbulimit të anomalive krahasuar me "
            "përdorimin e modeleve individuale?",
        ]
    ),
    p("""Kapitulli 5 u përgjigjet të treve dhe Kapitulli 6 i diskuton përgjigjet. Për secilën
      përgjigje jepen edhe kushtet nën të cilat vlen, sepse disa prej tyre varen nga protokolli i
      vlerësimit dhe nga konfigurimi i algoritmeve."""),
    h2("1.6", "Objektivat e punimit"),
    p("""Objektivat specifike janë ato të projekt-propozimit:"""),
    numbers(
        [
            "Rishikimi i literaturës për zbulimin e anomalive, për tri algoritmet e propozimit, "
            "për zbulimin e mashtrimeve me karta dhe për arkitekturat streaming me Apache Kafka.",
            "Dizajnimi dhe implementimi i një arkitekture end-to-end me pesë shtresa, nga leximi i "
            "të dhënave deri te gjenerimi dhe ruajtja e alarmeve, me vonesë të matur nën ritme të "
            "kontrolluara mbërritjeje.",
            "Trajnimi i tri modeleve unsupervised vetëm mbi transaksionet normale dhe krahasimi i "
            "tyre me Regresionin Logjistik, sipas cilësisë së zbulimit dhe kostos operacionale, në "
            "një protokoll vlerësimi pa rrjedhje informacioni.",
            "Testimi eksperimental i qasjes ensemble dhe raportimi i rezultatit, cilido qoftë "
            "drejtimi i tij.",
            "Ruajtja e rezultateve në PostgreSQL dhe vizualizimi i tyre në një panel Grafana të "
            "konfiguruar tërësisht nga kodi.",
            "Nxjerrja e përfundimeve dhe e rekomandimeve praktike nga rezultatet eksperimentale.",
        ]
    ),
    h2("1.7", "Kontributet"),
    p("""Kontributet kryesore të punimit janë këto:"""),
    bullets(
        [
            "Një pipeline i plotë mbi Apache Kafka, nga riprodhimi kronologjik i transaksioneve "
            "deri te alarmet në PostgreSQL dhe Grafana, me vonesë end-to-end të matur në katër "
            "ritme mbërritjeje.",
            "Krahasimi i unifikuar i Isolation Forest-it, Autoencoder-it dhe One-Class SVM-së me "
            "një referencë të mbikëqyrur mbi të njëjtën infrastrukturë, me cilësinë dhe koston "
            "operacionale krahas njëra-tjetrës, në një protokoll rolling-origin 8-fold ku në çdo "
            "fold rindërtohen nga fillimi skaluesi, modelet dhe pragjet.",
            "Rezultati negativ për ansamblet, i shpjeguar në nivel transaksioni: detektorët "
            "gabojnë njësoj, prandaj kombinimi i tyre nuk sjell informacion të ri.",
            "Dy gjetje metodologjike të matura mbi të njëjtat të dhëna dhe të njëjtat modele: "
            "ndarja e rastësishme e rrit Average Precision të metodave unsupervised rreth tri "
            "herë, dhe zgjedhja e paraprocesimit ndikon në rezultat më shumë se zgjedhja mes tri "
            "algoritmeve.",
            "Një prag adaptiv me dritare rrëshqitëse për shtresën e alarmeve, i cili e bën "
            "ngarkesën e hetimeve më të qëndrueshme për detektorët unsupervised.",
        ]
    ),
    h2("1.8", "Ajo që ky punim nuk e trajton"),
    p("""Disa çështje mbeten qëllimisht jashtë punimit. Nuk trajtohet përgatitja për prodhim, si
      disponueshmëria e lartë, autentikimi ose orkestrimi me Kubernetes. Nuk ndërtohet ritrajnim në
      kohë reale. Nuk përdoren teknika mbimostrimi si SMOTE [@chawla2002], sepse ato kërkojnë
      etiketa gjatë trajnimit. Nuk krahasohen platforma streaming mes tyre, dhe krahasimi nuk
      zgjerohet përtej tri algoritmeve të propozimit. Punimi nuk mat as vonesën nën trafik real:
      ritmi i mbërritjes është sintetik dhe i kontrolluar, dhe çdo vlerë e vonesës raportohet bashkë
      me ritmin nën të cilin u mat."""),
    h2("1.9", "Struktura e punimit"),
    p("""Kapitulli 2 rishikon literaturën: mekanizmat e zbulimit të anomalive, tri algoritmet e
      propozimit, punimet për zbulimin e mashtrimeve me karta, arkitekturat streaming dhe
      metodologjinë e vlerësimit. Kapitulli 3 e formulon problemin me saktësi, bashkë me supozimet,
      hipotezat dhe kriteret e suksesit. Kapitulli 4 përshkruan metodologjinë: dataset-in,
      protokollin e ndarjes, modelet, procedurën e pragut, metrikat dhe arkitekturën e implementuar.
      Kapitulli 5 paraqet rezultatet sipas tri pyetjeve hulumtuese dhe tregon sa varen ato nga
      konfigurimi i algoritmeve dhe nga protokolli i ndarjes. Kapitulli 6 i diskuton rezultatet, i
      krahason me literaturën, paraqet kufizimet dhe drejtimet për punë të mëtejshme. Shtojcat
      përmbajnë hollësitë e riprodhimit, strukturën e kodit, rezultatet për çdo fold, rezultatet e
      ndarjes 70/30, analizën e zhvendosjes dhe testet automatike."""),
]

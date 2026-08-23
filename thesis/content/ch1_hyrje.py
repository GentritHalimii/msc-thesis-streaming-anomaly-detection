"""Kapitulli 1 — HYRJE."""

from blocks import bullets, h1, h2, numbers, p

BLOCKS = [
    h1("1", "Hyrje"),
    h2("1.1", "Konteksti dhe motivimi"),
    p("""Pagesat me karta janë bërë infrastrukturë kritike e ekonomisë evropiane, dhe bashkë me
      to është rritur edhe sipërfaqja e sulmit. Sipas raportit të Bankës Qendrore Evropiane
      mbi mashtrimet me karta, humbjet vjetore në Zonën e Vetme të Pagesave në Euro maten në
      qindra milionë euro, me një zhvendosje të qartë drejt transaksioneve ku karta nuk
      paraqitet fizikisht [@ecb2021]. Kjo zhvendosje ka një pasojë teknike të drejtpërdrejtë:
      kontrollet që mbështeteshin te prania fizike e kartës ose te sjellja e terminalit
      humbasin vlerën, dhe pesha e vendimit bie mbi analizën e vetë të dhënave të
      transaksionit."""),
    p("""Ajo që e bën këtë problem të vështirë nuk është vetëm vëllimi, por kombinimi i tri
      kufizimeve që rrallë shfaqen bashkë. E para është çekuilibri ekstrem i klasave:
      mashtrimet përbëjnë një pjesë shumë të vogël të trafikut, zakonisht nën një të qindtën,
      gjë që i bën metrikat e zakonshme si saktësia praktikisht të pakuptimta [@he2009],
      [@branco2016]. E dyta është vonesa e etiketave. Një transaksion konfirmohet si mashtrues
      vetëm pasi mbajtësi i kartës e konteston ose pasi analisti e verifikon, dhe kjo zgjat
      ditë ose javë; në momentin kur duhet marrë vendimi, etiketa thjesht nuk ekziston
      [@dalpozzolo2018]. E treta është kufiri kohor: një vendim që mbërrin pas autorizimit nuk
      është vendim, është raport."""),
    p("""Këto tri kufizime shpjegojnë pse metodat unsupervised të zbulimit të anomalive janë
      tërheqëse në këtë fushë. Ato nuk kërkojnë etiketa gjatë trajnimit, ndërtojnë një model
      të asaj që është normale dhe sinjalizojnë atë që largohet prej tij [@chandola2009],
      [@aggarwal2017]. Në literaturë ato paraqiten shpesh si zgjidhje e natyrshme e problemit
      të etiketave. Pyetja që ky punim shtron është më e ashpër: sa mirë funksionojnë ato
      vërtet, kur vlerësohen nën kushtet kohore që do të hasnin në prodhim, dhe sa kushton
      mungesa e etiketave e shprehur në njësi të matshme."""),
    h2("1.2", "Pse një rrjedhë e simuluar dhe pse ky dataset"),
    p("""Një vërejtje e mundshme ndaj këtij punimi është se rrjedha nuk është reale, sepse të
      dhënat janë historike dhe riprodhohen. Kjo është e vërtetë dhe e qëllimshme, dhe arsyet
      meritojnë të thuhen qartë që në fillim."""),
    p("""E para është aksesueshmëria e të dhënave. Të dhënat reale të transaksioneve me karta
      janë ndër më të mbrojturat në sektorin financiar, asnjë institucion nuk i lëshon ato për
      një punim diplome, dhe punimet që përdorin të dhëna të brendshme janë të
      pariprodhueshme nga jashtë. Dataset-i i përdorur këtu është publik, i dokumentuar dhe
      tashmë i përdorur gjerësisht, gjë që e bën këtë studim të verifikueshëm nga kushdo."""),
    p("""E dyta, dhe metodologjikisht më e rëndësishmja, është se riprodhimi kronologjik i të
      dhënave historike e ruan pikërisht atë veti që ka rëndësi, pra rendin. Një sistem
      zbulimi në prodhim e sheh transaksionin e sotëm pasi ka parë atë të djeshmin dhe kurrë
      anasjelltas. Kjo veti ruhet plotësisht këtu, dhe pikërisht ajo shkatërrohet nga ndarja e
      rastësishme që përdor një pjesë e literaturës. Simulimi pra nuk e dobëson vlefshmërinë
      statistikore të krahasimit; ai e dobëson vetëm interpretimin e matjeve operacionale,
      sepse ritmi i mbërritjes është i imponuar nga eksperimentuesi dhe jo nga trafiku
      real."""),
    p("""E treta është kontrolli. Në një mjedis të simuluar mund të variohet ritmi i
      mbërritjes, të përsëritet i njëjti eksperiment me seed të fiksuar dhe të matet ndikimi i
      një ndryshimi të vetëm. Në një sistem prodhimi asnjëra prej këtyre nuk është e mundur.
      Meqë pyetja qendrore e këtij punimi është krahasuese, pra cili algoritëm, nën cilin
      protokoll dhe me çfarë kostoje, kontrolli eksperimental vlen më shumë se realizmi i
      trafikut."""),
    h2("1.3", "Deklarimi i shkurtër i problemit"),
    p("""Problemi që trajtohet është dizajnimi, implementimi dhe vlerësimi i ndershëm
      eksperimental i një sistemi për zbulimin e anomalive financiare mbi një rrjedhë të
      simuluar transaksionesh, duke integruar një platformë reale streaming me modele
      unsupervised. Fjala e ndershëm këtu nuk është dekorative. Një pjesë e mirë e rezultateve
      të publikuara mbi dataset-in e përdorur këtu janë prodhuar me ndarje të rastësishme të
      të dhënave, të cilat lejojnë që informacioni nga e ardhmja të ndikojë modelin e së
      kaluarës. Një nga gjetjet e këtij punimi është pikërisht sasia e fryrjes që kjo praktikë
      prodhon."""),
    p("""Fushëveprimi është i kufizuar me vetëdije në dy drejtime. Së pari, sistemi është
      prototip kërkimor në mjedis të kontrolluar, jo sistem prodhimi financiar. Së dyti,
      krahasimi kufizohet te tri algoritmet unsupervised që emërton propozimi, të cilat
      studiohen në thellësi, në vend që të zgjerohet numri i algoritmeve me trajtim
      sipërfaqësor të secilit. Kjo zgjedhje e dytë diskutohet më poshtë."""),
    h2("1.4", "Thellësi në vend të gjerësisë"),
    p("""Propozimi emërton Isolation Forest dhe Autoencoder-in si detektorët kryesorë,
      One-Class SVM si komponent shtesë, dhe Regresionin Logjistik si baseline. Studimi i
      përmbahet saktësisht kësaj bashkësie. Alternativa do të kishte qenë zgjerimi i listës me
      dhjetëra detektorë të tjerë, gjë që prodhon një tabelë më të gjatë por jo njohuri më të
      thellë: kur secili algoritëm merr një konfigurim të vetëm dhe një rresht në tabelë, nuk
      ka mënyrë të dihet nëse dallimet vijnë nga mekanizmi apo nga akordimi."""),
    p("""Thellësia këtu blihet në gjashtë drejtime. Karakterizimi gjeometrik i të dhënave
      përcakton kufirin e sipërm përpara se të përshtatet ndonjë model. Protokolli
      rolling-origin me tetë pika prerjeje zëvendëson ndarjen e vetme. Paraprocesimi trajtohet
      si variabël eksperimentale dhe jo si zgjedhje e nënkuptuar. Për secilin nga tri
      algoritmet hartohet sipërfaqja e plotë e hiperparametrave bashkë me diagnostikat
      specifike të mekanizmit të tij. Shpjegimi i renditjes nuk mbetet korrelacion, por
      testohet me ndërhyrje eksperimentale. Dhe analiza e gabimeve zbret në nivelin e
      transaksionit individual për të treguar cilat mashtrime mbeten të paarritshme dhe
      pse."""),
    h2("1.5", "Pyetjet hulumtuese"),
    p("""Punimi organizohet rreth tri pyetjeve hulumtuese, të cilat janë formuluar në
      projekt-propozimin e miratuar dhe janë ruajtur të pandryshuara gjatë gjithë
      implementimit."""),
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
    p("""Të tria pyetjet marrin përgjigje të drejtpërdrejtë në Kapitullin 5 dhe diskutohen në
      Kapitullin 6. Përgjigjet shoqërohen me kushtet nën të cilat vlejnë, sepse një nga
      gjetjet e studimit është pikërisht se disa prej tyre janë të kushtëzuara nga protokolli
      dhe jo veti të pandryshueshme të algoritmeve."""),
    h2("1.6", "Objektivat e punimit"),
    p("""Objektivat specifike, të renditura sipas rendit në të cilin realizohen:"""),
    numbers(
        [
            "Rishikimi i literaturës mbi tri algoritmet e propozimit, mbi zbulimin e mashtrimeve me "
            "karta dhe mbi arkitekturat streaming me Apache Kafka, me theks te metodologjia e "
            "vlerësimit.",
            "Karakterizimi gjeometrik i dataset-it për të përcaktuar kufirin e sipërm të "
            "arritshëm nga metodat e bazuara në distancë, përpara se të përshtatet ndonjë model.",
            "Dizajnimi i një arkitekture pesështresore end-to-end, nga leximi i të dhënave deri te "
            "gjenerimi dhe persistimi i alarmeve.",
            "Ndërtimi i një protokolli vlerësimi pa rrjedhje informacioni, me ndarje kronologjike "
            "dhe me përsëritje në tetë pika kohore prerjeje.",
            "Studimi i thelluar i secilit prej tri algoritmeve: sipërfaqja e hiperparametrave, "
            "ndjeshmëria ndaj paraprocesimit dhe diagnostikat specifike të mekanizmit.",
            "Matja e kostos operacionale, pra vonesë, kapacitet përpunues, memorie dhe CPU, nën "
            "ritme të kontrolluara mbërritjeje.",
            "Hetimi eksperimental i qasjes ensemble dhe raportimi i rezultatit pavarësisht nga "
            "drejtimi i tij.",
            "Analiza e shkaqeve: zhvendosja e shpërndarjeve, interpretueshmëria e vendimeve, "
            "testimi kauzal i mekanizmit të propozuar dhe analiza e gabimeve në nivel transaksioni.",
            "Persistimi i rezultateve në PostgreSQL dhe vizualizimi i tyre në një panel Grafana të "
            "konfiguruar plotësisht nga kodi.",
        ]
    ),
    h2("1.7", "Kontributet"),
    p("""Punimi jep shtatë kontribute, katër prej të cilave dolën gjatë punës dhe jo nga plani
      fillestar."""),
    bullets(
        [
            "Një protokoll vlerësimi rolling-origin i zbatuar mbi një pipeline të vërtetë "
            "streaming, ku çdo fold rindërton nga fillimi skalimin, modelet dhe pragjet. Kjo lejon "
            "të matet nëse renditja e algoritmeve është artefakt i një prerjeje të vetme kohore.",
            "Kuantifikimi i kostos së ndershmërisë metodologjike: krahasimi i drejtpërdrejtë midis "
            "protokollit kronologjik dhe atij me ndarje të rastësishme, mbi të njëjtat të dhëna "
            "dhe të njëjtat modele.",
            "Matja e paraprocesimit si variabël eksperimentale me të njëjtën rreptësi si "
            "algoritmi. Rezultati është se zgjedhja e transformimit i tejkalon dallimet mes vetë "
            "tri algoritmeve, dhe se referenca e mbikëqyrur nuk preket prej saj; asimetria mes "
            "të dyjave e shpjegon mekanizmin.",
            "Përcaktimi i kufirit të sipërm gjeometrik të problemit me një detektor pa model, i "
            "cili tregon se sa nga rezultati modest u atribuohet të dhënave dhe sa algoritmeve.",
            "Një shpjegim mekanicist i renditjes së algoritmeve përmes atribuimit të veçorive, i "
            "shndërruar nga korrelacion në pohim kauzal me një ndërhyrje eksperimentale.",
            "Dekompozimi i degradimit në zhvendosje kovariatësh kundrejt zhvendosjeje koncepti, me "
            "pasoja praktike të ndryshme, sepse e para zgjidhet me ritrajnim ndërsa e dyta jo.",
            "Pragu adaptiv me dritare rrëshqitëse për shtresën e alarmeve, i cili stabilizon "
            "ngarkesën hetimore dhe njëkohësisht përmirëson cilësinë e zbulimit për të tre "
            "detektorët unsupervised, ndërsa për referencën e mbikëqyrur e përkeqëson atë; "
            "asimetria shpjegohet dhe raportohet.",
        ]
    ),
    h2("1.8", "Ajo që ky punim nuk e trajton"),
    p("""Përcaktimi i qartë i asaj që mbetet jashtë është po aq i rëndësishëm sa përcaktimi i
      asaj që përfshihet. Ky punim nuk trajton fortësimin për prodhim, pra disponueshmëri të
      lartë, autentikim ose orkestrim me Kubernetes. Ai nuk ndërton ritrajnim në kohë reale.
      Nuk përdor teknika mbi-mostrimi si SMOTE [@chawla2002], sepse ato presupozojnë etiketa
      gjatë trajnimit. Nuk krahason platforma streaming mes tyre. Dhe nuk zgjeron krahasimin
      përtej tri algoritmeve të propozimit, për arsyet e shpjeguara në nënkapitullin 1.4.
      Gjithashtu, punimi nuk pretendon të matë vonesë në kushte trafiku real: ritmi i
      mbërritjes është sintetik dhe i kontrolluar, dhe çdo pohim për vonesën shoqërohet me
      ritmin nën të cilin u mat."""),
    h2("1.9", "Struktura e punimit"),
    p("""Kapitulli 2 rishikon literaturën në pesë drejtime: mekanizmat e zbulimit të anomalive,
      tri algoritmet e propozimit të trajtuara veçmas dhe në thellësi, puna specifike mbi
      zbulimin e mashtrimeve me karta, arkitekturat streaming, dhe metodologjia e vlerësimit
      me boshllëqet e saj. Kapitulli 3 formulon problemin në mënyrë të saktë, duke përfshirë
      formalizimin matematik, objektivin e vlerësimit, supozimet dhe hipotezat. Kapitulli 4
      përshkruan metodologjinë: dataset-in, protokollin e ndarjes, modelet, procedurën e
      pragut, metrikat dhe arkitekturën e implementuar. Kapitulli 5 paraqet rezultatet, të
      organizuara sipas tri pyetjeve hulumtuese dhe të ndjekura nga studimet e thelluara për
      secilin algoritëm. Kapitulli 6 i diskuton ato, i vendos përballë literaturës, pranon
      kufizimet dhe propozon drejtime të mëtejshme. Shtojcat përmbajnë detajet e
      riprodhueshmërisë, hiperparametrat e plotë dhe tabelat shtesë."""),
]

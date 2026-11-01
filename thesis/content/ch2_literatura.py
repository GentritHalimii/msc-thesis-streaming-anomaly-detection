"""Kapitulli 2 — SHQYRTIMI I LITERATURËS."""

from blocks import bullets, eq, h1, h2, h3, note, p

_HYRJE = [
    h1("2", "Shqyrtimi i literaturës"),
    p("""Ky kapitull rishikon literaturën në pesë drejtime: përkufizimin dhe klasifikimin e metodave
      të zbulimit të anomalive, tri algoritmet unsupervised të studimit, punimet për zbulimin e
      mashtrimeve me karta, arkitekturat për përpunimin e rrjedhave dhe metodologjinë e vlerësimit.
      Drejtimit të fundit i kushtohet më shumë hapësirë se zakonisht, sepse një nga përfundimet e
      studimit është metodologjik: mënyra se si vlerësohet një detektor ndikon në përfundimin se
      cili detektor është më i mirë."""),
    p("""Rishikimi përqendrohet te këto tri algoritme dhe nuk synon të mbulojë gjithë
      fushën e detektorëve unsupervised. Për të shpjeguar renditjen që del në Kapitullin 5 duhet
      njohur mirë mekanizmi, supozimet dhe dobësitë e njohura të secilit prej tyre; një listë e
      gjatë metodash të përshkruara shkurt nuk do të ndihmonte në këtë."""),
    h2("2.1", "Zbulimi i anomalive: përkufizimi dhe taksonomia"),
    h3("2.1.1", "Çfarë është një anomali"),
    p("""Sipas përkufizimit klasik të Hawkins-it, anomali është një vëzhgim që devijon aq shumë nga
      vëzhgimet e tjera sa ngjall dyshimin se është gjeneruar nga një mekanizëm tjetër
      [@hawkins1980]. Përkufizimi e zhvendos vëmendjen nga "e rrallë" te "e gjeneruar ndryshe", dhe
      të dyja nuk përputhen gjithmonë: një transaksion me vlerë shumë të lartë është i rrallë por
      mund të jetë plotësisht legjitim, ndërsa një mashtrim provues prej një euroje mund të duket
      krejt i zakonshëm."""),
    p("""Chandola, Banerjee dhe Kumar, në rishikimin që mbetet referenca standarde e fushës,
      dallojnë tri lloje anomalish: pikësore, kontekstuale dhe kolektive [@chandola2009]. Anomalia
      pikësore është një instancë e vetme që bie jashtë normës. Anomalia kontekstuale është normale
      në përgjithësi, por jo në kontekstin e vet, si një blerje prej dyqind eurosh në orën tre të
      mëngjesit nga një mbajtës që nuk blen kurrë natën. Anomalia kolektive është një varg
      instancash ku secila duket normale, por i gjithë vargu jo."""),
    p("""Ky dallim ka pasoja për studimin. Dataset-i i përdorur nuk përmban identifikues të kartës,
      prandaj konteksti i mbajtësit nuk mund të rindërtohet dhe dy nga tri llojet e anomalive mbeten
      jashtë modelimit. Ky është një kufizim i të dhënave dhe jo një zgjedhje, dhe diskutohet
      përsëri te kufizimet në Kapitullin 6."""),
    h3("2.1.2", "Mekanizmat e vendimit"),
    p("""Rishikimet më të reja, sidomos ai unifikues i Ruff-it dhe bashkautorëve, i grupojnë metodat
      sipas mekanizmit me të cilin përcaktohet çfarë është normale [@ruff2021]. Ky grupim është më i
      dobishëm se ndarja e zakonshme në metoda klasike dhe të thella, sepse dy metoda nga periudha
      të ndryshme mund të kenë të njëjtin mekanizëm dhe të njëjtat dobësi. Rishikimi i Pang-ut dhe
      bashkautorëve për metodat e thella ndjek një logjikë të ngjashme [@pang2021]."""),
    p("""Mekanizmat e njohur janë më të shumtë se tri familjet e këtij studimi. Metodat e bazuara në
      densitet dhe në distancë, nga të cilat më e cituara është Local Outlier Factor, vlerësojnë
      densitetin rreth një pike ose largësinë e saj nga fqinjët dhe e shpallin atë anomali kur është
      dukshëm më e izoluar se fqinjësia e vet [@breunig2000]. Metodat që vlerësojnë shpërndarjen e
      secilës veçori veç e veç, si ECOD, supozojnë pavarësinë e veçorive dhe fitojnë shpejtësi prej
      saj [@li2022ecod], ndërsa vlerësimi robust i kovariancës e modelon normalitetin si një
      elipsoid të vetëm. Të gjitha këto metoda gjenden në biblioteka të unifikuara si PyOD
      [@zhao2019pyod]. Ato mbeten jashtë krahasimit, sepse studimi zgjedh thellësinë mbi tri
      algoritme në vend të gjerësisë mbi shumë metoda (nënkapitulli 1.4)."""),
    p("""Tri algoritmet e studimit përdorin tri mekanizma të ndryshëm. Isolation Forest mat sa lehtë
      izolohet një pikë, Autoencoder-i sa keq rindërtohet ajo, dhe One-Class SVM se në cilën anë të
      një kufiri të mësuar ndodhet. Meqë mekanizmat ndryshojnë, diferencat në rezultate mund të
      lidhen me mekanizmin dhe jo vetëm me implementimin."""),
]

_ALGORITMET = [
    h2("2.2", "Isolation Forest"),
    h3("2.2.1", "Formulimi"),
    p("""Isolation Forest, i propozuar nga Liu, Ting dhe Zhou, e kthen përmbys logjikën e zakonshme:
      në vend që të modelojë normalitetin dhe të masë largësinë prej tij, mat sa lehtë izolohet një
      pikë [@liu2008], [@liu2012]. Algoritmi ndërton pemë duke zgjedhur rastësisht një dimension dhe
      një pikë ndarjeje brenda intervalit të atij dimensioni, dhe vazhdon derisa çdo pikë të mbetet
      vetëm në një gjethe."""),
    p("""Pika e anomalisë llogaritet nga gjatësia mesatare e shtegut deri te izolimi, e normalizuar
      me gjatësinë e pritur c(n) të shtegut në një pemë binare kërkimi me n nyje:"""),
    eq("s(x, n) = 2^{−E[h(x)] / c(n)},   c(n) = 2H(n−1) − 2(n−1)/n"),
    p("""ku H është numri harmonik. Normalizimi e bën pikën të krahasueshme mes pemëve me thellësi
      të ndryshme dhe e mban atë në intervalin (0, 1), ku vlerat afër njëshit tregojnë izolim të
      lehtë. Në implementimin e këtij punimi merret vlera me shenjë të kundërt e funksionit të
      bibliotekës, që të ruhet konventa e përbashkët e studimit: vlerë më e lartë do të thotë më
      anormale."""),
    h3("2.2.2", "Vetitë dhe dobësitë e dokumentuara"),
    p("""Popullariteti i algoritmit vjen nga tri veti. Trajnimi është i lirë, sepse çdo pemë
      ndërtohet mbi një nën-mostër të vogël me madhësi fikse, pavarësisht nga numri i rreshtave. Nuk
      llogariten distanca, prandaj algoritmi nuk vuan nga problemet e metrikave në dimension të
      lartë. Dhe ka vetëm dy hiperparametra kryesorë: numrin e pemëve dhe madhësinë e
      nën-mostrës."""),
    p("""Literatura përshkruan edhe dy dobësi. E para është maskimi dhe mbytja (masking dhe
      swamping): grupimet e anomalive ose një bisht i gjatë i klasës normale e shtrembërojnë
      gjatësinë e shtegut. E dyta, më e rëndësishmja për këtë studim, lidhet me zgjedhjen e
      dimensionit të ndarjes. Dimensioni zgjidhet rastësisht, pa marrë parasysh sa informativ është,
      prandaj kur sinjali ndodhet vetëm në pak dimensione, shumica e ndarjeve shkojnë dëm. Kjo
      dobësi përmendet shpesh si hipotezë por matet rrallë; në Kapitullin 5 ajo matet duke numëruar
      ndarjet në pemët e trajnuara dhe duke i krahasuar me fuqinë diskriminuese të secilës
      kolonë."""),
    p("""Një veti e tretë, më pak e diskutuar, ka rëndësi të veçantë për këtë dataset. Ndarjet e
      Isolation Forest-it janë paralele me boshtet, prandaj algoritmi varet nga orientimi i sistemit
      koordinativ. Veçoritë V1 deri V28 janë komponentë kryesorë, pra janë tashmë të rreshtuara
      sipas drejtimeve me variancë maksimale, dhe ky rreshtim mund ta ndihmojë ose ta dëmtojë
      algoritmin. Kapitulli 5 e teston këtë duke trajnuar të njëjtin pyll mbi një kopje të
      rrotulluar rastësisht të të dhënave."""),
    h2("2.3", "Autoencoder-ët"),
    h3("2.3.1", "Rindërtimi si kriter"),
    p("""Ideja e rindërtimit është po aq e vjetër sa analiza e komponentëve kryesorë. Nëse të dhënat
      normale shtrihen pranë një nënhapësire me dimension të ulët, gabimi i projektimit dhe i
      rikthimit është i vogël për to dhe i madh për anomalitë. Shyu dhe bashkautorët e formalizuan
      këtë si një klasifikues të bazuar në komponentë kryesorë [@shyu2003]. Autoencoder-ët e
      zgjerojnë idenë në rastin jolinear: rrjeti mëson një kodim të ngjeshur dhe një dekodim, dhe
      gabimi i rindërtimit përdoret si pikë anomalie [@hinton2006], [@sakurada2014]."""),
    eq("L = (1/n) Σ ‖x_i − g(f(x_i))‖²,    s(x) = ‖x − g(f(x))‖²"),
    p("""Supozimi i nënkuptuar është se rrjeti, i trajnuar vetëm mbi transaksione normale, nuk do të
      mësojë funksionin identitet. Këtë e siguron vetëm ngushtica e hapësirës latente. Nëse
      dimensioni latent i afrohet atij të hyrjes, rrjeti mund t'i rindërtojë mirë edhe anomalitë,
      dhe pika humbet fuqinë dalluese. Dimensioni latent pra nuk është një hiperparametër i
      zakonshëm, por pjesë e vetë mekanizmit të zbulimit, dhe Kapitulli 5 e studion atë veçmas."""),
    h3("2.3.2", "Variantet dhe regularizimi"),
    p("""Literatura ofron disa mënyra për ta forcuar këtë mekanizëm. Autoencoder-i denoising
      trajnohet të rindërtojë hyrjen e pastër nga një version i zhurmshëm i saj, gjë që e shtyn
      rrjetin të mësojë strukturën e qëndrueshme të të dhënave dhe jo hollësitë. Dropout dhe weight
      decay e kufizojnë kapacitetin efektiv të rrjetit në të njëjtin drejtim. Ndikim ka edhe
      funksioni i humbjes: humbja kuadratike u jep peshë të madhe devijimeve të mëdha, ndërsa humbja
      absolute dhe ajo e Huber-it janë më robuste ndaj vlerave ekstreme që ndodhen tashmë në të
      dhënat e trajnimit."""),
    p("""Variantet probabilistike shkojnë më tej. Autoencoder-i variacional e shtyn kodimin latent
      drejt një shpërndarjeje të njohur dhe lejon që pika e anomalisë të llogaritet me kufirin e
      poshtëm të evidencës ose me probabilitetin e rindërtimit [@kingma2014]; modelet hibride
      shtojnë mbi hapësirën latente një model densiteti që mësohet bashkë me ngjeshjen. Këto
      variante nuk hyjnë në krahasimin kryesor, sepse studimi përqendrohet te autoencoder-i
      standard, por janë drejtime të natyrshme zgjerimi."""),
    h3("2.3.3", "Lidhja me analizën e komponentëve kryesorë"),
    note("""Për këtë dataset lidhja ka edhe rëndësi praktike. Veçoritë V1 deri V28 janë vetë
      komponentë kryesorë, prandaj një detektor linear rindërtimi mbi një nënhapësirë PCA nuk është
      thjesht një model bazë i dobët, por niveli minimal i gjithë familjes së rindërtimit. Një
      autoencoder jolinear që nuk e kalon këtë nivel nuk ka nxjerrë asgjë përtej asaj që projeksioni
      linear e bënte tashmë të dukshme. Për këtë arsye projeksioni linear përfshihet në studim si
      ablacion i autoencoder-it, jo si detektor i katërt."""),
    h2("2.4", "One-Class SVM"),
    h3("2.4.1", "Formulimi"),
    p("""One-Class SVM i Schölkopf-it dhe bashkautorëve kërkon një hiperplan që i ndan të dhënat nga
      origjina në hapësirën e veçorive të kernelit, me distancë sa më të madhe [@scholkopf2001].
      Problemi i optimizimit është"""),
    eq("min ½‖w‖² + (1/νn)Σξ_i − ρ,   ⟨w, φ(x_i)⟩ ≥ ρ − ξ_i,  ξ_i ≥ 0"),
    p("""ku ν ∈ (0, 1] është njëkohësisht kufi i sipërm për pjesën e pikave që mbeten jashtë kufirit
      dhe kufi i poshtëm për pjesën e vektorëve mbështetës. Për shkak të kësaj vetie të dyfishtë, ν
      është parametri më i interpretueshëm i metodës dhe zakonisht vendoset pranë normës së pritur
      të kontaminimit. Formulimi i Tax-it dhe Duin-it, Support Vector Data Description, kërkon
      sferën më të vogël që i përfshin të dhënat; me kernel gausian dy formulimet janë ekuivalente
      [@tax2004]."""),
    h3("2.4.2", "Shkallëzueshmëria si kufizim praktik"),
    p("""Kostoja e trajnimit të një makine me kernel rritet të paktën në mënyrë kuadratike me numrin
      e mostrave, kështu që metoda nuk mund të zbatohet drejtpërsëdrejti mbi qindra mijëra rreshta.
      Literatura ofron dy rrugë: nën-mostrimin e të dhënave të trajnimit ose përafrimin e kernelit
      me metoda si Nyström ose me variante stokastike. Të dyja janë kompromise, dhe kostoja e tyre
      duhet matur e jo supozuar. Ky punim zgjedh nën-mostrimin, sepse kështu ruhet metoda ekzakte pa
      përafrim të kernelit, dhe në Kapitullin 5 mat sa kushton ky kompromis me një kurbë të mësuari
      deri në 80 000 transaksione."""),
    p("""Formulimi ka edhe një pasojë operacionale. Kostoja e inferencës varet nga numri i vektorëve
      mbështetës, i cili nga ana e vet varet nga ν. Kështu i njëjti hiperparametër që përcakton sa i
      ngushtë është kufiri përcakton edhe vonesën e inferencës, prandaj të dyja duhen raportuar
      bashkë."""),
    h2("2.5", "Modeli bazë supervised"),
    p("""Regresioni Logjistik, i cili shërben si model bazë, nuk mund të trajnohet vetëm mbi
      transaksione normale si detektorët, sepse ka nevojë për etiketa të të dy klasave. Literatura e
      zgjidh këtë duke e trajtuar modelin supervised si kufi të sipërm që arrihet kur etiketat janë
      në dispozicion, jo si konkurrent të barabartë. Bhattacharyya dhe bashkautorët bënë një nga
      krahasimet e para sistematike të metodave supervised për këtë problem, mbi të dhëna reale
      transaksionesh [@bhattacharyya2011]."""),
    p("""Ky punim ndjek të njëjtën logjikë. Regresioni logjistik trajnohet mbi gjithë dritaren e
      trajnimit me etiketat e saj dhe shënohet gjithmonë si referencë supervised. Ai nuk konkurron
      me detektorët; shërben për të matur sa vlejnë etiketat historike."""),
]

_DOMENI = [
    h2("2.6", "Zbulimi i mashtrimeve me karta krediti"),
    h3("2.6.1", "Karakteristikat e domenit"),
    p("""Dal Pozzolo dhe bashkautorët, në një punim që përmbledh përvojën e bashkëpunimit me një
      procesor real pagesash, veçojnë tri tipare që e dallojnë këtë domen nga klasifikimi i
      zakonshëm [@dalpozzolo2014]: çekuilibrin ekstrem të klasave; vonesën e verifikimit, sepse
      etiketat mbërrijnë vonë dhe vetëm për një pjesë të transaksioneve; dhe zhvendosjen e konceptit
      (concept drift), sepse mashtruesit përshtaten ndaj kontrolleve dhe shpërndarja e klasës
      pozitive ndryshon me kohën."""),
    p("""Në një punim të mëvonshëm, të njëjtët autorë propozojnë një modelim që e merr parasysh
      vonesën e verifikimit dhe tregojnë se vlerësimi që e injoron atë e mbivlerëson performancën
      [@dalpozzolo2018]. Ky punim nuk përdor rimostrim, në mënyrë që shpërndarja e vëzhguar të
      mbetet e paprekur dhe pragu i alarmit të mund të lexohet drejtpërsëdrejti mbi trafikun
      real."""),
    p("""Një drejtim i rëndësishëm i punës së aplikuar është ndërtimi i veçorive me agregim. Whitrow
      dhe bashkautorët treguan se agregimi i transaksioneve të një llogarie mbi dritare kohore e
      përmirëson ndjeshëm zbulimin [@whitrow2009], dhe Bahnsen me bashkautorë e zgjeruan këtë me
      veçori periodike të sjelljes së mbajtësit [@bahnsen2016]. Jurgovsky dhe bashkautorët e
      trajtuan problemin si klasifikim sekuencash me rrjete rekurrente [@jurgovsky2018]. Të gjitha
      këto qasje kërkojnë identifikuesin e kartës, i cili mungon në dataset-in publik të përdorur
      këtu."""),
    h3("2.6.2", "Punimet mbi dataset-in ULB"),
    p("""Dataset-i i publikuar nga grupi Machine Learning i Université Libre de Bruxelles është bërë
      standardi praktik për këtë problem [@ulb_dataset]. Ai përmban 284 807 transaksione nga dy ditë
      të shtatorit 2013, nga të cilat 492 janë mashtrime, dhe 28 nga 30 veçoritë janë komponentë
      kryesorë të anonimizuar."""),
    p("""Punimet që e përdorin janë të shumta, por cilësia e tyre metodologjike ndryshon shumë. Një
      pjesë e mirë raporton vlera shumë të larta të AUC-ROC, të cilat, siç shpjegohet në
      nënkapitullin 2.8, thonë pak në këtë nivel çekuilibri. Një pjesë tjetër përdor ndarje të
      rastësishme, ku transaksione të së njëjtës periudhë shpërndahen njëkohësisht në trajnim dhe në
      test. Kapitulli 5 mat sa i fryn rezultatet kjo praktikë."""),
    p("""Manuali praktik i Le Borgne-s dhe bashkautorëve është ndër burimet e pakta që e trajton
      riprodhueshmërinë si kërkesë qendrore dhe e diskuton hapur ndarjen kohore [@leborgne2022]. Ai
      rekomandon vlerësim me ndarje kohore dhe me vonesë verifikimi, që është edhe drejtimi i
      ndjekur këtu."""),
    h3("2.6.3", "Kombinimi i qasjes supervised me atë unsupervised"),
    p("""Carcillo dhe bashkautorët provuan pikët e anomalisë nga metodat unsupervised si veçori
      shtesë për një klasifikues supervised dhe raportuan përmirësim [@carcillo2021]. Rezultati
      sugjeron se metodat unsupervised mbartin informacion plotësues edhe kur, të marra vetëm,
      mbeten shumë pas një modeli supervised. Analiza e gabimeve në Kapitullin 5 e mbështet këtë
      nga një kënd tjetër: shumica e mashtrimeve që nuk i kap asnjë detektor unsupervised kapen nga
      referenca supervised."""),
    h2("2.7", "Arkitekturat për përpunim rrjedhash"),
    h3("2.7.1", "Apache Kafka"),
    p("""Kafka u prezantua nga Kreps, Narkhede dhe Rao si sistem i shpërndarë mesazhesh për
      përpunimin e log-eve, i ndërtuar rreth një abstraksioni të vetëm: një log i qëndrueshëm, i
      ndarë në particione, ku të dhënat vetëm shtohen [@kreps2011]. Ky abstraksion i thjeshtë e bëri
      Kafka-n shtyllë të arkitekturave moderne të të dhënave. Çdo konsumator mban vetë pozicionin e
      tij në log, kështu që konsumatorët janë të pavarur nga njëri-tjetri dhe riprodhimi i
      historikut është një operacion i zakonshëm [@kleppmann2017]. Kjo veti përdoret në këtë punim
      për të simuluar një rrjedhë nga të dhëna historike."""),
    p("""Modaliteti KRaft e zëvendëson ZooKeeper-in me një protokoll konsensusi të brendshëm dhe e
      thjeshton vendosjen. Për një prototip kërkimor me një broker kjo do të thotë një shërbim më
      pak për t'u konfiguruar e mirëmbajtur, prandaj u zgjodh ky modalitet."""),
    h3("2.7.2", "Platformat alternative dhe modelet e përpunimit"),
    p("""Apache Flink ofron një motor të përbashkët për përpunim rrjedhash dhe grupesh, me semantikë
      të qartë kohore të ndërtuar rreth dallimit mes kohës së eventit dhe kohës së përpunimit
      [@carbone2015], ndërsa Spark Streaming e trajton rrjedhën si varg mikro-grupesh. Dallimi mes
      dy kohëve vlen edhe për këtë prototip: koha e eventit është kolona Time e dataset-it, ndërsa
      koha e përpunimit është ora e sistemit gjatë riprodhimit, dhe të dyja masin gjëra të
      ndryshme."""),
    p("""Për zbulimin e mashtrimeve mbi rrjedha, punimi më i afërt me këtë është SCARFF i Carcillo-s
      dhe bashkautorëve, një kornizë e shkallëzueshme mbi Kafka, Spark dhe Cassandra
      [@carcillo2018]. SCARFF përqendrohet te shkallëzueshmëria dhe te integrimi i etiketave të
      vonuara, ndërsa ky punim te vlerësimi pa rrjedhje informacioni dhe te studimi i thelluar i tri
      algoritmeve."""),
    h3("2.7.3", "Mësimi mbi rrjedha"),
    p("""Literatura e mësimit mbi rrjedha ka traditën e vet të vlerësimit. Gama, Sebastião dhe
      Rodrigues argumentojnë se për të dhëna që mbërrijnë sipas radhës, protokolli i duhur është
      vlerësimi prekuencial (testo pastaj trajno), sepse ndjek rendin në të cilin informacioni bëhet
      i disponueshëm [@gama2013]. Protokolli rolling-origin i këtij punimi bazohet në të njëjtën
      ide, por për modele që trajnohen në grup dhe jo në mënyrë inkrementale."""),
]

_METODOLOGJIA = [
    h2("2.8", "Metodologjia e vlerësimit"),
    h3("2.8.1", "Metrikat nën çekuilibër ekstrem"),
    p("""Kur klasa pozitive përbën 0.17% të të dhënave, saktësia nuk ka vlerë: një model që i shpall
      të gjitha transaksionet legjitime arrin saktësi 99.83%. Më pak e dukshme, por po aq e
      rëndësishme, është problematika e AUC-ROC. Davis dhe Goadrich treguan se kurbat ROC dhe
      precision-recall janë të lidhura, por se një algoritëm që dominon në hapësirën ROC nuk dominon
      domosdoshmërisht në hapësirën precision-recall [@davis2006]. Saito dhe Rehmsmeier treguan
      empirikisht se ROC jep një pamje tepër optimiste në të dhëna të çekuilibruara, sepse norma e
      pozitivëve të rremë ka në emërues numrin e madh të negativëve dhe mbetet e vogël edhe kur
      alarmet e rreme janë shumë më tepër se ato të vërteta [@saito2015]."""),
    p("""Për këto arsye metrika kryesore në këtë punim është Average Precision (AP), ndërsa AUC-ROC
      raportohet vetëm për krahasim me literaturën. Rezultatet e Kapitullit 5 e tregojnë qartë
      dallimin mes dy metrikave."""),
    p("""As AP nuk e pasqyron plotësisht mënyrën se si përdoret një detektor. Një ekip hetimesh nuk
      e shqyrton gjithë renditjen, por vetëm aq alarme sa i lejon kapaciteti. Prandaj raportohen
      edhe metrika për një buxhet të fiksuar alarmesh, sa mashtrime dhe sa vlerë monetare kapen
      brenda tij, që një përmirësim në renditje të shprehet në njësi që ekipi operacional i
      njeh."""),
    h3("2.8.2", "Ndarja kohore dhe rrjedhja e informacionit"),
    p("""Bergmeir dhe Benítez analizuan validimin e kryqëzuar për të dhëna me strukturë kohore dhe
      treguan se ndarja e rastësishme jep vlerësime të anshme, sepse modeli trajnohet me të dhëna që
      në realitet do të vinin pas atyre të testimit [@bergmeir2012]. Origjina rrëshqitëse (rolling
      origin), ku modeli ritrajnohet në pika prerjeje të njëpasnjëshme dhe testohet gjithmonë mbi
      periudhën që vjen pas, e shmang këtë anshmëri dhe është protokolli që ndjek ky punim."""),
    p("""Në zbulimin e mashtrimeve rrjedhja e informacionit mund të ndodhë në tri mënyra, dhe të
      treja trajtohen në implementimin e këtij punimi. E para është përmes ndarjes: përzierja e
      rastësishme lejon që transaksione të së njëjtës periudhë, madje të të njëjtit sulm, të
      përfundojnë njëkohësisht në trajnim dhe në test. E dyta është përmes paraprocesimit: një
      skalues i përshtatur mbi gjithë dataset-in lejon që statistikat e testit të ndikojnë në
      trajnim. E treta, më e nënvlerësuara, është përmes pragut: kur pragu i alarmit zgjidhet duke
      maksimizuar F1 mbi të dhënat e testit, rezultati i raportuar është një kufi i sipërm që në
      praktikë nuk arrihet."""),
    h3("2.8.3", "Vonesa e verifikimit dhe pasojat e saj"),
    p("""Në zbulimin e mashtrimeve etiketa nuk vjen bashkë me shembullin, por javë më vonë dhe vetëm
      për një pjesë të tyre. Kjo përcaktoi disa zgjedhje të dizajnit. Meqë etiketa e sotme nuk
      ekziston, asnjë komponent që vepron mbi rrjedhën aktuale nuk mund të varet prej saj: as
      modeli, as skaluesi, as pragu. Nga ana tjetër, etiketat e së kaluarës ekzistojnë, dhe
      përjashtimi i tyre do të ishte një supozim i panevojshëm i ashpër për një bankë. Kufiri që
      vihet këtu, me etiketa historike por pa etiketa aktuale, është ai që vonesa e verifikimit
      imponon në praktikë."""),
    h3("2.8.4", "Krahasimi statistikor i algoritmeve"),
    p("""Demšar-i, në punimin që mbetet referenca standarde për krahasimin statistikor të
      algoritmeve mbi disa bashkësi të dhënash, rekomandon për krahasimet dyshe testin joparametrik
      të Wilcoxon-it për çifte [@demsar2006], [@wilcoxon1945]. Kur bëhen disa krahasime
      njëkohësisht, p-vlerat duhen korrigjuar; procedura e Holm-it është më e fuqishme se ajo e
      Bonferroni-t dhe e kontrollon njësoj gabimin [@holm1979]."""),
    p("""Një çështje që literatura e aplikuar shpesh e anashkalon është fuqia statistikore. Me N
      njësi vëzhgimi, p-vlera më e vogël që mund të japë testi dypalësh i Wilcoxon-it është 2/2^N.
      Me gjashtë njësi, asnjë krahasim nuk e kalon korrigjimin e Holm-it kur testohen më shumë se
      një hipotezë, sado i qëndrueshëm të jetë rezultati. Numri i fold-eve në këtë punim u zgjodh
      duke pasur parasysh këtë kufi, dhe krahasimet u fiksuan në kod para se të shiheshin
      rezultatet. Aty ku nevojitet një interval besimi mbi një bashkësi të vetme testimi, ai
      llogaritet me bootstrap [@efron1993]."""),
    h2("2.9", "Paraprocesimi dhe gjeometria e të dhënave"),
    p("""Çdo detektor i bazuar në distancë, densitet ose rindërtim e merr nocionin e largësisë nga
      paraprocesimi që zbatohet para tij, megjithatë skaluesi zakonisht zgjidhet një herë dhe nuk
      rishikohet më. Në zbulimin e anomalive kjo zgjedhje ka një hollësi: skaluesi duhet përshtatur
      mbi një dritare trajnimi që i përmban ende anomalitë, sepse në momentin e vendosjes askush nuk
      i njeh ato. Statistikat që përshkruajnë shpërndarjen normale janë pra të ndotura nga vetë
      vlerat ekstreme që sistemi duhet të nxjerrë në pah, dhe për këtë arsye alternativat robuste
      dhe ato të bazuara në rang duhen krahasuar empirikisht."""),
    p("""Një drejtim tjetër, më pak i përdorur në punët e aplikuara, është shikimi i gjeometrisë së
      të dhënave para modelimit: sa larg klasës normale ndodhen vlerat e jashtëzakonshme dhe sa
      mbivendosen dy klasat. Aggarwal e konsideron këtë hap paraprak të domosdoshëm në analizën e
      vlerave të jashtëzakonshme [@aggarwal2017]. Në këtë punim ai bëhet në analizën eksploruese të
      Kapitullit 4, me distancën e çdo transaksioni nga fqinjët legjitimë më të afërt."""),
    h2("2.10", "Zhvendosja e konceptit"),
    p("""Rishikimi i Gama-s dhe bashkautorëve për përshtatjen ndaj zhvendosjes së konceptit dallon
      zhvendosjen e shpërndarjes së hyrjeve nga zhvendosja e lidhjes mes hyrjeve dhe daljes, dhe
      përmbledh detektorët që e sinjalizojnë atë gjatë punës [@gama2014]."""),
    p("""Në punët e aplikuara shpesh përzihet dallimi mes zhvendosjes së popullatës normale dhe
      zhvendosjes së popullatës së anomalive, ndonëse pasojat janë të ndryshme. E para e bën të
      vjetëruar modelin e normalitetit dhe zgjidhet me ritrajnim mbi të dhëna të reja pa etiketa. E
      dyta nuk e prek modelin e normalitetit; anomalitë thjesht bëhen më pak të dallueshme, dhe
      ritrajnimi nuk ndihmon. Shtojca E e mat zhvendosjen veç e veç për këto dy popullata."""),
    h2("2.11", "Ansamblet e detektorëve"),
    p("""Zimek, Campello dhe Sander shtruan pyetjet themelore për ansamblet në zbulimin
      unsupervised: si normalizohen pikë me shkallë krejt të ndryshme, dhe si sigurohet diversiteti
      kur nuk ka etiketa për të matur gabimin [@zimek2014]. Aggarwal dhe Sathe analizuan teorikisht
      kompromisin anshmëri-variancë për ansamblet dhe treguan se mesatarizimi e ul variancën vetëm
      kur anëtarët gabojnë ndryshe nga njëri-tjetri [@aggarwal2015]."""),
    p("""Rayana dhe Akoglu argumentuan, siç e thotë edhe titulli i punimit të tyre, se më pak është
      më shumë: përzgjedhja e kujdesshme e anëtarëve jep më shumë se kombinimi i të gjithë
      detektorëve [@rayana2016]. Rezultati i këtij punimi shkon në të njëjtin drejtim, me një
      përfundim më të kufizuar, dhe analiza e gabimeve në nivel transaksioni tregon arsyen."""),
    h2("2.12", "Boshllëqet e identifikuara dhe pozicionimi i punimit"),
    p("""Nga ky rishikim dalin tri boshllëqe, mbi të cilat ndërtohet kontributi i punimit:"""),
    bullets(
        [
            "Studimet për këtë dataset i analizojnë modelet kryesisht në mënyrë statike, mbi një "
            "ndarje të vetme, dhe shpesh testojnë një algoritëm të vetëm unsupervised. Nuk u gjet "
            "një krahasim i Isolation Forest-it, Autoencoder-it dhe One-Class SVM-së mbi të "
            "njëjtën infrastrukturë Kafka, "
            "bashkë me një referencë supervised, me vonesë të matur dhe me një protokoll "
            "rolling-origin ku çdo fold rindërton gjithë zinxhirin e paraprocesimit dhe të "
            "pragjeve.",
            "Fryrja e rezultateve nga ndarja e rastësishme përmendet shpesh si rrezik, por rrallë "
            "matet mbi të njëjtat të dhëna dhe të njëjtat modele.",
            "Studimet për ansamblet në zbulimin unsupervised raportojnë kryesisht rezultate "
            "pozitive; rezultatet negative, po aq informuese kur shpjegohen, publikohen rrallë.",
        ]
    ),
    p("""Punimi i trajton të tri. Përveç tyre, ai shton një kontribut praktik që nuk vjen nga
      literatura, por nga një problem i hasur gjatë implementimit: paqëndrueshmëria e ngarkesës së
      hetimeve kur pragu mbahet fiks mbi një rrjedhë që ndryshon, dhe zgjidhja e saj me një prag
      adaptiv me dritare rrëshqitëse."""),
]

BLOCKS = _HYRJE + _ALGORITMET + _DOMENI + _METODOLOGJIA

"""Kapitulli 2 — SHQYRTIMI I LITERATURËS."""

from blocks import bullets, eq, h1, h2, h3, note, p

_HYRJE = [
    h1("2", "Shqyrtimi i literaturës"),
    p("""Ky kapitull rishikon literaturën në pesë drejtime që përcaktojnë hapësirën e këtij
      punimi: përkufizimin dhe taksonominë e zbulimit të anomalive, tri algoritmet
      unsupervised që trajton studimi, punën specifike mbi zbulimin e mashtrimeve me karta,
      arkitekturat për përpunim rrjedhash, dhe metodologjinë e vlerësimit. Drejtimi i fundit
      merr më shumë hapësirë sesa është zakon në punime të kësaj natyre, sepse gjetja
      qendrore e studimit është metodologjike: mënyra si vlerësohet një detektor e ndryshon
      përfundimin se cili detektor është më i mirë."""),
    p("""Shqyrtimi është i thelluar te tri algoritmet e propozimit dhe nuk përpiqet të mbulojë
      gjithë fushën e detektorëve unsupervised. Kjo është zgjedhje e vetëdijshme. Një listë e
      gjatë metodash të përshkruara sipërfaqësisht nuk ndihmon në interpretimin e
      rezultateve; ndërsa njohja e hollësishme e mekanizmit, e supozimeve dhe e dobësive të
      dokumentuara të secilit prej tri algoritmeve është pikërisht ajo që lejon shpjegimin e
      renditjes që del në Kapitullin 5."""),
    h2("2.1", "Zbulimi i anomalive: përkufizimi dhe taksonomia"),
    h3("2.1.1", "Çfarë është një anomali"),
    p("""Përkufizimi klasik i Hawkins-it e përshkruan anomalinë si një vëzhgim që devijon aq
      shumë nga vëzhgimet e tjera sa ngjall dyshimin se është gjeneruar nga një mekanizëm i
      ndryshëm [@hawkins1980]. Ky përkufizim është i dobishëm sepse e zhvendos vëmendjen nga
      "e rrallë" te "e gjeneruar ndryshe". Të dyja nuk përputhen domosdoshmërisht: një
      transaksion me vlerë shumë të lartë është i rrallë por mund të jetë krejtësisht
      legjitim, ndërsa një mashtrim testues me vlerë një euro mund të duket krejt i
      zakonshëm."""),
    p("""Chandola, Banerjee dhe Kumar, në rishikimin që mbetet referenca standarde e fushës,
      dallojnë tri lloje anomalish: pikësore, kontekstuale dhe kolektive [@chandola2009]. Një
      anomali pikësore është një instancë e vetme që bie jashtë normës. Një anomali
      kontekstuale është normale në përgjithësi por jo në kontekstin e vet, si për shembull
      një blerje prej dyqind eurosh në orën tre të mëngjesit për një mbajtës që nuk blen
      kurrë natën. Një anomali kolektive është një sekuencë instancash secila prej të cilave
      duket normale, por bashkësia e tyre nuk është."""),
    p("""Ky dallim ka pasoja të drejtpërdrejta për studimin. Dataset-i i përdorur këtu nuk
      përmban identifikues të kartës, prandaj konteksti individual i mbajtësit nuk mund të
      rindërtohet dhe dy nga tri llojet e anomalive mbeten jashtë mundësive të modelimit. Ky
      është kufizim i vërtetë i studimit, jo zgjedhje, dhe trajtohet përsëri në diskutimin e
      kufizimeve."""),
    h3("2.1.2", "Mekanizmat e vendimit"),
    p("""Rishikimet më të fundit, veçanërisht ai unifikues i Ruff-it dhe bashkautorëve, i
      organizojnë metodat sipas mekanizmit me të cilin përcaktohet se çfarë është normale
      [@ruff2021]. Ky organizim është më i dobishëm sesa ndarja e zakonshme mes metodave
      klasike dhe atyre të thella, sepse dy metoda nga epoka të ndryshme mund të ndajnë të
      njëjtin mekanizëm dhe të kenë të njëjtat dobësi. Rishikimi i Pang-ut dhe bashkautorëve
      mbi metodat e thella ndjek një logjikë të ngjashme organizimi [@pang2021]."""),
    p("""Peizazhi i plotë i mekanizmave është dukshëm më i gjerë se tri familjet e këtij
      studimi. Metodat e bazuara në densitet dhe në distancë, ku përfaqësuesi më i cituar është
      Local Outlier Factor, e vlerësojnë densitetin lokal rreth një pike ose largësinë e saj
      nga fqinjët më të afërt, dhe e shpallin atë anomali kur ajo është dukshëm më e izoluar
      sesa fqinjësia e vet [@breunig2000]. Metodat statistikore me histograme ose me kopula e
      supozojnë pavarësinë e veçorive dhe e fitojnë shpejtësinë prej saj [@li2022ecod], ndërsa
      vlerësimi robust i kovariancës e modelon normalitetin si një elipsoid të vetëm.
      Bashkësia e këtyre metodave është e disponueshme në biblioteka të unifikuara si PyOD
      [@zhao2019pyod], çka e bën testimin e dhjetëra detektorëve teknikisht të lehtë."""),
    p("""Pikërisht kjo lehtësi teknike përbën një rrezik metodologjik. Krahasimi i dhjetëra
      detektorëve mbi një dataset të vetëm e shumëfishon numrin e testeve statistikore, e
      dobëson korrigjimin për krahasime të shumëfishta deri në pikën ku asnjë dallim nuk mbetet
      i zbulueshëm, dhe e zëvendëson kuptimin e mekanizmit me renditjen e emrave. Ky punim
      ndjek rrugën e kundërt: tri familje, të zgjedhura sepse mekanizmat e tyre janë të
      ndryshëm, dhe secila e studiuar në thellësi. Arsyetimi i plotë i kësaj zgjedhjeje jepet
      në nënkapitullin 2.13."""),
    p("""Tri algoritmet e këtij studimi u përkasin tri mekanizmave të ndryshëm, gjë që nuk
      është rastësi e propozimit por përparësi metodologjike. Isolation Forest vendos duke
      matur sa lehtë izolohet një pikë. Autoencoder-i vendos duke matur sa keq rindërtohet
      ajo. One-Class SVM vendos duke matur nga cila anë e një kufiri të mësuar ndodhet. Meqë
      mekanizmat janë të ndryshëm, çdo dallim në rezultate mund t'i atribuohet mekanizmit dhe
      jo thjesht implementimit."""),
]

_ALGORITMET = [
    h2("2.2", "Isolation Forest"),
    h3("2.2.1", "Formulimi"),
    p("""Isolation Forest, i propozuar nga Liu, Ting dhe Zhou, e përmbys logjikën e zakonshme.
      Në vend që të modelojë normalitetin dhe të masë largësinë prej tij, ai mat sa lehtë
      izolohet një pikë [@liu2008], [@liu2012]. Algoritmi ndërton pemë duke zgjedhur në
      mënyrë uniforme të rastësishme një dimension dhe një pikë ndarjeje brenda intervalit të
      atij dimensioni, dhe përsërit derisa çdo pikë të mbetet e vetme në një gjethe."""),
    p("""Pika e anomalisë del nga gjatësia mesatare e shtegut deri te izolimi, e normalizuar
      me gjatësinë e pritur të shtegut c(n) në një pemë kërkimi binare me n nyje:"""),
    eq("s(x, n) = 2^{−E[h(x)] / c(n)},   c(n) = 2H(n−1) − 2(n−1)/n"),
    p("""ku H është numri harmonik. Normalizimi e bën pikën të krahasueshme mes pemëve me
      thellësi të ndryshme dhe e kufizon atë në intervalin (0, 1), ku vlerat afër njëshit
      tregojnë izolim të lehtë. Në implementimin e këtij punimi pika merret me shenjë të
      kundërt të funksionit të bibliotekës, që të respektohet konventa e vetme e studimit:
      vlerë më e lartë do të thotë më anormale."""),
    h3("2.2.2", "Vetitë dhe dobësitë e dokumentuara"),
    p("""Popullariteti i algoritmit vjen nga tri veti. Kompleksiteti i trajnimit është
      nënlinear në numrin e mostrave, sepse çdo pemë ndërtohet mbi një nën-mostër të vogël me
      madhësi të fiksuar. Nuk kërkohet llogaritje distancash, prandaj nuk vuan nga problemet
      e zakonshme të metrikave në dimension të lartë. Dhe ka vetëm dy hiperparametra
      kryesorë, numrin e pemëve dhe madhësinë e nën-mostrës."""),
    p("""Literatura ka dokumentuar edhe dy dobësi sistematike. E para është maskimi dhe
      mbytja, ku prania e grupimeve të anomalive ose e një bishti të gjatë të klasës normale
      e shtrembëron gjatësinë e shtegut. E dyta, më e rëndësishme për këtë studim, është
      zgjedhja e dimensionit të ndarjes. Dimensioni zgjidhet në mënyrë uniforme, pa asnjë
      preferencë për informativitetin, prandaj në hapësira ku vetëm pak dimensione mbajnë
      sinjal shumica e ndarjeve harxhohen. Ky mekanizëm përmendet shpesh si hipotezë, por
      matet rrallë; Kapitulli 5 e mat drejtpërdrejt duke hapur pemët e përshtatura dhe duke
      krahasuar shpërndarjen e ndarjeve me fuqinë diskriminuese të secilës kolonë."""),
    p("""Një veti e tretë, më pak e diskutuar, ka rëndësi të veçantë për dataset-in e këtushëm.
      Ndarjet e Isolation Forest-it janë paralele me boshtet, prandaj algoritmi është i
      ndjeshëm ndaj orientimit të sistemit koordinativ. Veçoritë V1 deri V28 janë komponentë
      kryesorë, pra tashmë të rreshtuar me drejtimet e variancës maksimale, dhe kjo përputhje
      mund ta ndihmojë ose ta dëmtojë algoritmin. Kapitulli 5 e teston këtë duke ripërshtatur
      të njëjtin pyll mbi një kopje të rrotulluar rastësisht të të dhënave."""),
    h2("2.3", "Autoencoder-ët"),
    h3("2.3.1", "Rindërtimi si kriter"),
    p("""Ideja e rindërtimit është e vjetër sa vetë analiza e komponentëve kryesorë. Nëse të
      dhënat normale shtrihen afër një nënhapësire me dimension të ulët, atëherë gabimi i
      projektimit dhe i rikthimit është i vogël për to dhe i madh për anomalitë. Shyu dhe
      bashkautorët e formalizuan këtë si klasifikues të bazuar në komponentë kryesorë
      [@shyu2003]. Autoencoder-ët e zgjerojnë idenë në rastin jolinear: rrjeti mëson një
      kodim të ngjeshur dhe një dekodim, dhe gabimi i rindërtimit shërben si pikë anomalie
      [@hinton2006], [@sakurada2014]."""),
    eq("L = (1/n) Σ ‖x_i − g(f(x_i))‖²,    s(x) = ‖x − g(f(x))‖²"),
    p("""Supozimi i heshtur këtu është se rrjeti, i trajnuar vetëm mbi transaksione normale,
      nuk do të mësojë funksionin identitet. Kjo garantohet vetëm nga ngushtica e hapësirës
      latente. Nëse dimensioni latent i afrohet atij hyrës, rrjeti mund t'i rindërtojë mirë
      edhe anomalitë dhe pika e humbet fuqinë dalluese. Zgjedhja e dimensionit latent nuk
      është pra thjesht një hiperparametër, por vetë mekanizmi i zbulimit, dhe Kapitulli 5 e
      studion atë përballë dimensionit të brendshëm të matur të klasës normale."""),
    h3("2.3.2", "Variantet dhe regullarizimi"),
    p("""Literatura ofron disa mënyra për ta forcuar këtë mekanizëm. Autoencoder-i denoising
      trajnohet për të rindërtuar hyrjen e pastër nga një version i korruptuar me zhurmë, gjë
      që e detyron rrjetin të mësojë strukturën e qëndrueshme të të dhënave në vend të
      detajeve. Dropout dhe weight decay veprojnë në të njëjtin drejtim duke kufizuar
      kapacitetin efektiv. Zgjedhja e funksionit të humbjes ndikon gjithashtu: humbja
      kuadratike i jep peshë të madhe devijimeve të mëdha, ndërsa humbja absolute ose ajo e
      Huber-it janë më robuste ndaj vlerave ekstreme që ndodhen tashmë në bashkësinë e
      trajnimit."""),
    p("""Variantet probabilistike shkojnë më tej. Autoencoder-i variacional rregullon kodimin
      latent drejt një shpërndarjeje të njohur dhe lejon pikëzim me kufirin e poshtëm të
      evidencës ose me probabilitetin e rindërtimit [@kingma2014]; modelet hibride e shtojnë
      mbi hapësirën latente edhe një model densiteti të mësuar njëkohësisht me ngjeshjen.
      Këto variante nuk janë pjesë e krahasimit kryesor të këtij punimi, sepse
      propozimi emërton autoencoder-in standard, por përmenden si drejtime të natyrshme
      zgjerimi."""),
    h3("2.3.3", "Lidhja me analizën e komponentëve kryesorë"),
    note("""Një hollësi e dataset-it e bën këtë lidhje më shumë se teorike. Veçoritë V1 deri
      V28 janë vetë komponentë kryesorë. Kjo do të thotë se një detektor linear rindërtimi
      mbi një nënhapësirë PCA nuk është thjesht një baseline e dobët, por pragu natyror i
      gjithë familjes së rindërtimit. Nëse një autoencoder jolinear nuk e tejkalon atë, ai
      nuk ka nxjerrë asgjë përtej asaj që projeksioni linear e kishte tashmë të dukshme. Për
      këtë arsye projeksioni linear përfshihet në studim, jo si konkurrent i katërt, por si
      ablacion i autoencoder-it."""),
    h2("2.4", "One-Class SVM"),
    h3("2.4.1", "Formulimi"),
    p("""One-Class SVM i Schölkopf-it dhe bashkautorëve kërkon një hiperplan që i ndan të
      dhënat nga origjina në hapësirën e veçorive me kernel, duke maksimizuar distancën
      [@scholkopf2001]. Problemi i optimizimit është"""),
    eq("min ½‖w‖² + (1/νn)Σξ_i − ρ,   ⟨w, φ(x_i)⟩ ≥ ρ − ξ_i,  ξ_i ≥ 0"),
    p("""ku ν ∈ (0, 1] është njëkohësisht kufi i sipërm për fraksionin e pikave jashtë kufirit
      dhe kufi i poshtëm për fraksionin e vektorëve mbështetës. Kjo veti e dyfishtë e bën ν
      parametrin e vetëm vërtet të interpretueshëm të metodës dhe shpjegon pse ai zakonshëm
      vendoset afër normës së pritur të kontaminimit. Formulimi ekuivalent i Tax-it dhe
      Duin-it, Support Vector Data Description, kërkon sferën më të vogël që i përmban të
      dhënat [@tax2004]."""),
    h3("2.4.2", "Shkallëzueshmëria si kufizim praktik"),
    p("""Kostoja e trajnimit të një makine me kernel rritet të paktën në mënyrë kuadratike me
      numrin e mostrave, gjë që e bën metodën të papërdorshme drejtpërdrejt mbi qindra mijëra
      rreshta. Literatura ofron dy rrugëdalje: nën-mostrimin e bashkësisë së trajnimit, ose
      përafrimin e kernelit me metoda si Nyström ose me variante stokastike. Të dyja janë
      kompromise, dhe të dyja kërkojnë që kostoja e tyre të matet e jo të supozohet. Ky punim
      zgjedh nën-mostrimin, sepse ai e ruan metodën ekzakte të emërtuar në propozim, dhe
      Kapitulli 5 e mat drejtpërdrejt sa kushton ai kompromis duke ndërtuar kurbën e të
      mësuarit deri në tetëdhjetë mijë transaksione."""),
    p("""Një pasojë e dytë e formulimit ka rëndësi operacionale. Kostoja e pikëzimit varet nga
      numri i vektorëve mbështetës të ruajtur, i cili nga ana e vet varet nga ν. Kështu i
      njëjti hiperparametër që rregullon ashpërsinë e kufirit rregullon edhe vonesën e
      inferencës, dhe të dyja duhen raportuar bashkë."""),
    h2("2.5", "Modeli baseline i mbikëqyrur"),
    p("""Propozimi kërkon njëkohësisht trajnim vetëm mbi transaksione normale dhe një baseline
      me Regresion Logjistik. Këto dy kërkesa janë në kundërshtim, sepse regresioni logjistik
      ka nevojë për etiketa. Literatura e zgjidh këtë kundërshti duke e trajtuar modelin e
      mbikëqyrur si kufi të sipërm të arritshëm nën disponueshmëri etiketash dhe jo si
      konkurrent të barabartë. Bhattacharyya dhe bashkautorët bënë një krahasim të hershëm e
      sistematik mes metodave të mbikëqyrura mbi këtë problem, mbi të dhëna reale
      transaksionesh [@bhattacharyya2011]."""),
    p("""Ky punim e ndjek të njëjtën logjikë. Regresioni logjistik trajnohet mbi të gjithë
      dritaren e trajnimit me etiketat e saj dhe raportohet gjithmonë i shënuar si referencë e
      mbikëqyrur. Roli i tij nuk është të konkurrojë, por të kuantifikojë vlerën e etiketave
      historike në njësi të matshme."""),
]

_DOMENI = [
    h2("2.6", "Zbulimi i mashtrimeve me karta krediti"),
    h3("2.6.1", "Karakteristikat e domenit"),
    p("""Dal Pozzolo dhe bashkautorët, në një punim që përmbledh mësimet nga bashkëpunimi me
      një procesor të vërtetë pagesash, identifikojnë tri veçori që e dallojnë këtë domen nga
      problemet e zakonshme të klasifikimit [@dalpozzolo2014]. E para është çekuilibri
      ekstrem. E dyta është vonesa e verifikimit: etiketat mbërrijnë me vonesë dhe vetëm për
      një nënbashkësi transaksionesh. E treta është zhvendosja e konceptit, sepse mashtruesit
      përshtaten ndaj kontrolleve dhe shpërndarja e klasës pozitive ndryshon me kalimin e
      kohës."""),
    p("""Në një punim të mëvonshëm, të njëjtët autorë propozojnë një modelim realist që e merr
      parasysh vonesën e verifikimit dhe tregojnë se vlerësimi që e injoron atë e mbivlerëson
      performancën [@dalpozzolo2018]. Ky punim nuk përdor ri-mostrim fare,
      zgjedhje që e mban të paprekur shpërndarjen e vëzhguar dhe që e bën pragun e alarmit të
      interpretueshëm drejtpërdrejt mbi trafikun real."""),
    p("""Një drejtim i rëndësishëm i punës aplikative është inxhinieria e veçorive përmes
      agregimit. Whitrow dhe bashkautorët treguan se agregimi i transaksioneve për llogari mbi
      dritare kohore e përmirëson ndjeshëm zbulimin [@whitrow2009], dhe Bahnsen me
      bashkautorë e zgjeruan këtë me veçori periodike të bazuara në sjelljen e mbajtësit
      [@bahnsen2016]. Jurgovsky dhe bashkautorët shkuan më tej, duke e trajtuar problemin si
      klasifikim sekuencash me rrjeta rekurrente [@jurgovsky2018]. Të gjitha këto qasje
      kërkojnë identifikuesin e kartës, i cili nuk ekziston në dataset-in publik të përdorur
      këtu."""),
    h3("2.6.2", "Punimet mbi dataset-in ULB"),
    p("""Dataset-i i publikuar nga grupi Machine Learning i Université Libre de Bruxelles është
      bërë standard de facto për këtë problem [@ulb_dataset]. Ai përmban 284,807 transaksione
      nga dy ditë të shtatorit 2013, prej të cilave 492 janë mashtruese, dhe 28 nga 30
      veçoritë janë komponentë kryesorë të anonimizuar."""),
    p("""Numri i punimeve që e përdorin është shumë i madh, por cilësia metodologjike ndryshon
      dukshëm. Një pjesë e konsiderueshme raporton vlera shumë të larta të AUC-ROC-së, të
      cilat, siç argumentohet në nënkapitullin 2.8, janë pothuajse pa vlerë informative në
      këtë nivel çekuilibri. Një pjesë tjetër përdor ndarje të rastësishme të të dhënave, gjë
      që lejon transaksione nga e njëjta periudhë të shpërndahen mes trajnimit dhe testimit.
      Kapitulli 5 e mat drejtpërdrejt sa i fryn rezultatet kjo praktikë."""),
    p("""Manuali praktik i Le Borgne-s dhe bashkautorëve meriton përmendje të veçantë sepse
      është ndër burimet e pakta që e trajton riprodhueshmërinë si kërkesë qendrore dhe që e
      diskuton hapur ndarjen kohore [@leborgne2022]. Ai rekomandon vlerësim me ndarje kohore
      dhe me vonesë verifikimi, pra pikërisht drejtimin që ndiqet këtu."""),
    h3("2.6.3", "Kombinimi i qasjes së mbikëqyrur dhe asaj unsupervised"),
    p("""Carcillo dhe bashkautorët hetuan nëse pikët e anomalisë të prodhuara nga metoda
      unsupervised mund të shërbejnë si veçori shtesë për një klasifikues të mbikëqyrur, dhe
      raportuan përmirësim [@carcillo2021]. Ky rezultat është i rëndësishëm për interpretimin
      e këtij punimi, sepse sugjeron se metodat unsupervised mbajnë informacion plotësues edhe
      kur, të marra vetëm, mbeten dukshëm nën një model të mbikëqyrur. Analiza e gabimeve në
      Kapitullin 5 e mbështet këtë nga një kënd tjetër, duke treguar se mashtrimet që
      detektorët unsupervised nuk i arrijnë kapen kryesisht nga referenca e mbikëqyrur."""),
    h2("2.7", "Arkitekturat për përpunim rrjedhash"),
    h3("2.7.1", "Apache Kafka"),
    p("""Kafka u prezantua nga Kreps, Narkhede dhe Rao si sistem i shpërndarë mesazhesh i
      optimizuar për përpunimin e log-jeve, me një abstraksion qendror: log-un e qëndrueshëm,
      të ndarë dhe vetëm-me-shtim [@kreps2011]. Ky abstraksion, i thjeshtë në pamje, është
      arsyeja pse Kafka u bë shtylla kurrizore e arkitekturave moderne të të dhënave.
      Konsumatorët mbajnë vetë pozicionin e tyre, gjë që i bën të pavarur nga njëri-tjetri dhe
      e bën riprodhimin e historikut një operacion të natyrshëm [@kleppmann2017]. Pikërisht
      kjo veti shfrytëzohet në këtë punim për të simuluar një rrjedhë nga të dhëna
      historike."""),
    p("""Modaliteti KRaft, i cili e zëvendëson varësinë nga ZooKeeper me një protokoll
      konsensusi të brendshëm, e thjeshton ndjeshëm vendosjen. Për një prototip kërkimor me
      një broker të vetëm kjo do të thotë një shërbim më pak për t'u konfiguruar dhe
      mirëmbajtur, arsye për të cilën u zgjodh këtu."""),
    h3("2.7.2", "Platformat alternative dhe modelet e përpunimit"),
    p("""Apache Flink ofron një motor të unifikuar për përpunim rrjedhash dhe grupesh me
      semantikë të fortë kohore, i ndërtuar rreth dallimit mes kohës së ngjarjes dhe kohës së
      përpunimit [@carbone2015], ndërsa Spark Streaming e trajton rrjedhën si një sekuencë
      mikro-grupesh të diskretizuara. Ky dallim ka rëndësi edhe në një
      prototip: koha e ngjarjes këtu është kolona Time e dataset-it, ndërsa koha e përpunimit
      është ora e murit gjatë riprodhimit, dhe të dyja masin gjëra të ndryshme."""),
    p("""Për zbulimin e mashtrimeve në rrjedhë, puna më e afërt me këtë punim është SCARFF e
      Carcillo-s dhe bashkautorëve, e cila ndërton një kornizë të shkallëzueshme mbi Kafka,
      Spark dhe Cassandra [@carcillo2018]. Dallimi kryesor është fokusi: SCARFF trajton
      shkallëzueshmërinë dhe integrimin me vonesën e etiketave, ndërsa ky punim trajton
      ndershmërinë e vlerësimit dhe studimin e thelluar të tri algoritmeve."""),
    h3("2.7.3", "Mësimi mbi rrjedha"),
    p("""Literatura e mësimit mbi rrjedha ka zhvilluar një traditë të veçantë vlerësimi. Gama,
      Sebastião dhe Rodrigues argumentojnë se për të dhëna që mbërrijnë me radhë, vlerësimi
      prekuencial, pra testo-pastaj-trajno, është protokolli i duhur, sepse riprodhon rendin
      në të cilin informacioni bëhet i disponueshëm [@gama2013]. Protokolli rolling-origin i
      përdorur në këtë punim është variant i së njëjtës ide, i përshtatur për modele që
      trajnohen në grup dhe jo në mënyrë inkrementale."""),
]

_METODOLOGJIA = [
    h2("2.8", "Metodologjia e vlerësimit"),
    h3("2.8.1", "Metrikat nën çekuilibër ekstrem"),
    p("""Kur klasa pozitive përbën 0.17 për qind të të dhënave, saktësia është e papërdorshme,
      sepse një model që i shpall të gjitha transaksionet legjitime arrin 99.83 për qind
      saktësi. Më pak e dukshme, por po aq e rëndësishme, është problematika e AUC-ROC-së.
      Davis dhe Goadrich treguan se kurbat ROC dhe precision-recall kanë një lidhje të
      caktuar, por se një algoritëm që dominon në hapësirën ROC nuk dominon domosdoshmërisht
      në hapësirën precision-recall [@davis2006]. Saito dhe Rehmsmeier e demonstruan
      empirikisht se ROC jep një pamje tepër optimiste në dataset-e të çekuilibruara, sepse
      norma e pozitivëve të rremë ka në emërues numrin e madh të negativëve dhe mbetet e vogël
      edhe kur alarmet e rreme janë shumë më të shumta se ato të vërteta [@saito2015]."""),
    p("""Rezultatet e këtij punimi e ilustrojnë këtë në mënyrë të mprehtë. Për këto arsye Average
      Precision është metrika kryesore këtu, ndërsa ROC raportohet vetëm për krahasueshmëri me
      literaturën ekzistuese."""),
    p("""Një kritikë e dytë, më pak e diskutuar, është se as Average Precision nuk pasqyron
      mënyrën si përdoret vërtet një detektor. Asnjë ekip hetimi nuk shqyrton një renditje të
      plotë; ai shqyrton alarmet që kapaciteti i tij i lejon. Prandaj në këtë punim raportohen
      edhe metrikat në buxhet fiks alarmesh dhe kursimet neto sipas një modeli kostoje, sepse
      vetëm ashtu një përmirësim në renditje kthehet në një madhësi që ekipi operacional e
      njeh."""),
    h3("2.8.2", "Ndarja kohore dhe rrjedhja e informacionit"),
    p("""Bergmeir dhe Benítez analizuan përdorimin e vleftësimit të kryqëzuar për të dhëna me
      strukturë kohore dhe treguan se ndarja e rastësishme prodhon vlerësime të anshme, sepse
      modeli trajnohet me të dhëna që në realitet do të vinin pas atyre të testimit
      [@bergmeir2012]. Origjina rrotulluese, ku modeli ritrajnohet në pika të njëpasnjëshme
      prerjeje dhe testohet gjithmonë mbi të ardhmen e tyre, është përgjigjja e drejtpërdrejtë
      ndaj kësaj anshmërie dhe protokolli që ndjek ky punim."""),
    p("""Në kontekstin e zbulimit të mashtrimeve, rrjedhja mund të ndodhë në tri forma të
      dallueshme, dhe të treja janë trajtuar shprehimisht në implementimin e këtij punimi. E
      para është rrjedhja përmes ndarjes, ku përzierja e rastësishme lejon që transaksione nga
      e njëjta dritare kohore, madje nga i njëjti sulm, të shpërndahen mes trajnimit dhe
      testimit. E dyta është rrjedhja përmes paraprocesimit, ku një skalues i vlerësuar mbi
      gjithë dataset-in lejon që statistikat e testimit të ndikojnë te trajnimi. E treta, dhe
      më e nënvlerësuara, është rrjedhja përmes pragut: nëse pragu i alarmit zgjidhet duke
      maksimizuar F1-shin mbi bashkësinë e testimit, atëherë rezultati i raportuar nuk është
      performancë por një kufi i sipërm i paarritshëm."""),
    h3("2.8.3", "Vonesa e verifikimit dhe pasojat e saj"),
    p("""Një aspekt që e dallon zbulimin e mashtrimeve nga shumica e problemeve të
      klasifikimit është se etiketa nuk mbërrin bashkë me shembullin, por javë më vonë dhe
      vetëm për një pjesë të tij. Pasoja për këtë punim është e drejtpërdrejtë dhe përcaktoi
      disa zgjedhje dizajni. Nëse etiketa e sotme nuk ekziston, atëherë asnjë komponent që
      vepron mbi rrjedhën aktuale nuk mund të varet prej saj: as modeli, as skaluesi, as
      pragu. Nga ana tjetër, etiketat e së kaluarës së largët ekzistojnë, dhe përjashtimi i
      tyre do të ishte supozim tepër i ashpër dhe jorealist për një bankë. Kufiri i tërhequr
      këtu, etiketa historike po dhe etiketa aktuale jo, është pikërisht kufiri që vonesa e
      verifikimit e imponon në praktikë."""),
    h3("2.8.4", "Përzgjedhja e modeleve pa etiketa"),
    p("""Një kontradiktë e njohur e fushës është se metodat unsupervised zakonisht akordohen me
      etiketa. Goix e formuloi problemin qartë dhe propozoi kritere që nuk kërkojnë etiketa:
      kurbat Excess-Mass dhe Mass-Volume, të cilat vlerësojnë sa mirë grupet e nivelit të një
      funksioni pikëzimi e përqendrojnë masën probabilitare në vëllim të vogël [@goix2015],
      [@goix2016]. Vështirësia praktike është vlerësimi i masës Lebesgue në dimension të
      lartë; zgjidhja e rekomanduar është mesatarizimi mbi nënhapësira të rastësishme me
      dimension të ulët, e cila zbatohet edhe këtu."""),
    p("""Kufizimi i këtyre kritereve është se ato masin përqendrimin e masës dhe jo dobinë
      operacionale, dhe se vlera e tyre absolute nuk krahasohet mes dataset-eve. Prandaj këtu
      ato nuk e zëvendësojnë kriterin me etiketa, por përdoren si kontroll i pavarur mbi një
      pyetje të vetme: a do ta zgjidhte një kriter pa etiketa të njëjtin konfigurim."""),
    h3("2.8.5", "Krahasimi statistikor i algoritmeve"),
    p("""Demšar-i dha protokollin që mbetet standard për krahasimin e disa algoritmeve mbi disa
      bashkësi të dhënash: testi jo-parametrik i Friedman-it mbi matricën e rangjeve, i
      ndjekur nga testi post-hoc i Nemenyi-t dhe nga diagrami i diferencës kritike
      [@demsar2006], [@friedman1937], [@nemenyi1963]. Për krahasime të veçanta dyshe
      rekomandohet testi i Wilcoxon-it me rangje me shenjë [@wilcoxon1945], me korrigjim për
      krahasime të shumëfishta, ku procedura e Holm-it është më e fuqishme se ajo e
      Bonferroni-t pa e humbur kontrollin e gabimit [@holm1979]."""),
    p("""Një pikë që literatura e aplikuar shpesh e anashkalon është fuqia statistikore. Me N
      njësi vëzhgimi, p-vlera më e vogël e arritshme nga testi i Wilcoxon-it me dy bishta është
      2/2^N. Kjo do të thotë se me gjashtë njësi asnjë krahasim nuk mund të mbijetojë
      korrigjimin e Holm-it për më shumë se një hipotezë, sado i qëndrueshëm të jetë
      rezultati. Numri i fold-eve në këtë punim u zgjodh pikërisht duke marrë parasysh këtë
      kufi, dhe bashkësia e krahasimeve u fiksua paraprakisht në kod për të shmangur zgjedhjen
      e krahasimeve pas shikimit të rezultateve. Aty ku nevojitet një interval besimi mbi një
      bashkësi të vetme testimi, ai nxirret me riparashtrim bootstrap [@efron1993]."""),
    h2("2.9", "Paraprocesimi dhe gjeometria e të dhënave"),
    p("""Çdo detektor i bazuar në distancë, densitet ose rindërtim e trashëgon nocionin e
      largësisë nga paraprocesimi që zbatohet përpara tij, dhe megjithatë skaluesi zgjidhet
      zakonisht një herë e nuk rishikohet. Në kontekstin e zbulimit të anomalive kjo zgjedhje
      ka një hollësi që rrallë përmendet: skaluesi duhet të përshtatet mbi një dritare
      trajnimi që ende përmban anomalitë, sepse në momentin e vendosjes askush nuk e di se
      cilat rreshta janë ato. Statistikat që përcaktojnë shpërndarjen normale janë pra të
      kontaminuara nga vetë vlerat ekstreme që sistemi duhet të nxjerrë në pah, dhe kjo është
      arsyeja pse alternativat robuste dhe ato të bazuara në rang meritojnë krahasim empirik e
      jo zgjedhje me intuitë."""),
    p("""Një drejtim i dytë, edhe më pak i shfrytëzuar në literaturën e aplikuar, është
      karakterizimi gjeometrik i vetë problemit përpara se të përshtatet ndonjë model.
      Vlerësuesit e dimensionit të brendshëm tregojnë sa dimensione zë realisht klasa normale,
      dhe masat e mbivendosjes së klasave tregojnë nëse pozitivët janë fare të ndashëm nga
      negativët. Aggarwal e trajton këtë si hap paraprak të domosdoshëm në analizën e
      jashtëzakonshmërive [@aggarwal2017]. Kur këto masa llogariten, ato japin një kufi të
      sipërm të pavarur nga algoritmi, dhe çdo rezultat i mëvonshëm duhet lexuar përballë atij
      kufiri."""),
    h2("2.10", "Zhvendosja e konceptit"),
    p("""Rishikimi i Gama-s dhe bashkautorëve mbi përshtatjen ndaj zhvendosjes së konceptit
      dallon mes zhvendosjes së shpërndarjes së hyrjeve dhe zhvendosjes së varësisë mes
      hyrjeve dhe daljes, dhe përmbledh familjen e detektorëve që e sinjalizojnë atë në kohë
      reale [@gama2014]. Ndër ta, skema e inspektimit të vazhdueshëm e Page-it akumulon
      devijimet nga mesatarja rrjedhëse dhe sinjalizon kur akumulimi kalon një prag
      [@page1954]; varianti Page-Hinkley i saj është monitoruesi i zhvendosjes që përdoret në
      Kapitullin 5."""),
    p("""Dallimi që ka rëndësi praktike, dhe që në literaturën e aplikuar shpesh përzihet,
      është ai mes zhvendosjes në popullatën normale dhe zhvendosjes në popullatën e
      anomalive. I pari e vjetërsohet modelin e normalitetit dhe zgjidhet me ritrajnim mbi të
      dhëna të reja të paetiketuara. I dyti nuk e prek modelin e normalitetit fare, sepse
      thjesht anomalitë bëhen më pak të dallueshme, dhe ritrajnimi nuk ndihmon. Ky punim e
      dekompozon degradimin pikërisht në këto dy komponentë."""),
    h2("2.11", "Ansamblet e detektorëve"),
    p("""Zimek, Campello dhe Sander ngritën pyetjet themelore mbi ansamblet për zbulim
      unsupervised: si normalizohen pikë me shkallë krejt të ndryshme, dhe si sigurohet
      diversiteti kur nuk ka etiketa për të matur gabimin [@zimek2014]. Aggarwal dhe Sathe
      dhanë një trajtim teorik të kompromisit anshmëri-variancë për ansamblet e
      jashtëzakonshmërive dhe treguan se mesatarizimi e zvogëlon variancën vetëm kur anëtarët
      gabojnë ndryshe [@aggarwal2015]."""),
    p("""Rayana dhe Akoglu argumentuan me titullin e tyre se më pak është më shumë, pra se
      përzgjedhja selektive e anëtarëve e tejkalon kombinimin e verbër të gjithçkaje
      [@rayana2016]. Rezultati i këtij punimi shkon në të njëjtin drejtim
      por me përfundim më të matur, dhe analiza e gabimeve në nivel transaksioni tregon
      drejtpërdrejt pse."""),
    h2("2.12", "Interpretueshmëria e vendimeve"),
    p("""SHAP-i i Lundberg-ut dhe Lee-së ofron një kornizë unifikuese për atribuimin e
      kontributit të veçorive, me bazë në vlerat e Shapley-t nga teoria e lojërave
      [@lundberg2017]. Rëndësia e matur me permutimin e një veçorie të vetme, e prezantuar
      nga Breiman në kontekstin e pyjeve të rastësishme, mbetet alternativa më e thjeshtë dhe
      më e pavarur nga modeli [@breiman2001]."""),
    p("""Në rastin e veçorive të anonimizuara me PCA, interpretueshmëria semantike është e
      pamundur. Nuk ka kuptim të thuhet se modeli i kushton vëmendje shpeshtësisë së
      transaksioneve, sepse komponentët nuk kanë emra. Megjithatë mbetet një pyetje
      krejtësisht e përgjigjshme dhe shumë informative: a përkon vëmendja e modelit me ato
      dimensione që vërtet mbajnë sinjal diskriminues. Kjo pyetje, sipas literaturës së
      shqyrtuar, nuk është shtruar në mënyrë sistematike mbi këtë dataset, dhe përgjigjja e saj
      në Kapitullin 5 shpjegon renditjen e algoritmeve. Më tej, ajo shndërrohet nga korrelacion
      në pohim kauzal përmes një ndërhyrjeje eksperimentale."""),
    h2("2.13", "Boshllëqet e identifikuara dhe pozicionimi i punimit"),
    p("""Nga ky rishikim dalin pesë boshllëqe që përcaktojnë kontributin e këtij punimi."""),
    bullets(
        [
            "Shumica e krahasimeve mbi dataset-in ULB përdorin një ndarje të vetme, shpesh të "
            "rastësishme. Nuk gjendet një krahasim i tri algoritmeve të propozimit mbi këtë "
            "dataset nën një protokoll rolling-origin ku çdo fold rindërton të gjithë zinxhirin "
            "e paraprocesimit dhe të pragjeve.",
            "Kostoja e ndershmërisë metodologjike, pra sa fryhen rezultatet nga ndarja e "
            "rastësishme, përmendet shpesh si rrezik por rrallë matet mbi të njëjtat të dhëna "
            "dhe të njëjtat modele.",
            "Renditja e algoritmeve raportohet gjerësisht, por shpjegimi mekanicist i asaj "
            "renditjeje përmes atribuimit të veçorive mungon, dhe testimi kauzal i atij "
            "shpjegimi mungon plotësisht.",
            "Kufiri i sipërm i vetë problemit, pra sa i ndashëm është ai gjeometrikisht pa asnjë "
            "model, rrallë matet, prandaj nuk dihet nëse rezultatet modeste vijnë nga algoritmet "
            "apo nga të dhënat.",
            "Studimet mbi ansamblet për zbulim unsupervised raportojnë kryesisht rezultate "
            "pozitive; rezultatet negative, të cilat janë po aq informative kur shpjegohen, "
            "publikohen rrallë.",
        ]
    ),
    p("""Nga këto boshllëqe rrjedh edhe arsyetimi i fushëveprimit. Zgjedhja e tri familjeve në
      vend të një bashkësie të gjerë detektorësh nuk është kufizim i imponuar por kusht i
      domosdoshëm që katër nga pesë boshllëqet e mësipërme të mund të adresohen fare. Studimi
      mekanicist i një algoritmi kërkon hapjen e strukturës së tij të brendshme, ndërtimin e
      probave specifike për të dhe një ndërhyrje eksperimentale që e teston shpjegimin; kjo
      punë nuk shkallëzohet në dhjetëra metoda. Ekziston edhe një arsye statistikore. Diferenca
      kritike e testit post-hoc rritet me numrin e metodave të krahasuara, prandaj mbi një numër
      të fiksuar fold-esh një bashkësi e gjerë detektorësh e bën testin të paaftë të refuzojë
      çfarëdo hipoteze. Kapitulli 5 e demonstron këtë numerikisht."""),
    p("""Ky punim i adreson të pesta. Ai shton gjithashtu një kontribut praktik që nuk buron
      nga një boshllëk i literaturës por nga një problem i vërejtur gjatë implementimit:
      paqëndrueshmëria e ngarkesës hetimore kur pragu mbahet fiks mbi një rrjedhë që
      zhvendoset, dhe zgjidhja e saj me prag adaptiv me dritare rrëshqitëse."""),
]

BLOCKS = _HYRJE + _ALGORITMET + _DOMENI + _METODOLOGJIA

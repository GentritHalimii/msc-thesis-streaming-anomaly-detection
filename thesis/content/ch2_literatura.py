"""Kapitulli 2 — SHQYRTIMI I LITERATURËS."""

from blocks import bullets, eq, h1, h2, h3, note, p

_PJESA_1 = [
    h1("2", "Shqyrtimi i literaturës"),
    p("""Ky kapitull rishikon literaturën në pesë drejtime që përcaktojnë hapësirën e
      këtij punimi: përkufizimin dhe taksonominë e zbulimit të anomalive, familjet
      kryesore algoritmike, punën specifike mbi zbulimin e mashtrimeve me karta,
      arkitekturat për përpunim rrjedhash, dhe metodologjinë e vlerësimit. Drejtimi i
      fundit trajtohet me hollësi më të madhe se zakonisht në punime të kësaj natyre,
      sepse gjetja qendrore e këtij studimi është metodologjike: mënyra si vlerësohet një
      detektor ndryshon përfundimin se cili detektor është më i mirë."""),
    h2("2.1", "Zbulimi i anomalive: përkufizimi dhe taksonomia"),
    h3("2.1.1", "Çfarë është një anomali"),
    p("""Përkufizimi klasik i Hawkins-it e përshkruan anomalinë si një vëzhgim që devijon
      aq shumë nga vëzhgimet e tjera sa ngjall dyshimin se është gjeneruar nga një
      mekanizëm i ndryshëm [@hawkins1980]. Ky përkufizim është i dobishëm sepse e
      zhvendos vëmendjen nga "e rrallë" te "e gjeneruar ndryshe". Të dy nuk përputhen
      domosdoshmërisht: një transaksion me vlerë shumë të lartë është i rrallë por mund
      të jetë krejtësisht legjitim, ndërsa një mashtrim testues me vlerë një euro mund të
      jetë krejt i zakonshëm në pamje."""),
    p("""Chandola, Banerjee dhe Kumar, në rishikimin e tyre që mbetet referenca standarde
      e fushës, dallojnë tri lloje anomalish: pikësore, kontekstuale dhe kolektive
      [@chandola2009]. Një anomali pikësore është një instancë e vetme që bie jashtë
      normës. Një anomali kontekstuale është normale në përgjithësi por jo në kontekstin
      e vet — një blerje prej 200 eurosh është e zakonshme, por jo në orën tre të mëngjesit
      për një mbajtës që nuk blen kurrë natën. Një anomali kolektive është një sekuencë
      instancash secila prej të cilave duket normale, por bashkësia e tyre nuk është."""),
    p("""Ky dallim ka pasoja të drejtpërdrejta për këtë punim. Dataset-i i përdorur këtu
      nuk përmban identifikues të kartës, prandaj konteksti individual i mbajtësit nuk
      mund të rindërtohet dhe anomalitë kontekstuale dhe kolektive mbeten jashtë
      mundësive të modelimit. Kjo është një kufizim i vërtetë i studimit, jo një zgjedhje,
      dhe do të kthehem tek ai në diskutimin e kufizimeve."""),
    h3("2.1.2", "Taksonomia sipas mekanizmit të vendimit"),
    p("""Rishikimet më të fundit, veçanërisht ai unifikues i Ruff-it dhe bashkautorëve, i
      organizojnë metodat sipas mekanizmit me të cilin përcaktohet se çfarë është normale
      [@ruff2021]. Kjo organizim është më i dobishëm sesa ndarja e zakonshme
      "klasike kundrejt të thella", sepse dy metoda nga epoka të ndryshme mund të ndajnë
      të njëjtin mekanizëm dhe të kenë të njëjtat dobësi; rishikimi i Pang-ut dhe
      bashkautorëve mbi metodat e thella ndjek një logjikë të ngjashme organizimi
      [@pang2021]. Në këtë punim përdoret pikërisht
      kjo taksonomi, me gjashtë familje: izolim, kufi vendimi, afërsi, rindërtim, densitet
      dhe statistikore marginale. Zgjedhja për ta organizuar eksperimentin sipas familjeve
      dhe jo sipas algoritmeve individuale u vërtetua e dobishme: dallimet brenda një
      familjeje rezultuan në disa raste më të vogla se dallimet mes familjeve."""),
    h2("2.2", "Familjet e metodave të pambikëqyrura"),
    h3("2.2.1", "Metodat e bazuara në izolim"),
    p("""Isolation Forest, i propozuar nga Liu, Ting dhe Zhou, e përmbys logjikën e
      zakonshme: në vend që të modelojë normalitetin dhe të masë largësinë prej tij, ai
      mat se sa lehtë izolohet një pikë [@liu2008], [@liu2012]. Algoritmi ndërton pemë me
      ndarje të rastësishme dhe përdor gjatësinë mesatare të shtegut deri te izolimi si
      pikë anomalie. Argumenti është elegant: pikat anormale, duke qenë të pakta dhe të
      largëta, izolohen me më pak ndarje."""),
    p("""Formalisht, për një pikë x pika e anomalisë përcaktohet nga gjatësia mesatare e
      shtegut E[h(x)] mbi ansamblin e pemëve, e normalizuar me gjatësinë e pritur të
      shtegut c(n) në një pemë kërkimi binare me n nyje:"""),
    eq("s(x, n) = 2^( −E[h(x)] / c(n) ),   c(n) = 2H(n−1) − 2(n−1)/n"),
    p("""ku H është numri harmonik. Normalizimi e bën pikën të krahasueshme mes pemëve me
      thellësi të ndryshme dhe e kufizon atë në intervalin (0, 1), ku vlerat afër njëshit
      tregojnë izolim të lehtë. Në implementimin e përdorur këtu pika merret me shenjë të
      kundërt të funksionit të bibliotekës, që të respektohet konventa e vetme e këtij
      punimi: vlerë më e lartë do të thotë më anormale."""),
    p("""Popullariteti i tij vjen nga kompleksiteti nënlinear dhe nga mungesa e nevojës
      për të llogaritur distanca. Megjithatë, literatura ka dokumentuar edhe dobësi
      sistematike. Ndarjet zgjidhen në mënyrë të rastësishme mbi dimensione dhe pragje, pa
      asnjë preferencë për dimensionet informative; në hapësira me shumë dimensione ku
      vetëm pak prej tyre mbajnë sinjal, shumica e ndarjeve harxhohen. Rezultatet e këtij
      punimi e konfirmojnë këtë dobësi në mënyrë të matshme, dhe analiza e atribuimit në
      Kapitullin 5 e tregon mekanizmin drejtpërdrejt."""),
    h3("2.2.2", "Metodat e bazuara në kufirin e vendimit"),
    p("""One-Class SVM i Schölkopf-it dhe bashkautorëve kërkon një hiperplan që i ndan të
      dhënat nga origjina në hapësirën e veçorive me kernel, duke maksimizuar distancën
      [@scholkopf2001]. Formulimi ekuivalent i Tax-it dhe Duin-it, Support Vector Data
      Description, kërkon sferën më të vogël që i përmban të dhënat [@tax2004]. Të dyja
      janë të fuqishme teorikisht, por kostoja e trajnimit rritet të paktën në mënyrë
      kuadratike me numrin e mostrave, gjë që i bën të papërdorshme drejtpërdrejt mbi
      qindra mijëra rreshta — një kufizim praktik që në këtë punim u zgjidh me
      nën-mostrim të dokumentuar."""),
    p("""Formulimi i One-Class SVM-së kërkon zgjidhjen e problemit të optimizimit"""),
    eq("min ½‖w‖² + (1/νn)Σξ_i − ρ,   ⟨w, φ(x_i)⟩ ≥ ρ − ξ_i,  ξ_i ≥ 0"),
    p("""ku ν ∈ (0, 1] është njëkohësisht kufi i sipërm për fraksionin e pikave jashtë
      kufirit dhe kufi i poshtëm për fraksionin e vektorëve mbështetës. Kjo veti e dyfishtë
      e bën ν parametrin e vetëm vërtet të interpretueshëm të metodës, dhe shpjegon pse ai
      zakonisht vendoset afër normës së pritur të kontaminimit."""),
    p("""Deep SVDD e transferon idenë e SVDD-së në një rrjet nervor: në vend të një sfere
      në hapësirën e kernelit, mësohet një transformim që i mbledh të dhënat normale
      brenda një sfere me qendër fikse [@ruff2018]. Autorët identifikojnë rrezikun
      kryesor — kolapsi i hiperzonës, ku rrjeti mëson të hartojë gjithçka në një pikë të
      vetme — dhe propozojnë masat mbrojtëse që përdoren edhe këtu: heqjen e termave të
      anshmërisë dhe fiksimin e qendrës nga një kalim fillestar. Ky detaj implementimi
      nuk është dytësor; pa të, modeli konvergjon në një zgjidhje triviale."""),
    h3("2.2.3", "Metodat e bazuara në afërsi"),
    p("""Local Outlier Factor i Breunig-ut dhe bashkautorëve prezantoi idenë se
      jashtëzakonshmëria është relative ndaj lagjes lokale, jo ndaj shpërndarjes globale
      [@breunig2000]. Kjo është veçanërisht e rëndësishme kur të dhënat kanë grumbuj me
      densitete të ndryshme, sepse një prag global do të shënonte si anomali të gjithë
      grumbullin më të shpërndarë. Detektori më i thjeshtë i bazuar në distancën deri te
      fqinji i k-të, i formalizuar nga Ramaswamy dhe bashkautorët, mbetet një bazë
      krahasimi surprizisht e fortë [@ramaswamy2000]."""),
    p("""Kostoja e këtyre metodave nuk qëndron te trajnimi por te pikëzimi: çdo transaksion
      i ri kërkon një kërkim fqinjësh në bashkësinë referuese. Në kontekstin e një rrjedhe
      kjo është pikërisht kostoja që ka rëndësi, dhe matjet e këtij punimi e tregojnë atë
      qartë: metodat e afërsisë janë ndër më të ngadaltat në pikëzim, me disa qindra herë
      më shumë kohë për transaksion sesa modelet e thella."""),
    h3("2.2.4", "Metodat e bazuara në rindërtim"),
    p("""Ideja e rindërtimit është e vjetër sa vetë analiza e komponentëve kryesorë: nëse
      të dhënat normale shtrihen afër një nënhapësire me dimension të ulët, atëherë
      gabimi i projektimit dhe i rikthimit është i vogël për to dhe i madh për anomalitë.
      Shyu dhe bashkautorët e formalizuan këtë si klasifikues të bazuar në komponentë
      kryesorë [@shyu2003]. Autoenkoderët e zgjerojnë idenë në rastin jolinear: rrjeti
      mëson një kodim të ngjeshur dhe një dekodim, dhe gabimi i rindërtimit shërben si
      pikë anomalie [@hinton2006], [@sakurada2014]."""),
    p("""Objektivi i autoenkoderit është minimizimi i gabimit të rindërtimit mbi të dhënat
      normale, dhe po ai gabim shërben si pikë anomalie në kohën e inferencës:"""),
    eq("L = (1/n) Σ ‖x_i − g(f(x_i))‖²,    s(x) = ‖x − g(f(x))‖²"),
    p("""Supozimi i heshtur këtu është se rrjeti, i trajnuar vetëm mbi normale, nuk do të
      mësojë funksionin identitet. Kjo garantohet vetëm nga ngushtica e hapësirës latente:
      nëse dimensioni latent i afrohet atij hyrës, rrjeti mund t'i rindërtojë mirë edhe
      anomalitë dhe pika e humbet fuqinë dalluese. Ky mekanizëm, i njohur teorikisht, u
      vëzhgua në mënyrë të matur në eksperimentet e këtij punimi te Deep SVDD-ja pas
      akordimit të hiperparametrave."""),
    p("""Autoenkoderi variacional shton një shtresë probabilistike: kodimi latent
      rregullohet drejt një shpërndarjeje të njohur, dhe pikëzimi mund të bazohet në
      kufirin e poshtëm të evidencës ose në probabilitetin e rindërtimit [@kingma2014],
      [@an2015]. Përparësia konceptuale është se pika kombinon dy burime befasie: sa keq
      rindërtohet pika dhe sa i pamundur është kodi i saj latent. Modelet hibride si
      DAGMM shkojnë më tej duke mësuar njëkohësisht ngjeshjen dhe një model densiteti mbi
      hapësirën latente [@zong2018]."""),
    note("""Një detaj që meriton vëmendje në rastin konkret: veçoritë V1–V28 të
      dataset-it të përdorur këtu janë vetë komponentë kryesorë. Kjo do të thotë se një
      detektor linear rindërtimi nuk është thjesht një bazë krahasimi e dobët, por
      pragu natyror i kësaj familjeje — nëse një autoenkoder jolinear nuk e tejkalon
      atë, ai nuk ka mësuar asgjë përtej asaj që PCA-ja e kishte tashmë të dukshme."""),
    h3("2.2.5", "Metodat e bazuara në densitet"),
    p("""Rruga statistikore klasike modelon shpërndarjen e të dhënave normale dhe pikëzon
      sipas gjasës. Një model përzierjeje gausiane e bën këtë me disa komponentë, ndërsa
      distanca e Mahalanobis-it e bën me një gausiane të vetme, duke marrë parasysh
      kovariancën. Në praktikë, vlerësimi i kovariancës është i ndjeshëm ndaj vetë
      anomalive që kërkohen, prandaj përdoren vlerësues robustë si Minimum Covariance
      Determinant, për të cilin Rousseeuw dhe Van Driessen dhanë algoritmin e shpejtë që
      e bëri të përdorshëm në praktikë [@rousseeuw1999]."""),
    h3("2.2.6", "Metodat statistikore marginale"),
    p("""Një zhvillim i rëndësishëm i viteve të fundit është rikthimi i metodave shumë të
      thjeshta si baza krahasimi serioze. HBOS supozon pavarësi mes veçorive dhe kombinon
      histograma njëdimensionale [@goldstein2012]. LODA përdor një ansambël projeksionesh
      të rastësishme njëdimensionale me histograma [@pevny2016]. COPOD dhe ECOD
      llogaritin bashkim kopula ose funksione empirike të shpërndarjes kumulative dhe janë
      praktikisht pa hiperparametra [@li2020copod], [@li2022ecod]."""),
    p("""Rëndësia e tyre nuk qëndron te performanca absolute por te roli metodologjik.
      Benchmark-u i gjerë ADBench, i cili krahasoi dhjetëra algoritme mbi dhjetëra
      dataset-e, gjeti se metodat e thjeshta janë konkurruese në një pjesë të
      konsiderueshme të rasteve dhe se asnjë metodë nuk dominon [@han2022]. Përfundimi
      praktik është se çdo metodë e ndërlikuar duhet të justifikohet kundrejt një baze të
      thjeshtë e të lirë, dhe pikërisht për këtë arsye këto katër metoda u përfshinë në
      krahasimin e këtij punimi."""),
    h2("2.3", "Zbulimi i mashtrimeve me karta krediti"),
    h3("2.3.1", "Karakteristikat e domenit"),
    p("""Dal Pozzolo dhe bashkautorët, në një punim që përmbledh mësimet e nxjerra nga
      bashkëpunimi me një procesor të vërtetë pagesash, identifikojnë tri veçori që e
      dallojnë këtë domen nga problemet e zakonshme të klasifikimit [@dalpozzolo2014].
      E para është çekuilibri ekstrem. E dyta është vonesa e verifikimit: etiketat
      mbërrijnë me vonesë dhe vetëm për një nënbashkësi transaksionesh. E treta është
      zhvendosja e konceptit: mashtruesit përshtaten ndaj kontrolleve, prandaj shpërndarja
      e klasës pozitive ndryshon me kalimin e kohës."""),
    p("""Në një punim të mëvonshëm, të njëjtët autorë propozojnë një modelim realist që e
      merr parasysh vonesën e verifikimit dhe tregojnë se vlerësimi që e injoron këtë
      vonesë e mbivlerëson performancën [@dalpozzolo2018]. Të njëjtët autorë kanë treguar
      gjithashtu se nën-mostrimi i klasës shumicë, teknikë e zakonshme kundër
      çekuilibrit, i shtrembëron probabilitetet e prodhuara dhe kërkon rikalibrim
      [@dalpozzolo2015] — një arsye më shumë pse ky punim nuk përdor ri-mostrim
      fare. Kjo është pikërisht kritika
      metodologjike që ky punim e zgjeron: nëse renditja kohore ka rëndësi për etiketat,
      ajo ka rëndësi edhe për ndarjen e të dhënave."""),
    p("""Një drejtim i rëndësishëm i punës aplikative është inxhinieria e veçorive përmes
      agregimit. Whitrow dhe bashkautorët treguan se agregimi i transaksioneve për
      llogari mbi dritare kohore përmirëson ndjeshëm zbulimin [@whitrow2009], dhe
      Bahnsen me bashkautorë e zgjeruan këtë me veçori periodike të bazuara në sjelljen e
      mbajtësit [@bahnsen2016]. Jurgovsky dhe bashkautorët shkuan edhe më tej, duke e
      trajtuar problemin si klasifikim sekuencash me rrjeta rekurrente [@jurgovsky2018].
      Të gjitha këto qasje kërkojnë identifikuesin e kartës, i cili nuk ekziston në
      dataset-in publik të përdorur këtu."""),
    h3("2.3.2", "Punimet mbi dataset-in ULB"),
    p("""Dataset-i i publikuar nga grupi Machine Learning i Université Libre de Bruxelles
      është bërë standard de facto për këtë problem [@ulb_dataset]. Ai përmban 284,807
      transaksione nga dy ditë të shtatorit 2013, prej të cilave 492 janë mashtruese, dhe
      28 nga 30 veçoritë janë komponentë kryesorë të anonimizuar."""),
    p("""Numri i punimeve që e përdorin është shumë i madh, por cilësia metodologjike
      ndryshon dukshëm. Bhattacharyya dhe bashkautorët bënë një krahasim të hershëm mes
      metodave të mbikëqyrura [@bhattacharyya2011]. Makki dhe bashkautorët krahasuan
      qasjet për trajtimin e çekuilibrit dhe raportuan se disa teknika mbi-mostrimi
      prodhojnë rezultate mashtruese kur vlerësimi bëhet gabim [@makki2019]. Një pjesë e
      madhe e literaturës raporton vlera shumë të larta të AUC-ROC-së, të cilat, siç do
      të argumentohet në nënkapitullin 2.5, janë pothuajse pa vlerë informative në këtë
      nivel çekuilibri."""),
    p("""Manuali praktik i Le Borgne-s dhe bashkautorëve meriton përmendje të veçantë
      sepse është ndër burimet e pakta që e trajton riprodhueshmërinë si kërkesë qendrore
      dhe që e diskuton hapur ndarjen kohore [@leborgne2022]. Ai rekomandon vlerësim me
      ndarje kohore dhe me vonesë verifikimi, pra pikërisht drejtimin që ndiqet këtu."""),
    h3("2.3.3", "Kombinimi i qasjes së mbikëqyrur dhe të pambikëqyrur"),
    p("""Carcillo dhe bashkautorët hetuan nëse pikët e anomalisë të prodhuara nga metoda
      të pambikëqyrura mund të shërbejnë si veçori shtesë për një klasifikues të
      mbikëqyrur, dhe raportuan përmirësim [@carcillo2021]. Ky rezultat është i
      rëndësishëm për interpretimin e këtij punimi: ai sugjeron se metodat e
      pambikëqyrura mbajnë informacion plotësues edhe kur, të marra vetëm, mbeten
      dukshëm nën një model të mbikëqyrur — përfundim që përputhet me hendekun e matur
      këtu mes referencës së mbikëqyrur dhe detektorëve të pambikëqyrur."""),
    h2("2.4", "Arkitekturat për përpunim rrjedhash"),
    h3("2.4.1", "Apache Kafka"),
    p("""Kafka u prezantua nga Kreps, Narkhede dhe Rao si sistem i shpërndarë mesazhesh i
      optimizuar për përpunimin e log-jeve, me një abstraksion qendror: log-u i
      qëndrueshëm, i ndarë dhe vetëm-me-shtim [@kreps2011]. Ky abstraksion, i thjeshtë në
      pamje, është arsyeja pse Kafka u bë shtylla kurrizore e arkitekturave moderne të
      të dhënave: konsumatorët mbajnë vetë pozicionin e tyre, gjë që i bën të pavarur nga
      njëri-tjetri dhe e bën riprodhimin e historikut një operacion të natyrshëm
      [@kleppmann2017]. Pikërisht kjo veti u shfrytëzua në këtë punim për të simuluar një
      rrjedhë nga të dhëna historike."""),
    p("""Modaliteti KRaft, i cili e zëvendëson varësinë nga ZooKeeper me një protokoll
      konsensusi të brendshëm, e thjeshton ndjeshëm vendosjen. Për një prototip kërkimor
      me një broker të vetëm kjo do të thotë një shërbim më pak për t'u konfiguruar dhe
      mirëmbajtur, arsye për të cilën u zgjodh këtu."""),
    h3("2.4.2", "Platformat alternative dhe modelet e përpunimit"),
    p("""Apache Flink ofron një motor të unifikuar për përpunim rrjedhash dhe grupesh me
      semantikë të fortë kohore [@carbone2015], ndërsa Spark Streaming përdor modelin e
      rrjedhave të diskretizuara, ku rrjedha trajtohet si një sekuencë mikro-grupesh
      [@zaharia2013]. Modeli Dataflow i Akidau-t dhe bashkautorëve dha kornizën
      konceptuale për të arsyetuar mbi kohën e ngjarjes kundrejt kohës së përpunimit dhe
      mbi kompromiset mes korrektësisë, vonesës dhe kostos [@akidau2015]. Ky dallim është
      i rëndësishëm edhe në një prototip: koha e ngjarjes këtu është kolona Time e
      dataset-it, ndërsa koha e përpunimit është ora e murit gjatë riprodhimit, dhe të dyja
      matën gjëra të ndryshme."""),
    p("""Për zbulimin e mashtrimeve në rrjedhë, puna më e afërt me këtë punim është SCARFF
      e Carcillo-s dhe bashkautorëve, e cila ndërton një kornizë të shkallëzueshme mbi
      Kafka, Spark dhe Cassandra [@carcillo2018]. Dallimi kryesor është fokusi: SCARFF
      trajton shkallëzueshmërinë dhe integrimin me vonesën e etiketave, ndërsa ky punim
      trajton ndershmërinë e vlerësimit dhe krahasimin sistematik të familjeve
      algoritmike."""),
    h3("2.4.3", "Mësimi mbi rrjedha"),
    p("""Literatura e mësimit mbi rrjedha ka zhvilluar një traditë të veçantë vlerësimi.
      Gama, Sebastião dhe Rodrigues argumentojnë se për të dhëna që mbërrijnë me radhë,
      vlerësimi prekuencial — testo-pastaj-trajno — është protokolli i duhur, sepse ai
      riprodhon rendin në të cilin informacioni bëhet i disponueshëm [@gama2013].
      Platforma MOA e bëri këtë praktikë të arritshme [@bifet2010]. Protokolli
      rolling-origin i përdorur në këtë punim është një variant i kësaj ideje, i
      përshtatur për modele që trajnohen në grup dhe jo në mënyrë inkrementale."""),
]

_PJESA_2 = [
    h2("2.5", "Metodologjia e vlerësimit"),
    h3("2.5.1", "Metrikat nën çekuilibër ekstrem"),
    p("""Kur klasa pozitive përbën 0.17 për qind të të dhënave, saktësia është e
      papërdorshme: një model që i shpall të gjitha transaksionet legjitime arrin 99.83
      për qind saktësi. Më pak e dukshme, por po aq e rëndësishme, është problematika e
      AUC-ROC-së. Davis dhe Goadrich treguan se kurbat ROC dhe PR kanë një lidhje të
      caktuar, por se një algoritëm që dominon në hapësirën ROC nuk dominon domosdoshmërisht
      në hapësirën PR [@davis2006]. Saito dhe Rehmsmeier e demonstruan empirikisht se ROC
      jep një pamje tepër optimiste në dataset-e të çekuilibruara, sepse norma e
      pozitivëve të rremë ka në emërues numrin e madh të negativëve dhe mbetet e vogël
      edhe kur alarmet e rreme janë shumë më të shumta se ato të vërteta [@saito2015]."""),
    p("""Rezultatet e këtij punimi e ilustrojnë këtë në mënyrë të mprehtë: disa detektorë
      arrijnë AUC-ROC mbi 0.94 ndërsa AP-ja e tyre mbetet nën 0.15. Nëse do të raportohej
      vetëm ROC, të gjithë do të dukeshin të shkëlqyer. Hand ka argumentuar edhe më tej
      se AUC-ja ka një mangësi konceptuale, sepse peshon në mënyrë implicite kostot e
      gabimeve ndryshe për modele të ndryshme [@hand2009]. Për këto arsye AP-ja është
      metrika kryesore këtu, ndërsa ROC raportohet vetëm për krahasueshmëri me
      literaturën ekzistuese."""),
    p("""Një kritikë e dytë, më pak e diskutuar, është se as AP-ja nuk pasqyron mënyrën si
      përdoret vërtet një detektor. Asnjë ekip hetimi nuk shqyrton një renditje të plotë;
      ai shqyrton alarmet që kapaciteti i tij i lejon. Prandaj në këtë punim raportohen
      edhe metrikat në buxhet fiks alarmesh dhe kursimet neto sipas një modeli kostoje,
      në traditën e mësimit të ndjeshëm ndaj kostos të formalizuar nga Elkan
      [@elkan2001]."""),
    h3("2.5.2", "Ndarja kohore dhe rrjedhja e informacionit"),
    p("""Bergmeir dhe Benítez analizuan përdorimin e vleftësimit të kryqëzuar për të dhëna
      me strukturë kohore dhe treguan se ndarja e rastësishme prodhon vlerësime të
      anshme, sepse modeli trajnohet me të dhëna që në realitet do të vinin pas atyre të
      testimit [@bergmeir2012]. Tashman, në rishikimin e tij mbi testet jashtë-mostrës
      për parashikim, kishte konsoliduar shumë më herët praktikën e origjinës rrotulluese
      si standard [@tashman2000]."""),
    p("""Në kontekstin e zbulimit të mashtrimeve, rrjedhja mund të ndodhë në tri forma të
      dallueshme, dhe të treta janë trajtuar shprehimisht në implementimin e këtij punimi.
      E para është rrjedhja përmes ndarjes: përzierja e rastësishme lejon që transaksione
      nga e njëjta dritare kohore, madje nga i njëjti sulm, të shpërndahen mes trajnimit
      dhe testimit. E dyta është rrjedhja përmes paraprocesimit: nëse skaluesi vlerësohet
      mbi të gjithë dataset-in, statistikat e testimit kanë ndikuar te trajnimi. E treta,
      dhe më e nënvlerësuara, është rrjedhja përmes pragut: nëse pragu i alarmit zgjidhet
      duke maksimizuar F1-shin mbi bashkësinë e testimit, atëherë rezultati i raportuar
      nuk është performancë por një kufi i sipërm i paarritshëm."""),
    h3("2.5.3", "Përzgjedhja e modeleve pa etiketa"),
    p("""Një kontradiktë e njohur e fushës është se metodat e pambikëqyrura zakonisht
      akordohen me etiketa. Goix e formuloi problemin qartë dhe propozoi kritere që nuk
      kërkojnë etiketa: kurbat Excess-Mass dhe Mass-Volume, të cilat vlerësojnë sa mirë
      grupet e nivelit të një funksioni pikëzimi e përqendrojnë masën probabilitare në
      vëllim të vogël [@goix2015], [@goix2016]. Vështirësia praktike është vlerësimi i
      masës Lebesgue në dimension të lartë; zgjidhja e rekomanduar është mesatarizimi mbi
      nënhapësira të rastësishme me dimension të ulët, e cila zbatohet edhe këtu."""),
    p("""Campos dhe bashkautorët, në një studim të gjerë mbi vlerësimin e zbulimit të
      jashtëzakonshmërive, treguan se rezultatet varen ndjeshëm nga zgjedhja e
      hiperparametrave dhe nga mënyra e normalizimit të pikëve, dhe bënë thirrje për
      protokolle më të standardizuara [@campos2016]. Emmott dhe bashkautorët kishin
      ngritur më herët problemin e ndërtimit sistematik të benchmark-eve
      [@emmott2013]."""),
    h3("2.5.4", "Vonesa e verifikimit dhe pasojat e saj"),
    p("""Një aspekt që e dallon zbulimin e mashtrimeve nga shumica e problemeve të
      klasifikimit është se etiketa nuk mbërrin bashkë me shembullin, por javë më vonë dhe
      vetëm për një pjesë të tij. Dal Pozzolo dhe bashkautorët e modeluan këtë shprehimisht
      dhe treguan se një skemë vlerësimi që e injoron vonesën e verifikimit e mbivlerëson
      performancën e sistemit, sepse i jep modelit akses te etiketa që në realitet nuk do
      t'i kishte pasur [@dalpozzolo2018]."""),
    p("""Pasoja për këtë punim është e drejtpërdrejtë dhe përcaktoi disa zgjedhje dizajni.
      Nëse etiketa e sotme nuk ekziston, atëherë asnjë komponent që vepron mbi rrjedhën
      aktuale nuk mund të varet prej saj: as modeli, as skaluesi, as pragu. Nga ana tjetër,
      etiketat e së kaluarës së largët ekzistojnë, dhe përjashtimi i tyre do të ishte një
      supozim tepër i ashpër dhe jorealist për një bankë. Kufiri i tërhequr këtu — etiketa
      historike po, etiketa aktuale jo — është pikërisht kufiri që vonesa e verifikimit e
      imponon në praktikë."""),
    h3("2.5.5", "Krahasimi statistikor i algoritmeve"),
    p("""Demšar-i dha protokollin që mbetet standard për krahasimin e disa algoritmeve mbi
      disa bashkësi të dhënash: testi jo-parametrik i Friedman-it mbi matricën e
      rangjeve, i ndjekur nga testi post-hoc i Nemenyi-t dhe nga diagrami i diferencës
      kritike [@demsar2006], [@friedman1937], [@nemenyi1963]. Për krahasime të veçanta
      dyshe rekomandohet testi i Wilcoxon-it me rangje me shenjë [@wilcoxon1945], me
      korrigjim për krahasime të shumëfishta, ku procedura e Holm-it është më e fuqishme
      se ajo e Bonferroni-t pa e humbur kontrollin e gabimit [@holm1979]."""),
    p("""Një pikë që literatura e aplikuar shpesh e anashkalon është fuqia statistikore.
      Me N njësi vëzhgimi, p-vlera më e vogël e arritshme nga testi i Wilcoxon-it me
      dy bishta është 2/2^N. Kjo do të thotë se me gjashtë njësi asnjë krahasim nuk mund
      të mbijetojë korrigjimin e Holm-it për më shumë se një hipotezë, sado i qëndrueshëm
      të jetë rezultati. Në këtë punim numri i folds-ave u zgjodh pikërisht duke marrë
      parasysh këtë kufi, dhe bashkësia e krahasimeve u fiksua paraprakisht në kod për të
      shmangur zgjedhjen e krahasimeve pas shikimit të rezultateve."""),
    h2("2.6", "Zhvendosja e konceptit"),
    p("""Rishikimi i Gama-s dhe bashkautorëve mbi përshtatjen ndaj zhvendosjes së konceptit
      dallon mes zhvendosjes së shpërndarjes së hyrjeve dhe zhvendosjes së varësisë mes
      hyrjeve dhe daljes [@gama2014], ndërsa Lu dhe bashkautorët e zgjerojnë klasifikimin
      dhe rishikojnë metodat e zbulimit [@lu2019]. ADWIN-i i Bifet-it dhe Gavaldà-s mban
      një dritare me gjatësi të ndryshueshme dhe e ndan atë kur dy nënpjesë ndryshojnë
      në mënyrë statistikisht domethënëse [@bifet2007]; testi i Page-it, shumë më i
      hershëm dhe shumë më i lirë, akumulon devijimet nga mesatarja rrjedhëse dhe
      sinjalizon kur akumulimi kalon një prag [@page1954]."""),
    p("""Dallimi që ka rëndësi praktike, dhe që në literaturën e aplikuar shpesh
      përzihet, është ai mes zhvendosjes në popullatën normale dhe zhvendosjes në
      popullatën e anomalive. I pari e vjetërsoh modelin e normalitetit dhe zgjidhet me
      ritrajnim mbi të dhëna të reja të paetiketuara. I dyti nuk e prek modelin e
      normalitetit fare — thjesht anomalitë bëhen më pak të dallueshme — dhe ritrajnimi
      nuk ndihmon. Ky punim e dekompozon degradimin pikërisht në këto dy komponentë dhe
      gjen se pesha bie qartazi te i dyti."""),
    h2("2.7", "Ansamblet e detektorëve të anomalive"),
    p("""Zimek, Campello dhe Sander ngritën pyetjet themelore mbi ansamblet për zbulim të
      pambikëqyrur: si normalizohen pikë me shkallë krejt të ndryshme, dhe si sigurohet
      diversiteti kur nuk ka etiketa për të matur gabimin [@zimek2014]. Aggarwal dhe
      Sathe dhanë një trajtim teorik të kompromisit anshmëri–variancë për ansamblet e
      jashtëzakonshmërive dhe treguan se mesatarizimi zvogëlon variancën vetëm kur
      anëtarët gabojnë ndryshe [@aggarwal2015]. Kuncheva dhe Whitaker kishin treguar më
      herët, në kontekstin e klasifikimit, se masat e diversitetit lidhen me saktësinë e
      ansamblit në mënyra jo gjithnjë intuitive [@kuncheva2003]."""),
    p("""Rayana dhe Akoglu argumentuan me titullin e tyre "më pak është më shumë" se
      përzgjedhja selektive e anëtarëve tejkalon kombinimin e verbër të gjithçkaje
      [@rayana2016], duke ndjekur idenë e përzgjedhjes së ansambleve nga një bibliotekë
      modelesh të Caruana-s dhe bashkautorëve [@caruana2004]. LSCP shkon më tej me
      kombinim lokalisht selektiv [@zhao2019lscp]. Rezultati i këtij punimi shkon në të
      njëjtin drejtim, por me një përfundim më të matur: përzgjedhja e kujdesshme e
      afron ansamblin me modelin më të mirë individual, pa e tejkaluar atë, ndërsa
      kombinimi i verbër është dramatikisht më i keq."""),
    h2("2.8", "Interpretueshmëria e vendimeve"),
    p("""SHAP-i i Lundberg-ut dhe Lee-së ofron një kornizë unifikuese për atribuimin e
      kontributit të veçorive, me bazë në vlerat e Shapley-t nga teoria e lojërave
      [@lundberg2017], ndërsa LIME e afron problemin me përafrim lokal linear
      [@ribeiro2016]. Rëndësia me permutim, e prezantuar nga Breiman në kontekstin e
      pyjeve të rastësishme, mbetet metoda më e thjeshtë dhe më e përgjithshme
      [@breiman2001]."""),
    p("""Në rastin e veçorive të anonimizuara me PCA, interpretueshmëria semantike është e
      pamundur: nuk ka kuptim të thuhet se "modeli i kushton vëmendje shpeshtësisë së
      transaksioneve", sepse komponentët nuk kanë emra. Megjithatë, mbetet një pyetje
      krejtësisht e përgjigjshme dhe shumë informative: a përkon vëmendja e modelit me
      ato dimensione që vërtet mbajnë sinjal diskriminues. Kjo pyetje, sipas njohurive
      të mia, nuk është shtruar në mënyrë sistematike në literaturën mbi këtë dataset,
      dhe përgjigjja e saj në Kapitullin 5 shpjegon renditjen e algoritmeve."""),
    h2("2.9", "Boshllëqet e identifikuara dhe pozicionimi i punimit"),
    p("""Nga ky rishikim dalin katër boshllëqe që përcaktojnë kontributin e këtij punimi."""),
    bullets(
        [
            "Shumica e krahasimeve mbi dataset-in ULB përdorin një ndarje të vetme, shpesh të "
            "rastësishme. Nuk ka, sipas njohurive të mia, një krahasim të familjeve "
            "algjoritmike mbi këtë dataset nën një protokoll rolling-origin ku çdo fold "
            "rindërton të gjithë zinxhirin e paraprocesimit dhe të pragjeve.",
            "Kostoja e ndershmërisë metodologjike — sa fryhen rezultatet nga ndarja e "
            "rastësishme — përmendet shpesh si rrezik, por rrallë matet mbi të njëjtat të "
            "dhëna dhe të njëjtat modele.",
            "Renditja e algoritmeve raportohet gjerësisht, por shpjegimi mekanicist i asaj "
            "renditjeje përmes atribuimit të veçorive mungon.",
            "Studimet mbi ansamblet për zbulim të pambikëqyrur raportojnë kryesisht "
            "rezultate pozitive; rezultatet negative, të cilat janë po aq informative kur "
            "shpjegohen, publikohen rrallë.",
        ]
    ),
    p("""Ky punim i adreson të katërt. Ai gjithashtu shton një kontribut praktik që nuk
      buron nga një boshllëk i literaturës por nga një problem i vërejtur gjatë
      implementimit: paqëndrueshmëria e ngarkesës hetimore kur pragu mbahet fiks mbi një
      rrjedhë që zhvendoset, dhe zgjidhja e saj me prag adaptiv me dritare rrëshqitëse."""),
]

BLOCKS = _PJESA_1 + _PJESA_2

"""Kapitulli 6 — DISKUTIME DHE PËRFUNDIME."""

from blocks import bullets, h1, h2, h3, note, numbers, p, tab

_SINTEZA = [
    h1("6", "Diskutime dhe përfundime"),
    h2("6.1", "Përmbledhje e gjetjeve"),
    p("""Përpara diskutimit të hollësishëm, tabela më poshtë jep përgjigjen e drejtpërdrejtë për
      secilën nga tri pyetjet hulumtuese së bashku me evidencën përkatëse. Ajo gjenerohet
      automatikisht nga artefaktet e eksperimenteve, prandaj nuk mund të bjerë ndesh me
      kapitujt që e paraprijnë."""),
    tab(
        "rq_summary",
        "Përgjigjet e drejtpërdrejta për tri pyetjet hulumtuese dhe evidenca mbi të cilën ato "
        "mbështeten.",
        font_size=8.5,
    ),
    p("""Ky punim ndërtoi dhe vlerësoi një sistem të plotë për zbulimin e anomalive mbi një
      rrjedhë të simuluar transaksionesh financiare, duke integruar Apache Kafka-n me tri
      algoritmet unsupervised të projekt-propozimit dhe me një referencë të mbikëqyrur. Gjetjet
      kryesore përmblidhen si vijon."""),
    numbers(
        [
            "Sistemi është i realizueshëm operacionalisht me rezervë të gjerë. Vonesa mesatare "
            "end-to-end qëndron midis pesëmbëdhjetë dhe pesëdhjetë e tre herë nën objektivin "
            "prej një sekonde në të gjashtëmbëdhjetë konfigurimet e testuara, percentili i "
            "nëntëdhjetë e nëntë nuk e kalon 132 milisekondën, dhe vetë inferenca zë nën dhjetë "
            "për qind të vonesës edhe në rastin më të keq.",
            "Kufiri i sipërm i problemit është gjeometrik dhe matet pa asnjë model. Mashtrimet "
            "ndodhen 7.9 herë më larg klasës legjitime sesa një transaksion tipik legjitim, por "
            "vetëm distanca jep Average Precision 0.30, sepse bishti i klasës legjitime e mbush të "
            "njëjtin rajon; mashtrimi median kërkon rreth 530 alarme.",
            "Nën konfigurimin bazë, Autoencoder-i ofron balancën më të mirë mes tre algoritmeve, "
            "i ndjekur nga One-Class SVM dhe nga Isolation Forest. Diferenca mes Autoencoder-it "
            "dhe Isolation Forest-it është statistikisht e qëndrueshme, ndërsa ajo mes "
            "Autoencoder-it dhe One-Class SVM-së nuk është.",
            "Zgjedhja e paraprocesimit ka ndikim më të madh se zgjedhja e algoritmit. Transformimi "
            "kuantil e ngre One-Class SVM-në me 0.218 njësi AP në të tetë fold-et, ndërsa "
            "referencën e mbikëqyrur nuk e prek fare.",
            "Dobësia e Isolation Forest-it është matur dhe jo hamendësuar. Pesë veçoritë më "
            "informative marrin 17.4 për qind të ndarjeve kundrejt 17.2 për qind që pritet nga "
            "rastësia e plotë, ndërsa rrotullimi i hapësirës e ndryshon rezultatin vetëm me 0.007 "
            "njësi, çka e përjashton përputhjen e boshteve si shpjegim.",
            "Referenca e mbikëqyrur mbetet dukshëm përpara, duke fituar në të tetë fold-et "
            "kundrejt "
            "secilit prej tre detektorëve.",
            "Akordimi i hiperparametrave e ndryshon renditjen mes dy detektorëve të fundit. "
            "Nën vlerat e parazgjedhura One-Class SVM qëndron para Isolation Forest-it; kur të "
            "tre akordohen njësoj, radha e tyre përmbyset, ndërsa udhëheqësi mbetet i njëjti.",
            "Në buxhet prej njëqind alarmesh, 37 për qind e mashtrimeve nuk arrihen nga asnjë "
            "detektor unsupervised, ndërsa referenca e mbikëqyrur i kap 59 për qind të tyre.",
            "Qasja ensemble nuk e përmirëson zbulimin në asnjë nga variantet e testuara, dhe "
            "analiza e gabimeve në nivel transaksioni e shpjegon pse.",
            "Kur secili detektor vlerësohet në konfigurimin e vet më të mirë, hapësira mes tyre "
            "bie nga 0.102 njësi në 0.049, pra nga një raport 2.1 herë në një raport 1.15 herë. "
            "Pjesa më e madhe e asaj që duket si dallim mes algoritmeve është dallim në se sa "
            "mirë vlerat e parazgjedhura u përshtaten këtyre të dhënave.",
            "Degradimi me kalimin e kohës vjen nga ndryshimi i popullatës së mashtrimeve dhe jo "
            "nga "
            "vjetërsimi i modelit të normalitetit.",
            "Pragu adaptiv me dritare rrëshqitëse e stabilizon ngarkesën hetimore dhe "
            "njëkohësisht e përmirëson cilësinë e zbulimit për të tre detektorët unsupervised, "
            "ndërsa për referencën e mbikëqyrur e përkeqëson atë; asimetria ka shpjegim të matur.",
        ]
    ),
    h2("6.2", "Interpretimi"),
    h3("6.2.1", "Pse rezultatet unsupervised janë modeste"),
    p("""Shpjegimi i parë dhe më i rëndësishëm nuk ka të bëjë me algoritmet. Karakterizimi
      gjeometrik tregoi se mashtrimet janë vërtet larg klasës legjitime, me distancë mesatare
      deri te fqinjët legjitimë afërsisht tetë herë më të madhe se ajo e një transaksioni tipik.
      Ky është pikërisht supozimi mbi të cilin mbështeten të tria metodat. Megjithatë, largësia
      nuk përkthehet në zbulim, sepse klasa legjitime ka njëqind e nëntëdhjetë e nëntë mijë
      anëtarë dhe bishti i saj e mbush të njëjtin rajon të largët; katërqind e nëntëdhjetë e dy
      mashtrime nuk mund të konkurrojnë numerikisht me pesë për qind të një popullate kaq të
      madhe."""),
    p("""Kjo është arsyeja pse një detektor pa asnjë parametër, që pikëzon thjesht sipas
      distancës nga fqinjët legjitimë, arrin Average Precision 0.30 në dritaren e trajnimit dhe
      0.12 në atë të testimit. Detektorët e trajnuar qëndrojnë brenda të njëjtit rend
      madhësie. Përfundimi është se pengesa nuk është zgjedhja e algoritmit, por gjeometria e
      problemit, dhe çdo krahasim algoritmesh duhet lexuar përballë atij kufiri."""),
    p("""Analiza e gabimeve e mbështet këtë nga një kënd tjetër dhe shton diçka të re. Në buxhet
      prej njëqind alarmesh, tridhjetë e shtatë për qind e mashtrimeve nuk arrihen nga asnjë
      detektor, dhe ato mashtrime ndodhen sistematikisht më afër popullatës legjitime.
      Megjithatë referenca e mbikëqyrur i kap pesëdhjetë e nëntë për qind të pikërisht atyre
      mashtrimeve brenda të njëjtit buxhet. Informacioni pra ekziston në të dhëna, por nuk është
      i formës që një detektor distancash mund ta shohë: ai qëndron në një drejtim diskriminues
      të cilin vetëm mbikëqyrja e gjen."""),
    h3("6.2.2", "Pse Isolation Forest renditet i fundit"),
    p("""Për Isolation Forest-in shpjegimi është strukturor dhe u mat drejtpërdrejt. Algoritmi
      zgjedh dimensionin e ndarjes në mënyrë uniforme të rastësishme, pa asnjë preferencë për
      informativitetin. Hapja e pemëve të përshtatura konfirmoi pikërisht këtë: veçoria më
      diskriminuese e dataset-it mori 3.5 për qind të ndarjeve, ndërsa pjesa e pritur nga
      rastësia e plotë është 3.4 për qind, dhe korrelacioni mes përdorimit të një kolone dhe
      fuqisë së saj diskriminuese është praktikisht zero."""),
    p("""Dy shpjegime alternative u testuan. I pari është se problemi mund të ishte thjesht
      akordimi, dhe ky shpjegim rezultoi pjesërisht i saktë. Sipërfaqja e hiperparametrave e
      ngriti detektorin nga 0.091 në 0.152, dhe kërkimi i plotë e ngriti më tej në 0.168, çka
      mjafton për ta kaluar One-Class SVM-në e akorduar. Vendi i fundit nën konfigurimin e
      parazgjedhur nuk është pra vendi i tij i pashmangshëm, dhe një pjesë e dobësisë së
      raportuar zakonisht për këtë algoritëm i takon vlerave të parazgjedhura të bibliotekave e
      jo vetë algoritmit. Megjithatë edhe pas akordimit ai mbetet nën Autoencoder-in, prandaj
      akordimi nuk e shpjegon të gjithë hendekun."""),
    p("""I dyti është se ndarjet paralele me boshtet mund të mos përshtaten me një hapësirë
      komponentësh kryesorë; ripërshtatja mbi një kopje të rrotulluar rastësisht e ndryshoi
      rezultatin vetëm me 0.007 njësi, çka e përjashton këtë shpjegim plotësisht."""),
    p("""Ndërhyrja eksperimentale e mbylli çështjen. Kur secilit detektor i jepen vetëm
      komponentët informativë, Isolation Forest-i është ai që fiton më shumë, siç do të pritej
      nëse dobësia e tij është shpërndarja e kapacitetit mbi kolona pa sinjal. Kjo e shndërron
      shpjegimin nga korrelacion në pohim kauzal."""),
    note("""Një vërejtje me interes praktik: performanca e dobët e Isolation Forest-it në këtë
      studim nuk duhet përgjithësuar në çdo problem. Ajo është pasojë e kombinimit mes
      dimensionalitetit të lartë dhe sinjalit të përqendruar në pak komponentë. Në probleme ku
      sinjali është i shpërndarë mbi shumë veçori, e njëjta rastësi e ndarjeve bëhet
      përparësi."""),
    h3("6.2.3", "Pse paraprocesimi peshon më shumë se algoritmi"),
    p("""Rezultati që ndoshta i kundërvihet më shumë intuitës është se zgjedhja e paraprocesimit
      i tejkalon dallimet mes vetë algoritmeve. Shpjegimi buron nga mekanizmi i përbashkët i
      tri metodave: të tria e përcaktojnë anomalinë përmes një nocioni largësie ose ngjeshjeje,
      dhe ai nocion përcaktohet plotësisht nga shkalla në të cilën vendosen veçoritë. Kur
      shkalla ndryshon, ndryshon vetë problemi që zgjidh algoritmi."""),
    p("""Asimetria me referencën e mbikëqyrur e vërteton këtë interpretim. Regresioni logjistik
      mëson një drejtim diskriminues dhe koeficientët e tij thjesht ripeshohen kur veçoritë
      riskalohen, prandaj rezultati i tij mbetet praktikisht i pandryshuar. E njëjta asimetri u
      vëzhgua edhe me ndarjen e rastësishme, ku metodat unsupervised fituan ndjeshëm ndërsa
      referenca jo. Të dyja rastet tregojnë të njëjtën gjë: metodat gjeometrike janë të
      ndjeshme ndaj asaj se si është ndërtuar hapësira, ndërsa një drejtim i mësuar nuk
      është."""),
    p("""Një hollësi teknike e vëzhguar në rezultate e forcon më tej pikën. Isolation Forest-i
      prodhon Average Precision saktësisht identik nën skalimin standard, atë robust, atë
      min-max dhe pa skalim fare. Kjo nuk është rastësi numerike, por pasojë e drejtpërdrejtë e
      algoritmit: pikat e ndarjes zgjidhen në mënyrë uniforme brenda intervalit të vëzhguar të
      secilës kolonë, prandaj çdo transformim afin i lë pemët të pandryshuara. Vetëm
      transformimet jo-afine, si ai kuantil, e lëvizin atë."""),
    h3("6.2.4", "Pse ansamblet nuk ndihmojnë"),
    p("""Teoria e ansambleve për zbulim të jashtëzakonshmërive e thotë qartë se mesatarizimi e
      zvogëlon variancën vetëm kur anëtarët gabojnë në mënyra të pavarura [@aggarwal2015]. Me
      tri anëtarë kjo kërkesë është edhe më e ashpër se me shumë, sepse nuk ka numër të madh
      votash mbi të cilat të mesatarizohet zhurma."""),
    p("""Analiza e gabimeve në nivel transaksioni tregon pse kushti nuk plotësohet. Nga
      mashtrimet që arrihen brenda buxhetit, një pjesë e madhe arrihet njëkohësisht nga të tre
      detektorët, ndërsa mashtrimet e paarritshme janë të paarritshme për të tre. Detektorët pra
      nuk gabojnë ndryshe; ata gabojnë njësoj, sepse të tre e ndjekin të njëjtën gjeometri. Në
      këto kushte kombinimi mund vetëm ta hollojë sinjalin e anëtarit më të mirë."""),
    p("""Ky përfundim ka vlerë praktike të drejtpërdrejtë. Në një hapësirë ku detektorët ndajnë
      të njëjtin mekanizëm bazë, investimi në një ansambël ka gjasa të japë më pak kthim se
      investimi në një paraprocesim më të mirë ose në një veçori të re. Rezultati gjithashtu
      tregon një rrezik konkret, sepse kombinimi i verbër i të gjithë detektorëve në
      dispozicion, praktikë e zakonshme, e ul cilësinë nën atë të anëtarit më të mirë."""),
    h3("6.2.5", "Pse renditja varet nga konfigurimi"),
    p("""Gjetja e nënkapitullit 5.16 e detyron një lexim më të kujdesshëm të çdo renditjeje të
      publikuar, përfshirë atë të këtij punimi. Nën konfigurimet e parazgjedhura tri algoritmet
      ndahen me raport 2.1 herë mes më të mirit dhe më të keqit; kur secilit i jepet
      paraprocesimi dhe hiperparametrat e vet më të mirë, ai raport bie në 1.15 herë dhe
      renditja përmbyset plotësisht."""),
    p("""Shpjegimi nuk është se algoritmet janë ekuivalente, por se vlerat e parazgjedhura të
      bibliotekave janë zgjedhur për probleme të tjera. Nën-mostra e parazgjedhur prej 256
      pikash e Isolation Forest-it vjen nga punimi origjinal, ku ajo justifikohet me argumentin
      se nën-mostra të vogla e zvogëlojnë maskimin; mbi këto të dhëna optimumi është
      gjashtëdhjetë e katër herë më i madh. Parametri nu i parazgjedhur prej 0.05 i One-Class
      SVM-së është tridhjetë herë mbi normën reale të mashtrimit. Dhe ngushtica e
      parazgjedhur e Autoencoder-it është më e ngushtë se optimumi i matur."""),
    p("""Pasoja metodologjike është se një krahasim algoritmesh nën vlera të parazgjedhura mat
      diçka të vërtetë por të kufizuar: sa mirë i shërbejnë secilit algoritëm zgjedhjet e
      autorëve të bibliotekës mbi këtë dataset. Ai nuk mat kapacitetin e algoritmit. Të dyja
      raportohen këtu, dhe dallimi mes tyre deklarohet, sepse studimet që raportojnë vetëm të
      parën dhe e përshkruajnë atë si të dytën janë burim i njohur i renditjeve që nuk
      përsëriten."""),
    h2("6.3", "Krahasimi me literaturën"),
    p("""Vlerat absolute të raportuara këtu janë dukshëm më të ulëta se shumica e rezultateve të
      publikuara mbi këtë dataset. Punimi ofron tri shpjegime të matura për këtë dallim në vend
      që ta lërë të pashpjeguar."""),
    p("""Së pari, protokolli. Krahasimi i drejtpërdrejtë tregoi se ndarja e rastësishme e
      stratifikuar e fryn Average Precision e metodave unsupervised mbi të njëjtat të dhëna dhe
      të njëjtat modele. Studimet që raportojnë ndarje të rastësishme nuk janë domosdoshmërisht
      të gabuara në implementim, por matin një problem më të lehtë se ai që has një sistem
      prodhimi."""),
    p("""Së dyti, metrika. Një pjesë e literaturës mbi këtë dataset raporton AUC-ROC mbi 0.95 dhe
      e paraqet si sukses. Rezultatet këtu tregojnë se AUC-ROC mbi 0.94 është e arritshme edhe
      nga detektori më i dobët i studimit, i cili ka Average Precision nën 0.10. Pra ajo metrikë
      nuk e dallon një detektor të përdorshëm nga një i papërdorshëm në këtë nivel çekuilibri,
      siç e kanë argumentuar Davis dhe Goadrich [@davis2006] dhe e kanë demonstruar Saito dhe
      Rehmsmeier [@saito2015]."""),
    p("""Së treti, mungesa e agregimit. Puna aplikative më e suksesshme mbi zbulimin e
      mashtrimeve mbështetet fort te veçoritë e agreguara për llogari mbi dritare kohore
      [@whitrow2009], [@bahnsen2016], ose te modelimi sekuencial i sjelljes së mbajtësit
      [@jurgovsky2018]. Dataset-i publik i përdorur këtu nuk përmban identifikuesin e kartës,
      prandaj asnjë prej këtyre rrugëve nuk ishte e hapur, dhe rezultatet duhen lexuar si kufi i
      poshtëm i asaj që arrihet me zbulim pikësor pa kontekst llogarie."""),
    p("""Gjetja se pikët unsupervised mbeten dukshëm nën një model të mbikëqyrur përputhet me atë
      të Carcillo-s dhe bashkautorëve, të cilët megjithatë treguan se këto pikë mbajnë
      informacion plotësues kur përdoren si veçori shtesë për një klasifikues të mbikëqyrur
      [@carcillo2021]. Analiza e gabimeve këtu e mbështet atë drejtim: mashtrimet që detektorët
      unsupervised nuk i arrijnë kapen kryesisht nga referenca, çka do të thotë se të dy burimet
      e informacionit nuk mbivendosen plotësisht."""),
    h2("6.4", "Implikime praktike"),
    p("""Për një institucion që do të ndërtonte një sistem të tillë, rezultatet sugjerojnë gjashtë
      përfundime konkrete."""),
    bullets(
        [
            "Infrastruktura nuk është pengesa. Me një broker të vetëm dhe një consumer, vonesa "
            "mbetet dukshëm nën objektivin deri në një mijë transaksione në sekondë. Investimi "
            "duhet shkuar te cilësia e modelit dhe te të dhënat, jo te optimizimi i transportit.",
            "Paraprocesimi duhet akorduar bashkë me modelin. Në këtë studim ai dha përfitime më të "
            "mëdha se çdo zgjedhje algoritmi, dhe një sistem që e trajton skaluesin si detaj "
            "implementimi po lë vlerë të konsiderueshme pa marrë.",
            "Kostoja e pikëzimit duhet të jetë kriter zgjedhjeje qysh në fillim. Dy metoda me "
            "cilësi të ngjashme mund të ndryshojnë me qindra herë në kosto pikëzimi, dhe në "
            "rrjedhë "
            "ky dallim përcakton nëse metoda është e vendosshme apo jo.",
            "Etiketat historike, edhe të vonuara, kanë vlerë të madhe. Hendeku i matur dhe analiza "
            "e mashtrimeve të paarritshme sugjerojnë që metodat unsupervised duhen përdorur si "
            "shtresë plotësuese për periudhën pa etiketa, jo si zëvendësim i përhershëm.",
            "Pragu duhet të jetë adaptiv për detektorët unsupervised, por jo për një model të "
            "kalibruar. Një prag i fiksuar në trajnim e bën ngarkesën hetimore të "
            "paparashikueshme pikërisht kur të dhënat ndryshojnë, dhe procedura e propozuar këtu "
            "e stabilizon atë duke përmirësuar edhe cilësinë; e njëjta procedurë e dëmton një "
            "model që tashmë prodhon probabilitete të kalibruara.",
            "Monitorimi i zhvendosjes duhet të dallojë popullatat. Nëse zhvendoset popullata "
            "normale, ritrajnimi ndihmon; nëse zhvendoset ajo e mashtrimeve, nevojiten veçori të "
            "reja ose etiketa, dhe ritrajnimi është humbje kohe.",
        ]
    ),
    h2("6.5", "Kufizimet"),
    p("""Kufizimet e këtij studimi janë të shumta dhe deklarohen shprehimisht, sepse leximi i
      rezultateve pa to do të ishte i gabuar."""),
    h3("6.5.1", "Kufizimet e të dhënave"),
    bullets(
        [
            "Mungesa e identifikuesit të kartës e bën të pamundur agregimin për llogari dhe "
            "modelimin sekuencial, pra dy nga tri llojet e anomalive në taksonominë standarde "
            "[@chandola2009] mbeten jashtë fushëveprimit.",
            "Kohëzgjatja prej dyzet e tetë orësh lejon vetëm vlerësimin e zhvendosjes "
            "brenda-ditore "
            "dhe mes dy ditëve, jo të asaj sezonale.",
            "Anonimizimi me PCA e bën interpretimin semantik të pamundur; interpretueshmëria e "
            "arritur këtu është relative ndaj sinjalit dhe jo ndaj kuptimit të biznesit.",
            "Etiketat supozohen të plota; mashtrimet e pakontestuara, të cilat ekzistojnë në "
            "realitet, do t'i bënin vlerësimet e precision-it pesimiste.",
        ]
    ),
    h3("6.5.2", "Kufizimet e vlerësimit"),
    bullets(
        [
            "Tetë fold-e japin fuqi statistikore të kufizuar. Kufizimi i krahasimit te tri "
            "algoritmet e bëri testin post-hoc të përdorshëm, por me një bashkësi më të gjerë ai "
            "do "
            "të ishte përsëri i pafuqishëm.",
            "Numri i pozitivëve për bllok testimi varion nga trembëdhjetë në tetëdhjetë e tetë, "
            "prandaj disa vlerësime për fold janë të zhurmshme, gjë që pasqyrohet në devijimet "
            "standarde të mëdha.",
            "Akordimi i hiperparametrave u krye një herë, në prerjen 70/30, dhe jo brenda çdo "
            "fold-i. Ri-akordimi për fold do të ishte më i rreptë por do ta shumëfishonte koston "
            "llogaritëse tetë herë.",
            "Kontaminimi i parazgjedhur nxirret nga norma e mashtrimit në dritaren e trajnimit, "
            "pra "
            "përdor etiketa historike. Kjo është e deklaruar dhe e njëjtë me supozimin e "
            "referencës "
            "së mbikëqyrur, por nuk është plotësisht pa etiketa.",
            "Studimi i paraprocesimit dhe ai i hiperparametrave u kryen veçmas dhe u kombinuan më "
            "pas në një dizajn dy-nga-dy; një kërkim i përbashkët mbi të dyja hapësirat "
            "njëkohësisht do të ishte më i plotë.",
        ]
    ),
    h3("6.5.3", "Kufizimet operacionale"),
    bullets(
        [
            "Ritmi i mbërritjes është sintetik dhe konstant. Trafiku real është i shpërthyeshëm, "
            "dhe shpërthimet do ta zhvendosnin bishtin e vonesës lart.",
            "Të gjitha matjet u kryen në një host të vetëm me një broker dhe një particion, "
            "prandaj "
            "rezultatet nuk thonë asgjë për sjelljen në një grumbull të shpërndarë.",
            "Sistemi nuk trajton dështime, ritentativa apo mesazhe të dyfishta, dhe nuk përfshin "
            "ritrajnim automatik.",
        ]
    ),
    h2("6.6", "Drejtime për punë të mëtejshme"),
    p("""Nga kufizimet dalin drejtimet, të renditura sipas premtimit që kanë."""),
    numbers(
        [
            "Vlerësimi mbi një dataset me identifikues llogarie, ku veçoritë e agreguara për "
            "mbajtës "
            "mund të ndërtohen. Kjo do të testonte nëse hendeku mes metodave unsupervised dhe "
            "atyre "
            "të mbikëqyrura ngushtohet kur konteksti bëhet i disponueshëm, dhe analiza e "
            "mashtrimeve të paarritshme sugjeron se pikërisht aty qëndron pjesa më e madhe e "
            "hapësirës për përmirësim.",
            "Kombinimi hibrid në stilin e Carcillo-s dhe bashkautorëve [@carcillo2021], ku pikët "
            "unsupervised shërbejnë si veçori shtesë për një model të mbikëqyrur të trajnuar mbi "
            "etiketat e vonuara.",
            "Kërkim i përbashkët mbi hapësirën e paraprocesimit dhe atë të hiperparametrave. Meqë "
            "të dyja ndikojnë ndjeshëm dhe ndërveprojnë, optimizimi i tyre veçmas nuk e gjen "
            "domosdoshmërisht konfigurimin më të mirë.",
            "Zgjerimi i familjes së detektorëve me metoda deep one-class si Deep SVDD [@ruff2018] "
            "ose me modele gjenerative të thella, të vlerësuara nën të njëjtin protokoll dhe me të "
            "njëjtin karakterizim gjeometrik paraprak.",
            "Ritrajnim inkremental me dritare rrëshqitëse dhe krahasim i drejtpërdrejtë me "
            "trajnimin "
            "një herë, në kuadrin e vlerësimit prekuencial [@gama2013]. Analiza e zhvendosjes këtu "
            "parashikon se përfitimi do të jetë modest, dhe ky parashikim është i testueshëm.",
            "Testimi i sistemit nën trafik të shpërthyeshëm dhe me disa consumer-a paralelë, për "
            "të "
            "matur sjelljen e vonesës nën ngarkesë realiste.",
        ]
    ),
    h2("6.7", "Përfundime"),
    p("""Ky punim tregoi se një pipeline i plotë për zbulimin e anomalive mbi një rrjedhë të
      simuluar transaksionesh është i realizueshëm me teknologji të lira dhe të hapura, dhe se
      kufizimi operacional prej një sekonde nuk është pengesa reale, sepse tejkalohet me një
      rend madhësie. Pengesa reale është cilësia e zbulimit pa etiketa, dhe ky punim e mati atë
      me kujdes në vend që ta anashkalonte."""),
    p("""Kontributi më i qëndrueshëm nuk është renditja e tri algoritmeve, e cila varet nga
      dataset-i dhe nga protokolli, por metodologjia dhe katër gjetjet shpjeguese që ajo
      mundësoi: përcaktimi i kufirit gjeometrik të problemit para çdo modelimi, kuantifikimi i
      fryrjes që prodhon ndarja e rastësishme, dekompozimi i degradimit në zhvendosje të
      popullatës së mashtrimeve dhe jo të asaj normale, dhe shndërrimi i shpjegimit të renditjes
      nga korrelacion në pohim kauzal përmes një ndërhyrjeje eksperimentale."""),
    p("""Dy nga tri hipotezat u konfirmuan dhe një u refuzua. Sistemi arrin vonesë nën një
      sekondë. Të paktën një metodë unsupervised arrin cilësi dukshëm mbi rastësinë dhe e ruan
      renditjen e saj nëpër fold-e. Qasja ensemble nuk e tejkalon modelin më të mirë individual,
      dhe refuzimi i hipotezës së tretë raportohet si gjetje e jo si dështim, i shoqëruar me
      shpjegimin e tij të matur në nivel transaksioni."""),
    p("""Mësimi i vetëm më i rëndësishëm i kësaj pune është se në këtë fushë vendimet
      metodologjike ndikojnë në rezultatin e raportuar më shumë se zgjedhja e algoritmit. Një
      ndarje e rastësishme e fryn Average Precision më shumë se sa e përmirëson atë kalimi nga
      algoritmi më i dobët te ai më i miri, dhe një zgjedhje tjetër paraprocesimi e bën po
      ashtu. Kjo do të thotë se përparimi i vërtetë matet vetëm nën protokolle të deklaruara
      plotësisht, dhe se raportimi i një numri të vetëm, pa pasigurinë e tij, pa protokollin e
      ndarjes dhe pa procedurën e paraprocesimit e të akordimit, fsheh më shumë sesa
      zbulon."""),
]

BLOCKS = _SINTEZA

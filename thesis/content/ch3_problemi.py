"""Kapitulli 3 — DEKLARIMI I PROBLEMIT."""

from blocks import bullets, eq, fig, h1, h2, numbers, p

BLOCKS = [
    h1("3", "Deklarimi i problemit"),
    p("""Ky kapitull e përcakton problemin me saktësi të mjaftueshme sa çdo pohim i
      mëvonshëm të jetë i verifikueshëm: formalizimin matematik, kufizimet operacionale
      që e bëjnë problemin të ndryshëm nga klasifikimi i zakonshëm, hipotezat që testohen
      dhe kriteret sipas të cilave gjykohet suksesi."""),
    h2("3.1", "Formulimi formal"),
    p("""Le të jetë një rrjedhë transaksionesh një sekuencë e renditur në kohë"""),
    eq("S = ⟨(x₁,t₁), …, (x_N,t_N)⟩,   t₁ ≤ t₂ ≤ … ≤ t_N"),
    p("""ku x_i ∈ ℝ^d është vektori i veçorive i transaksionit të i-të dhe t_i koha e tij.
      Secilit transaksion i përgjigjet një etiketë e vërtetë y_i ∈ {0, 1}, ku 1 shënon
      mashtrim, por kjo etiketë nuk është e disponueshme në momentin e vendimit. Kërkohet
      një funksion pikëzimi"""),
    eq("s: ℝ^d → ℝ,   vlerë më e lartë = më anormale"),
    p("""i mësuar vetëm nga transaksionet e vëzhguara para një momenti prerjeje T, dhe një
      prag τ i nxjerrë gjithashtu vetëm nga ato të dhëna, i tillë që vendimi
      ŷ_i = 1[s(x_i) ≥ τ] të jetë sa më i dobishëm. Kufizimi qendror është shkakësia:
      as s dhe as τ nuk mund të varen nga asnjë vëzhgim me t > T."""),
    p("""Për modelet e pambikëqyrura, bashkësia e trajnimit kufizohet më tej te
      transaksionet normale të dritares së trajnimit:"""),
    eq("D_train = { x_i : t_i < T,  y_i = 0 }"),
    p("""Ky kufizim pasqyron supozimin operacional se histori e verifikuar ekziston për të
      kaluarën e largët — një bankë e di se cilat transaksione të muajit të kaluar u
      kontestuan — ndërsa për rrjedhën aktuale nuk ekziston. Referenca e mbikëqyrur
      trajnohet mbi të njëjtën dritare por me të dyja klasat dhe me etiketa, dhe pikërisht
      për këtë arsye nuk është konkurrent i barabartë, por kufi i sipërm."""),
    h2("3.2", "Kufizimet që e bëjnë problemin të veçantë"),
    p("""Katër kufizime e dallojnë këtë formulim nga klasifikimi i zakonshëm binar, dhe
      secili prej tyre ka pasojë të drejtpërdrejtë në dizajnin e eksperimentit."""),
    numbers(
        [
            "Çekuilibri ekstrem. Me rreth 0.17 për qind pozitivë, saktësia dhe AUC-ROC-ja "
            "japin një pamje sistematikisht optimiste; prandaj metrika kryesore këtu është "
            "precizioni mesatar dhe raportohen edhe metrika në buxhet fiks alarmesh.",
            "Mungesa e etiketave në kohën e vendimit. Kjo përjashton çdo teknikë që kërkon "
            "etiketa gjatë inferencës ose gjatë kalibrimit të pragut mbi të dhënat aktuale.",
            "Renditja kohore. Transaksionet nuk janë mostra të pavarura dhe identikisht të "
            "shpërndara; përzierja e tyre shkatërron pikërisht strukturën që sistemi duhet "
            "të përballojë.",
            "Kufiri i vonesës. Vendimi duhet të mbërrijë brenda dritares së autorizimit, gjë "
            "që e bën koston e inferencës kriter zgjedhjeje po aq legjitim sa cilësinë e "
            "zbulimit.",
        ]
    ),
    h2("3.3", "Hipotezat"),
    p("""Projekt-propozimi formuloi tri hipoteza pune. Ato riformulohen këtu në formë të
      testueshme, me kriterin e refuzimit të përcaktuar paraprakisht."""),
    bullets(
        [
            "H1 — Realizueshmëria operacionale. Një pipeline Kafka me inferencë të "
            "pambikëqyrur mund të mbajë vonesë mesatare fund-më-fund nën një sekondë nën "
            "ritme sintetike mbërritjeje deri në një mijë mesazhe në sekondë. Refuzohet nëse "
            "vonesa mesatare e matur e kalon këtë kufi në ndonjë nga konfigurimet e testuara.",
            "H2 — Vlera e metodave të pambikëqyrura. Të paktën një metodë e pambikëqyrur "
            "arrin cilësi zbulimi dukshëm mbi rastësinë dhe e ruan atë në mënyrë të "
            "qëndrueshme nëpër pikat kohore të prerjes. Refuzohet nëse asnjë metodë nuk e "
            "kalon bindshëm nivelin e rastësisë ose nëse renditja është krejtësisht e "
            "paqëndrueshme nëpër folds.",
            "H3 — Vlera e ansamblit. Kombinimi i disa detektorëve e tejkalon modelin më të "
            "mirë individual. Refuzohet nëse asnjë variant kombinimi nuk e tejkalon atë në "
            "precizionin mesatar mbi folds.",
        ]
    ),
    p("""Formulimi paraprak i kritereve të refuzimit është një zgjedhje metodologjike e
      qëllimshme. Pa të, një hipotezë mund të "konfirmohet" duke zgjedhur pas faktit
      metrikën ose nënbashkësinë e folds-ave ku ajo del e vërtetë."""),
    h2("3.4", "Formulimi i objektivit të vlerësimit"),
    p("""Përcaktimi i funksionit të pikëzimit nuk mjafton; duhet përcaktuar edhe se çfarë
      do të thotë "i mirë". Metrika parësore këtu është precizioni mesatar, i cili
      përmbledh kurbën precision–recall pa u lidhur me një prag të vetëm:"""),
    eq("AP = Σ_n (R_n − R_{n−1}) · P_n"),
    p("""ku P_n dhe R_n janë preciziteti dhe ndjeshmëria në pragun e n-të të renditjes.
      Vlera e pritur e AP-së për një renditje krejtësisht të rastësishme është e barabartë
      me normën e klasës pozitive, pra rreth 0.0017 në këtë dataset. Ky është niveli i
      referencës kundrejt të cilit duhen lexuar të gjitha vlerat e raportuara: një AP prej
      0.09 nuk është "e ulët" në kuptimin absolut, ajo është pesëdhjetë herë mbi
      rastësinë; por ajo mbetet e pamjaftueshme operacionalisht, dhe ky dallim mes
      domethënies statistikore dhe dobisë praktike përshkon gjithë punimin."""),
    p("""Objektivi operacional formulohet veçmas. Nëse ekipi hetimor mund të shqyrtojë k
      alarme për periudhë, atëherë madhësia me interes nuk është AP-ja por vlera e
      rikuperuar brenda atij buxheti:"""),
    eq("Kursimi(k) = Σ_{i∈TP(k)} shuma_i − c_het · k"),
    p("""Këto dy objektiva nuk maksimizohen domosdoshmërisht nga i njëjti model, dhe
      rezultatet e Kapitullit 5 tregojnë se në disa raste renditja ndryshon kur kalohet nga
      njëri te tjetri. Raportimi i të dyve, në vend të njërit, është zgjedhje e
      qëllimshme."""),
    h2("3.5", "Supozimet"),
    p("""Katër supozime qëndrojnë nën gjithë ndërtimin dhe shkelja e secilit do të kufizonte
      vlefshmërinë e përfundimeve në një mënyrë specifike."""),
    numbers(
        [
            "Etiketat historike janë të disponueshme për të kaluarën e largët dhe të sakta. "
            "Kjo lejon nxjerrjen e normës së kontaminimit dhe trajnimin e referencës së "
            "mbikëqyrur. Nëse etiketat historike do të ishin të pjesshme, siç janë në "
            "realitet, referenca e mbikëqyrur do të ishte më e dobët dhe hendeku i matur më i "
            "vogël.",
            "Transaksionet normale të dritares së trajnimit janë përfaqësuese të normalitetit. "
            "Kjo është vetë supozimi i çdo metode të pambikëqyrur; analiza e zhvendosjes në "
            "Kapitullin 5 e teston atë në mënyrë empirike.",
            "Renditja sipas kolonës Time pasqyron rendin real të ngjarjeve. Dataset-i nuk "
            "përmban vula kohore absolute, vetëm sekonda nga transaksioni i parë, dhe "
            "besueshmëria e tyre merret si e mirëqenë.",
            "Kostoja e një hetimi është konstante dhe e pavarur nga transaksioni. Në realitet "
            "hetimi i një transaksioni me vlerë të lartë mund të justifikojë më shumë kohë; "
            "ndjeshmëria ndaj kësaj zgjedhjeje diskutohet në Kapitullin 6.",
        ]
    ),
    h2("3.6", "Rreziqet metodologjike dhe masat mbrojtëse"),
    p("""Katër rrugë të veçanta rrjedhjeje informacioni mund ta shndërrojnë këtë
      eksperiment në një ushtrim vetëkonfirmues. Figura më poshtë i përmbledh së bashku
      me masën konkrete që merret kundër secilës në implementim; secila masë verifikohet
      me test automatik në grupin e testeve të projektit."""),
    fig(
        "diagram_leakage",
        "Katër rrugët e rrjedhjes së informacionit dhe masat mbrojtëse përkatëse. "
        "Secila masë është e mbuluar nga një test automatik në depon e kodit.",
        15.0,
    ),
    p("""Rruga e katërt meriton koment të veçantë, sepse është më e fshehta. Nëse
      hiperparametrat zgjidhen duke parë rezultatin në bashkësinë e testimit, atëherë
      numri i raportuar nuk është performancë e pritshme por vlera maksimale e një
      kërkimi mbi testin. Në këtë punim zgjedhja bëhet mbi një ndarje të brendshme kohore
      të dritares së trajnimit, dhe përveç kësaj testohet edhe një rrugë krejtësisht pa
      etiketa, përmes kritereve Excess-Mass dhe Mass-Volume."""),
    h2("3.7", "Kriteret e suksesit"),
    p("""Suksesi i këtij punimi nuk matet me arritjen e një vlere të caktuar të metrikës.
      Kjo është e qëllimshme: një objektiv numerik i paracaktuar krijon presion për ta
      arritur atë me mjete metodologjikisht të dyshimta. Kriteret janë të tjera:"""),
    bullets(
        [
            "Çdo pohim në kapitullin e rezultateve gjurmohet te një artefakt i gjeneruar nga "
            "kodi — një CSV, një JSON ose një figurë — dhe te një manifest që përmban SHA-në "
            "e commit-it, hash-in e konfigurimit dhe versionet e paketave.",
            "I gjithë eksperimenti riprodhohet me një komandë të vetme dhe jep numra "
            "identikë; determinizmi verifikohet me krahasim bit-për-bit të tabelave mes dy "
            "ekzekutimeve të pavarura.",
            "Të tria pyetjet hulumtuese marrin përgjigje të drejtpërdrejtë, duke përfshirë "
            "përgjigjet negative aty ku rezultati është i tillë.",
            "Kufizimet e studimit deklarohen shprehimisht dhe nuk maskohen me zgjedhje raportimi.",
        ]
    ),
]

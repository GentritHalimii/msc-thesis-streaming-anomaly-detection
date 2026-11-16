"""Kapitulli 3 — DEKLARIMI I PROBLEMIT."""

from blocks import bullets, eq, fig, h1, h2, numbers, p

BLOCKS = [
    h1("3", "Deklarimi i problemit"),
    p("""Ky kapitull e përcakton problemin aq saktë sa çdo pohim i mëvonshëm të mund të verifikohet.
      Jepen formulimi matematik, kufizimet operacionale që e dallojnë nga klasifikimi i zakonshëm,
      objektivi i vlerësimit, supozimet, hipotezat dhe kriteret sipas të cilave gjykohet suksesi i
      punimit."""),
    h2("3.1", "Formulimi formal"),
    p("""Le të jetë rrjedha e transaksioneve një varg i renditur në kohë"""),
    eq("S = ⟨(x₁,t₁), …, (x_N,t_N)⟩,   t₁ ≤ t₂ ≤ … ≤ t_N"),
    p("""ku x_i ∈ ℝ^d është vektori i veçorive të transaksionit të i-të dhe t_i koha e tij. Çdo
      transaksioni i përgjigjet një etiketë e vërtetë y_i ∈ {0, 1}, ku 1 shënon mashtrim, por kjo
      etiketë nuk dihet në momentin e vendimit. Kërkohet një funksion që i jep çdo transaksioni një
      pikë anomalie"""),
    eq("s: ℝ^d → ℝ,   vlerë më e lartë = më anormale"),
    p("""i mësuar vetëm nga transaksionet e vëzhguara para një momenti prerjeje T, dhe një prag τ, i
      nxjerrë gjithashtu vetëm nga këto të dhëna, të tillë që vendimi ŷ_i = 1[s(x_i) ≥ τ] të jetë sa
      më i dobishëm. Kufizimi kryesor është shkakësia: as s, as τ nuk mund të varen nga ndonjë
      vëzhgim me t > T."""),
    p("""Për modelet unsupervised, të dhënat e trajnimit kufizohen te transaksionet normale të
      dritares së trajnimit:"""),
    eq("D_train = { x_i : t_i < T,  y_i = 0 }"),
    p("""Kjo pasqyron supozimin se historia e verifikuar ekziston për të kaluarën: një bankë e di se
      cilat transaksione të muajit të kaluar u kontestuan, por për rrjedhën aktuale nuk e di. Duhet
      thënë qartë se ky është një përdorim i etiketave historike, edhe pse i kufizuar vetëm në
      pastrimin e të dhënave të trajnimit. Referenca supervised trajnohet mbi të njëjtën dritare,
      por me të dyja klasat dhe me etiketa, prandaj shërben si kufi i sipërm e jo si konkurrent i
      barabartë."""),
    h2("3.2", "Kufizimet që e bëjnë problemin të veçantë"),
    p("""Katër kufizime e dallojnë këtë formulim nga klasifikimi i zakonshëm binar, dhe secili prej
      tyre e formëson dizajnin e eksperimentit."""),
    numbers(
        [
            "Çekuilibri ekstrem. Me rreth 0.17% pozitivë, saktësia dhe AUC-ROC japin një pamje "
            "sistematikisht optimiste, prandaj metrika kryesore është Average Precision dhe "
            "raportohen edhe metrika për buxhete të fiksuara alarmesh.",
            "Mungesa e etiketave në momentin e vendimit. Përjashtohet çdo teknikë që kërkon "
            "etiketa gjatë inferencës ose për kalibrimin e pragut mbi të dhënat aktuale.",
            "Renditja kohore. Transaksionet nuk janë mostra të pavarura dhe me shpërndarje të "
            "njëjtë; përzierja e tyre prish strukturën me të cilën sistemi duhet të përballet.",
            "Kufiri i vonesës. Vendimi ka vlerë vetëm nëse jepet para autorizimit, prandaj kostoja "
            "e inferencës është kriter zgjedhjeje po aq i rëndësishëm sa cilësia e zbulimit.",
        ]
    ),
    h2("3.3", "Formulimi i objektivit të vlerësimit"),
    p("""Nuk mjafton të përcaktohet funksioni s; duhet përcaktuar edhe çfarë do të thotë që ai është
      i mirë. Metrika kryesore është Average Precision, e cila përmbledh kurbën precision-recall pa
      u lidhur me një prag të vetëm:"""),
    eq("AP = Σ_n (R_n − R_{n−1}) · P_n"),
    p("""ku P_n dhe R_n janë precision dhe recall në pragun e n-të të renditjes. Për një renditje
      krejt të rastësishme vlera e pritur e AP-së është e barabartë me pjesën e klasës pozitive, pra
      rreth 0.0017 për këtë dataset. Kundrejt këtij niveli duhen lexuar të gjitha vlerat e
      raportuara: një AP prej 0.09 nuk është e ulët në kuptimin absolut, sepse është rreth 50 herë
      mbi rastësinë, por operacionalisht mbetet e pamjaftueshme. Dallimi mes domethënies
      statistikore dhe dobisë praktike shfaqet gjatë gjithë punimit."""),
    p("""Objektivi operacional formulohet veçmas. Nëse ekipi i hetimeve mund të shqyrtojë k alarme
      në një periudhë, ajo që ka rëndësi nuk është AP-ja, por sa mashtrime dhe sa vlerë monetare
      kapen brenda këtij buxheti. Dy objektivat nuk maksimizohen domosdoshmërisht nga i njëjti
      model, dhe në Kapitullin 5 renditja ndryshon kur kalohet nga njëri te tjetri. Për këtë arsye
      raportohen të dy."""),
    h2("3.4", "Supozimet"),
    p("""Studimi mbështetet në tri supozime. Nëse ndonjëri prej tyre nuk vlen, përfundimet kufizohen
      në mënyrën që përshkruhet më poshtë."""),
    numbers(
        [
            "Etiketat historike janë të disponueshme dhe të sakta. Kjo lejon llogaritjen e normës "
            "së kontaminimit, pastrimin e të dhënave të trajnimit dhe trajnimin e referencës "
            "supervised. Në realitet etiketat historike janë të paplota, kështu që referenca do të "
            "ishte më e dobët dhe hendeku i matur më i vogël.",
            "Transaksionet normale të dritares së trajnimit janë përfaqësuese të normalitetit. Ky "
            "është supozimi i çdo metode unsupervised, dhe analiza e zhvendosjes në Shtojcën E e "
            "teston atë empirikisht.",
            "Renditja sipas kolonës Time pasqyron rendin real të eventeve. Dataset-i nuk ka vula "
            "kohore absolute, vetëm sekonda nga transaksioni i parë, dhe ato pranohen ashtu siç "
            "janë.",
        ]
    ),
    h2("3.5", "Hipotezat"),
    p("""Punimi shtron tri hipoteza pune, të formuluara në mënyrë të testueshme dhe me kriterin e
      refuzimit të përcaktuar paraprakisht."""),
    bullets(
        [
            "H1, realizueshmëria operacionale. Një pipeline me Kafka dhe inferencë unsupervised "
            "mund të mbajë vonesë mesatare end-to-end nën një sekondë me ritme sintetike "
            "mbërritjeje deri në 1000 mesazhe në sekondë. Hipoteza refuzohet nëse vonesa mesatare "
            "e matur e kalon këtë kufi në ndonjë nga konfigurimet e testuara.",
            "H2, vlera e metodave unsupervised. Të paktën një metodë unsupervised arrin cilësi "
            "zbulimi qartësisht mbi rastësinë dhe e ruan atë në të gjitha pikat kohore të prerjes. "
            "Hipoteza refuzohet nëse asnjë metodë nuk e kalon bindshëm nivelin e rastësisë ose "
            "nëse renditja ndryshon pa ndonjë rregull nga një fold në tjetrin.",
            "H3, vlera e ansamblit. Kombinimi i disa detektorëve e kalon modelin më të mirë "
            "individual. Hipoteza refuzohet nëse asnjë variant kombinimi nuk e kalon atë në "
            "Average Precision mesatare mbi fold-et.",
        ]
    ),
    p("""Kriteret e refuzimit u përcaktuan para eksperimenteve, në mënyrë që hipotezat të mos
      konfirmohen pas faktit duke zgjedhur metrikën ose fold-et ku rezultati del i favorshëm."""),
    h2("3.6", "Rreziqet metodologjike dhe masat mbrojtëse"),
    p("""Informacioni nga e ardhmja mund të hyjë në eksperiment nga katër rrugë të ndryshme, dhe
      secila prej tyre do ta bënte vlerësimin vetëkonfirmues. Figura [[fig:diagram_leakage]] i
      përmbledh këto rrugë së bashku me masën e marrë kundër secilës. Çdo masë kontrollohet nga një
      test automatik në kodin e projektit."""),
    fig("diagram_leakage", "Rrugët e rrjedhjes së informacionit dhe masat kundër tyre.", 15.0),
    p("""Rruga e katërt kërkon kujdes të veçantë, sepse vërehet më vështirë. Nëse hiperparametrat
      zgjidhen duke parë rezultatin në të dhënat e testit, numri i raportuar nuk është performanca e
      pritur, por maksimumi i një kërkimi mbi testin. Në këtë punim zgjedhja bëhet mbi një ndarje të
      brendshme kohore të dritares së trajnimit, dhe pasoja e saj për fold-et e hershme trajtohet në
      nënkapitullin 4.7."""),
    h2("3.7", "Kriteret e suksesit"),
    p("""Suksesi i punimit nuk matet me arritjen e një vlere të caktuar të metrikës, sepse një
      objektiv numerik i paracaktuar krijon presion për ta arritur atë me mjete metodologjikisht të
      dyshimta. Kriteret janë këto:"""),
    bullets(
        [
            "Çdo pohim në kapitullin e rezultateve lidhet me një artefakt të gjeneruar nga kodi "
            "(një tabelë CSV, një skedar JSON ose një figurë) dhe me një manifest që ruan SHA-në e "
            "commit-it, hash-in e konfigurimit dhe versionet e paketave.",
            "I gjithë eksperimenti riprodhohet me komanda të dokumentuara dhe jep të njëjtët "
            "numra; determinizmi kontrollohet duke krahasuar tabelat e dy ekzekutimeve të "
            "pavarura.",
            "Të tri pyetjet hulumtuese marrin përgjigje të drejtpërdrejtë, edhe kur përgjigjja "
            "është negative.",
            "Kufizimet e studimit thuhen hapur dhe nuk fshihen me zgjedhjen e asaj që raportohet.",
        ]
    ),
]

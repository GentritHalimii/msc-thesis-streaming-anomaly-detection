"""Kapitulli 1 — HYRJE."""

from blocks import bullets, fig, h1, h2, note, numbers, p, tab

BLOCKS = [
    h1("1", "Hyrje"),

    h2("1.1", "Konteksti dhe motivimi"),
    p("""Pagesat me karta janë bërë infrastrukturë kritike e ekonomisë evropiane, dhe
      bashkë me to është rritur edhe sipërfaqja e sulmit. Sipas raportit të Bankës
      Qendrore Evropiane mbi mashtrimet me karta, humbjet vjetore në Zonën e Vetme të
      Pagesave në Euro matën në qindra miliona euro, me një zhvendosje të qartë drejt
      transaksioneve ku karta nuk paraqitet fizikisht [@ecb2021]. Kjo zhvendosje ka një
      pasojë teknike të drejtpërdrejtë: kontrollet që mbështeteshin te prania fizike e
      kartës ose te sjellja e terminalit humbasin vlerën, dhe pesha e vendimit bie mbi
      analizën e vetë të dhënave të transaksionit.""" ),
    p("""Ajo që e bën këtë problem të vështirë nuk është vetëm vëllimi. Është kombinimi i
      tre kufizimeve që rrallë shfaqen bashkë. E para është çekuilibri ekstrem i klasave:
      mashtrimet përbëjnë një pjesë shumë të vogël të trafikut, zakonisht nën një të
      qindtën, gjë që i bën metrikat e zakonshme si saktësia praktikisht të pakuptimta
      [@he2009], [@branco2016]. E dyta është vonesa e etiketave. Një transaksion
      konfirmohet si mashtrues vetëm pasi mbajtësi i kartës e kontestron ose pasi analisti
      e verifikon, dhe kjo zgjat ditë ose javë; në momentin kur duhet marrë vendimi,
      etiketa thjesht nuk ekziston [@dalpozzolo2018]. E treta është kufiri kohor: një
      vendim që mbërrin pas autorizimit nuk është vendim, është raport.""" ),
    p("""Këto tri kufizime shpjegojnë pse metodat e pambikëqyrura të zbulimit të anomalive
      janë tërheqëse në këtë fushë. Ato nuk kërkojnë etiketa gjatë trajnimit, ndërtojnë
      një model të asaj që është "normale" dhe sinjalizojnë atë që largohet prej tij
      [@chandola2009], [@aggarwal2017]. Në letërsi ato paraqiten shpesh si zgjidhje e
      natyrshme e problemit të etiketave. Pyetja që ky punim shtron është më e ashpër:
      sa mirë funksionojnë ato vërtet, kur vlerësohen nën kushtet kohore që do të hasnin
      në prodhim, dhe sa kushton mungesa e etiketave e shprehur në njësi të
      matshme.""" ),

    h2("1.2", "Deklarimi i shkurtër i problemit"),
    p("""Problemi që trajtohet në këtë punim është dizajnimi, implementimi dhe vlerësimi i
      ndershëm eksperimental i një sistemi për zbulimin e anomalive financiare mbi një
      rrjedhë të simuluar transaksionesh, duke integruar një platformë reale streaming me
      modele të Machine Learning-ut të pambikëqyrur. Fjala "i ndershëm" këtu nuk është
      dekorative. Një pjesë e mirë e rezultateve të publikuara mbi dataset-in e përdorur
      këtu janë prodhuar me ndarje të rastësishme të të dhënave, të cilat lejojnë që
      informacioni nga e ardhmja të ndikojë modelin e së kaluarës. Një nga gjetjet e
      këtij punimi është pikërisht sasia e fryrjes që kjo praktikë prodhon.""" ),
    p("""Fushëveprimi është i kufizuar me vetëdije. Sistemi është një prototip kërkimor në
      një mjedis të kontrolluar: të dhëna historike reale riprodhohen në rend kronologjik
      për të simuluar një rrjedhë. Ai nuk është një sistem prodhimi financiar dhe nuk
      pretendon të jetë. Kjo zgjedhje nuk e dobëson vlefshmërinë e matjeve statistikore,
      por e kufizon interpretimin e matjeve operacionale, dhe ky kufizim shënohet
      shprehimisht kudo ku raportohen numra vonese.""" ),

    h2("1.3", "Pyetjet hulumtuese"),
    p("""Punimi organizohet rreth tri pyetjeve hulumtuese, të cilat janë formuluar në
      projekt-propozimin e miratuar dhe janë ruajtur të pandryshuara gjatë gjithë
      implementimit:"""),
    numbers([
        "Si mund të implementohet një sistem për zbulimin e anomalive financiare në një "
        "mjedis të simuluar streaming, duke integruar Apache Kafka me modele të "
        "Unsupervised Machine Learning, dhe a mund të arrihet një latency mesatare nën "
        "1 sekondë?",
        "Cili nga algoritmet Isolation Forest, Autoencoder dhe One-Class SVM ofron "
        "balancën më të mirë ndërmjet performancës dhe efikasitetit operacional në "
        "krahasim me modelin baseline Logistic Regression?",
        "A përmirëson qasja ensemble performancën e zbulimit të anomalive krahasuar me "
        "përdorimin e modeleve individuale?",
    ]),
    p("""Të tria pyetjet marrin përgjigje të drejtpërdrejtë në Kapitullin 5 dhe
      diskutohen në Kapitullin 6. Për të dytën dhe të tretën, punimi shkon përtej
      formulimit fillestar: krahasimi zgjerohet nga tre algoritme në katërmbëdhjetë, dhe
      qasja ensemble testohet në pesë variante kombinimi me përzgjedhje automatike të
      anëtarëve. Zgjerimi nuk e zhvendos fokusin nga pyetja origjinale, por e vendos
      përgjigjen e saj në një kontekst ku ajo mund të interpretohet: pa e ditur ku
      qëndrojnë këto tre algoritme përballë familjeve të tjera, nuk dihet nëse dallimet
      mes tyre janë të mëdha apo të parëndësishme.""" ),

    h2("1.4", "Objektivat e punimit"),
    p("""Objektivat specifike, të renditura sipas rendit në të cilin realizohen:"""),
    numbers([
        "Rishikimi sistematik i literaturës mbi zbulimin e anomalive të pambikëqyrura, "
        "mbi zbulimin e mashtrimeve me karta dhe mbi arkitekturat streaming me Apache "
        "Kafka, me theks te metodologjia e vlerësimit dhe jo vetëm te algoritmet.",
        "Dizajnimi i një arkitekture pesështresore end-to-end, nga leximi i të dhënave "
        "deri te gjenerimi dhe persistimi i alarmeve.",
        "Ndërtimi i një protokolli vlerësimi pa rrjedhje informacioni, me ndarje "
        "kronologjike dhe me përsëritje në tetë pika kohore prerjeje.",
        "Implementimi dhe krahasimi i katërmbëdhjetë detektorëve të pambikëqyrur nga "
        "gjashtë familje algoritmike, kundrejt një reference të mbikëqyrur.",
        "Matja e kostos operacionale — vonesë, kapacitet përpunues, memorie dhe CPU — "
        "nën ritme të kontrolluara mbërritjeje.",
        "Hetimi eksperimental i qasjes ensemble dhe raportimi i rezultatit pavarësisht "
        "nga drejtimi i tij.",
        "Analiza e shkaqeve: zhvendosja e shpërndarjeve, interpretueshmëria e "
        "vendimeve dhe ndjeshmëria ndaj pragut.",
        "Persistimi i rezultateve në PostgreSQL dhe vizualizimi i tyre në një panel "
        "Grafana të konfiguruar plotësisht nga kodi.",
    ]),

    h2("1.5", "Kontributet"),
    p("""Punimi jep pesë kontribute që i konsideroj të veçanta, dy prej të cilave dolën
      gjatë punës dhe jo nga plani fillestar."""),
    bullets([
        "Një protokoll vlerësimi rolling-origin i zbatuar mbi një pipeline të vërtetë "
        "streaming, ku çdo fold rindërton nga fillimi skalimin, modelet dhe pragjet. "
        "Kjo lejon të matet nëse renditja e algoritmeve është artefakt i një prerjeje "
        "të vetme kohore — dhe përgjigjja rezulton e dyfishtë: renditja qëndron, "
        "ndërsa pasiguria e vlerësimeve është e njëjtë në madhësi me efektin.",
        "Kuantifikimi i kostos së ndershmërisë metodologjike: krahasimi i drejtpërdrejtë "
        "midis protokollit kronologjik dhe atij me ndarje të rastësishme, mbi të njëjtat "
        "të dhëna dhe të njëjtat modele.",
        "Një shpjegim mekanicist i renditjes së algoritmeve përmes analizës së "
        "atribuimit: shkalla në të cilën një model i kushton vëmendje veçorive që "
        "vërtet mbajnë sinjal parashikon cilësinë e tij të zbulimit.",
        "Dekompozimi i degradimit në zhvendosje kovariatësh kundrejt zhvendosjeje "
        "koncepti, me pasoja praktike të ndryshme: e para zgjidhet me ritrajnim, e dyta jo.",
        "Pragu adaptiv me dritare rrëshqitëse për shtresën e alarmeve, i cili stabilizon "
        "ngarkesën hetimore dhe njëkohësisht përmirëson cilësinë e zbulimit.",
    ]),

    h2("1.6", "Ajo që ky punim nuk e trajton"),
    p("""Përcaktimi i qartë i asaj që mbetet jashtë është po aq i rëndësishëm sa
      përcaktimi i asaj që përfshihet. Ky punim nuk trajton fortësimin për prodhim
      (disponueshmëri e lartë, autentikim, orkestrim me Kubernetes), nuk ndërton
      ritrajnim në kohë reale, nuk përdor teknika mbi-mostrimi si SMOTE [@chawla2002]
      sepse ato presupozojnë etiketa gjatë trajnimit, dhe nuk krahason platforma
      streaming mes tyre. Gjithashtu, punimi nuk pretendon të matë vonesë në kushte
      trafiku real: ritmi i mbërritjes është sintetik dhe i kontrolluar, dhe çdo pohim
      për vonesën shoqërohet me ritmin nën të cilin u mat.""" ),

    h2("1.7", "Struktura e punimit"),
    p("""Kapitulli 2 rishikon literaturën në katër drejtime: familjet e metodave të
      zbulimit të anomalive, puna specifike mbi zbulimin e mashtrimeve me karta,
      arkitekturat streaming, dhe — më e rëndësishmja për këtë punim — metodologjia e
      vlerësimit dhe boshllëqet e saj. Kapitulli 3 formulon problemin në mënyrë të
      saktë, duke përfshirë formalizimin matematik dhe hipotezat. Kapitulli 4 përshkruan
      metodologjinë: dataset-in, protokollin e ndarjes, modelet, procedurën e pragut,
      metrikat dhe arkitekturën e implementuar. Kapitulli 5 paraqet rezultatet, të
      organizuara sipas tri pyetjeve hulumtuese. Kapitulli 6 i diskuton ato, i vendos
      përballë literaturës, pranon kufizimet dhe propozon drejtime të mëtejshme.
      Shtojcat përmbajnë detajet e riprodhueshmërisë, hiperparametrat e plotë dhe
      tabelat shtesë.""" ),
]

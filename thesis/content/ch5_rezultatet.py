"""Kapitulli 5 — REZULTATET."""

from blocks import fig, h1, h2, h3, p, tab

_HYRJE = [
    h1("5", "Rezultatet"),
    p("""Rezultatet paraqiten sipas tri pyetjeve hulumtuese: vonesa e pipeline-it në nënkapitullin
      5.1, krahasimi i algoritmeve në 5.2 dhe ansamblet në 5.3. Tri nënkapitujt e fundit tregojnë sa
      varen këto përgjigje nga konfigurimi i algoritmeve (5.4), nga parametrat e secilit algoritëm
      (5.5) dhe nga mënyra si ndahen të dhënat dhe si trajnohen detektorët (5.6)."""),
    p("""Tabelat dhe figurat gjenerohen drejtpërdrejt nga rezultatet e ruajtura të eksperimenteve,
      dhe numrat në tekst janë marrë nga po këto tabela. Regresioni Logjistik shënohet kudo si
      referencë supervised. Ai ka përdorur etiketat historike, prandaj nuk konkurron me metodat
      unsupervised; tregon sa larg mund të shkohet kur këto etiketa ekzistojnë."""),
]

_PH1 = [
    h2("5.1", "PH1: realizueshmëria operacionale"),
    p("""Pyetja e parë hulumtuese ka dy pjesë: nëse një sistem i tillë mund të ndërtohet duke lidhur
      Apache Kafka-n me modele unsupervised, dhe nëse vonesa mesatare end-to-end mbetet nën një
      sekondë. Përgjigjen e pjesës së parë e jep vetë implementimi i përshkruar në Kapitullin 4;
      këtu jepet përgjigja e pjesës së dytë, me matje."""),
    p("""Për secilin nga katër modelet u riprodhuan 20 000 transaksione nëpër një broker real Kafka
      në modalitetin KRaft, me katër ritme mbërritjeje: 50, 200, 1000 dhe 2000 mesazhe në sekondë.
      Çdo kombinim u mat tri herë. Përsëritjet u bënë në tri kalime të plota, secili mbi të gjitha
      kombinimet, në mënyrë që një ndryshim i ngarkesës së host-it gjatë orëve të matjes të prekë
      njësoj të gjitha kombinimet dhe jo vetëm njërin. Vonesa end-to-end matet ashtu si përcaktohet
      në nënkapitullin 4.9.2, me orën e të njëjtit host, prandaj nuk përmban pasiguri sinkronizimi
      mes makinave."""),
    p("""Tabela [[tab:latency_summary]] jep për çdo kombinim mesataren e tri ekzekutimeve, dhe për
      vonesën mesatare edhe devijimin standard mes tyre. Inferenca jepet për mesazh: koha që i
      duhet modelit për të vlerësuar një mikro-grup, pjesëtuar me numrin e mesazheve në të. Kjo
      është e njëjta njësi si kostoja offline për transaksion (Tabela [[tab:benchmark_summary]]),
      por dy vlerat ndryshojnë për një arsye që shpjegohet më poshtë."""),
    tab(
        "latency_summary",
        "Vonesa end-to-end, koha e inferencës për mesazh dhe throughput-i për çdo model dhe ritëm "
        "(mesatare e tri ekzekutimeve; vonesa mesatare me devijimin standard mes tyre).",
        query="prag_adaptiv == False",
        columns=[
            "model",
            "rate_msg_s",
            "e2e_ms_mean_pm",
            "e2e_ms_p95",
            "e2e_ms_p99",
            "infer_us_mean",
            "throughput_msg_s",
        ],
        rename={
            "model": "Modeli",
            "rate_msg_s": "Ritmi (msg/s)",
            "e2e_ms_mean_pm": "Mesatarja (ms)",
            "e2e_ms_p95": "p95 (ms)",
            "e2e_ms_p99": "p99 (ms)",
            "infer_us_mean": "Inferenca (µs/mesazh)",
            "throughput_msg_s": "Throughput (msg/s)",
        },
        round={
            "e2e_ms_p95": 1,
            "e2e_ms_p99": 1,
            "infer_us_mean": 1,
            "throughput_msg_s": 0,
        },
    ),
    p("""Hipoteza H1 konfirmohet me diferencë të madhe. Në ritmet deri në 1000 mesazhe në sekondë,
      ato që mbulon hipoteza, vonesa mesatare end-to-end është 28.3 deri 57.6 milisekonda, 17 deri
      35 herë nën objektivin prej një sekonde (Figura [[fig:latency_vs_rate]]). Edhe percentili 99,
      matja e duhur për një kufizim operacional, nuk e kalon 116.2 milisekonda në mesataren e tri
      ekzekutimeve dhe 153.9 milisekonda në ekzekutimin më të keq."""),
    fig(
        "latency_vs_rate",
        "Vonesa end-to-end sipas modelit dhe ritmit të mbërritjes, kundrejt objektivit prej një "
        "sekonde (mesatare e tri ekzekutimeve).",
        15.0,
    ),
    p("""Matjet përsëriten mirë. Devijimi standard i vonesës mesatare mes tri ekzekutimeve është nën
      4 milisekonda në çdo kombinim deri në 1000 mesazhe në sekondë, pra më pak se 7% e vlerës.
      Bishti lëviz më shumë se mesatarja: për Isolation Forest-in në 1000 mesazhe në sekondë
      percentili 99 është 88.9, 105.8 dhe 153.9 milisekonda në tri ekzekutimet. Për bishtin e
      shpërndarjes një matje e vetme nuk do të mjaftonte."""),
    p("""Inferenca zë pjesë të vogël të vonesës për tre nga katër modelet. Të gjitha mesazhet e një
      mikro-grupi presin derisa të vlerësohet i gjithë grupi, prandaj pjesa e inferencës në vonesën
      e një mesazhi është koha e mikro-grupit dhe jo koha për mesazh. Për Autoencoder-in dhe
      referencën kjo kohë mbetet nën një milisekondë, nën 3.5% të vonesës. Për One-Class SVM-në ajo
      rritet me madhësinë e grupit, nga 1.0 në 6.5 milisekonda, sepse kostoja e saj është për çdo
      transaksion. Isolation Forest-i sillet ndryshe: një mikro-grup i kushton 19 deri 22
      milisekonda, si kur ka rreth katër mesazhe, ashtu edhe kur ka 64. Kostoja e tij është pra
      kryesisht fikse për çdo thirrje të modelit, sepse vlerësimi kalon pemë për pemë nëpër 200
      pemët e pyllit, sido që të jetë numri i transaksioneve. Kjo kosto zë rreth një të tretën e
      vonesës së tij dhe shpjegon pse vonesa e Isolation Forest-it, rreth 57 milisekonda, është
      afërsisht dyfishi i asaj të modeleve të tjera."""),
    p("""E njëjta kosto fikse shpjegon pse inferenca për mesazh në rrjedhë është më e lartë se
      kostoja offline. Offline modeli e vlerëson një bllok të tërë testimi me një thirrje, dhe
      kostoja fikse ndahet mbi dhjetëra mijëra transaksione; për Isolation Forest-in kjo jep 8.1
      mikrosekonda për transaksion. Në rrjedhë ajo ndahet mbi të shumtën 64 mesazhe, dhe në 1000
      mesazhe në sekondë jep 345 mikrosekonda për mesazh. Për të njëjtën arsye inferenca për mesazh
      bie kur ritmi rritet: mikro-grupet bëhen më të mëdha dhe kostoja fikse ndahet mbi më shumë
      mesazhe."""),
    p("""Mikro-grupet shpjegojnë edhe një vëzhgim që në pamje të parë duket i kundërt. Për
      Autoencoder-in, One-Class SVM-në dhe referencën vonesa është më e ulët në 2000 mesazhe në
      sekondë se në 1000; për Autoencoder-in ajo bie nga 31.1 në 19.0 milisekonda. Consumer-i e
      mbyll një mikro-grup kur ai mbush 64 mesazhe ose kur kalojnë 50 milisekonda. Për këto tre
      modele, deri në 1000 mesazhe në sekondë grupi mbyllet pothuajse gjithmonë nga kufiri kohor,
      dhe një mesazh pret mesatarisht rreth gjysmën e tij. Në 2000 mesazhe në sekondë 64 mesazhe
      mbërrijnë për rreth 32 milisekonda, grupi mbushet para kufirit dhe pritja shkurtohet. Në këto
      ritme vonesën e përcakton mënyra e mbledhjes së mesazheve dhe jo kapaciteti llogaritës."""),
    p("""Isolation Forest-i nuk e ndjek këtë rënie. Në 2000 mesazhe në sekondë vonesa e tij mesatare
      ndryshon shumë nga një ekzekutim në tjetrin, 31.7, 93.9 dhe 187.7 milisekonda, dhe në
      ekzekutimin më të ngadaltë vonesa në fund është rreth 340 milisekonda më e lartë se në
      fillim. Me 19 deri 22 milisekonda për çdo mikro-grup, consumer-i i tij punon këtu afër kufirit
      të vet, dhe çdo ngarkesë tjetër në host krijon radhë."""),
    p("""Deri në 1000 mesazhe në sekondë consumer-i nuk mbetet pas në asnjë ekzekutim: throughput-i,
      i matur siç përcaktohet në nënkapitullin 4.9.2, është të paktën 99.7% e ritmit të synuar. Në
      2000 mesazhe në sekondë Autoencoder-i, One-Class SVM-ja dhe referenca përpunojnë 1988 deri
      1993 mesazhe në sekondë, dhe Isolation Forest-i 1933 deri 1987."""),
    p("""Në këto ritme kufiri i consumer-it nuk arrihet për tre nga katër modelet, prandaj matja u
      zgjerua me ritmet 3000, 5000 dhe 10 000 mesazhe në sekondë. Çdo ekzekutim kishte 80 000
      mesazhe në vend të 20 000, që një radhë, nëse krijohet, të ketë kohë të shfaqet, dhe edhe këtu
      çdo kombinim u mat tri herë. Këto ritme janë teste kapaciteti jashtë hipotezës H1
      (nënkapitulli 3.5). Tabela [[tab:capacity_summary]] i përmbledh rezultatet."""),
    tab(
        "capacity_summary",
        "Testi i kapacitetit me 80 000 mesazhe për ekzekutim (mesatare e tri ekzekutimeve; vonesa "
        "mesatare me devijimin standard mes tyre).",
        columns=[
            "model",
            "rate_msg_s",
            "throughput_msg_s",
            "e2e_ms_mean_pm",
            "e2e_ms_p99",
        ],
        rename={
            "model": "Modeli",
            "rate_msg_s": "Ritmi (msg/s)",
            "throughput_msg_s": "Throughput (msg/s)",
            "e2e_ms_mean_pm": "Mesatarja (ms)",
            "e2e_ms_p99": "p99 (ms)",
        },
        round={
            "throughput_msg_s": 0,
            "e2e_ms_p99": 1,
        },
    ),
    p("""Isolation Forest-i arrin kufirin i pari. Në 3000 mesazhe në sekondë ai e mban ritmin pa
      krijuar radhë vetëm në një nga tri ekzekutimet, ndërsa në dy të tjerat vonesa mesatare arrin
      0.5 dhe 3.8 sekonda. Nga 5000 mesazhe në sekondë ai mbetet pas në çdo ekzekutim:
      throughput-i ndalet mes 3155 dhe 4820 mesazhesh në sekondë, dhe vonesa mesatare arrin 3.5
      sekonda në 5000 dhe 8.5 sekonda në 10 000 mesazhe në sekondë."""),
    p("""Tre modelet e tjera e mbajnë ritmin deri në 5000 mesazhe në sekondë. Throughput-i është të
      paktën 99.6% e ritmit të synuar në çdo ekzekutim, dhe vonesa mesatare 8 deri 46 milisekonda.
      Bishti është më pak i qëndrueshëm se në ritmet e ulëta: në disa ekzekutime një radhë e
      përkohshme e çon percentilin 99 deri në 372 milisekonda, para se consumer-i ta shkarkojë
      atë."""),
    p("""Në 10 000 mesazhe në sekondë arrihet kufiri i gjithë sistemit në këtë host. Producer-i, që
      e ndan procesorin me broker-in dhe consumer-in, nuk e arrin gjithmonë ritmin e synuar dhe në
      ekzekutimin më të dobët dërgon vetëm 8534 mesazhe në sekondë. Në pesë nga nëntë ekzekutimet e
      tre modeleve vonesa në fund të ekzekutimit është qartë më e lartë se në fillim, shenjë se po
      krijohet radhë, dhe vonesa mesatare lëviz nga 26 deri në 851 milisekonda sipas ekzekutimit.
      Për Autoencoder-in dhe referencën ky kufi nuk vjen nga modeli: inferenca e tyre kushton 5 deri
      7 mikrosekonda për mesazh, më pak se 10% të një bërthame në këtë ritëm. Ai vjen nga pjesa
      tjetër e punës për çdo mesazh, që bëhet në një proces të vetëm Python, dhe nga procesori i
      përbashkët. Për One-Class SVM-në vetë inferenca zë në këtë ritëm rreth dy të tretat e një
      bërthame."""),
    p("""Përmbledhtazi, në këtë host një consumer i vetëm e mban ritmin pa vështirësi deri në 5000
      mesazhe në sekondë me Autoencoder-in, One-Class SVM-në dhe referencën, ndërsa në 10 000
      arrihet kufiri i gjithë sistemit. Me Isolation Forest-in kufiri ndodhet rreth 2000 deri 3000
      mesazhe në sekondë. Vonesa mesatare e kalon një sekondë vetëm me Isolation Forest-in, nga 3000
      mesazhe në sekondë e lart. Këta kufij janë të gjithë sistemit në një makinë dhe jo vetëm të
      consumer-it (nënkapitulli 6.5.3), dhe nënkapitulli 6.2.6 diskuton si do të kapërceheshin."""),
    p("""Kostoja e burimeve është e moderuar në ritmet e hipotezës. Deri në 1000 mesazhe në sekondë
      consumer-i përdor mesatarisht 4% deri 60% të një bërthame, dhe vlerat më të larta i ka
      Isolation Forest-i. Memoria rezidente maksimale është 353 deri 360 MB dhe varet kryesisht nga
      interpretuesi Python dhe bibliotekat e ngarkuara, jo nga modelet. Ajo rritet deri në rreth
      440 MB vetëm kur consumer-i i Isolation Forest-it mbetet pas në testin e kapacitetit, me shumë
      gjasë sepse klienti Kafka mban në memorie mesazhet që presin."""),
    p("""U mat edhe kostoja e pragut adaptiv, i cili kërkon që consumer-i të mbajë një dritare
      rrëshqitëse pikësh dhe të rillogarisë periodikisht një kuantil. Në ritmin 200 mesazhe në
      sekondë, me 39 rifreskime gjatë 20 000 mesazheve, vonesa mesatare me prag adaptiv është 56.9
      milisekonda për Isolation Forest-in (57.6 me prag statik), 29.2 për Autoencoder-in (29.2) dhe
      30.3 për One-Class SVM-në (31.1). Dallimet janë nën një milisekondë dhe më të vogla se
      devijimi standard mes tri ekzekutimeve të së njëjtës matje, 0.5 deri 2.7 milisekonda; me prag
      adaptiv vonesa del madje pak më e ulët. Me tri ekzekutime një kosto prej një ose dy
      milisekondash nuk do të dallohej nga zhurma, por një kosto e tillë do të ishte e papërfillshme
      kundrejt objektivit prej një sekonde. Pragu adaptiv i nënkapitullit 5.2.4 nuk ka pra kosto
      operacionale të matshme."""),
    p("""Këto matje u bënë pa ruajtjen në PostgreSQL, që numrat të përshkruajnë vetë rrugën e
      zbulimit. Ruajtja dhe barazia me vlerësimin offline kontrollohen veçmas nga dy teste
      integrimi me broker-in real. I pari kontrollon që çdo event dhe çdo alarm i një ekzekutimi
      me ruajtje arrin në bazë dhe që pikët mbeten të pandryshuara gjatë rrugës. I dyti kontrollon
      që pikët e prodhuara në rrjedhë janë të njëjta me ato offline për të njëjtat transaksione,
      kështu që cilësia e matur offline në nënkapitujt në vijim vlen edhe për sistemin në punë.
      Kostoja e ruajtjes në vonesë nuk u mat (nënkapitulli 6.5.3)."""),
    p("""Kjo barazi lejon edhe një krahasim të drejtpërdrejtë me përpunimin batch. Offline modelet e
      vlerësojnë një bllok të tërë testimi me një thirrje, me 0.2 deri 55 mikrosekonda për
      transaksion (Tabela [[tab:benchmark_summary]]), pra shumë më shpejt për transaksion se në
      rrjedhë. Përpunimi batch e jep megjithatë vendimin vetëm pasi të jetë mbledhur grupi, ndërsa
      në rrjedhë çdo transaksion merr vendim mesatarisht 28 deri 58 milisekonda pas krijimit të tij,
      në ritmet deri në 1000 mesazhe në sekondë. Meqë pikët janë identike, rrjedha nuk humbet asgjë
      në cilësi kundrejt batch-it; kostoja e saj është koha e transportit dhe e mbledhjes së
      mikro-grupeve, e cila mbetet shumë nën objektiv."""),
]

_PH2 = [
    h2("5.2", "PH2: krahasimi i algoritmeve"),
    h3("5.2.1", "Rezultatet në konfigurimin bazë"),
    p("""Tabela [[tab:benchmark_summary]] paraqet tri algoritmet unsupervised dhe referencën
      supervised në
      protokollin rolling-origin 8-fold, me hiperparametrat bazë dhe me StandardScaler. Ky është
      konfigurimi bazë dhe jo ai më i miri i mundshëm; nënkapitulli 5.4 tregon sa ndryshon renditja
      kur ndryshon konfigurimi."""),
    tab(
        "benchmark_summary",
        "Rezultatet kryesore në konfigurimin bazë (mesatare 8-fold).",
        columns=[
            "model",
            "ap_mean",
            "ap_std",
            "avg_rank_ap",
            "roc_auc_mean",
            "f1_thr_mean",
            "recall_at_100",
            "score_us_per_tx",
            "fit_time_s",
        ],
        rename={
            "model": "Detektori",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "avg_rank_ap": "Rangu",
            "roc_auc_mean": "ROC-AUC",
            "f1_thr_mean": "F1",
            "recall_at_100": "R@100",
            "score_us_per_tx": "µs/tx",
            "fit_time_s": "Fit (s)",
        },
        round={
            "ap_mean": 3,
            "ap_std": 3,
            "avg_rank_ap": 2,
            "roc_auc_mean": 3,
            "f1_thr_mean": 3,
            "recall_at_100": 3,
            "score_us_per_tx": 2,
            "fit_time_s": 1,
        },
    ),
    p("""Në tabelë, rangu llogaritet mbi AP-në e çdo fold-i, R@100 është recall-i me 100 alarme për
      bllok, dhe kostoja e inferencës jepet në mikrosekonda për transaksion në regjimin offline.
      Rezultati i parë është hendeku me referencën: modeli supervised arrin AP 0.734 dhe është i
      pari në të tetë fold-et (rangu mesatar 1.00), ndërsa metoda më e mirë unsupervised arrin
      0.193. Raporti prej rreth 3.8 mes tyre tregon sa vlejnë etiketat historike në këtë
      problem."""),
    p("""Mes metodave unsupervised kryeson Autoencoder-i me 0.193, i ndjekur nga One-Class SVM me
      0.150 dhe Isolation Forest me 0.091 (Figura [[fig:benchmark_ap_ranking]]). Të tria vlerat janë
      rreth 50 deri 110 herë mbi nivelin e rastësisë, i cili është afërsisht 0.0017 (nënkapitulli
      3.3), por operacionalisht mbeten modeste."""),
    fig(
        "benchmark_ap_ranking",
        "AP e çdo detektori në tetë fold-et; rombi shënon mesataren.",
        15.0,
    ),
    p("""Krahasimi i AP-së me AUC-ROC është gjithashtu informues. Isolation Forest-i, me AP 0.091,
      ka AUC-ROC 0.941, praktikisht sa Autoencoder-i (0.943), i cili ka AP dy herë më të lartë. Nëse
      do të raportohej vetëm ROC, siç bën një pjesë e literaturës për këtë dataset, të tre
      detektorët do të dukeshin të barabartë. Ky është ilustrimi empirik i argumentit të Davis-it e
      Goadrich-it dhe të Saito-s e Rehmsmeier-it [@davis2006], [@saito2015]. Kurbat precision-recall
      dhe ROC të ndarjes 70/30 në Shtojcën D e tregojnë të njëjtën gjë grafikisht."""),
    p("""Shpërndarja nëpër fold-e ka po aq rëndësi sa mesatarja. Për çdo detektor unsupervised
      devijimi standard është i krahasueshëm me mesataren, dhe për Autoencoder-in madje e kalon atë.
      Performanca e një detektori varet shumë nga periudha kur vendoset (Figura
      [[fig:benchmark_ap_per_fold]])."""),
    fig(
        "benchmark_ap_per_fold",
        "AP e çdo detektori në çdo fold (shkallë logaritmike).",
        15.0,
    ),
    p("""Fold-i 1 dallohet qartë: në të AP rritet për të gjithë detektorët. Ai ka 88 mashtrime, të
      grumbulluara në një periudhë të shkurtër, gati katër herë më shumë se mesatarja prej 23 në
      blloqet e tjera. Një studim që do të testonte rastësisht mbi këtë periudhë do të raportonte
      rezultate shumë më të mira pa ndryshuar asgjë në metodë."""),
    p("""AP-ja rritet edhe mekanikisht me normën e mashtrimit në bllok, e cila në fold-in 1 është
      0.41%, kundrejt 0.06% deri 0.18% në blloqet e tjera, prandaj mesatarja mbi fold-et mbështetet
      fort te ky bllok. Për ta kontrolluar, renditja u llogarit edhe me dy përmbledhje që nuk varen
      prej tij. Mediana e AP-së është 0.104 për Autoencoder-in, 0.073 për One-Class SVM-në dhe 0.030
      për Isolation Forest-in, dhe mesatarja pa fold-in 1 është përkatësisht 0.112, 0.089 dhe 0.032.
      Renditja mbetet e njëjtë në të dyja, ndërsa vlerat absolute bien nga 41% deri 67%, gjë që
      tregon sa e ndjeshme ndaj periudhës është mesatarja e thjeshtë."""),
    h3("5.2.2", "Qëndrueshmëria statistikore e dallimeve"),
    p("""Dallimet mes detektorëve testohen me testin e Wilcoxon-it për çifte mbi AP-në e tetë
      fold-eve, me korrigjim Holm për krahasime të shumëfishta. Gjashtë krahasimet u fiksuan në kod
      para se të shihej ndonjë rezultat: Autoencoder-i kundrejt dy detektorëve të tjerë, One-Class
      SVM kundrejt Isolation Forest-it dhe referenca supervised kundrejt secilit detektor. Numri i
      tyre u kufizua nga fuqia statistike e tetë fold-eve. P-vlera më e vogël e mundshme është
      0.0078, dhe korrigjimi i Holm-it e shumëzon atë me numrin e krahasimeve: me gjashtë krahasime
      ajo bëhet 0.047 dhe mund ta kalojë pragun 0.05, ndërsa me shtatë do të bëhej 0.055 dhe asnjë
      krahasim nuk do të mund të ishte domethënës, sado i qëndrueshëm. Përveç p-vlerave, Tabela
      [[tab:significance_wilcoxon]] jep edhe madhësinë e efektit: diferencën mesatare të AP-së,
      fold-et e fituara nga secila palë dhe korrelacionin rank-biserial r, i cili shkon nga −1 kur
      detektori i dytë është më i mirë në çdo fold deri në +1 kur më i mirë është i pari."""),
    tab(
        "significance_wilcoxon",
        "Krahasimet dyshe të deklaruara paraprakisht (Wilcoxon, korrigjim Holm).",
        columns=[
            "krahasimi",
            "mean_diff",
            "fitore",
            "rank_biserial",
            "p_value",
            "p_holm",
            "significant_holm_05",
        ],
        rename={
            "krahasimi": "Krahasimi",
            "mean_diff": "Δ AP mesatar",
            "fitore": "Fitore A:B",
            "rank_biserial": "r",
            "p_value": "p",
            "p_holm": "p (Holm)",
            "significant_holm_05": "Domethënës",
        },
        round={"mean_diff": 4, "rank_biserial": 2, "p_value": 4, "p_holm": 4},
        widths=[6.2, 1.7, 1.4, 1.4, 1.3, 1.4, 1.6],
    ),
    p("""Pesë nga gjashtë krahasimet e kalojnë korrigjimin. Autoencoder-i e mund Isolation Forest-in
      në shtatë nga tetë fold-e, One-Class SVM e mund Isolation Forest-in në të tetë, dhe referenca
      supervised i mund të tre detektorët në të gjitha fold-et. I vetmi krahasim pa domethënie
      statistikore është Autoencoder kundrejt One-Class SVM: gjashtë fitore me dy, e qëndrueshme por
      jo e plotë. Renditja mes dy detektorëve të parë nuk është pra e vërtetuar statistikisht, dhe
      nënkapitulli 5.4 tregon se ajo përmbyset kur ndryshon paraprocesimi."""),
    p("""Hipoteza H2 konfirmohet, me një kufizim që duhet thënë qartë. Pjesa e parë e saj del pa
      dyshim: në çdo fold të tri metodat e kalojnë qartë nivelin e rastësisë, edhe në blloqet me
      vetëm 13 mashtrime, ku AP-ja më e ulët, 0.011, është rreth 17 herë mbi normën e mashtrimit të
      bllokut. Edhe renditja ka rregull: testi Friedman e hedh poshtë hipotezën se fold-et i
      renditin detektorët rastësisht (χ² = 9.75, p = 0.008), me përputhje të Kendall-it W = 0.61.
      Autoencoder-i është i pari në gjashtë nga tetë fold-et dhe Isolation Forest-i i fundit në
      shtatë. Kufizimi është se kjo rregullsi vlen për renditjen në tërësi dhe për konfigurimin
      bazë: dallimi mes dy detektorëve të parë nuk është i vërtetuar statistikisht, dhe nënkapitujt
      5.4 dhe 5.6 tregojnë se renditja ndryshon kur ndryshon paraprocesimi ose regjimi i
      trajnimit."""),
    h3("5.2.3", "Cilësia kundrejt kostos"),
    p("""Pyetja e dytë hulumtuese nuk kërkon detektorin më të saktë, por atë me balancën më të mirë
      mes performancës dhe efikasitetit operacional. Të dyja duhen parë bashkë (Figura
      [[fig:benchmark_quality_cost]])."""),
    fig(
        "benchmark_quality_cost",
        "Cilësia e zbulimit kundrejt kostos së inferencës (mesatare 8-fold).",
        15.0,
    ),
    p("""Në konfigurimin bazë përgjigja është e qartë. Autoencoder-i ka AP-në më të lartë mes
      metodave unsupervised dhe njëkohësisht koston më të ulët të inferencës, 0.22 mikrosekonda për
      transaksion. Isolation Forest-i kushton rreth 37 herë më shumë për transaksion (8.1
      mikrosekonda) dhe jep gjysmën e cilësisë, ndërsa One-Class SVM kushton rreth 250 herë më shumë
      (55.4 mikrosekonda), sepse çdo transaksion krahasohet me të gjithë vektorët mbështetës. Kjo
      kosto vjen nga konfigurimi: nënkapitulli 5.5.3 tregon se me një nën-mostër trajnimi më të
      vogël ajo bie nën gjashtë mikrosekonda pa humbje domethënëse cilësie."""),
    p("""Kostoja e trajnimit e rendit ndryshe: Autoencoder-i kërkon rreth 27 sekonda për fold,
      ndërsa Isolation Forest-i dhe One-Class SVM rreth një sekondë. Nëse modeli ritrajnohet një
      herë në ditë, ky dallim nuk ka rëndësi; do të kishte rëndësi vetëm me ritrajnim të
      vazhdueshëm. Edhe memoria shtesë gjatë trajnimit është e vogël për të gjithë modelet: në
      ndarjen 70/30 ajo shkon nga 48 MB për referencën supervised deri në 126 MB për One-Class
      SVM-në (Shtojca D)."""),
    h3("5.2.4", "Pragu dhe buxheti i alarmeve"),
    p("""AP-ja e vlerëson renditjen pa e lidhur me një prag. Në punë sistemi ka megjithatë nevojë
      për një prag, dhe protokolli kryesor e merr atë nga percentili (1 − c) i pikëve të trajnimit,
      me kontaminimin c të barabartë me normën e mashtrimit në dritaren e trajnimit (nënkapitulli
      4.5.1). Ndjeshmëria e rezultateve ndaj kësaj zgjedhjeje matet në ndarjen e vetme 70/30, me
      shtatë vlera të c nga 0.05% deri në 5% (Figura [[fig:contamination_sweep]]). Kjo ndarje jep të
      njëjtën renditje të detektorëve si protokolli 8-fold (nënkapitulli 5.6)."""),
    fig(
        "contamination_sweep",
        "Precision, recall dhe F1 në ndarjen 70/30 sipas kontaminimit nga i cili merret pragu.",
        15.0,
    ),
    p("""Për detektorët unsupervised ekziston një prag poshtë të cilit nuk kapet asnjë mashtrim. Me
      c deri në 0.1%, pra me 22 deri 88 alarme në një bllok testimi prej 85 443 transaksionesh,
      asnjë alarm nuk është mashtrim, sepse pikët më të larta u takojnë transaksioneve legjitime të
      pazakonta. Isolation Forest-i nuk kap asnjë mashtrim as me c = 0.2%. Precision-i i detektorëve
      unsupervised mbetet nën 0.18 në çdo vlerë të c, ndërsa recall-i arrin 0.81 deri 0.89 me c =
      5%, por me 4 500 deri 5 800 alarme."""),
    p("""F1 i Autoencoder-it dhe i One-Class SVM-së arrin kulmin me c = 0.5%, rreth 2.6 herë mbi
      normën e mashtrimit në trajnim, me 0.242 dhe 0.208; Isolation Forest-i arrin vetëm 0.075, me c
      = 1%. Referenca supervised arrin kulmin me c = 0.2%, vlera e provuar më e afërt me normën e
      mashtrimit, me F1 0.766. Për një model të kalibruar norma e mashtrimit është pra zgjedhja e
      duhur e pragut, ndërsa te metodat unsupervised optimumi ndodhet më lart, sepse mashtrimet nuk
      zënë majën e renditjes së tyre, por vijnë pak më poshtë."""),
    p("""Një ekip hetimesh, nga ana tjetër, nuk punon me një prag, por me një numër alarmesh që mund
      të shqyrtojë. Tabela [[tab:budget_summary]] tregon çfarë ndodh kur hetohen vetëm 100 alarmet
      me pikë më të
      lartë në çdo bllok testimi të protokollit 8-fold. Ky buxhet është realist, sepse një bllok ka
      mesatarisht 31 mashtrime."""),
    tab(
        "budget_summary",
        "Cilësia dhe vlera e kapur me 100 alarme për bllok testimi (mesatare 8-fold).",
        query="budget_k == 100",
        columns=["model", "precision_at_k", "recall_at_k", "amount_recall_at_k"],
        rename={
            "model": "Detektori",
            "precision_at_k": "Precision@100",
            "recall_at_k": "Recall@100",
            "amount_recall_at_k": "Vlera e kapur",
        },
        sort="recall_at_k",
        ascending=False,
        round={"precision_at_k": 3, "recall_at_k": 3, "amount_recall_at_k": 3},
    ),
    p("""Nga ky këndvështrim renditja ndryshon. One-Class SVM kalon para Autoencoder-it: kap 49.9%
      të mashtrimeve kundrejt 43.3%, dhe 45.2% të vlerës së tyre monetare kundrejt 38.4%. Ajo është
      më e mirë në krye të renditjes, edhe pse renditja e saj e plotë është më e dobët. Avantazhi
      megjithatë varet nga buxheti: me 50 alarme Autoencoder-i është përpara, dhe nga 250 alarme e
      lart të dy janë praktikisht të barabartë (Figura [[fig:budget_recall]]). Metrika duhet
      zgjedhur sipas mënyrës si do të përdoret sistemi."""),
    fig(
        "budget_recall",
        "Recall brenda buxhetit, për 50 deri në 1000 alarme për bllok.",
        15.0,
    ),
    p("""Dobësia e pragut statik, e përshkruar në nënkapitullin 4.5.3, shfaqet vetëm kur pikët vijnë
      sipas rendit kohor: kur shpërndarja e tyre zhvendoset, ekipi merr një ngarkesë të
      paparashikueshme pikërisht kur diçka ka ndryshuar. Pragu adaptiv e mban pragun te një kuantil
      i pikëve më të fundit, pa përdorur asnjë etiketë. Rezultatet më poshtë vijnë nga riprodhimi
      offline i blloqeve të testimit sipas rendit kohor, ashtu si përshkruhet në nënkapitullin
      4.5.3."""),
    p("""Qëllimi kryesor arrihet: koeficienti i variacionit të normës së alarmeve bie mesatarisht
      nga 0.84 në 0.62, kështu që ngarkesa e hetimeve bëhet më e parashikueshme (Figura
      [[fig:adaptive_tradeoff]]). Edhe F1 ndryshon, por kjo lidhet kryesisht me numrin e alarmeve
      dhe jo me përshtatjen në kohë. Për të tre detektorët unsupervised F1 rritet nga 0.124 në 0.166
      mesatarisht, ndërsa për referencën supervised bie nga 0.720 në 0.535."""),
    fig(
        "adaptive_tradeoff",
        "Paqëndrueshmëria e ngarkesës dhe F1 me pragun statik, me atë adaptiv dhe me një prag "
        "statik me po aq alarme, për çdo model.",
        15.0,
    ),
    p("""Mekanizmi lexohet te numri i alarmeve. Norma e synuar është rreth 0.20% e transaksioneve,
      sa norma e mashtrimit në dritaren e trajnimit. Me pragun statik, Autoencoder-i dhe Isolation
      Forest-i japin më pak alarme, 0.15% dhe 0.17%, ndërsa One-Class SVM afërsisht sa synohet;
      pragu adaptiv i çon të tre në rreth 0.25%, pra edhe pak mbi normën e synuar, me 54 deri 56
      alarme për bllok në vend të 33 deri 44. Recall-i rritet (te Autoencoder-i nga 0.158 në 0.312),
      ndërsa precision-i mbetet afërsisht i njëjtë."""),
    p("""Krahasimi me të njëjtin numër alarmesh e konfirmon këtë lexim. Një prag i vetëm statik që
      në të njëjtin bllok jep po aq alarme sa pragu adaptiv arrin F1 0.237 për Autoencoder-in,
      kundrejt 0.238 me pragun adaptiv, 0.090 për Isolation Forest-in, aq sa me pragun adaptiv, dhe
      0.192 për One-Class SVM-në, më shumë se 0.171 me pragun adaptiv. Rritja e F1 vjen pra nga
      numri më i madh i alarmeve dhe jo nga vendosja e tyre në kohë; vlera e vërtetë e pragut
      adaptiv është ngarkesa më e parashikueshme. Te referenca supervised alarmet rriten nga 31 në
      51 për bllok, por precision-i bie nga 0.756 në 0.443, sepse pragu statik i saj ishte tashmë i
      kalibruar mirë. Pragu adaptiv i shërben pra shtresës unsupervised si mjet për ta mbajtur
      ngarkesën të qëndrueshme, dhe jo si mënyrë për ta përmirësuar zbulimin."""),
]

_PH3 = [
    h2("5.3", "PH3: a ndihmon kombinimi i detektorëve"),
    p("""Pyetja e tretë hulumtuese testohet me pesë rregullat e kombinimit dhe me procedurën
      lakmitare të përshkruara në nënkapitullin 4.4.6, mbi pikët e tri detektorëve unsupervised.
      Tabela [[tab:ensemble_summary]] krahason çdo variant me anëtarin më të mirë: AP-në mesatare
      dhe devijimin e saj standard, diferencën nga anëtari më i mirë dhe numrin e fold-eve ku
      varianti e kalon atë."""),
    tab(
        "ensemble_summary",
        "Variantet e ansamblit kundrejt anëtarit më të mirë (mesatare 8-fold).",
        columns=[
            "varianti",
            "ap_mean",
            "ap_std",
            "vs_best_single",
            "fold_wins_vs_best_single",
            "n_folds",
        ],
        rename={
            "varianti": "Varianti",
            "ap_mean": "AP",
            "ap_std": "s.d.",
            "vs_best_single": "Δ ndaj më të mirit",
            "fold_wins_vs_best_single": "Fitore",
            "n_folds": "Fold-e",
        },
    ),
    p("""Rezultati është negativ. Asnjë variant nuk e kalon Autoencoder-in, i cili arrin 0.193
      (Figura [[fig:ensemble_vs_single]]). Rezultati më i mirë, 0.189, i takon procedurës lakmitare,
      por vetëm sepse në çdo fold me histori ajo zgjedh si anëtar të vetëm Autoencoder-in;
      diferencat e vogla nga Autoencoder-i vijnë nga barazimet që krijon normalizimi me rang. Vetë
      kërkimi arrin në përfundimin se asnjë kombinim nuk ndihmon. Votimi me shumicë është varianti
      më i dobët, me 0.090, më pak se gjysma e anëtarit më të mirë, gjë që pritet, sepse votimi e
      kthen çdo pikë në një vendim binar dhe humbet renditjen."""),
    fig(
        "ensemble_vs_single",
        "Diferenca e AP-së së çdo varianti të ansamblit nga Autoencoder-i, për çdo fold.",
        15.0,
    ),
    p("""Një rezultat negativ mund të vijë edhe nga akordimi i dobët, prandaj eksperimenti u
      përsërit me hiperparametrat e akorduar. Përfundimi nuk ndryshon: anëtari më i mirë arrin 0.335
      dhe ansambli më i mirë 0.334. Hipoteza H3 refuzohet në të dy regjimet e hiperparametrave."""),
    p("""Shkaku duket në të dhëna: detektorët nuk gabojnë në mënyra të pavarura. Korrelacioni i
      Spearman-it mes renditjeve të çdo çifti është 0.81 deri 0.91 dhe ndryshon pak nga një fold në
      tjetrin. Teoria e ansambleve e kërkon pavarësinë e gabimeve si kusht që mesatarizimi të
      ndihmojë, dhe këtu ky kusht nuk plotësohet."""),
    p("""Mbi të gjitha transaksionet ky korrelacion dominohet nga ato legjitime, ndërsa një ansambël
      vendoset te mashtrimet dhe në krye të renditjes, prandaj ai u mat edhe atje. Vetëm mbi
      mashtrimet korrelacioni mbetet i lartë, nga 0.80 deri 0.91. Alarmet e para përputhen më pak:
      100 alarmet e para të dy detektorëve kanë indeks Jaccard nga 0.37 deri 0.47. Mospërputhja
      mbetet megjithatë kryesisht te transaksionet legjitime, sepse vetëm 9 deri 18 nga 100 alarmet
      e para të çdo detektori janë mashtrime. Detektorët i renditin pra mashtrimet njësoj, dhe aty
      ku ndryshojnë, ndryshojnë kryesisht te alarmet e rreme."""),
    p("""E njëjta gjë duket në nivel transaksioni. Me buxhet prej 100 alarmesh për bllok, çdo
      mashtrim i tetë blloqeve të testimit u ndoq veçmas dhe u numërua sa detektorë e arrijnë. Nga
      251 mashtrime, 93 (37%) nuk i arrin asnjë detektor, ndërsa 66 (26%) i arrijnë të tre
      njëkohësisht. Vetëm 28 (11%) i arrin saktësisht një detektor (Figura [[fig:error_analysis]],
      majtas). Me shumicën e mashtrimeve në dy skajet, kombinimi nuk ka informacion plotësues për të
      shfrytëzuar."""),
    fig(
        "error_analysis",
        "Mbulimi i mashtrimeve nga tre detektorët me 100 alarme për bllok. Majtas: mashtrimet "
        "sipas numrit të detektorëve që i arrijnë. Djathtas: distanca nga qendra legjitime e "
        "mashtrimeve të arritura dhe të paarritura.",
        15.0,
    ),
    p("""Mashtrimet që nuk i arrin asnjë detektor kanë një tipar të përbashkët: ndodhen më afër
      popullatës legjitime, me distancë mediane 9.7 nga qendra e saj kundrejt 21.6 për ato që
      arrihen (Figura [[fig:error_analysis]], djathtas). Megjithatë referenca supervised, me të
      njëjtin buxhet, kap 59% të tyre. Informacioni që i dallon këto transaksione ekziston pra në të
      dhëna, por nuk ka formën që e sheh një detektor distancash; ndodhet në një drejtim
      diskriminues që e gjen vetëm mësimi supervised. Tabela [[tab:error_analysis_dark_set]] i
      krahason dy grupet e mashtrimeve sipas numrit, shumës mediane, distancës nga qendra legjitime
      dhe pjesës që kap referenca supervised."""),
    tab(
        "error_analysis_dark_set",
        "Mashtrimet e arritura nga të paktën një detektor dhe ato që nuk i arrin asnjë.",
        rename={
            "grupi": "Grupi",
            "n": "n",
            "shuma_mediane": "Shuma mediane",
            "norma_z_mediane": "‖z‖ mediane",
            "kapur_nga_LR": "Kapur nga referenca",
        },
        round={"shuma_mediane": 2, "norma_z_mediane": 1},
        fmt={"kapur_nga_LR": ".0%"},
    ),
    p("""Mashtrimet e paarritura nuk janë transaksione të vogla që humbasin në zhurmë: shuma e tyre
      mediane është 17.39 euro, kundrejt 9.36 euro për ato që kapen. Ato nuk janë as të
      parëndësishme financiarisht, as të dallueshme gjeometrikisht, dhe e përshkruajnë pjesën më të
      vështirë të problemit."""),
]

_KONFIGURIMI = [
    h2("5.4", "Sa varet renditja nga konfigurimi"),
    p("""Krahasimi i nënkapitullit 5.2 përdori StandardScaler dhe hiperparametrat bazë. Kjo është
      zgjedhje e paanshme, por lë pa përgjigje pyetjen nëse renditja do të ishte tjetër me çdo
      algoritëm në konfigurimin e tij më të mirë. Ky nënkapitull ndryshon veç e veç paraprocesimin
      dhe hiperparametrat, dhe pastaj të dyja bashkë."""),
    h3("5.4.1", "Paraprocesimi"),
    p("""Të tri metodat e përcaktojnë anomalinë përmes largësisë, dhe largësia varet plotësisht nga
      shkalla e veçorive. Për secilin detektor unsupervised, paraprocesimi më i mirë nga shtatë
      opsionet e nënkapitullit 4.3 e kalon StandardScaler-in në të tetë fold-et (p = 0.0078).
      One-Class SVM fiton 0.218 me transformimin kuantil uniform dhe arrin 0.368, rezultatin më të
      mirë unsupervised të gjithë studimit. Autoencoder-i fiton 0.103 me RobustScaler dhe arrin
      0.296, ndërsa Isolation Forest-i fiton 0.065 me transformimin kuantil uniform (Figura
      [[fig:scaling_effect]])."""),
    fig(
        "scaling_effect",
        "AP mesatare 8-fold e çdo detektori sipas paraprocesimit.",
        15.0,
    ),
    p("""Kur opsioni më i mirë zgjidhet dhe vlerësohet në të njëjtat fold-e, përfitimi mund të jetë
      i fryrë. Kontrolli prekuencial e shmang këtë: skaluesi për çdo fold zgjidhet vetëm nga fold-et
      paraardhëse. Përfitimi mbetet: 0.206 për One-Class SVM, 0.110 për Autoencoder-in dhe 0.045 për
      Isolation Forest-in, secili në shtatë nga shtatë fold-et (p = 0.016, vlera më e vogël e
      mundshme me shtatë fold-e)."""),
    p("""Krahasimi i drejtë është me paraprocesimin e konfigurimit bazë, StandardScaler, dhe jo me
      opsionin më të keq, i cili për One-Class SVM-në është mungesa e skalimit (AP 0.014), e
      papërshtatshme për një kernel RBF. Kundrejt StandardScaler, paraprocesimi më i mirë e rrit
      AP-në me 0.218 për One-Class SVM-në, me 0.103 për Autoencoder-in dhe me 0.065 për Isolation
      Forest-in, ndërsa diferenca mes tri detektorëve me StandardScaler është 0.102. Për One-Class
      SVM-në zgjedhja e paraprocesimit peshon pra më shumë se zgjedhja e algoritmit, për
      Autoencoder-in afërsisht njësoj, dhe për Isolation Forest-in më pak. Përfitimet prekuenciale
      ndjekin të njëjtin rend."""),
    p("""Referenca supervised sillet ndryshe. Asnjë paraprocesim nuk e përmirëson atë në mënyrë
      domethënëse (katër fitore nga tetë, p = 0.84), dhe zgjedhja prekuenciale e ul rezultatin e saj
      me 0.025. Regresioni logjistik mëson një drejtim diskriminues, dhe kur veçoritë shkallëzohen
      ndryshe ai thjesht i rregullon koeficientët. Për metodat gjeometrike, përkundrazi, ndryshimi i
      shkallës ndryshon vetë problemin që zgjidhin. Isolation Forest-i jep madje AP saktësisht të
      njëjtë me StandardScaler, RobustScaler, MinMaxScaler dhe pa skalim, sepse pikat e ndarjes
      zgjidhen uniformisht brenda intervalit të çdo kolone dhe një transformim linear i kolonës nuk
      i ndryshon pemët; rezultatin e tij e ndryshojnë vetëm transformimet jolineare, si ai
      kuantil."""),
    h3("5.4.2", "Hiperparametrat"),
    p("""Hiperparametrat u kërkuan me Optuna mbi ndarjen e brendshme kohore të nënkapitullit 4.7,
      dhe protokolli 8-fold u përsërit me konfigurimet e gjetura. Për të tre detektorët bashkë,
      konfigurimi i akorduar është më i mirë se ai bazë në të tetë fold-et (p = 0.0078), me një
      përfitim mesatar prej 0.071. Përfitimi shpërndahet megjithatë shumë pabarabartë. Autoencoder-i
      fiton 0.142, nga 0.193 në 0.335, me përmirësim në shtatë nga tetë fold-e. Isolation Forest-i
      fiton 0.076, nga 0.091 në 0.168, në të tetë fold-et. One-Class SVM humbet 0.005 dhe
      përmirësohet vetëm në dy fold-e, edhe pse në validimin e brendshëm akordimi i kishte dhënë
      0.076; një dritare e vetme validimi nuk garanton përmirësim në periudhat që vijnë."""),
    p("""Dritarja e kërkimit përmban blloqet e testimit të fold-eve 0 deri 3. Mbi fold-et 4 deri 7,
      që fillojnë pas saj, pamja është e njëjtë: Autoencoder-i fiton 0.173 dhe Isolation Forest-i
      0.070, të dy në katër nga katër fold-et, ndërsa One-Class SVM humbet 0.010. Përfitimet nuk
      vijnë pra nga mbivendosja mes kërkimit dhe testimit. Me hiperparametrat e akorduar renditja
      bëhet Autoencoder, Isolation Forest, One-Class SVM: i pari mbetet i njëjtë, por dy të fundit
      ndërrojnë vendet."""),
    p("""Konfigurimet që gjeti kërkimi përputhen me studimet e nënkapitullit 5.5, edhe pse të dyja
      procedurat janë të pavarura. Për Isolation Forest-in kërkimi zgjodhi nën-mostër 16 384 dhe
      pjesë kolonash 0.37, pikërisht dy parametrat që studimi i tij i gjeti vendimtarë. Për
      Autoencoder-in zgjodhi një rrjet me shtresë 64, dy shtresa enkoderi dhe dimension latent 20,
      në të njëjtin drejtim me gjetjen se arkitekturat më të gjera dhe më të thella janë më të
      mira."""),
    h3("5.4.3", "Paraprocesimi dhe hiperparametrat bashkë"),
    p("""Një dizajn faktorial 2×2 kombinon hiperparametrat bazë dhe të akorduar me StandardScaler
      dhe me paraprocesimin më të mirë për secilin detektor. Në qelizën e tij më të mirë, One-Class
      SVM arrin 0.368 me transformim kuantil dhe hiperparametra bazë, Autoencoder-i 0.335 me akordim
      dhe StandardScaler, dhe Isolation Forest-i 0.320 me të dyja ndërhyrjet bashkë (Figura
      [[fig:best_effort]]). One-Class SVM kalon në krye, ndërsa Isolation Forest-i mbetet i fundit,
      por vetëm 0.05 pas saj."""),
    fig(
        "best_effort",
        "AP mesatare 8-fold e çdo detektori në katër qelizat e dizajnit 2×2.",
        15.0,
    ),
    p("""Më e rëndësishme është sa ngushtohet diferenca. Me hiperparametrat bazë dhe StandardScaler,
      diferenca mes detektorit më të mirë dhe më të dobët është 0.102, me raport 2.1 herë. Kur
      secili vlerësohet në qelizën e tij më të mirë, ajo bie në 0.049, me raport vetëm 1.15 herë.
      Pjesa më e madhe e asaj që dukej si dallim mes algoritmeve është pra dallim në atë se sa mirë
      u përshtaten këtyre të dhënave vlerat bazë."""),
    p("""Dy ndërhyrjet nuk mblidhen. Për Autoencoder-in dhe One-Class SVM-në, kombinimi i të dyjave
      jep më pak se ndërhyrja e vetme më e mirë, sepse hiperparametrat e zgjedhur për hapësirën e
      vjetër nuk i përshtaten hapësirës që krijon paraprocesimi i ri. Isolation Forest-i bën
      përjashtim, sepse parametrat e tij kryesorë, madhësia e nën-mostrës dhe pjesa e kolonave, nuk
      varen nga shkalla e veçorive."""),
    p("""Këto vlera duhen lexuar si kufi i sipërm optimist. Paraprocesimi dhe hiperparametrat u
      zgjodhën nga studime që i kanë parë të njëjtat blloqe testimi, prandaj përmbajnë një
      përzgjedhje pas faktit. Vlerësimi i paanshëm mbetet ai i nënkapitullit 5.2; qëllimi këtu është
      të tregohet sa ndryshon renditja, jo të jepet një numër i ri për krahasim me literaturën."""),
]

_STUDIMET = [
    h2("5.5", "Studimet për secilin algoritëm"),
    p("""Studimet e nënkapitullit 4.8 ndryshojnë një parametër në një kohë dhe ekzekutohen në të
      tetë fold-et. Këtu jepen gjetjet kryesore për secilin algoritëm; vlerat për çdo konfigurim të
      provuar i ruan kodi në dosjen e rezultateve."""),
    h3("5.5.1", "Isolation Forest"),
    p("""Te Isolation Forest-i rezultatin e lëviz kryesisht madhësia e nën-mostrës. Konfigurimi
      bazë, me 200 pemë dhe nën-mostër 256, jep 0.091, ndërsa nën-mostra 16 384 me 800 pemë jep
      0.151, pra 66% më shumë; numri i pemëve e ndryshon rezultatin vetëm me 0.009. Vlera klasike
      256, që është edhe vlera e parazgjedhur e bibliotekës, rezulton e papërshtatshme për këtë
      dataset."""),
    p("""Edhe kur secili algoritëm merr konfigurimin e tij më të mirë (nënkapitulli 5.4.3),
      Isolation Forest-i mbetet i fundit, dhe shkaku duket te mënyra si zgjedh dimensionin e ndarjes
      (nënkapitulli 2.2.2). Numërimi i ndarjeve në pemët e trajnuara tregon se pesë veçoritë më
      informative marrin 17.4% të ndarjeve, ndërsa nga rastësia pritet 17.2%; korrelacioni i
      Spearman-it mes përdorimit të një kolone dhe fuqisë së saj diskriminuese është 0.10 (p =
      0.59). Algoritmi nuk i dallon kolonat e dobishme (Figura [[fig:iforest_capacity]], djathtas).
      Kur çdo pemë sheh më pak kolona, rezultati përmirësohet: me max_features 0.20 (rreth gjashtë
      kolona për pemë nga 29), AP rritet nga 0.091 në 0.113, me përmirësim në të tetë fold-et (p =
      0.0078; Figura [[fig:iforest_capacity]], majtas)."""),
    fig(
        "iforest_capacity",
        "Përdorimi i kolonave nga Isolation Forest-i. Majtas: ndryshimi i AP-së kur çdo pemë sheh "
        "vetëm një pjesë të kolonave. Djathtas: pjesa e ndarjeve kundrejt fuqisë diskriminuese të "
        "kolonës.",
        15.0,
    ),
    p("""Një shpjegim tjetër i mundshëm u përjashtua. Meqë V1 deri V28 janë komponentë kryesorë,
      ndarjet paralele me boshtet mund të ndihmohen ose të pengohen nga ky rreshtim. I njëjti pyll i
      trajnuar mbi një kopje të rrotulluar rastësisht të hapësirës, ku rreshtimi zhduket ndërsa
      distancat mbeten të njëjta, e ndryshon AP-në vetëm me 0.007."""),
    h3("5.5.2", "Autoencoder"),
    p("""Te Autoencoder-i arkitektura ka efektin më të madh. Kalimi nga konfigurimi bazë, me shtresë
      të fshehur 16 dhe dimension latent 8, te shtresa 32 me dimension latent 12 e rrit AP-në nga
      0.193 në 0.354, me 84%, dhe ky konfigurim është më i mirë në shtatë nga tetë fold-e (Figura
      [[fig:autoencoder_architecture]]). Diferenca mes arkitekturës më të mirë dhe më të dobët është
      0.223, më e madhe se diferenca prej 0.102 mes tri algoritmeve në konfigurimin bazë. Edhe
      thellësia ndihmon: me shtresë 32 dhe dimension latent 8, enkoderi me dy shtresa arrin 0.303
      kundrejt 0.222 me një shtresë."""),
    fig(
        "autoencoder_architecture",
        "AP mesatare 8-fold e Autoencoder-it sipas gjerësisë së shtresës së fshehur dhe "
        "dimensionit latent.",
        15.0,
    ),
    p("""Parametrat e tjerë kanë efekte më të vogla. Pika e anomalisë llogaritet gjithmonë si gabim
      kuadratik, ndërsa humbja e trajnimit ndryshon: gabimi kuadratik jep 0.193, gabimi absolut
      0.111 dhe humbja Huber 0.116. Humbjet robuste e dëmtojnë detektorin, sepse zbusin pikërisht
      gabimet e mëdha që mbartin sinjalin. Dropout dhe weight decay i vogël e rrisin rezultatin me
      më pak se 0.02, ndërsa weight decay 1e-2 e ul me 0.086. Varianti denoising nuk ka efekt
      praktik, dhe numri i epokave nuk jep efekt të qëndrueshëm, sepse rënia mesatare pas 20 epokash
      vjen kryesisht nga fold-i 1."""),
    p("""Jolineariteti ka vlerë. Një rindërtim linear me PCA me të njëjtin rang, niveli minimal i
      familjes së rindërtimit (nënkapitulli 2.3.3), mbetet nën Autoencoder-in në të shtatë rangjet e
      provuara, me diferencë 0.209 në rangun më të mirë të Autoencoder-it."""),
    h3("5.5.3", "One-Class SVM"),
    p("""Te One-Class SVM kerneli RBF është qartë më i miri, me 0.150, i ndjekur nga ai sigmoid me
      0.053 dhe ai polinomial me 0.032; kerneli linear dështon plotësisht me 0.001, në nivelin e
      rastësisë. Struktura e nevojshme është jolineare, njësoj si te Autoencoder-i. Në hapësirën
      nu–gamma vlerat e vogla të nu janë më të mira, me maksimum 0.163 për nu 0.001. Vlera 0.05 e
      konfigurimit bazë lejon që deri në 5% e transaksioneve normale të mbeten jashtë kufirit, rreth
      30 herë më shumë se norma e mashtrimit."""),
    p("""Rezultati më i rëndësishëm operacionalisht vjen nga kurba e të mësuarit. Rritja e
      nën-mostrës së trajnimit nga 1000 në 80 000 transaksione e rrit AP-në vetëm nga 0.151 në
      0.158, ndërsa koha e trajnimit rritet nga 0.006 në 50.6 sekonda dhe kostoja e inferencës nga
      5.2 në 188.2 mikrosekonda për transaksion (Figura [[fig:ocsvm_learning_curve]]). Kostoja ndjek
      numrin e vektorëve mbështetës, që rritet nga 102 në 4055."""),
    fig(
        "ocsvm_learning_curve",
        "Cilësia dhe kostoja e One-Class SVM-së sipas madhësisë së nën-mostrës së trajnimit.",
        15.0,
    ),
    p("""Pasoja praktike shkon kundër idesë se më shumë të dhëna janë gjithmonë më mirë, por me një
      kujdes. Me 1000 transaksione trajnimi AP-ja mesatare është 0.151, sa 0.150 me 20 000
      transaksionet e konfigurimit bazë, me kosto të inferencës nëntë herë më të ulët dhe kohë
      trajnimi rreth 160 herë më të shkurtër. Mesatarja e njëjtë fsheh megjithatë një dallim fold
      pas fold-i: me 1000 transaksione AP-ja është pak më e ulët në gjashtë nga tetë fold-et, me
      diferencë mediane 0.011, dhe barazia e mesatares vjen kryesisht nga fold-i 1. Dallimi nuk
      është statistikisht domethënës (Wilcoxon, p = 0.38), ndërsa devijimi standard nëpër fold-e
      është 0.215 me 1000 transaksione dhe 0.182 me 20 000. Përfundimi i saktë është pra se cilësia
      ndryshon pak me madhësinë e nën-mostrës, jo se ajo mbetet e njëjtë. Kostoja kuadratike e
      kernelit, që literatura e përmend si pengesën kryesore të metodës, këtu nuk është pengesë
      reale, sepse cilësia ngopet shumë më herët se kostoja."""),
]

_PROTOKOLLI = [
    h2("5.6", "Ndikimi i protokollit të ndarjes dhe të trajnimit"),
    p("""Tri zgjedhje protokolli u krahasuan mbi të njëjtat të dhëna dhe të njëjtat modele: ndarja e
      rastësishme kundrejt asaj kronologjike, prerja e vetme kundrejt protokollit 8-fold, dhe
      trajnimi mbi transaksionet normale të pastruara kundrejt trajnimit mbi gjithë dritaren. Dy të
      parat janë të përhapura në literaturë. Më shumë peshë ka ndarja e rastësishme: kur e njëjta
      ndarje 70/30 bëhet e rastësishme dhe e stratifikuar në vend të kronologjikes, AP e metodave
      unsupervised rritet mesatarisht 3.00 herë. Që numri të mos varet nga një shortim i vetëm,
      ndarja e rastësishme u përsërit me dhjetë seed-e. Fryrja mesatare e tri metodave lëviz nga
      2.47 deri 3.56 herë sipas ndarjes, dhe për asnjë detektor nuk bie nën 1.87 në asnjë ndarje
      (Tabela [[tab:protocol_inflation]])."""),
    tab(
        "protocol_inflation",
        "Fryrja e AP-së kur ndarja kronologjike zëvendësohet me ndarje të rastësishme (mesatare "
        "dhe shtrirja mbi dhjetë seed-e).",
        rename={
            "Detektori": "Detektori",
            "AP_kronologjik": "AP kronologjike",
            "AP_i_perzier": "AP e përzier",
            "fryrja": "Fryrja",
            "fryrja_min": "Min",
            "fryrja_max": "Maks",
        },
        round={"fryrja": 2, "fryrja_min": 2, "fryrja_max": 2},
    ),
    p("""Referenca supervised sillet përsëri ndryshe: për të ndarja e rastësishme sjell një rënie
      të lehtë, me raport mesatar 0.94, dhe raporti mbetet nën 1 në të dhjetë ndarjet, nga 0.86
      deri 0.97. Kjo sugjeron se fryrja nuk vjen nga vetë dataset-i ose metrika, por nga mënyra si
      metodat gjeometrike përfitojnë kur transaksione të së njëjtës periudhë ndodhen njëkohësisht në
      trajnim dhe në test; me një dataset të vetëm, ky shpjegim mbetet hipotezë e mbështetur dhe jo
      provë. Madhësia e efektit është shqetësuese: fryrja mesatare prej 3.00 herë është më e madhe
      se raporti prej 2.1 herë mes algoritmit më të mirë dhe më të dobët në protokollin korrekt, dhe
      Isolation Forest-i me ndarje të rastësishme arrin AP 0.129, afër Autoencoder-it me ndarje
      kronologjike (0.140)."""),
    p("""Zgjedhja e dytë është prerja e vetme kronologjike 70/30 kundrejt
      protokollit 8-fold. Renditja e detektorëve është e njëjtë në të dy rastet, kështu që prerja e
      vetme nuk e shtrembëron renditjen. Ajo që fsheh është pasiguria: për metodat unsupervised
      devijimi standard nëpër fold-e është mesatarisht 1.4 herë sa vetë mesatarja, dhe një numër i
      vetëm nuk e tregon fare këtë. Vlerat e prerjes së vetme jepen në Shtojcën D."""),
    p("""Zgjedhja e tretë është regjimi i trajnimit. Në protokollin kryesor detektorët trajnohen mbi
      transaksionet normale të dritares, të pastruara me etiketat historike, që në taksonominë e
      nënkapitullit 2.1.3 është regjimi semi-supervised. Një sistem pa asnjë etiketë do t'i
      trajnonte mbi gjithë dritaren, me rreth 0.2% mashtrime brenda saj. Protokolli 8-fold u
      përsërit në këtë regjim, me të njëjtin skalues, të njëjtat seed-e dhe të njëjtat blloqe
      testimi (Tabela [[tab:training_regime]]). AP nuk varet nga pragu, kështu që krahasimi nuk
      ndikohet nga norma e kontaminimit, e cila gjithashtu merret nga etiketat."""),
    tab(
        "training_regime",
        "AP mesatare 8-fold me trajnim mbi transaksionet normale të pastruara dhe mbi gjithë "
        "dritaren.",
        columns=[
            "Detektori",
            "AP_normalet",
            "AP_gjithe_dritarja",
            "delta",
            "fitore_gjithe_dritarja",
            "p_value",
        ],
        rename={
            "AP_normalet": "Normalet e pastruara",
            "AP_gjithe_dritarja": "Gjithë dritarja",
            "delta": "Δ AP",
            "fitore_gjithe_dritarja": "Fitore (gjithë dritarja)",
            "p_value": "p",
        },
        round={"AP_normalet": 3, "AP_gjithe_dritarja": 3, "delta": 3, "p_value": 3},
    ),
    p("""Rezultati i ndan detektorët qartë. Isolation Forest-i nuk ndikohet: AP-ja e tij lëviz nga
      0.091 në 0.097, pa dallim domethënës (p = 0.195). Autoencoder-i dhe One-Class SVM,
      përkundrazi, bien në të tetë fold-et, Autoencoder-i nga 0.193 në 0.047 dhe One-Class SVM nga
      0.150 në 0.111 (p = 0.008 për të dy). Renditja përmbyset: pa pastrim, One-Class SVM del i
      pari, Isolation Forest-i i dyti dhe Autoencoder-i i fundit; One-Class SVM është i pari dhe
      Autoencoder-i i fundit në shtatë nga tetë fold-et."""),
    p("""Shpjegimi më i mundshëm lidhet me mekanizmin e secilit algoritëm. Autoencoder-i mëson të
      rindërtojë atë që sheh; me disa qindra mashtrime në dritare ai mëson t'i rindërtojë edhe ato,
      dhe gabimi i tyre i rindërtimit, që është pika e anomalisë, bie. Edhe kufiri i One-Class
      SVM-së mësohet bashkë me mashtrimet e dritares. Isolation Forest-i, përkundrazi, e ndërton çdo
      pemë mbi një nën-mostër prej 256 transaksionesh. Me rreth 0.2% mashtrime, afërsisht gjashtë
      nga dhjetë pemë nuk shohin asnjë mashtrim, ndërsa të tjerat zakonisht shohin vetëm një.
      Nën-mostra e vogël e kufizon pra maskimin e përshkruar në nënkapitullin 2.2.2 [@liu2008], dhe
      pemët e tij ndryshojnë pak. Pasoja praktike është e
      rëndësishme. Rezultatet e konfigurimit bazë, dhe sidomos përparësia e Autoencoder-it, vlejnë
      për një sistem që i ka etiketat historike për ta pastruar dritaren e trajnimit; për një sistem
      pa asnjë etiketë, Isolation Forest-i dhe One-Class SVM janë zgjedhjet më të sigurta."""),
]

BLOCKS = _HYRJE + _PH1 + _PH2 + _PH3 + _KONFIGURIMI + _STUDIMET + _PROTOKOLLI

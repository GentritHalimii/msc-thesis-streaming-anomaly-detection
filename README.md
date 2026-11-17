# Zbulimi i anomalive në rrjedha të simuluara transaksionesh financiare

Implementimi teknik i punimit të diplomës së masterit *"Zbulimi i Anomalive në Rrjedha të
Simuluara të Transaksioneve Financiare duke përdorur Apache Kafka dhe Unsupervised Machine
Learning: Studim Rasti me Transaksione të Kartave të Kreditit"* (UBT, Shkenca Kompjuterike
dhe Inxhinieri).

Prototip kërkimor në mjedis të kontrolluar: të dhëna historike reale riprodhohen në rend
kronologjik për të simuluar një rrjedhë. Nuk është sistem prodhimi.

---

## Fushëveprimi

Studimi kufizohet te algoritmet që emërton projekt-propozimi dhe i studion ato në thellësi:

| Roli | Modeli |
|---|---|
| Detektorë primarë unsupervised | Isolation Forest, Autoencoder |
| Komponent shtesë unsupervised | One-Class SVM |
| Referencë supervised | Logistic Regression (kufi i sipërm, jo konkurrent) |

Thellësia vjen nga katër drejtime: protokolli rolling-origin me tetë fold-e, paraprocesimi dhe
hiperparametrat si variabla eksperimentale, studimi i parametrave kryesorë të secilit
algoritëm, dhe analiza e gabimeve në nivel transaksioni.

## Rezultatet kryesore

- **Vonesa (PH1).** Deri në 1000 msg/s vonesa mesatare end-to-end është 28–58 ms, 17–35 herë nën
  objektivin prej 1 s (12 konfigurime, mesatare e tri ekzekutimeve). p99 nuk e kalon 116 ms
  mesatarisht dhe 154 ms në ekzekutimin më të keq.
- **Kapaciteti.** Një consumer i vetëm e mban ritmin deri në 5000 msg/s me Autoencoder-in,
  One-Class SVM-në dhe referencën. Isolation Forest-i ngopet rreth 2000–3000 msg/s, sepse çdo
  thirrje e modelit kushton rreth 20 ms. Në 10 000 msg/s arrihet kufiri i gjithë makinës.
- **Krahasimi (PH2), konfigurimi bazë.** Autoencoder 0.193, One-Class SVM 0.150, Isolation
  Forest 0.091; referenca supervised 0.734. Renditja ka rregull nëpër fold-e (Kendall W = 0.61),
  por dallimi mes Autoencoder-it dhe One-Class SVM-së nuk është domethënës (Wilcoxon, Holm).
- **Regjimi i trajnimit.** Këto vlera vlejnë kur dritarja e trajnimit pastrohet me etiketat
  historike (regjimi semi-supervised). Me trajnim mbi gjithë dritaren, mashtrimet përfshirë,
  renditja përmbyset: One-Class SVM 0.111, Isolation Forest 0.097, Autoencoder 0.047.
- **Ansambli (PH3).** Rezultat negativ: varianti më i mirë arrin 0.189, nën Autoencoder-in
  (0.193). Detektorët gabojnë njësoj: me 100 alarme për bllok, 37% e mashtrimeve nuk i arrin
  asnjë prej tyre, ndërsa referenca supervised kap 59% të tyre.
- **Konfigurimi peshon sa algoritmi ose më shumë.** Transformimi kuantil e ngre One-Class SVM-në
  me +0.218 AP (në 0.368) në 8/8 fold-e, edhe kur skaluesi zgjidhet vetëm nga fold-et e
  mëparshme; akordimi e çon Autoencoder-in në 0.335 dhe Isolation Forest-in në 0.168. Me
  konfigurimin më të mirë për secilin, raporti mes më të mirit dhe më të dobëtit bie nga 2.1 në
  1.15.
- **Protokolli.** Ndarja e rastësishme e fryn AP-në unsupervised rreth 3.0 herë (2.5–3.6 mbi
  dhjetë seed-e; 4.1 herë për Isolation Forest); referencën supervised nuk e fryn (0.94).
- **Pragu.** Pragu adaptiv e ul paqëndrueshmërinë e ngarkesës (CV 0.84 → 0.62). F1 unsupervised
  rritet nga 0.124 në 0.166 vetëm sepse jep më shumë alarme: një prag statik me po aq alarme arrin
  të paktën të njëjtin F1.
- **Kostoja e One-Class SVM-së.** Me 1 000 mostra trajnimi AP-ja mesatare është sa me 20 000
  (0.151 kundrejt 0.150), me trajnim 160 herë dhe inferencë 9 herë më të shpejtë, por fold pas
  fold-i është pak më e ulët në 6 nga 8 (Wilcoxon p = 0.38).

---

## Si të ekzekutohet dhe si rigjenerohen rezultatet

Depoja përmban vetëm kodin. Dataset-i shkarkohet veçmas, ndërsa `results/` krijohet nga
komandat më poshtë: çdo hap shkruan aty tabelat, figurat dhe një manifest me commit-in,
konfigurimin dhe versionet e paketave. Hapat ekzekutohen sipas radhës, sepse secili lexon atë
që shkroi i mëparshmi.

**Kërkesat:** [uv](https://docs.astral.sh/uv/) dhe `make` (Python 3.12 e instalon vetë `uv`);
Docker me Compose për hapin 3; LibreOffice në `/snap/bin/libreoffice` për `make thesis`.

### 1. Mjedisi dhe të dhënat

```bash
make setup      # mjedisi me Python 3.12 dhe varësitë e fiksuara në uv.lock
make test       # testet njësi; ato që kërkojnë dataset-in ose rezultatet anashkalohen deri atëherë
```

Dataset-i Kaggle / ULB *Credit Card Fraud Detection* (284,807 transaksione, 492 mashtrime,
0.172%) nuk përfshihet në depo. Shkarkohet nga
<https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud> dhe vendoset në
`data/raw/creditcard.csv`.

### 2. Eksperimentet offline

```bash
make train                # modelet mbi ndarjen 70/30 → results/artifacts
make protocol             # protokolli rolling-origin me 8 fold-e; pikët → results/folds
make protocol-unfiltered  # detektorët e trajnuar mbi gjithë dritaren, mashtrimet përfshirë
make tune                 # kërkimi Optuna mbi një ndarje të brendshme kohore
make protocol-tuned       # protokolli me hiperparametrat e akorduar
make evaluate             # tabelat dhe figurat nga pikët e ruajtura, pa ritrajnuar (minuta)
make deep-studies         # studimet për secilin algoritëm; ritrajnojnë modelet (disa orë)
```

### 3. Rrjedha me Kafka

```bash
docker compose -f docker/docker-compose.yml up -d   # Kafka (KRaft), PostgreSQL, Grafana
make test-integration     # pikët në rrjedhë janë të njëjta me ato offline; kalimi nëpër PostgreSQL
make stream               # vonesa: 4 modele × 4 ritme (50–2000 msg/s) × 3 kalime, rreth 2 orë
make stream-adaptive      # kostoja e pragut adaptiv në 200 msg/s
make stream-capacity      # kapaciteti: 3000, 5000 dhe 10 000 msg/s me 80 000 mesazhe
make latency-report       # tabelat dhe figura e vonesës nga matjet
```

Kafka lidhet në portën **19092**, PostgreSQL në **15432** dhe Grafana në **3000**
(9092/5432 lihen të lira për stack-e të tjera lokale).

### 4. Punimi dhe paneli

```bash
uv run python -m experiments.make_rq_summary   # rifreskon tabelën e pyetjeve hulumtuese pas hapit 3
make thesis               # thesis/out/Punimi_Diplomes_GentritHalimi.docx nga results/
make webapp               # paneli i rezultateve në http://127.0.0.1:8800
```

- `make thesis` kërkon rezultatet e hapave 2 dhe 3. LibreOffice përdoret vetëm për numrat e
  faqeve në përmbajtje; pa të, `uv run python thesis/build_thesis.py --single-pass` e ndërton
  dokumentin pa ta, dhe Word-i i plotëson me Ctrl+A, F9.
- `make figures` i vizaton përsëri të gjitha figurat nga tabelat e ruajtura, pa ritrajnuar.
- Me të njëjtat seed-e metrikat e cilësisë dalin identike. Kohët (µs/tx dhe vonesa) maten nga e
  para në çdo ekzekutim, prandaj ndryshojnë pak.
- `make clean` i fshin rezultatet e gjeneruara.

---

## Paneli i rezultateve

Një aplikacion web lokal mbi të njëjtat rezultate (`make webapp`). Ai nuk ruan asnjë kopje të
tyre: çdo tabelë, figurë dhe verdikt lexohet nga `results/` në çastin kur kërkohet faqja,
prandaj paneli nuk mund të bjerë ndesh me studimin.

| Çfarë ofron | Pse |
|---|---|
| Nëntë faqe në rendin e punimit, me referencë te nënkapitulli përkatës | Për ta ndjekur të njëjtin argument më shpejt |
| Verdikti i çdo eksperimenti, i shkruar nga vetë kodi | Teksti që parafrazon punimi, i lexueshëm pa hapur dokumentin |
| Grafikë interaktivë krahas figurës origjinale të punimit | Eksplorim, pa humbur besnikërinë ndaj dokumentit |
| Konsolë ekzekutimi me log në kohë reale | Rigjenerimi i çdo hapi nga shfletuesi |
| Gjendja e Kafka-s, PostgreSQL-it dhe Grafana-s, me panelin e futur brenda faqes | Demonstrim i shtresës së rrjedhës pa hapur terminal |
| Modaliteti *Prezantim* | Mbrojtja e temës me projektor |

Konsola pranon vetëm identifikues nga katalogu i eksperimenteve, kurrë një rresht komande,
dhe i ekzekuton ato një nga një sepse eksperimentet konkurrojnë për çdo bërthamë të makinës.
Grafikët janë SVG të vizatuar nga kodi i vetë projektit, pa asnjë bibliotekë të jashtme, që
paneli të punojë edhe pa rrjet dhe ngjyrat e serive të jenë identike me ato të figurave.

---

## Metodologjia që një komision do ta shqyrtojë

**Ndarje kronologjike, pa përzierje.** Renditje e qëndrueshme sipas `Time`; asnjë rresht i
testimit nuk paraprin një rresht trajnimi.

**`Time` nuk është veçori hyrëse.** Ajo rendit rrjedhën dhe përcakton ndarjen. Po të ishte
veçori, në ndarje kronologjike çdo pikë testimi do të merrte një z-vlerë ekstreme në atë
dimension dhe do të prishte çdo detektor të bazuar në distancë. E verifikuar me test.

**Rolling-origin me 8 fold-e.** Numri nuk është i rrumbullakët: me N fold-e p-vlera më e vogël
e arritshme nga Wilcoxon-i është 2/2^N, pra N=6 jep 0.031 dhe nuk mbijeton Holm-in; me më
shumë fold-e disa blloqe bien nën 10 pozitivë. Me N=8 çdo bllok mban ≥13 pozitivë.

**Skaluesi dhe detektorët mësojnë nga të dhëna të ndryshme.** Skaluesi përshtatet mbi gjithë
dritaren e trajnimit, mashtrimet përfshirë, sepse një skalues i përshtatur mbi të dhëna të
pastra do t'i jepte modelit një avantazh që një sistem pa etiketa nuk e ka. Detektorët
trajnohen mbi transaksionet normale, të pastruara me etiketat historike (regjimi
semi-supervised); `make protocol-unfiltered` mat edhe regjimin pa këtë pastrim.

**Pragjet nuk e prekin kurrë testin.** Pragu parësor është percentili (1−c) i pikëve të
trajnimit. Pragu orakull raportohet vetëm si kufi i sipërm, në kolonë të veçantë.

**Metrika parësore është Average Precision.** Me 0.17% pozitivë, ROC-AUC mashton: një detektor
me AP 0.09 arrin këtu ROC-AUC 0.94.

**Vonesa matet nën ritëm sintetik.** Producer-i niset vetëm pasi consumer-i ka marrë caktimin e
particioneve; pa këtë sinkronizim bishti i shpërndarjes ndotet nga koha e nisjes.

## Struktura e depos

```
config/        një YAML: seed, ndarja, protokolli, hiperparametrat, Kafka, PostgreSQL
src/data/      lexim, ndarje kronologjike, shtatë opsione paraprocesimi
src/models/    iforest, autoencoder, ocsvm, logreg, pca (krahasim linear), ensemble
src/evaluation/protokolli, metrikat, distancat kNN, kostoja, validimi i brendshëm, statistikat, zhvendosja
src/streaming/ producer, consumer (prag statik ose adaptiv), serializimi
src/storage/   PostgreSQL
experiments/   një skript për eksperiment; asnjë logjikë modelimi
tests/         rrjedhja, protokolli, kontrata e modeleve, metrikat, stili i punimit, integrimi
docker/        Kafka (KRaft) + PostgreSQL + Grafana i provizionuar nga skedarë
thesis/        gjeneruesi i punimit .docx nga rezultatet
webapp/        paneli lokal i rezultateve (make webapp)
```

## Shënime mbi ndershmërinë e rezultateve

Vlerat e raportuara janë më të ulëta se shumica e punimeve mbi këtë dataset. Kjo është e
qëllimshme dhe e shpjeguar: `make evaluate` mat sa i fryn rezultatet ndarja e rastësishme
(`results/protocol_inflation.csv`). Rezultati negativ i ansamblit raportohet ashtu siç doli,
së bashku me shpjegimin e tij në nivel transaksioni.

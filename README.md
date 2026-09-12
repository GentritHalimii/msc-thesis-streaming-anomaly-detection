# Zbulimi i anomalive në rrjedha të simuluara transaksionesh financiare

Implementimi teknik i punimit të diplomës së masterit *"Zbulimi i Anomalive në Rrjedha të
Simuluara të Transaksioneve Financiare duke përdorur Apache Kafka dhe Unsupervised Machine
Learning: Studim Rasti me Transaksione të Kartave të Kreditit"* (UBT, Shkenca Kompjuterike
dhe Inxhinieri).

Prototip kërkimor në mjedis të kontrolluar: të dhëna historike reale riprodhohen në rend
kronologjik për të simuluar një rrjedhë. Nuk është sistem prodhimi.

---

## Fushëveprimi

Studimi kufizohet te algoritmet që emërton projekt-propozimi dhe blen **thellësi në vend të
gjerësisë**:

| Roli | Modeli |
|---|---|
| Detektorë primarë unsupervised | Isolation Forest, Autoencoder |
| Komponent shtesë unsupervised | One-Class SVM |
| Referencë e mbikëqyrur | Logistic Regression (kufi i sipërm, jo konkurrent) |
| Ablacion | PCA lineare (pragu i familjes së rindërtimit, jo detektor i pavarur) |

Thellësia vjen nga: karakterizimi gjeometrik i të dhënave para modelimit, protokolli
rolling-origin me tetë fold-e, paraprocesimi si variabël eksperimentale, sipërfaqja e plotë e
hiperparametrave dhe diagnostikat e mekanizmit për secilin algoritëm, test kauzal i
shpjegimit, politika e dritares së trajnimit, dhe analiza e gabimeve në nivel transaksioni.

## Rezultatet kryesore

- **Kufiri gjeometrik.** Mashtrimet janë 7.9× më larg klasës legjitime se një transaksion
  tipik legjitim, por vetëm distanca jep AP 0.30; bishti i klasës legjitime e mbush të
  njëjtin rajon. Mashtrimi median kërkon ~530 alarme.
- **Vonesa.** Mesatarja end-to-end nën 100 ms në të gjitha ritmet e testuara, rreth një rend
  madhësie nën objektivin prej 1 s. Ngopja rreth 2,400 msg/s me një consumer.
- **Cilësia (StandardScaler, hiperparametra të parazgjedhur).** LR 0.734; Autoencoder 0.193;
  One-Class SVM 0.151; Isolation Forest 0.091.
- **Akordimi e përmbys renditjen e dy të fundit.** Autoencoder 0.193 → 0.335, Isolation Forest
  0.091 → 0.168, One-Class SVM 0.151 → 0.146; udhëheqësi mbetet, dy të fundit ndërrohen.
- **Paraprocesimi ka ndikim më të madh se algoritmi.** Transformimi kuantil e ngre OCSVM-në me
  **+0.218 AP** (në 0.368, rezultati më i mirë unsupervised i studimit) në 8/8 fold-e;
  referencën e mbikëqyrur nuk e prek (p = 0.84).
- **Mekanizmi i Isolation Forest, i matur.** Pesë veçoritë më informative marrin 17.4% të
  ndarjeve kundrejt 17.2% të pritur nga rastësia (ρ = 0.10). Rrotullimi i hapësirës e ndryshon
  AP-në vetëm +0.007, pra shkaku nuk është përputhja e boshteve.
- **Analiza e gabimeve.** Në buxhet 100 alarmesh, 37% e mashtrimeve nuk arrihen nga asnjë
  detektor unsupervised; referenca e mbikëqyrur i kap 59% të tyre.
- **Ansambli.** Rezultat negativ nën të dy regjimet e hiperparametrave.
- **Protokolli.** Ndarja e rastësishme e fryn AP-në unsupervised ~3.0× (deri 4.5× për
  Isolation Forest); referencën e mbikëqyrur nuk e fryn fare (0.92×).
- **Zhvendosja.** PSI 3.22 për mashtrimet kundrejt 0.14 për normalet: ndryshojnë mashtrimet,
  jo modeli i normalitetit.
- **Pragu adaptiv.** Për të tre detektorët unsupervised F1 0.124 → 0.166 me CV të ngarkesës
  0.84 → 0.62; për referencën e mbikëqyrur e përkeqëson (0.720 → 0.535), sepse pragu i saj
  statik është tashmë i kalibruar.
- **Ndërhyrja kauzale.** Me vetëm 3 komponentët më informativë, Isolation Forest fiton +0.530 AP,
  më shumë se Autoencoder (+0.397) dhe One-Class SVM (+0.360); referenca humbet (−0.124).
- **Kostoja e One-Class SVM-së.** 1,000 mostra trajnimi japin të njëjtën cilësi si 20,000, me
  kohë trajnimi 160× më të vogël dhe kosto pikëzimi 9× më të vogël.

---

## Paneli i rezultateve

```bash
make webapp             # http://127.0.0.1:8800
```

Një aplikacion web lokal mbi të njëjtat rezultate. Ai nuk ruan asnjë kopje të tyre: çdo
tabelë, figurë dhe verdikt lexohet nga `results/` në çastin kur kërkohet faqja, prandaj
paneli nuk mund të bjerë ndesh me studimin.

| Çfarë ofron | Pse |
|---|---|
| Njëmbëdhjetë faqe në rendin e punimit, me referencë te nënkapitulli përkatës | Për ta ndjekur të njëjtin argument më shpejt |
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

## Dataset-i (nuk përfshihet në depo)

Kaggle / ULB *Credit Card Fraud Detection*: 284,807 transaksione, 492 mashtrime (0.172%).

1. Shkarko nga <https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud>
2. Vendose në `data/raw/creditcard.csv`

## Si të riprodhohet

```bash
make setup              # mjedis uv me Python 3.12 dhe lockfile të fiksuar
make test               # teste njësi: rrjedhja e informacionit, protokolli, metrikat, stili
make train              # përshtat modelet mbi ndarjen 70/30
make protocol           # 8 fold-e rolling-origin (hapi bazë, ~2 min)
make tune               # kërkim Optuna mbi ndarje të brendshme kohore
make protocol-tuned     # ri-ekzekuton protokollin me hiperparametrat e akorduar
make evaluate           # tabelat dhe figurat nga pikët e ruajtura (minuta)
make deep-studies       # studimet për algoritëm; ripërshtatin modelet (orë)
make thesis             # gjeneron punimin .docx nga results/
make webapp             # paneli interaktiv mbi results/

docker compose -f docker/docker-compose.yml up -d
make test-integration   # pariteti offline≈streaming + PostgreSQL
make stream             # skanimi i vonesës: modele × ritme
make stream-adaptive    # i njëjti skanim me prag adaptiv
make latency-report
```

Kafka lidhet në portën **19092**, PostgreSQL në **15432** dhe Grafana në **3000**
(9092/5432 lihen të lira për stack-e të tjera lokale).

---

## Metodologjia që një komision do ta shqyrtojë

**Ndarje kronologjike, pa përzierje.** Renditje e qëndrueshme sipas `Time`; asnjë rresht i
testimit nuk paraprin një rresht trajnimi. Modelet unsupervised shohin vetëm transaksione
normale të dritares së trajnimit.

**`Time` nuk është veçori hyrëse.** Ajo rendit rrjedhën dhe përcakton ndarjen. Po të ishte
veçori, në ndarje kronologjike çdo pikë testimi do të merrte një z-vlerë ekstreme në atë
dimension dhe do të prishte çdo detektor të bazuar në distancë. E verifikuar me test.

**Rolling-origin me 8 fold-e.** Numri nuk është i rrumbullakët: me N fold-e p-vlera më e vogël
e arritshme nga Wilcoxon-i është 2/2^N, pra N=6 jep 0.031 dhe nuk mbijeton Holm-in; me më
shumë fold-e disa blloqe bien nën 10 pozitivë. Me N=8 çdo bllok mban ≥13 pozitivë.

**Skaluesi përshtatet mbi dritaren e trajnimit me mashtrimet brenda.** Në momentin e vendosjes
etiketat nuk ekzistojnë, prandaj një skalues i përshtatur mbi të dhëna të pastra do të ishte
përparësi që sistemi real nuk e ka. Pasoja testohet, nuk supozohet.

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
src/models/    iforest, autoencoder, ocsvm, logreg, pca (ablacion), ensemble
src/evaluation/protokolli, metrikat, gjeometria, kostoja, EM/MV, statistikat, zhvendosja
src/streaming/ producer, consumer (prag statik ose adaptiv), serializimi
src/storage/   PostgreSQL
experiments/   një skript për eksperiment; asnjë logjikë modelimi
tests/         rrjedhja, protokolli, kontrata e modeleve, metrikat, stili i punimit, integrimi
docker/        Kafka (KRaft) + PostgreSQL + Grafana i provizionuar nga skedarë
thesis/        gjeneruesi i punimit .docx nga rezultatet
```

## Shënime mbi ndershmërinë e rezultateve

Vlerat e raportuara janë më të ulëta se shumica e punimeve mbi këtë dataset. Kjo është e
qëllimshme dhe e shpjeguar: `results/protocol_inflation.csv` mat sa i fryn rezultatet ndarja e
rastësishme, dhe `results/geometry_verdict.txt` tregon kufirin e sipërm të vetë problemit pa
asnjë model. Rezultati negativ i ansamblit raportohet ashtu siç doli, së bashku me shpjegimin
e tij në nivel transaksioni.

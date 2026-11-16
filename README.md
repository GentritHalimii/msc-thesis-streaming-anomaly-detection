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

- **Vonesa (PH1).** Mesatarja end-to-end 19–68 ms në 16 konfigurime (50 deri 2000 msg/s), 15–53
  herë nën objektivin prej 1 s; p99 maksimal 132 ms. Consumer-i nuk mbetet pas në asnjë
  konfigurim: në 2000 msg/s throughput-i është 1 984–1 999 msg/s.
- **Krahasimi (PH2), konfigurimi bazë.** Autoencoder 0.193, One-Class SVM 0.150, Isolation
  Forest 0.091; referenca supervised 0.734. Autoencoder-i ka edhe koston më të ulët të inferencës; dallimi i tij nga One-Class SVM nuk është domethënës (Wilcoxon, Holm).
- **Ansambli (PH3).** Rezultat negativ nën të dy regjimet e hiperparametrave. Detektorët gabojnë
  njësoj: me 100 alarme për bllok, 37% e mashtrimeve nuk i arrin asnjë prej tyre, ndërsa
  referenca supervised kap 59% të tyre.
- **Konfigurimi peshon më shumë se algoritmi.** Transformimi kuantil e ngre One-Class SVM-në me
  +0.218 AP (në 0.368) në 8/8 fold-e, edhe kur skaluesi zgjidhet vetëm nga fold-et e mëparshme;
  akordimi e çon Autoencoder-in në 0.335 dhe Isolation Forest-in në 0.168. Me konfigurimin më të
  mirë për secilin, raporti mes më të mirit dhe më të dobëtit bie nga 2.1 në 1.15.
- **Protokolli.** Ndarja e rastësishme e fryn AP-në unsupervised rreth 3.0 herë (4.5 herë për
  Isolation Forest); referencën supervised nuk e fryn (0.92).
- **Pragu.** Me prag sipas normës së mashtrimit detektorët unsupervised kapin pak; F1 arrin
  kulmin me kontaminim 0.5%. Pragu adaptiv e ul paqëndrueshmërinë e ngarkesës (CV 0.84 → 0.62)
  dhe rrit F1 unsupervised nga 0.124 në 0.166; referencës supervised ia ul F1-in.
- **Kostoja e One-Class SVM-së.** 1 000 mostra trajnimi japin të njëjtën cilësi si 20 000, me
  kohë trajnimi 160 herë dhe kosto të inferencës 9 herë më të vogël.

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
qëllimshme dhe e shpjeguar: `results/protocol_inflation.csv` mat sa i fryn rezultatet ndarja e
rastësishme. Rezultati negativ i ansamblit raportohet ashtu siç doli, së bashku me shpjegimin e
tij në nivel transaksioni.

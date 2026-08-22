# Zbulimi i anomalive në rrjedha të simuluara transaksionesh financiare

Implementimi teknik i punimit të diplomës së masterit *"Zbulimi i Anomalive në Rrjedha të
Simuluara të Transaksioneve Financiare duke përdorur Apache Kafka dhe Unsupervised Machine
Learning: Studim Rasti me Transaksione të Kartave të Kreditit"* (UBT, Shkenca Kompjuterike
dhe Inxhinieri).

Ky është një prototip kërkimor në një mjedis të kontrolluar: të dhëna historike reale
riprodhohen në rend kronologjik për të simuluar një rrjedhë. Nuk është një sistem prodhimi.

---

## Çfarë përmban

| Komponenti | Përshkrimi |
|---|---|
| **14 detektorë të pambikëqyrur** | gjashtë familje: izolim, kufi vendimi, afërsi, rindërtim, densitet, statistikore |
| **1 referencë e mbikëqyrur** | Regresion Logjistik, i etiketuar gjithmonë si kufi i sipërm, jo si konkurrent |
| **Protokoll rolling-origin** | 8 pika kohore prerjeje; çdo fold rindërton skalimin, modelet dhe pragjet nga fillimi |
| **Pipeline streaming** | Apache Kafka (KRaft) → pikëzim → topic `alerts` → PostgreSQL → Grafana |
| **Prag adaptiv** | kuantil me dritare rrëshqitëse, shkakësor, në konsumator |
| **Punimi** | dokument Word në shqip, i gjeneruar nga rezultatet (`make thesis`) |

## Rezultatet kryesore

- **Vonesa**: mesatarja fund-më-fund 28–85 ms në të gjitha ritmet e testuara, rreth një rend
  madhësie nën objektivin prej 1 s. Ngopja arrihet rreth **2,400 msg/s** me një konsumator.
- **Cilësia e zbulimit** (AP mbi 8 folds): referenca e mbikëqyrur 0.720; më i miri i
  pambikëqyrur Deep SVDD 0.449; Isolation Forest 0.091 (i 13-ti nga 14).
- **Ansambli**: rezultat negativ — asnjë nga 11 variantet nuk e tejkalon modelin më të mirë
  individual; shkaku është korrelacioni i lartë mes anëtarëve.
- **Protokolli**: ndarja e rastësishme e fryn AP-në e metodave të pambikëqyrura **2.74×**
  mesatarisht, ndërsa referencën e mbikëqyrur nuk e ndihmon.
- **Zhvendosja**: PSI 3.22 për popullatën e mashtrimeve kundrejt 0.14 për atë normale — nuk
  vjetërsohet modeli i normalitetit, ndryshojnë vetë mashtrimet.
- **Interpretueshmëria**: përputhja e vëmendjes së modelit me sinjalin realisht diskriminues
  (ρ = 0.75 / 0.50 / 0.02 për AE / OCSVM / IForest) parashikon renditjen e cilësisë.
- **Pragu adaptiv**: F1 mesatar 0.128 → 0.169, me ngarkesë hetimore dukshëm më të
  qëndrueshme.

---

## Dataset-i (nuk përfshihet në depo)

Kaggle / ULB *Credit Card Fraud Detection*: 284,807 transaksione, 492 mashtrime (0.172%).

1. Shkarko nga <https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud>
2. Vendose në `data/raw/creditcard.csv`

## Si të riprodhohet

```bash
make setup              # mjedis uv me Python 3.12 dhe lockfile të fiksuar
make test               # teste njësi: rrjedhja e informacionit, protokolli, metrikat
make train              # përshtat 15 modelet mbi ndarjen 70/30
make protocol           # 8 folds x 15 modele — hapi më i shtrenjtë (~30 min)
make tune               # kërkim Optuna mbi ndarje të brendshme kohore
make protocol-tuned     # ri-ekzekuton protokollin me hiperparametrat e akorduar
make evaluate           # të gjitha tabelat dhe figurat nga pikët e ruajtura
make thesis             # gjeneron punimin .docx nga results/

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
testimit nuk paraprin një rresht trajnimi. Modelet e pambikëqyrura shohin vetëm transaksione
normale të dritares së trajnimit.

**`Time` nuk është veçori hyrëse.** Ajo rendit rrjedhën dhe përcakton ndarjen. Po të ishte
veçori, në një ndarje kronologjike çdo pikë testimi do të merrte një z-vlerë ekstreme në atë
dimension dhe do të prishte çdo detektor të bazuar në distancë. E verifikuar me test.

**Rolling-origin me 8 folds.** Numri nuk është i rrumbullakët: me N folds p-vlera më e vogël
e arritshme nga Wilcoxon-i është 2/2^N, pra N=6 jep 0.031 dhe nuk mbijeton Holm-in; me më
shumë folds disa blloqe bien nën 10 pozitivë. Me N=8 çdo bllok mban ≥13 pozitivë dhe p-vlera
e arritshme është 0.0078.

**Pragjet nuk e prekin kurrë testin.** Pragu parësor është percentili (1−c) i pikëve të
trajnimit. Pragu orakull (best-F1 mbi test) raportohet vetëm si kufi i sipërm, gjithmonë në
kolonë të veçantë.

**Metrika parësore është AP.** Me 0.17% pozitivë, ROC-AUC mashton: në këto rezultate një
detektor me AP 0.09 arrin ROC-AUC 0.94.

**Referenca e mbikëqyrur nuk është konkurrent.** LR trajnohet me etiketat e dritares së
trajnimit dhe raportohet si kufi i sipërm nën disponueshmëri etiketash.

**Vonesa matet nën ritëm sintetik.** Prodhuesi niset vetëm pasi konsumatori ka marrë
caktimin e particioneve; pa këtë sinkronizim bishti i shpërndarjes ndotet nga koha e nisjes.

## Struktura e depos

```
config/        një YAML: seed, ndarja, protokolli, hiperparametrat, Kafka, PostgreSQL
src/data/      lexim, ndarje kronologjike, skalim i fituar vetëm mbi trajnimin
src/models/    një modul për familje, të gjithë pas fit/score/save/load
src/evaluation/protokolli, metrikat, kostoja, EM/MV, statistikat, zhvendosja, kombinimi
src/streaming/ prodhuesi, konsumatori (prag statik ose adaptiv), serializimi
src/storage/   PostgreSQL
experiments/   një skript për eksperiment; asnjë logjikë modelimi
tests/         rrjedhja, protokolli, kontrata e modeleve, metrikat, integrimi
docker/        Kafka (KRaft) + PostgreSQL + Grafana i provizionuar nga skedarë
thesis/        gjeneruesi i punimit .docx nga rezultatet
```

## Monitorimi me Grafana

`docker compose up -d` ngre edhe Grafana OSS me burimin e të dhënave dhe panelin të
provizionuar nga depo. Hape te <http://localhost:3000/d/sad-anomaly>. Të dhënat shfaqen pas
një ekzekutimi me `--store`.

## Shënime mbi ndershmërinë e rezultateve

Vlerat e raportuara janë më të ulëta se shumica e punimeve mbi këtë dataset. Kjo është e
qëllimshme dhe e shpjeguar: `results/protocol_inflation.csv` mat drejtpërdrejt sa i fryn
rezultatet ndarja e rastësishme. Rezultati negativ i ansamblit raportohet ashtu siç doli,
së bashku me shpjegimin e tij.

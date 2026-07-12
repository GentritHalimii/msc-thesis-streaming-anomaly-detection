# Streaming Anomaly Detection on Simulated Financial Transaction Streams

M.Sc. thesis prototype: anomaly detection on a simulated credit-card
transaction stream using Apache Kafka and unsupervised machine learning
(Isolation Forest, Autoencoder, One-Class SVM), against a supervised
Logistic Regression reference. Research code for a controlled experiment —
not a production fraud system.

## Dataset (not committed)

Kaggle / ULB "Credit Card Fraud Detection": 284,807 transactions, 492 frauds
(0.172%), columns `Time`, `V1..V28` (PCA-transformed), `Amount`, `Class`.

1. Download from <https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud>
2. Place the CSV at `data/raw/creditcard.csv`

## Quickstart

```bash
make setup                 # installs uv-managed venv (Python 3.12, pinned lockfile)
make test                  # unit tests (no docker needed)
make train                 # fit all models, save artifacts to results/artifacts/
make evaluate              # offline experiments 1,2,3,5 -> results/*.csv/.tex, figures/
uv run python -m experiments.exp4_ensemble        # experiment 4 (ensembles)

docker compose -f docker/docker-compose.yml up -d # Kafka (KRaft) + Postgres
make test-integration      # offline≈streaming parity + postgres round-trip
make stream                # latency sweep: models x {50,200,1000} msg/s
make latency-report        # aggregate -> results/latency_summary.*, figures
```

Kafka binds host port **19092** and Postgres **15432** (9092/5432 left free
for other local stacks).

## Methodology — the decisions an examiner will probe

**Chronological, leakage-free split.** Rows are sorted by `Time` (stable
sort) and split 70/30 *by time order* — never shuffled. With seed-fixed
config this yields 199,364 training transactions (384 frauds, 0.193%) and
85,443 test transactions (108 frauds, 0.126%). Unsupervised models train on
training-window **normals only**. The `StandardScaler` is fit on the
training window only; `tests/test_leakage.py` asserts its statistics equal
the train-window moments and are untouched by test data. `Time` itself is
not a model feature — it orders the stream and defines the split.

**The Logistic Regression baseline is a supervised *reference*, not a
peer.** LR is trained on the full training window *including its labels*
(the 384 frauds that naturally fall there). It answers "what would
label-supervised learning achieve on the same split?" — an upper bound under
label availability. Every table labels it as a reference; it is excluded
from the ensemble.

**Thresholds never touch the test set.** Primary protocol: each model's
alert threshold is the `(1 − contamination)` percentile of its
**training-score** distribution. `contamination` is a hyperparameter
(default: the fraud rate observed in the *training* window, 0.00193 — a
statistic using training labels only, the same availability assumption
already granted to the LR reference; experiment 2 sweeps it so no conclusion
depends on the default). Tables additionally report metrics at the **oracle
best-F1 threshold on test**, clearly labelled, as an upper bound only — the
two never share a column.

**Primary metric is Average Precision (PR-AUC).** At 0.126% test positives,
accuracy and ROC-AUC are misleading; ROC-AUC is still reported with that
caveat. F1/precision/recall are reported at both threshold protocols.

**One-Class SVM subsampling.** Exact kernel OCSVM is O(n²⁺) in training
size and infeasible on ~199k rows; it trains on a seeded random subsample
of 20,000 training-window normals (config `models.ocsvm.train_subsample`).

**Latency is measured under a synthetic arrival process.** The producer
replays the test window at a *constant configured rate* (50/200/1000 msg/s —
the dataset's real ~14 h test span is compressed accordingly), embedding a
wall-clock producer timestamp per message (single host; no clock skew).
The consumer logs, per message: **inference latency** (model forward pass
only) and **end-to-end latency** (producer timestamp → after alert
publish), reported as p50/p95/p99 + mean — never just the mean. Any
"sub-second" claim in the thesis is qualified with the replay rate used.

**Offline ≈ streaming reconciliation.** Both modes load the same saved
scaler and model artifacts and call the same `score()` code;
`tests/test_parity.py` replays test transactions through the dockerized
broker and asserts streaming scores match offline scores row-for-row.

## Architecture

```
CSV (chronological replay) -> Kafka `transactions` -> consumer:
    scale (train-fit scaler) -> model.score() -> threshold
        -> Kafka `alerts` + per-message latency CSV + Postgres
```

- **Offline evaluation mode** (no Kafka): deterministic batch scoring of the
  test window; source of all detection metrics. Fast to iterate.
- **Streaming mode** (Kafka replay): source of all operational metrics
  (latency distributions, throughput, CPU/RSS).

Kafka runs in KRaft mode (no ZooKeeper), single broker, via docker compose.
Apache Kafka rather than Redpanda because the thesis names Kafka; a
single-broker KRaft compose service costs little more. Messages are JSON:
debuggable, and Python floats round-trip exactly, which makes bit-exact
parity checks possible. PostgreSQL persists all scored events and alerts
(tables `scored_events`, `alerts`, keyed by `run_tag`).

Every model implements `fit / score / save / load` with **higher score =
more anomalous** (`src/models/base.py`), so the evaluation harness, the
ensemble, and the consumer stay generic.

## Experiments → artifacts (all under `results/`)

| # | Script | Artifacts |
|---|--------|-----------|
| 1 | `experiments/exp1_main_table.py` | `metrics_main.csv/.tex` — AP, ROC-AUC, P/R/F1 at percentile & oracle thresholds, fit time, memory, inference latency |
| 2 | `experiments/exp2_contamination_sweep.py` | `contamination_sweep.csv/.tex`, `figures/sweep_*.pdf/png` |
| 3 | `experiments/exp3_curves.py` | `figures/pr_curves.*`, `figures/roc_curves.*` |
| 4 | `experiments/exp4_ensemble.py` | `metrics_ensemble.csv/.tex`, `ensemble_verdict.txt`, `figures/pr_curves_with_ensembles.*` |
| 5 | `experiments/exp5_ae_ablation.py` | `ae_ablation.csv/.tex` |
| — | `experiments/run_streaming.py` + `latency_report.py` | `latency/latency_*.csv`, `latency_summary.csv/.tex`, `figures/latency_vs_rate.*` |

Ensembles (score-averaged and majority-vote over IF+AE+OCSVM, statistics
from training scores only): **negative result** — on this chronological
split neither variant beats the best single model (the autoencoder). See
`results/ensemble_verdict.txt`; the thesis reports this as a finding, not a
failure.

Every experiment writes `results/manifest_<run>.json` with git SHA, config
hash, package versions, timestamps, and hardware — every number in the
thesis is traceable to a manifest.

## Honest-results notes

- Detection quality on the chronological split is much lower than the
  shuffled-split numbers common in the literature for this dataset (train-
  window AP 0.17–0.49 vs test-window AP 0.03–0.14). The cause is measurable,
  not a vague "drift" (see `experiments/diag_window_shift.py` →
  `results/window_shift.csv`): the *fraud population* differs between
  windows while the normals barely move (median train-scaled ‖z‖ of normals
  4.16 → 4.25). Test-window frauds sit far closer to the normal manifold
  (fraud ‖z‖ median 14.5 vs 18.9; p90 18.9 vs **42.7**), and a model-free
  detector (score = ‖z‖) drops from AP 0.21 (train window) to 0.04 (test
  window) — the second day's frauds are intrinsically harder for ANY
  proximity/density method. `Time` is not an input feature (asserted in
  tests), so this is not a scaling artifact.
- The supervised LR reference (AP ≈ 0.77) dominates all unsupervised
  models, as expected when labels are available.

## Repo layout

```
config/            # single YAML: paths, seed, split, contamination, hyperparams
src/data/          # load, chronological split, train-only scaling
src/models/        # iforest, autoencoder, ocsvm, logreg (reference), ensemble
src/streaming/     # producer (rate-controlled replay), consumer, JSON serde
src/evaluation/    # metrics, thresholds, harness, report (CSV/LaTeX/figures)
src/storage/       # postgres sink
experiments/       # one runnable script per experiment
tests/             # leakage, split, model contracts, serde, parity, storage
docker/            # kafka (KRaft) + postgres compose
results/           # generated artifacts (gitignored)
```

## Tests

```bash
make test              # unit: split/leakage/model contracts/threshold math/serde
make test-integration  # parity (offline==streaming) + postgres round-trip
```

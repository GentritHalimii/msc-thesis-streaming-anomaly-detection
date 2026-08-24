# PLAN — Streaming Anomaly Detection with Kafka + Unsupervised ML

Implementation plan for the thesis prototype specified in `PROMPT.md`. Phases are ordered
so that every statistical result exists (offline) before any Kafka code runs, and each
phase ends with passing tests and a commit.

> **This file records the plan as written before implementation started, and is kept as
> that record.** The work went further than the plan in places and narrower in others: the
> detector set was later reduced to the three algorithms of the research proposal, and the
> single-split ensemble scripts were superseded by eight-fold versions. For the pipeline as
> it stands, see `README.md` and the `Makefile`.

## Phase 0 — Scaffolding

- `pyproject.toml` + pinned `requirements.txt` (uv-managed venv, Python pinned — see open
  decision D3), `ruff` config, `pytest` config, `Makefile` with targets:
  `setup`, `lint`, `test`, `train`, `evaluate`, `stream`, `all`, `clean`.
- `config/config.yaml`: data paths, seed, split ratio (0.70), contamination, model
  hyperparameters, Kafka settings (topics, bootstrap, replay rate), Postgres DSN.
  One config file, loaded once, passed around as a plain dataclass — no config framework.
- Repo layout as in the spec (no changes proposed):

```
config/  src/{data,models,streaming,evaluation,storage}/  experiments/  tests/  results/  docker/
```

**Deliverable:** `make lint test` passes on an empty-ish skeleton.

## Phase 1 — Data, chronological split, leakage tests

- `src/data/load.py`: read CSV, validate schema (Time, V1..V28, Amount, Class), sort by
  `Time` (stable sort, tie-safe).
- `src/data/split.py`: chronological 70/30 split **by time order, never shuffled**.
  Returns: `train_full` (both classes, for LR), `train_normal` (Class==0 only, for
  unsupervised fit), `test` (untouched, both classes). Logs fraud counts per window —
  the train-window fraud count is reported in the README and results (spec §2).
- `src/data/scale.py`: `StandardScaler` on `V1..V28` + `Amount` (`Time` is not a feature;
  it only orders the stream), **fit on the training window only**.
- Tests (`tests/test_split.py`, `tests/test_leakage.py`):
  - every train timestamp ≤ every test timestamp;
  - split is deterministic across runs;
  - scaler statistics computed from train rows only (assert scaler `mean_` equals the
    train-window mean, and changing test data doesn't change the scaler);
  - `train_normal` contains zero frauds; test window class counts match the raw CSV tail.

**Deliverable:** deterministic split artifacts + green leakage tests. Commit.

## Phase 2 — Offline models + evaluation (the statistical core)

- Common interface in `src/models/base.py`: `fit(X)`, `score(X) -> np.ndarray`
  (**higher = more anomalous**, uniform across models), `save(path)`, `load(path)`.
  Kept as a small ABC — no registry, no factory.
- Models (one module each):
  - `iforest.py` — sklearn `IsolationForest` (score = `-score_samples`).
  - `ocsvm.py` — One-Class SVM; exact kernel OCSVM is O(n²·⁺) and infeasible on ~199k
    training rows → open decision D1 (subsample vs. linear/Nyström approximation).
  - `autoencoder.py` — PyTorch (CPU) MLP autoencoder on the 29 scaled features,
    e.g. 29→16→8(latent)→16→29, MSE reconstruction error as anomaly score, fixed seeds,
    deterministic mode. PyTorch over Keras: torch is the lighter install for a small MLP
    and gives finer control of determinism.
  - `logreg.py` — supervised **reference**: trained on `train_full` **with labels**,
    `class_weight="balanced"`, score = `predict_proba[:,1]`. Framed everywhere (README,
    tables) as an upper-bound supervised reference, never as an unsupervised competitor.
- Thresholds (`src/evaluation/thresholds.py`):
  - **Primary:** `(1 − contamination)` percentile of the **training-score** distribution.
    Default contamination = fraud rate observed in the *training window* (uses train
    labels only — same label-availability assumption already granted to the LR reference;
    documented explicitly), swept in Experiment 2 so nothing hinges on the default.
  - **Oracle:** best-F1 threshold on test, always in a separate, clearly-labelled column.
- Metrics (`src/evaluation/metrics.py`): AP (primary), ROC-AUC, and F1/precision/recall
  at each of the two thresholds. Plus training time, inference time per batch, and peak
  memory per model.
- Experiments (`experiments/`, one script each, all writing CSV + booktabs LaTeX +
  300-dpi PDF/PNG into `results/`):
  1. `exp1_main_table.py` — main comparison table.
  2. `exp2_contamination_sweep.py` — contamination sweep → precision/recall trade-off plot.
  3. `exp3_curves.py` — overlaid PR curves and ROC curves.
  4. `exp5_ae_ablation.py` — latent dim × epochs grid (small: ~3×3), table + short plot.
     (Experiment 4, ensemble, lands in Phase 5 so it reuses the streaming-verified scorers.)
- Run manifest writer: every experiment writes `results/manifest_<run>.json` with git SHA,
  config hash, package versions, timestamps, hardware info.
- Tests: score-direction sanity (score of injected extreme point > median), save/load
  round-trip gives identical scores, metrics against hand-computed toy examples,
  determinism (two runs → identical metrics.csv).

**Deliverable:** full offline results for the four individual models. I report the actual
numbers, whatever they are. Commit.

## Phase 3 — Kafka streaming + latency

- `docker/docker-compose.yml`: **Apache Kafka in KRaft mode**, single broker, plus
  Postgres (used in Phase 4). Kafka rather than Redpanda: the thesis title and proposal
  name Apache Kafka; matching the named technology outweighs Redpanda's operational
  convenience, and single-broker KRaft is only a few lines of compose anyway.
- Topics: `transactions` (keyed by transaction index), `alerts`.
- Serialization: JSON (`src/streaming/serde.py`). At a few hundred msg/s, JSON overhead
  is irrelevant and debuggability wins; noted in README.
- `src/streaming/producer.py`: replays the **test window** in chronological order at a
  configurable synthetic rate (open decision D2), embedding `produced_at_ns`
  (`time.monotonic_ns`-based, single-host, so clock skew is a non-issue) and the true
  `Time` value.
- `src/streaming/consumer.py`: loads the **same saved model artifacts and the same
  scoring code** as offline mode, applies the saved scaler, scores each message, measures
  - **inference latency**: forward pass only,
  - **end-to-end latency**: `produced_at_ns` → alert published,
  publishes threshold-exceeding events to `alerts`, and appends per-message latency
  records to `results/latency_<run>.csv`. Micro-batching (poll up to N msgs, score as one
  matrix) with batch size in config — batch size 1 vs. small batches is itself a
  reportable operational trade-off.
- Latency report script: p50/p95/p99 + mean, per model; throughput; CPU/RSS sampled
  during the run; states the replay rate and the compression factor of the original
  ~2-day span. README wording: "sub-second under a synthetic arrival rate of X msg/s in
  a simulated replay" — never an unqualified "real-time" claim.
- **Parity test** (`tests/test_parity.py`): run producer+consumer over a fixed slice of
  the test window against a real broker (docker), assert streaming scores ≈ offline
  scores (`np.allclose`) row-for-row. Marked as an integration test
  (`pytest -m integration`) so unit tests stay docker-free.

**Deliverable:** latency distribution artifacts + parity test green. Commit.

## Phase 4 — PostgreSQL persistence

- Two tables: `scored_events` (all scored messages: id, event time, model, score,
  latencies) and `alerts` (threshold exceedances). Plain `psycopg` + explicit SQL,
  batched inserts (no ORM).
- Consumer gains a storage sink; a small test (integration-marked) asserts row counts
  and score round-trip fidelity.

**Deliverable:** a streaming run persists to Postgres. Commit.

## Phase 5 — Ensemble (Experiment 4)

- `src/models/ensemble.py`, same `fit/score/save/load` interface:
  - **Score-normalized averaging** — per-model scores rank-normalized (or z-normalized
    using *train-score* statistics — never test statistics) then averaged;
  - **Majority voting** — each model votes via its own train-percentile threshold.
- Members: the three unsupervised models only (IF + AE + OCSVM). LR stays outside — mixing
  the supervised reference into the ensemble would destroy the unsupervised framing.
- `experiments/exp4_ensemble.py`: both variants vs. best single model, offline and in one
  streaming run for latency. **If the ensemble loses, the table says so.**

**Deliverable:** ensemble results, honest sign either way. Commit.

## Phase 6 — README + reproducibility closure (+ optional Grafana)

- `make all`: setup → train → all offline experiments → (with docker up) streaming run →
  latency report. Every number in the thesis reproducible from one command + manifests.
- README: dataset acquisition (not committed), methodology notes the examiner will probe
  (chronological split, LR framing + train-window fraud count, threshold protocol,
  latency qualification), how to run everything.
- Grafana only if time remains and everything is stable: provisioned dashboard reading
  Postgres (alerts over time, latency percentiles). Explicitly droppable.

**Deliverable:** `make all` reproduces the thesis artifacts end-to-end. Final commit.

---

## Decisions I made myself (flagging, not asking)

- **Apache Kafka over Redpanda** — the thesis names Kafka; KRaft single-broker is cheap.
- **PyTorch over Keras** — lighter, better determinism control for a small CPU MLP.
- **JSON serialization** — debuggability over throughput at these rates.
- **`Time` excluded from features** — it orders the stream; using it as a feature would
  entangle the split variable with the model input.
- **Contamination default = train-window fraud rate** — uses training labels only, same
  assumption already granted to LR; swept in Experiment 2 regardless.
- **LR excluded from the ensemble** — keeps the ensemble purely unsupervised.
- **Postgres stores all scored events, not just alerts** — cheap at 85k rows and lets
  figures be regenerated from the DB.

## Open decisions — resolved with the author (2026-07-12)

- **D1 — OCSVM at scale → exact RBF OCSVM on a seeded ~20k subsample** of training
  normals. Faithful to the method named in the proposal; the subsampling is documented
  in README and results.
- **D2 — Replay rate → several fixed rates** (50 / 200 / 1000 msg/s) producing a
  latency-vs-throughput curve plus full latency distributions at each rate.
- **D3 — Python environment → install `uv`, pin Python 3.12** project-locally with a
  lockfile.

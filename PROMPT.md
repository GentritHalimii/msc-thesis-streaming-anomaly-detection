# Master's Thesis Implementation — Streaming Anomaly Detection with Kafka + Unsupervised ML

## Context

I'm implementing the technical part of my M.Sc. thesis (Computer Science & Engineering, Data Science and AI specialization). The academic proposal is approved; your job is the **engineering + experimental implementation**, not the writing.

**Thesis title:** Anomaly detection on simulated financial transaction streams using Apache Kafka and unsupervised machine learning — case study on credit card transactions.

**Dataset:** Kaggle / ULB `creditcardfraud` (284,807 transactions, 492 frauds = 0.172%, columns `Time`, `V1..V28` (PCA-transformed, uninterpretable), `Amount`, `Class`).

**What this is:** a research prototype in a controlled environment — historical data replayed chronologically to *simulate* a stream. It is **not** a production fraud system. Don't over-engineer toward production concerns (HA, auth, multi-tenancy, k8s). Correctness, reproducibility and honest measurement matter far more than infrastructure polish.

## Research questions the code must answer

1. Can a Kafka + unsupervised-ML pipeline detect anomalies on a simulated stream with **mean end-to-end latency under 1 second**?
2. Which of **Isolation Forest / Autoencoder / One-Class SVM** gives the best trade-off between detection quality and operational cost, compared to a **Logistic Regression** reference?
3. Does an **ensemble** improve over the individual models?

Every claim in my thesis must be traceable to an artifact your code produces (a CSV, a JSON, a figure). Nothing hand-waved.

## Two critical methodological decisions — handle these explicitly

These are the two things an examiner will attack. Implement them correctly and document them in the README.

**1. Leakage-free chronological split.**
- Sort by `Time`. First 70% by time = training window, last 30% = test window. Never shuffle, never `train_test_split` with random state.
- Unsupervised models train on **normal transactions only** (`Class == 0`) from the training window.
- `StandardScaler` (and any other transform) is **fit on the training window only**, then applied to test. Assert this in a test.
- Test window keeps both classes, untouched.

**2. The Logistic Regression baseline is a *supervised reference*, not a peer.**
The proposal says "training only on normals", but LR needs labels — this is a contradiction I want resolved in code, not hidden. Implement it as: LR trained on the **full training window including its labels** (the frauds that naturally fall in that window), explicitly framed in the README and in the results table as an *upper-bound supervised reference under label availability*, not an unsupervised competitor. Report how many frauds exist in the training window.

**3. Threshold selection must not touch the test set.**
- Primary protocol: derive each model's threshold from the **training-score distribution** (e.g. the `(1 - contamination)` percentile), where `contamination` is a hyperparameter, not something tuned on test labels.
- Additionally report, clearly labelled as such, the **oracle best-F1 threshold on test** — as an upper bound only. The two numbers must appear in separate columns and never be conflated.
- Primary metric is **Average Precision (PR-AUC)**, since accuracy and ROC-AUC are misleading at 0.172% positives. Report F1, precision, recall, ROC-AUC, AP.

## Architecture

Five layers, matching the proposal:

1. **Data source** — chronological CSV replay
2. **Kafka** — topics `transactions` and `alerts`
3. **Preprocessing** — deserialize, scale features
4. **Inference** — Isolation Forest, Autoencoder, One-Class SVM, LR reference, ensemble
5. **Output** — `alerts` topic, PostgreSQL persistence, optional Grafana

Run it as **two separable modes**, and keep them sharing the same model artifacts and the same scoring code:

- **Offline evaluation mode** — no Kafka. Batch scoring over the test window to produce all detection metrics, curves, and tables. This is where the statistical results come from. It must be fast enough to iterate on and fully deterministic.
- **Streaming mode** — the Kafka replay. This is where the **operational** results come from: end-to-end latency (p50/p95/p99, not just mean), throughput, memory, CPU. Detection metrics from streaming mode must reconcile with offline mode — write a test that asserts the scores match.

Separating these is important: if you couple them, a slow Kafka run blocks every experiment iteration.

## Latency measurement — be precise, examiners ask about this

Embed a producer timestamp in each message. In the consumer, measure and log separately:
- **inference latency** (model forward pass only)
- **end-to-end latency** (producer timestamp → alert published)

Report distributions, not just the mean. State the replay speed factor used (real 2-day data compressed to X) and be explicit that latency is measured under a synthetic arrival rate, since it's a simulation. Don't claim "sub-second real-time" without qualifying it.

## Stack

- Python, `uv` or venv, pinned `requirements.txt`
- Kafka in KRaft mode via `docker compose` (no ZooKeeper). Redpanda is acceptable if simpler — your call, justify it.
- scikit-learn (IForest, OCSVM, LR), PyTorch or Keras for the autoencoder — pick one, don't mix
- PostgreSQL for scored events + alerts
- Grafana **optional / last** — only if everything else is done and stable
- pytest, ruff, a `Makefile` or `justfile` with the standard targets

## Repo layout (adapt if you have a better idea, but tell me why)

```
config/            # YAML: paths, seeds, split ratios, contamination, model hyperparams
src/
  data/            # load, chronological split, scaling
  models/          # one module per model, common fit/score/save/load interface
  streaming/       # producer, consumer, serialization
  evaluation/      # metrics, curves, threshold analysis
  storage/         # postgres
experiments/       # runnable scripts, one per experiment
tests/             # leakage tests, chronological-order tests, offline≈streaming parity
results/           # generated: metrics.csv, figures/, run manifests
docker/
```

Every model implements the same interface (`fit`, `score` → higher = more anomalous, `save`, `load`) so the ensemble and the evaluation harness stay dumb.

## Experiments to produce

1. **Main comparison table** — all models × {AP, ROC-AUC, F1, precision, recall, latency, memory, training time}, at both the percentile threshold and the oracle threshold.
2. **Threshold / contamination sensitivity** — sweep contamination, plot precision–recall trade-off per model.
3. **PR and ROC curves** — all models overlaid on one figure each.
4. **Ensemble** — score-normalized averaging and majority voting; report whether it actually beats the best single model. **If it doesn't, say so in the results.** A negative result is a valid finding and I'd rather report it than fake an improvement.
5. **Ablation on the autoencoder** — latent dimension and epoch count, briefly.

Output every table as CSV **and** as LaTeX (`booktabs`), figures as 300-dpi PDF/PNG with readable fonts. I paste these directly into the thesis.

## Reproducibility

- One command reproduces everything: `make all` (or equivalent). Seeds fixed everywhere.
- Each run writes a manifest to `results/`: git SHA, config hash, package versions, timestamps, hardware.
- README documents exactly how to obtain the dataset (don't commit the CSV) and how to reproduce every number in the thesis.

## Non-goals — don't build these

Production hardening, authentication, k8s manifests, a custom web UI, real-time model retraining, or a deep-learning framework abstraction layer. If you find yourself writing a factory for a factory, stop.

## How I want you to work

1. **First, read this whole spec and write `PLAN.md`** — phased breakdown, and a short list of the decisions you're unsure about. Ask me before you start coding if anything is genuinely ambiguous. Don't ask about things you can reasonably decide yourself.
2. Then implement **phase by phase**, in this order: data + split + leakage tests → offline models + evaluation → Kafka streaming + latency → Postgres → ensemble → (optional) Grafana. Commit after each phase with a clear message.
3. After each phase, run the tests and tell me briefly what works and what the numbers look like. Don't dump full files at me; summarize.
4. **Be honest about results.** If Isolation Forest gets an AP of 0.15, report 0.15. If the autoencoder is beaten by the LR reference, that's the expected outcome given labels and it should be stated plainly. I will not accept metrics that were tuned into existence on the test set.
5. Keep the code clean and direct. No unnecessary abstraction layers, no premature generalization. Simple, readable, correct.

Start with `PLAN.md`.

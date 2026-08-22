UV ?= uv
RUN := $(UV) run

.PHONY: setup lint format test test-integration train protocol protocol-tuned \
        evaluate tune stream stream-store stream-adaptive latency-report \
        thesis all clean

setup:
	$(UV) sync

lint:
	$(RUN) ruff check src tests experiments thesis
	$(RUN) ruff format --check src tests experiments thesis

format:
	$(RUN) ruff check --fix src tests experiments thesis
	$(RUN) ruff format src tests experiments thesis

test:
	$(RUN) pytest

test-integration:
	$(RUN) pytest -m integration

# --- offline pipeline ------------------------------------------------------
train:                     ## fit every detector on the single 70/30 split
	$(RUN) python -m experiments.train_models

protocol:                  ## the expensive step: 8 rolling-origin folds x 15 detectors
	$(RUN) python -m experiments.run_protocol

tune:                      ## Optuna search on an inner temporal split of the training window
	$(RUN) python -m experiments.exp9_tuning

protocol-tuned:            ## re-run the protocol with the tuned hyperparameters
	$(RUN) python -m experiments.run_protocol --tuned
	$(RUN) python -m experiments.exp18_tuning_effect
	$(RUN) python -m experiments.exp12_ensembles --tuned

evaluate:                  ## every table and figure, from saved scores only
	$(RUN) python -m experiments.exp0_eda
	$(RUN) python -m experiments.make_diagrams
	$(RUN) python -m experiments.make_reference_tables
	$(RUN) python -m experiments.exp1_main_table
	$(RUN) python -m experiments.exp2_contamination_sweep
	$(RUN) python -m experiments.exp3_curves
	$(RUN) python -m experiments.exp5_ae_ablation
	$(RUN) python -m experiments.exp6_shuffled_split
	$(RUN) python -m experiments.exp10_benchmark
	$(RUN) python -m experiments.exp11_significance
	$(RUN) python -m experiments.exp12_ensembles
	$(RUN) python -m experiments.exp13_drift
	$(RUN) python -m experiments.exp14_alert_budget
	$(RUN) python -m experiments.exp15_explainability
	$(RUN) python -m experiments.exp16_adaptive_threshold
	$(RUN) python -m experiments.exp17_protocol_comparison
	$(RUN) python -m experiments.exp19_unsupervised_selection
	$(RUN) python -m experiments.make_rq_summary

# --- streaming pipeline (needs docker) -------------------------------------
stream:
	$(RUN) python -m experiments.run_streaming --models deep_svdd autoencoder iforest ocsvm lof logreg

stream-adaptive:
	$(RUN) python -m experiments.run_streaming --models deep_svdd autoencoder iforest --rates 200 --adaptive

stream-store:
	$(RUN) python -m experiments.run_streaming --store

latency-report:
	$(RUN) python -m experiments.latency_report

# --- thesis ----------------------------------------------------------------
thesis:                    ## build the Albanian thesis document from results/
	$(RUN) python thesis/build_thesis.py

all: setup test train protocol evaluate thesis

clean:
	rm -rf results/*.csv results/*.tex results/*.json results/*.txt \
	       results/figures results/artifacts results/folds results/tuned results/latency

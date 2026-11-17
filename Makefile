UV ?= uv
RUN := $(UV) run

.PHONY: setup lint format test test-integration train protocol protocol-tuned \
        protocol-unfiltered evaluate deep-studies figures tune stream stream-store \
        stream-adaptive stream-capacity latency-report webapp thesis all clean

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

protocol:                  ## the expensive step: 8 rolling-origin folds x 4 models
	$(RUN) python -m experiments.run_protocol

tune:                      ## Optuna search on an inner temporal split of the training window
	$(RUN) python -m experiments.exp9_tuning

protocol-unfiltered:       ## the detectors fitted on the whole window, frauds included
	$(RUN) python -m experiments.run_protocol --unfiltered
	$(RUN) python -m experiments.exp29_training_regime

protocol-tuned:            ## re-run the protocol with the tuned hyperparameters
	$(RUN) python -m experiments.run_protocol --tuned
	$(RUN) python -m experiments.exp18_tuning_effect
	$(RUN) python -m experiments.exp12_ensembles --tuned

evaluate:                  ## every table and figure that reads the saved fold scores
	$(RUN) python -m experiments.exp0_eda
	$(RUN) python -m experiments.make_diagrams
	$(RUN) python -m experiments.make_reference_tables
	$(RUN) python -m experiments.exp1_main_table
	$(RUN) python -m experiments.exp2_contamination_sweep
	$(RUN) python -m experiments.exp3_curves
	$(RUN) python -m experiments.exp6_shuffled_split
	$(RUN) python -m experiments.exp10_benchmark
	$(RUN) python -m experiments.exp11_significance
	$(RUN) python -m experiments.exp7_bootstrap_ci
	$(RUN) python -m experiments.exp12_ensembles
	$(RUN) python -m experiments.exp13_drift
	$(RUN) python -m experiments.exp14_alert_budget
	$(RUN) python -m experiments.exp16_adaptive_threshold
	$(RUN) python -m experiments.exp17_protocol_comparison
	$(RUN) python -m experiments.exp27_error_analysis
	$(RUN) python -m experiments.make_rq_summary

# The deep studies refit models from scratch and do not read results/folds,
# so they are independent of `protocol` and are kept out of `evaluate`: they
# cost hours, while `evaluate` costs minutes.
deep-studies:              ## per-algorithm studies; each one refits, hours not minutes
	$(RUN) python -m experiments.exp20_data_geometry
	$(RUN) python -m experiments.exp21_scaling
	$(RUN) python -m experiments.exp22_iforest_deep
	$(RUN) python -m experiments.exp23_autoencoder_deep
	$(RUN) python -m experiments.exp24_ocsvm_deep
	$(RUN) python -m experiments.exp28_best_effort

# Every thesis figure, redrawn from the tables the experiments saved or from
# the saved models. Nothing here refits a model, so a change of style costs a
# minute, not an afternoon.
figures:                   ## redraw all figures from saved results, no refitting
	$(RUN) python -m experiments.make_diagrams
	$(RUN) python -m experiments.exp0_eda
	$(RUN) python -m experiments.exp20_data_geometry --figures-only
	$(RUN) python -m experiments.exp2_contamination_sweep
	$(RUN) python -m experiments.exp3_curves
	$(RUN) python -m experiments.latency_report
	$(RUN) python -m experiments.exp10_benchmark
	$(RUN) python -m experiments.exp11_significance
	$(RUN) python -m experiments.exp14_alert_budget
	$(RUN) python -m experiments.exp12_ensembles
	$(RUN) python -m experiments.exp22_iforest_deep --figures-only
	$(RUN) python -m experiments.exp23_autoencoder_deep --from-saved
	$(RUN) python -m experiments.exp24_ocsvm_deep --from-saved
	$(RUN) python -m experiments.exp21_scaling --from-saved
	$(RUN) python -m experiments.exp28_best_effort --from-saved
	$(RUN) python -m experiments.exp18_tuning_effect
	$(RUN) python -m experiments.exp17_protocol_comparison
	$(RUN) python -m experiments.exp13_drift
	$(RUN) python -m experiments.exp16_adaptive_threshold
	$(RUN) python -m experiments.exp27_error_analysis

# --- streaming pipeline (needs docker) -------------------------------------
# Every configuration is measured three times, in interleaved passes, so the
# report can give the spread between runs and not only one run's numbers.
stream:
	$(RUN) python -m experiments.run_streaming --models iforest autoencoder ocsvm logreg \
	    --rates 50 200 1000 2000 --repeats 3 --out-subdir runs

stream-adaptive:
	$(RUN) python -m experiments.run_streaming --models iforest autoencoder ocsvm --rates 200 \
	    --adaptive --repeats 3 --out-subdir runs

# Rates past the operating range, with longer streams, to find where one
# consumer stops keeping pace.
stream-capacity:
	$(RUN) python -m experiments.run_streaming --models iforest autoencoder ocsvm logreg \
	    --rates 3000 5000 10000 --max-messages 80000 --repeats 3 --out-subdir capacity

stream-store:
	$(RUN) python -m experiments.run_streaming --store

latency-report:
	$(RUN) python -m experiments.latency_report

# --- results panel ---------------------------------------------------------
webapp:                    ## interactive panel over results/ at http://127.0.0.1:8800
	$(UV) run --group webapp python -m webapp

# --- thesis ----------------------------------------------------------------
thesis:                    ## build the Albanian thesis document from results/
	$(RUN) python thesis/build_thesis.py

all: setup test train protocol protocol-unfiltered evaluate deep-studies thesis

clean:
	rm -rf results/*.csv results/*.tex results/*.json results/*.txt \
	       results/figures results/artifacts results/folds results/tuned results/latency

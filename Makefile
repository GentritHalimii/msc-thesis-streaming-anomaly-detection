UV ?= uv
RUN := $(UV) run

.PHONY: setup lint test test-integration train evaluate stream latency-report all clean

setup:
	$(UV) sync

lint:
	$(RUN) ruff check src tests experiments
	$(RUN) ruff format --check src tests experiments

format:
	$(RUN) ruff check --fix src tests experiments
	$(RUN) ruff format src tests experiments

test:
	$(RUN) pytest

test-integration:
	$(RUN) pytest -m integration

train:
	$(RUN) python -m experiments.train_models

evaluate:
	$(RUN) python -m experiments.exp1_main_table
	$(RUN) python -m experiments.exp2_contamination_sweep
	$(RUN) python -m experiments.exp3_curves
	$(RUN) python -m experiments.exp4_ensemble
	$(RUN) python -m experiments.exp5_ae_ablation

stream:
	$(RUN) python -m experiments.run_streaming

stream-store:
	$(RUN) python -m experiments.run_streaming --store

latency-report:
	$(RUN) python -m experiments.latency_report

all: setup test train evaluate

clean:
	rm -rf results/*.csv results/*.json results/figures results/artifacts results/latency*

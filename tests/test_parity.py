"""Offline/streaming reconciliation: the consumer must produce the SAME
scores as offline batch evaluation for the same transactions.

Integration test — needs the dockerized broker:
    docker compose -f docker/docker-compose.yml up -d
    uv run pytest -m integration
"""

import subprocess
import sys
import uuid

import numpy as np
import pandas as pd
import pytest

from src.config import REPO_ROOT, load_config
from src.data.scale import load_scaler, transform
from src.models.build import artifacts_dir, load_model

N_MESSAGES = 500
MODEL = "iforest"


@pytest.mark.integration
def test_streaming_scores_match_offline(tmp_path, split):
    cfg = load_config()
    if not (artifacts_dir(cfg) / "scaler.joblib").exists():
        pytest.skip("artifacts missing; run experiments.train_models first")

    run_id = uuid.uuid4().hex[:8]
    tx_topic = f"parity-tx-{run_id}"
    alert_topic = f"parity-alerts-{run_id}"
    run_tag = f"parity_{run_id}_rate0"

    consumer = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "src.streaming.consumer",
            "--model",
            MODEL,
            "--run-tag",
            run_tag,
            "--tx-topic",
            tx_topic,
            "--alert-topic",
            alert_topic,
        ],
        cwd=REPO_ROOT,
    )
    producer = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.streaming.producer",
            "--rate",
            "2000",
            "--max-messages",
            str(N_MESSAGES),
            "--tx-topic",
            tx_topic,
        ],
        cwd=REPO_ROOT,
        timeout=120,
    )
    assert producer.returncode == 0
    assert consumer.wait(timeout=120) == 0

    lat_csv = REPO_ROOT / cfg.results_dir / "latency" / f"latency_{run_tag}.csv"
    streamed = pd.read_csv(lat_csv).set_index("tx_id").sort_index()
    assert len(streamed) == N_MESSAGES

    test_head = split.test.iloc[:N_MESSAGES]
    scaler = load_scaler(artifacts_dir(cfg) / "scaler.joblib")
    offline_scores = load_model(MODEL, cfg).score(transform(scaler, test_head))

    np.testing.assert_allclose(
        streamed.loc[test_head.index, "score"].to_numpy(),
        offline_scores,
        rtol=1e-9,
        err_msg="streaming and offline scores diverge — shared-code-path invariant broken",
    )
    # labels carried through the stream must match the raw data too
    np.testing.assert_array_equal(
        streamed.loc[test_head.index, "label"].to_numpy(), test_head["Class"].to_numpy()
    )

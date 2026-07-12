"""Postgres persistence: a streaming run with --store lands every scored
event and alert, with scores surviving the round-trip exactly.

Integration test — needs docker compose (kafka + postgres) up.
"""

import subprocess
import sys
import uuid

import numpy as np
import pandas as pd
import psycopg
import pytest

from src.config import REPO_ROOT, load_config
from src.models.build import artifacts_dir

N_MESSAGES = 300
MODEL = "iforest"


@pytest.mark.integration
def test_streaming_run_persists_to_postgres():
    cfg = load_config()
    if not (artifacts_dir(cfg) / "scaler.joblib").exists():
        pytest.skip("artifacts missing; run experiments.train_models first")

    run_id = uuid.uuid4().hex[:8]
    run_tag = f"storetest_{run_id}_rate0"
    tx_topic = f"store-tx-{run_id}"

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
            f"store-alerts-{run_id}",
            "--store",
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
    streamed = pd.read_csv(lat_csv).sort_values("tx_id")

    with psycopg.connect(cfg.postgres.dsn) as conn:
        events = conn.execute(
            "SELECT tx_id, score, is_alert FROM scored_events WHERE run_tag = %s ORDER BY tx_id",
            (run_tag,),
        ).fetchall()
        n_alerts = conn.execute(
            "SELECT count(*) FROM alerts WHERE run_tag = %s", (run_tag,)
        ).fetchone()[0]

    assert len(events) == N_MESSAGES == len(streamed)
    np.testing.assert_allclose(
        np.array([e[1] for e in events]), streamed["score"].to_numpy(), rtol=1e-12
    )
    assert n_alerts == int(streamed["is_alert"].sum()) == sum(e[2] for e in events)

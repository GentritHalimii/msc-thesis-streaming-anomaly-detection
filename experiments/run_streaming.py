"""Streaming runs: for each model x replay rate, spawn a producer and a
consumer as separate processes against the dockerized broker, collecting
per-message latency CSVs.

Requires: docker compose -f docker/docker-compose.yml up -d
Full-window replays at low rates take a while; --max-messages caps run length
(default 20000 -> ~7 min at 50 msg/s, ~20 s at 1000 msg/s).
"""

import argparse
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from confluent_kafka.admin import AdminClient, NewTopic

from src.config import REPO_ROOT, load_config
from src.evaluation.manifest import write_manifest
from src.models.build import UNSUPERVISED


def fresh_topics(cfg, run_id: str) -> tuple[str, str]:
    """Unique topics per run so replays don't mix; retention is short."""
    admin = AdminClient({"bootstrap.servers": cfg.kafka.bootstrap_servers})
    tx = f"{cfg.kafka.topic_transactions}-{run_id}"
    alerts = f"{cfg.kafka.topic_alerts}-{run_id}"
    futures = admin.create_topics(
        [NewTopic(t, num_partitions=1, replication_factor=1) for t in (tx, alerts)]
    )
    for f in futures.values():
        f.result(timeout=30)
    return tx, alerts


def run_one(
    cfg,
    model: str,
    rate: float,
    max_messages: int,
    store: bool = False,
    adaptive: bool = False,
    label: str = "",
) -> None:
    """One producer/consumer pair against the broker.

    `label` marks a run as a demonstration rather than a measurement. Labelled
    runs still reach PostgreSQL and Grafana, but their per-message CSV lands in
    a subdirectory that the latency report does not read, so showing the panel
    to somebody cannot overwrite a number the thesis quotes.
    """
    run_id = uuid.uuid4().hex[:8]
    tx_topic, alert_topic = fresh_topics(cfg, run_id)
    cfg.kafka.topic_transactions = tx_topic
    cfg.kafka.topic_alerts = alert_topic
    run_tag = f"{model}{'-adaptive' if adaptive else ''}_rate{rate:g}"
    if label:
        run_tag = f"{run_tag}-{label}"

    env_args = [
        "--tx-topic",
        tx_topic,
        "--alert-topic",
        alert_topic,
    ]
    ready_file = Path(tempfile.gettempdir()) / f"consumer-ready-{run_id}"
    consumer = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "src.streaming.consumer",
            "--model",
            model,
            "--run-tag",
            run_tag,
            "--ready-file",
            str(ready_file),
            *(["--out-dir", str(REPO_ROOT / cfg.results_dir / "latency" / label)] if label else []),
            *env_args,
            *(["--store"] if store else []),
            *(["--adaptive"] if adaptive else ["--no-adaptive"]),
        ],
        cwd=REPO_ROOT,
    )
    # Gate the producer on consumer readiness so latency reflects steady
    # state, not the consumer's startup backlog.
    deadline = time.monotonic() + 60
    while not ready_file.exists():
        if consumer.poll() is not None:
            raise RuntimeError(f"consumer exited before becoming ready for {run_tag}")
        if time.monotonic() > deadline:
            consumer.kill()
            raise RuntimeError(f"consumer not ready within 60s for {run_tag}")
        time.sleep(0.2)
    ready_file.unlink(missing_ok=True)
    producer = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.streaming.producer",
            "--rate",
            str(rate),
            "--max-messages",
            str(max_messages),
            *env_args,
        ],
        cwd=REPO_ROOT,
    )
    if producer.returncode != 0:
        consumer.kill()
        raise RuntimeError(f"producer failed for {run_tag}")
    if consumer.wait(timeout=600) != 0:
        raise RuntimeError(f"consumer failed for {run_tag}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=UNSUPERVISED + ["logreg"])
    parser.add_argument("--rates", nargs="*", type=float, default=None)
    parser.add_argument("--max-messages", type=int, default=20000)
    parser.add_argument("--store", action="store_true", help="persist to PostgreSQL")
    parser.add_argument(
        "--adaptive", action="store_true", help="sliding-window quantile threshold in the consumer"
    )
    parser.add_argument(
        "--label",
        default="",
        help="mark this run as a demonstration: it still reaches PostgreSQL, but its latency "
        "CSV is written aside so the measurement corpus is untouched",
    )
    args = parser.parse_args()

    cfg = load_config()
    rates = args.rates or cfg.kafka.replay_rates
    for model in args.models:
        for rate in rates:
            print(f"=== streaming run: {model} @ {rate} msg/s ===")
            run_one(
                load_config(),
                model,
                rate,
                args.max_messages,
                store=args.store,
                adaptive=args.adaptive,
                label=args.label,
            )
    write_manifest(REPO_ROOT / cfg.results_dir, "run_streaming", cfg.raw)


if __name__ == "__main__":
    main()

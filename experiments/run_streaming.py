"""Streaming runs: for each model x replay rate, spawn a producer and a
consumer as separate processes against the dockerized broker, collecting
per-message latency CSVs.

Requires: docker compose -f docker/docker-compose.yml up -d
Full-window replays at low rates take a while; --max-messages caps run length
(default 20000 -> ~7 min at 50 msg/s, ~20 s at 1000 msg/s).
"""

import argparse
import json
import re
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
    out_dir: Path | None = None,
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
    if label:
        out_dir = REPO_ROOT / cfg.results_dir / "latency" / label
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
            *(["--out-dir", str(out_dir)] if out_dir else []),
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
        capture_output=True,
        text=True,
    )
    print(producer.stdout, end="", flush=True)
    if producer.returncode != 0:
        consumer.kill()
        raise RuntimeError(f"producer failed for {run_tag}: {producer.stderr[-500:]}")
    # At high rates the producer itself may not keep the schedule. Its
    # achieved rate is kept next to the run, so a ceiling it imposes is not
    # mistaken for one of the consumer.
    achieved = re.search(r"at ([0-9.]+) msg/s", producer.stdout)
    target_dir = out_dir or REPO_ROOT / cfg.results_dir / "latency"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / f"producer_{run_tag}.json").write_text(
        json.dumps(
            {
                "target_rate_msg_s": rate,
                "achieved_rate_msg_s": float(achieved.group(1)) if achieved else None,
                "messages": max_messages,
            },
            indent=2,
        )
    )
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
        "--repeats",
        type=int,
        default=1,
        help="measure the whole grid this many times, one rep<k>/ folder per pass; the "
        "passes are interleaved so a slow drift of the machine spreads over every configuration",
    )
    parser.add_argument(
        "--out-subdir",
        default="",
        help="folder under results/latency for these runs, e.g. runs or capacity",
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
    base = REPO_ROOT / cfg.results_dir / "latency" / args.out_subdir if args.out_subdir else None
    for rep in range(1, args.repeats + 1):
        out_dir = base / f"rep{rep}" if base is not None else None
        for model in args.models:
            for rate in rates:
                print(f"=== streaming run {rep}/{args.repeats}: {model} @ {rate} msg/s ===")
                run_one(
                    load_config(),
                    model,
                    rate,
                    args.max_messages,
                    store=args.store,
                    adaptive=args.adaptive,
                    label=args.label,
                    out_dir=out_dir,
                )
    write_manifest(REPO_ROOT / cfg.results_dir, "run_streaming", cfg.raw)


if __name__ == "__main__":
    main()

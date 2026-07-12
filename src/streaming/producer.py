"""Replay the chronological test window into the `transactions` topic at a
fixed synthetic rate (msg/s).

The arrival process is synthetic — a constant rate, not the dataset's real
inter-arrival times — and every latency result is qualified with the rate
used. `produced_at_ns` is wall-clock (time.time_ns); producer and consumer
run on the same host, so no clock-skew handling is needed (documented).
"""

import argparse
import time

from confluent_kafka import Producer

from src.config import REPO_ROOT, load_config
from src.data.load import FEATURE_COLUMNS, load_transactions
from src.data.split import chronological_split
from src.streaming.serde import END_OF_STREAM, encode_transaction


def replay(cfg, rate: float, max_messages: int | None = None) -> int:
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    test = chronological_split(df, cfg.split.train_fraction).test
    if max_messages is not None:
        test = test.iloc[:max_messages]

    producer = Producer(
        {
            "bootstrap.servers": cfg.kafka.bootstrap_servers,
            "linger.ms": 0,  # send immediately; batching would add artificial latency
        }
    )
    topic = cfg.kafka.topic_transactions
    interval = 1.0 / rate
    columns = ["Time", *FEATURE_COLUMNS, "Class"]
    records = test[columns].to_dict("records")
    tx_ids = test.index.to_numpy()

    start = time.perf_counter()
    for i, (tx_id, row) in enumerate(zip(tx_ids, records, strict=True)):
        # Absolute schedule (start + i*interval), so per-message overhead
        # doesn't accumulate into rate drift.
        target = start + i * interval
        delay = target - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        payload = encode_transaction(int(tx_id), row, produced_at_ns=time.time_ns())
        producer.produce(topic, key=str(tx_id), value=payload)
        producer.poll(0)
    producer.produce(topic, key="eos", value=END_OF_STREAM)
    producer.flush()
    elapsed = time.perf_counter() - start
    achieved = len(records) / elapsed if elapsed > 0 else float("inf")
    print(f"replayed {len(records)} messages at {achieved:.1f} msg/s (target {rate})")
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, required=True, help="messages per second")
    parser.add_argument("--max-messages", type=int, default=None)
    parser.add_argument("--tx-topic", default=None, help="override transactions topic")
    parser.add_argument("--alert-topic", default=None, help="unused; accepted for symmetry")
    args = parser.parse_args()
    config = load_config()
    if args.tx_topic:
        config.kafka.topic_transactions = args.tx_topic
    replay(config, args.rate, args.max_messages)

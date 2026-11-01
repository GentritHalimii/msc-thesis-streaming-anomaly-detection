"""Score the transaction stream with a saved model and publish alerts.

Uses the SAME saved scaler and the SAME model.score() code path as offline
evaluation (tests/test_parity.py asserts score equality). Latency per message:

- infer_ms: model forward pass only, amortized over the micro-batch
- e2e_ms:   producer timestamp -> after alert publish (the full pipeline)

Micro-batching: poll collects up to `consumer_batch_max` already-arrived
messages and scores them as one matrix; at low arrival rates batches are
size 1, at high rates batching is what keeps throughput up.
"""

import argparse
import csv
import json
import threading
import time
import uuid
from collections import deque
from pathlib import Path

import numpy as np
import psutil
from confluent_kafka import Consumer, Producer

from src.config import REPO_ROOT, load_config
from src.data.scale import load_scaler
from src.evaluation.thresholds import percentile_threshold
from src.models.build import artifacts_dir, load_model
from src.streaming.serde import decode_transaction, encode_alert, is_end_of_stream


def _load_scoring_stack(cfg, model_name: str):
    scaler = load_scaler(artifacts_dir(cfg) / "scaler.joblib")
    model = load_model(model_name, cfg)
    train_scores = np.load(artifacts_dir(cfg) / "train_scores.npz")[model_name]
    split_summary = json.loads((artifacts_dir(cfg) / "split_summary.json").read_text())
    contamination = (
        float(cfg.contamination)
        if cfg.contamination is not None
        else split_summary["train_fraud_rate"]
    )
    if model_name == "ensemble_vote":
        from src.models.ensemble import MAJORITY_THRESHOLD

        threshold = MAJORITY_THRESHOLD  # majority rule, not a percentile
    else:
        threshold = percentile_threshold(train_scores, contamination)
    return scaler, model, threshold, contamination


class _AdaptiveThreshold:
    """Sliding-window quantile threshold maintained on the live stream.

    Keeps the alert *rate* stable rather than the alert *score*, so the
    investigation workload stays predictable when the score distribution
    drifts. Every decision uses only scores that arrived earlier: a message is
    never part of the buffer that judges it.
    """

    def __init__(
        self,
        contamination: float,
        window: int,
        refresh_every: int,
        warmup: float,
        min_warmup: int = 500,
    ):
        self._contamination = contamination
        self._buffer: deque[float] = deque(maxlen=window)
        self._refresh_every = refresh_every
        self._current = warmup
        self._min_warmup = min_warmup
        self._seen = 0
        self.refreshes = 0

    @property
    def value(self) -> float:
        return self._current

    def decide(self, score: float) -> bool:
        """Threshold this score, then admit it to the buffer."""
        if len(self._buffer) >= self._min_warmup and self._seen % self._refresh_every == 0:
            self._current = float(np.quantile(self._buffer, 1.0 - self._contamination))
            self.refreshes += 1
        flagged = score >= self._current
        self._buffer.append(float(score))
        self._seen += 1
        return bool(flagged)


def consume(
    cfg,
    model_name: str,
    run_tag: str,
    out_dir: Path | None = None,
    store: bool = False,
    ready_file: Path | str | None = None,
    adaptive: bool | None = None,
) -> Path:
    """`ready_file`: written once the consumer has joined the group and been
    assigned partitions. The orchestrator gates the producer on it so latency
    runs measure steady state, not consumer-startup backlog."""
    scaler, model, threshold, contamination = _load_scoring_stack(cfg, model_name)
    model.score(scaler.transform(np.zeros((1, 29))))  # warm-up: JIT/lazy-init out of band

    at_cfg = cfg.kafka.adaptive_threshold
    use_adaptive = at_cfg.enabled if adaptive is None else adaptive
    adaptive_thr = (
        _AdaptiveThreshold(contamination, at_cfg.window, at_cfg.refresh_every, threshold)
        if use_adaptive
        else None
    )
    sink = None
    if store:
        from src.storage.postgres import PostgresSink

        sink = PostgresSink(cfg.postgres.dsn, run_tag)
    out_dir = out_dir or (REPO_ROOT / cfg.results_dir / "latency")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"latency_{run_tag}.csv"

    consumer = Consumer(
        {
            "bootstrap.servers": cfg.kafka.bootstrap_servers,
            "group.id": f"scorer-{model_name}-{uuid.uuid4().hex[:8]}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )
    producer = Producer({"bootstrap.servers": cfg.kafka.bootstrap_servers, "linger.ms": 0})
    assigned = threading.Event()
    consumer.subscribe([cfg.kafka.topic_transactions], on_assign=lambda c, parts: assigned.set())
    batch_max = cfg.kafka.consumer_batch_max

    # Wait for partition assignment before declaring readiness. Messages
    # cannot be delivered before assignment, so pre_msgs stays empty in
    # gated runs; kept only for ungated invocations.
    pre_msgs = []
    while not assigned.is_set():
        pre_msgs.extend(consumer.consume(num_messages=batch_max, timeout=0.5))
    if ready_file is not None:
        Path(ready_file).touch()

    # Resource sampling for the operational-cost report.
    proc = psutil.Process()
    proc.cpu_percent()  # prime the counter
    samples = {"cpu": [], "rss": []}
    stop = threading.Event()

    def _sample():
        while not stop.is_set():
            samples["cpu"].append(proc.cpu_percent())
            samples["rss"].append(proc.memory_info().rss)
            stop.wait(0.25)

    threading.Thread(target=_sample, daemon=True).start()

    n_processed = 0
    n_alerts = 0
    done = False
    # Throughput window: creation of the first message to the decision on the
    # last, as in src.evaluation.operational.stream_throughput. A clock started
    # here would also count the producer's start-up, which begins only now.
    first_produced_ns = None
    last_decided_ns = None
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "tx_id",
                "model",
                "score",
                "is_alert",
                "label",
                "produced_at_ns",
                "infer_ms",
                "e2e_ms",
                "batch_size",
            ]
        )
        while not done:
            if pre_msgs:
                msgs, pre_msgs = pre_msgs, []
            else:
                # Short timeout bounds the micro-batch collection wait: without
                # it, batching itself adds O(100 ms) queueing delay at low
                # arrival rates and end-to-end latency inverts with rate.
                msgs = consumer.consume(num_messages=batch_max, timeout=0.05)
            if not msgs:
                continue
            batch = []
            for m in msgs:
                if m.error():
                    raise RuntimeError(m.error())
                record = decode_transaction(m.value())
                if is_end_of_stream(record):
                    done = True
                    continue
                batch.append(record)
            if not batch:
                continue
            if first_produced_ns is None:
                first_produced_ns = batch[0]["produced_at_ns"]

            X = scaler.transform(np.array([r["features"] for r in batch]))
            t0 = time.perf_counter()
            scores = model.score(X)
            infer_ms = (time.perf_counter() - t0) * 1e3 / len(batch)

            rows = []
            for record, score in zip(batch, scores, strict=True):
                if adaptive_thr is not None:
                    is_alert = adaptive_thr.decide(float(score))
                    active_threshold = adaptive_thr.value
                else:
                    is_alert = bool(score >= threshold)
                    active_threshold = threshold
                if is_alert:
                    alert = {
                        "tx_id": record["tx_id"],
                        "model": model_name,
                        "score": float(score),
                        "threshold": float(active_threshold),
                        "produced_at_ns": record["produced_at_ns"],
                        "alerted_at_ns": time.time_ns(),
                    }
                    producer.produce(
                        cfg.kafka.topic_alerts, key=str(record["tx_id"]), value=encode_alert(alert)
                    )
                    n_alerts += 1
                    if sink:
                        sink.add_alert(alert)
                e2e_ms = (time.time_ns() - record["produced_at_ns"]) / 1e6
                rows.append(
                    [
                        record["tx_id"],
                        model_name,
                        float(score),
                        int(is_alert),
                        record["class"],
                        record["produced_at_ns"],
                        infer_ms,
                        e2e_ms,
                        len(batch),
                    ]
                )
                if sink:
                    sink.add_event(
                        {
                            "tx_id": record["tx_id"],
                            "model": model_name,
                            "score": float(score),
                            "is_alert": is_alert,
                            "label": record["class"],
                            "produced_at_ns": record["produced_at_ns"],
                            "infer_ms": infer_ms,
                            "e2e_ms": e2e_ms,
                            "batch_size": len(batch),
                        }
                    )
            last_decided_ns = time.time_ns()
            producer.poll(0)
            writer.writerows(rows)
            n_processed += len(batch)

    elapsed = (last_decided_ns - first_produced_ns) / 1e9 if first_produced_ns else 0.0
    stop.set()
    producer.flush()
    consumer.close()
    if sink:
        sink.close()

    summary = {
        "run_tag": run_tag,
        "model": model_name,
        "threshold": threshold,
        "adaptive_threshold": bool(use_adaptive),
        "adaptive_refreshes": adaptive_thr.refreshes if adaptive_thr else 0,
        "n_processed": n_processed,
        "n_alerts": n_alerts,
        "elapsed_s": round(elapsed, 2),
        "throughput_msg_s": round(n_processed / elapsed, 1) if elapsed else None,
        "cpu_percent_mean": round(float(np.mean(samples["cpu"])), 1) if samples["cpu"] else None,
        "rss_peak_mb": round(max(samples["rss"]) / 1e6, 1) if samples["rss"] else None,
    }
    (out_dir / f"summary_{run_tag}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary))
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--tx-topic", default=None, help="override transactions topic")
    parser.add_argument("--alert-topic", default=None, help="override alerts topic")
    parser.add_argument("--store", action="store_true", help="persist to PostgreSQL")
    parser.add_argument("--ready-file", default=None, help="touched when consumer is assigned")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="where the per-message CSV goes; a demonstration run writes aside from the "
        "measurement corpus that the latency report reads",
    )
    parser.add_argument(
        "--adaptive",
        dest="adaptive",
        action="store_true",
        help="sliding-window quantile threshold instead of a fixed one",
    )
    parser.add_argument("--no-adaptive", dest="adaptive", action="store_false")
    parser.set_defaults(adaptive=None)
    args = parser.parse_args()
    config = load_config()
    if args.tx_topic:
        config.kafka.topic_transactions = args.tx_topic
    if args.alert_topic:
        config.kafka.topic_alerts = args.alert_topic
    consume(
        config,
        args.model,
        args.run_tag,
        out_dir=Path(args.out_dir) if args.out_dir else None,
        store=args.store,
        ready_file=args.ready_file,
        adaptive=args.adaptive,
    )

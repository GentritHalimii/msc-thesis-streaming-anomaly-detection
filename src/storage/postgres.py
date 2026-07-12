"""PostgreSQL persistence for scored events and alerts. Plain SQL, batched."""

import psycopg

DDL = """
CREATE TABLE IF NOT EXISTS scored_events (
    run_tag        text             NOT NULL,
    tx_id          bigint           NOT NULL,
    model          text             NOT NULL,
    score          double precision NOT NULL,
    is_alert       boolean          NOT NULL,
    label          integer          NOT NULL,
    produced_at_ns bigint           NOT NULL,
    infer_ms       double precision NOT NULL,
    e2e_ms         double precision NOT NULL,
    batch_size     integer          NOT NULL,
    PRIMARY KEY (run_tag, tx_id, model)
);
CREATE TABLE IF NOT EXISTS alerts (
    run_tag        text             NOT NULL,
    tx_id          bigint           NOT NULL,
    model          text             NOT NULL,
    score          double precision NOT NULL,
    threshold      double precision NOT NULL,
    produced_at_ns bigint           NOT NULL,
    alerted_at_ns  bigint           NOT NULL,
    PRIMARY KEY (run_tag, tx_id, model)
);
"""

_EVENT_SQL = (
    "INSERT INTO scored_events VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING"
)
_ALERT_SQL = "INSERT INTO alerts VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING"


class PostgresSink:
    """Buffered writer; flush() every `batch_size` rows and on close()."""

    def __init__(self, dsn: str, run_tag: str, batch_size: int = 500):
        self._conn = psycopg.connect(dsn)
        self._run_tag = run_tag
        self._batch_size = batch_size
        self._events: list[tuple] = []
        self._alerts: list[tuple] = []
        with self._conn.cursor() as cur:
            cur.execute(DDL)
        self._conn.commit()

    def add_event(self, row: dict) -> None:
        self._events.append(
            (
                self._run_tag,
                row["tx_id"],
                row["model"],
                row["score"],
                row["is_alert"],
                row["label"],
                row["produced_at_ns"],
                row["infer_ms"],
                row["e2e_ms"],
                row["batch_size"],
            )
        )
        if len(self._events) >= self._batch_size:
            self.flush()

    def add_alert(self, alert: dict) -> None:
        self._alerts.append(
            (
                self._run_tag,
                alert["tx_id"],
                alert["model"],
                alert["score"],
                alert["threshold"],
                alert["produced_at_ns"],
                alert["alerted_at_ns"],
            )
        )

    def flush(self) -> None:
        with self._conn.cursor() as cur:
            if self._events:
                cur.executemany(_EVENT_SQL, self._events)
                self._events.clear()
            if self._alerts:
                cur.executemany(_ALERT_SQL, self._alerts)
                self._alerts.clear()
        self._conn.commit()

    def close(self) -> None:
        self.flush()
        self._conn.close()

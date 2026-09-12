"""Health and live state of the three containers the streaming layer needs.

Kafka, PostgreSQL and Grafana run in the project's own docker stack on ports
19092, 15432 and 3000. This module answers three questions for the browser:
is each one reachable, what is already in the database, and can the Grafana
dashboard be embedded. It also exposes the two compose commands, because a
demo that begins with "open a terminal first" is a demo that goes wrong.
"""

from __future__ import annotations

import json
import socket
import subprocess
import urllib.error
import urllib.request
from functools import lru_cache
from typing import Any
from urllib.parse import urlsplit

from src.config import REPO_ROOT, load_config

COMPOSE_FILE = REPO_ROOT / "docker" / "docker-compose.yml"
GRAFANA_URL = "http://localhost:3000"
DASHBOARD_UID = "sad-anomaly"
CONTAINERS = {"kafka": "sad-kafka", "postgres": "sad-postgres", "grafana": "sad-grafana"}


@lru_cache(maxsize=1)
def _cfg():
    return load_config()


def _port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _container_states() -> dict[str, str]:
    try:
        out = subprocess.run(  # noqa: S603
            ["docker", "ps", "-a", "--format", "{{.Names}}\t{{.State}}"],
            capture_output=True,
            text=True,
            timeout=6,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}
    states = {}
    for line in out.stdout.splitlines():
        name, _, state = line.partition("\t")
        states[name.strip()] = state.strip()
    return states


def _kafka_endpoint() -> tuple[str, int]:
    servers = _cfg().kafka.bootstrap_servers.split(",")[0]
    host, _, port = servers.partition(":")
    return host or "localhost", int(port or 9092)


def _postgres_endpoint() -> tuple[str, int]:
    parts = urlsplit(_cfg().postgres.dsn)
    return parts.hostname or "localhost", parts.port or 5432


def grafana_health() -> dict[str, Any]:
    try:
        with urllib.request.urlopen(f"{GRAFANA_URL}/api/health", timeout=1.5) as response:  # noqa: S310
            payload = json.loads(response.read().decode())
        return {"ok": payload.get("database") == "ok", "version": payload.get("version")}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return {"ok": False, "version": None}


def grafana_embeddable() -> bool:
    """Grafana refuses to be framed unless allow_embedding is on."""
    try:
        request = urllib.request.Request(f"{GRAFANA_URL}/login", method="HEAD")
        with urllib.request.urlopen(request, timeout=1.5) as response:  # noqa: S310
            deny = (response.headers.get("X-Frame-Options") or "").lower()
        return deny not in {"deny", "sameorigin"}
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def status() -> dict[str, Any]:
    states = _container_states()
    kafka_host, kafka_port = _kafka_endpoint()
    pg_host, pg_port = _postgres_endpoint()
    grafana = grafana_health()
    services = {
        "kafka": {
            "container": states.get(CONTAINERS["kafka"], "mungon"),
            "reachable": _port_open(kafka_host, kafka_port),
            "endpoint": f"{kafka_host}:{kafka_port}",
        },
        "postgres": {
            "container": states.get(CONTAINERS["postgres"], "mungon"),
            "reachable": _port_open(pg_host, pg_port),
            "endpoint": f"{pg_host}:{pg_port}",
        },
        "grafana": {
            "container": states.get(CONTAINERS["grafana"], "mungon"),
            "reachable": grafana["ok"],
            "endpoint": GRAFANA_URL,
            "version": grafana["version"],
            "embeddable": grafana_embeddable() if grafana["ok"] else False,
        },
    }
    services["docker"] = {"available": bool(states) or _docker_present()}
    return {
        "services": services,
        "grafana_url": GRAFANA_URL,
        "dashboard_uid": DASHBOARD_UID,
        "all_up": all(services[k]["reachable"] for k in ("kafka", "postgres", "grafana")),
    }


def _docker_present() -> bool:
    try:
        subprocess.run(  # noqa: S603
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            timeout=6,
            check=False,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def compose(action: str) -> dict[str, Any]:
    if action not in {"up", "down"}:
        raise ValueError(action)
    argv = ["docker", "compose", "-f", str(COMPOSE_FILE)]
    argv += ["up", "-d"] if action == "up" else ["down"]
    try:
        out = subprocess.run(  # noqa: S603
            argv, capture_output=True, text=True, timeout=180, check=False
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "output": f"{type(exc).__name__}: {exc}"}
    return {
        "ok": out.returncode == 0,
        "output": (out.stdout + out.stderr).strip()[-4000:],
        "returncode": out.returncode,
    }


# --- what is already in the database ---------------------------------------

_SUMMARY_SQL = """
SELECT
  (SELECT count(*) FROM scored_events)                         AS events,
  (SELECT count(*) FROM alerts)                                AS alerts,
  (SELECT count(DISTINCT run_tag) FROM scored_events)          AS runs,
  (SELECT count(DISTINCT model) FROM scored_events)            AS models,
  (SELECT count(*) FROM scored_events WHERE label = 1)         AS frauds,
  (SELECT count(*) FROM alerts a JOIN scored_events s
     ON a.run_tag = s.run_tag AND a.tx_id = s.tx_id AND a.model = s.model
   WHERE s.label = 1)                                          AS true_alerts
"""

_PER_RUN_SQL = """
SELECT run_tag, model,
       count(*)                       AS events,
       sum(CASE WHEN is_alert THEN 1 ELSE 0 END) AS alerts,
       sum(label)                     AS frauds,
       avg(e2e_ms)                    AS e2e_mean,
       max(e2e_ms)                    AS e2e_max,
       avg(infer_ms)                  AS infer_mean,
       to_timestamp(max(produced_at_ns) / 1e9) AS last_seen
FROM scored_events
GROUP BY run_tag, model
ORDER BY max(produced_at_ns) DESC
LIMIT 12
"""

_RECENT_ALERTS_SQL = """
SELECT a.run_tag, a.model, a.tx_id, a.score, a.threshold, s.label,
       to_timestamp(a.alerted_at_ns / 1e9) AS alerted_at
FROM alerts a
LEFT JOIN scored_events s
  ON a.run_tag = s.run_tag AND a.tx_id = s.tx_id AND a.model = s.model
ORDER BY a.alerted_at_ns DESC
LIMIT 15
"""


def database() -> dict[str, Any]:
    """Live counters straight from PostgreSQL; empty payload when it is down."""
    host, port = _postgres_endpoint()
    if not _port_open(host, port):
        return {"available": False, "reason": "PostgreSQL nuk është i arritshëm"}
    try:
        import psycopg
    except ImportError:  # pragma: no cover - psycopg is a project dependency
        return {"available": False, "reason": "psycopg mungon"}
    try:
        with psycopg.connect(_cfg().postgres.dsn, connect_timeout=3) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT to_regclass('public.scored_events') IS NOT NULL"
                " AND to_regclass('public.alerts') IS NOT NULL"
            )
            row = cur.fetchone()
            if not row or not row[0]:
                return {"available": True, "empty": True, "reason": "tabelat nuk ekzistojnë ende"}
            cur.execute(_SUMMARY_SQL)
            keys = [c.name for c in cur.description or []]
            summary = dict(zip(keys, cur.fetchone() or [], strict=False))
            cur.execute(_PER_RUN_SQL)
            run_keys = [c.name for c in cur.description or []]
            runs = [dict(zip(run_keys, r, strict=False)) for r in cur.fetchall()]
            cur.execute(_RECENT_ALERTS_SQL)
            alert_keys = [c.name for c in cur.description or []]
            alerts = [dict(zip(alert_keys, r, strict=False)) for r in cur.fetchall()]
    except Exception as exc:  # noqa: BLE001 - any driver error means "not available"
        return {"available": False, "reason": f"{type(exc).__name__}: {exc}"}
    return {
        "available": True,
        "empty": not summary.get("events"),
        "summary": _jsonable(summary),
        "runs": [_jsonable(r) for r in runs],
        "alerts": [_jsonable(a) for a in alerts],
    }


def _jsonable(record: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in record.items():
        if hasattr(value, "isoformat"):
            out[key] = value.isoformat()
        elif isinstance(value, int | float | str | bool) or value is None:
            out[key] = value
        else:
            out[key] = float(value)
    return out

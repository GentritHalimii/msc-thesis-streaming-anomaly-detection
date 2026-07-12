"""Run manifests: every experiment records enough to reproduce its numbers."""

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

import psutil

TRACKED_PACKAGES = [
    "numpy",
    "pandas",
    "scikit-learn",
    "torch",
    "confluent-kafka",
    "psycopg",
]


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def write_manifest(results_dir: Path | str, run_name: str, raw_config: dict) -> Path:
    config_bytes = json.dumps(raw_config, sort_keys=True).encode()
    manifest = {
        "run": run_name,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "config": raw_config,
        "packages": {p: metadata.version(p) for p in TRACKED_PACKAGES},
        "python": platform.python_version(),
        "hardware": {
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(logical=True),
            "memory_gb": round(psutil.virtual_memory().total / 1e9, 1),
            "platform": platform.platform(),
        },
    }
    out = Path(results_dir) / f"manifest_{run_name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))
    return out

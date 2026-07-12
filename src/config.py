"""Load config/config.yaml into a plain namespace, once, at program start."""

from pathlib import Path
from types import SimpleNamespace

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "config.yaml"


def _to_namespace(obj):
    if isinstance(obj, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in obj.items()})
    return obj


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> SimpleNamespace:
    with open(path) as f:
        raw = yaml.safe_load(f)
    cfg = _to_namespace(raw)
    cfg.raw = raw  # kept for hashing into run manifests
    return cfg

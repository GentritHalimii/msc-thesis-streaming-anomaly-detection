"""Model registry: construct, locate and load every detector from config.

The study is deliberately narrow. The proposal names Isolation Forest and the
Autoencoder as the primary detectors, One-Class SVM as an additional
component, and Logistic Regression as a supervised baseline, and the
comparison here keeps exactly to that set. Depth is bought elsewhere: in the
evaluation protocol, in the hyperparameter surfaces, in the preprocessing and
feature studies, and in the per-transaction error analysis.

One extra estimator is registered but is not a competitor. A linear
reconstruction detector built on a PCA subspace is the natural floor of the
reconstruction family, and since V1..V28 are themselves principal components
it answers a sharp question about the Autoencoder: does the non-linear
encoder recover anything the linear projection had not already exposed. It is
used only inside the Autoencoder ablation and never enters the main table.
"""

import inspect
from pathlib import Path
from types import SimpleNamespace

from src.config import REPO_ROOT
from src.models.autoencoder import AutoencoderModel
from src.models.base import AnomalyModel
from src.models.ensemble import EnsembleModel
from src.models.iforest import IForestModel
from src.models.logreg import LogRegReference
from src.models.ocsvm import OCSVMModel
from src.models.reconstruction import PCAReconstruction

# The three unsupervised detectors named in the proposal, grouped by the
# mechanism each uses to decide what "abnormal" means.
FAMILIES = {
    "isolation": ["iforest"],
    "reconstruction": ["autoencoder"],
    "boundary": ["ocsvm"],
}
UNSUPERVISED = [m for members in FAMILIES.values() for m in members]
REFERENCE = "logreg"
ALL_MODELS = [*UNSUPERVISED, REFERENCE]

# Registered, but not part of the comparison: the linear floor used inside the
# Autoencoder ablation.
ABLATION_MODELS = ["pca_recon"]

ENSEMBLES = ["ensemble_avg", "ensemble_vote"]
FAMILY_OF = {m: fam for fam, members in FAMILIES.items() for m in members}
FAMILY_OF["pca_recon"] = "reconstruction"

_TORCH_MODELS = {"autoencoder"}

_CLASSES = {
    "iforest": IForestModel,
    "autoencoder": AutoencoderModel,
    "ocsvm": OCSVMModel,
    "logreg": LogRegReference,
    "pca_recon": PCAReconstruction,
    "ensemble_avg": EnsembleModel,
    "ensemble_vote": EnsembleModel,
}


def _hp(cfg: SimpleNamespace, name: str) -> dict:
    """Hyperparameters for `name` from config, as a plain dict."""
    node = getattr(cfg.models, name, None)
    return dict(vars(node)) if node is not None else {}


def build_model(name: str, cfg: SimpleNamespace, overrides: dict | None = None) -> AnomalyModel:
    """Construct an unfitted detector. `overrides` wins over config, which is
    how the hyperparameter searches inject candidate settings.

    Parameters are filtered against the constructor signature so that a global
    setting such as `seed` can be offered to every detector without breaking
    the deterministic-by-construction ones that do not take it.
    """
    if name not in _CLASSES:
        raise ValueError(f"unknown model: {name}")
    cls = _CLASSES[name]
    params = _hp(cfg, name)
    params.update(overrides or {})
    params.setdefault("seed", cfg.seed)
    accepted = set(inspect.signature(cls.__init__).parameters)
    unknown = set(params) - accepted - {"seed"}
    if unknown:
        raise ValueError(f"{name}: config has unknown hyperparameters {sorted(unknown)}")
    return cls(**{k: v for k, v in params.items() if k in accepted})


def artifacts_dir(cfg) -> Path:
    return REPO_ROOT / cfg.data.artifacts_dir


def model_path(cfg, name: str) -> Path:
    ext = "pt" if name in _TORCH_MODELS else "joblib"
    return artifacts_dir(cfg) / f"{name}.{ext}"


def scaler_path(cfg) -> Path:
    return artifacts_dir(cfg) / "scaler.joblib"


def load_model(name: str, cfg) -> AnomalyModel:
    return _CLASSES[name].load(model_path(cfg, name))

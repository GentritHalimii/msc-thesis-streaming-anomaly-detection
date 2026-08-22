"""Model registry: construct, locate and load every detector from config.

The zoo is organised by the mechanism each detector uses to decide what
"abnormal" means, because that taxonomy — not the individual algorithm — is
what the comparison in this thesis is really about.
"""

import inspect
from pathlib import Path
from types import SimpleNamespace

from src.config import REPO_ROOT
from src.models.autoencoder import AutoencoderModel
from src.models.base import AnomalyModel
from src.models.deep_svdd import DeepSVDDModel
from src.models.density import GMMDensity, RobustMahalanobis
from src.models.ensemble import EnsembleModel
from src.models.iforest import IForestModel
from src.models.logreg import LogRegReference
from src.models.ocsvm import OCSVMModel
from src.models.proximity import KNNDistance, LOFNovelty
from src.models.pyod_models import COPODModel, ECODModel, HBOSModel, LODAModel
from src.models.reconstruction import PCAReconstruction
from src.models.vae import VAEModel

# Detector family -> members. Drives both the results tables and the
# taxonomy discussion in the thesis.
FAMILIES = {
    "isolation": ["iforest"],
    "boundary": ["ocsvm", "deep_svdd"],
    "proximity": ["lof", "knn"],
    "reconstruction": ["pca_recon", "autoencoder", "vae"],
    "density": ["gmm", "mahalanobis"],
    "statistical": ["ecod", "copod", "hbos", "loda"],
}
UNSUPERVISED = [m for members in FAMILIES.values() for m in members]
REFERENCE = "logreg"
ALL_MODELS = [*UNSUPERVISED, REFERENCE]
ENSEMBLES = ["ensemble_avg", "ensemble_vote"]

FAMILY_OF = {m: fam for fam, members in FAMILIES.items() for m in members}

# The four detectors carried through the original proposal; reported as the
# headline comparison so the thesis answers its stated research question
# before widening the field.
CORE_MODELS = ["iforest", "autoencoder", "ocsvm", "logreg"]

_TORCH_MODELS = {"autoencoder", "vae", "deep_svdd"}

_CLASSES = {
    "iforest": IForestModel,
    "ocsvm": OCSVMModel,
    "deep_svdd": DeepSVDDModel,
    "lof": LOFNovelty,
    "knn": KNNDistance,
    "pca_recon": PCAReconstruction,
    "autoencoder": AutoencoderModel,
    "vae": VAEModel,
    "gmm": GMMDensity,
    "mahalanobis": RobustMahalanobis,
    "ecod": ECODModel,
    "copod": COPODModel,
    "hbos": HBOSModel,
    "loda": LODAModel,
    "logreg": LogRegReference,
    "ensemble_avg": EnsembleModel,
    "ensemble_vote": EnsembleModel,
}


def _hp(cfg: SimpleNamespace, name: str) -> dict:
    """Hyperparameters for `name` from config, as a plain dict."""
    node = getattr(cfg.models, name, None)
    return dict(vars(node)) if node is not None else {}


def build_model(name: str, cfg: SimpleNamespace, overrides: dict | None = None) -> AnomalyModel:
    """Construct an unfitted detector. `overrides` wins over config, which is
    how the hyperparameter search injects candidate settings.

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

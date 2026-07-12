"""Construct / load models from config. A dict, not a framework."""

from pathlib import Path
from types import SimpleNamespace

from src.config import REPO_ROOT
from src.models.autoencoder import AutoencoderModel
from src.models.base import AnomalyModel
from src.models.ensemble import EnsembleModel
from src.models.iforest import IForestModel
from src.models.logreg import LogRegReference
from src.models.ocsvm import OCSVMModel

UNSUPERVISED = ["iforest", "autoencoder", "ocsvm"]
ALL_MODELS = [*UNSUPERVISED, "logreg"]
ENSEMBLES = ["ensemble_avg", "ensemble_vote"]

_EXT = {"autoencoder": "pt"}
_CLASSES = {
    "iforest": IForestModel,
    "autoencoder": AutoencoderModel,
    "ocsvm": OCSVMModel,
    "logreg": LogRegReference,
    "ensemble_avg": EnsembleModel,
    "ensemble_vote": EnsembleModel,
}


def build_model(name: str, cfg: SimpleNamespace) -> AnomalyModel:
    seed = cfg.seed
    m = cfg.models
    if name == "iforest":
        return IForestModel(
            n_estimators=m.iforest.n_estimators, max_samples=m.iforest.max_samples, seed=seed
        )
    if name == "ocsvm":
        return OCSVMModel(
            train_subsample=m.ocsvm.train_subsample,
            kernel=m.ocsvm.kernel,
            nu=m.ocsvm.nu,
            gamma=m.ocsvm.gamma,
            seed=seed,
        )
    if name == "autoencoder":
        return AutoencoderModel(
            hidden_dim=m.autoencoder.hidden_dim,
            latent_dim=m.autoencoder.latent_dim,
            epochs=m.autoencoder.epochs,
            batch_size=m.autoencoder.batch_size,
            lr=m.autoencoder.lr,
            seed=seed,
        )
    if name == "logreg":
        return LogRegReference(
            max_iter=m.logreg.max_iter, class_weight=m.logreg.class_weight, seed=seed
        )
    raise ValueError(f"unknown model: {name}")


def artifacts_dir(cfg) -> Path:
    return REPO_ROOT / cfg.data.artifacts_dir


def model_path(cfg, name: str) -> Path:
    return artifacts_dir(cfg) / f"{name}.{_EXT.get(name, 'joblib')}"


def scaler_path(cfg) -> Path:
    return artifacts_dir(cfg) / "scaler.joblib"


def load_model(name: str, cfg) -> AnomalyModel:
    return _CLASSES[name].load(model_path(cfg, name))

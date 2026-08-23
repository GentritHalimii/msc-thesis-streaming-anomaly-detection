"""Autoencoder detector, with the design space the thesis actually explores.

The anomaly score is the reconstruction error of a network trained only on
normal transactions. Around that core the class exposes the levers that the
Autoencoder study varies one at a time: encoder depth and width, latent
dimension, training objective, weight decay, dropout, and input corruption
for a denoising variant.

One convention matters for the ablations to be interpretable. The training
objective can be squared error, absolute error or Huber, but the anomaly
score is always the mean squared reconstruction error. Scoring with the same
discrepancy that was trained would change the ranking function as well as the
learned weights, and the two effects could not then be separated.
"""

from pathlib import Path

import numpy as np
import torch
from torch import nn

from src.models.base import AnomalyModel

LOSSES = ("mse", "mae", "huber")


def _encoder_widths(n_features: int, hidden_dim: int, latent_dim: int, depth: int) -> list[int]:
    """Hidden widths tapering geometrically from `hidden_dim` to `latent_dim`.

    Depth 1 gives the single hidden layer used as the default configuration;
    deeper encoders interpolate so that a depth sweep changes only how the
    same compression is reached, not how much compression there is.
    """
    if depth < 1:
        raise ValueError("depth must be at least 1")
    if depth == 1:
        return [hidden_dim]
    ratio = (latent_dim / hidden_dim) ** (1.0 / depth)
    widths = [max(latent_dim + 1, int(round(hidden_dim * ratio**i))) for i in range(depth)]
    return widths


class _AE(nn.Module):
    def __init__(
        self, n_features: int, hidden_dim: int, latent_dim: int, depth: int, dropout: float
    ):
        super().__init__()
        widths = _encoder_widths(n_features, hidden_dim, latent_dim, depth)

        encoder: list[nn.Module] = []
        previous = n_features
        for width in widths:
            encoder += [nn.Linear(previous, width), nn.ReLU()]
            if dropout > 0:
                encoder.append(nn.Dropout(dropout))
            previous = width
        encoder += [nn.Linear(previous, latent_dim), nn.ReLU()]
        self.encoder = nn.Sequential(*encoder)

        decoder: list[nn.Module] = []
        previous = latent_dim
        for width in reversed(widths):
            decoder += [nn.Linear(previous, width), nn.ReLU()]
            previous = width
        decoder.append(nn.Linear(previous, n_features))
        self.decoder = nn.Sequential(*decoder)

    def forward(self, x):
        return self.decoder(self.encoder(x))


class AutoencoderModel(AnomalyModel):
    name = "autoencoder"

    def __init__(
        self,
        n_features: int = 29,
        hidden_dim: int = 16,
        latent_dim: int = 8,
        depth: int = 1,
        epochs: int = 20,
        batch_size: int = 512,
        lr: float = 1e-3,
        weight_decay: float = 0.0,
        dropout: float = 0.0,
        noise_std: float = 0.0,
        loss: str = "mse",
        seed: int = 42,
    ):
        if loss not in LOSSES:
            raise ValueError(f"unknown loss {loss!r}; expected one of {LOSSES}")
        if latent_dim >= hidden_dim and depth > 1:
            # A taper that does not narrow is a different architecture, not a
            # deeper one; refuse rather than silently build something else.
            raise ValueError("latent_dim must be smaller than hidden_dim for depth > 1")
        self._params = {
            "n_features": n_features,
            "hidden_dim": hidden_dim,
            "latent_dim": latent_dim,
            "depth": depth,
            "epochs": epochs,
            "batch_size": batch_size,
            "lr": lr,
            "weight_decay": weight_decay,
            "dropout": dropout,
            "noise_std": noise_std,
            "loss": loss,
            "seed": seed,
        }
        self._net = _AE(n_features, hidden_dim, latent_dim, depth, dropout)
        self.history: list[float] = []

    # -- training ---------------------------------------------------------
    def _criterion(self):
        return {"mse": nn.MSELoss(), "mae": nn.L1Loss(), "huber": nn.HuberLoss()}[
            self._params["loss"]
        ]

    def fit(self, X: np.ndarray) -> "AutoencoderModel":
        p = self._params
        torch.manual_seed(p["seed"])
        torch.use_deterministic_algorithms(True)
        # Re-initialise under the fixed seed so fit() is deterministic no
        # matter what happened at construction time.
        self._net = _AE(p["n_features"], p["hidden_dim"], p["latent_dim"], p["depth"], p["dropout"])
        opt = torch.optim.Adam(self._net.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        criterion = self._criterion()
        data = torch.from_numpy(X.astype(np.float32))
        generator = torch.Generator().manual_seed(p["seed"])

        self.history = []
        self._net.train()
        for _ in range(p["epochs"]):
            perm = torch.randperm(len(data), generator=generator)
            running, seen = 0.0, 0
            for start in range(0, len(data), p["batch_size"]):
                batch = data[perm[start : start + p["batch_size"]]]
                inputs = batch
                if p["noise_std"] > 0:
                    # Denoising variant: corrupt the input, reconstruct the
                    # clean transaction. The target is always the clean batch.
                    noise = torch.randn(batch.shape, generator=generator) * p["noise_std"]
                    inputs = batch + noise
                opt.zero_grad()
                loss = criterion(self._net(inputs), batch)
                loss.backward()
                opt.step()
                running += float(loss.detach()) * len(batch)
                seen += len(batch)
            self.history.append(running / max(seen, 1))
        self._net.eval()
        return self

    # -- scoring ----------------------------------------------------------
    @torch.no_grad()
    def score(self, X: np.ndarray) -> np.ndarray:
        self._net.eval()
        data = torch.from_numpy(X.astype(np.float32))
        recon = self._net(data)
        return ((recon - data) ** 2).mean(dim=1).numpy()

    @torch.no_grad()
    def reconstruction_error_per_feature(self, X: np.ndarray) -> np.ndarray:
        """Squared error per input component, averaged over rows.

        The anomaly score is the row mean of exactly these values, so this is
        the model's own account of why it flagged what it flagged.
        """
        self._net.eval()
        data = torch.from_numpy(X.astype(np.float32))
        return ((self._net(data) - data) ** 2).mean(dim=0).numpy()

    # -- persistence ------------------------------------------------------
    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {"params": self._params, "state_dict": self._net.state_dict(), "history": self.history},
            path,
        )

    @classmethod
    def load(cls, path: Path | str) -> "AutoencoderModel":
        payload = torch.load(path, weights_only=True)
        obj = cls(**payload["params"])
        obj._net.load_state_dict(payload["state_dict"])
        obj.history = list(payload.get("history", []))
        obj._net.eval()
        return obj

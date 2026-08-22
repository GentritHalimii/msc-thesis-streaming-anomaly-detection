"""Variational autoencoder scored by its negative evidence lower bound.

The plain autoencoder scores a point by how badly it is reconstructed; the VAE
adds a probabilistic penalty for how unlikely the point's latent code is under
the prior. The negative ELBO therefore combines "hard to reconstruct" with
"lands in an improbable region of latent space", which is the theoretically
cleaner notion of surprise.
"""

from pathlib import Path

import numpy as np
import torch
from torch import nn

from src.models.base import AnomalyModel


class _VAENet(nn.Module):
    def __init__(self, n_features: int, hidden_dim: int, latent_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(n_features, hidden_dim), nn.ReLU())
        self.to_mu = nn.Linear(hidden_dim, latent_dim)
        self.to_logvar = nn.Linear(hidden_dim, latent_dim)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, n_features)
        )

    def encode(self, x):
        h = self.encoder(x)
        # clamped for numerical stability: exp(0.5 * logvar) overflows fast
        return self.to_mu(h), self.to_logvar(h).clamp(-8.0, 8.0)

    def forward(self, x, generator=None):
        mu, logvar = self.encode(x)
        std = torch.exp(0.5 * logvar)
        eps = torch.randn(std.shape, generator=generator)
        return self.decoder(mu + eps * std), mu, logvar


class VAEModel(AnomalyModel):
    name = "vae"

    def __init__(
        self,
        n_features: int = 29,
        hidden_dim: int = 24,
        latent_dim: int = 8,
        epochs: int = 30,
        batch_size: int = 512,
        lr: float = 1e-3,
        beta: float = 1.0,
        seed: int = 42,
    ):
        self._params = {
            "n_features": n_features,
            "hidden_dim": hidden_dim,
            "latent_dim": latent_dim,
            "epochs": epochs,
            "batch_size": batch_size,
            "lr": lr,
            "beta": beta,
            "seed": seed,
        }
        self._net = _VAENet(n_features, hidden_dim, latent_dim)

    @staticmethod
    def _elbo_terms(recon, x, mu, logvar):
        recon_err = ((recon - x) ** 2).sum(dim=1)
        kl = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(dim=1)
        return recon_err, kl

    def fit(self, X: np.ndarray) -> "VAEModel":
        p = self._params
        torch.manual_seed(p["seed"])
        self._net = _VAENet(p["n_features"], p["hidden_dim"], p["latent_dim"])
        opt = torch.optim.Adam(self._net.parameters(), lr=p["lr"])
        data = torch.from_numpy(X.astype(np.float32))
        gen = torch.Generator().manual_seed(p["seed"])
        self._net.train()
        for _ in range(p["epochs"]):
            perm = torch.randperm(len(data), generator=gen)
            for start in range(0, len(data), p["batch_size"]):
                batch = data[perm[start : start + p["batch_size"]]]
                opt.zero_grad()
                recon, mu, logvar = self._net(batch, generator=gen)
                recon_err, kl = self._elbo_terms(recon, batch, mu, logvar)
                (recon_err + p["beta"] * kl).mean().backward()
                opt.step()
        self._net.eval()
        return self

    @torch.no_grad()
    def score(self, X: np.ndarray) -> np.ndarray:
        """Negative ELBO with the mean latent code (deterministic at inference)."""
        self._net.eval()
        data = torch.from_numpy(X.astype(np.float32))
        mu, logvar = self._net.encode(data)
        recon = self._net.decoder(mu)
        recon_err, kl = self._elbo_terms(recon, data, mu, logvar)
        return (recon_err + self._params["beta"] * kl).numpy()

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({"params": self._params, "state_dict": self._net.state_dict()}, path)

    @classmethod
    def load(cls, path: Path | str) -> "VAEModel":
        payload = torch.load(path, weights_only=True)
        obj = cls(**payload["params"])
        obj._net.load_state_dict(payload["state_dict"])
        obj._net.eval()
        return obj

from pathlib import Path

import numpy as np
import torch
from torch import nn

from src.models.base import AnomalyModel


class _AE(nn.Module):
    def __init__(self, n_features: int, hidden_dim: int, latent_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(n_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_features),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))


class AutoencoderModel(AnomalyModel):
    """MLP autoencoder trained on normal transactions; anomaly score = MSE
    reconstruction error. CPU-only, fully seeded for determinism."""

    name = "autoencoder"

    def __init__(
        self,
        n_features: int = 29,
        hidden_dim: int = 16,
        latent_dim: int = 8,
        epochs: int = 20,
        batch_size: int = 512,
        lr: float = 1e-3,
        seed: int = 42,
    ):
        self._params = {
            "n_features": n_features,
            "hidden_dim": hidden_dim,
            "latent_dim": latent_dim,
            "epochs": epochs,
            "batch_size": batch_size,
            "lr": lr,
            "seed": seed,
        }
        self._net = _AE(n_features, hidden_dim, latent_dim)

    def fit(self, X: np.ndarray) -> "AutoencoderModel":
        p = self._params
        torch.manual_seed(p["seed"])
        torch.use_deterministic_algorithms(True)
        # Re-init under the fixed seed so fit() is deterministic regardless of
        # what happened at construction time.
        self._net = _AE(p["n_features"], p["hidden_dim"], p["latent_dim"])
        opt = torch.optim.Adam(self._net.parameters(), lr=p["lr"])
        loss_fn = nn.MSELoss()
        data = torch.from_numpy(X.astype(np.float32))
        generator = torch.Generator().manual_seed(p["seed"])
        self._net.train()
        for _ in range(p["epochs"]):
            perm = torch.randperm(len(data), generator=generator)
            for start in range(0, len(data), p["batch_size"]):
                batch = data[perm[start : start + p["batch_size"]]]
                opt.zero_grad()
                loss = loss_fn(self._net(batch), batch)
                loss.backward()
                opt.step()
        self._net.eval()
        return self

    @torch.no_grad()
    def score(self, X: np.ndarray) -> np.ndarray:
        self._net.eval()
        data = torch.from_numpy(X.astype(np.float32))
        recon = self._net(data)
        return ((recon - data) ** 2).mean(dim=1).numpy()

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({"params": self._params, "state_dict": self._net.state_dict()}, path)

    @classmethod
    def load(cls, path: Path | str) -> "AutoencoderModel":
        payload = torch.load(path, weights_only=True)
        obj = cls(**payload["params"])
        obj._net.load_state_dict(payload["state_dict"])
        obj._net.eval()
        return obj

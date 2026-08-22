"""Deep Support Vector Data Description (Deep SVDD).

Learns a network phi that maps normal transactions inside a minimum-volume
hypersphere with fixed centre c; the anomaly score is the squared distance to
that centre. Unlike the autoencoder it optimises a genuine one-class
objective rather than reconstruction, so it tests whether "compactness in a
learned space" beats "reconstructability" on this data.

Two collapse safeguards from the original formulation are kept: the network
has no bias terms and no bounded activations that could map everything to a
constant, and the centre is fixed from an initial forward pass rather than
being learned jointly.
"""

from pathlib import Path

import numpy as np
import torch
from torch import nn

from src.models.base import AnomalyModel


class _SVDDNet(nn.Module):
    def __init__(self, n_features: int, hidden_dim: int, rep_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden_dim, bias=False),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_dim, rep_dim, bias=False),
        )

    def forward(self, x):
        return self.net(x)


class DeepSVDDModel(AnomalyModel):
    name = "deep_svdd"

    def __init__(
        self,
        n_features: int = 29,
        hidden_dim: int = 32,
        rep_dim: int = 12,
        epochs: int = 30,
        batch_size: int = 512,
        lr: float = 1e-3,
        weight_decay: float = 1e-5,
        seed: int = 42,
    ):
        self._params = {
            "n_features": n_features,
            "hidden_dim": hidden_dim,
            "rep_dim": rep_dim,
            "epochs": epochs,
            "batch_size": batch_size,
            "lr": lr,
            "weight_decay": weight_decay,
            "seed": seed,
        }
        self._net = _SVDDNet(n_features, hidden_dim, rep_dim)
        self._center: torch.Tensor | None = None

    def _init_center(self, data: torch.Tensor, eps: float = 0.1) -> torch.Tensor:
        """Centre = mean embedding of the untrained network; coordinates too
        close to zero are pushed away, otherwise they can be trivially matched
        by driving the corresponding weights to zero (hypersphere collapse)."""
        with torch.no_grad():
            c = self._net(data).mean(dim=0)
        c[(c.abs() < eps) & (c < 0)] = -eps
        c[(c.abs() < eps) & (c >= 0)] = eps
        return c

    def fit(self, X: np.ndarray) -> "DeepSVDDModel":
        p = self._params
        torch.manual_seed(p["seed"])
        self._net = _SVDDNet(p["n_features"], p["hidden_dim"], p["rep_dim"])
        data = torch.from_numpy(X.astype(np.float32))
        self._center = self._init_center(data)
        opt = torch.optim.Adam(self._net.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        gen = torch.Generator().manual_seed(p["seed"])
        self._net.train()
        for _ in range(p["epochs"]):
            perm = torch.randperm(len(data), generator=gen)
            for start in range(0, len(data), p["batch_size"]):
                batch = data[perm[start : start + p["batch_size"]]]
                opt.zero_grad()
                loss = ((self._net(batch) - self._center) ** 2).sum(dim=1).mean()
                loss.backward()
                opt.step()
        self._net.eval()
        return self

    @torch.no_grad()
    def score(self, X: np.ndarray) -> np.ndarray:
        self._net.eval()
        data = torch.from_numpy(X.astype(np.float32))
        return ((self._net(data) - self._center) ** 2).sum(dim=1).numpy()

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "params": self._params,
                "state_dict": self._net.state_dict(),
                "center": self._center,
            },
            path,
        )

    @classmethod
    def load(cls, path: Path | str) -> "DeepSVDDModel":
        payload = torch.load(path, weights_only=True)
        obj = cls(**payload["params"])
        obj._net.load_state_dict(payload["state_dict"])
        obj._center = payload["center"]
        obj._net.eval()
        return obj

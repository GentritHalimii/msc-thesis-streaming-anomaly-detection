"""Ensembles over the fitted unsupervised members (IF + AE + OCSVM).

Two variants, both leakage-free — every normalization statistic and vote
threshold comes from TRAINING scores:

- avg:  z-normalize each member's scores with its train-score mean/std,
        then average. A proper continuous ranking.
- vote: each member votes via its own train-percentile threshold; the
        ensemble score is the fraction of members voting anomalous. The
        deployment threshold is the majority rule (>= 0.5); as a *ranking*
        for AP/ROC it is coarse (4 distinct values) by construction.

The LR reference is deliberately excluded: mixing a supervised model into
the ensemble would break the unsupervised framing.
"""

from pathlib import Path

import joblib
import numpy as np

from src.models.base import AnomalyModel

MAJORITY_THRESHOLD = 0.5


class EnsembleModel(AnomalyModel):
    def __init__(
        self,
        mode: str,  # "avg" | "vote"
        member_names: list[str],
        train_means: dict[str, float],
        train_stds: dict[str, float],
        member_thresholds: dict[str, float],
        members: dict[str, AnomalyModel],
    ):
        if mode not in ("avg", "vote"):
            raise ValueError(f"unknown ensemble mode: {mode}")
        self.name = f"ensemble_{mode}"
        self._mode = mode
        self._member_names = member_names
        self._means = train_means
        self._stds = train_stds
        self._thresholds = member_thresholds
        self._members = members

    def fit(self, X: np.ndarray) -> "EnsembleModel":
        raise NotImplementedError(
            "ensembles are built from already-fitted members (see build_ensembles below)"
        )

    def combine(self, member_scores: dict[str, np.ndarray]) -> np.ndarray:
        """Combine per-member scores; used both by score() and to derive the
        ensemble's training-score distribution without re-scoring."""
        if self._mode == "avg":
            z = [(member_scores[n] - self._means[n]) / self._stds[n] for n in self._member_names]
            return np.mean(z, axis=0)
        votes = [
            (member_scores[n] >= self._thresholds[n]).astype(float) for n in self._member_names
        ]
        return np.mean(votes, axis=0)

    def score(self, X: np.ndarray) -> np.ndarray:
        return self.combine({n: m.score(X) for n, m in self._members.items()})

    def save(self, path: Path | str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "mode": self._mode,
                "member_names": self._member_names,
                "train_means": self._means,
                "train_stds": self._stds,
                "member_thresholds": self._thresholds,
            },
            path,
        )

    @classmethod
    def load(cls, path: Path | str) -> "EnsembleModel":
        # Members are reloaded from their own artifacts; the ensemble file
        # holds only combination statistics.
        from src.config import load_config
        from src.models.build import load_model

        payload = joblib.load(path)
        cfg = load_config()
        members = {n: load_model(n, cfg) for n in payload["member_names"]}
        return cls(
            mode=payload["mode"],
            member_names=payload["member_names"],
            train_means=payload["train_means"],
            train_stds=payload["train_stds"],
            member_thresholds=payload["member_thresholds"],
            members=members,
        )


def build_ensembles(cfg, scored, contamination) -> dict[str, "EnsembleModel"]:
    """The two fixed combination rules, built from already-fitted members.

    Lives here rather than in an experiment script because two experiments
    need it; it used to sit in the single-split ensemble experiment, which
    made that script an import target for another one.
    """
    from src.evaluation.thresholds import percentile_threshold
    from src.models.build import UNSUPERVISED, load_model

    means = {n: float(scored.train_scores[n].mean()) for n in UNSUPERVISED}
    stds = {n: float(scored.train_scores[n].std()) for n in UNSUPERVISED}
    thresholds = {
        n: percentile_threshold(scored.train_scores[n], contamination) for n in UNSUPERVISED
    }
    members = {n: load_model(n, cfg) for n in UNSUPERVISED}
    return {
        mode: EnsembleModel(
            mode=mode,
            member_names=UNSUPERVISED,
            train_means=means,
            train_stds=stds,
            member_thresholds=thresholds,
            members=members,
        )
        for mode in ("avg", "vote")
    }

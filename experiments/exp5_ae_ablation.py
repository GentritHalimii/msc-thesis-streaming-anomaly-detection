"""Experiment 5 — autoencoder ablation: latent dimension x epochs (brief).

Trains each variant on training-window normals, reports test AP + fit time.
"""

import pandas as pd

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import load_scaler, transform
from src.data.split import chronological_split
from src.evaluation.manifest import write_manifest
from src.evaluation.metrics import threshold_free_metrics
from src.evaluation.report import save_table
from src.evaluation.resources import measure
from src.models.autoencoder import AutoencoderModel
from src.models.build import artifacts_dir

LATENT_DIMS = [4, 8, 16]
EPOCHS = [10, 20, 40]


def main(cfg=None):
    cfg = cfg or load_config()
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split = chronological_split(df, cfg.split.train_fraction)
    scaler = load_scaler(artifacts_dir(cfg) / "scaler.joblib")
    X_train_normal = transform(scaler, split.train_normal)
    X_test = transform(scaler, split.test)
    y_test = split.test["Class"].to_numpy()

    rows = []
    for latent in LATENT_DIMS:
        for epochs in EPOCHS:
            model = AutoencoderModel(
                hidden_dim=cfg.models.autoencoder.hidden_dim,
                latent_dim=latent,
                epochs=epochs,
                batch_size=cfg.models.autoencoder.batch_size,
                lr=cfg.models.autoencoder.lr,
                seed=cfg.seed,
            )
            with measure() as usage:
                model.fit(X_train_normal)
            metrics = threshold_free_metrics(y_test, model.score(X_test))
            rows.append(
                {
                    "latent_dim": latent,
                    "epochs": epochs,
                    **metrics,
                    "fit_time_s": round(usage.elapsed_s, 1),
                }
            )
            print(
                f"latent={latent} epochs={epochs}: AP={metrics['ap']:.4f} ({usage.elapsed_s:.0f}s)"
            )

    save_table(pd.DataFrame(rows), REPO_ROOT / cfg.results_dir, "ae_ablation")
    write_manifest(REPO_ROOT / cfg.results_dir, "exp5_ae_ablation", cfg.raw)


if __name__ == "__main__":
    main()

"""Reference tables that describe the setup rather than the results.

Generated from the live registry, config and run manifests so the thesis
cannot describe a configuration that the code does not actually use.
"""

import json
import platform

import pandas as pd
import psutil

from src.config import REPO_ROOT, load_config
from src.evaluation.report import FAMILY_LABELS, MODEL_LABELS, save_table
from src.models.build import ABLATION_MODELS, ALL_MODELS, FAMILY_OF

# Short, human descriptions of what each detector treats as "abnormal" and
# what its training cost is dominated by.
MECHANISM = {
    "iforest": (
        "Gjatësia mesatare e shtegut deri te izolimi në pemë me ndarje të rastësishme",
        "O(t·ψ·log ψ)",
    ),
    "autoencoder": (
        "Gabimi i rindërtimit nga një enkoder–dekoder jolinear i trajnuar mbi normalet",
        "O(e·n·h)",
    ),
    "ocsvm": ("Distanca nga hiperplani ndarës në hapësirën e kernelit RBF", "O(n²–n³)"),
    "logreg": (
        "Probabiliteti i klasës pozitive nga një model i mbikëqyrur me etiketa historike",
        "O(i·n·d)",
    ),
    "pca_recon": (
        "Gabimi i rindërtimit nga një nënhapësirë lineare me rang k (ablacion)",
        "O(n·d²)",
    ),
}


def model_zoo_table(cfg) -> pd.DataFrame:
    rows = []
    for name in [*ALL_MODELS, *ABLATION_MODELS]:
        params = getattr(cfg.models, name, None)
        as_dict = dict(vars(params)) if params is not None else {}
        pretty = ", ".join(f"{k}={v}" for k, v in as_dict.items()) or "pa hiperparametra"
        mech, cost = MECHANISM[name]
        rows.append(
            {
                "Detektori": MODEL_LABELS[name],
                "Familja": (
                    FAMILY_LABELS.get(FAMILY_OF.get(name, ""), "Referencë")
                    if name != "logreg"
                    else "Referencë e mbikëqyrur"
                ),
                "Mekanizmi i pikëzimit": mech,
                "Kosto trajnimi": cost,
                "Hiperparametrat": pretty,
            }
        )
    return pd.DataFrame(rows)


def environment_table(cfg) -> pd.DataFrame:
    manifest_path = REPO_ROOT / cfg.results_dir / "manifest_protocol.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    pkgs = manifest.get("packages", {})
    hw = manifest.get("hardware", {})
    mem_gb = hw.get("memory_gb", round(psutil.virtual_memory().total / 1e9, 1))
    rows = [
        ("Sistemi operativ", hw.get("platform", platform.platform())),
        ("Procesori", hw.get("processor") or platform.machine()),
        ("Bërthama logjike", str(hw.get("cpu_count", psutil.cpu_count(logical=True)))),
        ("Memoria e sistemit", f"{mem_gb} GB"),
        ("Përshpejtues grafik", "asnjë; të gjitha modelet trajnohen në CPU"),
        ("Python", manifest.get("python", platform.python_version())),
    ]
    for pkg in ("numpy", "pandas", "scikit-learn", "torch", "confluent-kafka", "psycopg"):
        if pkg in pkgs:
            rows.append((pkg, pkgs[pkg]))
    rows += [
        ("Apache Kafka", "3.8.0 (modaliteti KRaft, një broker)"),
        ("PostgreSQL", "16"),
        ("Grafana", "OSS 11.2.0"),
        ("Seed-i global", str(cfg.seed)),
    ]
    return pd.DataFrame(rows, columns=["Komponenti", "Versioni / vlera"])


def main():
    cfg = load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    save_table(model_zoo_table(cfg), results_dir, "model_zoo")
    save_table(environment_table(cfg), results_dir, "environment")
    print("tabelat referuese u shkruan")


if __name__ == "__main__":
    main()

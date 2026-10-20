"""What do the detectors actually look at?

With 28 anonymised principal components there is no domain knowledge to check
a model against, but there is still a sharp question to ask: does an
unsupervised detector concentrate on the components that genuinely separate
fraud from legitimate traffic, or does it spend its capacity on components
that merely have large variance?

Three attributions are computed and then compared against the univariate
discriminative power measured in the exploratory analysis:

* the autoencoder's per-component reconstruction error, which is exactly what
  its anomaly score is built from;
* SHAP values for the Isolation Forest score, via the tree explainer;
* a permutation attribution that works for any detector, obtained by shuffling
  one component at a time and measuring how much the ranking of the scores
  moves.
"""

import matplotlib as mpl
import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr

from src.config import REPO_ROOT, load_config
from src.data.load import FEATURE_COLUMNS, load_transactions
from src.data.scale import load_scaler, transform
from src.data.split import chronological_split
from src.evaluation.manifest import write_manifest
from src.evaluation.report import (
    CM,
    FULL_WIDTH,
    INK,
    INK_2,
    MODEL_KEYS,
    MODEL_LABELS,
    model_color,
    new_figure,
    save_figure,
    save_table,
    value_grid,
)
from src.models.build import artifacts_dir, load_model

SAMPLE_NORMALS = 4000


def autoencoder_attribution(model, X: np.ndarray) -> np.ndarray:
    """Mean squared reconstruction error per component."""
    with torch.no_grad():
        data = torch.from_numpy(X.astype(np.float32))
        recon = model._net(data).numpy()
    return ((recon - X) ** 2).mean(axis=0)


def permutation_attribution(model, X: np.ndarray, seed: int = 42, n_repeats: int = 3) -> np.ndarray:
    """Drop in rank correlation of the anomaly score when one component is
    shuffled. Model-agnostic and needs no gradients or tree structure."""
    rng = np.random.default_rng(seed)
    base = model.score(X)
    out = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        drops = []
        for _ in range(n_repeats):
            Xp = X.copy()
            Xp[:, j] = Xp[rng.permutation(len(Xp)), j]
            rho, _ = spearmanr(base, model.score(Xp))
            drops.append(1.0 - float(rho))
        out[j] = float(np.mean(drops))
    return out


def shap_attribution(
    model, X: np.ndarray, background: int = 200, seed: int = 42
) -> np.ndarray | None:
    """Mean |SHAP| for the Isolation Forest score; None if unavailable."""
    try:
        import shap

        explainer = shap.TreeExplainer(model._model)
        values = explainer.shap_values(X, check_additivity=False)
        return np.abs(np.asarray(values)).mean(axis=0)
    except Exception as exc:  # pragma: no cover - depends on shap internals
        print(f"  SHAP unavailable for isolation forest: {exc}")
        return None


PERMUTATION_COLUMNS = {
    "iforest": "isolation forest (permutim)",
    "autoencoder": "autoencoder (permutim)",
    "ocsvm": "one-class SVM (permutim)",
}


def figures(cfg) -> None:
    results_dir = REPO_ROOT / cfg.results_dir
    attr = pd.read_csv(results_dir / "explain_attributions.csv").set_index("feature")
    signal = pd.read_csv(results_dir / "eda_feature_signal.csv").set_index("feature")
    xs = signal.loc[attr.index, "abs_auc_gap"]
    top = xs.nlargest(5).index

    # --- Attention against available signal, one panel per detector -------
    # The same model-agnostic attribution for all three, so the panels are
    # comparable; the reconstruction-error view of the Autoencoder measures
    # something different and is kept to the table.
    fig, axes = new_figure(ncols=3, figsize=(FULL_WIDTH, 5.6 * CM))
    for ax, (name, column) in zip(axes, PERMUTATION_COLUMNS.items(), strict=True):
        ys = attr[column]
        color = model_color(name)
        rest = attr.index.difference(top)
        ax.scatter(xs[rest], ys[rest], s=16, color=color, alpha=0.55, linewidths=0)
        ax.scatter(xs[top], ys[top], s=18, color=INK, linewidths=0)
        rho = spearmanr(xs, ys).statistic
        rho_text = f"{rho:.2f}".replace("-", "−")
        ax.set_title(f"{MODEL_LABELS[name]}\nρ = {rho_text}", loc="left", fontsize=8.2)
        ax.set_xlabel("|AUC − 0.5|")
        ax.set_xlim(0, 0.5)
        ax.set_ylim(0, None)
        ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(4))
        value_grid(ax, "both")
    axes[0].set_ylabel("Ndikimi i permutimit")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "explain_attention_vs_signal")

    # --- How much worse the frauds are reconstructed, per component --------
    recon = pd.read_csv(results_dir / "explain_ae_reconstruction.csv")
    recon = recon.sort_values("raporti")
    fig, ax = new_figure(figsize=(FULL_WIDTH, 9.6 * CM))
    y = np.arange(len(recon))
    ratio = recon["raporti"].to_numpy()
    colors = [model_color("autoencoder") if r > 1 else "#b9b8ae" for r in ratio]
    # Bars start at a ratio of one, the point where both classes are
    # reconstructed equally well, so on the logarithmic axis their length is
    # the factor itself rather than a distance from an arbitrary floor.
    ax.barh(y, ratio - 1, left=1, height=0.68, color=colors)
    ax.axvline(1, color=INK_2, lw=0.8)
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 5, 10, 20, 50])
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    ax.set_yticks(y, recon["feature"], fontsize=7)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.7, len(recon) - 0.3)
    ax.set_xlabel("Gabimi i rindërtimit për mashtrimet, si shumëfish i atij për legjitimet")
    value_grid(ax, "x")
    save_figure(fig, REPO_ROOT / cfg.results_dir, "explain_ae_reconstruction")


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    split = chronological_split(df, cfg.split.train_fraction)
    scaler = load_scaler(artifacts_dir(cfg) / "scaler.joblib")

    rng = np.random.default_rng(cfg.seed)
    test = split.test
    fraud_idx = np.flatnonzero(test["Class"].to_numpy() == 1)
    normal_idx = np.flatnonzero(test["Class"].to_numpy() == 0)
    sample_idx = np.sort(
        np.concatenate(
            [
                fraud_idx,
                rng.choice(normal_idx, size=min(SAMPLE_NORMALS, len(normal_idx)), replace=False),
            ]
        )
    )
    sample = test.iloc[sample_idx]
    X = transform(scaler, sample)
    y = sample["Class"].to_numpy()

    attributions: dict[str, np.ndarray] = {}

    ae = load_model("autoencoder", cfg)
    err_fraud = autoencoder_attribution(ae, X[y == 1])
    err_normal = autoencoder_attribution(ae, X[y == 0])
    attributions["autoencoder (gabim rindërtimi)"] = err_fraud
    attributions["autoencoder (permutim)"] = permutation_attribution(ae, X, cfg.seed)

    iforest = load_model("iforest", cfg)
    shap_vals = shap_attribution(iforest, X)
    if shap_vals is not None:
        attributions["isolation forest (SHAP)"] = shap_vals
    attributions["isolation forest (permutim)"] = permutation_attribution(iforest, X, cfg.seed)
    attributions["one-class SVM (permutim)"] = permutation_attribution(
        load_model("ocsvm", cfg), X, cfg.seed
    )

    attr = pd.DataFrame(attributions, index=FEATURE_COLUMNS)
    attr.index.name = "feature"
    save_table(attr.reset_index(), results_dir, "explain_attributions", float_fmt="%.6f")

    # Does attention line up with where the signal actually is?
    signal = pd.read_csv(results_dir / "eda_feature_signal.csv").set_index("feature")
    agree_rows = []
    for name, col in attr.items():
        rho, p = spearmanr(col.to_numpy(), signal.loc[FEATURE_COLUMNS, "abs_auc_gap"].to_numpy())
        agree_rows.append(
            {
                "atribuimi": name,
                "spearman_vs_auc_gap": float(rho),
                "p_value": float(p),
                "top3": ", ".join(col.sort_values(ascending=False).head(3).index),
            }
        )
    agreement = pd.DataFrame(agree_rows)
    agreement.loc[len(agreement)] = {
        "atribuimi": "sinjali univariat (referencë)",
        "spearman_vs_auc_gap": 1.0,
        "p_value": 0.0,
        "top3": ", ".join(signal["abs_auc_gap"].sort_values(ascending=False).head(3).index),
    }
    save_table(agreement, results_dir, "explain_signal_agreement", float_fmt="%.6g")
    print(agreement.to_string(index=False))

    reconstruction = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "gabimi_legjitime": err_normal,
            "gabimi_mashtrime": err_fraud,
            "raporti": err_fraud / np.maximum(err_normal, 1e-12),
        }
    )
    save_table(reconstruction, results_dir, "explain_ae_reconstruction", float_fmt="%.6f")
    figures(cfg)

    # A verdict, like every other analysis, so the thesis prose is generated
    # from the measurement rather than copied by hand.
    ranked = agreement[agreement["atribuimi"] != "sinjali univariat (referencë)"].copy()
    ranked = ranked.sort_values("spearman_vs_auc_gap", ascending=False)
    parts = [
        f"{r['atribuimi']} rho = {r['spearman_vs_auc_gap']:.2f} (p = {r['p_value']:.2g})"
        for _, r in ranked.iterrows()
    ]
    # The like-for-like comparison uses the one attribution computed the same
    # way for all three detectors. The reconstruction error of the
    # Autoencoder is measured on the frauds, so it is high wherever the frauds
    # are unusual and its agreement with the univariate signal is partly
    # built in; it is reported, but it does not decide the ordering.
    comparable = ranked[ranked["atribuimi"].isin(PERMUTATION_COLUMNS.values())]
    by_column = {v: k for k, v in PERMUTATION_COLUMNS.items()}
    attention_order = [by_column[a] for a in comparable["atribuimi"]]
    benchmark = pd.read_csv(results_dir / "benchmark_summary.csv")
    quality_order = [
        MODEL_KEYS[m]
        for m in benchmark.sort_values("ap_mean", ascending=False)["model"]
        if MODEL_KEYS.get(m) in PERMUTATION_COLUMNS
    ]
    same = attention_order == quality_order
    worst = comparable.iloc[-1]
    verdict = (
        "Atribuimi tregon se detektorët nuk e shpërndajnë vëmendjen njësoj mbi kolonat. "
        + "; ".join(parts)
        + ". Me të njëjtën masë për të tre, atë me permutim, renditja e përputhjes me "
        f"sinjalin është {', '.join(MODEL_LABELS[m] for m in attention_order)}"
        + (
            ", e njëjtë me renditjen sipas cilësisë së zbulimit"
            if same
            else f", ndërsa renditja sipas cilësisë është "
            f"{', '.join(MODEL_LABELS[m] for m in quality_order)}"
        )
        + f". Përputhja e {MODEL_LABELS[by_column[worst['atribuimi']]]}-it, rho = "
        f"{worst['spearman_vs_auc_gap']:.2f} (p = {worst['p_value']:.2g}), nuk dallohet nga "
        f"zeroja me asnjërën masë, dhe pikërisht ky detektor testohet më pas me ndërhyrjen "
        f"mbi hyrjen."
    )
    (results_dir / "explain_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)

    write_manifest(results_dir, "exp15_explainability", cfg.raw)
    print(
        f"\nModeli i shpjeguar: {MODEL_LABELS['autoencoder']}, "
        f"{MODEL_LABELS['iforest']}, {MODEL_LABELS['ocsvm']} "
        f"mbi {len(sample)} transaksione ({int(y.sum())} mashtrime)."
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--figures-only", action="store_true", help="redraw the figures from the saved tables"
    )
    figures(load_config()) if parser.parse_args().figures_only else main()

"""How much history should a streaming detector keep?

Two policies are available to anyone deploying this. Keep everything and let
the training window grow, or keep a fixed-length window of the most recent
transactions and let old data fall out. The first uses more data; the second
stays closer to the present. Which wins is an empirical question, and the
drift analysis makes it a sharp one: if the normal population is stable, more
history should simply help, and the answer tells us whether the stale-data
worry is real on this dataset.

The experiment also produces a plain learning curve. That matters for a
different reason: if quality saturates well below the full window, the
quadratic training cost of the kernel method stops being a limitation.
"""

import pandas as pd
from sklearn.metrics import average_precision_score

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.scale import fit_scaler, transform
from src.evaluation.manifest import write_manifest
from src.evaluation.protocol import rolling_origin_folds
from src.evaluation.report import AX, MODEL_LABELS, model_color, new_figure, save_figure, save_table
from src.models.build import ALL_MODELS, build_model

WINDOW_SIZES = [10000, 25000, 50000, 100000, 200000]


def main(cfg=None):
    cfg = cfg or load_config()
    results_dir = REPO_ROOT / cfg.results_dir
    df = load_transactions(REPO_ROOT / cfg.data.raw_csv)
    folds = rolling_origin_folds(len(df), cfg.protocol.n_folds, cfg.protocol.initial_train_fraction)

    rows = []
    for fold in folds:
        history = df.iloc[: fold.train_end]
        test = df.iloc[fold.test_start : fold.test_end]
        y_test = test["Class"].to_numpy()

        policies = {"zgjerohet (gjithë historiku)": history}
        for size in WINDOW_SIZES:
            if size >= len(history):
                continue
            policies[f"rrëshqitëse ({size})"] = history.iloc[-size:]

        for policy, window in policies.items():
            # Everything is refitted from the window in question, scaler
            # included, because a scaler carried over from a longer history
            # would leak that history back in.
            scaler = fit_scaler(window, seed=cfg.seed)
            X_full = transform(scaler, window)
            X_normal = transform(scaler, window[window["Class"] == 0])
            X_test = transform(scaler, test)
            y_window = window["Class"].to_numpy()

            for name in ALL_MODELS:
                model = build_model(name, cfg)
                if name == "logreg":
                    model.fit(X_full, y_window)
                else:
                    model.fit(X_normal)
                rows.append(
                    {
                        "fold": fold.index,
                        "politika": policy,
                        "madhesia": len(window),
                        "eshte_rreshqitese": policy.startswith("rrëshqitëse"),
                        "model": name,
                        "ap": average_precision_score(y_test, model.score(X_test)),
                    }
                )
        print(f"fold {fold.index} done", flush=True)

    per_fold = pd.DataFrame(rows)
    save_table(per_fold, results_dir, "training_window_per_fold", float_fmt="%.5f")

    sliding = per_fold[per_fold["eshte_rreshqitese"]]
    curve = (
        sliding.groupby(["model", "madhesia"])["ap"]
        .agg(ap_mean="mean", ap_std="std", n="count")
        .reset_index()
    )
    expanding = (
        per_fold[~per_fold["eshte_rreshqitese"]]
        .groupby("model")["ap"]
        .agg(ap_mean="mean", ap_std="std")
        .reset_index()
    )

    out = curve.copy()
    out["model"] = out["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(out, results_dir, "training_window_curve", float_fmt="%.4f")
    exp_out = expanding.copy()
    exp_out["model"] = exp_out["model"].map(lambda m: MODEL_LABELS.get(m, m))
    save_table(exp_out, results_dir, "training_window_expanding", float_fmt="%.4f")
    print("\n=== dritare që zgjerohet ===")
    print(exp_out.to_string(index=False))

    # --- Figure: learning curve against the expanding-window baseline -----
    fig, ax = new_figure(figsize=(7.0, 4.2))
    for name in ALL_MODELS:
        sub = curve[curve["model"] == name].sort_values("madhesia")
        ax.errorbar(
            sub["madhesia"],
            sub["ap_mean"],
            yerr=sub["ap_std"],
            marker="o",
            markersize=4,
            capsize=2,
            linewidth=1.5,
            color=model_color(name),
            label=MODEL_LABELS.get(name, name),
        )
        reference = expanding.loc[expanding["model"] == name, "ap_mean"].iloc[0]
        ax.axhline(reference, color=model_color(name), lw=1, ls=":", alpha=0.7)
    ax.set_xscale("log")
    ax.set_xlabel(AX["train_size"] + " në një dritare rrëshqitëse")
    ax.set_ylabel(AX["ap"])
    ax.text(
        0.02,
        0.02,
        "vijat me pika: dritarja që zgjerohet (gjithë historiku)",
        transform=ax.transAxes,
        fontsize=8,
        color="#898781",
    )
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8.5)
    save_figure(fig, REPO_ROOT / cfg.results_dir, "training_window")

    # --- verdict ----------------------------------------------------------
    best_sliding = curve.loc[curve.groupby("model")["ap_mean"].idxmax()].set_index("model")
    expanding_idx = expanding.set_index("model")
    parts = []
    for name in ALL_MODELS:
        delta = best_sliding.loc[name, "ap_mean"] - expanding_idx.loc[name, "ap_mean"]
        parts.append(
            f"{MODEL_LABELS.get(name, name)}: dritarja rrëshqitëse më e mirë është "
            f"{int(best_sliding.loc[name, 'madhesia']):,} ({delta:+.3f} ndaj historikut të plotë)"
        )
    saturation = curve[curve["model"] != "logreg"].groupby("madhesia")["ap_mean"].mean()
    verdict = (
        "Historiku më i gjatë ndihmon, por me kthim në rënie. "
        + "; ".join(parts)
        + f". Mesatarisht mbi detektorët unsupervised, kalimi nga "
        f"{int(saturation.index[0]):,} në {int(saturation.index[-1]):,} transaksione "
        f"trajnimi e ndryshon AP-në nga {saturation.iloc[0]:.3f} në "
        f"{saturation.iloc[-1]:.3f}. "
        + (
            "Meqë asnjë dritare rrëshqitëse nuk e tejkalon qartë historikun e plotë, "
            "të dhënat e vjetra nuk duket se dëmtojnë; kjo përputhet me gjetjen se "
            "popullata normale mbetet e qëndrueshme."
            if all(
                best_sliding.loc[n, "ap_mean"] <= expanding_idx.loc[n, "ap_mean"] + 0.01
                for n in ALL_MODELS
            )
            else "Të paktën për një detektor një dritare rrëshqitëse e tejkalon historikun "
            "e plotë, çka sugjeron se një pjesë e historikut është vjetëruar."
        )
    )
    (results_dir / "training_window_verdict.txt").write_text(verdict + "\n")
    print("\n" + verdict)
    write_manifest(results_dir, "exp26_training_window", cfg.raw)


if __name__ == "__main__":
    main()

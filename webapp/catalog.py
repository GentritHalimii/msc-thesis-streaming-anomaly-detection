"""What can be re-run, what it costs, and what it produces.

Every runnable unit of the study is declared here once. The run console lists
these, the result sections link back to them, and the job runner will execute
nothing that is not in this table: a request carries a catalogue id, never a
command line.

`minutes` is a measured order of magnitude on the reference machine, not a
promise. It exists so that nobody starts a seventy-minute refit expecting a
progress bar to finish during a meeting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Experiment:
    id: str
    title: str
    question: str
    group: str
    minutes: int
    module: str
    args: tuple[str, ...] = ()
    thesis: str = ""
    verdict: str | None = None
    tables: tuple[str, ...] = ()
    figures: tuple[str, ...] = ()
    manifest: str | None = None
    # Three helpers write figures or a document but no manifest, so their
    # absence from the provenance list is expected rather than a missing run.
    writes_manifest: bool = True
    needs: tuple[str, ...] = ()
    docker: bool = False
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "title": self.title,
            "question": self.question,
            "group": self.group,
            "minutes": self.minutes,
            "command": " ".join(["python", "-m", self.module, *self.args]),
            "thesis": self.thesis,
            "verdict": self.verdict,
            "tables": list(self.tables),
            "figures": list(self.figures),
            "manifest": self.manifest or self.module.rsplit(".", 1)[-1],
            "writes_manifest": self.writes_manifest,
            "needs": list(self.needs),
            "docker": self.docker,
            "note": self.note,
        }
        return data


@dataclass(frozen=True)
class Group:
    id: str
    title: str
    subtitle: str
    members: tuple[str, ...] = field(default_factory=tuple)


# --- groups, in the order the pipeline runs them ---------------------------

GROUPS: tuple[Group, ...] = (
    Group(
        "baza",
        "Baza",
        "Përshtatja e modeleve dhe matricat e pikëve mbi të cilat mbështetet çdo analizë tjetër.",
    ),
    Group(
        "vleresimi",
        "Vlerësimi",
        "Tabelat dhe figurat që lexohen nga pikët e ruajtura. Minuta, jo orë.",
    ),
    Group(
        "thellesia",
        "Studimet e thelluara",
        "Secili ripërshtat modelet nga fillimi. Orë, jo minuta.",
    ),
    Group(
        "akordimi",
        "Akordimi",
        "Kërkimi i hiperparametrave dhe ri-ekzekutimi i protokollit me to.",
    ),
    Group(
        "rrjedha",
        "Rrjedha",
        "Ekzekutimet mbi broker-in e vërtetë Kafka. Kërkojnë grumbullin docker.",
    ),
    Group(
        "punimi",
        "Punimi",
        "Gjenerimi i dokumentit nga rezultatet e ruajtura.",
    ),
)


# --- the catalogue ---------------------------------------------------------

_ALL: tuple[Experiment, ...] = (
    # ---------------------------------------------------------------- baza
    Experiment(
        id="train_models",
        title="Përshtatja mbi prerjen 70/30",
        question="Si sillen modelet mbi një prerje të vetme kronologjike?",
        group="baza",
        minutes=2,
        module="experiments.train_models",
        thesis="§4.2.1",
        tables=("split_summary",),
        note="Shkruan artefaktet e modeleve që i lexojnë exp1, exp2, exp3, exp6 dhe exp7.",
    ),
    Experiment(
        id="run_protocol",
        title="Protokolli rolling-origin",
        question="A qëndron renditja e algoritmeve nëpër tetë pika kohore prerjeje?",
        group="baza",
        minutes=6,
        module="experiments.run_protocol",
        thesis="§4.2.2",
        tables=("fold_summary",),
        manifest="protocol",
        note="Hapi i shtrenjtë i bazës. Shkruan results/folds/*.npz, burimin e çdo analize.",
    ),
    Experiment(
        id="make_diagrams",
        title="Diagramet konceptuale",
        question="Si duket arkitektura dhe ku mund të rrjedhë informacioni?",
        group="baza",
        minutes=1,
        module="experiments.make_diagrams",
        thesis="§3.6, §4.9",
        figures=("diagram_architecture", "diagram_protocol", "diagram_leakage"),
        writes_manifest=False,
    ),
    Experiment(
        id="make_reference_tables",
        title="Tabelat referuese",
        question="Cili është mjedisi dhe cilat janë vetitë e detektorëve?",
        group="baza",
        minutes=1,
        module="experiments.make_reference_tables",
        thesis="§4.4.1, §4.10",
        tables=("environment", "model_zoo"),
        writes_manifest=False,
    ),
    # ----------------------------------------------------------- vleresimi
    Experiment(
        id="exp0_eda",
        title="Analiza eksploruese",
        question="Çfarë përmban dataset-i dhe sa sinjal ka në secilën veçori?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp0_eda",
        thesis="§4.1.2",
        tables=("eda_overview", "eda_feature_signal"),
        figures=(
            "eda_volume_and_fraud",
            "eda_hourly_rate",
            "eda_amounts",
            "eda_correlation",
            "eda_feature_signal",
        ),
    ),
    Experiment(
        id="exp1_main_table",
        title="Rezultatet e prerjes së vetme",
        question="Çfarë jep secili model mbi ndarjen 70/30?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp1_main_table",
        thesis="Shtojca D",
        tables=("metrics_main",),
        needs=("train_models",),
    ),
    Experiment(
        id="exp2_contamination_sweep",
        title="Ndjeshmëria ndaj kontaminimit",
        question="Sa varet pika e funksionimit nga kontaminimi i supozuar?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp2_contamination_sweep",
        thesis="§5.2.4",
        tables=("contamination_sweep",),
        figures=("contamination_sweep",),
        needs=("train_models",),
    ),
    Experiment(
        id="exp3_curves",
        title="Kurbat precision-recall dhe ROC",
        question="Si duken kurbat e plota, jo vetëm përmbledhjet e tyre?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp3_curves",
        thesis="Shtojca D",
        figures=("curves_pr_roc",),
        needs=("train_models",),
    ),
    Experiment(
        id="exp6_shuffled_split",
        title="Kostoja e ndershmërisë metodologjike",
        question="Sa e fryn rezultatin një ndarje e rastësishme në vend të asaj kronologjike?",
        group="vleresimi",
        minutes=3,
        module="experiments.exp6_shuffled_split",
        thesis="§5.6",
        tables=("shuffled_split_comparison",),
        needs=("train_models",),
    ),
    Experiment(
        id="exp10_benchmark",
        title="Tabela kryesore mbi tetë fold-e",
        question="Cili detektor ofron balancën më të mirë mes cilësisë dhe kostos?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp10_benchmark",
        thesis="§5.2.1",
        tables=("benchmark_summary", "benchmark_per_fold"),
        figures=("benchmark_ap_ranking", "benchmark_ap_per_fold", "benchmark_quality_cost"),
        needs=("run_protocol",),
    ),
    Experiment(
        id="exp11_significance",
        title="Testet statistikore",
        question="A janë dallimet mes detektorëve më të mëdha se zhurma nëpër fold-e?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp11_significance",
        thesis="§5.2.2",
        tables=("significance_omnibus", "significance_wilcoxon", "significance_avg_ranks"),
        figures=("significance_cd_core",),
        needs=("exp10_benchmark",),
    ),
    Experiment(
        id="exp7_bootstrap_ci",
        title="Intervalet e besimit bootstrap",
        question="Sa e pasigurt është vlera mbi një bashkësi të vetme testimi?",
        group="vleresimi",
        minutes=2,
        module="experiments.exp7_bootstrap_ci",
        thesis="Shtojca D",
        tables=("bootstrap_ci", "bootstrap_pairwise"),
        needs=("train_models",),
    ),
    Experiment(
        id="exp12_ensembles",
        title="Ansamblet e detektorëve",
        question="A e tejkalon kombinimi modelin më të mirë individual?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp12_ensembles",
        thesis="§5.3",
        verdict="ensemble",
        tables=("ensemble_summary", "ensemble_rank_correlation"),
        figures=("ensemble_vs_single", "ensemble_rank_correlation", "pr_curves_with_ensembles"),
        needs=("run_protocol",),
    ),
    Experiment(
        id="exp13_drift",
        title="Dekompozimi i zhvendosjes",
        question="Cila popullatë lëviz me kohën: ajo legjitime apo ajo e mashtrimeve?",
        group="vleresimi",
        minutes=2,
        module="experiments.exp13_drift",
        thesis="Shtojca E",
        verdict="drift",
        tables=("drift_per_fold", "drift_per_feature", "drift_page_hinkley"),
        figures=("drift_psi_decomposition", "drift_separability"),
        needs=("run_protocol",),
    ),
    Experiment(
        id="exp14_alert_budget",
        title="Vlerësimi në buxhet alarmesh",
        question="Çfarë kapet kur shqyrtohen vetëm k alarme për bllok?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp14_alert_budget",
        thesis="§5.2.4",
        verdict="budget",
        tables=("budget_summary", "budget_per_fold"),
        figures=("budget_recall", "budget_savings", "budget_amount_recall"),
        needs=("run_protocol",),
    ),
    Experiment(
        id="exp16_adaptive_threshold",
        title="Pragu adaptiv me dritare rrëshqitëse",
        question="A e stabilizon ngarkesën hetimore një prag që ndjek shpërndarjen?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp16_adaptive_threshold",
        thesis="§5.2.4",
        verdict="adaptive_threshold",
        tables=("adaptive_threshold_summary", "adaptive_threshold_per_fold"),
        figures=("adaptive_alert_rate", "adaptive_tradeoff"),
        needs=("run_protocol",),
    ),
    Experiment(
        id="exp17_protocol_comparison",
        title="Krahasimi i protokolleve",
        question="Sa peshojnë vendimet e protokollit krahasuar me zgjedhjen e algoritmit?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp17_protocol_comparison",
        thesis="§5.6",
        verdict="protocol",
        tables=("protocol_comparison", "protocol_inflation"),
        figures=("protocol_comparison",),
        needs=("exp10_benchmark", "exp6_shuffled_split"),
    ),
    Experiment(
        id="exp27_error_analysis",
        title="Analiza e gabimeve në nivel transaksioni",
        question="Cilat mashtrime nuk i kap asnjë detektor, dhe pse?",
        group="vleresimi",
        minutes=1,
        module="experiments.exp27_error_analysis",
        thesis="§5.3",
        verdict="error_analysis",
        tables=("error_analysis_coverage", "error_analysis_dark_set", "error_analysis_overlap"),
        figures=("error_analysis",),
        needs=("run_protocol",),
    ),
    Experiment(
        id="make_rq_summary",
        title="Përgjigjet e pyetjeve hulumtuese",
        question="Cila është përgjigjja e drejtpërdrejtë për secilën pyetje hulumtuese?",
        group="vleresimi",
        minutes=1,
        module="experiments.make_rq_summary",
        thesis="§6.1",
        tables=("rq_summary",),
        needs=("exp10_benchmark", "exp12_ensembles", "latency_report"),
    ),
    # ----------------------------------------------------------- thellesia
    Experiment(
        id="exp20_data_geometry",
        title="Distancat nga fqinjët legjitimë",
        question="Sa larg klasës legjitime ndodhen mashtrimet?",
        group="thellesia",
        minutes=4,
        module="experiments.exp20_data_geometry",
        thesis="§4.1.2",
        verdict="geometry",
        tables=("geometry_summary", "geometry_feature_power"),
        figures=("geometry_knn_distance", "geometry_cost_to_catch", "geometry_hardness"),
    ),
    Experiment(
        id="exp21_scaling",
        title="Paraprocesimi si variabël",
        question="Sa peshon zgjedhja e transformimit krahasuar me zgjedhjen e algoritmit?",
        group="thellesia",
        minutes=16,
        module="experiments.exp21_scaling",
        thesis="§5.4.1",
        verdict="scaling",
        tables=(
            "scaling_summary",
            "scaling_significance",
            "scaling_prequential",
            "scaling_per_fold",
        ),
        figures=("scaling_effect",),
    ),
    Experiment(
        id="exp22_iforest_deep",
        title="Isolation Forest: ku shkon kapaciteti",
        question="A është zgjedhja uniforme e dimensionit të ndarjes shkaku i dobësisë?",
        group="thellesia",
        minutes=12,
        module="experiments.exp22_iforest_deep",
        thesis="§5.5.1",
        verdict="iforest",
        tables=(
            "iforest_surface",
            "iforest_rotation",
            "iforest_split_usage",
            "iforest_max_features_summary",
        ),
        figures=("iforest_surface", "iforest_capacity"),
    ),
    Experiment(
        id="exp23_autoencoder_deep",
        title="Autoencoder: arkitektura, humbja dhe trajnimi",
        question="Cila levë e arkitekturës dhe e trajnimit e lëviz vërtet rezultatin?",
        group="thellesia",
        minutes=70,
        module="experiments.exp23_autoencoder_deep",
        thesis="§5.5.2",
        verdict="autoencoder",
        tables=("autoencoder_studies_tidy", "autoencoder_studies_per_fold"),
        figures=("autoencoder_architecture", "autoencoder_vs_linear", "autoencoder_training"),
        note="Ekzekutimi më i gjatë i studimit. Ka edhe rindërtim të shpejtë nga të dhënat e "
        "ruajtura, pa ripërshtatje.",
    ),
    Experiment(
        id="exp23_autoencoder_rebuild",
        title="Autoencoder: rindërtim nga të dhënat e ruajtura",
        question="Si duken tabelat dhe figurat e Autoencoder-it pa ripërshtatur asgjë?",
        group="thellesia",
        minutes=2,
        module="experiments.exp23_autoencoder_deep",
        args=("--from-saved",),
        thesis="§5.5.2",
        verdict="autoencoder",
        manifest="exp23_autoencoder_deep",
        tables=("autoencoder_studies_tidy",),
        figures=("autoencoder_architecture", "autoencoder_vs_linear", "autoencoder_training"),
        needs=("exp23_autoencoder_deep",),
    ),
    Experiment(
        id="exp24_ocsvm_deep",
        title="One-Class SVM: kerneli, nu dhe çmimi i të dhënave",
        question="Sa kushton cilësia kur kostoja e kernelit rritet kuadratikisht?",
        group="thellesia",
        minutes=55,
        module="experiments.exp24_ocsvm_deep",
        thesis="§5.5.3",
        verdict="ocsvm",
        tables=("ocsvm_kernels", "ocsvm_surface", "ocsvm_learning_curve"),
        figures=("ocsvm_surface", "ocsvm_learning_curve"),
    ),
    Experiment(
        id="exp24_ocsvm_rebuild",
        title="One-Class SVM: rindërtim nga të dhënat e ruajtura",
        question="Si duken tabelat dhe figurat e One-Class SVM-së pa ripërshtatur asgjë?",
        group="thellesia",
        minutes=1,
        module="experiments.exp24_ocsvm_deep",
        args=("--from-saved",),
        thesis="§5.5.3",
        verdict="ocsvm",
        manifest="exp24_ocsvm_deep",
        tables=("ocsvm_kernels", "ocsvm_surface", "ocsvm_learning_curve"),
        figures=("ocsvm_surface", "ocsvm_learning_curve"),
        needs=("exp24_ocsvm_deep",),
    ),
    Experiment(
        id="exp28_best_effort",
        title="Secili detektor në kapacitetin e vet më të mirë",
        question="Sa mbetet nga renditja kur asgjë nuk lihet në vlerën e parazgjedhur?",
        group="thellesia",
        minutes=60,
        module="experiments.exp28_best_effort",
        thesis="§5.4.3",
        verdict="best_effort",
        tables=("best_effort", "best_effort_interaction", "best_effort_per_fold"),
        figures=("best_effort",),
        needs=("exp9_tuning", "exp21_scaling"),
    ),
    Experiment(
        id="exp28_best_effort_rebuild",
        title="Dizajni faktorial: rindërtim nga të dhënat e ruajtura",
        question="Si duket dizajni dy-nga-dy pa ripërshtatur asgjë?",
        group="thellesia",
        minutes=1,
        module="experiments.exp28_best_effort",
        args=("--from-saved",),
        thesis="§5.4.3",
        verdict="best_effort",
        manifest="exp28_best_effort",
        tables=("best_effort", "best_effort_interaction"),
        figures=("best_effort",),
        needs=("exp28_best_effort",),
    ),
    # ------------------------------------------------------------ akordimi
    Experiment(
        id="exp9_tuning",
        title="Kërkimi i hiperparametrave",
        question="Cili konfigurim fiton mbi një ndarje të brendshme kohore, pa parë testin?",
        group="akordimi",
        minutes=50,
        module="experiments.exp9_tuning",
        thesis="§4.7",
        tables=("tuning_summary", "tuning_history"),
        needs=("train_models",),
    ),
    Experiment(
        id="run_protocol_tuned",
        title="Protokolli me hiperparametrat e akorduar",
        question="Si ndryshon renditja kur të tre akordohen njësoj?",
        group="akordimi",
        minutes=12,
        module="experiments.run_protocol",
        args=("--tuned",),
        thesis="§5.4.2",
        manifest="protocol_tuned",
        needs=("exp9_tuning",),
    ),
    Experiment(
        id="exp18_tuning_effect",
        title="Efekti i akordimit",
        question="Sa fiton secili detektor, dhe a mbijeton renditja?",
        group="akordimi",
        minutes=1,
        module="experiments.exp18_tuning_effect",
        thesis="§5.4.2",
        verdict="tuning",
        tables=("tuning_effect", "tuning_effect_wilcoxon"),
        figures=("tuning_effect", "tuning_transfer"),
        needs=("run_protocol_tuned",),
    ),
    Experiment(
        id="exp12_ensembles_tuned",
        title="Ansamblet me hiperparametra të akorduar",
        question="A ndryshon përfundimi negativ i ansamblit kur anëtarët akordohen?",
        group="akordimi",
        minutes=1,
        module="experiments.exp12_ensembles",
        args=("--tuned",),
        thesis="§5.3",
        verdict="ensemble_verdict_tuned",
        manifest="exp12_ensembles_tuned",
        tables=("ensemble_summary_tuned",),
        needs=("run_protocol_tuned",),
    ),
    # -------------------------------------------------------------- rrjedha
    Experiment(
        id="stream_sweep",
        title="Skanimi i vonesës",
        question="A mbetet vonesa mesatare nën një sekondë në çdo ritëm të testuar?",
        group="rrjedha",
        minutes=35,
        module="experiments.run_streaming",
        args=("--models", "iforest", "autoencoder", "ocsvm", "logreg"),
        thesis="§5.1",
        manifest="run_streaming",
        docker=True,
        note="Katër modele mbi tri ritme. Kërkon Kafka-n në ekzekutim.",
    ),
    Experiment(
        id="stream_adaptive",
        title="Rrjedha me prag adaptiv",
        question="Sa kushton operacionalisht pragu adaptiv brenda consumer-it?",
        group="rrjedha",
        minutes=6,
        module="experiments.run_streaming",
        args=("--models", "iforest", "autoencoder", "ocsvm", "--rates", "200", "--adaptive"),
        thesis="§5.1",
        manifest="run_streaming",
        docker=True,
    ),
    Experiment(
        id="stream_store",
        title="Rrjedhë me persistim në PostgreSQL",
        question="A qarkullojnë të dhënat deri te baza dhe paneli Grafana?",
        group="rrjedha",
        minutes=3,
        module="experiments.run_streaming",
        args=("--models", "iforest", "--rates", "200", "--store", "--label", "demo"),
        thesis="§4.9.3",
        manifest="run_streaming",
        docker=True,
        note="Ushqen panelin Grafana me të dhëna të freskëta.",
    ),
    Experiment(
        id="latency_report",
        title="Raporti i vonesës",
        question="Çfarë thonë të gjitha ekzekutimet e rrjedhës së bashku?",
        group="rrjedha",
        minutes=1,
        module="experiments.latency_report",
        thesis="§5.1",
        tables=("latency_summary",),
        figures=("latency_vs_rate",),
        needs=("stream_sweep",),
    ),
    # --------------------------------------------------------------- punimi
    Experiment(
        id="thesis_build",
        title="Ndërtimi i punimit",
        question="Si duket dokumenti i gjeneruar nga gjendja aktuale e rezultateve?",
        group="punimi",
        minutes=3,
        module="thesis.build_thesis",
        thesis="",
        note="Dy kalime: i pari shkruan dokumentin, i dyti zgjidh numrat e faqeve.",
        writes_manifest=False,
    ),
)

EXPERIMENTS: dict[str, Experiment] = {e.id: e for e in _ALL}


# --- batches ---------------------------------------------------------------

BATCHES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "evaluate": (
        "Rigjenero vlerësimin",
        "Çdo tabelë dhe figurë që lexohet nga pikët e ruajtura. Rreth 15 minuta.",
        (
            "exp0_eda",
            "make_diagrams",
            "make_reference_tables",
            "exp1_main_table",
            "exp2_contamination_sweep",
            "exp3_curves",
            "exp6_shuffled_split",
            "exp10_benchmark",
            "exp11_significance",
            "exp7_bootstrap_ci",
            "exp12_ensembles",
            "exp13_drift",
            "exp14_alert_budget",
            "exp16_adaptive_threshold",
            "exp17_protocol_comparison",
            "exp27_error_analysis",
            "make_rq_summary",
        ),
    ),
    "baza": (
        "Rindërto bazën",
        "Përshtatja mbi prerjen 70/30 dhe protokolli me tetë fold-e. Rreth 10 minuta.",
        ("train_models", "run_protocol", "make_diagrams", "make_reference_tables"),
    ),
    "rebuild_fast": (
        "Rindërtim i shpejtë",
        "Rindërton tabelat dhe figurat e studimeve të thelluara pa ripërshtatur asnjë model.",
        ("exp23_autoencoder_rebuild", "exp24_ocsvm_rebuild", "exp28_best_effort_rebuild"),
    ),
    "deep": (
        "Studimet e thelluara",
        "Të gjashtë studimet që ripërshtatin modelet. Disa orë.",
        (
            "exp20_data_geometry",
            "exp21_scaling",
            "exp22_iforest_deep",
            "exp23_autoencoder_deep",
            "exp24_ocsvm_deep",
            "exp28_best_effort",
        ),
    ),
}


def experiments_payload() -> dict[str, Any]:
    by_group: dict[str, list[dict[str, Any]]] = {g.id: [] for g in GROUPS}
    for exp in _ALL:
        by_group[exp.group].append(exp.as_dict())
    return {
        "groups": [
            {
                "id": g.id,
                "title": g.title,
                "subtitle": g.subtitle,
                "experiments": by_group[g.id],
            }
            for g in GROUPS
        ],
        "batches": [
            {"id": k, "title": v[0], "subtitle": v[1], "members": list(v[2])}
            for k, v in BATCHES.items()
        ],
    }


def resolve(target: str) -> list[Experiment]:
    """A catalogue id or a batch id, expanded to the experiments to run."""
    if target in EXPERIMENTS:
        return [EXPERIMENTS[target]]
    if target in BATCHES:
        return [EXPERIMENTS[m] for m in BATCHES[target][2]]
    raise KeyError(target)

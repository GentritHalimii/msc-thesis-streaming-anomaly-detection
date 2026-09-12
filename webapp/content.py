"""The structure of the application: pages, sections, and the blocks in them.

This module is the only place that decides what the reader sees and in which
order. It holds no data. A block names an artefact, and the server resolves
that name against `results/` when the page is requested, so the application
cannot drift out of step with the study.

The order follows the thesis, because the point of the application is to let
somebody walk the same argument faster, and then re-run any step of it.
"""

from __future__ import annotations

from typing import Any

MODEL_LABELS = {
    "iforest": "Isolation Forest",
    "autoencoder": "Autoencoder",
    "ocsvm": "One-Class SVM",
    "logreg": "LR (referencë)",
    "pca_recon": "PCA lineare (ablacion)",
    "statik": "Prag statik",
    "adaptiv": "Prag adaptiv",
}

MODEL_COLORS = {
    "Isolation Forest": "#2a78d6",
    "Autoencoder": "#1baf7a",
    "One-Class SVM": "#4a3aa7",
    "LR (referencë)": "#52514e",
    "PCA lineare (ablacion)": "#008300",
    "iforest": "#2a78d6",
    "autoencoder": "#1baf7a",
    "ocsvm": "#4a3aa7",
    "logreg": "#52514e",
}


# --- block constructors -----------------------------------------------------


def prose(*paragraphs: str) -> dict[str, Any]:
    return {"kind": "prose", "paragraphs": list(paragraphs)}


def callout(text: str, tone: str = "note", title: str = "") -> dict[str, Any]:
    return {"kind": "callout", "text": text, "tone": tone, "title": title}


def verdict(source: str, title: str = "Verdikti i matur") -> dict[str, Any]:
    return {"kind": "verdict", "source": source, "title": title}


def metrics(compute: str) -> dict[str, Any]:
    return {"kind": "metrics", "compute": compute}


REFERENCE_ROWS = ("LR (referencë)", "logreg")


def table(
    source: str,
    caption: str = "",
    columns: list[str] | None = None,
    labels: dict[str, str] | None = None,
    round_: dict[str, int] | None = None,
    query: str | None = None,
    highlight: str | None = None,
    highlight_skip: tuple[str, ...] = REFERENCE_ROWS,
    max_rows: int | None = None,
) -> dict[str, Any]:
    return {
        "kind": "table",
        "source": source,
        "caption": caption,
        "columns": columns,
        "labels": labels or {},
        "round": round_ or {},
        "query": query,
        "highlight": highlight,
        "highlight_skip": list(highlight_skip),
        "max_rows": max_rows,
    }


def figure(source: str, caption: str = "") -> dict[str, Any]:
    return {"kind": "figure", "source": source, "caption": caption}


def chart(kind: str, source: str, **spec: Any) -> dict[str, Any]:
    return {"kind": "chart", "chart": kind, "source": source, **spec}


def runner(*experiments: str, title: str = "Rigjenero") -> dict[str, Any]:
    return {"kind": "runner", "experiments": list(experiments), "title": title}


def widget(name: str, **spec: Any) -> dict[str, Any]:
    return {"kind": "widget", "widget": name, **spec}


def section(id_: str, title: str, thesis: str = "", *blocks: dict[str, Any]) -> dict[str, Any]:
    return {"id": id_, "title": title, "thesis": thesis, "blocks": list(blocks)}


def page(id_: str, title: str, subtitle: str, *sections: dict[str, Any]) -> dict[str, Any]:
    return {"id": id_, "title": title, "subtitle": subtitle, "sections": list(sections)}


# --- pages ------------------------------------------------------------------

_OVERVIEW = page(
    "permbledhje",
    "Përmbledhje",
    "Çfarë pyet ky studim, çfarë gjeti, dhe nën cilat kushte vlejnë përgjigjet.",
    section(
        "hero",
        "Gjetjet kryesore",
        "§6.1",
        prose(
            "Ky panel lexon drejtpërdrejt nga dosja e rezultateve të depos. Asnjë numër këtu "
            "nuk është i shkruar me dorë: çdo shifër, tabelë dhe figurë vjen nga skedarët që "
            "prodhojnë eksperimentet, dhe çdo seksion ka butonin e vet për t'i rigjeneruar. "
            "Nëse një eksperiment ri-ekzekutohet, faqja ndryshon bashkë me të.",
        ),
        metrics("headline"),
        widget("research_questions"),
    ),
    section(
        "udherrefyesi",
        "Argumenti me radhë",
        "Kapitujt 5 dhe 6",
        prose(
            "Nëntë gjetjet e studimit, në rendin në të cilin varen nga njëra-tjetra. Secila "
            "shoqërohet me numrin e vet të lexuar nga dosja e rezultateve dhe me lidhjen te "
            "seksioni që e provon. Kjo është edhe rruga më e shkurtër për ta kuptuar punimin, "
            "edhe skeleti i një prezantimi."
        ),
        widget("tour"),
    ),
    section(
        "fushëveprimi",
        "Fushëveprimi dhe pse është i ngushtë",
        "§1.4, §2.13",
        prose(
            "Studimi kufizohet te tri algoritmet që emërton projekt-propozimi, Isolation "
            "Forest, Autoencoder dhe One-Class SVM, plus një referencë e mbikëqyrur me "
            "Regresion Logjistik dhe një ablacion linear me PCA. Ngushtimi nuk është kufizim "
            "i imponuar por kusht: studimi mekanicist i një algoritmi kërkon proba të "
            "ndërtuara posaçërisht për të, dhe kjo punë nuk shkallëzohet në dhjetëra metoda.",
            "Ka edhe një arsye statistikore që matet. Diferenca kritike e testit post-hoc "
            "rritet me numrin e metodave të krahasuara, prandaj mbi tetë fold-e një bashkësi "
            "e gjerë detektorësh e bën testin të paaftë të refuzojë çfarëdo hipoteze. Me tre "
            "detektorë ajo bie nën gjerësinë e rangjeve dhe testi bëhet i përdorshëm.",
        ),
        table(
            "model_zoo",
            "Detektorët e krahasuar, mekanizmi i tyre dhe kostoja asimptotike.",
        ),
    ),
    section(
        "arkitektura",
        "Arkitektura e implementuar",
        "§4.9",
        prose(
            "Sistemi ndjek një arkitekturë pesështresore: burimi i të dhënave, shtresa e "
            "rrjedhës me Apache Kafka në modalitetin KRaft, shtresa e pikëzimit me modelet "
            "unsupervised, shtresa e alarmeve me prag, dhe shtresa e persistimit e "
            "vizualizimit me PostgreSQL dhe Grafana."
        ),
        figure("diagram_architecture", "Arkitektura pesështresore e sistemit."),
    ),
)


_DATASET = page(
    "dataseti",
    "Dataset-i dhe gjeometria",
    "Çfarë përmbajnë të dhënat, dhe sa i ndashëm është problemi para çdo modeli.",
    section(
        "eda",
        "Analiza eksploruese",
        "§4.1",
        metrics("dataset"),
        table(
            "eda_overview",
            "Karakteristikat kryesore të dataset-it.",
            labels={"treguesi": "Treguesi", "vlera": "Vlera"},
        ),
        figure(
            "eda_volume_and_fraud", "Volumi i transaksioneve dhe mashtrimet me kalimin e kohës."
        ),
        figure("eda_amounts", "Shpërndarja e shumave sipas klasës."),
        chart(
            "barsh",
            "eda_feature_signal",
            label="feature",
            value="abs_auc_gap",
            xlabel="Fuqia diskriminuese |AUC − 0.5|",
            sort="desc",
            limit=15,
            color="#2a78d6",
            title="Sinjali njëvariablësh për veçori, pesëmbëdhjetë më të fortat",
        ),
        runner("exp0_eda"),
    ),
    section(
        "gjeometria",
        "Kufiri i sipërm gjeometrik",
        "§5.1",
        prose(
            "Të tria metodat unsupervised e përcaktojnë anomalinë përmes një nocioni largësie "
            "ose ngjeshjeje. Prandaj pyetja e parë nuk është se cila prej tyre është më e "
            "mirë, por se sa larg mund të shkojë çdo metodë e kësaj natyre mbi këto të dhëna. "
            "Përgjigja merret pa përshtatur asnjë model: një detektor që pikëzon thjesht sipas "
            "distancës nga fqinjët legjitimë."
        ),
        verdict("geometry"),
        table(
            "geometry_summary",
            "Karakterizimi gjeometrik i të dyja dritareve.",
            columns=[
                "dritarja",
                "rreshta",
                "mashtrime",
                "id_twonn_normale",
                "knn_distanca_normale",
                "knn_distanca_mashtrime",
                "raporti_distancave",
                "ap_vetem_distance",
                "rangu_median_i_mashtrimit",
                "mashtrime_ne_top100",
            ],
            labels={
                "dritarja": "Dritarja",
                "rreshta": "Rreshta",
                "mashtrime": "Mashtrime",
                "id_twonn_normale": "Dim. i brendshëm",
                "knn_distanca_normale": "kNN legjitime",
                "knn_distanca_mashtrime": "kNN mashtrime",
                "raporti_distancave": "Raporti",
                "ap_vetem_distance": "AP vetëm distancë",
                "rangu_median_i_mashtrimit": "Rangu median",
                "mashtrime_ne_top100": "Në top-100",
            },
            round_={
                "id_twonn_normale": 2,
                "knn_distanca_normale": 2,
                "knn_distanca_mashtrime": 2,
                "raporti_distancave": 2,
                "ap_vetem_distance": 3,
                "rangu_median_i_mashtrimit": 0,
            },
        ),
        figure("geometry_knn_distance", "Distanca deri te dhjetë fqinjët legjitimë më të afërt."),
        figure("geometry_cost_to_catch", "Sa alarme kushton secili mashtrim."),
        callout(
            "Ky nënkapitull përcakton kornizën e leximit për gjithçka tjetër. Nëse një "
            "detektor i trajnuar arrin AP në rendin 0.1 deri 0.3 mbi këto të dhëna, ai nuk "
            "është domosdoshmërisht i dobët; ai ndodhet afër kufirit që gjeometria e lejon.",
            tone="accent",
            title="Si duhet lexuar çdo rezultat që vjen pas kësaj",
        ),
        runner("exp20_data_geometry"),
    ),
)


_PROTOCOL = page(
    "protokolli",
    "Protokolli dhe disiplina",
    "Si matet, dhe sa do të ndryshonte numri i raportuar po të matej ndryshe.",
    section(
        "folds",
        "Protokolli rolling-origin",
        "§4.2.2",
        prose(
            "Çdo fold trajnohet mbi gjithçka përpara prerjes së vet dhe testohet mbi bllokun "
            "që vjen pas saj. Skaluesi, modelet dhe pragjet rindërtohen nga fillimi brenda "
            "secilit fold, prandaj asnjë statistikë e bashkësisë së testimit nuk rrjedh prapa."
        ),
        metrics("protocol"),
        figure("diagram_protocol", "Gjeometria e tetë fold-eve mbi rrjedhën kronologjike."),
        chart(
            "line",
            "fold_summary",
            x="fold",
            series=[{"col": "test_frauds", "label": "Mashtrime në bllokun e testimit"}],
            xlabel="Fold-i kohor",
            ylabel="Mashtrime",
            colors=["#e34948"],
            markers=True,
            title="Sa mashtrime përmban secili bllok testimi",
        ),
        table("fold_summary", "Struktura e tetë fold-eve."),
        runner("run_protocol"),
    ),
    section(
        "rrjedhja",
        "Katër rrugët e rrjedhjes së informacionit",
        "§3.7",
        prose(
            "Ndarja, paraprocesimi, pragu dhe zgjedhja e hiperparametrave janë katër rrugë të "
            "veçanta përmes të cilave bashkësia e testimit mund të ndikojë modelin. Secila ka "
            "masën e vet mbrojtëse, dhe secila masë mbulohet nga një test automatik."
        ),
        figure("diagram_leakage", "Rrugët e rrjedhjes dhe masat mbrojtëse përkatëse."),
    ),
    section(
        "krahasimi",
        "Sa peshojnë vendimet e protokollit",
        "§5.10",
        verdict("protocol"),
        chart(
            "grouped",
            "protocol_inflation",
            index="Detektori",
            series=[
                {"col": "AP_kronologjik", "label": "Ndarje kronologjike", "color": "#2a78d6"},
                {"col": "AP_i_perzier", "label": "Ndarje e rastësishme", "color": "#e34948"},
            ],
            ylabel="Average Precision (AP)",
            title="E njëjta ndarje 70/30, një herë sipas kohës dhe një herë e përzier",
        ),
        table("protocol_inflation", "Fryrja e AP-së nën ndarje të rastësishme."),
        figure("protocol_comparison", "Prerja e vetme kundrejt shpërndarjes nëpër tetë fold-e."),
        table("protocol_comparison", "Prerja e vetme kundrejt protokollit me tetë fold-e."),
        runner("exp6_shuffled_split", "exp17_protocol_comparison"),
    ),
)


_RESULTS = page(
    "rezultatet",
    "Rezultatet kryesore",
    "PH2: cili algoritëm ofron balancën më të mirë mes performancës dhe efikasitetit.",
    section(
        "kryesore",
        "Krahasimi nën konfigurimin bazë",
        "§5.3.1",
        prose(
            "Tabela kryesore krahason tri algoritmet unsupervised dhe referencën e mbikëqyrur "
            "në tetë pika kohore prerjeje, me hiperparametrat e parazgjedhur dhe me skalim "
            "standard. Ky është konfigurimi bazë, jo ai më i mirë i arritshëm; dallimi mes "
            "tyre matet veçmas dhe rezulton i madh."
        ),
        chart(
            "barsh",
            "benchmark_summary",
            label="model",
            value="ap_mean",
            error="ap_std",
            colorByLabel=True,
            xlabel="Average Precision (AP)",
            sort="desc",
            title="Average Precision mesatar mbi tetë fold-e",
        ),
        table(
            "benchmark_summary",
            "Rezultatet kryesore mbi tetë fold-e.",
            columns=[
                "model",
                "ap_mean",
                "ap_std",
                "avg_rank_ap",
                "roc_auc_mean",
                "recall_at_100",
                "score_us_per_tx",
                "fit_time_s",
            ],
            labels={
                "model": "Detektori",
                "ap_mean": "AP",
                "ap_std": "s.d.",
                "avg_rank_ap": "Rangu",
                "roc_auc_mean": "ROC-AUC",
                "recall_at_100": "Recall@100",
                "score_us_per_tx": "µs/tx",
                "fit_time_s": "Fit (s)",
            },
            round_={
                "ap_mean": 4,
                "ap_std": 4,
                "avg_rank_ap": 2,
                "roc_auc_mean": 3,
                "recall_at_100": 3,
                "score_us_per_tx": 2,
                "fit_time_s": 1,
            },
            highlight="ap_mean",
        ),
        callout(
            "Isolation Forest ka AP 0.09 dhe ROC-AUC 0.94, praktikisht të njëjtën ROC si "
            "Autoencoder-i që ka AP dyfish më të lartë. Nëse raportohej vetëm ROC, siç bën "
            "një pjesë e literaturës mbi këtë dataset, të tre detektorët do të dukeshin "
            "ekuivalentë. Kjo është arsyeja pse metrika parësore këtu është Average Precision.",
            tone="warn",
            title="Pse ROC-AUC nuk raportohet si metrikë parësore",
        ),
        chart(
            "line",
            "benchmark_per_fold",
            x="fold",
            group="model",
            y="ap",
            xlabel="Fold-i kohor",
            ylabel="Average Precision (AP)",
            markers=True,
            colorByGroup=True,
            title="Cilësia për fold: shpërhapja që një prerje e vetme nuk e tregon",
        ),
        runner("run_protocol", "exp10_benchmark"),
    ),
    section(
        "domethenia",
        "A janë dallimet statistikisht të qëndrueshme",
        "§5.3.2",
        prose(
            "Testi omnibus i Friedman-it refuzon hipotezën se detektorët janë ekuivalentë. "
            "Krahasimet dyshe të paradeklaruara bëhen me testin e çiftuar të Wilcoxon-it mbi "
            "fold-et, me korrigjim Holm për gjashtë krahasime."
        ),
        table("significance_omnibus", "Testi omnibus dhe diferenca kritike e Nemenyi-t."),
        figure("significance_cd_core", "Diagrami i diferencës kritike."),
        table(
            "significance_wilcoxon",
            "Krahasimet e paradeklaruara dyshe me korrigjim Holm.",
            columns=[
                "krahasimi",
                "mean_diff",
                "wins_a",
                "wins_b",
                "p_value",
                "p_holm",
                "significant_holm_05",
            ],
            labels={
                "krahasimi": "Krahasimi",
                "mean_diff": "Δ AP",
                "wins_a": "Fitore A",
                "wins_b": "Fitore B",
                "p_value": "p",
                "p_holm": "p (Holm)",
                "significant_holm_05": "Domethënës",
            },
            round_={"mean_diff": 4, "p_value": 4, "p_holm": 4},
        ),
        runner("exp11_significance"),
    ),
    section(
        "kostoja",
        "Cilësia përballë kostos",
        "§5.3.3",
        prose(
            "Pyetja hulumtuese nuk kërkon detektorin më të saktë por atë me balancën më të "
            "mirë. Kostoja e pikëzimit ndryshon me qindra herë mes detektorëve, dhe në rrjedhë "
            "ky dallim përcakton nëse një metodë është e vendosshme apo jo."
        ),
        chart(
            "scatter",
            "benchmark_summary",
            x="score_us_per_tx",
            y="ap_mean",
            label="model",
            colorByLabel=True,
            xlabel="Kostoja e pikëzimit (µs për transaksion)",
            ylabel="Average Precision (AP)",
            logx=True,
            title="Këndi i sipërm i majtë është pozicioni i dëshiruar",
        ),
        figure("benchmark_quality_cost", "Cilësia kundrejt kostos, siç del në punim."),
    ),
    section(
        "buxheti",
        "Vlerësimi në buxhet alarmesh",
        "§5.3.4",
        prose(
            "Average Precision përmbledh të gjithë renditjen, por asnjë ekip nuk e shqyrton "
            "atë të tërën. Këtu matet çfarë kapet kur investigohen vetëm k alarmet më të larta "
            "për bllok testimi."
        ),
        verdict("budget"),
        chart(
            "line",
            "budget_summary",
            x="budget_k",
            group="model",
            y="recall_at_k",
            xlabel="Buxheti i alarmeve (k)",
            ylabel="Recall brenda buxhetit",
            logx=True,
            markers=True,
            colorByGroup=True,
            title="Sa mashtrime kapen brenda buxhetit",
        ),
        table(
            "budget_summary",
            "Cilësia dhe rikuperimi monetar në buxhet prej njëqind alarmesh.",
            query="budget_k == 100",
            labels={
                "model": "Detektori",
                "budget_k": "k",
                "precision_at_k": "Precision@k",
                "recall_at_k": "Recall@k",
                "amount_recall_at_k": "Vlera e kapur",
                "net_savings_eur": "Kursime neto (EUR)",
                "savings_ratio": "Raporti",
            },
            round_={
                "precision_at_k": 3,
                "recall_at_k": 3,
                "amount_recall_at_k": 3,
                "net_savings_eur": 0,
                "savings_ratio": 3,
            },
            highlight="recall_at_k",
        ),
        figure("budget_savings", "Raporti i kursimeve neto sipas buxhetit."),
        runner("exp14_alert_budget"),
    ),
)


_ENSEMBLE = page(
    "ansambli",
    "Ansamblet dhe gabimet",
    "PH3: a e përmirëson kombinimi zbulimin, dhe cilat mashtrime nuk i kap askush.",
    section(
        "ansambli",
        "A ndihmon kombinimi i detektorëve",
        "§5.4",
        prose(
            "Pesë rregulla kombinimi mbi tri pikët e detektorëve unsupervised, plus një "
            "procedurë lakmitare që i shton anëtarët një nga një. Referenca e mbikëqyrur "
            "përjashtohet nga çdo ansambël, sepse përfshirja e saj do ta shndërronte "
            "kombinimin unsupervised në një model me etiketa."
        ),
        verdict("ensemble", "Verdikti me hiperparametra të parazgjedhur"),
        verdict("ensemble_verdict_tuned", "Verdikti me hiperparametra të akorduar"),
        metrics("ensembles"),
        chart(
            "barsh",
            "ensemble_summary",
            label="combiner",
            value="ap_mean",
            error="ap_std",
            groupLabel="pool",
            xlabel="Average Precision (AP)",
            sort="desc",
            color="#4a3aa7",
            title="Variantet e ansamblit kundrejt anëtarit më të mirë",
        ),
        figure("ensemble_vs_single", "Ansamblet kundrejt modelit më të mirë individual."),
        figure(
            "ensemble_rank_correlation", "Korrelacioni i renditjeve mes çifteve të detektorëve."
        ),
        runner("exp12_ensembles", "exp12_ensembles_tuned"),
    ),
    section(
        "gabimet",
        "Cilat mashtrime nuk kapen",
        "§5.14",
        prose(
            "Metrikat e grumbulluara e fshehin identitetin e transaksioneve. Këtu secili "
            "mashtrim ndiqet individualisht nëpër tetë fold-et, dhe regjistrohet nga sa "
            "detektorë arrihet brenda buxhetit prej njëqind alarmesh."
        ),
        verdict("error_analysis"),
        chart(
            "bars",
            "error_analysis_coverage",
            label="n_detektore",
            value="mashtrime",
            xlabel="Sa detektorë e arrijnë mashtrimin",
            ylabel="Numri i mashtrimeve",
            color="#2a78d6",
            title="Shpërndarja e mbulimit: kulme në të dyja skajet",
        ),
        table(
            "error_analysis_coverage",
            "Mbulimi sipas numrit të detektorëve që arrijnë mashtrimin.",
            labels={
                "n_detektore": "Detektorë që e kapin",
                "mashtrime": "Mashtrime",
                "shuma_mesatare": "Shuma mesatare",
                "norma_z_mediane": "‖z‖ mediane",
                "pjesa": "Pjesa",
            },
            round_={"shuma_mesatare": 2, "norma_z_mediane": 2, "pjesa": 4},
        ),
        figure("error_analysis", "Mbulimi dhe pozicioni gjeometrik i mashtrimeve të paarritshme."),
        table("error_analysis_dark_set", "Mashtrimet e kapura kundrejt atyre të paarritshme."),
        callout(
            "Nga mashtrimet që nuk i arrin asnjë detektor unsupervised, referenca e "
            "mbikëqyrur i kap afërsisht gjashtëdhjetë për qind brenda të njëjtit buxhet. "
            "Informacioni ekziston pra në të dhëna; ai thjesht nuk është i formës që një "
            "detektor distancash mund ta shohë.",
            tone="accent",
        ),
        runner("exp27_error_analysis"),
    ),
)


_DEPTH = page(
    "thellesia",
    "Studimet për algoritëm",
    "Brenda secilit detektor: cila levë e lëviz rezultatin, dhe pse sillet siç sillet.",
    section(
        "iforest",
        "Isolation Forest: ku shkon kapaciteti",
        "§5.5.1",
        prose(
            "Hipoteza është se dobësia e Isolation Forest-it vjen nga zgjedhja uniforme e "
            "dimensionit të ndarjes. Ajo testohet me tri proba të pavarura: numërimi i "
            "ndarjeve brenda pemëve të përshtatura, ripërshtatja mbi një hapësirë të "
            "rrotulluar rastësisht, dhe kufizimi i secilës pemë në një nën-hapësirë veçorish."
        ),
        verdict("iforest"),
        chart(
            "heatmap",
            "iforest_surface",
            rowKey="n_estimators",
            xlabel="Madhësia e nën-mostrës",
            ylabel="Numri i pemëve",
            valueLabel="Average Precision (AP)",
            title="Sipërfaqja e hiperparametrave",
        ),
        figure("iforest_capacity", "Ku shkojnë ndarjet, dhe a lidhen ato me sinjalin."),
        chart(
            "bars",
            "iforest_max_features_summary",
            label="max_features",
            value="ap_mean",
            error="ap_std",
            xlabel="max_features (pjesa e kolonave për pemë)",
            ylabel="Average Precision (AP)",
            color="#2a78d6",
            title="Kufizimi i nën-hapësirës: prova e tretë e mekanizmit",
        ),
        table("iforest_max_features_summary", "Efekti i kufizimit të nën-hapësirës."),
        runner("exp22_iforest_deep"),
    ),
    section(
        "autoencoder",
        "Autoencoder: ngushtica, humbja dhe mbitrajnimi",
        "§5.5.2",
        prose(
            "Gjashtë leva u ndryshuan veç e veç mbi të njëjtat tetë fold-e: gjerësia e "
            "shtresës së fshehur bashkë me dimensionin latent, thellësia e enkoderit, "
            "funksioni i humbjes, tri regullarizues, dhe numri i epokave. Në të gjitha "
            "variantet pika e anomalisë llogaritet gjithmonë si gabim kuadratik mesatar, "
            "përndryshe ablacioni nuk do të ishte i interpretueshëm."
        ),
        verdict("autoencoder"),
        figure("autoencoder_architecture", "Sipërfaqja e arkitekturës."),
        chart(
            "barsh",
            "autoencoder_studies_tidy",
            label="Konfigurimi",
            value="AP",
            error="s.d.",
            facet="Studimi",
            xlabel="Average Precision (AP)",
            sort="desc",
            color="#1baf7a",
            title="Zgjidh studimin për të parë konfigurimet e tij",
        ),
        figure("autoencoder_vs_linear", "Enkoderi jolinear kundrejt dyshemesë lineare."),
        figure("autoencoder_training", "Humbja e trajnimit kundrejt cilësisë së zbulimit."),
        callout(
            "Dy gjetje me interes teorik: dimensioni latent optimal është rreth tri herë "
            "dimensioni i brendshëm i vlerësuar, pra heuristika që i barazon të dyja nuk vlen "
            "për zbulim; dhe mbitrajnimi e dëmton zbulimin ndërsa humbja e trajnimit vazhdon "
            "të bjerë, prandaj kriteri i ndalimit nuk mund të jetë humbja e trajnimit.",
            tone="accent",
        ),
        runner("exp23_autoencoder_deep", "exp23_autoencoder_rebuild"),
    ),
    section(
        "ocsvm",
        "One-Class SVM: kerneli, nu dhe çmimi i të dhënave",
        "§5.5.3",
        prose(
            "Tri boshte: zgjedhja e kernelit, sipërfaqja mbi nu dhe gamma, dhe kurba e të "
            "mësuarit mbi madhësinë e nën-mostrës. Boshti i fundit është i veçantë për këtë "
            "algoritëm, sepse kostoja e tij rritet afërsisht kuadratikisht dhe nën-mostrimi "
            "nuk është zgjedhje por domosdoshmëri."
        ),
        verdict("ocsvm"),
        chart(
            "bars",
            "ocsvm_kernels",
            label="kernel",
            value="ap_mean",
            error="ap_std",
            xlabel="Kerneli",
            ylabel="Average Precision (AP)",
            color="#4a3aa7",
            title="Kerneli linear dështon plotësisht: struktura e nevojshme është jolineare",
        ),
        chart(
            "heatmap",
            "ocsvm_surface",
            rowKey="nu",
            xlabel="gamma",
            ylabel="nu",
            valueLabel="Average Precision (AP)",
            title="Sipërfaqja nu-gamma me kernel RBF",
        ),
        chart(
            "line",
            "ocsvm_learning_curve",
            x="train_subsample",
            series=[
                {"col": "ap_mean", "label": "Average Precision", "color": "#4a3aa7"},
            ],
            error={"ap_mean": "ap_std"},
            xlabel="Transaksione normale në trajnim",
            ylabel="Average Precision (AP)",
            logx=True,
            markers=True,
            title="Cilësia ngopet shumë përpara se kostoja të ndalojë së rrituri",
        ),
        chart(
            "line",
            "ocsvm_learning_curve",
            x="train_subsample",
            series=[
                {"col": "fit_s", "label": "Koha e trajnimit (s)", "color": "#e34948"},
                {"col": "us_per_tx", "label": "Pikëzimi (µs/tx)", "color": "#d98c1f"},
                {"col": "support_vectors", "label": "Vektorë mbështetës", "color": "#898781"},
            ],
            xlabel="Transaksione normale në trajnim",
            ylabel="Kosto (shkallë logaritmike)",
            logx=True,
            logy=True,
            markers=True,
            title="Kostoja që paguhet për ato të dhëna",
        ),
        table("ocsvm_learning_curve", "Kurba e të mësuarit me koston përkatëse."),
        runner("exp24_ocsvm_deep", "exp24_ocsvm_rebuild"),
    ),
)


_CONFIG = page(
    "konfigurimi",
    "Paraprocesimi, akordimi, kapaciteti",
    "Sa nga dallimi mes algoritmeve është vërtet dallim algoritmi.",
    section(
        "paraprocesimi",
        "Paraprocesimi si variabël eksperimentale",
        "§5.6",
        prose(
            "Të tria metodat e përcaktojnë anomalinë përmes një nocioni largësie, dhe ai "
            "nocion varet plotësisht nga shkalla e veçorive. Prandaj zgjedhja e transformimit "
            "meriton të testohet e jo të supozohet. Shtatë opsione u vlerësuan mbi të njëjtat "
            "tetë fold-e, me skaluesin e përshtatur brenda çdo fold-i."
        ),
        verdict("scaling"),
        chart(
            "grouped",
            "scaling_summary",
            index="Paraprocesimi",
            series=[
                {"col": "Isolation Forest", "label": "Isolation Forest", "color": "#2a78d6"},
                {"col": "Autoencoder", "label": "Autoencoder", "color": "#1baf7a"},
                {"col": "One-Class SVM", "label": "One-Class SVM", "color": "#4a3aa7"},
                {"col": "LR (referencë)", "label": "LR (referencë)", "color": "#52514e"},
            ],
            ylabel="Average Precision (AP)",
            title="Referenca e mbikëqyrur nuk lëviz; metodat gjeometrike po",
        ),
        table(
            "scaling_significance",
            "Testi i Friedman-it mbi shtatë opsionet dhe krahasimi me skalimin standard.",
            round_={"Friedman_chi2": 2, "delta_ndaj_standard": 4, "wilcoxon_p": 4},
        ),
        callout(
            "Hapësira mes paraprocesimit më të mirë dhe atij më të keq për një detektor të "
            "vetëm është rreth tri herë më e madhe se hapësira mes vetë tre detektorëve nën "
            "skalim standard. Mënyra si përgatiten të dhënat peshon pra më shumë se cili nga "
            "tre algoritmet zgjidhet.",
            tone="accent",
        ),
        runner("exp21_scaling"),
    ),
    section(
        "akordimi",
        "Sa e ndryshon akordimi renditjen",
        "§5.9",
        prose(
            "I njëjti protokoll u përsërit plotësisht me hiperparametrat e nxjerrë nga një "
            "kërkim mbi ndarjen e brendshme kohore të dritares së trajnimit. Bashkësia e "
            "detektorëve fiton në të tetë fold-et, por përfitimi shpërndahet shumë "
            "pabarabartë."
        ),
        verdict("tuning"),
        chart(
            "grouped",
            "tuning_effect",
            index="Detektori",
            series=[
                {"col": "AP_default", "label": "Me parazgjedhje", "color": "#c3c2b7"},
                {"col": "AP_i_akorduar", "label": "Me akordim", "color": "#2a78d6"},
            ],
            ylabel="Average Precision (AP)",
            title="Udhëheqësi mbetet, dy të fundit ndërrohen",
        ),
        table("tuning_effect", "Efekti i akordimit mbi blloqet e testimit."),
        figure("tuning_transfer", "Përmirësimi i brendshëm kundrejt atij në test."),
        runner("exp9_tuning", "run_protocol_tuned", "exp18_tuning_effect"),
    ),
    section(
        "kapaciteti",
        "Secili detektor në kapacitetin e vet më të mirë",
        "§5.16",
        prose(
            "Dizajni faktorial dy-nga-dy kryqëzon hiperparametrat e parazgjedhur me ata të "
            "akorduar, dhe skalimin standard me paraprocesimin që studimi i mëparshëm zgjodhi "
            "për secilin detektor. Ai e ndan përfitimin total në kontributin e secilës "
            "ndërhyrje dhe në ndërveprimin mes tyre."
        ),
        verdict("best_effort"),
        chart(
            "grouped",
            "best_effort",
            index="model",
            series=[
                {"col": "parazgjedhur / standard", "label": "bazë", "color": "#c3c2b7"},
                {"col": "parazgjedhur / më i miri", "label": "+ paraprocesim", "color": "#1baf7a"},
                {"col": "i akorduar / standard", "label": "+ akordim", "color": "#2a78d6"},
                {"col": "i akorduar / më i miri", "label": "+ të dyja", "color": "#4a3aa7"},
            ],
            ylabel="Average Precision (AP)",
            title="Katër qelizat e dizajnit, për secilin detektor",
        ),
        table(
            "best_effort_interaction",
            "Dekompozimi i përfitimit dhe qeliza më e mirë për secilin detektor.",
            round_={
                "bazë": 4,
                "vetëm paraprocesim": 4,
                "vetëm akordim": 4,
                "të dyja": 4,
                "shuma e efekteve": 4,
                "ndërveprimi": 4,
                "AP më i mirë i arritshëm": 4,
            },
            highlight="AP më i mirë i arritshëm",
        ),
        callout(
            "Nën konfigurimet e parazgjedhura tri algoritmet ndahen me raport rreth dy herë "
            "mes më të mirit dhe më të keqit. Kur secilit i jepet konfigurimi i vet më i mirë, "
            "ai raport bie nën një e gjysmë dhe renditja përmbyset. Pjesa më e madhe e asaj "
            "që duket si dallim mes algoritmeve është dallim në se sa mirë u shërbejnë atyre "
            "vlerat e parazgjedhura të bibliotekave.",
            tone="accent",
            title="Gjetja që e ndryshon leximin e çdo renditjeje të publikuar",
        ),
        runner("exp28_best_effort", "exp28_best_effort_rebuild"),
    ),
)


_CAUSAL = page(
    "kauzaliteti",
    "Nga korrelacioni te shkaku",
    "Shpjegimi mekanicist i renditjes, dhe ndërhyrja që e teston atë.",
    section(
        "atribuimi",
        "Ku e drejtojnë vëmendjen detektorët",
        "§5.12",
        prose(
            "Për secilin detektor matet sa përputhet vëmendja e tij me sinjalin realisht të "
            "disponueshëm në secilën kolonë. Atribuimi është i jashtëm dhe i njëjtë për të "
            "tre, prandaj vlerat janë të krahasueshme mes tyre."
        ),
        verdict("explain"),
        chart(
            "barsh",
            "explain_signal_agreement",
            label="atribuimi",
            value="spearman_vs_auc_gap",
            xlabel="Korrelacion rangjesh me sinjalin e disponueshëm",
            sort="desc",
            color="#2a78d6",
            title="Rendi i përputhjes është i njëjti me rendin e cilësisë së zbulimit",
        ),
        table("explain_signal_agreement", "Përputhja mes atribuimit dhe sinjalit."),
        figure("explain_attention_vs_signal", "Vëmendja kundrejt sinjalit, kolonë për kolonë."),
        callout(
            "Dy renditje mbi tre elemente mund të përputhen rastësisht. Prandaj kjo mbetet "
            "hipotezë mekaniciste derisa të ndërhyhet mbi shkakun e supozuar, gjë që bëhet "
            "në seksionin e mëposhtëm.",
            tone="note",
        ),
        runner("exp15_explainability"),
    ),
    section(
        "nderhyrja",
        "Ndërhyrja mbi hyrjen",
        "§5.7",
        prose(
            "Në secilin fold, komponentët renditen sipas fuqisë së tyre diskriminuese të "
            "matur vetëm mbi dritaren e trajnimit, dhe secili detektor ripërshtatet duke parë "
            "vetëm k komponentët e parë. Nëse shpërndarja e ndarjeve mbi kolona pa sinjal "
            "është vërtet mekanizmi i dobësisë, Isolation Forest duhet të fitojë më shumë se "
            "të tjerët, dhe më shumë te k-të e vogla."
        ),
        verdict("feature_selection"),
        chart(
            "line",
            "feature_selection",
            x="k",
            group="model",
            y="ap_mean",
            facet="renditja",
            xlabel="Numri i komponentëve të ruajtur (k)",
            ylabel="Average Precision (AP)",
            markers=True,
            colorByGroup=True,
            title="Zgjidh renditjen: me etiketa është rasti më i mirë, kurtoza është e vendosshme",
        ),
        figure("feature_selection", "Efekti i kufizimit të hyrjes, për të dyja renditjet."),
        table("feature_selection_agreement", "Mbivendosja mes dy renditjeve."),
        callout(
            "Referenca e mbikëqyrur humbet nga çdo kufizim, ndërsa të tre detektorët "
            "unsupervised fitojnë. Ky kontroll e bën argumentin të vlefshëm: një model që "
            "tashmë i peshon vetë kolonat nuk ka çfarë të fitojë nga një peshim i jashtëm.",
            tone="accent",
        ),
        runner("exp25_feature_selection"),
    ),
)


_TIME = page(
    "koha",
    "Koha: zhvendosja, historiku, pragu",
    "Çfarë ndryshon me kalimin e kohës, dhe çfarë duhet bërë për të.",
    section(
        "zhvendosja",
        "Cila popullatë lëviz",
        "§5.11",
        prose(
            "Degradimi me kohën vërehet lehtë; pyetja e dobishme është cila popullatë lëviz. "
            "Nëse lëviz ajo legjitime, ritrajnimi ndihmon. Nëse lëviz ajo e mashtrimeve, "
            "ritrajnimi mbi të dhëna të reja normale nuk ndryshon asgjë."
        ),
        verdict("drift"),
        chart(
            "line",
            "drift_per_fold",
            x="fold",
            series=[
                {"col": "psi_normals_mean", "label": "Transaksione legjitime", "color": "#2a78d6"},
                {"col": "psi_frauds_mean", "label": "Mashtrime", "color": "#e34948"},
            ],
            xlabel="Fold-i kohor",
            ylabel="Indeksi PSI (mesatar mbi veçoritë)",
            markers=True,
            logy=True,
            refs=[{"y": 0.25, "label": "pragu i zhvendosjes së moderuar"}],
            title="Një rend madhësie dallim mes dy popullatave",
        ),
        figure("drift_psi_decomposition", "Dekompozimi i zhvendosjes sipas popullatës."),
        figure("drift_separability", "Aftësia ndarëse e matur pa model."),
        runner("exp13_drift"),
    ),
    section(
        "historiku",
        "Sa histori duhet mbajtur",
        "§5.8",
        verdict("training_window"),
        chart(
            "line",
            "training_window_curve",
            x="madhesia",
            group="model",
            y="ap_mean",
            xlabel="Gjatësia e dritares rrëshqitëse (transaksione)",
            ylabel="Average Precision (AP)",
            logx=True,
            markers=True,
            colorByGroup=True,
            title="Më shumë të dhëna nuk ndihmojnë detektorët unsupervised",
        ),
        table(
            "training_window_expanding", "Rezultati me dritaren që zgjerohet mbi gjithë historikun."
        ),
        figure("training_window", "Kurba e të mësuarit mbi gjatësinë e dritares."),
        runner("exp26_training_window"),
    ),
    section(
        "pragu",
        "Pragu adaptiv me dritare rrëshqitëse",
        "§5.13",
        prose(
            "Një prag i fiksuar nga kuantili i pikëve të trajnimit e ka një dobësi që del "
            "vetëm në rrjedhë: kur shpërndarja zhvendoset, numri i alarmeve zhvendoset bashkë "
            "me të, dhe ekipi hetimor merr ngarkesë të paparashikueshme pikërisht kur diçka "
            "ka ndryshuar."
        ),
        verdict("adaptive_threshold"),
        chart(
            "grouped",
            "adaptive_threshold_summary",
            index="model",
            pivot={"column": "regjimi", "value": "f1"},
            ylabel="F1",
            title="F1 nën pragun statik kundrejt atij adaptiv",
        ),
        chart(
            "grouped",
            "adaptive_threshold_summary",
            index="model",
            pivot={"column": "regjimi", "value": "alert_rate_cv"},
            ylabel="Koeficienti i variacionit të ngarkesës",
            title="Sa e parashikueshme bëhet ngarkesa hetimore",
        ),
        figure("adaptive_tradeoff", "Kompromisi mes qëndrueshmërisë dhe cilësisë."),
        callout(
            "Për të tre detektorët unsupervised F1 rritet; për referencën e mbikëqyrur ai "
            "bie. Pragu statik i saj është tashmë i kalibruar, prandaj një kuantil mbi "
            "dritare rrëshqitëse vetëm sa e detyron të alarmojë më shumë se ç'duhet. "
            "Rekomandimi është pra i kushtëzuar.",
            tone="warn",
        ),
        runner("exp16_adaptive_threshold"),
    ),
    section(
        "pa-etiketa",
        "A mund të zgjidhet një konfigurim pa etiketa",
        "§5.15",
        verdict("unsupervised_selection"),
        table("unsupervised_selection", "Zgjedhja pa etiketa kundrejt asaj me etiketa."),
        figure(
            "unsupervised_selection", "Renditja sipas kriterit pa etiketa kundrejt asaj me etiketa."
        ),
        runner("exp19_unsupervised_selection"),
    ),
)


_STREAM = page(
    "rrjedha",
    "Rrjedha, vonesa dhe Grafana",
    "PH1: a mund të ndërtohet sistemi, dhe a qëndron vonesa nën një sekondë.",
    section(
        "sherbimet",
        "Gjendja e grumbullit",
        "§4.9.1",
        prose(
            "Shtresa e rrjedhës kërkon tre kontejnerë: Apache Kafka në modalitetin KRaft, "
            "PostgreSQL për persistim, dhe Grafana për vizualizim. Portat janë 19092, 15432 "
            "dhe 3000, të zgjedhura që të mos përplasen me shërbime të tjera lokale."
        ),
        widget("services"),
    ),
    section(
        "vonesa",
        "Vonesa end-to-end",
        "§5.2",
        prose(
            "Për secilin model, njëzet mijë transaksione ripërsëriten mbi broker-in e vërtetë "
            "me ritëm të kontrolluar. Vonesa matet nga çasti kur producer-i e krijon mesazhin "
            "deri kur consumer-i e ka pikëzuar atë, me orë monotonike të të njëjtit host."
        ),
        metrics("streaming"),
        chart(
            "line",
            "latency_summary",
            x="rate_msg_s",
            group="model",
            y="e2e_ms_mean",
            query="prag_adaptiv == False",
            xlabel="Ritmi i replay-it (mesazhe/s)",
            ylabel="Vonesa mesatare end-to-end (ms)",
            logx=True,
            logy=True,
            markers=True,
            colorByGroup=True,
            refs=[{"y": 1000, "label": "objektivi prej 1 sekonde"}],
            title="Vonesa qëndron një deri dy rende madhësie nën objektivin",
        ),
        chart(
            "line",
            "latency_summary",
            x="rate_msg_s",
            group="model",
            y="throughput_ratio",
            query="prag_adaptiv == False",
            xlabel="Ritmi i replay-it (mesazhe/s)",
            ylabel="Kapaciteti i arritur / i synuar",
            logx=True,
            markers=True,
            colorByGroup=True,
            refs=[{"y": 1.0, "label": "consumer-i mban ritmin"}],
            title="Ku fillon ngopja e një consumer-i të vetëm",
        ),
        table(
            "latency_summary",
            "Vonesa, inferenca dhe kapaciteti për çdo kombinim modeli dhe ritmi.",
            query="prag_adaptiv == False",
            columns=[
                "model",
                "rate_msg_s",
                "e2e_ms_mean",
                "e2e_ms_p95",
                "e2e_ms_p99",
                "infer_ms_mean",
                "batch_size_mean",
                "throughput_msg_s",
                "throughput_ratio",
            ],
            labels={
                "model": "Modeli",
                "rate_msg_s": "Ritmi",
                "e2e_ms_mean": "e2e mes. (ms)",
                "e2e_ms_p95": "p95",
                "e2e_ms_p99": "p99",
                "infer_ms_mean": "Inferenca (ms)",
                "batch_size_mean": "Grumbulli",
                "throughput_msg_s": "msg/s",
                "throughput_ratio": "Raporti",
            },
            round_={
                "e2e_ms_mean": 1,
                "e2e_ms_p95": 1,
                "e2e_ms_p99": 1,
                "infer_ms_mean": 3,
                "batch_size_mean": 1,
                "throughput_msg_s": 0,
                "throughput_ratio": 3,
            },
        ),
        figure("latency_vs_rate", "Vonesa sipas ritmit, siç del në punim."),
        runner("stream_sweep", "stream_adaptive", "latency_report"),
    ),
    section(
        "baza-e-te-dhenave",
        "Çfarë ka arritur te baza e të dhënave",
        "§4.9.3",
        prose(
            "Çdo ngjarje e pikëzuar dhe çdo alarm shkruhen në PostgreSQL me shkrime të "
            "grumbulluara. Numëruesit më poshtë lexohen drejtpërdrejt nga baza sa herë "
            "rifreskohet faqja."
        ),
        widget("database"),
        runner("stream_store"),
    ),
    section(
        "grafana",
        "Paneli Grafana",
        "§4.9.3",
        prose(
            "Paneli është konfiguruar tërësisht nga skedarë në depo, burimi i të dhënave dhe "
            "vetë paneli, prandaj gjendja e vizualizimit nuk varet nga veprime manuale në "
            "ndërfaqe dhe është pjesë e riprodhueshmërisë."
        ),
        widget("grafana"),
    ),
)


_REPRO = page(
    "riprodhimi",
    "Riprodhimi",
    "Ekzekuto çdo hap të studimit nga këtu, dhe shih se çfarë ekziston në disk.",
    section(
        "konsola",
        "Konsola e ekzekutimit",
        "Shtojca A",
        prose(
            "Çdo njësi e ekzekutueshme e studimit është e deklaruar në një katalog. Konsola "
            "pranon vetëm identifikues nga ai katalog, kurrë një rresht komande, dhe i "
            "ekzekuton ato një nga një sepse eksperimentet konkurrojnë për çdo bërthamë të "
            "makinës."
        ),
        widget("jobs"),
    ),
    section(
        "provenienca",
        "Provenienca e rezultateve",
        "§4.10",
        prose(
            "Çdo eksperiment shkruan një manifest me emrin e ekzekutimit, vulën kohore, SHA-në "
            "e commit-it, hash-in e konfigurimit dhe versionet e paketave. Nëse dy rezultate "
            "vijnë nga commit-e të ndryshme, kjo duket këtu."
        ),
        widget("provenance"),
    ),
    section(
        "punimi",
        "Dokumenti i punimit",
        "",
        prose(
            "Punimi gjenerohet nga i njëjti katalog rezultatesh: tabelat dhe figurat e tij "
            "lexohen nga dosja e rezultateve në kohën e ndërtimit, prandaj dokumenti dhe ky "
            "panel nuk mund të bien ndesh."
        ),
        widget("document"),
        runner("thesis_build"),
    ),
    section(
        "mjedisi",
        "Mjedisi eksperimental",
        "Shtojca H",
        table("environment", "Konfigurimi harduerik dhe softuerik i matjeve."),
    ),
)


PAGES: tuple[dict[str, Any], ...] = (
    _OVERVIEW,
    _DATASET,
    _PROTOCOL,
    _RESULTS,
    _ENSEMBLE,
    _DEPTH,
    _CONFIG,
    _CAUSAL,
    _TIME,
    _STREAM,
    _REPRO,
)

PAGES_BY_ID = {p["id"]: p for p in PAGES}


def navigation() -> list[dict[str, Any]]:
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "subtitle": p["subtitle"],
            "sections": [
                {"id": s["id"], "title": s["title"], "thesis": s["thesis"]} for s in p["sections"]
            ],
        }
        for p in PAGES
    ]


def tables_used(page_payload: dict[str, Any]) -> list[tuple[str, str | None]]:
    """(table name, query) pairs a page needs, deduplicated."""
    seen: dict[tuple[str, str | None], None] = {}
    for sec in page_payload["sections"]:
        for block in sec["blocks"]:
            if block["kind"] in {"table", "chart"} and block.get("source"):
                seen[(block["source"], block.get("query"))] = None
    return list(seen.keys())

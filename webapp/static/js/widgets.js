// Widgets are the blocks that talk to something live: the job runner, the
// docker stack, the database, Grafana, the provenance of the artefacts on
// disk. Everything else on a page is a static read of `results/`.

import { api, followJob } from "./api.js";
import { ago, bytes, clear, duration, el, num, when } from "./util.js";

export function renderWidget(block, context) {
  const widgets = {
    research_questions: researchQuestions,
    services,
    database,
    grafana,
    jobs,
    provenance,
    tour,
    document: documentWidget,
  };
  const widget = widgets[block.widget];
  if (!widget) return el("div");
  return widget(block, context);
}

const loading = (text = "Duke lexuar…") => el("div", { class: "skeleton", "aria-label": text });

function asyncHost(load) {
  const host = el("div", {}, loading());
  load()
    .then((node) => {
      clear(host);
      host.append(node);
    })
    .catch((error) => {
      clear(host);
      host.append(
        el("div", { class: "empty" }, el("strong", { text: "Nuk u lexua dot" }), String(error))
      );
    });
  return host;
}

// ------------------------------------------------------- research questions

function verdictWord(answer) {
  const text = String(answer || "").trim();
  const upper = text.toUpperCase();
  if (upper.startsWith("PO")) return { word: "PO", rest: text.slice(2).trim(), cls: "yes" };
  if (upper.startsWith("JO")) return { word: "JO", rest: text.slice(2).trim(), cls: "no" };
  return { word: "", rest: text, cls: "" };
}

function researchQuestions() {
  return asyncHost(async () => {
    const payload = await api.table("rq_summary");
    if (payload.missing) {
      return el(
        "div",
        { class: "empty" },
        el("strong", { text: "Përgjigjet nuk janë gjeneruar ende" }),
        "Ekzekuto make_rq_summary për t'i parë këtu."
      );
    }
    return el(
      "div",
      { class: "rq" },
      ...payload.rows.map((row) => {
        const verdict = verdictWord(row["Përgjigjja"]);
        return el(
          "div",
          { class: "rq-card" },
          el("div", { class: "tag", text: row["Pyetja"] }),
          el(
            "div",
            {},
            el("div", { class: "q", text: row["Formulimi"] }),
            el(
              "div",
              { class: "a" },
              verdict.word
                ? el("span", { class: `verdict-word ${verdict.cls}`, text: verdict.word })
                : null,
              verdict.word ? " " : "",
              verdict.rest
            ),
            el("div", { class: "e", text: row["Evidenca"] })
          )
        );
      })
    );
  });
}

// --------------------------------------------------------------------- tour

function tour(block, context) {
  const steps = block.payload || [];
  if (!steps.length) {
    return el(
      "div",
      { class: "empty" },
      el("strong", { text: "Udhërrëfyesi kërkon rezultate" }),
      "Ekzekuto të paktën protokollin dhe vlerësimin."
    );
  }
  return el(
    "div",
    { class: "tour" },
    ...steps.map((step) =>
      el(
        "div",
        { class: "tour-step" },
        el("div", { class: "n", text: String(step.index).padStart(2, "0") }),
        el(
          "div",
          {},
          el("div", { class: "t", text: step.title }),
          el("div", { class: "d", text: step.text }),
          el("div", { class: "ev", text: step.evidence })
        ),
        el("button", {
          class: "btn small go",
          text: "Shih provën",
          onClick: () => context.goto(step.page, step.section),
        })
      )
    )
  );
}

// ----------------------------------------------------------------- services

const SERVICE_LABELS = {
  kafka: "Apache Kafka",
  postgres: "PostgreSQL",
  grafana: "Grafana",
};

function services() {
  const host = el("div");

  async function refresh() {
    clear(host);
    host.append(loading());
    let status;
    try {
      status = await api.services();
    } catch (error) {
      clear(host);
      host.append(el("div", { class: "empty" }, String(error)));
      return;
    }
    clear(host);
    const grid = el(
      "div",
      { class: "svc-grid" },
      ...Object.entries(SERVICE_LABELS).map(([key, title]) => {
        const info = status.services[key];
        const tone = info.reachable ? "good" : info.container === "running" ? "warn" : "bad";
        return el(
          "div",
          { class: "svc" },
          el(
            "div",
            { class: "n" },
            el("span", { class: `pill ${tone}` }, el("span", { class: "dot" }), info.reachable ? "aktiv" : "i ndalur"),
            title
          ),
          el("div", { class: "d", text: info.endpoint }),
          el("div", { class: "d", text: `kontejneri: ${info.container}` }),
          key === "grafana" && info.reachable && !info.embeddable
            ? el("div", { class: "d", text: "embedding i çaktivizuar" })
            : null
        );
      })
    );
    const bar = el(
      "div",
      { class: "runner" },
      el("span", {
        class: "lead",
        text: status.all_up
          ? "Të tre shërbimet janë aktive."
          : "Grumbulli nuk është plotësisht aktiv. Ngrije që të mund të ekzekutosh rrjedhën.",
      }),
      el("button", {
        class: "btn small primary",
        text: "docker compose up",
        onClick: async (event) => {
          event.target.disabled = true;
          event.target.textContent = "duke ngritur…";
          await api.compose("up").catch(() => null);
          refresh();
        },
      }),
      el("button", {
        class: "btn small",
        text: "down",
        onClick: async (event) => {
          event.target.disabled = true;
          await api.compose("down").catch(() => null);
          refresh();
        },
      }),
      el("button", { class: "btn small", text: "Rifresko", onClick: refresh })
    );
    host.append(grid, bar);
  }

  refresh();
  return host;
}

// ----------------------------------------------------------------- database

function database() {
  const host = el("div");

  async function refresh() {
    clear(host);
    host.append(loading());
    const payload = await api.database().catch((error) => ({ available: false, reason: String(error) }));
    clear(host);
    if (!payload.available) {
      host.append(
        el(
          "div",
          { class: "empty" },
          el("strong", { text: "Baza e të dhënave nuk është e arritshme" }),
          payload.reason || ""
        ),
        el("div", { class: "runner" }, el("button", { class: "btn small", text: "Rifresko", onClick: refresh }))
      );
      return;
    }
    if (payload.empty) {
      host.append(
        el(
          "div",
          { class: "empty" },
          el("strong", { text: "Baza është bosh" }),
          "Ekzekuto një rrjedhë me persistim që të mbushen tabelat."
        ),
        el("div", { class: "runner" }, el("button", { class: "btn small", text: "Rifresko", onClick: refresh }))
      );
      return;
    }
    const summary = payload.summary || {};
    const tiles = [
      ["Ngjarje të pikëzuara", summary.events],
      ["Alarme", summary.alerts],
      ["Alarme që janë mashtrime", summary.true_alerts],
      ["Mashtrime në rrjedhë", summary.frauds],
      ["Ekzekutime", summary.runs],
      ["Modele", summary.models],
    ].map(([label, value]) =>
      el(
        "div",
        { class: "tile" },
        el("div", { class: "label", text: label }),
        el("div", { class: "value", text: Number(value || 0).toLocaleString("sq") })
      )
    );

    const runsTable = el(
      "table",
      { class: "data" },
      el(
        "thead",
        el(
          "tr",
          ...["Ekzekutimi", "Modeli", "Ngjarje", "Alarme", "Mashtrime", "e2e mes. (ms)", "E fundit"].map(
            (text) => el("th", { text })
          )
        )
      ),
      el(
        "tbody",
        ...(payload.runs || []).map((run) =>
          el(
            "tr",
            el("td", { text: run.run_tag }),
            el("td", { text: run.model }),
            el("td", { class: "num", text: Number(run.events || 0).toLocaleString("sq") }),
            el("td", { class: "num", text: String(run.alerts ?? 0) }),
            el("td", { class: "num", text: String(run.frauds ?? 0) }),
            el("td", { class: "num", text: num(run.e2e_mean, 1) }),
            el("td", { text: ago(run.last_seen) })
          )
        )
      )
    );

    host.append(
      el("div", { class: "tiles" }, ...tiles),
      el(
        "div",
        { class: "card" },
        el(
          "div",
          { class: "card-head" },
          el("h4", { text: "Ekzekutimet e fundit në bazë" }),
          el("span", { class: "spacer" }),
          el("button", { class: "btn small", text: "Rifresko", onClick: refresh })
        ),
        el("div", { class: "table-wrap" }, runsTable)
      )
    );
  }

  refresh();
  return host;
}

// ------------------------------------------------------------------ grafana

function grafana() {
  return asyncHost(async () => {
    const status = await api.services();
    const info = status.services.grafana;
    const url = `${status.grafana_url}/d/${status.dashboard_uid}/?orgId=1&kiosk&refresh=10s`;
    if (!info.reachable) {
      return el(
        "div",
        { class: "empty" },
        el("strong", { text: "Grafana nuk është aktive" }),
        "Ngrije grumbullin docker nga seksioni i mësipërm, pastaj rifresko këtë faqe."
      );
    }
    const header = el(
      "div",
      { class: "card-head" },
      el("h4", { text: "Streaming Anomaly Detection · Pipeline Monitor" }),
      el("span", { class: "spacer" }),
      el("span", { class: "pill good" }, el("span", { class: "dot" }), `Grafana ${info.version || ""}`),
      el("a", { class: "btn small", href: url.replace("&kiosk", ""), target: "_blank", text: "Hap veçmas" })
    );
    if (!info.embeddable) {
      return el(
        "div",
        { class: "card" },
        header,
        el(
          "div",
          { class: "empty" },
          el("strong", { text: "Paneli nuk mund të futet brenda faqes" }),
          "Grafana e ndalon këtë nëse allow_embedding është i çaktivizuar. Hape veçmas me butonin më sipër."
        )
      );
    }
    return el(
      "div",
      { class: "card" },
      header,
      el("div", { class: "frame-wrap" }, el("iframe", { src: url, title: "Grafana" }))
    );
  });
}

// --------------------------------------------------------------------- jobs

const STATUS_LABELS = {
  pending: "në radhë",
  running: "duke ekzekutuar",
  done: "përfundoi",
  failed: "dështoi",
  cancelled: "u ndal",
};

function lineClass(line) {
  if (line.startsWith("===")) return "l-step";
  if (line.startsWith("$")) return "l-cmd";
  if (line.startsWith("[ok]") || line.startsWith("[përfundoi]")) return "l-ok";
  if (line.startsWith("[gabim]")) return "l-err";
  if (line.startsWith("[radha]")) return "l-queue";
  return "";
}

function jobs(block, context) {
  const console_ = el("div", { class: "console" });
  const head = el("div", { class: "card-head" });
  const steps = el("div");
  const queueHost = el("div");
  const historyHost = el("div");
  const catalogHost = el("div");
  let stop = null;
  let follows = null;

  function appendLines(lines) {
    const atBottom = console_.scrollHeight - console_.scrollTop - console_.clientHeight < 40;
    for (const line of lines) {
      console_.append(el("div", { class: lineClass(line), text: line || " " }));
    }
    if (atBottom) console_.scrollTop = console_.scrollHeight;
  }

  function renderSteps(job) {
    clear(steps);
    if (!job || !job.steps || job.steps.length < 2) return;
    const done = job.steps.filter((s) => s.status === "done").length;
    steps.append(
      el("div", { class: "progress" }, el("span", { style: `width:${(100 * done) / job.steps.length}%` })),
      el("div", {
        class: "card-note",
        text: `${done}/${job.steps.length} hapa · ${job.steps.map((s) => s.title).slice(done, done + 1)[0] || ""}`,
      })
    );
  }

  function renderHead(job) {
    clear(head);
    head.append(el("h4", { text: job ? job.label : "Asnjë punë aktive" }));
    head.append(el("span", { class: "spacer" }));
    if (job) {
      head.append(el("span", { class: `status ${job.status}`, text: STATUS_LABELS[job.status] || job.status }));
      if (job.status === "running" || job.status === "pending") {
        head.append(
          el("button", {
            class: "btn small danger",
            text: "Ndale",
            onClick: () => api.cancel(job.id).catch(() => null),
          })
        );
      }
    }
    head.append(el("button", { class: "btn small", text: "Rifresko", onClick: refresh }));
  }

  function attach(jobId) {
    if (follows === jobId) return;
    stop?.();
    follows = jobId;
    clear(console_);
    stop = followJob(jobId, {
      onLog: appendLines,
      onState: (job) => {
        renderHead(job);
        renderSteps(job);
      },
      onEnd: () => {
        follows = null;
        context.onJobFinished?.();
        refresh();
      },
    });
  }

  async function refresh() {
    const state = await api.jobs().catch(() => null);
    if (!state) return;
    context.onJobsState?.(state);
    renderHead(state.active);
    renderSteps(state.active);
    if (state.active) attach(state.active.id);
    else if (!follows) clear(steps);

    clear(queueHost);
    if (state.queued.length) {
      queueHost.append(
        el("div", { class: "card-note", text: `Në radhë: ${state.queued.length}` }),
        ...state.queued.map((job) =>
          el(
            "div",
            { class: "job-row" },
            el("div", { class: "grow" }, el("div", { class: "name", text: job.label })),
            el("span", { class: "status pending", text: "në radhë" }),
            el("button", {
              class: "btn small danger",
              text: "Hiqe",
              onClick: () => api.cancel(job.id).then(refresh).catch(() => null),
            })
          )
        )
      );
    }

    clear(historyHost);
    const finished = state.recent.filter((job) => job.status !== "running");
    if (finished.length) {
      historyHost.append(
        ...finished.slice(0, 8).map((job) =>
          el(
            "div",
            { class: "job-row" },
            el(
              "div",
              { class: "grow" },
              el("div", { class: "name", text: job.label }),
              el("div", {
                class: "meta",
                text: `${when(job.started || job.created)} · ${job.n_steps} hapa${job.error ? ` · ${job.error}` : ""}`,
              })
            ),
            el("span", { class: `status ${job.status}`, text: STATUS_LABELS[job.status] || job.status }),
            el("button", {
              class: "btn small",
              text: "Shih",
              onClick: () => {
                stop?.();
                follows = null;
                api.job(job.id).then((full) => {
                  clear(console_);
                  appendLines(full.lines || []);
                  renderHead(full);
                  renderSteps(full);
                });
              },
            })
          )
        )
      );
    }
  }

  async function renderCatalog() {
    const payload = await api.catalog().catch(() => null);
    if (!payload) return;
    clear(catalogHost);
    catalogHost.append(
      el(
        "div",
        { class: "runner" },
        el("span", { class: "lead", text: "Grupe të gatshme:" }),
        ...payload.batches.map((batch) =>
          el(
            "span",
            { class: "exp" },
            el("button", {
              class: "btn small",
              text: batch.title,
              title: batch.subtitle,
              onClick: () => context.run(batch.id),
            }),
            el("span", { class: "cost", text: `${batch.members.length} hapa` })
          )
        )
      )
    );
    for (const group of payload.groups) {
      catalogHost.append(
        el(
          "div",
          { class: "cat-group" },
          el("h4", { text: group.title }),
          el("p", { text: group.subtitle }),
          el(
            "div",
            { class: "cat-grid" },
            ...group.experiments.map((experiment) =>
              el(
                "div",
                { class: "cat-card" },
                el("div", { class: "t", text: experiment.title }),
                el("div", { class: "q", text: experiment.question }),
                el(
                  "div",
                  { class: "f" },
                  el("span", { class: "cost", text: duration(experiment.minutes) }),
                  experiment.docker ? el("span", { class: "pill", text: "docker" }) : null,
                  el("span", { class: "spacer" }),
                  el("button", {
                    class: "btn small",
                    text: "Ekzekuto",
                    title: experiment.command,
                    onClick: () => context.run(experiment.id),
                  })
                )
              )
            )
          )
        )
      );
    }
  }

  refresh();
  renderCatalog();
  context.registerJobRefresh?.(refresh);

  return el(
    "div",
    {},
    el("div", { class: "card" }, head, steps, console_),
    queueHost,
    el(
      "div",
      { class: "card" },
      el("div", { class: "card-head" }, el("h4", { text: "Historiku i ekzekutimeve" })),
      historyHost
    ),
    catalogHost
  );
}

// --------------------------------------------------------------- provenance

function provenance(block, context) {
  return asyncHost(async () => {
    const payload = await api.provenance();
    const counts = payload.inventory.counts;
    const tiles = [
      ["Tabela", counts.tables],
      ["Figura", counts.figures],
      ["Verdikte", counts.verdicts],
      ["Manifeste", counts.manifests],
      ["Fold-e të ruajtura", counts.folds],
      ["Ekzekutime rrjedhe", counts.latency_runs],
    ].map(([label, value]) =>
      el(
        "div",
        { class: "tile" },
        el("div", { class: "label", text: label }),
        el("div", { class: "value", text: String(value) })
      )
    );

    const stale = payload.staleness || { stale: [], never_run: [] };
    const staleCard = stale.stale.length
      ? el(
          "div",
          { class: "callout warn" },
          el("h4", { text: `${stale.stale.length} rezultate janë më të vjetra se hyrjet e tyre` }),
          el("p", {
            text:
              "Një rezultat i llogaritur përpara se hyrja e tij të rigjenerohej nuk është i " +
              "gabuar në ndonjë mënyrë që lexuesi e sheh; ai thjesht përshkruan një version " +
              "të mëparshëm të studimit. Rigjeneroji përpara dorëzimit.",
          }),
          el(
            "div",
            { class: "runner", style: "border-style:solid" },
            ...stale.stale.map((item) =>
              el(
                "span",
                { class: "exp" },
                el("button", {
                  class: "btn small",
                  text: item.title,
                  title: `më i vjetër se: ${item.newer_inputs.map((n) => n.id).join(", ")}`,
                  onClick: () => context.run(item.id),
                }),
                el("span", {
                  class: "cost",
                  text: `më i vjetër se ${item.newer_inputs.map((n) => n.id).join(", ")}`,
                })
              )
            )
          )
        )
      : el(
          "div",
          { class: "callout" },
          el("p", {
            text: `Asnjë rezultat nuk është më i vjetër se hyrjet e veta; ${stale.known} ekzekutime janë kontrolluar.`,
          })
        );

    const mixed = payload.distinct_commits.length > 1;
    const table = el(
      "table",
      { class: "data" },
      el(
        "thead",
        el("tr", ...["Ekzekutimi", "Kur", "Commit", "Hash i konfigurimit"].map((text) => el("th", { text })))
      ),
      el(
        "tbody",
        ...payload.runs.map((run) =>
          el(
            "tr",
            el("td", { text: run.run }),
            el("td", { text: when(run.timestamp) }),
            el("td", { text: run.git_sha_short || "—" }),
            el("td", { text: run.config_sha_short || "—" })
          )
        )
      )
    );

    return el(
      "div",
      {},
      el("div", { class: "tiles" }, ...tiles),
      staleCard,
      mixed
        ? el(
            "div",
            { class: "callout warn" },
            el("h4", { text: "Rezultatet vijnë nga commit-e të ndryshme" }),
            el("p", {
              text: `Në disk ndodhen artefakte nga ${payload.distinct_commits.length} commit-e: ${payload.distinct_commits.join(", ")}. Kjo është normale gjatë punës, por përpara dorëzimit ia vlen një ri-ekzekutim i plotë.`,
            })
          )
        : el(
            "div",
            { class: "callout" },
            el("p", {
              text: `Të gjitha artefaktet vijnë nga i njëjti commit (${payload.distinct_commits[0] || "—"}) dhe i njëjti konfigurim.`,
            })
          ),
      el(
        "div",
        { class: "card" },
        el("div", { class: "card-head" }, el("h4", { text: "Manifestet e ekzekutimeve" })),
        el("div", { class: "table-wrap" }, table)
      )
    );
  });
}

// ----------------------------------------------------------------- document

function documentWidget() {
  return asyncHost(async () => {
    const meta = await api.meta();
    const doc = meta.document || {};
    if (!doc.docx && !doc.pdf) {
      return el(
        "div",
        { class: "empty" },
        el("strong", { text: "Dokumenti nuk është ndërtuar ende" }),
        "Ekzekuto ndërtimin e punimit më poshtë."
      );
    }
    const rows = el("dl", { class: "kv" });
    for (const [key, value] of Object.entries(doc)) {
      if (!value) continue;
      rows.append(
        el("dt", { text: key.toUpperCase() }),
        el("dd", { text: `${bytes(value.bytes)} · ${when(value.modified)}` })
      );
    }
    return el(
      "div",
      { class: "card" },
      el(
        "div",
        { class: "card-head" },
        el("h4", { text: "Punimi i Diplomës" }),
        el("span", { class: "spacer" }),
        doc.docx ? el("a", { class: "btn small", href: "/api/thesis/docx", text: "Shkarko .docx" }) : null,
        doc.pdf ? el("a", { class: "btn small primary", href: "/api/thesis/pdf", target: "_blank", text: "Hap PDF" }) : null
      ),
      rows
    );
  });
}

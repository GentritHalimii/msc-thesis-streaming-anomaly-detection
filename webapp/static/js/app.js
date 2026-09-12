// Shell: navigation, page rendering, the global job indicator, the theme,
// and the presentation mode used when the panel is shown on a projector.

import { api } from "./api.js";
import { renderBlock } from "./blocks.js";
import { setChartLabels } from "./charts.js";
import { ago, clear, el } from "./util.js";

const state = {
  meta: null,
  page: null,
  jobRefresh: null,
  present: false,
};

// ------------------------------------------------------------------- theme

function initTheme() {
  const stored = localStorage.getItem("panel-theme");
  if (stored) document.documentElement.dataset.theme = stored;
  else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.dataset.theme = "dark";
  }
}

function toggleTheme() {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("panel-theme", next);
  renderTopbar();
}

// --------------------------------------------------------------- job status

let jobTimer = null;

async function pollJobs() {
  try {
    const jobs = await api.jobs();
    renderJobPill(jobs);
  } catch {
    /* the panel keeps working without the runner */
  }
}

function renderJobPill(jobs) {
  const host = document.getElementById("job-pill");
  if (!host) return;
  clear(host);
  const active = jobs.active;
  if (!active) {
    const failed = (jobs.recent || []).find((job) => job.status === "failed");
    if (failed) {
      host.append(
        el(
          "button",
          { class: "pill bad", onClick: () => go("riprodhimi", "konsola") },
          el("span", { class: "dot" }),
          `${failed.label} dështoi`
        )
      );
    }
    return;
  }
  const label =
    active.n_steps > 1 ? `${active.label} · ${active.n_done}/${active.n_steps}` : active.label;
  host.append(
    el(
      "button",
      { class: "pill live", title: "shko te konsola", onClick: () => go("riprodhimi", "konsola") },
      el("span", { class: "dot" }),
      label
    )
  );
}

async function run(target) {
  try {
    await api.run(target);
  } catch (error) {
    alert(`Nuk u nis: ${error.message}`);
    return;
  }
  await pollJobs();
  state.jobRefresh?.();
  if (state.page?.id !== "riprodhimi") {
    const host = document.getElementById("job-pill");
    host?.animate(
      [{ opacity: 0.3 }, { opacity: 1 }],
      { duration: 420, iterations: 2 }
    );
  }
}

// ------------------------------------------------------------------ routing

function currentRoute() {
  const hash = location.hash.replace(/^#\/?/, "");
  const [page, section] = hash.split("/");
  return { page: page || state.meta?.navigation[0]?.id, section };
}

function go(page, section) {
  location.hash = section ? `#/${page}/${section}` : `#/${page}`;
}

// ------------------------------------------------------------------ sidebar

function renderSidebar() {
  const host = document.getElementById("nav");
  clear(host);
  const { page: activePage } = currentRoute();
  state.meta.navigation.forEach((page, index) => {
    const button = el(
      "button",
      {
        class: "nav-item",
        "aria-current": page.id === activePage ? "page" : null,
        onClick: () => go(page.id),
      },
      el("span", { class: "idx", text: String(index + 1).padStart(2, "0") }),
      page.title
    );
    host.append(button);
    if (page.id === activePage && page.sections.length > 1) {
      host.append(
        el(
          "div",
          { class: "nav-sub" },
          ...page.sections.map((section) =>
            el("button", { text: section.title, onClick: () => go(page.id, section.id) })
          )
        )
      );
    }
  });

  const foot = document.getElementById("sidebar-foot");
  clear(foot);
  const inv = state.meta.inventory;
  foot.append(
    el("div", { class: "row" }, el("span", { text: "tabela" }), el("span", { text: String(inv.counts.tables) })),
    el("div", { class: "row" }, el("span", { text: "figura" }), el("span", { text: String(inv.counts.figures) })),
    el(
      "div",
      { class: "row" },
      el("span", { text: "rezultati i fundit" }),
      el("span", { text: ago(inv.newest_artifact) })
    )
  );
}

// ------------------------------------------------------------------- topbar

function renderTopbar() {
  const host = document.getElementById("topbar");
  clear(host);
  const { page } = currentRoute();
  const nav = state.meta.navigation.find((entry) => entry.id === page);
  host.append(
    el("strong", { style: "font-size:14px", text: nav ? nav.title : "Paneli" }),
    el("span", { class: "spacer" }),
    el("span", { id: "job-pill" }),
    el("button", {
      class: "btn small",
      text: state.present ? "Dil nga prezantimi" : "Prezantim",
      onClick: togglePresent,
    }),
    el("button", {
      class: "btn small",
      title: "ndërro temën",
      text: document.documentElement.dataset.theme === "dark" ? "Dritë" : "Errësirë",
      onClick: toggleTheme,
    }),
    el("button", { class: "btn small", text: "Rifresko", onClick: () => renderPage(true) })
  );
  pollJobs();
}

// -------------------------------------------------------------- presentation

function togglePresent() {
  state.present = !state.present;
  document.body.classList.toggle("present", state.present);
  renderTopbar();
  if (state.present) {
    document.getElementById("present-bar").hidden = false;
    focusSection(0);
  } else {
    document.getElementById("present-bar").hidden = true;
  }
}

let presentIndex = 0;

function sectionNodes() {
  return [...document.querySelectorAll(".content .section")];
}

function focusSection(index) {
  const nodes = sectionNodes();
  if (!nodes.length) return;
  presentIndex = Math.max(0, Math.min(index, nodes.length - 1));
  nodes[presentIndex].scrollIntoView({ behavior: "smooth", block: "start" });
  const position = document.getElementById("present-pos");
  if (position) position.textContent = `${presentIndex + 1} / ${nodes.length}`;
}

function presentStep(delta) {
  const nodes = sectionNodes();
  const next = presentIndex + delta;
  if (next >= 0 && next < nodes.length) {
    focusSection(next);
    return;
  }
  const pages = state.meta.navigation.map((entry) => entry.id);
  const here = pages.indexOf(currentRoute().page);
  const target = here + Math.sign(delta);
  if (target >= 0 && target < pages.length) {
    go(pages[target]);
    setTimeout(() => focusSection(delta > 0 ? 0 : sectionNodes().length - 1), 260);
  }
}

// ---------------------------------------------------------------- rendering

async function renderPage(force = false) {
  const { page: pageId, section } = currentRoute();
  const host = document.getElementById("content");
  if (!force && state.page && state.page.id === pageId) {
    if (section) scrollToSection(section);
    return;
  }
  clear(host);
  host.append(el("div", { class: "skeleton", style: "height:220px" }));
  let payload;
  try {
    payload = await api.page(pageId);
  } catch (error) {
    clear(host);
    host.append(el("div", { class: "empty" }, el("strong", { text: "Faqja nuk u lexua" }), String(error)));
    return;
  }
  state.page = payload;
  const context = {
    tables: payload.tables,
    colors: state.meta.colors,
    run,
    goto: go,
    registerJobRefresh: (fn) => {
      state.jobRefresh = fn;
    },
    onJobFinished: () => {
      api.meta().then((meta) => {
        state.meta = meta;
        renderSidebar();
      });
      if (state.page?.id !== "riprodhimi") renderPage(true);
    },
  };

  clear(host);
  host.append(
    el(
      "div",
      { class: "page-head" },
      el("h2", { text: payload.title }),
      el("p", { text: payload.subtitle })
    )
  );
  for (const sec of payload.sections) {
    const node = el(
      "section",
      { class: "section", id: `s-${sec.id}` },
      el(
        "div",
        { class: "section-head" },
        el("h3", { text: sec.title }),
        sec.thesis ? el("span", { class: "thesis-ref", text: `Punimi ${sec.thesis}` }) : null
      ),
      ...sec.blocks.map((block) => renderBlock(block, context))
    );
    host.append(node);
  }
  renderSidebar();
  renderTopbar();
  if (section) scrollToSection(section);
  else window.scrollTo({ top: 0 });
  if (state.present) focusSection(0);
}

function scrollToSection(id) {
  const node = document.getElementById(`s-${id}`);
  if (node) node.scrollIntoView({ behavior: "smooth", block: "start" });
}

// --------------------------------------------------------------------- boot

async function boot() {
  initTheme();
  try {
    state.meta = await api.meta();
  } catch (error) {
    document.getElementById("content").append(
      el("div", { class: "empty" }, el("strong", { text: "Serveri nuk u përgjigj" }), String(error))
    );
    return;
  }
  setChartLabels(state.meta.labels);
  document.getElementById("brand-title").textContent = state.meta.title;
  document.getElementById("brand-sub").textContent = state.meta.subtitle;
  if (!location.hash) go(state.meta.navigation[0].id);
  renderSidebar();
  renderTopbar();
  await renderPage(true);

  window.addEventListener("hashchange", () => renderPage());
  document.getElementById("present-prev").addEventListener("click", () => presentStep(-1));
  document.getElementById("present-next").addEventListener("click", () => presentStep(1));
  document.getElementById("present-exit").addEventListener("click", togglePresent);
  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, select, textarea")) return;
    if (event.key === "p" && (event.metaKey || event.ctrlKey)) return;
    if (state.present && (event.key === "ArrowRight" || event.key === "PageDown")) presentStep(1);
    if (state.present && (event.key === "ArrowLeft" || event.key === "PageUp")) presentStep(-1);
    if (event.key === "Escape" && state.present) togglePresent();
  });
  jobTimer = setInterval(pollJobs, 3000);
  window.addEventListener("beforeunload", () => clearInterval(jobTimer));
}

boot();

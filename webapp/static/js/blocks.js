// Renderers for the block kinds that `webapp/content.py` declares.
//
// A block names an artefact; the server has already read it. Nothing here
// knows anything about the study, which is why adding a section to the panel
// is a change to one Python list and not to this file.

import { renderChart } from "./charts.js";
import { ago, bytes, el, num, when } from "./util.js";
import { renderWidget } from "./widgets.js";

export function renderBlock(block, context) {
  const renderers = {
    prose,
    callout,
    verdict,
    metrics,
    table: dataTable,
    figure,
    chart,
    runner,
    widget: (b, c) => renderWidget(b, c),
  };
  const renderer = renderers[block.kind];
  if (!renderer) return el("div");
  try {
    return renderer(block, context) || el("div");
  } catch (error) {
    return el(
      "div",
      { class: "empty" },
      el("strong", { text: "Ky bllok nuk u vizatua dot" }),
      String(error)
    );
  }
}

function prose(block) {
  return el("div", { class: "prose" }, ...block.paragraphs.map((text) => el("p", { text })));
}

function callout(block) {
  return el(
    "div",
    { class: `callout ${block.tone || "note"}` },
    block.title ? el("h4", { text: block.title }) : null,
    el("p", { text: block.text })
  );
}

function verdict(block) {
  if (!block.payload) {
    return el(
      "div",
      { class: "empty" },
      el("strong", { text: "Verdikti nuk ekziston ende" }),
      "Ai shkruhet nga vetë eksperimenti; ekzekutoje atë për ta parë."
    );
  }
  return el(
    "div",
    { class: "verdict" },
    el("h4", { text: block.title || "Verdikti i matur" }),
    el("p", { text: block.payload.text }),
    el("div", {
      class: "src",
      text: `${block.payload.file.path} · ${when(block.payload.file.modified)} · i gjeneruar nga kodi, jo i shkruar me dorë`,
    })
  );
}

function metrics(block) {
  const tiles = block.payload || [];
  if (!tiles.length) return el("div");
  return el(
    "div",
    { class: "tiles" },
    ...tiles.map((tile) =>
      el(
        "div",
        { class: `tile ${tile.tone || ""}` },
        el("div", { class: "label", text: tile.label }),
        el(
          "div",
          { class: "value" },
          String(tile.value),
          tile.unit ? el("span", { class: "unit", text: tile.unit }) : null
        ),
        tile.hint ? el("div", { class: "hint", text: tile.hint }) : null
      )
    )
  );
}

function missingTable(name) {
  return el(
    "div",
    { class: "empty" },
    el("strong", { text: `Tabela "${name}" nuk ekziston ende` }),
    "Ekzekuto eksperimentin që e prodhon për ta parë këtu."
  );
}

function figure(block) {
  if (!block.payload || !block.payload.png) {
    return el(
      "div",
      { class: "empty" },
      el("strong", { text: "Figura nuk ekziston ende" }),
      `Ajo prodhohet nga eksperimenti përkatës (${block.source}).`
    );
  }
  const image = el("img", {
    src: `${block.url}?v=${encodeURIComponent(block.payload.png.modified)}`,
    alt: block.caption || block.source,
    loading: "lazy",
  });
  return el(
    "div",
    { class: "card" },
    el(
      "div",
      { class: "card-head" },
      el("h4", { text: "Figura e punimit" }),
      el("span", { class: "spacer" }),
      el("span", {
        class: "pill",
        text: `${ago(block.payload.png.modified)} · ${bytes(block.payload.png.bytes)}`,
      }),
      el("a", { class: "btn small", href: block.pdf_url, text: "PDF" })
    ),
    el(
      "figure",
      { class: "thesis-figure" },
      image,
      block.caption ? el("figcaption", { text: block.caption }) : null
    )
  );
}

function chart(block, context) {
  const payload = context.tables[block.table_key];
  const host = el("div");
  const card = el(
    "div",
    { class: "card" },
    el(
      "div",
      { class: "card-head" },
      el("h4", { text: "Grafik interaktiv" }),
      el("span", { class: "spacer" }),
      payload && !payload.missing
        ? el("span", { class: "pill", text: `${payload.n_rows} rreshta · ${block.source}.csv` })
        : null,
      payload && payload.download
        ? el("a", { class: "btn small", href: payload.download, text: "CSV" })
        : null
    ),
    host
  );
  renderChart(host, block, payload, context.colors);
  return card;
}

function formatCell(value, column, block) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "po" : "jo";
  if (typeof value !== "number") return String(value);
  const digits = block.round && block.round[column];
  if (digits !== undefined) return value.toFixed(digits);
  if (Number.isInteger(value) && Math.abs(value) < 1e7) return String(value);
  return num(value);
}

function dataTable(block, context) {
  const payload = context.tables[block.table_key];
  if (!payload || payload.missing) return missingTable(block.source);

  let columns = payload.columns.map((column) => column.key);
  if (block.columns && block.columns.length) {
    columns = block.columns.filter((column) => columns.includes(column));
  }
  const numeric = new Set(payload.columns.filter((c) => c.numeric).map((c) => c.key));
  let rows = [...payload.rows];
  if (block.max_rows) rows = rows.slice(0, block.max_rows);

  const state = { sort: null, dir: 1 };
  const body = el("tbody");

  // The supervised reference is an upper bound, not a competitor, so it is
  // never marked as the best row even when it holds the largest value.
  const skip = new Set(block.highlight_skip || []);
  const eligible = rows.filter((row) => !columns.some((column) => skip.has(row[column])));
  const best =
    block.highlight && numeric.has(block.highlight)
      ? Math.max(
          ...eligible.map((row) =>
            typeof row[block.highlight] === "number" ? row[block.highlight] : -Infinity
          )
        )
      : null;

  function fill() {
    body.replaceChildren();
    const ordered = state.sort
      ? [...rows].sort((a, b) => {
          const left = a[state.sort];
          const right = b[state.sort];
          if (left === null || left === undefined) return 1;
          if (right === null || right === undefined) return -1;
          if (typeof left === "number" && typeof right === "number") return (left - right) * state.dir;
          return String(left).localeCompare(String(right), "sq") * state.dir;
        })
      : rows;
    for (const row of ordered) {
      const isBest =
        best !== null &&
        row[block.highlight] === best &&
        !columns.some((column) => skip.has(row[column]));
      const cells = columns.map((column) => {
        const value = row[column];
        const swatch = context.colors && context.colors[value];
        return el(
          "td",
          { class: `${numeric.has(column) ? "num" : ""}${swatch ? " swatch-cell" : ""}` },
          swatch ? el("span", { class: "swatch", style: `background:${swatch}` }) : null,
          formatCell(value, column, block)
        );
      });
      body.append(el("tr", { class: isBest ? "best" : "" }, ...cells));
    }
  }

  const head = el(
    "tr",
    ...columns.map((column) =>
      el(
        "th",
        {
          class: numeric.has(column) ? "num" : "",
          title: "kliko për të renditur",
          onClick: () => {
            state.dir = state.sort === column ? -state.dir : numeric.has(column) ? -1 : 1;
            state.sort = column;
            fill();
            for (const th of head.children) th.querySelector(".sort")?.remove();
            const index = columns.indexOf(column);
            head.children[index].append(
              el("span", { class: "sort", text: state.dir > 0 ? "▲" : "▼" })
            );
          },
        },
        (block.labels && block.labels[column]) || column
      )
    )
  );
  fill();

  return el(
    "div",
    { class: "card" },
    el(
      "div",
      { class: "card-head" },
      el("h4", { text: block.caption || block.source }),
      el("span", { class: "spacer" }),
      el("span", { class: "pill", text: `${payload.n_rows} rreshta` }),
      el("a", { class: "btn small", href: payload.download, text: "CSV" })
    ),
    el("div", { class: "table-wrap" }, el("table", { class: "data" }, el("thead", head), body)),
    el("div", {
      class: "card-note",
      text: `Burimi: ${payload.file.path} · përditësuar ${when(payload.file.modified)}`,
    })
  );
}

function runner(block, context) {
  const experiments = block.payload || [];
  if (!experiments.length) return el("div");
  return el(
    "div",
    { class: "runner" },
    el("span", { class: "lead", text: "Rigjenero këtë seksion:" }),
    ...experiments.map((experiment) =>
      el(
        "span",
        { class: "exp" },
        el("button", {
          class: "btn small",
          text: experiment.title,
          title: `${experiment.command}${experiment.docker ? " · kërkon docker" : ""}`,
          onClick: () => context.run(experiment.id),
        }),
        el("span", {
          class: "cost",
          text: experiment.minutes >= 60 ? `~${(experiment.minutes / 60).toFixed(1)} orë` : `~${experiment.minutes} min`,
        })
      )
    )
  );
}

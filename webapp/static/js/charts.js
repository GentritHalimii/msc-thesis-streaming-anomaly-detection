// Interactive charts drawn as SVG, with no charting library.
//
// Two reasons for hand-drawing them. The panel must work with no network at
// all, which rules out a CDN and makes a vendored bundle dead weight; and the
// series colours have to be exactly the ones the thesis figures use, which is
// easier to guarantee when nothing sits between the palette and the mark.
//
// Every chart reads a table as it came from the CSV. Nothing is precomputed.

import { clear, colorFor, compact, el, isNum, num, svg } from "./util.js";

// ------------------------------------------------------------------ tooltip

let tipNode = null;
function tip() {
  if (!tipNode) {
    tipNode = el("div", { class: "tooltip" });
    document.body.append(tipNode);
  }
  return tipNode;
}

function showTip(event, title, rows) {
  const node = tip();
  clear(node);
  if (title) node.append(el("div", { class: "t-title", text: title }));
  for (const [key, value] of rows) {
    node.append(
      el("div", { class: "t-row" }, el("span", { text: key }), el("strong", { text: value }))
    );
  }
  node.classList.add("on");
  moveTip(event);
}

function moveTip(event) {
  const node = tip();
  const pad = 14;
  const width = node.offsetWidth;
  const height = node.offsetHeight;
  let x = event.clientX + pad;
  let y = event.clientY + pad;
  if (x + width > window.innerWidth - 8) x = event.clientX - width - pad;
  if (y + height > window.innerHeight - 8) y = event.clientY - height - pad;
  node.style.left = `${Math.max(8, x)}px`;
  node.style.top = `${Math.max(8, y)}px`;
}

function hideTip() {
  tip().classList.remove("on");
}

function interactive(node, title, rows) {
  node.addEventListener("mouseenter", (event) => showTip(event, title, rows));
  node.addEventListener("mousemove", moveTip);
  node.addEventListener("mouseleave", hideTip);
  return node;
}

// ------------------------------------------------------------------- scales

const linear = (d0, d1, r0, r1) => {
  const span = d1 - d0 || 1;
  return (value) => r0 + ((value - d0) / span) * (r1 - r0);
};

const logScale = (d0, d1, r0, r1) => {
  const l0 = Math.log10(Math.max(d0, 1e-12));
  const l1 = Math.log10(Math.max(d1, 1e-12));
  const span = l1 - l0 || 1;
  return (value) => r0 + ((Math.log10(Math.max(value, 1e-12)) - l0) / span) * (r1 - r0);
};

function niceTicks(min, max, count = 5) {
  if (!Number.isFinite(min) || !Number.isFinite(max) || min === max) {
    return [min || 0];
  }
  const raw = (max - min) / count;
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const normalized = raw / magnitude;
  const step = (normalized >= 7.5 ? 10 : normalized >= 3.5 ? 5 : normalized >= 1.5 ? 2 : 1) * magnitude;
  const start = Math.ceil(min / step) * step;
  const ticks = [];
  for (let value = start; value <= max + step * 1e-6; value += step) {
    ticks.push(Math.round(value / step) * step);
  }
  return ticks;
}

function logTicks(min, max) {
  const ticks = [];
  const lo = Math.floor(Math.log10(Math.max(min, 1e-12)));
  const hi = Math.ceil(Math.log10(Math.max(max, 1e-12)));
  for (let power = lo; power <= hi; power += 1) {
    const base = 10 ** power;
    if (base >= min * 0.95 && base <= max * 1.05) ticks.push(base);
  }
  if (ticks.length < 2) return niceTicks(min, max, 4);
  return ticks;
}

function extent(values, padFraction = 0.08, includeZero = false) {
  const clean = values.filter(isNum);
  if (!clean.length) return [0, 1];
  let min = Math.min(...clean);
  let max = Math.max(...clean);
  if (includeZero) min = Math.min(min, 0);
  if (min === max) {
    const pad = Math.abs(min) * 0.1 || 1;
    return [min - pad, max + pad];
  }
  const pad = (max - min) * padFraction;
  return [min - pad, max + pad];
}

// -------------------------------------------------------------------- axes

function axisBottom(x, ticks, y, formatter) {
  const group = svg("g", { class: "axis" });
  group.append(svg("line", { x1: 0, x2: 0, y1: y, y2: y }));
  for (const tick of ticks) {
    const px = x(tick);
    group.append(
      svg(
        "g",
        { class: "tick", transform: `translate(${px},${y})` },
        svg("line", { y2: 5, stroke: "currentColor", opacity: 0.35 }),
        svg("text", { y: 18, "text-anchor": "middle", text: formatter(tick) })
      )
    );
  }
  return group;
}

function axisLeft(y, ticks, formatter) {
  const group = svg("g", { class: "axis" });
  for (const tick of ticks) {
    const py = y(tick);
    group.append(
      svg(
        "g",
        { class: "tick", transform: `translate(0,${py})` },
        svg("line", { x2: -5, stroke: "currentColor", opacity: 0.35 }),
        svg("text", { x: -9, dy: "0.32em", "text-anchor": "end", text: formatter(tick) })
      )
    );
  }
  return group;
}

function gridLines(y, ticks, width) {
  const group = svg("g", { class: "grid" });
  for (const tick of ticks) {
    group.append(svg("line", { x1: 0, x2: width, y1: y(tick), y2: y(tick) }));
  }
  return group;
}

function label(text, x, y, rotate = 0) {
  return svg("text", {
    class: "axis-label",
    x,
    y,
    "text-anchor": "middle",
    transform: rotate ? `rotate(${rotate},${x},${y})` : null,
    text,
  });
}

// ------------------------------------------------------------------ legend

function legend(items, onToggle) {
  const node = el("div", { class: "chart-legend" });
  items.forEach((item, index) => {
    const chip = el(
      "span",
      { class: `item${item.off ? " off" : ""}`, title: "kliko për ta fshehur" },
      el("span", { class: "key", style: `background:${item.color}` }),
      el("span", { text: item.label })
    );
    if (onToggle) chip.addEventListener("click", () => onToggle(index));
    node.append(chip);
  });
  return node;
}

// ------------------------------------------------------------------- entry

/** Raw CSV keys such as "iforest" become the names the thesis uses. */
let LABELS = {};
export function setChartLabels(labels) {
  LABELS = labels || {};
}
const pretty = (value) => LABELS[value] || String(value);

export function renderChart(host, spec, tablePayload, palette) {
  clear(host);
  if (!tablePayload || tablePayload.missing) {
    host.append(
      el(
        "div",
        { class: "empty" },
        el("strong", { text: "Kjo tabelë nuk ekziston ende" }),
        `Ekzekuto eksperimentin që e prodhon (${spec.source}) për ta parë këtë grafik.`
      )
    );
    return;
  }
  const state = { hidden: new Set(), facet: null };
  const rows = tablePayload.rows || [];

  if (spec.facet) {
    const values = [...new Set(rows.map((r) => r[spec.facet]).filter((v) => v !== null))];
    state.facet = values[0];
    const bar = el(
      "div",
      { class: "facet-bar" },
      el("label", { text: `${spec.facet}:` }),
      el(
        "select",
        {
          class: "facet",
          onChange: (event) => {
            state.facet = event.target.value;
            draw();
          },
        },
        ...values.map((value) => el("option", { value, text: String(value) }))
      )
    );
    host.append(bar);
  }

  if (spec.title) host.append(el("p", { class: "chart-title", text: spec.title }));
  const plot = el("div", { class: "chart-host" });
  const legendHost = el("div");
  host.append(plot, legendHost);

  function draw() {
    const width = Math.max(plot.clientWidth || host.clientWidth || 720, 320);
    let data = rows;
    if (spec.facet && state.facet !== null) {
      data = rows.filter((row) => String(row[spec.facet]) === String(state.facet));
    }
    const context = {
      spec,
      rows: data,
      palette,
      width,
      state,
      legendHost,
      redraw: draw,
      columns: (tablePayload.columns || []).map((column) => column.key),
    };
    clear(plot);
    clear(legendHost);
    const drawers = { bars, barsh, grouped, line, scatter, heatmap };
    const drawer = drawers[spec.chart] || bars;
    const node = drawer(context);
    if (node) plot.append(node);
  }

  draw();
  const observer = new ResizeObserver(() => draw());
  observer.observe(plot);
  host._chartObserver = observer;
}

// ------------------------------------------------------------ vertical bars

function bars(ctx) {
  const { spec, rows, width } = ctx;
  const height = spec.height || 320;
  const margin = { top: 12, right: 14, bottom: 56, left: 62 };
  const inner = { w: width - margin.left - margin.right, h: height - margin.top - margin.bottom };
  const labels = rows.map((row) => pretty(row[spec.label]));
  const values = rows.map((row) => row[spec.value]);
  const errors = spec.error ? rows.map((row) => row[spec.error] || 0) : null;
  const upper = values.map((value, index) => (isNum(value) ? value + (errors ? errors[index] : 0) : 0));
  const [, max] = extent(upper, 0.12, true);
  const y = linear(0, max, inner.h, 0);
  const step = inner.w / Math.max(labels.length, 1);
  const barWidth = Math.min(step * 0.68, 74);
  const ticks = niceTicks(0, max, 5);

  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, height });
  const g = svg("g", { transform: `translate(${margin.left},${margin.top})` });
  g.append(gridLines(y, ticks, inner.w));

  rows.forEach((row, index) => {
    const value = row[spec.value];
    if (!isNum(value)) return;
    const cx = step * (index + 0.5);
    const color = spec.colorByLabel ? colorFor(labels[index], ctx.palette, index) : spec.color || "#2a78d6";
    const top = y(Math.max(value, 0));
    const rect = svg("rect", {
      x: cx - barWidth / 2,
      y: top,
      width: barWidth,
      height: Math.max(y(0) - top, 1),
      fill: color,
      rx: 2,
    });
    g.append(
      interactive(rect, labels[index], [
        [spec.ylabel || "vlera", num(value)],
        ...(errors && errors[index] ? [["s.d.", num(errors[index])]] : []),
      ])
    );
    if (errors && errors[index]) {
      const lo = y(value - errors[index]);
      const hi = y(value + errors[index]);
      g.append(svg("line", { x1: cx, x2: cx, y1: lo, y2: hi, stroke: "currentColor", opacity: 0.45 }));
      g.append(svg("line", { x1: cx - 4, x2: cx + 4, y1: hi, y2: hi, stroke: "currentColor", opacity: 0.45 }));
    }
    g.append(
      svg("text", { class: "value-label", x: cx, y: top - 5, "text-anchor": "middle", text: compact(value) })
    );
  });

  const tickLabels = svg("g", { class: "axis" });
  labels.forEach((text, index) => {
    tickLabels.append(
      svg("g", { class: "tick" }, svg("text", {
        x: step * (index + 0.5),
        y: inner.h + 18,
        "text-anchor": "middle",
        text,
      }))
    );
  });
  g.append(tickLabels);
  g.append(axisLeft(y, ticks, (value) => compact(value)));
  g.append(svg("line", { class: "axis", x1: 0, x2: inner.w, y1: inner.h, y2: inner.h, stroke: "currentColor", opacity: 0.35 }));
  if (spec.xlabel) g.append(label(spec.xlabel, inner.w / 2, inner.h + 44));
  if (spec.ylabel) g.append(label(spec.ylabel, -46, inner.h / 2, -90));
  root.append(g);
  return root;
}

// ---------------------------------------------------------- horizontal bars

function barsh(ctx) {
  const { spec, width } = ctx;
  let rows = ctx.rows.filter((row) => isNum(row[spec.value]));
  if (spec.sort) {
    rows = [...rows].sort((a, b) =>
      spec.sort === "asc" ? a[spec.value] - b[spec.value] : b[spec.value] - a[spec.value]
    );
  }
  if (spec.limit) rows = rows.slice(0, spec.limit);

  const labels = rows.map((row) =>
    spec.groupLabel ? `${row[spec.groupLabel]} · ${pretty(row[spec.label])}` : pretty(row[spec.label])
  );
  const longest = Math.max(...labels.map((text) => text.length), 6);
  const margin = { top: 8, right: 58, bottom: 40, left: Math.min(Math.max(longest * 6.6, 90), 260) };
  const rowHeight = 26;
  const height = margin.top + margin.bottom + rows.length * rowHeight;
  const inner = { w: Math.max(width - margin.left - margin.right, 120), h: rows.length * rowHeight };

  const errors = spec.error ? rows.map((row) => row[spec.error] || 0) : null;
  const upper = rows.map((row, index) => row[spec.value] + (errors ? errors[index] : 0));
  const lower = rows.map((row, index) => row[spec.value] - (errors ? errors[index] : 0));
  const [minRaw, max] = extent([...upper, ...lower], 0.1, true);
  const min = Math.min(minRaw, 0);
  const x = linear(min, max, 0, inner.w);
  const ticks = niceTicks(min, max, 5);

  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, height });
  const g = svg("g", { transform: `translate(${margin.left},${margin.top})` });
  for (const tick of ticks) {
    g.append(svg("line", { class: "grid", x1: x(tick), x2: x(tick), y1: 0, y2: inner.h, stroke: "currentColor", opacity: 0.12 }));
  }

  rows.forEach((row, index) => {
    const value = row[spec.value];
    const cy = index * rowHeight + rowHeight / 2;
    const color = spec.colorByLabel
      ? colorFor(String(row[spec.label]), ctx.palette, index)
      : spec.color || "#2a78d6";
    const x0 = x(Math.min(0, value));
    const x1 = x(Math.max(0, value));
    const rect = svg("rect", {
      x: x0,
      y: cy - 8,
      width: Math.max(x1 - x0, 1),
      height: 16,
      fill: color,
      rx: 2,
    });
    g.append(
      interactive(rect, labels[index], [
        [spec.xlabel || "vlera", num(value)],
        ...(errors && errors[index] ? [["s.d.", num(errors[index])]] : []),
      ])
    );
    if (errors && errors[index]) {
      g.append(svg("line", { x1: x(value - errors[index]), x2: x(value + errors[index]), y1: cy, y2: cy, stroke: "currentColor", opacity: 0.4 }));
    }
    const labelX = errors && errors[index] ? Math.max(x1, x(value + errors[index])) : x1;
    g.append(svg("text", { class: "value-label", x: labelX + 7, y: cy, dy: "0.33em", text: num(value) }));
    g.append(
      svg("text", {
        class: "tick",
        x: -10,
        y: cy,
        dy: "0.33em",
        "text-anchor": "end",
        fill: "currentColor",
        "font-size": 11.5,
        opacity: 0.75,
        text: labels[index],
      })
    );
  });

  g.append(axisBottom(x, ticks, inner.h, (value) => compact(value)));
  if (spec.xlabel) g.append(label(spec.xlabel, inner.w / 2, inner.h + 34));
  root.append(g);
  return root;
}

// ------------------------------------------------------------- grouped bars

function seriesFromSpec(spec, rows) {
  if (spec.pivot) {
    const keys = [...new Set(rows.map((row) => row[spec.pivot.column]))];
    return keys.map((key, index) => ({
      key,
      label: pretty(key),
      color: null,
      pick: (row) => (String(row[spec.pivot.column]) === String(key) ? row[spec.pivot.value] : null),
      index,
    }));
  }
  return (spec.series || []).map((entry, index) => ({
    key: entry.col,
    label: entry.label || entry.col,
    color: entry.color,
    pick: (row) => row[entry.col],
    index,
  }));
}

function grouped(ctx) {
  const { spec, rows, width, state } = ctx;
  const height = spec.height || 340;
  const series = seriesFromSpec(spec, rows).filter((s) => !state.hidden.has(s.label));
  const allSeries = seriesFromSpec(spec, rows);

  let groups;
  if (spec.pivot) {
    const names = [...new Set(rows.map((row) => String(row[spec.index])))];
    groups = names.map((name) => ({
      name,
      values: series.map((s) => {
        const match = rows.find(
          (row) => String(row[spec.index]) === name && s.pick(row) !== null && s.pick(row) !== undefined
        );
        return match ? s.pick(match) : null;
      }),
    }));
  } else {
    groups = rows.map((row) => ({
      name: pretty(row[spec.index]),
      values: series.map((s) => s.pick(row)),
    }));
  }

  const flat = groups.flatMap((group) => group.values).filter(isNum);
  const [, max] = extent(flat, 0.12, true);
  const longest = Math.max(...groups.map((group) => group.name.length), 4);
  const rotate = longest > 12 && groups.length > 3;
  const margin = { top: 12, right: 14, bottom: rotate ? 92 : 58, left: 62 };
  const inner = { w: width - margin.left - margin.right, h: height - margin.top - margin.bottom };
  const y = linear(0, max, inner.h, 0);
  const ticks = niceTicks(0, max, 5);
  const step = inner.w / Math.max(groups.length, 1);
  const barWidth = Math.min((step * 0.78) / Math.max(series.length, 1), 46);

  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, height });
  const g = svg("g", { transform: `translate(${margin.left},${margin.top})` });
  g.append(gridLines(y, ticks, inner.w));

  groups.forEach((group, gi) => {
    const center = step * (gi + 0.5);
    const total = series.length * barWidth;
    series.forEach((s, si) => {
      const value = group.values[si];
      if (!isNum(value)) return;
      const x = center - total / 2 + si * barWidth;
      const top = y(Math.max(value, 0));
      const color = s.color || colorFor(s.label, ctx.palette, s.index);
      const rect = svg("rect", {
        x: x + 1,
        y: top,
        width: Math.max(barWidth - 2, 1),
        height: Math.max(y(0) - top, 1),
        fill: color,
        rx: 2,
      });
      g.append(interactive(rect, group.name, [[s.label, num(value)]]));
    });
  });

  const tickGroup = svg("g", { class: "axis" });
  groups.forEach((group, gi) => {
    const x = step * (gi + 0.5);
    tickGroup.append(
      svg("g", { class: "tick" }, svg("text", {
        x,
        y: inner.h + 16,
        "text-anchor": rotate ? "end" : "middle",
        transform: rotate ? `rotate(-35,${x},${inner.h + 16})` : null,
        text: group.name,
      }))
    );
  });
  g.append(tickGroup);
  g.append(axisLeft(y, ticks, (value) => compact(value)));
  g.append(svg("line", { x1: 0, x2: inner.w, y1: inner.h, y2: inner.h, stroke: "currentColor", opacity: 0.35 }));
  if (spec.ylabel) g.append(label(spec.ylabel, -46, inner.h / 2, -90));
  root.append(g);

  ctx.legendHost.append(
    legend(
      allSeries.map((s) => ({
        label: s.label,
        color: s.color || colorFor(s.label, ctx.palette, s.index),
        off: state.hidden.has(s.label),
      })),
      (index) => {
        const key = allSeries[index].label;
        if (state.hidden.has(key)) state.hidden.delete(key);
        else state.hidden.add(key);
        ctx.redraw();
      }
    )
  );
  return root;
}

// -------------------------------------------------------------------- lines

function line(ctx) {
  const { spec, rows, width, state } = ctx;
  const height = spec.height || 340;
  const margin = { top: 12, right: 16, bottom: 58, left: 66 };
  const inner = { w: width - margin.left - margin.right, h: height - margin.top - margin.bottom };

  let seriesList;
  if (spec.group) {
    const keys = [...new Set(rows.map((row) => String(row[spec.group])))];
    seriesList = keys.map((key, index) => ({
      label: pretty(key),
      key,
      color: spec.colorByGroup ? colorFor(key, ctx.palette, index) : null,
      index,
      points: rows
        .filter((row) => String(row[spec.group]) === key)
        .map((row) => ({ x: row[spec.x], y: row[spec.y], e: null }))
        .filter((point) => isNum(point.x) && isNum(point.y))
        .sort((a, b) => a.x - b.x),
    }));
  } else {
    seriesList = (spec.series || []).map((entry, index) => ({
      label: entry.label || entry.col,
      color: entry.color,
      index,
      points: rows
        .map((row) => ({
          x: row[spec.x],
          y: row[entry.col],
          e: spec.error && spec.error[entry.col] ? row[spec.error[entry.col]] : null,
        }))
        .filter((point) => isNum(point.x) && isNum(point.y))
        .sort((a, b) => a.x - b.x),
    }));
  }

  const visible = seriesList.filter((s) => !state.hidden.has(s.label) && s.points.length);
  const xs = visible.flatMap((s) => s.points.map((p) => p.x));
  const ys = visible.flatMap((s) => s.points.flatMap((p) => [p.y, p.y + (p.e || 0), p.y - (p.e || 0)]));
  for (const ref of spec.refs || []) ys.push(ref.y);

  const [x0, x1] = spec.logx ? [Math.min(...xs), Math.max(...xs)] : extent(xs, 0.04);
  const [y0raw, y1] = spec.logy ? [Math.min(...ys.filter((v) => v > 0)), Math.max(...ys)] : extent(ys, 0.1);
  const y0 = spec.logy ? y0raw : Math.min(y0raw, spec.zero === false ? y0raw : 0);
  const x = spec.logx ? logScale(x0, x1, 0, inner.w) : linear(x0, x1, 0, inner.w);
  const y = spec.logy ? logScale(y0, y1, inner.h, 0) : linear(y0, y1, inner.h, 0);
  const xTicks = spec.logx ? logTicks(x0, x1) : niceTicks(x0, x1, 6);
  const yTicks = spec.logy ? logTicks(y0, y1) : niceTicks(y0, y1, 5);

  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, height });
  const g = svg("g", { transform: `translate(${margin.left},${margin.top})` });
  g.append(gridLines(y, yTicks, inner.w));

  for (const ref of spec.refs || []) {
    if (ref.y < y0 || ref.y > y1) continue;
    g.append(svg("line", { class: "ref-line", x1: 0, x2: inner.w, y1: y(ref.y), y2: y(ref.y) }));
    if (ref.label) {
      g.append(svg("text", { class: "ref-label", x: 4, y: y(ref.y) - 5, text: ref.label }));
    }
  }

  visible.forEach((s) => {
    const color = s.color || colorFor(s.label, ctx.palette, s.index);
    const path = s.points.map((p, i) => `${i ? "L" : "M"}${x(p.x)},${y(p.y)}`).join(" ");
    g.append(svg("path", { d: path, fill: "none", stroke: color, "stroke-width": 2, "stroke-linejoin": "round" }));
    s.points.forEach((point) => {
      if (point.e) {
        g.append(
          svg("line", {
            x1: x(point.x),
            x2: x(point.x),
            y1: y(point.y - point.e),
            y2: y(point.y + point.e),
            stroke: color,
            opacity: 0.4,
          })
        );
      }
      if (spec.markers !== false) {
        const dot = svg("circle", { cx: x(point.x), cy: y(point.y), r: 3.4, fill: color });
        g.append(
          interactive(dot, s.label, [
            [spec.xlabel || "x", num(point.x)],
            [spec.ylabel || "y", num(point.y)],
          ])
        );
      }
    });
  });

  g.append(axisBottom(x, xTicks, inner.h, (value) => compact(value)));
  g.append(axisLeft(y, yTicks, (value) => compact(value)));
  if (spec.xlabel) g.append(label(spec.xlabel, inner.w / 2, inner.h + 44));
  if (spec.ylabel) g.append(label(spec.ylabel, -50, inner.h / 2, -90));
  root.append(g);

  if (seriesList.length > 1) {
    ctx.legendHost.append(
      legend(
        seriesList.map((s) => ({
          label: s.label,
          color: s.color || colorFor(s.label, ctx.palette, s.index),
          off: state.hidden.has(s.label),
        })),
        (index) => {
          const key = seriesList[index].label;
          if (state.hidden.has(key)) state.hidden.delete(key);
          else state.hidden.add(key);
          ctx.redraw();
        }
      )
    );
  }
  return root;
}

// ------------------------------------------------------------------ scatter

function scatter(ctx) {
  const { spec, rows, width } = ctx;
  const height = spec.height || 340;
  const margin = { top: 14, right: 22, bottom: 58, left: 66 };
  const inner = { w: width - margin.left - margin.right, h: height - margin.top - margin.bottom };
  const points = rows
    .map((row, index) => ({
      x: row[spec.x],
      y: row[spec.y],
      label: spec.label ? pretty(row[spec.label]) : `#${index + 1}`,
      index,
    }))
    .filter((point) => isNum(point.x) && isNum(point.y));

  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const [x0, x1] = spec.logx ? [Math.min(...xs) * 0.6, Math.max(...xs) * 1.6] : extent(xs, 0.12);
  const [y0, y1] = extent(ys, 0.14, true);
  const x = spec.logx ? logScale(x0, x1, 0, inner.w) : linear(x0, x1, 0, inner.w);
  const y = linear(y0, y1, inner.h, 0);
  const xTicks = spec.logx ? logTicks(x0, x1) : niceTicks(x0, x1, 5);
  const yTicks = niceTicks(y0, y1, 5);

  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, height });
  const g = svg("g", { transform: `translate(${margin.left},${margin.top})` });
  g.append(gridLines(y, yTicks, inner.w));
  for (const tick of xTicks) {
    g.append(svg("line", { class: "grid", x1: x(tick), x2: x(tick), y1: 0, y2: inner.h }));
  }

  points.forEach((point) => {
    const color = spec.colorByLabel ? colorFor(point.label, ctx.palette, point.index) : spec.color || "#2a78d6";
    const dot = svg("circle", { cx: x(point.x), cy: y(point.y), r: 6.5, fill: color, "fill-opacity": 0.9 });
    g.append(
      interactive(dot, point.label, [
        [spec.xlabel || "x", num(point.x)],
        [spec.ylabel || "y", num(point.y)],
      ])
    );
    g.append(
      svg("text", {
        class: "value-label",
        x: x(point.x) + 10,
        y: y(point.y) - 8,
        text: point.label,
      })
    );
  });

  g.append(axisBottom(x, xTicks, inner.h, (value) => compact(value)));
  g.append(axisLeft(y, yTicks, (value) => compact(value)));
  if (spec.xlabel) g.append(label(spec.xlabel, inner.w / 2, inner.h + 44));
  if (spec.ylabel) g.append(label(spec.ylabel, -50, inner.h / 2, -90));
  root.append(g);
  return root;
}

// ------------------------------------------------------------------ heatmap

function heatmap(ctx) {
  const { spec, rows, width } = ctx;
  const columns = (ctx.columns || Object.keys(rows[0] || {})).filter((key) => key !== spec.rowKey);
  const values = rows.flatMap((row) => columns.map((column) => row[column])).filter(isNum);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const cellH = 40;
  const margin = { top: 24, right: 16, bottom: 54, left: 66 };
  const height = margin.top + margin.bottom + rows.length * cellH;
  const inner = { w: width - margin.left - margin.right, h: rows.length * cellH };
  const cellW = inner.w / Math.max(columns.length, 1);

  const ramp = (value) => {
    if (!isNum(value)) return "transparent";
    const t = max === min ? 0.5 : (value - min) / (max - min);
    const from = [244, 249, 244];
    const to = [11, 92, 56];
    const mix = from.map((channel, index) => Math.round(channel + (to[index] - channel) * t));
    return `rgb(${mix.join(",")})`;
  };

  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, height });
  const g = svg("g", { transform: `translate(${margin.left},${margin.top})` });

  rows.forEach((row, ri) => {
    columns.forEach((column, ci) => {
      const value = row[column];
      const rect = svg("rect", {
        x: ci * cellW + 1,
        y: ri * cellH + 1,
        width: cellW - 2,
        height: cellH - 2,
        fill: ramp(value),
        rx: 2,
      });
      g.append(
        interactive(rect, `${spec.ylabel || spec.rowKey} ${row[spec.rowKey]} · ${spec.xlabel || ""} ${column}`, [
          [spec.valueLabel || "vlera", num(value)],
        ])
      );
      if (isNum(value)) {
        const t = max === min ? 0.5 : (value - min) / (max - min);
        g.append(
          svg("text", {
            x: ci * cellW + cellW / 2,
            y: ri * cellH + cellH / 2,
            dy: "0.34em",
            "text-anchor": "middle",
            "font-size": 11,
            "font-family": "var(--mono)",
            fill: t > 0.55 ? "#ffffff" : "#191817",
            text: num(value, 3),
          })
        );
      }
    });
  });

  const axis = svg("g", { class: "axis" });
  columns.forEach((column, ci) => {
    axis.append(
      svg("g", { class: "tick" }, svg("text", {
        x: ci * cellW + cellW / 2,
        y: inner.h + 18,
        "text-anchor": "middle",
        text: column,
      }))
    );
  });
  rows.forEach((row, ri) => {
    axis.append(
      svg("g", { class: "tick" }, svg("text", {
        x: -10,
        y: ri * cellH + cellH / 2,
        dy: "0.33em",
        "text-anchor": "end",
        text: String(row[spec.rowKey]),
      }))
    );
  });
  g.append(axis);
  if (spec.xlabel) g.append(label(spec.xlabel, inner.w / 2, inner.h + 42));
  if (spec.ylabel) g.append(label(spec.ylabel, -48, inner.h / 2, -90));
  root.append(g);
  return root;
}

// Small shared helpers: element construction, number and date formatting.
// Albanian locale formatting throughout, so the panel and the document agree.

/** True only for `{...}` literals, so an element or an array is never
 *  mistaken for an attribute bag. */
const isAttrs = (value) =>
  value !== null &&
  typeof value === "object" &&
  !value.nodeType &&
  !Array.isArray(value) &&
  (value.constructor === Object || value.constructor === undefined);

export const el = (tag, ...rest) => {
  const node = document.createElement(tag);
  const attrs = isAttrs(rest[0]) ? rest.shift() : {};
  const children = rest;
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else if (key === "text") node.textContent = value;
    else if (key === "dataset") Object.assign(node.dataset, value);
    else if (key.startsWith("on") && typeof value === "function") {
      node.addEventListener(key.slice(2).toLowerCase(), value);
    } else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
};

export const svg = (tag, ...rest) => {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  const attrs = isAttrs(rest[0]) ? rest.shift() : {};
  const children = rest;
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child) node.append(child);
  }
  return node;
};

export const clear = (node) => {
  while (node.firstChild) node.removeChild(node.firstChild);
  return node;
};

/** Significant-figure formatting that keeps columns readable. */
export function num(value, digits = null) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  if (typeof value !== "number") return String(value);
  if (digits !== null) return value.toFixed(digits);
  const abs = Math.abs(value);
  if (abs === 0) return "0";
  if (abs >= 1e6) return value.toExponential(2);
  if (abs >= 1000) return value.toLocaleString("sq", { maximumFractionDigits: 0 });
  if (abs >= 100) return value.toFixed(1);
  if (abs >= 1) return value.toFixed(2);
  if (abs >= 0.001) return value.toFixed(4);
  return value.toExponential(2);
}

export function compact(value) {
  if (typeof value !== "number") return String(value ?? "—");
  const abs = Math.abs(value);
  if (abs >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (abs >= 1e3) return `${(value / 1e3).toFixed(abs >= 1e4 ? 0 : 1)}k`;
  if (abs >= 1) return String(Math.round(value * 100) / 100);
  return num(value);
}

export function when(iso) {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return String(iso);
  return date.toLocaleString("sq", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ago(iso) {
  if (!iso) return "";
  const seconds = (Date.now() - new Date(iso).getTime()) / 1000;
  if (Number.isNaN(seconds)) return "";
  if (seconds < 60) return "pak sekonda më parë";
  if (seconds < 3600) return `${Math.round(seconds / 60)} min më parë`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)} orë më parë`;
  return `${Math.round(seconds / 86400)} ditë më parë`;
}

export function duration(minutes) {
  if (!minutes) return "";
  if (minutes < 60) return `~${minutes} min`;
  const hours = minutes / 60;
  return `~${hours % 1 === 0 ? hours : hours.toFixed(1)} orë`;
}

export function bytes(value) {
  if (!value && value !== 0) return "—";
  const units = ["B", "kB", "MB", "GB"];
  let index = 0;
  let size = value;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(size >= 100 || index === 0 ? 0 : 1)} ${units[index]}`;
}

export const isNum = (value) => typeof value === "number" && Number.isFinite(value);

/** Stable colour for a label not covered by the shared model palette. */
const FALLBACK = ["#2a78d6", "#1baf7a", "#4a3aa7", "#d98c1f", "#b3352c", "#1c7c53", "#7c7871"];
export function colorFor(label, palette, index = 0) {
  if (palette && palette[label]) return palette[label];
  return FALLBACK[index % FALLBACK.length];
}

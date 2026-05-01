// F50 — Inspector sidebar: OCR / NLP / Nakdan / Voice tabs.
//
// Exports:
//   loadInspector(pageJson, audioJson)  — populates all 4 tab panels
//   syncInspectorWord(markId)           — highlights the active OCR row

/**
 * Populate all inspector tab panels from pipeline JSON data.
 *
 * @param {Object|null} pageJson  — parsed page.json (may be null in stub mode)
 * @param {Object|null} audioJson — parsed audio.json (may be null in stub mode)
 */
export function loadInspector(pageJson, audioJson) {
  _populateOcrTab(pageJson);
  _populateNlpTab(pageJson);
  _populateNakdanTab(pageJson);
  _populateVoiceTab(audioJson);
}

/**
 * Highlight the OCR row matching markId and scroll it into view.
 *
 * @param {string|null} markId
 */
export function syncInspectorWord(markId) {
  const panel = document.getElementById("tab-ocr");
  if (!panel) return;
  const prev = panel.querySelector("tr.active");
  if (prev) prev.classList.remove("active");
  if (!markId) return;
  const row = panel.querySelector(`tr[data-mark-id="${CSS.escape(markId)}"]`);
  if (!row) return;
  row.classList.add("active");
  row.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

// ---------------------------------------------------------------------------
// Tab builders
// ---------------------------------------------------------------------------

function _populateOcrTab(pageJson) {
  const panel = document.getElementById("tab-ocr");
  if (!panel) return;
  panel.innerHTML = "";

  const words = pageJson && Array.isArray(pageJson.words) ? pageJson.words : [];
  const markMap = _buildMarkMap(pageJson);

  if (words.length === 0) {
    panel.appendChild(_emptyMsg("OCR data unavailable"));
    return;
  }

  const tbl = _createTable(["Text", "Conf", "Lang", "BBox"]);
  const tbody = tbl.querySelector("tbody");

  words.forEach((w, idx) => {
    const markId = markMap[idx] ?? null;
    const tr = _makeOcrRow(w, markId);
    tbody.appendChild(tr);
  });

  panel.appendChild(tbl);
}

function _makeOcrRow(word, markId) {
  const tr = document.createElement("tr");
  if (markId) tr.setAttribute("data-mark-id", markId);

  const bbox = Array.isArray(word.bbox) ? word.bbox.join(", ") : "—";
  const conf = word.confidence !== undefined ? String(word.confidence) : "—";
  const lang = word.lang ?? "—";
  const text = word.text ?? word.word ?? "—";

  [text, conf, lang, bbox].forEach((val) => {
    const td = document.createElement("td");
    td.dir = "auto";
    td.textContent = val;
    tr.appendChild(td);
  });

  return tr;
}

function _populateNlpTab(pageJson) {
  const panel = document.getElementById("tab-nlp");
  if (!panel) return;
  panel.innerHTML = "";

  const tokens = pageJson && Array.isArray(pageJson.nlp_tokens) ? pageJson.nlp_tokens : [];

  if (tokens.length === 0) {
    panel.appendChild(_emptyMsg("NLP data unavailable"));
    return;
  }

  const tbl = _createTable(["Token", "POS", "Lemma", "Morph", "Conf"]);
  const tbody = tbl.querySelector("tbody");

  tokens.forEach((tok) => {
    const tr = document.createElement("tr");
    const conf = tok.confidence !== undefined ? String(tok.confidence) : "—";
    [tok.token ?? "—", tok.pos ?? "—", tok.lemma ?? "—", tok.morph ?? "—", conf].forEach((v) => {
      const td = document.createElement("td");
      td.dir = "auto";
      td.textContent = v;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  panel.appendChild(tbl);
}

function _populateNakdanTab(pageJson) {
  const panel = document.getElementById("tab-nakdan");
  if (!panel) return;
  panel.innerHTML = "";

  const text = pageJson && pageJson.diacritized_text ? pageJson.diacritized_text : null;

  if (!text) {
    panel.appendChild(_emptyMsg("Diacritization unavailable"));
    return;
  }

  const p = document.createElement("p");
  p.dir = "rtl";
  p.textContent = text;
  panel.appendChild(p);
}

function _populateVoiceTab(audioJson) {
  const panel = document.getElementById("tab-voice");
  if (!panel) return;
  panel.innerHTML = "";

  const timings = audioJson && Array.isArray(audioJson.timings) ? audioJson.timings : [];

  if (timings.length === 0) {
    panel.appendChild(_emptyMsg("Voice timing data unavailable"));
    return;
  }

  const tbl = _createTable(["Mark ID", "Start (s)", "End (s)"]);
  const tbody = tbl.querySelector("tbody");

  timings.forEach((t) => {
    const tr = document.createElement("tr");
    const endVal = t.end_s !== null && t.end_s !== undefined ? String(t.end_s) : "—";
    [t.mark_id ?? "—", String(t.start_s ?? "—"), endVal].forEach((v) => {
      const td = document.createElement("td");
      td.textContent = v;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  panel.appendChild(tbl);
}

// ---------------------------------------------------------------------------
// DOM helpers (CC ≤ 5 each)
// ---------------------------------------------------------------------------

function _createTable(headers) {
  const tbl = document.createElement("table");
  tbl.className = "inspector-table";

  const thead = document.createElement("thead");
  const hrow = document.createElement("tr");
  headers.forEach((h) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = h;
    hrow.appendChild(th);
  });
  thead.appendChild(hrow);
  tbl.appendChild(thead);
  tbl.appendChild(document.createElement("tbody"));

  return tbl;
}

function _emptyMsg(text) {
  const p = document.createElement("p");
  p.className = "inspector-empty";
  p.textContent = text;
  return p;
}

/**
 * Build a word-index → mark_id lookup from pageJson.marks_to_word_index.
 * Returns an inverted map: wordIndex → markId.
 *
 * @param {Object|null} pageJson
 * @returns {Record<number, string>}
 */
function _buildMarkMap(pageJson) {
  const fwd = pageJson && pageJson.marks_to_word_index ? pageJson.marks_to_word_index : {};
  const inv = {};
  for (const [markId, wordIdx] of Object.entries(fwd)) {
    inv[wordIdx] = markId;
  }
  return inv;
}

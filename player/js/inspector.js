// F50 — Inspector sidebar: OCR / NLP-per-model / Nakdan / Voice tabs.
//
// Exports:
//   loadInspector(pageJson, audioJson)  — populates all panels + dynamic NLP tabs
//   syncInspectorWord(markId)           — highlights the active OCR row

const NLP_TAB_PREFIX = "tab-nlp-";
const NLP_BTN_CLASS  = "nlp-model-tab";

export function loadInspector(pageJson, audioJson) {
  _populateOcrTab(pageJson);
  _rebuildNlpTabs(pageJson);
  _populateNakdanTab(pageJson);
  _populateVoiceTab(audioJson);
}

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
// Dynamic NLP tabs — one per model in pageJson.nlp_models
// ---------------------------------------------------------------------------

function _rebuildNlpTabs(pageJson) {
  const tablist  = document.getElementById("inspector-tabs");
  const content  = document.getElementById("inspector-content");
  if (!tablist || !content) return;

  // Remove any previously-created NLP model tabs + panels
  tablist.querySelectorAll(`.${NLP_BTN_CLASS}`).forEach((b) => b.remove());
  content.querySelectorAll(`[id^="${NLP_TAB_PREFIX}"]`).forEach((p) => p.remove());

  const models = pageJson && Array.isArray(pageJson.nlp_models) ? pageJson.nlp_models : [];

  if (models.length === 0) {
    _addNlpTabSlot(tablist, content, "nlp-0", "NLP", []);
    return;
  }

  models.forEach((model, idx) => {
    const tabId = `${NLP_TAB_PREFIX}${idx}`;
    const label = model.name || `NLP ${idx + 1}`;
    _addNlpTabSlot(tablist, content, `nlp-${idx}`, label, model.tokens || []);
  });

  // Wire tab-click for new buttons
  _initNlpTabClicks(tablist);
}

function _addNlpTabSlot(tablist, content, key, label, tokens) {
  const btn = document.createElement("button");
  btn.role = "tab";
  btn.dataset.tab = key;
  btn.setAttribute("aria-controls", `tab-${key}`);
  btn.setAttribute("aria-selected", "false");
  btn.className = NLP_BTN_CLASS;
  btn.textContent = label;
  tablist.appendChild(btn);

  const panel = document.createElement("div");
  panel.id = `tab-${key}`;
  panel.setAttribute("role", "tabpanel");
  panel.setAttribute("aria-label", label);
  panel.hidden = true;
  _fillNlpPanel(panel, tokens);
  content.appendChild(panel);
}

function _fillNlpPanel(panel, tokens) {
  panel.innerHTML = "";
  if (!tokens.length) {
    panel.appendChild(_emptyMsg("NLP data unavailable"));
    return;
  }
  const tbl   = _createTable(["Token", "POS", "Lemma", "Morph", "Conf"]);
  const tbody = tbl.querySelector("tbody");
  tokens.forEach((tok) => {
    const tr   = document.createElement("tr");
    const morph = tok.morph ? JSON.stringify(tok.morph) : "—";
    const conf  = tok.confidence !== undefined ? tok.confidence.toFixed(2) : "—";
    [tok.text ?? "—", tok.pos ?? "—", tok.lemma ?? "—", morph, conf].forEach((v) => {
      const td = document.createElement("td");
      td.dir   = "auto";
      td.textContent = typeof v === "object" ? JSON.stringify(v) : v;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  panel.appendChild(tbl);
}

function _initNlpTabClicks(tablist) {
  const allTabs = tablist.querySelectorAll("[role='tab']");
  tablist.querySelectorAll(`.${NLP_BTN_CLASS}`).forEach((btn) => {
    btn.addEventListener("click", () => {
      allTabs.forEach((t) => {
        const isActive = t === btn;
        t.setAttribute("aria-selected", isActive ? "true" : "false");
        const p = document.getElementById(`tab-${t.dataset.tab}`);
        if (p) p.hidden = !isActive;
      });
    });
  });
}

// ---------------------------------------------------------------------------
// OCR tab
// ---------------------------------------------------------------------------

function _populateOcrTab(pageJson) {
  const panel = document.getElementById("tab-ocr");
  if (!panel) return;
  panel.innerHTML = "";

  const words   = pageJson && Array.isArray(pageJson.words) ? pageJson.words : [];
  const markMap = _buildMarkMap(pageJson);

  if (words.length === 0) { panel.appendChild(_emptyMsg("OCR data unavailable")); return; }

  const tbl   = _createTable(["Text", "Conf", "Lang", "BBox"]);
  const tbody = tbl.querySelector("tbody");
  words.forEach((w, idx) => { tbody.appendChild(_makeOcrRow(w, markMap[idx] ?? null)); });
  panel.appendChild(tbl);
}

function _makeOcrRow(word, markId) {
  const tr   = document.createElement("tr");
  if (markId) tr.setAttribute("data-mark-id", markId);
  const bbox = Array.isArray(word.bbox) ? word.bbox.join(", ") : "—";
  const conf = word.confidence !== undefined ? String(word.confidence) : "—";
  [word.text ?? "—", conf, word.lang_hint ?? "—", bbox].forEach((v) => {
    const td = document.createElement("td"); td.dir = "auto"; td.textContent = v; tr.appendChild(td);
  });
  return tr;
}

// ---------------------------------------------------------------------------
// Nakdan tab
// ---------------------------------------------------------------------------

function _populateNakdanTab(pageJson) {
  const panel = document.getElementById("tab-nakdan");
  if (!panel) return;
  panel.innerHTML = "";
  const text = pageJson && pageJson.diacritized_text ? pageJson.diacritized_text : null;
  if (!text) { panel.appendChild(_emptyMsg("Diacritization unavailable")); return; }
  const p = document.createElement("p"); p.dir = "rtl"; p.textContent = text;
  panel.appendChild(p);
}

// ---------------------------------------------------------------------------
// Voice tab
// ---------------------------------------------------------------------------

function _populateVoiceTab(audioJson) {
  const panel = document.getElementById("tab-voice");
  if (!panel) return;
  panel.innerHTML = "";
  const timings = audioJson && Array.isArray(audioJson.timings) ? audioJson.timings : [];
  if (timings.length === 0) { panel.appendChild(_emptyMsg("Voice timing data unavailable")); return; }
  const tbl   = _createTable(["Mark ID", "Start (s)", "End (s)"]);
  const tbody = tbl.querySelector("tbody");
  timings.forEach((t) => {
    const tr  = document.createElement("tr");
    const end = t.end_s != null ? String(t.end_s) : "—";
    [t.mark_id ?? "—", String(t.start_s ?? "—"), end].forEach((v) => {
      const td = document.createElement("td"); td.textContent = v; tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  panel.appendChild(tbl);
}

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------

function _createTable(headers) {
  const tbl   = document.createElement("table");
  tbl.className = "inspector-table";
  const thead  = document.createElement("thead");
  const hrow   = document.createElement("tr");
  headers.forEach((h) => {
    const th = document.createElement("th"); th.scope = "col"; th.textContent = h; hrow.appendChild(th);
  });
  thead.appendChild(hrow);
  tbl.appendChild(thead);
  tbl.appendChild(document.createElement("tbody"));
  return tbl;
}

function _emptyMsg(text) {
  const p = document.createElement("p"); p.className = "inspector-empty"; p.textContent = text; return p;
}

function _buildMarkMap(pageJson) {
  const fwd = pageJson && pageJson.marks_to_word_index ? pageJson.marks_to_word_index : {};
  const inv = {};
  for (const [markId, wordIdx] of Object.entries(fwd)) inv[wordIdx] = markId;
  return inv;
}

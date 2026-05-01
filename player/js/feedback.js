// N04/F33 T-08/T-10/T-12 — feedback.js: mountFeedbackPanel word annotation panel.
// DE-06  AC: US-02/AC-05..AC-10, US-04/AC-16..AC-20
// FT-317, FT-318, FT-322, FT-323, FT-324, FT-326, FT-327, FT-328  BT-209, BT-210, BT-212, BT-214, BT-215

const CATEGORIES = [
  { id: "wrong_pronunciation", label: "Wrong pronunciation" },
  { id: "wrong_stress",        label: "Wrong stress" },
  { id: "wrong_order",         label: "Wrong order" },
  { id: "wrong_nikud",         label: "Wrong nikud" },
  { id: "other",               label: "Other" },
];

/**
 * Mount the word annotation feedback panel.
 *
 * @param {Object} state
 * @param {function} state.onHighlight   - Register highlight callback.
 * @param {function} state.getOpenStages - Returns array of stage names opened this session.
 * @param {HTMLElement} state.panel      - DOM element to render into.
 * @param {string} [state.feedbackEndpoint="/feedback"] - POST target URL.
 */
export function mountFeedbackPanel(state) {
  const endpoint = state.feedbackEndpoint ?? "/feedback";
  // Track which markIds have been successfully submitted (cleared drafts)
  const submitted = new Set();
  const run = _getRunParam();

  // Build export button (hidden until first annotation exists)
  const exportBtn = _buildExportBtn();
  if (_collectEntries(run, localStorage).length > 0) {
    exportBtn.hidden = false;
  }
  exportBtn.addEventListener("click", () => _exportFeedback(run, localStorage, document));
  state.panel.appendChild(exportBtn);

  _renderEmpty(state.panel);

  state.onHighlight((word) => {
    if (!word) {
      _renderEmpty(state.panel);
      state.panel.appendChild(exportBtn);
    } else {
      _renderForm(state.panel, word, state, endpoint, submitted, exportBtn);
    }
  });
}

// ---------------------------------------------------------------------------
// Draft helpers
// ---------------------------------------------------------------------------

function _draftKey(run, markId) {
  return `feedback-draft:${run}:${markId}`;
}

function _saveDraft(markId, category, note) {
  const run = _getRunParam();
  localStorage.setItem(_draftKey(run, markId), JSON.stringify({ category, note }));
}

function _loadDraft(markId) {
  const run = _getRunParam();
  const raw = localStorage.getItem(_draftKey(run, markId));
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (_) { return null; }
}

function _clearDraft(markId) {
  const run = _getRunParam();
  localStorage.removeItem(_draftKey(run, markId));
}

// ---------------------------------------------------------------------------
// Rendering helpers (CC ≤ 5 each)
// ---------------------------------------------------------------------------

function _renderEmpty(panel) {
  panel.innerHTML = "";
  const msg = document.createElement("p");
  msg.className = "feedback-panel-empty";
  msg.textContent = "Click a word to annotate";
  panel.appendChild(msg);
}

function _renderForm(panel, word, state, endpoint, submitted, exportBtn) {
  panel.innerHTML = "";

  const wrapper = document.createElement("div");
  wrapper.className = "feedback-panel";

  wrapper.appendChild(_buildWordInfo(word));
  const { buttons, getCategory, setCategory } = _buildIssuePicker();
  wrapper.appendChild(buttons);
  const ta = _buildTextarea();
  wrapper.appendChild(ta);
  const errorEl = _buildError();
  wrapper.appendChild(errorEl);
  const submitBtn = _buildSubmitBtn();
  wrapper.appendChild(submitBtn);

  // Restore draft if available and not yet submitted
  if (!submitted.has(word.markId)) {
    _restoreDraft(word.markId, ta, setCategory);
  }

  // Persist draft on every keystroke
  ta.addEventListener("input", () =>
    _saveDraft(word.markId, getCategory(), ta.value)
  );

  // Persist draft on category selection (delegated from issue-picker).
  // The individual button listener runs first (bubble), so getCategory()
  // already reflects the new value when this container listener fires.
  buttons.addEventListener("click", () =>
    _saveDraft(word.markId, getCategory(), ta.value)
  );

  submitBtn.addEventListener("click", () =>
    _onSubmit({ panel, wrapper, word, state, endpoint, getCategory, ta, errorEl, submitted, exportBtn })
  );

  panel.appendChild(wrapper);
  if (exportBtn) panel.appendChild(exportBtn);
}

function _restoreDraft(markId, ta, setCategory) {
  const draft = _loadDraft(markId);
  if (!draft) return;
  ta.value = draft.note ?? "";
  if (draft.category) setCategory(draft.category);
}

function _buildWordInfo(word) {
  const info = document.createElement("div");
  info.className = "feedback-word-info";

  const idEl = document.createElement("span");
  idEl.className = "feedback-mark-id";
  idEl.textContent = word.markId;

  const ocrEl = document.createElement("span");
  ocrEl.className = "feedback-ocr-text";
  ocrEl.textContent = word.ocrText;

  const diacEl = document.createElement("span");
  diacEl.className = "feedback-diacritized-text";
  diacEl.textContent = word.diacritizedText;

  info.appendChild(idEl);
  info.appendChild(ocrEl);
  info.appendChild(diacEl);
  return info;
}

function _buildIssuePicker() {
  const container = document.createElement("div");
  container.className = "issue-picker";
  let selectedId = null;

  const setter = (next) => { selectedId = next; };

  CATEGORIES.forEach(({ id, label }) => {
    const btn = document.createElement("button");
    btn.className = "issue-btn";
    btn.dataset.category = id;
    btn.textContent = label;
    btn.addEventListener("click", () => _toggleCategory(container, btn, id, selectedId, setter));
    container.appendChild(btn);
  });

  function setCategory(id) {
    const btn = container.querySelector(`.issue-btn[data-category="${id}"]`);
    if (!btn) return;
    container.querySelectorAll(".issue-btn").forEach((b) => b.classList.remove("selected"));
    btn.classList.add("selected");
    setter(id);
  }

  return {
    buttons: container,
    getCategory: () => selectedId,
    setCategory,
  };
}

function _toggleCategory(container, btn, id, current, setter) {
  if (current === id) {
    btn.classList.remove("selected");
    setter(null);
    return;
  }
  container.querySelectorAll(".issue-btn").forEach((b) => b.classList.remove("selected"));
  btn.classList.add("selected");
  setter(id);
}

function _buildTextarea() {
  const ta = document.createElement("textarea");
  ta.className = "feedback-note";
  ta.setAttribute("maxlength", "500");
  ta.placeholder = "Optional note (max 500 chars)";
  return ta;
}

function _buildError() {
  const el = document.createElement("p");
  el.className = "feedback-error";
  el.style.display = "none";
  el.textContent = "Please select an issue category";
  return el;
}

function _buildSubmitBtn() {
  const btn = document.createElement("button");
  btn.className = "feedback-submit";
  btn.textContent = "Submit";
  return btn;
}

// ---------------------------------------------------------------------------
// Submit handler (CC ≤ 5 each)
// ---------------------------------------------------------------------------

async function _onSubmit({ panel, wrapper, word, state, endpoint, getCategory, ta, errorEl, submitted, exportBtn }) {
  const category = getCategory();
  if (!category) {
    errorEl.style.display = "";
    return;
  }
  errorEl.style.display = "none";

  const body = _buildPostBody({ word, state, category, note: ta.value });
  try {
    await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    _storeEntry(word.markId, body);
    _clearDraft(word.markId);
    submitted.add(word.markId);
    if (exportBtn) exportBtn.hidden = false;
    _onSuccess({ wrapper, word });
  } catch (_) {
    // Network failure — leave form visible
  }
}

function _buildPostBody({ word, state, category, note }) {
  return {
    markId: word.markId,
    run: _getRunParam(),
    category,
    note,
    ocr_text: word.ocrText,
    diacritized_text: word.diacritizedText,
    stages_visible_at_capture: state.getOpenStages(),
    schema_version: "1",
  };
}

function _getRunParam() {
  const search = (typeof window !== "undefined" && window.location && window.location.search) || "";
  const params = new URLSearchParams(search);
  return params.get("run") ?? "001";
}

function _onSuccess({ wrapper, word }) {
  // Mark the word's .marker element
  const marker = document.querySelector(`.marker[data-mark-id="${word.markId}"]`);
  if (marker) marker.classList.add("annotated");

  // Show success indicator
  const success = document.createElement("p");
  success.className = "feedback-success";
  success.textContent = "Feedback submitted";
  wrapper.appendChild(success);
}

// ---------------------------------------------------------------------------
// Entry storage helpers
// ---------------------------------------------------------------------------

function _entryKey(run, markId) {
  return `feedback-entry:${run}:${markId}`;
}

function _storeEntry(markId, body) {
  const run = _getRunParam();
  localStorage.setItem(_entryKey(run, markId), JSON.stringify(body));
}

// ---------------------------------------------------------------------------
// Export helpers (exported for testability)
// ---------------------------------------------------------------------------

/**
 * Collect all feedback entries for a given run from a localStorage-like object.
 * @param {string} run
 * @param {{ keys: function(): string[], getItem: function(string): string|null }} ls
 * @returns {Object[]}
 */
export function _collectEntries(run, ls) {
  const prefix = `feedback-entry:${run}:`;
  const allKeys = typeof ls.keys === "function" ? ls.keys() : Object.keys(ls);
  return allKeys.reduce((acc, key) => {
    if (!key.startsWith(prefix)) return acc;
    const raw = ls.getItem(key);
    if (!raw) return acc;
    try {
      acc.push(JSON.parse(raw));
    } catch (_) { /* skip malformed */ }
    return acc;
  }, []);
}

/**
 * Collect entries for run and trigger a JSON file download.
 * @param {string} run
 * @param {{ keys: function(): string[], getItem: function(string): string|null }} ls
 * @param {Document} doc
 */
export function _exportFeedback(run, ls, doc) {
  const entries = _collectEntries(run, ls);
  const json = JSON.stringify(entries, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const iso = new Date().toISOString();
  const a = doc.createElement("a");
  a.href = url;
  a.download = `feedback-run-${run}-${iso}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function _buildExportBtn() {
  const btn = document.createElement("button");
  btn.className = "feedback-export-btn";
  btn.textContent = "Export feedback";
  btn.hidden = true;
  return btn;
}

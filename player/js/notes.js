// F50 — Reviewer notes: per-SHA, per-tab persistent notepad + JSON export.

const TABS = ["ocr", "nlp", "nakdan", "voice"];
const DEBOUNCE_MS = 500;

let _activeSha = "";
let _debounceTimers = {};

/**
 * Initialize notes for the given SHA.  Attaches textareas + export buttons
 * below each tab panel, restores saved content, and wires auto-save.
 *
 * @param {Object} args
 * @param {string} args.sha
 */
export function initNotes({ sha }) {
  _activeSha = sha;
  TABS.forEach((tab) => _setupTabNotes(tab));
}

/**
 * Switch to a new SHA: save current content, update _activeSha, restore.
 *
 * @param {string} sha
 */
export function switchNotesSha(sha) {
  _activeSha = sha;
  TABS.forEach((tab) => _restoreNotes(tab));
}

// ---------------------------------------------------------------------------
// Per-tab setup
// ---------------------------------------------------------------------------

function _setupTabNotes(tab) {
  const panel = document.getElementById(`tab-${tab}`);
  if (!panel) return;
  if (panel.querySelector(".notes-area")) return; // already wired

  const wrapper = _buildNotesWidget(tab);
  panel.appendChild(wrapper);
}

function _buildNotesWidget(tab) {
  const wrapper = document.createElement("div");
  wrapper.className = "notes-widget";

  const textarea = _buildTextarea(tab);
  const exportBtn = _buildExportButton(tab, textarea);

  wrapper.appendChild(textarea);
  wrapper.appendChild(exportBtn);
  return wrapper;
}

function _buildTextarea(tab) {
  const ta = document.createElement("textarea");
  ta.className = "notes-area";
  ta.placeholder = "Add reviewer notes…";
  ta.setAttribute("aria-label", `Reviewer notes for ${tab} tab`);
  ta.rows = 4;

  ta.value = _loadNote(tab);

  ta.addEventListener("input", () => {
    clearTimeout(_debounceTimers[tab]);
    _debounceTimers[tab] = setTimeout(() => _saveNote(tab, ta.value), DEBOUNCE_MS);
  });

  return ta;
}

function _buildExportButton(tab, textarea) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "notes-export";
  btn.textContent = "Export notes";
  btn.setAttribute("aria-label", `Export reviewer notes as JSON`);
  btn.addEventListener("click", () => _exportNotes());
  return btn;
}

// ---------------------------------------------------------------------------
// Storage helpers
// ---------------------------------------------------------------------------

function _storageKey(sha, tab) {
  return `tirvi:notes:${sha}:${tab}`;
}

function _saveNote(tab, value) {
  try {
    localStorage.setItem(_storageKey(_activeSha, tab), value);
  } catch {
    // localStorage may be unavailable in some environments
  }
}

function _loadNote(tab) {
  try {
    return localStorage.getItem(_storageKey(_activeSha, tab)) ?? "";
  } catch {
    return "";
  }
}

function _restoreNotes(tab) {
  const panel = document.getElementById(`tab-${tab}`);
  if (!panel) return;
  const ta = panel.querySelector(".notes-area");
  if (!ta) return;
  ta.value = _loadNote(tab);
}

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------

function _exportNotes() {
  const notes = {};
  TABS.forEach((tab) => {
    notes[tab] = _loadNote(tab);
  });

  const payload = JSON.stringify({ sha: _activeSha, notes }, null, 2);
  const blob = new Blob([payload], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `notes-${_activeSha.slice(0, 8)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

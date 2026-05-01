// N04/F33 T-08 — feedback.js: mountFeedbackPanel word annotation panel.
// DE-06  AC: US-02/AC-05, US-02/AC-06, US-02/AC-07, US-02/AC-08, US-02/AC-09, US-02/AC-10
// FT-317, FT-318, FT-323, FT-327  BT-210, BT-212

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
  _renderEmpty(state.panel);

  state.onHighlight((word) => {
    if (!word) {
      _renderEmpty(state.panel);
    } else {
      _renderForm(state.panel, word, state, endpoint);
    }
  });
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

function _renderForm(panel, word, state, endpoint) {
  panel.innerHTML = "";

  const wrapper = document.createElement("div");
  wrapper.className = "feedback-panel";

  wrapper.appendChild(_buildWordInfo(word));
  const { buttons, getCategory } = _buildIssuePicker();
  wrapper.appendChild(buttons);
  const ta = _buildTextarea();
  wrapper.appendChild(ta);
  const errorEl = _buildError();
  wrapper.appendChild(errorEl);
  const submitBtn = _buildSubmitBtn();
  wrapper.appendChild(submitBtn);

  submitBtn.addEventListener("click", () =>
    _onSubmit({ panel, wrapper, word, state, endpoint, getCategory, ta, errorEl })
  );

  panel.appendChild(wrapper);
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

  CATEGORIES.forEach(({ id, label }) => {
    const btn = document.createElement("button");
    btn.className = "issue-btn";
    btn.dataset.category = id;
    btn.textContent = label;
    btn.addEventListener("click", () => _toggleCategory(container, btn, id, selectedId, (next) => { selectedId = next; }));
    container.appendChild(btn);
  });

  return {
    buttons: container,
    getCategory: () => selectedId,
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

async function _onSubmit({ panel, wrapper, word, state, endpoint, getCategory, ta, errorEl }) {
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

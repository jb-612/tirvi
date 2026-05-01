// N04/F33 T-08 — feedback.js: mountFeedbackPanel word annotation panel.
// AC: US-02/AC-05, US-02/AC-06, US-02/AC-07, US-02/AC-08, US-02/AC-09, US-02/AC-10
// Spec: N04/F33 DE-06  FT: FT-317, FT-318, FT-323, FT-327  BT: BT-210, BT-212

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { mountFeedbackPanel } from "../js/feedback.js";

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

function _makeState(overrides = {}) {
  let _highlightCb = null;
  return {
    onHighlight: vi.fn((cb) => { _highlightCb = cb; }),
    getOpenStages: vi.fn().mockReturnValue(["01-ocr"]),
    panel: document.createElement("div"),
    feedbackEndpoint: "/feedback",
    // Helper to fire highlight event from tests
    _fireHighlight: (payload) => _highlightCb && _highlightCb(payload),
    ...overrides,
  };
}

function _makeFetchOk() {
  return vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({}) });
}

function _makeFetchFail() {
  return vi.fn().mockResolvedValue({ ok: false, json: () => Promise.resolve({}) });
}

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------

let state;

beforeEach(() => {
  state = _makeState();
  document.body.appendChild(state.panel);
  vi.unstubAllGlobals();
});

afterEach(() => {
  state.panel.remove();
  vi.unstubAllGlobals();
});

// ---------------------------------------------------------------------------
// 1. Empty state rendering
// ---------------------------------------------------------------------------

describe("mountFeedbackPanel renders empty state when no word selected", () => {
  it("shows .feedback-panel-empty placeholder text", () => {
    mountFeedbackPanel(state);
    expect(state.panel.querySelector(".feedback-panel-empty")).not.toBeNull();
    expect(state.panel.querySelector(".feedback-panel-empty").textContent).toMatch(/click/i);
  });

  it("registers onHighlight callback", () => {
    mountFeedbackPanel(state);
    expect(state.onHighlight).toHaveBeenCalledOnce();
  });
});

// ---------------------------------------------------------------------------
// 2. Show word info when highlight fires
// ---------------------------------------------------------------------------

describe("mountFeedbackPanel shows word info when highlight event fires", () => {
  it("displays markId, ocrText, diacritizedText", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const panel = state.panel;
    expect(panel.textContent).toContain("word-3");
    expect(panel.textContent).toContain("שלום");
    expect(panel.textContent).toContain("שָׁלוֹם");
  });

  it("hides .feedback-panel-empty when word is selected", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const empty = state.panel.querySelector(".feedback-panel-empty");
    expect(!empty || empty.style.display === "none" || !state.panel.contains(empty)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// 3. Clear panel when null highlight fires
// ---------------------------------------------------------------------------

describe("mountFeedbackPanel clears panel when null highlight fired", () => {
  it("restores empty state when null fired after a word", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });
    state._fireHighlight(null);

    expect(state.panel.querySelector(".feedback-panel-empty")).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// 4. Issue buttons render all 5 categories
// ---------------------------------------------------------------------------

describe("issue buttons render all 5 categories", () => {
  const CATEGORIES = [
    "wrong_pronunciation",
    "wrong_stress",
    "wrong_order",
    "wrong_nikud",
    "other",
  ];

  it("renders 5 .issue-btn elements after word selected", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btns = state.panel.querySelectorAll(".issue-btn");
    expect(btns.length).toBe(5);
  });

  it.each(CATEGORIES)("has button with data-category=%s", (cat) => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btn = state.panel.querySelector(`.issue-btn[data-category="${cat}"]`);
    expect(btn).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// 5. Clicking issue button marks it selected
// ---------------------------------------------------------------------------

describe("clicking issue button marks it selected", () => {
  it("adds .selected class to clicked button", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btn = state.panel.querySelector('.issue-btn[data-category="wrong_stress"]');
    btn.click();
    expect(btn.classList.contains("selected")).toBe(true);
  });

  it("only one button is selected at a time", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btns = Array.from(state.panel.querySelectorAll(".issue-btn"));
    btns[0].click();
    btns[1].click();

    const selected = btns.filter((b) => b.classList.contains("selected"));
    expect(selected.length).toBe(1);
    expect(selected[0]).toBe(btns[1]);
  });
});

// ---------------------------------------------------------------------------
// 6. Clicking selected button deselects (toggle)
// ---------------------------------------------------------------------------

describe("clicking selected button deselects (toggle)", () => {
  it("removes .selected when already-selected button is clicked again", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btn = state.panel.querySelector('.issue-btn[data-category="other"]');
    btn.click(); // select
    btn.click(); // deselect
    expect(btn.classList.contains("selected")).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// 7. Textarea enforces 500 char limit
// ---------------------------------------------------------------------------

describe("textarea enforces 500 char limit", () => {
  it("textarea has maxlength 500", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const ta = state.panel.querySelector(".feedback-note");
    expect(ta).not.toBeNull();
    expect(ta.getAttribute("maxlength")).toBe("500");
  });
});

// ---------------------------------------------------------------------------
// 8. Submit without category shows inline error
// ---------------------------------------------------------------------------

describe("submit without category shows inline error", () => {
  it("shows .feedback-error and does NOT fetch", () => {
    const fetchMock = _makeFetchOk();
    vi.stubGlobal("fetch", fetchMock);

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const submitBtn = state.panel.querySelector(".feedback-submit");
    submitBtn.click();

    expect(state.panel.querySelector(".feedback-error")).not.toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// 9. Submit with category POSTs correct JSON to /feedback
// ---------------------------------------------------------------------------

describe("submit with category POSTs correct JSON to /feedback", () => {
  it("calls fetch with POST and correct body fields", async () => {
    const fetchMock = _makeFetchOk();
    vi.stubGlobal("fetch", fetchMock);

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const btn = state.panel.querySelector('.issue-btn[data-category="wrong_pronunciation"]');
    btn.click();

    const ta = state.panel.querySelector(".feedback-note");
    ta.value = "test note";

    const submitBtn = state.panel.querySelector(".feedback-submit");
    submitBtn.click();

    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    const [url, opts] = fetchMock.mock.calls[0];
    expect(url).toBe("/feedback");
    expect(opts.method).toBe("POST");

    const body = JSON.parse(opts.body);
    expect(body.markId).toBe("word-3");
    expect(body.category).toBe("wrong_pronunciation");
    expect(body.note).toBe("test note");
    expect(body.ocr_text).toBe("שלום");
    expect(body.diacritized_text).toBe("שָׁלוֹם");
    expect(body.schema_version).toBe("1");
  });
});

// ---------------------------------------------------------------------------
// 10. POST body includes stages_visible_at_capture
// ---------------------------------------------------------------------------

describe("POST body includes stages_visible_at_capture", () => {
  it("reads stages from state.getOpenStages()", async () => {
    const fetchMock = _makeFetchOk();
    vi.stubGlobal("fetch", fetchMock);

    state.getOpenStages.mockReturnValue(["01-ocr", "03-nlp"]);
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btn = state.panel.querySelector('.issue-btn[data-category="other"]');
    btn.click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body.stages_visible_at_capture).toEqual(["01-ocr", "03-nlp"]);
  });
});

// ---------------------------------------------------------------------------
// 11. POST body includes run from URL param
// ---------------------------------------------------------------------------

describe("POST body includes run from URL param", () => {
  it("uses ?run=NN from window.location.search", async () => {
    const fetchMock = _makeFetchOk();
    vi.stubGlobal("fetch", fetchMock);
    // Override search on the location object
    Object.defineProperty(window, "location", {
      value: { ...window.location, search: "?run=007" },
      writable: true,
      configurable: true,
    });

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btn = state.panel.querySelector('.issue-btn[data-category="wrong_nikud"]');
    btn.click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body.run).toBe("007");
  });

  it("defaults run to '001' when no ?run param", async () => {
    const fetchMock = _makeFetchOk();
    vi.stubGlobal("fetch", fetchMock);
    Object.defineProperty(window, "location", {
      value: { ...window.location, search: "" },
      writable: true,
      configurable: true,
    });

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    const btn = state.panel.querySelector('.issue-btn[data-category="other"]');
    btn.click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body.run).toBe("001");
  });
});

// ---------------------------------------------------------------------------
// 12. Successful submit shows success indicator
// ---------------------------------------------------------------------------

describe("successful submit shows success indicator", () => {
  it("shows .feedback-success element after successful POST", async () => {
    vi.stubGlobal("fetch", _makeFetchOk());

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-1", ocrText: "א", diacritizedText: "א" });

    state.panel.querySelector('.issue-btn[data-category="other"]').click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() =>
      expect(state.panel.querySelector(".feedback-success")).not.toBeNull()
    );
  });
});

// ---------------------------------------------------------------------------
// 13. Re-annotation of same markId overwrites previous selection
// ---------------------------------------------------------------------------

describe("re-annotation of same markId overwrites previous selection", () => {
  it("clears previous category selection on new highlight of same markId", async () => {
    vi.stubGlobal("fetch", _makeFetchOk());

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    // First annotation
    state.panel.querySelector('.issue-btn[data-category="wrong_pronunciation"]').click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() =>
      expect(state.panel.querySelector(".feedback-success")).not.toBeNull()
    );

    // Re-highlight same markId — should re-render fresh form
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const selected = state.panel.querySelectorAll(".issue-btn.selected");
    expect(selected.length).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 14. Annotated word gets .annotated CSS class on its .marker element
// ---------------------------------------------------------------------------

describe("annotated word gets .annotated CSS class on its .marker element", () => {
  it("adds .annotated to marker element matching markId after submit", async () => {
    vi.stubGlobal("fetch", _makeFetchOk());

    // Add a marker element to document.body
    const marker = document.createElement("div");
    marker.className = "marker";
    marker.dataset.markId = "word-3";
    document.body.appendChild(marker);

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    state.panel.querySelector('.issue-btn[data-category="wrong_pronunciation"]').click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() => expect(marker.classList.contains("annotated")).toBe(true));

    marker.remove();
  });
});

// ---------------------------------------------------------------------------
// T-10: localStorage draft persistence
// ---------------------------------------------------------------------------

describe("T-10: localStorage draft persistence", () => {
  function _makeLocalStorageMock() {
    const store = new Map();
    return {
      getItem: vi.fn((key) => store.get(key) ?? null),
      setItem: vi.fn((key, value) => store.set(key, value)),
      removeItem: vi.fn((key) => store.delete(key)),
      _store: store,
    };
  }

  let lsMock;

  beforeEach(() => {
    lsMock = _makeLocalStorageMock();
    vi.stubGlobal("localStorage", lsMock);
    // Ensure default run param (no ?run= in URL)
    Object.defineProperty(window, "location", {
      value: { ...window.location, search: "" },
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("saves draft to localStorage on textarea input", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const ta = state.panel.querySelector(".feedback-note");
    ta.value = "my note";
    ta.dispatchEvent(new Event("input"));

    expect(lsMock.setItem).toHaveBeenCalled();
    const [key, val] = lsMock.setItem.mock.calls[lsMock.setItem.mock.calls.length - 1];
    expect(key).toBe("feedback-draft:001:word-3");
    const parsed = JSON.parse(val);
    expect(parsed.note).toBe("my note");
  });

  it("saves draft to localStorage on category button click", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const btn = state.panel.querySelector('.issue-btn[data-category="wrong_stress"]');
    btn.click();

    expect(lsMock.setItem).toHaveBeenCalled();
    const [key, val] = lsMock.setItem.mock.calls[lsMock.setItem.mock.calls.length - 1];
    expect(key).toBe("feedback-draft:001:word-3");
    const parsed = JSON.parse(val);
    expect(parsed.category).toBe("wrong_stress");
  });

  it("restores draft when same markId highlighted again", () => {
    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    // Type a note and pick a category
    const ta = state.panel.querySelector(".feedback-note");
    ta.value = "restored note";
    ta.dispatchEvent(new Event("input"));

    const catBtn = state.panel.querySelector('.issue-btn[data-category="wrong_nikud"]');
    catBtn.click();

    // Deselect by firing null highlight
    state._fireHighlight(null);

    // Re-highlight same markId
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const restoredTa = state.panel.querySelector(".feedback-note");
    expect(restoredTa.value).toBe("restored note");

    const selectedBtn = state.panel.querySelector('.issue-btn[data-category="wrong_nikud"]');
    expect(selectedBtn.classList.contains("selected")).toBe(true);
  });

  it("clears draft from localStorage after successful POST", async () => {
    vi.stubGlobal("fetch", _makeFetchOk());

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const btn = state.panel.querySelector('.issue-btn[data-category="other"]');
    btn.click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() =>
      expect(lsMock.removeItem).toHaveBeenCalledWith("feedback-draft:001:word-3")
    );
  });

  it("does not restore draft after successful POST", async () => {
    vi.stubGlobal("fetch", _makeFetchOk());

    mountFeedbackPanel(state);
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const ta = state.panel.querySelector(".feedback-note");
    ta.value = "should not restore";
    ta.dispatchEvent(new Event("input"));

    const btn = state.panel.querySelector('.issue-btn[data-category="other"]');
    btn.click();
    state.panel.querySelector(".feedback-submit").click();

    await vi.waitFor(() =>
      expect(state.panel.querySelector(".feedback-success")).not.toBeNull()
    );

    // Re-highlight same markId — draft was cleared, form should be blank
    state._fireHighlight({ markId: "word-3", ocrText: "שלום", diacritizedText: "שָׁלוֹם" });

    const restoredTa = state.panel.querySelector(".feedback-note");
    expect(restoredTa.value).toBe("");
    const selectedBtns = state.panel.querySelectorAll(".issue-btn.selected");
    expect(selectedBtns.length).toBe(0);
  });
});

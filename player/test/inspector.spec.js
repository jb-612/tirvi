// F50 T-13 — Inspector module: loadInspector, syncInspectorWord, initVersionNav,
// initNotes, switchNotesSha, notes export.
//
// AC: US-03/AC-03/1, US-04/AC-04/3, US-05/AC-05/2
// Spec: N04/F50 DE-03, DE-04, DE-05.

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { loadInspector, syncInspectorWord } from "../js/inspector.js";
import { initVersionNav } from "../js/version-nav.js";
import { initNotes, switchNotesSha } from "../js/notes.js";

// ---------------------------------------------------------------------------
// DOM scaffold — four fixed panels + tab list + version list
// ---------------------------------------------------------------------------

// jsdom does not expose CSS.escape — polyfill it once at module scope
if (typeof globalThis.CSS === "undefined") {
  globalThis.CSS = {
    escape: (v) => String(v).replace(/([^\w-])/g, "\\$1"),
  };
}

function _setupDom() {
  document.body.innerHTML = `
    <nav id="inspector-tabs">
      <button role="tab" data-tab="ocr"    aria-controls="tab-ocr"    aria-selected="false">OCR</button>
      <button role="tab" data-tab="nakdan" aria-controls="tab-nakdan" aria-selected="false">Nakdan</button>
      <button role="tab" data-tab="voice"  aria-controls="tab-voice"  aria-selected="false">Voice</button>
    </nav>
    <div id="inspector-content">
      <div id="tab-ocr"    role="tabpanel"></div>
      <div id="tab-nlp"    role="tabpanel"></div>
      <div id="tab-nakdan" role="tabpanel"></div>
      <div id="tab-voice"  role="tabpanel"></div>
    </div>
    <ul id="version-list"></ul>
  `;
  // jsdom does not implement scrollIntoView
  window.HTMLElement.prototype.scrollIntoView = vi.fn();
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const _pageJson = {
  words: [
    { text: "שלום", confidence: 0.95, lang_hint: "he", bbox: [10, 20, 30, 40] },
    { text: "עולם", confidence: 0.88, lang_hint: "he", bbox: [50, 20, 90, 40] },
  ],
  marks_to_word_index: { "b1-0": 0, "b1-1": 1 },
  nlp_models: [
    {
      name: "dictabert",
      tokens: [
        { text: "שלום", pos: "NOUN", lemma: "שלום", morph: { Number: "Sing" }, confidence: 0.9 },
      ],
    },
  ],
  diacritized_text: "שָׁלוֹם עוֹלָם",
};

const _audioJson = {
  timings: [
    { mark_id: "b1-0", start_s: 0.0, end_s: 0.4 },
    { mark_id: "b1-1", start_s: 0.4, end_s: 0.9 },
  ],
};

// ---------------------------------------------------------------------------
// loadInspector — OCR tab
// ---------------------------------------------------------------------------

describe("loadInspector — OCR tab", () => {
  beforeEach(_setupDom);

  it("renders one table row per word", () => {
    loadInspector(_pageJson, _audioJson);
    const rows = document.querySelectorAll("#tab-ocr tbody tr");
    expect(rows).toHaveLength(2);
  });

  it("first cell of each row contains word text", () => {
    loadInspector(_pageJson, _audioJson);
    const cells = document.querySelectorAll("#tab-ocr tbody tr td:first-child");
    expect(cells[0].textContent).toBe("שלום");
    expect(cells[1].textContent).toBe("עולם");
  });

  it("assigns data-mark-id via inverted marks_to_word_index", () => {
    loadInspector(_pageJson, _audioJson);
    const row0 = document.querySelector('#tab-ocr tr[data-mark-id="b1-0"]');
    const row1 = document.querySelector('#tab-ocr tr[data-mark-id="b1-1"]');
    expect(row0).not.toBeNull();
    expect(row1).not.toBeNull();
  });

  it("shows empty placeholder when words array is empty", () => {
    loadInspector({ words: [], marks_to_word_index: {} }, _audioJson);
    const msg = document.querySelector("#tab-ocr .inspector-empty");
    expect(msg).not.toBeNull();
    expect(msg.textContent).toMatch(/unavailable/i);
  });

  it("clears previous content on re-load", () => {
    loadInspector(_pageJson, _audioJson);
    loadInspector({ words: [], marks_to_word_index: {} }, _audioJson);
    const rows = document.querySelectorAll("#tab-ocr tbody tr");
    expect(rows).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// loadInspector — NLP tab
// ---------------------------------------------------------------------------

describe("loadInspector — NLP tab", () => {
  beforeEach(_setupDom);

  it("creates one tab button per nlp_model", () => {
    loadInspector(_pageJson, _audioJson);
    const btns = document.querySelectorAll(".nlp-model-tab");
    expect(btns).toHaveLength(1);
    expect(btns[0].textContent).toBe("dictabert");
  });

  it("creates a panel for each nlp_model", () => {
    loadInspector(_pageJson, _audioJson);
    const panel = document.getElementById("tab-nlp-0");
    expect(panel).not.toBeNull();
    expect(panel.getAttribute("role")).toBe("tabpanel");
  });

  it("renders one token row per token in the model", () => {
    loadInspector(_pageJson, _audioJson);
    const rows = document.querySelectorAll("#tab-nlp-0 tbody tr");
    expect(rows).toHaveLength(1);
    expect(rows[0].cells[0].textContent).toBe("שלום");
  });

  it("shows fallback NLP panel when nlp_models is empty", () => {
    loadInspector({ ..._pageJson, nlp_models: [] }, _audioJson);
    const panel = document.getElementById("tab-nlp-0");
    expect(panel).not.toBeNull();
    const msg = panel.querySelector(".inspector-empty");
    expect(msg).not.toBeNull();
  });

  it("removes old NLP tabs on re-load", () => {
    loadInspector(_pageJson, _audioJson);
    loadInspector({ ..._pageJson, nlp_models: [] }, _audioJson);
    const btns = document.querySelectorAll(".nlp-model-tab");
    // one fallback tab remains, previous named tab is gone
    expect(btns).toHaveLength(1);
    expect(document.getElementById("tab-nlp-1")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// loadInspector — Nakdan tab
// ---------------------------------------------------------------------------

describe("loadInspector — Nakdan tab", () => {
  beforeEach(_setupDom);

  it("renders diacritized_text in an RTL paragraph", () => {
    loadInspector(_pageJson, _audioJson);
    const p = document.querySelector("#tab-nakdan p[dir='rtl']");
    expect(p).not.toBeNull();
    expect(p.textContent).toBe("שָׁלוֹם עוֹלָם");
  });

  it("shows placeholder when diacritized_text is absent", () => {
    const { diacritized_text: _, ...rest } = _pageJson;
    loadInspector(rest, _audioJson);
    const msg = document.querySelector("#tab-nakdan .inspector-empty");
    expect(msg).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// loadInspector — Voice tab
// ---------------------------------------------------------------------------

describe("loadInspector — Voice tab", () => {
  beforeEach(_setupDom);

  it("renders one timing row per entry", () => {
    loadInspector(_pageJson, _audioJson);
    const rows = document.querySelectorAll("#tab-voice tbody tr");
    expect(rows).toHaveLength(2);
  });

  it("first cell contains mark_id", () => {
    loadInspector(_pageJson, _audioJson);
    const cell = document.querySelector("#tab-voice tbody tr:first-child td");
    expect(cell.textContent).toBe("b1-0");
  });

  it("shows placeholder when timings array is empty", () => {
    loadInspector(_pageJson, { timings: [] });
    const msg = document.querySelector("#tab-voice .inspector-empty");
    expect(msg).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// syncInspectorWord
// ---------------------------------------------------------------------------

describe("syncInspectorWord", () => {
  beforeEach(() => {
    _setupDom();
    loadInspector(_pageJson, _audioJson);
  });

  it("adds active class to the matching OCR row", () => {
    syncInspectorWord("b1-0");
    const row = document.querySelector('#tab-ocr tr[data-mark-id="b1-0"]');
    expect(row.classList.contains("active")).toBe(true);
  });

  it("removes active class from the previously highlighted row", () => {
    syncInspectorWord("b1-0");
    syncInspectorWord("b1-1");
    const prev = document.querySelector('#tab-ocr tr[data-mark-id="b1-0"]');
    expect(prev.classList.contains("active")).toBe(false);
    const next = document.querySelector('#tab-ocr tr[data-mark-id="b1-1"]');
    expect(next.classList.contains("active")).toBe(true);
  });

  it("clears active when markId is null/empty", () => {
    syncInspectorWord("b1-0");
    syncInspectorWord(null);
    expect(document.querySelector("#tab-ocr tr.active")).toBeNull();
  });

  it("does not throw when markId has no matching row", () => {
    expect(() => syncInspectorWord("nonexistent-id")).not.toThrow();
  });

  it("calls scrollIntoView on the activated row", () => {
    syncInspectorWord("b1-0");
    const row = document.querySelector('#tab-ocr tr[data-mark-id="b1-0"]');
    expect(row.scrollIntoView).toHaveBeenCalledWith({ block: "nearest", behavior: "smooth" });
  });
});

// ---------------------------------------------------------------------------
// initVersionNav — version list rendering + switching
// ---------------------------------------------------------------------------

describe("initVersionNav", () => {
  beforeEach(_setupDom);

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function _stubVersions(versions) {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: async () => versions }),
    );
  }

  it("renders one list item per version", async () => {
    _stubVersions([
      { sha: "abc12345def67890", mtime: 1000, label: "run-1" },
      { sha: "fff00000aaa11111", mtime: 900,  label: "run-0" },
    ]);
    await initVersionNav({ onSwitch: vi.fn() });
    expect(document.querySelectorAll("#version-list li")).toHaveLength(2);
  });

  it("button text includes short sha and label", async () => {
    _stubVersions([{ sha: "abc12345def67890", mtime: 1000, label: "run-1" }]);
    await initVersionNav({ onSwitch: vi.fn() });
    const btn = document.querySelector("#version-list button");
    expect(btn.textContent).toContain("abc12345");
    expect(btn.textContent).toContain("run-1");
  });

  it("marks currentSha button with aria-current=true", async () => {
    _stubVersions([{ sha: "abc12345def67890", mtime: 1000, label: "run-1" }]);
    await initVersionNav({ currentSha: "abc12345def67890", onSwitch: vi.fn() });
    const btn = document.querySelector("#version-list button");
    expect(btn.getAttribute("aria-current")).toBe("true");
    expect(btn.classList.contains("version-active")).toBe(true);
  });

  it("calls onSwitch with the sha when button is clicked", async () => {
    _stubVersions([{ sha: "abc12345def67890", mtime: 1000, label: "run-1" }]);
    const onSwitch = vi.fn();
    await initVersionNav({ onSwitch });
    document.querySelector("#version-list button").click();
    expect(onSwitch).toHaveBeenCalledWith("abc12345def67890");
  });

  it("shows empty-state item when API returns empty array", async () => {
    _stubVersions([]);
    await initVersionNav({ onSwitch: vi.fn() });
    expect(document.querySelector("#version-list .version-empty")).not.toBeNull();
  });

  it("shows empty-state item when fetch throws", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network error")));
    await initVersionNav({ onSwitch: vi.fn() });
    expect(document.querySelector("#version-list .version-empty")).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// initNotes + switchNotesSha — per-sha per-tab localStorage persistence
// ---------------------------------------------------------------------------

describe("initNotes — per-tab persistence", () => {
  let _store;

  beforeEach(() => {
    _setupDom();
    _store = {};
    vi.stubGlobal("localStorage", {
      getItem:    vi.fn((k)    => _store[k] ?? null),
      setItem:    vi.fn((k, v) => { _store[k] = v; }),
      removeItem: vi.fn((k)    => { delete _store[k]; }),
    });
    initNotes({ sha: "sha-abc" });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("adds a notes-area textarea inside each tab panel", () => {
    for (const tab of ["ocr", "nakdan", "voice"]) {
      expect(document.querySelector(`#tab-${tab} .notes-area`)).not.toBeNull();
    }
  });

  it("restores a previously saved note from localStorage on init", () => {
    _store["tirvi:notes:sha-abc:ocr"] = "my reviewer note";
    // Re-run init to trigger restore
    document.querySelector("#tab-ocr .notes-area").remove();
    initNotes({ sha: "sha-abc" });
    const ta = document.querySelector("#tab-ocr .notes-area");
    expect(ta.value).toBe("my reviewer note");
  });

  it("textarea value is empty string when localStorage has no entry", () => {
    const ta = document.querySelector("#tab-ocr .notes-area");
    expect(ta.value).toBe("");
  });

  it("switchNotesSha restores notes for the new sha", () => {
    _store["tirvi:notes:sha-xyz:ocr"] = "note for xyz";
    switchNotesSha("sha-xyz");
    expect(document.querySelector("#tab-ocr .notes-area").value).toBe("note for xyz");
  });

  it("switchNotesSha clears textarea when new sha has no saved note", () => {
    _store["tirvi:notes:sha-abc:ocr"] = "old note";
    initNotes({ sha: "sha-abc" });
    switchNotesSha("brand-new-sha");
    expect(document.querySelector("#tab-ocr .notes-area").value).toBe("");
  });

  it("auto-saves after debounce on textarea input", () => {
    vi.useFakeTimers();
    const ta = document.querySelector("#tab-ocr .notes-area");
    ta.value = "typed text";
    ta.dispatchEvent(new Event("input"));
    vi.advanceTimersByTime(600);
    expect(localStorage.setItem).toHaveBeenCalledWith(
      "tirvi:notes:sha-abc:ocr",
      "typed text",
    );
  });
});

// ---------------------------------------------------------------------------
// Notes export — Blob download
// ---------------------------------------------------------------------------

describe("notes export", () => {
  let _store;
  let _capturedBlobParts;

  beforeEach(() => {
    _setupDom();
    _store = {};
    vi.stubGlobal("localStorage", {
      getItem:    vi.fn((k)    => _store[k] ?? null),
      setItem:    vi.fn((k, v) => { _store[k] = v; }),
      removeItem: vi.fn(),
    });
    _capturedBlobParts = null;
    vi.stubGlobal("Blob", class MockBlob {
      constructor(parts, opts) { _capturedBlobParts = parts; this.type = opts?.type; }
    });
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:mock"),
      revokeObjectURL: vi.fn(),
    });
    initNotes({ sha: "expsha1234567890" });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("export button triggers createObjectURL with a Blob", () => {
    document.querySelector(".notes-export").click();
    expect(URL.createObjectURL).toHaveBeenCalledOnce();
  });

  it("exported JSON contains the active sha", () => {
    document.querySelector(".notes-export").click();
    const parsed = JSON.parse(_capturedBlobParts[0]);
    expect(parsed.sha).toBe("expsha1234567890");
  });

  it("exported JSON contains notes keyed by tab name", () => {
    _store["tirvi:notes:expsha1234567890:ocr"] = "ocr note";
    document.querySelector(".notes-export").click();
    const parsed = JSON.parse(_capturedBlobParts[0]);
    expect(parsed.notes.ocr).toBe("ocr note");
    expect(parsed.notes).toHaveProperty("nlp");
    expect(parsed.notes).toHaveProperty("nakdan");
    expect(parsed.notes).toHaveProperty("voice");
  });

  it("revokeObjectURL is called after download trigger", () => {
    document.querySelector(".notes-export").click();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock");
  });
});

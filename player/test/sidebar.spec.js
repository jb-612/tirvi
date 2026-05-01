// N04/F33 T-06 — sidebar.js: mountArtifactTree artifact tree.
// AC: US-03/AC-11, US-03/AC-13, US-03/AC-14
// Spec: N04/F33 DE-03  FT: FT-320, FT-321, FT-325, FT-329  BT: BT-211

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { mountArtifactTree } from "../js/sidebar.js";

// jsdom does not expose CSS.escape — polyfill it once at module scope
if (typeof globalThis.CSS === "undefined") {
  globalThis.CSS = {
    escape: (v) => String(v).replace(/([^\w-])/g, "\\$1"),
  };
}

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

function _manifest(overrides = {}) {
  return {
    stages: [
      { name: "01-ocr", label: "OCR words", files: ["data.json"], available: true },
      { name: "04-normalize", label: "Normalized text", files: [], available: false },
    ],
    feedback_dir: "feedback/",
    ...overrides,
  };
}

function _makeFetchOk(data) {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(data),
  });
}

function _makeFetchNotOk() {
  return vi.fn().mockResolvedValue({
    ok: false,
    json: () => Promise.resolve({}),
  });
}

function _makeFetchReject() {
  return vi.fn().mockRejectedValue(new Error("network error"));
}

// ---------------------------------------------------------------------------
// Render tree — happy-path tests
// ---------------------------------------------------------------------------

describe("mountArtifactTree — renders stage list", () => {
  let container;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchOk(_manifest()));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("renders one li.artifact-stage per stage", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    const stages = container.querySelectorAll("li.artifact-stage");
    expect(stages).toHaveLength(2);
  });

  it("stage header shows human-readable label not dir name", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    const btn = container.querySelector("li.artifact-stage button.stage-header");
    expect(btn).not.toBeNull();
    expect(btn.textContent).toBe("OCR words");
    expect(btn.textContent).not.toContain("01-ocr");
  });
});

// ---------------------------------------------------------------------------
// Available stage — file list
// ---------------------------------------------------------------------------

describe("mountArtifactTree — available stage", () => {
  let container;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchOk(_manifest()));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("available stage renders file list", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    const firstStage = container.querySelectorAll("li.artifact-stage")[0];
    const fileList = firstStage.querySelector("ul.artifact-files");
    expect(fileList).not.toBeNull();
    expect(fileList.querySelectorAll("li")).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// Unavailable stage
// ---------------------------------------------------------------------------

describe("mountArtifactTree — unavailable stage", () => {
  let container;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchOk(_manifest()));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("unavailable stage shows not-available indicator", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    const stages = container.querySelectorAll("li.artifact-stage");
    const unavailableStage = stages[1];
    const indicator = unavailableStage.querySelector(".stage-unavailable");
    expect(indicator).not.toBeNull();
  });

  it("unavailable stage has no file list", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    const stages = container.querySelectorAll("li.artifact-stage");
    const unavailableStage = stages[1];
    const fileList = unavailableStage.querySelector("ul.artifact-files");
    expect(fileList).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Click callback
// ---------------------------------------------------------------------------

describe("mountArtifactTree — file click callback", () => {
  let container;
  const ROOT = "http://localhost/runs/001";

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchOk(_manifest()));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("clicking file button calls onArtifactClick with url, name, stage", async () => {
    const onArtifactClick = vi.fn();
    await mountArtifactTree(container, ROOT, { onArtifactClick });
    const fileBtn = container.querySelector("button.artifact-file");
    expect(fileBtn).not.toBeNull();
    fileBtn.click();
    expect(onArtifactClick).toHaveBeenCalledOnce();
  });

  it("onArtifactClick url includes rootUrl and stage name and filename", async () => {
    const onArtifactClick = vi.fn();
    await mountArtifactTree(container, ROOT, { onArtifactClick });
    const fileBtn = container.querySelector("button.artifact-file");
    fileBtn.click();
    const arg = onArtifactClick.mock.calls[0][0];
    expect(arg.url).toContain(ROOT);
    expect(arg.url).toContain("01-ocr");
    expect(arg.url).toContain("data.json");
    expect(arg.name).toBe("data.json");
    expect(arg.stage).toBe("01-ocr");
  });
});

// ---------------------------------------------------------------------------
// Error states
// ---------------------------------------------------------------------------

describe("mountArtifactTree — fetch error", () => {
  let container;

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("fetch error renders error message", async () => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchReject());
    await mountArtifactTree(container, "http://localhost/runs/001");
    const err = container.querySelector(".artifact-error");
    expect(err).not.toBeNull();
  });

  it("non-ok response renders error message", async () => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchNotOk());
    await mountArtifactTree(container, "http://localhost/runs/001");
    const err = container.querySelector(".artifact-error");
    expect(err).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Empty stages
// ---------------------------------------------------------------------------

describe("mountArtifactTree — empty stages", () => {
  let container;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchOk(_manifest({ stages: [] })));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("empty stages array renders empty-state message", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    const empty = container.querySelector(".artifact-empty");
    expect(empty).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Re-render / idempotency
// ---------------------------------------------------------------------------

describe("mountArtifactTree — re-render", () => {
  let container;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchOk(_manifest()));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("clears container before re-render", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    await mountArtifactTree(container, "http://localhost/runs/001");
    const trees = container.querySelectorAll("ul.artifact-tree");
    expect(trees).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// Accessibility
// ---------------------------------------------------------------------------

describe("mountArtifactTree — accessibility", () => {
  let container;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
    vi.stubGlobal("fetch", _makeFetchOk(_manifest()));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    container.remove();
  });

  it("container has aria-label or role on the tree ul", async () => {
    await mountArtifactTree(container, "http://localhost/runs/001");
    const ul = container.querySelector("ul.artifact-tree");
    expect(ul).not.toBeNull();
    const hasRole = ul.getAttribute("role") !== null;
    const hasLabel = ul.getAttribute("aria-label") !== null;
    expect(hasRole || hasLabel).toBe(true);
  });
});

// N04/F33 T-07 — preview.js: renderArtifact artifact content renderer.
// AC: US-03/AC-12, US-05/AC-23
// Spec: N04/F33 DE-03  FT: FT-319, FT-322  BT: BT-213, BT-217

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { renderArtifact } from "../js/preview.js";

// jsdom does not expose CSS.escape — polyfill it once at module scope
if (typeof globalThis.CSS === "undefined") {
  globalThis.CSS = {
    escape: (v) => String(v).replace(/([^\w-])/g, "\\$1"),
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _node(name, url = `http://localhost/output/001/01-ocr/${name}`) {
  return { url, name, stage: "01-ocr" };
}

function _makeFetchText(text) {
  return vi.fn().mockResolvedValue({
    ok: true,
    text: () => Promise.resolve(text),
  });
}

function _makeFetchReject() {
  return vi.fn().mockRejectedValue(new Error("network error"));
}

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------

let panel;

beforeEach(() => {
  panel = document.createElement("div");
  document.body.appendChild(panel);
});

afterEach(() => {
  panel.remove();
  vi.unstubAllGlobals();
});

// ---------------------------------------------------------------------------
// JSON tests
// ---------------------------------------------------------------------------

describe("renderArtifact — .json", () => {
  it("renders json artifact in pre.preview-json", async () => {
    vi.stubGlobal("fetch", _makeFetchText('{"key":"val"}'));
    await renderArtifact(_node("data.json"), panel);
    expect(panel.querySelector("pre.preview-json")).not.toBeNull();
  });

  it("json content is pretty-printed", async () => {
    vi.stubGlobal("fetch", _makeFetchText('{"key":"val"}'));
    await renderArtifact(_node("data.json"), panel);
    const pre = panel.querySelector("pre.preview-json");
    expect(pre.textContent).toContain("\n");
  });

  it("json content set via textContent not innerHTML", async () => {
    vi.stubGlobal("fetch", _makeFetchText('{"xss":"<script>alert(1)<\\/script>"}'));
    await renderArtifact(_node("data.json"), panel);
    // If innerHTML was used, the script tag would be parsed and the text would
    // not contain the literal angle brackets in the DOM text.
    expect(panel.querySelector("pre.preview-json").textContent).toContain("<script>");
  });

  it("renders empty json object as preview-empty", async () => {
    vi.stubGlobal("fetch", _makeFetchText("{}"));
    await renderArtifact(_node("data.json"), panel);
    expect(panel.querySelector(".preview-empty")).not.toBeNull();
  });

  it("renders empty json array as preview-empty", async () => {
    vi.stubGlobal("fetch", _makeFetchText("[]"));
    await renderArtifact(_node("data.json"), panel);
    expect(panel.querySelector(".preview-empty")).not.toBeNull();
  });

  it("invalid json falls back to raw text display", async () => {
    vi.stubGlobal("fetch", _makeFetchText("not json {"));
    await renderArtifact(_node("data.json"), panel);
    const pre = panel.querySelector("pre.preview-json");
    expect(pre).not.toBeNull();
    expect(pre.textContent).toContain("not json {");
  });
});

// ---------------------------------------------------------------------------
// Plain text tests
// ---------------------------------------------------------------------------

describe("renderArtifact — .txt", () => {
  it("renders txt artifact in pre.preview-text", async () => {
    vi.stubGlobal("fetch", _makeFetchText("hello"));
    await renderArtifact(_node("notes.txt"), panel);
    expect(panel.querySelector("pre.preview-text")).not.toBeNull();
  });

  it("renders empty txt as preview-empty", async () => {
    vi.stubGlobal("fetch", _makeFetchText(""));
    await renderArtifact(_node("notes.txt"), panel);
    expect(panel.querySelector(".preview-empty")).not.toBeNull();
  });

  it("renders ssml same as txt", async () => {
    vi.stubGlobal("fetch", _makeFetchText("<speak>hello</speak>"));
    await renderArtifact(_node("speech.ssml"), panel);
    expect(panel.querySelector("pre.preview-text")).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Image tests
// ---------------------------------------------------------------------------

describe("renderArtifact — image", () => {
  it("renders png as img.preview-image", async () => {
    // No fetch needed — browser loads image via src attribute
    await renderArtifact(_node("page.png"), panel);
    const img = panel.querySelector("img.preview-image");
    expect(img).not.toBeNull();
    expect(img.src).toContain("page.png");
  });
});

// ---------------------------------------------------------------------------
// Audio tests
// ---------------------------------------------------------------------------

describe("renderArtifact — audio", () => {
  it("renders mp3 as audio.preview-audio", async () => {
    // No fetch needed — browser loads audio via src attribute
    await renderArtifact(_node("speech.mp3"), panel);
    const audio = panel.querySelector("audio.preview-audio");
    expect(audio).not.toBeNull();
    expect(audio.hasAttribute("controls")).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Unknown extension
// ---------------------------------------------------------------------------

describe("renderArtifact — unknown extension", () => {
  it("unknown extension renders preview-unknown", async () => {
    await renderArtifact(_node("file.xyz"), panel);
    expect(panel.querySelector(".preview-unknown")).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

describe("renderArtifact — error handling", () => {
  it("fetch error renders preview-error", async () => {
    vi.stubGlobal("fetch", _makeFetchReject());
    await renderArtifact(_node("data.json"), panel);
    expect(panel.querySelector(".preview-error")).not.toBeNull();
  });

  it("clears panel before rendering", async () => {
    vi.stubGlobal("fetch", _makeFetchText("hello"));
    await renderArtifact(_node("a.txt"), panel);
    await renderArtifact(_node("b.txt"), panel);
    expect(panel.children.length).toBe(1);
  });
});

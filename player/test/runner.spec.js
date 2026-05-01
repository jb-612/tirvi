// N04/F33 T-09 — runner.js: run number management
//
// AC: US-01/AC-01, US-01/AC-03, US-01/AC-04
// FT anchors: FT-316, FT-317

import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  currentRunNumber,
  listAvailableRuns,
  renderRunError,
} from "../js/runner.js";

// jsdom does not expose CSS.escape — polyfill it once at module scope
if (typeof globalThis.CSS === "undefined") {
  globalThis.CSS = {
    escape: (v) => String(v).replace(/([^\w-])/g, "\\$1"),
  };
}

// ---------------------------------------------------------------------------
// currentRunNumber
// ---------------------------------------------------------------------------

describe("currentRunNumber", () => {
  it("returns run from ?run=001 param", () => {
    expect(currentRunNumber("?run=001")).toBe("001");
  });

  it("returns run from ?run=042 param", () => {
    expect(currentRunNumber("?run=042")).toBe("042");
  });

  it("returns null when param absent", () => {
    expect(currentRunNumber("")).toBeNull();
  });

  it("returns null for non-numeric param", () => {
    expect(currentRunNumber("?run=abc")).toBeNull();
  });

  it("returns null for empty run param", () => {
    expect(currentRunNumber("?run=")).toBeNull();
  });

  it("handles param among others", () => {
    expect(currentRunNumber("?foo=bar&run=007")).toBe("007");
  });
});

// ---------------------------------------------------------------------------
// listAvailableRuns
// ---------------------------------------------------------------------------

describe("listAvailableRuns", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns array from manifest-index.json", async () => {
    const runs = [{ run: "001", label: "Run 1", ts: "2026-05-01T00:00:00Z" }];
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => runs,
      })
    );
    const result = await listAvailableRuns("https://example.com/base");
    expect(result).toEqual(runs);
    expect(fetch).toHaveBeenCalledWith(
      "https://example.com/base/manifest-index.json"
    );
  });

  it("returns empty array on fetch error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("network error"))
    );
    const result = await listAvailableRuns("https://example.com/base");
    expect(result).toEqual([]);
  });

  it("returns empty array on non-ok response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
      })
    );
    const result = await listAvailableRuns("https://example.com/base");
    expect(result).toEqual([]);
  });

  it("returns empty array when index is empty", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [],
      })
    );
    const result = await listAvailableRuns("https://example.com/base");
    expect(result).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// renderRunError
// ---------------------------------------------------------------------------

describe("renderRunError", () => {
  let panel;

  beforeEach(() => {
    panel = document.createElement("div");
    document.body.appendChild(panel);
  });

  it("renders p.run-error with message", () => {
    renderRunError(panel, "Run not found");
    const p = panel.querySelector("p.run-error");
    expect(p).not.toBeNull();
    expect(p.textContent).toBe("Run not found");
  });

  it("uses role=alert", () => {
    renderRunError(panel, "Something went wrong");
    const p = panel.querySelector("p.run-error");
    expect(p.getAttribute("role")).toBe("alert");
  });

  it("clears panel first", () => {
    panel.innerHTML = "<span>old content</span>";
    renderRunError(panel, "New error");
    expect(panel.querySelector("span")).toBeNull();
    expect(panel.querySelectorAll("p").length).toBe(1);
  });

  it("uses textContent not innerHTML — script tag is escaped", () => {
    const malicious = '<script>alert("xss")</script>';
    renderRunError(panel, malicious);
    const p = panel.querySelector("p.run-error");
    // textContent means no child script element is parsed
    expect(p.querySelector("script")).toBeNull();
    expect(p.textContent).toBe(malicious);
  });
});

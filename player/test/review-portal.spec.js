// F33 T-01 — Review Portal Layout: three-panel grid shell + CSS variables.
// AC: US-01/AC-01, US-01/AC-03  Spec: N04/F33 DE-01, DE-02  FT: FT-316

import { describe, it, expect, beforeEach } from "vitest";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dir = dirname(fileURLToPath(import.meta.url));
const indexHtml = readFileSync(resolve(__dir, "../index.html"), "utf-8");
const playerCss  = readFileSync(resolve(__dir, "../player.css"),  "utf-8");

// Load the actual index.html body into jsdom for DOM queries.
function _loadIndex() {
  const m = indexHtml.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  document.body.innerHTML = m ? m[1] : "";
}

// ---------------------------------------------------------------------------
// HTML structure — F33 containers required by sidebar.js and feedback.js
// ---------------------------------------------------------------------------

describe("Review Portal HTML structure (DE-01)", () => {
  beforeEach(_loadIndex);

  it("has an #app-layout three-panel container", () => {
    expect(document.getElementById("app-layout")).not.toBeNull();
  });

  it("has an #artifact-tree container for sidebar.js", () => {
    expect(document.getElementById("artifact-tree")).not.toBeNull();
  });

  it("has an #annotation-panel container for feedback.js", () => {
    expect(document.getElementById("annotation-panel")).not.toBeNull();
  });

  it("#artifact-tree has an accessible aria-label", () => {
    const el = document.getElementById("artifact-tree");
    expect(el).not.toBeNull();
    expect(el.getAttribute("aria-label")).toBeTruthy();
  });

  it("#annotation-panel has an accessible aria-label", () => {
    const el = document.getElementById("annotation-panel");
    expect(el).not.toBeNull();
    expect(el.getAttribute("aria-label")).toBeTruthy();
  });

  it("#player-root (center column) is present", () => {
    expect(document.getElementById("player-root")).not.toBeNull();
  });
});

// ---------------------------------------------------------------------------
// CSS — grid column widths and center-panel max-width (DE-01, DE-02)
// ---------------------------------------------------------------------------

describe("Review Portal CSS variables (DE-01, DE-02)", () => {
  it("defines --artifact-tree-width as 280px", () => {
    expect(playerCss).toMatch(/--artifact-tree-width\s*:\s*280px/);
  });

  it("defines --annotation-panel-width as 320px", () => {
    expect(playerCss).toMatch(/--annotation-panel-width\s*:\s*320px/);
  });

  it("#app-layout grid uses the two new CSS variables", () => {
    expect(playerCss).toMatch(
      /grid-template-columns\s*:[^;]*--artifact-tree-width[^;]*--annotation-panel-width/,
    );
  });

  it("#page-figure max-width is 800px (center panel constraint DE-02)", () => {
    // Match the page-figure rule block and find max-width therein.
    const figureBlock = playerCss.match(/#page-figure\s*\{([^}]+)\}/);
    expect(figureBlock).not.toBeNull();
    expect(figureBlock[1]).toMatch(/max-width\s*:\s*800px/);
  });
});

// ---------------------------------------------------------------------------
// HTML framing — F33 admin portal context (not debug-viewer)
// ---------------------------------------------------------------------------

describe("Review Portal HTML framing (DE-01)", () => {
  it("index.html does not contain stale 'debug-viewer' class references", () => {
    expect(indexHtml).not.toContain("debug-viewer");
  });

  it("index.html references the exam review portal context in a comment", () => {
    expect(indexHtml).toMatch(/[Rr]eview [Pp]ortal|review-portal|exam.review/i);
  });
});

// F36 T-01 — single play button (POC scope per POC-CRITICAL-PATH.md).
//
// Spec: N04/F36 DE-01. AC: US-01/AC-01.
// Bounded context: bc:audio_delivery. Language: javascript (vanilla, ADR-023).
//
// POC ships ONE button. T-02..T-06 (full state machine, ARIA, keyboard
// shortcuts, focus, disabled states) deferred to v0.1.

import { describe, it, expect, beforeEach, vi } from "vitest";
import { mountPlayButton } from "../js/controls.js";

describe("F36 T-01 — single play button", () => {
  let audio;
  let toolbar;

  beforeEach(() => {
    document.body.innerHTML = '<div id="controls"></div><audio id="a"></audio>';
    audio = document.getElementById("a");
    toolbar = document.getElementById("controls");
    audio.play = vi.fn().mockResolvedValue(undefined);
  });

  it("us_01_ac_01 — mounts a single button into the toolbar", () => {
    mountPlayButton({ audio, toolbar });
    const buttons = toolbar.querySelectorAll("button");
    expect(buttons.length).toBe(1);
  });

  it("us_01_ac_01 — button has accessible label", () => {
    mountPlayButton({ audio, toolbar });
    const btn = toolbar.querySelector("button");
    // Either visible text or aria-label is sufficient for AT
    const label = btn.textContent.trim() || btn.getAttribute("aria-label");
    expect(label).toBeTruthy();
    expect(label.length).toBeGreaterThan(0);
  });

  it("us_01_ac_01 — clicking the button calls audio.play()", () => {
    mountPlayButton({ audio, toolbar });
    const btn = toolbar.querySelector("button");
    btn.click();
    expect(audio.play).toHaveBeenCalledTimes(1);
  });

  it("us_01_ac_01 — multiple clicks call play each time (idempotent)", () => {
    mountPlayButton({ audio, toolbar });
    const btn = toolbar.querySelector("button");
    btn.click();
    btn.click();
    btn.click();
    expect(audio.play).toHaveBeenCalledTimes(3);
  });

  it("us_01_ac_01 — works without throwing when audio.play() rejects", async () => {
    audio.play = vi.fn().mockRejectedValue(new Error("autoplay blocked"));
    mountPlayButton({ audio, toolbar });
    const btn = toolbar.querySelector("button");
    // Clicking must not throw synchronously even if the audio API rejects
    expect(() => btn.click()).not.toThrow();
    // Allow the rejected promise to settle
    await new Promise((r) => setTimeout(r, 0));
  });
});

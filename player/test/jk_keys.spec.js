// F39 T-04 — J/K keyboard handlers (next/prev question_stem).
//
// Spec: N04/F39 DE-03, DE-06. AC: F39-S04/AC-01.
// J advances to the next question_stem block; K reverses to the previous.
// Seek by setting audio.currentTime; never dispatch "continue" — paused
// players stay paused, playing players keep playing through the seek.

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { mountControls, bindKeyboard } from "../js/controls.js";

function block(id, kind, firstMark, lastMark) {
  return { block_id: id, block_kind: kind, first_mark_id: firstMark, last_mark_id: lastMark };
}

const BLOCKS = [
  block("p1", "paragraph",     "p1-0", "p1-2"),
  block("q1", "question_stem", "q1-0", "q1-3"),
  block("d1", "datum",         "d1-0", "d1-1"),
  block("q2", "question_stem", "q2-0", "q2-2"),
  block("p2", "paragraph",     "p2-0", "p2-0"),
  block("q3", "question_stem", "q3-0", "q3-1"),
];

// timings list — start_s for every mark referenced above.
// findActiveMark(timings, currentTime) picks the last mark whose start_s <= t.
const TIMINGS = [
  { mark_id: "p1-0", start_s: 0.0,  end_s: 0.5 },
  { mark_id: "p1-2", start_s: 1.0,  end_s: 1.5 },
  { mark_id: "q1-0", start_s: 2.0,  end_s: 2.5 },
  { mark_id: "q1-3", start_s: 3.0,  end_s: 3.5 },
  { mark_id: "d1-0", start_s: 4.0,  end_s: 4.5 },
  { mark_id: "d1-1", start_s: 5.0,  end_s: 5.5 },
  { mark_id: "q2-0", start_s: 6.0,  end_s: 6.5 },
  { mark_id: "q2-2", start_s: 7.0,  end_s: 7.5 },
  { mark_id: "p2-0", start_s: 8.0,  end_s: 8.5 },
  { mark_id: "q3-0", start_s: 9.0,  end_s: 9.5 },
  { mark_id: "q3-1", start_s: 10.0, end_s: 10.5 },
];

function fire(key) {
  const ev = new KeyboardEvent("keydown", { key, bubbles: true, cancelable: true });
  document.dispatchEvent(ev);
  return ev;
}

describe("F39 T-04 — bindKeyboard J/K", () => {
  let audio;
  let toolbar;
  let c;
  let unbind;

  beforeEach(() => {
    document.body.innerHTML = '<div id="controls"></div><audio id="a"></audio>';
    audio = document.getElementById("a");
    toolbar = document.getElementById("controls");
    audio.play = vi.fn().mockResolvedValue(undefined);
    audio.pause = vi.fn();
    c = mountControls({ audio, toolbar });
    unbind = bindKeyboard(c, document, { blocks: BLOCKS, timings: TIMINGS, audio, toolbar });
  });

  afterEach(() => unbind());

  it("J from playing — seeks to next question_stem first_mark_id", () => {
    c.buttons.play.click(); // playing
    audio.currentTime = TIMINGS.find((t) => t.mark_id === "q1-3").start_s; // inside q1
    fire("J");
    expect(audio.currentTime).toBe(6.0); // q2-0 start_s
    expect(c.getState()).toBe("playing");
  });

  it("J from paused — seeks but does NOT dispatch continue (stays paused)", () => {
    c.buttons.play.click();
    c.buttons.pause.click();
    expect(c.getState()).toBe("paused");
    audio.play.mockClear();
    audio.currentTime = 3.0; // inside q1
    fire("J");
    expect(audio.currentTime).toBe(6.0); // q2-0
    expect(c.getState()).toBe("paused");
    expect(audio.play).not.toHaveBeenCalled();
  });

  it("K from playing — seeks to previous question_stem first_mark_id", () => {
    c.buttons.play.click();
    audio.currentTime = 7.0; // inside q2 (q2-2)
    fire("K");
    expect(audio.currentTime).toBe(2.0); // q1-0
    expect(c.getState()).toBe("playing");
  });

  it("K from paused — seeks but does NOT dispatch continue", () => {
    c.buttons.play.click();
    c.buttons.pause.click();
    audio.play.mockClear();
    audio.currentTime = 7.0;
    fire("K");
    expect(audio.currentTime).toBe(2.0);
    expect(c.getState()).toBe("paused");
    expect(audio.play).not.toHaveBeenCalled();
  });

  it("J on last question — no-op (currentTime unchanged)", () => {
    c.buttons.play.click();
    audio.currentTime = 10.0; // inside q3 (q3-1 mark)
    fire("J");
    expect(audio.currentTime).toBe(10.0);
  });

  it("K on first question — no-op (currentTime unchanged)", () => {
    c.buttons.play.click();
    audio.currentTime = 2.0; // inside q1 (q1-0)
    fire("K");
    expect(audio.currentTime).toBe(2.0);
  });

  it("lowercase j behaves the same as J", () => {
    c.buttons.play.click();
    audio.currentTime = 3.0;
    fire("j");
    expect(audio.currentTime).toBe(6.0);
  });

  it("lowercase k behaves the same as K", () => {
    c.buttons.play.click();
    audio.currentTime = 7.0;
    fire("k");
    expect(audio.currentTime).toBe(2.0);
  });

  it("toolbar advertises J K in aria-keyshortcuts when context provided", () => {
    expect(toolbar.getAttribute("aria-keyshortcuts")).toMatch(/J\s+K/);
  });
});

describe("F39 T-04 — bindKeyboard backwards compat (no context)", () => {
  let audio;
  let toolbar;
  let c;
  let unbind;

  beforeEach(() => {
    document.body.innerHTML = '<div id="controls"></div><audio id="a"></audio>';
    audio = document.getElementById("a");
    toolbar = document.getElementById("controls");
    audio.play = vi.fn().mockResolvedValue(undefined);
    audio.pause = vi.fn();
    c = mountControls({ audio, toolbar });
    unbind = bindKeyboard(c, document); // no context — Space/R only
  });

  afterEach(() => unbind());

  it("Space still toggles play/pause without context", () => {
    fire(" ");
    expect(c.getState()).toBe("playing");
  });

  it("J without context is a no-op (does not throw, no seek)", () => {
    c.buttons.play.click();
    audio.currentTime = 3.0;
    expect(() => fire("J")).not.toThrow();
    expect(audio.currentTime).toBe(3.0);
  });
});

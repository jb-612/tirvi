// F39 T-07 — Economy.pdf page-1 E2E: Phase-0 demo verification.
//
// Spec: N04/F39 DE-01..DE-06. AC: F39-S07/AC-01.
// Exercises the full pause-and-jump affordance against a synthetic
// fixture derived from Economy.pdf page 1.

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { mountControls, bindKeyboard, handleBlockEnd } from "../js/controls.js";
import { questionIndexFromBlocks } from "../js/question_index.js";
import FIXTURE from "./fixtures/economy_page1.json";

// Synthetic TTS timings — one entry per mark_id referenced in the fixture.
// start_s values are evenly spaced; real timings come from the TTS pipeline.
const TIMINGS = [
  { mark_id: "b0-0", start_s: 0.0, end_s: 1.0 },
  { mark_id: "b0-1", start_s: 1.0, end_s: 2.0 },
  { mark_id: "b1-0", start_s: 2.0, end_s: 3.0 },
  { mark_id: "b1-1", start_s: 3.0, end_s: 4.0 },
  { mark_id: "b1-2", start_s: 4.0, end_s: 5.0 },
  { mark_id: "b2-0", start_s: 5.0, end_s: 6.0 },
  { mark_id: "b3-0", start_s: 6.0, end_s: 7.0 },
  { mark_id: "b3-1", start_s: 7.0, end_s: 8.0 },
];

function makeStorage(enabled) {
  const store = { "tirvi.player.auto_pause_after_question": String(enabled) };
  return {
    getItem: (k) => store[k] ?? null,
    setItem: (k, v) => { store[k] = String(v); },
  };
}

function makeControls(initialState = "playing") {
  let state = initialState;
  return {
    getState: () => state,
    dispatch: vi.fn((event) => {
      if (event === "pause" && state === "playing") state = "paused";
      if (event === "continue" && state === "paused") state = "playing";
      return state;
    }),
  };
}

function fire(key) {
  const ev = new KeyboardEvent("keydown", { key, bubbles: true, cancelable: true });
  document.dispatchEvent(ev);
}

describe("F39 T-07 — Economy.pdf page-1 E2E", () => {
  // ── fixture shape ──────────────────────────────────────────────────
  it("fixture has ≥ 1 question_stem block", () => {
    const qs = FIXTURE.blocks.filter((b) => b.block_kind === "question_stem");
    expect(qs.length).toBeGreaterThanOrEqual(1);
  });

  it("questionIndexFromBlocks reports correct total from fixture", () => {
    const expected = FIXTURE.blocks.filter((b) => b.block_kind === "question_stem").length;
    const { total } = questionIndexFromBlocks(FIXTURE.blocks);
    expect(total).toBe(expected);
  });

  // ── auto-pause ─────────────────────────────────────────────────────
  it("auto-pause fires at first question_stem block_end with toggle ON", () => {
    const qs = FIXTURE.blocks.find((b) => b.block_kind === "question_stem");
    const ctrl = makeControls("playing");
    handleBlockEnd({ block_kind: qs.block_kind }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).toHaveBeenCalledWith("pause");
  });

  it("auto-pause does NOT fire when toggle is OFF", () => {
    const qs = FIXTURE.blocks.find((b) => b.block_kind === "question_stem");
    const ctrl = makeControls("playing");
    handleBlockEnd({ block_kind: qs.block_kind }, ctrl, makeStorage(false));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  // ── J key from paused ──────────────────────────────────────────────
  describe("J key from paused state", () => {
    let audio, toolbar, c, unbind;

    beforeEach(() => {
      document.body.innerHTML = '<div id="toolbar"></div><audio id="a"></audio>';
      audio = document.getElementById("a");
      toolbar = document.getElementById("toolbar");
      audio.play = vi.fn().mockResolvedValue(undefined);
      audio.pause = vi.fn();
      c = mountControls({ audio, toolbar });
      unbind = bindKeyboard(c, document, {
        blocks: FIXTURE.blocks,
        timings: TIMINGS,
        audio,
        toolbar,
      });
    });

    afterEach(() => unbind());

    it("J seeks to next question_stem and audio stays paused", () => {
      c.buttons.play.click();
      c.buttons.pause.click();
      expect(c.getState()).toBe("paused");
      audio.play.mockClear();

      const qs = FIXTURE.blocks.filter((b) => b.block_kind === "question_stem");
      audio.currentTime = TIMINGS.find((t) => t.mark_id === qs[0].first_mark_id).start_s;

      fire("J");

      const q2Start = TIMINGS.find((t) => t.mark_id === qs[1].first_mark_id).start_s;
      expect(audio.currentTime).toBe(q2Start);
      expect(c.getState()).toBe("paused");
      expect(audio.play).not.toHaveBeenCalled();
    });

    it("J at last question_stem is a no-op", () => {
      c.buttons.play.click();
      c.buttons.pause.click();
      audio.play.mockClear();

      const qs = FIXTURE.blocks.filter((b) => b.block_kind === "question_stem");
      const lastFirst = qs[qs.length - 1].first_mark_id;
      const expected = TIMINGS.find((t) => t.mark_id === lastFirst).start_s;
      audio.currentTime = expected;

      fire("J");

      expect(audio.currentTime).toBe(expected);
      expect(c.getState()).toBe("paused");
    });
  });
});

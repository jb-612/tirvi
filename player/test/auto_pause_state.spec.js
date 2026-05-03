// F39 T-03 — state-machine extension: auto-pause on question_stem block end.
//
// Spec: N04/F39 DE-01. AC: F39-S03/AC-01.
// Covers FT-265 (pauses on question_stem), FT-266 (no pause on other kinds),
// FT-267 (toggle-off mid-page keeps current pause).

import { describe, it, expect, vi, beforeEach } from "vitest";
import { handleBlockEnd } from "../js/controls.js";

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

describe("F39 T-03 — handleBlockEnd", () => {
  it("ft_265 — pauses on question_stem block end when policy on and playing", () => {
    const ctrl = makeControls("playing");
    handleBlockEnd({ block_kind: "question_stem" }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).toHaveBeenCalledWith("pause");
  });

  it("ft_266 — does NOT pause on paragraph block end (policy on)", () => {
    const ctrl = makeControls("playing");
    handleBlockEnd({ block_kind: "paragraph" }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("ft_266 — does NOT pause on heading block end (policy on)", () => {
    const ctrl = makeControls("playing");
    handleBlockEnd({ block_kind: "heading" }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("ft_266 — does NOT pause on datum block end (policy on)", () => {
    const ctrl = makeControls("playing");
    handleBlockEnd({ block_kind: "datum" }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("policy off — does NOT pause on question_stem block end", () => {
    const ctrl = makeControls("playing");
    handleBlockEnd({ block_kind: "question_stem" }, ctrl, makeStorage(false));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("3 question_stem block ends → 3 pause dispatches when policy on", () => {
    // Each block_end restores playing first (simulating resume between questions)
    const ctrl = makeControls("playing");
    for (let i = 0; i < 3; i++) {
      ctrl.dispatch.mockImplementationOnce((e) => {
        if (e === "pause") return "paused";
        return "playing";
      });
      handleBlockEnd({ block_kind: "question_stem" }, ctrl, makeStorage(true));
    }
    expect(ctrl.dispatch).toHaveBeenCalledTimes(3);
    expect(ctrl.dispatch).toHaveBeenNthCalledWith(1, "pause");
    expect(ctrl.dispatch).toHaveBeenNthCalledWith(2, "pause");
    expect(ctrl.dispatch).toHaveBeenNthCalledWith(3, "pause");
  });

  it("0 pauses when policy off across 3 question_stem block ends", () => {
    const ctrl = makeControls("playing");
    const storage = makeStorage(false);
    for (let i = 0; i < 3; i++) {
      handleBlockEnd({ block_kind: "question_stem" }, ctrl, storage);
    }
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("ft_267 — player already paused: block_end does not dispatch again", () => {
    // Covers: mid-page toggle-off leaves current pause intact.
    // The pause is already in effect; handleBlockEnd must not re-dispatch.
    const ctrl = makeControls("paused");
    handleBlockEnd({ block_kind: "question_stem" }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("ft_267 — toggle off mid-pause: current pause stays (no dispatch needed)", () => {
    // Player is paused from a previous auto-pause.
    // User toggles policy OFF. Next block_end fires.
    // State is still "paused" — block_end should NOT dispatch.
    const ctrl = makeControls("paused");
    handleBlockEnd({ block_kind: "question_stem" }, ctrl, makeStorage(false));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("does not dispatch when player is idle", () => {
    const ctrl = makeControls("idle");
    handleBlockEnd({ block_kind: "question_stem" }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });

  it("does not dispatch when player has ended", () => {
    const ctrl = makeControls("ended");
    handleBlockEnd({ block_kind: "question_stem" }, ctrl, makeStorage(true));
    expect(ctrl.dispatch).not.toHaveBeenCalled();
  });
});

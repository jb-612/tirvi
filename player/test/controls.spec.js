// F36 — controls + state-machine + keyboard + ARIA tests.
//
// Covers T-01 (DOM scaffold), T-02 (state machine), T-03 (handlers),
// T-04 (enable/disable), T-05 (keyboard), T-06 (ARIA + focus).
// Spec: N04/F36. Bounded context: bc:audio_delivery.

import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import {
  mountControls,
  mountPlayButton,
  nextState,
  disabledFor,
  bindKeyboard,
} from "../js/controls.js";

describe("F36 T-02 — nextState (pure player state machine)", () => {
  it("us_01_ac_01 — idle → play → playing", () => {
    expect(nextState("idle", "play")).toBe("playing");
  });
  it("us_01_ac_01 — playing → pause → paused", () => {
    expect(nextState("playing", "pause")).toBe("paused");
  });
  it("us_01_ac_01 — paused → continue → playing", () => {
    expect(nextState("paused", "continue")).toBe("playing");
  });
  it("us_01_ac_01 — playing → audio_ended → ended", () => {
    expect(nextState("playing", "audio_ended")).toBe("ended");
  });
  it("us_01_ac_01 — ended → play → playing (replay from idle)", () => {
    expect(nextState("ended", "play")).toBe("playing");
  });
  it("us_01_ac_01 — reset from any state → idle", () => {
    for (const s of ["idle", "playing", "paused", "ended"]) {
      expect(nextState(s, "reset")).toBe("idle");
    }
  });
  it("us_02_ac_01 — invalid transitions return current state unchanged", () => {
    expect(nextState("idle", "pause")).toBe("idle");
    expect(nextState("idle", "continue")).toBe("idle");
    expect(nextState("playing", "play")).toBe("playing");
    expect(nextState("paused", "pause")).toBe("paused");
    expect(nextState("ended", "pause")).toBe("ended");
    expect(nextState("ended", "continue")).toBe("ended");
    expect(nextState("idle", "audio_ended")).toBe("idle");
  });
});

describe("F36 T-04 — disabledFor (enable/disable per state)", () => {
  it("us_01_ac_01 — idle: only Play enabled", () => {
    expect(disabledFor("idle")).toEqual({
      play: false, pause: true, continue: true, reset: true,
    });
  });
  it("us_01_ac_01 — playing: only Pause enabled", () => {
    expect(disabledFor("playing")).toEqual({
      play: true, pause: false, continue: true, reset: true,
    });
  });
  it("us_01_ac_01 — paused: Continue + Reset enabled", () => {
    expect(disabledFor("paused")).toEqual({
      play: true, pause: true, continue: false, reset: false,
    });
  });
  it("us_01_ac_01 — ended: Play + Reset enabled", () => {
    expect(disabledFor("ended")).toEqual({
      play: false, pause: true, continue: true, reset: false,
    });
  });
});

describe("F36 T-01/T-03 — mountControls (DOM scaffold + handlers)", () => {
  let audio;
  let toolbar;

  beforeEach(() => {
    document.body.innerHTML = '<div id="controls"></div><audio id="a"></audio>';
    audio = document.getElementById("a");
    toolbar = document.getElementById("controls");
    audio.play = vi.fn().mockResolvedValue(undefined);
    audio.pause = vi.fn();
  });

  it("us_01_ac_01 — mounts exactly 4 buttons in order", () => {
    mountControls({ audio, toolbar });
    const buttons = toolbar.querySelectorAll("button");
    expect(buttons.length).toBe(4);
    expect(buttons[0].id).toBe("btn-play");
    expect(buttons[1].id).toBe("btn-pause");
    expect(buttons[2].id).toBe("btn-continue");
    expect(buttons[3].id).toBe("btn-reset");
  });

  it("us_01_ac_01 — Play click dispatches play and calls audio.play()", () => {
    const c = mountControls({ audio, toolbar });
    c.buttons.play.click();
    expect(c.getState()).toBe("playing");
    expect(audio.play).toHaveBeenCalledTimes(1);
  });

  it("us_01_ac_01 — Pause click while playing calls audio.pause()", () => {
    const c = mountControls({ audio, toolbar });
    c.buttons.play.click();
    c.buttons.pause.click();
    expect(c.getState()).toBe("paused");
    expect(audio.pause).toHaveBeenCalledTimes(1);
  });

  it("us_01_ac_01 — Continue from paused resumes audio.play()", () => {
    const c = mountControls({ audio, toolbar });
    c.buttons.play.click();
    c.buttons.pause.click();
    c.buttons.continue.click();
    expect(c.getState()).toBe("playing");
    expect(audio.play).toHaveBeenCalledTimes(2);
  });

  it("us_01_ac_01 — Reset (from paused) rewinds to 0 and returns to idle", () => {
    const c = mountControls({ audio, toolbar });
    c.buttons.play.click();
    c.buttons.pause.click();
    audio.currentTime = 12.3;
    c.buttons.reset.click();
    expect(c.getState()).toBe("idle");
    expect(audio.currentTime).toBe(0);
    expect(audio.pause).toHaveBeenCalled();
  });

  it("us_01_ac_01 — audio 'ended' event drives ended state", () => {
    const c = mountControls({ audio, toolbar });
    c.buttons.play.click();
    audio.dispatchEvent(new Event("ended"));
    expect(c.getState()).toBe("ended");
  });

  it("us_01_ac_01 — audio.play() rejection does not throw synchronously", () => {
    audio.play = vi.fn().mockRejectedValue(new Error("autoplay blocked"));
    const c = mountControls({ audio, toolbar });
    expect(() => c.buttons.play.click()).not.toThrow();
  });
});

describe("F36 T-04 — render disabled flips per state", () => {
  let audio;
  let toolbar;
  let c;

  beforeEach(() => {
    document.body.innerHTML = '<div id="controls"></div><audio id="a"></audio>';
    audio = document.getElementById("a");
    toolbar = document.getElementById("controls");
    audio.play = vi.fn().mockResolvedValue(undefined);
    audio.pause = vi.fn();
    c = mountControls({ audio, toolbar });
  });

  it("us_01_ac_01 — initial idle: only Play enabled in DOM", () => {
    expect(c.buttons.play.disabled).toBe(false);
    expect(c.buttons.pause.disabled).toBe(true);
    expect(c.buttons.continue.disabled).toBe(true);
    expect(c.buttons.reset.disabled).toBe(true);
  });

  it("us_01_ac_01 — after play: Pause becomes the only enabled control", () => {
    c.buttons.play.click();
    expect(c.buttons.play.disabled).toBe(true);
    expect(c.buttons.pause.disabled).toBe(false);
    expect(c.buttons.continue.disabled).toBe(true);
    expect(c.buttons.reset.disabled).toBe(true);
  });

  it("us_01_ac_01 — after pause: Continue + Reset enabled", () => {
    c.buttons.play.click();
    c.buttons.pause.click();
    expect(c.buttons.continue.disabled).toBe(false);
    expect(c.buttons.reset.disabled).toBe(false);
  });
});

describe("F36 T-05 — bindKeyboard (Space, R)", () => {
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
    unbind = bindKeyboard(c, document);
  });
  afterEach(() => unbind());

  function fire(key) {
    const ev = new KeyboardEvent("keydown", { key, bubbles: true, cancelable: true });
    document.dispatchEvent(ev);
    return ev;
  }

  it("us_02_ac_01 — Space from idle plays", () => {
    const ev = fire(" ");
    expect(c.getState()).toBe("playing");
    expect(ev.defaultPrevented).toBe(true);
  });

  it("us_02_ac_01 — Space from playing pauses", () => {
    fire(" ");
    fire(" ");
    expect(c.getState()).toBe("paused");
  });

  it("us_02_ac_01 — Space from paused resumes (continue)", () => {
    fire(" ");
    fire(" ");
    fire(" ");
    expect(c.getState()).toBe("playing");
  });

  it("us_02_ac_01 — Space from ended replays from idle", () => {
    fire(" ");
    audio.dispatchEvent(new Event("ended"));
    expect(c.getState()).toBe("ended");
    fire(" ");
    expect(c.getState()).toBe("playing");
  });

  it("us_02_ac_01 — R always resets and preventDefaults", () => {
    fire(" ");
    const ev = fire("r");
    expect(c.getState()).toBe("idle");
    expect(ev.defaultPrevented).toBe(true);
  });

  it("us_02_ac_01 — uppercase R also resets", () => {
    fire(" ");
    fire("R");
    expect(c.getState()).toBe("idle");
  });
});

describe("F36 T-06 — ARIA labels + keyshortcuts + focus contract", () => {
  let audio;
  let toolbar;

  beforeEach(() => {
    document.body.innerHTML = '<div id="controls"></div><audio id="a"></audio>';
    audio = document.getElementById("a");
    toolbar = document.getElementById("controls");
    audio.play = vi.fn().mockResolvedValue(undefined);
    audio.pause = vi.fn();
  });

  it("us_03_ac_01 — every button exposes aria-label in he+en", () => {
    mountControls({ audio, toolbar });
    const buttons = toolbar.querySelectorAll("button");
    for (const btn of buttons) {
      const label = btn.getAttribute("aria-label") || "";
      expect(label.length).toBeGreaterThan(0);
      // Hebrew block U+0590..U+05FF
      expect(/[֐-׿]/.test(label)).toBe(true);
      // Latin letters
      expect(/[A-Za-z]/.test(label)).toBe(true);
    }
  });

  it("us_03_ac_01 — Space-bound buttons advertise aria-keyshortcuts=Space", () => {
    mountControls({ audio, toolbar });
    expect(toolbar.querySelector("#btn-play").getAttribute("aria-keyshortcuts")).toBe("Space");
    expect(toolbar.querySelector("#btn-pause").getAttribute("aria-keyshortcuts")).toBe("Space");
    expect(toolbar.querySelector("#btn-continue").getAttribute("aria-keyshortcuts")).toBe("Space");
    expect(toolbar.querySelector("#btn-reset").getAttribute("aria-keyshortcuts")).toBe("R");
  });

  it("us_03_ac_01 — buttons are focusable (default tabindex)", () => {
    mountControls({ audio, toolbar });
    const btn = toolbar.querySelector("button");
    btn.focus();
    expect(document.activeElement).toBe(btn);
  });
});

describe("F36 — back-compat: mountPlayButton still mounts the play button", () => {
  it("us_01_ac_01 — returns the Play button element", () => {
    document.body.innerHTML = '<div id="controls"></div><audio id="a"></audio>';
    const audio = document.getElementById("a");
    const toolbar = document.getElementById("controls");
    audio.play = vi.fn().mockResolvedValue(undefined);
    audio.pause = vi.fn();
    const btn = mountPlayButton({ audio, toolbar });
    expect(btn.id).toBe("btn-play");
    btn.click();
    expect(audio.play).toHaveBeenCalledTimes(1);
  });
});

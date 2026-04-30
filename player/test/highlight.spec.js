// F35 T-03 — rAF highlight loop + bbox positioning tests.
//
// Spec: N04/F35 DE-03, DE-04, DE-05. AC: US-01/AC-01.

import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import {
  findActiveMark,
  scaleBbox,
  setMarkerPosition,
  startHighlightLoop,
} from "../js/highlight.js";

describe("F35 T-03 — findActiveMark (binary-search active by currentTime)", () => {
  const timings = [
    { mark_id: "a", start_s: 0.0, end_s: 0.5 },
    { mark_id: "b", start_s: 0.5, end_s: 1.0 },
    { mark_id: "c", start_s: 1.0, end_s: null },
  ];

  it("us_01_ac_01 — picks first mark when currentTime is at 0", () => {
    expect(findActiveMark(timings, 0.0)).toBe("a");
  });

  it("us_01_ac_01 — picks the mark whose interval includes the currentTime", () => {
    expect(findActiveMark(timings, 0.25)).toBe("a");
    expect(findActiveMark(timings, 0.75)).toBe("b");
  });

  it("us_01_ac_01 — picks last mark when currentTime is past last start_s (end_s=null)", () => {
    expect(findActiveMark(timings, 5.0)).toBe("c");
  });

  it("us_01_ac_01 — returns null for empty timings", () => {
    expect(findActiveMark([], 0.0)).toBeNull();
  });

  it("us_01_ac_01 — returns null for negative currentTime", () => {
    expect(findActiveMark(timings, -1.0)).toBeNull();
  });

  it("us_01_ac_01 — picks mark at exact start_s boundary (>=)", () => {
    expect(findActiveMark(timings, 0.5)).toBe("b");
    expect(findActiveMark(timings, 1.0)).toBe("c");
  });
});

describe("F35 T-03 — scaleBbox (retina-safe per DE-05)", () => {
  it("us_01_ac_01 — 1:1 ratio leaves bbox unchanged", () => {
    expect(scaleBbox([10, 20, 30, 40], 1000, 1000)).toEqual([10, 20, 30, 40]);
  });

  it("us_01_ac_01 — 2x upscale doubles all coords", () => {
    expect(scaleBbox([10, 20, 30, 40], 1000, 2000)).toEqual([20, 40, 60, 80]);
  });

  it("us_01_ac_01 — 0.5x downscale halves all coords", () => {
    expect(scaleBbox([10, 20, 30, 40], 1000, 500)).toEqual([5, 10, 15, 20]);
  });

  it("us_01_ac_01 — naturalWidth==0 returns bbox unchanged (defensive)", () => {
    expect(scaleBbox([10, 20, 30, 40], 0, 100)).toEqual([10, 20, 30, 40]);
  });
});

describe("F35 T-03 — setMarkerPosition (DOM side effect)", () => {
  let marker;

  beforeEach(() => {
    document.body.innerHTML = '<div id="m"></div>';
    marker = document.getElementById("m");
  });

  it("us_01_ac_01 — sets left/top/width/height styles in px", () => {
    setMarkerPosition(marker, [10, 20, 30, 40]);
    expect(marker.style.left).toBe("10px");
    expect(marker.style.top).toBe("20px");
    expect(marker.style.width).toBe("30px");
    expect(marker.style.height).toBe("40px");
  });

  it("us_01_ac_01 — sets visibility to visible", () => {
    setMarkerPosition(marker, [0, 0, 1, 1]);
    expect(marker.style.visibility).toBe("visible");
  });
});

describe("F35 T-03 — startHighlightLoop (rAF orchestration)", () => {
  let audio;
  let marker;
  let img;
  let state;

  beforeEach(() => {
    document.body.innerHTML = `
      <audio id="a"></audio>
      <img id="i" />
      <div id="m"></div>
    `;
    audio = document.getElementById("a");
    marker = document.getElementById("m");
    img = document.getElementById("i");
    Object.defineProperty(img, "naturalWidth", { value: 1000, configurable: true });
    Object.defineProperty(img, "clientWidth", { value: 1000, configurable: true });
    state = {
      audio,
      marker,
      pageImage: img,
      timings: [
        { mark_id: "b1-0", start_s: 0.0, end_s: 0.5 },
        { mark_id: "b1-1", start_s: 0.5, end_s: 1.0 },
      ],
      pageProjection: {
        words: [
          { text: "א", bbox: [10, 20, 30, 40] },
          { text: "ב", bbox: [50, 20, 30, 40] },
        ],
        marks_to_word_index: { "b1-0": 0, "b1-1": 1 },
      },
    };
    // jsdom doesn't natively run rAF callbacks; mock to step once
    let frame = 0;
    vi.stubGlobal("requestAnimationFrame", (cb) => {
      if (frame++ < 1) setTimeout(cb, 0);
      return frame;
    });
    vi.stubGlobal("cancelAnimationFrame", () => {});
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("us_01_ac_01 — returns a stop() function (cleanup handle)", () => {
    const stop = startHighlightLoop(state);
    expect(typeof stop).toBe("function");
    stop();
  });

  it("us_01_ac_01 — positions marker to current word's bbox on tick", async () => {
    Object.defineProperty(audio, "currentTime", { value: 0.25, writable: true });
    const stop = startHighlightLoop(state);
    await new Promise((r) => setTimeout(r, 5)); // let rAF mock fire
    expect(marker.style.left).toBe("10px");
    expect(marker.style.top).toBe("20px");
    stop();
  });

  it("us_01_ac_01 — stop() halts further rAF scheduling", () => {
    const stop = startHighlightLoop(state);
    expect(() => stop()).not.toThrow();
  });
});

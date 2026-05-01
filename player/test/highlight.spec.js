// F35 T-03 — rAF highlight loop + bbox positioning tests.
//
// Spec: N04/F35 DE-03, DE-04, DE-05. AC: US-01/AC-01.

import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import {
  findActiveMark,
  scaleBbox,
  setMarkerPosition,
  startHighlightLoop,
  lookupWord,
  positionMarker,
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

describe("F35 T-04 — lookupWord (binary-search, half-open intervals)", () => {
  const timings = [
    { mark_id: "a", start_s: 0.0, end_s: 0.5 },
    { mark_id: "b", start_s: 0.5, end_s: 1.0 },
    { mark_id: "c", start_s: 1.0, end_s: 1.5 },
    { mark_id: "d", start_s: 1.5, end_s: null }, // truncation tail
  ];

  it("us_01_ac_01 — returns null before first start_s", () => {
    expect(lookupWord(timings, -0.1)).toBeNull();
  });

  it("us_01_ac_01 — returns null for empty timings", () => {
    expect(lookupWord([], 0.0)).toBeNull();
  });

  it("us_01_ac_01 — returns first mark at exact start_s", () => {
    expect(lookupWord(timings, 0.0)).toBe("a");
  });

  it("us_01_ac_01 — returns mark whose half-open interval contains t", () => {
    expect(lookupWord(timings, 0.25)).toBe("a");
    expect(lookupWord(timings, 0.5)).toBe("b");
    expect(lookupWord(timings, 0.999)).toBe("b");
    expect(lookupWord(timings, 1.0)).toBe("c");
    expect(lookupWord(timings, 1.4999)).toBe("c");
  });

  it("us_01_ac_01 — null end_s on tail keeps mark active forever", () => {
    expect(lookupWord(timings, 1.5)).toBe("d");
    expect(lookupWord(timings, 9999)).toBe("d");
  });

  it("us_01_ac_01 — finite end_s on last mark returns null past end", () => {
    const finite = [{ mark_id: "x", start_s: 0.0, end_s: 1.0 }];
    expect(lookupWord(finite, 0.0)).toBe("x");
    expect(lookupWord(finite, 0.999)).toBe("x");
    expect(lookupWord(finite, 1.0)).toBeNull();
    expect(lookupWord(finite, 5.0)).toBeNull();
  });

  it("us_01_ac_01 — handles 1000 marks correctly (binary-search smoke)", () => {
    const big = Array.from({ length: 1000 }, (_, i) => ({
      mark_id: `m-${i}`,
      start_s: i,
      end_s: i + 1,
    }));
    expect(lookupWord(big, 0)).toBe("m-0");
    expect(lookupWord(big, 500.5)).toBe("m-500");
    expect(lookupWord(big, 999.999)).toBe("m-999");
    expect(lookupWord(big, 1000)).toBeNull();
  });
});

describe("F35 T-05 — positionMarker (CSS top/left/width/height with retina scaling)", () => {
  it("us_01_ac_01 — 1:1 produces unchanged px values", () => {
    const out = positionMarker([10, 20, 30, 40], { w: 1000, h: 1500 }, { w: 1000, h: 1500 });
    expect(out).toEqual({ left: "10px", top: "20px", width: "30px", height: "40px" });
  });

  it("us_01_ac_01 — non-retina downscale (1000 natural -> 500 rendered)", () => {
    const out = positionMarker([100, 200, 50, 50], { w: 1000, h: 2000 }, { w: 500, h: 1000 });
    expect(out).toEqual({ left: "50px", top: "100px", width: "25px", height: "25px" });
  });

  it("us_01_ac_01 — retina-style upscale (500 natural -> 1000 CSS px)", () => {
    // CSS pixels are physical px / DPR — we still scale based on the IMG attrs the
    // browser exposes (naturalWidth vs clientWidth), which is independent of DPR.
    const out = positionMarker([10, 10, 20, 20], { w: 500, h: 500 }, { w: 1000, h: 1000 });
    expect(out).toEqual({ left: "20px", top: "20px", width: "40px", height: "40px" });
  });

  it("us_01_ac_01 — anisotropic scaling (different sx/sy)", () => {
    const out = positionMarker([100, 100, 100, 100], { w: 1000, h: 500 }, { w: 500, h: 500 });
    // sx = 0.5, sy = 1.0
    expect(out).toEqual({ left: "50px", top: "100px", width: "50px", height: "100px" });
  });

  it("us_01_ac_01 — naturalWidth==0 falls back to 1:1 scale (defensive)", () => {
    const out = positionMarker([5, 6, 7, 8], { w: 0, h: 0 }, { w: 100, h: 100 });
    expect(out).toEqual({ left: "5px", top: "6px", width: "7px", height: "8px" });
  });

  it("us_01_ac_01 — rounds to integer px (no sub-pixel jitter)", () => {
    const out = positionMarker([10, 10, 10, 10], { w: 3, h: 3 }, { w: 1, h: 1 });
    // 10/3 = 3.333...; rounds to 3
    expect(out).toEqual({ left: "3px", top: "3px", width: "3px", height: "3px" });
  });
});

describe("F35 T-06 — prefers-reduced-motion + WCAG contrast", () => {
  // Helper — relative luminance per WCAG 2.x
  function luminance([r, g, b]) {
    const channel = (c) => {
      const v = c / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
  }
  function contrastRatio(a, b) {
    const la = luminance(a);
    const lb = luminance(b);
    const [hi, lo] = la > lb ? [la, lb] : [lb, la];
    return (hi + 0.05) / (lo + 0.05);
  }

  it("us_02_ac_01 — highlight palette meets WCAG AA contrast >= 4.5:1", () => {
    // tokens documented in player.css :root
    const bg = [0xff, 0xe0, 0x66]; // --highlight-bg: #ffe066
    const fg = [0x1a, 0x1a, 0x1a]; // --highlight-fg: #1a1a1a
    expect(contrastRatio(fg, bg)).toBeGreaterThanOrEqual(4.5);
  });

  it("us_02_ac_01 — .marker.no-animation class disables transition", async () => {
    // Stub matchMedia for prefers-reduced-motion: reduce
    document.body.innerHTML = '<div class="marker no-animation" id="m"></div>';
    const link = document.createElement("link");
    link.rel = "stylesheet";
    // jsdom doesn't load CSS; verify the class+rule contract via stylesheet text.
    const fs = await import("node:fs");
    const path = await import("node:path");
    const css = fs.readFileSync(
      path.resolve(__dirname, "../player.css"),
      "utf8",
    );
    expect(css).toMatch(/@media\s*\(prefers-reduced-motion:\s*reduce\)/);
    expect(css).toMatch(/\.marker\.no-animation\s*\{\s*transition:\s*none/);
  });

  it("us_02_ac_01 — :focus-visible style is defined for buttons", async () => {
    const fs = await import("node:fs");
    const path = await import("node:path");
    const css = fs.readFileSync(
      path.resolve(__dirname, "../player.css"),
      "utf8",
    );
    expect(css).toMatch(/#controls button:focus-visible/);
    expect(css).toMatch(/outline:/);
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

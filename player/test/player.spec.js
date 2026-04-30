// F35 T-01 — bootPlayer orchestrator tests.
//
// Spec: N04/F35 DE-01, DE-02. AC: US-01/AC-01.
// Wire contracts: audio.json (F30, schema), page.json (F22 DE-07, schema).
// Degraded path: post-review C2 (audio.json missing/error → play without
// highlight + non-blocking banner). page.json missing → fail loud.

import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { bootPlayer } from "../js/player.js";

const _validPage = {
  page_image_url: "page-1.png",
  words: [{ text: "א", bbox: [10, 20, 30, 40] }],
  marks_to_word_index: { "b1-0": 0 },
};
const _validAudio = {
  block_id: "b1",
  provider: "tts-marks",
  source: "tts-marks",
  timings: [{ mark_id: "b1-0", start_s: 0.0 }],
};

function _setupDom() {
  document.body.innerHTML = `
    <div id="error-banner" hidden></div>
    <figure id="page-figure"></figure>
    <div id="controls"></div>
    <audio id="audio-element"></audio>
  `;
}

function _mockFetch(map) {
  return vi.fn(async (url) => {
    const body = map[url];
    if (body === undefined) {
      return { ok: false, status: 404, json: async () => ({}) };
    }
    if (body === "error") {
      return { ok: false, status: 500, json: async () => ({}) };
    }
    return { ok: true, status: 200, json: async () => body };
  });
}

describe("F35 T-01 — bootPlayer (happy path)", () => {
  beforeEach(() => {
    _setupDom();
    vi.stubGlobal(
      "fetch",
      _mockFetch({ "page.json": _validPage, "audio.json": _validAudio }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("us_01_ac_01 — fetches both page.json and audio.json", async () => {
    await bootPlayer();
    expect(fetch).toHaveBeenCalledWith("page.json");
    expect(fetch).toHaveBeenCalledWith("audio.json");
  });

  it("us_01_ac_01 — returns state with audio element + parsed projections", async () => {
    const state = await bootPlayer();
    expect(state.audio).toBeInstanceOf(HTMLAudioElement);
    expect(state.pageProjection).toEqual(_validPage);
    expect(state.timings).toEqual(_validAudio.timings);
  });

  it("us_01_ac_01 — wires audio.src to drafts/<sha>/audio.mp3 (POC default)", async () => {
    const state = await bootPlayer();
    // POC default: audio.mp3 colocated with page.json
    expect(state.audio.getAttribute("src")).toBe("audio.mp3");
  });
});

describe("F35 T-01 — bootPlayer (degraded path: missing audio.json)", () => {
  beforeEach(() => {
    _setupDom();
    vi.stubGlobal("fetch", _mockFetch({ "page.json": _validPage })); // audio.json absent
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("us_01_ac_01 — boots without throwing (degraded; post-review C2)", async () => {
    await expect(bootPlayer()).resolves.toBeDefined();
  });

  it("us_01_ac_01 — surfaces a non-blocking error banner", async () => {
    await bootPlayer();
    const banner = document.getElementById("error-banner");
    expect(banner.hidden).toBe(false);
    expect(banner.textContent.length).toBeGreaterThan(0);
  });

  it("us_01_ac_01 — state.timings is empty when audio.json missing", async () => {
    const state = await bootPlayer();
    expect(state.timings).toEqual([]);
  });
});

describe("F35 T-01 — bootPlayer (fail-loud: missing page.json)", () => {
  beforeEach(() => {
    _setupDom();
    vi.stubGlobal("fetch", _mockFetch({ "audio.json": _validAudio })); // page.json absent
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("us_01_ac_01 — throws when page.json is missing (cannot show page image)", async () => {
    await expect(bootPlayer()).rejects.toThrow(/page\.json/);
  });
});

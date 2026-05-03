// F35/F36 integration — main.js orchestration entry point.
//
// Verifies that init() wires bootPlayer → page image → marker → play button
// and hooks the highlight loop to audio play/pause events.

import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";

vi.mock("../js/player.js", () => ({ bootPlayer: vi.fn() }));
vi.mock("../js/controls.js", () => ({
  mountPlayButton: vi.fn(),
  mountControls: vi.fn(() => ({ getState: vi.fn(() => "idle"), dispatch: vi.fn(), buttons: {}, destroy: vi.fn() })),
  bindKeyboard: vi.fn(() => () => {}),
}));
vi.mock("../js/highlight.js", () => ({
  startHighlightLoop: vi.fn(() => vi.fn()),
  findActiveMark: vi.fn(() => null),
}));

import { bootPlayer } from "../js/player.js";
import { mountControls } from "../js/controls.js";
import { startHighlightLoop } from "../js/highlight.js";
import { init } from "../js/main.js";

const _validPage = {
  page_image_url: "page-1.png",
  words: [{ text: "א", bbox: [10, 20, 30, 40] }],
  marks_to_word_index: { "b1-0": 0 },
};

function _makeAudio() {
  const audio = document.createElement("audio");
  audio.play = vi.fn().mockResolvedValue(undefined);
  document.body.appendChild(audio);
  return audio;
}

function _setupDom() {
  document.body.innerHTML = `
    <div id="error-banner" hidden></div>
    <figure id="page-figure"></figure>
    <div id="controls" role="toolbar"></div>
    <audio id="audio-element"></audio>
  `;
}

describe("F35/F36 — init() orchestration", () => {
  beforeEach(() => {
    _setupDom();
    vi.clearAllMocks();
    bootPlayer.mockResolvedValue({
      audio: document.getElementById("audio-element"),
      pageProjection: _validPage,
      timings: [{ mark_id: "b1-0", start_s: 0.0, end_s: 0.5 }],
      audioError: null,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("calls bootPlayer on init", async () => {
    await init();
    expect(bootPlayer).toHaveBeenCalledTimes(1);
  });

  it("injects <img> into #page-figure with page_image_url src", async () => {
    await init();
    const img = document.querySelector("#page-figure img");
    expect(img).not.toBeNull();
    expect(img.src).toContain("page-1.png");
  });

  it("injects marker div into #page-figure", async () => {
    await init();
    const marker = document.querySelector("#page-figure .marker");
    expect(marker).not.toBeNull();
  });

  it("mounts controls into toolbar", async () => {
    await init();
    expect(mountControls).toHaveBeenCalledTimes(1);
    const [{ toolbar }] = mountControls.mock.calls[0];
    expect(toolbar).toBe(document.getElementById("controls"));
  });

  it("starts highlight loop when audio fires play event", async () => {
    await init();
    const audio = document.getElementById("audio-element");
    audio.dispatchEvent(new Event("play"));
    expect(startHighlightLoop).toHaveBeenCalledTimes(1);
  });

  it("stops highlight loop when audio fires pause", async () => {
    const stopFn = vi.fn();
    startHighlightLoop.mockReturnValueOnce(stopFn);
    await init();
    const audio = document.getElementById("audio-element");
    audio.dispatchEvent(new Event("play"));
    audio.dispatchEvent(new Event("pause"));
    expect(stopFn).toHaveBeenCalledTimes(1);
  });

  it("does not throw when bootPlayer rejects (logs error)", async () => {
    bootPlayer.mockRejectedValueOnce(new Error("page.json missing"));
    await expect(init()).resolves.toBeUndefined();
  });
});

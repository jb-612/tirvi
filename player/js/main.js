// F35/F36/F50 — Orchestration entry point.
//
// Wires bootPlayer → page image → marker → 4 controls → highlight loop
// → inspector → version nav → reviewer notes.
// Auto-executes on module load; index.html only needs this one script tag.

import { bootPlayer } from "./player.js";
import { mountControls, bindKeyboard } from "./controls.js";
import { startHighlightLoop, findActiveMark } from "./highlight.js";
import { loadInspector, syncInspectorWord } from "./inspector.js";
import { initVersionNav } from "./version-nav.js";
import { initNotes, switchNotesSha } from "./notes.js";

// ---------------------------------------------------------------------------
// Module-level state shared between init and the rAF loop
// ---------------------------------------------------------------------------

/** @type {{pageJson: Object, audioJson: Object, sha: string}} */
let _current = { pageJson: null, audioJson: null, sha: "" };

export async function init() {
  try {
    // Get current sha from server so version switching and notes work correctly
    const currentInfo = await _fetchJson("/api/current");
    _current.sha = currentInfo ? currentInfo.sha : "";

    const state = await bootPlayer(_current.sha);
    _current.pageJson = state.pageProjection;
    _current.audioJson = _extractAudioJson(state);

    _mountPageImage(state);
    const { marker, img } = _getPageElements();
    _mountControls(state);

    loadInspector(_current.pageJson, _current.audioJson);
    initNotes({ sha: _current.sha });
    _initTabs();
    _initInspectorToggle();

    await initVersionNav({ currentSha: _current.sha, onSwitch: (sha) => _onSwitch(sha, state) });

    _wireHighlightLoop(state, marker, img);
  } catch (e) {
    console.error("[tirvi init]", e);
  }
}

// ---------------------------------------------------------------------------
// Page image setup
// ---------------------------------------------------------------------------

function _mountPageImage(state) {
  const fig = document.getElementById("page-figure");
  const img = document.createElement("img");
  img.id = "page-image";
  img.src = state.pageProjection.page_image_url;
  img.alt = "";
  fig.appendChild(img);

  const marker = document.createElement("div");
  marker.id = "word-marker";
  marker.className = "marker";
  marker.style.visibility = "hidden";
  fig.appendChild(marker);
}

function _getPageElements() {
  return {
    marker: document.getElementById("word-marker"),
    img: document.getElementById("page-image"),
  };
}

// ---------------------------------------------------------------------------
// Controls
// ---------------------------------------------------------------------------

function _mountControls(state) {
  const toolbar = document.getElementById("controls");
  const ctrl = mountControls({ audio: state.audio, toolbar });
  bindKeyboard(ctrl);
  return ctrl;
}

// ---------------------------------------------------------------------------
// rAF highlight loop — wires inspector sync alongside marker positioning
// ---------------------------------------------------------------------------

function _wireHighlightLoop(state, marker, img) {
  let stopLoop = null;

  state.audio.addEventListener("play", () => {
    stopLoop = startHighlightLoop({
      audio: state.audio,
      marker,
      pageImage: img,
      timings: state.timings,
      pageProjection: state.pageProjection,
      onActiveMark: (markId) => syncInspectorWord(markId),
    });
  });

  state.audio.addEventListener("pause", () => {
    if (stopLoop) {
      stopLoop();
      stopLoop = null;
    }
  });
}

// ---------------------------------------------------------------------------
// Version switch
// ---------------------------------------------------------------------------

async function _onSwitch(sha, state) {
  state.audio.pause();
  _current.sha = sha;

  const [pageJson, audioJson] = await Promise.all([
    _fetchJson(`/${sha}/page.json`),
    _fetchJson(`/${sha}/audio.json`),
  ]);

  _current.pageJson = pageJson;
  _current.audioJson = audioJson;
  _current.sha = sha;

  loadInspector(pageJson, audioJson);
  switchNotesSha(sha);

  if (audioJson) {
    state.audio.src = `/${sha}/audio.mp3`;
    state.audio.load();
  }
}

async function _fetchJson(url) {
  try {
    const res = await fetch(url);
    return res.ok ? res.json() : null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Tab UI
// ---------------------------------------------------------------------------

function _initTabs() {
  const tablist = document.getElementById("inspector-tabs");
  if (!tablist) return;
  const tabs = tablist.querySelectorAll("[role='tab']");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => _activateTab(tab, tabs));
  });
  if (tabs.length > 0) _activateTab(tabs[0], tabs);
}

function _activateTab(activeTab, allTabs) {
  allTabs.forEach((t) => {
    const isActive = t === activeTab;
    t.setAttribute("aria-selected", isActive ? "true" : "false");
    const panel = document.getElementById(`tab-${t.dataset.tab}`);
    if (panel) panel.hidden = !isActive;
  });
}

// ---------------------------------------------------------------------------
// Inspector collapse toggle
// ---------------------------------------------------------------------------

function _initInspectorToggle() {
  const btn = document.getElementById("inspector-toggle");
  const inspector = document.getElementById("inspector");
  if (!btn || !inspector) return;

  btn.addEventListener("click", () => {
    const collapsed = inspector.classList.toggle("collapsed");
    btn.textContent = collapsed ? "▶" : "◀";
    btn.setAttribute("aria-label", collapsed ? "Expand inspector" : "Collapse inspector");
    btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
  });
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

function _extractAudioJson(state) {
  // player.js only returns parsed timings; reconstruct a minimal audioJson
  // so inspector can display raw timing rows.
  if (state.timings && state.timings.length > 0) {
    return { timings: state.timings };
  }
  return null;
}

init();

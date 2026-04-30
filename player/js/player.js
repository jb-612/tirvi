// F35 T-01 — Player shell + state initialization.
//
// Spec: N04/F35 DE-01, DE-02. AC: US-01/AC-01.
//
// Fetches page.json (F22 DE-07 wire contract) + audio.json (F30 wire
// contract), parses, wires the <audio> element, and returns the state
// the rAF highlight loop and play-button consume.
//
// Degraded path (post-review C2):
//   - audio.json missing or errored → return state with empty timings;
//     surface a non-blocking error banner; player still plays audio.
//   - page.json missing → throw (cannot show page image; demo is dead).

import { parseAudioTimings } from "./timing.js";

/**
 * @typedef {Object} PlayerState
 * @property {HTMLAudioElement} audio
 * @property {Object} pageProjection - parsed page.json
 * @property {Array} timings - sorted timings from parseAudioTimings (or [])
 * @property {string|null} audioError - non-null when audio.json was missing/errored
 */

/**
 * Boot the player.
 * @returns {Promise<PlayerState>}
 */
export async function bootPlayer() {
  const pageProjection = await _fetchRequired("page.json");
  const audioOutcome = await _fetchOptional("audio.json");
  const audio = _wireAudioElement();

  if (audioOutcome.error) {
    _surfaceErrorBanner(audioOutcome.error);
  }

  return {
    audio,
    pageProjection,
    timings: audioOutcome.json ? parseAudioTimings(audioOutcome.json) : [],
    audioError: audioOutcome.error,
  };
}

async function _fetchRequired(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(
      `F35: required ${url} unreachable (HTTP ${res.status}); demo cannot render the page image`,
    );
  }
  return res.json();
}

async function _fetchOptional(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      return { json: null, error: `${url} unreachable (HTTP ${res.status})` };
    }
    return { json: await res.json(), error: null };
  } catch (e) {
    return { json: null, error: `${url} fetch failed: ${e.message}` };
  }
}

function _wireAudioElement() {
  const audio = document.getElementById("audio-element");
  // POC default — audio.mp3 colocated with page.json under drafts/<sha>/.
  audio.setAttribute("src", "audio.mp3");
  return audio;
}

function _surfaceErrorBanner(message) {
  const banner = document.getElementById("error-banner");
  if (!banner) return;
  banner.hidden = false;
  banner.textContent = `Audio sync unavailable: ${message}. Playback continues without word highlight.`;
}

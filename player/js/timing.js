// F35 — audio.json parser + timing index.
//
// Spec: N04/F35 DE-02. AC: US-01/AC-01.
//
// Parses audio.json (docs/schemas/audio.schema.json) into Player.state.

/**
 * @typedef {Object} Timing
 * @property {string} mark_id
 * @property {number} start_s
 * @property {number|null} end_s
 */

/**
 * Parse audio.json bytes into a sorted timing index.
 * @param {Object} audioJson — raw object from JSON.parse(audio.json bytes)
 * @returns {Timing[]}
 */
export function parseAudioTimings(audioJson) {
  // TODO INV-TIMING-001 (T-02): validate schema (mark_id, start_s required)
  // TODO INV-TIMING-002: sort by start_s ascending
  throw new Error("F35 timing.js — not implemented (scaffold)");
}

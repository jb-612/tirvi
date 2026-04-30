// F35 T-02 — audio.json parser + timing index.
//
// Spec: N04/F35 DE-02. AC: US-01/AC-01.
// Schema: docs/schemas/audio.schema.json (produced by F30).

/**
 * @typedef {Object} Timing
 * @property {string} mark_id
 * @property {number} start_s
 * @property {number|null} [end_s]
 */

/**
 * Parse a parsed-JSON audio.json object into a sorted timing index.
 * Validates that timings is an array and that each entry has the
 * required mark_id + start_s fields. end_s may be null for the
 * truncation-tail case (F30 DE-05). Returns timings sorted by
 * start_s ascending (stable for already-ordered input).
 *
 * @param {Object} audioJson - parsed contents of audio.json
 * @returns {Timing[]}
 * @throws {Error} when timings is missing or any entry lacks required fields
 */
export function parseAudioTimings(audioJson) {
  if (!audioJson || !Array.isArray(audioJson.timings)) {
    throw new Error("audio.json is missing required 'timings' array");
  }
  audioJson.timings.forEach(_assertTimingShape);
  return [...audioJson.timings].sort((a, b) => a.start_s - b.start_s);
}

function _assertTimingShape(t, idx) {
  if (typeof t.mark_id !== "string") {
    throw new Error(`timing[${idx}] missing required mark_id`);
  }
  if (typeof t.start_s !== "number") {
    throw new Error(`timing[${idx}] missing required start_s`);
  }
}

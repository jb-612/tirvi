// F35 — Player shell + state initialization.
//
// Spec: N04/F35 DE-01. AC: US-01/AC-01.
//
// Loads audio.json + page.json (via fetch), wires the <audio> element, and
// boots the rAF highlight loop on play. Degraded path (post-review C2): if
// audio.json is missing or carries `error`, plays audio without highlight
// and surfaces a non-blocking banner; missing page.json fails loud.

/**
 * @typedef {Object} PlayerState
 * @property {Object} audioTimings — parsed audio.json
 * @property {Object} pageProjection — parsed page.json
 * @property {HTMLAudioElement} audio
 * @property {HTMLDivElement} marker
 */

/**
 * Boot the player. Returns initialized state.
 * @returns {Promise<PlayerState>}
 */
export async function bootPlayer() {
  // TODO US-01/AC-01 (T-01..T-02): fetch audio.json + page.json; build state
  // TODO INV-PLAYER-DEG-001 (post-review C2): degraded path on missing audio.json
  // TODO INV-PLAYER-DEG-002: fail loud on missing page.json (cannot show page image)
  throw new Error("F35 player.js — not implemented (scaffold)");
}

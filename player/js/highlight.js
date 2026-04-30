// F35 — rAF-driven word highlight loop + bbox positioning.
//
// Spec: N04/F35 DE-03, DE-04, DE-05. AC: US-01/AC-01.
//
// On <audio> play, starts a requestAnimationFrame loop that reads
// audio.currentTime and updates the marker overlay over the active word's
// bbox. Stops on pause.

/**
 * Start the rAF highlight loop.
 * @param {Object} state — PlayerState from player.js
 */
export function startHighlightLoop(state) {
  // TODO INV-HL-001 (T-03): rAF loop reads audio.currentTime, picks active mark
  // TODO INV-HL-002 (T-04): update marker bbox to active word
  // TODO INV-HL-003 (T-05, DE-05): retina-safe scale based on image.naturalWidth
  // TODO INV-HL-004 (T-06): stop loop on pause/ended
  throw new Error("F35 highlight.js — not implemented (scaffold)");
}

// F36 — 4-button player controls + state machine + keyboard shortcuts.
//
// Spec: N04/F36. AC: US-01/AC-01. Bounded context: bc:audio_delivery.
//
// State machine: "idle" → "playing" ↔ "paused" → "ended"; reset to "idle".

/**
 * @typedef {"idle"|"playing"|"paused"|"ended"} PlayerStateName
 */

/**
 * Pure transition function. Invalid transitions silently return current state.
 * @param {PlayerStateName} state
 * @param {string} event — one of "play", "pause", "restart", "ended"
 * @returns {PlayerStateName}
 */
export function nextState(state, event) {
  // TODO INV-CTRL-001 (T-02): pure function; no side effects; no exceptions
  throw new Error("F36 controls.js — not implemented (scaffold)");
}

/**
 * Mount the 4 control buttons into the toolbar; bind to <audio> element.
 * @param {Object} state — PlayerState from player.js
 */
export function mountControls(state) {
  // TODO INV-CTRL-002 (T-03): create play/pause/restart/replay buttons with ARIA labels
  // TODO INV-CTRL-003 (T-04): bind keyboard shortcuts (Space=toggle, R=restart) with preventDefault on Space
  throw new Error("F36 controls.js — not implemented (scaffold)");
}

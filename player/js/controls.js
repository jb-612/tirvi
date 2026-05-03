// F36/F39 — vanilla controls for the POC reader.
//
// Spec: N04/F36 DE-01..DE-06, N04/F39 DE-01, DE-03. AC: US-01..US-03/AC-01.
// Bounded context: bc:audio_delivery / bc:reading_accommodation.
// Language: vanilla JS (ADR-023).

import { loadAutoPause } from "./auto_pause_policy.js";
import { advanceQuestion } from "./question_index.js";
import { findActiveMark } from "./highlight.js";

/**
 * @typedef {"idle"|"playing"|"paused"|"ended"} PlayerState
 * @typedef {"play"|"pause"|"continue"|"reset"|"audio_ended"} PlayerEvent
 */

/**
 * F36 T-02 — pure state-machine transition function.
 * Invalid transitions return the current state unchanged (no throw).
 *
 * @param {PlayerState} state
 * @param {PlayerEvent} event
 * @returns {PlayerState}
 */
export function nextState(state, event) {
  if (event === "reset") return "idle";
  if (event === "audio_ended") return state === "playing" ? "ended" : state;
  if (event === "play") {
    return state === "idle" || state === "ended" ? "playing" : state;
  }
  if (event === "pause") return state === "playing" ? "paused" : state;
  if (event === "continue") return state === "paused" ? "playing" : state;
  return state;
}

/**
 * F36 T-04 — given a state, returns the disabled-flag for each button.
 * idle    -> Play enabled
 * playing -> Pause enabled
 * paused  -> Continue + Reset enabled
 * ended   -> Play + Reset enabled
 *
 * @param {PlayerState} state
 * @returns {{play: boolean, pause: boolean, continue: boolean, reset: boolean}}
 *          true == disabled
 */
export function disabledFor(state) {
  return {
    play: !(state === "idle" || state === "ended"),
    pause: state !== "playing",
    continue: state !== "paused",
    reset: !(state === "paused" || state === "ended"),
  };
}

const BUTTON_SPEC = [
  { id: "btn-play", event: "play", label: "Play / נגן", keys: "Space" },
  { id: "btn-pause", event: "pause", label: "Pause / השהה", keys: "Space" },
  { id: "btn-continue", event: "continue", label: "Continue / המשך", keys: "Space" },
  { id: "btn-reset", event: "reset", label: "Reset / אפס", keys: "R" },
];

/**
 * F36 T-01 + T-03 — Controls component. Owns the four buttons, the
 * state machine, and the audio side-effect glue. Returned object
 * exposes the live state, transition dispatch, and the button DOM
 * map so tests + keyboard handlers can drive it.
 *
 * @param {Object} args
 * @param {HTMLAudioElement} args.audio
 * @param {HTMLElement} args.toolbar
 * @returns {{
 *   getState: () => PlayerState,
 *   dispatch: (event: PlayerEvent) => PlayerState,
 *   buttons: Record<"play"|"pause"|"continue"|"reset", HTMLButtonElement>,
 *   destroy: () => void,
 * }}
 */
export function mountControls({ audio, toolbar }) {
  /** @type {PlayerState} */
  let state = "idle";
  /** @type {Record<string, HTMLButtonElement>} */
  const buttons = {};

  for (const spec of BUTTON_SPEC) {
    const btn = document.createElement("button");
    btn.id = spec.id;
    btn.type = "button";
    btn.textContent = spec.label;
    btn.setAttribute("aria-label", spec.label);
    btn.setAttribute("aria-keyshortcuts", spec.keys);
    btn.addEventListener("click", () => dispatch(spec.event));
    toolbar.appendChild(btn);
    const key = spec.id.replace("btn-", "");
    buttons[key] = btn;
  }

  function applyDisabled() {
    const dis = disabledFor(state);
    buttons.play.disabled = dis.play;
    buttons.pause.disabled = dis.pause;
    buttons.continue.disabled = dis.continue;
    buttons.reset.disabled = dis.reset;
  }

  function applyAudio(prev, next, event) {
    if (next === "playing" && prev !== "playing") {
      Promise.resolve(audio.play()).catch(() => {});
    } else if (next === "paused" && prev === "playing") {
      audio.pause();
    } else if (event === "reset") {
      audio.pause();
      audio.currentTime = 0;
    }
  }

  function dispatch(event) {
    const prev = state;
    const next = nextState(state, event);
    state = next;
    applyAudio(prev, next, event);
    applyDisabled();
    return state;
  }

  const onEnded = () => dispatch("audio_ended");
  audio.addEventListener("ended", onEnded);

  applyDisabled();

  return {
    getState: () => state,
    dispatch,
    buttons,
    destroy: () => audio.removeEventListener("ended", onEnded),
  };
}

function _handleSpace(controls) {
  const s = controls.getState();
  if (s === "playing") controls.dispatch("pause");
  else if (s === "paused") controls.dispatch("continue");
  else controls.dispatch("play"); // idle / ended
}

function _seekToMark(context, markId) {
  const t = context.timings.find((x) => x.mark_id === markId);
  if (!t) return;
  context.audio.currentTime = t.start_s;
}

// F39 T-04 — seek to neighbouring question_stem; never dispatch continue.
function _handleJump(context, direction) {
  if (!context) return;
  const currentMarkId = findActiveMark(context.timings, context.audio.currentTime);
  if (currentMarkId === null) return;
  const result = advanceQuestion(context.blocks, currentMarkId, direction);
  if (result.markId === null) return;
  _seekToMark(context, result.markId);
}

function _normalizeKey(e) {
  if (e.key === " " || e.code === "Space") return "space";
  const k = e.key.toLowerCase();
  return ["r", "j", "k"].includes(k) ? k : "";
}

function _routeKey(e, controls, context) {
  const k = _normalizeKey(e);
  if (k === "") return;
  e.preventDefault();
  if (k === "space") return _handleSpace(controls);
  if (k === "r") return controls.dispatch("reset");
  if (k === "j") return _handleJump(context, 1);
  return _handleJump(context, -1);
}

/**
 * F36 T-05 + F39 T-04 — keyboard shortcuts.
 * Space toggles play/pause/resume; R resets;
 * J/K (and j/k) jump to next/prev question_stem when context is provided.
 * Returns an unbind() function.
 *
 * @param {{getState: () => PlayerState, dispatch: (e: PlayerEvent) => PlayerState}} controls
 * @param {HTMLElement} [root=document]
 * @param {{blocks: Array, timings: Array, audio: HTMLAudioElement, toolbar?: HTMLElement}} [context]
 *        Optional. When absent, J/K are no-ops and Space/R behaviour is unchanged.
 * @returns {() => void}
 */
export function bindKeyboard(controls, root, context) {
  const target = root || document;
  const handler = (e) => _routeKey(e, controls, context);
  target.addEventListener("keydown", handler);
  if (context && context.toolbar) {
    context.toolbar.setAttribute("aria-keyshortcuts", "J K");
  }
  return () => target.removeEventListener("keydown", handler);
}

/**
 * F39 T-03 — handle a block_end signal from the rAF highlight loop.
 * When the finished block is question_stem AND the auto-pause policy is
 * enabled AND the player is currently playing, dispatch "pause".
 * No-ops for all other block kinds, policy-off, and non-playing states.
 *
 * @param {{block_kind: string}} block
 * @param {{getState: () => string, dispatch: (e: string) => string}} controls
 * @param {object} [storage] - localStorage-shaped adapter (injectable for tests)
 */
export function handleBlockEnd(block, controls, storage) {
  if (block.block_kind !== "question_stem") return;
  if (controls.getState() !== "playing") return;
  if (!loadAutoPause(storage)) return;
  controls.dispatch("pause");
}

/**
 * Back-compat — main.js currently imports `mountPlayButton`. The new
 * `mountControls` supersedes it; keep this thin alias mounting the
 * full 4-button toolbar so existing wiring in main.js still works.
 *
 * @param {Object} args
 * @param {HTMLAudioElement} args.audio
 * @param {HTMLElement} args.toolbar
 * @returns {HTMLButtonElement} the Play button (legacy return shape)
 */
export function mountPlayButton({ audio, toolbar }) {
  const ctrl = mountControls({ audio, toolbar });
  return ctrl.buttons.play;
}

// F35 T-03 — rAF-driven word highlight loop + bbox positioning.
//
// Spec: N04/F35 DE-03, DE-04, DE-05. AC: US-01/AC-01.
//
// On <audio> play, startHighlightLoop runs a requestAnimationFrame loop
// that reads audio.currentTime, picks the active mark, looks up the
// word's bbox in the page projection, scales for retina/render-size
// mismatch, and updates the marker overlay's position. Stops on pause.

/**
 * Find the mark_id whose timing interval covers `currentTime`.
 * Returns null if currentTime is before the first mark or timings is
 * empty. The last mark's end_s may be null (truncation tail per F30
 * DE-05); past the last start_s, that mark stays selected.
 *
 * @param {Array<{mark_id: string, start_s: number, end_s?: number|null}>} timings
 * @param {number} currentTime
 * @returns {string|null}
 */
export function findActiveMark(timings, currentTime) {
  if (timings.length === 0 || currentTime < 0) return null;
  if (currentTime < timings[0].start_s) return null;
  // Linear scan from the back — picks the last mark whose start_s <= t.
  // Smaller than 100 marks per page in POC; binary search not worth the cost.
  for (let i = timings.length - 1; i >= 0; i--) {
    if (timings[i].start_s <= currentTime) return timings[i].mark_id;
  }
  return null;
}

/**
 * Scale a bbox from natural-image coords to rendered-image coords.
 * Defensive: when naturalWidth is 0 or unset, returns the bbox unchanged.
 *
 * @param {[number, number, number, number]} bbox - [x, y, w, h]
 * @param {number} naturalWidth - image.naturalWidth
 * @param {number} renderedWidth - image.clientWidth
 * @returns {[number, number, number, number]}
 */
export function scaleBbox(bbox, naturalWidth, renderedWidth) {
  if (!naturalWidth) return bbox;
  const ratio = renderedWidth / naturalWidth;
  return bbox.map((v) => Math.round(v * ratio));
}

/**
 * Apply a bbox to the marker DOM element.
 * @param {HTMLElement} marker
 * @param {[number, number, number, number]} bbox
 */
export function setMarkerPosition(marker, bbox) {
  marker.style.left = `${bbox[0]}px`;
  marker.style.top = `${bbox[1]}px`;
  marker.style.width = `${bbox[2]}px`;
  marker.style.height = `${bbox[3]}px`;
  marker.style.visibility = "visible";
}

/**
 * Start the rAF highlight loop. Returns a stop() function that cancels
 * any pending frame. Idempotent — calling stop() twice is harmless.
 *
 * @param {Object} state
 * @param {HTMLAudioElement} state.audio
 * @param {HTMLElement} state.marker
 * @param {HTMLImageElement} state.pageImage
 * @param {Array} state.timings
 * @param {Object} state.pageProjection - {words[], marks_to_word_index}
 * @returns {() => void} stop function
 */
export function startHighlightLoop(state) {
  let rafId = 0;
  let stopped = false;

  const tick = () => {
    if (stopped) return;
    _renderActiveWord(state);
    rafId = requestAnimationFrame(tick);
  };

  rafId = requestAnimationFrame(tick);
  return () => {
    stopped = true;
    if (rafId) cancelAnimationFrame(rafId);
  };
}

function _renderActiveWord(state) {
  const markId = findActiveMark(state.timings, state.audio.currentTime);
  if (!markId) return;
  const wordIndex = state.pageProjection.marks_to_word_index[markId];
  if (wordIndex === undefined) return;
  const word = state.pageProjection.words[wordIndex];
  if (!word) return;
  const scaled = scaleBbox(
    word.bbox,
    state.pageImage.naturalWidth,
    state.pageImage.clientWidth,
  );
  setMarkerPosition(state.marker, scaled);
}

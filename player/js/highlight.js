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
 * F35 T-04 — strict-interval word lookup via binary search.
 *
 * Returns the mark_id of the timing whose half-open interval
 * [start_s, end_s) contains `tSeconds`. Unlike findActiveMark (which
 * "sticks" to the last mark forever), lookupWord returns null once
 * tSeconds has passed the last interval's end_s, and null when
 * tSeconds is before the first interval's start_s.
 *
 * end_s may be null (F30 DE-05 truncation tail); for that final
 * entry, any tSeconds >= start_s matches.
 *
 * @param {Array<{mark_id: string, start_s: number, end_s?: number|null}>} timings
 *        Must be sorted ascending by start_s (parseAudioTimings guarantees this).
 * @param {number} tSeconds
 * @returns {string|null}
 */
export function lookupWord(timings, tSeconds) {
  const n = timings.length;
  if (n === 0 || !Number.isFinite(tSeconds) || tSeconds < 0) return null;
  if (tSeconds < timings[0].start_s) return null;

  let lo = 0;
  let hi = n - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >>> 1;
    if (timings[mid].start_s <= tSeconds) lo = mid;
    else hi = mid - 1;
  }
  const cand = timings[lo];
  const end = cand.end_s;
  if (end === null || end === undefined) return cand.mark_id;
  return tSeconds < end ? cand.mark_id : null;
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
 * F35 T-05 — scale a bbox in natural-image coords to CSS pixels in
 * rendered-image coords, returning a `{top, left, width, height}`
 * object suitable for direct assignment to element.style.
 *
 * `imageNatural` and `imageRendered` are `{w, h}` pairs, e.g.
 * `{w: image.naturalWidth, h: image.naturalHeight}` for natural and
 * `{w: image.clientWidth, h: image.clientHeight}` for rendered.
 *
 * Retina-safe: scaling uses the image-rendered ratio, not
 * window.devicePixelRatio — the browser already maps CSS pixels
 * to physical pixels.
 *
 * Returns rounded integer pixel values to avoid sub-pixel jitter.
 *
 * @param {[number, number, number, number]} bbox - [x, y, w, h]
 * @param {{w: number, h: number}} imageNatural
 * @param {{w: number, h: number}} imageRendered
 * @returns {{top: string, left: string, width: string, height: string}}
 */
export function positionMarker(bbox, imageNatural, imageRendered) {
  const [x, y, w, h] = bbox;
  const sx = imageNatural.w ? imageRendered.w / imageNatural.w : 1;
  const sy = imageNatural.h ? imageRendered.h / imageNatural.h : 1;
  return {
    left: `${Math.round(x * sx)}px`,
    top: `${Math.round(y * sy)}px`,
    width: `${Math.round(w * sx)}px`,
    height: `${Math.round(h * sy)}px`,
  };
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

// Wavenet timestamps lead perceived audio by ~300ms due to buffering.
// Subtract this offset so the highlight matches what the listener hears.
const HIGHLIGHT_OFFSET_S = parseFloat(
  document.documentElement.dataset.highlightOffset ?? "0.3"
);

function _renderActiveWord(state) {
  const t = Math.max(0, state.audio.currentTime - HIGHLIGHT_OFFSET_S);
  const markId = findActiveMark(state.timings, t);
  // Notify inspector regardless of whether we can resolve a bbox.
  if (typeof state.onActiveMark === "function") state.onActiveMark(markId);
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

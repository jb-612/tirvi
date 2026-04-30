// F36 T-01 — single play button mount (POC scope).
//
// Spec: N04/F36 DE-01. AC: US-01/AC-01. Bounded context: bc:audio_delivery.
// Language: vanilla JS (ADR-023). Per POC-CRITICAL-PATH.md, T-02..T-06
// (full 4-button state machine, ARIA shortcuts, focus management, disabled
// states) deferred to v0.1.

/**
 * Mount a single play button into the toolbar; clicking it triggers
 * audio.play(). Rejections from the audio API (e.g., autoplay-blocked
 * before a user gesture) are swallowed so the click handler stays
 * synchronous and never throws.
 *
 * @param {Object} args
 * @param {HTMLAudioElement} args.audio - the page's <audio> element
 * @param {HTMLElement} args.toolbar - the container to mount into
 * @returns {HTMLButtonElement} the mounted button (useful for tests)
 */
export function mountPlayButton({ audio, toolbar }) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = "Play";
  btn.setAttribute("aria-label", "Play");
  btn.addEventListener("click", () => {
    // .play() returns a Promise; swallow rejection (autoplay policy etc.)
    Promise.resolve(audio.play()).catch(() => {
      /* noop — degraded path; downstream UI may surface the error */
    });
  });
  toolbar.appendChild(btn);
  return btn;
}

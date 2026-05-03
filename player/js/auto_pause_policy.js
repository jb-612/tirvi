// F39 T-01 — auto-pause policy module + localStorage persistence.
//
// Spec: N04/F39 DE-01, DE-05. AC: F39-S01/AC-01.
// Bounded context: bc:reading_accommodation. Language: vanilla JS (ADR-023).

export const STORAGE_KEY = "tirvi.player.auto_pause_after_question";

function _storage(adapter) {
  if (adapter) return adapter;
  return typeof window !== "undefined" ? window.localStorage : null;
}

/**
 * Read the auto-pause toggle from a localStorage-shaped adapter.
 * Returns true (the default per F39 DE-05) on missing key, parse
 * failure, or storage exception.
 *
 * @param {{getItem: (k: string) => string | null}} [adapter]
 * @returns {boolean}
 */
export function loadAutoPause(adapter) {
  const storage = _storage(adapter);
  if (!storage) return true;
  let raw;
  try {
    raw = storage.getItem(STORAGE_KEY);
  } catch {
    return true;
  }
  if (raw === "true") return true;
  if (raw === "false") return false;
  return true;
}

/**
 * Persist the auto-pause toggle. Swallows quota / SecurityError
 * exceptions per FT-278 (private browsing / quota exceeded keeps
 * the in-memory toggle working).
 *
 * @param {boolean} enabled
 * @param {{setItem: (k: string, v: string) => void}} [adapter]
 */
export function saveAutoPause(enabled, adapter) {
  const storage = _storage(adapter);
  if (!storage) return;
  try {
    storage.setItem(STORAGE_KEY, enabled ? "true" : "false");
  } catch (e) {
    console.warn("[F39] auto-pause persistence failed:", e.message || e);
  }
}

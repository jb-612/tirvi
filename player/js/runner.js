// N04/F33 DE-05 — Run number management
// Exports: currentRunNumber, listAvailableRuns, renderRunError

const RUN_PARAM_RE = /^\d{1,3}$/;

/**
 * Returns the run number string from ?run=NNN URL param, or null if absent/invalid.
 * @param {string} searchString - URLSearchParams-compatible query string
 *   (defaults to window.location.search so callers can pass a test value)
 */
export function currentRunNumber(searchString = window.location.search) {
  const params = new URLSearchParams(searchString);
  const run = params.get("run");
  if (run === null) return null;
  const trimmed = run.trim();
  return RUN_PARAM_RE.test(trimmed) ? trimmed : null;
}

/**
 * Fetches manifest-index.json from baseUrl and returns array of run descriptors.
 * Returns [] on any error or non-ok response — never throws.
 * @param {string} baseUrl
 * @returns {Promise<Array>}
 */
export async function listAvailableRuns(baseUrl) {
  try {
    const response = await fetch(`${baseUrl}/manifest-index.json`);
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
}

/**
 * Renders an accessible error paragraph inside panel.
 * Clears panel first. Uses textContent (not innerHTML).
 * @param {HTMLElement} panel
 * @param {string} message
 */
export function renderRunError(panel, message) {
  panel.innerHTML = "";
  const p = document.createElement("p");
  p.className = "run-error";
  p.setAttribute("role", "alert");
  p.textContent = message;
  panel.appendChild(p);
}

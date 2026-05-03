// F39 T-06 — settings-panel auto-pause toggle row.
//
// Spec: N04/F39 DE-05. AC: F39-S06/AC-01.
// Bounded context: bc:reading_accommodation. Language: vanilla JS (ADR-023).

import { loadAutoPause, saveAutoPause } from "./auto_pause_policy.js";

const TOOLTIP = "לחץ J למעבר לשאלה הבאה, K לשאלה הקודמת (press J = next question, K = previous)";

/**
 * Mount the F39 settings panel with the auto-pause toggle row.
 * Appends a .settings-panel element to `parent` and returns it.
 *
 * @param {HTMLElement} parent
 * @param {object} [storage] - localStorage-shaped adapter (injectable for tests)
 * @returns {HTMLElement} the mounted panel element
 */
export function mountSettingsPanel(parent, storage) {
  const panel = document.createElement("div");
  panel.className = "settings-panel";
  panel.title = TOOLTIP;

  const label = document.createElement("label");
  label.textContent = "השהיה אוטומטית בסוף שאלה ";

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = loadAutoPause(storage);
  checkbox.addEventListener("click", () => saveAutoPause(checkbox.checked, storage));

  label.appendChild(checkbox);
  panel.appendChild(label);
  parent.appendChild(panel);
  return panel;
}

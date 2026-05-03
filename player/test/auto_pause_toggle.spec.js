// F39 T-06 — settings-panel auto-pause toggle row.
//
// Spec: N04/F39 DE-05. AC: F39-S06/AC-01.
// Covers FT-262 (click toggles + persists), FT-261 (initial state from storage).

import { describe, it, expect, beforeEach, vi } from "vitest";
import { mountSettingsPanel } from "../js/settings_panel.js";

function makeStorage(enabled) {
  const store = { "tirvi.player.auto_pause_after_question": String(enabled) };
  return {
    getItem: (k) => store[k] ?? null,
    setItem: vi.fn((k, v) => { store[k] = String(v); }),
  };
}

describe("F39 T-06 — mountSettingsPanel", () => {
  let container;
  beforeEach(() => {
    container = document.createElement("div");
  });

  it("appends a settings panel element to the container", () => {
    mountSettingsPanel(container, makeStorage(true));
    expect(container.querySelector(".settings-panel")).not.toBeNull();
  });

  it("ft_261 — checkbox initial state is checked when policy is ON", () => {
    mountSettingsPanel(container, makeStorage(true));
    const cb = container.querySelector("input[type='checkbox']");
    expect(cb.checked).toBe(true);
  });

  it("ft_261 — checkbox initial state is unchecked when policy is OFF", () => {
    mountSettingsPanel(container, makeStorage(false));
    const cb = container.querySelector("input[type='checkbox']");
    expect(cb.checked).toBe(false);
  });

  it("renders label text in Hebrew", () => {
    mountSettingsPanel(container, makeStorage(true));
    const label = container.querySelector("label");
    expect(label.textContent).toContain("השהיה אוטומטית בסוף שאלה");
  });

  it("ft_262 — clicking checkbox persists the new value via saveAutoPause", () => {
    const storage = makeStorage(true);
    mountSettingsPanel(container, storage);
    const cb = container.querySelector("input[type='checkbox']");
    cb.click();
    expect(storage.setItem).toHaveBeenCalledWith(
      "tirvi.player.auto_pause_after_question",
      "false"
    );
  });

  it("ft_262 — clicking again toggles back to true", () => {
    const storage = makeStorage(false);
    mountSettingsPanel(container, storage);
    const cb = container.querySelector("input[type='checkbox']");
    cb.click();
    expect(storage.setItem).toHaveBeenLastCalledWith(
      "tirvi.player.auto_pause_after_question",
      "true"
    );
  });

  it("tooltip describes J/K shortcuts", () => {
    mountSettingsPanel(container, makeStorage(true));
    const panel = container.querySelector(".settings-panel");
    const tooltip = panel.title || panel.getAttribute("aria-description") ||
      container.querySelector("[title]")?.title || "";
    expect(tooltip.toLowerCase()).toMatch(/j|k/);
  });

  it("returns the panel element", () => {
    const el = mountSettingsPanel(container, makeStorage(true));
    expect(el).toBe(container.querySelector(".settings-panel"));
  });
});

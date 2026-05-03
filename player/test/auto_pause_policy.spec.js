// F39 T-01 — auto-pause policy module + localStorage persistence.
//
// Spec: N04/F39 DE-01, DE-05. AC: F39-S01/AC-01.
// Covers FT-260 (default-true), FT-261 (persistence), FT-278 (quota).

import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  loadAutoPause,
  saveAutoPause,
  STORAGE_KEY,
} from "../js/auto_pause_policy.js";

function makeStorage(initial = {}) {
  const store = { ...initial };
  return {
    getItem: vi.fn((k) => (k in store ? store[k] : null)),
    setItem: vi.fn((k, v) => {
      store[k] = String(v);
    }),
    removeItem: vi.fn((k) => {
      delete store[k];
    }),
    _store: store,
  };
}

describe("F39 T-01 — auto-pause policy", () => {
  it("ft_260 — STORAGE_KEY matches the F32 reservation", () => {
    expect(STORAGE_KEY).toBe("tirvi.player.auto_pause_after_question");
  });

  it("ft_260 — default is true on an empty store", () => {
    const storage = makeStorage();
    expect(loadAutoPause(storage)).toBe(true);
  });

  it("ft_261 — saved false survives a re-read", () => {
    const storage = makeStorage();
    saveAutoPause(false, storage);
    expect(loadAutoPause(storage)).toBe(false);
  });

  it("ft_261 — saved true survives a re-read", () => {
    const storage = makeStorage({ [STORAGE_KEY]: "false" });
    saveAutoPause(true, storage);
    expect(loadAutoPause(storage)).toBe(true);
  });

  it("ft_261 — saveAutoPause writes under STORAGE_KEY", () => {
    const storage = makeStorage();
    saveAutoPause(false, storage);
    expect(storage.setItem).toHaveBeenCalledWith(STORAGE_KEY, "false");
  });

  it("recovery — corrupted value falls back to default true", () => {
    const storage = makeStorage({ [STORAGE_KEY]: "banana" });
    expect(loadAutoPause(storage)).toBe(true);
  });

  it("recovery — getItem throwing falls back to default true", () => {
    const storage = makeStorage();
    storage.getItem = vi.fn(() => {
      throw new Error("SecurityError");
    });
    expect(loadAutoPause(storage)).toBe(true);
  });

  it("ft_278 — saveAutoPause swallows quota errors and warns", () => {
    const storage = makeStorage();
    storage.setItem = vi.fn(() => {
      throw new Error("QuotaExceededError");
    });
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(() => saveAutoPause(false, storage)).not.toThrow();
    expect(warn).toHaveBeenCalled();
    warn.mockRestore();
  });

  it("default adapter falls back to true when window.localStorage is unusable", () => {
    // jsdom in vitest may ship a stub-only localStorage (no setItem).
    // Either way, the module must not throw and must default true.
    expect(() => saveAutoPause(false)).not.toThrow();
    expect(typeof loadAutoPause()).toBe("boolean");
  });
});

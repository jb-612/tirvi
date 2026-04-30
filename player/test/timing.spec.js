// F35 T-02 — audio.json parser tests.
//
// Spec: N04/F35 DE-02. AC: US-01/AC-01.
// Schema: docs/schemas/audio.schema.json (produced by F30).

import { describe, it, expect } from "vitest";
import { parseAudioTimings } from "../js/timing.js";

describe("F35 T-02 — parseAudioTimings", () => {
  it("us_01_ac_01 — extracts timings array from audio.json", () => {
    const json = {
      block_id: "b1",
      provider: "tts-marks",
      source: "tts-marks",
      timings: [
        { mark_id: "b1-0", start_s: 0.0, end_s: 0.5 },
        { mark_id: "b1-1", start_s: 0.5, end_s: 1.0 },
      ],
    };
    const out = parseAudioTimings(json);
    expect(out).toHaveLength(2);
    expect(out[0].mark_id).toBe("b1-0");
    expect(out[0].start_s).toBe(0.0);
  });

  it("us_01_ac_01 — sorts timings by start_s ascending", () => {
    const json = {
      timings: [
        { mark_id: "c", start_s: 2.0 },
        { mark_id: "a", start_s: 0.0 },
        { mark_id: "b", start_s: 1.0 },
      ],
    };
    const out = parseAudioTimings(json);
    expect(out.map((t) => t.mark_id)).toEqual(["a", "b", "c"]);
  });

  it("us_01_ac_01 — preserves null end_s (truncation tail per F30 DE-05)", () => {
    const json = {
      timings: [
        { mark_id: "a", start_s: 0.0, end_s: 0.5 },
        { mark_id: "b", start_s: 0.5, end_s: null },
      ],
    };
    const out = parseAudioTimings(json);
    expect(out[1].end_s).toBeNull();
  });

  it("us_01_ac_01 — empty timings list returns empty array", () => {
    expect(parseAudioTimings({ timings: [] })).toEqual([]);
  });

  it("us_01_ac_01 — missing timings field throws", () => {
    expect(() => parseAudioTimings({})).toThrow();
  });

  it("us_01_ac_01 — missing required mark_id throws", () => {
    const json = { timings: [{ start_s: 0.0 }] };
    expect(() => parseAudioTimings(json)).toThrow(/mark_id/);
  });

  it("us_01_ac_01 — missing required start_s throws", () => {
    const json = { timings: [{ mark_id: "a" }] };
    expect(() => parseAudioTimings(json)).toThrow(/start_s/);
  });

  it("us_01_ac_01 — sort is stable across already-sorted input (no reordering)", () => {
    const sorted = [
      { mark_id: "a", start_s: 0.0 },
      { mark_id: "b", start_s: 0.5 },
    ];
    const out = parseAudioTimings({ timings: sorted });
    expect(out.map((t) => t.mark_id)).toEqual(["a", "b"]);
  });
});

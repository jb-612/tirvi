// F39 T-02 — questionIndex computation.
//
// Spec: N04/F39 DE-02. AC: F39-S02/AC-01.
// Covers FT-263 (from_blocks), FT-264 (advance), FT-270 (last no-op),
// FT-271 (first no-op), FT-274 (zero question_stem blocks).

import { describe, it, expect } from "vitest";
import {
  questionIndexFromBlocks,
  advanceQuestion,
} from "../js/question_index.js";

// Minimal block fixture matching the page.json blocks[] shape from F22 T-08.
function block(id, kind, firstMark, lastMark) {
  return { block_id: id, block_kind: kind, first_mark_id: firstMark, last_mark_id: lastMark };
}

const THREE_QUESTIONS = [
  block("p1", "paragraph",     "p1-0", "p1-2"),
  block("q1", "question_stem", "q1-0", "q1-3"),
  block("d1", "datum",         "d1-0", "d1-1"),
  block("q2", "question_stem", "q2-0", "q2-2"),
  block("p2", "paragraph",     "p2-0", "p2-0"),
  block("q3", "question_stem", "q3-0", "q3-1"),
];

describe("F39 T-02 — questionIndexFromBlocks", () => {
  it("ft_263 — returns current=1, total=3 for page with 3 question_stem blocks", () => {
    const idx = questionIndexFromBlocks(THREE_QUESTIONS);
    expect(idx.total).toBe(3);
    expect(idx.current).toBe(1);
  });

  it("ft_274 — zero question_stem blocks → total=0, current=0", () => {
    const blocks = [
      block("p1", "paragraph", "p1-0", "p1-2"),
      block("h1", "heading",   "h1-0", "h1-0"),
    ];
    const idx = questionIndexFromBlocks(blocks);
    expect(idx.total).toBe(0);
    expect(idx.current).toBe(0);
  });

  it("returns current=0 and total=0 for empty blocks array", () => {
    const idx = questionIndexFromBlocks([]);
    expect(idx.total).toBe(0);
    expect(idx.current).toBe(0);
  });

  it("current=1 on a single question_stem page", () => {
    const blocks = [block("q1", "question_stem", "q1-0", "q1-1")];
    const idx = questionIndexFromBlocks(blocks);
    expect(idx.total).toBe(1);
    expect(idx.current).toBe(1);
  });
});

describe("F39 T-02 — advanceQuestion", () => {
  it("ft_264 — advance from q1 last mark → moves to question 2", () => {
    // currentMarkId is the last mark of q1
    const result = advanceQuestion(THREE_QUESTIONS, "q1-3", 1);
    expect(result.current).toBe(2);
    expect(result.markId).toBe("q2-0");
  });

  it("advance from q2 last mark → moves to question 3", () => {
    const result = advanceQuestion(THREE_QUESTIONS, "q2-2", 1);
    expect(result.current).toBe(3);
    expect(result.markId).toBe("q3-0");
  });

  it("ft_270 — advance from last question → no-op (current stays, markId null)", () => {
    const result = advanceQuestion(THREE_QUESTIONS, "q3-1", 1);
    expect(result.current).toBe(3);
    expect(result.markId).toBeNull();
  });

  it("reverse from q2 first mark → moves to question 1", () => {
    const result = advanceQuestion(THREE_QUESTIONS, "q2-0", -1);
    expect(result.current).toBe(1);
    expect(result.markId).toBe("q1-0");
  });

  it("ft_271 — reverse from first question → no-op (current stays, markId null)", () => {
    const result = advanceQuestion(THREE_QUESTIONS, "q1-0", -1);
    expect(result.current).toBe(1);
    expect(result.markId).toBeNull();
  });

  it("mark_id inside a non-question block → advances to next question_stem", () => {
    // currentMarkId is in the datum block d1 between q1 and q2
    const result = advanceQuestion(THREE_QUESTIONS, "d1-0", 1);
    expect(result.current).toBe(2);
    expect(result.markId).toBe("q2-0");
  });

  it("mark_id inside a non-question block → reverses to previous question_stem", () => {
    const result = advanceQuestion(THREE_QUESTIONS, "d1-0", -1);
    expect(result.current).toBe(1);
    expect(result.markId).toBe("q1-0");
  });

  it("unknown mark_id → defaults to question 1 first mark on advance", () => {
    const result = advanceQuestion(THREE_QUESTIONS, "unknown-mark", 1);
    expect(result.current).toBe(1);
    expect(result.markId).toBe("q1-0");
  });

  it("zero question_stem blocks → returns current=0, markId=null", () => {
    const blocks = [block("p1", "paragraph", "p1-0", "p1-2")];
    const result = advanceQuestion(blocks, "p1-0", 1);
    expect(result.current).toBe(0);
    expect(result.markId).toBeNull();
  });
});

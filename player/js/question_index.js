// F39 T-02 — question-index computation.
//
// Spec: N04/F39 DE-02. AC: F39-S02/AC-01.
// Bounded context: bc:reading_accommodation. Language: vanilla JS (ADR-023).
//
// Pure functions over the blocks[] array produced by F22 T-08
// (page.json: [{block_id, block_kind, first_mark_id, last_mark_id}]).

/**
 * Collect only question_stem blocks from the blocks array.
 *
 * @param {Array<{block_id:string, block_kind:string, first_mark_id:string|null, last_mark_id:string|null}>} blocks
 * @returns {Array}
 */
function _questionBlocks(blocks) {
  return blocks.filter((b) => b.block_kind === "question_stem");
}

/**
 * Return the 1-based question number that contains `markId`,
 * or 0 if the mark does not fall within any question_stem block.
 *
 * "Contains" is defined as: markId equals first_mark_id, last_mark_id,
 * or any mark that sorts between them by the block's prefix.
 * For simplicity we match by block ownership: a mark belongs to a block
 * when its id starts with the block's block_id prefix
 * (e.g. "q1-0" starts with "q1").
 *
 * @param {Array} questionBlocks - already filtered to question_stem
 * @param {string} markId
 * @returns {number} 1-based index, or 0
 */
function _currentQuestionNumber(questionBlocks, markId) {
  for (let i = 0; i < questionBlocks.length; i++) {
    const q = questionBlocks[i];
    if (markId.startsWith(q.block_id + "-") ||
        markId === q.first_mark_id ||
        markId === q.last_mark_id) {
      return i + 1;
    }
  }
  return 0;
}

/**
 * Compute the initial question index from a blocks array.
 * Returns {current: 1, total: N} where N is the number of
 * question_stem blocks and current is always 1 (first question).
 * Returns {current: 0, total: 0} when there are no question_stem blocks.
 *
 * @param {Array} blocks
 * @returns {{current: number, total: number}}
 */
export function questionIndexFromBlocks(blocks) {
  const qs = _questionBlocks(blocks);
  if (qs.length === 0) return { current: 0, total: 0 };
  return { current: 1, total: qs.length };
}

/**
 * Find the 1-based index of the question_stem block whose position in
 * `blocks` is nearest to `blockIdx` in the given direction.
 * Returns the question number (1-based) and its first_mark_id, or
 * a no-op result when already at the boundary.
 *
 * @param {Array} qs - filtered question blocks
 * @param {Array} blocks - full block list
 * @param {number} blockIdx - index in `blocks` of the current mark's block
 * @param {1|-1} direction
 * @returns {{current: number, markId: string|null}}
 */
function _nearestQuestion(qs, blocks, blockIdx, direction) {
  const candidate = direction > 0
    ? qs.find((q) => blocks.indexOf(q) > blockIdx)
    : [...qs].reverse().find((q) => blocks.indexOf(q) < blockIdx);
  if (!candidate) {
    return { current: direction > 0 ? qs.length : 1, markId: null };
  }
  return { current: qs.indexOf(candidate) + 1, markId: candidate.first_mark_id };
}

/**
 * Advance or reverse to the neighbouring question_stem block.
 *
 * `direction`: +1 to advance (J), -1 to reverse (K).
 *
 * Returns {current, markId} where:
 * - `current` is the 1-based question number after the jump
 * - `markId` is the first_mark_id of the target block (the seek target)
 * - `markId` is null on a no-op (already at first/last question)
 *
 * When `currentMarkId` is inside a non-question block, the jump is
 * computed relative to the surrounding question_stem blocks.
 *
 * @param {Array} blocks
 * @param {string} currentMarkId
 * @param {1|-1} direction
 * @returns {{current: number, markId: string|null}}
 */
export function advanceQuestion(blocks, currentMarkId, direction) {
  const qs = _questionBlocks(blocks);
  if (qs.length === 0) return { current: 0, markId: null };

  const currentQ = _currentQuestionNumber(qs, currentMarkId);
  if (currentQ === 0) {
    const blockIdx = blocks.findIndex((b) =>
      currentMarkId.startsWith(b.block_id + "-") ||
      currentMarkId === b.first_mark_id ||
      currentMarkId === b.last_mark_id
    );
    return _nearestQuestion(qs, blocks, blockIdx, direction);
  }

  const targetIdx = currentQ - 1 + direction;
  if (targetIdx < 0) return { current: 1, markId: null };
  if (targetIdx >= qs.length) return { current: qs.length, markId: null };
  return { current: targetIdx + 1, markId: qs[targetIdx].first_mark_id };
}

# N04 — Player UI

**Window:** weeks 11–13 (parallel with N03 from week 11) · **Features:** 6 · **Type:** ui

Accommodation-grade reader UX. Every interaction the public criticism of
the 2024 MoE pilot demanded — replay sentence, slow this word, jump to
question, word-sync highlight, font enlarge — is a feature here. WCAG 2.2
AA from day 1, not as a polish step.

## Features

- **F33-side-by-side-viewer** — original PDF page image + cleaned text
- **F34-per-block-controls** — distinct affordances for "read question only" / "read answers only"
- **F35-word-sync-highlight** — Web Audio API + word timings, no flashing animation
- **F36-accessibility-controls** — play/pause, speed (0.5×–1.5×), repeat sentence, next/prev block, font size, high-contrast
- **F37-spell-word** — long-press to spell a word letter-by-letter
- **F38-wcag-conformance** — keyboard, focus, contrast ≥ 4.5:1, `prefers-reduced-motion`, no autoplay
- **F39-pause-after-question** *(Phase 0 reading-accommodation)* — auto-pause at `question_stem` block end (default ON), `J`/`K` keyboard navigation between questions, "שאלה N מתוך M" progress hint; per ADR-041 row #5. Coexists with N05/F39-tirvi-bench-v0 per per-namespace numbering policy.

## Exit criteria

- Player TTI ≤ 2 s on a mid-range laptop
- Sentence-level cached-audio playback latency ≤ 300 ms
- Manual WCAG 2.2 AA checklist passes; axe-core CI gate green

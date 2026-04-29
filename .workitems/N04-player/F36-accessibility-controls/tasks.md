---
feature_id: N04/F36
status: ready
total_estimate_hours: 5.5
---

# Tasks: N04/F36 — Accessibility controls (4-button POC)

## T-01: Button DOM scaffold (4 buttons + ARIA)

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_button_scaffold.py
- dependencies: []
- hints: 4 `<button>` elements in tirvi/player/index.html with id, aria-label (he/en), aria-keyshortcuts; HTML lint passes; visual order Play | Pause | Continue | Reset

## T-02: Player state machine (pure function)

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-249, FT-250]
- bt_anchors: [BT-168]
- estimate: 1.5h
- test_file: tests/unit/test_player_state_machine.py
- dependencies: []
- hints: next_state(state, event); states = idle/playing/paused/ended; events = play/pause/continue/reset/audio_ended; invalid transitions return current state unchanged

## T-03: Button event handlers + audio side effects

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_button_handlers.py
- dependencies: [T-01, T-02]
- hints: Controls.bind(audio): each click -> dispatch event -> apply side effect (play/pause/currentTime=0); audio.addEventListener("ended", ...) feeds audio_ended

## T-04: Enable/disable per state

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_button_enable.py
- dependencies: [T-02, T-03]
- hints: idle -> Play enabled, others disabled; playing -> Pause enabled; paused -> Continue+Reset enabled; ended -> Play+Reset enabled; render after each transition

## T-05: Keyboard shortcuts (Space, R)

- design_element: DE-05
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-253]
- bt_anchors: [BT-169]
- estimate: 0.5h
- test_file: tests/unit/test_keyboard_shortcuts.py
- dependencies: [T-03]
- hints: Space -> if state in (idle,paused,ended) play; if playing pause; R -> always reset; preventDefault on focused player root

## T-06: ARIA labels + focus + WCAG contrast

- design_element: DE-06
- acceptance_criteria: [US-03/AC-01]
- ft_anchors: [FT-252]
- bt_anchors: [BT-171]
- estimate: 0.5h
- test_file: tests/unit/test_aria_focus.py
- dependencies: [T-01]
- hints: :focus-visible style always rendered; aria-labels in he+en (e.g., "Play / נגן"); palette tokens reuse F35's --highlight-bg/fg; contrast >= 4.5:1 measured via small contrast-ratio helper in test

## Dependency DAG

```
T-01 → T-03 → T-04
T-02 → T-03
T-02 → T-04
T-03 → T-05
T-01 → T-06
```

Critical path: T-02 → T-03 → T-04 (3.5h)

---
feature_id: N04/F35
status: ready
total_estimate_hours: 7.0
---

# Tasks: N04/F35 — Word-sync highlight (vanilla HTML POC)

## T-01: Static HTML scaffold

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_player_html.py
- dependencies: []
- hints: tirvi/player/index.html with `<img id="page">`, `<div class="marker">`, `<audio id="audio" src=...>`; minimal inline CSS; HTML lint check via Python parser

## T-02: Timings + page loader

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-244]
- estimate: 1h
- test_file: tests/unit/test_timings_loader.py
- dependencies: [T-01]
- hints: async load audio.json + page.json; jsdom-based test exercises the JS module without browser; cache in Player.state once

## T-03: requestAnimationFrame loop

- [x] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-248]
- estimate: 1.5h
- test_file: tests/unit/test_raf_loop.py
- dependencies: [T-02]
- hints: start on play, stop on pause; rAF callback reads audio.currentTime; one frame per animation tick; tests stub rAF + currentTime

## T-04: Active-word lookup (binary search)

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-244]
- bt_anchors: [BT-167]
- estimate: 1h
- test_file: tests/unit/test_lookup_word.py
- dependencies: [T-02]
- hints: lookupWord(timings, t_seconds) returns mark_id where timings[i].start_s <= t < timings[i].end_s; binary search; return null when t before first or after last

## T-05: Marker positioning + bbox scaling

- [ ] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-248]
- bt_anchors: [BT-167]
- estimate: 1.5h
- test_file: tests/unit/test_marker_position.py
- dependencies: [T-04]
- hints: positionMarker(bbox, image_natural, image_rendered): scale_x = rendered_w/natural_w; same for y; set CSS top/left/width/height; tests check pixel math for retina + non-retina

## T-06: prefers-reduced-motion + WCAG contrast

- [ ] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-246, FT-247]
- bt_anchors: [BT-165, BT-166]
- estimate: 1h
- test_file: tests/unit/test_a11y_player.py
- dependencies: [T-05]
- hints: query prefers-reduced-motion media; toggle `.no-animation` class; .marker palette uses --highlight-fg / --highlight-bg tokens with WCAG-compliant contrast; documented in README (deferred)

## Dependency DAG

```
T-01 → T-02 → T-03
              T-04
T-04 → T-05 → T-06
```

Critical path: T-01 → T-02 → T-04 → T-05 → T-06 (5.5h)

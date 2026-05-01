---
feature_id: N01/F08
status: ready
total_estimate_hours: 8.5
---

# Tasks: N01/F08 — Tesseract `heb` adapter

## T-01: PDF page rasterizer (300 dpi)

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-061]
- estimate: 1h
- test_file: tests/unit/test_pdf_rasterizer.py
- dependencies: []
- hints: pdf2image or pypdfium2; one PIL Image per page; 300 dpi default; raise on corrupt PDF

## T-02: Tesseract invoker with image_to_data

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-056, FT-057]
- bt_anchors: [BT-040, BT-041]
- estimate: 2h
- test_file: tests/unit/test_tesseract_adapter.py
- dependencies: [T-01]
- hints: pytesseract.image_to_data; psm 6, lang heb, tessdata_best path env-driven; per-word conf normalised to [0..1]

## T-03: RTL column reorder

- [x] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-057, FT-062]
- estimate: 2h
- test_file: tests/unit/test_rtl_column_reorder.py
- dependencies: [T-02]
- hints: cluster word x-centers via 1D k-means or histogram peaks; sort columns by max-x desc; within-column sort by y asc then x desc

## T-04: Inline lang_hint detector

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-058]
- estimate: 1h
- test_file: tests/unit/test_lang_hint.py
- dependencies: [T-02]
- hints: per-word codepoint-class scan; HE if any U+05D0..U+05EA, EN if all ASCII letters, else None

## T-05: Deskew preprocessor (≥ 5° threshold)

- [ ] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-059]
- bt_anchors: [BT-041]
- estimate: 1.5h
- test_file: tests/unit/test_deskew.py
- dependencies: [T-01]
- hints: cv2.HoughLinesP or numpy edge gradient median angle; rotate via PIL Image.rotate(expand=True); skip when |angle|<5 or env TIRVI_TESSERACT_DESKEW=off

## T-06: OCRResult assembly + adapter contract

- [ ] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-060]
- bt_anchors: [BT-042, BT-043]
- estimate: 1h
- test_file: tests/unit/test_tesseract_adapter.py
- dependencies: [T-02, T-03, T-04, T-05]
- hints: emit OCRResult(provider="tesseract", text=..., blocks=..., confidence=mean_word_conf or None); pass through assert_adapter_contract

## Dependency DAG

```
T-01 → T-02 → T-03
T-01 → T-05
T-02 → T-04
T-02, T-03, T-04, T-05 → T-06
```

Critical path: T-01 → T-02 → T-03 → T-06 (6h)

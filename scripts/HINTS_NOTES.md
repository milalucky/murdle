# Original book hints

The user requested the textual Hints sections, in addition to checking the selected answer categories. `data/volume1-hints.json` and `data/skulls-hints.json` are independent reviewed text catalogs so rebuilding the grids does not remove them.

- Volume 1: supplied PDF pages 327–338 (printed pages 321–332). Extracted with PyMuPDF layout ordering; corrected OCR list markers for 1, 2, 6, 9, 11, 12, 42, 48, 60 and 94. Joined continuations across pages for 7, 15, 23 and 86.
- Seven Skulls: supplied normalized scans 91–95. Apple Vision OCR; removed running headers, chapter labels and page numbers. Joined continuations for 4.2, 5.3 and 6.4. Hints 8.6–8.8 were visually checked against scan 95 and OCR word damage corrected. Extraction stops before SOLUTIONS on that spread.
- Each entry records its source PDF page(s). Original English prose is displayed only on request, with an explicit book-hint heading. The separate category-check button is labelled accordingly.
- Tests require one hint per case, complete cross-page continuations and no accidental solution-section inclusion.

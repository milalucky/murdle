# Original case endings

The two `data/*-endings.json` catalogs contain the English narrative solutions requested by the user, separate from the deduction grids and hints. They are loaded only after the reader requests an unlocked ending. They are not part of backup state.

- Volume 1: supplied PDF pages 339–384, 100 numbered entries. Extracted narrative text up to each answer table, joined cross-page continuations, corrected OCR and checked damaged passages against rendered pages. Case 25 retains the original encoded message, not a decoded replacement.
- Seven Skulls: normalized supplied scans 95 and 121–141, 64 printed IDs (1.1–8.8). OCR lines were ordered per page half using their vertical centers to compensate for perspective distortion. Running headers, page numbers and assignment tables were removed. Damaged passages and reading-order errors were corrected against the scans.
- One word in Seven Skulls 1.5 is covered by a finger. It is explicitly marked `[word obscured in scan]`, with a transcription note, rather than invented.
- Each entry retains source page numbers. Paragraph breaks are normalized for screen reading. Whole scans and PDFs are not published.
- The catalogs are independent of grid extraction scripts; rebuilding icon or assignment data does not overwrite these transcriptions.

## Visibility

An ending is available after a checked correct answer or during an explicitly revealed solution. Finishing without checking does not unlock it. Changing an answer removes the ending control until the answer is checked again. The load handler ignores stale responses after a dialog is closed or replaced, or the case changes. A failed request offers retry without changing the notebook.

## Validation

Tests cover one entry per case, source metadata, exclusion of table text and representative cross-page endings. Browser QA covers success, reveal, spoilers remaining hidden for unsolved cases, returning to an already solved case, mobile reading, next-case navigation and marks preserved after reading.

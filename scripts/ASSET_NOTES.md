# Volume 1 assets

The supplied PDF is a scan with an imperfect OCR layer. The published assets include only option icons, concise option labels, case headings, and numeric answer keys. The complete PDF, puzzle prose, clues, solution narrative, and full page images are not included.

- `data/volume1.json`: 100 cases. Cases 1–50 have three items in each of three categories. Cases 51–100 have four items in each of four categories.
- `assets/icons/`: 1,250 small transparent PNG icon crops (approximately 1.3 MB total). The original printed symbols are retained. Grayscale scan backgrounds are removed using a local threshold. Hair which is gray in the book remains gray.
- Category order: suspects, weapons, locations, motives (when present).
- Option order: left-to-right in the printed grid; for source option cards arranged in 2×2 panels, this means row-major order.
- `solution`: zero-based option indices for the final who/what/where/why answer, **not** a full solution of every deduction cell.
- `sourcePages`: one-based PDF page numbers, not printed page numbers.
- `verification: "verified"`: all 100 final answer sentences were visually checked against the printed Solutions section and mapped to the corresponding options. The 1,250 output icons were reviewed together on contact sheets. All resource paths and index bounds were checked programmatically.

## OCR corrections

The generator includes corrections for dropped or misread names, panel captions and headings. In particular, the OCR layer calls the solution to case 38 “28”, and reads the heading for case 44 with a comma. Neither error is carried into the answer keys. Cases with missing OCR captions were inspected as images. Final answer indices are kept as explicitly reviewed constants so future OCR differences cannot silently change correctness.

The short captions are normalized for use in the app; capitalization and punctuation may differ from the printed text. Several repeated symbols vary slightly in contrast or alignment because the input is a scan.

## Regeneration

Requires Python 3 and PyMuPDF (`pip install pymupdf`). Run from any working directory:

```sh
python scripts/extract_book.py '/absolute/path/to/the/supplied/book.pdf'
```

To rebuild JSON and validate existing image paths without regenerating the PNGs:

```sh
python scripts/extract_book.py '/absolute/path/to/the/supplied/book.pdf' --skip-icons
```

This script is specific to the supplied 392-page edition. A different scan needs a fresh page/layout audit. Its final validation requires 100 cases, 1,250 existing icon references, nonempty labels, and a complete in-range answer key for every case.

## Full deduction grids

`assignments` now stores all associations for each case, one object per suspect, with zero-based indices for every category. The UI can therefore render all six or three pair grids without deriving unknown associations from the murderer's final answer alone. `assignmentsVerification: "reviewed"` refers to this additional data.

All 100 tables were compared with their extracted source rows. Ambiguous OCR rows and merged/missing rows were inspected directly in the PDF. Manual corrections to the draft were needed for cases 2, 7, 15, 30, 56, 64, 79, 91 and 99. Case 64's first three rows were absent from the OCR layer and were read from the bottom of PDF page 363. Cases 25 and several noisy but unambiguous rows were also inspected or cross-checked against the remaining unique category values. Equivalent shortened names in the book's solutions are matched to their original choice icons.

The reviewed numeric mappings are persisted in `scripts/assignments-reviewed.json`; `extract_book.py` includes them during regeneration. Validation requires each category to be a permutation of 0..size−1 and the final murder answer to equal one complete assignment. Narrative solution text and page renders remain outside the project.

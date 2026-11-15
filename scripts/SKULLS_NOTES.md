# Seven Skulls extraction audit

The supplied PDF contains 141 photographed pages/spreads, including duplicates, out-of-order pages, five clockwise rotations and one counterclockwise rotation. The catalog contains 64 cases, numbered 1.1–8.8. Internal storage keys remain `skulls:1`–`skulls:64`.

Only case titles, choice labels, icon contours and numeric solution matrices are included. Full scans, clues, story text and the original PDF are not published.

## Reproduction

- Normalize scanned pages into PNG files and run Apple Vision OCR, retaining text boxes in top-left pixel coordinates.
- `scripts/skulls-reviewed.json` is the reviewed source for the catalog. It records input and solution page numbers, labels in **grid order**, assignments and final answers.
- Run `python3 scripts/extract_skulls.py` to generate `data/skulls.json`.
- `scripts/extract_skulls_icons.py` takes the normalized images, OCR boxes and a layout manifest via CLI arguments. It detects grid geometry, compensates for page curvature, isolates printed connected components, removes paper/noise and traces them as transparent SVG paths. Python dependencies: OpenCV and NumPy.
- The icon extractor writes a separate audit directory of raw glyph crops, final masks and annotated pages; these private intermediate images are not part of the website. Two reviewed coordinate corrections handle the photographed grid in 1.4 and the pigeon in 6.3. The dotted disappearing-person glyph in 7.1 uses a bounded crop because its components are deliberately disconnected.

## Review decisions

- Grid dimensions and category counts are independent: e.g. 1.8 has three choices and four categories, while 8.2 has four choices and three categories.
- Cards and grid do not always have the same order. Weapon indices were remapped for 3.5, 3.6, 3.7, 3.8 and 7.2. Assignments and answers were remapped together.
- Some fourth-category description pages are absent from the supplied scan (2.8, 3.8, 5.4–7.8, 8.5–8.8). Their labels come from the solution tables; positions were matched to the visible grid glyphs. This part is a semantic reconstruction, not a direct transcription of the missing cards. Letter glyphs explicitly resolve the words in 7.7 (F/S/B/K) and 8.7 (F/G/M/P).
- 5.8: Ferris wheel = amusement park opening, eye = mirage, blood drops = ancient sacrifice, money = tax write-off.
- Special categories retain the book's names, including Explanations, Armies, Skull spots, Heights, College degree and Magick words. The fourth question is “And?” where printed, rather than always “Why?”.
- 1.8's printed table names “the big stage”, absent from its available locations. The narrative final answer and listed choice identify “the administration trailer”; the dataset records this correction.
- 2.1 uses the card label “A Newspaper”; the solution describes a crowbar inside it. 6.6 uses the visible card label “A Murder-Themed Card Game”; the solution calls it a board game.

## Save compatibility

Existing manual templates with marks, answers or labels remain in manual mode. Opening the official book grid archives the complete old record in `legacyTemplate`; the old template can still be opened and edited. Notes and words remain available. Official and manual records are distinguished when comparing shared answers. Backups validate both versions and preserve the archive.

## Validation

Unit tests cover 64 printed IDs, icon existence, category sizes, solution bijections, final-answer membership, sensitive order corrections and archive backup validation. Browser QA exercised all 64 cases at 393 px (answer check and reveal), overflow checks at 375/393 px, hints and preservation of marks. These are browser viewport checks, not a physical iPhone/Safari device certification.

# Browser verification

Checked locally with Chromium mobile viewport emulation. This is not a physical iPhone/Safari test.

Portrait viewports: 375×812, 390×844, 393×852, 402×874, 430×932, 440×956.

- Full small and large fields fit their panels and the page width. No horizontal scrolling in the field or page. Tested cases 1, 51 and 100, vocabulary and case library at every listed viewport.
- 27 cells for the small grid, 96 for the large grid. Large solution view has 24 checks and 72 crosses; small has 9 checks and 18 crosses.
- Cell cycle, undo, keyboard direction handling and independent profile/case state.
- Wrong final answers rejected, correct answers accepted, incomplete answers reported. Optional category hint identifies only the incorrect categories.
- Solution display confirms spoiler intent, fills the entire grid, highlights final choices, and never modifies stored user marks or answers. Return to own grid restores the original view.
- Manual vocabulary, learned status, editing, filtering, and Quizlet TSV. No automatic translation button, code or service calls remain.
- Backup JSON contains profiles, cases and vocabulary. Invalid imports preserve state. Valid restoration requires confirmation. Result comparison does not overwrite saved data.
- Storage quota failure produces a persistent warning and recovers when storage becomes available.
- Custom second-book grid, 4 categories × 4 options, including long user labels, fits a 393 px viewport without overflow.
- Browser console: no errors or warnings in the final interaction pass.

Automated tests: `npm test` (9 tests). Static packaging: `npm run build`.

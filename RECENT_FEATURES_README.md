# Recently implemented features

**How this list was built:** Cursor **agent transcripts** under your project are mostly very large JSONL dumps and don’t reliably expose exact calendar dates per feature. This file combines **(1)** what’s present in the **repo today**, **(2)** **`feature.md`** phase items that clearly match shipped UI/APIs, and **(3)** the **recent chat thread** where builds like gap drill, readiness lite, weekly focus, and `/cheatsheet` were completed. **Adjust the “Yesterday / Today” headings** to match your real calendar if these two buckets don’t line up with when you merged or deployed.

Format: **short description** — **feature name**

---

## Yesterday (earlier session / batch)

- **Prerequisite-knowledge drill playlist from tier labels, with API and return-to-question flow.** **Gap drill** — `POST /api/v1/practice/gap-drill`, `GapDrillRequest` / `GapDrillResponse`, `GapDetectorCard` on question detail, playlist wiring in `MainContent`, optional highlight after wrong answers.
- **Additive readiness headline, target band from planner, gap and days-to-target from pace (no readiness × predicted score).** **Exam readiness lite** — `backend/app/domains/questions/readiness_lite.py`, extra `DashboardStats` fields, `target_band` on `GET /dashboard/stats`, Dashboard “Readiness lite” card + legacy line.
- **Prioritized weekly actions from bookmarks, mistakes, revision queue, slow topics, optional mock.** **Smart weekly focus plan** — `frontend/src/utils/weeklyFocusPlan.js`, `frontend/src/components/WeeklyFocusPlanCard.jsx`, placed above Study planner on the Dashboard.
- **Aligns with `feature.md` Phase 3 #7 (time vs target).** **Time insights on Dashboard** — per-topic average `time_taken_seconds` vs user “target sec/Q”, slow-topic highlighting (already part of the Dashboard analytics UI).

---

## Today (latest session / batch)

- **Merged printable sheet from bookmarks, remediation, revision queue, and optional subject/topic search; grouped; browser print → PDF.** **Formula cheat sheet (`/cheatsheet`)** — `frontend/src/components/CheatSheetPage.jsx`, `frontend/src/utils/formulaBlocks.js`, chunked `api.getQuestionsByIds` in `frontend/src/utils/api.js`, print CSS + `cheatsheet-print-mode`, Sidebar + Dashboard entry, `MainContent` URL/history sync for `/cheatsheet`.
- **Single-question print modal shares parsing with the cheat sheet.** **Formula sheet print** — `frontend/src/components/FormulaSheetPrint.jsx` refactored to use `extractFormulaBlocksFromTier1` (fits **`feature.md` Phase 6 #12** per-question path).

---

## `feature.md` cross-check (not necessarily “yesterday/today” in git)

| `feature.md` | Status in codebase (high level) |
|----------------|-----------------------------------|
| Phase 3 #7 Time insight strip | Present on Dashboard (timing vs target). |
| Phase 3 #8 Readiness lite | Shipped as **mean + gap + days** variant (see above); doc still describes product formula — update `feature.md` when you want docs to match. |
| Phase 4 #9 Wrong-answer queue | **Remediation playlist**, mistake **museum** / dashboard flows — related; dedicated `review-queue` view may still be backlog. |
| Phase 6 #12 Printable formula sheet | **Cheat sheet route** + **per-question** print modal. |
| Phase 7 #13 Smart Planner entry | **SmartPlannerStub** + sidebar/dashboard planner controls (full scheduler still out of scope per doc). |

---

## Repo / process hygiene (ongoing)

- **AST code graph refresh after substantive code edits** — `graphify update .` (workspace rule).

---

## Where to try it

| Feature | Where |
|--------|--------|
| Gap drill | **Question detail** (gap card); launches **playlist practice** |
| Readiness lite | Logged-in **Dashboard** |
| Weekly focus | **Dashboard** (card above Study planner) |
| Time insights | **Dashboard** (“Time insights” card) |
| Cheat sheet | **Sidebar → Cheat sheet**, **Dashboard → Formula cheat sheet**, or **`/cheatsheet`** |
| Per-question formulas | **Question detail** → formula print (modal) |

---

## Note on git history

Recent **commits** in `git log` may not list every item above if work lived only on a branch or wasn’t committed yet; this README is **behavior-centric** (what the app does now), not **commit-centric**.

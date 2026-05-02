# Feature backlog — implementation order (easy → harder)

This file merges **quick analytics wins** and the **Deep Dive Viewer v2** UI initiative. Order reflects **typical** engineering effort in Aerogate’s stack: reuse existing question JSON, attempts API, and dashboard patterns first; new persistence and print/PDF last.

**Legend (rough effort):** S = small (hours–1 day), M = medium (2–4 days), L = larger (about a week+).

---

## Where features live (website map)

The frontend is a **single-page app** driven by `MainContent` **view** state (not every screen has its own URL path yet). Use this table when placing UI.

| User-facing area | Code / view (`MainContent`) | When user sees it |
|------------------|----------------------------|-------------------|
| **Landing** | `view === 'landing'` | First visit / logo click |
| **Dashboard** (logged-in home) | `view === 'home'` → `Dashboard` | Sidebar **Dashboard** |
| **Home search** (guest) | `view === 'home'` (no user) | Search hub before login |
| **Search results** | `view === 'results'` | After search / filters |
| **Question detail** (“deep dive” question page) | `view === 'question-detail'` → `QuestionDetail` | Click a question from results or lists |
| **Practice by year** | `year_select` → `years` | Sidebar **Practice by Year** |
| **Browse by syllabus** | `syllabus-subjects` → `syllabus-topics` | Sidebar **Browse by Syllabus** |
| **Playlist / paper practice** | `playlist-practice` (+ `PaperAttemptView`) | Remediation playlist, mock paper flow |
| **Premium / Pro** | `view === 'premium'` → `PremiumPage` | Pro upsell, tier content |
| **Global chrome** | `Header`, `Sidebar` | All main views except full-screen flows |

**Deep Dive Viewer v2** layout maps mainly to **Question detail** (and secondarily **Premium** where tier panels already exist).

---

## Phase 1 — Display & layout only (S)

Build these when the data already exists on the question payload (e.g. `tier_1` / `tier_2` / analytics fields). No new tables.

1. **Question header metadata** — Show human-readable id, internal id, and any “DP” or legacy ids in `QuestionDetail`. *(S)*  
   **Surfaces:** **Question detail** (`question-detail`). Optional compact repeat on **Playlist / paper practice** if you show the same deep-dive panel there.

2. **Tier 1: Pitfall & exam strategy blocks** — Cards for: pitfall tags (type, frequency, severity), per-pitfall “what goes wrong / how to avoid / consequence”, exam priority, time budget, triage tip, guessing heuristic. Pure layout mapping from JSON. *(S–M depending on schema shape)*  
   **Surfaces:** **Question detail** (primary). Align with existing premium sections on **Premium** only if you keep marketing parity.

3. **Tier 2: Learning zone blocks** — Common mistakes & traps (severity + frequency + conceptual vs calculation tags), mnemonics with effectiveness + context, flashcard strip (flip UI), real-world context + “why it matters”. *(S–M)*  
   **Surfaces:** **Question detail** (same scroll / tabs as Tier 1). Flashcards can mirror **Revision / Tier** panels you already use on **Premium** for consistency.

4. **Theme polish** — Keep dark/light toggle consistent across Deep Dive shell and main app (reuse existing `useTheme` / Tailwind patterns). *(S)*  
   **Surfaces:** **Global** — **Header** (theme toggle), **Sidebar**, **Question detail**, **Dashboard**, **Results**, **Playlist practice**.

---

## Phase 2 — Navigation shell (S–M)

Mostly frontend routing + listing; may reuse existing year/subject/question APIs.

5. **Breadcrumbs** — `Year > Subject/stream > Qn` (or paper segment if you model it). *(S)*  
   **Surfaces:** **Question detail**, **Search results**, **Year flow**, **Syllabus flow** — anywhere `MainContent` already builds crumb arrays (extend that strip).

6. **Sidebar question navigator** — List Q1…Qn for selected paper/year; highlight active question; keyboard-friendly jump. *(M — needs stable ordering and list endpoint or client-side filter)*  
   **Surfaces:** **Question detail** (left column like your mock) and/or **Playlist / paper practice** when a finite question list is active. Optional slim variant on **Results** if you open questions as a “paper”.

---

## Phase 3 — Analytics from existing attempts (no new tables) (M)

Uses `/attempt` records and dashboard aggregates you already store.

7. **Time insight strip** — Per-subject (or per-topic) avg `time_taken_seconds` vs configurable target; flag “slow” areas. Chart or compact strip on Dashboard / paper view. *(M)*  
   **Surfaces:** **Dashboard** (hero or analytics section). Optional secondary strip on **Playlist / paper practice** summary after a session.

8. **Readiness lite (honest)** — Single score from **accuracy × syllabus coverage** (topics touched / total); show formula in UI so it stays trustworthy. No rank prediction. *(M)*  
   **Surfaces:** **Dashboard** (top card). Optional one-line on **Landing** for logged-in users only (keep guest landing clean).

---

## Phase 4 — One-screen queues & drills (reuse APIs) (M)

9. **Wrong-answer review queue** — Screen: last N incorrect attempts + link back to question + optional “redo weakest topic” using aggregates. *(M)*  
   **Surfaces:** **Dashboard** section or new view `review-queue` (still rendered inside `MainContent`). Entry point: Sidebar or button from **Dashboard**.

10. **One-tap trap drill** — Button: “N trap questions from weak topics” calling existing trap/search + practice/mock plumbing (`/practice`, trap filters). Guard with same Pro rules as today. *(M)*  
    **Surfaces:** **Dashboard** (primary CTA). Optional duplicate on **Search results** (trap chips row) for Pro users.

---

## Phase 5 — New persistence (M–L)

11. **Bookmarks + short notes (server-backed)** — Table `user_id`, `question_id`, `note`, `updated_at` (+ optional bookmark flag); CRUD API; wire `QuestionDetail` / list views. Big UX win; needs migration + auth. *(M–L)*  
    **Surfaces:** **Question detail** (bookmark + note editor). **Dashboard** “Saved” widget / list. Optional **Sidebar** link “Saved questions”.

---

## Phase 6 — Export / print (M–L)

12. **Printable formula sheet** — Single route or modal: render `formulas_principles` (or equivalent field) in a print stylesheet; optional “Save as PDF” via browser print. No LLM. *(M–L if PDF generation beyond print CSS)*  
    **Surfaces:** New view e.g. `formulas-print` **or** modal launched from **Question detail** / **Premium** / **Dashboard** (“Formula sheet” tool). Print CSS = browser **Print** dialog (no extra page strictly required).

---

## Phase 7 — Placeholder / future integration (S stub → later product)

13. **Smart Planner nav entry** — Link to Dashboard or a stub page (“Coming soon”) so IA matches Deep Dive shell; replace with real planner when schedule logic exists. *(S stub; full planner is separate large feature)*  
    **Surfaces:** **Sidebar** (new item) → stub content or **Dashboard** anchor; avoid cluttering **Landing**.

---

## Initiative name (umbrella)

**Deep Dive Viewer v2** — Per-question strategy + pitfall + memory layer + navigation shell, backed by existing enriched question JSON.

---

## Suggested build sequence (two parallel tracks)

| Track A — Ship value fast | Track B — Deep Dive shell |
|---------------------------|---------------------------|
| Time insight strip | Header metadata + Tier 1 / Tier 2 layout |
| Readiness lite | Breadcrumbs + sidebar navigator |
| Wrong-answer queue | Theme polish |
| Trap drill button | Smart Planner stub link |

After Track A + B, add **bookmarks/notes** then **printable formulas**.

---

## Out of scope for this doc

Features that require large datasets, ML, or heavy infra: cohort recommendations, video/voice generation, full adaptive scheduling, peer matching, rank prediction.

---

## Appendix: Deep Dive JSON → UI (null / empty rules)

Maps question payload fields to UI blocks in **Question detail**. Source shapes follow `Tier1CoreResearch` / `Tier2StudentLearning` in `backend/app/schemas/analytics.py`.

| UI block | JSON path | Renders when |
|----------|-----------|--------------|
| Header ids | `question_id`, `id`, `year`, `question_number`, optional `tier_4_metadata_*` | Always show core ids; tier_4 extras only if keys exist |
| Exam triage strip | `tier_2_student_learning.exam_strategy` | Non-null object with any of priority / time_management / triage_tip / guessing_heuristic |
| Common mistakes grid | `tier_2_student_learning.common_mistakes[]` | Array length ≥ 1 |
| Mnemonics | `tier_2_student_learning.mnemonics_memory_aids[]` | Array length ≥ 1 |
| Flashcards | `tier_2_student_learning.flashcards[]` | Array length ≥ 1 |
| Real-world context | `tier_2_student_learning.real_world_context[]` | Array length ≥ 1 |
| Formula sheet print | `tier_1_core_research.formulas_principles` | Non-empty string or non-empty list (after normalize) |
| Tier tabs (TierViews) | `tier_0` … `tier_4` | Each tab gated by presence of matching tier object + Pro |

If parent `tier_2_student_learning` is **null**, all Tier 2 blocks above hide (no placeholders). Same for `tier_1_core_research` for formulas.

**Premium:** Inline Tier 2 sections + `RevisionPanel` + `TierViews` remain Pro-gated where existing code uses `isPremium`.

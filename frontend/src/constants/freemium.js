/**
 * Aerogate freemium rules (single source of truth for product copy + hint caps).
 *
 * - Full step-by-step solution + Tier 0–4 analytics: Pro / trial, or limited daily
 *   free unlock (see QuestionDetail / PaperAttemptView).
 * - Progressive hints (step_by_step): free users see up to FREE_HINT_STEPS_CAP steps
 *   per question; Pro sees all steps (see HintSteps.jsx).
 * - Dashboard topic heatmap: logged-in users (dashboard stats API).
 * - Practice weak topic (dashboard heatmap CTA): Pro / trial only (syllabus topic browse stays free).
 * - GET /search complexity_flags: optional Pro-only filter on the API (backend search.py); no UI in app.
 * - Exam triage strip: free users see a one-line preview; Pro sees full strategy block.
 * - Textbook/video references: Pro (blurred teaser for free).
 * - Adaptive mock papers: Pro (POST /practice/mock-paper).
 */
export const FREE_HINT_STEPS_CAP = 1;

/** When true, non-Pro only sees first-line triage preview (see ExamTriageStrip). */
export const EXAM_TRIAGE_FREE_PREVIEW = true;

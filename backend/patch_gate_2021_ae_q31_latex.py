"""
Fix LaTeX / formatting for GATE_2021_AE_Q31.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2021_AE_Q31"

NEW_QUESTION_TEXT = (
    "Which statements are true for f(x)=e^{-x}|cos x|, x>0?"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Which of the following statement(s) is/are true about
    $$f(x)=e^{-x}|\cos x|,\qquad x>0?$$
    """
).strip()

NEW_OPTIONS = {
    "A": r"Differentiable at $x=\frac{\pi}{2}$",
    "B": r"Differentiable at $x=\pi$",
    "C": r"Differentiable at $x=\frac{3\pi}{2}$",
    "D": r"Continuous at $x=2\pi$",
}

NEW_REASONING = dedent(
    r"""
    Consider
    $$f(x)=e^{-x}|\cos x|,\qquad x>0.$$
    The only possible non-differentiable points come from $|\cos x|$, i.e. where $\cos x=0$:
    $$x=\frac{\pi}{2},\frac{3\pi}{2},\dots$$

    Let $g(x)=e^{-x}\cos x$, so
    $$g'(x)=-e^{-x}(\cos x+\sin x).$$

    - At $x=\frac{\pi}{2}$:
      left branch $f=g$, right branch $f=-g$.
      Thus
      $$f'_-\!\left(\frac{\pi}{2}\right)=g'\!\left(\frac{\pi}{2}\right)=-e^{-\pi/2},\quad
      f'_+\!\left(\frac{\pi}{2}\right)=-g'\!\left(\frac{\pi}{2}\right)=e^{-\pi/2},$$
      not equal $\Rightarrow$ not differentiable (A false).

    - At $x=\pi$, $\cos\pi=-1\neq0$, so locally sign of $\cos x$ does not change and $f$ is smooth there.
      Hence differentiable at $x=\pi$ (B true).

    - At $x=\frac{3\pi}{2}$ similarly left/right derivatives are opposite:
      $$f'_-\!\left(\frac{3\pi}{2}\right)=-e^{-3\pi/2},\quad
      f'_+\!\left(\frac{3\pi}{2}\right)=e^{-3\pi/2},$$
      so not differentiable (C false).

    - Continuity: $e^{-x}$ and $|\cos x|$ are continuous for all $x$, so their product is continuous.
      Therefore continuous at $x=2\pi$ (D true).

    Correct statements: **B and D**.
    """
).strip()

NEW_STEPS = [
    r"Given $f(x)=e^{-x}|\cos x|$, identify critical points where $|\cos x|$ changes form: $\cos x=0$.",
    r"Critical points in options are $x=\frac{\pi}{2}$ and $x=\frac{3\pi}{2}$ for differentiability checks.",
    r"Define $g(x)=e^{-x}\cos x$ so $g'(x)=-e^{-x}(\cos x+\sin x)$.",
    r"At $x=\frac{\pi}{2}$, branches switch sign: LHD $=-e^{-\pi/2}$, RHD $=e^{-\pi/2}$, hence not differentiable.",
    r"At $x=\pi$, $\cos\pi\neq0$ so no cusp; function is differentiable there.",
    r"At $x=\frac{3\pi}{2}$, LHD and RHD are opposite, so not differentiable.",
    r"Product of continuous functions is continuous, so continuity at $x=2\pi$ holds.",
]

NEW_FORMULAS_USED = [
    r"$f(x)=e^{-x}|\cos x|$",
    r"$|u|=\begin{cases}u,&u\ge0\\-u,&u<0\end{cases}$",
    r"$(uv)'=u'v+uv'$",
    r"$f'(x_0^-),\,f'(x_0^+)$ comparison for differentiability",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Given function",
        "type": "equation",
        "formula": r"$f(x)=e^{-x}|\cos x|$",
        "conditions": r"$x>0$",
        "relevance": "Function under test.",
    },
    {
        "name": "Absolute-value piecewise rule",
        "type": "principle",
        "formula": r"$|u|=\begin{cases}u,&u\ge0\\-u,&u<0\end{cases}$",
        "conditions": "Check sign changes of argument.",
        "relevance": "Explains cusps at zeros of cos.",
    },
    {
        "name": "Differentiability criterion",
        "type": "principle",
        "formula": r"$f'(x_0)$ exists iff $f'_-(x_0)=f'_+(x_0)$",
        "conditions": "One-variable function.",
        "relevance": "Used at critical points.",
    },
]

NEW_HINTS = [
    r"Look first where $\cos x=0$; those are potential non-differentiable points.",
    r"Continuity is easier: both $e^{-x}$ and $|\cos x|$ are continuous.",
    r"At nonzero $\cos x$ points, absolute value behaves like a smooth sign-fixed branch.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "definition",
        "front": "What condition must hold for differentiability at x0?",
        "back": r"Left and right derivatives must both exist and be equal: $f'_-(x_0)=f'_+(x_0)$.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "concept_recall",
        "front": r"For $|g(x)|$, which points need special differentiability check?",
        "back": r"Points where $g(x)=0$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"Is $e^{-x}|\cos x|$ differentiable at $x=\pi$?",
        "back": r"Yes, because $\cos\pi=-1\neq0$, so no cusp there.",
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Diff implies Cont, not reverse",
        "concept": "Differentiable => continuous, but continuous need not be differentiable",
        "effectiveness": "high",
        "context": "Continuity vs differentiability MCQs",
    },
    {
        "mnemonic": "Zero of inside, check cusp outside",
        "concept": "For absolute value, inspect points where inside term is zero",
        "effectiveness": "high",
        "context": "Rapid screening of non-smooth points",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Assuming continuity implies differentiability.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Marks options A/C true incorrectly.",
        "how_to_avoid": "Always compute/check LHD and RHD at cusp candidates.",
        "why_students_make_it": "Overgeneralization from smooth examples.",
    },
    {
        "type": "Procedural",
        "mistake": "Checking derivative only from one side at sign-change points.",
        "severity": "High",
        "frequency": "common",
        "consequence": "False differentiability conclusion.",
        "how_to_avoid": "Evaluate both one-sided derivatives whenever branch changes.",
        "why_students_make_it": "Rushed exam workflow.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Mark zeros of $\cos x$ first. Check LHD/RHD only there; elsewhere branch is smooth.",
    "guessing_heuristic": "For |cos x|-type functions, continuity usually holds but differentiability can fail at zeros of cos.",
    "time_management": "2-3 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Requires distinction between continuity and differentiability.",
    "Needs careful one-sided derivative checks at branch-change points.",
]

NEW_ALT_METHODS = [
    {
        "name": "Graph-based cusp detection",
        "description": r"Sketch $|\cos x|$ and multiply by smooth envelope $e^{-x}$; cusps persist at zeros of $\cos x$.",
        "pros_cons": "Pros: fast intuition. Cons: still verify with derivatives for exam certainty.",
        "when_to_use": "Quick sanity check after algebra.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "B;D"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Conceptual Application"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Find zeros of $\cos x$ $\rightarrow$ test one-sided derivatives there $\rightarrow$ use continuity of product elsewhere"
    sbs["key_insights"] = [
        "Zeros of argument inside absolute value are critical for differentiability.",
        "Continuity can hold even when differentiability fails.",
    ]

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS
    return o


def patch_t2(t2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t2 or {})
    o["flashcards"] = NEW_FLASHCARDS
    o["mnemonics_memory_aids"] = NEW_MNEMONICS
    o["common_mistakes"] = NEW_COMMON_MISTAKES
    o["exam_strategy"] = NEW_EXAM_STRATEGY
    return o


def patch_t3(t3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t3 or {})
    o["alternative_methods"] = NEW_ALT_METHODS
    conn = o.get("connections_to_other_subjects")
    if isinstance(conn, dict):
        conn = deepcopy(conn)
        conn.pop("subject_name_1", None)
        conn.pop("subject_name_2", None)
        conn.pop("subject_name_3", None)
        o["connections_to_other_subjects"] = conn
    return o


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning "
                "FROM questions WHERE question_id=:q"
            ),
            {"q": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit("Question not found")

        t1 = patch_t1(row[0])
        t2 = patch_t2(row[1])
        t3 = patch_t3(row[2])

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=CAST(:opts AS jsonb), "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(t1),
                "t2": json.dumps(t2),
                "t3": json.dumps(t3),
                "u": datetime.utcnow(),
                "q": PUBLIC_ID,
            },
        )

    print("patched", PUBLIC_ID)


if __name__ == "__main__":
    asyncio.run(main())

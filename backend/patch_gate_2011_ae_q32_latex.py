"""
Fix LaTeX / formatting for GATE_2011_AE_Q32.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2011_AE_Q32"

NEW_QUESTION_TEXT = (
    "Consider the matrix [[2, a], [b, 2]], where a and b are real numbers. "
    "The two eigenvalues lambda1 and lambda2 are real and distinct (lambda1 != lambda2) when:"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Consider the matrix
    $$\mathbf{A}=\begin{bmatrix}2 & a\\ b & 2\end{bmatrix},\qquad a,b\in\mathbb{R}.$$
    The two eigenvalues $\lambda_1,\lambda_2$ of $\mathbf{A}$ are real and distinct
    ($\lambda_1\ne\lambda_2$) when:
    """
).strip()

NEW_OPTIONS = {
    "A": r"$a<0,\ b>0$",
    "B": r"$a>0,\ b<0$",
    "C": r"$a<0,\ b<0$",
    "D": r"$a=0,\ b=0$",
}

NEW_REASONING = dedent(
    r"""
    For
    $$\mathbf{A}=\begin{bmatrix}2 & a\\ b & 2\end{bmatrix},$$
    characteristic equation is
    $$\det(\mathbf{A}-\lambda\mathbf{I})=0
    \Rightarrow (2-\lambda)^2-ab=0.$$
    Hence
    $$\lambda_{1,2}=2\pm\sqrt{ab}.$$

    Real eigenvalues require
    $$ab\ge 0.$$
    Distinct eigenvalues require
    $$\sqrt{ab}\ne 0\Rightarrow ab\ne 0.$$
    So combined condition is
    $$ab>0.$$
    Thus $a$ and $b$ must have the same sign.

    From options, only
    $$a<0,\ b<0$$
    is listed. Therefore option **C** is correct.
    """
).strip()

NEW_STEPS = [
    r"Write characteristic equation: $\det(\mathbf{A}-\lambda\mathbf{I})=0$.",
    r"Compute determinant: $(2-\lambda)^2-ab=0$.",
    r"Solve to get $\lambda_{1,2}=2\pm\sqrt{ab}$.",
    r"Require reality: $ab\ge 0$.",
    r"Require distinctness: $ab\ne 0$.",
    r"Combine to $ab>0$, then pick option with same-sign $a,b$.",
]

NEW_FORMULAS_USED = [
    r"$\det(\mathbf{A}-\lambda\mathbf{I})=0$",
    r"$\lambda_{1,2}=2\pm\sqrt{ab}$",
    r"Real and distinct $\iff ab>0$",
    r"$D=B^2-4AC,\ D>0$ for distinct real roots",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Characteristic equation",
        "type": "equation",
        "formula": r"$\det(\mathbf{A}-\lambda\mathbf{I})=0$",
        "conditions": "Square matrix.",
        "relevance": "Primary tool to find eigenvalues.",
    },
    {
        "name": "Eigenvalues for this 2x2 form",
        "type": "equation",
        "formula": r"$\lambda_{1,2}=2\pm\sqrt{ab}$",
        "conditions": "From $(2-\lambda)^2-ab=0$.",
        "relevance": "Directly gives condition on a,b.",
    },
    {
        "name": "Real-distinct condition",
        "type": "principle",
        "formula": r"$ab>0$",
        "conditions": r"Need $\sqrt{ab}$ real and non-zero.",
        "relevance": "Final decision criterion.",
    },
]

NEW_HINTS = [
    r"Use eigenvalue formula, not option-by-option guesswork.",
    r"Separate 'real' from 'distinct': first $ab\ge0$, then exclude $ab=0$.",
    r"Same-sign product condition is the key.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "definition",
        "front": "What equation gives eigenvalues of a square matrix?",
        "back": r"$\det(\mathbf{A}-\lambda\mathbf{I})=0$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"For $\mathbf{A}=\begin{bmatrix}2 & a\\ b & 2\end{bmatrix}$, when are eigenvalues real and distinct?",
        "back": r"When $ab>0$.",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": "What discriminant condition corresponds to real and distinct roots?",
        "back": r"$D>0$ (not just $D\ge0$).",
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Real then distinct: >=0 then !=0",
        "concept": r"For $\sqrt{ab}$ in eigenvalues, require $ab\ge0$ then exclude $ab=0$.",
        "effectiveness": "high",
        "context": "Root-nature checks",
    },
    {
        "mnemonic": "Same sign, sharp split",
        "concept": r"$ab>0$ means same sign and distinct real pair.",
        "effectiveness": "high",
        "context": "Fast option elimination",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Using only $ab\ge0$ and forgetting distinctness.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Incorrectly allows repeated eigenvalues.",
        "how_to_avoid": r"Apply both conditions: real ($ab\ge0$) and distinct ($ab\ne0$).",
        "why_students_make_it": "Mixes up root-type criteria.",
    },
    {
        "type": "Algebra",
        "mistake": "Sign error while expanding characteristic equation.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Wrong condition on a,b.",
        "how_to_avoid": r"Keep $(2-\lambda)^2-ab=0$ in compact form before simplification.",
        "why_students_make_it": "Rushed expansion and regrouping.",
    },
    {
        "type": "Logic",
        "mistake": r"Interpreting $ab>0$ as only $a>0,b>0$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Misses both-negative case.",
        "how_to_avoid": "Remember product positive for both positive or both negative.",
        "why_students_make_it": "Partial sign-rule recall.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Derive $\lambda=2\pm\sqrt{ab}$ in one line, then impose real+distinct directly.",
    "guessing_heuristic": r"Reject options with $ab\le0$ immediately.",
    "time_management": "1-2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Short derivation if characteristic equation is set correctly.",
    "Primary trap is discriminant/strict-inequality confusion.",
]

NEW_ALT_METHODS = [
    {
        "name": "Discriminant route",
        "description": r"Write quadratic in $\lambda$ as $\lambda^2-4\lambda+(4-ab)=0$, then use $D>0$ to get $ab>0$.",
        "pros_cons": "Pros: familiar for many students. Cons: more algebra than direct square-root form.",
        "when_to_use": "When you prefer standard quadratic-root tests.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "C"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Conceptual Application"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Characteristic equation $\rightarrow$ eigenvalue form $\rightarrow$ real+distinct constraints"
    sbs["key_insights"] = [
        r"Eigenvalues reduce to $2\pm\sqrt{ab}$ immediately.",
        r"Real and distinct jointly force strict condition $ab>0$.",
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

"""
Fix LaTeX / formatting for GATE_2013_AE_Q56.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2013_AE_Q56"

NEW_QUESTION_TEXT = (
    "If 3 <= X <= 5 and 8 <= Y <= 11, then which of the following is true?"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    If
    $$3\le X\le 5,\qquad 8\le Y\le 11,$$
    then which of the following options is true?
    """
).strip()

NEW_OPTIONS = {
    "A": r"$\frac{3}{5}\le \frac{X}{Y}\le \frac{8}{5}$",
    "B": r"$\frac{3}{11}\le \frac{X}{Y}\le \frac{5}{8}$",
    "C": r"$\frac{3}{11}\le \frac{X}{Y}\le \frac{8}{5}$",
    "D": r"$\frac{3}{5}\le \frac{X}{Y}\le \frac{8}{11}$",
}

NEW_REASONING = dedent(
    r"""
    Given
    $$3\le X\le 5,\qquad 8\le Y\le 11,$$
    with $X,Y>0$.

    For positive independent variables:
    - minimum of $\frac{X}{Y}$ occurs at minimum numerator and maximum denominator,
    - maximum of $\frac{X}{Y}$ occurs at maximum numerator and minimum denominator.

    So
    $$\min\!\left(\frac{X}{Y}\right)=\frac{3}{11},\qquad
    \max\!\left(\frac{X}{Y}\right)=\frac{5}{8}.$$
    Hence
    $$\frac{3}{11}\le \frac{X}{Y}\le \frac{5}{8}.$$
    Therefore, option **B** is correct.
    """
).strip()

NEW_STEPS = [
    r"Read intervals: $X\in[3,5]$ and $Y\in[8,11]$, both positive.",
    r"Target expression is the ratio $\frac{X}{Y}$.",
    r"Minimum ratio uses smallest numerator and largest denominator: $\frac{3}{11}$.",
    r"Maximum ratio uses largest numerator and smallest denominator: $\frac{5}{8}$.",
    r"Since variables vary independently over closed intervals, endpoint values are attainable.",
    r"Final range: $\frac{3}{11}\le \frac{X}{Y}\le \frac{5}{8}$.",
]

NEW_FORMULAS_USED = [
    r"If $a\le X\le b$ and $c\le Y\le d$ with $X,Y>0$, then $\frac{a}{d}\le \frac{X}{Y}\le \frac{b}{c}$.",
    r"$\min\!\left(\frac{X}{Y}\right)=\frac{\min X}{\max Y}$",
    r"$\max\!\left(\frac{X}{Y}\right)=\frac{\max X}{\min Y}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Minimum of ratio",
        "type": "principle",
        "formula": r"$\min\!\left(\frac{X}{Y}\right)=\frac{\min X}{\max Y}$",
        "conditions": r"$X,Y>0$ and independent interval bounds.",
        "relevance": "Finds lower bound.",
    },
    {
        "name": "Maximum of ratio",
        "type": "principle",
        "formula": r"$\max\!\left(\frac{X}{Y}\right)=\frac{\max X}{\min Y}$",
        "conditions": r"$X,Y>0$ and independent interval bounds.",
        "relevance": "Finds upper bound.",
    },
]

NEW_HINTS = [
    r"Denominator effect: larger denominator makes ratio smaller.",
    r"For minimum ratio, use smallest $X$ and largest $Y$.",
    r"For maximum ratio, use largest $X$ and smallest $Y$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": r"If $a\le X\le b$, $c\le Y\le d$, and $X,Y>0$, what is $\min\!\left(\frac{X}{Y}\right)$?",
        "back": r"$\frac{a}{d}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"If $a\le X\le b$, $c\le Y\le d$, and $X,Y>0$, what is $\max\!\left(\frac{X}{Y}\right)$?",
        "back": r"$\frac{b}{c}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"For $3\le X\le 5$ and $8\le Y\le 11$, find range of $\frac{X}{Y}$.",
        "back": r"$\frac{3}{11}\le \frac{X}{Y}\le \frac{5}{8}$",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Small top + big bottom = smallest ratio",
        "concept": r"How to get $\min\!\left(\frac{X}{Y}\right)$ for positive bounds.",
        "effectiveness": "high",
        "context": "Fast inequality MCQ solving",
    },
    {
        "mnemonic": "Big top + small bottom = biggest ratio",
        "concept": r"How to get $\max\!\left(\frac{X}{Y}\right)$ for positive bounds.",
        "effectiveness": "high",
        "context": "Endpoint selection under pressure",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Using $\frac{\min X}{\min Y}$ for minimum ratio.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrong lower bound.",
        "how_to_avoid": r"Remember denominator inversion effect: use $\max Y$ for minimum ratio.",
        "why_students_make_it": "Ignores denominator behavior.",
    },
    {
        "type": "Inequality Handling",
        "mistake": r"Mishandling reciprocal logic when working with $Y$ bounds.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Reversed or incorrect interval.",
        "how_to_avoid": r"Process stepwise and keep positivity in mind.",
        "why_students_make_it": "Rushed compound-inequality manipulation.",
    },
    {
        "type": "Assumption Error",
        "mistake": "Treating X and Y as correlated without statement.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Non-extreme or wrong endpoints.",
        "how_to_avoid": "Assume independence unless relation is explicitly given.",
        "why_students_make_it": "Over-interprets wording.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Directly compute two endpoints: $\frac{3}{11}$ and $\frac{5}{8}$, then match option.",
    "guessing_heuristic": r"Only correct option should contain both $\frac{3}{11}$ and $\frac{5}{8}$ in that order.",
    "time_management": "60-90 seconds.",
}

NEW_DIFFICULTY_FACTORS = [
    "Simple endpoint substitution once positivity is recognized.",
    "Main trap is denominator intuition error for minimum ratio.",
]

NEW_ALT_METHODS = [
    {
        "name": "Monotonicity in two variables",
        "description": r"For $f(X,Y)=\frac{X}{Y}$ with $Y>0$, $f$ increases with $X$ and decreases with $Y$, so extrema occur at rectangle corners.",
        "pros_cons": "Pros: rigorous and general. Cons: slower than direct ratio rule for this question.",
        "when_to_use": "Useful in multivariable bound problems.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "B"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Identify positive intervals $\rightarrow$ compute min/max ratio endpoints $\rightarrow$ write bound"
    sbs["key_insights"] = [
        "Min ratio uses min numerator and max denominator.",
        "Max ratio uses max numerator and min denominator.",
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

"""
Fix LaTeX / formatting for GATE_2024_AE_Q31.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2024_AE_Q31"

NEW_QUESTION_TEXT = (
    "Using trapezoidal rule with one interval, approximate "
    "integral_1^2 dx/(1+x^2), rounded to 2 decimal places."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Using trapezoidal rule with one interval, the approximate value of
    $$\int_{1}^{2}\frac{dx}{1+x^2}$$
    is \_\_\_\_\_\_ (rounded to 2 decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Given
    $$I=\int_{1}^{2}\frac{dx}{1+x^2},\qquad f(x)=\frac{1}{1+x^2},\ a=1,\ b=2.$$
    For one-interval trapezoidal rule:
    $$I\approx \frac{h}{2}\,[f(a)+f(b)],\qquad h=b-a=1.$$

    Endpoint values:
    $$f(1)=\frac{1}{2}=0.5,\qquad f(2)=\frac{1}{5}=0.2.$$

    Therefore:
    $$I\approx \frac{1}{2}(0.5+0.2)=\frac{1}{2}(0.7)=0.35.$$
    Rounded to two decimals: **0.35**.
    """
).strip()

NEW_STEPS = [
    r"Identify $f(x)=\frac{1}{1+x^2}$ over $[1,2]$.",
    r"Use one-interval trapezoidal formula: $I\approx \frac{h}{2}(f(a)+f(b))$.",
    r"Compute step size: $h=2-1=1$.",
    r"Evaluate endpoints: $f(1)=0.5$, $f(2)=0.2$.",
    r"Substitute: $I\approx \frac{1}{2}(0.5+0.2)=0.35$.",
    r"Round to two decimal places: $0.35$.",
]

NEW_FORMULAS_USED = [
    r"$I\approx \frac{h}{2}(f(a)+f(b))$",
    r"$h=b-a$",
    r"$f(x)=\frac{1}{1+x^2}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Single-interval trapezoidal rule",
        "type": "equation",
        "formula": r"$I\approx \frac{h}{2}\,[f(a)+f(b)]$",
        "conditions": "One subinterval on [a,b].",
        "relevance": "Core approximation formula.",
    },
    {
        "name": "Step size",
        "type": "equation",
        "formula": r"$h=b-a$",
        "conditions": "Single or equal subinterval partition.",
        "relevance": "Required before substitution.",
    },
]

NEW_HINTS = [
    r"Only endpoint values are used for one trapezoid.",
    r"Do not forget the factor $\frac{1}{2}$ in trapezoidal rule.",
    r"Compute $f(2)$ carefully: $\frac{1}{1+4}=\frac{1}{5}=0.2$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "What is the one-interval trapezoidal rule formula?",
        "back": r"$I\approx \frac{h}{2}(f(a)+f(b))$, with $h=b-a$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"Approximate $\int_{1}^{2}\frac{dx}{1+x^2}$ with one trapezoid.",
        "back": r"$0.35$",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Common trap in trapezoidal rule?",
        "back": r"Forgetting division by 2, which doubles the answer.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Half step, sum ends",
        "concept": r"$I\approx \frac{h}{2}[f(a)+f(b)]$",
        "effectiveness": "high",
        "context": "Single-interval trapezoidal rule",
    },
    {
        "mnemonic": "Ends only for one trap",
        "concept": "One interval uses only endpoint function values.",
        "effectiveness": "high",
        "context": "Quick exam recall",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": r"Using $h(f(a)+f(b))$ instead of $\frac{h}{2}(f(a)+f(b))$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Answer becomes exactly double.",
        "how_to_avoid": "Write full formula before substitution.",
        "why_students_make_it": "Formula memory slip under time pressure.",
    },
    {
        "type": "Calculation",
        "mistake": r"Wrong endpoint evaluation, especially $f(2)$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Wrong final value after otherwise correct method.",
        "how_to_avoid": r"Evaluate denominator first: $1+2^2=5$.",
        "why_students_make_it": "Arithmetic haste.",
    },
    {
        "type": "Instructions",
        "mistake": "Ignoring requested 2-decimal rounding.",
        "severity": "Low",
        "frequency": "occasional",
        "consequence": "Numerical format may be marked incorrect in strict checks.",
        "how_to_avoid": "Round only at final step.",
        "why_students_make_it": "Focuses on method, misses final formatting instruction.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Direct substitution question: compute h, evaluate two endpoints, apply one formula.",
    "guessing_heuristic": "Expected value should lie between 0.2 and 0.5 and near their average.",
    "time_management": "Under 2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Direct one-formula substitution problem.",
    "Minor risk only from arithmetic or missing 1/2 factor.",
]

NEW_ALT_METHODS = [
    {
        "name": "Exact integration check",
        "description": r"Compute exact value $\arctan(2)-\arctan(1)$ and compare with trapezoidal approximation.",
        "pros_cons": "Pros: gives benchmark error insight. Cons: unnecessary for asked numerical-rule task.",
        "when_to_use": "For validation or error discussion.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "0.35"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Identify f,a,b $\rightarrow$ compute h and endpoints $\rightarrow$ apply trapezoidal formula"
    sbs["key_insights"] = [
        "One-interval trapezoidal rule depends only on endpoint values.",
        "Correct 1/2 factor is essential for final accuracy.",
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
                "opts": json.dumps(None),
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

"""
Fix LaTeX / formatting for GATE_2021_AE_Q38.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2021_AE_Q38"

NEW_QUESTION_TEXT = (
    "Evaluate integral_1^5 x^2 dx using four equal intervals by trapezoidal rule "
    "and Simpson's one-third rule. Find absolute difference, rounded to 2 decimals."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The definite integral
    $$\int_{1}^{5}x^2\,dx$$
    is evaluated using four equal intervals by two methods:
    trapezoidal rule and Simpson's one-third rule.
    The absolute value of the difference between the two calculations is
    \_\_\_\_\_\_\_ (rounded to two decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Given $f(x)=x^2$, interval $[1,5]$, and $n=4$ equal subintervals:
    $$h=\frac{5-1}{4}=1.$$
    Nodes: $x_0=1,x_1=2,x_2=3,x_3=4,x_4=5$ with
    $$f_0=1,\ f_1=4,\ f_2=9,\ f_3=16,\ f_4=25.$$

    Composite trapezoidal rule:
    $$I_T=\frac{h}{2}\left[f_0+2(f_1+f_2+f_3)+f_4\right]$$
    $$=\frac{1}{2}[1+2(4+9+16)+25]=\frac{1}{2}(84)=42.$$

    Composite Simpson's 1/3 rule:
    $$I_S=\frac{h}{3}\left[f_0+4f_1+2f_2+4f_3+f_4\right]$$
    $$=\frac{1}{3}[1+16+18+64+25]=\frac{124}{3}\approx 41.3333.$$

    Absolute difference:
    $$|I_T-I_S|=\left|42-\frac{124}{3}\right|=\frac{2}{3}\approx 0.6667.$$
    Rounded to two decimals:
    $$0.67.$$
    """
).strip()

NEW_STEPS = [
    r"Set $f(x)=x^2,\ a=1,\ b=5,\ n=4$.",
    r"Compute step size: $h=(b-a)/n=1$.",
    r"Evaluate nodes $x_i$ and values $f_i$: $1,4,9,16,25$.",
    r"Apply composite trapezoidal rule to get $I_T=42$.",
    r"Apply composite Simpson's 1/3 rule to get $I_S=124/3$.",
    r"Compute $|I_T-I_S|=2/3\approx 0.67$.",
]

NEW_FORMULAS_USED = [
    r"$h=\frac{b-a}{n}$",
    r"$I_T=\frac{h}{2}\left[f_0+2\sum_{i=1}^{n-1}f_i+f_n\right]$",
    r"$I_S=\frac{h}{3}\left[f_0+4\sum_{i=1,3,\dots}^{n-1}f_i+2\sum_{i=2,4,\dots}^{n-2}f_i+f_n\right]$",
    r"$\Delta=\left|I_T-I_S\right|$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Step size",
        "type": "equation",
        "formula": r"$h=\frac{b-a}{n}$",
        "conditions": "Equal interval partition.",
        "relevance": "Defines spacing of nodes.",
    },
    {
        "name": "Composite trapezoidal rule",
        "type": "equation",
        "formula": r"$I_T=\frac{h}{2}\left[f_0+2\sum_{i=1}^{n-1}f_i+f_n\right]$",
        "conditions": "Any n >= 1.",
        "relevance": "First required approximation.",
    },
    {
        "name": "Composite Simpson's 1/3 rule",
        "type": "equation",
        "formula": r"$I_S=\frac{h}{3}\left[f_0+4\sum_{i=1,3,\dots}^{n-1}f_i+2\sum_{i=2,4,\dots}^{n-2}f_i+f_n\right]$",
        "conditions": "n must be even.",
        "relevance": "Second required approximation.",
    },
]

NEW_HINTS = [
    r"Write coefficient patterns explicitly: trapezoidal $1,2,2,2,1$.",
    r"For Simpson's 1/3 with n=4, use $1,4,2,4,1$.",
    r"Take absolute difference only after both integrals are computed.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "What is composite trapezoidal rule?",
        "back": r"$I_T=\frac{h}{2}\left[f_0+2\sum_{i=1}^{n-1}f_i+f_n\right]$",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "formula_recall",
        "front": "What is composite Simpson's 1/3 rule condition?",
        "back": r"Requires even number of intervals $n$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"For $\int_{1}^{5}x^2dx$ with $n=4$, what is $|I_T-I_S|$?",
        "back": r"$\frac{2}{3}\approx 0.67$",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Trap: 1-2-2-...-2-1",
        "concept": "Composite trapezoidal coefficients.",
        "effectiveness": "high",
        "context": "Fast setup for endpoint/interior weights",
    },
    {
        "mnemonic": "Simpson: 1-4-2-4-...-2-4-1",
        "concept": "Composite Simpson's 1/3 coefficients for even n.",
        "effectiveness": "high",
        "context": "Avoid weight-order mistakes",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": "Mixing coefficient patterns between trapezoidal and Simpson rules.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Large numerical error in both approximations.",
        "how_to_avoid": "Write coefficient sequence before substituting values.",
        "why_students_make_it": "Pattern memory confusion.",
    },
    {
        "type": "Conceptual",
        "mistake": "Applying Simpson's 1/3 when n is odd.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Invalid formula usage.",
        "how_to_avoid": "Check n-even condition first.",
        "why_students_make_it": "Skips method conditions.",
    },
    {
        "type": "Calculation",
        "mistake": r"Using wrong step size formula for h.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "All terms scaled incorrectly.",
        "how_to_avoid": r"Always compute $h=(b-a)/n$ before anything else.",
        "why_students_make_it": "Rushed setup.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Build small xi-fi table first, then apply coefficient templates directly.",
    "guessing_heuristic": "For convex x^2, trapezoidal exceeds Simpson exact-like value, so difference is positive and moderate.",
    "time_management": "2-3 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Mostly formula substitution once xi and fi are listed.",
    "Main risk is coefficient-order arithmetic errors.",
]

NEW_ALT_METHODS = [
    {
        "name": "Exact-integral cross-check",
        "description": r"Compute exact $\int_{1}^{5}x^2dx=\frac{124}{3}$ and compare with trapezoidal result to get same difference.",
        "pros_cons": "Pros: quick validation. Cons: not always possible for arbitrary integrands.",
        "when_to_use": "When integrand is simple polynomial.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "0.67 (within range 0.66 to 0.68)"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Compute h and nodes $\rightarrow$ evaluate both rules $\rightarrow$ absolute difference and rounding"
    sbs["key_insights"] = [
        "For quadratic integrand, Simpson's 1/3 is exact here.",
        "Difference effectively captures trapezoidal discretization error.",
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

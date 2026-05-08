"""
Fix LaTeX / formatting for GATE_2020_AE_Q36.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2020_AE_Q36"

NEW_QUESTION_TEXT = (
    "If integral_0^1 (x^2-2x+1) dx is evaluated numerically using trapezoidal "
    "rule with four intervals, find the difference between numerical and analytical "
    "values, rounded to three decimals."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    If
    $$\int_{0}^{1}(x^2-2x+1)\,dx$$
    is evaluated numerically using trapezoidal rule with four intervals, then the
    difference between the numerically evaluated value and the analytical value is
    \_\_\_\_\_\_\_\_\_\_ (rounded to three decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Let
    $$f(x)=x^2-2x+1=(x-1)^2,\qquad a=0,\ b=1,\ n=4.$$
    Step size:
    $$h=\frac{b-a}{n}=\frac{1}{4}=0.25.$$

    Nodes:
    $$x_0=0,\ x_1=0.25,\ x_2=0.5,\ x_3=0.75,\ x_4=1.$$
    Function values:
    $$f_0=1,\ f_1=0.5625,\ f_2=0.25,\ f_3=0.0625,\ f_4=0.$$

    Composite trapezoidal value:
    $$I_T=\frac{h}{2}\left[f_0+2(f_1+f_2+f_3)+f_4\right]$$
    $$=\frac{0.25}{2}\left[1+2(0.5625+0.25+0.0625)+0\right]
    =0.125(2.75)=0.34375.$$

    Exact integral:
    $$I_{\text{exact}}=\int_0^1(x^2-2x+1)\,dx
    =\left[\frac{x^3}{3}-x^2+x\right]_0^1
    =\frac{1}{3}\approx 0.333333.$$

    Difference (numerical minus analytical):
    $$I_T-I_{\text{exact}}=0.34375-\frac{1}{3}=0.0104167.$$
    Rounded to three decimals:
    $$0.010.$$
    """
).strip()

NEW_STEPS = [
    r"Set $f(x)=x^2-2x+1$, interval $[0,1]$, and $n=4$.",
    r"Compute $h=(1-0)/4=0.25$ and nodes $x_i=0,0.25,0.5,0.75,1$.",
    r"Evaluate function values: $1,0.5625,0.25,0.0625,0$.",
    r"Apply composite trapezoidal rule to get $I_T=0.34375$.",
    r"Compute exact value $I_{\text{exact}}=\frac{1}{3}$.",
    r"Find difference $I_T-I_{\text{exact}}=0.0104167$.",
    r"Round to three decimals: $0.010$.",
]

NEW_FORMULAS_USED = [
    r"$h=\frac{b-a}{n}$",
    r"$I_T=\frac{h}{2}\left[f_0+2\sum_{i=1}^{n-1}f_i+f_n\right]$",
    r"$I_{\text{exact}}=\int_a^b f(x)\,dx$",
    r"$\Delta=I_T-I_{\text{exact}}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Composite trapezoidal rule",
        "type": "equation",
        "formula": r"$I_T=\frac{h}{2}\left[f_0+2\sum_{i=1}^{n-1}f_i+f_n\right]$",
        "conditions": r"Equal spacing, $h=\frac{b-a}{n}$.",
        "relevance": "Core numerical approximation used.",
    },
    {
        "name": "Fundamental theorem of calculus",
        "type": "principle",
        "formula": r"$\int_a^b f(x)\,dx=F(b)-F(a)$",
        "conditions": "f has antiderivative F on interval.",
        "relevance": "Used to compute analytical benchmark.",
    },
    {
        "name": "Difference definition",
        "type": "equation",
        "formula": r"$\Delta=I_T-I_{\text{exact}}$",
        "conditions": "As worded: numerical minus analytical.",
        "relevance": "Direct asked quantity.",
    },
]

NEW_HINTS = [
    r"With $n=4$, use 5 nodes in the composite trapezoidal formula.",
    r"Apply coefficient pattern $1,2,2,2,1$ to $f_0,\dots,f_4$.",
    r"Compute numerical and analytical values separately before subtracting.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "What is composite trapezoidal rule for n equal intervals?",
        "back": r"$I_T=\frac{h}{2}\left[f_0+2\sum_{i=1}^{n-1}f_i+f_n\right]$",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": r"For $f(x)=x^2-2x+1$ on $[0,1]$ with $n=4$, what is $I_T$?",
        "back": r"$0.34375$",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "application",
        "front": r"What is $I_T-I_{\text{exact}}$ rounded to 3 decimals?",
        "back": r"$0.010$",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Trap weights: 1-2-...-2-1",
        "concept": "Endpoint vs interior coefficients in composite trapezoidal rule.",
        "effectiveness": "high",
        "context": "Fast setup in exam calculations",
    },
    {
        "mnemonic": "h from span over slices",
        "concept": r"$h=(b-a)/n$",
        "effectiveness": "high",
        "context": "Avoid wrong step-size inversion",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Using single-interval trapezoidal rule instead of composite (n=4).",
        "severity": "High",
        "frequency": "common",
        "consequence": "Large wrong difference value.",
        "how_to_avoid": "Remember n intervals imply n+1 nodes.",
        "why_students_make_it": "Misreads interval count.",
    },
    {
        "type": "Calculation",
        "mistake": "Forgetting factor 2 on interior points.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Incorrect trapezoidal estimate.",
        "how_to_avoid": "Write coefficient pattern before substitution.",
        "why_students_make_it": "Rushed summation.",
    },
    {
        "type": "Instructions",
        "mistake": "Rounding too early or to wrong decimal places.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Final value outside accepted range.",
        "how_to_avoid": "Round only final difference to three decimals.",
        "why_students_make_it": "Premature truncation.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Build x-f table quickly, evaluate I_T, then subtract exact integral 1/3.",
    "guessing_heuristic": "For convex function on [0,1], trapezoidal is overestimate, so difference is small positive.",
    "time_management": "2-3 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Method is straightforward but coefficient discipline is required.",
    "Sign convention in 'difference' and final rounding can trap students.",
]

NEW_ALT_METHODS = [
    {
        "name": "Trapezoidal error formula check",
        "description": r"Use error estimate involving $f''(\xi)$ to validate magnitude/order of computed difference.",
        "pros_cons": "Pros: quick plausibility check. Cons: gives estimate, not exact computed difference.",
        "when_to_use": "When verifying numerical reasonableness.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "0.010"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Compute I_T $\rightarrow$ compute I_exact $\rightarrow$ difference and rounding"
    sbs["key_insights"] = [
        "Composite trapezoidal with n=4 requires 5 nodes and interior doubling.",
        "For this convex quadratic, numerical value is slightly above exact value.",
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

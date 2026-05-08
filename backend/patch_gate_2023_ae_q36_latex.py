"""
Fix LaTeX / formatting for GATE_2023_AE_Q36.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q36"

NEW_QUESTION_TEXT = (
    "Given y(x)=(x+3)(x-2) for -4<x<4, what is the x-value at which y has a minimum?"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Given the function
    $$y(x)=(x+3)(x-2),\qquad -4<x<4,$$
    what is the value of $x$ at which the function has a minimum?
    """
).strip()

NEW_OPTIONS = {
    "A": r"$-\frac{3}{2}$",
    "B": r"$-\frac{1}{2}$",
    "C": r"$\frac{1}{2}$",
    "D": r"$\frac{3}{2}$",
}

NEW_REASONING = dedent(
    r"""
    Expand:
    $$y(x)=x^2+x-6.$$
    Differentiate:
    $$y'(x)=2x+1.$$
    Set to zero:
    $$2x+1=0\Rightarrow x=-\frac{1}{2}.$$

    Second derivative:
    $$y''(x)=2>0,$$
    so this critical point is a minimum.
    Also, $-\frac{1}{2}\in(-4,4)$, so it is valid in the given domain.

    Therefore, the minimum occurs at
    $$x=-\frac{1}{2},$$
    i.e. option **B**.
    """
).strip()

NEW_STEPS = [
    r"Write $y(x)=(x+3)(x-2)=x^2+x-6$.",
    r"Compute first derivative: $y'(x)=2x+1$.",
    r"Find stationary point: $2x+1=0\Rightarrow x=-\frac{1}{2}$.",
    r"Compute second derivative: $y''(x)=2$.",
    r"Since $y''(x)>0$, stationary point is a minimum.",
    r"Check interval: $-\frac{1}{2}$ lies in $(-4,4)$.",
]

NEW_FORMULAS_USED = [
    r"$\frac{d}{dx}(x^n)=nx^{n-1}$",
    r"$y'(x)=0$ for critical points",
    r"$y''(x)>0\Rightarrow$ local minimum",
    r"$x_v=-\frac{b}{2a}$ (for ax^2+bx+c)",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Quadratic standard form",
        "type": "equation",
        "formula": r"$y=ax^2+bx+c,\ a\neq0$",
        "conditions": "Real coefficients.",
        "relevance": "Supports derivative and vertex methods.",
    },
    {
        "name": "Critical point condition",
        "type": "principle",
        "formula": r"$y'(x)=0$",
        "conditions": "Differentiable function.",
        "relevance": "Find candidate extremum location.",
    },
    {
        "name": "Second derivative minimum test",
        "type": "principle",
        "formula": r"$y''(x_0)>0\Rightarrow$ local minimum at $x_0$",
        "conditions": "Second derivative exists near $x_0$.",
        "relevance": "Classifies the critical point.",
    },
]

NEW_HINTS = [
    r"Expand first to avoid sign mistakes in derivative.",
    r"For quadratic, one stationary point equals vertex location.",
    r"Use second derivative sign or upward-opening parabola check.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"What is vertex x-coordinate of $ax^2+bx+c$?",
        "back": r"$x=-\frac{b}{2a}$",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"For $y=x^2+x-6$, where is minimum x?",
        "back": r"$x=-\frac{1}{2}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": "What does y''>0 at critical point imply?",
        "back": "Local minimum.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Minus b over two a",
        "concept": "Vertex x-location of quadratic",
        "effectiveness": "high",
        "context": "Fast MCQ solving",
    },
    {
        "mnemonic": "Smile parabola means minimum",
        "concept": "If a>0, parabola opens upward, so vertex is minimum",
        "effectiveness": "high",
        "context": "Graph intuition check",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Sign Error",
        "mistake": r"Solving $2x+1=0$ as $x=+\frac{1}{2}$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Selects wrong option.",
        "how_to_avoid": r"Isolate carefully: $2x=-1\Rightarrow x=-\frac{1}{2}$.",
        "why_students_make_it": "Rushed algebra step.",
    },
    {
        "type": "Calculation",
        "mistake": "Wrong expansion of (x+3)(x-2).",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Wrong derivative and wrong extremum.",
        "how_to_avoid": "Multiply term-by-term and recheck constant/sign terms.",
        "why_students_make_it": "Basic algebra slip.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Quick 2-marker: use derivative or vertex formula directly.",
    "guessing_heuristic": r"After expansion to $x^2+x-6$, vertex x is naturally near $-0.5$.",
    "time_management": "1-2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Straightforward quadratic minimization.",
    "Primary traps are sign/algebra slips.",
]

NEW_ALT_METHODS = [
    {
        "name": "Completing the square",
        "description": r"$x^2+x-6=\left(x+\frac{1}{2}\right)^2-\frac{25}{4}$, minimum when squared term is zero.",
        "pros_cons": "Pros: gives vertex and minimum value directly. Cons: slightly longer algebra.",
        "when_to_use": "When you want explicit minimum value too.",
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
    sbs["solution_path"] = r"Expand $\rightarrow$ differentiate $\rightarrow$ set $y'=0$ $\rightarrow$ confirm with $y''>0$"
    sbs["key_insights"] = [
        "Quadratic has single vertex, so single extremum location.",
        "Second derivative constant positive confirms minimum immediately.",
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

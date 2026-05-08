"""
Fix LaTeX / formatting for GATE_2019_AE_Q1.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q1"

NEW_QUESTION_TEXT = (
    "The maximum value of f(x)=x e^{-x}, where x is real, is:"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The maximum value of the function
    $$f(x)=x e^{-x},\qquad x\in\mathbb{R}$$
    is:
    """
).strip()

NEW_OPTIONS = {
    "A": r"$\frac{1}{e}$",
    "B": r"$\frac{2}{e^2}$",
    "C": r"$\frac{e^{-1/2}}{2}$",
    "D": r"$\infty$",
}

NEW_REASONING = dedent(
    r"""
    Given
    $$f(x)=xe^{-x}.$$
    Differentiate:
    $$f'(x)=e^{-x}-xe^{-x}=e^{-x}(1-x).$$
    Since $e^{-x}>0$ for all $x$, critical point is
    $$1-x=0\Rightarrow x=1.$$

    Second derivative:
    $$f''(x)=\frac{d}{dx}\left[e^{-x}(1-x)\right]=e^{-x}(x-2).$$
    At $x=1$:
    $$f''(1)=-e^{-1}<0,$$
    so $x=1$ gives a local maximum (also global here by end behavior).

    Maximum value:
    $$f(1)=1\cdot e^{-1}=\frac{1}{e}.$$
    Hence correct option is **A**.
    """
).strip()

NEW_STEPS = [
    r"Start with $f(x)=xe^{-x}$.",
    r"Use product rule: $f'(x)=e^{-x}(1-x)$.",
    r"Solve $f'(x)=0$: since $e^{-x}\neq0$, get $x=1$.",
    r"Compute second derivative: $f''(x)=e^{-x}(x-2)$.",
    r"Check at $x=1$: $f''(1)=-e^{-1}<0$, so maximum at $x=1$.",
    r"Evaluate: $f(1)=\frac{1}{e}$.",
]

NEW_FORMULAS_USED = [
    r"$f(x)=xe^{-x}$",
    r"$(uv)'=u'v+uv'$",
    r"$\frac{d}{dx}(e^{ax})=ae^{ax}$",
    r"$f'(x)=e^{-x}(1-x)$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Given function",
        "type": "equation",
        "formula": r"$f(x)=xe^{-x}$",
        "conditions": [r"$x\in\mathbb{R}$"],
        "relevance": "Function to optimize.",
    },
    {
        "name": "First derivative condition",
        "type": "principle",
        "formula": r"$f'(x)=0$ at interior extrema",
        "conditions": "Differentiable function.",
        "relevance": "Finds candidate maximizer.",
    },
    {
        "name": "Second derivative test",
        "type": "principle",
        "formula": r"$f''(x_0)<0\Rightarrow$ local maximum at $x_0$",
        "conditions": "Second derivative exists near critical point.",
        "relevance": "Classifies critical point.",
    },
]

NEW_HINTS = [
    r"Product of polynomial and exponential: apply product rule carefully.",
    r"$e^{-x}$ never becomes zero, so only $(1-x)$ decides critical point.",
    r"Use second derivative sign to confirm max/min.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"What is $\frac{d}{dx}(xe^{-x})$?",
        "back": r"$e^{-x}(1-x)$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": "How do you classify a critical point using second derivative?",
        "back": r"If $f''(x_0)<0$, it is a local maximum; if $f''(x_0)>0$, local minimum.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"For $f(x)=xe^{-x}$, what is the maximizing x and maximum value?",
        "back": r"$x=1,\ f_{\max}=\frac{1}{e}$",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Differentiate-Check-Evaluate",
        "concept": "Optimization workflow",
        "effectiveness": "high",
        "context": "Single-variable extrema MCQs",
    },
    {
        "mnemonic": "MAX means f'' negative",
        "concept": "Second derivative sign memory aid",
        "effectiveness": "high",
        "context": "Critical point classification",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": r"Differentiating $e^{-x}$ as $+e^{-x}$ instead of $-e^{-x}$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Wrong critical point and wrong answer.",
        "how_to_avoid": r"Use chain rule: $\frac{d}{dx}(e^{u})=e^{u}u'$ with $u=-x$.",
        "why_students_make_it": "Misses inner derivative sign.",
    },
    {
        "type": "Conceptual",
        "mistake": "Stopping at critical point without checking if it is maximum.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "May misclassify extrema.",
        "how_to_avoid": "Always apply first/second derivative test.",
        "why_students_make_it": "Procedural shortcut.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Standard one-variable optimization. Differentiate once, solve, classify, evaluate.",
    "guessing_heuristic": r"For $xe^{-x}$ type, max often occurs near $x=1$ and value near $1/e$.",
    "time_management": "Under 2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Direct derivative-based optimization.",
    "Minor sign trap in chain rule for exponential.",
]

NEW_ALT_METHODS = [
    {
        "name": "Log-derivative method",
        "description": r"For $x>0$, maximize $\ln f=\ln x-x$. Set derivative $1/x-1=0\Rightarrow x=1$.",
        "pros_cons": "Pros: compact algebra. Cons: needs positivity domain handling.",
        "when_to_use": "Useful for product/power forms in optimization.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "A"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Differentiate $\rightarrow$ solve $f'(x)=0$ $\rightarrow$ classify via $f''$ $\rightarrow$ evaluate $f$"
    sbs["key_insights"] = [
        "Exponential factor never vanishes, simplifying critical point search.",
        "Second derivative quickly confirms maximum at x=1.",
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

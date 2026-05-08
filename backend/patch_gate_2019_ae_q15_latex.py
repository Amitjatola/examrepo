"""
Fix LaTeX / formatting for GATE_2019_AE_Q15.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q15"

NEW_QUESTION_TEXT = (
    "Evaluate the limit and round to 2 decimal places: lim(theta->0) (theta - sin(theta))/theta^3."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The value of the following limit is $\underline{\qquad\qquad}$
    (round off to 2 decimal places):
    $$\lim_{\theta\to 0}\frac{\theta-\sin\theta}{\theta^3}.$$
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Use Maclaurin expansion:
    $$\sin\theta=\theta-\frac{\theta^3}{3!}+\frac{\theta^5}{5!}-\cdots.$$

    Then
    $$\theta-\sin\theta
    =\theta-\left(\theta-\frac{\theta^3}{6}+\frac{\theta^5}{120}-\cdots\right)
    =\frac{\theta^3}{6}-\frac{\theta^5}{120}+\cdots.$$

    Therefore
    $$\frac{\theta-\sin\theta}{\theta^3}
    =\frac{1}{6}-\frac{\theta^2}{120}+\cdots
    \xrightarrow[\theta\to 0]{}\frac{1}{6}.$$

    Numerically,
    $$\frac{1}{6}=0.1666\ldots\approx 0.17\quad(\text{to 2 decimals}).$$
    """
).strip()

NEW_STEPS = [
    r"Recognize $\frac{\theta-\sin\theta}{\theta^3}$ gives $0/0$ as $\theta\to0$.",
    r"Use Taylor/Maclaurin series for $\sin\theta$ about $\theta=0$.",
    r"Substitute $\sin\theta=\theta-\frac{\theta^3}{6}+\frac{\theta^5}{120}-\cdots$.",
    r"Simplify numerator: $\theta-\sin\theta=\frac{\theta^3}{6}-\frac{\theta^5}{120}+\cdots$.",
    r"Divide by $\theta^3$: $\frac{1}{6}-\frac{\theta^2}{120}+\cdots$.",
    r"Take limit $\theta\to0$ to get $\frac{1}{6}$.",
    r"Convert and round: $0.1666\ldots\to 0.17$.",
]

NEW_FORMULAS_USED = [
    r"$\sin\theta=\theta-\frac{\theta^3}{3!}+\frac{\theta^5}{5!}-\cdots$",
    r"$\lim_{\theta\to0}\frac{\theta-\sin\theta}{\theta^3}=\frac{1}{6}$",
    r"$\lim_{\theta\to0}\frac{\sin\theta}{\theta}=1$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Maclaurin series of sine",
        "type": "series expansion",
        "formula": r"$\sin\theta=\theta-\frac{\theta^3}{3!}+\frac{\theta^5}{5!}-\cdots$",
        "conditions": "Theta in radians.",
        "relevance": "Primary method to evaluate the limit quickly.",
    },
    {
        "name": "Standard limit result",
        "type": "limit",
        "formula": r"$\lim_{\theta\to0}\frac{\theta-\sin\theta}{\theta^3}=\frac{1}{6}$",
        "conditions": "Theta in radians.",
        "relevance": "Direct known result from expansion or repeated L'Hopital.",
    },
]

NEW_HINTS = [
    r"For trigonometric limits with derivatives/series, use radians.",
    r"Keep enough terms so leading cancellation is handled correctly.",
    r"After exact value, apply proper decimal rounding (not truncation).",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"State $\sin\theta$ expansion up to $\theta^5$ term.",
        "back": r"$\sin\theta=\theta-\frac{\theta^3}{6}+\frac{\theta^5}{120}-\cdots$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"What is $\lim_{\theta\to0}\frac{\theta-\sin\theta}{\theta^3}$?",
        "back": r"$\frac{1}{6}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": "What is 1/6 rounded to two decimals?",
        "back": "0.17",
        "difficulty": "easy",
        "time_limit_seconds": 10,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Sine: odd powers, alternating signs",
        "concept": "Pattern of sin Taylor series",
        "effectiveness": "high",
        "context": "Quick series recall",
    },
    {
        "mnemonic": "Cube-over-six error",
        "concept": r"Leading deviation in $\sin\theta\approx\theta$ is $\theta^3/6$",
        "effectiveness": "medium",
        "context": "Small-angle limit intuition",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Using degrees instead of radians.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrong limit value.",
        "how_to_avoid": "Always interpret calculus trig limits in radians unless stated otherwise.",
        "why_students_make_it": "Unit oversight in hurry.",
    },
    {
        "type": "Approximation",
        "mistake": "Truncating 0.1666... to 0.16 instead of rounding to 0.17.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Format/value mismatch in NAT.",
        "how_to_avoid": "Check third decimal before final rounding.",
        "why_students_make_it": "Uses truncation habit.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Recognize as a standard small-angle/Taylor limit; solve in under 1 minute if recalled.",
    "guessing_heuristic": "Common outcomes are simple fractions; here value is near 0.17.",
    "time_management": "1-2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Standard formula-based limit with light algebra.",
    "Main trap is unit (radian) and rounding precision.",
]

NEW_ALT_METHODS = [
    {
        "name": "Repeated L'Hopital method",
        "description": r"Apply L'Hopital three times: $\frac{\theta-\sin\theta}{\theta^3}\to\frac{1-\cos\theta}{3\theta^2}\to\frac{\sin\theta}{6\theta}\to\frac{\cos\theta}{6}\to\frac{1}{6}$.",
        "pros_cons": "Pros: systematic differentiation path. Cons: longer than series approach.",
        "when_to_use": "When series expansion is not remembered.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "0.17"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Recognize 0/0 $\rightarrow$ expand sin around 0 $\rightarrow$ simplify $\rightarrow$ limit and round"
    sbs["key_insights"] = [
        "Series method avoids repetitive differentiation.",
        "Correct rounding required for NAT final entry.",
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
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=:opts, "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": None,
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

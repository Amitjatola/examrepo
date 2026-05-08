"""
Fix LaTeX / formatting for GATE_2009_AE_Q05.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2009_AE_Q05"

NEW_QUESTION_TEXT = (
    "The ordinary differential equation d^2y/dx^2 + ky = 0, where k is real and positive:"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The ordinary differential equation
    $$\frac{d^2y}{dx^2}+ky=0,\qquad k>0,\ k\in\mathbb{R}$$
    """
).strip()

NEW_OPTIONS = {
    "A": "is non-linear",
    "B": "has a characteristic equation with one real and one complex root",
    "C": "has a characteristic equation with two real roots",
    "D": "has a complementary function that is simple harmonic",
}

NEW_REASONING = dedent(
    r"""
    Given
    $$\frac{d^2y}{dx^2}+ky=0,\qquad k>0.$$
    Assume $y=e^{mx}$, then characteristic equation:
    $$m^2+k=0.$$
    So
    $$m=\pm i\sqrt{k}.$$
    Roots are purely imaginary conjugates.

    For roots $m=\alpha\pm i\beta$, complementary function is
    $$y_c=e^{\alpha x}\left(C_1\cos\beta x+C_2\sin\beta x\right).$$
    Here $\alpha=0,\ \beta=\sqrt{k}$, hence
    $$y_c=C_1\cos\!\left(\sqrt{k}\,x\right)+C_2\sin\!\left(\sqrt{k}\,x\right).$$
    This is simple harmonic form.

    Therefore, option **D** is correct.
    """
).strip()

NEW_STEPS = [
    r"Identify it as a linear homogeneous second-order ODE with constant coefficients.",
    r"Assume trial solution $y=e^{mx}$ and form characteristic equation.",
    r"Get $m^2+k=0\Rightarrow m=\pm i\sqrt{k}$ for $k>0$.",
    r"Recognize roots are purely imaginary conjugates.",
    r"Write $y_c=e^{\alpha x}(C_1\cos\beta x+C_2\sin\beta x)$ with $\alpha=0,\beta=\sqrt{k}$.",
    r"Conclude $y_c=C_1\cos(\sqrt{k}x)+C_2\sin(\sqrt{k}x)$: simple harmonic.",
]

NEW_FORMULAS_USED = [
    r"$\frac{d^2y}{dx^2}+ky=0$",
    r"$m^2+k=0$",
    r"$m=\pm i\sqrt{k}$",
    r"$y_c=e^{\alpha x}\left(C_1\cos\beta x+C_2\sin\beta x\right)$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Second-order linear homogeneous ODE",
        "type": "equation",
        "formula": r"$\frac{d^2y}{dx^2}+ky=0$",
        "conditions": r"$k\in\mathbb{R},\ k>0$",
        "relevance": "Base equation under analysis.",
    },
    {
        "name": "Characteristic equation",
        "type": "equation",
        "formula": r"$m^2+k=0$",
        "conditions": "From substitution y=e^{mx}.",
        "relevance": "Determines root nature and solution form.",
    },
    {
        "name": "Imaginary roots for positive k",
        "type": "principle",
        "formula": r"$m=\pm i\sqrt{k}$",
        "conditions": r"$k>0$",
        "relevance": "Leads to sinusoidal complementary function.",
    },
    {
        "name": "Complementary function for complex roots",
        "type": "equation",
        "formula": r"$y_c=e^{\alpha x}\left(C_1\cos\beta x+C_2\sin\beta x\right)$",
        "conditions": r"$m=\alpha\pm i\beta$",
        "relevance": "Final solution form classification.",
    },
]

NEW_HINTS = [
    r"Use characteristic equation; do not integrate directly first.",
    r"For $k>0$, equation $m^2=-k$ gives imaginary roots.",
    r"Imaginary roots imply sine-cosine complementary function.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"For $\frac{d^2y}{dx^2}+ky=0$, what is the characteristic equation?",
        "back": r"$m^2+k=0$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"If roots are $\pm i\omega$, what is $y_c$ form?",
        "back": r"$y_c=C_1\cos(\omega x)+C_2\sin(\omega x)$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"For $k>0$ in $y''+ky=0$, what type of complementary function appears?",
        "back": "Simple harmonic (sinusoidal).",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Positive k, imaginary m, oscillatory y",
        "concept": r"In $y''+ky=0$, sign of $k$ controls root nature and solution type.",
        "effectiveness": "high",
        "context": "Quick ODE option elimination",
    },
    {
        "mnemonic": "Complex roots -> cosine-sine routes",
        "concept": "Complex conjugate roots give trigonometric complementary function.",
        "effectiveness": "high",
        "context": "Second-order linear ODE recall",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Treating equation as non-linear.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Eliminates correct method and option.",
        "how_to_avoid": "Check powers/products: y and derivatives appear linearly.",
        "why_students_make_it": "Confuses constant-coefficient ODE categories.",
    },
    {
        "type": "Sign Error",
        "mistake": r"From $m^2=-k$, writing $m=\pm\sqrt{k}$ instead of $m=\pm i\sqrt{k}$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrongly predicts real roots.",
        "how_to_avoid": r"Remember $\sqrt{-1}=i$.",
        "why_students_make_it": "Misses imaginary unit in square-root step.",
    },
    {
        "type": "Formula Recall",
        "mistake": "Using exponential-only form for imaginary roots.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Misses simple harmonic complementary function.",
        "how_to_avoid": r"Use standard complex-root template with $\cos$ and $\sin$.",
        "why_students_make_it": "Memorization gap in root-to-solution mapping.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Immediate pattern match: $y''+ky=0,\ k>0 \Rightarrow m=\pm i\sqrt{k}\Rightarrow$ sinusoidal $y_c$.",
    "guessing_heuristic": "If confused, select option mentioning simple harmonic complementary function.",
    "time_management": "45-75 seconds.",
}

NEW_DIFFICULTY_FACTORS = [
    "Fast concept check on characteristic roots.",
    "Main trap is sign handling in square root of negative quantity.",
]

NEW_ALT_METHODS = [
    {
        "name": "Energy-integral method",
        "description": r"Multiply by $2y'$: $\frac{d}{dx}\!\left((y')^2+ky^2\right)=0$, giving conserved quadratic form and oscillatory solution.",
        "pros_cons": "Pros: physical intuition. Cons: longer than characteristic-equation method.",
        "when_to_use": "When linking ODE to vibration/SHM physics.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "D"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Conceptual"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Form characteristic equation $\rightarrow$ identify imaginary roots $\rightarrow$ write trigonometric complementary function"
    sbs["key_insights"] = [
        r"$k>0$ gives purely imaginary roots for $m^2+k=0$.",
        "Imaginary conjugate roots map to simple harmonic complementary form.",
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

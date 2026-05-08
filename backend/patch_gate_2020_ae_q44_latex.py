"""
Fix GATE_2020_AE_Q44 (NAT, phugoid → U0): stem, tier_1/2/3 LaTeX.

- Stem: use $\\underline{\\hspace{...}}$ for NAT blank (avoid $\\text{\\_\_\_\_}$ raw TeX issues).
- Strip **markdown** from strings rendered via MathText (shows literal asterisks).
- Exam strategy / alternatives: wrap loose \\omega_n etc. in $...$.
- Correct mistaken phrase $\\sqrt{2g/U_0}$ → $\\sqrt{2}\\,g/U_0$ in common_mistakes.

Replaces separate tier2-only runs; use only this script.

Usage (from backend/):
  ./venv/bin/python patch_gate_2020_ae_q44_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2020_AE_Q44"

NEW_QUESTION_TEXT = (
    "The eigenvalues for phugoid mode of a general aviation airplane at a stable cruise flight condition at low "
    "angle of attack are λ1,2 = - 0.02 ± i 0.25. If the acceleration due to gravity is 9.8 m/s2, the equilibrium "
    "speed of the airplane is \\_\\_\\_\\_\\_\\_\\_\\_\\_\\_ m/s (round off to two decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    "The eigenvalues for phugoid mode of a general aviation airplane at a stable cruise flight condition at low "
    "angle of attack are $\\lambda_{1,2}=-0.02\\pm i\\,0.25$. If $g=9.8~\\mathrm{m/s^2}$, the equilibrium speed "
    "$U_0$ is $\\underline{\\hspace{3.5em}}~\\mathrm{m/s}$ (round off to two decimal places)."
)

NEW_REASONING = (
    "Given phugoid roots $\\lambda_{1,2}=-0.02\\pm i\\,0.25$, write $\\lambda=\\sigma\\pm i\\omega_d$ with "
    "$\\sigma=-0.02\\ \\mathrm{rad/s}$ and $\\omega_d=0.25\\ \\mathrm{rad/s}$. "
    "The undamped natural frequency is\n"
    "$$\\Omega_n=\\sqrt{\\sigma^2+\\omega_d^2}"
    "=\\sqrt{0.0004+0.0625}=\\sqrt{0.0629}\\approx 0.250798\\ \\mathrm{rad/s}.$$\n"
    "For nearly level cruise at small $\\alpha$, a standard phugoid approximation is\n"
    "$$\\Omega_n\\approx \\frac{\\sqrt{2}\\,g}{U_0}\\quad\\Rightarrow\\quad "
    "U_0=\\frac{\\sqrt{2}\\,g}{\\Omega_n}.$$\n"
    "With $g=9.8\\ \\mathrm{m/s^2}$,\n"
    "$$U_0\\approx \\frac{\\sqrt{2}\\times 9.8}{0.250798}"
    "\\approx \\frac{1.41421\\times 9.8}{0.250798}"
    "\\approx \\frac{13.8593}{0.250798}\\approx 55.255\\ \\mathrm{m/s}.$$\n"
    "Rounded to two decimal places, $U_0\\approx 55.26\\ \\mathrm{m/s}$, consistent with the allowed band "
    "55.20 to 55.33 for this NAT."
)

NEW_HINTS = [
    "From $\\lambda=\\sigma\\pm i\\omega_d$, compute $\\Omega_n=\\sqrt{\\sigma^2+\\omega_d^2}$ (not $\\omega_d$ alone).",
    "Use the phugoid approximation $\\Omega_n\\approx \\sqrt{2}\\,g/U_0$ $\\Rightarrow$ $U_0=\\sqrt{2}\\,g/\\Omega_n$.",
    "Carry enough digits in $\\Omega_n$ before dividing; round only the final $U_0$ to two decimals.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: Read $\\lambda_{1,2}=-0.02\\pm i\\,0.25$ as $\\sigma=-0.02\\ \\mathrm{rad/s}$, "
        "$\\omega_d=0.25\\ \\mathrm{rad/s}$."
    ),
    (
        "Step 2: Undamped natural frequency: "
        "$\\Omega_n=\\sqrt{\\sigma^2+\\omega_d^2}"
        "=\\sqrt{(-0.02)^2+(0.25)^2}=\\sqrt{0.0629}\\approx 0.250798\\ \\mathrm{rad/s}$."
    ),
    (
        "Step 3: Phugoid approximation (level cruise, small $\\alpha$): "
        "$\\Omega_n\\approx \\dfrac{\\sqrt{2}\\,g}{U_0}$."
    ),
    ("Step 4: Solve for equilibrium speed: $U_0=\\dfrac{\\sqrt{2}\\,g}{\\Omega_n}$."),
    (
        "Step 5: Substitute $g=9.8\\ \\mathrm{m/s^2}$, $\\Omega_n\\approx 0.250798\\ \\mathrm{rad/s}$:\n"
        "$U_0=\\dfrac{\\sqrt{2}\\times 9.8}{0.250798}"
        "\\approx \\dfrac{1.41421\\times 9.8}{0.250798}"
        "\\approx \\dfrac{13.8593}{0.250798}\\approx 55.255\\ \\mathrm{m/s}$."
    ),
    (
        "Step 6: Round to two decimals: $U_0\\approx 55.26\\ \\mathrm{m/s}$ "
        "(within 55.20 to 55.33)."
    ),
]

NEW_FORMULAS_USED = [
    r"$\lambda=\sigma\pm i\omega_d$",
    r"$\Omega_n=\sqrt{\sigma^2+\omega_d^2}$",
    r"$\Omega_n\approx \sqrt{2}\,g/U_0$",
    r"$U_0=\sqrt{2}\,g/\Omega_n$",
]

NEW_SOLUTION_PATH = (
    "Eigenvalues → $\\Omega_n=\\sqrt{\\sigma^2+\\omega_d^2}$ → phugoid $\\Omega_n\\approx\\sqrt{2}\\,g/U_0$ → "
    "arithmetic → $55.26\\ \\mathrm{m/s}$."
)

NEW_KEY_INSIGHTS: List[str] = [
    "$\\Omega_n$ uses both $\\sigma$ and $\\omega_d$, not $\\omega_d$ alone.",
    "The $\\sqrt{2}\\,g/U_0$ phugoid link is the intended GATE path from eigenvalues to cruise speed.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Requires the phugoid approximation $\Omega_n=\sqrt{2}\,g/U_0$ (or equivalent) for steady level flight.",
    r"Correctly forms $\Omega_n=\sqrt{\sigma^2+\omega_d^2}$ from $\lambda=\sigma\pm i\omega_d$.",
    "Careful numeric evaluation and two-decimal rounding (trap: rounding $\\Omega_n$ too early).",
]

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": (
            "Approximate phugoid natural frequency $\\omega_n$ in level flight vs $U_0$ and $g$?"
        ),
        "back": (
            "$\\displaystyle \\omega_n \\approx \\frac{\\sqrt{2}\\,g}{U_0}$ "
            "(low $\\alpha$, small drag variation). $U_0$ is equilibrium speed."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "concept_recall",
        "front": (
            "Given $\\lambda=\\sigma\\pm i\\omega_d$ (e.g. $\\lambda=-0.02\\pm i\\,0.25$), find $\\omega_n$?"
        ),
        "back": (
            "$\\omega_n=\\sqrt{\\sigma^2+\\omega_d^2}$. Here "
            "$\\omega_n=\\sqrt{0.0629}\\approx 0.2508\\ \\mathrm{rad/s}$."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "application",
        "front": (
            "If $\\omega_n=0.2508\\ \\mathrm{rad/s}$ and $g=9.8\\ \\mathrm{m/s^2}$, find $U_0$."
        ),
        "back": (
            "$U_0=\\dfrac{\\sqrt{2}\\,g}{\\omega_n}\\approx \\dfrac{1.4142\\times 9.8}{0.2508}\\approx "
            "55.26\\ \\mathrm{m/s}$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": (
            "Common mistake using $\\omega_n\\approx \\dfrac{\\sqrt{2}\\,g}{U_0}$?"
        ),
        "back": (
            "Dropping $\\sqrt{2}$ and using $\\omega_n\\approx g/U_0$, skewing $U_0$ low "
            "(e.g. $\\sim 39\\ \\mathrm{m/s}$ vs $\\sim 55\\ \\mathrm{m/s}$)."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "definition",
        "front": "What is the phugoid mode?",
        "back": (
            "Long-period longitudinal oscillation exchanging kinetic and potential energy with $\\alpha$ nearly fixed."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": (
            "Phugoid frequency: “root-two-gee-over-you” — "
            "$\\omega_n\\approx \\dfrac{\\sqrt{2}\\,g}{U_0}$."
        ),
        "concept": "Phugoid approximation: $\\omega_n\\approx \\dfrac{\\sqrt{2}\\,g}{U_0}$.",
        "effectiveness": "high",
        "context": "Steady low-$\\alpha$ cruise.",
    },
    {
        "mnemonic": (
            "Eigenvalue magnitude: $\\omega_n=\\sqrt{\\sigma^2+\\omega_d^2}$ from $\\lambda=\\sigma\\pm i\\omega_d$."
        ),
        "concept": "Undamped natural frequency from damped pair.",
        "effectiveness": "medium",
        "context": "Computing $\\Omega_n$ before applying phugoid–speed link.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            "Using only $\\omega_d=0.25\\ \\mathrm{rad/s}$ as $\\omega_n$ and ignoring $\\sigma=-0.02$."
        ),
        "why_students_make_it": "Assuming $\\omega_d\\approx \\omega_n$ without checking damping magnitude.",
        "type": "Approximation",
        "severity": "Medium",
        "frequency": "common",
        "how_to_avoid": (
            "Use $\\omega_n=\\sqrt{\\sigma^2+\\omega_d^2}$ unless told damping is negligible."
        ),
        "consequence": "$U_0$ can drift outside the keyed numeric band.",
    },
    {
        "mistake": (
            "Forgetting $\\sqrt{2}$: using $\\omega_n=g/U_0$ instead of $\\omega_n\\approx \\sqrt{2}\\,g/U_0$."
        ),
        "why_students_make_it": "Misremembering the standard phugoid approximation.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": (
            "Memorize $\\Omega_n\\approx \\sqrt{2}\\,g/U_0$ (level, low-$\\alpha$); sanity-check dimensions."
        ),
        "consequence": "$U_0$ wrong by a large factor.",
    },
    {
        "mistake": "Mixing units (e.g. $g$ in ft/s$^2$ while expecting $U_0$ in m/s).",
        "why_students_make_it": "Sloppy unit bookkeeping.",
        "type": "Units",
        "severity": "High",
        "frequency": "rare",
        "how_to_avoid": "Keep SI: $g$ in $\\mathrm{m/s^2}$, $U_0$ in $\\mathrm{m/s}$.",
        "consequence": "Answers off by conversion factors.",
    },
    {
        "mistake": (
            "Wrong algebra for $\\omega_n$ (e.g. adding $\\sigma+\\omega_d$) or over-building full state matrices."
        ),
        "why_students_make_it": "Algebra slip or over-rigorous approach under time pressure.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": "Use $\\omega_n=\\sqrt{\\sigma^2+\\omega_d^2}$; GATE expects standard shortcuts here.",
        "consequence": "Incorrect $\\omega_n\\Rightarrow$ incorrect $U_0$.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Must Attempt",
    "triage_tip": (
        "Recognize $\\lambda=\\sigma\\pm i\\omega_d$. Compute $\\Omega_n=\\sqrt{\\sigma^2+\\omega_d^2}$, then "
        "$U_0\\approx \\sqrt{2}\\,g/\\Omega_n$ with $g=9.8\\ \\mathrm{m/s^2}$. About 2 minutes if you know the link."
    ),
    "guessing_heuristic": (
        "$\\Omega_n\\approx 0.25\\ \\mathrm{rad/s}$, $g=9.8\\ \\mathrm{m/s^2}$ "
        "$\\Rightarrow U_0\\sim \\sqrt{2}\\cdot 9.8/0.25\\approx 55\\ \\mathrm{m/s}$; drop answers far from 50–80."
    ),
    "time_management": "Budget 2–3 minutes; avoid deriving the full longitudinal model from scratch.",
}

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Full linearized longitudinal model",
        "description": (
            "Build the $4\\times 4$ longitudinal state matrix, form the characteristic polynomial, identify phugoid "
            "roots without invoking $\\Omega_n\\approx \\sqrt{2}\\,g/U_0$ directly."
        ),
        "pros_cons": "Rigorous but slow; needs stability derivatives.",
        "when_to_use": "Design/academic verification—not first-line for GATE time.",
    },
    {
        "name": "Energy-based phugoid picture",
        "description": (
            "Model exchange of kinetic/potential energy; linearizing yields the same order of magnitude "
            "$\\Omega_n\\sim \\sqrt{2}\\,g/U_0$ relation."
        ),
        "pros_cons": "Good intuition; easy to mis-sign without practice.",
        "when_to_use": "Concept checks after you know the shortcut.",
    },
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    return t1


def patch_tier_2(tier_2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t2 = deepcopy(tier_2 or {})
    t2["flashcards"] = NEW_FLASHCARDS
    t2["mnemonics_memory_aids"] = NEW_MNEMONICS
    t2["common_mistakes"] = NEW_COMMON_MISTAKES
    t2["exam_strategy"] = NEW_EXAM_STRATEGY
    return t2


def patch_tier_3(tier_3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t3 = deepcopy(tier_3 or {})
    t3["alternative_methods"] = NEW_ALTERNATIVE_METHODS
    return t3


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning "
                "FROM questions WHERE question_id = :qid"
            ),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        new_t1 = patch_tier_1(row[0])
        new_t2 = patch_tier_2(row[1])
        new_t3 = patch_tier_3(row[2])

        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "tier_2_student_learning = CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning = CAST(:t3 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "t1": json.dumps(new_t1),
                "t2": json.dumps(new_t2),
                "t3": json.dumps(new_t3),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: stem + tier_1/2/3 (single script)")


if __name__ == "__main__":
    asyncio.run(main())

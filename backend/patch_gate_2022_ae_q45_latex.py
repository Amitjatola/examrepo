"""
Fix GATE_2022_AE_Q45 LaTeX across stem, options, tier-1/2/3 (incl. flashcards, mnemonics, mistakes, exam strategy, alternatives).

Straight, level, constant-velocity cruise: typically $\\phi=0$, $\\beta=0$, $\\psi$ arbitrary constant, $\\gamma=0\\Rightarrow\\theta=\\alpha>0$.
Answer **A** matches $\\phi=0,\\ \\theta=2^\\circ,\\ \\psi=0,\\ \\alpha=2^\\circ,\\ \\beta=0$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2022_ae_q45_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2022_AE_Q45"

NEW_QUESTION_TEXT = (
    "For a conventional airplane in straight, level, constant velocity flight, which of the following "
    "condition(s) is/are possible for the Euler angles (φ, θ, ψ), angle of attack α, and sideslip angle β?"
)

NEW_QUESTION_TEXT_LATEX = (
    "For a conventional airplane in **straight, level, constant-velocity** flight, which of the following "
    "condition(s) is/are possible for the Euler angles $(\\phi,\\theta,\\psi)$, angle of attack $\\alpha$, "
    "and sideslip angle $\\beta$?"
)

NEW_OPTIONS = {
    "A": r"$\phi=0^\circ,\ \theta=2^\circ,\ \psi=0^\circ,\ \alpha=2^\circ,\ \beta=0^\circ$",
    "B": r"$\phi=5^\circ,\ \theta=0^\circ,\ \psi=0^\circ,\ \alpha=2^\circ,\ \beta=0^\circ$",
    "C": r"$\phi=0^\circ,\ \theta=3^\circ,\ \psi=0^\circ,\ \alpha=3^\circ,\ \beta=5^\circ$",
    "D": r"$\phi=0^\circ,\ \theta=5^\circ,\ \psi=0^\circ,\ \alpha=2^\circ,\ \beta=5^\circ$",
}

NEW_REASONING = (
    "**Straight** flight (no net lateral maneuver as intended here): sideslip should vanish, **$\\beta=0$**; "
    "wings level implies **$\\phi=0$** (not a coordinated turn). **Level** flight means flight-path angle "
    "**$\\gamma=0$**. With standard wind-axis relation **$\\theta=\\alpha+\\gamma$**, level flight gives "
    "**$\\theta=\\alpha$**. Lift must balance weight, so **$\\alpha>0$** (small positive) in normal cruise. "
    "**$\\psi$** can be any constant heading (e.g. $0^\\circ$).\n\n"
    "**A:** $\\phi=0$, $\\beta=0$, $\\theta=\\alpha=2^\\circ$, $\\psi=0$ — consistent.\n\n"
    "**B:** $\\phi=5^\\circ$ breaks wings-level straight flight; also $\\theta=0$ while $\\alpha=2^\\circ$ gives "
    "$\\gamma=\\theta-\\alpha=-2^\\circ$ (descending), not level.\n\n"
    "**C, D:** $\\beta\\neq 0$ contradicts straight, symmetric flight. Hence **A** is correct."
)

NEW_HINTS = [
    "Parse the words: **straight** $\\Rightarrow$ typically $\\beta=0$ and $\\phi=0$; **level** $\\Rightarrow$ $\\gamma=0\\Rightarrow \\theta=\\alpha$.",
    "Need **$\\alpha>0$** in normal level cruise so lift $\\approx W$.",
    "Eliminate any option with **$\\beta\\neq 0$** or **$\\phi\\neq 0$** for this intended straight/level reading.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: **Straight, level, constant-$V$** means: no climb/descent ($\\gamma=0$), no sideslip ($\\beta=0$), "
        "wings level ($\\phi=0$) for non-turning flight, and $\\psi$ may be any constant."
    ),
    (
        "Step 2: Use **$\\theta=\\alpha+\\gamma$**. With **$\\gamma=0$**, **$\\theta=\\alpha$**."
    ),
    (
        "Step 3: **Lift** in level flight requires **$\\alpha>0$** (small); thus **$\\theta>0$** too."
    ),
    (
        "Step 4: **Scan options:** reject **B** ($\\phi\\neq 0$, and $\\theta\\neq\\alpha$). "
        "Reject **C** and **D** ($\\beta\\neq 0$)."
    ),
    (
        "Step 5: **A** satisfies $\\phi=0$, $\\beta=0$, $\\theta=\\alpha=2^\\circ$, $\\psi=0$ — select **A**."
    ),
]

NEW_FORMULAS_USED = [
    r"$\theta=\alpha+\gamma$",
    r"$\gamma=0$ (level flight)",
    r"$\beta=0,\ \phi=0$ (straight, wings-level, non-turning)",
    r"$\alpha>0$ for lift in normal cruise",
]

NEW_SOLUTION_PATH = (
    "Interpret straight/level $\\Rightarrow$ $\\beta=0$, $\\phi=0$, $\\gamma=0$; "
    "then $\\theta=\\alpha>0$; match **A**."
)

NEW_KEY_INSIGHTS = [
    "$\\theta$ (pitch Euler) is not the same as $\\alpha$ unless $\\gamma=0$.",
    "Nonzero $\\beta$ or bank $\\phi$ contradicts the usual GATE reading of straight + level + symmetric cruise.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    (
        "Links **Euler** $(\\phi,\\theta,\\psi)$ to **aerodynamic** $(\\alpha,\\beta)$ and flight-path angle $\\gamma$ "
        "via $\\theta=\\alpha+\\gamma$."
    ),
    "Must enforce **$\\beta=0$**, **$\\phi=0$**, and **$\\theta=\\alpha$** simultaneously for the intended condition.",
    "Trap: accepting **nonzero bank** or **sideslip** as still “straight/level.”",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$\theta=\alpha+\gamma$",
        "name": "Pitch vs angle of attack vs flight-path angle",
        "conditions": "Standard small-angle wind-triangle relation in longitudinal plane; $\\gamma$ is flight-path angle.",
        "type": "equation",
        "relevance": "Level flight ($\\gamma=0$) forces $\\theta=\\alpha$.",
    },
    {
        "formula": r"$\beta=0,\ \phi=0$",
        "name": "Straight, wings-level flight (GATE-style reading)",
        "conditions": "No sideslip; no bank for non-turning symmetric flight.",
        "type": "constraint",
        "relevance": "Eliminates options with nonzero $\\beta$ or $\\phi$.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            "Confusing Euler angles $(\\psi,\\theta,\\phi)$ with aerodynamic angles $(\\alpha,\\beta)$—e.g. assuming "
            "$\\theta=\\alpha$ always, or allowing nonzero $\\phi$ in “straight, level” flight."
        ),
        "why_students_make_it": (
            "Similar words (“pitch/roll”) and overlapping notation; forgetting $\\gamma$ in $\\theta=\\alpha+\\gamma$; "
            "not visualizing that bank tilts the lift vector."
        ),
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            "Separate frames: Euler = body vs inertial; $\\alpha,\\beta$ = body vs wind. Memorize "
            "$\\theta=\\alpha+\\gamma$. Remember **nonzero bank $\\phi\\neq 0$** tilts lift horizontally unless "
            "coordinated—**not** plain straight & level in this MCQ sense."
        ),
        "consequence": (
            "Wrong elimination of valid sets or acceptance of $\\phi\\neq 0$ / $\\beta\\neq 0$ options."
        ),
    },
    {
        "mistake": "Assuming $\\alpha=0$ in level cruise.",
        "why_students_make_it": "Confusing “fuselage horizontal” with zero $\\alpha$; neglecting that $L\\approx W$ needs incidence.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": "In normal level flight, **$\\alpha>0$** (small) is required for positive lift at cruise $C_L$.",
        "consequence": "May accept inconsistent $\\theta,\\alpha$ pairs or deny valid $\\theta=\\alpha>0$ cases.",
    },
    {
        "mistake": "Ignoring that **$\\beta\\neq 0$** breaks “straight” symmetric flight in this context.",
        "why_students_make_it": "Underestimating how strictly GATE ties “straight” to $\\beta=0$ (and $\\phi=0$).",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": "Check **$\\beta=0$** and **$\\phi=0$** first; then enforce **$\\theta=\\alpha$**, **$\\alpha>0$**.",
        "consequence": "Selecting **C** or **D** despite nonzero sideslip.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Must Attempt",
    "triage_tip": (
        "Pure definitions: **straight** $\\Rightarrow$ **$\\beta=0$**, **$\\phi=0$**; **level** $\\Rightarrow$ "
        "**$\\gamma=0\\Rightarrow\\theta=\\alpha$** with **$\\alpha>0$**. Eliminate contradictions in seconds."
    ),
    "guessing_heuristic": (
        "Prefer rows with **$\\beta=0$** and **$\\phi=0$**; then require **$\\theta=\\alpha$**."
    ),
    "time_management": "1–3 minutes: eliminate by constraints, no heavy algebra.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "definition",
        "front": "**Straight flight:** what about $\\beta$ and $\\phi$ (usual GATE reading)?",
        "back": "**$\\beta=0$** (no sideslip). **$\\phi=0$** (wings level) if not in a coordinated turn.",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "definition",
        "front": "**Level flight:** relate $\\gamma$, $\\theta$, and $\\alpha$.",
        "back": "**$\\gamma=0$**. Use **$\\theta=\\alpha+\\gamma$**, so **$\\theta=\\alpha$**.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application",
        "front": "Straight, level, constant-$V$ cruise: typical constraints on $(\\phi,\\beta,\\psi,\\theta,\\alpha)$?",
        "back": (
            "$\\phi\\approx 0^\\circ$, $\\beta\\approx 0^\\circ$, $\\psi$ any constant, "
            "$\\theta\\approx\\alpha>0$ with $\\gamma\\approx 0^\\circ$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 60,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Common mix-up: Euler vs aerodynamic angles?",
        "back": (
            "Euler $(\\phi,\\theta,\\psi)$: body vs **inertial**. "
            "$\\alpha,\\beta$: body vs **wind** (velocity)."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Why is **$\\phi\\neq 0$** incompatible with plain straight & level here?",
        "back": (
            "Bank tilts the lift vector, adding a **horizontal** component unless a coordinated turn is intended—"
            "so **non-turning** straight & level needs **$\\phi\\approx 0$** together with **$\\beta=0$**."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": "**SAL:** Straight And Level → **$\\phi=0$**, **$\\beta=0$**, and **$\\theta=\\alpha$** (since **$\\gamma=0$**).",
        "concept": "Constraint checklist for symmetric cruise in this question style.",
        "effectiveness": "high",
        "context": "MCQs tying words “straight/level” to angle constraints.",
    },
    {
        "mnemonic": "**Bank zero, beta zero** — then match **$\\theta$** to **$\\alpha$**.",
        "concept": "First kill sideslip & bank; then enforce level-flight wind triangle.",
        "effectiveness": "high",
        "context": "Rapid option scanning on flight-mechanics concept items.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Rotation matrix method",
        "description": (
            "Express $\\vec{V}$ in Earth axes via direction cosines; enforce **level** ($w_E\\approx 0$ in the chosen frame) "
            "and **straight** (no lateral path curvature) to derive $\\beta=0$, $\\phi=0$, and $\\theta=\\alpha$ when $\\gamma=0$."
        ),
        "pros_cons": "Rigorous; slower for a quick MCQ.",
        "when_to_use": "Verification or when geometry feels ambiguous.",
    },
    {
        "name": "Velocity-triangle sketch",
        "description": (
            "Draw $\\vec{V}$, body $x$-axis, and horizontal. For **$\\gamma=0$**, the angle between $\\vec{V}$ and horizontal "
            "equals **$\\theta-\\alpha$** (sign convention as in $\\theta=\\alpha+\\gamma$); setting **$\\gamma=0$** forces "
            "**$\\theta=\\alpha$**."
        ),
        "pros_cons": "Builds intuition; needs practice to be fast.",
        "when_to_use": "If you forget $\\theta=\\alpha+\\gamma$ but can sketch.",
    },
    {
        "name": "Direct Euler-angle extraction",
        "description": (
            "If velocity components are given, compute $\\phi,\\theta,\\psi$ from transformation formulas—overkill when the "
            "item only asks feasibility of angle sets."
        ),
        "pros_cons": "Exact but time-consuming.",
        "when_to_use": "Numeric verification, not first-line triage.",
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
    sbs["approach_type"] = sbs.get("approach_type") or "Conceptual Application and Constraint Satisfaction"

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    return t1


def patch_tier_2(tier_2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t2 = deepcopy(tier_2 or {})
    t2["common_mistakes"] = NEW_COMMON_MISTAKES
    t2["exam_strategy"] = NEW_EXAM_STRATEGY
    t2["flashcards"] = NEW_FLASHCARDS
    t2["mnemonics_memory_aids"] = NEW_MNEMONICS
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
                "options = CAST(:opts AS jsonb), "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "tier_2_student_learning = CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning = CAST(:t3 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(new_t1),
                "t2": json.dumps(new_t2),
                "t3": json.dumps(new_t3),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: stem/options/tier-1/2/3 LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

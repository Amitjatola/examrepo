"""
Fix GATE_2019_AE_Q18 LaTeX across stem, tier-1/2/3.

Vertical-plane kinematics (wind axes): $\\theta=\\alpha+\\gamma$, 
$\\tan\\gamma=V_V/V_H$. NAT band $5.98$–$6.00^\\circ$; $\\theta\\approx 5.9996^\\circ\\to 6.00^\\circ$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2019_ae_q18_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q18"

NEW_QUESTION_TEXT_PLAIN = (
    "For an airplane flying in a vertical plane, the angle of attack is 3°, "
    "and the horizontal and vertical components of velocity in wind axes are "
    "300 km/h and 15.72 km/h, respectively. The pitch attitude of the airplane is "
    "______° (round off to 2 decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    "For an airplane flying in a vertical plane, the angle of attack is $\\alpha = 3^\\circ$. "
    "The horizontal and vertical components of velocity in wind axes are "
    "$V_H = 300~\\mathrm{km/h}$ and $V_V = 15.72~\\mathrm{km/h}$, respectively. "
    "The pitch attitude is $\\underline{\\hspace{3.5em}}~^\\circ$ "
    "(round off to 2 decimal places)."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"In the longitudinal vertical plane, pitch attitude $\theta$, angle of attack $\alpha$, and flight-path "
    r"angle $\gamma$ satisfy the wind-axis relation $\theta=\alpha+\gamma$."
    "\n\n"
    r"Given $\alpha=3^\circ$, $V_H=300~\mathrm{km/h}$, $V_V=15.72~\mathrm{km/h}$ (consistent units), "
    r"$\displaystyle \tan\gamma=\frac{V_V}{V_H}=\frac{15.72}{300}=0.0524$, so "
    r"$\gamma=\arctan(0.0524)\approx 2.99956^\circ$."
    "\n\n"
    r"Hence $\theta=\alpha+\gamma\approx 3^\circ+2.99956^\circ\approx 5.99956^\circ$. "
    r"Rounded to two decimals: $\theta\approx 6.00^\circ$, within $5.98^\circ$–$6.00^\circ$."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Given $\alpha=3^\circ$, $V_H=300~\mathrm{km/h}$, $V_V=15.72~\mathrm{km/h}$ (wind-axis components)."
    ),
    (r"Recall $\theta=\alpha+\gamma$ with flight-path angle $\gamma$."),
    (
        r"From velocity components (horizontal/vertical), $\tan\gamma=\dfrac{V_V}{V_H}$ "
        r"(angle of velocity above horizontal)."
    ),
    (
        r"Compute $\tan\gamma=15.72/300=0.0524$; $\gamma=\arctan(0.0524)\approx 2.99956^\circ$."
    ),
    (r"Sum: $\theta\approx 3^\circ+2.99956^\circ\approx 5.99956^\circ$."),
    (r"Round to two decimal places: $\theta\approx 6.00^\circ$."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$\theta=\alpha+\gamma$",
    r"$\tan\gamma=\dfrac{V_V}{V_H}$",
]

NEW_HINTS: List[str] = [
    (
        r"Wind-axis horizontal/vertical velocity components fix the flight-path direction: "
        r"$\gamma=\arctan(V_V/V_H)$."
    ),
    (
        r"Pitch attitude is not $\alpha$ alone: add $\gamma$ for $\theta=\alpha+\gamma$."
    ),
    (
        r"$V_H$ and $V_V$ share units here—no extra conversion needed before taking the ratio."
    ),
]

NEW_SOLUTION_PATH = (
    r"$V_H,V_V \Rightarrow \gamma=\arctan(V_V/V_H)$ $\Rightarrow$ $\theta=\alpha+\gamma$ $\Rightarrow$ round"
)

NEW_KEY_INSIGHTS: List[str] = [
    r"$\theta$ (pitch Euler about lateral axis in this vertical-plane picture) follows $\theta=\alpha+\gamma$ "
    r"when $\gamma$ is the flight-path angle above horizontal.",
    (
        r"$\alpha$ is body attitude relative to the wind; $\gamma$ sets where the wind vector points vs horizon."
    ),
    r"Ratio $V_V/V_H$ is small here, but still use $\arctan$ for $\gamma$ in degrees.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Must recall $\theta=\alpha+\gamma$ (not $\theta=\alpha$).",
    r"Correct identification of $\gamma$ from $(V_H,V_V)$ via $\tan\gamma=V_V/V_H$.",
    r"Final rounding to two decimals after full-precision $\gamma$.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$\theta=\alpha+\gamma$",
        "name": r"Pitch vs angle of attack vs flight-path angle",
        "conditions": [
            r"Vertical-plane / longitudinal wind-triangle relation with $\gamma$ measured from horizontal.",
        ],
        "type": "equation",
        "relevance": r"Combines body pitch and flight path into pitch attitude.",
    },
    {
        "formula": r"$\tan\gamma=\dfrac{V_V}{V_H}$",
        "name": r"Flight-path angle from wind-axis velocity components",
        "conditions": [
            r"$V_H,V_V$ are horizontal and vertical components of true airspeed in the vertical plane.",
        ],
        "type": "equation",
        "relevance": r"Solves $\gamma$ needed in $\theta=\alpha+\gamma$.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": r"Taking $\theta=\alpha$ and ignoring $\gamma$.",
        "why_students_make_it": r"Confusing pitch attitude with angle of attack.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Always add $\gamma$ when velocity is not horizontal.",
        "consequence": r"Answer near $3^\circ$ instead of $\approx 6^\circ$.",
    },
    {
        "mistake": r"Using $\sin$ or $\cos$ instead of $\tan$ for $\gamma$ from $(V_H,V_V)$.",
        "why_students_make_it": r"Misremembering the right-triangle ratio.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Opposite/adjacent: $V_V/V_H=\tan\gamma$.",
        "consequence": r"Wrong $\gamma$ and $\theta$.",
    },
    {
        "mistake": r"Rounding $\gamma$ to $3.00^\circ$ early then summing, masking $5.9996^\circ$ vs $6.00^\circ$ nuance.",
        "why_students_make_it": r"Rounding intermediate steps.",
        "type": "Calculation",
        "severity": "Low",
        "frequency": "occasional",
        "how_to_avoid": r"Carry precision; round the final $\theta$.",
        "consequence": r"Possible $0.01^\circ$ shifts near boundaries.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": r"Quick score if $\theta=\alpha+\gamma$ is automatic.",
    "triage_tip": (
        r"Vertical-plane wind components $\Rightarrow$ $\gamma=\arctan(V_V/V_H)$ "
        r"$\Rightarrow$ $\theta=\alpha+\gamma$."
    ),
    "guessing_heuristic": (
        r"$V_V/V_H\approx 0.0524$ is a few degrees on the radian scale—expect $\gamma\approx 3^\circ$, "
        r"so $\theta\approx 6^\circ$."
    ),
    "time_management": r"About 2 minutes including rounding.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "concept_recall",
        "front": r"Relate pitch attitude $\theta$, angle of attack $\alpha$, and flight-path angle $\gamma$.",
        "back": r"$\theta=\alpha+\gamma$ (vertical-plane wind-triangle form used here).",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": r"Compute $\gamma$ from horizontal and vertical wind-axis speeds $V_H,V_V$.",
        "back": r"$\tan\gamma=\dfrac{V_V}{V_H}$, i.e.\ $\gamma=\arctan\left(\dfrac{V_V}{V_H}\right)$.",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Why is $\alpha$ not equal to pitch attitude $\theta$ in general?",
        "back": (
            r"$\alpha$ is relative to the wind direction; $\theta$ is relative to the horizon— they differ by $\gamma$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application",
        "front": (
            r"Given $\alpha=3^\circ$, $V_H=300~\mathrm{km/h}$, $V_V=15.72~\mathrm{km/h}$, estimate $\theta$ ($2$ decimals)."
        ),
        "back": (
            r"$\gamma=\arctan(15.72/300)\approx 2.99956^\circ$; "
            r"$\theta\approx 3^\circ+2.99956^\circ\approx 6.00^\circ$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 60,
    },
    {
        "card_type": "formula_recall",
        "front": r"Express $\gamma$ using $V_H$ and $V_V$ only.",
        "back": r"$\gamma=\arctan\left(\dfrac{V_V}{V_H}\right)$.",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"PAP: Pitch = Attack + Path ($\theta=\alpha+\gamma$).",
        "concept": r"Longitudinal angle bookkeeping",
        "effectiveness": "high",
        "context": r"VERT-plane velocity-component items.",
    },
    {
        "mnemonic": r"$\tan\gamma$: vertical over horizontal ($V_V/V_H$).",
        "concept": r"Flight-path angle from components",
        "effectiveness": "medium",
        "context": r"Wind-axis decomposition.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": r"Vector direction angle",
        "description": (
            r"Treat $\mathbf{V}=(V_H,V_V)$; its angle above horizontal is still "
            r"$\gamma=\arctan(V_V/V_H)$—same calculation."
        ),
        "pros_cons": r"Same algebra; geometry reinforces signs.",
        "when_to_use": r"If sketching the velocity triangle.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "pitch attitude angle of attack flight path angle",
    "theta equals alpha plus gamma",
    "wind axis velocity components vertical plane",
    "arctan vertical horizontal velocity",
    "GATE AE flight mechanics longitudinal",
    "flight path angle tangent ratio",
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = r"$\approx 6.00^\circ$ (official band: $5.98^\circ$ to $6.00^\circ$)"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["approach_type"] = sbs.get("approach_type") or "Kinematic wind triangle"

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = [
        r"Trigonometry: $\tan$, $\arctan$.",
        r"Resolve velocity into horizontal/vertical components.",
        r"Definitions of $\alpha$, $\gamma$, and $\theta$ in longitudinal flight.",
    ]

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
    t3["search_keywords"] = NEW_SEARCH_KEYWORDS
    return t3


async def main() -> None:
    opts_json = json.dumps(NEW_OPTIONS)

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
                "qt": NEW_QUESTION_TEXT_PLAIN,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": opts_json,
                "t1": json.dumps(new_t1),
                "t2": json.dumps(new_t2),
                "t3": json.dumps(new_t3),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: stem/tier-1/2/3 LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

"""
Fix GATE_2015_AE_Q42 LaTeX across stem, tier-1/2/3.

Equilibrium glide: $L=W\cos\theta=\tfrac{1}{2}\rho_\infty V_\infty^2 S C_L$
$\Rightarrow$ $V_\infty=\sqrt{\dfrac{2(W/S)\cos\theta}{\rho_\infty C_L}}$.
At $(L/D)_{\max}$, $\tan\theta=1/(L/D)$; small-angle $\cos\theta\approx 1$.
NAT band $39.5$–$40.5~\mathrm{m/s}$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2015_ae_q42_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2015_AE_Q42"

NEW_QUESTION_TEXT_PLAIN = (
    "An aircraft with wing loading W/S = 500 N/m² is gliding at (L/D)max = 10 and C_L = 0.69. "
    "Considering the free-stream density ρ∞ = 0.9 kg/m³, the equilibrium glide speed (in m/s) is ______."
)

NEW_QUESTION_TEXT_LATEX = (
    "An aircraft with wing loading $(W/S) = 500~\mathrm{N/m^2}$ is gliding at "
    r"$(L/D)_{\max} = 10$ and $C_L = 0.69$. Freestream density is $\rho_\infty = 0.9~\mathrm{kg/m^3}$. "
    r"The equilibrium glide speed is $\underline{\hspace{3.5em}}~\mathrm{m/s}$."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"In steady equilibrium glide along a straight path at angle $\theta$ to the horizontal, "
    r"lift balances the component of weight normal to the velocity: $L=W\cos\theta$. "
    r"Using $L=\tfrac{1}{2}\rho_\infty V_\infty^2 S C_L$ and dividing by $S$, "
    r"$\tfrac{1}{2}\rho_\infty V_\infty^2 C_L=(W/S)\cos\theta$, hence "
    r"$V_\infty=\sqrt{\dfrac{2(W/S)\cos\theta}{\rho_\infty C_L}}$."
    "\n\n"
    r"Given $(L/D)_{\max}=10$, for minimum-drag glide $\tan\theta = 1/(L/D)=0.1$, so "
    r"$\theta=\arctan(0.1)\approx 5.71^\circ$ and $\cos\theta\approx 0.9950$. "
    r"Often (including quick GATE substitution) one uses $\cos\theta\approx 1$ because the angle is small."
    "\n\n"
    r"With $(W/S)=500~\mathrm{N/m^2}$, $\rho_\infty=0.9~\mathrm{kg/m^3}$, $C_L=0.69$:"
    "\n\n"
    r"$\displaystyle V_\infty \approx \sqrt{\frac{2\times 500\times 1}{0.9\times 0.69}}"
    r"=\sqrt{\dfrac{1000}{0.621}}\approx 40.13~\mathrm{m/s}$ (using $\cos\theta\approx 1$)."
    "\n\n"
    r"Using $\cos\theta\approx 0.9950$ instead gives $V_\infty\approx 40.03~\mathrm{m/s}$—still within "
    r"$39.5$–$40.5~\mathrm{m/s}$."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Glide equilibrium: $L=W\cos\theta$, $D=W\sin\theta$; lift equation "
        r"$L=\tfrac{1}{2}\rho_\infty V_\infty^2 S C_L$."
    ),
    (
        r"Eliminate $S$: $\tfrac{1}{2}\rho_\infty V_\infty^2 C_L=(W/S)\cos\theta$ "
        r"$\Rightarrow$ $V_\infty=\sqrt{\dfrac{2(W/S)\cos\theta}{\rho_\infty C_L}}$."
    ),
    (
        r"Relate $\theta$ to $L/D$: $\tan\theta=D/L=1/(L/D)$. Here $\tan\theta=1/10$, small angle."
    ),
    (
        r"Substitute $(W/S)=500~\mathrm{N/m^2}$, $\rho_\infty=0.9~\mathrm{kg/m^3}$, $C_L=0.69$; "
        r"use $\cos\theta\approx 1$ (or include $\cos\theta$ for a slightly smaller value)."
    ),
    (r"Compute $V_\infty\approx 40.1~\mathrm{m/s}$ (nearest typical rounding); check band."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$V_\infty=\sqrt{\dfrac{2(W/S)\cos\theta}{\rho_\infty C_L}}$",
    r"$L=W\cos\theta$ (glide, lift normal to flight path)",
    r"$L=\tfrac{1}{2}\rho_\infty V_\infty^2 S C_L$",
    r"$\tan\theta=\dfrac{D}{L}=\dfrac{1}{L/D}$",
]

NEW_HINTS: List[str] = [
    (
        r"Do not plug $(L/D)_{\max}$ into the speed formula as if it were $C_L$; speed uses the given $C_L$."
    ),
    (
        r"Convert force balance to wing loading: divide the lift equation by $S$."
    ),
    (
        r"For $\tan\theta=0.1$, either use $\cos\theta\approx 1$ or include $\cos\theta\approx 0.995$."
    ),
]

NEW_SOLUTION_PATH = (
    r"Force balance $\Rightarrow$ $V_\infty(\rho_\infty,C_L,W/S,\theta)$ $\Rightarrow$ "
    r"$\tan\theta$ from $L/D$ $\Rightarrow$ substitute numbers"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"Glide speed at a chosen $C_L$ scales like $\sqrt{(W/S)/(\rho_\infty C_L)}$; "
        r"$(L/D)_{\max}$ sets $\theta$ (and range), not $V_\infty$ directly."
    ),
    r"Small glide angles make $\cos\theta$ close to $1$ in the lift–weight relation.",
    r"Always use $L=W\cos\theta$, not $L=W$, unless $\theta$ is negligible by assumption.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Recognize correct glide balance $L=W\cos\theta$ versus level cruise $L=W$.",
    r"Separate roles of $C_L$ (speed) vs $L/D$ (angle/range).",
    r"Optional precision: $\cos\theta$ vs $1$ changes the answer slightly.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$V_\infty=\sqrt{\dfrac{2(W/S)\cos\theta}{\rho_\infty C_L}}$",
        "name": "Equilibrium glide speed (incompressible lift equation)",
        "conditions": [
            r"Steady unaccelerated glide; constant $\rho_\infty$ and $C_L$ along the segment considered.",
        ],
        "type": "equation",
        "relevance": r"Solves $V_\infty$ given wing loading, density, and operating $C_L$.",
    },
    {
        "formula": r"$\tan\theta=\dfrac{1}{L/D}$",
        "name": r"Glide angle from $L/D$ (equilibrium)",
        "conditions": [r"Small-angle glide with thrust off; drag equals weight component along path."],
        "type": "equation",
        "relevance": r"Links $(L/D)_{\max}$ to $\theta$ for minimum-drag glide.",
    },
    {
        "formula": r"$L=\tfrac{1}{2}\rho_\infty V_\infty^2 S C_L$",
        "name": "Lift equation",
        "conditions": [r"Incompressible model; $\rho_\infty$ is freestream density."],
        "type": "equation",
        "relevance": r"Combined with $L=W\cos\theta$ to eliminate $S$ via $W/S$.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": r"Using $L=W$ instead of $L=W\cos\theta$ for glide.",
        "why_students_make_it": r"Habit from level-flight formulas.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "common",
        "how_to_avoid": r"Sketch forces relative to the flight path.",
        "consequence": r"Missed $\cos\theta$ factor (small here, but conceptually wrong).",
    },
    {
        "mistake": r"Treating $(L/D)_{\max}$ like $C_L$ in the velocity formula.",
        "why_students_make_it": r"Parameter confusion under time pressure.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Tag each symbol: given $C_L=0.69$ is what enters $C_L$ in the lift equation.",
        "consequence": r"Large numerical error.",
    },
    {
        "mistake": r"Forgetting to divide lift equation by $S$ to use wing loading directly.",
        "why_students_make_it": r"Algebra slip.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Start from $L=W\cos\theta$ and $L=qSC_L$.",
        "consequence": r"Wrong scaling with area.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Fast points if glide-speed template is memorized.",
    "triage_tip": (
        r"Glide $\Rightarrow$ $L=W\cos\theta$ + lift equation $\Rightarrow$ "
        r"$V_\infty=\sqrt{2(W/S)\cos\theta/(\rho_\infty C_L)}$."
    ),
    "guessing_heuristic": (
        r"Order $\sqrt{(W/S)/\rho}$: here $\sqrt{500/0.9}\sim 23.6$, corrected by $C_L$ gives $\sim 40~\mathrm{m/s}$ scale."
    ),
    "time_management": r"About 2 minutes including a quick $\cos\theta$ check.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"Equilibrium glide speed $V_\infty$ in terms of $(W/S)$, $\rho_\infty$, $C_L$, and $\theta$?",
        "back": (
            r"$V_\infty=\sqrt{\dfrac{2(W/S)\cos\theta}{\rho_\infty C_L}}$ "
            r"(from $L=W\cos\theta$ and $L=\tfrac{1}{2}\rho_\infty V_\infty^2 S C_L$)."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "concept_recall",
        "front": r"In a steady glide with zero thrust, relate $L$, $D$, $W$, and $\theta$.",
        "back": (
            r"$L=W\cos\theta$ (normal to path), $D=W\sin\theta$ (along path)."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Does $(L/D)_{\max}$ directly set glide speed if $C_L$ is given?",
        "back": (
            r"No for this setup: $C_L$ enters the lift equation for $V_\infty$. "
            r"$L/D$ mainly sets $\theta$ via $\tan\theta=D/L$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application",
        "front": (
            r"Estimate $V_\infty$ with $(W/S)=600~\mathrm{N/m^2}$, $\rho=1.2~\mathrm{kg/m^3}$, "
            r"$C_L=0.8$, $\cos\theta\approx 1$."
        ),
        "back": (
            r"$V_\infty\approx\sqrt{2\cdot 600/(1.2\cdot 0.8)}=\sqrt{1250}\approx 35.4~\mathrm{m/s}$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 60,
    },
    {
        "card_type": "definition",
        "front": r"What is wing loading $(W/S)$?",
        "back": (
            r"Aircraft weight per unit reference wing area; higher $(W/S)$ tends to increase speeds "
            r"for a fixed aerodynamic operating point."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Glide lift normal: $L=W\cos\theta$, not $W$.",
        "concept": r"Force resolution in glide",
        "effectiveness": "high",
        "context": r"Equilibrium glide vs level cruise.",
    },
    {
        "mnemonic": r"Angle from $L/D$: $\tan\theta=D/L$; speed from $C_L$ + $(W/S)$, $\rho$.",
        "concept": r"Splitting angle vs speed drivers",
        "effectiveness": "high",
        "context": r"Reading GATE stems quickly.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": r"Exact $\cos\theta$",
        "description": (
            r"Compute $\theta=\arctan(1/(L/D))$, then $\cos\theta$ exactly in "
            r"$V_\infty=\sqrt{2(W/S)\cos\theta/(\rho_\infty C_L)}$."
        ),
        "pros_cons": r"Slightly more accurate; usually unnecessary when $\theta$ is small.",
        "when_to_use": r"Low $L/D$ glides or if the prompt demands exact trigonometry.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "equilibrium glide speed formula",
    "gliding flight L equals W cos theta",
    "wing loading glide velocity",
    "lift coefficient glide speed",
    "glide angle arctan 1 over L/D",
    "GATE AE flight mechanics glide",
    "small angle approximation glide",
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = r"$\approx 40~\mathrm{m/s}$ (official band: 39.5 to 40.5)"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["approach_type"] = sbs.get("approach_type") or "Force balance + lift equation"

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = [
        r"Glide equilibrium: $L=W\cos\theta$, $D=W\sin\theta$ (no thrust).",
        r"Lift equation $L=\tfrac{1}{2}\rho_\infty V_\infty^2 S C_L$.",
        r"Wing loading $(W/S)$.",
        r"Relation $\tan\theta=D/L$ for steady glide.",
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

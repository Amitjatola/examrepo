"""
Fix GATE_2019_AE_Q40 LaTeX across stem, tier-1 (solution, hints, prerequisites), tier-2, tier-3.

Symmetric pull-up with pitch angular acceleration: local load factor varies along fuselage.
NAT answer band 2.06–2.08; computed $n_P \\approx 2.07$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2019_ae_q40_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q40"

NEW_QUESTION_TEXT = (
    "The airplane shown in the figure starts executing a symmetric pull-up maneuver from steady level "
    "attitude with a constant nose-up pitch acceleration of 20 deg/s². The vertical load factor measured "
    "at this instant at the centre of gravity (CG) is 2. Given that the acceleration due to gravity is "
    "9.81 m/s², the vertical load factor measured at point P on the nose of the airplane, which is 2 m ahead "
    "of the CG, is ______ (round off to 2 decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    "The airplane shown in the figure starts executing a symmetric pull-up maneuver from steady level attitude "
    "with a constant nose-up pitch acceleration of $20~\\mathrm{deg/s^2}$. The vertical load factor measured "
    "at this instant at the centre of gravity (CG) is $2$. Given that the acceleration due to gravity is "
    "$9.81~\\mathrm{m/s^2}$, the vertical load factor measured at point $P$ on the nose of the airplane, "
    "which is $2~\\mathrm{m}$ ahead of the CG, is $\\underline{\\hspace{3.5em}}$ (round off to 2 decimal places)."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"The vertical load factor at any point on an aircraft is $n = 1 + a_z/g$, where $a_z$ is the total upward "
    r"vertical acceleration at that point. At point $P$, $a_{z,P} = a_{z,\mathrm{CG}} + a_{z,\mathrm{rot}}$, where "
    r"$a_{z,\mathrm{rot}}$ comes from nose-up pitch angular acceleration $\alpha \equiv \ddot{\theta}$ about the CG."
    "\n\n"
    r"1. Vertical acceleration at the CG: given $n_{\mathrm{CG}} = 2$ and $g = 9.81~\mathrm{m/s^2}$,"
    "\n   "
    r"$n_{\mathrm{CG}} = 1 + a_{z,\mathrm{CG}}/g \Rightarrow a_{z,\mathrm{CG}} = (n_{\mathrm{CG}}-1)g "
    r"= 9.81~\mathrm{m/s^2}$ (upward)."
    "\n\n"
    r"2. Convert pitch acceleration to radians: $\ddot{\theta} = 20~\mathrm{deg/s^2}$,"
    "\n   "
    r"$\alpha = 20 \cdot (\pi/180)~\mathrm{rad/s^2} = \pi/9~\mathrm{rad/s^2} \approx 0.34906~\mathrm{rad/s^2}$."
    "\n\n"
    r"3. Additional vertical acceleration at $P$: with $r = 2~\mathrm{m}$ forward of the CG and nose-up $\alpha$,"
    "\n   "
    r"$a_{z,\mathrm{rot}} = r\alpha = 2(\pi/9)~\mathrm{m/s^2} \approx 0.69813~\mathrm{m/s^2}$."
    "\n\n"
    r"4. Total vertical acceleration at $P$: $a_{z,P} = a_{z,\mathrm{CG}} + a_{z,\mathrm{rot}} "
    r"\approx 9.81 + 0.69813 = 10.50813~\mathrm{m/s^2}$."
    "\n\n"
    r"5. Load factor at $P$: $n_P = 1 + a_{z,P}/g \approx 1 + 10.50813/9.81 \approx 2.07117$."
    "\n\n"
    r"6. Rounded to two decimals: $n_P \approx 2.07$, within the specified band $2.06$–$2.08$."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Identify data: $n_{\mathrm{CG}} = 2$, $\ddot{\theta} = 20~\mathrm{deg/s^2}$, "
        r"$r = 2~\mathrm{m}$ (forward of CG), $g = 9.81~\mathrm{m/s^2}$."
    ),
    (
        r"From $n = 1 + a_z/g$, get $a_{z,\mathrm{CG}} = (n_{\mathrm{CG}} - 1)g = g = 9.81~\mathrm{m/s^2}$."
    ),
    (
        r"Convert angular acceleration: $\alpha = 20 \cdot \pi/180~\mathrm{rad/s^2} \approx 0.3491~\mathrm{rad/s^2}$."
    ),
    (
        r"Forward of CG, nose-up $\alpha$ adds upward tangential acceleration: "
        r"$a_{z,\mathrm{rot}} = r\alpha \approx 0.6982~\mathrm{m/s^2}$."
    ),
    (
        r"Superpose: $a_{z,P} = a_{z,\mathrm{CG}} + a_{z,\mathrm{rot}} \approx 10.508~\mathrm{m/s^2}$."
    ),
    (r"Load factor at $P$: $n_P = 1 + a_{z,P}/g \approx 1 + 10.508/9.81 \approx 2.071$."),
    (r"Round to two decimal places: $n_P \approx 2.07$."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$n = 1 + \dfrac{a_z}{g}$",
    r"$a_{z,\mathrm{CG}} = (n_{\mathrm{CG}} - 1)\,g$",
    r"$\alpha_{\mathrm{rad}} = \alpha_{\mathrm{deg}} \cdot \dfrac{\pi}{180}$",
    r"$a_{z,\mathrm{rot}} = r\alpha$",
    r"$a_{z,P} = a_{z,\mathrm{CG}} + a_{z,\mathrm{rot}}$",
    r"$n_P = 1 + \dfrac{a_{z,P}}{g}$",
]

NEW_HINTS: List[str] = [
    (
        r"Use $n_{\mathrm{CG}}$ to get $a_{z,\mathrm{CG}}$ first: "
        r"$n = 1 + a_z/g \Rightarrow a_{z,\mathrm{CG}} = (n_{\mathrm{CG}} - 1)g$."
    ),
    (
        r"Convert $\ddot{\theta}$ from $\mathrm{deg/s^2}$ to $\mathrm{rad/s^2}$ before $a_{z,\mathrm{rot}} = r\alpha$."
    ),
    (
        r"Forward of CG in a nose-up angular acceleration, add $r\alpha$ to $a_{z,\mathrm{CG}}$ along the maneuver plane."
    ),
]

NEW_SOLUTION_PATH = (
    r"Compute $a_{z,\mathrm{CG}}$ from $n_{\mathrm{CG}}$; convert $\ddot{\theta}$ to $\mathrm{rad/s^2}$; "
    r"add $a_{z,\mathrm{rot}} = r\alpha$ at the nose; then $n_P = 1 + a_{z,P}/g$."
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"Load factor is local: different fuselage stations see different $a_z$ when $\alpha \neq 0$ "
        r"(rigid-body kinematics)."
    ),
    (
        r"Here $\omega \approx 0$ at the instant considered, so only tangential/triad terms from $\alpha$ matter "
        r"for the extra nose acceleration (no centripetal term from pitch rate)."
    ),
    (
        r"Always keep angular quantities in radians when combining with distances in SI."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    (
        r"Must treat load factor as local: $n$ varies along the aircraft when pitch angular acceleration is nonzero."
    ),
    (
        r"Rigid-body step $a_{z,P} = a_{z,\mathrm{CG}} + r\alpha$ with consistent axes/sign for nose-up motion."
    ),
    (
        r"Unit trap: $20~\mathrm{deg/s^2}$ must become $\mathrm{rad/s^2}$ via $\pi/180$ before using $a=r\alpha$."
    ),
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$n = 1 + \dfrac{a_z}{g}$",
        "name": "Load factor vs vertical acceleration",
        "conditions": r"$a_z$ is upward vertical acceleration of the point; $g$ is gravitational acceleration.",
        "type": "equation",
        "relevance": r"Relates measured/normalized $n$ to kinematics at any station.",
    },
    {
        "formula": r"$a_{\mathrm{tang}} = r\,\ddot{\theta} = r\alpha$",
        "name": "Tangential acceleration from angular acceleration",
        "conditions": (
            r"Point at distance $r$ from the pivot/CG on a rigid body; small planar maneuver coupling into $a_z$ "
            r"as modeled here."
        ),
        "type": "equation",
        "relevance": r"Adds $a_{z,\mathrm{rot}}$ at the nose for nose-up $\alpha$.",
    },
    {
        "formula": r"$1~\mathrm{deg} = \dfrac{\pi}{180}~\mathrm{rad}$",
        "name": "Degrees to radians",
        "conditions": r"Angular kinematics in SI.",
        "type": "constant",
        "relevance": r"Required before using $a=r\alpha$ with $r$ in meters.",
    },
    {
        "formula": r"$a_{z,P} = a_{z,\mathrm{CG}} + a_{z,\mathrm{rot}}$",
        "name": "Superposition along longitudinal line",
        "conditions": r"Instantaneous vertical-axis component relevant to local load factor in this setup.",
        "type": "principle",
        "relevance": r"Combines translation of CG with rotational contribution at $P$.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": r"Leaving pitch angular acceleration in $\mathrm{deg/s^2}$ when computing $a=r\alpha$.",
        "why_students_make_it": (
            r"Aerospace wording often uses degrees; SI dynamics expects $\alpha$ in $\mathrm{rad/s^2}$."
        ),
        "type": "Units",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Multiply by $\pi/180$ before using $a_{z,\mathrm{rot}} = r\alpha$.",
        "consequence": r"Answer scaled by $\approx 180/\pi$ or $\pi/180$ — typically far off.",
    },
    {
        "mistake": r"Confusing pitch rate $q$ with pitch acceleration $\dot{q}$ or $\ddot{\theta}$.",
        "why_students_make_it": (
            r"Similar notation; this problem gives angular acceleration (tangential effect), not centripetal $q^2 r$."
        ),
        "type": "Conceptual",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Read for $\ddot{\theta}$ (or $\dot{q}$) vs $q$; use $\alpha$ only per problem statement.",
        "consequence": r"Wrong kinematic term (e.g., centripetal) at $\omega \approx 0$.",
    },
    {
        "mistake": r"Using $n_{\mathrm{CG}}$ directly as $n_P$.",
        "why_students_make_it": r"Assuming load factor is uniform across the fuselage.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Recompute $a_z$ at $P$ with rigid-body additions, then $n = 1 + a_z/g$.",
        "consequence": r"Answer stuck at $2.00$ instead of $\approx 2.07$.",
    },
    {
        "mistake": r"Dropping the $1$ in $n = 1 + a_z/g$.",
        "why_students_make_it": r"Treat $n$ as $a_z/g$ only.",
        "type": "Formula Recall",
        "severity": "Medium",
        "frequency": "common",
        "how_to_avoid": r"Remember $n = L/W$ in straight flight maps to $1 + a_z/g$ in this vertical-axis model.",
        "consequence": r"Off by $1g$ in implied $n$.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Must attempt if comfortable with load factor + rigid-body kinematics.",
    "triage_tip": (
        r"Tag as local load factor under $\ddot{\theta}$: get $a_{z,\mathrm{CG}}$ from $n_{\mathrm{CG}}$, convert "
        r"$\mathrm{deg/s^2}\to\mathrm{rad/s^2}$, add $r\alpha$, then $n_P=1+a_{z,P}/g$."
    ),
    "guessing_heuristic": (
        r"$n_P$ should be slightly above $n_{\mathrm{CG}} = 2$ for a nose-forward point in nose-up $\alpha$ "
        r"(order $\sim 0.07$ here)."
    ),
    "time_management": r"Target 2–3 minutes; if units still fuzzy after that, mark and move on.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "definition_and_formula_recall",
        "front": (
            r"What is vertical load factor $n$, and how is it written using upward acceleration $a_z$ and $g$?"
        ),
        "back": (
            r"$n$ compares apparent weight to weight; in this vertical-axis setup $n = 1 + a_z/g$. "
            r"If $n=2$ at the CG, then $a_{z,\mathrm{CG}} = g$."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "concept_and_formula_recall",
        "front": (
            r"With pitch angular acceleration, is $n$ the same at the nose and CG? How does $a_P$ relate to "
            r"$a_{\mathrm{CG}}$ and $\alpha$?"
        ),
        "back": (
            r"In general, no. Along the fuselage, $a$ differs because of rotation; for this 2-D nose-ahead case, "
            r"$a_{z,P} = a_{z,\mathrm{CG}} + r\alpha$ (nose-up $\alpha$ adds upward $a_z$ forward of CG), "
            r"then $n_P = 1 + a_{z,P}/g$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention_and_application",
        "front": r"Why convert angular acceleration from $\mathrm{deg/s^2}$ before using $a = r\alpha$?",
        "back": (
            "SI uses radians in $\\alpha$ paired with $r$ in meters. "
            "Convert using $\\pi/180$ before $r\\alpha$, or the result is off by a large factor."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application_and_mistake_prevention",
        "front": (
            r"During nose-up pitch angular acceleration, how does $a_z$ at a forward point compare to $a_{z,\mathrm{CG}}$?"
        ),
        "back": (
            r"It increases (for a point ahead of CG): add $r\alpha$ converted to $\mathrm{rad/s^2}$. "
            r"Example: $\alpha = 10~\mathrm{deg/s^2} \Rightarrow \alpha \approx 0.1745~\mathrm{rad/s^2}$; "
            r"at $r=3~\mathrm{m}$, extra $a_z \approx 0.5235~\mathrm{m/s^2}$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"Distinguish pitch rate $q$ from pitch angular acceleration ($\dot{q}$ or $\ddot{\theta}$).",
        "back": (
            r"$q$ is angular velocity (centripetal effects scale with $q^2$); $\dot{q}$ or $\ddot{\theta}$ is angular "
            r"acceleration (tangential/$r\alpha$ effects)."
        ),
        "difficulty": "hard",
        "time_limit_seconds": 45,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"One Plus $a_z$ Over $g$: $n = 1 + a_z/g$",
        "concept": r"Load factor from vertical acceleration",
        "effectiveness": "medium",
        "context": r"First step from any stated $n$ or $a_z$.",
    },
    {
        "mnemonic": r"Nose-up $\alpha$: forward station picks up extra $r\alpha$",
        "concept": r"Sign/direction for tangential contribution ahead of CG",
        "effectiveness": "high",
        "context": r"Symmetric pull-up with angular acceleration.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Non-inertial (body-fixed) frame",
        "description": (
            r"Write apparent weight at $P$ using inertial forces from translational and rotational acceleration of "
            r"the body; read off equivalent $n$."
        ),
        "pros_cons": r"General; slightly more bookkeeping than the straight $a_{z,\mathrm{CG}} + r\alpha$ split.",
        "when_to_use": r"3-D motion or when multiple angular components matter.",
    },
    {
        "name": "Full 6-DoF simulation equations",
        "description": r"Solve complete equations for accelerations at stations — unnecessary for this instant.",
        "pros_cons": r"Exact but slow for a timed numeric item.",
        "when_to_use": r"Simulation / verification, not first-pass exam algebra.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "aircraft load factor",
    "pull-up maneuver load factor",
    "load factor rigid body dynamics",
    "pitch angular acceleration load factor",
    "acceleration of a point on a rotating body",
    "vertical load factor fuselage station",
    "maneuver loads aircraft",
    "tangential acceleration pitch acceleration",
]

NEW_PREREQUISITES_ESSENTIAL: List[str] = [
    (
        r"Definition $n = L/W$ and $n = 1 + a_z/g$ for vertical-axis wording used here."
    ),
    (
        r"Rigid-body kinematics: $\mathbf{a}_P = \mathbf{a}_{\mathrm{CG}} + \boldsymbol{\alpha} \times \mathbf{r} "
        r"+ \boldsymbol{\omega} \times (\boldsymbol{\omega} \times \mathbf{r})$."
    ),
    (
        r"Planar specialization: $a_{z,\mathrm{rot}} = r\alpha$ for nose-ahead station in symmetric pull-up."
    ),
    (
        r"Convert degrees to radians for $\alpha$ when using SI meters."
    ),
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
    sbs["approach_type"] = sbs.get("approach_type") or "First Principles Derivation and Direct Formula Application"

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = NEW_PREREQUISITES_ESSENTIAL

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
                "qt": NEW_QUESTION_TEXT,
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

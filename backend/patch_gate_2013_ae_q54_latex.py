"""
Fix GATE_2013_AE_Q54 LaTeX: trim lift coefficient stem, tiers, KaTeX-safe math.

Steady level flight: $L=W$, $C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2013_ae_q54_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2013_AE_Q54"

# Notation: C_{L,\mathrm{trim}} (KaTeX-friendly; avoid C\_{L} broken escapes in plain DB text)
NEW_QUESTION_TEXT_PLAIN = "The airplane trim lift coefficient C_L,trim is"

NEW_QUESTION_TEXT_LATEX = (
    r"The airplane trim lift coefficient $C_{L,\mathrm{trim}}$ is"
)

NEW_OPTIONS: Dict[str, str] = {
    "A": "0.502",
    "B": "0.402",
    "C": "0.302",
    "D": "0.202",
}

NEW_REASONING = (
    r"For steady, level, unaccelerated flight, $L=W$. With "
    r"$L=\tfrac{1}{2}\rho V^2 S C_L$, solve for the trim lift coefficient: "
    r"$C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$."
    "\n\n"
    r"Given $W/S=1000~\mathrm{N/m^2}$, $\rho=1.22~\mathrm{kg/m^3}$, $V=90~\mathrm{m/s}$: "
    r"$\rho V^2=1.22\times 90^2=9882~\mathrm{N/m^2}$ (dynamic-pressure units). "
    r"Then $C_{L,\mathrm{trim}}=\dfrac{2000}{9882}\approx 0.2024$, so the closest option is "
    r"$\mathbf{0.202}$ (D). Aerodynamic-center and zero-lift pitching-moment data are for "
    r"linked trim-moment parts, not this $C_{L,\mathrm{trim}}$ from $L=W$ alone."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Steady level flight: net vertical acceleration is zero, so lift balances weight: $L=W$."
    ),
    (
        r"Lift equation: $L=\tfrac{1}{2}\rho V^2 S C_L$ with true airspeed $V$, reference area $S$, "
        r"and lift coefficient $C_L$."
    ),
    (
        r"At trim in level flight, set $C_L=C_{L,\mathrm{trim}}$ and eliminate $S$ using wing loading "
        r"$W/S$: $C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$."
    ),
    (
        r"Substitute $W/S=1000~\mathrm{N/m^2}$, $\rho=1.22~\mathrm{kg/m^3}$, $V=90~\mathrm{m/s}$."
    ),
    (r"Compute $\rho V^2=1.22\times 8100=9882$."),
    (
        r"Compute $C_{L,\mathrm{trim}}=\dfrac{2\times 1000}{9882}\approx 0.2024$; pick $0.202$ (D)."
    ),
]

NEW_FORMULAS_USED: List[str] = [
    r"$L=W$ (steady, level, unaccelerated flight)",
    r"$L=\tfrac{1}{2}\rho V^2 S C_L$ (lift equation)",
    r"$C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$ (trim $C_L$ from wing loading)",
]

NEW_HINTS: List[str] = [
    (
        r"From $L=W$ and $L=\tfrac{1}{2}\rho V^2 S C_L$, isolate $C_L$ and rewrite $W/S$."
    ),
    (r"Denominator is $\rho V^2$, not $\rho V$—dynamic pressure is $\tfrac{1}{2}\rho V^2$."),
    (r"Use the problem's $\rho$ and $V$ exactly; don't swap in $1.225$ from memory."),
]

NEW_SOLUTION_PATH = (
    r"$L=W$ $\Rightarrow$ $C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$ $\Rightarrow$ substitute numbers"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"$C_{L,\mathrm{trim}}$ from $L=W$ depends only on $W/S$, $\rho$, and $V$—not on $x_{\mathrm{ac}}$ "
        r"or $C_{m0}$."
    ),
    (r"Wing loading $W/S$ removes the need to know $S$ separately."),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Recognize steady cruise implies $L=W$ before reaching for stability formulas.",
    r"Algebra: $C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$ (watch the $V^2$).",
    r"Numeric discipline: use given $\rho=1.22$ and $V=90$.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$",
        "name": r"Trim lift coefficient from wing loading",
        "conditions": [
            r"Steady, level, unaccelerated flight; incompressible lift equation form.",
            r"$W/S$ is weight per reference wing area; $\rho$ and $V$ consistent with $L=\tfrac{1}{2}\rho V^2 S C_L$.",
        ],
        "type": "equation",
        "relevance": r"Directly gives $C_{L,\mathrm{trim}}$ when only wing loading is supplied.",
    },
    {
        "formula": r"$L=\tfrac{1}{2}\rho V^2 S C_L$",
        "name": r"Lift equation",
        "conditions": [
            r"Incompressible / low Mach; $\rho$ uniform; $S$ is reference area.",
        ],
        "type": "equation",
        "relevance": r"Starting point to relate weight, speed, and $C_L$.",
    },
    {
        "formula": r"$L=W$",
        "name": r"Level-flight vertical equilibrium",
        "conditions": [r"No vertical acceleration; horizontal flight path."],
        "type": "principle",
        "relevance": r"Sets trim lift equal to weight for this item.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            r"Using $\rho V$ instead of $\rho V^2$ in the denominator (omitting the square on $V$)."
        ),
        "why_students_make_it": (
            r"Misreading dynamic pressure or rushing the lift equation $L=\tfrac{1}{2}\rho V^2 S C_L$."
        ),
        "type": "Calculation",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            r"Write $L=\tfrac{1}{2}\rho V^2 S C_L$ and circle $V^2$ before substituting."
        ),
        "consequence": r"Inflates $C_L$ by $\sim V$; often lands near option A ($\approx 0.502$).",
    },
    {
        "mistake": r"Substituting a memorized $\rho$ (e.g.\ $1.225$) instead of the given $1.22$.",
        "why_students_make_it": r"Automatic sea-level habit without re-reading the problem.",
        "type": "Units",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Use only the stated $\rho$, $V$, and $W/S$.",
        "consequence": r"Shifts the numeric answer toward B or C.",
    },
    {
        "mistake": (
            r"Dragging $x_{\mathrm{ac}}$, $C_{m0}$, or elevator trim relations into the $C_L$ calculation."
        ),
        "why_students_make_it": r"Linked-question extras look mandatory but are for moment trim, not $L=W$.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"For $C_{L,\mathrm{trim}}$ here, stop at force balance $L=W$.",
        "consequence": r"Wasted time or wrong formula path.",
    },
    {
        "mistake": r"Confusing $W/S$ with total weight $W$ alone.",
        "why_students_make_it": r"Unclear definition of wing loading.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "rare",
        "how_to_avoid": r"$W/S$ is already force per unit area—plug into $\dfrac{2(W/S)}{\rho V^2}$.",
        "consequence": r"Dead ends or inconsistent units.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": r"Must attempt: one formula, two multiplies and a divide.",
    "triage_tip": (
        r"Level cruise $\Rightarrow$ $L=W$ $\Rightarrow$ "
        r"$C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$."
    ),
    "guessing_heuristic": (
        r"If you used $\rho V$ by mistake, expect $\sim 0.5$ (A). Correct denominator $\rho V^2$ is "
        r"larger, so $C_L$ is the smallest listed ($\approx 0.2$, D)."
    ),
    "time_management": r"Target under 2–3 minutes; re-check $V^2$ once.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": (
            r"Trim lift coefficient $C_{L,\mathrm{trim}}$ for level flight given $W/S$, $\rho$, $V$?"
        ),
        "back": (
            r"$C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$ from $L=W$ and "
            r"$L=\tfrac{1}{2}\rho V^2 S C_L$."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "concept_recall",
        "front": r"What force balance defines $C_{L,\mathrm{trim}}$ in unaccelerated level flight?",
        "back": r"$L=W$ at the operating $C_L$ (here, $C_{L,\mathrm{trim}}$).",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Common algebra slip when eliminating $S$ from the lift equation?",
        "back": (
            r"Keep $V^2$: $C_{L,\mathrm{trim}}=\dfrac{2(W/S)}{\rho V^2}$, not $\dfrac{2(W/S)}{\rho V}$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "definition",
        "front": r"Define wing loading and its SI units.",
        "back": r"$W/S$ is weight per reference wing area; SI: $\mathrm{N/m^2}$.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": (
            r"Given $W/S=1500~\mathrm{N/m^2}$, $\rho=1.2~\mathrm{kg/m^3}$, $V=100~\mathrm{m/s}$, "
            r"find $C_{L,\mathrm{trim}}$."
        ),
        "back": (
            r"$C_{L,\mathrm{trim}}=\dfrac{3000}{1.2\times 10^4}=0.25$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
]

NEW_REAL_WORLD_CONTEXT: List[Dict[str, str]] = [
    {
        "application": "Aircraft cruise performance and fuel efficiency",
        "industry_example": (
            r"Example: wing loading $\sim 6000~\mathrm{N/m^2}$ on a narrow-body jet; at cruise "
            r"$\rho\approx 0.4~\mathrm{kg/m^3}$ and $V\approx 230~\mathrm{m/s}$, "
            r"$C_{L,\mathrm{trim}}\sim 0.5$ is typical near best $L/D$."
        ),
        "why_it_matters": (
            r"Operating near the intended $C_{L,\mathrm{trim}}$ reduces excess drag and fuel burn; "
            r"mismatches force climb/descent or higher workload."
        ),
    },
    {
        "application": "Flight test and certification",
        "industry_example": (
            r"Engineers measure trim $C_L$ across weights and speeds to validate performance models."
        ),
        "why_it_matters": (
            r"Reliable $C_{L,\mathrm{trim}}$ data feed POHs, autopilot schedules, and safety margins."
        ),
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"LEWLF: Lift Equals Weight in Level Flight.",
        "concept": r"Start every cruise $C_L$ item with $L=W$.",
        "effectiveness": "high",
        "context": r"Trim / performance MCQs.",
    },
    {
        "mnemonic": r"$C_L\sim \dfrac{W/S}{q}$ with $q=\tfrac{1}{2}\rho V^2$ (here doubled to $2(W/S)/(\rho V^2)$).",
        "concept": r"Link wing loading to dynamic pressure.",
        "effectiveness": "medium",
        "context": r"Remember factor of 2 from $L=\tfrac{1}{2}\rho V^2 S C_L$.",
    },
    {
        "mnemonic": r"Square $V$ before you share (divide).",
        "concept": r"Denominator uses $V^2$, not $V$.",
        "effectiveness": "high",
        "context": r"Lift-coefficient numeric traps.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "trim lift coefficient GATE",
    "C_L trim wing loading",
    "steady level flight L equals W",
    "lift equation rho V squared",
    "aircraft cruise trim C_L",
    "GATE AE aircraft performance",
    "dynamic pressure wing loading",
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": r"Explicit wing area",
        "description": (
            r"If $S$ and $W$ are given separately, $C_{L,\mathrm{trim}}=\dfrac{2W}{\rho V^2 S}$—same as "
            r"using $W/S$."
        ),
        "pros_cons": r"Same physics; pick the form that matches the data.",
        "when_to_use": r"When area and weight are listed instead of wing loading.",
    },
    {
        "name": r"Solve from dynamic pressure",
        "description": (
            r"Let $q=\tfrac{1}{2}\rho V^2$. Then $C_{L,\mathrm{trim}}=\dfrac{W/S}{q}=\dfrac{2(W/S)}{\rho V^2}$."
        ),
        "pros_cons": r"Reinforces $q$ definition; one extra mental step.",
        "when_to_use": r"If you think naturally in dynamic pressure.",
    },
]

NEW_DEEPER_DIVE: List[str] = [
    r"Altitude: lower $\rho$ raises $C_{L,\mathrm{trim}}$ for fixed $V$ and $W/S$.",
    r"Drag polar: cruise often occurs near $C_L$ for favorable $L/D$.",
    r"Stick-fixed vs.\ stick-free trim: hinge moments affect forces felt, not $C_{L,\mathrm{trim}}$ from $L=W$ alone.",
    r"CG location changes elevator deflection for trim, not $C_{L,\mathrm{trim}}$ from vertical force balance.",
]


def _merge_unique(a: List[str], b: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for x in a + b:
        k = x.strip()
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = "D"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["approach_type"] = sbs.get("approach_type") or "Direct formula application"

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
    t2["real_world_context"] = NEW_REAL_WORLD_CONTEXT
    # Remove misplaced nested blobs (canonical tier_3 / tier_4 live in their columns)
    t2.pop("tier_3_enhanced_learning", None)
    t2.pop("tier_4_metadata_and_future", None)
    return t2


def patch_tier_3(tier_3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t3 = deepcopy(tier_3 or {})
    old_kw = list(t3.get("search_keywords") or [])
    t3["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, old_kw)
    t3["alternative_methods"] = NEW_ALTERNATIVE_METHODS
    t3["deeper_dive_topics"] = NEW_DEEPER_DIVE

    conn = dict(t3.get("connections_to_other_subjects") or {})
    conn.update(
        {
            "Aerodynamics": (
                r"The lift coefficient $C_L$ comes from airfoil and wing aerodynamics; "
                r"angle of attack sets $C_L$ on the curve."
            ),
            "Aircraft Performance": (
                r"$C_{L,\mathrm{trim}}$ links cruise speed, altitude ($\rho$), and range relations "
                r"(e.g.\ Breguet)."
            ),
            "Stability and Control": (
                r"$C_{L,\mathrm{trim}}$ follows from $L=W$; elevator deflection for trim follows from "
                r"pitching-moment balance (linked items)."
            ),
            "Aircraft Design": (
                r"Choosing $C_{L,\mathrm{trim}}$ drives wing sizing, aspect ratio, and the performance envelope."
            ),
            "Physics (Mechanics)": (
                r"Lift = weight is Newton's first law for unaccelerated level flight."
            ),
        }
    )
    t3["connections_to_other_subjects"] = conn
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

    print(f"Patched {PUBLIC_ID}: stem/options/tier-1/2/3 LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

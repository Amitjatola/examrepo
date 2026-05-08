"""
Fix GATE_2023_AE_Q32 LaTeX (NAT): arresting cable, horizontal load factor $n_x=F_x/W$.

Replaces backticks in reasoning, fixes stem wrapped in \\text{...}, normalizes formulas_used,
hints, flashcards, mnemonics, tier-3 alternative_methods.

Typical figure: $\\alpha=10^\\circ$, $W=40\\ \\mathrm{kN}$, $T=100\\ \\mathrm{kN}$ $\\Rightarrow$
$F_x=T\\cos\\alpha$, $n_x\\approx2.46\\rightarrow2.5$ (one decimal); band **2.4 to 2.6**.

Usage (from backend/):
  ./venv/bin/python patch_gate_2023_ae_q32_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q32"

NEW_QUESTION_TEXT = (
    "An airplane weighing 40 kN is landing on a horizontal runway during which it is retarded by an arresting "
    "cable mechanism. The tension in the arresting cable at a given instant, as shown in the figure, is 100 kN. "
    "The cable makes an angle of 10° with the horizontal. Assuming that the thrust from the engine continues to "
    "balance airplane drag, the magnitude of horizontal load factor is \\_\\_\\_\\_\\_\\_\\_\\_\\_. "
    "(round off to one decimal place)"
)

# Single math atoms use ~ between number and unit (avoid splitting "40" and "kN" across spans).
# Blank: \underline{\hspace{...}} — avoid \text{\_\_\_\_} (shows raw / fragile in KaTeX). No **markdown** here:
# LatexRenderer passes prose through ReactMarkdown but math-heavy stems render cleaner without **.
NEW_QUESTION_TEXT_LATEX = (
    "An airplane weighing $W=40~\\mathrm{kN}$ lands on a horizontal runway while an arresting cable retards it. "
    "At the instant shown in the figure, the cable tension is $T=100~\\mathrm{kN}$ and the cable makes an angle "
    "$\\alpha=10^\\circ$ with the horizontal. Engine thrust balances aerodynamic drag. "
    "The magnitude of the horizontal load factor is $\\underline{\\hspace{3.5em}}$ "
    "(dimensionless; round off to one decimal place)."
)

NEW_REASONING = (
    "Given: $W=40~\\mathrm{kN}$, $T=100~\\mathrm{kN}$, $\\alpha=10^\\circ$. "
    "Thrust balances drag $\\Rightarrow$ no net horizontal force from propulsion/aero along the runway; "
    "the only horizontal retardation comes from the cable.\n\n"
    "Horizontal cable force:\n"
    "$$F_{x}=T\\cos\\alpha=100~\\mathrm{kN}\\times\\cos 10^\\circ\\approx 98.48~\\mathrm{kN}.$$\n\n"
    "Horizontal load factor (ratio of horizontal resultant to weight):\n"
    "$$n_x=\\frac{F_x}{W}=\\frac{T\\cos\\alpha}{W}\\approx\\frac{98.48}{40}=2.462.$$\n\n"
    "Rounded to one decimal place, $n_x\\approx 2.5$, consistent with the acceptable numeric band 2.4 to 2.6."
)

NEW_HINTS = [
    "From “thrust balances drag”: net horizontal force along the runway is only $T\\cos\\alpha$ (no $T\\sin$ mix-up).",
    "Horizontal load factor: $n_x=F_x/W=(T\\cos\\alpha)/W$ — dimensionless; keep kN/kN consistent.",
    "Use $\\cos 10^\\circ\\approx 0.985$; round only the final $n_x$ to one decimal.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: Parse: $W=40~\\mathrm{kN}$, $T=100~\\mathrm{kN}$, $\\alpha=10^\\circ$; thrust $=$ drag $\\Rightarrow$ "
        "no extra horizontal push/pull from propulsion/drag along the runway."
    ),
    (
        "Step 2: Resolve tension: horizontal component along the runway is $F_x=T\\cos\\alpha$ "
        "(angle measured from horizontal)."
    ),
    (
        "Step 3: Evaluate: $F_x=100\\cos 10^\\circ~\\mathrm{kN}\\approx 98.48~\\mathrm{kN}$."
    ),
    (
        "Step 4: Define horizontal load factor $n_x=F_x/W$ (same as $a_x/g$ when $F_x=ma_x$, $W=mg$)."
    ),
    (
        "Step 5: Compute $n_x\\approx 98.48/40=2.462$."
    ),
    (
        "Step 6: Round one decimal: $n_x\\approx 2.5$."
    ),
]

NEW_FORMULAS_USED = [
    r"$F_x=T\cos\alpha$",
    r"$n_x=\dfrac{F_x}{W}=\dfrac{T\cos\alpha}{W}$",
    r"$n_x=a_x/g$",
    r"$W=mg$",
]

NEW_SOLUTION_PATH = (
    "Thrust=drag $\\Rightarrow F_x=T\\cos\\alpha$ only $\\Rightarrow n_x=(T\\cos\\alpha)/W\\approx2.5$."
)

NEW_KEY_INSIGHTS = [
    "$\\cos\\alpha$ attaches to the horizontal piece when $\\alpha$ is measured from horizontal.",
    "Load factor is a force ratio $F/W$ in the axis of interest — here, horizontal.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    "Interpreting thrust balances drag so horizontal dynamics reduce to the cable’s horizontal component only.",
    "Resolving tension: use $F_x=T\\cos\\alpha$ (not $T\\sin\\alpha$) when $\\alpha$ is measured from the horizontal.",
    "Applying $n_x=F_x/W$ (dimensionless) and one-decimal rounding.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$F_x=T\cos\alpha$",
        "name": "Horizontal component of cable tension",
        "conditions": r"$\alpha$ measured from horizontal; tension magnitude $T$.",
        "type": "equation",
        "relevance": "Retarding force along the runway during arrested landing.",
    },
    {
        "formula": r"$n_x=F_x/W=a_x/g$",
        "name": "Horizontal load factor",
        "conditions": r"Weight $W=mg$; horizontal resultant $F_x$.",
        "type": "equation",
        "relevance": "Defines $n_x$ used in the answer.",
    },
    {
        "formula": r"$F=ma$, $W=mg$",
        "name": "Newton's second law and weight",
        "conditions": "Point-mass idealization along runway.",
        "type": "principle",
        "relevance": "Links force ratio to $a_x/g$.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            "Using $T\\sin\\alpha$ instead of $T\\cos\\alpha$ for the horizontal component when $\\alpha$ is "
            "measured from the horizontal."
        ),
        "why_students_make_it": "Mixing sine/cosine roles or skipping a clear free-body sketch.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            "Label $\\alpha$ from horizontal; horizontal piece is $T\\cos\\alpha$, vertical is $T\\sin\\alpha$."
        ),
        "consequence": r"Forces like $\dfrac{100\sin 10^\circ}{40}\approx0.43$ — far from the correct $n_x$.",
    },
    {
        "mistake": (
            "Ignoring “thrust balances drag” and dragging extra horizontal thrust/drag terms into $F_x$."
        ),
        "why_students_make_it": "Over-modeling instead of reading the problem’s equilibrium statement.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": "When thrust equals drag, their net along the runway is zero — omit both from $F_x$.",
        "consequence": "Adds bogus terms and corrupts $n_x$.",
    },
    {
        "mistake": "Confusing horizontal load factor with normal load factor or mishandling kN vs N.",
        "why_students_make_it": "Sloppy units or thinking “load factor” always means $L/W$.",
        "type": "Units",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Use $n_x=F_x/W$ with consistent force units; $n_x$ is dimensionless.",
        "consequence": "Answers off by orders of magnitude if N and kN are mixed.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Must Attempt",
    "triage_tip": (
        "List $W,T,\\alpha$; note thrust=drag $\\Rightarrow F_x=T\\cos\\alpha$ only; compute "
        "$n_x=(T\\cos\\alpha)/W$; round one decimal."
    ),
    "guessing_heuristic": (
        "$n_x$ should be order-one here (not 0.05); bound using $\\cos 10^\\circ\\approx 1$ "
        "$\\Rightarrow n_x\\approx 100/40=2.5$."
    ),
    "time_management": "About 2–4 minutes: one trig factor and one ratio.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "definition",
        "front": "Define horizontal load factor $n_x$.",
        "back": (
            "$n_x=F_x/W=a_x/g$: horizontal resultant divided by weight (dimensionless)."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": "Horizontal component of tension $T$ at angle $\\alpha$ from horizontal?",
        "back": "$F_x=T\\cos\\alpha$. (Vertical piece is $T\\sin\\alpha$.)",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Thrust balances drag — effect on horizontal balance?",
        "back": (
            "Net horizontal thrust+drag $\\approx 0$ along the runway; do not add them into $F_x$ for this setup."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application",
        "front": "$W=40~\\mathrm{kN}$, $T=100~\\mathrm{kN}$, $\\alpha=10^\\circ$, thrust=drag. Find $n_x$.",
        "back": (
            "$n_x=\\dfrac{T\\cos\\alpha}{W}=\\dfrac{100\\cos 10^\\circ}{40}\\approx 2.46\\Rightarrow 2.5$ (one decimal)."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "concept_recall",
        "front": "Why does thrust=drag simplify this problem?",
        "back": "Horizontal aerodynamic/propulsive resultant along runway is ~0; retardation comes from cable tension only.",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": "Cosine for horizontal when $\\alpha$ is measured from horizontal: $F_x=T\\cos\\alpha$.",
        "concept": "Trig resolution for cable tension.",
        "effectiveness": "high",
        "context": "Arrested landing / inclined cable pull.",
    },
    {
        "mnemonic": "$n_x=F_x/W$: horizontal force over weight.",
        "concept": "Load factor as a ratio of collinear resultant to weight.",
        "effectiveness": "medium",
        "context": "Remember axis: horizontal vs vertical load factors differ.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "D'Alembert / pseudo-static balance",
        "description": (
            "Write $T\\cos\\alpha - ma_x=0$ with $m=W/g$, so $a_x=(T\\cos\\alpha)/m$ and "
            "$n_x=a_x/g=(T\\cos\\alpha)/W$ — same result."
        ),
        "pros_cons": "Same arithmetic; extra rename of $ma_x$ as inertia force.",
        "when_to_use": "If you prefer equilibrium wording with an inertia term.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "horizontal load factor",
    "arresting cable aircraft",
    "arrested landing",
    "T cos alpha",
    "load factor definition",
    "GATE AE flight mechanics",
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
    t3["search_keywords"] = NEW_SEARCH_KEYWORDS
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

    print(f"Patched {PUBLIC_ID}: NAT stem/tier-1/2/3 LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

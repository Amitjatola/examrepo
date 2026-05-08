"""
Fix GATE_2021_AE_Q54 LaTeX across stem, tier-1/2/3.

Steady level @ V_max: $T_{\max}=D$. Elliptic wing $\Rightarrow e=1$, 
$C_{D,i}=C_L^2/(\pi e AR)$, $C_D=C_{D_0}+C_{D,i}$, $D=q S C_D$.
NAT band $9787$–$9795$; computed $T_{\max}\approx 9790.65~\mathrm{N}$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2021_ae_q54_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2021_AE_Q54"

NEW_QUESTION_TEXT_LATEX = (
    "A jet aircraft weighing $10{,}000~\mathrm{kg}$ has an elliptic wing with span $b = 10~\mathrm{m}$ "
    "and area $S = 30~\mathrm{m^2}$. The zero-lift drag coefficient is $C_{D_0} = 0.025$. "
    "The maximum speed in steady level flight at sea level is $V_{\max} = 100~\mathrm{m/s}$. "
    "Air density is $\\rho = 1.225~\mathrm{kg/m^3}$ and $g = 10~\mathrm{m/s^2}$. "
    "The maximum thrust developed by the engine at sea level is $\\underline{\\hspace{3.5em}}~\mathrm{N}$ "
    "(round off to two decimal places)."
)


def _plain_question_text_no_inline_math() -> str:
    """Some surfaces render only question_text without math — avoid stray `$`."""
    return (
        "A jet aircraft weighing 10,000 kg has an elliptic wing with a span of 10 m and area 30 m². "
        "The zero-lift drag coefficient C_D0 is 0.025. The maximum speed of the aircraft in steady "
        "level flight at sea level is 100 m/s. The density of air at sea level is 1.225 kg/m³, and take "
        "g = 10 m/s². The maximum thrust developed by the engine at sea level is ______ N "
        "(round off to two decimal places)."
    )


NEW_QUESTION_TEXT_PLAIN = _plain_question_text_no_inline_math()

NEW_OPTIONS = None

NEW_REASONING = (
    r"At the stated maximum speed in steady level flight, thrust balances drag: $T_{\max}=D$. "
    r"Weight $W=mg=10{,}000~\mathrm{kg}\times 10~\mathrm{m/s^2}=10^5~\mathrm{N}$. "
    r"Aspect ratio $\mathrm{AR}=b^2/S=10^2/30=10/3$."
    "\n\n"
    r"Dynamic pressure $q=\tfrac{1}{2}\rho V_{\max}^2=\tfrac{1}{2}(1.225)(100)^2=6125~\mathrm{Pa}$."
    "\n\n"
    r"Level flight: $L=W$, hence $C_L=\dfrac{W}{qS}=\dfrac{10^5}{6125\times 30}\approx 0.544218$."
    "\n\n"
    r"Elliptic wing: Oswald efficiency $e=1$, so "
    r"$C_{D,i}=\dfrac{C_L^2}{\pi e\,\mathrm{AR}}\approx 0.028282$."
    "\n\n"
    r"Total drag coefficient $C_D=C_{D_0}+C_{D,i}\approx 0.025+0.028282=0.053282$."
    "\n\n"
    r"Drag $D=q S C_D\approx 6125\times 30\times 0.053282\approx 9790.65~\mathrm{N}$."
    "\n\n"
    r"Hence $T_{\max}\approx 9790.65~\mathrm{N}$ (within $9787$–$9795~\mathrm{N}$)."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Given $m=10{,}000~\mathrm{kg}$, $g=10~\mathrm{m/s^2}$: "
        r"$W=mg=10^5~\mathrm{N}$; level flight implies $L=W$."
    ),
    (
        r"Compute $q=\tfrac{1}{2}\rho V_{\max}^2$ with $\rho=1.225~\mathrm{kg/m^3}$, "
        r"$V_{\max}=100~\mathrm{m/s}$ $\Rightarrow$ $q=6125~\mathrm{Pa}$."
    ),
    (
        r"Lift coefficient: $C_L=\dfrac{W}{qS}$ with $S=30~\mathrm{m^2}$ "
        r"$\Rightarrow$ $C_L\approx 0.544218$."
    ),
    (r"Aspect ratio: $\mathrm{AR}=\dfrac{b^2}{S}=\dfrac{100}{30}=\dfrac{10}{3}$."),
    (
        r"Induced drag (elliptic wing, $e=1$): "
        r"$C_{D,i}=\dfrac{C_L^2}{\pi e\,\mathrm{AR}}$."
    ),
    (r"Total drag coefficient: $C_D=C_{D_0}+C_{D,i}$ with $C_{D_0}=0.025$."),
    (
        r"Drag force $D=q S C_D$; steady level at $V_{\max}$ gives $T_{\max}=D\approx 9790.65~\mathrm{N}$ "
        r"(two decimals)."
    ),
]

NEW_FORMULAS_USED: List[str] = [
    r"$W = mg$",
    r"$q = \tfrac{1}{2}\rho V^2$",
    r"$\mathrm{AR} = b^2/S$",
    r"$C_L = \dfrac{W}{qS}$ (level flight, $L=W$)",
    r"$C_{D,i} = \dfrac{C_L^2}{\pi e\,\mathrm{AR}}$",
    r"$C_D = C_{D_0} + C_{D,i}$",
    r"$D = q S C_D$",
    r"$T = D$ (level flight)",
]

NEW_HINTS: List[str] = [
    (
        r"At the given $V_{\max}$, equilibrium gives $T=D$; do not assume minimum-drag speed unless stated."
    ),
    (
        r"Elliptic wing in textbook/GATE context: use $e=1$ in $C_{D,i}=C_L^2/(\pi e\,\mathrm{AR})$."
    ),
    (
        r"Use the stated $g=10~\mathrm{m/s^2}$ for weight (not $9.81$)."
    ),
]

NEW_SOLUTION_PATH = (
    r"$W$ $\rightarrow$ $q$ $\rightarrow$ $C_L$ $\rightarrow$ $\mathrm{AR}$ $\rightarrow$ $C_{D,i}$ "
    r"$\rightarrow$ $C_D$ $\rightarrow$ $D=T_{\max}$"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"At maximum sustainable level speed (for the quoted thrust limit), $T_{\mathrm{avail}}=D_{\mathrm{req}}$; "
        r"here that operating point is given by $V_{\max}$."
    ),
    r"Elliptic loading implies $e=1$, simplifying induced drag.",
    r"Drag polar: $C_D=C_{D_0}+C_{D,i}$ always includes induced term when $C_L>0$.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Chains $q$, $C_L$, $\mathrm{AR}$, and $C_{D,i}$ without skipping steps.",
    r"Must apply $e=1$ for an ideal elliptic wing in induced-drag formulas.",
    r"Must use problem-specific $g=10~\mathrm{m/s^2}$ exactly as stated.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$L=W=\tfrac{1}{2}\rho V^2 S C_L$",
        "name": "Lift in steady level flight",
        "conditions": [r"Unaccelerated longitudinal flight; lift balances weight."],
        "type": "equation",
        "relevance": r"Relates $C_L$ to weight once $q$ and $S$ are known.",
    },
    {
        "formula": r"$C_{D,i}=\dfrac{C_L^2}{\pi e\,\mathrm{AR}}$",
        "name": "Induced drag coefficient (lifting-line form)",
        "conditions": [
            r"Elliptic spanwise loading; for stated elliptic wing take $e=1$.",
        ],
        "type": "equation",
        "relevance": r"Adds lift-dependent drag to $C_{D_0}$.",
    },
    {
        "formula": r"$C_D = C_{D_0} + C_{D,i}$",
        "name": "Drag polar (split)",
        "conditions": [r"Parasite drag plus induced drag for this modeling level."],
        "type": "equation",
        "relevance": r"Forms total $C_D$ used in $D=qSC_D$.",
    },
    {
        "formula": r"$D=\tfrac{1}{2}\rho V^2 S C_D = q S C_D$",
        "name": "Drag force",
        "conditions": [r"Incompressible, steady flow at the flight condition."],
        "type": "equation",
        "relevance": r"Equals required thrust in steady level flight.",
    },
    {
        "formula": r"$\mathrm{AR}=b^2/S$",
        "name": "Aspect ratio",
        "conditions": [r"Rectangular/standard definition from span and reference area."],
        "type": "equation",
        "relevance": r"Feeds induced drag magnitude.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": r"Using $C_D=C_{D_0}$ only and ignoring $C_{D,i}$.",
        "why_students_make_it": r"Treating drag as purely parasite drag.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Always add induced term when $C_L>0$: $C_D=C_{D_0}+C_{D,i}$.",
        "consequence": r"Thrust estimate far too low.",
    },
    {
        "mistake": r"Using $\mathrm{AR}=b/S$ instead of $\mathrm{AR}=b^2/S$.",
        "why_students_make_it": r"Mixing span with span-squared.",
        "type": "Calculation",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Write $\mathrm{AR}=b^2/S$ before substituting numbers.",
        "consequence": r"Wrong $C_{D,i}$ and wrong thrust.",
    },
    {
        "mistake": r"Taking $e\neq 1$ for an elliptic wing without justification.",
        "why_students_make_it": r"Defaulting to typical transport-airplane $e\approx 0.85$–$0.95$.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"If the stem says elliptic wing, use $e=1$ unless another value is given.",
        "consequence": r"Small shift in $C_{D,i}$ and final thrust.",
    },
    {
        "mistake": r"Using $g=9.81~\mathrm{m/s^2}$ when the problem specifies $g=10~\mathrm{m/s^2}$.",
        "why_students_make_it": r"Habit / autopilot with standard gravity.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "common",
        "how_to_avoid": r"Use exactly the constants printed in the statement.",
        "consequence": r"Different $W$, hence different $C_L$ and thrust; may leave the official band.",
    },
    {
        "mistake": (
            r"Assuming level-flight maximum speed occurs at minimum-drag conditions rather than using the "
            r"given $V_{\max}$."
        ),
        "why_students_make_it": r"Confusing extrema of drag curve with a fixed-speed equilibrium statement.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "rare",
        "how_to_avoid": (
            r"If $V_{\max}$ is given, compute $q$, $C_L$, and drag at that speed; do not substitute "
            r"$C_L$ from $D_{\min}$ unless asked."
        ),
        "consequence": r"Inconsistent $C_L$ and thrust.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Strong candidate if equilibrium + drag polar are familiar.",
    "triage_tip": (
        r"Level flight $\Rightarrow$ $L=W$, $T=D$. Build $q\to C_L\to \mathrm{AR}\to C_{D,i}\to C_D\to D$."
    ),
    "guessing_heuristic": (
        r"Order-of-magnitude: $q\sim 6\times 10^3~\mathrm{Pa}$, $S=30~\mathrm{m^2}$, $C_D\sim 0.05$ "
        r"$\Rightarrow$ $D\sim 9\times 10^3~\mathrm{N}$."
    ),
    "time_management": r"About 2–3 minutes; bail after 4 minutes if still stuck on induced term.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"What is the split drag polar used here?",
        "back": (
            r"$C_D=C_{D_0}+C_{D,i}$ with $C_{D,i}=\dfrac{C_L^2}{\pi e\,\mathrm{AR}}$; elliptic wing $\Rightarrow$ "
            r"$e=1$."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"In steady level flight, how do thrust and drag relate?",
        "back": r"$T=D$ and $L=W$ (unaccelerated flight in the longitudinal vertical plane).",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "calculation",
        "front": (
            r"If $L=10^5~\mathrm{N}$, $q=6000~\mathrm{Pa}$, $S=30~\mathrm{m^2}$, find $C_L$."
        ),
        "back": r"$C_L=\dfrac{L}{qS}=\dfrac{10^5}{180000}\approx 0.5556$.",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"What term is most often dropped in this thrust-at-speed setup?",
        "back": (
            r"$C_{D,i}$. Without it you effectively set $C_D=C_{D_0}$, underestimating drag and thrust."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "definition",
        "front": r"Define aspect ratio $\mathrm{AR}$.",
        "back": r"$\mathrm{AR}=b^2/S$ (span squared over reference wing area).",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Elliptic wing: $e=1$ for induced drag bookkeeping.",
        "concept": r"Oswald efficiency on textbook elliptic loading",
        "effectiveness": "high",
        "context": r"Induced drag coefficient formulas.",
    },
    {
        "mnemonic": r"$\mathrm{AR}=b^2/S$: span squared over area.",
        "concept": r"Aspect ratio",
        "effectiveness": "medium",
        "context": r"Geometry given $b$ and $S$.",
    },
    {
        "mnemonic": r"$C_D=C_{D_0}+C_L^2/(\pi e\,\mathrm{AR})$",
        "concept": r"Drag polar composition",
        "effectiveness": "high",
        "context": r"Performance calculations with induced drag.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Equivalent $C_L$ from lift equation, then $D=qSC_D$",
        "description": (
            r"Same pipeline: compute $C_L$ from $W=qSC_L$, then $C_{D,i}$, then $D$ — algebraically identical "
            r"rearrangements."
        ),
        "pros_cons": r"Useful if you prefer eliminating $q$ early.",
        "when_to_use": r"Verification.",
    },
    {
        "name": "Numerical integration / tabulated polar",
        "description": (
            r"If $C_D(C_L)$ were tabulated non-parabolically, interpolate — overkill for this closed-form item."
        ),
        "pros_cons": r"Flexible; slower.",
        "when_to_use": r"Non-parabolic provided data (not this problem).",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "elliptic wing Oswald efficiency",
    "induced drag coefficient lifting line",
    "steady level flight thrust equals drag",
    "dynamic pressure lift coefficient",
    "aspect ratio formula",
    "drag polar C_D0 induced",
    "GATE AE aircraft performance",
    "maximum speed equilibrium thrust",
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = r"$\approx 9790.65~\mathrm{N}$ (official band: 9787 to 9795)"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["approach_type"] = sbs.get("approach_type") or "Equilibrium + drag polar"

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = [
        r"Steady level flight: $L=W$, $T=D$.",
        r"Dynamic pressure $q=\tfrac{1}{2}\rho V^2$ and lift coefficient $C_L=W/(qS)$ when $L=W$.",
        r"Aspect ratio $\mathrm{AR}=b^2/S$.",
        r"Induced drag: $C_{D,i}=C_L^2/(\pi e\,\mathrm{AR})$; elliptic wing $\Rightarrow$ $e=1$.",
        r"Total drag $D=qSC_D$ with $C_D=C_{D_0}+C_{D,i}$.",
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

"""
Fix GATE_2019_AE_Q43 LaTeX across stem, tier-1/2/3.

Propeller endurance (Breguet): 
$E=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}\left(\dfrac{1}{\sqrt{W_1}}-\dfrac{1}{\sqrt{W_0}}\right)$
with $c$ from $0.76~\mathrm{kg/(kW\cdot hr)}$. Fuel weight $W_f=W_0-W_1$.
NAT band $1440$–$1490$; computed $W_f\approx 1477~\mathrm{N}$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2019_ae_q43_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q43"

NEW_QUESTION_TEXT_PLAIN = (
    "A propeller-driven airplane has a gross take-off weight of 4905 N with a wing area of 6.84 m². "
    "Assume that the wings are operating at the maximum C_L^(3/2)/C_D ratio of 13, the propeller efficiency "
    "is 0.9, and the specific fuel consumption of the engine is 0.76 kg/(kW·hr). Given that the density of "
    "air at sea level is 1.225 kg/m³ and the acceleration due to gravity is 9.81 m/s², the weight of the fuel "
    "required for an endurance of 18 hours at sea level is ______ N (round off to the nearest integer)."
)

NEW_QUESTION_TEXT_LATEX = (
    "A propeller-driven airplane has gross take-off weight $W_0 = 4905~\mathrm{N}$ and wing area "
    "$S = 6.84~\mathrm{m^2}$. The wings operate at maximum "
    r"$\dfrac{C_L^{3/2}}{C_D} = 13$. Propeller efficiency is $\eta = 0.9$ and specific fuel consumption is "
    r"$0.76~\mathrm{kg/(kW\cdot hr)}$. Sea-level air density is $\rho = 1.225~\mathrm{kg/m^3}$ and "
    r"$g = 9.81~\mathrm{m/s^2}$. The fuel weight required for endurance $E = 18~\mathrm{hr}$ at sea level is "
    r"$\underline{\hspace{3.5em}}~\mathrm{N}$ (round off to the nearest integer)."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"For a propeller aircraft in steady level flight at constant $\rho$, flying at the endurance optimum fixes "
    r"$\dfrac{C_L^{3/2}}{C_D}$ (maximum for this polar). With weight-specific fuel consumption $c$ "
    r"(consistent SI), the Breguet endurance relation used here is"
    "\n\n"
    r"$E=\dfrac{\eta}{c}\,\dfrac{C_L^{3/2}}{C_D}\,\sqrt{2\rho S}\left(\dfrac{1}{\sqrt{W_1}}-\dfrac{1}{\sqrt{W_0}}\right)$,"
    "\n\n"
    r"where $W_0$ is initial weight and $W_1$ is final weight after burning fuel."
    "\n\n"
    r"Given: $W_0=4905~\mathrm{N}$, $S=6.84~\mathrm{m^2}$, $\rho=1.225~\mathrm{kg/m^3}$, $\eta=0.9$, "
    r"$\dfrac{C_L^{3/2}}{C_D}=13$, $g=9.81~\mathrm{m/s^2}$, mass-specific consumption "
    r"$c_m=0.76~\mathrm{kg/(kW\cdot hr)}$, and $E=18~\mathrm{hr}=64800~\mathrm{s}$."
    "\n\n"
    r"Convert $c_m$ to a weight basis per shaft energy: multiply by $g$ for $\mathrm{N}$ per $\mathrm{kW\cdot hr}$, "
    r"then divide by $1~\mathrm{kW\cdot hr}=3.6\times 10^6~\mathrm{N\cdot m}$ to obtain "
    r"$c\approx 2.071\times 10^{-6}~\mathrm{m^{-1}}$ (same grouping as standard textbook substitution)."
    "\n\n"
    r"Compute $\sqrt{2\rho S}\approx 4.0937$, hence "
    r"$A=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}\approx 2.313\times 10^7~\mathrm{s\cdot N^{1/2}}$ "
    r"(equivalently carry the product numerically)."
    "\n\n"
    r"Then $\dfrac{1}{\sqrt{W_1}}=\dfrac{E}{A}+\dfrac{1}{\sqrt{W_0}}$ gives $W_1\approx 3428~\mathrm{N}$, so "
    r"$W_f=W_0-W_1\approx 1477~\mathrm{N}$ (nearest integer), within $1440$–$1490~\mathrm{N}$."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Identify propeller endurance optimum: maximize $\dfrac{C_L^{3/2}}{C_D}$; list "
        r"$W_0,S,\rho,\eta,c_m,g,E$."
    ),
    (
        r"Convert $c_m=0.76~\mathrm{kg/(kW\cdot hr)}$: weight rate per $\mathrm{kW\cdot hr}$ is $c_m g$; "
        r"divide by $3.6\times 10^6~\mathrm{J}$ per $\mathrm{kW\cdot hr}$ to get consistent $c$."
    ),
    (r"Use $E=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}\left(\dfrac{1}{\sqrt{W_1}}-\dfrac{1}{\sqrt{W_0}}\right)$."),
    (
        r"Define $A=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}$ after computing $\sqrt{2\rho S}$."
    ),
    (
        r"Solve $\dfrac{1}{\sqrt{W_1}}=\dfrac{E}{A}+\dfrac{1}{\sqrt{W_0}}$; square to get $W_1$."
    ),
    (r"Fuel weight: $W_f=W_0-W_1$; round to nearest integer."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$E=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}\left(\dfrac{1}{\sqrt{W_1}}-\dfrac{1}{\sqrt{W_0}}\right)$",
    r"$c \approx \dfrac{c_m\, g}{3.6\times 10^{6}}$ (from $\mathrm{kg/(kW\cdot hr)}$ via $\mathrm{N/(kW\cdot hr)}$)",
    r"$W_f = W_0 - W_1$",
    r"$\sqrt{2\rho S}$",
    r"$\dfrac{1}{\sqrt{W_1}} = \dfrac{E}{A}+\dfrac{1}{\sqrt{W_0}}$ with $A=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}$",
]

NEW_HINTS: List[str] = [
    (
        r"Propeller endurance uses $\dfrac{C_L^{3/2}}{C_D}$ (not jet $\dfrac{C_L}{C_D}$) with power-related $c$."
    ),
    (
        r"From $\mathrm{kg/(kW\cdot hr)}$: multiply by $g$, then convert $\mathrm{kW\cdot hr}$ to joules "
        r"($3.6\times 10^6~\mathrm{J}$)."
    ),
    (
        r"Fuel weight is $W_0-W_1$ once $W_1$ comes from the inverse-square-root relation."
    ),
]

NEW_SOLUTION_PATH = (
    r"$c_m\to c$ $\Rightarrow$ assemble $\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}$ "
    r"$\Rightarrow$ solve for $W_1$ $\Rightarrow$ $W_f=W_0-W_1$"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"$c$ must match weight-based bookkeeping with $W$ in newtons; convert mass-SFC with $g$ and $\mathrm{kW\cdot hr}\to\mathrm{J}$."
    ),
    (
        r"As fuel burns, $W$ drops, so $\dfrac{1}{\sqrt{W_1}}>\dfrac{1}{\sqrt{W_0}}$ and the bracket is positive."
    ),
    (
        r"Isolate $\dfrac{1}{\sqrt{W_1}}$ before squaring the reciprocal."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Heavy unit conversion on $c_m$ (kg basis and $\mathrm{kW\cdot hr}$).",
    r"Correct Breguet propeller form with $\dfrac{C_L^{3/2}}{C_D}$.",
    r"Inverting $\dfrac{1}{\sqrt{W}}$ algebra without sign slips.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": (
            r"$E=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}"
            r"\left(\dfrac{1}{\sqrt{W_1}}-\dfrac{1}{\sqrt{W_0}}\right)$"
        ),
        "name": "Breguet endurance (propeller, level cruise modeling)",
        "conditions": [
            r"Level flight; $\eta,c,\rho,S,\dfrac{C_L^{3/2}}{C_D}$ treated constant over the endurance segment.",
        ],
        "type": "equation",
        "relevance": r"Relates endurance to weight loss for propeller aircraft.",
    },
    {
        "formula": r"$c_w = c_m\, g$",
        "name": r"Mass-SFC to weight-SFC (per $\mathrm{kW\cdot hr}$)",
        "conditions": [r"Local $g$ given in the problem statement."],
        "type": "conversion",
        "relevance": r"Links $\mathrm{kg}$ fuel rate to $\mathrm{N}$ fuel rate before dividing by energy.",
    },
    {
        "formula": r"$1~\mathrm{kW\cdot hr}=3.6\times 10^6~\mathrm{J}$",
        "name": "Energy unit conversion",
        "conditions": [r"SI joules for consistent $c$ grouping."],
        "type": "conversion",
        "relevance": r"Required when $c_m$ is quoted per $\mathrm{kW\cdot hr}$.",
    },
    {
        "formula": r"$W_f=W_0-W_1$",
        "name": "Fuel weight from weights",
        "conditions": [r"Weights expressed as forces (newtons)."],
        "type": "equation",
        "relevance": r"Final fuel-weight answer.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": r"Using jet endurance / jet $C_L/C_D$ instead of propeller $\dfrac{C_L^{3/2}}{C_D}$.",
        "why_students_make_it": r"Template mismatch across prop versus jet Breguet forms.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Tag aircraft type first; prop endurance pairs with $\dfrac{C_L^{3/2}}{C_D}$.",
        "consequence": r"Wrong formula $\Rightarrow$ wrong magnitude.",
    },
    {
        "mistake": r"Mishandling $\mathrm{kg/(kW\cdot hr)}$ conversions ($g$, $\mathrm{kW\cdot hr}\to\mathrm{J}$, powers of ten).",
        "why_students_make_it": r"Unit clutter and rushing.",
        "type": "Units",
        "severity": "High",
        "frequency": "very_common",
        "how_to_avoid": r"Track dimensions explicitly: $\mathrm{N}$, $\mathrm{J}$, seconds.",
        "consequence": r"Answers off by $\sim 9.81$, $3600$, or $10^6$ factors.",
    },
    {
        "mistake": r"Algebra slip isolating $\dfrac{1}{\sqrt{W_1}}$.",
        "why_students_make_it": r"Inverting/squaring steps done out of order.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Solve linearly for $\dfrac{1}{\sqrt{W_1}}$, then square.",
        "consequence": r"Nonphysical $W_1$ or fuel weight.",
    },
    {
        "mistake": r"Flipping $\dfrac{1}{\sqrt{W_1}}-\dfrac{1}{\sqrt{W_0}}$ sign.",
        "why_students_make_it": r"Forgetting $W_1<W_0$ after fuel burn.",
        "type": "Sign Error",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Sanity check: bracket must be positive for positive endurance.",
        "consequence": r"Negative endurance or nonsense weights.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "High value if you recognize prop Breguet + unit path.",
    "triage_tip": (
        r"Prop + endurance $\Rightarrow$ $\dfrac{C_L^{3/2}}{C_D}$ Breguet; budget time for $c_m$ conversion."
    ),
    "guessing_heuristic": (
        r"Fuel weight often a sizable fraction of $W_0$ for multi-hour endurance; expect $\mathcal{O}(10^3)~\mathrm{N}$ here."
    ),
    "time_management": r"About 4–5 minutes including careful unit conversion.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"Write the propeller Breguet endurance relation used for constant $\dfrac{C_L^{3/2}}{C_D}$.",
        "back": (
            r"$E=\dfrac{\eta}{c}\dfrac{C_L^{3/2}}{C_D}\sqrt{2\rho S}"
            r"\left(\dfrac{1}{\sqrt{W_1}}-\dfrac{1}{\sqrt{W_0}}\right)$"
        ),
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "concept_recall",
        "front": r"What ratio is maximized for propeller endurance in this modeling?",
        "back": r"Maximize $\dfrac{C_L^{3/2}}{C_D}$ (minimum power required side of the story).",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "units",
        "front": (
            r"Convert $c_m=0.76~\mathrm{kg/(kW\cdot hr)}$ toward SI grouping using $g=9.81~\mathrm{m/s^2}$ "
            r"and $1~\mathrm{kW\cdot hr}=3.6\times 10^6~\mathrm{J}$."
        ),
        "back": (
            r"$c_m g\approx 7.4556~\mathrm{N/(kW\cdot hr)}$; "
            r"$c=\dfrac{c_m g}{3.6\times 10^6}\approx 2.071\times 10^{-6}~\mathrm{m^{-1}}$."
        ),
        "difficulty": "hard",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Common unit/bookkeeping traps in this endurance calculation?",
        "back": (
            r"Mass vs weight ($g$), hours vs seconds, and $\mathrm{kW\cdot hr}\to\mathrm{J}$."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Jet vs propeller: what fuel-consumption descriptor pairs with which Breguet form?",
        "back": (
            r"Propeller models use shaft-power–related consumption; jet models use thrust-specific consumption—do not swap."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 60,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Prop endurance: $\dfrac{C_L^{3/2}}{C_D}$ inside Breguet (not $L/D$ alone).",
        "concept": r"Propeller vs jet endurance optima",
        "effectiveness": "high",
        "context": r"Breguet template selection.",
    },
    {
        "mnemonic": r"$c_m\to c$: multiply by $g$, divide joules per $\mathrm{kW\cdot hr}$.",
        "concept": r"SFC conversion",
        "effectiveness": "medium",
        "context": r"kg basis SFC to consistent $c$.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Derive from $\mathrm{d}W/\mathrm{d}t$ with power required",
        "description": (
            r"Start from fuel burn rate proportional to shaft power, use $P_{\mathrm{req}}=DV$, "
            r"$L=W$, and integrate between $W_0$ and $W_1$ — arrives at the same closed form under the stated assumptions."
        ),
        "pros_cons": r"Conceptually revealing; slower on exam day.",
        "when_to_use": r"Studying / verification.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "Breguet endurance propeller aircraft",
    "C_L^{3/2}/C_D maximum endurance",
    "specific fuel consumption kg per kW hr conversion",
    "propeller efficiency endurance",
    "fuel weight from endurance formula",
    "GATE AE flight mechanics endurance",
    "inverse square root weight Breguet",
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = r"$\approx 1477~\mathrm{N}$ (official band: 1440 to 1490)"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["approach_type"] = sbs.get("approach_type") or "Standard Breguet substitution"

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = [
        r"Breguet endurance forms for propeller vs jet aircraft.",
        r"Specific fuel consumption definitions and conversions ($\mathrm{kg}$, $\mathrm{kW\cdot hr}$, $\mathrm{J}$).",
        r"Steady level flight: $L=W$, $T=D$.",
        r"Algebra with $\dfrac{1}{\sqrt{W}}$ terms.",
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

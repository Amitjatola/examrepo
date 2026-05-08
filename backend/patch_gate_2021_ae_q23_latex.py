"""
Fix GATE_2021_AE_Q23 LaTeX across stem, tier-1/2/3.

Jet endurance (steady level): fly at $(L/D)_{\max}$ for parabolic polar
$C_D=C_{D_0}+K C_L^2 \Rightarrow C_L=\sqrt{C_{D_0}/K}$; then
$V=\sqrt{2(W/S)/(\rho C_L)}$. NAT band $64.30$–$64.60$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2021_ae_q23_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2021_AE_Q23"

NEW_QUESTION_TEXT = (
    "A jet aircraft has the following specifications: wing loading = 1800 N/m², wing area = 30 m², "
    "drag polar C_D = 0.02 + 0.04 C_L², and C_L,max = 1.6. Take density of air at sea level as "
    "1.225 kg/m³. The speed at which the aircraft achieves maximum endurance in steady level flight at sea "
    "level is ______ m/s (round off to two decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    "A jet aircraft has the following specifications: wing loading $(W/S) = 1800~\\mathrm{N/m^2}$, "
    "wing area $S = 30~\\mathrm{m^2}$, drag polar $C_D = 0.02 + 0.04 C_L^2$, and $C_{L,\\max} = 1.6$. "
    "Take density of air at sea level as $\\rho = 1.225~\\mathrm{kg/m^3}$. The speed at which the aircraft "
    "achieves maximum endurance in steady level flight at sea level is $\\underline{\\hspace{3.5em}}~\\mathrm{m/s}$ "
    "(round off to two decimal places)."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"For a jet in steady level flight, maximum endurance occurs at minimum thrust required, i.e.\ when "
    r"$L/D = C_L/C_D$ is maximized. With a parabolic polar $C_D = C_{D_0} + K C_L^2$, setting "
    r"$\mathrm{d}(L/D)/\mathrm{d}C_L = 0$ gives $C_{D_0} = K C_L^2$, hence "
    r"$C_L = \sqrt{C_{D_0}/K}$."
    "\n\n"
    r"Given $C_D = 0.02 + 0.04 C_L^2$: $C_{D_0}=0.02$, $K=0.04$. Wing loading $W/S = 1800~\mathrm{N/m^2}$, "
    r"$\rho = 1.225~\mathrm{kg/m^3}$."
    "\n\n"
    r"1. Optimum lift coefficient: "
    r"$C_L = \sqrt{C_{D_0}/K} = \sqrt{0.02/0.04} = \sqrt{1/2} \approx 0.70711$. "
    r"This satisfies $C_L < C_{L,\max}=1.6$."
    "\n\n"
    r"2. Level flight: $L=W$. From $L=\tfrac{1}{2}\rho V^2 S C_L$, divide by $S$: "
    r"$W/S = \tfrac{1}{2}\rho V^2 C_L$, so $V = \sqrt{\dfrac{2(W/S)}{\rho C_L}}$."
    "\n\n"
    r"3. Substitute: "
    r"$V = \sqrt{\dfrac{2\times 1800}{1.225\times C_L}} "
    r"= \sqrt{\dfrac{3600}{1.225\sqrt{1/2}}} \approx 64.47~\mathrm{m/s}$."
    "\n\n"
    r"Rounded to two decimal places: $V \approx 64.47~\mathrm{m/s}$, within $64.30$–$64.60~\mathrm{m/s}$."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Jet endurance (steady level): minimize thrust $\Rightarrow$ maximize $L/D \Rightarrow$ fly at "
        r"$C_L=\sqrt{C_{D_0}/K}$ for $C_D=C_{D_0}+K C_L^2$."
    ),
    (
        r"Read off $C_{D_0}=0.02$, $K=0.04$; then $C_L=\sqrt{0.02/0.04}=\sqrt{1/2}\approx 0.70711$. "
        r"Check $C_L < C_{L,\max}=1.6$."
    ),
    (
        r"Use wing loading directly: $W/S=\tfrac{1}{2}\rho V^2 C_L \Rightarrow "
        r"V=\sqrt{2(W/S)/(\rho C_L)}$."
    ),
    (
        r"Insert $(W/S)=1800~\mathrm{N/m^2}$, $\rho=1.225~\mathrm{kg/m^3}$, $C_L\approx 0.70711$: "
        r"$V\approx 64.47~\mathrm{m/s}$."
    ),
    (r"Round to two decimals: $64.47~\mathrm{m/s}$."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$C_D = C_{D_0} + K C_L^2$",
    r"$C_L = \sqrt{C_{D_0}/K}$ at $(L/D)_{\max}$ for a parabolic polar",
    r"$L = \tfrac{1}{2}\rho V^2 S C_L$",
    r"$W/S = \tfrac{1}{2}\rho V^2 C_L$",
    r"$V = \sqrt{\dfrac{2(W/S)}{\rho C_L}}$",
]

NEW_HINTS: List[str] = [
    (
        r"Jet endurance $\neq$ propeller endurance: jets fly max endurance at $(L/D)_{\max}$, "
        r"not at max $C_L^{3/2}/C_D$."
    ),
    (
        r"For $C_D=C_{D_0}+K C_L^2$, maximize $C_L/C_D$ gives $C_{D_0}=K C_L^2$ "
        r"$\Rightarrow$ $C_L=\sqrt{C_{D_0}/K}$."
    ),
    (
        r"Avoid computing $W$ unless needed: $W/S$ plugs straight into "
        r"$V=\sqrt{2(W/S)/(\rho C_L)}$."
    ),
]

NEW_SOLUTION_PATH = (
    r"Max endurance (jet, level) $\Rightarrow$ $(L/D)_{\max}$ $\Rightarrow$ "
    r"$C_L=\sqrt{C_{D_0}/K}$ $\Rightarrow$ $V=\sqrt{2(W/S)/(\rho C_L)}$."
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"Jet max endurance aligns with min drag / max $L/D$ in steady level flight (not the propeller "
        r"$C_L^{3/2}/C_D$ rule)."
    ),
    (
        r"Parabolic polar optimum: $C_{D_0} = K C_L^2$ at $(L/D)_{\max}$."
    ),
    (
        r"Given $W/S$, use $V=\sqrt{2(W/S)/(\rho C_L)}$ without forming $W$ explicitly."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    (
        r"Must recall jet endurance $\leftrightarrow$ $(L/D)_{\max}$ and not confuse with range or "
        r"propeller criteria."
    ),
    (
        r"Must derive or remember $C_L=\sqrt{C_{D_0}/K}$ from $C_D=C_{D_0}+K C_L^2$."
    ),
    (
        r"Numerical trap: mix-ups with units ($W/S$, $\rho$) or using $C_{L,\max}$ instead of optimum $C_L$."
    ),
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$C_D = C_{D_0} + K C_L^2$",
        "name": "Parabolic drag polar",
        "conditions": [
            r"Subsonic cruise where parasite + induced drag dominate; $C_{D_0}$ and $K$ treated as constants.",
        ],
        "type": "equation",
        "relevance": r"Defines $C_{D_0}$ and $K$ used to find optimum $C_L$.",
    },
    {
        "formula": r"$C_L = \sqrt{C_{D_0}/K}$",
        "name": r"$(L/D)_{\max}$ lift coefficient (parabolic polar)",
        "conditions": [
            r"Maximize $C_L/(C_{D_0}+K C_L^2)$ w.r.t.\ $C_L$; equivalently $C_{D_0}=K C_L^2$ at the optimum.",
        ],
        "type": "equation",
        "relevance": r"Sets the operating $C_L$ for jet max endurance in level flight (minimum thrust).",
    },
    {
        "formula": r"$L=\tfrac{1}{2}\rho V^2 S C_L$",
        "name": "Lift equation",
        "conditions": [
            r"Incompressible, quasi-steady level flight with lift aligned with weight.",
        ],
        "type": "equation",
        "relevance": r"Solves $V$ once $C_L$ and wing loading are known.",
    },
    {
        "formula": r"$V=\sqrt{\dfrac{2(W/S)}{\rho C_L}}$",
        "name": r"Speed from wing loading (level flight)",
        "conditions": [
            r"$L=W$ so $(W/S)=\tfrac{1}{2}\rho V^2 C_L$.",
        ],
        "type": "equation",
        "relevance": r"Direct NAT computation without separately calculating aircraft weight.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            r"Using propeller endurance ($\max C_L^{3/2}/C_D$) or jet-range heuristics instead of jet endurance "
            r"($(L/D)_{\max}$)."
        ),
        "why_students_make_it": r"Similar-looking performance topics blur together without a decision checklist.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            r"Memorize: jet endurance level $\Rightarrow$ $(L/D)_{\max}$; prop endurance $\Rightarrow$ "
            r"$C_L^{3/2}/C_D$ (typical textbook contrast)."
        ),
        "consequence": r"Wrong $C_L$, hence wrong $V$.",
    },
    {
        "mistake": (
            r"Using $C_L = C_{D_0}/K$ instead of $C_L = \sqrt{C_{D_0}/K}$."
        ),
        "why_students_make_it": r"Algebra slip when recalling the optimum condition.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": (
            r"Derive once: maximize $C_L/(C_{D_0}+K C_L^2)$ $\Rightarrow$ $C_{D_0}=K C_L^2$."
        ),
        "consequence": r"$C_L$ wrong by $\sqrt{\cdot}$ factor $\Rightarrow$ large $V$ error.",
    },
    {
        "mistake": r"Unit inconsistency (mass vs weight, or wrong density area units).",
        "why_students_make_it": r"Mixing kg with N or omitting SI prefixes.",
        "type": "Units",
        "severity": "Medium",
        "frequency": "common",
        "how_to_avoid": (
            r"Keep $W/S$ in $\mathrm{N/m^2}$, $\rho$ in $\mathrm{kg/m^3}$, $C_L$ dimensionless; track squareroot units."
        ),
        "consequence": r"Answer scaled by $\sqrt{g}$ or similar.",
    },
    {
        "mistake": r"Misreading wing loading as total weight.",
        "why_students_make_it": r"Vocabulary: $W/S$ vs $W$.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"If needed: $W=(W/S)\cdot S$, but prefer $V=\sqrt{2(W/S)/(\rho C_L)}$ directly.",
        "consequence": r"Incorrect substitution into the lift relation.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Must attempt if performance basics are fresh.",
    "triage_tip": (
        r"Tag “jet + endurance + level” $\Rightarrow$ $(L/D)_{\max}$ $\Rightarrow$ "
        r"$C_L=\sqrt{C_{D_0}/K}$ $\Rightarrow$ $V=\sqrt{2(W/S)/(\rho C_L)}$."
    ),
    "guessing_heuristic": (
        r"Ballpark: $C_L\approx 1/\sqrt{2}\approx 0.707$ gives $V\sim \sqrt{3600/0.866}\sim 64~\mathrm{m/s}$."
    ),
    "time_management": r"About 2–3 minutes; if stuck after selecting $C_L$, skip and return.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "concept_recall",
        "front": r"What condition maximizes endurance for a jet in steady level flight?",
        "back": (
            r"Minimum thrust required $\Leftrightarrow$ maximum $L/D$. With a parabolic polar, fly at $C_L$ giving "
            r"$(L/D)_{\max}$."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": r"For $C_D=C_{D_0}+K C_L^2$, what is $C_L$ at $(L/D)_{\max}$?",
        "back": r"$C_L=\sqrt{C_{D_0}/K}$ (equivalently $C_{D_0}=K C_L^2$ at the optimum).",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application",
        "front": (
            r"Given wing loading $(W/S)=1800~\mathrm{N/m^2}$ and $S=30~\mathrm{m^2}$, what is weight $W$?"
        ),
        "back": r"$W=(W/S)\cdot S=1800\times 30=54000~\mathrm{N}$.",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"How does jet endurance differ from typical propeller endurance (same level-flight modeling)?",
        "back": (
            r"Jet (min thrust): optimize $L/D$. Propeller endurance often ties to maximizing "
            r"$C_L^{3/2}/C_D$ (power/thrust bookkeeping differs)."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 40,
    },
    {
        "card_type": "calculation",
        "front": (
            r"Compute $V$ for max endurance using $\rho=1.225~\mathrm{kg/m^3}$, $(W/S)=1800~\mathrm{N/m^2}$, "
            r"$C_L=\sqrt{1/2}$."
        ),
        "back": (
            r"$V=\sqrt{2(W/S)/(\rho C_L)}=\sqrt{3600/(1.225\sqrt{1/2})}\approx 64.47~\mathrm{m/s}$."
        ),
        "difficulty": "hard",
        "time_limit_seconds": 60,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Jet endurance: max $L/D$ (minimum thrust).",
        "concept": r"Jet vs propeller endurance distinction",
        "effectiveness": "high",
        "context": r"Level-flight performance MCQs / NATs.",
    },
    {
        "mnemonic": r"$C_{D_0}=K C_L^2$ at the $(L/D)_{\max}$ corner on a parabolic polar.",
        "concept": r"Optimality condition",
        "effectiveness": "medium",
        "context": r"Deriving $C_L=\sqrt{C_{D_0}/K}$.",
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Graphical $L/D$ vs $C_L$",
        "description": (
            r"Plot $C_L/(C_{D_0}+K C_L^2)$ vs $C_L$ (or read $(L/D)_{\max}$ from a drag polar sketch), pick optimum "
            r"$C_L$, then compute $V$ from wing loading."
        ),
        "pros_cons": r"Builds intuition; slower than the closed form.",
        "when_to_use": r"Verification or non-parabolic polars.",
    },
    {
        "name": r"Calculus on $C_L/(C_{D_0}+K C_L^2)$",
        "description": (
            r"Differentiate $L/D$ with respect to $C_L$, set to zero, obtain $C_{D_0}=K C_L^2$, then solve $V$."
        ),
        "pros_cons": r"First-principles; takes slightly longer.",
        "when_to_use": r"If you forget $C_L=\sqrt{C_{D_0}/K}$.",
    },
    {
        "name": "Numerical sweep",
        "description": (
            r"Evaluate $V(C_L)=\sqrt{2(W/S)/(\rho C_L)}$ together with drag/thrust bookkeeping across $C_L$ grid "
            r"near the optimum — unnecessary here."
        ),
        "pros_cons": r"Robust but slow.",
        "when_to_use": r"Sanity-check only.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "jet aircraft maximum endurance",
    "maximum lift-to-drag ratio parabolic drag polar",
    "C_L optimum sqrt(C_D0/K)",
    "wing loading steady level flight velocity",
    "GATE AE aircraft performance endurance",
    "minimum thrust required jet endurance",
    "endurance vs range jet propeller",
    "lift equation wing loading form",
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = r"$\approx 64.47~\mathrm{m/s}$ (within $64.30$–$64.60$)"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["approach_type"] = sbs.get("approach_type") or "Standard Performance Relations"

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = [
        r"Steady level flight: $L=W$, $T=D$.",
        r"Parabolic polar: $C_D=C_{D_0}+K C_L^2$.",
        r"Lift equation: $L=\tfrac{1}{2}\rho V^2 S C_L$.",
        r"$(L/D)=C_L/C_D$; jet endurance (level) ties to $(L/D)_{\max}$ for min thrust.",
        r"Wing loading: $W/S$; hence $V=\sqrt{2(W/S)/(\rho C_L)}$ when $C_L$ is known.",
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

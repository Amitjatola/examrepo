"""
Fix GATE_2019_AE_Q19 LaTeX: EAS from TAS via dynamic-pressure scaling.

$q=\tfrac{1}{2}\rho V^2$ at altitude equals $\tfrac{1}{2}\rho_{\mathrm{SL}}V_{\mathrm{EAS}}^2$
$\\Rightarrow$ $V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\rho/\rho_{\mathrm{SL}}}$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2019_ae_q19_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q19"

NEW_QUESTION_TEXT_PLAIN = (
    "An airplane is in steady level flight with a true airspeed of 50 m/s. "
    "The ambient air density and ambient pressure at the flight altitude are "
    "0.91 kg/m³ and 7×10⁴ N/m², respectively. At sea level, air density is "
    "1.225 kg/m³ and ambient pressure is 1.01×10⁵ N/m². "
    "The equivalent or indicated airspeed of the airplane is ______ m/s (round off to 2 decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    r"An airplane is in steady level flight with true airspeed $V_{\mathrm{TAS}}=50~\mathrm{m/s}$. "
    r"At flight altitude, $\rho=0.91~\mathrm{kg/m^3}$ and $p=7\times 10^{4}~\mathrm{N/m^2}$. "
    r"At sea level, $\rho_{\mathrm{SL}}=1.225~\mathrm{kg/m^3}$ and $p_{\mathrm{SL}}=1.01\times 10^{5}~\mathrm{N/m^2}$. "
    r"The equivalent or indicated airspeed is $V_{\mathrm{EAS}}=\underline{\hspace{3.5em}}~\mathrm{m/s}$ "
    r"(round off to 2 decimal places)."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"Equivalent airspeed $V_{\mathrm{EAS}}$ is the sea-level speed that gives the same dynamic pressure "
    r"as the actual flight condition: "
    r"$\tfrac{1}{2}\rho V_{\mathrm{TAS}}^2=\tfrac{1}{2}\rho_{\mathrm{SL}}V_{\mathrm{EAS}}^2$, hence "
    r"$V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\rho/\rho_{\mathrm{SL}}}$."
    "\n\n"
    r"Given $V_{\mathrm{TAS}}=50~\mathrm{m/s}$, $\rho=0.91~\mathrm{kg/m^3}$, "
    r"$\rho_{\mathrm{SL}}=1.225~\mathrm{kg/m^3}$:"
    "\n"
    r"$\sqrt{\rho/\rho_{\mathrm{SL}}}=\sqrt{0.91/1.225}\approx 0.86189$, so "
    r"$V_{\mathrm{EAS}}\approx 50\times 0.86189=43.0945~\mathrm{m/s}$."
    "\n\n"
    r"Rounded to two decimals: $43.09~\mathrm{m/s}$. "
    r"The stated pressures are consistent with the densities but are not needed for this "
    r"incompressible scaling once $\rho$ and $\rho_{\mathrm{SL}}$ are given."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Given $V_{\mathrm{TAS}}=50~\mathrm{m/s}$, $\rho=0.91~\mathrm{kg/m^3}$, "
        r"$\rho_{\mathrm{SL}}=1.225~\mathrm{kg/m^3}$."
    ),
    (
        r"Match dynamic pressures: $\tfrac{1}{2}\rho V_{\mathrm{TAS}}^2="
        r"\tfrac{1}{2}\rho_{\mathrm{SL}}V_{\mathrm{EAS}}^2$."
    ),
    (
        r"Solve: $V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\rho/\rho_{\mathrm{SL}}}$."
    ),
    (r"Compute $\rho/\rho_{\mathrm{SL}}=0.91/1.225\approx 0.742857$."),
    (r"$\sqrt{\rho/\rho_{\mathrm{SL}}}\approx 0.86189$."),
    (r"$V_{\mathrm{EAS}}\approx 50\times 0.86189=43.0945~\mathrm{m/s}$."),
    (r"Round: $43.09~\mathrm{m/s}$."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$q=\tfrac{1}{2}\rho V^2$",
    r"$V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\dfrac{\rho}{\rho_{\mathrm{SL}}}}}$",
]

NEW_HINTS: List[str] = [
    (
        r"EAS follows from equal dynamic pressure: scale $V$ by $\sqrt{\rho/\rho_{\mathrm{SL}}}$."
    ),
    (
        r"You only need $\rho$ at altitude and $\rho_{\mathrm{SL}}$—not $p$ directly for this shortcut."
    ),
    (
        r"At altitude, $\rho<\rho_{\mathrm{SL}}$ so $V_{\mathrm{EAS}}<V_{\mathrm{TAS}}$ when $q$ is matched."
    ),
]

NEW_SOLUTION_PATH = (
    r"$q_{\mathrm{alt}}=q_{\mathrm{SL}}$ $\Rightarrow$ "
    r"$V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\rho/\rho_{\mathrm{SL}}}$ $\Rightarrow$ numeric"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"IAS/EAS concepts tie to pitot–static sensing through dynamic pressure; here densities are given "
        r"explicitly."
    ),
    (
        r"Always check $V_{\mathrm{EAS}}<V_{\mathrm{TAS}}$ when flying above sea level in ISA-like thinning air."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Recognize the governing relation is dynamic pressure, not ambient pressure alone.",
    r"Apply the square root from $V^2\propto 1/\rho$ at fixed $q$.",
    r"Avoid inverting $\rho/\rho_{\mathrm{SL}}$.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\dfrac{\rho}{\rho_{\mathrm{SL}}}}}$",
        "name": r"EAS from TAS (incompressible / low Mach)",
        "conditions": [
            r"$\rho$ is actual density; $\rho_{\mathrm{SL}}$ is reference sea-level density (here $1.225~\mathrm{kg/m^3}$).",
            r"Compressibility neglected (standard GATE framing unless stated otherwise).",
        ],
        "type": "equation",
        "relevance": r"Directly computes $V_{\mathrm{EAS}}$ from $V_{\mathrm{TAS}}$.",
    },
    {
        "formula": r"$q=\tfrac{1}{2}\rho V^2$",
        "name": r"Dynamic pressure",
        "conditions": [r"Incompressible Bernoulli/Pitot framework."],
        "type": "equation",
        "relevance": r"Explains why $V_{\mathrm{EAS}}$ scales with $\sqrt{\rho}$.",
    },
    {
        "formula": r"$\rho=\dfrac{p}{RT}$",
        "name": r"Ideal gas (dry air)",
        "conditions": [r"Use when $\rho$ must be inferred from $p$ and $T$."],
        "type": "equation",
        "relevance": r"Background only—$\rho$ is given explicitly here.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": r"Inverting the density ratio: $\sqrt{\rho_{\mathrm{SL}}/\rho}$ instead of $\sqrt{\rho/\rho_{\mathrm{SL}}}$.",
        "why_students_make_it": r"Direction confusion between TAS and EAS magnitude.",
        "type": "Formula recall",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            r"Physical check: at altitude $\rho<\rho_{\mathrm{SL}}$ implies $V_{\mathrm{EAS}}<V_{\mathrm{TAS}}$ "
            r"for the same $q$."
        ),
        "consequence": r"$V_{\mathrm{EAS}}>V_{\mathrm{TAS}}$ (impossible for this setup).",
    },
    {
        "mistake": r"Dropping the square root (using linear $\rho/\rho_{\mathrm{SL}}$ scaling).",
        "why_students_make_it": r"Forgetting $q\propto V^2$.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Derive once from $\rho V_{\mathrm{TAS}}^2=\rho_{\mathrm{SL}}V_{\mathrm{EAS}}^2$.",
        "consequence": r"Noticeably wrong magnitude.",
    },
    {
        "mistake": r"Using pressure ratio $p/p_{\mathrm{SL}}$ instead of density ratio.",
        "why_students_make_it": r"Mixing ideal-gas steps when $\rho$ is already supplied.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Use $\rho$ directly for $q=\tfrac{1}{2}\rho V^2$.",
        "consequence": r"Wrong answer unless temperature/humidity assumptions accidentally align.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": r"High-yield: one square root and one multiply.",
    "triage_tip": (
        r"TAS + densities $\Rightarrow$ $V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\rho/\rho_{\mathrm{SL}}}$."
    ),
    "guessing_heuristic": (
        r"$V_{\mathrm{EAS}}$ must be below $50~\mathrm{m/s}$ here since $\rho<\rho_{\mathrm{SL}}$."
    ),
    "time_management": r"About 1–2 minutes including rounding.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "definition",
        "front": r"Define equivalent airspeed $V_{\mathrm{EAS}}$.",
        "back": (
            r"Sea-level speed in ISA giving the same dynamic pressure as the actual $(\rho,V)$ condition."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": r"Relate $V_{\mathrm{EAS}}$ and $V_{\mathrm{TAS}}$ at low Mach.",
        "back": r"$V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\rho/\rho_{\mathrm{SL}}}$.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Why is $V_{\mathrm{EAS}}<V_{\mathrm{TAS}}$ in this problem?",
        "back": r"Lower $\rho$ at altitude means a smaller speed at SL matches the same $q$.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application",
        "front": (
            r"$V_{\mathrm{TAS}}=200~\mathrm{m/s}$, $\rho=0.6~\mathrm{kg/m^3}$, $\rho_{\mathrm{SL}}=1.225~\mathrm{kg/m^3}$. "
            r"Find $V_{\mathrm{EAS}}$."
        ),
        "back": (
            r"$V_{\mathrm{EAS}}=200\sqrt{0.6/1.225}\approx 139.98~\mathrm{m/s}$."
        ),
        "difficulty": "hard",
        "time_limit_seconds": 90,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Same $q$: scale $V$ by $\sqrt{\rho}$ relative to SL.",
        "concept": r"Dynamic-pressure equivalence.",
        "effectiveness": "high",
        "context": r"TAS/EAS conversions.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "GATE 2019 AE equivalent airspeed TAS",
    "EAS TAS sqrt density ratio",
    "dynamic pressure sea level",
]

NEW_CONNECTIONS: Dict[str, str] = {
    "Fluid mechanics": (
        r"Bernoulli/Pitot–static theory links measured pressures to $q$ and calibrated speeds."
    ),
    "Thermodynamics": (
        r"Ideal gas connects $p$, $\rho$, $T$ when density is not tabulated."
    ),
    "Flight mechanics": (
        r"Performance charts and stall speeds are often referenced to EAS/CAS."
    ),
}

NEW_DEEPER_DIVE: List[str] = [
    r"CAS/EAS/Mach: compressibility corrections at higher speeds.",
    r"IAS position error and pitot/static instrument corrections.",
    r"Humidity and non-standard atmosphere effects on $\rho$.",
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Dynamic Pressure First Principles",
        "description": (
            r"Start from $q=\tfrac{1}{2}\rho V_{\mathrm{TAS}}^2=\tfrac{1}{2}\rho_{\mathrm{SL}}V_{\mathrm{EAS}}^2$, "
            r"cancel $\tfrac{1}{2}$, and take the positive root to obtain "
            r"$V_{\mathrm{EAS}}=V_{\mathrm{TAS}}\sqrt{\rho/\rho_{\mathrm{SL}}}$."
        ),
        "pros_cons": (
            "Pros: Conceptually rigorous, reinforces understanding of dynamic pressure equality. "
            "Cons: Involves more steps and can be more prone to intermediate rounding errors if not careful."
        ),
        "when_to_use": (
            "When deriving the formula, for conceptual understanding, or if given pitot-static pressure "
            "differences or dynamic pressure directly instead of TAS."
        ),
    }
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
    av["correct_answer"] = "43.09"

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
    old_kw = list(t3.get("search_keywords") or [])
    t3["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, old_kw)

    conn = dict(t3.get("connections_to_other_subjects") or {})
    conn.update(NEW_CONNECTIONS)
    t3["connections_to_other_subjects"] = conn

    dd = list(t3.get("deeper_dive_topics") or [])
    t3["deeper_dive_topics"] = _merge_unique(NEW_DEEPER_DIVE, dd)

    t3["alternative_methods"] = NEW_ALTERNATIVE_METHODS

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

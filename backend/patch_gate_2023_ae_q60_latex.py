"""
Fix LaTeX / formatting for GATE_2023_AE_Q60 (corner velocity / max turn rate NAT).

Usage (from backend/):
  PYTHONPATH=. python patch_gate_2023_ae_q60_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q60"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    The maximum permissible load factor is 7 and the maximum lift coefficient is 2.
    Wing loading is 6500 N/m^2 and air density is 1.23 kg/m^3.
    The speed yielding the highest possible turn rate in the vertical plane is ________ m/s (round off to the nearest integer).
    """
).strip()

# Markdown + inline math (LatexRenderer-friendly). NAT: blank as underline placeholder.
NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The maximum permissible load factor is $n_{\max}=7$ and the maximum lift coefficient is $C_{L,\max}=2$.

    Wing loading is $W/S = 6500~\mathrm{N/m^2}$ and air density is $\rho=1.23~\mathrm{kg/m^3}$.

    The speed (in $\mathrm{m/s}$) yielding the **highest possible turn rate** in the **vertical plane** is $\underline{\qquad\qquad}$ (round to the nearest integer).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    For **maximum instantaneous turn rate** in the vertical pull-up, the airplane operates at the **maneuver point** on the $V$–$n$ diagram: both limits are **active** — **structural** $n=n_{\max}$ and **aerodynamic** $C_L=C_{L,\max}$ (**stall / $C_{L,\max}$ boundary**). That speed is the **corner (maneuver) velocity** $V^*$.

    Use load factor $n=L/W$ with the lift equation $L=\tfrac{1}{2}\rho V^2 S C_L$. At the corner,
    $$n_{\max}W=\frac{1}{2}\rho {V^*}^2 S\,C_{L,\max}.$$
    Divide by wing area:
    $$n_{\max}(W/S)=\frac{1}{2}\rho {V^*}^2 C_{L,\max}.$$
    Hence
    $${V^*}^2=\frac{2\,n_{\max}(W/S)}{\rho\,C_{L,\max}},\qquad V^*=\sqrt{\frac{2\,n_{\max}(W/S)}{\rho\,C_{L,\max}}}.$$

    Substitute $n_{\max}=7$, $W/S=6500~\mathrm{N/m^2}$, $\rho=1.23~\mathrm{kg/m^3}$, $C_{L,\max}=2$:
    $${V^*}^2=\frac{2\times7\times6500}{1.23\times2}=\frac{91000}{2.46}\approx36991.87~(\mathrm{m/s})^2,$$
    $$V^*\approx\sqrt{36991.87}\approx192.3~\mathrm{m/s}\;\Rightarrow\;\boxed{192~\mathrm{m/s}}$$
    (nearest integer; consistent with an official band around $190\text{–}195~\mathrm{m/s}$ if rounding policy differs slightly).
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Recognize **corner velocity**: max turn-rate condition uses **both** $n_{\max}$ and $C_{L,\max}$ simultaneously.",
    r"Relate load factor and lift: $n=L/W$ and $L=\tfrac{1}{2}\rho V^2 S C_L$.",
    r"At $V^*$: $n_{\max}W=\tfrac{1}{2}\rho {V^*}^2 S\,C_{L,\max}$.",
    r"Divide by $S$: $n_{\max}(W/S)=\tfrac{1}{2}\rho {V^*}^2 C_{L,\max}$.",
    r"Solve: ${V^*}^2=\dfrac{2\,n_{\max}(W/S)}{\rho\,C_{L,\max}}$.",
    r"Substitute numbers: ${V^*}^2=\dfrac{91000}{2.46}\approx36992~(\mathrm{m/s})^2$.",
    r"$V^*=\sqrt{{V^*}^2}\approx192~\mathrm{m/s}$ (nearest integer).",
]

NEW_FORMULAS_USED = [
    r"$n=\dfrac{L}{W}$",
    r"$L=\dfrac{1}{2}\rho V^2 S C_L$",
    r"$V^*=\sqrt{\dfrac{2\,n_{\max}(W/S)}{\rho\,C_{L,\max}}}$",
    r"${V^*}^2=\dfrac{2\,n_{\max}(W/S)}{\rho\,C_{L,\max}}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Corner (maneuver) velocity",
        "type": "equation",
        "formula": r"$V^*=\sqrt{\dfrac{2\,n_{\max}(W/S)}{\rho\,C_{L,\max}}}$",
        "relevance": r"Speed where stall ($C_{L,\max}$) and structural $n_{\max}$ limits intersect on the $V$–$n$ diagram.",
        "conditions": [r"Simultaneous $n=n_{\max}$ and $C_L=C_{L,\max}$; incompressible model as stated."],
    },
    {
        "name": "Lift equation",
        "type": "equation",
        "formula": r"$L=\dfrac{1}{2}\rho V^2 S C_L$",
        "relevance": r"Links dynamic pressure and $C_L$ to lift for the corner-speed derivation.",
        "conditions": [r"Steady maneuver; use given $\rho$ and $C_{L,\max}$."],
    },
    {
        "name": "Load factor",
        "type": "definition",
        "formula": r"$n=L/W$",
        "relevance": r"Sets $L=nW$ at the structural limit $n_{\max}$.",
        "conditions": [r"Vertical pull-up context as in the stem."],
    },
]

NEW_HINTS = [
    r"Max **instantaneous** turn rate $\Rightarrow$ **corner speed**: both $n_{\max}$ **and** $C_{L,\max}$ are saturated.",
    r"Combine $n_{\max}W=\tfrac{1}{2}\rho V^2 S C_{L,\max}$ then divide by $S$ to use $W/S$ directly.",
    r"Remember the factor **2** from $\tfrac{1}{2}$ in the lift equation when solving for $V^*$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"Corner velocity $V^*$ in terms of $n_{\max}$, $W/S$, $\rho$, and $C_{L,\max}$?",
        "back": r"$V^*=\sqrt{\dfrac{2\,n_{\max}(W/S)}{\rho\,C_{L,\max}}}$ from $n_{\max}(W/S)=\tfrac{1}{2}\rho {V^*}^2 C_{L,\max}$.",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
    {
        "card_type": "concept_recall",
        "front": r"What does the maneuver point on a $V$–$n$ diagram represent?",
        "back": r"Intersection of the **stall / $C_{L,\max}$** boundary and the **limit load** $n_{\max}$ — corner speed.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "definition",
        "front": r"Define wing loading.",
        "back": r"$W/S$: weight per unit wing area; lower $W/S$ generally improves turn capability at a given $C_{L,\max}$ and $n_{\max}$.",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "numerical_calculation",
        "front": r"$n_{\max}=5$, $W/S=5000~\mathrm{N/m^2}$, $\rho=1.2~\mathrm{kg/m^3}$, $C_{L,\max}=1.5$. Corner speed (nearest integer)?",
        "back": r"$V^*=\sqrt{\dfrac{2\times5\times5000}{1.2\times1.5}}=\sqrt{\dfrac{50000}{1.8}}\approx167~\mathrm{m/s}$.",
        "difficulty": "medium",
        "time_limit_seconds": 60,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": r"$V^*=\sqrt{\dfrac{2 n (W/S)}{\rho\,C_{L,\max}}}$",
        "concept": r"“**2** from $\tfrac{1}{2}\rho V^2$” — don't drop the 2",
        "effectiveness": "high",
        "context": r"Corner-velocity algebra",
    },
    {
        "mnemonic": r"“Both maxes at the corner”",
        "concept": r"$n_{\max}$ and $C_{L,\max}$ active together",
        "effectiveness": "high",
        "context": r"$V$–$n$ diagram",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Using level-turn radius/rate formulas instead of the **corner** condition for max **instantaneous** turn rate.",
        "severity": "High",
        "frequency": "common",
        "consequence": r"Wrong speed scale vs. $V^*$.",
        "how_to_avoid": r"Vertical pull-up here still asks for the **same** corner-speed condition: saturate $n_{\max}$ and $C_{L,\max}$.",
        "why_students_make_it": r"Formula soup: different turn equations look similar.",
    },
    {
        "type": "Formula",
        "mistake": r"Missing the factor **2** in $V^*=\sqrt{\dfrac{\,n_{\max}(W/S)}{\rho C_{L,\max}}}$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": r"Answer $\approx V^*/\sqrt{2}$ (too low).",
        "how_to_avoid": r"Derive once from $n_{\max}(W/S)=\tfrac{1}{2}\rho V^2 C_{L,\max}$.",
        "why_students_make_it": r"Memorizing without derivation.",
    },
    {
        "type": "Calculation",
        "mistake": r"Forgetting $\sqrt{\cdot}$ after forming ${V^*}^2$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": r"Absurd magnitude (off by ~$\times V^*$).",
        "how_to_avoid": r"Check dimensions: ${V^*}^2$ is $(\mathrm{m/s})^2$.",
        "why_students_make_it": r"Time pressure.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"If you see max turn rate + $n_{\max}$ + $C_{L,\max}$ + $W/S$ + $\rho$ $\Rightarrow$ **corner** formula $\Rightarrow$ ~2 min.",
    "guessing_heuristic": r"${V^*}^2\sim 9\times10^4/2.5\sim3.7\times10^4$ $\Rightarrow$ $V^*\sim190\text{–}195~\mathrm{m/s}$.",
    "time_management": r"2–3 min: one formula, careful arithmetic, then $\sqrt{\cdot}$ and round.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Must recognize **corner velocity** without naming it in the stem.",
    r"Algebra with $W/S$ and the factor **2** from dynamic pressure.",
    r"Numeric division + square root under time pressure.",
]

NEW_ALT_METHODS = [
    {
        "name": r"Equivalent derivation from $n(V)$",
        "description": r"Write $n(V)=\dfrac{\tfrac{1}{2}\rho V^2 C_{L,\max}}{W/S}\le n_{\max}$; at the maneuver point equality holds $\Rightarrow$ same expression for $V^*$.",
        "pros_cons": r"Pros: reinforces constraints. Cons: slower than direct formula.",
        "when_to_use": r"If you forget $V^*$ but remember $n=L/W$ and the lift equation.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2023 AE Q60 corner velocity",
    "maneuver speed max turn rate",
    "V-n diagram maneuver point",
    "n_max C_L max simultaneous",
]


def _merge_unique(a: List[str], b: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in a + b:
        k = x.strip()
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    o.pop("_recovered_malformed_key", None)
    o.pop("lift", None)  # stray duplicate key if present at root

    av = o.setdefault("answer_validation", {})
    av.pop("lift", None)
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = "192"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    exp["question_nature"] = "Calculation"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["solution_path"] = (
        r"$n_{\max}(W/S)=\tfrac{1}{2}\rho {V^*}^2 C_{L,\max}$ "
        r"$\Rightarrow$ $V^*=\sqrt{2n_{\max}(W/S)/(\rho C_{L,\max})}$ "
        r"$\Rightarrow$ substitute $\Rightarrow$ round"
    )
    sbs["key_insights"] = [
        r"Corner speed: **both** $n_{\max}$ and $C_{L,\max}$ limits active.",
        r"$V^*$ uses wing loading $W/S$ after canceling $S$ from $nW=L$.",
    ]

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    return o


def patch_t2(t2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t2 or {})
    o["flashcards"] = NEW_FLASHCARDS
    o["mnemonics_memory_aids"] = NEW_MNEMONICS
    o["common_mistakes"] = NEW_COMMON_MISTAKES
    o["exam_strategy"] = NEW_EXAM_STRATEGY

    nested = o.get("tier_3_enhanced_learning")
    if isinstance(nested, dict):
        nested = deepcopy(nested)
        nested["alternative_methods"] = NEW_ALT_METHODS
        nested["search_keywords"] = _merge_unique(
            NEW_SEARCH_KEYWORDS, list(nested.get("search_keywords") or [])
        )
        o["tier_3_enhanced_learning"] = nested

    return o


def patch_t3(t3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t3 or {})
    o["alternative_methods"] = NEW_ALT_METHODS
    o["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, list(o.get("search_keywords") or []))

    conn = o.get("connections_to_other_subjects")
    if isinstance(conn, dict):
        conn = deepcopy(conn)
        for k in ("subject_name_1", "subject_name_2", "subject_name_3"):
            conn.pop(k, None)
        aer = conn.get("Aerodynamics")
        if isinstance(aer, str) and "C\\_" in aer:
            conn["Aerodynamics"] = (
                r"The lift equation and $C_{L,\max}$ (stall / angle-of-attack limit) set the aerodynamic "
                r"side of the maneuver boundary, linking turn performance to airfoil and configuration design."
            )
        o["connections_to_other_subjects"] = conn

    return o


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning, options "
                "FROM questions WHERE question_id=:q"
            ),
            {"q": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit("Question not found")

        t1 = patch_t1(row[0])
        t2 = patch_t2(row[1])
        t3 = patch_t3(row[2])
        existing_options = row[3]

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, "
                "options=CAST(:opts AS jsonb), "
                "tier_1_core_research=CAST(:t1 AS jsonb), "
                "tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), "
                "updated_at=:u "
                "WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT_PLAIN,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(existing_options),
                "t1": json.dumps(t1),
                "t2": json.dumps(t2),
                "t3": json.dumps(t3),
                "u": datetime.utcnow(),
                "q": PUBLIC_ID,
            },
        )

    print("patched", PUBLIC_ID)


if __name__ == "__main__":
    asyncio.run(main())

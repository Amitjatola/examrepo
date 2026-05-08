"""
Fix LaTeX / formatting for GATE_2021_AE_Q25 (circular-orbit speed at 250 km, NAT).

Usage (from backend/):
  PYTHONPATH=. python patch_gate_2021_ae_q25_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2021_AE_Q25"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    The velocity required to launch a space shuttle from Earth's surface
    to achieve a circular orbit of altitude 250 km is ______ (round to two decimal places).
    For Earth, Gm_e = 398600.4 km^3/s^2 and surface radius R_0 = 6378.14 km.
    """
).strip()

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The velocity required to launch a space shuttle from Earth's surface
    to achieve a circular orbit of altitude $h=250\ \mathrm{km}$ is
    $\underline{\qquad\qquad}\ \mathrm{km/s}$ (round to two decimal places).

    For Earth, $\mu=Gm_e=398600.4\ \mathrm{km^3/s^2}$ and surface radius
    $R_0=6378.14\ \mathrm{km}$.
    """
).strip()

NEW_REASONING = dedent(
    r"""
    For a circular orbit, orbital speed is
    $$V=\sqrt{\frac{\mu}{r}},$$
    where $\mu=Gm_e$ and $r$ is distance from Earth's center.

    First compute orbital radius:
    $$r=R_0+h=6378.14+250=6628.14\ \mathrm{km}.$$

    Then
    $$V=\sqrt{\frac{398600.4}{6628.14}}
      =\sqrt{60.1378}
      \approx 7.7549\ \mathrm{km/s}.$$

    Rounding to two decimals:
    $$\boxed{V\approx 7.75\ \mathrm{km/s}}.$$

    Hence the answer falls within the accepted NAT range $7.75$ to $7.77\ \mathrm{km/s}$.
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Use circular-orbit speed formula: $V=\sqrt{\mu/r}$.",
    r"Compute orbital radius from Earth's center: $r=R_0+h=6378.14+250=6628.14\ \mathrm{km}$.",
    r"Substitute $\mu=398600.4\ \mathrm{km^3/s^2}$ and $r=6628.14\ \mathrm{km}$.",
    r"Evaluate ratio: $\mu/r\approx 60.1378\ \mathrm{km^2/s^2}$.",
    r"Take square root: $V\approx 7.7549\ \mathrm{km/s}$.",
    r"Round to two decimals: $\boxed{7.75\ \mathrm{km/s}}$.",
]

NEW_FORMULAS_USED = [
    r"$r=R_0+h$",
    r"$V=\sqrt{\dfrac{\mu}{r}}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Circular orbital velocity",
        "type": "equation",
        "formula": r"$V=\sqrt{\dfrac{\mu}{r}}$",
        "relevance": "Gives the speed needed to sustain a circular orbit at radius r.",
        "conditions": ["Two-body central-gravity model, circular orbit."],
    },
    {
        "name": "Orbital radius",
        "type": "equation",
        "formula": r"$r=R_0+h$",
        "relevance": "Converts surface altitude to center-based orbital radius required in velocity formula.",
        "conditions": ["h measured above Earth's surface."],
    },
    {
        "name": "Gravitational parameter",
        "type": "constant",
        "formula": r"$\mu=Gm_e$",
        "relevance": "Earth constant used directly to avoid separate G and m substitutions.",
        "conditions": ["Given numerically in the stem."],
    },
]

NEW_HINTS = [
    r"Use center-based radius: $r=R_0+h$, not $r=h$.",
    r"Because $\mu$ is in $\mathrm{km^3/s^2}$, keep radius in km to get speed in km/s.",
    r"This asks for orbital speed at altitude, not escape speed and not full launch \(\Delta v\) with losses.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "What is the circular orbital velocity formula?",
        "back": r"$V=\sqrt{\mu/r}$, where $\mu=GM$ and r is from Earth's center.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": "How to compute orbital radius from altitude?",
        "back": r"$r=R_0+h$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Common unit trap in this question?",
        "back": r"If $\mu$ is in $\mathrm{km^3/s^2}$, use r in km; then V is in km/s.",
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"Given $\mu=398600.4\ \mathrm{km^3/s^2}$ and $r=6628.14\ \mathrm{km}$, estimate V.",
        "back": r"$V\approx\sqrt{398600.4/6628.14}\approx 7.75\ \mathrm{km/s}$.",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "CORE: Center Orbit Radius = Earth radius + altitude",
        "concept": r"$r=R_0+h$",
        "effectiveness": "high",
        "context": "Radius setup before substitution",
    },
    {
        "mnemonic": "V-root-mu-over-r",
        "concept": r"$V=\sqrt{\mu/r}$",
        "effectiveness": "high",
        "context": "Quick recall for circular orbit speed",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Using altitude directly as radius in $V=\sqrt{\mu/r}$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Grossly incorrect velocity (too high).",
        "how_to_avoid": r"Always compute $r=R_0+h$ explicitly.",
        "why_students_make_it": "Mixing surface altitude with center-based radius.",
    },
    {
        "type": "Units",
        "mistake": "Mixing km and m with the given μ in km^3/s^2.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Order-of-magnitude errors.",
        "how_to_avoid": "Keep all lengths in km here.",
        "why_students_make_it": "Switching formulas from memory without checking units.",
    },
    {
        "type": "Conceptual",
        "mistake": "Computing escape speed or full launch delta-v instead of orbital speed.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Answer shifts toward 9–11 km/s, outside range.",
        "how_to_avoid": "Read the target condition: circular orbit at 250 km altitude.",
        "why_students_make_it": "Misinterpreting 'launch' wording.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"One-formula NAT: compute $r$, apply $V=\sqrt{\mu/r}$, round.",
    "guessing_heuristic": r"LEO speed is around $7.7$–$7.9\ \mathrm{km/s}$; for 250 km, expect near $7.75\ \mathrm{km/s}$.",
    "time_management": "2–3 minutes maximum for this 1-mark numerical.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Radius must be center-based ($R_0+h$).",
    r"Need clean unit consistency with \mu in km^3/s^2.",
    r"Minor rounding sensitivity near the final second decimal.",
]

NEW_ALT_METHODS = [
    {
        "name": "g0-R0 form",
        "description": r"Use $\mu=g_0R_0^2$ and then $V=\sqrt{g_0R_0^2/(R_0+h)}$ with consistent SI conversion.",
        "pros_cons": "Pros: useful when μ not given explicitly. Cons: extra conversions, higher unit-error risk.",
        "when_to_use": "When only g0 and Earth radius are provided.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2021 AE Q25 circular orbit velocity",
    "orbital speed at 250 km",
    "mu over r square root",
    "LEO velocity km/s",
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

    av = o.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = "7.75 km/s"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    exp["question_nature"] = "Calculation"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["solution_path"] = r"Compute $r=R_0+h$ $\Rightarrow$ apply $V=\sqrt{\mu/r}$ $\Rightarrow$ round to 2 decimals"
    sbs["key_insights"] = [
        r"Use center-based radius, not altitude alone.",
        r"With μ in km^3/s^2 and r in km, V comes directly in km/s.",
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
    return o


def patch_t3(t3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t3 or {})
    o["alternative_methods"] = NEW_ALT_METHODS
    o["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, list(o.get("search_keywords") or []))
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
                "options=CAST(:opts AS jsonb), tier_1_core_research=CAST(:t1 AS jsonb), "
                "tier_2_student_learning=CAST(:t2 AS jsonb), tier_3_enhanced_learning=CAST(:t3 AS jsonb), "
                "updated_at=:u WHERE question_id=:q"
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

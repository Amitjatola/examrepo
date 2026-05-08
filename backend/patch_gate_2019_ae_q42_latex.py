"""
Fix LaTeX / formatting for GATE_2019_AE_Q42 (escape delta-v from circular orbit, NAT).

Usage (from backend/):
  PYTHONPATH=. python patch_gate_2019_ae_q42_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q42"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    The product of Earth's mass (M) and the universal gravitational constant (G) is
    GM = 3.986 x 10^14 m^3/s^2. The Earth's radius is 6371 km.
    The minimum velocity increment to be imparted to a spacecraft in a circular orbit
    at altitude 4000 km, so that it exits Earth's gravitational field, is ______ km/s
    (round off to 2 decimal places).
    """
).strip()

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The product of Earth's mass and the universal gravitational constant is
    $$\mu = GM = 3.986\times 10^{14}\ \mathrm{m^3/s^2}.$$
    The Earth's radius is $R_E=6371\ \mathrm{km}$.

    The minimum increment in velocity required for a spacecraft in a circular orbit at
    altitude $h=4000\ \mathrm{km}$ to exit Earth's gravitational field is
    $\underline{\qquad\qquad}\ \mathrm{km/s}$
    (round to 2 decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    For a circular orbit at radius $r$, the speeds are
    $$v_c=\sqrt{\frac{\mu}{r}},\qquad v_e=\sqrt{\frac{2\mu}{r}}=\sqrt{2}\,v_c.$$
    The required impulse from circular orbit to a parabolic escape trajectory at the **same radius** is
    $$\Delta v=v_e-v_c=v_c(\sqrt{2}-1).$$

    First compute orbital radius:
    $$r=R_E+h=(6371+4000)\ \mathrm{km}=10371\ \mathrm{km}=1.0371\times 10^7\ \mathrm{m}.$$

    Circular speed:
    $$v_c=\sqrt{\frac{3.986\times10^{14}}{1.0371\times10^7}}
      \approx 6199.5\ \mathrm{m/s}=6.1995\ \mathrm{km/s}.$$

    Escape speed at same radius:
    $$v_e=\sqrt{2}\,v_c\approx 1.4142\times 6.1995=8.7675\ \mathrm{km/s}.$$

    Therefore
    $$\Delta v=v_e-v_c\approx 8.7675-6.1995=2.5680\ \mathrm{km/s}\approx \boxed{2.57\ \mathrm{km/s}}.$$

    So the answer lies in the accepted NAT range $2.54$ to $2.62\ \mathrm{km/s}$.
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Use orbital radius, not altitude alone: $r=R_E+h=(6371+4000)\ \mathrm{km}=1.0371\times10^7\ \mathrm{m}$.",
    r"Compute circular speed: $v_c=\sqrt{\mu/r}$ with $\mu=3.986\times10^{14}\ \mathrm{m^3/s^2}$.",
    r"Compute escape speed at same radius: $v_e=\sqrt{2\mu/r}=\sqrt{2}\,v_c$.",
    r"Required increment is additional speed, not total escape speed: $\Delta v=v_e-v_c$.",
    r"Equivalent shortcut: $\Delta v=v_c(\sqrt{2}-1)$.",
    r"Numerically: $v_c\approx6.1995\ \mathrm{km/s}$, so $\Delta v\approx2.568\ \mathrm{km/s}$.",
    r"Round to 2 decimals: $\boxed{2.57\ \mathrm{km/s}}$.",
]

NEW_FORMULAS_USED = [
    r"$r=R_E+h$",
    r"$v_c=\sqrt{\dfrac{\mu}{r}}$",
    r"$v_e=\sqrt{\dfrac{2\mu}{r}}=\sqrt{2}\,v_c$",
    r"$\Delta v=v_e-v_c=v_c(\sqrt{2}-1)$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Orbital radius from altitude",
        "type": "equation",
        "formula": r"$r=R_E+h$",
        "relevance": "Converts surface-referenced altitude to center-referenced orbital radius.",
        "conditions": ["Spherical Earth approximation for this numerical problem."],
    },
    {
        "name": "Circular orbital speed",
        "type": "equation",
        "formula": r"$v_c=\sqrt{\dfrac{\mu}{r}}$",
        "relevance": "Current orbital speed before the escape impulse.",
        "conditions": ["Circular orbit, two-body model."],
    },
    {
        "name": "Escape speed at radius r",
        "type": "equation",
        "formula": r"$v_e=\sqrt{\dfrac{2\mu}{r}}$",
        "relevance": "Minimum speed for zero specific orbital energy (parabolic escape).",
        "conditions": ["No atmospheric drag, impulsive maneuver."],
    },
    {
        "name": "Minimum increment from circular to escape",
        "type": "equation",
        "formula": r"$\Delta v=v_e-v_c=v_c(\sqrt{2}-1)$",
        "relevance": "Direct final relation used to compute required burn magnitude.",
        "conditions": ["Same orbital radius before and after impulse point."],
    },
]

NEW_HINTS = [
    r"Do **not** use altitude directly in velocity formulas; first compute $r=R_E+h$.",
    r"Escape speed at a given radius is $\sqrt{2}$ times the circular speed at that radius.",
    r"The question asks for **increment**: $\Delta v=v_e-v_c$, not $v_e$ alone.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"Circular orbital speed in terms of $\mu$ and $r$?",
        "back": r"$v_c=\sqrt{\mu/r}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "formula_recall",
        "front": r"Escape speed at radius $r$?",
        "back": r"$v_e=\sqrt{2\mu/r}=\sqrt{2}\,v_c$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"Minimum increment from circular orbit to escape at same radius?",
        "back": r"$\Delta v=v_e-v_c=v_c(\sqrt{2}-1)$",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Most common radius mistake in orbital questions?",
        "back": r"Using altitude only. Correct radius is $r=R_E+h$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "ROA: Radius = Earth radius + Altitude",
        "concept": r"$r=R_E+h$",
        "effectiveness": "high",
        "context": "Pre-substitution checklist",
    },
    {
        "mnemonic": "Escape = Orbit × root2",
        "concept": r"$v_e=\sqrt{2}\,v_c$",
        "effectiveness": "high",
        "context": "Fast Δv estimation",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Using only altitude instead of $r=R_E+h$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Overestimated speeds and wrong $\Delta v$.",
        "how_to_avoid": r"Write $r$ explicitly before any velocity formula.",
        "why_students_make_it": "Surface-based intuition mixed with center-based formulas.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Taking $\Delta v=v_e$ instead of $v_e-v_c$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Answer near $8.8\ \mathrm{km/s}$ instead of $2.57\ \mathrm{km/s}$.",
        "how_to_avoid": r"Read “increment” as additional burn over existing orbital speed.",
        "why_students_make_it": "Misreading of wording.",
    },
    {
        "type": "Calculation",
        "mistake": "Unit inconsistency (km vs m, m/s vs km/s).",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Order-of-magnitude errors.",
        "how_to_avoid": "Use SI through calculation, convert to km/s only at end.",
        "why_students_make_it": "Rushed arithmetic.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Direct numerical: compute $r$, then $v_c$, then $\Delta v=v_c(\sqrt{2}-1)$.",
    "guessing_heuristic": r"For this orbit, expect $\Delta v$ around $2.5$–$2.6\ \mathrm{km/s}$.",
    "time_management": r"2–3 min max; avoid long derivations.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Must identify increment as $v_e-v_c$.",
    r"Careful conversion from altitude to orbital radius.",
    r"Consistent SI units and final km/s conversion.",
]

NEW_ALT_METHODS = [
    {
        "name": "Specific-energy method",
        "description": r"Use $\epsilon_c=-\mu/(2r)$ for circular orbit and $\epsilon_e=0$ for parabolic escape; derive same $v_e$ and then $\Delta v=v_e-v_c$.",
        "pros_cons": "Pros: conceptual energy insight. Cons: longer than direct velocity formulas.",
        "when_to_use": "For cross-checks or when teaching first principles.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2019 AE Q42 escape delta v",
    "circular orbit to escape velocity increment",
    "delta v equals vc root2 minus 1",
    "orbital radius earth altitude conversion",
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
    av["correct_answer"] = "2.57 km/s"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    exp["question_nature"] = "Calculation"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["solution_path"] = (
        r"$r=R_E+h$ $\Rightarrow$ $v_c=\sqrt{\mu/r}$ $\Rightarrow$ "
        r"$v_e=\sqrt{2\mu/r}$ $\Rightarrow$ $\Delta v=v_e-v_c$"
    )
    sbs["key_insights"] = [
        r"Escape from a circular orbit needs only the **difference** to escape speed at same radius.",
        r"Shortcut: $\Delta v=v_c(\sqrt{2}-1)$.",
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

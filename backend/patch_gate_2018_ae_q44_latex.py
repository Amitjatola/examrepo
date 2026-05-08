"""
Fix LaTeX / formatting for GATE_2018_AE_Q44 (circular-orbit injection speed, NAT).

Usage (from backend/):
  PYTHONPATH=. python patch_gate_2018_ae_q44_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2018_AE_Q44"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    A spacecraft forms a circular orbit at an altitude of 150 km above the surface of a spherical Earth.
    Assuming gravitational parameter mu = 3.986 x 10^14 m^3/s^2 and radius of Earth R_E = 6400 km,
    the velocity required for injection of the spacecraft, parallel to the local horizon, is ________ (accurate to two decimal places).
    """
).strip()

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    A spacecraft forms a circular orbit at altitude $h=150\ \mathrm{km}$ above a spherical Earth.

    Assume gravitational parameter
    $$\mu=3.986\times10^{14}\ \mathrm{m^3/s^2}$$
    and Earth radius
    $$R_E=6400\ \mathrm{km}.$$

    The velocity required for injection of the spacecraft, parallel to the local horizon, is
    $\underline{\qquad\qquad}\ \mathrm{m/s}$ (accurate to two decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    For circular orbit, the required tangential speed is
    $$v=\sqrt{\frac{\mu}{r}},$$
    where $r$ is orbital radius from Earth's center.

    Convert geometry to SI:
    $$R_E=6400\ \mathrm{km}=6.4\times10^6\ \mathrm{m},\qquad
      h=150\ \mathrm{km}=1.5\times10^5\ \mathrm{m}.$$
    So,
    $$r=R_E+h=6.55\times10^6\ \mathrm{m}.$$

    Substitute:
    $$v=\sqrt{\frac{3.986\times10^{14}}{6.55\times10^6}}
      =\sqrt{6.0855\times10^7}
      \approx 7800.96\ \mathrm{m/s}.$$

    Therefore, the required injection velocity is
    $$\boxed{7800.96\ \mathrm{m/s}}\approx 7801\ \mathrm{m/s},$$
    which lies within the accepted range $7800$ to $7802\ \mathrm{m/s}$.
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Use circular-orbit speed formula: $v=\sqrt{\mu/r}$.",
    r"Convert given lengths to meters: $R_E=6.4\times10^6\ \mathrm{m}$ and $h=1.5\times10^5\ \mathrm{m}$.",
    r"Compute orbital radius from Earth's center: $r=R_E+h=6.55\times10^6\ \mathrm{m}$.",
    r"Substitute into $v=\sqrt{\mu/r}$ with $\mu=3.986\times10^{14}\ \mathrm{m^3/s^2}$.",
    r"Evaluate ratio: $\mu/r\approx6.0855\times10^7\ \mathrm{m^2/s^2}$.",
    r"Take square root and round: $v\approx7800.96\ \mathrm{m/s}$.",
]

NEW_FORMULAS_USED = [
    r"$r=R_E+h$",
    r"$v=\sqrt{\dfrac{\mu}{r}}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Circular orbital velocity",
        "type": "equation",
        "formula": r"$v=\sqrt{\dfrac{\mu}{r}}$",
        "relevance": "Direct formula for the required tangential speed in a circular orbit.",
        "conditions": ["Two-body central-gravity model, circular orbit, negligible drag."],
    },
    {
        "name": "Orbital radius",
        "type": "equation",
        "formula": r"$r=R_E+h$",
        "relevance": "Converts surface altitude to center-based radius required in the velocity formula.",
        "conditions": ["Altitude measured above Earth's surface."],
    },
    {
        "name": "Gravitational parameter",
        "type": "definition",
        "formula": r"$\mu=GM$",
        "relevance": "Earth's combined gravity constant used in orbital speed calculations.",
        "conditions": ["Given numerically in the stem."],
    },
]

NEW_HINTS = [
    r"Do not use altitude alone in $v=\sqrt{\mu/r}$; use $r=R_E+h$.",
    r"Since $\mu$ is in $\mathrm{m^3/s^2}$, convert all distances to meters.",
    r"This is circular-orbit injection speed, not escape speed.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "Formula for circular orbital speed around Earth?",
        "back": r"$v=\sqrt{\mu/r}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": "How do you get orbital radius from altitude?",
        "back": r"$r=R_E+h$",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Most common unit trap in this question?",
        "back": r"If $\mu$ is in $\mathrm{m^3/s^2}$, use $r$ in meters; answer comes in $\mathrm{m/s}$.",
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"Given $\mu=3.986\times10^{14}\ \mathrm{m^3/s^2}$ and $r=6.55\times10^6\ \mathrm{m}$, estimate $v$.",
        "back": r"$v\approx\sqrt{3.986\times10^{14}/6.55\times10^6}\approx7801\ \mathrm{m/s}$.",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "CORE radius: Center = Earth radius + altitude",
        "concept": r"$r=R_E+h$",
        "effectiveness": "high",
        "context": "Orbital radius setup",
    },
    {
        "mnemonic": "CIRC speed = root(mu over r)",
        "concept": r"$v=\sqrt{\mu/r}$",
        "effectiveness": "high",
        "context": "Circular orbit velocity recall",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Using altitude $h$ directly in $v=\sqrt{\mu/r}$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Velocity grossly overestimated.",
        "how_to_avoid": r"Always compute $r=R_E+h$ first.",
        "why_students_make_it": "Confusion between surface-referenced and center-referenced distances.",
    },
    {
        "type": "Units",
        "mistake": "Mixing km with m when μ is in SI units.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Answer off by factor ~sqrt(1000).",
        "how_to_avoid": "Convert all lengths to meters before substitution.",
        "why_students_make_it": "Rushing through unit conversion.",
    },
    {
        "type": "Conceptual",
        "mistake": "Using escape-velocity formula instead of circular-orbit formula.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Answer near 11 km/s equivalent, far too high.",
        "how_to_avoid": "Check the phrase: 'forms a circular orbit'.",
        "why_students_make_it": "Formula memorization without context check.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Compute $r=R_E+h$, then one substitution in $v=\sqrt{\mu/r}$.",
    "guessing_heuristic": r"LEO speeds are around $7.7$–$7.9\ \mathrm{km/s}$ (about $7700$–$7900\ \mathrm{m/s}$).",
    "time_management": "2–3 minutes; one careful unit conversion then calculator.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Center-based orbital radius must be used ($R_E+h$).",
    r"SI unit consistency with $\mu$ in $\mathrm{m^3/s^2}$.",
    r"Scientific-notation arithmetic and square-root accuracy.",
]

NEW_ALT_METHODS = [
    {
        "name": "Force-balance derivation",
        "description": r"Start from $\mu m/r^2 = m v^2/r$ (gravity provides centripetal force), then solve to recover $v=\sqrt{\mu/r}$.",
        "pros_cons": "Pros: gives physical derivation. Cons: longer than direct substitution.",
        "when_to_use": "When formula memory is uncertain but mechanics fundamentals are clear.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2018 AE Q44 circular orbit velocity",
    "injection velocity at 150 km",
    "v equals root mu by r",
    "orbital radius RE plus h",
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
    av["correct_answer"] = "7800.96 m/s"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    exp["question_nature"] = "Calculation"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["solution_path"] = r"Convert units $\Rightarrow$ compute $r=R_E+h$ $\Rightarrow$ apply $v=\sqrt{\mu/r}$ $\Rightarrow$ round"
    sbs["key_insights"] = [
        r"Circular-orbit injection speed equals local circular orbital speed.",
        r"Radius in formula is from Earth's center, not altitude alone.",
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

    conn = o.get("connections_to_other_subjects")
    if isinstance(conn, dict):
        conn = deepcopy(conn)
        # normalize duplicated naming styles where practical
        if "Mathematics" in conn and "mathematics" in conn:
            conn.pop("mathematics", None)
        if "Physics" in conn and "classical_mechanics" in conn:
            conn.pop("classical_mechanics", None)
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

"""
Fix LaTeX / formatting for GATE_2023_AE_Q63 (circular orbit altitude NAT).

Usage (from backend/):
  PYTHONPATH=. python patch_gate_2023_ae_q63_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q63"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    A satellite is in a circular orbit around Earth with period 90 minutes.
    Radius of Earth = 6370 km, mass of Earth = 5.98 x 10^24 kg, and universal gravitational constant = 6.67 x 10^-11 N m^2/kg^2.
    The altitude of the satellite above mean sea level is ______ km (round to nearest integer).
    """
).strip()

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    A satellite is in a circular orbit around Earth with time period $T=90~\mathrm{min}$.

    The Earth radius is $R_E=6370~\mathrm{km}$, Earth mass is $M_E=5.98\times10^{24}~\mathrm{kg}$, and
    the universal gravitational constant is $G=6.67\times10^{-11}~\mathrm{N\,m^2/kg^2}$.

    The altitude of the satellite above mean sea level is $\underline{\qquad\qquad}~\mathrm{km}$ (round to the nearest integer).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    For a circular orbit, use Kepler's third-law form
    $$T=2\pi\sqrt{\frac{r^3}{\mu}},\qquad \mu=GM_E.$$
    Convert to SI units: $T=90\times60=5400~\mathrm{s}$ and $R_E=6370~\mathrm{km}=6.370\times10^6~\mathrm{m}$.

    Compute gravitational parameter:
    $$\mu=(6.67\times10^{-11})(5.98\times10^{24})=3.98866\times10^{14}~\mathrm{m^3/s^2}.$$

    Rearranging Kepler's relation:
    $$r^3=\frac{\mu T^2}{4\pi^2},\qquad
      r=\left(\frac{\mu T^2}{4\pi^2}\right)^{1/3}.$$

    Substitute values:
    $$r=\left(\frac{(3.98866\times10^{14})(5400)^2}{4\pi^2}\right)^{1/3}
      \approx 6.654\times10^6~\mathrm{m}=6654~\mathrm{km}.$$

    Altitude above mean sea level:
    $$h=r-R_E\approx 6654-6370=284~\mathrm{km}.$$

    Hence the required altitude is
    $$\boxed{284~\mathrm{km}}.$$
    This lies within the official acceptance range $260$ to $300~\mathrm{km}$.
    """
).strip()

NEW_HINTS = [
    r"Convert period first: $90~\mathrm{min}\to5400~\mathrm{s}$ before using orbital formulas.",
    r"Use $\mu=GM_E$ and then $T=2\pi\sqrt{r^3/\mu}$ for a circular orbit.",
    r"Kepler gives radius from Earth's center ($r$), not altitude; final step is $h=r-R_E$.",
]

NEW_STEP_BY_STEP = [
    r"Convert data to SI: $T=5400~\mathrm{s}$ and $R_E=6.370\times10^6~\mathrm{m}$.",
    r"Compute $\mu=GM_E=(6.67\times10^{-11})(5.98\times10^{24})=3.98866\times10^{14}~\mathrm{m^3/s^2}$.",
    r"Write period relation for circular orbit: $T=2\pi\sqrt{r^3/\mu}$.",
    r"Rearrange: $r=\left(\mu T^2/(4\pi^2)\right)^{1/3}$.",
    r"Substitute numbers to obtain $r\approx6.654\times10^6~\mathrm{m}=6654~\mathrm{km}$.",
    r"Compute altitude: $h=r-R_E\approx6654-6370=284~\mathrm{km}$.",
    r"Round to nearest integer: $\boxed{284~\mathrm{km}}$.",
]

NEW_FORMULAS_USED = [
    r"$\mu=GM_E$",
    r"$T=2\pi\sqrt{\dfrac{r^3}{\mu}}$",
    r"$r=\left(\dfrac{\mu T^2}{4\pi^2}\right)^{1/3}$",
    r"$h=r-R_E$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Gravitational parameter",
        "type": "equation",
        "formula": r"$\mu=GM_E$",
        "relevance": "Combines Earth mass and gravitational constant into one orbital constant.",
        "conditions": ["Two-body approximation around Earth."],
    },
    {
        "name": "Circular-orbit period relation",
        "type": "equation",
        "formula": r"$T=2\pi\sqrt{\dfrac{r^3}{\mu}}$",
        "relevance": "Primary equation linking time period and orbital radius.",
        "conditions": ["Circular orbit, central-gravity model, neglecting perturbations."],
    },
    {
        "name": "Altitude from orbital radius",
        "type": "equation",
        "formula": r"$h=r-R_E$",
        "relevance": "Converts radius measured from Earth's center to altitude above surface.",
        "conditions": ["Mean Earth radius used for NAT-level approximation."],
    },
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"Period of a satellite in circular orbit (in terms of $r,\mu$)?",
        "back": r"$T=2\pi\sqrt{r^3/\mu}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"Difference between orbital radius $r$ and altitude $h$?",
        "back": r"$r$ is from Earth's center; $h$ is above surface. Relation: $r=R_E+h$.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Critical conversion when period is 90 minutes?",
        "back": r"Use SI time: $T=90\times60=5400~\mathrm{s}$ before substitution.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"What altitude scale corresponds to a ~90 min Earth orbit?",
        "back": r"Low Earth orbit (LEO), typically a few hundred km (about $200$–$500~\mathrm{km}$).",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": r"Square T, cube r",
        "concept": r"Kepler form: $T^2\propto r^3$",
        "effectiveness": "high",
        "context": "Period-radius relation",
    },
    {
        "mnemonic": r"Center minus surface",
        "concept": r"Altitude comes from $h=r-R_E$",
        "effectiveness": "high",
        "context": "Final step check",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Units",
        "mistake": r"Using $T=90$ directly instead of $5400~\mathrm{s}$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Large order-of-magnitude error in altitude.",
        "how_to_avoid": r"Convert to SI at the start and keep units in every line.",
        "why_students_make_it": "Rushing unit conversion.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Reporting orbital radius $r$ as altitude $h$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": r"Answer around $6650~\mathrm{km}$ instead of a few hundred km.",
        "how_to_avoid": r"Always finish with $h=r-R_E$.",
        "why_students_make_it": "Mixing center-based and surface-based distances.",
    },
    {
        "type": "Calculation",
        "mistake": "Cube-root/scientific-notation mistakes in evaluating r.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Altitude outside expected LEO range.",
        "how_to_avoid": "Compute in two stages: first r^3, then cube root with sanity check.",
        "why_students_make_it": "Calculator keying errors under exam pressure.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Direct 2-marker: use $\mu=GM$, then $T=2\pi\sqrt{r^3/\mu}$, then $h=r-R_E$.",
    "guessing_heuristic": r"A $90$-minute Earth orbit is LEO; plausible altitude is a few hundred km.",
    "time_management": r"3–4 min: conversions first, one formula rearrangement, then arithmetic and rounding.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Strict SI-unit consistency required.",
    r"Scientific-notation arithmetic and cube root handling.",
    r"Need to distinguish radius from altitude in the final step.",
]

NEW_ALT_METHODS = [
    {
        "name": "Velocity-elimination route",
        "description": r"Combine $v=\sqrt{\mu/r}$ with $T=2\pi r/v$ to recover $T=2\pi\sqrt{r^3/\mu}$, then solve for $r$ and compute $h$.",
        "pros_cons": "Pros: reinforces physical meaning of orbital speed. Cons: extra algebra for same result.",
        "when_to_use": "If period formula is forgotten but circular-orbit speed is remembered.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2023 AE Q63 circular orbit altitude",
    "Kepler third law satellite period",
    "altitude from orbital period Earth",
    "mu GM orbital mechanics",
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
    av["correct_answer"] = "284 km"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    exp["question_nature"] = "Calculation"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["solution_path"] = (
        r"Convert units $\Rightarrow$ compute $\mu=GM_E$ $\Rightarrow$ solve "
        r"$r=(\mu T^2/4\pi^2)^{1/3}$ $\Rightarrow$ compute $h=r-R_E$"
    )
    sbs["key_insights"] = [
        r"Period relation gives center-based radius $r$, not altitude directly.",
        r"Final answer must be in km above mean sea level after subtracting $R_E$.",
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
        for k in ("subject_name_1", "subject_name_2", "subject_name_3", "subject_name_4"):
            conn.pop(k, None)
        o["connections_to_other_subjects"] = conn

    return o


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, "
                "tier_3_enhanced_learning, options "
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

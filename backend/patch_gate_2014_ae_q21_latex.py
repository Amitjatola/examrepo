"""
Fix GATE_2014_AE_Q21 LaTeX: pitching moment about CG vs AC, lift coefficient.

$C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$ with $h=x_{\mathrm{cg}}/c$, $h_{\mathrm{ac}}=x_{\mathrm{ac}}/c$
from LE; AC $0.06c$ ahead of CG $\\Rightarrow$ $h-h_{\mathrm{ac}}=0.06$ $\\Rightarrow$ $C_L=0.5$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2014_ae_q21_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2014_AE_Q21"

NEW_QUESTION_TEXT_PLAIN = (
    "The moment coefficient measured about the centre of gravity and about the aerodynamic centre "
    "of a given wing-body combination are 0.0065 and −0.0235 respectively. The aerodynamic centre "
    "lies 0.06 chord lengths ahead of the centre of gravity. The lift coefficient for this wing-body is "
    "______."
)

NEW_QUESTION_TEXT_LATEX = (
    r"The pitching-moment coefficient about the centre of gravity is $C_{M,\mathrm{cg}}=0.0065$ and "
    r"about the aerodynamic centre is $C_{M,\mathrm{ac}}=-0.0235$. The aerodynamic centre lies "
    r"$0.06\,c$ ahead of the centre of gravity. The lift coefficient is "
    r"$\underline{\hspace{3em}}$."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"Let $h=x_{\mathrm{cg}}/c$ and $h_{\mathrm{ac}}=x_{\mathrm{ac}}/c$ denote positions of the CG and AC "
    r"as fractions of chord measured from the leading edge, positive aft. Transfer of pitching moment "
    r"from the AC to the CG gives"
    "\n"
    r"$C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L\,(h-h_{\mathrm{ac}})$."
    "\n\n"
    r"If the AC is $0.06\,c$ ahead of the CG, then $x_{\mathrm{ac}}=x_{\mathrm{cg}}-0.06c$, hence "
    r"$h_{\mathrm{ac}}=h-0.06$ and $h-h_{\mathrm{ac}}=+0.06$."
    "\n\n"
    r"Solve:"
    "\n"
    r"$0.0065=-0.0235+C_L(0.06)\quad\Rightarrow\quad "
    r"C_L=\dfrac{0.0065-(-0.0235)}{0.06}=\dfrac{0.03}{0.06}=0.5$."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Data: $C_{M,\mathrm{cg}}=0.0065$, $C_{M,\mathrm{ac}}=-0.0235$, AC is $0.06\,c$ forward of CG."
    ),
    (
        r"Moment relation (chord fractions $h,h_{\mathrm{ac}}$ from LE, positive aft): "
        r"$C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$."
    ),
    (
        "Geometry: AC ahead of CG $\\Rightarrow$ $h_{\\mathrm{ac}}=h-0.06$ $\\Rightarrow$ "
        "$h-h_{\\mathrm{ac}}=0.06$."
    ),
    (
        "Substitute: $0.0065=-0.0235+0.06\\,C_L$ $\\Rightarrow$ $0.03=0.06\\,C_L$."
    ),
    (r"Thus $C_L=0.03/0.06=0.5$."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$",
    r"$C_L=\dfrac{C_{M,\mathrm{cg}}-C_{M,\mathrm{ac}}}{h-h_{\mathrm{ac}}}$",
]

NEW_HINTS: List[str] = [
    (
        r"Write positions as fractions of chord from the leading edge: $h=x_{\mathrm{cg}}/c$, "
        r"$h_{\mathrm{ac}}=x_{\mathrm{ac}}/c$."
    ),
    (
        r"'AC ahead of CG by $0.06\,c$' means $h-h_{\mathrm{ac}}=+0.06$ in the standard transfer formula."
    ),
    (
        r"Subtract carefully: $C_{M,\mathrm{cg}}-C_{M,\mathrm{ac}}=0.0065-(-0.0235)=0.03$."
    ),
]

NEW_SOLUTION_PATH = (
    "$C_{M,\\mathrm{cg}}=C_{M,\\mathrm{ac}}+C_L(h-h_{\\mathrm{ac}})$ $\\Rightarrow$ "
    "$(h-h_{\\mathrm{ac}})=0.06$ $\\Rightarrow$ $C_L$"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"The lift force acts through the AC; moving the reference point from AC to CG adds "
        r"$C_L(h-h_{\mathrm{ac}})$."
    ),
    (
        r"Sign of $(h-h_{\mathrm{ac}})$ follows geometry: AC forward of CG gives positive arm in this "
        r"formulation."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Correct geometric interpretation of 'AC ahead of CG' as $h-h_{\mathrm{ac}}=+0.06$.",
    r"Arithmetic with $C_{M,\mathrm{cg}}-C_{M,\mathrm{ac}}$ including the double negative.",
    r"Choosing $C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$ vs.\ the flipped arm sign.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$",
        "name": r"Pitching moment about CG from AC",
        "conditions": [
            r"$h$ and $h_{\mathrm{ac}}$ are CG and AC positions as $x/c$ from the leading edge, positive aft.",
            r"Small-angle, linear lift; wing–body treated as single effective lifting system.",
        ],
        "type": "equation",
        "relevance": r"Relates $C_L$ to moment coefficients and CG–AC spacing.",
    },
    {
        "formula": r"$C_L=\dfrac{C_{M,\mathrm{cg}}-C_{M,\mathrm{ac}}}{h-h_{\mathrm{ac}}}$",
        "name": r"Lift coefficient from moment difference",
        "conditions": [
            r"$h\neq h_{\mathrm{ac}}$ (finite arm).",
        ],
        "type": "equation",
        "relevance": r"Direct rearrangement for NAT-style numeric items.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            r"Using $(h_{\mathrm{ac}}-h)=+0.06$ in $C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h_{\mathrm{ac}}-h)$ "
            r"without flipping sign—gives $C_L=-0.5$."
        ),
        "why_students_make_it": r"Mixing two equivalent forms of the same relation.",
        "type": "Sign convention",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            r"Fix one template: e.g.\ always use $C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$ "
            r"with LE-based $h$."
        ),
        "consequence": r"Wrong sign on $C_L$.",
    },
    {
        "mistake": r"Computing $0.0065-0.0235$ instead of $0.0065-(-0.0235)$.",
        "why_students_make_it": r"Dropping parentheses on $C_{M,\mathrm{ac}}$.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Write $C_{M,\mathrm{cg}}-C_{M,\mathrm{ac}}$ explicitly before dividing.",
        "consequence": r"Incorrect numerator.",
    },
    {
        "mistake": r"Dividing by $c$ twice or confusing dimensional distance with $h=x/c$.",
        "why_students_make_it": r"Inconsistent non-dimensionalization.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "rare",
        "how_to_avoid": r"Work entirely in chord fractions $x/c$.",
        "consequence": r"Wrong magnitude.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": r"Fast NAT: one transfer equation + one fraction.",
    "triage_tip": (
        r"$C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$ with $h-h_{\mathrm{ac}}=0.06$ here."
    ),
    "guessing_heuristic": (
        r"Numerator $0.0065-(-0.0235)=0.03$; divide by $0.06$ gives a clean $0.5$."
    ),
    "time_management": r"Under 3 minutes including sign check.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"Relate $C_{M,\mathrm{cg}}$, $C_{M,\mathrm{ac}}$, $C_L$, and CG/AC positions $h,h_{\mathrm{ac}}$.",
        "back": r"$C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "concept_recall",
        "front": r"What is special about pitching moment about the aerodynamic centre?",
        "back": (
            r"$C_{M,\mathrm{ac}}$ is independent of $\alpha$ for the linear range (lift curve slope fixed); "
            r"lift acts at AC."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 40,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"AC is $0.06\,c$ ahead of CG. What is $h-h_{\mathrm{ac}}$ (LE-based fractions)?",
        "back": r"$+0.06$ (CG aft of AC).",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "application",
        "front": r"$C_{M,\mathrm{cg}}=0.01$, $C_{M,\mathrm{ac}}=-0.02$, $h-h_{\mathrm{ac}}=0.1$ — find $C_L$.",
        "back": r"$C_L=(0.01-(-0.02))/0.1=0.3$.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": "CG moment = AC moment + lift $\\times$ (CG $-$ AC) arm in chords.",
        "concept": r"Parallel-axis style transfer along the chord.",
        "effectiveness": "high",
        "context": r"Longitudinal moments.",
    },
    {
        "mnemonic": r"Ahead means smaller $x_{\mathrm{ac}}$: check $(h-h_{\mathrm{ac}})$ sign once.",
        "concept": r"Geometry before algebra.",
        "effectiveness": "medium",
        "context": r"AC/CG distance wording.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "GATE 2014 AE pitching moment CG AC lift coefficient",
    "C_M cg C_M ac C_L wing body",
    "aerodynamic centre ahead centre of gravity 0.06 chord",
]

NEW_CONNECTIONS: Dict[str, str] = {
    "Statics": (
        r"Resultant moments about different reference points on a rigid body."
    ),
    "Flight mechanics": (
        r"Longitudinal trim, static margin, neutral point—built on CG–AC moment transfer."
    ),
    "Aerodynamics": (
        r"AC location and $C_{M,\mathrm{ac}}$ characterize the lifting system."
    ),
}

NEW_DEEPER_DIVE: List[str] = [
    r"Tail contribution and full-aircraft pitching-moment curves.",
    r"Neutral point and static margin: $SM=(x_{\mathrm{np}}-x_{\mathrm{cg}})/c$.",
    r"Mach-dependent AC shift in compressible flow.",
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
    av["correct_answer"] = "0.5"

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

    for am in t3.get("alternative_methods") or []:
        if not isinstance(am, dict):
            continue
        if am.get("name") == "First Principles Derivation from Physics":
            am["description"] = (
                r"Start from $M_{\mathrm{cg}}=M_{\mathrm{ac}}+L(x_{\mathrm{cg}}-x_{\mathrm{ac}})$; divide by "
                r"$qSc$ to obtain $C_{M,\mathrm{cg}}=C_{M,\mathrm{ac}}+C_L(h-h_{\mathrm{ac}})$."
            )
            am["pros_cons"] = (
                r"Reinforces sign conventions; slightly slower than using the coefficient form directly."
            )

    conn = dict(t3.get("connections_to_other_subjects") or {})
    conn.update(NEW_CONNECTIONS)
    for k in ("subject_name_1", "subject_name_2"):
        conn.pop(k, None)
    t3["connections_to_other_subjects"] = conn

    dd = list(t3.get("deeper_dive_topics") or [])
    t3["deeper_dive_topics"] = _merge_unique(NEW_DEEPER_DIVE, dd)

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

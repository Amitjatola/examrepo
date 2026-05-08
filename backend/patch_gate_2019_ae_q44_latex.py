"""
Fix LaTeX / formatting for GATE_2019_AE_Q44.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q44"

NEW_QUESTION_TEXT = (
    "An airplane design is modified: vertical tail area increases by 20% and moment arm from vertical-tail "
    "aerodynamic center to aircraft CG decreases by 20%. Assuming all else unchanged, find the ratio of modified "
    "to original directional static stability contribution (C_N_beta due to tail fin), rounded to 2 decimals."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The design of an airplane is modified to increase vertical tail area by $20\%$ and decrease the moment arm
    from the aerodynamic center of the vertical tail to the airplane center of gravity by $20\%$.
    Assuming all other factors remain unchanged, the ratio of modified to original directional static stability
    contribution $\left(C_{N_\beta}\ \text{due to tail fin}\right)$ is
    $\underline{\qquad\qquad}$ (round off to 2 decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    For vertical-tail contribution,
    $$C_{N_\beta,\text{tail}} \propto S_v\,l_v.$$

    Modified values:
    $$S_v' = 1.2\,S_v,\qquad l_v' = 0.8\,l_v.$$

    Ratio:
    $$\frac{C'_{N_\beta,\text{tail}}}{C_{N_\beta,\text{tail}}}
    =\frac{S_v' l_v'}{S_v l_v}
    =\frac{(1.2S_v)(0.8l_v)}{S_v l_v}
    =1.2\times 0.8
    =0.96.$$

    Rounded to 2 decimals: **0.96**.
    """
).strip()

NEW_STEPS = [
    r"Use proportionality for vertical tail: $C_{N_\beta,\text{tail}} \propto S_v l_v$.",
    r"Apply changes: $S_v' = 1.2S_v$ and $l_v' = 0.8l_v$.",
    r"Form ratio: $\dfrac{C'_{N_\beta,\text{tail}}}{C_{N_\beta,\text{tail}}}=\dfrac{S_v'l_v'}{S_v l_v}$.",
    r"Substitute: $\dfrac{(1.2S_v)(0.8l_v)}{S_v l_v}$.",
    r"Cancel common factors and multiply: $1.2\times0.8=0.96$.",
    r"Final answer (2 decimals): $0.96$.",
]

NEW_FORMULAS_USED = [
    r"$C_{N_\beta,\text{tail}} \propto S_v l_v$",
    r"$\dfrac{C'_{N_\beta,\text{tail}}}{C_{N_\beta,\text{tail}}}=\dfrac{S_v' l_v'}{S_v l_v}$",
    r"$S_v' = 1.2S_v,\ l_v' = 0.8l_v$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Vertical-tail directional stability contribution",
        "type": "equation",
        "formula": r"$C_{N_\beta,\text{tail}} = k\,S_v l_v$",
        "conditions": "Other factors (reference quantities and derivative constants) unchanged.",
        "relevance": "Core scaling relation in this problem.",
    },
    {
        "name": "Modified-to-original ratio",
        "type": "equation",
        "formula": r"$\dfrac{C'_{N_\beta,\text{tail}}}{C_{N_\beta,\text{tail}}}=\dfrac{S_v'}{S_v}\dfrac{l_v'}{l_v}$",
        "conditions": "Only area and moment arm changed.",
        "relevance": "Direct computation form.",
    },
]

NEW_HINTS = [
    r"Convert percentage changes to factors: $+20\%\to 1.2$, $-20\%\to 0.8$.",
    r"Directional stability tail contribution scales with product $S_v l_v$.",
    r"Do multiplication, not percentage cancellation.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"How does vertical-tail contribution to $C_{N_\beta}$ scale?",
        "back": r"$C_{N_\beta,\text{tail}} \propto S_v l_v$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": "What are factors for +20% and -20% changes?",
        "back": r"$1.2$ and $0.8$ respectively.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"If $S_v$ increases by $30\%$ and $l_v$ decreases by $10\%$, ratio?",
        "back": r"$1.3\times0.9=1.17$",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Area times Arm",
        "concept": r"Tail contribution scales as $S_v l_v$",
        "effectiveness": "high",
        "context": "Directional stability quick recall",
    },
    {
        "mnemonic": "Percent to factor first",
        "concept": "Convert percentages before multiplying",
        "effectiveness": "high",
        "context": "NAT calculation accuracy",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": "Adding/subtracting percentages directly instead of multiplying factors.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Gets 1.0 instead of 0.96.",
        "how_to_avoid": r"Write factors explicitly: $1.2$ and $0.8$, then multiply.",
        "why_students_make_it": "Treats percent changes as additive offsets.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Using only $S_v$ or only $l_v$ change, not the product.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Gets 1.2 or 0.8 (wrong).",
        "how_to_avoid": r"Start from $C_{N_\beta,\text{tail}} \propto S_v l_v$ every time.",
        "why_students_make_it": "Partial recall of formula.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Direct proportionality NAT. Convert percentages to factors and multiply.",
    "guessing_heuristic": "Equal +20% and -20% do not cancel; product is slightly below 1.",
    "time_management": "Under 2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Single-step scaling once formula is known.",
    "Main trap is percent-factor conversion.",
]

NEW_ALT_METHODS = [
    {
        "name": "Tail volume ratio form",
        "description": r"Use $V_v=\dfrac{S_v l_v}{Sb}$ and note $S,b$ unchanged, so ratio reduces to $\dfrac{S_v' l_v'}{S_v l_v}$.",
        "pros_cons": "Pros: more general framework. Cons: extra symbols for same arithmetic.",
        "when_to_use": "When wing reference terms are also changing.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "0.96"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Write $C_{N_\beta,\text{tail}}\propto S_v l_v$ $\rightarrow$ apply factors $1.2,0.8$ $\rightarrow$ compute ratio"
    sbs["key_insights"] = [
        "Directional stability contribution scales with area and moment arm product.",
        "Percent changes combine multiplicatively.",
    ]

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    prereq = o.get("prerequisites")
    if isinstance(prereq, dict):
        dep = prereq.get("dependency_tree")
        if isinstance(dep, dict):
            dep.pop("Directional Static Stability", None)

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
    return o


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning "
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

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=:opts, "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": None,
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

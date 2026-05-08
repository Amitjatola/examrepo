"""
Fix LaTeX / formatting for GATE_2023_AE_Q19.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q19"

NEW_QUESTION_TEXT = (
    "For a longitudinally statically stable aircraft, which graph represents the relationship between pitching "
    "moment coefficient about the center of gravity and absolute angle of attack? (Nose-up moment is positive.)"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    For a longitudinally statically stable aircraft, which one of the following represents the relationship
    between pitching moment coefficient about the center of gravity, $C_{m,cg}$, and absolute angle of attack,
    $\alpha_a$? (Note: nose-up moment is positive.)
    """
).strip()

NEW_OPTIONS = {
    "A": "Graph A",
    "B": "Graph B",
    "C": "Graph C",
    "D": "Graph D",
}

NEW_REASONING = dedent(
    r"""
    Longitudinal static stability requires
    $$\frac{dC_{m,cg}}{d\alpha_a}<0.$$
    So when $\alpha_a$ increases, $C_{m,cg}$ must decrease to create a restoring nose-down moment.

    Also, trim occurs where
    $$C_{m,cg}(\alpha_{a,e})=0.$$
    A typical stable aircraft has a negative slope and a realistic trim crossing at positive $\alpha_a$.
    Among the given graphs, **Graph D** matches this behavior.
    """
).strip()

NEW_STEPS = [
    r"Recall stability condition (nose-up positive): $\frac{dC_{m,cg}}{d\alpha_a}<0$.",
    r"Interpret physically: increase in $\alpha_a$ must generate restoring nose-down moment, i.e., lower $C_{m,cg}$.",
    r"Therefore the required graph slope is negative.",
    r"Use trim check: at equilibrium $\alpha_{a,e}$, $C_{m,cg}=0$.",
    r"Among negative-slope options, pick the one showing realistic trim crossing.",
    r"Hence, correct option is **D**.",
]

NEW_FORMULAS_USED = [
    r"$\frac{dC_{m,cg}}{d\alpha_a}<0$",
    r"$C_{m,cg}(\alpha_{a,e})=0$",
    r"$\alpha_a=\alpha+\left|\alpha_{L=0}\right|$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Longitudinal static stability condition",
        "type": "principle",
        "formula": r"$\frac{dC_{m,cg}}{d\alpha_a}<0$",
        "conditions": [
            "Moment reference about CG",
            "Nose-up moment taken positive",
            "Small perturbation about trim",
        ],
        "relevance": "Core selection criterion for the graph.",
    },
    {
        "name": "Absolute angle of attack definition",
        "type": "definition",
        "formula": r"$\alpha_a=\alpha+\left|\alpha_{L=0}\right|$",
        "conditions": ["Offset term is constant for a given airfoil/configuration."],
        "relevance": "Offset changes intercept, not slope sign.",
    },
    {
        "name": "Pitch trim condition",
        "type": "equation",
        "formula": r"$C_{m,cg}(\alpha_{a,e})=0$",
        "conditions": ["Steady equilibrium flight condition."],
        "relevance": "Used for realistic curve interpretation.",
    },
]

NEW_HINTS = [
    r"Do not mix with lift curve slope; here stability depends on $C_m$ slope.",
    r"Stable means $\alpha_a\uparrow \Rightarrow C_{m,cg}\downarrow$.",
    r"Look for a negative-slope $C_{m,cg}$ vs $\alpha_a$ line with sensible trim crossing.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "What is the static longitudinal stability criterion using pitching moment coefficient?",
        "back": r"$\frac{dC_{m,cg}}{d\alpha}<0$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": "If nose-up moment is positive, what slope of $C_{m,cg}$ vs $\\alpha$ indicates stability?",
        "back": "Negative slope.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"Why can $\alpha_a=\alpha+\left|\alpha_{L=0}\right|$ still use same stability slope test?",
        "back": "Because adding a constant shifts the curve horizontally but does not change derivative sign.",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "UP alpha, DOWN Cm",
        "concept": r"Stable longitudinal condition: $\frac{dC_m}{d\alpha}<0$",
        "effectiveness": "high",
        "context": "Graph-based MCQ in stability",
    },
    {
        "mnemonic": "Stable slope is negative",
        "concept": "Quick sign check in Cm-alpha plots",
        "effectiveness": "high",
        "context": "Fast elimination strategy",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Choosing positive slope as stable.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Picks unstable graph.",
        "how_to_avoid": r"Always verify restoring condition: $\alpha\uparrow$ should cause nose-down moment.",
        "why_students_make_it": "Confusion with other positive-slope aero curves.",
    },
    {
        "type": "Sign Error",
        "mistake": "Ignoring stated sign convention for pitching moment.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Reverses slope interpretation.",
        "how_to_avoid": "Write 'nose-up positive' before interpreting graph.",
        "why_students_make_it": "Skips note text under time pressure.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Immediate filter: keep only graphs with $\frac{dC_{m,cg}}{d\alpha_a}<0$.",
    "guessing_heuristic": "If two negative slopes appear, pick one with realistic trim crossing at positive angle.",
    "time_management": "30-60 seconds.",
}

NEW_DIFFICULTY_FACTORS = [
    "Pure concept check on slope sign and convention.",
    "Minor trap: alpha vs absolute-alpha notation.",
]

NEW_ALT_METHODS = [
    {
        "name": "Restoring-moment thought experiment",
        "description": "Imagine a small pitch-up disturbance. Stable aircraft must generate nose-down restoring moment; map that to Cm sign change with alpha.",
        "pros_cons": "Pros: avoids rote memorization. Cons: slower if sign convention not explicit.",
        "when_to_use": "When formula recall is uncertain during exam.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "D"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Conceptual Application"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Apply $\frac{dC_{m,cg}}{d\alpha_a}<0$ $\rightarrow$ inspect slopes $\rightarrow$ verify trim realism"
    sbs["key_insights"] = [
        "Stability criterion depends on slope sign, not absolute intercept.",
        "Absolute angle offset does not alter derivative sign.",
    ]

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    # Clean malformed dependency subtree if present
    prereq = o.get("prerequisites")
    if isinstance(prereq, dict):
        dep = prereq.get("dependency_tree")
        if isinstance(dep, dict):
            dep.pop("Main Concept: Graphical relationship of C_m vs", None)

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
    conn = o.get("connections_to_other_subjects")
    if isinstance(conn, dict):
        conn = deepcopy(conn)
        conn.pop("subject_name_1", None)
        conn.pop("subject_name_2", None)
        conn.pop("subject_name_3", None)
        o["connections_to_other_subjects"] = conn
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
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=CAST(:opts AS jsonb), "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
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

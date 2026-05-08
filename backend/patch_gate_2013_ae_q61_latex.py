"""
Fix LaTeX / formatting for GATE_2013_AE_Q61.

Usage:
  cd backend
  PYTHONPATH=. python patch_gate_2013_ae_q61_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2013_AE_Q61"

NEW_QUESTION_TEXT = (
    "Velocity of an object fired directly upward is given by V = 80 - 32t, where t (time) is in seconds. "
    "When will the velocity be between 32 m/s and 64 m/s?"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Velocity of an object fired directly upward is
    $V(t)=80-32t$, where $t$ is in seconds.
    Find the time interval for which
    $$32<V(t)<64 \quad (\mathrm{m/s}).$$
    """
).strip()

NEW_OPTIONS = {
    "A": r"$\left(1,\frac{3}{2}\right)$",
    "B": r"$\left(\frac{1}{2},1\right)$",
    "C": r"$\left(\frac{1}{2},\frac{3}{2}\right)$",
    "D": r"$(1,3)$",
}

NEW_REASONING = dedent(
    r"""
    Given $V(t)=80-32t$, apply the condition:
    $$32<80-32t<64.$$

    Split into two inequalities:
    $$32<80-32t \;\Rightarrow\; t<\frac{3}{2},$$
    $$80-32t<64 \;\Rightarrow\; t>\frac{1}{2}.$$
    (Inequality reverses when dividing by $-32$.)

    Combine:
    $$\frac{1}{2}<t<\frac{3}{2}.$$
    So the correct option is **C**.
    """
).strip()

NEW_STEPS = [
    r"Start with velocity law $V(t)=80-32t$ and target band $32<V<64$.",
    r"Write compound inequality: $32<80-32t<64$.",
    r"Left part: $32<80-32t \Rightarrow -48<-32t \Rightarrow t<\frac{3}{2}$.",
    r"Right part: $80-32t<64 \Rightarrow -32t<-16 \Rightarrow t>\frac{1}{2}$.",
    r"Intersect both results: $\frac{1}{2}<t<\frac{3}{2}$.",
    r"Write answer in interval form: $\left(\frac{1}{2},\frac{3}{2}\right)$.",
]

NEW_FORMULAS_USED = [
    r"$V(t)=80-32t$",
    r"$32<V(t)<64$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Linear velocity-time relation",
        "type": "equation",
        "formula": r"$V(t)=80-32t$",
        "relevance": "Given model for vertical motion velocity.",
        "conditions": "Constant downward acceleration, neglecting drag.",
    },
    {
        "name": "Constant acceleration",
        "type": "equation",
        "formula": r"$a=\frac{dV}{dt}=-32$",
        "relevance": "Confirms linear decrease of velocity with time.",
        "conditions": "Acceleration is uniform over interval.",
    },
]

NEW_HINTS = [
    r"Treat 'between 32 and 64' as strict inequality: $32<V<64$.",
    r"Split the compound inequality into two simple inequalities.",
    r"When dividing by a negative number, reverse the inequality sign.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "For upward throw under constant gravity, what is velocity-time form?",
        "back": r"$V=u-gt$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": "What happens to inequality sign when dividing by a negative number?",
        "back": "It reverses direction.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"Given $V(t)=80-32t$, solve $32<V<64$. What interval comes?",
        "back": r"$\left(\frac{1}{2},\frac{3}{2}\right)$",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "NEGATIVE? FLIP inequality",
        "concept": "Sign reversal in inequalities",
        "effectiveness": "high",
        "context": "Linear inequality solving",
    },
    {
        "mnemonic": "BETWEEN means strict",
        "concept": r"Use $<$ and $>$ unless endpoints explicitly included",
        "effectiveness": "high",
        "context": "Interval interpretation in MCQ",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Sign Error",
        "mistake": "Not reversing inequality when dividing by -32.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrong interval bounds.",
        "how_to_avoid": "Mark negative division step explicitly and flip sign immediately.",
        "why_students_make_it": "Rushed algebra.",
    },
    {
        "type": "Conceptual",
        "mistake": "Taking 'between' as inclusive and using closed interval.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Conceptual error even if option accidentally matches.",
        "how_to_avoid": "Default to strict inequality unless words 'including endpoints' appear.",
        "why_students_make_it": "Natural language ambiguity.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Fast 2-inequality algebra question. Solve bounds, intersect, match interval.",
    "guessing_heuristic": "Test t=1 first. If V(1)=48 (inside range), correct option must include t=1.",
    "time_management": "Under 2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Simple algebraic inequality handling.",
    "Primary trap is sign flip on negative division.",
]

NEW_ALT_METHODS = [
    {
        "name": "Graphical check",
        "description": r"Plot $V(t)=80-32t$ and horizontal lines $V=32$, $V=64$. Read intersection times $t=\frac{1}{2},\frac{3}{2}$ and pick interval between them.",
        "pros_cons": "Pros: visual validation. Cons: slower for straightforward algebra.",
        "when_to_use": "Cross-check final answer quickly.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "C"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Set $32<V(t)<64$ $\rightarrow$ solve both inequalities $\rightarrow$ intersect bounds"
    sbs["key_insights"] = [
        "Reverse inequality when dividing by a negative.",
        "Intersection of bounds gives final open interval.",
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

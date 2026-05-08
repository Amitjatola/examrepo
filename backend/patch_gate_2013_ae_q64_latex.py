"""
Fix LaTeX / formatting for GATE_2013_AE_Q64.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2013_AE_Q64"

NEW_QUESTION_TEXT = (
    "If |-2X + 9| = 3, then a possible value of |-X| - X^2 is:"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    If
    $$|-2X+9|=3,$$
    then a possible value of
    $$|-X|-X^2$$
    is:
    """
).strip()

NEW_OPTIONS = {
    "A": "30",
    "B": "-30",
    "C": "-42",
    "D": "42",
}

NEW_REASONING = dedent(
    r"""
    From
    $$|-2X+9|=3,$$
    we get two cases:
    $$-2X+9=3 \quad \text{or} \quad -2X+9=-3.$$

    Solving gives:
    $$X=3 \quad \text{or} \quad X=6.$$

    Evaluate $|-X|-X^2$:
    - For $X=3$: $|-3|-3^2=3-9=-6$.
    - For $X=6$: $|-6|-6^2=6-36=-30$.

    A possible value is **$-30$**, so the correct option is **B**.
    """
).strip()

NEW_STEPS = [
    r"Interpret absolute value equation: $|A|=3 \Rightarrow A=3$ or $A=-3$.",
    r"Set $A=-2X+9$, so solve $-2X+9=3$ and $-2X+9=-3$.",
    r"First case gives $X=3$.",
    r"Second case gives $X=6$.",
    r"Substitute each into $|-X|-X^2$.",
    r"For $X=3$: $3-9=-6$; for $X=6$: $6-36=-30$.",
    r"Among options, possible value is $-30$.",
]

NEW_FORMULAS_USED = [
    r"$|a|=b \Rightarrow a=b \text{ or } a=-b$",
    r"$|x|=\begin{cases}x,&x\ge0\\-x,&x<0\end{cases}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Absolute-value equation rule",
        "type": "equation",
        "formula": r"$|a|=b \Rightarrow a=b \text{ or } a=-b,\ b\ge0$",
        "conditions": "Real numbers, nonnegative RHS.",
        "relevance": "Generates two linear equations to solve.",
    },
    {
        "name": "Absolute-value definition",
        "type": "principle",
        "formula": r"$|x|=\begin{cases}x,&x\ge0\\-x,&x<0\end{cases}$",
        "conditions": "All real x.",
        "relevance": "Used while evaluating $|-X|$.",
    },
]

NEW_HINTS = [
    r"Do not forget both cases from $|A|=3$.",
    r"After finding X values, evaluate expression for each.",
    r"Compute $X^2$ first, then apply minus sign in $-X^2$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": r"If $|A|=k$ with $k>0$, what are the two equations?",
        "back": r"$A=k$ and $A=-k$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "formula_recall",
        "front": "What is $|x|$ in piecewise form?",
        "back": r"$|x|=x$ if $x\ge0$, and $|x|=-x$ if $x<0$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"For $X=6$, evaluate $|-X|-X^2$.",
        "back": r"$|-6|-36=6-36=-30$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "ABS gives two branches",
        "concept": "Equation with absolute value splits into two cases",
        "effectiveness": "high",
        "context": "Quick solving in MCQ",
    },
    {
        "mnemonic": "Square first, sign later",
        "concept": "Handle $-X^2$ as $-(X^2)$",
        "effectiveness": "high",
        "context": "Avoid precedence mistakes",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Solving only one branch of absolute-value equation.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Misses valid X and wrong option selection.",
        "how_to_avoid": r"Always write both equations: $A=3$ and $A=-3$.",
        "why_students_make_it": "Rushing through absolute-value step.",
    },
    {
        "type": "Calculation",
        "mistake": r"Misreading $-X^2$ as $(-X)^2$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Sign error in final value.",
        "how_to_avoid": "Apply exponent before unary minus.",
        "why_students_make_it": "Operator precedence confusion.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Straightforward 2-case absolute-value problem; solve both branches and substitute.",
    "guessing_heuristic": "If first branch value is not in options, check second branch before concluding.",
    "time_management": "2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Two-case branching from absolute value.",
    "Possible precedence/sign mistakes in final expression.",
]

NEW_ALT_METHODS = [
    {
        "name": "Graphical intersection",
        "description": r"Plot $y=|-2X+9|$ and $y=3$; intersections give X values, then evaluate expression.",
        "pros_cons": "Pros: visual intuition. Cons: slower than algebra for MCQ.",
        "when_to_use": "For conceptual check if algebra feels uncertain.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "B"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Split absolute value into two equations $\rightarrow$ solve X $\rightarrow$ evaluate $|-X|-X^2$"
    sbs["key_insights"] = [
        "Absolute-value equations usually produce two candidate solutions.",
        "Evaluate final expression for all valid candidates.",
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

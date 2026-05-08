"""
Fix LaTeX / formatting for GATE_2024_AE_Q29.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2024_AE_Q29"

NEW_QUESTION_TEXT = (
    "Two fair dice are rolled together. Find probability of getting odd numbers on "
    "both dice, rounded to 2 decimal places."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Two fair dice are rolled together. Each die has faces numbered $1$ to $6$.
    The probability of getting odd numbers on both dice is
    \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ (rounded to 2 decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Odd outcomes on one die are $\{1,3,5\}$, i.e. $3$ out of $6$ outcomes.
    Hence
    $$P(\text{odd on one die})=\frac{3}{6}=\frac{1}{2}.$$

    For two independent dice:
    $$P(\text{odd on both})=
    P(\text{odd on die 1})\cdot P(\text{odd on die 2})
    =\frac{1}{2}\cdot\frac{1}{2}
    =\frac{1}{4}=0.25.$$

    Rounded to two decimals: **0.25**.
    """
).strip()

NEW_STEPS = [
    r"List odd faces on one die: $1,3,5$.",
    r"Compute single-die odd probability: $\frac{3}{6}=\frac{1}{2}$.",
    r"Use independence of the two dice rolls.",
    r"Multiply probabilities: $\frac{1}{2}\times\frac{1}{2}=\frac{1}{4}$.",
    r"Convert to decimal: $0.25$.",
    r"Round to two decimal places (unchanged): $0.25$.",
]

NEW_FORMULAS_USED = [
    r"$P(A)=\frac{\text{favorable outcomes}}{\text{total outcomes}}$",
    r"$P(A\cap B)=P(A)\,P(B)$ for independent events",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Classical probability",
        "type": "equation",
        "formula": r"$P(A)=\frac{n(A)}{n(S)}$",
        "conditions": "Finite equally likely sample space.",
        "relevance": "Computes odd probability on one die.",
    },
    {
        "name": "Multiplication rule for independent events",
        "type": "equation",
        "formula": r"$P(A\cap B)=P(A)\cdot P(B)$",
        "conditions": "Events A and B are independent.",
        "relevance": "Combines odd probabilities for two dice.",
    },
]

NEW_HINTS = [
    r"Do not use addition; event requires both dice to be odd.",
    r"Compute one-die odd probability first, then square it.",
    r"Two decimal places for $\frac14$ is exactly $0.25$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": "What are odd numbers on a standard die?",
        "back": "1, 3, 5",
        "difficulty": "easy",
        "time_limit_seconds": 10,
    },
    {
        "card_type": "formula_recall",
        "front": "How do you combine probabilities of independent events?",
        "back": r"Multiply: $P(A\cap B)=P(A)P(B)$",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": "Probability both dice show odd numbers?",
        "back": r"$\frac14=0.25$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "1-3-5 odd survive",
        "concept": "Odd faces on one die.",
        "effectiveness": "medium",
        "context": "Dice probability setup",
    },
    {
        "mnemonic": "INDE = multiply",
        "concept": "Independent events use multiplication rule.",
        "effectiveness": "high",
        "context": "Two-dice joint event calculations",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Treating rolls as dependent events.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Wrong combination method.",
        "how_to_avoid": "Remember dice outcomes do not influence each other.",
        "why_students_make_it": "Overthinks relation between events.",
    },
    {
        "type": "Calculation",
        "mistake": r"Using $\frac{3}{6}+\frac{3}{6}$ instead of multiplication.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Probability exceeds correct value substantially.",
        "how_to_avoid": "Event is 'both odd', so use intersection rule.",
        "why_students_make_it": "Confuses 'both' with 'either'.",
    },
    {
        "type": "Instructions",
        "mistake": "Incorrect rounding of 0.25.",
        "severity": "Low",
        "frequency": "rare",
        "consequence": "Outside accepted answer range.",
        "how_to_avoid": "Note that 0.25 already has two decimal places.",
        "why_students_make_it": "Unnecessary post-processing.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Fast route: $P(\text{odd})=\frac12$, then square for two independent dice.",
    "guessing_heuristic": "Result should be less than 0.5 and near 0.25 for a both-condition.",
    "time_management": "Under 1 minute.",
}

NEW_DIFFICULTY_FACTORS = [
    "Single-step independent-event multiplication.",
    "Minimal arithmetic and direct decimal output.",
]

NEW_ALT_METHODS = [
    {
        "name": "Sample space counting",
        "description": r"Out of 36 ordered outcomes, 9 have both odd entries, so probability is $\frac{9}{36}=\frac14$.",
        "pros_cons": "Pros: fully explicit verification. Cons: slower than direct independence method.",
        "when_to_use": "When double-checking without formulas.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "0.25"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Find one-die odd probability $\rightarrow$ apply independence $\rightarrow$ round"
    sbs["key_insights"] = [
        "Odd on one die is exactly half the outcomes.",
        "Joint probability for independent rolls is product of marginals.",
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
                "opts": json.dumps(None),
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

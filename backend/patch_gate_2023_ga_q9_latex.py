"""
Fix LaTeX / formatting for GATE_2023_GA_Q9.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_GA_Q9"

NEW_QUESTION_TEXT = (
    "The coefficient of x^4 in the polynomial (x-1)^3 (x-2)^3 is equal to _____."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The coefficient of $x^4$ in the polynomial
    $$(x-1)^3(x-2)^3$$
    is equal to $\underline{\qquad\qquad}$.
    """
).strip()

NEW_OPTIONS = {
    "A": "33",
    "B": "-3",
    "C": "30",
    "D": "21",
}

NEW_REASONING = dedent(
    r"""
    Expand each factor:
    $$(x-1)^3=x^3-3x^2+3x-1,$$
    $$(x-2)^3=x^3-6x^2+12x-8.$$

    For coefficient of $x^4$ in product, add terms where powers sum to $4$:
    $$[x^3]\cdot[x^1]:\ 1\cdot12=12,$$
    $$[x^2]\cdot[x^2]:\ (-3)\cdot(-6)=18,$$
    $$[x^1]\cdot[x^3]:\ 3\cdot1=3.$$

    Total:
    $$12+18+3=33.$$
    Hence correct option is **A**.
    """
).strip()

NEW_STEPS = [
    r"Use binomial expansion: $(x-1)^3=x^3-3x^2+3x-1$.",
    r"Expand second factor: $(x-2)^3=x^3-6x^2+12x-8$.",
    r"Target power is $x^4$, so collect pairings with exponent sum $4$.",
    r"$x^3\cdot 12x$ contributes $12x^4$.",
    r"$(-3x^2)\cdot(-6x^2)$ contributes $18x^4$.",
    r"$3x\cdot x^3$ contributes $3x^4$; sum is $33x^4$.",
]

NEW_FORMULAS_USED = [
    r"$(a-b)^3=a^3-3a^2b+3ab^2-b^3$",
    r"$C_n=\sum_{i+j=n}A_iB_j$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Cubic binomial expansion",
        "type": "equation",
        "formula": r"$(a-b)^3=a^3-3a^2b+3ab^2-b^3$",
        "conditions": "Valid for all real/complex a,b.",
        "relevance": "Used to expand both polynomial factors.",
    },
    {
        "name": "Coefficient convolution rule",
        "type": "principle",
        "formula": r"$C_n=\sum_{i+j=n}A_iB_j$",
        "conditions": r"If $A(x)=\sum A_i x^i$, $B(x)=\sum B_j x^j$.",
        "relevance": "Extracts coefficient of target power without full multiplication.",
    },
]

NEW_HINTS = [
    r"Expand both cubics correctly before multiplying.",
    r"For $x^4$, only use term pairs with exponent sum $4$.",
    r"Track signs carefully: $(-)\times(-)=(+)$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "What is the expansion of $(a-b)^3$?",
        "back": r"$(a-b)^3=a^3-3a^2b+3ab^2-b^3$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": "How to get coefficient of x^n in A(x)B(x)?",
        "back": r"$C_n=\sum_{i+j=n}A_iB_j$",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "application",
        "front": r"In $(x-1)^3(x-2)^3$, which pairings contribute to $x^4$?",
        "back": r"$(x^3,x^1), (x^2,x^2), (x^1,x^3)$",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "1-3-3-1 with signs + - + -",
        "concept": "Quick recall for $(a-b)^3$ coefficients/signs",
        "effectiveness": "high",
        "context": "Fast binomial expansion",
    },
    {
        "mnemonic": "Sum powers to target",
        "concept": "Coefficient extraction by exponent pairing",
        "effectiveness": "high",
        "context": "Product-polynomial coefficient problems",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": r"Incorrect cubic expansion (missing/mis-signed terms).",
        "severity": "High",
        "frequency": "common",
        "consequence": "Final coefficient becomes wrong.",
        "how_to_avoid": r"Write $(a-b)^3$ pattern explicitly before substitution.",
        "why_students_make_it": "Rushed recall of binomial pattern.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Missing one valid $(i,j)$ pair with $i+j=4$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Partial sum like 12 or 30.",
        "how_to_avoid": "List all exponent pairings systematically.",
        "why_students_make_it": "Unstructured multiplication.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "2-minute algebra: expand, pick only x^4 pairings, sum coefficients.",
    "guessing_heuristic": "Sign should be positive because major contributing products are positive.",
    "time_management": "Under 3 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Requires careful sign handling.",
    "Needs systematic exponent pairing for target coefficient.",
]

NEW_ALT_METHODS = [
    {
        "name": "Direct combinatorial binomial sum",
        "description": r"Write each cubic as binomial sum and apply condition $k+m=2$ for $x^4$ term.",
        "pros_cons": "Pros: compact, no full expansion needed. Cons: index bookkeeping may confuse.",
        "when_to_use": "When comfortable with binomial indices.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "A"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Expand two cubics $\rightarrow$ keep terms giving $x^4$ $\rightarrow$ add coefficients"
    sbs["key_insights"] = [
        "Use exponent-sum matching for target coefficient.",
        "Do not miss the middle pairing (x^2 with x^2).",
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
    conn = o.get("connections_to_other_subjects")
    if isinstance(conn, dict):
        conn = deepcopy(conn)
        conn.pop("subject_name_1", None)
        conn.pop("subject_name_2", None)
        conn.pop("subject_name_3", None)
        conn.pop("subject_name_4", None)
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

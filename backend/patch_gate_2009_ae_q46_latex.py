"""
Fix LaTeX / formatting for GATE_2009_AE_Q46.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2009_AE_Q46"

NEW_QUESTION_TEXT = (
    "The product of the eigenvalues of the matrix [[2,1,1],[1,3,1],[1,1,4]] is:"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The product of the eigenvalues of the matrix
    $$\mathbf{A}=\begin{bmatrix}
    2 & 1 & 1\\
    1 & 3 & 1\\
    1 & 1 & 4
    \end{bmatrix}$$
    is:
    """
).strip()

NEW_OPTIONS = {"A": "20", "B": "24", "C": "9", "D": "17"}

NEW_REASONING = dedent(
    r"""
    For any square matrix, product of eigenvalues equals determinant:
    $$\prod_{i=1}^{n}\lambda_i=\det(\mathbf{A}).$$

    So compute
    $$\det(\mathbf{A})=
    \det\!\begin{bmatrix}
    2 & 1 & 1\\
    1 & 3 & 1\\
    1 & 1 & 4
    \end{bmatrix}.$$

    Expanding along first row:
    $$\det(\mathbf{A})
    =2\begin{vmatrix}3&1\\1&4\end{vmatrix}
    -1\begin{vmatrix}1&1\\1&4\end{vmatrix}
    +1\begin{vmatrix}1&3\\1&1\end{vmatrix}.$$

    Evaluate minors:
    $$\begin{vmatrix}3&1\\1&4\end{vmatrix}=11,\quad
    \begin{vmatrix}1&1\\1&4\end{vmatrix}=3,\quad
    \begin{vmatrix}1&3\\1&1\end{vmatrix}=-2.$$

    Therefore
    $$\det(\mathbf{A})=2(11)-1(3)+1(-2)=22-3-2=17.$$

    Hence the product of eigenvalues is
    $$17,$$
    i.e. option **D**.
    """
).strip()

NEW_STEPS = [
    r"Recall property: $\det(\mathbf{A})=\prod_i \lambda_i$.",
    r"Write the given matrix in determinant form.",
    r"Expand determinant along first row.",
    r"Compute each $2\times2$ minor.",
    r"Substitute and simplify numeric expression.",
    r"Conclude product of eigenvalues equals $17$.",
]

NEW_FORMULAS_USED = [
    r"$\det(\mathbf{A})=\prod_{i=1}^{n}\lambda_i$",
    r"$\det\!\begin{bmatrix}a&b&c\\d&e&f\\g&h&i\end{bmatrix}=a(ei-fh)-b(di-fg)+c(dh-eg)$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Product of eigenvalues",
        "type": "equation",
        "formula": r"$\det(\mathbf{A})=\prod_{i=1}^{n}\lambda_i$",
        "conditions": "Square matrix; eigenvalues counted with algebraic multiplicity.",
        "relevance": "Directly converts asked quantity to determinant.",
    },
    {
        "name": "3x3 determinant expansion",
        "type": "equation",
        "formula": r"$\det\!\begin{bmatrix}a&b&c\\d&e&f\\g&h&i\end{bmatrix}=a(ei-fh)-b(di-fg)+c(dh-eg)$",
        "conditions": "Any 3x3 matrix.",
        "relevance": "Used to get final numerical value.",
    },
]

NEW_HINTS = [
    r"No need to compute individual eigenvalues.",
    r"Use determinant directly; this is a one-property question.",
    r"Watch cofactor signs $(+,-,+)$ in first-row expansion.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "What is the relation between determinant and eigenvalues?",
        "back": r"$\det(\mathbf{A})=\prod_i \lambda_i$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": "What is trace relation for eigenvalues?",
        "back": r"$\operatorname{tr}(\mathbf{A})=\sum_i \lambda_i$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"For $\mathbf{A}=\begin{bmatrix}2&1&1\\1&3&1\\1&1&4\end{bmatrix}$, find $\prod \lambda_i$.",
        "back": r"$17$",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Det means product",
        "concept": "Determinant gives eigenvalue product.",
        "effectiveness": "high",
        "context": "Quick eigenvalue-property recall",
    },
    {
        "mnemonic": "Trace sum, det product",
        "concept": "Keep sum/product roles separate.",
        "effectiveness": "high",
        "context": "Avoiding common confusion in MCQs",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": "Finding all eigenvalues explicitly instead of determinant.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Wastes time and increases error probability.",
        "how_to_avoid": "Apply determinant-product property first.",
        "why_students_make_it": "Defaults to full eigenvalue workflow.",
    },
    {
        "type": "Sign Error",
        "mistake": "Wrong sign in cofactor expansion.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Incorrect final answer.",
        "how_to_avoid": r"Use explicit $(+,-,+)$ sign pattern for first-row expansion.",
        "why_students_make_it": "Rushed arithmetic.",
    },
    {
        "type": "Conceptual",
        "mistake": "Mixing up trace and determinant properties.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Chooses wrong distractor.",
        "how_to_avoid": r"Memorize: $\sum\lambda_i=\operatorname{tr}(\mathbf{A})$, $\prod\lambda_i=\det(\mathbf{A})$.",
        "why_students_make_it": "Property recall confusion under pressure.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Immediately convert product-of-eigenvalues question to determinant computation.",
    "guessing_heuristic": "Avoid diagonal-product trap unless matrix is triangular.",
    "time_management": "1-2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Concept is direct once determinant-product property is recalled.",
    "Only challenge is clean 3x3 determinant arithmetic.",
]

NEW_ALT_METHODS = [
    {
        "name": "Characteristic polynomial constant term",
        "description": r"Form $p(\lambda)=\det(\lambda\mathbf{I}-\mathbf{A})$ and use constant term relation to read product of roots.",
        "pros_cons": "Pros: theory-consistent. Cons: longer than direct determinant evaluation.",
        "when_to_use": "When characteristic polynomial is already being computed.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "17"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Use eigenvalue-product property $\rightarrow$ compute determinant $\rightarrow$ finalize"
    sbs["key_insights"] = [
        "Product of eigenvalues can be computed without finding each eigenvalue.",
        "Correct cofactor signs determine correct determinant quickly.",
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

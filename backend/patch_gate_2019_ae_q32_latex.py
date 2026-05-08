"""
Fix GATE_2019_AE_Q32 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2019_ae_q32_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q32"

NEW_QUESTION_TEXT = (
    "One of the eigenvalues of the following matrix is 1.\n"
    "[[x, 2], [-1, 3]]\n"
    "The other eigenvalue is _______."
)

NEW_QUESTION_TEXT_LATEX = (
    "One of the eigenvalues of the following matrix is $1$.\n"
    "$$\\begin{pmatrix}x & 2 \\\\ -1 & 3\\end{pmatrix}$$\n"
    "The other eigenvalue is $\\underline{\\hspace{2cm}}$."
)

NEW_REASONING = (
    "Let the matrix be\n"
    "$$A=\\begin{pmatrix}x & 2 \\\\ -1 & 3\\end{pmatrix}$$\n"
    "and let the eigenvalues be $\\lambda_1=1$ and $\\lambda_2$.\n\n"
    "For a $2\\times 2$ matrix:\n"
    "$$\\lambda_1+\\lambda_2=\\operatorname{tr}(A),\\qquad "
    "\\lambda_1\\lambda_2=\\det(A)$$\n\n"
    "Compute trace and determinant:\n"
    "$$\\operatorname{tr}(A)=x+3,\\qquad \\det(A)=3x+2$$\n\n"
    "From sum of eigenvalues:\n"
    "$$1+\\lambda_2=x+3\\Rightarrow \\lambda_2=x+2$$\n\n"
    "From product of eigenvalues:\n"
    "$$1\\cdot \\lambda_2=3x+2\\Rightarrow \\lambda_2=3x+2$$\n\n"
    "Equate both expressions for $\\lambda_2$:\n"
    "$$x+2=3x+2\\Rightarrow x=0$$\n\n"
    "Hence:\n"
    "$$\\lambda_2=x+2=2$$\n\n"
    "Therefore, the other eigenvalue is $\\boxed{2}$."
)

NEW_HINTS = [
    "Use $\\lambda_1+\\lambda_2=\\operatorname{tr}(A)$ for a $2\\times2$ matrix.",
    "Use $\\lambda_1\\lambda_2=\\det(A)$ and write both equations in terms of $x$ and $\\lambda_2$.",
    "Eliminate $x$ by equating the two expressions for $\\lambda_2$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Write the matrix as $A=\\begin{pmatrix}x & 2 \\\\ -1 & 3\\end{pmatrix}$ and use the given eigenvalue $\\lambda_1=1$.",
    "Step 2: Compute trace and determinant: $\\operatorname{tr}(A)=x+3$, $\\det(A)=3x+2$.",
    "Step 3: From $\\lambda_1+\\lambda_2=\\operatorname{tr}(A)$, get $1+\\lambda_2=x+3$, so $\\lambda_2=x+2$.",
    "Step 4: From $\\lambda_1\\lambda_2=\\det(A)$, get $1\\cdot\\lambda_2=3x+2$, so $\\lambda_2=3x+2$.",
    "Step 5: Equate: $x+2=3x+2\\Rightarrow x=0$.",
    "Step 6: Substitute into $\\lambda_2=x+2$ to get $\\lambda_2=2$.",
]

NEW_FORMULAS_USED = [
    "$\\lambda_1+\\lambda_2=\\operatorname{tr}(A)$",
    "$\\lambda_1\\lambda_2=\\det(A)$",
]

NEW_SOLUTION_PATH = (
    "Apply trace and determinant eigenvalue identities, solve for $x$, then compute the second eigenvalue."
)

NEW_KEY_INSIGHTS = [
    "For $2\\times2$ matrices, trace gives eigenvalue sum and determinant gives eigenvalue product.",
    "Using both identities removes ambiguity and gives a unique second eigenvalue.",
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = 6

    t1["hints"] = NEW_HINTS
    return t1


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT question_text, question_text_latex, options, tier_1_core_research "
                "FROM questions WHERE question_id = :qid"
            ),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        existing_options = row[2]
        new_t1 = patch_tier_1(row[3])

        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "options = CAST(:opts AS jsonb), "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(existing_options),
                "t1": json.dumps(new_t1),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: question/options/solution/hints/steps LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

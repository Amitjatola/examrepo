"""
Fix GATE_2016_AE_Q09 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2016_ae_q09_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2016_AE_Q09"

NEW_QUESTION_TEXT = (
    "Consider an eigenvalue problem given by Ax = lambda_i x. If lambda_i represents the eigenvalues "
    "of the non-singular square matrix A, what will be the eigenvalues of matrix A^2?"
)

NEW_QUESTION_TEXT_LATEX = (
    "Consider an eigenvalue problem given by $A\\mathbf{x}=\\lambda_i\\mathbf{x}$. If $\\lambda_i$ represents "
    "the eigenvalues of a non-singular square matrix $A$, then what are the eigenvalues of $A^2$?"
)

NEW_OPTIONS = {
    "A": "$\\lambda_i^4$",
    "B": "$\\lambda_i^2$",
    "C": "$\\lambda_i^{1/2}$",
    "D": "$\\lambda_i^{1/4}$",
}

NEW_REASONING = (
    "Given $A\\mathbf{x}=\\lambda_i\\mathbf{x}$ for a non-zero eigenvector $\\mathbf{x}$, apply $A$ once more:\n"
    "$A^2\\mathbf{x}=A(A\\mathbf{x})=A(\\lambda_i\\mathbf{x})=\\lambda_i(A\\mathbf{x})"
    "=\\lambda_i(\\lambda_i\\mathbf{x})=\\lambda_i^2\\mathbf{x}$.\n"
    "Hence $\\mathbf{x}$ remains an eigenvector and the corresponding eigenvalue for $A^2$ is $\\lambda_i^2$. "
    "Therefore the correct option is $\\mathbf{B}$."
)

NEW_HINTS = [
    "Start from $A\\mathbf{x}=\\lambda\\mathbf{x}$ and multiply by $A$ on the left once more.",
    "Use scalar factoring: $A(\\lambda\\mathbf{x})=\\lambda(A\\mathbf{x})$.",
    "Compare final form with eigenvalue definition for $A^2$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Recall eigenvalue definition: if $A\\mathbf{x}=\\lambda\\mathbf{x}$ with $\\mathbf{x}\\neq\\mathbf{0}$, "
    "then $\\lambda$ is an eigenvalue of $A$.",
    "Step 2: To get eigenvalues of $A^2$, evaluate $A^2\\mathbf{x}=A(A\\mathbf{x})$.",
    "Step 3: Substitute $A\\mathbf{x}=\\lambda_i\\mathbf{x}$: "
    "$A^2\\mathbf{x}=A(\\lambda_i\\mathbf{x})$.",
    "Step 4: Pull out scalar $\\lambda_i$: "
    "$A(\\lambda_i\\mathbf{x})=\\lambda_i(A\\mathbf{x})$.",
    "Step 5: Substitute again $A\\mathbf{x}=\\lambda_i\\mathbf{x}$: "
    "$A^2\\mathbf{x}=\\lambda_i(\\lambda_i\\mathbf{x})=\\lambda_i^2\\mathbf{x}$.",
    "Step 6: This matches eigenvalue form for $A^2$, so eigenvalues become $\\lambda_i^2$.",
    "Step 7: Therefore, correct option is $\\mathbf{B}$.",
]

NEW_FORMULAS_USED = [
    "$A\\mathbf{x}=\\lambda\\mathbf{x}$",
    "$A^2\\mathbf{x}=A(A\\mathbf{x})$",
    "$A^m\\mathbf{x}=\\lambda^m\\mathbf{x}$",
]

NEW_SOLUTION_PATH = (
    "Use eigenvalue definition $\\rightarrow$ apply $A$ again $\\rightarrow$ factor scalar $\\lambda_i$ "
    "$\\rightarrow$ obtain $A^2\\mathbf{x}=\\lambda_i^2\\mathbf{x}$."
)

NEW_KEY_INSIGHTS = [
    "Raising matrix power raises each eigenvalue by the same power for the same eigenvector.",
    "For $A^2$, each eigenvalue transforms as $\\lambda_i\\mapsto\\lambda_i^2$.",
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
    sbs["total_steps"] = 7

    t1["hints"] = NEW_HINTS
    return t1


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT tier_1_core_research FROM questions WHERE question_id = :qid"),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        new_t1 = patch_tier_1(row[0])

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
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(new_t1),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: question/options/hints/solution/steps LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

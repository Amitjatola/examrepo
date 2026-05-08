"""
Fix GATE_2023_AE_Q31 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2023_ae_q31_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q31"

NEW_QUESTION_TEXT = (
    "The system of equations x - 2y + alpha z = 0, 2x + y - 4z = 0, x - y + z = 0 "
    "has a non-trivial solution for alpha = _____. (Answer in integer)"
)

NEW_QUESTION_TEXT_LATEX = (
    "The system of equations\n"
    "$x-2y+\\alpha z=0$\n"
    "$2x+y-4z=0$\n"
    "$x-y+z=0$\n"
    "has a non-trivial solution for $\\alpha=\\underline{\\qquad}$ (answer in integer)."
)

NEW_REASONING = (
    "For a homogeneous linear system $A\\mathbf{x}=\\mathbf{0}$ to have a non-trivial solution, "
    "the coefficient matrix must be singular, i.e. $\\det(A)=0$.\n"
    "Here,\n"
    "$A=\\begin{bmatrix}1&-2&\\alpha\\\\2&1&-4\\\\1&-1&1\\end{bmatrix}$.\n"
    "Compute determinant along first row:\n"
    "$\\det(A)=1\\begin{vmatrix}1&-4\\\\-1&1\\end{vmatrix}"
    "-(-2)\\begin{vmatrix}2&-4\\\\1&1\\end{vmatrix}"
    "+\\alpha\\begin{vmatrix}2&1\\\\1&-1\\end{vmatrix}$\n"
    "$=1(1-4)+2(2+4)+\\alpha(-2-1)$\n"
    "$=-3+12-3\\alpha=9-3\\alpha$.\n"
    "Set $\\det(A)=0$:\n"
    "$9-3\\alpha=0\\Rightarrow\\alpha=3$.\n"
    "Hence the required integer is $\\boxed{3}$."
)

NEW_HINTS = [
    "Form coefficient matrix $A$ from the given equations.",
    "Use non-trivial solution condition for homogeneous system: $\\det(A)=0$.",
    "Expand determinant and solve linear equation in $\\alpha$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Write system as $A\\mathbf{x}=\\mathbf{0}$ with "
    "$A=\\begin{bmatrix}1&-2&\\alpha\\\\2&1&-4\\\\1&-1&1\\end{bmatrix}$.",
    "Step 2: For a homogeneous $3\\times3$ system, non-trivial solution exists iff $\\det(A)=0$.",
    "Step 3: Expand determinant along first row:\n"
    "$\\det(A)=1\\begin{vmatrix}1&-4\\\\-1&1\\end{vmatrix}"
    "-(-2)\\begin{vmatrix}2&-4\\\\1&1\\end{vmatrix}"
    "+\\alpha\\begin{vmatrix}2&1\\\\1&-1\\end{vmatrix}$.",
    "Step 4: Evaluate minors:\n"
    "$\\begin{vmatrix}1&-4\\\\-1&1\\end{vmatrix}=-3$, "
    "$\\begin{vmatrix}2&-4\\\\1&1\\end{vmatrix}=6$, "
    "$\\begin{vmatrix}2&1\\\\1&-1\\end{vmatrix}=-3$.",
    "Step 5: Substitute: $\\det(A)=-3+2\\cdot6+\\alpha(-3)=9-3\\alpha$.",
    "Step 6: Set $9-3\\alpha=0$ and solve: $\\alpha=3$.",
    "Step 7: Therefore the system has non-trivial solution at $\\boxed{\\alpha=3}$.",
]

NEW_FORMULAS_USED = [
    "$A\\mathbf{x}=\\mathbf{0}$",
    "$\\det(A)=0$ (non-trivial solution condition for homogeneous square system)",
    "$\\det\\begin{bmatrix}a&b&c\\\\d&e&f\\\\g&h&i\\end{bmatrix}=a(ei-fh)-b(di-fg)+c(dh-eg)$",
    "$\\det\\begin{bmatrix}a&b\\\\c&d\\end{bmatrix}=ad-bc$",
]

NEW_SOLUTION_PATH = (
    "Form coefficient matrix $\\rightarrow$ apply singularity condition $\\det(A)=0$ "
    "$\\rightarrow$ compute determinant in terms of $\\alpha$ $\\rightarrow$ solve."
)

NEW_KEY_INSIGHTS = [
    "Homogeneous square system has non-trivial solution iff determinant is zero.",
    "Problem reduces to one-variable linear equation after determinant expansion.",
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
            text("SELECT tier_1_core_research, options FROM questions WHERE question_id = :qid"),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        new_t1 = patch_tier_1(row[0])
        existing_options = row[1]

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

    print(f"Patched {PUBLIC_ID}: question/solution/hints/steps LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

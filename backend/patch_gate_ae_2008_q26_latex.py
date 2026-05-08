"""
Fix GATE_AE_2008_Q26 LaTeX fields for frontend rendering.

Usage (from backend/):
  ./venv/bin/python patch_gate_ae_2008_q26_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_AE_2008_Q26"

NEW_QUESTION_TEXT = (
    "Which of the following is a solution of d2y/dx2 + 2(dy/dx) + y = 0?"
)

NEW_QUESTION_TEXT_LATEX = (
    "Which of the following is a solution of "
    "$\\dfrac{d^2y}{dx^2}+2\\dfrac{dy}{dx}+y=0$?"
)

NEW_OPTIONS = {
    "A": "$e^{-x}+x e^{-x}$",
    "B": "$e^{x}+x e^{-x}$",
    "C": "$e^{x}+e^{-x}$",
    "D": "$e^{-x}+x e^{x}$",
}

NEW_REASONING = (
    "Given ODE:\n"
    "$$\\dfrac{d^2y}{dx^2}+2\\dfrac{dy}{dx}+y=0$$\n\n"
    "Assume $y=e^{mx}$. Then the characteristic equation is\n"
    "$$m^2+2m+1=0=(m+1)^2$$\n"
    "So the repeated root is $m=-1$.\n\n"
    "For a repeated root $m$, solution form is\n"
    "$$y=(C_1+C_2x)e^{mx}$$\n"
    "Hence\n"
    "$$y=(C_1+C_2x)e^{-x}=C_1e^{-x}+C_2xe^{-x}$$\n\n"
    "Option $A$ is $e^{-x}+xe^{-x}$, which matches this form.\n"
    "Therefore the correct option is $\\mathbf{A}$."
)

NEW_HINTS = [
    "Use trial solution $y=e^{mx}$ and form the auxiliary equation.",
    "Check whether the root is repeated or distinct.",
    "For repeated root $m$, solution is $(C_1+C_2x)e^{mx}$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Start with $\\dfrac{d^2y}{dx^2}+2\\dfrac{dy}{dx}+y=0$.",
    "Step 2: Put $y=e^{mx}$ to get auxiliary equation $m^2+2m+1=0$.",
    "Step 3: Factor: $(m+1)^2=0$, so root is repeated: $m=-1$.",
    "Step 4: Write general solution for repeated root: $y=(C_1+C_2x)e^{-x}$.",
    "Step 5: Compare options; only $e^{-x}+xe^{-x}$ matches.",
    "Step 6: Therefore correct answer is option $A$.",
]

NEW_FORMULAS_USED = [
    "$m^2+2m+1=0$",
    "$y=(C_1+C_2x)e^{mx}$ for repeated root",
]

NEW_SOLUTION_PATH = (
    "Form characteristic equation, identify repeated root, write repeated-root solution, match option."
)

NEW_KEY_INSIGHTS = [
    "Repeated characteristic root introduces the extra factor $x$.",
    "Only expressions of form $(a+bx)e^{-x}$ can satisfy this ODE.",
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

    print(f"Patched {PUBLIC_ID}: question/options/solution/hints/steps LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

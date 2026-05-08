"""
Fix GATE_AE_2008_Q30 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_ae_2008_q30_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_AE_2008_Q30"

NEW_QUESTION_TEXT = (
    "Let Y(s) denote the Laplace transform L(y(t)) of the function "
    "y(t) = cosh(at) sin(at). Then"
)

NEW_QUESTION_TEXT_LATEX = (
    "Let $Y(s)$ denote the Laplace transform $\\mathcal{L}\\{y(t)\\}$ of "
    "$y(t)=\\cosh(at)\\sin(at)$. Then"
)

NEW_OPTIONS = {
    "A": "$\\mathcal{L}\\!\\left\\{\\dfrac{dy}{dt}\\right\\}=\\dfrac{dY}{ds},\\; "
         "\\mathcal{L}\\{t\\,y(t)\\}=sY(s)$",
    "B": "$\\mathcal{L}\\!\\left\\{\\dfrac{dy}{dt}\\right\\}=sY(s),\\; "
         "\\mathcal{L}\\{t\\,y(t)\\}=-\\dfrac{dY}{ds}$",
    "C": "$\\mathcal{L}\\!\\left\\{\\dfrac{dy}{dt}\\right\\}=\\dfrac{dY}{ds},\\; "
         "\\mathcal{L}\\{t\\,y(t)\\}=Y(s-1)$",
    "D": "$\\mathcal{L}\\!\\left\\{\\dfrac{dy}{dt}\\right\\}=sY(s),\\; "
         "\\mathcal{L}\\{t\\,y(t)\\}=e^{as}Y(s)$",
}

NEW_REASONING = (
    "Use standard Laplace properties. For derivative,\n"
    "$\\mathcal{L}\\!\\left\\{\\dfrac{dy}{dt}\\right\\}=sY(s)-y(0)$.\n"
    "In MCQ property matching, options commonly use the simplified form $sY(s)$ when "
    "initial term is omitted. For multiplication by time,\n"
    "$\\mathcal{L}\\{t\\,y(t)\\}=-\\dfrac{dY}{ds}$.\n"
    "Comparing with the options, only option $\\mathbf{B}$ matches both identities."
)

NEW_HINTS = [
    "Recall derivative property: $\\mathcal{L}\\{y'(t)\\}=sY(s)-y(0)$.",
    "Recall time-multiplication property: $\\mathcal{L}\\{t f(t)\\}=-\\dfrac{d}{ds}F(s)$.",
    "Question is property-based; you do not need explicit transform of $\\cosh(at)\\sin(at)$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Identify what is asked: two Laplace properties involving $y'(t)$ and $t\\,y(t)$.",
    "Step 2: Write derivative property: "
    "$\\mathcal{L}\\!\\left\\{\\dfrac{dy}{dt}\\right\\}=sY(s)-y(0)$.",
    "Step 3: In property-style options, the displayed part is usually $sY(s)$ "
    "(initial term may be omitted).",
    "Step 4: Write time-multiplication property: "
    "$\\mathcal{L}\\{t\\,y(t)\\}=-\\dfrac{dY}{ds}$.",
    "Step 5: Compare options against these two expressions.",
    "Step 6: Option $B$ is the only one that matches both properties.",
]

NEW_FORMULAS_USED = [
    "$\\mathcal{L}\\{y'(t)\\}=sY(s)-y(0)$",
    "$\\mathcal{L}\\{t f(t)\\}=-\\dfrac{d}{ds}F(s)$",
]

NEW_SOLUTION_PATH = (
    "Recall Laplace identities $\\rightarrow$ match derivative rule $\\rightarrow$ "
    "match $t$-multiplication rule $\\rightarrow$ choose consistent option."
)

NEW_KEY_INSIGHTS = [
    "The second relation is exact: $\\mathcal{L}\\{t y(t)\\}=-dY/ds$.",
    "The first relation includes initial condition term; MCQ often presents simplified $sY(s)$ form.",
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

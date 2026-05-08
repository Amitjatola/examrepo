"""
Fix GATE_2012_AE_Q31 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2012_ae_q31_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2012_AE_Q31"

NEW_QUESTION_TEXT = "The $n$th derivative of the function $y=\\dfrac{1}{x+3}$ is"
NEW_QUESTION_TEXT_LATEX = "The $n$th derivative of the function $y=\\dfrac{1}{x+3}$ is"

NEW_OPTIONS = {
    "A": "$\\dfrac{(-1)^n n!}{(x+3)^{n+1}}$",
    "B": "$\\dfrac{(-1)^{n+1} n!}{(x+3)^{n+1}}$",
    "C": "$\\dfrac{(-1)^n (n+1)!}{(x+3)^n}$",
    "D": "$\\dfrac{(-1)^n n!}{(x+3)^n}$",
}

NEW_REASONING = (
    "Rewrite $y=\\dfrac{1}{x+3}$ as $y=(x+3)^{-1}$. Differentiate repeatedly:\n"
    "$y'=-1(x+3)^{-2}$,\n"
    "$y''=2(x+3)^{-3}$,\n"
    "$y'''=-6(x+3)^{-4}$.\n"
    "The signs alternate as $(-1)^n$, coefficients follow $n!$, and power becomes $-(n+1)$. "
    "Hence\n"
    "$y^{(n)}=\\dfrac{(-1)^n n!}{(x+3)^{n+1}}$, which matches option $\\mathbf{A}$."
)

NEW_HINTS = [
    "First rewrite $\\dfrac{1}{x+3}$ as $(x+3)^{-1}$.",
    "Differentiate first 2-3 times and inspect coefficient/sign pattern.",
    "Use the general derivative form for powers of $(x+a)$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Rewrite the function in power form: $y=(x+3)^{-1}$.",
    "Step 2: First derivative: $y'=-1(x+3)^{-2}$.",
    "Step 3: Second derivative: $y''=2(x+3)^{-3}$.",
    "Step 4: Third derivative: $y'''=-6(x+3)^{-4}$.",
    "Step 5: Identify patterns: sign $(-1)^n$, coefficient $n!$, exponent $-(n+1)$.",
    "Step 6: Therefore, $y^{(n)}=(-1)^n n!(x+3)^{-(n+1)}=\\dfrac{(-1)^n n!}{(x+3)^{n+1}}$.",
    "Step 7: Match with options: correct answer is $\\mathbf{A}$.",
]

NEW_FORMULAS_USED = [
    "$y=(x+3)^{-1}$",
    "$\\dfrac{d}{dx}(u^k)=k u^{k-1}\\dfrac{du}{dx}$",
    "$\\dfrac{d^n}{dx^n}(x+a)^m=m(m-1)\\cdots(m-n+1)(x+a)^{m-n}$",
    "$n!=n(n-1)\\cdots1$",
]

NEW_SOLUTION_PATH = (
    "Rewrite as negative power $\\rightarrow$ compute first derivatives $\\rightarrow$ detect factorial and sign pattern "
    "$\\rightarrow$ write general $n$th derivative $\\rightarrow$ match options."
)

NEW_KEY_INSIGHTS = [
    "Converting reciprocal form to negative exponent makes repeated differentiation straightforward.",
    "Each differentiation contributes one additional negative integer factor, producing $(-1)^n n!$.",
    "Denominator power is always one more than derivative order: $(x+3)^{n+1}$.",
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

    print(f"Patched {PUBLIC_ID}: question, options, hints, steps, and solution LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

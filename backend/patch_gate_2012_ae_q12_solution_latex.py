"""
Fix solution LaTeX for GATE_2012_AE_Q12.

Usage (from backend/):
  ./venv/bin/python patch_gate_2012_ae_q12_solution_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2012_AE_Q12"

NEW_REASONING = (
    "Given differential equation:\n"
    "$$m\\frac{d^2x}{dt^2}+kx=u(t)$$\n"
    "where $u(t)$ is the unit step input.\n\n"
    "Taking Laplace transform on both sides:\n"
    "$$m\\,\\mathcal{L}\\!\\left\\{\\frac{d^2x}{dt^2}\\right\\}+k\\,\\mathcal{L}\\{x(t)\\}=\\mathcal{L}\\{u(t)\\}$$\n\n"
    "Use standard transforms:\n"
    "$$\\mathcal{L}\\!\\left\\{\\frac{d^2x}{dt^2}\\right\\}=s^2X(s)-s x(0)-\\dot{x}(0),\\quad "
    "\\mathcal{L}\\{x(t)\\}=X(s),\\quad \\mathcal{L}\\{u(t)\\}=\\frac{1}{s}$$\n\n"
    "Assuming zero initial conditions $x(0)=0$ and $\\dot{x}(0)=0$:\n"
    "$$m\\left(s^2X(s)\\right)+kX(s)=\\frac{1}{s}$$\n"
    "$$X(s)\\,(ms^2+k)=\\frac{1}{s}$$\n"
    "$$X(s)=\\frac{1}{s\\,(ms^2+k)}$$\n\n"
    "Hence the correct option is $\\mathbf{A}$."
)


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})
    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
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
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "t1": json.dumps(new_t1),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: solution reasoning LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

"""
Patch GATE_2021_AE_Q1: proper \\frac in stem + options.

Issue: stem used \\text{...} interleaved with \\frac; some clients rendered
commands as prose ('fracdydx'). Use explicit $...$ math spans only.

Usage (from backend/):
  venv/bin/python patch_gate_2021_ae_q1_latex.py
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2021_AE_Q1"

NEW_QUESTION_TEXT_LATEX = (
    "Consider the differential equation "
    "$\\frac{d^2y}{dx^2} + 8\\frac{dy}{dx} + 16y = 0$ "
    "and the boundary conditions $y(0)=1$ and $\\frac{dy}{dx}(0)=0$. "
    "The solution to this equation is:"
)

NEW_QUESTION_TEXT = (
    "Consider the differential equation "
    "d\u00b2y/dx\u00b2 + 8(dy/dx) + 16y = 0 "
    "and the boundary conditions y(0) = 1 and (dy/dx)(0) = 0. "
    "The solution to this equation is:"
)

NEW_OPTIONS = {
    "A": "$y = (1+2x)e^{-4x}$",
    "B": "$y = (1-4x)e^{-4x}$",
    "C": "$y = (1+8x)e^{-4x}$",
    "D": "$y = (1+4x)e^{-4x}$",
}


async def main() -> None:
    opts_json = json.dumps(NEW_OPTIONS)
    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT question_id FROM questions WHERE question_id = :qid"),
            {"qid": QID},
        )
        if not res.fetchone():
            raise SystemExit(f"Question {QID} not found in DB")

        await conn.execute(
            text(
                "UPDATE questions "
                "SET question_text_latex = :qtl, "
                "    question_text = :qt, "
                "    options = CAST(:opts AS jsonb), "
                "    updated_at = :ts "
                "WHERE question_id = :qid"
            ),
            {
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "qt": NEW_QUESTION_TEXT,
                "opts": opts_json,
                "ts": datetime.utcnow(),
                "qid": QID,
            },
        )

    print(f"Patched {QID}: question_text_latex, question_text, options updated.")


if __name__ == "__main__":
    asyncio.run(main())

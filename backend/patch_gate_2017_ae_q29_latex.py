"""
Patch GATE_2017_AE_Q29: full prose + properly delimited KaTeX stem.

Issue: question_text_latex held only a short PDE fragment, so questionStem.js
preferred plain question_text (ASCII d^2u/dt^2, etc.) and math did not render.

Usage (from backend/):
  venv/bin/python patch_gate_2017_ae_q29_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2017_AE_Q29"

NEW_QUESTION_TEXT_LATEX = (
    "Let $u(x,t)$ denote the displacement of a point on a rod. "
    "The displacement satisfies the following equation of motion:\n"
    "$$\\frac{\\partial^2 u}{\\partial t^2} - 25\\frac{\\partial^2 u}{\\partial x^2} = 0,\\quad 0<x<1$$\n"
    "with $u(x,0)=0.01\\sin(10\\pi x)$, $\\frac{\\partial u}{\\partial t}(x,0)=0$; "
    "$u(0,t)=0$, $u(1,t)=0$. "
    "The value of $u(0.25,1)$ is $\\underline{\\hspace{6em}}$ (in three decimal places)."
)

NEW_QUESTION_TEXT = (
    "Let u(x, t) denote the displacement of a point on a rod. "
    "The displacement satisfies the following equation of motion: "
    "\u2202\u00b2u/\u2202t\u00b2 - 25 \u2202\u00b2u/\u2202x\u00b2 = 0, 0 < x < 1 "
    "with u(x, 0) = 0.01 sin(10\u03c0 x), \u2202u/\u2202t (x, 0) = 0; "
    "u(0, t) = 0, u(1, t) = 0. "
    "The value of u(0.25, 1) is ________ (in three decimal places)."
)


async def main() -> None:
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
                "    updated_at = :ts "
                "WHERE question_id = :qid"
            ),
            {
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "qt": NEW_QUESTION_TEXT,
                "ts": datetime.utcnow(),
                "qid": QID,
            },
        )

    print(f"Patched {QID}: question_text_latex and question_text updated.")


if __name__ == "__main__":
    asyncio.run(main())

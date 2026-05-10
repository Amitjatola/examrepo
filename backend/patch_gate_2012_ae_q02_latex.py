"""
Fix GATE_2012_AE_Q02: ODE stem + options KaTeX-safe.

Issues:
  - question_text_latex used \\text{...} around prose + bare \\frac which interacts badly with
    LatexRenderer unwrap/heuristics; users saw "fracd^2y" without backslashes.
  - options lacked $...$ delimiters so exponentials did not render reliably.

Usage (from backend/):
  venv/bin/python patch_gate_2012_ae_q02_latex.py
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2012_AE_Q02"

NEW_QUESTION_TEXT = (
    "The general solution of the differential equation (d^2 y)/(dt^2) + (dy)/(dt) - 2y = 0 is"
)

NEW_QUESTION_TEXT_LATEX = (
    r"The general solution of the differential equation "
    r"$$\dfrac{d^2y}{dt^2}+\dfrac{dy}{dt}-2y=0$$ "
    r"is"
)

NEW_OPTIONS = {
    "A": r"$Ae^{-t}+Be^{2t}$",
    "B": r"$Ae^{-2t}+Be^{-t}$",
    "C": r"$Ae^{-2t}+Be^{t}$",
    "D": r"$Ae^{t}+Be^{2t}$",
}


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT question_id FROM questions WHERE question_id=:q"), {"q": QID})
        if not res.fetchone():
            raise SystemExit(f"{QID} not found")

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, "
                "options=CAST(:opts AS jsonb), updated_at=:ts WHERE question_id=:qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "ts": datetime.utcnow(),
                "qid": QID,
            },
        )

    print(f"Patched {QID}")


if __name__ == "__main__":
    asyncio.run(main())

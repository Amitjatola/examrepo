"""
Patch GATE_2017_AE_Q55: full stem with \\omega_n, \\sqrt{}, degrees.

Issue: question_text_latex was a short fragment; UI fell back to ASCII
omega_n = a sqrt(k/m).

Usage (from backend/):
  venv/bin/python patch_gate_2017_ae_q55_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2017_AE_Q55"

NEW_QUESTION_TEXT_LATEX = (
    "The natural frequency of the system suspended by two identical springs of stiffness "
    "$k$ as shown in the figure is given by $\\omega_n = a\\sqrt{\\dfrac{k}{m}}$ for small "
    "displacement. Both the springs make an angle of $45^\\circ$ with the horizontal. "
    "The value of $a$ is $\\underline{\\hspace{6em}}$ (in two decimal places)."
)

NEW_QUESTION_TEXT = (
    "The natural frequency of the system suspended by two identical springs of stiffness k "
    "as shown in the figure is given by \u03c9_n = a \u221a(k/m) for small displacement. "
    "Both the springs make an angle of 45\u00b0 with the horizontal. "
    "The value of a is ________ (in two decimal places)."
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

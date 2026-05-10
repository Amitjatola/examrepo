"""
Patch GATE_2022_AE_Q63: full stem question_text_latex with \\omega_1, \\omega_2.

Issue: question_text_latex was only "m, \\omega_1, \\omega_2" so selectQuestionStemText
preferred plain question_text with literal "omega1"/"omega2".

Usage (from backend/):
  venv/bin/python patch_gate_2022_ae_q63_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2022_AE_Q63"

NEW_QUESTION_TEXT_LATEX = (
    "A uniform rigid prismatic bar of total mass $m$ is suspended from a ceiling by "
    "two identical springs as shown in figure. Let $\\omega_1$ and $\\omega_2$ be the "
    "natural frequencies of mode I and mode II respectively ($\\omega_1 < \\omega_2$). "
    "The value of $\\omega_2/\\omega_1$ is $\\underline{\\hspace{6em}}$ "
    "(rounded off to one decimal place)."
)

NEW_QUESTION_TEXT = (
    "A uniform rigid prismatic bar of total mass m is suspended from a ceiling by "
    "two identical springs as shown in figure. Let \u03c9\u2081 and \u03c9\u2082 be the "
    "natural frequencies of mode I and mode II respectively (\u03c9\u2081 < \u03c9\u2082). "
    "The value of \u03c9\u2082/\u03c9\u2081 is _________ (rounded off to one decimal place)."
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

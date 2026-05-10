"""
Patch GATE_2020_AE_Q30: fix broken matrix LaTeX in question_text_latex.

Issues in existing string:
  - \\_ used for subscripts (should be _)
  - \\ followed by space used as row separator (should be \\\\)
  - \\& used as column separator (should be &)

This caused KaTeX to render all matrix entries on one line -> horizontal overflow.

Usage (from backend/):
  venv/bin/python patch_gate_2020_ae_q30_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2020_AE_Q30"

NEW_QUESTION_TEXT_LATEX = (
    "The three dimensional strain-stress relation for an isotropic material, "
    "written in a general matrix form, is\n\n"
    "$$\\begin{Bmatrix} \\epsilon_{xx} \\\\ \\epsilon_{yy} \\\\ \\epsilon_{zz} \\\\ "
    "\\gamma_{yz} \\\\ \\gamma_{xz} \\\\ \\gamma_{xy} \\end{Bmatrix} = "
    "\\begin{bmatrix} "
    "A & C & C & 0 & 0 & 0 \\\\ "
    "C & A & C & 0 & 0 & 0 \\\\ "
    "C & C & A & 0 & 0 & 0 \\\\ "
    "0 & 0 & 0 & B & 0 & 0 \\\\ "
    "0 & 0 & 0 & 0 & B & 0 \\\\ "
    "0 & 0 & 0 & 0 & 0 & B "
    "\\end{bmatrix} "
    "\\begin{Bmatrix} \\sigma_{xx} \\\\ \\sigma_{yy} \\\\ \\sigma_{zz} \\\\ "
    "\\tau_{yz} \\\\ \\tau_{xz} \\\\ \\tau_{xy} \\end{Bmatrix}$$\n\n"
    "$A$, $B$ and $C$ are compliances which depend on the elastic properties "
    "of the material. Which one of the following is correct?"
)


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT question_id FROM questions WHERE question_id = :qid"),
            {"qid": QID},
        )
        if not res.fetchone():
            raise SystemExit(f"{QID} not found in DB")

        await conn.execute(
            text(
                "UPDATE questions "
                "SET question_text_latex = :qtl, updated_at = :ts "
                "WHERE question_id = :qid"
            ),
            {"qtl": NEW_QUESTION_TEXT_LATEX, "ts": datetime.utcnow(), "qid": QID},
        )

    print(f"Patched {QID}: question_text_latex fixed.")


if __name__ == "__main__":
    asyncio.run(main())

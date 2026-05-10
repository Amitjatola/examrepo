"""
Patch GATE_2024_AE_Q13: fix broken matrix LaTeX in question_text_latex.

Same broken pattern as Q30:
  - \\_ used for subscripts  -> _
  - \\ followed by space as row separator -> \\\\
  - \\& as column separator -> &

Usage (from backend/):
  venv/bin/python patch_gate_2024_ae_q13_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2024_AE_Q13"

NEW_QUESTION_TEXT_LATEX = (
    "The three-dimensional stress-strain relationship for an isotropic material is given as\n"
    "$$\\begin{Bmatrix} \\sigma_{xx} \\\\ \\sigma_{yy} \\\\ \\sigma_{zz} \\\\ "
    "\\tau_{yz} \\\\ \\tau_{xz} \\\\ \\tau_{xy} \\end{Bmatrix} = "
    "\\begin{bmatrix} "
    "P & Q & Q & 0 & 0 & 0 \\\\ "
    "Q & P & Q & 0 & 0 & 0 \\\\ "
    "Q & Q & P & 0 & 0 & 0 \\\\ "
    "0 & 0 & 0 & R & 0 & 0 \\\\ "
    "0 & 0 & 0 & 0 & R & 0 \\\\ "
    "0 & 0 & 0 & 0 & 0 & R "
    "\\end{bmatrix} "
    "\\begin{Bmatrix} \\epsilon_{xx} \\\\ \\epsilon_{yy} \\\\ \\epsilon_{zz} \\\\ "
    "\\gamma_{yz} \\\\ \\gamma_{xz} \\\\ \\gamma_{xy} \\end{Bmatrix}$$\n"
    "where, $P$, $Q$ and $R$ are the three elastic constants, $\\sigma$ and $\\tau$ "
    "represent normal and shear stresses and $\\epsilon$ and $\\gamma$ represent normal "
    "and engineering shear strains. Which one of the following options is correct?"
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

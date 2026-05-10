"""
Patch GATE_2012_AE_Q30: full stem with bmatrix mode shapes, Hz, mm, blank.

Issue: question_text_latex was a short fragment; plain text showed {1 0.5}^T etc.

Usage (from backend/):
  venv/bin/python patch_gate_2012_ae_q30_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2012_AE_Q30"

NEW_QUESTION_TEXT_LATEX = (
    "The mode shapes of an un-damped two degrees of freedom system are "
    "$\\begin{bmatrix} 1 \\\\ 0.5 \\end{bmatrix}$ and "
    "$\\begin{bmatrix} 1 \\\\ -0.675 \\end{bmatrix}$. "
    "The corresponding natural frequencies are "
    "$0.45\\ \\mathrm{Hz}$ and $1.2471\\ \\mathrm{Hz}$. "
    "The maximum amplitude (in mm) of vibration of the first degree of freedom "
    "due to an initial displacement of $\\begin{bmatrix} 2 \\\\ 1 \\end{bmatrix}$ "
    "(in mm) and zero initial velocities is $\\underline{\\hspace{6em}}$."
)

NEW_QUESTION_TEXT = (
    "The mode shapes of an un-damped two degrees of freedom system are "
    "[1; 0.5] and [1; \u22120.675] (column vectors). "
    "The corresponding natural frequencies are 0.45 Hz and 1.2471 Hz. "
    "The maximum amplitude (in mm) of vibration of the first degree of freedom "
    "due to an initial displacement of [2; 1] (in mm) and zero initial velocities "
    "is _________."
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

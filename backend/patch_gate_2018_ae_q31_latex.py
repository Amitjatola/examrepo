"""
Patch GATE_2018_AE_Q31: add question_text_latex with proper inline KaTeX math.

Root issue: question_text_latex was NULL so the app fell back to question_text
which contained raw ASCII tokens (epsilon_zz, sigma_zz, !=) instead of math.

Usage (from backend/):
  venv/bin/python patch_gate_2018_ae_q31_latex.py
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2018_AE_Q31"

NEW_QUESTION_TEXT_LATEX = (
    "Which of the following statement(s) is/are true about the state of a body "
    "in plane strain condition? "
    "P: All the points in the body undergo displacements in one plane only, "
    "for example the $x$-$y$ plane, leading to "
    "$\\epsilon_{zz}=\\gamma_{xz}=\\gamma_{yz}=0$. "
    "Q: All the components of stress perpendicular to the plane of deformation, "
    "for example the $x$-$y$ plane, of the body are equal to zero, i.e.\\ "
    "$\\sigma_{zz}=\\tau_{xz}=\\tau_{yz}=0$. "
    "R: Except the normal component, all the other components of stress "
    "perpendicular to the plane of deformation of the body, for example the "
    "$x$-$y$ plane, are equal to zero, i.e.\\ "
    "$\\sigma_{zz}\\neq 0,\\;\\tau_{xz}=\\tau_{yz}=0$."
)

NEW_QUESTION_TEXT = (
    "Which of the following statement(s) is/are true about the state of a body "
    "in plane strain condition? "
    "P: All the points in the body undergo displacements in one plane only "
    "(for example, the x-y plane), leading to "
    "\u03b5\u208a\u208a = \u03b3_xz = \u03b3_yz = 0. "
    "Q: All the components of stress perpendicular to the plane of deformation "
    "(for example, the x-y plane) are equal to zero, i.e. "
    "\u03c3_zz = \u03c4_xz = \u03c4_yz = 0. "
    "R: Except the normal component, all the other components of stress "
    "perpendicular to the plane of deformation (for example, the x-y plane) "
    "are equal to zero, i.e. \u03c3_zz \u2260 0, \u03c4_xz = \u03c4_yz = 0."
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

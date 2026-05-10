"""
Patch GATE_2017_AE_Q22: full stem with \\omega_i, \\phi_i, bmatrix mode shapes.

Issue: question_text_latex was a short fragment; UI showed ASCII omega1, phi1, etc.

Usage (from backend/):
  venv/bin/python patch_gate_2017_ae_q22_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2017_AE_Q22"

NEW_QUESTION_TEXT_LATEX = (
    "A $2$-DOF undamped spring-mass system with two masses and two springs has natural "
    "frequencies $\\omega_1 = 0.79\\ \\mathrm{rad/s}$ and "
    "$\\omega_2 = 1.538\\ \\mathrm{rad/s}$. "
    "The mode shapes for the system are given by "
    "$\\boldsymbol{\\phi}_1 = \\begin{bmatrix} 0.732 \\\\ 1 \\end{bmatrix}$ and "
    "$\\boldsymbol{\\phi}_2 = \\begin{bmatrix} -2.73 \\\\ 1 \\end{bmatrix}$. "
    "If the first mass is displaced by $1\\ \\mathrm{cm}$, the minimum displacement "
    "in cm to be given to the second mass to make the system vibrate in first mode alone "
    "is $\\underline{\\hspace{6em}}$ (in three decimal place)."
)

NEW_QUESTION_TEXT = (
    "A 2-DOF undamped spring-mass system with two masses and two springs has natural "
    "frequencies \u03c9\u2081 = 0.79 rad/s and \u03c9\u2082 = 1.538 rad/s. "
    "The mode shapes for the system are given by "
    "\u03c6\u2081 = [0.732; 1]^T and \u03c6\u2082 = [-2.73; 1]^T "
    "(column vectors). "
    "If the first mass is displaced by 1 cm, the minimum displacement in cm to be given "
    "to the second mass to make the system vibrate in first mode alone is = _________ "
    "(in three decimal place)."
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

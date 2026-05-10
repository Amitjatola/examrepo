"""
Fix GATE_2023_AE_Q30 stem: broken \\text{...} wrapper, k\\_\\theta, spacing.

Usage (from backend/):
  venv/bin/python patch_gate_2023_ae_q30_stem_latex.py
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2023_AE_Q30"

NEW_QUESTION_TEXT = (
    "For studying wing vibrations, a wing of mass M and finite dimensions has been idealized by "
    "assuming it to be supported using a linear spring of equivalent stiffness k and a torsional "
    "spring of equivalent stiffness k_theta as shown in the figure. The centre of gravity (CG) of "
    "the wing idealized as an airfoil is marked in the figure. The number of degree(s) of freedom "
    "for this idealized wing vibration model is _________. (Answer in integer)"
)

NEW_QUESTION_TEXT_LATEX = (
    r"For studying wing vibrations, a wing of mass $M$ and finite dimensions has been idealized "
    r"by assuming it to be supported using a linear spring of equivalent stiffness $k$ and a "
    r"torsional spring of equivalent stiffness $k_{\theta}$ as shown in the figure. The centre of "
    r"gravity (CG) of the wing idealized as an airfoil is marked in the figure. The number of "
    r"degree(s) of freedom for this idealized wing vibration model is $\underline{\hspace{6em}}$. "
    r"(Answer in integer)"
)


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT question_id FROM questions WHERE question_id=:q"), {"q": QID})
        if not res.fetchone():
            raise SystemExit(f"{QID} not in DB")

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, updated_at=:ts "
                "WHERE question_id=:qid"
            ),
            {"qt": NEW_QUESTION_TEXT, "qtl": NEW_QUESTION_TEXT_LATEX, "ts": datetime.utcnow(), "qid": QID},
        )

    print(f"Patched {QID}: question_text + question_text_latex")


if __name__ == "__main__":
    asyncio.run(main())

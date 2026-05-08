"""
Fix question stem LaTeX for GATE_2016_AE_Q47.

QuestionDetail uses question_text_latex first; it was only `\\Delta s > 0` (no $...$), and
question_text wrote "Delta s" in plain text. This patch sets both fields to a full stem
with proper $...$ delimiters for KaTeX.

Usage (from backend/):
  venv/bin/python patch_gate_2016_ae_q47_latex.py
"""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2016_AE_Q47"

NEW_DESCRIPTION = (
    r"A substance experiences an entropy change of $\Delta s > 0$ in a quasi-steady process. "
    r"The rise in temperature (corresponding to the entropy change $\Delta s$) is highest for "
    r"the following process:"
)


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_DESCRIPTION,
                "qtl": NEW_DESCRIPTION,
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: question_text + question_text_latex")


if __name__ == "__main__":
    asyncio.run(main())

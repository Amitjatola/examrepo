"""
Fix GATE_2009_AE_Q55: options missing $...$ delimiters; fix evaluated-at notation.

Usage (from backend/):
  venv/bin/python patch_gate_2009_ae_q55_options_latex.py
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2009_AE_Q55"

NEW_QUESTION_TEXT = (
    "If the shaft is fixed at both ends, the boundary conditions are:"
)

NEW_QUESTION_TEXT_LATEX = NEW_QUESTION_TEXT

# Prose "and" between math chunks — avoids nested $ from \\text{and} inside one $...$
# (LatexRenderer blankTextToRule wraps \\text{...} with $ and breaks non-greedy $ split).
NEW_OPTIONS = {
    "A": (
        r"$\left.\dfrac{\partial\theta}{\partial x}\right|_{x=0}=0$ and "
        r"$\left.\dfrac{\partial\theta}{\partial x}\right|_{x=L}=0$"
    ),
    "B": r"$\theta(0)=0$ and $\theta(L)=0$",
    "C": (
        r"$\left.\dfrac{\partial\theta}{\partial x}\right|_{x=0}=0$ and $\theta(L)=0$"
    ),
    "D": (
        r"$\theta(0)=0$ and "
        r"$\left.\dfrac{\partial\theta}{\partial x}\right|_{x=L}=0$"
    ),
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

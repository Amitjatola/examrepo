"""
Fix GATE_2014_AE_Q04: KaTeX options + full question stem.

Usage (from backend/):
  venv/bin/python patch_gate_2014_ae_q04_latex.py
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2014_AE_Q04"

NEW_QUESTION_TEXT = (
    "Given the boundary-value problem (d/dx)(x dy/dx) + k y = 0 on 0 < x < 1 with y(0) = y(1) = 0. "
    "Then the solutions for k = 1 (y_1) and k = 5 (y_5) satisfy:"
)

NEW_QUESTION_TEXT_LATEX = (
    r"Given the boundary-value problem "
    r"$\dfrac{d}{dx}\!\left(x\,\dfrac{dy}{dx}\right)+ky=0$, \quad $0<x<1$, \quad $y(0)=y(1)=0$. "
    r"Then the solutions of the boundary-value problem for $k=1$ (given by $y_1$) and $k=5$ (given by $y_5$) satisfy:"
)

NEW_OPTIONS = {
    "A": r"$\displaystyle\int_{0}^{1} y_1 y_5\,dx = 0$",
    "B": r"$\displaystyle\int_{0}^{1} \left(\dfrac{dy_1}{dx}\right)\left(\dfrac{dy_5}{dx}\right)\,dx = 0$",
    "C": r"$\displaystyle\int_{0}^{1} y_1 y_5\,dx \neq 0$",
    "D": r"$\displaystyle\int_{0}^{1} \left(y_1 y_5 + \dfrac{dy_1}{dx}\,\dfrac{dy_5}{dx}\right)\,dx = 0$",
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

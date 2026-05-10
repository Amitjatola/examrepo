"""
Patch GATE_2009_AE_Q40 options: wrap full expression in $...$ so KaTeX runs.

Stored strings had \\sqrt{\\frac{...}{...}} without math delimiters — UI showed
literal \"sqrt frack...\".

Usage (from backend/):
  venv/bin/python patch_gate_2009_ae_q40_options_latex.py
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2009_AE_Q40"

NEW_OPTIONS = {
    "A": r"$0 \text{ and } \sqrt{\dfrac{k(m_1+m_2)}{m_1 m_2}}$",
    "B": r"$0 \text{ and } \sqrt{\dfrac{k(m_1+m_2)}{2m_1 m_2}}$",
    "C": r"$0 \text{ and } \sqrt{\dfrac{k}{m_1+m_2}}$",
    "D": r"$0 \text{ and } \sqrt{\dfrac{k}{2(m_1+m_2)}}$",
}


async def main() -> None:
    opts_json = json.dumps(NEW_OPTIONS)
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
                "SET options = CAST(:opts AS jsonb), "
                "    updated_at = :ts "
                "WHERE question_id = :qid"
            ),
            {"opts": opts_json, "ts": datetime.utcnow(), "qid": QID},
        )

    print(f"Patched {QID}: options updated with delimited KaTeX.")


if __name__ == "__main__":
    asyncio.run(main())

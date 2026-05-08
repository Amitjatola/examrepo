"""
Set full prose+math question_text_latex for GATE_2015_AE_Q49 (momentum thrust MCQ).

Legacy rows often stored a short delimiter-free fragment; the app used to prefer that over question_text.
Run: PYTHONPATH=backend python backend/patch_gate_2015_ae_q49_latex.py
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2015_AE_Q49"
CORRECTED = Path(__file__).resolve().parent / "scripts/latex_bulk/out/gate_2015_ae_q49_corrected.json"


async def main() -> None:
    payload = json.loads(CORRECTED.read_text(encoding="utf-8"))
    qtl = payload["question_description"]["question_text_latex"]

    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT 1 FROM questions WHERE question_id=:q LIMIT 1"),
            {"q": PUBLIC_ID},
        )
        if res.fetchone() is None:
            raise SystemExit(f"Question not found: {PUBLIC_ID}")

        await conn.execute(
            text(
                "UPDATE questions SET question_text_latex=:qtl, updated_at=:u "
                "WHERE question_id=:q"
            ),
            {"qtl": qtl, "u": datetime.utcnow(), "q": PUBLIC_ID},
        )

    print("patched question_text_latex for", PUBLIC_ID)


if __name__ == "__main__":
    asyncio.run(main())

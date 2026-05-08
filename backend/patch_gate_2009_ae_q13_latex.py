"""
Fix question_text_latex for GATE_2009_AE_Q13 (TAS/EAS density ratio).

The DB has a broken legacy string with raw \\text{} interleaving. Replace with
proper prose + inline $...$ delimiters.

Usage (from repo root)::

    PYTHONPATH=backend python backend/patch_gate_2009_ae_q13_latex.py --json

Postgres (needs valid DATABASE_URL in backend/.env)::

    PYTHONPATH=backend python backend/patch_gate_2009_ae_q13_latex.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

PUBLIC_ID = "GATE_2009_AE_Q13"

QUESTION_TEXT_LATEX = (
    r"The relation between an airplane's true airspeed $V_{\mathrm{TAS}}$ and "
    r"equivalent airspeed $V_{\mathrm{EAS}}$ in terms of the density ratio "
    r"$\sigma = \rho/\rho_0$, where $\rho_0$ is the air density at sea level and "
    r"$\rho$ is the air density at the altitude at which the airplane is flying, "
    r"is given by the formula:"
)

DEFAULT_JSON = Path(__file__).resolve().parent / "scripts/latex_bulk/out/db_all_questions.json"


def patch_json_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"JSON file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected a JSON array of questions in {path}")

    found = False
    for q in data:
        if isinstance(q, dict) and q.get("question_id") == PUBLIC_ID:
            q["question_text_latex"] = QUESTION_TEXT_LATEX
            found = True
            break

    if not found:
        raise SystemExit(f"Question not found in JSON: {PUBLIC_ID}")

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("patched question_text_latex in", path)


async def patch_database() -> None:
    from app.core.database import engine

    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT 1 FROM questions WHERE question_id=:q LIMIT 1"),
            {"q": PUBLIC_ID},
        )
        if res.fetchone() is None:
            raise SystemExit(f"Question not in database: {PUBLIC_ID}")

        await conn.execute(
            text(
                "UPDATE questions SET question_text_latex=:qtl, updated_at=:u "
                "WHERE question_id=:q"
            ),
            {"qtl": QUESTION_TEXT_LATEX, "u": datetime.utcnow(), "q": PUBLIC_ID},
        )

    print("patched question_text_latex in database for", PUBLIC_ID)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        nargs="?",
        const="__default__",
        help="Patch db_all_questions.json (default path) or a given file path",
    )
    args = parser.parse_args()

    if args.json is not None:
        path = DEFAULT_JSON if args.json == "__default__" else Path(args.json)
        patch_json_file(path)
        return

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(patch_database())


if __name__ == "__main__":
    main()

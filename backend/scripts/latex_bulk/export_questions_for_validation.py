#!/usr/bin/env python3
"""
Export a JSON array of questions from PostgreSQL for validate_latex.py.
Run from backend/:
  PYTHONPATH=. python scripts/latex_bulk/export_questions_for_validation.py -o scripts/latex_bulk/out/db_all.json
  PYTHONPATH=. python scripts/latex_bulk/export_questions_for_validation.py --limit 100 -o scripts/latex_bulk/out/db_slice.json
Omit --limit to export every row (large JSON).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from sqlalchemy import select  # noqa: E402
from app.core.database import async_session_maker  # noqa: E402
from app.domains.questions.models import Question  # noqa: E402


async def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("-o", "--out", type=Path, required=True)
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max rows (default: all questions)",
    )
    args = p.parse_args()

    async with async_session_maker() as session:
        stmt = select(Question).order_by(Question.year.asc(), Question.question_number.asc())
        if args.limit is not None:
            stmt = stmt.limit(args.limit)
        res = await session.execute(stmt)
        rows = res.scalars().all()
        out = [
            q.model_dump(mode="json", exclude={"embedding", "search_content"})
            for q in rows
        ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(out)} questions to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

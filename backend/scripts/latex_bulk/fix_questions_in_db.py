#!/usr/bin/env python3
"""
Apply `latex_fixers.apply_full_pipeline` to every question row in PostgreSQL.

Run from repo `backend/` with PYTHONPATH including the app package:

  cd /path/to/aerogate/backend
  source venv/bin/activate   # if you use one
  PYTHONPATH=. python scripts/latex_bulk/fix_questions_in_db.py --dry-run --limit 10

Then drop --dry-run for real updates. Requires DATABASE_URL / settings like the API.

After changing text/tiers, search_content + embedding are recomputed by default
(same logic as QuestionRepository._prepare_search_data). Use --skip-embedding only if
you plan to reindex separately.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_LATEX = Path(__file__).resolve().parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if str(SCRIPTS_LATEX) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_LATEX))

from latex_fixers import apply_full_pipeline  # noqa: E402
from sqlalchemy import select  # noqa: E402
from app.core.database import async_session_maker  # noqa: E402
from app.domains.questions.models import Question  # noqa: E402
from app.domains.questions.repository import QuestionRepository  # noqa: E402
from app.domains.questions.schemas import QuestionCreate  # noqa: E402

LATEX_FIELDS = (
    "question_text",
    "question_text_latex",
    "options",
    "image_metadata",
    "tier_0_classification",
    "tier_1_core_research",
    "tier_2_student_learning",
    "tier_3_enhanced_learning",
    "tier_4_metadata",
)


def _snap(blob: dict) -> str:
    return json.dumps(blob, sort_keys=True, default=str)


def _latex_blob(q: Question) -> dict:
    return {k: getattr(q, k) for k in LATEX_FIELDS}


async def run(*, dry_run: bool, limit: int | None, skip_embedding: bool, no_auto_wrap: bool) -> int:
    updated = 0
    unchanged = 0
    async with async_session_maker() as session:
        repo = QuestionRepository(session)
        stmt = select(Question).order_by(Question.year.asc(), Question.question_number.asc())
        if limit is not None:
            stmt = stmt.limit(limit)
        res = await session.execute(stmt)
        rows = list(res.scalars().all())

        for q in rows:
            before = _latex_blob(q)
            fixed = apply_full_pipeline(before, auto_wrap=not no_auto_wrap)
            if _snap(before) == _snap(fixed):
                unchanged += 1
                continue
            updated += 1
            if dry_run:
                continue
            for k in LATEX_FIELDS:
                setattr(q, k, fixed[k])
            if not skip_embedding:
                payload = {name: getattr(q, name) for name in QuestionCreate.model_fields}
                content, emb = repo._prepare_search_data(payload)
                q.search_content = content
                q.embedding = emb
            q.updated_at = datetime.utcnow()
            session.add(q)

        if not dry_run and updated:
            await session.commit()

    print(
        f"rows_scanned={len(rows)} latex_changed={updated} unchanged={unchanged} "
        f"dry_run={dry_run} skip_embedding={skip_embedding}",
    )
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Fix LaTeX in DB question rows")
    p.add_argument("--dry-run", action="store_true", help="Do not commit")
    p.add_argument("--limit", type=int, default=None, help="Max rows (for testing)")
    p.add_argument(
        "--skip-embedding",
        action="store_true",
        help="Do not refresh search_content / embedding (faster; search drifts until reindex)",
    )
    p.add_argument("--no-auto-wrap", action="store_true", help="Pass through to latex_fixers")
    args = p.parse_args()
    return asyncio.run(
        run(
            dry_run=args.dry_run,
            limit=args.limit,
            skip_embedding=args.skip_embedding,
            no_auto_wrap=args.no_auto_wrap,
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())

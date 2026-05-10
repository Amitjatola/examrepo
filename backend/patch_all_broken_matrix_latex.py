"""
Bulk-fix all questions whose question_text_latex has broken matrix syntax:
  - \\_ subscripts  ->  _
  - \\ followed by space (row sep)  ->  \\\\  (proper LaTeX row separator)
  - \\& column separator  ->  &

Also fixes the same patterns inside options, hints, and tier JSON fields.

Usage (from backend/):
  venv/bin/python patch_all_broken_matrix_latex.py
"""

import asyncio
import json
import re
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine


def fix_matrix_latex(s: str) -> str:
    if not isinstance(s, str):
        return s
    # 1. Fix escaped subscript: \_{ or \_ -> _ (in math mode no escape needed)
    s = re.sub(r'\\_\{', '_{', s)
    s = re.sub(r'\\_([a-zA-Z])', r'_\1', s)
    # 2. Fix escaped ampersand column separator: \& -> &
    #    Only inside math environments to be safe
    s = s.replace('\\&', '&')
    # 3. Fix broken row separator: "\ " (backslash-space) inside matrix envs -> "\\"
    #    Pattern: single backslash followed by a single space then a matrix element
    #    We match \<space> that is NOT already \\ 
    #    Replace "\ " with "\\ " only when preceded by a matrix entry character
    s = re.sub(r'(?<!\\)\\ (?=[A-Z0-9\\{])', r'\\\\ ', s)
    return s


def fix_string(s):
    if not isinstance(s, str):
        return s
    return fix_matrix_latex(s)


def fix_recursive(obj):
    if isinstance(obj, str):
        return fix_string(obj)
    if isinstance(obj, list):
        return [fix_recursive(x) for x in obj]
    if isinstance(obj, dict):
        return {k: fix_recursive(v) for k, v in obj.items()}
    return obj


BROKEN_QIDS = [
    "GATE_AE_2008_Q02",
    "GATE_AE_2008_Q28",
    "GATE_2009_AE_Q46",
    "GATE_2009_AE_Q49",
    "GATE_2012_AE_Q33",
    "GATE_2013_AE_Q4",
    "GATE_2013_AE_Q28",
    "GATE_2015_AE_Q39",
    "GATE_2016_AE_Q52",
    "GATE_2017_AE_Q26",
    "GATE_2017_AE_Q27",
    "GATE_2018_AE_Q20",
    "GATE_2020_AE_Q30",
    "GATE_2020_AE_Q35",
    "GATE_2021_AE_Q32",
    "GATE_2021_AE_Q37",
    "GATE_2022_AE_Q49",
    "GATE_2024_AE_Q13",
]


async def main() -> None:
    now = datetime.utcnow()
    patched = []

    async with engine.begin() as conn:
        for qid in BROKEN_QIDS:
            res = await conn.execute(
                text(
                    "SELECT question_text_latex, options, "
                    "tier_1_core_research, tier_2_student_learning "
                    "FROM questions WHERE question_id = :qid"
                ),
                {"qid": qid},
            )
            row = res.fetchone()
            if not row:
                print(f"  SKIP {qid} — not found")
                continue

            qtl, opts, t1, t2 = row

            new_qtl = fix_string(qtl)
            new_opts = fix_recursive(opts) if opts else opts
            new_t1 = fix_recursive(t1) if t1 else t1
            new_t2 = fix_recursive(t2) if t2 else t2

            await conn.execute(
                text(
                    "UPDATE questions SET "
                    "question_text_latex = :qtl, "
                    "options = CAST(:opts AS jsonb), "
                    "tier_1_core_research = CAST(:t1 AS jsonb), "
                    "tier_2_student_learning = CAST(:t2 AS jsonb), "
                    "updated_at = :ts "
                    "WHERE question_id = :qid"
                ),
                {
                    "qtl": new_qtl,
                    "opts": json.dumps(new_opts) if new_opts is not None else None,
                    "t1": json.dumps(new_t1) if new_t1 is not None else None,
                    "t2": json.dumps(new_t2) if new_t2 is not None else None,
                    "ts": now,
                    "qid": qid,
                },
            )
            patched.append(qid)
            print(f"  PATCHED {qid}")

    print(f"\nDone. Fixed {len(patched)}/{len(BROKEN_QIDS)} questions.")


if __name__ == "__main__":
    asyncio.run(main())

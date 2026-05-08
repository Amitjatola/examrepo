"""
Fix KaTeX-safe question + hint text for GATE_2024_AE_Q61.

LatexRenderer only typesets $...$$/$$...$$. The blank \\text{\\_...} was outside math mode,
and units were split as $1.225$ kg/m$^3$ (awkward spacing). This patch wraps the stem in
consistent math segments and tightens hint step 7.

Usage (from backend/):
  venv/bin/python patch_gate_2024_ae_q61_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2024_AE_Q61"

# Fill-in uses seven underscore slots, matching stored NAT stem
NEW_QUESTION_TEXT_LATEX = (
    r"For an aircraft moving at $4\ \text{km}$ altitude above mean sea level at a Mach number of $0.2$, "
    r"the ratio of equivalent air speed to true air speed is $\text{\_\_\_\_\_\_\_}$ (rounded off to "
    r"2 decimal places). The density of air at mean sea level is $1.225\ \text{kg/m}^3$ and at "
    r"$4\ \text{km}$ altitude is $0.819\ \text{kg/m}^3$."
)


def patch_tier_1(tier_1: Optional[dict]) -> dict:
    t1 = deepcopy(tier_1 or {})
    exp = dict(t1.get("explanation") or {})
    steps = list(exp.get("step_by_step") or [])
    if len(steps) >= 7 and isinstance(steps[6], str):
        steps[6] = "Step 7: Round off to two decimal places as requested: $0.82$."
    exp["step_by_step"] = steps
    t1["explanation"] = exp
    return t1


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT tier_1_core_research FROM questions WHERE question_id = :qid"),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        new_t1 = patch_tier_1(row[0])

        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text_latex = :qtl, "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "t1": json.dumps(new_t1),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: question_text_latex + hint step 7")


if __name__ == "__main__":
    asyncio.run(main())

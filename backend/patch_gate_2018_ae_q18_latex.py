"""
Fix KaTeX-facing solution + hints for GATE_2018_AE_Q18.

- explanation.step_by_step[2] had \\Delta outside math mode.
- formulas_used entries were not wrapped in $...$.

Usage (from backend/):
  venv/bin/python patch_gate_2018_ae_q18_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2018_AE_Q18"

NEW_STEP_BY_STEP = [
    (
        "The First Law of Thermodynamics states that energy cannot be created or destroyed, only transformed "
        "from one form to another."
    ),
    (
        "This fundamental principle is also known as the Conservation of Energy, as it asserts that the total "
        "energy of an isolated system remains constant."
    ),
    (
        "Mathematically, for a closed system: "
        r"$\mathrm{d}E = \delta Q - \delta W$, or in finite form $\Delta E = Q - W$."
    ),
    (
        "Therefore, the First Law of Thermodynamics is synonymous with the principle of conservation of energy."
    ),
]

NEW_FORMULAS_USED = [
    r"$\mathrm{d}E = \delta Q - \delta W$",
    r"$\dot{Q} - \dot{W} = \dfrac{\mathrm{d}E}{\mathrm{d}t}$",
    r"$h_0 = h + \dfrac{V^2}{2}$",
]

NEW_FP0_FORMULA = r"$\mathrm{d}E = \delta Q - \delta W$"
NEW_FP0_CONDITIONS = (
    r"Applies to a closed thermodynamic system, where $\Delta E$ is the change in total energy, "
    r"$Q$ is heat added to the system, and $W$ is work done by the system."
)

NEW_FP1_FORMULA = (
    r"$\dot{Q} - \dot{W} = \dfrac{\mathrm{d}}{\mathrm{d}t} \int_{CV} e\rho\,\mathrm{d}V + \int_{CS} "
    r"\left(h + \dfrac{V^2}{2} + gz\right) \rho \vec{V} \cdot \mathrm{d}\vec{A}$"
)


def patch_tier_1(tier_1: Optional[dict]) -> dict:
    t1 = deepcopy(tier_1 or {})
    exp = dict(t1.get("explanation") or {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    t1["explanation"] = exp

    fps = t1.get("formulas_principles")
    if isinstance(fps, list) and len(fps) >= 2:
        fps[0] = dict(fps[0])
        fps[0]["formula"] = NEW_FP0_FORMULA
        fps[0]["conditions"] = NEW_FP0_CONDITIONS
        fps[1] = dict(fps[1])
        fps[1]["formula"] = NEW_FP1_FORMULA

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
                "UPDATE questions SET tier_1_core_research = CAST(:t1 AS jsonb), "
                "updated_at = :updated_at WHERE question_id = :qid"
            ),
            {"t1": json.dumps(new_t1), "updated_at": datetime.utcnow(), "qid": PUBLIC_ID},
        )

    print(f"Patched {PUBLIC_ID}: hints (step_by_step), formulas_used, formulas_principles")


if __name__ == "__main__":
    asyncio.run(main())

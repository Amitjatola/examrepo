"""
Fix GATE_2017_AE_Q19 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2017_ae_q19_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2017_AE_Q19"

NEW_QUESTION_TEXT = (
    "In the vane-less space between the impeller and the diffuser vanes in a centrifugal compressor, "
    "the angular momentum varies in the following manner in the radial direction."
)

NEW_QUESTION_TEXT_LATEX = (
    "In the vane-less space between the impeller and the diffuser vanes in a centrifugal compressor, "
    "the angular momentum $rV_\\theta$ varies in the following manner in the radial direction."
)

NEW_OPTIONS = {
    "A": "Increases",
    "B": "Remains constant",
    "C": "Decreases",
    "D": "First increases and then decreases",
}

NEW_REASONING = (
    "In the vaneless space of a centrifugal compressor, there is no blade row and hence no significant external "
    "torque transfer to the flow. Therefore angular momentum about the axis is approximately conserved, giving "
    "$rV_\\theta=\\text{constant}$ (free-vortex behavior). As fluid moves radially outward ($r\\uparrow$), "
    "$V_\\theta$ decreases such that the product $rV_\\theta$ remains constant. Hence angular momentum remains "
    "constant in the radial direction. Therefore the correct option is $\\mathbf{B}$."
)

NEW_HINTS = [
    "Use the free-vortex model in the vaneless space.",
    "For axisymmetric flow with negligible external torque, $rV_\\theta=\\text{constant}$.",
    "Do not confuse $V_\\theta$ variation with $rV_\\theta$ variation.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Identify the region: vaneless space between impeller exit and diffuser vane inlet in a centrifugal compressor.",
    "Step 2: Since this region has no blade row, assume negligible external torque on the fluid element.",
    "Step 3: Apply angular-momentum conservation about the shaft axis: $rV_\\theta=\\text{constant}$.",
    "Step 4: As flow moves outward, radius $r$ increases while whirl velocity $V_\\theta$ decreases accordingly.",
    "Step 5: Thus the product $rV_\\theta$ (specific angular momentum) remains constant with radius.",
    "Step 6: Therefore, in the radial direction, angular momentum remains constant.",
]

NEW_FORMULAS_USED = [
    "$rV_\\theta=\\text{constant}$",
]

NEW_SOLUTION_PATH = (
    "Vaneless-space physics $\\rightarrow$ angular-momentum conservation $\\rightarrow$ free-vortex relation "
    "$rV_\\theta=\\text{constant}$ $\\rightarrow$ choose 'Remains constant'."
)

NEW_KEY_INSIGHTS = [
    "In vaneless space, swirl velocity changes with radius, but angular momentum $rV_\\theta$ stays nearly constant.",
    "This free-vortex behavior helps condition flow before entering the vaned diffuser.",
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = 6

    t1["hints"] = NEW_HINTS

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
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "options = CAST(:opts AS jsonb), "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(new_t1),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: question, options, solution, hints, and step-by-step LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

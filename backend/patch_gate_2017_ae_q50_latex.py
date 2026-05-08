"""
Fix GATE_2017_AE_Q50 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2017_ae_q50_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2017_AE_Q50"

NEW_QUESTION_TEXT = (
    "A centrifugal compressor requires 1800 kW of power to compress 10 kg/s of air. "
    "Consider the whirl velocity component is equal to the impeller speed (i.e., no slip) and no losses in the impeller. "
    "If the impeller has to rotate at 1900 rad/s, the diameter of the impeller is ________ m (in two decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    "A centrifugal compressor requires $P=1800\\,\\mathrm{kW}$ of power to compress "
    "$\\dot m=10\\,\\mathrm{kg/s}$ of air. Consider the whirl velocity component is equal to the impeller speed "
    "(i.e., no slip: $C_{w2}=U_2$) and no losses in the impeller. If the impeller rotates at "
    "$\\omega=1900\\,\\mathrm{rad/s}$, the diameter of the impeller is $\\underline{\\qquad\\qquad}$ "
    "$\\mathrm{m}$ (to two decimal places)."
)

NEW_REASONING = (
    "From compressor power relation, $P=\\dot m\\,w_c$, so "
    "$w_c=\\frac{P}{\\dot m}=\\frac{1.8\\times10^6}{10}=1.8\\times10^5\\,\\mathrm{J/kg}$. "
    "Euler work input equation is $w_c=U_2C_{w2}-U_1C_{w1}$. With idealized axial inlet "
    "($C_{w1}=0$) and no slip ($C_{w2}=U_2$), this reduces to $w_c=U_2^2$. Hence "
    "$U_2=\\sqrt{w_c}=\\sqrt{1.8\\times10^5}=424.264\\,\\mathrm{m/s}$. "
    "Using $U_2=\\omega\\,\\frac{D_2}{2}$ gives $D_2=\\frac{2U_2}{\\omega}"
    "=\\frac{2\\times424.264}{1900}=0.4466\\,\\mathrm{m}$. "
    "Therefore, to two decimal places, $D_2\\approx\\boxed{0.45\\,\\mathrm{m}}$."
)

NEW_HINTS = [
    "Start from shaft power per unit mass flow: $w_c=\\frac{P}{\\dot m}$.",
    "Apply Euler equation with no-slip and zero inlet whirl: $w_c=U_2C_{w2}-U_1C_{w1}\\Rightarrow w_c=U_2^2$.",
    "Use tip-speed relation: $U_2=\\omega\\frac{D_2}{2}$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Convert data to SI form: $P=1800\\,\\mathrm{kW}=1.8\\times10^6\\,\\mathrm{W}$, "
    "$\\dot m=10\\,\\mathrm{kg/s}$, and $\\omega=1900\\,\\mathrm{rad/s}$.",
    "Step 2: Compute specific work input to the fluid: "
    "$w_c=\\frac{P}{\\dot m}=\\frac{1.8\\times10^6}{10}=1.8\\times10^5\\,\\mathrm{J/kg}$.",
    "Step 3: Write Euler compressor equation: $w_c=U_2C_{w2}-U_1C_{w1}$.",
    "Step 4: Use assumptions: no prewhirl at inlet ($C_{w1}=0$) and no slip ($C_{w2}=U_2$), "
    "so $w_c=U_2^2$.",
    "Step 5: Solve for impeller tip speed: "
    "$U_2=\\sqrt{w_c}=\\sqrt{1.8\\times10^5}=424.264\\,\\mathrm{m/s}$.",
    "Step 6: Relate tip speed to diameter: $U_2=\\omega\\frac{D_2}{2}\\Rightarrow D_2=\\frac{2U_2}{\\omega}$.",
    "Step 7: Substitute values: "
    "$D_2=\\frac{2\\times424.264}{1900}=0.4466\\,\\mathrm{m}$.",
    "Step 8: Round to two decimals: $D_2\\approx\\boxed{0.45\\,\\mathrm{m}}$.",
]

NEW_FORMULAS_USED = [
    "$P=\\dot m\\,w_c$",
    "$w_c=U_2C_{w2}-U_1C_{w1}$",
    "$C_{w2}=U_2$ (no slip)",
    "$w_c=U_2^2$",
    "$U_2=\\omega\\frac{D_2}{2}$",
    "$D_2=\\frac{2U_2}{\\omega}$",
]

NEW_SOLUTION_PATH = (
    "Power data $\\rightarrow$ specific work $\\rightarrow$ Euler equation with no-slip simplification "
    "$\\rightarrow$ tip speed $U_2$ $\\rightarrow$ convert to diameter using $\\omega$."
)

NEW_KEY_INSIGHTS = [
    "The no-slip condition ($C_{w2}=U_2$) is the key simplification that makes $w_c=U_2^2$.",
    "Unit conversion from kW to W is essential before computing specific work.",
    "After finding $U_2$, diameter follows directly from $U_2=\\omega D_2/2$.",
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
    sbs["total_steps"] = 8

    t1["hints"] = NEW_HINTS

    return t1


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT tier_1_core_research, options FROM questions WHERE question_id = :qid"),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        new_t1 = patch_tier_1(row[0])
        existing_options = row[1]

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
                "opts": json.dumps(existing_options),
                "t1": json.dumps(new_t1),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: question, solution, hints, step-by-step, and formula LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

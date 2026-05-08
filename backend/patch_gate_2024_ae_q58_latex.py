"""
Fix GATE_2024_AE_Q58 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2024_ae_q58_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2024_AE_Q58"

NEW_QUESTION_TEXT = (
    "A centrifugal compressor is designed to operate with air. At the leading edge of the tip of the inducer "
    "(eye of the impeller), the blade angle is 45 deg, and the relative Mach number is 1.0. "
    "The stagnation temperature of the incoming air is 300 K. Consider gamma = 1.4. "
    "Neglect pre-whirl and slip. The inducer tip speed is ________ m/s (rounded off to the nearest integer)."
)

NEW_QUESTION_TEXT_LATEX = (
    "A centrifugal compressor is designed to operate with air. At the leading edge of the tip of the inducer "
    "(eye of the impeller), the blade angle is $\\beta_1=45^{\\circ}$, and the relative Mach number is "
    "$M_{r1}=1.0$. The stagnation temperature of the incoming air is $T_{01}=300\\,\\mathrm{K}$. "
    "Consider $\\gamma=1.4$. Neglect pre-whirl and slip. The inducer tip speed is $\\underline{\\qquad\\qquad}$ "
    "$\\mathrm{m/s}$ (rounded off to the nearest integer)."
)

NEW_REASONING = (
    "With no pre-whirl, $c_{\\theta 1}=0$, so inlet absolute flow is axial. From the inlet velocity triangle, "
    "$\\tan\\beta_1 = \\frac{c_{f1}}{U_1}$. With $\\beta_1=45^{\\circ}$, we get $c_{f1}=U_1$, hence "
    "$c_1=U_1$. Relative velocity is $w_1^2 = c_{f1}^2 + (U_1-c_{\\theta 1})^2 = 2U_1^2$, so "
    "$w_1=\\sqrt{2}U_1$. Given $M_{r1}=\\frac{w_1}{a_1}=1$, we have $w_1=a_1=\\sqrt{\\gamma RT_1}$, "
    "thus $2U_1^2=\\gamma RT_1$. Also, $T_{01}=T_1+\\frac{c_1^2}{2C_p}$ with $c_1=U_1$ and "
    "$C_p=\\frac{\\gamma R}{\\gamma-1}$ gives "
    "$T_1=T_{01}-\\frac{(\\gamma-1)U_1^2}{2\\gamma R}$. Substituting into $2U_1^2=\\gamma RT_1$ yields "
    "$U_1^2=\\frac{2\\gamma RT_{01}}{\\gamma+3}$. For $\\gamma=1.4$, $R=287\\,\\mathrm{J/(kg\\cdot K)}$, "
    "$T_{01}=300\\,\\mathrm{K}$: $U_1\\approx 234.07\\,\\mathrm{m/s}$, so the required tip speed is "
    "$\\boxed{234\\,\\mathrm{m/s}}$."
)

NEW_HINTS = [
    "Use no pre-whirl: $c_{\\theta 1}=0$.",
    "From geometry at inlet: $\\tan\\beta_1=\\frac{c_{f1}}{U_1}$ and $\\beta_1=45^{\\circ}$.",
    "Apply both $M_{r1}=\\frac{w_1}{a_1}$ and $T_{01}=T_1+\\frac{c_1^2}{2C_p}$, then eliminate $T_1$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Write given data: $\\beta_1=45^{\\circ}$, $M_{r1}=1$, $T_{01}=300\\,\\mathrm{K}$, "
    "$\\gamma=1.4$, and no pre-whirl ($c_{\\theta 1}=0$).",
    "Step 2: From inlet velocity triangle, $\\tan\\beta_1=\\frac{c_{f1}}{U_1}$. Since "
    "$\\beta_1=45^{\\circ}$, $c_{f1}=U_1$. With $c_{\\theta 1}=0$, absolute inlet speed is "
    "$c_1=c_{f1}=U_1$.",
    "Step 3: Relative speed magnitude is "
    "$w_1^2=c_{f1}^2+(U_1-c_{\\theta 1})^2=U_1^2+U_1^2=2U_1^2$, so $w_1=\\sqrt{2}U_1$.",
    "Step 4: Use relative Mach number at inlet: $M_{r1}=\\frac{w_1}{a_1}=1\\Rightarrow w_1=a_1$, where "
    "$a_1=\\sqrt{\\gamma RT_1}$. Hence $2U_1^2=\\gamma RT_1$.",
    "Step 5: Use stagnation relation with absolute speed: "
    "$T_{01}=T_1+\\frac{c_1^2}{2C_p}=T_1+\\frac{U_1^2}{2C_p}$ and "
    "$C_p=\\frac{\\gamma R}{\\gamma-1}$, so "
    "$T_1=T_{01}-\\frac{(\\gamma-1)U_1^2}{2\\gamma R}$.",
    "Step 6: Substitute this $T_1$ into $2U_1^2=\\gamma RT_1$ and simplify: "
    "$U_1^2=\\frac{2\\gamma RT_{01}}{\\gamma+3}$.",
    "Step 7: Put numbers: "
    "$U_1^2=\\frac{2\\times1.4\\times287\\times300}{1.4+3}=54790.909$ and "
    "$U_1=\\sqrt{54790.909}=234.07\\,\\mathrm{m/s}$.",
    "Step 8: Round to nearest integer: $U_1\\approx\\boxed{234\\,\\mathrm{m/s}}$.",
]

NEW_FORMULAS_USED = [
    "$\\tan\\beta_1=\\frac{c_{f1}}{U_1}$",
    "$w_1^2=c_{f1}^2+(U_1-c_{\\theta 1})^2$",
    "$M_{r1}=\\frac{w_1}{a_1}$",
    "$a_1=\\sqrt{\\gamma RT_1}$",
    "$T_{01}=T_1+\\frac{c_1^2}{2C_p}$",
    "$C_p=\\frac{\\gamma R}{\\gamma-1}$",
    "$U_1^2=\\frac{2\\gamma RT_{01}}{\\gamma+3}$",
]

NEW_SOLUTION_PATH = (
    "Velocity triangle at inducer inlet ($c_{\\theta 1}=0$, $\\beta_1=45^{\\circ}$) "
    "$\\rightarrow$ relative Mach condition ($M_{r1}=1$) $\\rightarrow$ stagnation-temperature relation "
    "$\\rightarrow$ eliminate $T_1$ $\\rightarrow$ solve for $U_1$."
)

NEW_KEY_INSIGHTS = [
    "For $\\beta_1=45^{\\circ}$ with no pre-whirl, inlet axial speed equals blade speed: $c_{f1}=U_1$.",
    "The condition $M_{r1}=1$ directly couples relative velocity and local speed of sound at inlet.",
    "Combining inlet kinematics with $T_{01}$ relation yields a closed-form tip-speed formula in "
    "$\\gamma$, $R$, and $T_{01}$.",
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

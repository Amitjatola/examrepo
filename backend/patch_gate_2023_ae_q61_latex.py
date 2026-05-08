"""
Fix GATE_2023_AE_Q61 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2023_ae_q61_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q61"

NEW_QUESTION_TEXT = (
    "A gas turbine combustor is burning methane and air at an equivalence ratio phi = 0.5, "
    "where phi = (F/A)/(F/A)_stoich and (F/A)_stoich is the ratio of mass flow rate of fuel to "
    "the mass flow rate of air at stoichiometry. If the air flow rate is m_dot_air = 20 kg/s, "
    "then the mass flow rate of methane is ______ kg/s (round off to two decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    "A gas turbine combustor is burning methane and air at an equivalence ratio $\\phi=0.5$, where "
    "$\\phi=\\dfrac{(F/A)}{(F/A)_{\\mathrm{stoich}}}$ and $(F/A)_{\\mathrm{stoich}}$ is the stoichiometric "
    "fuel-to-air mass ratio. If the air flow rate is $\\dot m_{\\mathrm{air}}=20\\,\\mathrm{kg/s}$, then "
    "the mass flow rate of methane is $\\underline{\\qquad\\qquad}$ $\\mathrm{kg/s}$ "
    "(round off to two decimal places)."
)

NEW_REASONING = (
    "Use the equivalence-ratio definition directly. For methane, stoichiometric combustion is "
    "$\\mathrm{CH_4}+2(\\mathrm{O_2}+3.76\\mathrm{N_2})\\rightarrow "
    "\\mathrm{CO_2}+2\\mathrm{H_2O}+7.52\\mathrm{N_2}$. "
    "This gives $(A/F)_{\\mathrm{stoich}}\\approx17.2$, so "
    "$(F/A)_{\\mathrm{stoich}}\\approx\\frac{1}{17.2}\\approx0.0581$. "
    "Given $\\phi=\\dfrac{(F/A)}{(F/A)_{\\mathrm{stoich}}}=0.5$, the actual ratio is "
    "$(F/A)=0.5\\times0.0581\\approx0.02905$. Then "
    "$\\dot m_f=(F/A)\\,\\dot m_{\\mathrm{air}}\\approx0.02905\\times20=0.581\\,\\mathrm{kg/s}$. "
    "Rounded to two decimals, $\\dot m_f\\approx\\boxed{0.58\\,\\mathrm{kg/s}}$."
)

NEW_HINTS = [
    "Find $(F/A)_{\\mathrm{stoich}}$ for methane first, then use $\\phi=\\dfrac{(F/A)}{(F/A)_{\\mathrm{stoich}}}$.",
    "Use stoichiometric methane reaction: $\\mathrm{CH_4}+2(\\mathrm{O_2}+3.76\\mathrm{N_2})\\rightarrow\\cdots$.",
    "After getting $(F/A)$, multiply by $\\dot m_{\\mathrm{air}}$ to get $\\dot m_f$.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Given $\\phi=0.5$ and $\\dot m_{\\mathrm{air}}=20\\,\\mathrm{kg/s}$. Use "
    "$\\phi=\\dfrac{(F/A)}{(F/A)_{\\mathrm{stoich}}}$.",
    "Step 2: Write stoichiometric methane combustion: "
    "$\\mathrm{CH_4}+2(\\mathrm{O_2}+3.76\\mathrm{N_2})\\rightarrow\\mathrm{CO_2}+2\\mathrm{H_2O}+7.52\\mathrm{N_2}$.",
    "Step 3: Compute stoichiometric mass ratio: "
    "$(A/F)_{\\mathrm{stoich}}\\approx17.2\\Rightarrow(F/A)_{\\mathrm{stoich}}\\approx\\dfrac{1}{17.2}=0.0581$.",
    "Step 4: Actual fuel-air ratio is "
    "$(F/A)=\\phi\\,(F/A)_{\\mathrm{stoich}}=0.5\\times0.0581=0.02905$.",
    "Step 5: Use flow-rate relation "
    "$(F/A)=\\dfrac{\\dot m_f}{\\dot m_{\\mathrm{air}}}\\Rightarrow"
    "\\dot m_f=(F/A)\\,\\dot m_{\\mathrm{air}}$.",
    "Step 6: Substitute values: "
    "$\\dot m_f=0.02905\\times20=0.581\\,\\mathrm{kg/s}$.",
    "Step 7: Round to two decimals: $\\dot m_f\\approx\\boxed{0.58\\,\\mathrm{kg/s}}$.",
]

NEW_FORMULAS_USED = [
    "$\\mathrm{CH_4}+2(\\mathrm{O_2}+3.76\\mathrm{N_2})\\rightarrow\\mathrm{CO_2}+2\\mathrm{H_2O}+7.52\\mathrm{N_2}$",
    "$\\phi=\\dfrac{(F/A)}{(F/A)_{\\mathrm{stoich}}}$",
    "$(A/F)_{\\mathrm{stoich}}=\\dfrac{m_{\\mathrm{air,stoich}}}{m_{\\mathrm{fuel,stoich}}}$",
    "$(F/A)_{\\mathrm{stoich}}=\\dfrac{1}{(A/F)_{\\mathrm{stoich}}}$",
    "$\\dot m_f=(F/A)\\,\\dot m_{\\mathrm{air}}$",
]

NEW_SOLUTION_PATH = (
    "Use equivalence-ratio definition $\\rightarrow$ find methane stoichiometric $F/A$ "
    "$\\rightarrow$ compute actual $F/A$ using $\\phi$ $\\rightarrow$ multiply by air flow rate."
)

NEW_KEY_INSIGHTS = [
    "This is a ratio problem; no energy balance is required.",
    "Correct stoichiometric methane $F/A$ is the key to the final number.",
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
    sbs["total_steps"] = 7

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

    print(f"Patched {PUBLIC_ID}: question, solution, hints, steps, options, and LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

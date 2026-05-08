"""
Fix GATE_2024_AE_Q18 LaTeX fields for frontend rendering.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2024_ae_q18_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2024_AE_Q18"

NEW_QUESTION_TEXT = (
    "In the figure shown below, various thermodynamic processes for an ideal gas are represented. "
    "Match each curve with the process that it best represents."
)

NEW_QUESTION_TEXT_LATEX = (
    "In the figure shown below, various thermodynamic processes for an ideal gas are represented on a "
    "$T\\text{-}S$ diagram. Match each curve with the process that it best represents."
)

NEW_OPTIONS = {
    "A": "$aa'$ - Isentropic; $bb'$ - Isothermal; $cc'$ - Isobaric; $dd'$ - Isochoric",
    "B": "$aa'$ - Isothermal; $bb'$ - Isentropic; $cc'$ - Isochoric; $dd'$ - Isobaric",
    "C": "$aa'$ - Isothermal; $bb'$ - Isentropic; $cc'$ - Isobaric; $dd'$ - Isochoric",
    "D": "$aa'$ - Isothermal; $bb'$ - Isobaric; $cc'$ - Isentropic; $dd'$ - Isochoric",
}

NEW_REASONING = (
    "The question asks to match thermodynamic processes on a $T\\text{-}S$ diagram for an ideal gas. "
    "Curve $aa'$ is horizontal, so $T$ is constant (isothermal). Curve $bb'$ is vertical, so $S$ is constant "
    "(isentropic). For $cc'$ and $dd'$, compare slopes using ideal-gas relations: "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_P = \\frac{T}{C_p}$ and "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V = \\frac{T}{C_v}$. Since $C_p > C_v$, we get "
    "$\\frac{1}{C_v} > \\frac{1}{C_p}$, hence "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V > \\left(\\frac{\\partial T}{\\partial S}\\right)_P$. "
    "So the isochoric line is steeper than the isobaric line. From the figure, $dd'$ is steeper than $cc'$, "
    "thus $dd'$ is isochoric and $cc'$ is isobaric. Therefore the correct option is $\\mathbf{C}$."
)

NEW_HINTS = [
    "On a $T\\text{-}S$ diagram, horizontal lines indicate constant $T$, and vertical lines indicate constant $S$.",
    "For an ideal gas: $\\left(\\frac{\\partial T}{\\partial S}\\right)_P = \\frac{T}{C_p}$ and "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V = \\frac{T}{C_v}$.",
    "Use $C_p > C_v$ to compare the steepness of isobaric and isochoric curves.",
]

NEW_STEP_BY_STEP = [
    "Step 1: Identify the plot as a $T\\text{-}S$ diagram (temperature $T$ on vertical axis, entropy $S$ on horizontal axis).",
    "Step 2: Curve $aa'$ is horizontal, so $T=\\text{constant}$ and the process is isothermal.",
    "Step 3: Curve $bb'$ is vertical, so $S=\\text{constant}$ and the process is isentropic.",
    "Step 4: Curves $cc'$ and $dd'$ must be isobaric and isochoric; distinguish them using slope relations on the $T\\text{-}S$ diagram.",
    "Step 5: For an isobaric process, $ds = C_p\\,\\frac{dT}{T}$, so "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_P = \\frac{T}{C_p}$.",
    "Step 6: For an isochoric process, $ds = C_v\\,\\frac{dT}{T}$, so "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V = \\frac{T}{C_v}$.",
    "Step 7: Since $C_p > C_v$, we have "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V > \\left(\\frac{\\partial T}{\\partial S}\\right)_P$, "
    "so the isochoric curve is steeper.",
    "Step 8: In the figure, $dd'$ is steeper than $cc'$, so $dd'$ is isochoric and $cc'$ is isobaric. "
    "Hence option $\\mathbf{C}$ is correct.",
]

NEW_FORMULAS_USED = [
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_P = \\frac{T}{C_p}$",
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V = \\frac{T}{C_v}$",
    "$C_p > C_v$",
    "$T = \\text{constant}$ (isothermal)",
    "$S = \\text{constant}$ (isentropic)",
    "$T\\,dS = C_p\\,dT$ (isobaric, ideal gas)",
    "$T\\,dS = C_v\\,dT$ (isochoric, ideal gas)",
]

NEW_SOLUTION_PATH = (
    "Identify the $T\\text{-}S$ axes and map direct geometric signatures first "
    "($aa'$ horizontal $\\Rightarrow$ isothermal, $bb'$ vertical $\\Rightarrow$ isentropic). "
    "Then use ideal-gas slope relations "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_P = \\frac{T}{C_p}$ and "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V = \\frac{T}{C_v}$ with $C_p > C_v$ to infer that "
    "isochoric curves are steeper than isobaric curves. Match the steeper curve as $dd'$ (isochoric) and "
    "the less steep one as $cc'$ (isobaric)."
)

NEW_KEY_INSIGHTS = [
    "On a $T\\text{-}S$ diagram, horizontal lines are isothermal and vertical lines are isentropic.",
    "For ideal gases, $C_p > C_v$ implies "
    "$\\left(\\frac{\\partial T}{\\partial S}\\right)_V > \\left(\\frac{\\partial T}{\\partial S}\\right)_P$.",
    "Hence on the same $T\\text{-}S$ plot, the isochoric line is steeper than the isobaric line.",
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

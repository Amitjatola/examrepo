"""
Patch LaTeX / notation for GATE_2022_AE_Q39 (stem, reasoning, formulas, hints).

Frontend LatexRenderer only typesets $...$ and $$...$$. This patch wraps all math in
$...$, fixes question_text_latex, answer_validation.reasoning, formulas_used, and steps.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2022_ae_q39_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2022_AE_Q39"

# Full stem preferred: QuestionDetail renders question_text_latex before question_text
NEW_QUESTION_TEXT_LATEX = (
    r"A cylindrical object of diameter $900\ \mathrm{mm}$ is designed to move axially in air at "
    r"$60\ \mathrm{m/s}$. Its drag is estimated on a geometrically half-scaled model in water, assuming flow "
    r"similarity. Coefficients of dynamic viscosity and densities for air and water are "
    r"$\mu_a = 1.86\times 10^{-5}\ \mathrm{Pa\,s}$, $\rho_a = 1.2\ \mathrm{kg/m^3}$ and "
    r"$\mu_w = 1.01\times 10^{-3}\ \mathrm{Pa\,s}$, $\rho_w = 1000\ \mathrm{kg/m^3}$ respectively. Drag measured for "
    r"the model is $2280\ \mathrm{N}$. Drag experienced by the full-scale object is \_\_\_\_ N "
    r"(rounded off to the nearest integer)."
)

NEW_REASONING = (
    "The problem is solved by dynamic similarity: for geometrically similar cylinders at the same Reynolds "
    "number, the drag coefficients match, so $C_{D,m}=C_{D,p}$. With "
    "$F_D=\\tfrac{1}{2}\\rho V^2 S C_D$ and frontal area $S=\\pi D^2/4$, enforcing "
    "$\\mathrm{Re}_m=\\mathrm{Re}_p$ and eliminating the model speed gives the drag ratio "
    "$\\frac{F_{D,p}}{F_{D,m}}=\\frac{\\rho_m}{\\rho_p}\\bigl(\\frac{\\mu_p}{\\mu_m}\\bigr)^2$. "
    "Using prototype diameter $D_p=0.9\\ \\mathrm{m}$, model diameter $D_m=0.45\\ \\mathrm{m}$, "
    "$\\rho_p=1.2\\ \\mathrm{kg/m^3}$, $\\rho_m=1000\\ \\mathrm{kg/m^3}$, "
    "$\\mu_p=1.86\\times 10^{-5}\\ \\mathrm{Pa\\,s}$, $\\mu_m=1.01\\times 10^{-3}\\ \\mathrm{Pa\\,s}$, "
    "and measured model drag $F_{D,m}=2280\\ \\mathrm{N}$ yields $F_{D,p}\\approx 644\\ \\mathrm{N}$, "
    "matching the answer key."
)

NEW_FORMULAS_USED = [
    r"$\mathrm{Re}=\dfrac{\rho V D}{\mu}$",
    r"$F_D=\dfrac{1}{2}\rho V^2 S C_D$",
    r"$S=\dfrac{\pi D^2}{4}$",
    r"$\dfrac{F_{D,p}}{F_{D,m}}=\dfrac{\rho_m}{\rho_p}\left(\dfrac{\mu_p}{\mu_m}\right)^2$",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: Identify the governing principle and given data. For dynamic similarity with the same drag "
        "coefficient ($C_D$), match the Reynolds number ($\\mathrm{Re}=\\rho V D/\\mu$) between the prototype "
        "(full-scale in air) and the model (half-scale in water). List parameters with consistent SI units "
        "(convert mm to m)."
    ),
    (
        "Step 2: Write the governing equations. $\\mathrm{Re}=\\rho V D/\\mu$ with diameter $D$. "
        "Drag force $F_D=\\tfrac{1}{2}\\rho V^2 S C_D$ with frontal area $S=\\pi D^2/4$ for axial motion. "
        "Because $C_{D,m}=C_{D,p}$, the dimensionless drag coefficient cancels when forming the drag-force ratio."
    ),
    (
        "Step 3: Velocity ratio from Reynolds matching. From $\\mathrm{Re}_m=\\mathrm{Re}_p$: "
        "$\\frac{\\rho_m V_m D_m}{\\mu_m}=\\frac{\\rho_p V_p D_p}{\\mu_p}$, hence "
        "$\\frac{V_m}{V_p}=\\frac{\\rho_p}{\\rho_m}\\frac{D_p}{D_m}\\frac{\\mu_m}{\\mu_p}$."
    ),
    (
        "Step 4: Drag-force ratio. "
        "$\\frac{F_{D,p}}{F_{D,m}}=\\frac{\\rho_p V_p^2 S_p}{\\rho_m V_m^2 S_m}"
        "=\\frac{\\rho_p}{\\rho_m}\\bigl(\\frac{V_p}{V_m}\\bigr)^2\\frac{S_p}{S_m}$."
    ),
    (
        "Step 5: Substitute geometry. Half-scale model: $D_m=D_p/2$, so $S_p/S_m=(D_p/D_m)^2=4$. "
        "Eliminate $V_p/V_m$ using Step 3 to obtain the standard result "
        "$\\frac{F_{D,p}}{F_{D,m}}=\\frac{\\rho_m}{\\rho_p}\\bigl(\\frac{\\mu_p}{\\mu_m}\\bigr)^2$ "
        "(all diameter factors cancel)."
    ),
    (
        "Step 6: Numbers. "
        "$\\rho_p=1.2\\ \\mathrm{kg/m^3}$, $\\mu_p=1.86\\times 10^{-5}\\ \\mathrm{Pa\\,s}$, "
        "$\\rho_m=1000\\ \\mathrm{kg/m^3}$, $\\mu_m=1.01\\times 10^{-3}\\ \\mathrm{Pa\\,s}$, "
        "$F_{D,m}=2280\\ \\mathrm{N}$. "
        "$\\mu_p/\\mu_m\\approx 0.0184158$, $(\\mu_p/\\mu_m)^2\\approx 3.3914\\times 10^{-4}$, "
        "$\\rho_m/\\rho_p\\approx 833.333$, so $F_{D,p}/F_{D,m}\\approx 0.28262$ and "
        "$F_{D,p}\\approx 2280\\times 0.28262\\approx 644\\ \\mathrm{N}$ (nearest integer)."
    ),
]

NEW_TRIAGE = (
    "Standard similarity drill: enforce $\\mathrm{Re}_m=\\mathrm{Re}_p$, use $F_D=\\tfrac{1}{2}\\rho V^2 S C_D$ "
    "with $S=\\pi D^2/4$, eliminate $V_m$ to get $F_{D,p}/F_{D,m}=(\\rho_m/\\rho_p)(\\mu_p/\\mu_m)^2$, "
    "then plug in values (viscosities in $\\mathrm{Pa\\,s}$, model drag $F_{D,m}=2280\\ \\mathrm{N}$)."
)

NEW_GUESS = (
    "Water is much denser than air ($\\sim 833\\times$), while $\\mu_p/\\mu_m$ is small ($\\sim 0.018$); "
    "squaring makes $F_{D,p}/F_{D,m}$ $\\ll 1$, so prototype drag should be far below 2280 N. "
    "$644$ N is $\\approx 0.28\\times 2280$ N — plausible."
)


def patch_payloads(tier_1: Optional[dict], tier_2: Optional[dict]) -> Tuple[dict, dict]:
    t1 = deepcopy(tier_1 or {})
    t2 = deepcopy(tier_2 or {})

    av = dict((t1.get("answer_validation") or {}))
    av["reasoning"] = NEW_REASONING
    t1["answer_validation"] = av

    exp = dict((t1.get("explanation") or {}))
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    t1["explanation"] = exp

    es = dict((t2.get("exam_strategy") or {}))
    es["triage_tip"] = NEW_TRIAGE
    es["guessing_heuristic"] = NEW_GUESS
    t2["exam_strategy"] = es

    return t1, t2


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning "
                "FROM questions WHERE question_id = :qid"
            ),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        tier_1, tier_2 = row[0], row[1]
        new_t1, new_t2 = patch_payloads(tier_1, tier_2)

        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text_latex = :qtl, "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "tier_2_student_learning = CAST(:t2 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "t1": json.dumps(new_t1),
                "t2": json.dumps(new_t2),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(
        f"Patched {PUBLIC_ID}: question_text_latex, reasoning, formulas_used, "
        "explanation.step_by_step, exam_strategy"
    )


if __name__ == "__main__":
    asyncio.run(main())

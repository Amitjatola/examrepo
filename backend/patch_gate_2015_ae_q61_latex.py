"""
Fix GATE_2015_AE_Q61 LaTeX: full stem, options display, reasoning (fix arcsin/rad bug), steps, formulas, hints, difficulty_factors.

Frontend LatexRenderer splits on $...$ / $$...$$; bare \\vec{...} and \\(...\\) do not render reliably.

Also corrects an error in the stored reasoning that treated \\arcsin(0.0984) as if it were already in radians.

Usage (from backend/):
  ./venv/bin/python patch_gate_2015_ae_q61_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2015_AE_Q61"

NEW_QUESTION_TEXT = (
    "An aircraft is flying with inertial ground and wind speeds of v_g^b = (100, 5, 5) m/s and "
    "v_w^b = (0, -5, -10) m/s, respectively, as expressed in the body frame. "
    "The corresponding sideslip angle (in degrees) is"
)

NEW_QUESTION_TEXT_LATEX = (
    "An aircraft is flying with inertial ground and wind speeds of "
    "$\\vec{v}_g^{\\,b}=(100,\\,5,\\,5)\\ \\mathrm{m/s}$ and "
    "$\\vec{v}_w^{\\,b}=(0,\\,-5,\\,-10)\\ \\mathrm{m/s}$, respectively, as expressed in the body frame. "
    "The corresponding **sideslip angle** $\\beta$ (in degrees) is"
)

NEW_OPTIONS = {
    "A": r"$0$",
    "B": r"$5.65$",
    "C": r"$8.49$",
    "D": r"$9.54$",
}

NEW_REASONING = (
    "Sideslip $\\beta$ is defined from the aircraft **velocity relative to the air** in body axes, "
    "$\\vec{v}_a^{\\,b}=\\vec{v}_g^{\\,b}-\\vec{v}_w^{\\,b}$ (same wind triangle idea as "
    "$\\vec{V}_T=\\vec{V}_G-\\vec{V}_W$, expressed here in the **body** frame).\n\n"
    "**Given**\n"
    "$\\vec{v}_g^{\\,b}=(100,\\,5,\\,5)\\ \\mathrm{m/s}$, "
    "$\\vec{v}_w^{\\,b}=(0,\\,-5,\\,-10)\\ \\mathrm{m/s}$.\n\n"
    "**1) Airspeed components**\n"
    "$u=100-0=100$, $v=5-(-5)=10$, $w=5-(-10)=15$ "
    "$\\Rightarrow\\ \\vec{v}_a^{\\,b}=(100,\\,10,\\,15)\\ \\mathrm{m/s}$.\n\n"
    "**2) Airspeed magnitude**\n"
    "$|\\vec{v}_a|=\\sqrt{u^2+v^2+w^2}=\\sqrt{100^2+10^2+15^2}=\\sqrt{10325}\\approx 101.61\\ \\mathrm{m/s}$.\n\n"
    "**3) Sideslip**\n"
    "With $v$ the **lateral (body-$y$)** component, "
    "$\\beta=\\arcsin\\!\\bigl(v/|\\vec{v}_a|\\bigr)$.\n"
    "$\\beta=\\arcsin(10/\\sqrt{10325})\\approx \\arcsin(0.09844)\\approx 0.0986\\ \\mathrm{rad}\\approx 5.65^\\circ$.\n\n"
    "Nearest listed value is **$5.65$** $\\Rightarrow$ **B**."
)

NEW_HINTS = [
    "First form **airspeed in body axes**: $\\vec{v}_a^{\\,b}=\\vec{v}_g^{\\,b}-\\vec{v}_w^{\\,b}$ (component-wise).",
    "Then $|\\vec{v}_a|=\\sqrt{u^2+v^2+w^2}$ — do **not** use $|\\vec{v}_g|$ for $\\beta$.",
    "Sideslip uses the **$y$-component**: $\\beta=\\arcsin(v/|\\vec{v}_a|)$ (small-angle OK here, but use the formula).",
    "Convert to degrees if needed: multiply radians by $180/\\pi$.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: **Given (body frame).** "
        "$\\vec{v}_g^{\\,b}$ is inertial ground velocity resolved in body axes; "
        "$\\vec{v}_w^{\\,b}$ is the wind (air-mass) velocity resolved in body axes. "
        "Aerodynamic angles follow **airspeed** "
        "$\\vec{v}_a^{\\,b}=\\vec{v}_g^{\\,b}-\\vec{v}_w^{\\,b}$. "
        "Here $\\vec{v}_g^{\\,b}=(100,\\,5,\\,5)\\ \\mathrm{m/s}$, "
        "$\\vec{v}_w^{\\,b}=(0,\\,-5,\\,-10)\\ \\mathrm{m/s}$."
    ),
    (
        "Step 2: **Subtract component-wise:** "
        "$u=100-0=100\\ \\mathrm{m/s}$, "
        "$v=5-(-5)=10\\ \\mathrm{m/s}$, "
        "$w=5-(-10)=15\\ \\mathrm{m/s}$ "
        "$\\Rightarrow \\vec{v}_a^{\\,b}=(100,\\,10,\\,15)\\ \\mathrm{m/s}$."
    ),
    (
        "Step 3: **Magnitude:** "
        "$|\\vec{v}_a|=\\sqrt{100^2+10^2+15^2}=\\sqrt{10325}\\approx 101.61\\ \\mathrm{m/s}$."
    ),
    (
        "Step 4: **Definition:** $\\beta$ is the angle between $\\vec{v}_a$ and the body $xz$ plane; "
        "equivalently $\\beta=\\arcsin\\!\\bigl(v/|\\vec{v}_a|\\bigr)$ with $v$ the lateral component."
    ),
    (
        "Step 5: **Evaluate:** "
        "$\\beta=\\arcsin(10/\\sqrt{10325})\\approx \\arcsin(0.09844)\\approx 5.65^\\circ$."
    ),
    (
        "Step 6: **Select** the closest option: **B** ($5.65$)."
    ),
]

NEW_FORMULAS_USED = [
    r"$\vec{v}_a^{\,b}=\vec{v}_g^{\,b}-\vec{v}_w^{\,b}$",
    r"$|\vec{v}_a|=\sqrt{u^2+v^2+w^2}$",
    r"$\beta=\arcsin\!\bigl(v/|\vec{v}_a|\bigr)$",
    r"$\mathrm{deg}=\mathrm{rad}\times 180/\pi$",
]

NEW_SOLUTION_PATH = (
    "Form $\\vec{v}_a=\\vec{v}_g-\\vec{v}_w$ in body axes → compute $|\\vec{v}_a|$ → "
    "$\\beta=\\arcsin(v/|\\vec{v}_a|)$ → $5.65^\\circ$ → B."
)

NEW_KEY_INSIGHTS = [
    "$\\beta$ always uses **airspeed**, not ground speed, when wind is nonzero.",
    "In body axes, the lateral component is **$v$** (body $y$); use it in $\\arcsin(v/V)$.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    (
        "Correctly interpreting the relative velocity relationship between ground speed, wind speed, and **airspeed** "
        "in the body frame, and performing accurate vector subtraction "
        "($\\vec{v}_a^{\\,b}=\\vec{v}_g^{\\,b}-\\vec{v}_w^{\\,b}$)."
    ),
    (
        "Calculating $|\\vec{v}_a|=\\sqrt{u^2+v^2+w^2}$ and applying the correct sideslip definition "
        "$\\beta=\\arcsin\\!\\bigl(v/|\\vec{v}_a|\\bigr)$ (not $|\\vec{v}_g|$ in the denominator)."
    ),
    "Potential trap: using **ground speed** (or its lateral component) instead of **airspeed** when computing $\\beta$.",
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
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

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

    print(f"Patched {PUBLIC_ID}: stem/options/reasoning/steps/formulas/hints/difficulty LaTeX + reasoning math fix")


if __name__ == "__main__":
    asyncio.run(main())

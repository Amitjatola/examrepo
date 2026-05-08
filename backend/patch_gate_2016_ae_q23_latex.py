"""
Fix GATE_2016_AE_Q23 LaTeX: stem, options (unchanged prose), reasoning, steps, formulas, hints.

Plain fragments like `q = 0.5 \\rho V^2` and `L = 0.5 \\rho V^2 S C_L` must be in $...$ for KaTeX.

Usage (from backend/):
  ./venv/bin/python patch_gate_2016_ae_q23_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2016_AE_Q23"

NEW_QUESTION_TEXT = "Indicated airspeed is used by a pilot during"

NEW_QUESTION_TEXT_LATEX = (
    "Indicated airspeed ($\\mathrm{IAS}$) is used by a pilot during"
)

NEW_OPTIONS = {
    "A": "take-off.",
    "B": "navigation.",
    "C": "setting the engine RPM.",
    "D": "setting the elevator angle.",
}

NEW_REASONING = (
    "**Indicated airspeed** ($\\mathrm{IAS}$) is what the **airspeed indicator** shows; it tracks **dynamic pressure** "
    "$q=\\tfrac{1}{2}\\rho V^2$, which is what sets **lift** and control **hinge moments** at a given configuration. "
    "During **takeoff**, the pilot flies to published speeds (e.g. rotation $V_R$, lift-off $V_{\\mathrm{LOF}}$) read "
    "as $\\mathrm{IAS}$, because **stall margin** and **lift** depend on $q$, not on true/geometric speed alone.\n\n"
    "For **en-route navigation** and **fuel/time** planning, **true airspeed** ($\\mathrm{TAS}$) and **ground speed** "
    "matter more than $\\mathrm{IAS}$ alone. **Engine RPM** / power is set with the **throttle** using power charts "
    "(often vs. altitude/OAT), not by \"setting RPM from the ASI.\" **Elevator** deflection is a **pitch** control to "
    "command attitude/$\\alpha$; the pilot does not use the ASI to \"set elevator angle\" as a primary procedure. "
    "Hence the best choice is **A** (take-off)."
)

NEW_HINTS = [
    "Remember $\\mathrm{IAS}\\propto \\sqrt{q}$ with $q=\\tfrac{1}{2}\\rho V^2$ — it is the cockpit proxy for **aerodynamic loading**.",
    "Takeoff/landing: you **fly target $\\mathrm{IAS}$** ($V_R$, $V_{\\mathrm{LOF}}$, $V_{\\mathrm{REF}}$, …) for stall/lift margins.",
    "Cruise **navigation**: need $\\mathrm{TAS}$/GS and wind; $\\mathrm{IAS}$ alone does not fix groundspeed or ETA.",
    "Power: **throttle/RPM** from engine performance data, not from reading the ASI as the primary setting rule.",
    "Elevator: **pitch** control; not the main answer for \"what $\\mathrm{IAS}$ is used for\" in this MCQ.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: $\\mathrm{IAS}$ is the speed **shown on the airspeed indicator**, driven by **impact/dynamic pressure** "
        "$q=\\tfrac{1}{2}\\rho V^2$. That is why it correlates with **lift** and **stall** behavior for a given airplane."
    ),
    (
        "Step 2: **Lift** obeys $L=\\tfrac{1}{2}\\rho V^2 S C_L$. On **takeoff**, the pilot monitors $\\mathrm{IAS}$ to "
        "reach **rotation** ($V_R$) and **lift-off** ($V_{\\mathrm{LOF}}$) speeds so $C_L$ and $q$ produce enough lift "
        "within runway limits."
    ),
    (
        "Step 3: Those takeoff speeds are defined/used as **$\\mathrm{IAS}$** because the limiting aerodynamics "
        "(stall, controllability) scale with $q$ at the **pilot’s reference** (instrument) level."
    ),
    (
        "Step 4: **Navigation** (wind triangle, ETA, fuel) relies on **$\\mathrm{TAS}$** and **ground speed**; "
        "$\\mathrm{IAS}$ alone is not the primary navigation output — eliminate **B** as the intended answer."
    ),
    (
        "Step 5: **Engine RPM** / power is commanded with the **throttle** per **power charts** and operating limits; "
        "it is not primarily “set using $\\mathrm{IAS}$” — eliminate **C**."
    ),
    (
        "Step 6: **Elevator** is used for **pitch** and trim; you do not normally “set elevator angle from the ASI” as "
        "the core use case — eliminate **D**. The remaining best option is **A**."
    ),
]

NEW_FORMULAS_USED = [
    r"$q=\tfrac{1}{2}\rho V^2$",
    r"$L=\tfrac{1}{2}\rho V^2 S C_L$",
]

NEW_SOLUTION_PATH = (
    "Link IAS to $q$ and lift → identify takeoff as the phase where target IAS ($V_R$, $V_{\\mathrm{LOF}}$) is primary "
    "→ rule out nav/TAS, RPM setting, elevator “setting” → A."
)

NEW_KEY_INSIGHTS = [
    "IAS is a dynamic-pressure surrogate: aerodynamic limits are naturally expressed in IAS for the pilot.",
    "TAS/GS matter for navigation; IAS matters most in low-speed, high-$q$-margin phases like takeoff and landing.",
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

    print(f"Patched {PUBLIC_ID}: question/options/reasoning/hints/step_by_step LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

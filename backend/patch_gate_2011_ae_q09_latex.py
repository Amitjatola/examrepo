"""
Fix KaTeX-facing fields for GATE_2011_AE_Q09 (stem, MCQ options, reasoning, formulas_used).

Hints (tier_1 explanation.step_by_step) already use $...$; no content change unless broken.

Usage (from backend/):
  venv/bin/python patch_gate_2011_ae_q09_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2011_AE_Q09"

NEW_QUESTION_TEXT_LATEX = (
    r"Consider a single degree of freedom spring-mass-damper system with mass, damping and stiffness of "
    r"$m$, $c$ and $k$, respectively. The logarithmic decrement of this system can be calculated using"
)

NEW_OPTIONS = {
    "A": r"$\dfrac{2\pi c}{\sqrt{4mk - c^2}}$",
    "B": r"$\dfrac{\pi c}{\sqrt{4mk - c^2}}$",
    "C": r"$\dfrac{2\pi c}{\sqrt{mk - c^2}}$",
    "D": r"$\dfrac{2\pi c}{\sqrt{4mk + c^2}}$",
}

NEW_REASONING = (
    r"The logarithmic decrement ($\delta$) for a single-degree-of-freedom (SDOF) system is fundamentally "
    r"related to the damping ratio ($\zeta$). The exact relationship for an underdamped system is given by:"
    "\n"
    r"$$\delta = \frac{2\pi\zeta}{\sqrt{1 - \zeta^2}}$$"
    "\n"
    r"For an SDOF system with mass $m$, damping coefficient $c$, and stiffness $k$, the undamped natural "
    r"frequency ($\omega_n$) is:"
    "\n"
    r"$$\omega_n = \sqrt{\frac{k}{m}}$$"
    "\n"
    r"The critical damping coefficient ($c_c$) is defined as:"
    "\n"
    r"$$c_c = 2m\omega_n = 2m\sqrt{\frac{k}{m}} = 2\sqrt{mk}$$"
    "\n"
    r"The damping ratio ($\zeta$) is the ratio of the actual damping coefficient to the critical damping "
    r"coefficient:"
    "\n"
    r"$$\zeta = \frac{c}{c_c} = \frac{c}{2\sqrt{mk}}$$"
    "\n"
    r"Now, substitute this expression for $\zeta$ into the logarithmic decrement formula:"
    "\n"
    r"$$\delta = \frac{2\pi \left(\frac{c}{2\sqrt{mk}}\right)}{\sqrt{1 - \left(\frac{c}{2\sqrt{mk}}\right)^2}}$$"
    "\n"
    "Simplify the expression:\n"
    r"$$\delta = \frac{\frac{\pi c}{\sqrt{mk}}}{\sqrt{1 - \frac{c^2}{4mk}}}$$"
    "\n"
    r"$$\delta = \frac{\frac{\pi c}{\sqrt{mk}}}{\sqrt{\frac{4mk - c^2}{4mk}}}$$"
    "\n"
    r"$$\delta = \frac{\frac{\pi c}{\sqrt{mk}}}{\frac{\sqrt{4mk - c^2}}{\sqrt{4mk}}}$$"
    "\n"
    r"$$\delta = \frac{\frac{\pi c}{\sqrt{mk}}}{\frac{\sqrt{4mk - c^2}}{2\sqrt{mk}}}$$"
    "\n"
    r"$$\delta = \frac{\pi c}{\sqrt{mk}} \times \frac{2\sqrt{mk}}{\sqrt{4mk - c^2}}$$"
    "\n"
    r"$$\delta = \frac{2\pi c}{\sqrt{4mk - c^2}}$$"
    "\n"
    "This derived formula matches Option A."
)

NEW_FORMULAS_USED = [
    r"$\delta = \dfrac{2\pi\zeta}{\sqrt{1-\zeta^2}}$",
    r"$\zeta = \dfrac{c}{c_c}$",
    r"$c_c = 2\sqrt{mk}$",
    r"$\omega_n = \sqrt{\dfrac{k}{m}}$",
]


def patch_tier_1(tier_1: Optional[dict]) -> dict:
    t1 = deepcopy(tier_1 or {})

    av = dict(t1.get("answer_validation") or {})
    av["reasoning"] = NEW_REASONING
    t1["answer_validation"] = av

    exp = dict(t1.get("explanation") or {})
    exp["formulas_used"] = NEW_FORMULAS_USED
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
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "options = CAST(:opts AS jsonb), "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT_LATEX,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(new_t1),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: stem, options, reasoning, formulas_used (hints unchanged)")


if __name__ == "__main__":
    asyncio.run(main())

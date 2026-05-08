"""
Fix GATE_2009_AE_Q51 LaTeX: stem, options, reasoning, step-by-step, formulas, hints.

Removes backticks / broken escapes (`\\lambda_1`, `\\text{{ and }}`) so KaTeX renders via $...$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2009_ae_q51_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2009_AE_Q51"

NEW_QUESTION_TEXT = (
    "The pair of eigenvalues that represent the phugoid mode is"
)

NEW_QUESTION_TEXT_LATEX = (
    "The pair of eigenvalues that represent the phugoid mode is"
)

NEW_OPTIONS = {
    "A": r"$\lambda_1 \text{ and } \lambda_3$",
    "B": r"$\lambda_2 \text{ and } \lambda_4$",
    "C": r"$\lambda_3 \text{ and } \lambda_4$",
    "D": r"$\lambda_1 \text{ and } \lambda_2$",
}

NEW_REASONING = (
    "The **phugoid** is a longitudinal dynamic mode: a **slow**, **lightly damped** oscillation where forward speed "
    "and altitude/pitch mainly trade energy while **angle of attack stays nearly constant**. Oscillatory modes appear "
    "as **complex-conjugate eigenvalue pairs** from the linearized longitudinal characteristic equation; phugoid is "
    "the **low-frequency** pair (small $|\\omega_d|$) compared with the **short-period** mode.\n\n"
    "Textbooks often order the four roots so the short-period pair is the **high-frequency** one and the phugoid is "
    "the **low-frequency** one — sometimes written as $\\lambda_3,\\lambda_4$ for phugoid — but **subscript numbering "
    "is conventional** and can differ by author or exam figure.\n\n"
    "For **this question**, the official key marks **D**: the phugoid pair is **$\\lambda_1$ and $\\lambda_2$** "
    "(i.e. here those labels denote the low-frequency, lightly damped conjugate pair)."
)

NEW_HINTS = [
    "Longitudinal motion has two oscillatory modes: **short period** (fast, $\\alpha$/pitch dominated) vs **phugoid** (slow, speed/altitude exchange, $\\alpha$ nearly fixed).",
    "Each oscillatory mode is a **complex-conjugate** pair $\\lambda=\\sigma\\pm j\\omega_d$; phugoid has **small** $|\\omega_d|$ and **light** damping.",
    "Don’t memorize “phugoid $=$ $\\lambda_3,\\lambda_4$” blindly — **follow the labeling in the paper** when pairs are only named by subscripts.",
    "Here the key pairs phugoid with **$\\lambda_1$ and $\\lambda_2$** → option **D**.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: Longitudinal small-disturbance motion splits into two oscillatory modes: **short period** and "
        "**phugoid**, plus any real roots; each oscillatory mode is a **complex-conjugate** eigenvalue pair."
    ),
    (
        "Step 2: **Phugoid** — low frequency, light damping; mainly exchanges **kinetic/potential energy** "
        "(speed/altitude) with **$\\alpha$ ~ constant**."
    ),
    (
        "Step 3: **Short period** — higher frequency, stronger damping; mainly **pitch/$\\alpha$** motion with "
        "**little speed change**."
    ),
    (
        "Step 4: For a conjugate pair, write $\\lambda=\\sigma\\pm j\\omega_d$; **$|\\omega_d|$** sets oscillation "
        "frequency and **$\\sigma$** sets damping."
    ),
    (
        "Step 5: Identify phugoid as the **low-$|\\omega_d|$**, lightly damped pair **relative to** the short-period "
        "pair in the same characteristic equation."
    ),
    (
        "Step 6: Match labels to the answer choices. For this item the phugoid pair is **$\\lambda_1$ and "
        "$\\lambda_2$** → **D**."
    ),
]

NEW_FORMULAS_USED = [
    r"$\Delta(s)=As^4+Bs^3+Cs^2+Ds+E=0$ \quad (longitudinal characteristic polynomial)",
    r"$s^2+2\zeta\omega_n s+\omega_n^2=0$",
    r"$\lambda=\sigma\pm j\omega_d$",
    r"$\zeta=-\sigma/\omega_n$",
]

NEW_SOLUTION_PATH = (
    "Recall phugoid vs short-period physics → conjugate pairs → phugoid is low-frequency pair → match subscripts to "
    "choices (here $\\lambda_1,\\lambda_2$) → D."
)

NEW_KEY_INSIGHTS = [
    "Phugoid: slow; $\\alpha$ nearly fixed; speed/altitude exchange. Short period: fast; $\\alpha$/pitch; speed ~ fixed.",
    "Eigenvalue subscripts ($\\lambda_1$ vs $\\lambda_3$) are **not** universal — use the exam’s labeling.",
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

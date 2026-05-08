"""
Fix GATE_AE_2008_Q38 LaTeX: stem, options, solution reasoning, hints (step_by_step), formulas.

Frontend LatexRenderer typesets $...$ / $$...$$. Plain \\phi etc. without delimiters fails.

Usage (from backend/):
  ./venv/bin/python patch_gate_ae_2008_q38_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_AE_2008_Q38"

NEW_QUESTION_TEXT = (
    "In the definition of the aircraft Euler angles φ (roll), θ (pitch), and ψ (yaw), the correct "
    "sequence of rotations required to make the inertial frame coincide with the aircraft body frame is"
)

NEW_QUESTION_TEXT_LATEX = (
    "In the definition of the aircraft Euler angles $\\phi$ (roll), $\\theta$ (pitch), and $\\psi$ (yaw), "
    "the correct sequence of rotations required to make the inertial frame coincide with the aircraft body "
    "frame is"
)

NEW_OPTIONS = {
    "A": "first $\\psi$ about the $z$-axis, second $\\theta$ about the $y$-axis, third $\\phi$ about the $x$-axis",
    "B": "first $\\theta$ about the $y$-axis, second $\\phi$ about the $x$-axis, third $\\psi$ about the $z$-axis",
    "C": "first $\\phi$ about the $x$-axis, second $\\theta$ about the $y$-axis, third $\\psi$ about the $z$-axis",
    "D": "first $\\psi$ about the $z$-axis, second $\\phi$ about the $x$-axis, third $\\theta$ about the $y$-axis",
}

NEW_REASONING = (
    "The usual aerospace convention (often called **yaw–pitch–roll**) takes the inertial (Earth-fixed) "
    "frame to the body frame using a **$\\mathrm{Z}$–$\\mathrm{Y}$–$\\mathrm{X}$** sequence:\n\n"
    "1. **Yaw** $\\psi$ about the **initial** $z$-axis.\n"
    "2. **Pitch** $\\theta$ about the **intermediate** $y$-axis (after the first rotation).\n"
    "3. **Roll** $\\phi$ about the **final** body $x$-axis (after the first two rotations).\n\n"
    "So the rotation order is $\\psi\\rightarrow\\theta\\rightarrow\\phi$ about "
    "$z_{\\text{initial}}\\rightarrow y_{\\text{intermediate}}\\rightarrow x_{\\text{body}}$.\n\n"
    "Option **A** states exactly that: first $\\psi$ about the $z$-axis, then $\\theta$ about the $y$-axis, "
    "then $\\phi$ about the $x$-axis. Therefore the correct answer is $\\mathbf{A}$."
)

NEW_HINTS = [
    "Aircraft Euler attitude is usually built as three successive rotations; the **order** and **which axis** "
    "(initial vs intermediate vs body) are part of the definition.",
    "Memorize the standard **yaw–pitch–roll** order: **$\\psi$ then $\\theta$ then $\\phi$**.",
    "First rotation: **yaw** $\\psi$ about the **inertial** $z$-axis (heading).",
    "Second rotation: **pitch** $\\theta$ about the **intermediate** $y$-axis (nose up/down).",
    "Third rotation: **roll** $\\phi$ about the **final body** $x$-axis (bank).",
    "That is a **$\\mathrm{Z}$–$\\mathrm{Y}$–$\\mathrm{X}$** chain; match this to the options — only **A** fits.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: Euler angles $(\\phi,\\theta,\\psi)$ encode orientation by a **fixed sequence** of three "
        "rotations from the inertial frame to the body frame; changing the order changes the meaning."
    ),
    (
        "Step 2: In the common aerospace **yaw–pitch–roll** convention, the first rotation is **yaw** "
        "$\\psi$ about the **original** (inertial) $z$-axis."
    ),
    (
        "Step 3: The second rotation is **pitch** $\\theta$ about the **intermediate** $y$-axis — the "
        "$y$-axis after the yaw rotation, not necessarily the final body $y$-axis yet."
    ),
    (
        "Step 4: The third rotation is **roll** $\\phi$ about the **final** body $x$-axis — the longitudinal "
        "body axis after yaw and pitch."
    ),
    (
        "Step 5: Summarize the sequence as **$\\mathrm{Z}$–$\\mathrm{Y}$–$\\mathrm{X}$**: "
        "$\\psi$ about $z$, then $\\theta$ about $y$, then $\\phi$ about $x$."
    ),
    (
        "Step 6: Compare with the options. Only option **A** lists "
        "$\\psi\\,(z)\\rightarrow \\theta\\,(y)\\rightarrow \\phi\\,(x)$, so **A** is correct."
    ),
]

NEW_FORMULAS_USED = [
    r"$R_{B/E} = R_x(\phi)\,R_y(\theta)\,R_z(\psi)$ (Z–Y–X, yaw–pitch–roll)",
    r"$\psi$: yaw about initial $z$; $\theta$: pitch about intermediate $y$; $\phi$: roll about final body $x$",
]

NEW_SOLUTION_PATH = (
    "Recall Z–Y–X (yaw–pitch–roll): ψ about initial z, θ about intermediate y, φ about final body x; match option A."
)

NEW_KEY_INSIGHTS = [
    "Order matters: the middle rotation is about an **intermediate** axis, not the final body axis.",
    "Standard aircraft Euler convention is **ψ → θ → φ** corresponding to **Z → Y → X**.",
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

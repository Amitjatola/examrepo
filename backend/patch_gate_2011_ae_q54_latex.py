"""
Fix GATE_2011_AE_Q54 for the frontend LatexRenderer.

The renderer only typesets math inside $...$ or $$...$$. Bare \\alpha, \\frac, and \\( ... \\)
do not render. question_text_latex was only the fraction, so QuestionDetail showed incomplete stem.

Usage (from backend/):
  source venv/bin/activate
  python patch_gate_2011_ae_q54_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2011_AE_Q54"

LIFTING_LINE_INLINE = (
    "$\\alpha(y_0) = \\frac{\\Gamma(y_0)}{\\pi U_{\\infty} c(y_0)} + \\alpha_{L=0}(y_0) + "
    "\\frac{1}{4\\pi U_{\\infty}} \\int_{-b/2}^{b/2} \\frac{d\\Gamma/dy}{y_0 - y}\\,dy$"
)

NEW_QUESTION_TEXT_LATEX = (
    "The rate of change of circulation with angle of attack "
    "$\\dfrac{\\partial \\Gamma}{\\partial \\alpha}$ is"
)

NEW_OPTIONS = {
    "A": r"inversely proportional to $\alpha$",
    "B": r"independent of $\alpha$",
    "C": r"a linear function of $\alpha$",
    "D": r"a quadratic function of $\alpha$",
}

NEW_REASONING = (
    "Prandtl's lifting line theory is a fundamental linear aerodynamic theory, valid for small angles of "
    "attack. In linear aerodynamic theories, all aerodynamic forces, moments, and circulation are considered "
    "to be linearly proportional to the angle of attack. The lifting line equation itself is a linear "
    "integral equation that relates the local angle of attack to the local circulation and its spanwise "
    "derivative. Since the entire framework is linear, the circulation $\\Gamma(y_0)$ at any spanwise station "
    "$y_0$ will be a linear function of the overall wing angle of attack $\\alpha$. If $\\Gamma(y_0)$ can be "
    "expressed as $\\Gamma(y_0) = K(y_0)\\,\\alpha + C(y_0)$, where $K(y_0)$ and $C(y_0)$ are coefficients "
    "that depend on the wing geometry, free-stream conditions, and zero-lift angle but are independent of "
    "$\\alpha$, then the derivative $\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha}$ will simply be $K(y_0)$. "
    "As $K(y_0)$ does not contain $\\alpha$, the rate of change of circulation with angle of attack is "
    "independent of $\\alpha$. This is a direct consequence of the linearization inherent in the lifting "
    "line theory."
)

NEW_STEP_BY_STEP = [
    (
        "Step 1: Understand the nature of Prandtl's Lifting Line Theory. It is a linear aerodynamic theory, "
        "meaning it assumes small perturbations and linear relationships between aerodynamic quantities and "
        "angle of attack."
    ),
    f"Step 2: Analyze the given Prandtl's lifting line equation: {LIFTING_LINE_INLINE}.",
    (
        "Step 3: Observe that all terms in the equation are linear with respect to $\\Gamma(y_0)$ and "
        "$\\alpha(y_0)$. The integral term, representing the induced angle of attack, is also linearly "
        "dependent on the circulation distribution $\\Gamma(y)$."
    ),
    (
        "Step 4: Conclude that because the governing equation is linear, the circulation distribution "
        "$\\Gamma(y_0)$ must be a linear function of the angle of attack $\\alpha$. This can be generally "
        "represented as $\\Gamma(y_0) = K(y_0)\\,\\alpha + C(y_0)$, where $K(y_0)$ and $C(y_0)$ are "
        "functions of spanwise position, wing geometry, and flight conditions, but not of $\\alpha$ itself."
    ),
    (
        "Step 5: Differentiate this linear relationship with respect to $\\alpha$. If "
        "$\\Gamma(y_0) = K(y_0)\\,\\alpha + C(y_0)$, then $\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha} = K(y_0)$."
    ),
    (
        "Step 6: Since $K(y_0)$ does not contain $\\alpha$, the derivative "
        "$\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha}$ is independent of $\\alpha$."
    ),
]

NEW_FORMULAS_USED = [
    LIFTING_LINE_INLINE,
    r"$\Gamma \propto \alpha$ for small $\alpha$",
]

NEW_SOLUTION_PATH = (
    "Understand Prandtl's Lifting Line Theory and its governing equation. Identify the linearity of the "
    "equation with respect to circulation ($\\Gamma$) and angle of attack ($\\alpha$) for small disturbances. "
    "Infer that $\\Gamma$ is linearly dependent on $\\alpha$. Recognize that the derivative of a linear "
    "function with respect to its independent variable is a constant. Conclude that the rate of change of "
    "circulation with respect to angle of attack, $\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha}$, is "
    "constant and independent of $\\alpha$."
)

NEW_KEY_INSIGHTS = [
    (
        "Prandtl's lifting line theory is a linear aerodynamic theory, meaning the circulation $\\Gamma$ is a "
        "linear function of the angle of attack $\\alpha$. Consequently, the rate of change "
        "$\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha}$ is a constant, independent of $\\alpha$."
    ),
    (
        "For a fixed wing, circulation scales linearly with angle of attack. Therefore, the derivative of this "
        "linear function (circulation) with respect to its independent variable (angle of attack), "
        "$\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha}$, is a constant, independent of the angle of attack itself."
    ),
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

    fps = t1.get("formulas_principles")
    if isinstance(fps, list) and len(fps) >= 2:
        fps[0] = dict(fps[0])
        fps[0]["formula"] = LIFTING_LINE_INLINE
        fps[1] = dict(fps[1])
        fps[1]["formula"] = r"$\Gamma = K\,\alpha + C$"

    return t1


def patch_tier_2(tier_2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t2 = deepcopy(tier_2 or {})
    cm = t2.get("common_mistakes")
    if isinstance(cm, list) and len(cm) >= 2:
        cm[0] = dict(cm[0])
        cm[0]["mistake"] = (
            r"Assuming $\frac{\mathrm{d}\Gamma}{\mathrm{d}\alpha}$ is a function of angle of attack, often due to "
            r"misinterpreting the integral term or the complex appearance of the equation as non-linear."
        )
        cm[0]["why_students_make_it"] = (
            r"Students might be intimidated by the integral equation and overlook the fundamental linear assumption "
            r"of Prandtl's lifting line theory, leading them to believe the relationship is more complex than it is. "
            r"This can stem from confusion between the function $\Gamma(\alpha)$ and its derivative."
        )
        cm[0]["how_to_avoid"] = (
            r"Carefully study Prandtl's lifting line equation and understand that the rate of change of circulation "
            r"with angle of attack is a constant, independent of the specific value of $\alpha$, due to the "
            r"underlying linearization for small angles of attack."
        )
        cm[0]["consequence"] = (
            r"Incorrectly choosing options that imply a non-linear dependence, such as a linear or quadratic "
            r"function of $\alpha$."
        )
        cm[1] = dict(cm[1])
        cm[1]["mistake"] = (
            r"Confusing the overall wing angle of attack $\alpha$ with the local zero-lift angle $\alpha_{L=0}(y_0)$."
        )
        cm[1]["how_to_avoid"] = (
            r"Carefully read the definitions of each term provided in the question and understand their physical "
            r"meaning. For example, $\alpha_{L=0}$ is a property of the airfoil section, while $\alpha$ is the wing's "
            r"angle of attack relative to the free stream."
        )
        cm[1]["consequence"] = (
            r"Could conclude that $\frac{\mathrm{d}\Gamma}{\mathrm{d}\alpha}$ depends on $\alpha$, leading to wrong answer."
        )

    fc = t2.get("flashcards")
    if isinstance(fc, list) and len(fc) >= 4:
        fc[0] = dict(fc[0])
        fc[0]["front"] = (
            r"What does $\frac{\mathrm{d}\Gamma}{\mathrm{d}\alpha}$ represent in Prandtl's lifting line theory?"
        )
        fc[0]["back"] = (
            r"$\frac{\mathrm{d}\Gamma}{\mathrm{d}\alpha}$ represents the rate of change of circulation with angle "
            r"of attack, which is a constant independent of the specific value of $\alpha$."
        )
        fc[1] = dict(fc[1])
        fc[1]["front"] = (
            r"What does $\frac{\mathrm{d}\Gamma}{\mathrm{d}\alpha}$ represent in the context of Prandtl's lifting "
            r"line theory?"
        )
        fc[1]["back"] = (
            r"It represents the rate of change of circulation with respect to the angle of attack at a given "
            r"spanwise location. For a given wing, it is constant and independent of $\alpha$ due to the linearity "
            r"of Prandtl's theory."
        )
        fc[3] = dict(fc[3])
        fc[3]["back"] = LIFTING_LINE_INLINE

    es = t2.get("exam_strategy")
    if isinstance(es, dict):
        es = dict(es)
        es["triage_tip"] = (
            "If you recognize that Prandtl's lifting line theory is a linear theory, the answer is immediate. "
            "The key is how circulation depends on $\\alpha$ and therefore what "
            "$\\frac{\\partial\\Gamma}{\\partial\\alpha}$ (or $\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha}$) "
            "means for a linear relation."
        )
        es["guessing_heuristic"] = (
            "In linearized aerodynamics, $\\Gamma$ is linear in $\\alpha$, so "
            "$\\frac{\\mathrm{d}\\Gamma}{\\mathrm{d}\\alpha}$ does not depend on $\\alpha$; "
            "choose independent of $\\alpha$ (option B)."
        )
        t2["exam_strategy"] = es

    return t2


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

        new_t1 = patch_tier_1(row[0])
        new_t2 = patch_tier_2(row[1])

        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "options = CAST(:opts AS jsonb), "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "tier_2_student_learning = CAST(:t2 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT_LATEX,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(new_t1),
                "t2": json.dumps(new_t2),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: question_text_latex, options, tier_1 + tier_2 LaTeX for KaTeX")


if __name__ == "__main__":
    asyncio.run(main())

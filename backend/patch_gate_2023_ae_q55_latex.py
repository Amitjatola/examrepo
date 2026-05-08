"""
Fix LaTeX / formatting for GATE_2023_AE_Q55 (pump power / flow coefficient, NAT).
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q55"

NEW_QUESTION_TEXT = (
    "The operating characteristics of a pump were measured to be C_p = a Φ², where power coefficient "
    "C_p = P / (ρ ω³ D⁵), Φ is the flow coefficient, a is a constant, D is a length scale, ω is the "
    "rotation rate, ρ is fluid density, and P is the power required. The flow coefficient is a "
    "dimensionless volume flow rate scaled with ω and D. Assuming that the flow rate remains the same, "
    "if the rotation rate is increased to 1.25 ω, the power changes to α P. The value of α is ________ "
    "(round off to two decimal places)."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The operating characteristics of a pump were measured to be $C_p = a\Phi^2$, where the power coefficient is
    \[
    C_p = \frac{P}{\rho\,\omega^3 D^5}.
    \]
    Here $\Phi$ is the flow coefficient, $a$ is a constant, $D$ is a length scale, $\omega$ is the rotation rate,
    $\rho$ is the fluid density, and $P$ is the power required. The flow coefficient is a dimensionless volume flow
    rate scaled with $\omega$ and $D$.

    Assuming that the flow rate remains the same, if the rotation rate is increased to $1.25\,\omega$, the power
    changes to $\alpha P$. The value of $\alpha$ is $\underline{\hspace{2.5cm}}$ (round off to two decimal places).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Definitions:
    \[
    C_p = \frac{P}{\rho\,\omega^3 D^5}, \qquad \Phi = \frac{Q}{\omega D^3}.
    \]
    The measured characteristic is $C_p = a\Phi^2$ with constant $a$. Substitute $\Phi$:
    \[
    \frac{P}{\rho\,\omega^3 D^5} = a\left(\frac{Q}{\omega D^3}\right)^{\!2}
    = a\,\frac{Q^2}{\omega^2 D^6}.
    \]
    Solve for $P$:
    \[
    P = a\,\rho\,\omega^3 D^5 \cdot \frac{Q^2}{\omega^2 D^6}
    = \frac{a\,\rho\,Q^2}{D}\,\omega.
    \]

    If $Q$, $\rho$, $D$, and $a$ are fixed, then $P \propto \omega$. **Do not** use $P\propto \omega^3$ here—that
    shortcut assumes homologous (constant-$\Phi$) operation; with $Q$ fixed, $\Phi = Q/(\omega D^3)$ changes with
    $\omega$.

    New speed $\omega_2 = 1.25\,\omega_1$ gives
    \[
    \frac{P_2}{P_1} = \frac{\omega_2}{\omega_1} = 1.25,
    \]
    so $P_2 = \alpha P_1$ with $\alpha = 1.25$.

    Rounded to two decimal places: **1.25**.
    """
).strip()

NEW_STEPS = [
    r"Write $C_p = P/(\rho \omega^3 D^5)$ and $\Phi = Q/(\omega D^3)$.",
    r"Use the given law $C_p = a\Phi^2$ and substitute $\Phi$.",
    r"Simplify to $P = \dfrac{a\rho Q^2}{D}\,\omega$.",
    r"With $Q,\rho,D,a$ constant, conclude $P \propto \omega$ (linear), not $\omega^3$.",
    r"Scale: $\omega \mapsto 1.25\omega \Rightarrow P \mapsto 1.25\,P$, so $\alpha = 1.25$.",
    r"Round to two decimals: $1.25$.",
]

NEW_FORMULAS_USED = [
    r"$C_p = \dfrac{P}{\rho\,\omega^3 D^5}$",
    r"$\Phi = \dfrac{Q}{\omega D^3}$",
    r"$C_p = a\Phi^2$",
    r"$P = \dfrac{a\rho Q^2}{D}\,\omega$ \quad ($Q,\rho,D,a$ fixed)",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Power coefficient",
        "type": "equation",
        "formula": r"$C_p = \dfrac{P}{\rho\,\omega^3 D^5}$",
        "conditions": "Dimensionless shaft power for geometrically similar scaling.",
        "relevance": "Given in the problem statement.",
    },
    {
        "name": "Flow coefficient",
        "type": "equation",
        "formula": r"$\Phi = \dfrac{Q}{\omega D^3}$",
        "conditions": "Dimensionless volume flow rate (standard turbomachinery grouping).",
        "relevance": r"Links $Q$ to $\omega$ when $D$ is fixed; with $Q$ constant, $\Phi \propto 1/\omega$.",
    },
    {
        "name": "Quadratic characteristic in coefficients",
        "type": "equation",
        "formula": r"$C_p = a\Phi^2$",
        "conditions": r"Given measured curve; $a$ constant.",
        "relevance": "Combined with definitions, yields $P \propto \omega$ at fixed $Q$.",
    },
    {
        "name": "Derived power law under fixed flow",
        "type": "equation",
        "formula": r"$P = \dfrac{a\rho Q^2}{D}\,\omega$",
        "conditions": r"Constant $Q$, $\rho$, $D$, $a$.",
        "relevance": r"Immediate ratio $P_2/P_1 = \omega_2/\omega_1$.",
    },
]

NEW_HINTS = [
    r"Expand $C_p=a\Phi^2$ with $\Phi=Q/(\omega D^3)$ and solve for $P$ before using affinity shortcuts.",
    r"$Q$ fixed $\Rightarrow$ $\Phi$ is **not** fixed when $\omega$ changes.",
    r"Combine exponents: $\omega^3$ in $C_p$ versus $\omega^{-2}$ from $\Phi^2$ leaves one factor of $\omega$ in $P$.",
    r"Final check: $1.25\times$ speed with linear $P$ gives $\alpha=1.25$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"Define $C_p$ and $\Phi$ for a pump (symbols $P,\rho,\omega,D,Q$).",
        "back": r"$C_p = \dfrac{P}{\rho\,\omega^3 D^5}$; $\Phi = \dfrac{Q}{\omega D^3}$.",
        "difficulty": "easy",
        "time_limit_seconds": 35,
    },
    {
        "card_type": "concept_recall",
        "front": r"When do standard affinity laws $Q\propto\omega$, $P\propto\omega^3$ (at fixed $D$) apply?",
        "back": r"Homologous points: constant $\Phi$ (dynamic similarity), not necessarily constant $Q$.",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Problem says $Q$ is constant while $\omega$ changes. Can you use $P\propto \omega^3$?",
        "back": r"No. Constant $Q$ means $\Phi$ varies with $\omega$; use the given $C_p=a\Phi^2$ to find $P(\omega)$.",
        "difficulty": "medium",
        "time_limit_seconds": 40,
    },
    {
        "card_type": "application",
        "front": r"Given $C_p=a\Phi^2$ and $Q$ constant, if $\omega$ increases 20%, by what factor does $P$ change?",
        "back": r"$P \propto \omega$, so a 20% increase in $\omega$ gives factor $1.20$.",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Phi falls when omega rises (Q fixed)",
        "concept": r"$\Phi = Q/(\omega D^3)$: larger $\omega$ $\Rightarrow$ smaller $\Phi$ if $Q$ fixed.",
        "effectiveness": "high",
        "context": "Pump problems with constant volumetric flow",
    },
    {
        "mnemonic": "Cube minus two equals one",
        "concept": r"In $C_p=a\Phi^2$, powers of $\omega$: $3$ from $C_p$ minus $2$ from $\Phi^2$ $\Rightarrow$ $P\propto\omega^1$.",
        "effectiveness": "medium",
        "context": r"Quick exponent scan on $P/\omega$.",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Using $P\propto \omega^3$ from memory while $Q$ is held constant.",
        "why_students_make_it": r"Affinity laws are practiced with constant $\Phi$; problem states constant $Q$ instead.",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Derive $P(\omega)$ from $C_p=a\Phi^2$ and $\Phi=Q/(\omega D^3)$.",
        "consequence": r"Typical wrong $\alpha \approx 1.25^3$.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Wrong dimensionless definition for $\Phi$ (exponents on $\omega$ or $D$).",
        "why_students_make_it": r"Guesswork instead of matching $Q/(\omega D^3)$.",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Track dimensions: $[Q]=L^3T^{-1}$, need $\Phi$ dimensionless with $\omega\sim T^{-1}$, $D\sim L$.",
        "consequence": r"Wrong proportionality for $P$.",
    },
    {
        "type": "Calculation",
        "mistake": r"Algebra errors canceling $\omega$ and $D$ powers when substituting $\Phi^2$.",
        "why_students_make_it": r"Rushing exponent arithmetic.",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Write one clean line: $P = (a\rho Q^2/D)\,\omega$ then scale.",
        "consequence": r"Intermediate powers like $\omega^2$ or $\omega^0$.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Spot $C_p=a\Phi^2$ + constant $Q$: derive $P\propto\omega$ first; skip blind $\omega^3$.",
    "guessing_heuristic": r"If stuck, note $C_p$ brings $\omega^3$ while $\Phi^2$ brings $\omega^{-2}$ at fixed $Q$—net $\omega^1$; answer near $1.25$.",
    "time_management": r"About 2–3 minutes once the proportionality is clear.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Separating constant-$Q$ operation from homologous constant-$\Phi$ scaling.",
    r"Careful algebra combining $C_p$ and $\Phi$ definitions.",
    r"Recognizing linear $P$ versus $\omega$ under the stated constraints.",
]

NEW_ALT_METHODS = [
    {
        "name": "Buckingham–Pi from scratch",
        "description": (
            r"Form $\pi$-groups from $(P,\rho,\omega,D,Q,a)$; impose the given relation $C_p=a\Phi^2$ to recover "
            r"$P \propto \omega$ at fixed $Q$."
        ),
        "pros_cons": "Pros: fundamental. Cons: slower on exam.",
        "when_to_use": r"If definitions were not provided.",
    },
    {
        "name": "Numerical substitution",
        "description": (
            r"Pick convenient constants $(a,\rho,Q,D)$, compute $P$ at $\omega$ and $1.25\omega$; read off the ratio."
        ),
        "pros_cons": "Pros: self-check. Cons: slightly more writing.",
        "when_to_use": r"If symbolic simplification feels uncertain.",
    },
]

NEW_REAL_WORLD_CONTEXT = [
    {
        "application": "Rocket Engine Thrust Control",
        "industry_example": (
            "Liquid rocket turbopumps: thrust phases may hold volumetric flow near constant while shaft speed trims "
            "losses. Power must scale with the actual $P(\omega)$ relation for the enforced operating curve—not a "
            "generic homologous-point cube law."
        ),
        "why_it_matters": "Motor/turbine sizing errors from wrong scaling can under- or overpower the drive stage.",
    },
    {
        "application": "Aircraft & Propulsion Fluid Systems",
        "industry_example": (
            "Engine fuel/oxidizer pumps at regulated flow setpoints: speed changes at fixed $Q$ alter dimensionless "
            "flow $\Phi$ and move along the pump characteristic."
        ),
        "why_it_matters": "Predicts electrical/mechanical load when controllers change RPM without changing schedule $Q$.",
    },
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "1.25"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = (
        r"Definitions of $C_p$, $\Phi$ $\to$ substitute in $C_p=a\Phi^2$ $\to$ isolate $P(\omega)$ "
        r"$\to$ linear scaling $\to$ $\alpha=1.25$"
    )
    sbs["key_insights"] = [
        r"Constant $Q$ breaks constant-$\Phi$ affinity; derive $P$ from the given $C_p(\Phi)$ law.",
        r"Exponent check: $\omega^3$ from $C_p$ versus $\omega^{-2}$ from $\Phi^2$ yields $P\propto\omega$.",
        r"Numerical ratio follows directly: $1.25\times$ speed $\Rightarrow$ $1.25\times$ power.",
    ]

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS
    return o


def patch_t2(t2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t2 or {})
    o["flashcards"] = NEW_FLASHCARDS
    o["mnemonics_memory_aids"] = NEW_MNEMONICS
    o["common_mistakes"] = NEW_COMMON_MISTAKES
    o["exam_strategy"] = NEW_EXAM_STRATEGY
    o["real_world_context"] = NEW_REAL_WORLD_CONTEXT
    return o


def patch_t3(t3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t3 or {})
    o["alternative_methods"] = NEW_ALT_METHODS
    return o


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning "
                "FROM questions WHERE question_id=:q"
            ),
            {"q": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit("Question not found")

        t1 = patch_t1(row[0])
        t2 = patch_t2(row[1])
        t3 = patch_t3(row[2])

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=CAST(:opts AS jsonb), "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(None),
                "t1": json.dumps(t1, ensure_ascii=False),
                "t2": json.dumps(t2, ensure_ascii=False),
                "t3": json.dumps(t3, ensure_ascii=False),
                "u": datetime.utcnow(),
                "q": PUBLIC_ID,
            },
        )

    print("patched", PUBLIC_ID)


if __name__ == "__main__":
    asyncio.run(main())

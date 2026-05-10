"""
Patch GATE_2020_AE_Q18: fix LaTeX delimiters across all sections.

Issues:
  - step_by_step: bare \\omega, \\frac, \\rho etc. without $...$
  - formulas_used[0]: missing $...$
  - common_mistakes: bare Unicode symbols (∝, δ) and undelimited math

Usage (from backend/):
  venv/bin/python patch_gate_2020_ae_q18_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime

from sqlalchemy import text

from app.core.database import engine

QID = "GATE_2020_AE_Q18"

NEW_STEP_BY_STEP = [
    (
        r"Recall the formula for the natural frequency of a uniform cantilever beam in transverse "
        r"vibration. The general formula for the natural angular frequency $\omega_n$ for the "
        r"$n$-th mode is "
        r"$\omega_n = (\beta_n L)^2 \sqrt{\dfrac{EI}{\rho A L^4}}$."
    ),
    (
        r"Here, $E$ is Young's modulus, $I$ is the area moment of inertia, $\rho$ is the material "
        r"density, $A$ is the cross-sectional area, and $(\beta_n L)$ is an eigenvalue parameter "
        r"determined by the boundary conditions and mode number. For the first mode of a cantilever "
        r"beam, $(\beta_1 L)$ is a fixed constant (approximately $1.875$)."
    ),
    (
        r"For fixed material properties ($E$, $\rho$) and cross-sectional properties ($I$, $A$), "
        r"and for a specific mode (constant $\beta_n L$), the natural frequency $\omega_n$ is "
        r"inversely proportional to the square of the beam's length $L$: "
        r"$\omega \propto \dfrac{1}{L^2}$."
    ),
    (
        r"Let the initial natural frequency be $\omega_1 = \omega$ for initial length $L_1$. "
        r"The problem states the length is doubled, so the new length $L_2 = 2L_1$."
    ),
    (
        r"Using the proportionality, the ratio of the new frequency $\omega_2$ to the initial "
        r"frequency $\omega_1$ is: "
        r"$\dfrac{\omega_2}{\omega_1} = \left(\dfrac{L_1}{L_2}\right)^2$."
    ),
    (
        r"Substitute $L_2 = 2L_1$: "
        r"$\dfrac{\omega_2}{\omega} = \left(\dfrac{L_1}{2L_1}\right)^2 = \left(\dfrac{1}{2}\right)^2 = \dfrac{1}{4}$."
    ),
    (
        r"Therefore, the new natural frequency $\omega_2 = \dfrac{\omega}{4}$ rad/s."
    ),
]

NEW_FORMULAS_USED = [
    r"$\omega_n = (\beta_n L)^2 \sqrt{\dfrac{EI}{\rho A L^4}}$",
    r"$\omega \propto \dfrac{1}{L^2}$",
    r"$\dfrac{\omega_2}{\omega_1} = \left(\dfrac{L_1}{L_2}\right)^2$",
]

NEW_REASONING = (
    r"For a uniform cantilever beam undergoing transverse vibration (Euler-Bernoulli theory), "
    r"the natural angular frequency for the $n$-th mode is "
    r"$\omega_n = \dfrac{(\beta_n L)^2}{L^2}\sqrt{\dfrac{EI}{\rho A}}$, "
    r"where $E$ is Young's modulus, $I$ is the area moment of inertia, $\rho$ is material density, "
    r"$A$ is the cross-sectional area, and $(\beta_n L)$ is a mode-dependent constant. "
    r"For fixed material and cross-section, $\omega \propto 1/L^2$. "
    r"Doubling $L$ gives $\omega_2/\omega_1 = (L_1/L_2)^2 = (1/2)^2 = 1/4$, "
    r"so the new frequency is $\omega/4$ rad/s. Answer: $\boxed{A}$."
)

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"Scaling law for natural frequency $\omega$ with length $L$ for a uniform cantilever beam?",
        "back": r"$\omega \propto 1/L^2$. From $\omega_n = (\beta_n L)^2\sqrt{EI/(\rho A L^4)}$, all non-$L$ terms are constant for fixed material and section.",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "concept_recall",
        "front": r"How does doubling the length of a cantilever beam change its first natural frequency?",
        "back": r"Frequency becomes $\omega/4$ because $\omega \propto 1/L^2$ and $(1/2)^2 = 1/4$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Why can't you use $\omega = \sqrt{k/m}$ with $k \propto 1/L^3$ for a uniform cantilever beam?",
        "back": r"For a distributed-mass beam, the effective mass also scales with $L$. The correct result is $\omega \propto 1/L^2$. Only for a massless beam with a tip mass does $\omega \propto 1/L^{3/2}$.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": r"Longer beam $\Rightarrow$ lower frequency, squared: $\omega \propto 1/L^2$.",
        "concept": r"$\omega \propto 1/L^2$ for uniform cantilever",
        "effectiveness": "high",
        "context": "Quick recall during MCQ",
    }
]

NEW_COMMON_MISTAKES = [
    {
        "mistake": r"Assuming $\omega \propto 1/L^3$ (confusing stiffness $k \propto 1/L^3$ without accounting for distributed mass).",
        "why_students_make_it": r"Static deflection $\delta \propto L^3/(EI)$ gives $k \propto 1/L^3$. Applying $\omega = \sqrt{k/m}$ without noting $m \propto L$ leads to $\omega \propto 1/L$ or $1/L^{3/2}$, not $1/L^2$.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Use the exact distributed-mass formula $\omega \propto 1/L^2$ directly, or track both $k$ and $m$ length dependencies carefully.",
        "consequence": r"Selects option C ($\omega/16$) instead of A ($\omega/4$).",
    },
    {
        "mistake": r"Using a direct proportionality $\omega \propto L^2$ (sign error in exponent).",
        "why_students_make_it": r"Misremembering $\omega \propto \sqrt{EI/(\rho A)}\cdot L^2$ and forgetting the $L^4$ in the denominator under the root.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Check dimensions: $\omega$ has units s$^{-1}$. From $\omega \propto \sqrt{EI/(\rho A L^4)}$, dimensions yield $\omega \propto 1/L^2$.",
        "consequence": r"Selects option B ($4\omega$) or D ($16\omega$).",
    },
    {
        "mistake": r"Arithmetic error when squaring: calculating $(1/2)^2$ as $1/2$ or $1/8$.",
        "why_students_make_it": "Carelessness or rushing.",
        "type": "Calculation",
        "severity": "Low",
        "frequency": "occasional",
        "how_to_avoid": r"Write $(1/2)^2 = 1/4$ explicitly before substituting.",
        "consequence": "Wrong numerical factor in the final answer.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Direct scaling: recall $\omega \propto 1/L^2$ and answer in under 30 seconds.",
    "guessing_heuristic": r"Longer beam $\Rightarrow$ lower $\omega$. Eliminates B and D. Between A ($\omega/4$) and C ($\omega/16$): inverse-square law gives factor $1/4$.",
    "time_management": "1–2 minutes maximum. High-return if scaling law is memorised.",
}

NEW_ALTERNATIVES = [
    {
        "name": "Rayleigh's Energy Method",
        "description": (
            r"Assume a mode shape (e.g. static deflection curve $y(x) = \delta_0[3(x/L)^2 - (x/L)^3]/2$), "
            r"compute maximum potential energy $U_{\max} = \frac{EI}{2}\int_0^L (y'')^2\,dx$ and "
            r"maximum kinetic energy $T_{\max} = \frac{\rho A \omega^2}{2}\int_0^L y^2\,dx$, "
            r"then set $U_{\max} = T_{\max}$ to extract $\omega$."
        ),
        "pros_cons": "Pros: gives upper-bound estimate without solving PDE; conceptually clear. Cons: slower than direct formula for simple scaling questions.",
        "when_to_use": "When exact formula is forgotten or for beams with variable cross-section.",
    }
]


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning "
                "FROM questions WHERE question_id = :qid"
            ),
            {"qid": QID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"{QID} not found")

        t1, t2, t3 = [deepcopy(x) if x else {} for x in row]

        # tier_1
        av = t1.setdefault("answer_validation", {})
        av["reasoning"] = NEW_REASONING
        exp = t1.setdefault("explanation", {})
        exp["step_by_step"] = NEW_STEP_BY_STEP
        exp["formulas_used"] = NEW_FORMULAS_USED

        # tier_2
        t2["flashcards"] = NEW_FLASHCARDS
        t2["mnemonics_memory_aids"] = NEW_MNEMONICS
        t2["common_mistakes"] = NEW_COMMON_MISTAKES
        t2["exam_strategy"] = NEW_EXAM_STRATEGY

        # tier_3
        t3["alternative_methods"] = NEW_ALTERNATIVES

        now = datetime.utcnow()
        await conn.execute(
            text(
                "UPDATE questions SET "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "tier_2_student_learning = CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning = CAST(:t3 AS jsonb), "
                "updated_at = :ts "
                "WHERE question_id = :qid"
            ),
            {
                "t1": json.dumps(t1),
                "t2": json.dumps(t2),
                "t3": json.dumps(t3),
                "ts": now,
                "qid": QID,
            },
        )

    print(f"Patched {QID}: all LaTeX sections fixed.")


if __name__ == "__main__":
    asyncio.run(main())

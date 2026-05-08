"""
Fix LaTeX / formatting for GATE_2024_AE_Q62.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2024_AE_Q62"

NEW_QUESTION_TEXT = (
    "For a general aviation airplane, one of the complex conjugate pair eigenvalues for longitudinal dynamics is "
    "-0.039 ± 0.0567 i (SI units). If only this mode is excited, find the time for response amplitude to become "
    "half of its initial magnitude (rounded to 1 decimal place)."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    For a general aviation airplane, one complex-conjugate eigenvalue pair for longitudinal dynamics is
    $$\lambda=-0.039\pm 0.0567\,i \quad (\mathrm{SI\ units}).$$
    If only this mode is excited, the time taken for the response amplitude to become half of its initial magnitude is
    $\underline{\qquad\qquad}$ s (rounded to 1 decimal place).
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Write the eigenvalue in standard damped form:
    $$\lambda=-\sigma\pm j\omega,\qquad \sigma=0.039~\mathrm{s^{-1}}.$$

    Amplitude envelope decays as
    $$A(t)=A_0e^{-\sigma t}.$$
    For half amplitude,
    $$\frac{A(t)}{A_0}=\frac{1}{2}=e^{-\sigma t}.$$

    Taking natural log:
    $$-\sigma t=\ln\!\left(\frac{1}{2}\right)=-\ln 2.$$
    Hence,
    $$t=\frac{\ln 2}{\sigma}=\frac{0.693147}{0.039}\approx 17.7729~\mathrm{s}\approx 17.8~\mathrm{s}.$$
    """
).strip()

NEW_STEPS = [
    r"Given eigenvalue: $\lambda=-0.039\pm 0.0567\,i$.",
    r"Compare with $\lambda=-\sigma\pm j\omega$ to identify decay constant $\sigma=0.039~\mathrm{s^{-1}}$.",
    r"Use amplitude envelope relation $A(t)=A_0e^{-\sigma t}$.",
    r"Set half-amplitude condition: $A(t)=\frac{A_0}{2}\Rightarrow e^{-\sigma t}=\frac{1}{2}$.",
    r"Take natural logarithm: $-\sigma t=\ln\!\left(\frac{1}{2}\right)=-\ln 2$.",
    r"Solve: $t=\frac{\ln 2}{\sigma}=\frac{0.693147}{0.039}\approx 17.7729$ s.",
    r"Rounded to one decimal place: $t\approx 17.8$ s.",
]

NEW_FORMULAS_USED = [
    r"$\lambda=-\sigma\pm j\omega$",
    r"$A(t)=A_0e^{-\sigma t}$",
    r"$t_{1/2}=\frac{\ln 2}{\sigma}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Eigenvalue form for damped oscillation",
        "type": "equation",
        "formula": r"$\lambda=-\sigma\pm j\omega$",
        "conditions": r"Stable oscillatory mode has $\sigma>0$.",
        "relevance": "Real part magnitude gives decay rate.",
    },
    {
        "name": "Amplitude decay envelope",
        "type": "equation",
        "formula": r"$A(t)=A_0e^{-\sigma t}$",
        "conditions": "Linear mode response, single mode excitation.",
        "relevance": "Used to impose half-amplitude condition.",
    },
    {
        "name": "Half-amplitude time",
        "type": "equation",
        "formula": r"$t_{1/2}=\frac{\ln 2}{\sigma}$",
        "conditions": "Exponential decay process.",
        "relevance": "Direct numerical answer relation.",
    },
]

NEW_HINTS = [
    r"Imaginary part controls oscillation frequency, not decay envelope.",
    r"Use $\lambda=-\sigma\pm j\omega$, so $\sigma=|\Re(\lambda)|$.",
    r"Half amplitude condition is $e^{-\sigma t}=\frac{1}{2}$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"For exponential decay $A=A_0e^{-\sigma t}$, what is $t_{1/2}$?",
        "back": r"$t_{1/2}=\frac{\ln 2}{\sigma}$",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "concept_recall",
        "front": r"If $\lambda=-0.039\pm 0.0567i$, what is $\sigma$?",
        "back": r"$\sigma=0.039~\mathrm{s^{-1}}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Does imaginary part of eigenvalue affect amplitude half-life?",
        "back": "No. Half-life depends only on decay rate from the real part.",
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "HALF = ln2 / sigma",
        "concept": "Half-amplitude time for exponential decay",
        "effectiveness": "high",
        "context": "Eigenvalue-based damping questions",
    },
    {
        "mnemonic": "Real kills, Imag spins",
        "concept": "Real part damps/grows; imaginary part oscillates",
        "effectiveness": "high",
        "context": "Interpret complex eigenvalues quickly",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Using imaginary part in half-life calculation.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Incorrect time (too low).",
        "how_to_avoid": "Use only real-part magnitude for decay envelope.",
        "why_students_make_it": "Mixes frequency and damping roles.",
    },
    {
        "type": "Sign Error",
        "mistake": "Using negative real part directly and reporting negative time.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Non-physical negative time.",
        "how_to_avoid": r"Map $\lambda=-\sigma\pm j\omega$ first; then use $\sigma>0$.",
        "why_students_make_it": "Sign convention confusion.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Direct formula NAT: identify $\sigma$, apply $t_{1/2}=\ln2/\sigma$, round to one decimal.",
    "guessing_heuristic": r"Use $\ln2\approx0.693$. For $\sigma=0.039$, answer must be near $18$ s.",
    "time_management": "2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "One-step formula after proper eigenvalue interpretation.",
    "Main trap is sign convention and confusing real/imaginary parts.",
]

NEW_ALT_METHODS = [
    {
        "name": "Envelope ratio method",
        "description": r"Use $A(t_2)/A(t_1)=e^{-\sigma(t_2-t_1)}$. Set ratio to $1/2$, then $\Delta t=\ln2/\sigma$.",
        "pros_cons": "Pros: reusable for any amplitude ratio. Cons: same arithmetic as direct half-life formula.",
        "when_to_use": "When problem asks for fraction other than 1/2.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "17.8"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Extract $\sigma$ from eigenvalue $\rightarrow$ apply $e^{-\sigma t}=1/2$ $\rightarrow$ compute and round"
    sbs["key_insights"] = [
        "Decay envelope uses real part only.",
        "Half-amplitude time is independent of oscillation frequency.",
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
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=:opts, "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": None,
                "t1": json.dumps(t1),
                "t2": json.dumps(t2),
                "t3": json.dumps(t3),
                "u": datetime.utcnow(),
                "q": PUBLIC_ID,
            },
        )

    print("patched", PUBLIC_ID)


if __name__ == "__main__":
    asyncio.run(main())

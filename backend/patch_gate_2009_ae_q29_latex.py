import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2009_AE_Q29"

NEW_QUESTION_TEXT_PLAIN = (
    "The linearized dynamics of an aircraft (with no large rotating components) in straight and level flight is given in block form. "
    "Which statement about the 4x4 matrices [A], [B], [C], [D] is true?"
)

NEW_QUESTION_TEXT_LATEX = (
    r"The linearized dynamics of an aircraft (which has no large rotating components) in straight and level flight is written as"
    r" $$\frac{d\mathbf{x}}{dt}=\begin{bmatrix}[A] & [B] \\ [C] & [D]\end{bmatrix}\mathbf{x},$$"
    r" where"
    r" $$\mathbf{x}=\begin{bmatrix}u & w & q & \theta & v & p & r & \phi\end{bmatrix}^{\mathsf{T}},$$"
    r" the superscript $\mathsf{T}$ denotes transpose, and each of $[A],[B],[C],[D]$ is a $4\times 4$ matrix."
    r" If $[0]$ denotes the $4\times 4$ null matrix, which of the following is true?"
)

NEW_OPTIONS = {
    "A": r"$[A]\neq[0],\ [B]\neq[0],\ [C]=[0],\ [D]\neq[0]$",
    "B": r"$[A]=[0],\ [B]\neq[0],\ [C]\neq[0],\ [D]=[0]$",
    "C": r"$[A]\neq[0],\ [B]=[0],\ [C]=[0],\ [D]\neq[0]$",
    "D": r"$[A]\neq[0],\ [B]=[0],\ [C]\neq[0],\ [D]=[0]$",
}

NEW_REASONING = (
    r"The 8-state vector is partitioned as longitudinal states "
    r"$\mathbf{x}_{\text{lon}}=\begin{bmatrix}u&w&q&\theta\end{bmatrix}^\mathsf{T}$ and lateral-directional states "
    r"$\mathbf{x}_{\text{lat}}=\begin{bmatrix}v&p&r&\phi\end{bmatrix}^\mathsf{T}$."
    "\n\n"
    r"In straight, level, symmetric trim with no large rotating components, linearization yields near-decoupled dynamics:"
    "\n"
    r"$\dot{\mathbf{x}}_{\text{lon}}=[A]\mathbf{x}_{\text{lon}}+[B]\mathbf{x}_{\text{lat}}$,"
    "\n"
    r"$\dot{\mathbf{x}}_{\text{lat}}=[C]\mathbf{x}_{\text{lon}}+[D]\mathbf{x}_{\text{lat}}$."
    "\n\n"
    r"The self-dynamics blocks $[A]$ (longitudinal) and $[D]$ (lateral-directional) contain non-zero stability derivatives, so both are non-zero."
    "\n"
    r"Under the given assumptions, coupling blocks between longitudinal and lateral dynamics vanish to first order, so $[B]=[0]$ and $[C]=[0]$."
    "\n\n"
    r"Hence the correct statement is"
    r" $[A]\neq[0],\ [B]=[0],\ [C]=[0],\ [D]\neq[0]$, i.e. option C."
)

NEW_STEP_BY_STEP = [
    r"Read the state ordering: first four states are longitudinal $(u,w,q,\theta)$ and next four are lateral-directional $(v,p,r,\phi)$.",
    r"Interpret the system matrix as 4x4 blocks: self-dynamics blocks $[A],[D]$ and cross-coupling blocks $[B],[C]$.",
    r"For straight, level, symmetric trim, longitudinal and lateral dynamics decouple to first order.",
    r"Therefore coupling blocks vanish: $[B]=[0]$ and $[C]=[0]$.",
    r"Longitudinal and lateral self-dynamics still exist through stability derivatives, so $[A]\neq[0]$ and $[D]\neq[0]$.",
    r"Match with options: only option C satisfies these conditions.",
]

NEW_FORMULAS_USED = [
    r"$\dfrac{d\mathbf{x}}{dt}=\begin{bmatrix}[A] & [B] \\ [C] & [D]\end{bmatrix}\mathbf{x}$",
    r"$\mathbf{x}=\begin{bmatrix}u&w&q&\theta&v&p&r&\phi\end{bmatrix}^{\mathsf{T}}$",
    r"$[B]=[0],\ [C]=[0]$ under linearized longitudinal-lateral decoupling in symmetric trim",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Block state-space partition",
        "type": "equation",
        "formula": r"$\dot{\mathbf{x}}=\begin{bmatrix}[A] & [B] \\ [C] & [D]\end{bmatrix}\mathbf{x}$",
        "relevance": "Separates self-dynamics and cross-coupling between longitudinal and lateral states.",
        "conditions": ["States ordered as longitudinal followed by lateral-directional."],
    },
    {
        "name": "Symmetry-based decoupling",
        "type": "principle",
        "formula": r"$[B]=[0],\ [C]=[0]$ (first-order, straight-level symmetric trim)",
        "relevance": "Identifies which cross-coupling blocks vanish under standard assumptions.",
        "conditions": ["No large rotating components; linearized small-perturbation model."],
    },
    {
        "name": "Non-zero subsystem dynamics",
        "type": "principle",
        "formula": r"$[A]\neq[0],\ [D]\neq[0]$",
        "relevance": "Longitudinal and lateral modes each have intrinsic dynamics.",
        "conditions": ["Physical aircraft with non-zero stability derivatives."],
    },
]

NEW_HINTS = [
    r"Treat $[A],[B],[C],[D]$ as block partitions of an 8x8 system matrix, not as separate input/output matrices.",
    r"Identify first 4 states as longitudinal and last 4 as lateral-directional.",
    r"For symmetric straight-level trim, cross-coupling blocks vanish to first order.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": r"In block form $\dot{x}=\begin{bmatrix}A&B\\C&D\end{bmatrix}x$, what do $B$ and $C$ represent?",
        "back": r"Cross-coupling blocks between longitudinal and lateral-directional state subsets.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"Under symmetric straight-level trim, what is typically true about $[B]$ and $[C]$?",
        "back": r"$[B]=[0]$ and $[C]=[0]$ to first order (decoupled longitudinal/lateral dynamics).",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Common interpretation error in this question?",
        "back": r"Mistaking $[A],[B],[C],[D]$ for state/input/output/disturbance matrices instead of 4x4 block partitions.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": r"Which option matches decoupled symmetric-flight blocks?",
        "back": r"$[A]\neq[0],\ [B]=[0],\ [C]=[0],\ [D]\neq[0]$ (option C).",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Self blocks stay, cross blocks fade",
        "concept": r"$[A],[D]$ non-zero; $[B],[C]$ zero in symmetric decoupling",
        "effectiveness": "high",
        "context": "Block-matrix aircraft dynamics questions",
    },
    {
        "mnemonic": "Long with long, lat with lat",
        "concept": "Decoupled subsystem view in straight-level symmetric trim",
        "effectiveness": "medium",
        "context": "Quick option elimination",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Interpreting [A],[B],[C],[D] as A/B/C/D of standard control form with external input/output matrices.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrong inference that [B] and [C] must be non-zero due to controls/outputs.",
        "how_to_avoid": "Use the given 8-state partition and read [A],[B],[C],[D] as 4x4 blocks of one system matrix.",
        "why_students_make_it": "Notation overlap with control-theory conventions.",
    },
    {
        "type": "Conceptual",
        "mistake": "Assuming straight-level trim makes all blocks zero.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Misses intrinsic longitudinal and lateral dynamics.",
        "how_to_avoid": "Remember equilibrium does not imply zero stability derivatives.",
        "why_students_make_it": "Confusion between trim values and linearized dynamics coefficients.",
    },
    {
        "type": "Conceptual",
        "mistake": "Forgetting the implication of symmetry/no large rotating components on cross-coupling terms.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Incorrectly marks [B] or [C] as non-zero.",
        "how_to_avoid": "Recall first-order decoupling of longitudinal and lateral-directional modes in this condition.",
        "why_students_make_it": "Partial recall of mode-decoupling assumptions.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Identify block meaning first, then apply symmetric-flight decoupling: cross blocks zero, self blocks non-zero.",
    "guessing_heuristic": "If decoupling is remembered, immediately choose the option with [B]=[0] and [C]=[0] but [A],[D] non-zero.",
    "time_management": "1-2 minutes; this is conceptual pattern recognition, not derivation-heavy.",
}

NEW_DIFFICULTY_FACTORS = [
    "Notation ambiguity with standard control A/B/C/D can mislead.",
    "Requires correct conceptual decoupling between longitudinal and lateral blocks.",
    "No arithmetic, but high penalty for interpretation error.",
]

NEW_ALT_METHODS = [
    {
        "name": "Mode-partition argument",
        "description": r"Start from known decoupled longitudinal and lateral linearized equations, then reassemble into an 8x8 block matrix to infer which blocks vanish.",
        "pros_cons": "Pros: physically grounded. Cons: slower if not fluent with mode equations.",
        "when_to_use": "When unsure about notation and wanting a first-principles check.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2009 AE Q29 block matrix dynamics",
    "longitudinal lateral decoupling aircraft",
    "A B C D block partition flight dynamics",
    "no large rotating components aircraft equations",
]


def _merge_unique(a: List[str], b: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in a + b:
        k = x.strip()
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = "C"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    exp["question_nature"] = "Conceptual Application"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = 6
    sbs["solution_path"] = (
        r"Interpret 8x8 block partition $\Rightarrow$ apply symmetric straight-level decoupling "
        r"$\Rightarrow$ infer non-zero/zero status of blocks"
    )

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
    o["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, list(o.get("search_keywords") or []))
    o["alternative_methods"] = NEW_ALT_METHODS
    c = dict(o.get("connections_to_other_subjects") or {})
    c["Control Systems"] = "Careful distinction between block partitions of one system matrix and standard (A,B,C,D) input-output notation is essential."
    o["connections_to_other_subjects"] = c
    return o


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning FROM questions WHERE question_id=:q"),
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
                "qt": NEW_QUESTION_TEXT_PLAIN,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
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

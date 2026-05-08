"""
Fix LaTeX / formatting for GATE_2017_AE_Q26.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2017_AE_Q26"

NEW_QUESTION_TEXT = (
    "Matrix A=[[2,0,2],[3,2,7],[3,1,5]] and vector b=[4,4,5]^T are given. "
    "If x is the solution to A x = b, which of the following is true for x?"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Matrix
    $$\mathbf{A}=\begin{bmatrix}
    2 & 0 & 2\\
    3 & 2 & 7\\
    3 & 1 & 5
    \end{bmatrix},\qquad
    \mathbf{b}=\begin{bmatrix}4\\4\\5\end{bmatrix}$$
    are given. If $\mathbf{x}$ satisfies
    $$\mathbf{A}\mathbf{x}=\mathbf{b},$$
    which of the following is true for $\mathbf{x}$?
    """
).strip()

NEW_OPTIONS = {
    "A": "Solution does not exist",
    "B": "Infinite solutions exist",
    "C": "Unique solution exists",
    "D": "Five possible solutions exist",
}

NEW_REASONING = dedent(
    r"""
    Consider
    $$\mathbf{A}=\begin{bmatrix}
    2 & 0 & 2\\
    3 & 2 & 7\\
    3 & 1 & 5
    \end{bmatrix},\qquad
    \mathbf{b}=\begin{bmatrix}4\\4\\5\end{bmatrix}.$$

    First check determinant:
    $$\det(\mathbf{A})=
    2(2\cdot 5-7\cdot 1)-0(\cdots)+2(3\cdot 1-2\cdot 3)=0.$$
    So unique solution is not possible.

    Use augmented matrix:
    $$[\mathbf{A}\mid\mathbf{b}]=
    \begin{bmatrix}
    2&0&2&4\\
    3&2&7&4\\
    3&1&5&5
    \end{bmatrix}.$$
    Row-reducing gives
    $$\begin{bmatrix}
    1&0&1&2\\
    0&1&2&-1\\
    0&0&0&0
    \end{bmatrix}.$$

    Hence
    $$\operatorname{rank}(\mathbf{A})=\operatorname{rank}([\mathbf{A}\mid\mathbf{b}])=2<3=n.$$
    By Rouche-Capelli theorem, system is consistent with infinitely many solutions.

    Therefore, option **B** is correct.
    """
).strip()

NEW_STEPS = [
    r"Write the system as $\mathbf{A}\mathbf{x}=\mathbf{b}$ with $n=3$ unknowns.",
    r"Compute $\det(\mathbf{A})$; it is zero, so $\mathbf{A}$ is singular.",
    r"Form the augmented matrix $[\mathbf{A}\mid\mathbf{b}]$.",
    r"Apply Gaussian elimination to row-echelon form.",
    r"Count pivots: $\operatorname{rank}(\mathbf{A})=2$ and $\operatorname{rank}([\mathbf{A}\mid\mathbf{b}])=2$.",
    r"Since equal ranks are less than $n=3$, conclude infinitely many solutions.",
]

NEW_FORMULAS_USED = [
    r"$\det(\mathbf{A})$ test for invertibility",
    r"$\operatorname{rank}(\mathbf{A})=\operatorname{rank}([\mathbf{A}\mid\mathbf{b}])<n$",
    r"Free variables $=n-\operatorname{rank}(\mathbf{A})$",
    r"$\operatorname{rank}(\mathbf{A})\ne \operatorname{rank}([\mathbf{A}\mid\mathbf{b}])\Rightarrow$ no solution",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Non-uniqueness condition",
        "type": "equation",
        "formula": r"$\det(\mathbf{A})=0$",
        "conditions": "Square system.",
        "relevance": "Rules out unique solution immediately.",
    },
    {
        "name": "Rouche-Capelli infinite-solution condition",
        "type": "principle",
        "formula": r"$\operatorname{rank}(\mathbf{A})=\operatorname{rank}([\mathbf{A}\mid\mathbf{b}])<n$",
        "conditions": "Linear system with n unknowns.",
        "relevance": "Core classification criterion.",
    },
    {
        "name": "Rouche-Capelli no-solution condition",
        "type": "principle",
        "formula": r"$\operatorname{rank}(\mathbf{A})\ne \operatorname{rank}([\mathbf{A}\mid\mathbf{b}])$",
        "conditions": "Linear system with augmented matrix.",
        "relevance": "Distinguishes inconsistent case.",
    },
]

NEW_HINTS = [
    r"Do not stop at $\det(\mathbf{A})=0$; check ranks.",
    r"Look for contradictory row $[0\ 0\ 0\mid c\ne0]$ after elimination.",
    r"If equal ranks are below n, solution set is infinite.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": r"What does $\det(\mathbf{A})\ne 0$ imply for $\mathbf{A}\mathbf{x}=\mathbf{b}$?",
        "back": "Unique solution exists.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "definition",
        "front": "State Rouche-Capelli consistency condition.",
        "back": r"System is consistent iff $\operatorname{rank}(\mathbf{A})=\operatorname{rank}([\mathbf{A}\mid\mathbf{b}])$.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": r"If $\operatorname{rank}(\mathbf{A})=\operatorname{rank}([\mathbf{A}\mid\mathbf{b}])=2$ and $n=3$, how many solutions?",
        "back": "Infinitely many solutions (one free variable).",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Equal rank = consistent, less than n = infinite",
        "concept": "Fast solution-type decision rule.",
        "effectiveness": "high",
        "context": "Linear-system MCQs",
    },
    {
        "mnemonic": "Zero row fine, contradiction line fatal",
        "concept": r"$[0\cdots 0\mid 0]$ is okay; $[0\cdots0\mid c\ne0]$ means no solution.",
        "effectiveness": "high",
        "context": "Augmented-matrix elimination",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Concluding no solution immediately from $\det(\mathbf{A})=0$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Misclassifies infinite-solution systems.",
        "how_to_avoid": r"Always compare $\operatorname{rank}(\mathbf{A})$ and $\operatorname{rank}([\mathbf{A}\mid\mathbf{b}])$.",
        "why_students_make_it": "Incomplete recall of rank theorem.",
    },
    {
        "type": "Calculation",
        "mistake": "Arithmetic slip during row reduction.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Incorrect rank and wrong option.",
        "how_to_avoid": "Perform one row operation per line and recheck pivots.",
        "why_students_make_it": "Rushed elimination.",
    },
    {
        "type": "Conceptual",
        "mistake": "Treating finite number >1 as possible solution count for linear system.",
        "severity": "Low",
        "frequency": "occasional",
        "consequence": "Falls for distractor options.",
        "how_to_avoid": "Remember: linear systems give 0, 1, or infinitely many solutions.",
        "why_students_make_it": "Confuses with nonlinear systems.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Quick path: compute $\det(\mathbf{A})$. If zero, do 2-3 elimination steps and compare ranks.",
    "guessing_heuristic": r"If rank comparison shows no contradiction and determinant is zero, pick infinite solutions.",
    "time_management": "2-3 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Concept is standard rank theorem application.",
    "Time sink is arithmetic care during elimination.",
]

NEW_ALT_METHODS = [
    {
        "name": "Independent-row rank check",
        "description": "Detect two independent rows/columns first, then verify third is dependent and consistent with b-column relation.",
        "pros_cons": "Pros: quicker with practice. Cons: less systematic than full elimination.",
        "when_to_use": "When matrix structure suggests obvious dependence.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "B"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Determinant check $\rightarrow$ augmented elimination $\rightarrow$ rank comparison"
    sbs["key_insights"] = [
        r"$\det(\mathbf{A})=0$ only says non-unique; rank comparison decides existence type.",
        "Equal ranks below n imply free variable(s) and infinite solutions.",
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
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=CAST(:opts AS jsonb), "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
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

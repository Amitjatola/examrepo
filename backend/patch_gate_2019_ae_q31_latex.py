"""
Fix LaTeX / formatting for GATE_2019_AE_Q31.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q31"

NEW_QUESTION_TEXT = (
    "For real x, the number of points of intersection between y=x and y=cos x is _____."
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    For real $x$, the number of points of intersection between
    $$y=x \quad \text{and} \quad y=\cos x$$
    is \_\_\_\_\_.
    """
).strip()

NEW_REASONING = dedent(
    r"""
    Intersections satisfy
    $$x=\cos x.$$
    Define
    $$f(x)=x-\cos x.$$

    Since $|\cos x|\le 1$, any solution of $x=\cos x$ must lie in $[-1,1]$.
    Also,
    $$f(0)= -1 < 0,\qquad f(1)=1-\cos 1>0.$$
    By continuity, at least one root exists in $(0,1)$.

    Now,
    $$f'(x)=1+\sin x.$$
    For $x\in[-1,1]$, we have $\sin x\in[-\sin 1,\sin 1]$, hence
    $$f'(x)\ge 1-\sin 1>0.$$
    So $f$ is strictly increasing on $[-1,1]$, therefore can have at most one root.

    Existence + uniqueness $\Rightarrow$ exactly one real intersection point.
    """
).strip()

NEW_STEPS = [
    r"Set intersections by equating curves: $x=\cos x$.",
    r"Define $f(x)=x-\cos x$ and solve $f(x)=0$.",
    r"Restrict solution interval using $|\cos x|\le 1 \Rightarrow x\in[-1,1]$.",
    r"Check sign change: $f(0)=-1<0$ and $f(1)=1-\cos 1>0$.",
    r"Use continuity of $f$ to confirm at least one root in $(0,1)$.",
    r"Compute $f'(x)=1+\sin x$ and note $f'(x)>0$ on $[-1,1]$, so root is unique.",
]

NEW_FORMULAS_USED = [
    r"$x=\cos x$",
    r"$f(x)=x-\cos x$",
    r"$f'(x)=1+\sin x$",
    r"$|\cos x|\le 1$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Intersection-to-root conversion",
        "type": "equation",
        "formula": r"$g(x)=h(x)\iff g(x)-h(x)=0$",
        "conditions": "Used to convert curve intersection problem to root-finding.",
        "relevance": "Core setup step.",
    },
    {
        "name": "Intermediate Value Theorem",
        "type": "principle",
        "formula": r"If $f$ is continuous on $[a,b]$ and $f(a)f(b)<0$, then $\exists\,c\in(a,b)$ such that $f(c)=0$.",
        "conditions": "Continuity on closed interval and sign change at endpoints.",
        "relevance": "Proves existence of a root.",
    },
    {
        "name": "Monotonicity via derivative",
        "type": "principle",
        "formula": r"$f'(x)>0$ on an interval $\Rightarrow f$ is strictly increasing there.",
        "conditions": "Derivative exists and remains positive.",
        "relevance": "Proves uniqueness of root.",
    },
]

NEW_HINTS = [
    r"Convert intersection count to root count of $x-\cos x=0$.",
    r"Use boundedness: if $x=\cos x$, then $x$ must lie in $[-1,1]$.",
    r"Use IVT for existence and derivative sign for uniqueness.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": r"How do you count intersections of $y=g(x)$ and $y=h(x)$?",
        "back": r"Solve $g(x)-h(x)=0$ and count real roots.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"For $x=\cos x$, how many real solutions exist?",
        "back": "Exactly one.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Why is IVT alone insufficient in this problem?",
        "back": r"IVT proves at least one root, not uniqueness; use monotonicity via $f'(x)$.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Bound then prove",
        "concept": r"First bound roots with $|\cos x|\le 1$, then prove one root using IVT + monotonicity.",
        "effectiveness": "high",
        "context": "Root-count problems with trig and line",
    },
    {
        "mnemonic": "IVT gives one, slope locks one",
        "concept": "Existence comes from sign change; uniqueness from strictly increasing behavior.",
        "effectiveness": "high",
        "context": "Fast NAT logic chain",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Using only rough graph and claiming multiple intersections.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrong root count.",
        "how_to_avoid": r"Always verify analytically with $f(x)=x-\cos x$, IVT, and $f'(x)$ sign.",
        "why_students_make_it": "Cosine oscillation creates false intuition.",
    },
    {
        "type": "Proof Gap",
        "mistake": "Proving existence but not uniqueness.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Incomplete or incorrect conclusion.",
        "how_to_avoid": r"After IVT, check monotonicity using derivative.",
        "why_students_make_it": "Stops after first sign change check.",
    },
    {
        "type": "Calculation",
        "mistake": r"Derivative sign error: writing $\frac{d}{dx}(-\cos x)=-\sin x$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Wrong monotonicity conclusion.",
        "how_to_avoid": r"Remember $\frac{d}{dx}(-\cos x)=+\sin x$, so $f'(x)=1+\sin x$.",
        "why_students_make_it": "Trig derivative memory slip.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Do 3-line proof: define $f(x)=x-\cos x$, show sign change on $(0,1)$, show $f'(x)>0$ on $[-1,1]$.",
    "guessing_heuristic": "If rushed, answer 1 (line vs bounded cosine intersects once).",
    "time_management": "1-2 minutes.",
}

NEW_DIFFICULTY_FACTORS = [
    "Conceptually easy, but requires existence plus uniqueness proof.",
    "Most errors arise from derivative/sign handling and incomplete argument.",
]

NEW_ALT_METHODS = [
    {
        "name": "Fixed-point contraction view",
        "description": r"On $[-1,1]$, iterate $x_{n+1}=\cos x_n$. Since $|\!-\sin x|\le \sin 1<1$ here, mapping is a contraction, giving a unique fixed point.",
        "pros_cons": "Pros: elegant uniqueness argument. Cons: heavier than standard IVT + monotonicity for exam.",
        "when_to_use": "For deeper understanding or numerical-method linkage.",
    }
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "1"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Application"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Set $x=\cos x$ $\rightarrow$ define $f(x)$ $\rightarrow$ IVT existence $\rightarrow$ monotonicity uniqueness"
    sbs["key_insights"] = [
        r"Boundedness of $\cos x$ localizes search to $[-1,1]$.",
        r"$f'(x)>0$ on that interval guarantees only one crossing.",
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
                "SELECT options, tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning "
                "FROM questions WHERE question_id=:q"
            ),
            {"q": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit("Question not found")

        options = row[0]
        t1 = patch_t1(row[1])
        t2 = patch_t2(row[2])
        t3 = patch_t3(row[3])

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, options=CAST(:opts AS jsonb), "
                "tier_1_core_research=CAST(:t1 AS jsonb), tier_2_student_learning=CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning=CAST(:t3 AS jsonb), updated_at=:u WHERE question_id=:q"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(options),
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

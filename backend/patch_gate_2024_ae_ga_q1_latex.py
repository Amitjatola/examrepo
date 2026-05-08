"""
Fix LaTeX / formatting for GATE_2024_AE_GA_Q1.
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2024_AE_GA_Q1"

NEW_QUESTION_TEXT = (
    "If '->' denotes increasing order of intensity, then the meaning of the words "
    "[dry -> arid -> parched] is analogous to [diet -> fast -> ________]. "
    "Which one of the given options is appropriate to fill the blank?"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    If $\rightarrow$ denotes increasing order of intensity, then the meaning of the words
    \[
    \text{dry} \rightarrow \text{arid} \rightarrow \text{parched}
    \]
    is analogous to
    \[
    \text{diet} \rightarrow \text{fast} \rightarrow \underline{\hspace{2cm}}.
    \]
    Which one of the given options is appropriate to fill the blank?
    """
).strip()

NEW_OPTIONS = {
    "A": "starve",
    "B": "reject",
    "C": "feast",
    "D": "deny",
}

NEW_REASONING = dedent(
    r"""
    The relation is an increasing intensity scale.

    In the first sequence:
    \[
    \text{dry} \rightarrow \text{arid} \rightarrow \text{parched}
    \]
    each word is a stronger form of dryness.

    Apply the same pattern to food intake:
    \[
    \text{diet} \rightarrow \text{fast} \rightarrow ?
    \]
    where $\text{diet}$ is controlled intake, $\text{fast}$ is temporary abstinence, and the strongest form is $\text{starve}$.

    Hence, the correct option is **A (starve)**.
    """
).strip()

NEW_STEPS = [
    r"Identify pattern in the first chain: intensity increases from $\text{dry}$ to $\text{parched}$.",
    r"Transfer the same pattern to the second chain: $\text{diet} \rightarrow \text{fast} \rightarrow ?$.",
    r"Evaluate options by intensity of food deprivation.",
    r"$\text{starve}$ matches the extreme end; $\text{reject}$ and $\text{deny}$ are semantically unrelated.",
    r"$\text{feast}$ is opposite in direction (abundance, not deprivation).",
    r"Select $\boxed{\text{A: starve}}$.",
]

NEW_FORMULAS_USED = [
    r"No numeric formula is required; this is an analogy based on monotonic intensity ordering.",
    r"Pattern template: $A_1 \to A_2 \to A_3$ with increasing severity.",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Verbal analogy by intensity scaling",
        "type": "principle",
        "formula": r"$A_1 \rightarrow A_2 \rightarrow A_3$ (increasing intensity)",
        "conditions": "All terms must belong to the same semantic axis.",
        "relevance": "Maps the dryness scale to the food-deprivation scale.",
    }
]

NEW_HINTS = [
    r"Focus on *degree* (mild $\to$ strong $\to$ extreme), not just topic similarity.",
    r"In the second chain, words must remain in the food-intake/deprivation domain.",
    r"Eliminate opposite-direction word first: $\text{feast}$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": "What relation is tested in this analogy question?",
        "back": r"Increasing intensity: $A_1 \rightarrow A_2 \rightarrow A_3$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"Complete: $\text{diet} \rightarrow \text{fast} \rightarrow$ ?",
        "back": r"$\text{starve}$",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Why is 'feast' incorrect?",
        "back": "It reverses the direction of intensity; it indicates abundance, not deprivation.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "DAP-DFS ladder",
        "concept": r"$\text{Dry} \to \text{Arid} \to \text{Parched}$ and $\text{Diet} \to \text{Fast} \to \text{Starve}$",
        "effectiveness": "high",
        "context": "Intensity-based analogy questions",
    },
    {
        "mnemonic": "Same axis, same arrow",
        "concept": "Keep both triplets on one semantic axis and preserve direction.",
        "effectiveness": "medium",
        "context": "Verbal analogy elimination",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Matching topic only, not intensity progression.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Attractive but wrong option selection.",
        "how_to_avoid": "State the exact relation in words before checking options.",
        "why_students_make_it": "They stop at superficial similarity.",
    },
    {
        "type": "Elimination",
        "mistake": "Keeping opposite-direction options like 'feast'.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Logical inversion of the pattern.",
        "how_to_avoid": "Check whether each option increases deprivation.",
        "why_students_make_it": "Misses directionality of analogy.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Identify relation in first triplet in 3-5 seconds, then map same relation to options.",
    "guessing_heuristic": "Remove semantic mismatch and direction mismatch first; choose strongest same-axis word.",
    "time_management": "30-45 seconds.",
}

NEW_DIFFICULTY_FACTORS = [
    "Requires precise identification of relation type (intensity, not synonymy alone).",
    "Distractors are linguistically valid words but semantically off-axis.",
]

NEW_ALT_METHODS = [
    {
        "name": "Axis-and-direction check",
        "description": r"Build an axis: deprivation level. Place $\text{diet}$, $\text{fast}$, and each option on that axis; pick the next higher point.",
        "pros_cons": "Pros: robust against vocabulary traps. Cons: slightly slower than direct intuition.",
        "when_to_use": "When two options seem close.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE GA analogy intensity",
    "verbal analogy increasing order",
    "diet fast starve analogy",
    "word relationship intensity scale",
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "A"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Application"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = r"Identify intensity relation $\to$ map to second chain $\to$ eliminate distractors"
    sbs["key_insights"] = [
        "Relation type controls the answer more than raw vocabulary overlap.",
        "Direction of progression (mild to extreme) must be preserved.",
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
    o["search_keywords"] = NEW_SEARCH_KEYWORDS
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

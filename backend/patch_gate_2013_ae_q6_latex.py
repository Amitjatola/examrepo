"""
Fix LaTeX / formatting for GATE_2013_AE_Q6 (attitude indicator instrument question).

Usage (from backend/):
  PYTHONPATH=. python patch_gate_2013_ae_q6_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2013_AE_Q6"

NEW_QUESTION_TEXT_PLAIN = (
    "Which one of the following flight instruments is used on an aircraft to determine its attitude in flight?"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Which one of the following flight instruments is used on an aircraft to determine its
    attitude (pitch and roll) in flight?
    """
).strip()

NEW_OPTIONS = {
    "A": "Vertical speed indicator",
    "B": "Altimeter",
    "C": "Artificial horizon (attitude indicator)",
    "D": "Turn-bank indicator",
}

NEW_REASONING = dedent(
    r"""
    Aircraft **attitude** means orientation in pitch and roll relative to the horizon.
    The instrument designed to display this directly is the **Artificial Horizon** (also called
    the **Attitude Indicator**).

    - **Vertical Speed Indicator (VSI):** rate of climb/descent.
    - **Altimeter:** pressure altitude.
    - **Turn-bank indicator:** turn rate and slip/skid coordination.

    Therefore, the correct option is **C**.
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Identify the keyword **attitude**: it refers to pitch and roll orientation.",
    r"Match each instrument with function: VSI $\rightarrow$ vertical rate, altimeter $\rightarrow$ altitude, turn-bank $\rightarrow$ turn/slip.",
    r"Artificial horizon (attitude indicator) is the only instrument that directly shows pitch and roll against a horizon reference.",
    r"Select option **C**.",
]

NEW_FORMULAS_USED = [
    r"Attitude is represented by pitch and roll angles, commonly denoted $(\theta,\phi)$.",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Aircraft attitude",
        "type": "principle",
        "formula": r"Attitude $\equiv$ pitch ($\theta$) and roll ($\phi$)",
        "relevance": "The question asks which instrument determines this orientation.",
        "conditions": ["Body orientation with respect to local horizon."],
    },
    {
        "name": "Gyroscopic/inertial reference",
        "type": "principle",
        "formula": r"Attitude indicator uses inertial (historically gyroscopic) horizon reference",
        "relevance": "Explains why this instrument can display pitch/roll directly.",
        "conditions": ["Traditional gyro AI or modern AHRS/PFD implementation."],
    },
]

NEW_HINTS = [
    r"Do not confuse **attitude** with **altitude**.",
    r"If it shows pitch and roll relative to a horizon bar, it is the attitude indicator.",
    r"VSI and turn-bank give rates/coordination, not full attitude.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": "Which cockpit instrument directly indicates aircraft pitch and roll?",
        "back": "Artificial horizon / attitude indicator.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "definition",
        "front": "What does aircraft attitude mean?",
        "back": r"Orientation of the aircraft: pitch ($\theta$) and roll ($\phi$) relative to horizon.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Why is the altimeter not the correct answer here?",
        "back": "Altimeter gives height (altitude), not orientation (attitude).",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": "In IMC (no outside view), which instrument is primary for keeping wings level and pitch set?",
        "back": "Attitude indicator (artificial horizon).",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "ATTitude = ARTificial horizon",
        "concept": "Artificial horizon determines attitude",
        "effectiveness": "high",
        "context": "Quick exam recall",
    },
    {
        "mnemonic": "Altitude is height, attitude is angle",
        "concept": r"Distinguish altitude from pitch/roll $(\theta,\phi)$",
        "effectiveness": "high",
        "context": "Avoid keyword confusion",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Confusing attitude with altitude and choosing altimeter.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Wrong option despite knowing instrument panel basics.",
        "how_to_avoid": "Translate words first: attitude = orientation angles; altitude = vertical distance.",
        "why_students_make_it": "Similar-sounding terms under time pressure.",
    },
    {
        "type": "Conceptual",
        "mistake": "Choosing turn-bank indicator as a full attitude display.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Misidentifies a rate/coordination instrument as an orientation instrument.",
        "how_to_avoid": "Remember turn-bank shows turn rate and slip/skid, not direct pitch/roll horizon picture.",
        "why_students_make_it": "Both are gyroscopic-class instruments in traditional panels.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": "Single-concept recall: map each instrument to its primary variable, then pick attitude indicator.",
    "guessing_heuristic": "If options include Artificial Horizon/Attitude Indicator for an attitude question, it is almost always correct.",
    "time_management": "Under 30 seconds.",
}

NEW_DIFFICULTY_FACTORS = [
    "Terminology confusion: attitude vs altitude.",
    "Need to distinguish primary function of closely related cockpit instruments.",
]

NEW_ALT_METHODS = [
    {
        "name": "Elimination by measurement type",
        "description": "Eliminate instruments that measure rates or scalar states (VSI, altimeter, turn rate) and retain the one that shows orientation.",
        "pros_cons": "Pros: very fast. Cons: requires basic instrument-function mapping.",
        "when_to_use": "For direct MCQ recall questions under time pressure.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2013 AE Q6 attitude indicator",
    "artificial horizon function",
    "attitude vs altitude instrument",
    "flight instrument pitch roll",
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
    exp["question_nature"] = "Conceptual"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["solution_path"] = (
        r"Interpret 'attitude' $\Rightarrow$ map instrument functions $\Rightarrow$ select attitude indicator"
    )
    sbs["key_insights"] = [
        "Artificial horizon is the direct pitch/roll display.",
        "Other options measure altitude, vertical rate, or turn coordination.",
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
    o["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, list(o.get("search_keywords") or []))

    conn = o.get("connections_to_other_subjects")
    if isinstance(conn, dict):
        conn = deepcopy(conn)
        # remove duplicate key variants if both appear
        if "Physics (Mechanics)" in conn and "Physics" in conn:
            conn.pop("Physics (Mechanics)", None)
        o["connections_to_other_subjects"] = conn

    return o


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning, options "
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
        existing_options = row[3]

        await conn.execute(
            text(
                "UPDATE questions SET question_text=:qt, question_text_latex=:qtl, "
                "options=CAST(:opts AS jsonb), tier_1_core_research=CAST(:t1 AS jsonb), "
                "tier_2_student_learning=CAST(:t2 AS jsonb), tier_3_enhanced_learning=CAST(:t3 AS jsonb), "
                "updated_at=:u WHERE question_id=:q"
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

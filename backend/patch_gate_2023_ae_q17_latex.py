import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q17"

NEW_QUESTION_TEXT_PLAIN = (
    "An ideal glider has drag characteristics given by "
    "C_D = C_{D_0} + C_{D_i}, where C_{D_i} = K C_L^2 is the induced drag coefficient, "
    "C_L is the lift coefficient, and K is a constant. For maximum range of the glider, "
    "the ratio C_{D_0}/C_{D_i} is"
)

NEW_QUESTION_TEXT_LATEX = (
    r"An ideal glider has drag characteristics given by "
    r"$C_D = C_{D_0} + C_{D_i}$, where $C_{D_i} = K C_L^2$ is the induced drag coefficient, "
    r"$C_L$ is the lift coefficient, and $K$ is a constant. "
    r"For maximum range of the glider, the ratio $\dfrac{C_{D_0}}{C_{D_i}}$ is"
)

NEW_OPTIONS = {
    "A": "$1$",
    "B": r"$\dfrac{1}{3}$",
    "C": "$3$",
    "D": r"$\dfrac{3}{2}$",
}

NEW_REASONING = (
    r"For an ideal glider in still air, maximum range corresponds to maximum aerodynamic efficiency "
    r"$(L/D)_{\max}$. With the parabolic drag polar"
    "\n"
    r"$C_D = C_{D_0} + K C_L^2 = C_{D_0} + C_{D_i}$,"
    "\n"
    r"we write"
    "\n"
    r"$\dfrac{L}{D} = \dfrac{C_L}{C_D} = \dfrac{C_L}{C_{D_0} + K C_L^2}$."
    "\n\n"
    r"Maximize with respect to $C_L$:"
    "\n"
    r"$\dfrac{d}{dC_L}\left(\dfrac{C_L}{C_{D_0}+K C_L^2}\right)=0$."
    "\n"
    r"Using quotient rule, numerator condition is"
    "\n"
    r"$(C_{D_0}+K C_L^2)-C_L(2K C_L)=0"
    r"\Rightarrow C_{D_0}-K C_L^2=0"
    r"\Rightarrow C_{D_0}=K C_L^2=C_{D_i}$."
    "\n\n"
    r"Hence $\dfrac{C_{D_0}}{C_{D_i}}=1$, so option A is correct."
)

NEW_STEP_BY_STEP = [
    r"For an ideal glider, maximum range occurs at maximum lift-to-drag ratio $(L/D)_{\max}$.",
    r"Use the drag polar: $C_D = C_{D_0} + C_{D_i}$ with $C_{D_i}=K C_L^2$, so $C_D=C_{D_0}+K C_L^2$.",
    r"Write efficiency in coefficient form: $\dfrac{L}{D}=\dfrac{C_L}{C_D}=\dfrac{C_L}{C_{D_0}+K C_L^2}$.",
    r"Apply optimum condition: $\dfrac{d}{dC_L}\left(\dfrac{C_L}{C_{D_0}+K C_L^2}\right)=0$.",
    r"From quotient-rule numerator: $(C_{D_0}+K C_L^2)-2K C_L^2=0 \Rightarrow C_{D_0}=K C_L^2$.",
    r"Since $K C_L^2=C_{D_i}$, we get $C_{D_0}=C_{D_i}$.",
    r"Therefore $\dfrac{C_{D_0}}{C_{D_i}}=1$.",
]

NEW_FORMULAS_USED = [
    r"$C_D = C_{D_0} + C_{D_i}$",
    r"$C_{D_i}=K C_L^2$",
    r"$\dfrac{L}{D}=\dfrac{C_L}{C_D}$",
    r"$\dfrac{d}{dC_L}\left(\dfrac{C_L}{C_{D_0}+K C_L^2}\right)=0$",
    r"$C_{D_0}=C_{D_i}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Parabolic drag polar",
        "type": "equation",
        "formula": r"$C_D = C_{D_0} + K C_L^2$",
        "relevance": "Defines total drag as parasite plus induced component.",
        "conditions": ["Standard parabolic approximation in subsonic regime."],
    },
    {
        "name": "Glider range criterion",
        "type": "principle",
        "formula": r"$\text{Maximum range} \Leftrightarrow (L/D)_{\max}$",
        "relevance": "For unpowered glide in still air, maximizing distance per altitude loss.",
        "conditions": ["Ideal glider assumptions."],
    },
    {
        "name": "Efficiency ratio",
        "type": "equation",
        "formula": r"$\dfrac{L}{D}=\dfrac{C_L}{C_D}$",
        "relevance": "Optimization variable relation in coefficient form.",
        "conditions": ["Steady flight coefficient representation."],
    },
    {
        "name": "Optimum condition at max L/D",
        "type": "principle",
        "formula": r"$C_{D_0}=C_{D_i}$",
        "relevance": "Gives the direct ratio asked in the question.",
        "conditions": ["Derived from maximizing $C_L/(C_{D_0}+K C_L^2)$."],
    },
]

NEW_HINTS = [
    r"For gliders, maximize $L/D$ for maximum range.",
    r"Substitute $C_{D_i}=K C_L^2$ into $C_D$ before differentiating.",
    r"At $(L/D)_{\max}$ for a parabolic polar, parasite and induced drag coefficients are equal.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "Drag polar for ideal glider?",
        "back": r"$C_D=C_{D_0}+K C_L^2$, with $C_{D_i}=K C_L^2$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "concept_recall",
        "front": "Glider maximum range corresponds to maximizing what?",
        "back": r"$L/D$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"At $(L/D)_{\max}$, what is $C_{D_0}/C_{D_i}$?",
        "back": r"$1$, because $C_{D_0}=C_{D_i}$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Which condition is for jet max range, not glider max range?",
        "back": r"Jet max range uses maximizing $C_L^{1/2}/C_D$, giving $C_{D_i}=\dfrac{1}{3}C_{D_0}$.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Best Glide: Drag Split Equal",
        "concept": r"At $(L/D)_{\max}$, $C_{D_0}=C_{D_i}$",
        "effectiveness": "high",
        "context": "Glider max-range questions",
    },
    {
        "mnemonic": r"3 - 1 - 1/3 ladder: prop endurance, max $L/D$, jet range",
        "concept": "Remember common induced/parasite drag ratios",
        "effectiveness": "medium",
        "context": "Avoid mixing aircraft-performance criteria",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Using jet/prop criteria instead of glider max-range criterion.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Chooses 1/3 or 3 instead of 1.",
        "how_to_avoid": r"First identify platform: glider max range $\Rightarrow (L/D)_{\max}$.",
        "why_students_make_it": "Memorized formulas without aircraft-type filtering.",
    },
    {
        "type": "Calculation",
        "mistake": "Algebra error after differentiation of $C_L/(C_{D_0}+K C_L^2)$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Wrong optimum condition.",
        "how_to_avoid": "Set only numerator to zero; simplify stepwise.",
        "why_students_make_it": "Rushed quotient-rule execution.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Immediate recall path: glider max range $\Rightarrow (L/D)_{\max} \Rightarrow C_{D_0}=C_{D_i}$.",
    "guessing_heuristic": "If uncertain between standard ratios, pick 1 for glider max-range condition.",
    "time_management": "30-60 s with recall, <2 min with derivation.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Need correct mapping: glider maximum range $\leftrightarrow$ maximize $L/D$.",
    "Short calculus step required if formula not remembered.",
]

NEW_ALT_METHODS = [
    {
        "name": "Graphical tangent method on drag polar",
        "description": (
            r"On $C_D$ vs $C_L$ plot, $(L/D)_{\max}$ is tangent from origin. "
            r"Equating tangent slope $C_D/C_L$ with local slope $dC_D/dC_L$ yields $C_{D_0}=K C_L^2=C_{D_i}$."
        ),
        "pros_cons": "Pros: high intuition. Cons: slower for exam algebraic answer.",
        "when_to_use": "Concept checks, visual understanding, or when derivative form is forgotten.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2023 AE Q17 glider max range",
    "CD0 equals CDi condition",
    "maximum L over D derivation",
    "drag polar optimum glider",
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
    av["correct_answer"] = "A"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = 7
    sbs["solution_path"] = (
        r"Identify glider criterion $(L/D)_{\max}$ $\Rightarrow$ write drag polar form "
        r"$\Rightarrow$ optimize $C_L/(C_{D_0}+K C_L^2)$ $\Rightarrow$ use $C_{D_i}=K C_L^2$"
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
    c["Aerodynamics"] = r"Parabolic polar $C_D=C_{D_0}+K C_L^2$ and induced drag modeling drive the optimum condition."
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

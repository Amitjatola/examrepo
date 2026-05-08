import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2013_AE_Q30"

NEW_QUESTION_TEXT_PLAIN = (
    "A glider is launched from a 500 m high hilltop. Following data is available for the glider: "
    "zero-lift drag coefficient C_{D_0} = 0.02, aspect ratio AR = 10, and Oswald efficiency factor e = 0.95. "
    "The maximum range of the glider in km is ________"
)

NEW_QUESTION_TEXT_LATEX = (
    r"A glider is launched from a $500~\mathrm{m}$ high hilltop. Following data is available for the glider: "
    r"zero-lift drag coefficient $C_{D_0}=0.02$, aspect ratio $AR=10$, and Oswald efficiency factor $e=0.95$. "
    r"The maximum range of the glider in km is $\underline{\hspace{5em}}$."
)

NEW_REASONING = (
    r"For steady unpowered glide in still air, maximum horizontal range is"
    r" $R_{\max}=h\,(L/D)_{\max}$."
    "\n\n"
    r"Use parabolic drag polar: $C_D=C_{D_0}+K C_L^2$, with "
    r"$K=\dfrac{1}{\pi e AR}$."
    "\n"
    r"$K=\dfrac{1}{\pi\times0.95\times10}\approx 0.033506$."
    "\n\n"
    r"At $(L/D)_{\max}$, parasite drag equals induced drag:"
    r" $C_{D_0}=K C_L^2$."
    "\n"
    r"Hence $(L/D)_{\max}=\dfrac{1}{2\sqrt{C_{D_0}K}}"
    r"=\dfrac{\sqrt{\pi e AR C_{D_0}}}{2C_{D_0}}"
    r"\approx 19.315$."
    "\n\n"
    r"Therefore"
    r" $R_{\max}=500\times19.315=9657.5~\mathrm{m}=9.6575~\mathrm{km}$."
    "\n"
    r"So the required maximum range is approximately $9.66~\mathrm{km}$ (within key band 9 to 10 km)."
)

NEW_STEP_BY_STEP = [
    r"For a glider, maximum range occurs at maximum aerodynamic efficiency $(L/D)_{\max}$.",
    r"Use $R_{\max}=h\,(L/D)_{\max}$ with $h=500~\mathrm{m}$.",
    r"Write drag polar: $C_D=C_{D_0}+K C_L^2$, where $K=\dfrac{1}{\pi e AR}$.",
    r"Compute $K=\dfrac{1}{\pi\cdot0.95\cdot10}\approx0.033506$.",
    r"At optimum, $C_{D_0}=K C_L^2$, giving $(L/D)_{\max}=\dfrac{1}{2\sqrt{C_{D_0}K}}\approx19.315$.",
    r"Compute range: $R_{\max}=500\times19.315=9657.5~\mathrm{m}$.",
    r"Convert to km: $R_{\max}=9.6575~\mathrm{km}\approx9.66~\mathrm{km}$."
]

NEW_FORMULAS_USED = [
    r"$C_D=C_{D_0}+K C_L^2$",
    r"$K=\dfrac{1}{\pi e AR}$",
    r"$(L/D)_{\max}=\dfrac{1}{2\sqrt{C_{D_0}K}}=\dfrac{\sqrt{\pi e AR C_{D_0}}}{2C_{D_0}}$",
    r"$R_{\max}=h\,(L/D)_{\max}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Parabolic drag polar",
        "type": "equation",
        "formula": r"$C_D=C_{D_0}+K C_L^2$",
        "relevance": "Model for total drag in terms of parasite and induced parts.",
        "conditions": ["Subsonic parabolic-polar approximation."],
    },
    {
        "name": "Induced drag factor",
        "type": "equation",
        "formula": r"$K=\dfrac{1}{\pi e AR}$",
        "relevance": "Connects geometry/efficiency with induced drag level.",
        "conditions": ["Finite-wing induced drag model."],
    },
    {
        "name": "Maximum-glide condition",
        "type": "principle",
        "formula": r"$C_{D_0}=K C_L^2$ at $(L/D)_{\max}$",
        "relevance": "Optimum condition used to compute $(L/D)_{\max}$.",
        "conditions": ["Steady glide with parabolic drag polar."],
    },
    {
        "name": "Maximum glide range",
        "type": "equation",
        "formula": r"$R_{\max}=h\,(L/D)_{\max}$",
        "relevance": "Final range expression for still-air glide.",
        "conditions": ["Steady, unpowered glide; no wind."],
    },
]

NEW_HINTS = [
    r"Start with $R_{\max}=h\,(L/D)_{\max}$.",
    r"Compute $K$ correctly as $1/(\pi e AR)$, not $\pi e AR$.",
    r"At optimum glide, use $C_{D_0}=K C_L^2$ to get $(L/D)_{\max}$ quickly.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "Maximum glide range formula?",
        "back": r"$R_{\max}=h\,(L/D)_{\max}$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "concept_recall",
        "front": "Condition at $(L/D)_{\max}$ for parabolic polar?",
        "back": r"$C_{D_0}=K C_L^2$ (parasite drag equals induced drag).",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "formula_recall",
        "front": "Expression for $K$?",
        "back": r"$K=\dfrac{1}{\pi e AR}$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": "Given $h=500~\mathrm{m}$ and $(L/D)_{\max}=19.315$, range?",
        "back": r"$R_{\max}=9657.5~\mathrm{m}=9.66~\mathrm{km}$ (approx).",
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Glide Range = Height times Best L over D",
        "concept": r"$R_{\max}=h\,(L/D)_{\max}$",
        "effectiveness": "high",
        "context": "Fast recall for glide-range NATs",
    },
    {
        "mnemonic": "Peak Glide: Parasite equals Induced",
        "concept": r"$C_{D_0}=K C_L^2$ at optimum",
        "effectiveness": "high",
        "context": "Deriving $(L/D)_{\max}$",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": r"Using $K=\pi e AR$ instead of $K=1/(\pi e AR)$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Severely wrong $(L/D)_{\max}$ and range.",
        "how_to_avoid": r"Write induced-drag term first: $C_{D_i}=\dfrac{C_L^2}{\pi e AR}=K C_L^2$.",
        "why_students_make_it": "Reciprocal confusion under time pressure.",
    },
    {
        "type": "Units",
        "mistake": "Leaving final range in meters when answer asks km.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": "Value off by factor 1000 in final unit.",
        "how_to_avoid": "Do explicit final conversion by dividing by 1000.",
        "why_students_make_it": "Rushed final step.",
    },
    {
        "type": "Conceptual",
        "mistake": "Using wrong optimum relation for $(L/D)_{\max}$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Incorrect answer band.",
        "how_to_avoid": r"Remember at best glide: $C_{D_0}=C_{D_i}$.",
        "why_students_make_it": "Mixing with other performance optima.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Compute $K$, then $(L/D)_{\max}$, then multiply by $h$, then convert to km.",
    "guessing_heuristic": "Expected range order is around 9-10 km (since 500 m times L/D near 20).",
    "time_management": "2-3 minutes with careful arithmetic and final unit conversion.",
}

NEW_DIFFICULTY_FACTORS = [
    "Direct substitution once formulas are recalled.",
    r"Arithmetic care needed for $K$ and square root.",
    "Final unit conversion (m to km).",
]

NEW_ALT_METHODS = [
    {
        "name": "Energy-balance derivation",
        "description": r"Use $mgh=D\,R$ and $L\approx W$ in steady shallow glide to recover $R=h(L/D)$, then apply $(L/D)_{\max}$.",
        "pros_cons": "Pros: physical intuition. Cons: still needs best-glide condition for final numeric answer.",
        "when_to_use": "Conceptual explanation or first-principles checks.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2013 AE Q30 glider range",
    "maximum glide range formula",
    "CD0 K CL2 drag polar",
    "best L over D glider",
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
    av["correct_answer"] = "9.66 km (approx; key band 9 to 10 km)"

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
        r"Use $R_{\max}=h(L/D)_{\max}$ $\Rightarrow$ compute $K=1/(\pi e AR)$ "
        r"$\Rightarrow$ get $(L/D)_{\max}$ $\Rightarrow$ compute and convert range"
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
    c["Aerodynamics"] = r"Drag polar $C_D=C_{D_0}+K C_L^2$ and induced-drag scaling govern best-glide performance."
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
                "opts": json.dumps(None),
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

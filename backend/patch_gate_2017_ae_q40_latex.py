"""
Fix GATE_2017_AE_Q40 LaTeX: min thrust / max L/D ⇒ $C_{D,0}=C_{D,i}=KC_L^2$, $AR=C_L^2/(\pi e C_{D,0})$.

NAT $\approx 10.186$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2017_ae_q40_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2017_AE_Q40"

NEW_QUESTION_TEXT_PLAIN = (
    "A conventional low-speed aircraft has the following aerodynamic characteristics: "
    "zero-lift drag coefficient C_D,0 = 0.020 and Oswald efficiency e = 1.0. "
    "The aircraft is flown to maintain steady level flight at minimum thrust required, "
    "at a lift coefficient C_L = 0.8. The numerical value of the aspect ratio of the wing is "
    "______ (in three decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    r"A conventional low-speed aircraft has $C_{D,0}=0.020$ and Oswald efficiency $e=1.0$. "
    r"It flies steady level flight at minimum thrust required with $C_L=0.8$. "
    r"The wing aspect ratio is $\underline{\hspace{3.5em}}$ (three decimal places)."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"For steady level flight with parabolic polar $C_D=C_{D,0}+KC_L^2$, $K=\dfrac{1}{\pi e AR}$, "
    r"thrust required $T=D$ is minimized when $L/D$ is maximized. For jet aircraft this occurs when "
    r"parasite (zero-lift) drag equals induced drag:"
    "\n"
    r"$C_{D,0}=C_{D,i}=KC_L^2=\dfrac{C_L^2}{\pi e AR}$."
    "\n\n"
    r"Hence $AR=\dfrac{C_L^2}{\pi e C_{D,0}}$. With $C_L=0.8$, $e=1.0$, $C_{D,0}=0.020$:"
    "\n"
    r"$AR=\dfrac{0.64}{\pi(0.020)}=\dfrac{0.64}{0.06283185\ldots}\approx 10.1859$, "
    r"so $AR=10.186$ to three decimals."
)

NEW_STEP_BY_STEP_FIX: List[str] = [
    (
        r"Data: $C_{D,0}=0.020$, $e=1.0$, steady level flight at minimum thrust with $C_L=0.8$."
    ),
    (
        r"Parabolic polar: $C_D=C_{D,0}+KC_L^2$, $K=\dfrac{1}{\pi e AR}$, "
        r"$C_{D,i}=\dfrac{C_L^2}{\pi e AR}$."
    ),
    (
        r"Jet aircraft, steady level: minimum thrust required occurs at $(L/D)_{\max}$, i.e.\ "
        r"$C_{D,0}=C_{D,i}$."
    ),
    (r"Thus $C_{D,0}=\dfrac{C_L^2}{\pi e AR}$ $\Rightarrow$ $AR=\dfrac{C_L^2}{\pi e C_{D,0}}$."),
    (r"Substitute $C_L=0.8$, $e=1$, $C_{D,0}=0.02$: $AR=\dfrac{0.64}{\pi(0.02)}$."),
    (r"Evaluate: $AR\approx 10.1859$; three decimal places: $10.186$."),
]

NEW_FORMULAS_USED: List[str] = [
    r"$C_D=C_{D,0}+KC_L^2$ (parabolic polar)",
    r"$K=\dfrac{1}{\pi e AR}$",
    r"$C_{D,0}=C_{D,i}$ at $(L/D)_{\max}$ (min thrust, level jet cruise)",
    r"$AR=\dfrac{C_L^2}{\pi e C_{D,0}}$",
]

NEW_HINTS: List[str] = [
    (
        r"Minimum thrust (level, jet) lines up with maximum $L/D$ on the drag polar."
    ),
    (
        r"At $(L/D)_{\max}$, zero-lift drag equals induced drag: $C_{D,0}=C_{D,i}=KC_L^2$."
    ),
    (
        r"Eliminate $K$: $AR=\dfrac{C_L^2}{\pi e C_{D,0}}$—do not drop $\pi$."
    ),
]

NEW_SOLUTION_PATH = (
    r"$(L/D)_{\max}$ $\Rightarrow$ $C_{D,0}=C_{D,i}$ $\Rightarrow$ "
    r"$AR=\dfrac{C_L^2}{\pi e C_{D,0}}$ $\Rightarrow$ numeric"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"$(L/D)_{\max}$ for $C_D=C_{D,0}+KC_L^2$ implies $C_{D,0}=KC_L^2$ (parasite = induced)."
    ),
    (
        r"$e=1$ is idealized (elliptic loading); only $C_{D,0}$, $e$, and $C_L$ enter $AR$ here."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Recall $C_{D,0}=C_{D,i}$ at min thrust / max $L/D$ for this polar.",
    r"Use $K=\dfrac{1}{\pi e AR}$ with the factor $\pi$.",
    r"Square $C_L$ in $C_{D,0}=KC_L^2$.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$C_{D,0}=KC_L^2$",
        "name": r"Parasite equals induced at $(L/D)_{\max}$",
        "conditions": [
            r"Steady level flight; parabolic polar; thrust minimized (jet).",
        ],
        "type": "equation",
        "relevance": r"Directly links $C_{D,0}$, $C_L$, and $K$.",
    },
    {
        "formula": r"$K=\dfrac{1}{\pi e AR}$",
        "name": r"Induced-drag factor",
        "conditions": [
            r"Incompressible lifting-line form; $e$ is Oswald efficiency.",
        ],
        "type": "equation",
        "relevance": r"Relates $K$ to aspect ratio.",
    },
    {
        "formula": r"$AR=\dfrac{C_L^2}{\pi e C_{D,0}}$",
        "name": r"Aspect ratio from min-thrust point",
        "conditions": [
            r"Follows from $C_{D,0}=C_{D,i}$ and $C_{D,i}=C_L^2/(\pi e AR)$.",
        ],
        "type": "equation",
        "relevance": r"Computes $AR$ from given $C_L$, $e$, $C_{D,0}$.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            r"Using $C_{D,0}=KC_L$ without squaring $C_L$, or $K=C_{D,0}/C_L$."
        ),
        "why_students_make_it": r"Algebra slip on $C_{D,i}=KC_L^2$.",
        "type": "Calculation",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Write $C_{D,0}=KC_L^2$ then $K=C_{D,0}/C_L^2$.",
        "consequence": r"Wrong $K$ and wrong $AR$.",
    },
    {
        "mistake": r"Omitting $\pi$ in $K=\dfrac{1}{\pi e AR}$.",
        "why_students_make_it": r"Memorization gap.",
        "type": "Formula",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Track dimensions: induced coefficient scales as $C_L^2/(\pi AR)$ in standard form.",
        "consequence": r"$AR$ off by factor $\sim\pi$.",
    },
    {
        "mistake": r"Confusing min thrust (jet) with min power (propeller) condition.",
        "why_students_make_it": r"Mixing performance optima.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Problem states thrust—use max $L/D$ / $C_{D,0}=C_{D,i}$ for this setup.",
        "consequence": r"Wrong governing equation.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": r"Fast NAT: one condition + one formula.",
    "triage_tip": (
        r"Level min thrust $\Rightarrow$ $C_{D,0}=C_{D,i}$ $\Rightarrow$ "
        r"$AR=\dfrac{C_L^2}{\pi e C_{D,0}}$."
    ),
    "guessing_heuristic": (
        r"Typical GA/small aircraft $AR$ is often single digits to low teens; $\approx 10.2$ matches "
        r"the $\pi C_{D,0}$ denominator scale."
    ),
    "time_management": r"About 2 minutes: 30 s setup, 60 s compute, 30 s round.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"At $(L/D)_{\max}$ with $C_D=C_{D,0}+KC_L^2$, relate $C_{D,0}$ and $C_{D,i}$.",
        "back": r"$C_{D,0}=C_{D,i}=KC_L^2$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "formula_recall",
        "front": r"$K$ vs.\ $AR$ and $e$?",
        "back": r"$K=\dfrac{1}{\pi e AR}$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "concept_recall",
        "front": r"Steady level flight: what minimizes thrust required for a jet?",
        "back": r"Flying at $(L/D)_{\max}$ (here $C_{D,0}=C_{D,i}$ on the polar).",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "application",
        "front": r"$C_{D,0}=0.02$, $e=1$, $C_L=0.8$ at min thrust—find $AR$.",
        "back": r"$AR=\dfrac{0.64}{\pi(0.02)}\approx 10.186$.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Max $L/D$: parasite meets induced ($C_{D,0}=C_{D,i}$).",
        "concept": r"Drag polar symmetry point for min thrust (jet, level).",
        "effectiveness": "high",
        "context": r"Aircraft performance MCQs.",
    },
    {
        "mnemonic": r"$K$-formula: $1/(\pi e AR)$—never forget $\pi$.",
        "concept": r"Induced drag factor.",
        "effectiveness": "high",
        "context": r"Polar / span efficiency problems.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "GATE 2017 AE aspect ratio minimum thrust",
    "max L/D C_D0 equals induced",
    "K equals 1 over pi e AR",
    "Oswald efficiency drag polar",
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": r"Maximize $L/D$ explicitly",
        "description": (
            r"Maximize $C_L/(C_{D,0}+KC_L^2)$ w.r.t.\ $C_L$; at optimum $C_{D,0}=KC_L^2$, same result."
        ),
        "pros_cons": r"Longer; confirms the shortcut.",
        "when_to_use": r"When deriving the condition from scratch.",
    },
]

NEW_CONNECTIONS: Dict[str, str] = {
    "Aerodynamics": (
        r"Induced drag and $e$ come from 3-D wing theory; polar ties parasite and induced terms."
    ),
    "Flight mechanics": (
        r"Thrust required $T=D$ in level flight; min $T$ aligns with min drag at fixed weight for this model."
    ),
    "Mathematics": (
        r"Maximizing a ratio $f/g$ on an interval (smooth polar)."
    ),
}

NEW_DEEPER_DIVE: List[str] = [
    r"Compressibility and Mach effects modify $C_{D,0}$ and $e$ at higher speed.",
    r"Non-elliptic loading lowers effective $e$ below 1 in practice.",
    r"Structural/aeroelastic limits cap achievable $AR$.",
]


def _merge_unique(a: List[str], b: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for x in a + b:
        k = x.strip()
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING
    av["correct_answer"] = "10.186"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP_FIX
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP_FIX)

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = [
        r"Parabolic drag polar: $C_D=C_{D,0}+KC_L^2$, $K=\dfrac{1}{\pi e AR}$.",
        r"Induced term: $C_{D,i}=\dfrac{C_L^2}{\pi e AR}$.",
        r"Steady level flight: $L=W$, $T=D$.",
        r"Minimum thrust (jet) at $(L/D)_{\max}$: $C_{D,0}=C_{D,i}$.",
    ]
    prereq["helpful"] = _merge_unique(
        [
            r"Do not confuse min thrust with min power (propeller) optima.",
        ],
        list(prereq.get("helpful") or []),
    )

    return t1


def patch_tier_2(tier_2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t2 = deepcopy(tier_2 or {})
    t2["common_mistakes"] = NEW_COMMON_MISTAKES
    t2["exam_strategy"] = NEW_EXAM_STRATEGY
    t2["flashcards"] = NEW_FLASHCARDS
    t2["mnemonics_memory_aids"] = NEW_MNEMONICS
    return t2


def patch_tier_3(tier_3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t3 = deepcopy(tier_3 or {})
    old_kw = list(t3.get("search_keywords") or [])
    t3["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, old_kw)

    old_alt = list(t3.get("alternative_methods") or [])
    names = {x.get("name") for x in NEW_ALTERNATIVE_METHODS if isinstance(x, dict)}
    kept = [x for x in old_alt if isinstance(x, dict) and x.get("name") not in names]
    t3["alternative_methods"] = NEW_ALTERNATIVE_METHODS + kept

    conn = dict(t3.get("connections_to_other_subjects") or {})
    conn.update(NEW_CONNECTIONS)
    t3["connections_to_other_subjects"] = conn

    dd = list(t3.get("deeper_dive_topics") or [])
    t3["deeper_dive_topics"] = _merge_unique(NEW_DEEPER_DIVE, dd)

    for am in t3.get("alternative_methods") or []:
        if not isinstance(am, dict):
            continue
        if am.get("name") == "Using the full drag polar equation":
            am["description"] = (
                r"Maximize $L/D=C_L/C_D$ with $C_D=C_{D,0}+KC_L^2$; setting $\mathrm{d}(L/D)/\mathrm{d}C_L=0$ "
                r"yields $C_{D,0}=KC_L^2$, equivalent to the shortcut."
            )
            am["pros_cons"] = r"More rigorous derivation; same numerical condition."

    return t3


async def main() -> None:
    opts_json = json.dumps(NEW_OPTIONS)

    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning, tier_3_enhanced_learning "
                "FROM questions WHERE question_id = :qid"
            ),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        new_t1 = patch_tier_1(row[0])
        new_t2 = patch_tier_2(row[1])
        new_t3 = patch_tier_3(row[2])

        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "options = CAST(:opts AS jsonb), "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "tier_2_student_learning = CAST(:t2 AS jsonb), "
                "tier_3_enhanced_learning = CAST(:t3 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT_PLAIN,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": opts_json,
                "t1": json.dumps(new_t1),
                "t2": json.dumps(new_t2),
                "t3": json.dumps(new_t3),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: stem/options/tier-1/2/3 LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

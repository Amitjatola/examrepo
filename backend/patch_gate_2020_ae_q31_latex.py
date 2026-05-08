"""
Fix GATE_2020_AE_Q31: directional static stability from tabulated C_n vs beta.

Correct table-driven slopes (0 to 5 deg): A 0.030/5, B 0.025/5, C -0.040/5.

Usage (from backend/):
  ./venv/bin/python patch_gate_2020_ae_q31_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2020_AE_Q31"

NEW_QUESTION_TEXT_PLAIN = (
    "For three different airplanes A, B and C, the yawing moment coefficient "
    "was measured in a wind tunnel for three sideslip angles β and tabulated below. "
    "Which statement is true regarding directional static stability of A, B and C?"
)

NEW_QUESTION_TEXT_LATEX = (
    r"For three different airplanes A, B and C, the yawing moment coefficient $C_n$ "
    r"was measured in a wind tunnel for three sideslip angles $\beta$ and tabulated below."
    "\n\n"
    r"$$\begin{array}{|c|c|c|c|}"
    r"\hline"
    r"\beta & \text{Airplane A} & \text{Airplane B} & \text{Airplane C} \\"
    r"\hline"
    r"-5^\circ & -0.030 & -0.025 & 0.040 \\"
    r"\hline"
    r"0^\circ & 0 & 0 & 0 \\"
    r"\hline"
    r"5^\circ & 0.030 & 0.025 & -0.040 \\"
    r"\hline"
    r"\end{array}$$"
    "\n\n"
    r"Which one of the following statements is true regarding directional static stability "
    r"of the airplanes A, B and C?"
)

NEW_OPTIONS = {
    "A": "All three airplanes A, B, and C are stable.",
    "B": "Only airplane C is stable, while both A and B are unstable.",
    "C": "Airplane C is unstable, A and B are stable with A being more stable than B.",
    "D": "Airplane C is unstable, A and B are both stable with A less stable than B.",
}

NEW_REASONING = (
    r"Directional static stability requires a restoring yawing moment for a sideslip disturbance. "
    r"In the usual stability-axes sign convention used with tabulated $C_n(\beta)$, "
    r"directional static stability corresponds to a positive slope "
    r"$C_{n_\beta}=\partial C_n/\partial\beta$ (equivalently positive $\Delta C_n/\Delta\beta$ "
    r"when $C_n$ is nearly linear in $\beta$ near $0^\circ$)."
    "\n\n"
    r"Using the segment from $\beta=0^\circ$ to $\beta=5^\circ$:"
    "\n"
    r"(A) $\Delta C_n=0.030-0=0.030$, $\Delta\beta=5^\circ$, so "
    r"$C_{n_\beta}\approx 0.030/5^\circ=0.006$ per degree $>0$ (stable)."
    "\n"
    r"(B) $\Delta C_n=0.025$, giving $C_{n_\beta}\approx 0.005$ per degree $>0$ (stable)."
    "\n"
    r"(C) $\Delta C_n=-0.040$, giving $C_{n_\beta}\approx -0.008$ per degree $<0$ (unstable)."
    "\n\n"
    r"Among stable cases, a larger positive $C_{n_\beta}$ implies stronger weathercock stability, "
    r"so A is more stable than B. Therefore option C is correct."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Directional static stability is indicated by the sign of $C_{n_\beta}=\partial C_n/\partial\beta$. "
        r"For the usual wind-tunnel-style $C_n$ versus $\beta$ plot near $\beta=0$, "
        r"a positive slope ($C_{n_\beta}>0$) means stable; negative means unstable."
    ),
    (
        r"Approximate $C_{n_\beta}$ from the table using "
        r"$C_{n_\beta}\approx \Delta C_n/\Delta\beta$ between $\beta=0^\circ$ and $\beta=5^\circ$."
    ),
    (
        r"Airplane A: $\Delta C_n=0.030$, $\Delta\beta=5^\circ$, so "
        r"$C_{n_\beta}\approx 0.030/5^\circ=0.006$ per degree $>0$ (stable)."
    ),
    (
        r"Airplane B: $\Delta C_n=0.025$, so $C_{n_\beta}\approx 0.005$ per degree $>0$ (stable)."
    ),
    (
        r"Airplane C: $\Delta C_n=-0.040$, so $C_{n_\beta}\approx -0.008$ per degree $<0$ (unstable)."
    ),
    (
        r"Compare stable slopes: $0.006>0.005$, so A is more directionally stable than B."
    ),
    (
        r"Match to options: C is unstable; A and B are stable with A more stable than B $\Rightarrow$ option C."
    ),
]

NEW_FORMULAS_USED: List[str] = [
    r"$C_{n_\beta}=\dfrac{\partial C_n}{\partial \beta}$",
    r"$C_{n_\beta}\approx \dfrac{\Delta C_n}{\Delta \beta}$",
    r"$C_n=\dfrac{N}{\tfrac{1}{2}\rho V^2 S\,b}$",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "name": r"Yaw stiffness derivative",
        "type": "equation",
        "formula": r"$C_{n_\beta}=\dfrac{\partial C_n}{\partial \beta}$",
        "relevance": r"Relates tabulated $C_n(\beta)$ slopes to directional static stability.",
        "conditions": [r"Small $\beta$ so local slope estimates are meaningful."],
    },
    {
        "name": r"Directional static stability (weathercock) criterion",
        "type": "principle",
        "formula": r"$C_{n_\beta}>0$",
        "relevance": r"Positive stiffness restores heading after a sideslip disturbance.",
        "conditions": [r"Consistent sign conventions for $C_n$ and $\beta$ as in the table."],
    },
    {
        "name": r"Yawing moment coefficient definition",
        "type": "equation",
        "formula": r"$C_n=\dfrac{N}{\tfrac{1}{2}\rho V^2 S\,b}$",
        "relevance": r"Background definition linking dimensional yaw moment to $C_n$.",
        "conditions": [r"Uses wing span $b$ as reference length for yawing moment."],
    },
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": "Graphical interpretation",
        "description": (
            r"Plot $C_n$ versus $\beta$ for each airplane. Near $\beta=0$, the slope is $C_{n_\beta}$: "
            r"positive slope implies stability; negative implies instability. Steeper positive slope "
            r"means stronger directional stiffness."
        ),
        "pros_cons": (
            "Pros: Visual slope check. Cons: slower than a single finite-difference ratio on exam day."
        ),
        "when_to_use": r"When verifying linearity or scanning multiple $\beta$ points.",
    },
    {
        "name": "Linear regression",
        "description": (
            r"Fit a line $C_n=c_0+c_1\beta$ through multiple points; take $c_1$ as $C_{n_\beta}$."
        ),
        "pros_cons": "Pros: uses all points. Cons: slower without tooling.",
        "when_to_use": r"Noisy or multi-point datasets.",
    },
]

NEW_HINTS: List[str] = [
    r"Stability is about the slope of $C_n$ versus $\beta$, not a single $C_n$ value.",
    r"Check the sign of $\Delta C_n/\Delta\beta$ near $\beta=0$; $C_{n_\beta}>0$ is stable here.",
    r"If two airplanes are stable, the larger positive $C_{n_\beta}$ is the more stable one.",
]

NEW_SOLUTION_PATH = (
    r"$C_{n_\beta}$ sign from $\Delta C_n/\Delta\beta$ $\Rightarrow$ classify A,B,C $\Rightarrow$ compare magnitudes"
)

NEW_KEY_INSIGHTS: List[str] = [
    r"The table is antisymmetric about $\beta=0$ for each airplane, so the $0^\circ\to 5^\circ$ slope suffices.",
    r"Do not apply the longitudinal rule $C_{m_\alpha}<0$ to directional stability; use $C_{n_\beta}>0$ here.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Requires the correct directional criterion $C_{n_\beta}>0$ (not the longitudinal pitch rule).",
    r"Must estimate a derivative from tabulated points (slope), not a single coefficient entry.",
    r"Must compare relative stability using magnitudes of positive $C_{n_\beta}$ for A vs B.",
]

NEW_STEP_BY_STEP_META = {
    "approach_type": "Direct Formula Application and Data Analysis",
    "total_steps": 7,
    "solution_path": NEW_SOLUTION_PATH,
    "key_insights": NEW_KEY_INSIGHTS,
}

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Must attempt",
    "triage_tip": (
        r"Read stability as the slope of $C_n$ versus $\beta$ near $0^\circ$: compute "
        r"$\Delta C_n/\Delta\beta$ from $0^\circ\to 5^\circ$, check sign, then compare magnitudes."
    ),
    "guessing_heuristic": (
        r"If two airplanes look stable (positive slope) and one is unstable (negative slope), "
        r"eliminate all‑stable / only‑C‑stable patterns first."
    ),
    "time_management": r"About 1–2 minutes: three slopes and one comparison.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "definition",
        "front": r"Directional static stability condition on $C_{n_\beta}$",
        "back": (
            r"$C_{n_\beta}=\partial C_n/\partial\beta>0$: a positive sideslip produces a yawing moment "
            r"that tends to reduce sideslip (weathercock stability)."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 35,
    },
    {
        "card_type": "formula_recall",
        "front": r"Finite-difference estimate of $C_{n_\beta}$ from data",
        "back": r"$C_{n_\beta}\approx \Delta C_n/\Delta\beta$ using two nearby $\beta$ points.",
        "difficulty": "medium",
        "time_limit_seconds": 40,
    },
    {
        "card_type": "application",
        "front": r"If $C_{n_\beta}=-0.005\ \mathrm{per\ deg}$, stable or unstable?",
        "back": r"Unstable: negative slope means sideslip grows rather than being damped directionally.",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Contrast $C_{m_\alpha}$ vs $C_{n_\beta}$ stability signs",
        "back": (
            r"Longitudinal: typically $C_{m_\alpha}<0$. Directional: $C_{n_\beta}>0$ for weathercock stability."
        ),
        "difficulty": "hard",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "comparison",
        "front": r"Why can $|C_n|$ at one $\beta$ mislead stability ranking?",
        "back": r"Stability depends on the slope $C_{n_\beta}$, not the magnitude of $C_n$ at a single $\beta$.",
        "difficulty": "hard",
        "time_limit_seconds": 50,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Directional: Beta up, slope up $\Rightarrow$ $C_{n_\beta}>0$ stable.",
        "concept": r"Sign of $C_{n_\beta}$",
        "effectiveness": "high",
        "context": r"Directional vs longitudinal criteria",
    },
    {
        "mnemonic": r"Longitudinal: Alpha up, moment down $\Rightarrow$ $C_{m_\alpha}<0$ stable.",
        "concept": r"Do not mix pitch and yaw rules",
        "effectiveness": "medium",
        "context": r"Cross-axis confusion",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            r"Treating directional stability like longitudinal stability "
            r"($C_{m_\alpha}<0$) and expecting $C_{n_\beta}<0$."
        ),
        "why_students_make_it": r"Over-generalizing the pitch stability sign convention to yaw.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            r"Memorize separately: $C_{m_\alpha}<0$ (pitch) vs $C_{n_\beta}>0$ (yaw) under standard conventions."
        ),
        "consequence": r"Reverses stable/unstable classification for yaw.",
    },
    {
        "mistake": (
            r"Arithmetic slip when forming $\Delta C_n$ or dividing by $\Delta\beta$, "
            r"or ranking stability without comparing positive slopes."
        ),
        "why_students_make_it": r"Haste or unclear definition of “more stable”.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Compute $\Delta C_n/\Delta\beta$ explicitly for each airplane before comparing.",
        "consequence": r"Wrong slope magnitude ordering between A and B.",
    },
    {
        "mistake": r"Ignoring magnitude of $C_{n_\beta}$ among stable airplanes.",
        "why_students_make_it": r"Checking only the sign of stability.",
        "type": "Conceptual",
        "severity": "Low",
        "frequency": "occasional",
        "how_to_avoid": r"Among $C_{n_\beta}>0$, larger positive means stronger directional stiffness.",
        "consequence": r"Picking D instead of C.",
    },
    {
        "mistake": (
            r"Judging stability from $|C_n|$ at a single $\beta$ instead of the slope versus $\beta$."
        ),
        "why_students_make_it": r"Misreading the table as static values rather than a local derivative.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Always estimate $C_{n_\beta}$ from differences (or plot mentally).",
        "consequence": r"Incorrect ranking or false instability.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "GATE 2020 AE directional static stability",
    "Cn beta derivative sideslip",
    "weathercock stability wind tunnel table",
    "yawing moment coefficient beta slope",
]

NEW_CONNECTIONS: Dict[str, str] = {
    "Flight mechanics": (
        r"$C_{n_\beta}$ sets initial directional stiffness; ties to Dutch roll/spiral context at higher level."
    ),
    "Aerodynamics": (
        r"Vertical tail sideforce creates yawing moments that produce positive $C_{n_\beta}$ for many configs."
    ),
}

NEW_DEEPER_DIVE: List[str] = [
    r"Dutch roll and spiral mode coupling (lateral-directional dynamics).",
    r"Rudder effectiveness $C_{n_{\delta_r}}$ and trim changes.",
    r"Fuselage sidewash and wing sweep effects on $C_{n_\beta}$.",
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
    av["correct_answer"] = "C"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs.update(NEW_STEP_BY_STEP_META)

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

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
    cleaned_old = [
        k
        for k in old_kw
        if k
        and "$C_{N\\_\\beta}" not in k
        and not (k.startswith("$") and "stability criterion" in k)
    ]
    t3["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, cleaned_old)

    conn = dict(t3.get("connections_to_other_subjects") or {})
    conn.update(NEW_CONNECTIONS)
    t3["connections_to_other_subjects"] = conn

    dd = list(t3.get("deeper_dive_topics") or [])
    merged_dd = _merge_unique(NEW_DEEPER_DIVE, dd)
    t3["deeper_dive_topics"] = [x for x in merged_dd if x and "($C_{N_" not in x]

    t3["alternative_methods"] = NEW_ALTERNATIVE_METHODS

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

    print(f"Patched {PUBLIC_ID}: stem/options/tiers LaTeX + numeric reasoning")


if __name__ == "__main__":
    asyncio.run(main())

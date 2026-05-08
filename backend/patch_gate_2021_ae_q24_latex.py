"""
Fix GATE_2021_AE_Q24: engine-out rudder trim LaTeX + notation (C_{n_{delta_r}}, units).

Usage (from backend/):
  ./venv/bin/python patch_gate_2021_ae_q24_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2021_AE_Q24"

NEW_QUESTION_TEXT_PLAIN = (
    "An aircraft with twin jet engines has the following specifications:\n"
    "Thrust produced (per engine) = 8000 N\n"
    "Spanwise distance between the two engines = 10 m\n"
    "Wing area = 50 m², wing span = 10 m\n"
    "Rudder effectiveness ∂C_n/∂δ_r = −0.002 per degree\n"
    "Density of air at sea level = 1.225 kg/m³\n"
    "The rudder deflection, in degrees, required to maintain zero sideslip at 100 m/s in "
    "steady and level flight at sea level with a non-functional right engine is ________ "
    "(round off to two decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    r"$$\begin{array}{l}"
    r"\text{An aircraft with twin jet engines has the following specifications:}\\[0.6em]"
    r"\text{Thrust produced (per engine)} = 8000~\mathrm{N}\\[0.35em]"
    r"\text{Spanwise distance between the two engines} = 10~\mathrm{m}\\[0.35em]"
    r"\text{Wing area} = 50~\mathrm{m}^2,\quad \text{wing span} = 10~\mathrm{m}\\[0.35em]"
    r"\text{Rudder effectiveness } C_{n_{\delta_r}} = -0.002~\mathrm{deg}^{-1}\\[0.35em]"
    r"\text{Density of air at sea level} = 1.225~\mathrm{kg}/\mathrm{m}^3\\[0.6em]"
    r"\text{The rudder deflection (degrees) required to maintain zero sideslip at } "
    r"100~\mathrm{m}/\mathrm{s}\text{ in steady level flight at sea level with a "
    r"non-functional right engine is }\underline{\hspace{5em}}\\[0.35em]"
    r"\text{(round off to two decimal places).}"
    r"\end{array}$$"
)

NEW_REASONING = (
    r"The yaw from asymmetric thrust must be canceled by rudder yaw so that net yawing moment "
    r"about the CG is zero for $\beta=0$."
    "\n\n"
    r"(1) Asymmetric thrust yaw. With the right engine inoperative, the left engine "
    r"thrust $T=8000~\mathrm{N}$ acts at lateral offset "
    r"$y_{\mathrm{engine}}=\dfrac{10~\mathrm{m}}{2}=5~\mathrm{m}$ from the aircraft centerline:"
    "\n"
    r"$N_{\mathrm{thrust}} = T\, y_{\mathrm{engine}} = 8000\times 5 = 40000~\mathrm{N\,m}$ "
    r"(tends to yaw the nose to the right for the usual symmetric twin layout)."
    "\n\n"
    r"(2) Dynamic pressure. "
    r"$q=\tfrac{1}{2}\rho V^2=\tfrac{1}{2}(1.225)(100)^2=6125~\mathrm{N/m^2}$."
    "\n\n"
    r"(3) Rudder yaw (linear model). "
    r"$N_{\mathrm{rudder}} = C_{n_{\delta_r}}\,\delta_r\, q\, S\, b$, so equilibrium "
    r"$N_{\mathrm{thrust}}+N_{\mathrm{rudder}}=0$ gives"
    "\n"
    r"$T\, y_{\mathrm{engine}} + C_{n_{\delta_r}}\,\delta_r\, q\, S\, b = 0$."
    "\n\n"
    r"(4) Solve for $\delta_r$. Using $qSb=6125\times 50\times 10=3.0625\times 10^6~\mathrm{N\,m}$ "
    r"and $C_{n_{\delta_r}}=-0.002~\mathrm{deg}^{-1}$:"
    "\n"
    r"$\delta_r = -\dfrac{T\, y_{\mathrm{engine}}}{C_{n_{\delta_r}}\, q\, S\, b}"
    r" = -\dfrac{40000}{(-0.002)(3.0625\times 10^6)}"
    r" \approx 6.5306~\mathrm{deg}$."
    "\n\n"
    r"(5) Rounding. Two decimals: $\delta_r \approx 6.53~\mathrm{deg}$, within the "
    r"acceptable GATE numeric band $6.50$–$6.60$."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Principle: for $\beta=0$, yaw moment balance $N_{\mathrm{thrust}}+N_{\mathrm{rudder}}=0$; "
        r"identify $T$, $\rho$, $V$, $S$, $b$, engine spacing, and $C_{n_{\delta_r}}$ with consistent "
        r"angular units."
    ),
    (
        r"Compute thrust yaw: one engine at $y_{\mathrm{engine}}=\tfrac{10}{2}=5~\mathrm{m}$, "
        r"$N_{\mathrm{thrust}}=T\, y_{\mathrm{engine}}=8000\times 5=40000~\mathrm{N\,m}$."
    ),
    (
        r"Dynamic pressure $q=\tfrac{1}{2}\rho V^2=\tfrac{1}{2}(1.225)(100)^2=6125~\mathrm{Pa}$."
    ),
    (
        r"Rudder moment model: $N_{\mathrm{rudder}}=C_{n_{\delta_r}}\,\delta_r\, q\, S\, b$. "
        r"Form $qSb=6125\times 50\times 10=3.0625\times 10^6~\mathrm{N\,m}$."
    ),
    (
        r"Substitute: $40000 + (-0.002~\mathrm{deg}^{-1})\,\delta_r\,(3.0625\times 10^6)=0$, "
        r"equivalently $6125\,\delta_r=40000$ when $C_{n_{\delta_r}}\, qSb=-6125~\mathrm{N\,m/deg}$."
    ),
    (
        r"Solve: $\delta_r=40000/6125\approx 6.530612~\mathrm{deg}$."
    ),
    (
        r"Round to two decimals: $6.53~\mathrm{deg}$ (within $6.50$–$6.60$)."
    ),
]

NEW_FORMULAS_USED: List[str] = [
    r"$N_{\mathrm{thrust}} = T\, y_{\mathrm{engine}}$",
    r"$q=\tfrac{1}{2}\rho V^2$",
    r"$N_{\mathrm{rudder}} = C_{n_{\delta_r}}\,\delta_r\, q\, S\, b$",
    r"$N_{\mathrm{thrust}} + N_{\mathrm{rudder}} = 0$",
    r"$\delta_r = -\dfrac{T\, y_{\mathrm{engine}}}{C_{n_{\delta_r}}\, q\, S\, b}$",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "name": r"Yawing moment from asymmetric thrust",
        "type": "equation",
        "formula": r"$N_{\mathrm{thrust}} = T\, y_{\mathrm{engine}}$",
        "relevance": r"Disturbing yaw when only one engine produces thrust at lateral offset "
        r"$y_{\mathrm{engine}}$.",
        "conditions": [
            r"Symmetric twin layout: offset from centerline is half the engine-to-engine spacing.",
        ],
    },
    {
        "name": r"Yawing moment from rudder (linear)",
        "type": "equation",
        "formula": r"$N_{\mathrm{rudder}} = C_{n_{\delta_r}}\,\delta_r\, q\, S\, b$",
        "relevance": r"Relates rudder deflection to dimensional yawing moment via $C_{n_{\delta_r}}$.",
        "conditions": [
            r"Small $\delta_r$ in the linear regime; $C_{n_{\delta_r}}$ and $\delta_r$ use "
            r"matching angular units (here per degree).",
        ],
    },
    {
        "name": r"Yaw moment equilibrium (zero sideslip)",
        "type": "principle",
        "formula": r"$N_{\mathrm{thrust}} + N_{\mathrm{rudder}} = 0$",
        "relevance": r"Trim condition used to solve for required $\delta_r$.",
        "conditions": [r"Steady straight flight with $\beta=0$."],
    },
    {
        "name": r"Rudder deflection for trim",
        "type": "equation",
        "formula": (
            r"$\delta_r = -\dfrac{T\, y_{\mathrm{engine}}}{C_{n_{\delta_r}}\, q\, S\, b}$"
        ),
        "relevance": r"Direct rearrangement after substituting the linear rudder model.",
        "conditions": [
            r"$q=\tfrac{1}{2}\rho V^2$ evaluated at the flight condition.",
        ],
    },
]

NEW_HINTS: List[str] = [
    (
        r"For symmetric twins, moment arm from centerline to the operating engine is half the "
        r"engine-to-engine distance."
    ),
    (
        r"Keep $C_{n_{\delta_r}}$ and $\delta_r$ in consistent angular units (here per degree)."
    ),
    (
        r"Balance moments: $T\, y_{\mathrm{engine}} + C_{n_{\delta_r}}\,\delta_r\, q\, S\, b = 0$."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Single-step equilibrium once $N_{\mathrm{thrust}}$ and $qSb$ are formed.",
    r"Watch units: $C_{n_{\delta_r}}$ is per degree (avoid mixing radians without conversion).",
    r"Sign of $C_{n_{\delta_r}}$ must be carried through—two negatives yield positive $\delta_r$.",
]

NEW_STEP_BY_STEP_META: Dict[str, Any] = {
    "approach_type": "Direct formula application (moment equilibrium)",
    "total_steps": 7,
    "solution_path": (
        r"$N_{\mathrm{thrust}}$ from geometry $\Rightarrow$ $q$ and $qSb$ $\Rightarrow$ "
        r"linear rudder model $\Rightarrow$ solve $\delta_r$"
    ),
    "key_insights": [
        (
            r"Engine-out yaw is trimmed by rudder authority; static balance uses "
            r"$N_{\mathrm{thrust}}+C_{n_{\delta_r}}\delta_r qSb=0$."
        ),
        (
            r"$y_{\mathrm{engine}}$ is half of the $10~\mathrm{m}$ spanwise separation for a "
            r"symmetric installation."
        ),
        (
            r"A negative $C_{n_{\delta_r}}$ (per deg) with positive $\delta_r$ contributes negative "
            r"$N_{\mathrm{rudder}}$ in this model—check signs against your convention sketch."
        ),
    ],
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"Yaw moment equilibrium for engine-out, $\beta=0$?",
        "back": (
            r"$N_{\mathrm{thrust}} + N_{\mathrm{rudder}} = 0$ with "
            r"$N_{\mathrm{rudder}} = C_{n_{\delta_r}}\,\delta_r\, q\, S\, b$."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "concept_recall",
        "front": r"What does $C_{n_{\delta_r}} < 0$ imply about rudder effectiveness?",
        "back": (
            r"In the usual linear model, positive right-rudder $\delta_r$ produces negative yawing "
            r"moment contribution $C_{n_{\delta_r}}\delta_r qSb$ when $C_{n_{\delta_r}}<0$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Common unit pitfall for $C_{n_{\delta_r}} = -0.002~\mathrm{deg}^{-1}$?",
        "back": (
            r"Do not treat it as per-radian without multiplying $\delta_r$ by "
            r"$\pi/180$ (or converting $C_{n_{\delta_r}}$ to per-radian)."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"Why does lower $V$ increase required rudder for the same thrust yaw?",
        "back": (
            r"Lower $V$ lowers $q$, so the same $\delta_r$ generates less $|N_{\mathrm{rudder}}|$; "
            r"more $\delta_r$ is needed—ties to $V_{MC}$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": r"Explicit $\delta_r$ for trim against $T\, y_{\mathrm{engine}}$?",
        "back": (
            r"$\delta_r = -\dfrac{T\, y_{\mathrm{engine}}}{C_{n_{\delta_r}}\, q\, S\, b}$ "
            r"(match angular units with $C_{n_{\delta_r}}$)."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 60,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"HALF-SPAN: offset from centerline to engine is half the engine spacing.",
        "concept": r"Thrust yaw moment arm $y_{\mathrm{engine}}$",
        "effectiveness": "high",
        "context": r"Symmetric twin geometry",
    },
    {
        "mnemonic": r"DEG MATCH: if $C_{n_{\delta_r}}$ is per degree, keep $\delta_r$ in degrees.",
        "concept": r"Unit consistency for control derivatives",
        "effectiveness": "high",
        "context": r"Exam numerical traps",
    },
    {
        "mnemonic": r"QBARN: yaw moment from coefficient $\propto q\,S\,b$ (not just $qS$).",
        "concept": r"Dimensional yawing moment scaling",
        "effectiveness": "medium",
        "context": r"Relating $C_n$ to $N$",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": r"Using the full $10~\mathrm{m}$ engine spacing as $y_{\mathrm{engine}}$.",
        "why_students_make_it": r"Misreading lateral offset versus separation distance.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Sketch the top view: each thrust line is $\tfrac{1}{2}$ the separation "
        r"from the centerline.",
        "consequence": r"Roughly doubles $\delta_r$ (e.g., $\approx 13.06^\circ$).",
    },
    {
        "mistake": r"Treating $C_{n_{\delta_r}}$ as per-radian while using $\delta_r$ in degrees.",
        "why_students_make_it": r"Defaulting to radian-based aerodynamics without checking the prompt.",
        "type": "Units",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"If you prefer radians, convert consistently: "
        r"$C_{n_{\delta_r}}(\mathrm{rad}^{-1}) \approx C_{n_{\delta_r}}(\mathrm{deg}^{-1})\times "
        r"\tfrac{180}{\pi}$.",
        "consequence": r"Deflection off by $\sim 57\times$ if mishandled.",
    },
    {
        "mistake": r"Dropping the $\tfrac{1}{2}$ in $q=\tfrac{1}{2}\rho V^2$.",
        "why_students_make_it": r"Haste or confusing dynamic pressure with $\rho V^2$.",
        "type": "Calculation",
        "severity": "Medium",
        "frequency": "common",
        "how_to_avoid": r"Write $q=\tfrac{1}{2}\rho V^2$ explicitly before multiplying $S,b$.",
        "consequence": r"Wrong $qSb$ scales $\delta_r$ by $\sim 2\times$.",
    },
    {
        "mistake": r"Sign slip in $N_{\mathrm{thrust}}+N_{\mathrm{rudder}}=0$ with negative "
        r"$C_{n_{\delta_r}}$.",
        "why_students_make_it": r"Not tracking how the two negatives combine.",
        "type": "Sign Error",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Substitute numbers once: $({-0.002})\times 3.0625\times 10^6=-6125~\mathrm{N\,m}/\mathrm{deg}$.",
        "consequence": r"Confusion about direction despite often still getting the magnitude in drills.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": "Must Attempt",
    "triage_tip": (
        r"Compute $y_{\mathrm{engine}}$, then $q$ and $qSb$, then solve "
        r"$T y_{\mathrm{engine}} + C_{n_{\delta_r}}\delta_r qSb=0$ for $\delta_r$ in degrees."
    ),
    "guessing_heuristic": (
        r"If orders-of-magnitude check fails, revisit $y_{\mathrm{engine}}$ and whether "
        r"$C_{n_{\delta_r}}$ is per degree."
    ),
    "time_management": r"Target about 2–3 minutes: mostly bookkeeping on $qSb$ and unit checks.",
}

NEW_SEARCH_KEYWORDS: List[str] = [
    "GATE 2021 AE engine out rudder",
    "asymmetric thrust rudder deflection",
    "CN_delta_r per degree",
    "yawing moment equilibrium twin jet",
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": r"Coefficient-domain balance",
        "description": (
            r"Write $C_{n,\mathrm{thrust}} + C_{n,\mathrm{rudder}} = 0$ with "
            r"$C_{n,\mathrm{thrust}} = \dfrac{T\, y_{\mathrm{engine}}}{q\, S\, b}$ and "
            r"$C_{n,\mathrm{rudder}} = C_{n_{\delta_r}}\,\delta_r$. Solve for $\delta_r$."
        ),
        "pros_cons": (
            r"Pros: highlights nondimensional bookkeeping. Cons: one extra ratio versus direct "
            r"moment balance."
        ),
        "when_to_use": r"When the whole solution is being tracked in $C_n$ space.",
    },
    {
        "name": r"Prefactor grouping",
        "description": (
            r"Group $k = C_{n_{\delta_r}}\, q\, S\, b$ so $\delta_r = -N_{\mathrm{thrust}}/k$ "
            r"after computing $N_{\mathrm{thrust}}$ once."
        ),
        "pros_cons": r"Pros: fewer symbolic steps. Cons: still requires correct $k$ units.",
        "when_to_use": r"Repetitive exam drill / sanity checks.",
    },
]

NEW_CONNECTIONS: Dict[str, str] = {
    "Aerodynamics": (
        r"Relates yawing-moment coefficient $C_n$ and rudder control derivative "
        r"$C_{n_{\delta_r}}$ to dimensional moments via $q\,S\,b$."
    ),
}


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
    av["correct_answer"] = "6.53° (acceptable numeric band 6.50–6.60 per GATE key)"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs.update(NEW_STEP_BY_STEP_META)

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    hp = t1.setdefault("prerequisites", {})
    hel = list(hp.get("helpful") or [])
    fixed_helpful = [h for h in hel if h and "C\\_" not in h]
    fixed_helpful.append(
        r"Rudder control derivative $C_{n_{\delta_r}}=\partial C_n/\partial \delta_r$ "
        r"(use degree- or radian-consistent units as stated)."
    )
    hp["helpful"] = _merge_unique(fixed_helpful, [])

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

    conn = dict(t3.get("connections_to_other_subjects") or {})
    conn.update(NEW_CONNECTIONS)
    t3["connections_to_other_subjects"] = conn

    t3["alternative_methods"] = NEW_ALTERNATIVE_METHODS

    return t3


async def main() -> None:
    opts_json = json.dumps(None)

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

    print(f"Patched {PUBLIC_ID}: NAT stem + tiers LaTeX (engine-out rudder trim)")


if __name__ == "__main__":
    asyncio.run(main())

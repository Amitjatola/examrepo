"""
Fix GATE_2019_AE_Q41 LaTeX: induced-drag ratio level vs climb (NAT ~1.33).

Correct ratio: $C_{D,i,\mathrm{level}}/C_{D,i,\mathrm{climb}}=(L_{\mathrm{level}}/L_{\mathrm{climb}})^2
=\sec^2\gamma$ with $\gamma=30^\circ$.

Usage (from backend/):
  ./venv/bin/python patch_gate_2019_ae_q41_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q41"

NEW_QUESTION_TEXT_PLAIN = (
    "Consider an airplane with a weight of 8000 N, wing area of 16 m², wing zero-lift drag coefficient "
    "of 0.02, Oswald efficiency factor of 0.8, and wing aspect ratio of 6, in steady level flight with "
    "wing lift coefficient of 0.375. Considering the same flight speed and ambient density, the ratio "
    "of the induced drag coefficient during steady level flight to that during a 30° climb is ______ "
    "(round off to 2 decimal places)."
)

NEW_QUESTION_TEXT_LATEX = (
    r"Consider an airplane with weight $W=8000~\mathrm{N}$, wing area $S=16~\mathrm{m}^2$, "
    r"zero-lift drag coefficient $C_{D,0}=0.02$, Oswald efficiency $e=0.8$, and aspect ratio "
    r"$AR=6$, in steady level flight with wing lift coefficient $C_{L,\mathrm{level}}=0.375$. "
    r"With the same flight speed and ambient density, the ratio of induced drag coefficient in "
    r"steady level flight to that in a $30^\circ$ steady climb is "
    r"$\underline{\hspace{3.5em}}$ (round off to 2 decimal places)."
)

NEW_OPTIONS = None

NEW_REASONING = (
    r"For a given wing in the drag polar model, $C_{D,i}=\dfrac{C_L^2}{\pi e AR}$, so with fixed "
    r"$e$ and $AR$, $C_{D,i}\propto C_L^2$."
    "\n\n"
    r"Lift obeys $L=qSC_L$ with $q=\tfrac{1}{2}\rho V^2$. The problem fixes $V$ and $\rho$ (hence $q$) "
    r"and $S$, so $C_L\propto L$."
    "\n\n"
    r"Thus $C_{D,i}\propto L^2$. In steady level flight, $L_{\mathrm{level}}=W$. In a steady climb at "
    r"flight-path angle $\gamma$ measured from horizontal, lift perpendicular to the path balances "
    r"the perpendicular weight component: $L_{\mathrm{climb}}=W\cos\gamma$."
    "\n\n"
    r"The requested ratio is "
    r"$\dfrac{C_{D,i,\mathrm{level}}}{C_{D,i,\mathrm{climb}}}"
    r"=\left(\dfrac{L_{\mathrm{level}}}{L_{\mathrm{climb}}}\right)^2"
    r"=\left(\dfrac{W}{W\cos\gamma}\right)^2=\sec^2\gamma$."
    "\n\n"
    r"With $\gamma=30^\circ$, $\cos 30^\circ=\dfrac{\sqrt{3}}{2}$, "
    r"$\cos^2 30^\circ=\dfrac{3}{4}$, hence $\sec^2 30^\circ=\dfrac{4}{3}\approx 1.3333$. "
    r"Rounded to two decimals: $1.33$. "
    r"(Values like $C_{D,0}$, $e$, $AR$, and $C_{L,\mathrm{level}}$ cancel out of this induced-drag coefficient ratio.)"
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Given $W$, $S$, $C_{D,0}$, $e$, $AR$, and $C_{L,\mathrm{level}}=0.375$; climb angle "
        r"$\gamma=30^\circ$; same $V$ and $\rho$ for level vs.\ climb."
    ),
    (
        r"Induced drag coefficient: $C_{D,i}=\dfrac{C_L^2}{\pi e AR}$ $\Rightarrow$ "
        r"$C_{D,i}\propto C_L^2$ for fixed $e,AR$."
    ),
    (
        r"Lift equation: $L=qSC_L$ with $q=\tfrac{1}{2}\rho V^2$. Fixed $V,\rho,S$ $\Rightarrow$ "
        r"$C_L\propto L$."
    ),
    (
        r"Combine: $C_{D,i}\propto L^2$. Level flight: $L_{\mathrm{level}}=W$. "
        r"Steady climb: $L_{\mathrm{climb}}=W\cos\gamma$ (lift $\perp$ flight path)."
    ),
    (
        r"Ratio $\dfrac{C_{D,i,\mathrm{level}}}{C_{D,i,\mathrm{climb}}}"
        r"=\left(\dfrac{L_{\mathrm{level}}}{L_{\mathrm{climb}}}\right)^2"
        r"=\sec^2\gamma$."
    ),
    (
        r"Substitute $\gamma=30^\circ$: $\sec^2 30^\circ=\dfrac{1}{\cos^2 30^\circ}=\dfrac{4}{3}\approx 1.33$."
    ),
]

NEW_FORMULAS_USED: List[str] = [
    r"$C_{D,i}=\dfrac{C_L^2}{\pi e AR}$",
    r"$L=qSC_L$, $q=\tfrac{1}{2}\rho V^2$",
    r"$L_{\mathrm{level}}=W$",
    r"$L_{\mathrm{climb}}=W\cos\gamma$",
    r"$\dfrac{C_{D,i,\mathrm{level}}}{C_{D,i,\mathrm{climb}}}=\sec^2\gamma$",
]

NEW_HINTS: List[str] = [
    (
        r"Same $V$ and $\rho$ $\Rightarrow$ same $q$; then $C_L$ scales with lift force $L$."
    ),
    (
        r"Induced drag coefficient scales as $C_L^2$ when $e$ and $AR$ are fixed."
    ),
    (
        r"In steady climb, $L=W\cos\gamma$ (not $W$); compare $C_{D,i,\mathrm{level}}/C_{D,i,\mathrm{climb}}$, "
        r"not the reciprocal."
    ),
]

NEW_SOLUTION_PATH = (
    r"$C_{D,i}\propto C_L^2$, $C_L\propto L$ $\Rightarrow$ ratio $\propto (L_{\mathrm{level}}/L_{\mathrm{climb}})^2"
    r"=\sec^2\gamma$"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"$C_{D,0}$ and absolute $C_L$ values cancel when taking the ratio at fixed $q,S,e,AR$."
    ),
    (
        r"The numerical trap is using $\cos^2\gamma$ instead of $\sec^2\gamma$—that gives $\approx 0.75$, "
        r"the inverse ratio."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Recognize $L=W\cos\gamma$ in steady climb (lift perpendicular to the flight path).",
    r"Use $C_{D,i}\propto C_L^2$ and $C_L\propto L$ before plugging numbers.",
    r"Ignore redundant data ($C_{D,0}$, $e$, $AR$, $C_{L,\mathrm{level}}$) for the coefficient ratio.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$C_{D,i}=\dfrac{C_L^2}{\pi e AR}$",
        "name": r"Induced drag coefficient (parabolic polar)",
        "conditions": [
            r"Incompressible lifting-line / polar form with constant $e$, $AR$.",
        ],
        "type": "equation",
        "relevance": r"Relates induced drag coefficient to $C_L$.",
    },
    {
        "formula": r"$L_{\mathrm{climb}}=W\cos\gamma$",
        "name": r"Lift in steady climb",
        "conditions": [
            r"Steady climb; $\gamma$ is flight-path angle above horizontal; thrust drag along path.",
        ],
        "type": "equation",
        "relevance": r"Gives lift magnitude normal to the flight path.",
    },
    {
        "formula": r"$\dfrac{C_{D,i,\mathrm{level}}}{C_{D,i,\mathrm{climb}}}=\sec^2\gamma$",
        "name": r"Induced-drag coefficient ratio (fixed $q,S,e,AR$)",
        "conditions": [
            r"Same dynamic pressure and geometry; level vs.\ steady climb at angle $\gamma$.",
        ],
        "type": "equation",
        "relevance": r"Directly yields the NAT after substituting $\gamma$.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            r"Inverting the ratio: reporting $\cos^2\gamma\approx 0.75$ instead of $\sec^2\gamma\approx 1.33$."
        ),
        "why_students_make_it": (
            r"Computing $C_{D,i,\mathrm{climb}}/C_{D,i,\mathrm{level}}$ or misreading 'level to climb'."
        ),
        "type": "Conceptual",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": (
            r"Write $\dfrac{C_{D,i,\mathrm{level}}}{C_{D,i,\mathrm{climb}}}$ explicitly before simplifying."
        ),
        "consequence": r"Answer near $0.75$ instead of $1.33$.",
    },
    {
        "mistake": r"Using $L=W\sin\gamma$ or $L=W/\cos\gamma$ instead of $L=W\cos\gamma$.",
        "why_students_make_it": r"Confusing weight components parallel vs.\ perpendicular to the flight path.",
        "type": "Calculation",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Resolve $\mathbf{W}$ into components normal and tangential to the path.",
        "consequence": r"Wrong $C_L$ ratio and wrong drag ratio.",
    },
    {
        "mistake": (
            r"Dragging $C_{D,0}$ into an 'induced drag coefficient ratio' or mixing total $C_D$ with $C_{D,i}$."
        ),
        "why_students_make_it": r"Not noticing the question specifies induced drag coefficient.",
        "type": "Conceptual",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Use $C_{D,i}=\dfrac{C_L^2}{\pi e AR}$ only.",
        "consequence": r"Unnecessary algebra and wrong cancellation assumptions.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": r"Quick NAT once you see fixed $q$ and induced-drag scaling.",
    "triage_tip": (
        r"$C_{D,i}\propto C_L^2$, $C_L\propto L$, level $L=W$, climb $L=W\cos\gamma$ $\Rightarrow$ ratio "
        r"$\sec^2\gamma$."
    ),
    "guessing_heuristic": (
        r"Level flight needs more lift than climb at the same speed $\Rightarrow$ "
        r"$C_{D,i,\mathrm{level}}>C_{D,i,\mathrm{climb}}$ $\Rightarrow$ ratio $>1$. "
        r"For $\gamma=30^\circ$, expect $\dfrac{4}{3}\approx 1.33$, not $0.75$."
    ),
    "time_management": r"About 2–3 minutes; avoid full numeric $C_{D,i}$ unless checking.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"Induced drag coefficient from $C_L$, $e$, $AR$?",
        "back": r"$C_{D,i}=\dfrac{C_L^2}{\pi e AR}$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "concept_recall",
        "front": r"In steady climb at flight-path angle $\gamma$, how do lift and weight relate?",
        "back": r"$L=W\cos\gamma$ (lift perpendicular to the flight path).",
        "difficulty": "medium",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": (
            r"Same $q,S$: level vs.\ steady climb at $\gamma$. Ratio "
            r"$C_{D,i,\mathrm{level}}/C_{D,i,\mathrm{climb}}$?"
        ),
        "back": r"$\sec^2\gamma$ (since $C_{D,i}\propto C_L^2$ and $C_L\propto L\propto \cos\gamma$ in climb).",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Common sign error for lift in climb?",
        "back": r"Use $W\cos\gamma$, not $W$ or $W\sin\gamma$, for lift magnitude in the steady-climb diagram.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "application",
        "front": r"Compute $\sec^2 30^\circ$ numerically to two decimals.",
        "back": r"$\cos 30^\circ=\dfrac{\sqrt{3}}{2}$, $\sec^2 30^\circ=\dfrac{4}{3}\approx 1.33$.",
        "difficulty": "easy",
        "time_limit_seconds": 45,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"Climb shrinks lift: $L=W\cos\gamma$ (normal component).",
        "concept": r"Weight resolution perpendicular to the flight path.",
        "effectiveness": "high",
        "context": r"Steady climb/descent force balances.",
    },
    {
        "mnemonic": r"$C_{D,i}$ follows $C_L^2$: small lift change, squared drag effect.",
        "concept": r"Induced drag scales with lift squared at fixed span efficiency.",
        "effectiveness": "high",
        "context": r"Drag polar / performance ratios.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "GATE 2019 AE induced drag ratio climb",
    "sec squared climb angle induced drag",
    "steady climb lift W cos gamma",
    "C_D,i proportional C_L squared",
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": r"Explicit $C_L$ ratio",
        "description": (
            r"$C_{L,\mathrm{climb}}/C_{L,\mathrm{level}}=\cos\gamma$ at fixed $qS$, so "
            r"$C_{D,i,\mathrm{level}}/C_{D,i,\mathrm{climb}}=1/\cos^2\gamma=\sec^2\gamma$."
        ),
        "pros_cons": r"Same algebra; emphasizes $C_L$ scaling.",
        "when_to_use": r"When you prefer lifting $C_L$ explicitly.",
    },
    {
        "name": r"Along-path thrust balance (sanity check)",
        "description": (
            r"In steady climb, $T=D+W\sin\gamma$ along the path; this item only needs "
            r"$C_{D,i}\propto C_L^2$ and $L=W\cos\gamma$."
        ),
        "pros_cons": r"Useful for climb performance context; extra variables not needed for the NAT.",
        "when_to_use": r"When verifying forces beyond the perpendicular lift relation.",
    },
]

NEW_CONNECTIONS: Dict[str, str] = {
    "Aerodynamics": (
        r"Induced drag arises from lift distribution; $C_{D,i}=\dfrac{C_L^2}{\pi e AR}$ links to wing theory."
    ),
    "Flight mechanics": (
        r"Climb equations split weight along and normal to the flight path."
    ),
    "Mathematics": (
        r"Trigonometric identities: $\sec^2\gamma=1/\cos^2\gamma$."
    ),
    "Physics": (
        r"Static equilibrium along perpendicular directions in an inclined plane."
    ),
}

NEW_DEEPER_DIVE: List[str] = [
    r"Thrust-required vs.\ speed in climb: $T=D+W\sin\gamma$ modifies power bookkeeping.",
    r"Range/endurance in climb: Breguet-style formulas change when $L\neq W$.",
    r"Low-speed stall: solutions assume attached flow; near stall, polar nonlinearities matter.",
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
    av["correct_answer"] = "1.33"

    exp = t1.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED

    sbs = t1.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = NEW_SOLUTION_PATH
    sbs["key_insights"] = NEW_KEY_INSIGHTS
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)

    t1["hints"] = NEW_HINTS

    da = t1.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    t1["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    prereq = t1.setdefault("prerequisites", {})
    prereq["essential"] = [
        r"Drag polar: $C_D=C_{D,0}+\dfrac{C_L^2}{\pi e AR}$; induced term $C_{D,i}=\dfrac{C_L^2}{\pi e AR}$.",
        r"Lift equation: $L=qSC_L$, $q=\tfrac{1}{2}\rho V^2$.",
        r"Level flight: $L=W$, $T=D$.",
        r"Steady climb: $L=W\cos\gamma$ (normal to path), along-path $T=D+W\sin\gamma$.",
        r"Trigonometry: $\cos$, $\sec$, identities for special angles.",
    ]
    helpful = list(prereq.get("helpful") or [])
    prereq["helpful"] = _merge_unique(
        [
            r"At fixed $q$ and $S$, $C_L\propto L$.",
            r"For ratios at fixed $e,AR$, compare $C_L^2$ only.",
        ],
        helpful,
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
    for k in ("subject_name_1", "subject_name_2", "subject_name_3", "subject_name_4"):
        conn.pop(k, None)
    t3["connections_to_other_subjects"] = conn

    dd = list(t3.get("deeper_dive_topics") or [])
    t3["deeper_dive_topics"] = _merge_unique(NEW_DEEPER_DIVE, dd)

    for am in t3.get("alternative_methods") or []:
        if not isinstance(am, dict):
            continue
        if am.get("name") == "Energy Method Derivation":
            am["description"] = (
                r"Power/climb context uses $P=TV=(D+W\sin\gamma)V$ and ties thrust margin to climb "
                r"rate—more detail than needed for the $C_{D,i}$ ratio at fixed $q,S,e,AR$."
            )

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

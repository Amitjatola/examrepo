"""
Fix GATE_2023_AE_Q40 LaTeX: drag polar, thrust = drag, quadratic in V^2.

Usage (from backend/):
  ./venv/bin/python patch_gate_2023_ae_q40_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2023_AE_Q40"

NEW_QUESTION_TEXT_PLAIN = (
    "Consider a general aviation airplane with weight 10 kN and a wing planform area of 15 m². "
    "The drag coefficient is C_D = C_D,0 + K C_L² with C_D,0 = 0.025 and K = 0.05. "
    "For level flight at an altitude where the density is 0.60 kg/m³ and thrust 1 kN, "
    "the maximum cruise speed is (rounded off to the nearest integer)"
)

NEW_QUESTION_TEXT_LATEX = (
    r"Consider a general aviation airplane with weight $W=10~\mathrm{kN}$ and wing planform area "
    r"$S=15~\mathrm{m}^2$. The drag coefficient is $C_D=C_{D,0}+KC_L^2$ with $C_{D,0}=0.025$ and "
    r"$K=0.05$. For level flight where $\rho=0.60~\mathrm{kg/m^3}$ and available thrust "
    r"$T=1~\mathrm{kN}$, the maximum cruise speed is (rounded off to the nearest integer)"
)

NEW_OPTIONS: Dict[str, str] = {
    "A": "87 m/s",
    "B": "30 m/s",
    "C": "36 m/s",
    "D": "101 m/s",
}

NEW_REASONING = (
    r"In steady level flight, $L=W$ and $T=D$. With $q=\tfrac{1}{2}\rho V^2$, "
    r"$C_L=\dfrac{W}{qS}=\dfrac{2W}{\rho V^2 S}$ and the parabolic polar "
    r"$C_D=C_{D,0}+KC_L^2$ gives"
    "\n"
    r"\["
    r"T_R=qSC_{D,0}+\frac{KW^2}{qS}"
    r"=\tfrac{1}{2}\rho V^2 S C_{D,0}+\frac{2KW^2}{\rho V^2 S}."
    r"\]"
    "\n"
    r"Using $W=10~\mathrm{kN}=10^4~\mathrm{N}$, $S=15~\mathrm{m}^2$, $\rho=0.60~\mathrm{kg/m^3}$, "
    r"$C_{D,0}=0.025$, $K=0.05$, and $T_{\mathrm{avail}}=10^3~\mathrm{N}$:"
    "\n"
    r"Parasite term: $\tfrac{1}{2}\rho SC_{D,0}=4.5\times 0.025=0.1125~\mathrm{N\,s^2/m^2}\cdot V^2$."
    "\n"
    r"Induced term: $\dfrac{2KW^2}{\rho S}\cdot\dfrac{1}{V^2}=\dfrac{10^7}{9}\cdot\dfrac{1}{V^2}~\mathrm{N}$ "
    r"(since $\dfrac{2KW^2}{\rho S}=\dfrac{2(0.05)(10^4)^2}{0.6\cdot 15}=\dfrac{10^7}{9}$)."
    "\n"
    r"Set $T_R=T_{\mathrm{avail}}$ and let $x=V^2$:"
    "\n"
    r"\[0.1125\,x+\frac{10^7}{9x}=1000\quad\Rightarrow\quad"
    r"0.1125\,x^2-1000\,x+\frac{10^7}{9}=0.\]"
    "\n"
    r"The discriminant is $\Delta=1000^2-4(0.1125)\!\left(\frac{10^7}{9}\right)=5\times 10^5$, so "
    r"$x=\dfrac{1000\pm\sqrt{\Delta}}{0.225}$ yields $x\approx 7587$ or $\approx 1302~\mathrm{m^2/s^2}$, "
    r"hence $V\approx 87~\mathrm{m/s}$ or $\approx 36~\mathrm{m/s}$. The larger root is the "
    r"high-speed intersection (maximum cruise speed for this thrust), so $V_{\max}\approx 87~\mathrm{m/s}$ "
    r"(option A)."
)

NEW_STEP_BY_STEP: List[str] = [
    (
        r"Given $W=10~\mathrm{kN}=10^4~\mathrm{N}$, $S=15~\mathrm{m}^2$, $\rho=0.60~\mathrm{kg/m^3}$, "
        r"$C_{D,0}=0.025$, $K=0.05$, $T_{\mathrm{avail}}=1~\mathrm{kN}=10^3~\mathrm{N}$."
    ),
    (r"Level flight: $L=W$ and $T=D$."),
    (
        r"$C_L=\dfrac{2W}{\rho V^2 S}$ from $W=L=\tfrac{1}{2}\rho V^2 S C_L$; "
        r"substitute into $C_D=C_{D,0}+KC_L^2$."
    ),
    (
        r"Thrust required: $T_R=\tfrac{1}{2}\rho V^2 S C_{D,0}+\dfrac{2KW^2}{\rho V^2 S}$ "
        r"(equivalently $qSC_{D,0}+KW^2/(qS)$ with $q=\tfrac{1}{2}\rho V^2$)."
    ),
    (
        r"Numbers: $\tfrac{1}{2}\rho S C_{D,0}=4.5\times 0.025=0.1125$; "
        r"$\dfrac{2KW^2}{\rho S}=\dfrac{10^7}{9}$."
    ),
    (
        r"Balance $T_R=T_{\mathrm{avail}}$: $1000=0.1125\,V^2+\dfrac{10^7}{9V^2}$."
    ),
    (
        r"Let $x=V^2$: multiply by $x$ to get $0.1125\,x^2-1000\,x+10^7/9=0$."
    ),
    (
        r"Roots $x\approx 7587$ and $\approx 1302~\mathrm{m^2/s^2}$ $\Rightarrow$ "
        r"$V\approx 87$ and $\approx 36~\mathrm{m/s}$; take the larger for maximum cruise speed: "
        r"$87~\mathrm{m/s}$."
    ),
]

NEW_FORMULAS_USED: List[str] = [
    r"$L=W$, $T=D$ (steady level flight)",
    r"$L=\tfrac{1}{2}\rho V^2 S C_L$",
    r"$D=\tfrac{1}{2}\rho V^2 S C_D$",
    r"$C_D=C_{D,0}+KC_L^2$",
    r"$C_L=\dfrac{2W}{\rho V^2 S}$",
    r"$T_R=\tfrac{1}{2}\rho V^2 S C_{D,0}+\dfrac{2KW^2}{\rho V^2 S}$",
]

NEW_HINTS: List[str] = [
    (
        r"Eliminate $C_L$ using $C_L=\dfrac{2W}{\rho V^2 S}$ before forming $C_D=C_{D,0}+KC_L^2$."
    ),
    (
        r"After substitution, $T$ has a term $\propto V^2$ and a term $\propto 1/V^2$; multiply by $V^2$ "
        r"to get a quadratic in $V^2$."
    ),
    (
        r"Two positive speeds satisfy $T_R=T_{\mathrm{avail}}$; the higher one is the "
        r"maximum cruise speed for that thrust."
    ),
]

NEW_SOLUTION_PATH = (
    r"$L=W\Rightarrow C_L$ $\Rightarrow$ $C_D=C_{D,0}+KC_L^2$ $\Rightarrow$ $T_R=D$ $\Rightarrow$ "
    r"quadratic in $V^2$ $\Rightarrow$ larger $V$"
)

NEW_KEY_INSIGHTS: List[str] = [
    (
        r"$T_R(V)$ from a parabolic polar is the sum of parasite drag $\propto V^2$ and induced drag "
        r"$\propto 1/V^2$."
    ),
    (
        r"Setting $T_{\mathrm{avail}}=T_R$ generally gives two speeds (high- and low-speed intersections); "
        r"here the question asks for the maximum cruise speed (upper branch)."
    ),
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    r"Correct substitution $C_L(W,V)$ into the drag polar (watch squaring).",
    r"Algebra: multiply by $V^2$ to clear $1/V^2$ and solve a quadratic in $V^2$.",
    r"Interpretation: pick the larger root as $V_{\max}$ for given thrust.",
]

NEW_FORMULAS_PRINCIPLES: List[Dict[str, Any]] = [
    {
        "formula": r"$L=\tfrac{1}{2}\rho V^2 S C_L$",
        "name": r"Lift equation",
        "conditions": [
            r"Steady level flight uses $L=W$; incompressible form as stated.",
        ],
        "type": "equation",
        "relevance": r"Relates $C_L$ to weight, density, speed, and wing area.",
    },
    {
        "formula": r"$C_D=C_{D,0}+KC_L^2$",
        "name": r"Parabolic drag polar",
        "conditions": [
            r"Subsonic attached flow; $C_{D,0}$ and $K$ treated as constants for this item.",
        ],
        "type": "equation",
        "relevance": r"Expresses total drag coefficient vs.\ lift coefficient.",
    },
    {
        "formula": r"$T_R=\tfrac{1}{2}\rho V^2 S C_{D,0}+\dfrac{2KW^2}{\rho V^2 S}$",
        "name": r"Thrust required (level flight, parabolic polar)",
        "conditions": [
            r"$L=W$ used to eliminate $C_L$; $T_R=D$.",
        ],
        "type": "equation",
        "relevance": r"Directly sets up $T_{\mathrm{avail}}=T_R(V)$ for maximum speed.",
    },
    {
        "formula": r"$C_L=\dfrac{2W}{\rho V^2 S}$",
        "name": r"Lift coefficient from weight",
        "conditions": [r"Follows from $L=W$ with $L=\tfrac{1}{2}\rho V^2 S C_L$."],
        "type": "equation",
        "relevance": r"Bridge between flight speed and polar drag.",
    },
]

NEW_COMMON_MISTAKES: List[Dict[str, Any]] = [
    {
        "mistake": (
            r"Forgetting to square $C_L=\dfrac{2W}{\rho V^2 S}$ when substituting into $KC_L^2$."
        ),
        "why_students_make_it": r"Treating induced drag as $\propto 1/V$ instead of $1/V^2$.",
        "type": "Calculation",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Write $C_L$ once, then square it explicitly before multiplying by $K$.",
        "consequence": r"Wrong power of $V$ in $T_R(V)$; roots no longer match the options.",
    },
    {
        "mistake": (
            r"Solving $T=\tfrac{1}{2}\rho V^2 S C_{D,0}$ only (ignoring induced drag)."
        ),
        "why_students_make_it": r"Stopping after the parasite term.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Use the full $T_R=qSC_{D,0}+KW^2/(qS)$ form.",
        "consequence": r"Underestimates drag and overestimates $V$.",
    },
    {
        "mistake": r"Choosing the smaller root of the quadratic as $V_{\max}$.",
        "why_students_make_it": r"Confusing low-speed and high-speed intersections on the thrust-required curve.",
        "type": "Conceptual",
        "severity": "High",
        "frequency": "occasional",
        "how_to_avoid": r"Sketch $T_R(V)$ vs.\ $T_{\mathrm{avail}}$: upper intersection is faster.",
        "consequence": r"Picking $\approx 36~\mathrm{m/s}$ instead of $\approx 87~\mathrm{m/s}$.",
    },
    {
        "mistake": r"Mixing kN and N (e.g.\ using $W=10$ instead of $10^4~\mathrm{N}$).",
        "why_students_make_it": r"Unit inconsistency under time pressure.",
        "type": "Units",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Convert everything to SI (N, m, kg, s) before algebra.",
        "consequence": r"Answers off by orders of magnitude.",
    },
]

NEW_EXAM_STRATEGY: Dict[str, Any] = {
    "priority": r"High-yield: one substitution and a quadratic in $V^2$.",
    "triage_tip": (
        r"Level flight $\Rightarrow$ $C_L=\dfrac{2W}{\rho V^2 S}$ into $C_D=C_{D,0}+KC_L^2$, then "
        r"$T=\tfrac{1}{2}\rho V^2 S C_D$; multiply by $V^2$."
    ),
    "guessing_heuristic": (
        r"Here $T/W=0.1$: not tiny—both parasite and induced parts matter. Expect two plausible speeds "
        r"($\sim 36$ and $\sim 87~\mathrm{m/s}$); max cruise is the larger."
    ),
    "time_management": r"About 4–5 minutes: 2 min setup, 2 min algebra, 1 min check.",
}

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": r"Force balances for steady level flight?",
        "back": r"$L=W$ and $T=D$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
    {
        "card_type": "formula_recall",
        "front": r"Parabolic drag polar?",
        "back": r"$C_D=C_{D,0}+KC_L^2$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": (
            r"For fixed $T_{\mathrm{avail}}$, how many level-flight speeds from $T_R(V)$, and which is "
            r"$V_{\max}$?"
        ),
        "back": (
            r"Generally two intersections; the higher speed is the maximum cruise speed for that thrust "
            r"(upper branch)."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"After substituting $C_L(W,V)$ into the polar, what power of $V$ appears with $K$?",
        "back": r"$C_L^2\propto 1/V^4$ gives induced drag $\propto 1/V^2$ in thrust.",
        "difficulty": "hard",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": (
            r"Given $W=10~\mathrm{kN}$, $S=15~\mathrm{m}^2$, $\rho=0.6~\mathrm{kg/m^3}$, "
            r"$C_L=0.5$, find $V$ from $L=W$."
        ),
        "back": (
            r"$V=\sqrt{\dfrac{2W}{\rho S C_L}}=\sqrt{\dfrac{2\times 10^4}{0.6\cdot 15\cdot 0.5}}"
            r"\approx 66.7~\mathrm{m/s}$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": r"LTWD: Lift–Weight, Thrust–Drag.",
        "concept": r"Start every level-flight performance item with $L=W$, $T=D$.",
        "effectiveness": "high",
        "context": r"Static performance / cruise speed.",
    },
    {
        "mnemonic": r"$C_D=C_{D,0}+KC_L^2$: base plus induced (square of lift).",
        "concept": r"Parabolic polar structure.",
        "effectiveness": "medium",
        "context": r"Subsonic drag modeling.",
    },
]

NEW_SEARCH_KEYWORDS: List[str] = [
    "GATE 2023 AE drag polar maximum cruise speed",
    "thrust required parabolic polar quadratic",
    "T equals D level flight two speeds",
    "C_D0 K C_L squared induced drag",
    "maximum cruise speed thrust available",
]

NEW_ALTERNATIVE_METHODS: List[Dict[str, Any]] = [
    {
        "name": r"Explicit $T_R(V)$ formula",
        "description": (
            r"$T_R=\tfrac{1}{2}\rho V^2 S C_{D,0}+\dfrac{2KW^2}{\rho V^2 S}$; set equal to "
            r"$T_{\mathrm{avail}}$ and solve for $V$."
        ),
        "pros_cons": r"Fast if memorized; still requires careful algebra.",
        "when_to_use": r"When you want one equation in $V$ immediately.",
    },
    {
        "name": r"Via $L/D=W/T$",
        "description": (
            r"Use $L/D=W/T$ with $C_L/C_D$ and the polar to solve for $C_L$, then "
            r"$V=\sqrt{2W/(\rho S C_L)}$ (two $C_L$ $\Rightarrow$ two $V$)."
        ),
        "pros_cons": r"Highlights efficiency; same algebra in disguise.",
        "when_to_use": r"When $W/T$ simplifies nicely (here $W/T=10$).",
    },
]

NEW_CONNECTIONS: Dict[str, str] = {
    "Aerodynamics": (
        r"The polar $C_D=C_{D,0}+KC_L^2$ encodes parasite and induced drag; $K$ ties to aspect ratio "
        r"and efficiency."
    ),
    "Algebra": (
        r"Multiplying by $V^2$ clears $1/V^2$ and yields a quadratic in $V^2$."
    ),
    "Aircraft performance": (
        r"$T_R(V)$ sets cruise feasibility; intersections with $T_{\mathrm{avail}}$ give speed envelope."
    ),
    "Propulsion": (
        r"$T_{\mathrm{avail}}$ depends on engine and altitude; here it is given as $1~\mathrm{kN}$."
    ),
    "Stability and control": (
        r"Operating point affects trim and margins; this item only needs force equilibrium."
    ),
}

NEW_DEEPER_DIVE: List[str] = [
    r"$T_{\mathrm{avail}}$ vs.\ $T_{\mathrm{req}}(V)$ plots: two intersections except at tangency.",
    r"Altitude: lower $\rho$ shifts $T_{\mathrm{req}}$ and changes $V_{\max}$ for fixed thrust.",
    r"Propeller aircraft: often analyze $P_{\mathrm{req}}=T_{\mathrm{req}}\cdot V$ instead of thrust alone.",
    r"Stall: the low-speed root must exceed $V_{\mathrm{stall}}$ to be physically usable.",
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
    av["correct_answer"] = "A"

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
    t3["alternative_methods"] = NEW_ALTERNATIVE_METHODS
    t3["deeper_dive_topics"] = NEW_DEEPER_DIVE
    t3["connections_to_other_subjects"] = NEW_CONNECTIONS
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

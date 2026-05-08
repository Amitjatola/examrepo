import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2012_AE_Q36"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    An aircraft is trimmed straight and level at true air speed (TAS) of 100 m/s at standard sea level (SSL).
    Further, pull of 5 N holds the speed at 90 m/s without re-trimming at SSL (air density = 1.22 kg/m^3).
    To fly at 3000 m altitude (air density = 0.91 kg/m^3) and 120 m/s TAS without re-trimming, the aircraft needs
    """
).strip()

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    An aircraft is trimmed straight and level at true airspeed (TAS) $V_0 = 100\ \mathrm{m/s}$ at standard sea level (SSL), with air density $\rho_{\mathrm{SL}} = 1.22\ \mathrm{kg/m^3}$.

    A **pull** of $5\ \mathrm{N}$ on the stick holds $V = 90\ \mathrm{m/s}$ at SSL **without re-trimming**.

    For flight at $3000\ \mathrm{m}$ altitude with $\rho = 0.91\ \mathrm{kg/m^3}$ and $V = 120\ \mathrm{m/s}$ TAS, also **without re-trimming**, the aircraft needs
    """
).strip()

NEW_OPTIONS = {
    "A": r"$1.95\ \mathrm{N}$ upward force.",
    "B": r"$1.95\ \mathrm{N}$ downward force.",
    "C": r"$1.85\ \mathrm{N}$ upward force.",
    "D": r"$1.75\ \mathrm{N}$ downward force.",
}

NEW_REASONING = dedent(
    r"""
    **Model:** With elevator fixed at the trim setting, stick force varies approximately linearly with dynamic-pressure deviation from trim:
    $$F \;=\; C\,\bigl(q - q_0\bigr),$$
    where $q=\tfrac{1}{2}\rho V^2$, $q_0$ is trim dynamic pressure, and we take a **pull** (nose-up) as **negative** $F$ and a **push** (nose-down) as **positive** $F$.

    **Trim at SSL:** $\rho_{\mathrm{SL}} = 1.22\ \mathrm{kg/m^3}$, $V_0 = 100\ \mathrm{m/s}$:
    $$q_0 = \tfrac{1}{2}(1.22)(100)^2 = 6100\ \mathrm{Pa}.$$

    **First off-trim point (SSL, $V_1=90\ \mathrm{m/s}$):**
    $$q_1 = \tfrac{1}{2}(1.22)(90)^2 = 4941\ \mathrm{Pa}.$$
    Given a **$5\ \mathrm{N}$ pull**, $F_1=-5\ \mathrm{N}$:
    $$-5 = C(4941-6100)= -1159\,C \quad\Rightarrow\quad C=\frac{5}{1159}\ \mathrm{N}/\mathrm{Pa}.$$

    **New point ($\rho_2=0.91$, $V_2=120\ \mathrm{m/s}$):**
    $$q_2 = \tfrac{1}{2}(0.91)(120)^2 = 6552\ \mathrm{Pa}.$$
    $$F_2 = C(q_2-q_0)=\frac{5}{1159}(6552-6100)\approx 1.95\ \mathrm{N}.$$
    The sign is **positive** ⇒ **push** ⇒ **downward** stick force $\approx 1.95\ \mathrm{N}$ → **option B**.
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Write dynamic pressure $q=\tfrac{1}{2}\rho V^2$; trim at SSL gives $q_0=\tfrac{1}{2}\rho_{\mathrm{SL}}V_0^2$.",
    r"Compute $q_0=\tfrac{1}{2}(1.22)(100)^2=6100\ \mathrm{Pa}$.",
    r"At SSL, $V_1=90\ \mathrm{m/s}$: $q_1=\tfrac{1}{2}(1.22)(90)^2=4941\ \mathrm{Pa}$. A $5\ \mathrm{N}$ **pull** means $F_1=-5\ \mathrm{N}$ if push is $+$.",
    r"Linear fit: $F=C(q-q_0)$ ⇒ $C=\dfrac{-5}{q_1-q_0}=\dfrac{5}{1159}\ \mathrm{N}/\mathrm{Pa}$.",
    r"At altitude: $q_2=\tfrac{1}{2}(0.91)(120)^2=6552\ \mathrm{Pa}$; then $F_2=C(q_2-q_0)\approx 1.95\ \mathrm{N}$ (push / downward).",
    r"Select **B**.",
]

NEW_FORMULAS_USED = [
    r"$q=\dfrac{1}{2}\rho V^2$",
    r"$F = C\,(q-q_0)$ (stick-fixed; small deviations from trim, linearized)",
    r"$C = \dfrac{F_1}{q_1-q_0}$ from one measured off-trim point",
    r"$F_2 = C\,(q_2-q_0)$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Dynamic pressure",
        "type": "equation",
        "formula": r"$q=\dfrac{1}{2}\rho V^2$",
        "relevance": "Relates density and TAS to the aerodynamic load factor scaling stick/hinge moments at fixed elevator.",
        "conditions": [r"Incompressible/low-$M$ approximation as in the problem statement."],
    },
    {
        "name": "Stick force vs. dynamic pressure (stick-fixed)",
        "type": "principle",
        "formula": r"$F \propto (q-q_{\mathrm{trim}})$",
        "relevance": "Lets you infer a constant from the $90\ \mathrm{m/s}$ point and extrapolate to $120\ \mathrm{m/s}$ at new density.",
        "conditions": ["Fixed trim tab/elevator; linear range; neglect compressibility as implied."],
    },
    {
        "name": "Trim dynamic pressure",
        "type": "equation",
        "formula": r"$q_{\mathrm{trim}}=\dfrac{1}{2}\rho_{\mathrm{SL}}V_0^2$",
        "relevance": "Reference $q_0$ for the given trim TAS at SSL.",
        "conditions": [r"Trim at SSL with stated $\rho_{\mathrm{SL}}$ and $V_0$."],
    },
]

NEW_HINTS = [
    r"Use $q=\tfrac{1}{2}\rho V^2$ at each condition; trim gives $q_0$.",
    r"Assume $F \propto (q-q_0)$ with fixed elevator; one data point fixes $C$.",
    r"A **pull** corresponds to nose-up → use a consistent sign (here pull $=-5\ \mathrm{N}$ if push is $+$).",
    r"Faster than trim at higher $q$ usually needs a **push** (downward) for a stable airplane.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": r"Dynamic pressure in terms of $\rho$ and $V$?",
        "back": r"$q=\dfrac{1}{2}\rho V^2$",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "concept_recall",
        "front": r"Stable aircraft, fixed trim: slower than trim vs faster than trim stick force?",
        "back": r"Slower than trim: pull (nose-up tendency must be countered). Faster than trim: push.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Two common errors in the $q$ ratio?",
        "back": r"Forgetting $V^2$ (not $V$) and using sea-level $\rho$ when altitude $\rho$ is given.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "definition",
        "front": r"What does “trimmed straight and level” mean?",
        "back": r"$L=W$, thrust $\approx$ drag, and pitching moment about the CG is zero at the reference condition (zero stick force at $V_0$ here).",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "q uses $V^2$",
        "concept": r"$q=\dfrac{1}{2}\rho V^2$",
        "effectiveness": "high",
        "context": "Dynamic pressure calculations",
    },
    {
        "mnemonic": "Pull slow, push fast (stable, fixed trim)",
        "concept": r"Off-trim speed lower than trim $\Rightarrow$ pull; higher $\Rightarrow$ push",
        "effectiveness": "high",
        "context": "Sign sanity check",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": r"Using $V$ instead of $V^2$ in dynamic pressure.",
        "severity": "High",
        "frequency": "common",
        "consequence": r"Force magnitude wrong by order of $\sqrt{\cdot}$ scaling errors.",
        "how_to_avoid": r"Always write $q=\tfrac{1}{2}\rho V^2$ explicitly.",
        "why_students_make_it": "Rushing the algebra.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Using $\rho_{\mathrm{SL}}$ at altitude.",
        "severity": "High",
        "frequency": "common",
        "consequence": r"Wrong $q_2$ and wrong force.",
        "how_to_avoid": r"Label $\rho$ for each segment; use $0.91$ for the $120\ \mathrm{m/s}$ case.",
        "why_students_make_it": "Single-$\rho$ habit from textbook SSL drills.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Sign error: pull vs push.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": r"Picks upward-force distractors.",
        "how_to_avoid": r"Fix a convention ($F>0$ push) before solving; check $q_2>q_0$ here implies push.",
        "why_students_make_it": r"Confusing “hold speed” wording with force direction.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Attempt If Time",
    "triage_tip": r"Recognize $F\propto(q-q_0)$ pattern → compute three $q$’s → one proportionality constant → **~3 min**.",
    "guessing_heuristic": r"$q_2>q_0$ at $120\ \mathrm{m/s}$ ⇒ push/downward → eliminate A, C; magnitude $\sim2\ \mathrm{N}$ → **B**.",
    "time_management": r"Budget 3–4 min; if stuck after $q_0$, guess using sign + ~2 N scale.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Multi-step numeric with different $(\rho,V)$ pairs.",
    r"Requires a consistent pull/push sign convention.",
    r"Easy to use wrong $\rho$ or forget $V^2$.",
]

NEW_ALT_METHODS = [
    {
        "name": r"Sketch $q$ vs. $V$ at two densities",
        "description": r"Plot qualitative $q=\tfrac{1}{2}\rho V^2$ to see $q_2>q_0$ and confirm push direction; still need numbers for magnitude.",
        "pros_cons": "Pros: sign check. Cons: slower than direct algebra.",
        "when_to_use": r"If unsure about push vs pull.",
    },
    {
        "name": r"Hinge-moment / control-derivative route",
        "description": r"Use $C_H = C_{H_\alpha}\Delta\alpha + C_{H_{\delta_e}}\delta_e$ and elevator effectiveness to relate $\Delta C_L$ to stick force. Not practical here—derivatives unstated.",
        "pros_cons": "Pros: rigorous. Cons: over-parameterized for this MCQ.",
        "when_to_use": r"Design courses with full derivative tables.",
    },
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2012 AE Q36 stick force trim",
    "dynamic pressure trim extrapolation",
    "stick fixed without re-trimming",
    "longitudinal trim SSL altitude",
    "q half rho V squared",
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
    av["correct_answer"] = "B"

    exp = o.setdefault("explanation", {})
    exp["step_by_step"] = NEW_STEP_BY_STEP
    exp["formulas_used"] = NEW_FORMULAS_USED
    exp["question_nature"] = "Application"

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEP_BY_STEP)
    sbs["solution_path"] = (
        r"$q=\tfrac{1}{2}\rho V^2$ at trim and off-trim "
        r"$\Rightarrow$ $F=C(q-q_0)$ from SSL point "
        r"$\Rightarrow$ apply at $(\rho_2,V_2)$"
    )

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    return o


def patch_t2(t2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t2 or {})
    o["flashcards"] = NEW_FLASHCARDS
    o["mnemonics_memory_aids"] = NEW_MNEMONICS
    o["common_mistakes"] = NEW_COMMON_MISTAKES
    o["exam_strategy"] = NEW_EXAM_STRATEGY

    nested = o.get("tier_3_enhanced_learning")
    if isinstance(nested, dict):
        nested = deepcopy(nested)
        nested["alternative_methods"] = NEW_ALT_METHODS
        nested["search_keywords"] = _merge_unique(
            NEW_SEARCH_KEYWORDS, list(nested.get("search_keywords") or [])
        )
        o["tier_3_enhanced_learning"] = nested

    return o


def patch_t3(t3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t3 or {})
    o["alternative_methods"] = NEW_ALT_METHODS
    o["search_keywords"] = _merge_unique(NEW_SEARCH_KEYWORDS, list(o.get("search_keywords") or []))
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

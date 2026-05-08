import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2021_AE_Q13"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    The C_m–alpha variation for a certain aircraft is shown in the figure.
    Which one of the following statements is true for this aircraft?
    """
).strip()

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    The **$C_m$–$\alpha$** variation (pitching-moment coefficient vs. angle of attack) for a certain aircraft is shown in the figure.

    Which one of the following statements is true for this aircraft?
    """
).strip()

NEW_OPTIONS = {
    "A": r"The aircraft can trim at a positive $\alpha$ and it is stable.",
    "B": r"The aircraft can trim at a positive $\alpha$, but it is unstable.",
    "C": r"The aircraft can trim at a negative $\alpha$ and it is stable.",
    "D": r"The aircraft can trim at a negative $\alpha$, but it is unstable.",
}

NEW_REASONING = dedent(
    r"""
    **Trim:** Pitch equilibrium requires zero pitching-moment coefficient about the CG, i.e. $C_m=0$. On a $C_m$ vs. $\alpha$ plot, trim occurs where the curve crosses the $\alpha$-axis. For the given GATE figure, that intersection is at **$\alpha>0$**, so the aircraft **can trim at a positive $\alpha$**.

    **Static longitudinal stability:** Near trim, static stability is determined by the **slope**
    $$\frac{dC_m}{d\alpha}$$
    at the trim point. With the usual sign convention (nose-up moment positive or as in the plot), **static stability requires**
    $$\frac{dC_m}{d\alpha}<0$$
    at trim (restoring tendency). **If** $\dfrac{dC_m}{d\alpha}>0$ **at trim, the aircraft is statically unstable.**

    From the figure, at the $C_m=0$ crossing with $\alpha>0$, the local tangent **rises** as $\alpha$ increases, so $\dfrac{dC_m}{d\alpha}>0$ there → **unstable**.

    **Conclusion:** trims at **positive $\alpha$** but is **unstable** → **option B**.
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Read axes: $C_m$ (pitching-moment coefficient) vs. $\alpha$ (angle of attack).",
    r"**Trim:** locate $C_m=0$ → intersection with $\alpha$-axis. Here $\alpha_{\mathrm{trim}}>0$.",
    r"**Stability:** at that trim point, examine the **local slope** $\dfrac{dC_m}{d\alpha}$ (tangent).",
    r"Criterion: $\dfrac{dC_m}{d\alpha}<0$ stable; $\dfrac{dC_m}{d\alpha}>0$ unstable; $=0$ neutral.",
    r"Graph shows **positive slope** at the $C_m=0$, $\alpha>0$ point → **unstable**.",
    r"Match: positive-$\alpha$ trim + unstable → **B**.",
]

NEW_FORMULAS_USED = [
    r"Trim: $C_m=0$ at equilibrium $\alpha_{\mathrm{trim}}$",
    r"$C_m \approx C_{m_0} + C_{m_\alpha}\,\alpha$ (linear range)",
    r"Static stability at trim: $\dfrac{dC_m}{d\alpha}<0$",
    r"Static instability at trim: $\dfrac{dC_m}{d\alpha}>0$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Linearized pitching-moment model",
        "type": "equation",
        "formula": r"$C_m = C_{m_0} + C_{m_\alpha}\,\alpha$",
        "relevance": r"Relates $C_m$ to $\alpha$ near trim; slope and intercept set trim and stability in the linear approximation.",
        "conditions": [r"Small $\alpha$; linear aerodynamics."],
    },
    {
        "name": "Longitudinal static stability (stick-fixed)",
        "type": "principle",
        "formula": r"$\dfrac{dC_m}{d\alpha}<0$ at trim",
        "relevance": r"Restoring pitch response after an $\alpha$ disturbance.",
        "conditions": [r"Evaluated at the trim point on the $C_m$–$\alpha$ curve."],
    },
    {
        "name": "Longitudinal static instability",
        "type": "principle",
        "formula": r"$\dfrac{dC_m}{d\alpha}>0$ at trim",
        "relevance": r"Divergent pitch tendency from trim after an $\alpha$ disturbance.",
        "conditions": [r"Evaluated at the trim point."],
    },
]

NEW_HINTS = [
    r"Trim is **where** $C_m=0$ (axis crossing). Stability is the **slope** there, not the sign of $\alpha_{\mathrm{trim}}$.",
    r"Tangent rising with $\alpha$ ⇒ $\dfrac{dC_m}{d\alpha}>0$ ⇒ **unstable**.",
    r"Do not assume “positive-$\alpha$ trim ⇒ stable”; trim angle and stability are separate checks.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "definition",
        "front": r"Longitudinal trim in pitch?",
        "back": r"$C_m=0$: no net pitching moment about the CG at that $\alpha$ (equilibrium in pitch).",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "definition",
        "front": r"Static longitudinal stability condition on $C_m(\alpha)$?",
        "back": r"$\dfrac{dC_m}{d\alpha}<0$ at the trim point (restoring moment after an $\alpha$ perturbation).",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
    {
        "card_type": "application",
        "front": r"If $C_m(\alpha)$ crosses zero at $\alpha=-5^\circ$ and $\dfrac{dC_m}{d\alpha}<0$ there, trim and stability?",
        "back": r"Trims at $\alpha=-5^\circ$; negative slope ⇒ **statically stable** at that trim point.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"How to avoid mixing trim and stability on a $C_m$–$\alpha$ graph?",
        "back": r"Trim: **location** of $C_m=0$. Stability: **slope** $\dfrac{dC_m}{d\alpha}$ **at** that point.",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": r"Linear trim angle: relate $\alpha_{\mathrm{trim}}$ to $C_{m_0}$ and $C_{m_\alpha}$.",
        "back": r"$\alpha_{\mathrm{trim}}=-\dfrac{C_{m_0}}{C_{m_\alpha}}$ (when $C_m\approx C_{m_0}+C_{m_\alpha}\alpha$).",
        "difficulty": "medium",
        "time_limit_seconds": 40,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "SSN — stable slope negative",
        "concept": r"$\dfrac{dC_m}{d\alpha}<0$ ⇒ stable",
        "effectiveness": "high",
        "context": r"$C_m$ vs. $\alpha$ plots",
    },
    {
        "mnemonic": "Zero moment, check tangent",
        "concept": r"Trim at $C_m=0$; stability from slope at that $\alpha$",
        "effectiveness": "high",
        "context": r"Graph problems",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Confusing trim ($C_m=0$) with stability (sign of $\dfrac{dC_m}{d\alpha}$).",
        "severity": "High",
        "frequency": "common",
        "consequence": r"Wrong stability label despite correct trim.",
        "how_to_avoid": r"Two-step: (1) zero crossing (2) tangent sign at that point.",
        "why_students_make_it": r"Both ideas read from the same curve.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Misreading the local slope at trim.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": r"Flips stable vs. unstable.",
        "how_to_avoid": r"Draw the tangent at the $C_m=0$ crossing only.",
        "why_students_make_it": r"Eyeballing a distant part of the curve.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Assuming positive-$\alpha$ trim implies stability.",
        "severity": "High",
        "frequency": "common",
        "consequence": r"Picks “positive $\alpha$ and stable” by habit.",
        "how_to_avoid": r"Many trainers are stable at positive $\alpha$ — not automatic for an arbitrary curve.",
        "why_students_make_it": r"Pattern-matching typical textbook sketches.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"~60 s: find $C_m=0$ crossing → sign of $\alpha_{\mathrm{trim}}$ → slope at that point.",
    "guessing_heuristic": r"If trim is clearly $\alpha>0$ but slope is clearly positive, **unstable** → favor **B** over **A**.",
    "time_management": r"1–2 min; avoid calculating — this is graphical.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Requires correct **local** slope at the trim crossing.",
    r"Separating trim location from stability sign.",
    r"Image-based: mis-read curve if axes are skimmed.",
]

NEW_ALT_METHODS = [
    {
        "name": r"Analytic $C_m(\alpha)$ if coefficients given",
        "description": r"Solve $C_m(\alpha_{\mathrm{trim}})=0$ from $C_m=C_{m_0}+C_{m_\alpha}\alpha$; stability from sign of $C_{m_\alpha}=\dfrac{dC_m}{d\alpha}$.",
        "pros_cons": r"Pros: exact. Cons: not available when only a plot is given.",
        "when_to_use": r"Algebraic stems with stated $C_{m_0},\,C_{m_\alpha}$.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2021 AE Q13 Cm alpha graph",
    "longitudinal static stability slope",
    "trim Cm equals zero",
    "positive slope Cm alpha unstable",
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
        r"$C_m=0$ crossing $\Rightarrow$ sign of $\alpha_{\mathrm{trim}}$ "
        r"$\Rightarrow$ $\dfrac{dC_m}{d\alpha}$ at that point $\Rightarrow$ match option"
    )
    sbs["key_insights"] = [
        r"Trim: $C_m=0$ (intersection with $\alpha$-axis).",
        r"Static stability: sign of $\dfrac{dC_m}{d\alpha}$ at trim ($<0$ stable, $>0$ unstable).",
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

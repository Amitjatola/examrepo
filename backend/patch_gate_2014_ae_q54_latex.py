import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2014_AE_Q54"

NEW_QUESTION_TEXT_PLAIN = dedent(
    """
    Consider the following four statements regarding aircraft longitudinal stability:
    P. C_M,cg at zero lift must be positive.
    Q. dC_M,cg / d alpha_a must be negative (alpha_a is absolute angle of attack).
    R. C_M,cg at zero lift must be negative.
    S. Slope of C_L versus alpha_a must be negative.
    Which combination is the necessary criterion for stick-fixed longitudinal balance and static stability?
    """
).strip()

# Mixed markdown + inline/display math; safe for LatexRenderer (no erroneous outer $$ wrapper).
NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    Consider the following four statements regarding aircraft longitudinal stability:

    **P.** $C_{M,\mathrm{cg}}$ at zero lift must be positive.

    **Q.** $\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}$ must be negative ($\alpha_a$ is absolute angle of attack).

    **R.** $C_{M,\mathrm{cg}}$ at zero lift must be negative.

    **S.** The slope of $C_L$ versus $\alpha_a$ must be negative, i.e. $\dfrac{dC_L}{d\alpha_a}<0$.

    Which of the following combinations is the necessary criterion for stick-fixed longitudinal balance and static stability?
    """
).strip()

NEW_OPTIONS = {
    "A": r"$Q$ and $R$ only",
    "B": r"$Q$, $R$, and $S$ only",
    "C": r"$P$ and $Q$ only",
    "D": r"$Q$ and $S$ only",
}

NEW_REASONING = dedent(
    r"""
    **Statements:** **P** — $C_{M,\mathrm{cg}}$ at zero lift must be positive; **Q** — $\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$; **R** — $C_{M,\mathrm{cg}}$ at zero lift must be negative; **S** — $\dfrac{dC_L}{d\alpha_a}<0$.

    **Q (static stability):** Longitudinal static stability (stick-fixed) requires a *restoring* pitching moment response to an angle-of-attack disturbance. With the usual sign convention, that is
    $$\frac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0.$$
    So **Q is necessary**.

    **P (trim / balance at positive $\alpha$):** In the linear range, $C_{M,\mathrm{cg}}(\alpha)\approx C_{M,0}+C_{M_\alpha}\,\alpha$ with $C_{M_\alpha}=\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}$. Trim satisfies $C_{M,\mathrm{cg}}(\alpha_{\mathrm{trim}})=0$, hence
    $$\alpha_{\mathrm{trim}}=-\frac{C_{M,0}}{C_{M_\alpha}}.$$
    If $C_{M_\alpha}<0$ (stable) and we want $\alpha_{\mathrm{trim}}>0$ for normal positive-lift flight, then $C_{M,0}>0$. The stem ties “at zero lift” to the constant term in the linear model, so **P is necessary** for the usual trim-at-positive-$\alpha$ interpretation.

    **R:** Contradicts **P**; not required.

    **S:** For normal attached flow below stall, the lift curve slope satisfies $\dfrac{dC_L}{d\alpha_a}>0$, not negative. **S is false.**

    Therefore only **P** and **Q** are necessary → option **C**.
    """
).strip()

NEW_STEP_BY_STEP = [
    r"Identify **Q**: static stability requires a restoring pitching-moment response — stick-fixed that is $\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$.",
    r"Identify **P**: with linearization $C_{M,\mathrm{cg}}\approx C_{M,0}+C_{M_\alpha}\alpha$ and stability $C_{M_\alpha}<0$, trim at $\alpha_{\mathrm{trim}}>0$ needs $C_{M,0}>0$ (consistent with “at zero lift” in the usual small-angle / linear-coefficient wording).",
    r"Eliminate **R**: it requires $C_{M,0}<0$, which conflicts with the stable trim-at-positive-$\alpha$ sign requirement above.",
    r"Eliminate **S**: slope $\dfrac{dC_L}{d\alpha_a}$ is positive for a normal wing below stall.",
    r"Pick the option that lists only **P** and **Q**.",
    r"Answer: **C** ($P$ and $Q$ only).",
]

NEW_FORMULAS_USED = [
    r"$C_{M,\mathrm{cg}}(\alpha)\approx C_{M,0}+C_{M_\alpha}\,\alpha,\quad C_{M_\alpha}=\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}$",
    r"$\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$ (longitudinal static stability, stick-fixed)",
    r"$\alpha_{\mathrm{trim}}=-\dfrac{C_{M,0}}{C_{M_\alpha}}$ (trim from linear pitching-moment model)",
    r"$\dfrac{dC_L}{d\alpha_a}>0$ (typical lift curve below stall)",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Longitudinal static stability (stick-fixed)",
        "type": "equation",
        "formula": r"$\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$",
        "relevance": r"Negative slope of $C_{M,\mathrm{cg}}$ vs. $\alpha_a$ gives a restoring pitch response (statement **Q**).",
        "conditions": ["Small perturbations; linear aerodynamic regime; conventional sign conventions about CG/ac reference."],
    },
    {
        "name": "Trim with linear pitching-moment model",
        "type": "equation",
        "formula": r"$\alpha_{\mathrm{trim}}=-\dfrac{C_{M,0}}{C_{M_\alpha}}$",
        "relevance": r"If $C_{M_\alpha}<0$, a positive $C_{M,0}$ is needed for $\alpha_{\mathrm{trim}}>0$ (statement **P** in the usual interpretation).",
        "conditions": [
            r"Linear $C_{M}$ vs. $\alpha$; stick-fixed; desire trim at positive $\alpha$ for normal flight."
        ],
    },
    {
        "name": "Lift curve slope (normal operating range)",
        "type": "principle",
        "formula": r"$\dfrac{dC_L}{d\alpha_a}>0$",
        "relevance": r"Rejects **S**, which incorrectly requires a negative $C_L$ vs. $\alpha_a$ slope.",
        "conditions": ["Below stall; conventional wing in attached flow."],
    },
]

NEW_HINTS = [
    r"Stability: look for the sign of $\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}$ (must be $<0$ for static stability).",
    r"Trim at positive $\alpha$ with $C_{M_\alpha}<0$ forces $C_{M,0}>0$ when using $C_{M}\approx C_{M,0}+C_{M_\alpha}\alpha$.",
    r"Do not confuse moment stability with lift curve slope: $\dfrac{dC_L}{d\alpha_a}$ is usually positive below stall.",
    r"**R** contradicts **P** for the same “zero-lift / $C_{M,0}$ sign” interpretation.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "definition",
        "front": r"Stick-fixed longitudinal static stability criterion (in $C_{M,\mathrm{cg}}$ vs. $\alpha_a$)?",
        "back": r"$\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$: an increase in $\alpha_a$ must produce a nose-down pitching-moment tendency (restoring).",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "definition",
        "front": r"In $C_{M,\mathrm{cg}}\approx C_{M,0}+C_{M_\alpha}\alpha$, why is $C_{M,0}>0$ often required with $C_{M_\alpha}<0$?",
        "back": r"Trim: $\alpha_{\mathrm{trim}}=-C_{M,0}/C_{M_\alpha}$. If $C_{M_\alpha}<0$, then $C_{M,0}>0$ gives $\alpha_{\mathrm{trim}}>0$.",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Typical sign of $\dfrac{dC_L}{d\alpha_a}$ below stall?",
        "back": r"Positive: lift increases with angle of attack before stall.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "concept_recall",
        "front": "Static vs. dynamic stability?",
        "back": "Static: initial tendency to return to equilibrium after a disturbance. Dynamic: character of the subsequent motion (damping, oscillation, divergence).",
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Slope negative for stability",
        "concept": r"$\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$",
        "effectiveness": "high",
        "context": "Longitudinal static stability quick check",
    },
    {
        "mnemonic": r"Trim fraction: $\alpha_{\mathrm{trim}}=-C_{M,0}/C_{M_\alpha}$",
        "concept": r"If $C_{M_\alpha}<0$, need $C_{M,0}>0$ for $\alpha_{\mathrm{trim}}>0$",
        "effectiveness": "high",
        "context": "Sign reasoning for statement **P**",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Confusing static stability with dynamic stability.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrong sign rules or irrelevant reasoning about oscillations.",
        "how_to_avoid": "Static = initial restoring tendency; dynamic = how the motion evolves in time.",
        "why_students_make_it": "Both words contain “stability” but gates different tests.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Using $\dfrac{dC_L}{d\alpha_a}<0$ as a stability requirement.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Selecting options that include **S**.",
        "how_to_avoid": r"Stability is tied to $\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}$; lift curve slope is usually $>0$ below stall.",
        "why_students_make_it": r"Mixing “more lift with $\alpha$” with “restoring moment”.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Forgetting the trim sign link between $C_{M,0}$ and $C_{M_\alpha}$ when $\alpha_{\mathrm{trim}}>0$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Incorrectly accepts **R** or rejects **P**.",
        "how_to_avoid": r"Use $\alpha_{\mathrm{trim}}=-C_{M,0}/C_{M_\alpha}$ with $C_{M_\alpha}<0$.",
        "why_students_make_it": "Recalls stability slope but not the intercept/trim argument.",
    },
    {
        "type": "Conceptual",
        "mistake": "Overcomplicating with stick-free or control-system arguments under a stick-fixed stem.",
        "severity": "Low",
        "frequency": "occasional",
        "consequence": "Time loss; occasional wrong elimination.",
        "how_to_avoid": r"Stick-fixed → use rigid elevator ($C_{M}$ vs. $\alpha$) static criteria only.",
        "why_students_make_it": "Advanced courses blend stick-fixed and stick-free concepts.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Lock **Q** first ($\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$). Then trim/sign reasoning for **P** via $C_{M}\approx C_{M,0}+C_{M_\alpha}\alpha$. Kill **S** with $\dfrac{dC_L}{d\alpha_a}>0$.",
    "guessing_heuristic": r"Any option containing **S** is suspect; **R** opposes **P** on $C_{M,0}$ sign.",
    "time_management": r"60–90 s if sign rules are fluent; otherwise ~2 min — do not over-derive.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Needs both stability slope ($C_{M_\alpha}<0$) and trim/sign reasoning for $C_{M,0}$.",
    r"Statement **S** is a deliberate trap using $\dfrac{dC_L}{d\alpha_a}$.",
    "Multiple Boolean statements → combination elimination under time pressure.",
]

NEW_ALT_METHODS = [
    {
        "name": r"Graphical ($C_{M,\mathrm{cg}}$ vs. $\alpha_a$) sketch",
        "description": (
            r"Sketch $C_{M,\mathrm{cg}}(\alpha_a)$: stability means negative slope. "
            r"For $\alpha_{\mathrm{trim}}>0$ with negative slope, the intercept $C_{M,0}$ at $\alpha_a=0$ is positive."
        ),
        "pros_cons": "Pros: fast sign checks. Cons: must keep axis/sign conventions consistent.",
        "when_to_use": "If algebraic trim formula is not immediate.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2014 AE Q54 longitudinal static stability",
    "stick-fixed trim C_M0 C_M_alpha",
    "dCm/dalpha negative stability",
    "dCL/dalpha positive lift curve",
    "longitudinal balance criterion",
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
        r"Classify statements $\Rightarrow$ apply $\dfrac{dC_{M,\mathrm{cg}}}{d\alpha_a}<0$ "
        r"$\Rightarrow$ trim/sign with $C_{M,0},\,C_{M_\alpha}$ $\Rightarrow$ reject **R**, **S** $\Rightarrow$ **C**"
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

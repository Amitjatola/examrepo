"""
Fix GATE_2009_AE_Q30 LaTeX across stem, options, tier-1 (reasoning, steps, formulas, hints, sbs), tier-2 (flashcards, mnemonics).

Body-axis wind triangle: $u=V\\cos\\beta\\cos\\alpha$, $v=V\\sin\\beta$, $w=V\\cos\\beta\\sin\\alpha$ (option D).

Usage (from backend/):
  ./venv/bin/python patch_gate_2009_ae_q30_latex.py
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2009_AE_Q30"

NEW_QUESTION_TEXT = (
    "The velocity vector of an aircraft along its body-fixed axis is given by V = {u, v, w}ᵀ. "
    "If V is the magnitude of V, α is the angle of attack and β is the angle of sideslip, "
    "which of the following set of relations is correct?"
)

NEW_QUESTION_TEXT_LATEX = (
    "The velocity vector of an aircraft along its body-fixed axis is "
    "$\\vec{V}=\\begin{Bmatrix} u\\\\ v\\\\ w\\end{Bmatrix}$. "
    "If $V=|\\vec{V}|$, $\\alpha$ is the angle of attack and $\\beta$ is the sideslip angle, "
    "which of the following set of relations is correct?"
)

NEW_OPTIONS = {
    "A": r"$u=V\sin\beta\cos\alpha,\quad v=V\sin\beta,\quad w=V\cos\beta\sin\alpha$",
    "B": r"$u=V\cos\beta\cos\alpha,\quad v=V\cos\beta,\quad w=V\cos\beta\sin\alpha$",
    "C": r"$u=V\cos\beta\cos\alpha,\quad v=V\sin\beta,\quad w=V\sin\beta\sin\alpha$",
    "D": r"$u=V\cos\beta\cos\alpha,\quad v=V\sin\beta,\quad w=V\cos\beta\sin\alpha$",
}

NEW_REASONING = (
    "In body axes, $|\\vec{V}|=V=\\sqrt{u^2+v^2+w^2}$. The sideslip angle $\\beta$ is the angle between "
    "$\\vec{V}$ and the body $xz$-plane, so the lateral component is\n"
    "$$v=V\\sin\\beta.$$\n"
    "The projection onto the $xz$-plane has magnitude\n"
    "$$V_{xz}=V\\cos\\beta.$$\n"
    "The angle of attack $\\alpha$ lies in the $xz$-plane between the $x$-axis and this projection, hence\n"
    "$$u=V_{xz}\\cos\\alpha=V\\cos\\beta\\cos\\alpha,\\qquad "
    "w=V_{xz}\\sin\\alpha=V\\cos\\beta\\sin\\alpha.$$\n"
    "Together: $u=V\\cos\\beta\\cos\\alpha$, $v=V\\sin\\beta$, $w=V\\cos\\beta\\sin\\alpha$, which is **option D**."
)

NEW_HINTS = [
    "First use $\\beta$ to split $V$ into **$v$** and the **$xz$ projection** $V_{xz}=V\\cos\\beta$.",
    "Then use $\\alpha$ **in the $xz$ plane** to get $u=V_{xz}\\cos\\alpha$ and $w=V_{xz}\\sin\\alpha$.",
    "Check $v$: it must be $V\\sin\\beta$ (not $V\\cos\\beta$) for standard sideslip definition $\\sin\\beta=v/V$.",
]

NEW_STEP_BY_STEP = [
    (
        "Step 1: Represent $\\vec{V}=[u,v,w]^\\mathsf{T}$ with $V=|\\vec{V}|=\\sqrt{u^2+v^2+w^2}$; "
        "$\\alpha$ and $\\beta$ are wind angles in body axes."
    ),
    (
        "Step 2: **Sideslip:** $\\beta$ is measured from the $xz$-plane, so $v=V\\sin\\beta$ and "
        "$V_{xz}=V\\cos\\beta$."
    ),
    (
        "Step 3: **Angle of attack:** in the $xz$-plane, $u=V_{xz}\\cos\\alpha$ and $w=V_{xz}\\sin\\alpha$."
    ),
    (
        "Step 4: **Substitute** $V_{xz}$: $u=V\\cos\\beta\\cos\\alpha$, $w=V\\cos\\beta\\sin\\alpha$."
    ),
    ("Step 5: **Assemble** $u,v,w$ and compare with options — **D** matches."),
]

NEW_FORMULAS_USED = [
    r"$V=\sqrt{u^2+v^2+w^2}$",
    r"$v=V\sin\beta,\quad V_{xz}=V\cos\beta$",
    r"$u=V_{xz}\cos\alpha,\quad w=V_{xz}\sin\alpha$",
    r"$u=V\cos\beta\cos\alpha,\quad v=V\sin\beta,\quad w=V\cos\beta\sin\alpha$",
    r"$\tan\alpha=w/u$ (when $u\neq0$)",
]

NEW_SOLUTION_PATH = (
    "$\\beta\\Rightarrow v,\\ V_{xz}$; $\\alpha\\Rightarrow u,w$ in $xz$; match **D**."
)

NEW_KEY_INSIGHTS = [
    "$\\beta$ controls the split between lateral $v$ and the $xz$ projection; $\\alpha$ splits that projection into $u$ and $w$.",
    "A frequent trap is swapping $\\sin\\beta$ and $\\cos\\beta$ for $v$.",
]

NEW_DIFFICULTY_FACTORS: List[str] = [
    "Requires correct 3-D sequencing: **sideslip** projection first, then **angle of attack** in the $xz$-plane.",
    "Must know standard definitions $\\sin\\beta=v/V$ and how $\\alpha$ applies to the $xz$ projection.",
    "Easy to confuse option **B** ($v=V\\cos\\beta$) if the $\\beta$ geometry is misremembered.",
]

NEW_FLASHCARDS: List[Dict[str, Any]] = [
    {
        "card_type": "formula_recall",
        "front": (
            "Body-axis components $(u,v,w)$ in terms of $V$, $\\alpha$, and $\\beta$ (standard wind-angle definitions)?"
        ),
        "back": (
            "$u=V\\cos\\beta\\cos\\alpha$,\\quad $v=V\\sin\\beta$,\\quad $w=V\\cos\\beta\\sin\\alpha$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "definition",
        "front": "Define sideslip $\\beta$ from $\\vec{V}$ in body axes.",
        "back": (
            "$\\beta$ is the angle between $\\vec{V}$ and the body $xz$-plane; equivalently "
            "$\\sin\\beta=v/V$ with $v$ the body-$y$ component."
        ),
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": "Relate $V_{xz}$ to $V$ and $\\beta$; then $u,w$ to $V_{xz}$ and $\\alpha$.",
        "back": (
            "$V_{xz}=V\\cos\\beta$;\\quad $u=V_{xz}\\cos\\alpha$,\\quad $w=V_{xz}\\sin\\alpha$."
        ),
        "difficulty": "hard",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": "Typical trap when projecting with $\\alpha$ and $\\beta$?",
        "back": (
            "Using $v=V\\cos\\beta$ instead of $v=V\\sin\\beta$, or applying $\\alpha$ before forming the $xz$ projection. "
            "Order: $\\beta\\to(v,V_{xz})$, then $\\alpha\\to(u,w)$."
        ),
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "application",
        "front": "If $V=100\\ \\mathrm{m/s}$, $\\alpha=10^\\circ$, $\\beta=5^\\circ$, estimate $u,v,w$.",
        "back": (
            "$u=V\\cos\\beta\\cos\\alpha\\approx 98.1\\ \\mathrm{m/s}$, "
            "$v=V\\sin\\beta\\approx 8.72\\ \\mathrm{m/s}$, "
            "$w=V\\cos\\beta\\sin\\alpha\\approx 17.3\\ \\mathrm{m/s}$."
        ),
        "difficulty": "hard",
        "time_limit_seconds": 60,
    },
]

NEW_MNEMONICS: List[Dict[str, Any]] = [
    {
        "mnemonic": (
            "**Beta → sideways:** $\\sin\\beta=v/V$ gives $v$ and leaves the **$xz$** patch $V_{xz}=V\\cos\\beta$. "
            "**Alpha → in-plane:** splits $V_{xz}$ into $u$ and $w$."
        ),
        "concept": "Resolve $\\vec{V}$: first $\\beta$ (out of $xz$), then $\\alpha$ (inside $xz$).",
        "effectiveness": "high",
        "context": "Body-axis $(u,v,w)$ from wind angles $(\\alpha,\\beta)$.",
    },
    {
        "mnemonic": "**Cos-cos / sin / cos-sin:** $u$ has two cosines, $v$ a single sine, $w$ cosine-sine.",
        "concept": "Pattern for option D: $u=V\\cos\\beta\\cos\\alpha$, $v=V\\sin\\beta$, $w=V\\cos\\beta\\sin\\alpha$.",
        "effectiveness": "medium",
        "context": "Quick MCQ check after derivation.",
    },
]


def patch_tier_1(tier_1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t1 = deepcopy(tier_1 or {})

    av = t1.setdefault("answer_validation", {})
    av["reasoning"] = NEW_REASONING

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

    return t1


def patch_tier_2(tier_2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    t2 = deepcopy(tier_2 or {})
    t2["flashcards"] = NEW_FLASHCARDS
    t2["mnemonics_memory_aids"] = NEW_MNEMONICS
    return t2


async def main() -> None:
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                "SELECT tier_1_core_research, tier_2_student_learning FROM questions WHERE question_id = :qid"
            ),
            {"qid": PUBLIC_ID},
        )
        row = res.fetchone()
        if not row:
            raise SystemExit(f"Question {PUBLIC_ID} not found")

        new_t1 = patch_tier_1(row[0])
        new_t2 = patch_tier_2(row[1])

        await conn.execute(
            text(
                "UPDATE questions SET "
                "question_text = :qt, "
                "question_text_latex = :qtl, "
                "options = CAST(:opts AS jsonb), "
                "tier_1_core_research = CAST(:t1 AS jsonb), "
                "tier_2_student_learning = CAST(:t2 AS jsonb), "
                "updated_at = :updated_at "
                "WHERE question_id = :qid"
            ),
            {
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(new_t1),
                "t2": json.dumps(new_t2),
                "updated_at": datetime.utcnow(),
                "qid": PUBLIC_ID,
            },
        )

    print(f"Patched {PUBLIC_ID}: stem/options/tier-1/tier-2 LaTeX")


if __name__ == "__main__":
    asyncio.run(main())

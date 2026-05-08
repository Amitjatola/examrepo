import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2016_AE_Q52"

NEW_QUESTION_TEXT_PLAIN = (
    "The Dutch roll motion of an aircraft is described by: "
    "[Delta beta_dot; Delta r_dot] = [-0.26 -1; 4.49 -0.76] [Delta beta; Delta r]. "
    "The undamped natural frequency (rad/s) and damping ratio for the Dutch roll motion, in that order, are:"
)

NEW_QUESTION_TEXT_LATEX = (
    r"The Dutch roll motion of an aircraft is described by"
    r" $$\begin{bmatrix}\Delta\dot{\beta}\\\Delta\dot{r}\end{bmatrix}="
    r"\begin{bmatrix}-0.26 & -1\\4.49 & -0.76\end{bmatrix}"
    r"\begin{bmatrix}\Delta\beta\\\Delta r\end{bmatrix}.$$"
    r" The undamped natural frequency (rad/s) and damping ratio for the Dutch roll motion, "
    r"in that order, are:"
)

NEW_OPTIONS = {
    "A": "$4.68,\ 1.02$",
    "B": "$4.49,\ 1.02$",
    "C": "$2.165,\ 0.235$",
    "D": "$2.165,\ 1.02$",
}

NEW_REASONING = (
    r"Write the system as $\dot{\mathbf{x}}=A\mathbf{x}$ with "
    r"$\mathbf{x}=\begin{bmatrix}\Delta\beta & \Delta r\end{bmatrix}^\mathsf{T}$ and "
    r"$A=\begin{bmatrix}-0.26 & -1\\4.49 & -0.76\end{bmatrix}$."
    "\n\n"
    r"Characteristic equation from $\det(\lambda I-A)=0$:"
    "\n"
    r"$\det\!\begin{bmatrix}\lambda+0.26 & 1\\-4.49 & \lambda+0.76\end{bmatrix}=0$"
    r"$\Rightarrow (\lambda+0.26)(\lambda+0.76)+4.49=0$"
    r"$\Rightarrow \lambda^2+1.02\lambda+4.6876=0$."
    "\n\n"
    r"Compare with second-order form "
    r"$\lambda^2+2\zeta\omega_n\lambda+\omega_n^2=0$:"
    "\n"
    r"$\omega_n^2=4.6876\Rightarrow\omega_n=\sqrt{4.6876}\approx2.165\ \mathrm{rad/s}$,"
    "\n"
    r"$2\zeta\omega_n=1.02\Rightarrow\zeta=\dfrac{1.02}{2\times2.165}\approx0.235$."
    "\n\n"
    r"Hence the required pair is $(\omega_n,\zeta)=(2.165,\ 0.235)$, i.e. option C."
)

NEW_STEP_BY_STEP = [
    r"Identify the state matrix: $A=\begin{bmatrix}-0.26 & -1\\4.49 & -0.76\end{bmatrix}$ from $\dot{\mathbf{x}}=A\mathbf{x}$.",
    r"Form characteristic equation using $\det(\lambda I-A)=0$.",
    r"Compute determinant: $(\lambda+0.26)(\lambda+0.76)+4.49=0$.",
    r"Expand: $\lambda^2+1.02\lambda+4.6876=0$.",
    r"Match with $\lambda^2+2\zeta\omega_n\lambda+\omega_n^2=0$.",
    r"From constant term: $\omega_n=\sqrt{4.6876}\approx2.165\ \mathrm{rad/s}$.",
    r"From linear term: $\zeta=\dfrac{1.02}{2\omega_n}=\dfrac{1.02}{2\times2.165}\approx0.235$.",
    r"Therefore $(\omega_n,\zeta)=(2.165,0.235)$.",
]

NEW_FORMULAS_USED = [
    r"$\det(\lambda I-A)=0$",
    r"$\lambda^2+2\zeta\omega_n\lambda+\omega_n^2=0$",
    r"$\omega_n=\sqrt{\omega_n^2}$",
    r"$\zeta=\dfrac{\text{coefficient of }\lambda}{2\omega_n}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Characteristic equation from state matrix",
        "type": "equation",
        "formula": r"$\det(\lambda I-A)=0$",
        "relevance": "Gives system poles/eigenvalues directly from state-space form.",
        "conditions": [r"Linear time-invariant system $\dot{\mathbf{x}}=A\mathbf{x}$."],
    },
    {
        "name": "Standard second-order polynomial",
        "type": "equation",
        "formula": r"$\lambda^2+2\zeta\omega_n\lambda+\omega_n^2=0$",
        "relevance": "Maps polynomial coefficients to natural frequency and damping ratio.",
        "conditions": ["Oscillatory second-order mode representation."],
    },
    {
        "name": "Natural frequency extraction",
        "type": "formula",
        "formula": r"$\omega_n=\sqrt{b}$ for $\lambda^2+a\lambda+b=0$",
        "relevance": "Fast extraction of $\omega_n$ after polynomial expansion.",
        "conditions": ["Compare with standard second-order form."],
    },
    {
        "name": "Damping ratio extraction",
        "type": "formula",
        "formula": r"$\zeta=\dfrac{a}{2\omega_n}$ for $\lambda^2+a\lambda+b=0$",
        "relevance": "Direct computation of $\zeta$ from linear coefficient and $\omega_n$.",
        "conditions": ["Use same polynomial normalization (leading coefficient = 1)."],
    },
]

NEW_HINTS = [
    r"Start by forming $\det(\lambda I-A)=0$ from the given 2x2 state matrix.",
    r"For a 2x2 matrix, be careful with determinant signs: $ad-bc$.",
    r"After expansion, match with $\lambda^2+2\zeta\omega_n\lambda+\omega_n^2=0$ coefficient-by-coefficient.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "How do you form the characteristic equation from state matrix $A$?",
        "back": r"Use $\det(\lambda I-A)=0$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "formula_recall",
        "front": r"For $\lambda^2+a\lambda+b=0$, formulas for $\omega_n$ and $\zeta$?",
        "back": r"$\omega_n=\sqrt{b}$, $\zeta=\dfrac{a}{2\omega_n}$.",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": "Given $\lambda^2+1.02\lambda+4.6876=0$, find $(\omega_n,\zeta)$.",
        "back": r"$\omega_n\approx2.165\ \mathrm{rad/s}$ and $\zeta\approx0.235$.",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
    {
        "card_type": "mistake_prevention",
        "front": "What mistake gives $\zeta\approx0.471$ instead of $0.235$?",
        "back": r"Forgetting the factor 2 in $2\zeta\omega_n$; using $\zeta=a/\omega_n$ instead of $a/(2\omega_n)$.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "SOD: Square-root constant for Omega_n, Divide a by 2Omega_n",
        "concept": r"From $\lambda^2+a\lambda+b=0$ get $\omega_n$ and $\zeta$ quickly",
        "effectiveness": "high",
        "context": "Second-order coefficient mapping",
    }
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Calculation",
        "mistake": r"Sign error in determinant expansion of $\lambda I-A$.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Wrong characteristic polynomial and wrong final option.",
        "how_to_avoid": r"Write matrix explicitly and apply $ad-bc$ carefully.",
        "why_students_make_it": "Rushed algebra with mixed signs.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Using $a=\zeta\omega_n$ instead of $a=2\zeta\omega_n$.",
        "severity": "Medium",
        "frequency": "common",
        "consequence": r"Damping ratio approximately doubles (e.g., 0.471).",
        "how_to_avoid": r"Always rewrite standard form $\lambda^2+2\zeta\omega_n\lambda+\omega_n^2=0$ before comparing.",
        "why_students_make_it": "Misremembered standard second-order form.",
    },
    {
        "type": "Conceptual",
        "mistake": r"Taking $\omega_n=\sqrt{a}$ instead of $\sqrt{b}$ for $\lambda^2+a\lambda+b=0$.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Incorrect natural frequency and wrong elimination among options.",
        "how_to_avoid": r"Map constant term to $\omega_n^2$ only.",
        "why_students_make_it": "Coefficient-position confusion.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Compute determinant polynomial first, then map to $\omega_n^2$ and $2\zeta\omega_n$.",
    "guessing_heuristic": r"If constant term is about 4.69, $\omega_n\approx\sqrt{4.69}\approx2.17$, so eliminate high-frequency options quickly.",
    "time_management": "2-3 minutes; spend most care on determinant signs and final divide-by-2 step.",
}

NEW_DIFFICULTY_FACTORS = [
    "Requires correct 2x2 determinant with sign care.",
    "Requires precise coefficient mapping to second-order standard form.",
    "Numerical arithmetic can introduce small but option-changing errors.",
]

NEW_ALT_METHODS = [
    {
        "name": "Direct eigenvalue formula for 2x2 matrix",
        "description": r"Use $\lambda=\dfrac{\operatorname{tr}(A)}{2}\pm\dfrac{1}{2}\sqrt{\operatorname{tr}(A)^2-4\det(A)}$, then map $\sigma\pm j\omega_d$ to $\omega_n=\sqrt{\sigma^2+\omega_d^2}$ and $\zeta=-\sigma/\omega_n$.",
        "pros_cons": "Pros: compact and software-friendly. Cons: more complex arithmetic by hand in exam.",
        "when_to_use": "Verification or calculator-assisted workflows.",
    }
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2016 AE Q52 Dutch roll",
    "state matrix to damping ratio",
    "characteristic equation 2x2 aircraft dynamics",
    "omega_n zeta from eigenvalues",
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

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = 8
    sbs["solution_path"] = (
        r"Form $\det(\lambda I-A)$ $\Rightarrow$ expand polynomial $\Rightarrow$ compare with "
        r"$\lambda^2+2\zeta\omega_n\lambda+\omega_n^2$ $\Rightarrow$ compute $\omega_n,\zeta$"
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
    c["Control Systems"] = "Pole locations from state matrix determine oscillation frequency and damping, identical to standard second-order control interpretation."
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

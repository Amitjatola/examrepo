import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2019_AE_Q2"

NEW_QUESTION_TEXT_PLAIN = (
    "Vector b is obtained by rotating a = i-hat + j-hat by 90° about k-hat, where i-hat, "
    "j-hat and k-hat are unit vectors along the x, y and z axes, respectively. b is given by"
)

NEW_QUESTION_TEXT_LATEX = (
    r"Vector $\vec{b}$ is obtained by rotating $\vec{a}=\hat{\mathbf{i}}+\hat{\mathbf{j}}$ "
    r"by $90^\circ$ about $\hat{\mathbf{k}}$, where $\hat{\mathbf{i}}$, $\hat{\mathbf{j}}$ and "
    r"$\hat{\mathbf{k}}$ are unit vectors along the $x$, $y$ and $z$ axes, respectively. "
    r"$\vec{b}$ is given by"
)

NEW_OPTIONS = {
    "A": r"$\hat{\mathbf{i}}-\hat{\mathbf{j}}$",
    "B": r"$-\hat{\mathbf{i}}+\hat{\mathbf{j}}$",
    "C": r"$\hat{\mathbf{i}}+\hat{\mathbf{j}}$",
    "D": r"$-\hat{\mathbf{i}}-\hat{\mathbf{j}}$",
}

NEW_REASONING = (
    r"Write the initial vector as $\vec{a}=(1,1,0)^\mathsf{T}$ in Cartesian components. "
    r"A positive $90^\circ$ rotation about $\hat{\mathbf{k}}$ follows the right-hand rule "
    r"(counter-clockwise in the $x$-$y$ plane)."
    "\n\n"
    r"Use the standard $z$-axis rotation matrix:"
    "\n"
    r"$R_z(\theta)=\begin{bmatrix}"
    r"\cos\theta & -\sin\theta & 0\\"
    r"\sin\theta & \cos\theta & 0\\"
    r"0 & 0 & 1"
    r"\end{bmatrix}$."
    "\n"
    r"For $\theta=90^\circ$,"
    "\n"
    r"$R_z(90^\circ)=\begin{bmatrix}0 & -1 & 0\\1 & 0 & 0\\0 & 0 & 1\end{bmatrix}$."
    "\n\n"
    r"Then"
    "\n"
    r"$\vec{b}=R_z(90^\circ)\vec{a}="
    r"\begin{bmatrix}0 & -1 & 0\\1 & 0 & 0\\0 & 0 & 1\end{bmatrix}"
    r"\begin{bmatrix}1\\1\\0\end{bmatrix}="
    r"\begin{bmatrix}-1\\1\\0\end{bmatrix}$."
    "\n"
    r"Hence $\vec{b}=-\hat{\mathbf{i}}+\hat{\mathbf{j}}$, i.e. option B."
)

NEW_STEP_BY_STEP = [
    r"Represent the vector in components: $\vec{a}=\hat{\mathbf{i}}+\hat{\mathbf{j}}=(1,1,0)^\mathsf{T}$.",
    r"A positive $90^\circ$ rotation about $\hat{\mathbf{k}}$ is counter-clockwise in the $x$-$y$ plane.",
    r"Use $R_z(\theta)=\begin{bmatrix}\cos\theta & -\sin\theta & 0\\\sin\theta & \cos\theta & 0\\0 & 0 & 1\end{bmatrix}$.",
    r"Substitute $\theta=90^\circ$ to get $R_z(90^\circ)=\begin{bmatrix}0 & -1 & 0\\1 & 0 & 0\\0 & 0 & 1\end{bmatrix}$.",
    r"Multiply: $\vec{b}=R_z(90^\circ)\vec{a}=\begin{bmatrix}-1\\1\\0\end{bmatrix}$.",
    r"Convert back to unit-vector form: $\vec{b}=-\hat{\mathbf{i}}+\hat{\mathbf{j}}$.",
]

NEW_FORMULAS_USED = [
    r"$R_z(\theta)=\begin{bmatrix}\cos\theta & -\sin\theta & 0\\\sin\theta & \cos\theta & 0\\0 & 0 & 1\end{bmatrix}$",
    r"$\vec{b}=R_z(\theta)\vec{a}$",
    r"$\cos 90^\circ=0,\ \sin 90^\circ=1$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Rotation matrix about z-axis",
        "type": "equation",
        "formula": r"$R_z(\theta)=\begin{bmatrix}\cos\theta & -\sin\theta & 0\\\sin\theta & \cos\theta & 0\\0 & 0 & 1\end{bmatrix}$",
        "relevance": "Core transformation to rotate vectors about z-axis.",
        "conditions": ["Positive angle uses right-hand rule convention."],
    },
    {
        "name": "Vector rotation relation",
        "type": "equation",
        "formula": r"$\vec{b}=R_z(\theta)\vec{a}$",
        "relevance": "Applies matrix transformation to obtain rotated vector.",
        "conditions": ["Use consistent coordinate basis and column-vector convention."],
    },
]

NEW_HINTS = [
    r"Treat $\hat{\mathbf{k}}$ as the z-axis and rotate in the $x$-$y$ plane.",
    r"For positive $90^\circ$: $\hat{\mathbf{i}}\to\hat{\mathbf{j}}$ and $\hat{\mathbf{j}}\to-\hat{\mathbf{i}}$.",
    r"You can solve either by matrix multiplication or by rotating basis vectors directly.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "Standard matrix for rotation about z-axis by angle $\theta$?",
        "back": r"$R_z(\theta)=\begin{bmatrix}\cos\theta & -\sin\theta & 0\\\sin\theta & \cos\theta & 0\\0 & 0 & 1\end{bmatrix}$",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": r"What is $(1,1,0)^\mathsf{T}$ rotated by $+90^\circ$ about z-axis?",
        "back": r"$(-1,1,0)^\mathsf{T}$, i.e. $-\hat{\mathbf{i}}+\hat{\mathbf{j}}$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Where do sine signs go in $R_z(\theta)$?",
        "back": r"Top-right is $-\sin\theta$, bottom-left is $+\sin\theta$.",
        "difficulty": "easy",
        "time_limit_seconds": 15,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": r"z-rotate block: C -S / S C",
        "concept": r"$R_z(\theta)$ sign pattern",
        "effectiveness": "high",
        "context": "Fast recall for 3D elementary rotations",
    },
    {
        "mnemonic": r"plus ninety on z: $\hat{\mathbf{i}}\to\hat{\mathbf{j}}$",
        "concept": "Right-hand-rule direction",
        "effectiveness": "medium",
        "context": "Quick geometric check",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": "Using rotation matrix about x/y axis instead of z-axis.",
        "severity": "High",
        "frequency": "common",
        "consequence": "Incorrect vector direction/components.",
        "how_to_avoid": r"Map $\hat{\mathbf{k}}$ to z-axis before writing matrix.",
        "why_students_make_it": "Axis misread from statement.",
    },
    {
        "type": "Calculation",
        "mistake": "Swapping signs of sine terms in $R_z(\theta)$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": "Gives opposite/incorrect rotation result.",
        "how_to_avoid": r"Remember pattern $\begin{bmatrix}C & -S\\S & C\end{bmatrix}$ in x-y block.",
        "why_students_make_it": "Matrix memorization error.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Use direct basis rotation for 90°: $\hat{\mathbf{i}}\to\hat{\mathbf{j}}$, $\hat{\mathbf{j}}\to-\hat{\mathbf{i}}$.",
    "guessing_heuristic": r"Result should be $(-1,1)$ in x-y if rotation is +90° CCW.",
    "time_management": "30-60 seconds; do not overcompute.",
}

NEW_DIFFICULTY_FACTORS = [
    "Single standard formula application.",
    "Common sign-convention trap in rotation matrix.",
]

NEW_ALT_METHODS = [
    {
        "name": "Basis-vector geometric method",
        "description": r"Rotate $\hat{\mathbf{i}}$ and $\hat{\mathbf{j}}$ individually by $+90^\circ$ about z, then add results.",
        "pros_cons": "Pros: fastest for right-angle cases. Cons: less general for arbitrary angles.",
        "when_to_use": "When angle is 90°/180° and vector uses standard basis.",
    },
    {
        "name": "Complex-plane method (x-y components)",
        "description": r"Map $(x,y)$ to $z=x+iy$; multiply by $e^{i\theta}$ with $\theta=90^\circ$.",
        "pros_cons": "Pros: compact in 2D. Cons: not direct for full 3D arbitrary-axis rotations.",
        "when_to_use": "Quick checks for planar rotations.",
    },
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2019 AE Q2 vector rotation",
    "rotation about k hat",
    "Rz theta matrix sign convention",
    "90 degree rotation i+j",
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

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    da = o.setdefault("difficulty_analysis", {})
    da["difficulty_factors"] = NEW_DIFFICULTY_FACTORS

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = 6
    sbs["solution_path"] = (
        r"Write $\vec{a}$ in components $\Rightarrow$ choose $R_z(90^\circ)$ "
        r"$\Rightarrow$ multiply $R_z\vec{a}$ $\Rightarrow$ convert back to unit-vector form"
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
    c["Linear Algebra"] = "Rotation matrices are orthogonal transformations preserving vector norms and angles."
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

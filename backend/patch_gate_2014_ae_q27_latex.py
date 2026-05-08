"""
Fix LaTeX / formatting for GATE_2014_AE_Q27 (Fourier series / Leibniz for π/4).
"""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.core.database import engine

PUBLIC_ID = "GATE_2014_AE_Q27"

NEW_QUESTION_TEXT = (
    "For the periodic function f(x) = -2 on (-π, 0), f(x) = 2 on (0, π), with "
    "f(x + 2π) = f(x), using Fourier series, the sum "
    "s = 1 - 1/3 + 1/5 - 1/7 + … converges to"
)

NEW_QUESTION_TEXT_LATEX = dedent(
    r"""
    For the periodic function
    \[
    f(x) = \begin{cases}
    -2, & -\pi < x < 0 \\
    2, & 0 < x < \pi
    \end{cases},
    \qquad f(x + 2\pi) = f(x),
    \]
    using Fourier series, the sum
    \[
    s = 1 - \frac{1}{3} + \frac{1}{5} - \frac{1}{7} + \cdots
    \]
    converges to
    """
).strip()

NEW_OPTIONS = {
    "A": r"$1$",
    "B": r"$\dfrac{\pi}{3}$",
    "C": r"$\dfrac{\pi}{4}$",
    "D": r"$\dfrac{\pi}{5}$",
}

NEW_REASONING = dedent(
    r"""
    The function satisfies $f(-x) = -f(x)$ on $(-\pi,\pi)$, so $f$ is **odd**. Hence the Fourier series on $[-\pi,\pi]$ has
    $$a_0 = 0,\qquad a_n = 0 \quad (n \ge 1),$$
    and only sine terms remain:
    $$f(x) = \sum_{n=1}^{\infty} b_n \sin(nx).$$

    For an odd function with period $2\pi$,
    $$b_n = \frac{1}{\pi}\int_{-\pi}^{\pi} f(x)\sin(nx)\,dx
    = \frac{2}{\pi}\int_{0}^{\pi} f(x)\sin(nx)\,dx.$$
    On $(0,\pi)$, $f(x)=2$, so
    $$b_n = \frac{4}{\pi}\int_{0}^{\pi} \sin(nx)\,dx
    = \frac{4}{\pi n}\bigl(1 - \cos(n\pi)\bigr)
    = \frac{4}{\pi n}\bigl(1-(-1)^n\bigr).$$
    Thus $b_n = 0$ for even $n$, and for odd $n$,
    $$b_n = \frac{8}{\pi n}.$$

    Therefore (odd harmonics only),
    $$f(x) = \frac{8}{\pi}\sum_{m=0}^{\infty} \frac{\sin\bigl((2m+1)x\bigr)}{2m+1}.$$

    At $x=\frac{\pi}{2}$ the definition gives $f(\pi/2)=2$ (point of continuity). Also
    $$\sin\!\left((2m+1)\frac{\pi}{2}\right) = (-1)^m,$$
    so
    $$2 = \frac{8}{\pi}\sum_{m=0}^{\infty} \frac{(-1)^m}{2m+1}
      = \frac{8}{\pi}\left(1 - \frac13 + \frac15 - \frac17 + \cdots\right)
      = \frac{8}{\pi}\, s.$$
    Hence $s = \dfrac{2\pi}{8} = \dfrac{\pi}{4}$.

    Match with options: **C** ($\pi/4$).
    """
).strip()

NEW_STEPS = [
    r"Confirm odd symmetry: $f(-x) = -f(x)$ on $(-\pi,\pi)$, so $a_0 = a_n = 0$.",
    r"Write sine coefficients: $b_n = \dfrac{2}{\pi}\int_{0}^{\pi} f(x)\sin(nx)\,dx$.",
    r"Substitute $f(x)=2$ on $(0,\pi)$: $b_n = \dfrac{4}{\pi}\int_{0}^{\pi} \sin(nx)\,dx$.",
    r"Integrate: $b_n = \dfrac{4}{\pi n}\bigl(1-\cos(n\pi)\bigr) = \dfrac{4}{\pi n}\bigl(1-(-1)^n\bigr)$.",
    r"Odd $n$ survive: for odd $n$, $b_n = \dfrac{8}{\pi n}$; even $n$ give $b_n=0$.",
    r"Series: $f(x) = \dfrac{8}{\pi}\sum_{m=0}^{\infty} \dfrac{\sin\bigl((2m+1)x\bigr)}{2m+1}$.",
    r"Evaluate at $x=\dfrac{\pi}{2}$: $f(\pi/2)=2$ and $\sin\bigl((2m+1)\pi/2\bigr)=(-1)^m$.",
    r"So $2 = \dfrac{8}{\pi}\, s$ with $s = 1 - \dfrac13 + \dfrac15 - \cdots$, hence $s=\dfrac{\pi}{4}$ (option C).",
]

NEW_FORMULAS_USED = [
    r"$f(x) = \dfrac{a_0}{2} + \sum_{n=1}^{\infty}\bigl(a_n\cos(nx) + b_n\sin(nx)\bigr)$",
    r"$b_n = \dfrac{1}{\pi}\int_{-\pi}^{\pi} f(x)\sin(nx)\,dx$",
    r"$b_n = \dfrac{2}{\pi}\int_{0}^{\pi} f(x)\sin(nx)\,dx$ for odd $f$ on $[-\pi,\pi]$",
    r"$\int \sin(nx)\,dx = -\dfrac{\cos(nx)}{n} + C$",
    r"$\cos(n\pi) = (-1)^n$",
    r"$\sin\!\left((2m+1)\dfrac{\pi}{2}\right) = (-1)^m$",
    r"$1 - \dfrac13 + \dfrac15 - \dfrac17 + \cdots = \dfrac{\pi}{4}$ (Leibniz)",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Fourier sine coefficients for an odd $2\pi$-periodic function",
        "type": "equation",
        "formula": r"$b_n = \dfrac{2}{\pi}\int_{0}^{\pi} f(x)\sin(nx)\,dx$",
        "conditions": r"$f$ odd on $[-\pi,\pi]$, period $2\pi$.",
        "relevance": "Removes $a_0,a_n$ and gives the sine-only expansion used here.",
    },
    {
        "name": "Leibniz series for $\pi/4$",
        "type": "series sum",
        "formula": r"$\sum_{m=0}^{\infty} \dfrac{(-1)^m}{2m+1} = \dfrac{\pi}{4}$",
        "conditions": "Conditionally convergent alternating series.",
        "relevance": "This is exactly the sum $s$ after matching coefficients.",
    },
    {
        "name": "Cosine at integer multiples of $\pi$",
        "type": "identity",
        "formula": r"$\cos(n\pi) = (-1)^n$",
        "conditions": r"$n \in \mathbb{Z}$.",
        "relevance": r"Simplifies $b_n \propto 1-(-1)^n$ to kill even harmonics.",
    },
    {
        "name": "Sine at odd multiples of $\pi/2$",
        "type": "identity",
        "formula": r"$\sin\!\left((2m+1)\dfrac{\pi}{2}\right) = (-1)^m$",
        "conditions": r"$m \in \mathbb{Z}_{\ge 0}$.",
        "relevance": r"Choosing $x=\pi/2$ turns the sine series into the alternating odd-harmonic sum.",
    },
]

NEW_HINTS = [
    r"Odd square wave $\Rightarrow$ only $\sin(nx)$ terms; start with $a_0=a_n=0$.",
    r"Compute $b_n$ using $f(x)=2$ on $(0,\pi)$ only.",
    r"Use $\cos(n\pi)=(-1)^n$: even $n$ give $b_n=0$.",
    r"Evaluate the Fourier series at $x=\dfrac{\pi}{2}$ where $\sin((2m+1)\pi/2)=(-1)^m$.",
    r"Then isolate $s$ from $f(\pi/2)=2$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "concept_recall",
        "front": r"Odd function on $[-\pi,\pi]$: which Fourier coefficients vanish?",
        "back": r"$a_0 = 0$ and $a_n = 0$; only $b_n$ may be nonzero.",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "formula_recall",
        "front": r"$b_n$ for odd $f$ with period $2\pi$ (interval $[0,\pi]$)?",
        "back": r"$b_n = \dfrac{2}{\pi}\int_{0}^{\pi} f(x)\sin(nx)\,dx$",
        "difficulty": "easy",
        "time_limit_seconds": 30,
    },
    {
        "card_type": "application",
        "front": r"Square wave: $f=-k$ on $(-\pi,0)$, $f=k$ on $(0,\pi)$. Sine series form?",
        "back": r"$f(x) = \dfrac{4k}{\pi}\sum_{m=0}^{\infty} \dfrac{\sin\bigl((2m+1)x\bigr)}{2m+1}$",
        "difficulty": "medium",
        "time_limit_seconds": 45,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Common slip: value of $\cos(n\pi)$?",
        "back": r"$\cos(n\pi)=(-1)^n$ (not always $1$).",
        "difficulty": "easy",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "concept_recall",
        "front": r"How does the Leibniz sum $1-\frac{1}{3}+\frac{1}{5}-\cdots$ relate to this Fourier series?",
        "back": r"Evaluate the sine series at $x=\pi/2$; with amplitude $k=2$ you get $2=\frac{8}{\pi}s$, so $s=\pi/4$.",
        "difficulty": "medium",
        "time_limit_seconds": 60,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "Odd → Sine only",
        "concept": r"Odd $f \Rightarrow a_0=a_n=0$, only $b_n \sin(nx)$.",
        "effectiveness": "high",
        "context": "Fourier series symmetry shortcuts",
    },
    {
        "mnemonic": r"Leibniz: $1 - \frac{1}{3} + \frac{1}{5} - \cdots = \frac{\pi}{4}$",
        "concept": r"Alternating odd reciprocals sum to $\pi/4$.",
        "effectiveness": "high",
        "context": "Recognizing the target series after setting $x=\pi/2$",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Forgetting odd symmetry and carrying $\cos$-terms unnecessarily.",
        "why_students_make_it": "Not checking $f(-x)$ before writing full Euler formulas.",
        "severity": "High",
        "frequency": "common",
        "how_to_avoid": r"Test $f(-x)$ first; for odd $f$, use $b_n = \frac{2}{\pi}\int_0^{\pi} f(x)\sin(nx)\,dx$.",
        "consequence": r"Wrong $a_n$ work and a much longer path.",
    },
    {
        "type": "Calculation",
        "mistake": r"Sign/limit errors integrating $\sin(nx)$ or evaluating $\cos(n\pi)$.",
        "why_students_make_it": r"Rushing the antiderivative $-\cos(nx)/n$.",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Substitute limits carefully; memorize $\cos(n\pi)=(-1)^n$.",
        "consequence": r"Wrong $b_n$ pattern (even/odd harmonics).",
    },
    {
        "type": "Problem Solving",
        "mistake": r"Evaluating at $x=0$ or $x=\pi$ where the square wave jumps or sines vanish unhelpfully.",
        "why_students_make_it": r"Not matching $\sin((2m+1)x)$ to $(-1)^m$.",
        "severity": "Medium",
        "frequency": "occasional",
        "how_to_avoid": r"Pick $x=\pi/2$ so $\sin((2m+1)\pi/2)=(-1)^m$.",
        "consequence": r"Cannot isolate the target alternating sum $s$.",
    },
    {
        "type": "Calculation",
        "mistake": r"Algebra slip solving $2 = \frac{8}{\pi}s$ (e.g., $s=\pi/8$).",
        "why_students_make_it": r"Hasty rearrangement.",
        "severity": "Low",
        "frequency": "rare",
        "how_to_avoid": r"$s = \frac{2\pi}{8} = \frac{\pi}{4}$.",
        "consequence": r"Wrong letter option despite correct series.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"If you know the odd square-wave sine series, jump to $x=\pi/2$ and match $s$ in under 3 minutes.",
    "guessing_heuristic": r"The alternating odd-harmonic series is the classic Leibniz form for $\pi/4$—useful if time is short.",
    "time_management": r"Target 3–4 minutes including integral check.",
}

NEW_DIFFICULTY_FACTORS = [
    r"Requires recognizing odd symmetry before integrating.",
    r"Needs correct evaluation point $x=\frac{\pi}{2}$ to match the alternating sum.",
    r"Careful algebra tying $f(\pi/2)=2$ to $s$.",
]

NEW_ALT_METHODS = [
    {
        "name": "Complex exponential Fourier series",
        "description": (
            r"Use $f(x)=\sum_{n=-\infty}^{\infty} c_n e^{inx}$ with "
            r"$c_n=\frac{1}{2\pi}\int_{-\pi}^{\pi} f(x)e^{-inx}\,dx$, then relate $c_n$ to $b_n$. "
            r"Same result after algebra; heavier machinery."
        ),
        "pros_cons": "Pros: compact. Cons: More complex arithmetic for this stem.",
        "when_to_use": r"When comfortable with complex coefficients or spectrum view.",
    },
    {
        "name": "Recognize Leibniz sum directly",
        "description": (
            r"If you identify $s = \sum_{m=0}^{\infty} (-1)^m/(2m+1)$ as $\pi/4$ from standard series, "
            r"you can pick C quickly—ideal if time-constrained."
        ),
        "pros_cons": "Pros: fastest. Cons: little derivation credit if scratch work is required.",
        "when_to_use": r"Final moments after eliminating absurd options.",
    },
]


def patch_t1(t1: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t1 or {})
    av = o.setdefault("answer_validation", {})
    av["correct_answer"] = "C"
    av["reasoning"] = NEW_REASONING

    exp = o.setdefault("explanation", {})
    exp["question_nature"] = "Calculation"
    exp["step_by_step"] = NEW_STEPS
    exp["formulas_used"] = NEW_FORMULAS_USED

    o["hints"] = NEW_HINTS
    o["formulas_principles"] = NEW_FORMULAS_PRINCIPLES

    sbs = o.setdefault("step_by_step_solution", {})
    sbs["total_steps"] = len(NEW_STEPS)
    sbs["solution_path"] = (
        r"Odd symmetry $\to$ sine series $\to$ compute $b_n$ "
        r"$\to$ set $x=\pi/2$ $\to$ identify Leibniz sum $\to$ $s=\pi/4$"
    )
    sbs["key_insights"] = [
        r"Odd square wave ⇒ only $\sin(nx)$ terms; even harmonics vanish via $1-(-1)^n$.",
        r"At $x=\pi/2$, odd sines alternate sign and reproduce $1-\frac13+\frac15-\cdots$.",
        r"Continuity at $\pi/2$ lets you equate series value to $f(\pi/2)=2$.",
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
    return o


def patch_t3(t3: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    o = deepcopy(t3 or {})
    o["alternative_methods"] = NEW_ALT_METHODS
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
                "qt": NEW_QUESTION_TEXT,
                "qtl": NEW_QUESTION_TEXT_LATEX,
                "opts": json.dumps(NEW_OPTIONS),
                "t1": json.dumps(t1, ensure_ascii=False),
                "t2": json.dumps(t2, ensure_ascii=False),
                "t3": json.dumps(t3, ensure_ascii=False),
                "u": datetime.utcnow(),
                "q": PUBLIC_ID,
            },
        )

    print("patched", PUBLIC_ID)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from app.core.database import engine

PUBLIC_ID = "GATE_2016_AE_Q49"

NEW_QUESTION_TEXT_PLAIN = (
    "An aircraft is flying level in the north direction at 55 m/s under crosswind from east to west "
    "of 5 m/s. For the aircraft, C_n_beta = 0.012/deg and C_n_delta_r = -0.0072/deg, where delta_r "
    "is rudder deflection and beta is sideslip angle. The rudder deflection exerted by the pilot is ________ degrees."
)

NEW_QUESTION_TEXT_LATEX = (
    r"An aircraft is flying level in the north direction at $U=55~\mathrm{m/s}$ under crosswind from east to west "
    r"of $v_{\text{cross}}=5~\mathrm{m/s}$. For the aircraft, $C_{n_\beta}=0.012~\mathrm{deg}^{-1}$ and "
    r"$C_{n_{\delta_r}}=-0.0072~\mathrm{deg}^{-1}$, where $\delta_r$ is rudder deflection and $\beta$ is sideslip angle. "
    r"The rudder deflection exerted by the pilot is $\underline{\hspace{5em}}$ degrees."
)

NEW_REASONING = (
    r"Use directional trim (zero net yawing moment):"
    "\n"
    r"$C_{n_\beta}\,\beta + C_{n_{\delta_r}}\,\delta_r = 0$"
    "\n"
    r"$\Rightarrow \delta_r = -\dfrac{C_{n_\beta}\,\beta}{C_{n_{\delta_r}}}$."
    "\n\n"
    r"First find sideslip from velocity triangle:"
    "\n"
    r"$\beta = \tan^{-1}\!\left(\dfrac{v_{\text{cross}}}{U}\right) = \tan^{-1}\!\left(\dfrac{5}{55}\right) "
    r"\approx 5.194^\circ$."
    "\n\n"
    r"Now substitute:"
    "\n"
    r"$\delta_r = -\dfrac{0.012\times 5.194}{-0.0072} \approx 8.657^\circ$."
    "\n"
    r"Hence required rudder deflection is approximately $8.66^\circ$ (about $8.7^\circ$; key band 8.6–8.7)."
)

NEW_STEP_BY_STEP = [
    r"Given: $U=55~\mathrm{m/s}$, $v_{\text{cross}}=5~\mathrm{m/s}$, $C_{n_\beta}=0.012~\mathrm{deg}^{-1}$, $C_{n_{\delta_r}}=-0.0072~\mathrm{deg}^{-1}$.",
    r"Compute sideslip from velocity geometry: $\beta=\tan^{-1}(v_{\text{cross}}/U)=\tan^{-1}(5/55)\approx5.194^\circ$.",
    r"Write trim condition: $C_{n_\beta}\beta + C_{n_{\delta_r}}\delta_r=0$.",
    r"Rearrange: $\delta_r=-\dfrac{C_{n_\beta}\beta}{C_{n_{\delta_r}}}$.",
    r"Substitute values: $\delta_r=-\dfrac{0.012\times5.194}{-0.0072}\approx8.657^\circ$.",
    r"Report: $\delta_r\approx8.66^\circ\approx8.7^\circ$.",
]

NEW_FORMULAS_USED = [
    r"$\beta=\tan^{-1}\!\left(\dfrac{v_{\text{cross}}}{U}\right)$",
    r"$C_{n_\beta}\beta + C_{n_{\delta_r}}\delta_r=0$",
    r"$\delta_r=-\dfrac{C_{n_\beta}\beta}{C_{n_{\delta_r}}}$",
]

NEW_FORMULAS_PRINCIPLES = [
    {
        "name": "Sideslip angle from velocity components",
        "type": "equation",
        "formula": r"$\beta=\tan^{-1}\!\left(\dfrac{v_{\text{cross}}}{U}\right)$",
        "relevance": "Converts crosswind and forward speed into sideslip angle.",
        "conditions": ["Use consistent axis/sign convention and angle units."],
    },
    {
        "name": "Directional trim equation",
        "type": "equation",
        "formula": r"$C_{n_\beta}\beta + C_{n_{\delta_r}}\delta_r=0$",
        "relevance": "Zero net yawing moment condition in steady trimmed flight.",
        "conditions": ["Steady flight, linearized derivatives."],
    },
    {
        "name": "Rudder deflection for trim",
        "type": "equation",
        "formula": r"$\delta_r=-\dfrac{C_{n_\beta}\beta}{C_{n_{\delta_r}}}$",
        "relevance": "Direct expression for required pilot rudder input.",
        "conditions": ["$C_{n_\beta}$ and $C_{n_{\delta_r}}$ given in matching angle units."],
    },
]

NEW_HINTS = [
    r"Do not use crosswind speed directly as angle; compute $\beta=\tan^{-1}(v_{\text{cross}}/U)$.",
    r"Keep units consistent: derivatives are per degree, so use $\beta$ in degrees.",
    r"Apply trim as $C_{n_\beta}\beta + C_{n_{\delta_r}}\delta_r=0$.",
]

NEW_FLASHCARDS = [
    {
        "card_type": "formula_recall",
        "front": "Directional trim equation with sideslip and rudder?",
        "back": r"$C_{n_\beta}\beta + C_{n_{\delta_r}}\delta_r = 0$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "concept_recall",
        "front": r"How do you compute sideslip from crosswind and forward speed?",
        "back": r"$\beta=\tan^{-1}(v_{\text{cross}}/U)$.",
        "difficulty": "easy",
        "time_limit_seconds": 20,
    },
    {
        "card_type": "mistake_prevention",
        "front": r"Common unit trap in this problem?",
        "back": r"Using radians for $\beta$ while derivatives are per degree; convert or use degree mode.",
        "difficulty": "medium",
        "time_limit_seconds": 25,
    },
    {
        "card_type": "application",
        "front": r"Given $U=55$, $v_{\text{cross}}=5$, $C_{n_\beta}=0.012$, $C_{n_{\delta_r}}=-0.0072$, find $\delta_r$.",
        "back": r"$\beta\approx5.194^\circ$, then $\delta_r\approx8.66^\circ$.",
        "difficulty": "medium",
        "time_limit_seconds": 35,
    },
]

NEW_MNEMONICS = [
    {
        "mnemonic": "CRAB: Crosswind Requires Arctan for Beta",
        "concept": r"Compute sideslip as $\beta=\tan^{-1}(v/U)$",
        "effectiveness": "high",
        "context": "Crosswind trim numericals",
    },
    {
        "mnemonic": "Trim Yaw = Zero",
        "concept": r"Use $C_{n_\beta}\beta + C_{n_{\delta_r}}\delta_r = 0$",
        "effectiveness": "high",
        "context": "Directional trim sign bookkeeping",
    },
]

NEW_COMMON_MISTAKES = [
    {
        "type": "Conceptual",
        "mistake": r"Treating crosswind speed as sideslip angle directly.",
        "severity": "High",
        "frequency": "common",
        "consequence": r"Large error in $\delta_r$ (typically far below 8.7°).",
        "how_to_avoid": r"Always compute $\beta=\tan^{-1}(v_{\text{cross}}/U)$ first.",
        "why_students_make_it": "Angle-speed confusion under time pressure.",
    },
    {
        "type": "Units",
        "mistake": r"Using radians for $\beta$ with derivatives per degree.",
        "severity": "High",
        "frequency": "occasional",
        "consequence": "Answer off by factor about 57.3 if mishandled.",
        "how_to_avoid": "Use degree mode or convert consistently.",
        "why_students_make_it": "Calculator mode mismatch.",
    },
    {
        "type": "Sign Error",
        "mistake": r"Dropping minus sign in $\delta_r=-\dfrac{C_{n_\beta}\beta}{C_{n_{\delta_r}}}$.",
        "severity": "Medium",
        "frequency": "occasional",
        "consequence": r"Wrong rudder direction sign.",
        "how_to_avoid": r"Write trim equation before substituting signs.",
        "why_students_make_it": "Fast algebra without sign check.",
    },
]

NEW_EXAM_STRATEGY = {
    "priority": "Must Attempt",
    "triage_tip": r"Two-step solve: find $\beta$ from arctan, then apply trim formula for $\delta_r$.",
    "guessing_heuristic": "With 5/55 crosswind ratio, beta is near 5 degrees; derivative ratio gives rudder near 8-9 degrees.",
    "time_management": "2-3 minutes with careful sign and unit handling.",
}

NEW_DIFFICULTY_FACTORS = [
    "Requires geometry-to-aerodynamic coupling (beta from velocity triangle, then trim).",
    "Sign convention and per-degree units can cause avoidable mistakes.",
    "Arithmetic is short but error-sensitive.",
]

NEW_ALT_METHODS = [
    {
        "name": "Small-angle approximation",
        "description": r"Use $\beta\approx v_{\text{cross}}/U$ in radians, then convert to degrees before trim equation.",
        "pros_cons": "Pros: faster mental estimate. Cons: requires careful rad-to-deg conversion.",
        "when_to_use": "Quick checks under time pressure.",
    },
    {
        "name": "Airspeed-magnitude route",
        "description": r"Compute $V=\sqrt{U^2+v_{\text{cross}}^2}$ and use $\beta=\sin^{-1}(v_{\text{cross}}/V)$, then trim.",
        "pros_cons": "Pros: exact geometric interpretation. Cons: extra arithmetic with no practical gain here.",
        "when_to_use": "When airspeed magnitude is also needed.",
    },
]

NEW_SEARCH_KEYWORDS = [
    "GATE 2016 AE Q49 rudder deflection",
    "directional trim crosswind beta",
    "Cn_beta Cn_delta_r equation",
    "sideslip angle arctan crosswind",
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
    av["correct_answer"] = "8.6 : 8.7"

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
        r"Compute $\beta=\tan^{-1}(v_{\text{cross}}/U)$ $\Rightarrow$ apply "
        r"$C_{n_\beta}\beta+C_{n_{\delta_r}}\delta_r=0$ $\Rightarrow$ solve $\delta_r$"
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
    c["Control Systems"] = "Directional trim is a steady-state zero-moment balance, analogous to zero-error equilibrium in control design."
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
                "opts": json.dumps(None),
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

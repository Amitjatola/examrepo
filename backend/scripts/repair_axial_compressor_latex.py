"""
One-off repair: Axial Flow Compressors topic questions corrupted by bad re.sub
replacements (literal \\1). Restores explanation steps and reasoning from
search_content, fixes known NAT LaTeX fields, then applies conservative TeX
fragment repairs to remaining tier_1 strings.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

QUESTION_IDS = [
    "GATE_2012_AE_Q52",
    "GATE_2012_AE_Q53",
    "GATE_2013_AE_Q46",
    "GATE_2014_AE_Q18",
    "GATE_2015_AE_Q57",
    "GATE_2017_AE_Q46",
    "GATE_2018_AE_Q53",
    "GATE_2019_AE_Q48",
    "GATE_2020_AE_Q23",
    "GATE_2021_AE_Q46",
    "GATE_2022_AE_Q65",
    "GATE_2023_AE_Q21",
    "GATE_2024_AE_Q40",
    "GATE_2024_AE_Q50",
]

NATURES = {
    "Calculation",
    "Conceptual",
    "Numerical",
    "MCQ",
    "Theoretical",
    "Analytical",
    "Assertion-Reason",
    "Linked",
    "Multi-Concept",
    "Problem Solving",
    "Application",
    "Descriptive",
}

STEP_START = re.compile(
    r"^(Step \d+:|Understand |Recall |Analyze |Identify (the |all )?|Calculate |Determine |Conclude |Evaluate |Compare |Use |Apply |From |For |The problem|The question|Statement )",
    re.I,
)


def step_start_index(parts: list[str]) -> Optional[int]:
    nature_idx: Optional[int] = None
    for i, p in enumerate(parts):
        if p in NATURES:
            nature_idx = i
            break
    if nature_idx is not None:
        return nature_idx + 1
    for i in range(2, len(parts)):
        if STEP_START.match(parts[i]):
            return i
    return None


def extract_steps_from_search_content(search_content: str) -> list[str]:
    parts = [p.strip() for p in (search_content or "").split(" | ")]
    si = step_start_index(parts)
    if si is None:
        return []
    return [s for s in parts[si:] if s]


def fix_greek_stubs(s: str) -> str:
    """Repair common '\\\\command\\\\1' truncation patterns."""
    repl = [
        (r"\\bet\\1(?![A-Za-z])", r"\\beta"),
        (r"\\alph\\1(?![A-Za-z])", r"\\alpha"),
        (r"\\gamm\\1(?![A-Za-z])", r"\\gamma"),
        (r"\\thet\\1(?![A-Za-z])", r"\\theta"),
        (r"\\cir\\1", r"\\circ"),
        (r"\\p\\1(?![A-Za-z])", r"\\pi"),
        (r"\\up\\1(?![A-Za-z])", r"\\upsilon"),
        (r"\\zet\\1(?![A-Za-z])", r"\\zeta"),
    ]
    out = s
    for pat, rep in repl:
        out = re.sub(pat, rep, out)
    return out


def fix_angle_subscripts(s: str) -> str:
    """
    Many corrupted strings use \\\\alpha_\\\\1 / \\\\beta_\\\\1 for station subscripts.
    Alternate 1/2 by occurrence order (works for typical inlet/outlet wording).
    """
    a_count = 0

    def sub_alphas(_m: re.Match) -> str:
        nonlocal a_count
        a_count += 1
        return r"\alpha_" + ("1" if a_count % 2 == 1 else "2")

    b_count = 0

    def sub_betas(_m: re.Match) -> str:
        nonlocal b_count
        b_count += 1
        return r"\beta_" + ("1" if b_count % 2 == 1 else "2")

    out = re.sub(r"\\alpha_\\1(?![0-9])", sub_alphas, s)
    out = re.sub(r"\\beta_\\1(?![0-9])", sub_betas, out)
    return out


def fix_placeholder_tokens(s: str) -> str:
    """Remove standalone placeholder \\\\1 where it clearly closes a delimiter."""
    out = s
    out = re.sub(r"\\\}\s*\\1\s*\\\$", r"}$", out)
    out = re.sub(r"\^\s*\\1\s*\\\}", r"^2}", out)
    out = re.sub(r"\^\s*\\1\s*\)", r"^2)", out)
    return out


def fix_right_delim(s: str) -> str:
    return s.replace(r"\right\1", r"\right)")


def fix_unbalanced_math_backslash_one(s: str) -> str:
    """
    In $...$ spans, a trailing \\\\1 often replaced a missing ')' after the bulk
    update used a bad re.sub replacement string.
    """

    def repl(m: re.Match) -> str:
        inner = m.group(1)
        chunk = inner
        chunk = fix_right_delim(chunk)
        if chunk.count("(") > chunk.count(")") and re.search(r"\\1\s*$", chunk):
            chunk = re.sub(r"\\1\s*$", ")", chunk)
        return f"${chunk}$"

    return re.sub(r"\$([^$]*)\$", repl, s)


def fix_placeholder_symbol_tokens(s: str) -> str:
    """Repair common corrupted symbol tokens where \\\\1 ate a single LaTeX character or subscript."""
    out = s
    rules: list[tuple[str, str]] = [
        (r"\$\s*\\1\s*\$\s*is blade speed", r"$U$ is blade speed"),
        (r"\$\s*\\1_\\1\s*\$\s*is axial velocity", r"$c_a$ is axial velocity"),
        (r"\$\s*\\1_\{t1\}\s*\$\s*is tangential absolute velocity", r"$c_{t1}$ is tangential absolute velocity"),
        (
            r"\$\\alpha_1\s*\$\s*is the angle of absolute velocity\s*\$\s*\\1_\\1\s*\$",
            r"$\alpha_1$ is the angle of absolute velocity $C_1$",
        ),
        (
            r"\$\\beta_1\s*\$\s*is the angle of relative velocity\s*\$\s*\\1_\\1\s*\$",
            r"$\beta_1$ is the angle of relative velocity $W_1$",
        ),
        (r"\$\s*\\1\s*=\s*\\dot\{m\}\s*\\cdot\s*\\Delta\s*\\1\s*\$", r"$P = \dot{m} \cdot \Delta W$"),
        (r"\$\s*\\1\s*=\s*\\frac\{P\}\{\\dot\{m\}\}\s*\$", r"$w = \frac{P}{\dot{m}}$"),
        (r"\$\s*\\1\s*=\s*c_a\s*\(\\tan\(\\alpha_1\)\s*\+\s*\\tan\(\\beta_1\)\\1\s*\$", r"$u = c_a (\tan(\alpha_1) + \tan(\beta_1))$"),
        (r"\$\s*\\1\s*=\s*u\s*c_a\s*\(\\tan\(\\alpha_2\)\s*-\s*\\tan\(\\alpha_1\)\\1\s*\$", r"$w = u c_a (\tan(\alpha_2) - \tan(\alpha_1))$"),
        (r"\$\s*\\1_2\s*=\s*\\frac\{V_f\}\{\\cos\(\\beta_2\)\}\s*\$", r"$W_2 = \frac{V_f}{\cos(\beta_2)}$"),
        (r"\$\s*\\1_2\s*=\s*\\frac\{V_f\}\{\\cos\\alpha_1\}\s*\$", r"$W_2 = \frac{V_f}{\cos\alpha_1}$"),
        (r"\$\s*\\1_2\s*=\s*\\frac\{V_f\}\{\\cos\\beta_2\}\s*\$", r"$W_2 = \frac{V_f}{\cos\beta_2}$"),
        (r"\$\s*\\1_a\s*=\s*V_1\s*\\cos\(\\alpha_1\\1\s*\$", r"$c_a = V_1 \cos(\alpha_1)$"),
        (r"\$\s*\\1_a\s*=\s*\\text\{constant\}\s*\$", r"$c_a = \text{constant}$"),
        (r"\$\s*\\1_\{actual\}\s*=\s*U\(V_\{w2\}\s*-\s*V_\{w1\}\\1\s*\$", r"$w_{\mathrm{actual}} = U(V_{w2} - V_{w1})$"),
        (r"\$\s*\\1_\{shaft\}\s*=\s*\\dot\{m\}\s*W_\\1\s*\$", r"$P_{\mathrm{shaft}} = \dot{m} w$"),
        (r"\$\s*\\1_\{t2\}\s*=\s*U\s*\+\s*W_\{t2\}\s*\$", r"$c_{t2} = U + W_{t2}$"),
        (r"\$\s*\\1_\{t2\}\s*=\s*V_a\s*\\tan\(\\beta_2\\1\s*\$", r"$c_{t2} = V_a \tan(\beta_2)$"),
        (r"\$\s*\\1_\{w\}\s*=\s*U\s*-\s*V_z\s*\\tan\s*\\beta\s*\$", r"$V_w = U - V_z \tan \beta$"),
        (r"\$\(h_2\s*-\s*h_1\)\s*=\s*0\.5\s*\\times\s*\(h_3\s*-\s*h_1\\1\s*\$", r"$(h_2 - h_1) = 0.5 \times (h_3 - h_1)$"),
        (r"\$\\Delta\s*W\s*=\s*U\s*\(V_\{t2\}\s*-\s*V_\{t1\}\\1\s*\$", r"$\Delta W = U (V_{t2} - V_{t1})$"),
        (r"\$\\dot\{m\}\s*=\s*\\rho\s*A\s*V_\\1\s*\$", r"$\dot{m} = \rho A V_x$"),
        (
            r"\$\\dot\{m\}\$\s*is mass flow rate,\s*\$\s*\\1_\\1\s*\$\s*is specific work",
            r"$\dot{m}$ is mass flow rate, $w$ is specific work",
        ),
        (
            r"Applicable for an axial compressor stage with constant axial velocity\s*\$\s*\\1_\\1\s*\$\s*\.\s*"
            r"\$\\alpha_1\s*\$\s*and\s*\$\\alpha_2\s*\$\s*are absolute inlet and outlet flow angles\.\s*"
            r"Relates blade speed\s*\$\s*\\1\s*\$\s*to",
            r"Applicable for an axial compressor stage with constant axial velocity $c_a$. "
            r"$\alpha_1$ and $\alpha_2$ are absolute inlet and outlet flow angles. Relates blade speed $U$ to",
        ),
        (
            r"Applies to a compressor stage for a perfect gas with constant specific heats\.\s*"
            r"\$\\pi\s*\$\s*is the stage pressure ratio,\s*\$\\eta_\{st\}\s*\$\s*is the stage isentropic efficiency,\s*"
            r"\$\\Delta\s*T_\\1\s*\$\s*is",
            r"Applies to a compressor stage for a perfect gas with constant specific heats. "
            r"$\pi$ is the stage pressure ratio, $\eta_{st}$ is the stage isentropic efficiency, $\Delta T_0$ is",
        ),
        (
            r"Applies to adiabatic flow through a rotating blade row\.\s*\$\s*\\1\s*\$\s*is blade speed,\s*"
            r"\$\s*\\1_\{w1\}\s*\$\s*and\s*\$\s*\\1_\{w2\}\s*\$\s*are whirl components",
            r"Applies to adiabatic flow through a rotating blade row. $U$ is blade speed, $V_{w1}$ and $V_{w2}$ are whirl components",
        ),
        (
            r"Applies to an axial compressor stage, where\s*\$\s*\\1_\\1\s*\$\s*is rotor inlet static enthalpy,\s*"
            r"\$\s*\\1_\\1\s*\$\s*is rotor outlet static enthalpy, and\s*\$\s*\\1_\\1\s*\$\s*is stage outlet static enthalpy",
            r"Applies to an axial compressor stage, where $h_1$ is rotor inlet static enthalpy, $h_2$ is rotor outlet static enthalpy, and $h_3$ is stage outlet static enthalpy",
        ),
        (
            r"Applies to rotor section of axial turbomachines with constant mean blade speed\s*\$\s*\\1\s*\$\s*"
            r"\(at a given radius\)\.\s*Energy transfer only via change in angular momentum\.\s*\$\s*\\1_\{t1\}\s*\$",
            r"Applies to rotor section of axial turbomachines with constant mean blade speed $U$ (at a given radius). "
            r"Energy transfer only via change in angular momentum. $c_{t1}$",
        ),
        (
            r"Applies to steady, adiabatic turbomachinery with negligible changes in potential energy\.\s*"
            r"Specifically for an axial compressor stage with constant axial velocity\s*\$\s*\\1_\\1\s*\$\s*\.\s*\$\s*\\1\s*\$\s*is",
            r"Applies to steady, adiabatic turbomachinery with negligible changes in potential energy. "
            r"Specifically for an axial compressor stage with constant axial velocity $c_a$. $w$ is",
        ),
        (
            r"Applies to turbomachines \(compressors, turbines\) for steady flow and constant blade speed\s*\$\s*\\1\s*\$\s*"
            r"\(at a given radius\)\.\s*Energy transfer only via change in angular momentum\.\s*\$\s*\\1_\{t1\}\s*\$",
            r"Applies to turbomachines (compressors, turbines) for steady flow and constant blade speed $U$ (at a given radius). "
            r"Energy transfer only via change in angular momentum. $c_{t1}$",
        ),
        (
            r"Axial compressor stage with constant axial velocity;\s*\$\s*\\1_\\1\s*\$\s*is degree of reaction,\s*\$\s*\\1\s*\$\s*blade speed,\s*"
            r"\$\s*\\1_\\1\s*\$\s*axial velocity",
            r"Axial compressor stage with constant axial velocity; $R$ is degree of reaction, $U$ blade speed, $c_a$ axial velocity",
        ),
        (
            r"For a 50\\% reaction stage with constant axial velocity, the blade speed \(u\) can be directly related\s*"
            r"to the axial velocity \(\$\s*\\1_\\1\s*\$\) and flow angles using the relation\s*\$\s*\\1\s*=\s*c_a",
            r"For a 50\\% reaction stage with constant axial velocity, the blade speed (u) can be directly related "
            r"to the axial velocity ($c_a$) and flow angles using the relation $u = c_a",
        ),
        (
            r"For a perfect gas with constant specific heat at constant pressure \(\$\s*\\1_\\1\s*\$\), relates the specific\s*"
            r"work input \(\$\s*\\1\s*\$\) to the actual stagnation temperature rise \(\$\s*\\Delta\s*T_\\1\s*\$\)",
            r"For a perfect gas with constant specific heat at constant pressure ($C_p$), relates the specific "
            r"work input ($w$) to the actual stagnation temperature rise ($\Delta T_0$)",
        ),
        (
            r"For axial compressors, relates blade speed \(\$\s*\\1\s*\$\), axial velocity \(\$\s*\\1_\\1\s*\$\), and relative\s*"
            r"flow angle \(\$\\beta\s*\$\) to the tangential component of absolute velocity \(\$\s*\\1_\\1\s*\$\)",
            r"For axial compressors, relates blade speed ($U$), axial velocity ($c_a$), and relative "
            r"flow angle ($\beta$) to the tangential component of absolute velocity ($c_\theta$)",
        ),
        (
            r"For axial turbomachines,\s*\$\s*\\1\s*=\s*0\.\s*\\1\s*\$\s*implies\s*"
            r"\$\\Delta\s*h_\{static,\s*rotor\}\s*=\s*\\Delta\s*h_\{static,\s*stator\}\s*\$",
            r"For axial turbomachines, $R=0.5$ implies $\Delta h_{\mathrm{static, rotor}} = \Delta h_{\mathrm{static, stator}}$",
        ),
        (r"Steady flow, constant\s*\$\s*\\1_\\1\s*\$, no potential energy change", r"Steady flow, constant $c_a$, no potential energy change"),
        (
            r"The velocity triangle diagram provides all necessary components, but careful identification of\s*"
            r"\$\s*\\1_\{t1\}\s*\$\s*and\s*\$\s*\\1_\{t2\}\s*\$\s*is crucial",
            r"The velocity triangle diagram provides all necessary components, but careful identification of $c_{t1}$ and $c_{t2}$ is crucial",
        ),
        (
            r"The work coefficient \(ψ\) directly relates to the specific work input per stage \(\$\s*\\1_s\s*=\s*ψU\^\\1\s*\$\)",
            r"The work coefficient ($\psi$) directly relates to the specific work input per stage ($w_s = \psi U^2$)",
        ),
        (
            r"Used for a right-angled velocity triangle where\s*\$\s*\\1_\\1\s*\$\s*is the axial component and\s*\$\\alpha\s*\$\s*"
            r"is the absolute flow angle",
            r"Used for a right-angled velocity triangle where $V_x$ is the axial component and $\alpha$ is the absolute flow angle",
        ),
        (
            r"Used to determine the change in axial velocity \(\$\s*\\1_\\1\s*\$\) based on changes in mass flow rate\s*"
            r"\(\$\\dot\{m\}\$\)",
            r"Used to determine the change in axial velocity ($V_x$) based on changes in mass flow rate ($\dot{m}$)",
        ),
        (r"\$\s*\\1_a\s*=\s*V_1\s*\\cos\(\\alpha_1\)\s*\$", r"$c_a = V_1 \cos(\alpha_1)$"),
        (r"\$\s*\\1_\{t2\}\s*=\s*V_a\s*\\tan\(\\beta_2\)\s*\$", r"$c_{t2} = V_a \tan(\beta_2)$"),
        (r"\$\s*\\1\s*=\s*c_a\s*\(\\tan\(\\alpha_1\)\s*\+\s*\\tan\(\\beta_1\)\)\s*\$", r"$u = c_a (\tan(\alpha_1) + \tan(\beta_1))$"),
        (r"\$\s*\\1\s*=\s*u\s*c_a\s*\(\\tan\(\\alpha_2\)\s*-\s*\\tan\(\\alpha_1\)\)\s*\$", r"$w = u c_a (\tan(\alpha_2) - \tan(\alpha_1))$"),
        (
            r"\$w\$\s*is specific work per unit mass.*?,\s*\$U\$\s*is blade speed,\s*\$\s*\\1_\\1\s*\$\s*is tangential component",
            r"$w$ is specific work per unit mass (work done *on* the fluid), $U$ is blade speed, $c_\theta$ is tangential component",
        ),
        (
            r"Euler Turbomachinery Work Equation \(\$\s*\\1\s*=\s*u\(C_\{w1\}\s*-\s*C_\{w2\}\)\$\s*or\s*\$\s*\\1\s*=\s*u\s*c_a\s*\(\\tan\s*\\alpha_1\s*-\s*\\tan\s*\\alpha_2\)\$\)",
            r"Euler Turbomachinery Work Equation ($w = u(C_{w1} - C_{w2})$ or $w = u c_a (\tan \alpha_1 - \tan \alpha_2)$)",
        ),
        (r"\$\s*\\1_\{actual\}\s*=\s*U\(V_\{w2\}\s*-\s*V_\{w1\}\)\s*\$", r"$w_{\mathrm{actual}} = U(V_{w2} - V_{w1})$"),
        (
            r"\$U\$\s*is blade speed,\s*\$\s*\\1_\{w1\}\s*\$\s*and\s*\$\s*\\1_\{w2\}\s*\$\s*are whirl components.*?respectively\.\s*\$\\1\s*\$\s*is specific work",
            r"$U$ is blade speed, $V_{w1}$ and $V_{w2}$ are whirl components of absolute velocity at inlet and outlet respectively. $w$ is specific work",
        ),
        (
            r"\$\\Delta\s*T_0\$\s*is the actual stagnation temperature rise,\s*\$\s*\\1_\{01\}\s*\$\s*is the inlet stagnation temperature",
            r"$\Delta T_0$ is the actual stagnation temperature rise, $T_{01}$ is the inlet stagnation temperature",
        ),
        (
            r"constant mean blade speed\s*\$\s*\\1\s*\$\.\s*\$\s*\\1_\{t1\}\s*\$\s*is whirl at inlet,\s*\$\s*\\1_\{t2\}\s*\$\s*is whirl at outlet",
            r"constant mean blade speed $U$. $C_{w1}$ is whirl at inlet, $C_{w2}$ is whirl at outlet",
        ),
        (
            r"Energy transfer only via change in angular momentum\.\s*\$c_\{t1\}\$\s*and\s*\$\s*\\1_\{t2\}\s*\$\s*are tang",
            r"Energy transfer only via change in angular momentum. $c_{t1}$ and $c_{t2}$ are tang",
        ),
    ]
    for pat, rep in rules:
        out = re.sub(pat, lambda _m, fixed=rep: fixed, out, flags=re.I | re.S)
    return out


def repair_string_leaf(s: str) -> str:
    if "\\1" not in s and "\\\\1" not in s:
        return s
    out = s
    out = fix_right_delim(out)
    out = fix_greek_stubs(out)
    out = fix_angle_subscripts(out)
    out = fix_placeholder_tokens(out)
    out = fix_unbalanced_math_backslash_one(out)
    out = fix_placeholder_symbol_tokens(out)
    return out


def deep_repair_strings(obj: Any) -> Any:
    if isinstance(obj, str):
        return repair_string_leaf(obj)
    if isinstance(obj, list):
        return [deep_repair_strings(x) for x in obj]
    if isinstance(obj, dict):
        return {k: deep_repair_strings(v) for k, v in obj.items()}
    return obj


def build_question_text_latex_2020_q23() -> str:
    return (
        "Air enters the rotor of an axial compressor stage with no pre-whirl ($C_{\\theta} = 0$) "
        "and exits the rotor with whirl velocity, $C_{\\theta} = 150\\ \\mathrm{m/s}$. "
        "The velocity of rotor vanes, $U$ is $200\\ \\mathrm{m/s}$. "
        "Assuming $C_p = 1005\\ \\mathrm{J/(kg\\cdot K)}$, the stagnation temperature rise across "
        "the rotor is __________ K (round off to one decimal place)."
    )


def build_question_text_plain_2020_q23() -> str:
    return (
        "Air enters the rotor of an axial compressor stage with no pre-whirl "
        "(C_θ = 0) and exits the rotor with whirl velocity, C_θ = 150 m/s. "
        "The velocity of rotor vanes, U is 200 m/s. Assuming C_p = 1005 J/(kg·K), "
        "the stagnation temperature rise across the rotor is __________ K "
        "(round off to one decimal place)."
    )


def build_question_text_latex_2024_q40(question_text_plain: str) -> str:
    """Derive LaTeX from clean plain stem (DB question_text is trusted)."""
    t = question_text_plain
    return (
        t.replace("0.83", r"$0.83$")
        .replace("300 K", r"$300\ \mathrm{K}$")
        .replace("10:1", r"$10:1$")
        .replace("20 K", r"$20\ \mathrm{K}$")
        .replace("Cp = 1005 J/kg K", r"$C_p = 1005\ \mathrm{J/(kg\cdot K)}$")
        .replace("gamma = 1.4", r"$\gamma = 1.4$")
    )


def build_search_content(
    question_text: str,
    year: int,
    tier_1: Optional[dict],
    tier_3: Optional[dict],
) -> str:
    """Mirror QuestionRepository._prepare_search_data text join (embedding omitted)."""
    parts: list[str] = [
        str(question_text or ""),
        str(year or ""),
        "",
    ]
    tier1 = tier_1 or {}
    if tier1:
        tags = tier1.get("hierarchical_tags") or {}
        parts.append(str((tags.get("topic") or {}).get("name", "")))
        concepts = [str(c.get("name", "")) for c in (tags.get("concepts") or [])]
        parts.extend(concepts)
        expl = tier1.get("explanation") or {}
        parts.append(str(expl.get("question_nature", "")))
        if expl.get("step_by_step"):
            parts.extend([str(s) for s in expl["step_by_step"] if s])
    tier3 = tier_3 or {}
    keywords = tier3.get("search_keywords") or []
    if keywords:
        parts.extend([str(k) for k in keywords])
    return " | ".join([p for p in parts if p and str(p).strip()])


async def repair_row(conn: AsyncConnection, question_id: str) -> None:
    r = await conn.execute(
        text(
            "SELECT year, tier_3_enhanced_learning, search_content, question_text, question_text_latex, "
            "tier_1_core_research FROM questions WHERE question_id = :qid"
        ),
        {"qid": question_id},
    )
    row = r.mappings().first()
    if not row:
        print(f"skip missing {question_id}")
        return

    search_content = row["search_content"] or ""
    steps = extract_steps_from_search_content(search_content)
    if not steps:
        print(f"warn: no steps parsed for {question_id}")

    t1 = row["tier_1_core_research"]
    if not isinstance(t1, dict):
        t1 = json.loads(t1) if t1 else {}

    if steps:
        exp = t1.setdefault("explanation", {})
        if isinstance(exp, dict):
            exp["step_by_step"] = steps
        av = t1.get("answer_validation")
        if isinstance(av, dict):
            av["reasoning"] = " ".join(steps)

    t1 = deep_repair_strings(t1)

    qtext = row["question_text"] or ""
    qlatex = row["question_text_latex"]

    if question_id == "GATE_2020_AE_Q23":
        qtext = build_question_text_plain_2020_q23()
        qlatex = build_question_text_latex_2020_q23()
    elif question_id == "GATE_2024_AE_Q40":
        qlatex = build_question_text_latex_2024_q40(qtext)
    else:
        qlatex = row["question_text_latex"]

    t3 = row["tier_3_enhanced_learning"]
    if not isinstance(t3, dict):
        t3 = json.loads(t3) if t3 else {}

    new_search = build_search_content(qtext, row["year"], t1, t3)

    t1_json = json.dumps(t1, ensure_ascii=False)
    if "\\1" in t1_json:
        print(f"warn: {question_id} tier_1 still contains literal \\1 after repair")

    await conn.execute(
        text(
            "UPDATE questions SET "
            "question_text = :qt, question_text_latex = :ql, tier_1_core_research = CAST(:t1 AS jsonb), "
            "search_content = :sc, updated_at = :ts "
            "WHERE question_id = :qid"
        ),
        {
            "qt": qtext,
            "ql": qlatex,
            "t1": t1_json,
            "sc": new_search,
            "ts": datetime.utcnow(),
            "qid": question_id,
        },
    )
    print(f"ok {question_id} steps={len(steps)}")


async def main() -> None:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL not set")

    engine = create_async_engine(url)
    async with engine.begin() as conn:
        for qid in QUESTION_IDS:
            await repair_row(conn, qid)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

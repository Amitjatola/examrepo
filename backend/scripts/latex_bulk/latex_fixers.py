"""
Deterministic LaTeX normalization for bulk question data (no ML / no APIs).

Operates on arbitrary strings and on nested JSON (dict/list) structures.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable

# Commands that strongly suggest the string (or tail) is math and may need wrapping.
_MATHISH_CMD = re.compile(
    r"\\(?:frac|sqrt|sum|int|prod|lim|sin|cos|tan|log|ln|exp|alpha|beta|gamma|delta|epsilon|theta|lambda|mu|sigma|omega|pi|infty|partial|nabla|cdot|times|div|pm|mp|leq|geq|neq|approx|equiv|rightarrow|left|right|text)\b",
)

_PROSE_HINT = re.compile(
    r"\b(first|second|then|when|note|use|constants|compute|risk|done|unescaped|the|and|for|with|from|into|"
    r"that|this|are|was|were|comment|half|value|question|answer|option|step|therefore|hence)\b",
    re.I,
)

# obviously broken / noise
_INVALID_SNIPPETS = (
    "\\begin{document}",
    "\\end{document}",
    "\\usepackage",
    "\\documentclass",
)


def fix_unicode_symbols(s: str) -> str:
    """Normalize unicode punctuation that often appears in exam PDFs."""
    if not s:
        return s
    t = (
        s.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("\u00d7", r"\times ")
        .replace("\u00f7", r"\div ")
        .replace("\u03b1", r"\alpha ")
        .replace("\u03b2", r"\beta ")
        .replace("\u03b3", r"\gamma ")
        .replace("\u03b4", r"\delta ")
        .replace("\u03b8", r"\theta ")
        .replace("\u03c0", r"\pi ")
        .replace("\u03a9", r"\Omega ")
    )
    t = unicodedata.normalize("NFKC", t)
    return t


def fix_double_backslashes(obj: Any) -> Any:
    """JSON import often stores `\\\\` where LaTeX needs `\\`."""
    if isinstance(obj, str):
        return obj.replace("\\\\", "\\")
    if isinstance(obj, dict):
        return {k: fix_double_backslashes(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_double_backslashes(v) for v in obj]
    return obj


def _expand_frac_two_single_digits(s: str) -> str:
    """\\frac12 -> \\frac{1}{2} when numerator/denominator are single digits."""

    def repl(m: re.Match[str]) -> str:
        a, b = m.group(1), m.group(2)
        return f"\\frac{{{a}}}{{{b}}}"

    p1 = re.compile(r"\\frac\s*([0-9])\s*([0-9])(?![0-9])")
    s = p1.sub(repl, s)
    p2 = re.compile(r"\\frac\s*([A-Za-z])\s*([A-Za-z])(?![A-Za-z0-9])")
    s = p2.sub(repl, s)
    return s


def _expand_frac_one_braced_one_digit(s: str) -> str:
    """\\frac{1}2 -> \\frac{1}{2}, \\frac1{2} -> \\frac{1}{2}."""
    s = re.sub(
        r"\\frac\s*\{([^{}]+)\}\s*([0-9A-Za-z])(?![0-9A-Za-z])",
        r"\\frac{\1}{\2}",
        s,
    )
    s = re.sub(
        r"\\frac\s*([0-9A-Za-z])\s*\{([^{}]+)\}",
        r"\\frac{\1}{\2}",
        s,
    )
    return s


def expand_frac_shorthand(s: str) -> str:
    s = _expand_frac_two_single_digits(s)
    s = _expand_frac_one_braced_one_digit(s)
    return s


def strip_invalid_latex_declarations(s: str) -> str:
    low = s.lower()
    out = s
    for bad in _INVALID_SNIPPETS:
        if bad.lower() in low:
            out = re.sub(re.escape(bad), "", out, flags=re.IGNORECASE)
    return out


def collapse_math_whitespace_segment(seg: str) -> str:
    """Inside a math span: trim spaces around ^ and _; normalize repeat spaces."""
    seg = re.sub(r"\s*([\^_])\s*", r"\1", seg)
    seg = re.sub(r"\s{2,}", " ", seg)
    return seg.strip()


def _split_dollar_segments(s: str) -> list[tuple[bool, str]]:
    """
    Split on `$` into (is_math, text) runs. Odd runs (index 1,3,...) are math when
    using empty-string convention: segments[0] not math, after first $ math, etc.
    """
    parts = s.split("$")
    out: list[tuple[bool, str]] = []
    for i, p in enumerate(parts):
        is_math = i % 2 == 1
        out.append((is_math, p))
    return out


def process_mixed_dollar_string(s: str) -> str:
    """Apply whitespace collapse in $...$ portions; leave non-math alone."""
    if "$" not in s:
        return s
    segs = _split_dollar_segments(s)
    rebuilt: list[str] = []
    for i, (is_math, seg) in enumerate(segs):
        rebuilt.append(collapse_math_whitespace_segment(seg) if is_math else seg)
    # re-join with $ — note: odd length means trailing unfinished `$` — keep as-is
    out = ""
    for i, (is_math, _) in enumerate(segs):
        out += rebuilt[i]
        if i < len(segs) - 1:
            out += "$"
    return out


def escape_percent_unless_command(s: str) -> str:
    """Bare `%` starts a TeX comment. Prefer `\%` for literal percent (math + text)."""
    # Do not touch \% already
    return re.sub(r"(?<!\\)%", r"\\%", s)


def escape_ampersand_outside_alignment_dummy(s: str) -> str:
    """Escape bare `&` — safe for KaTeX when not building align tables."""
    return re.sub(r"(?<!\\)&", r"\\&", s)


def escape_unescaped_underscores_in_text_runs_between_dollars(s: str) -> str:
    """
    Outside `$...$`, a lone `_` can surprise parsers mixing text+math.
    Escape `_` that is clearly not part of `\_`.
    """
    if "$" not in s:
        return re.sub(r"(?<!\\)_(?![A-Za-z0-9])", r"\_", s)
    segs = _split_dollar_segments(s)
    rebuilt = []
    for is_math, seg in segs:
        if is_math:
            rebuilt.append(seg)
        else:
            rebuilt.append(re.sub(r"(?<!\\)_(?![A-Za-z0-9])", r"\_", seg))
    out = ""
    for i, part in enumerate(rebuilt):
        out += part
        if i < len(rebuilt) - 1:
            out += "$"
    return out


def normalize_sqrt(s: str) -> str:
    """`\\sqrt x` -> `\\sqrt{x}` when x is a single token (digit or letter)."""
    return re.sub(r"\\sqrt\s+([A-Za-z0-9])", r"\\sqrt{\1}", s)


def _key_is_corrupt(k: str) -> bool:
    if not isinstance(k, str):
        return False
    if "$" in k:
        return True
    if "\n" in k or "\r" in k:
        return True
    if k == "t_1$)":
        return True
    return False


def fix_corrupted_dict_keys(obj: Any) -> Any:
    """Rename tier/json keys that accidentally contain math (`$`, `^`) or newlines."""
    if isinstance(obj, dict):
        out: dict[Any, Any] = {}
        used: set[str] = set()
        for k, v in obj.items():
            sk = k if isinstance(k, str) else None
            if sk is not None and _key_is_corrupt(sk):
                idx = 0
                while True:
                    nk = "_recovered_malformed_key" if idx == 0 else f"_recovered_malformed_key_{idx}"
                    idx += 1
                    if nk not in used and nk not in out:
                        break
                vv = fix_corrupted_dict_keys(v)
                if isinstance(vv, str) and not vv.lstrip().startswith("[Recovered from key"):
                    vv = f"[Recovered from key {sk!r}] {vv}"
                out[nk] = vv
                used.add(nk)
            else:
                ks = str(k) if k is not None else k
                if isinstance(ks, str):
                    used.add(ks)
                out[k] = fix_corrupted_dict_keys(v)
        return out
    if isinstance(obj, list):
        return [fix_corrupted_dict_keys(v) for v in obj]
    return obj


def _split_text_middle_dot(s: str) -> str:
    """Turn \\text{kN·s} into \\text{kN}\\cdot\\text{s} (KaTeX: · inside \\text → \\cdotp error)."""
    t = s
    while True:
        m = re.search(r"\\text\{([^{}]*)\u00b7([^{}]*)\}", t)
        if not m:
            break
        rep = f"\\text{{{m.group(1)}}}\\cdot\\text{{{m.group(2)}}}"
        t = t[: m.start()] + rep + t[m.end() :]
    while True:
        m = re.search(r"\\text\{([^{}]*?)\\cdot([^{}]*)\}", t)
        if not m:
            break
        rep = f"\\text{{{m.group(1)}}}\\cdot\\text{{{m.group(2)}}}"
        t = t[: m.start()] + rep + t[m.end() :]
    return t


def _fix_double_braced_simple_cmds(s: str) -> str:
    t = s
    for cmd in ("mathbf", "mathrm", "mathit", "textrm", "textit"):
        t = re.sub("\\\\" + cmd + r"\{\{", "\\\\" + cmd + r"{", t)
        pat = re.compile("\\\\" + cmd + r"\{([^{}]+)\}\}")
        t = pat.sub(lambda m, c=cmd: f"\\{c}{{{m.group(1)}}}", t)
    t = t.replace("\\begin{{vmatrix}}", "\\begin{vmatrix}")
    t = t.replace("\\end{{vmatrix}}", "\\end{vmatrix}")
    return t


def _fix_backslash_dollar_delimiters(s: str) -> str:
    """Turn ``\\$...\\$`` (bad imports) into ``$...$`` so KaTeX extraction sees normal math."""
    if "\\$" not in s:
        return s
    return re.sub(r"\\\$(.+?)\\\$", r"$\1$", s, flags=re.DOTALL)


def fix_katex_compatibility(s: str) -> str:
    """Normalize strings so extracted math fragments pass KaTeX (best-effort)."""
    if not isinstance(s, str) or not s:
        return s
    t = s
    t = _fix_backslash_dollar_delimiters(t)
    t = t.replace("\r\n", "\n").replace("\r", "")
    t = t.replace("\x0c", "")
    t = t.replace("\x08", "")
    t = re.sub(r"-\s*rac\{", r"-\\frac{", t)
    t = t.replace("}ight)", "}\\right)")
    t = t.replace("}ight]", "}\\right]")
    t = re.sub(r"\\\[([A-Z])\\\]", r"[\1]", t)
    t = _split_text_middle_dot(t)
    t = _fix_double_braced_simple_cmds(t)
    t = re.sub(r"m_\\dot\{([^}]*)\}", r"\\dot{m}_{\1}", t)
    t = t.replace("\\omega_n_P", "\\omega_{nP}")
    t = re.sub(r"\\u_(\d)", r"u_{\1}", t)
    t = re.sub(r"C_m_u(?![0-9A-Za-z_])", r"C_{m_u}", t)
    t = re.sub(r"C_m_q(?![0-9A-Za-z_])", r"C_{m_q}", t)
    t = re.sub(r"C_m_\{\\alpha\}", r"C_{m_\\alpha}", t)
    t = re.sub(r"C_m_\{\\dot\{\\alpha\}\}", r"C_{m_{\\dot{\\alpha}}}", t)
    t = re.sub(r"(?<![0-9A-Za-z_])C_N_total(?![0-9A-Za-z_])", r"C_{N,\\text{total}}", t)
    t = re.sub(r"C_l_\\beta", r"C_{l_\\beta}", t)
    t = re.sub(r"C_N_\\beta", r"C_{N_\\beta}", t)
    t = re.sub(r"C_n_\\beta", r"C_{n_\\beta}", t)
    t = re.sub(r"C_n_\{\\beta\}", r"C_{n_\\beta}", t)
    t = re.sub(r"C_L_\{max\}", r"C_{L,\\max}", t)
    t = re.sub(r"C_\{L_\\delta_a\}", r"C_{L_{\\delta_a}}", t)
    t = re.sub(r"C_\{n_\\delta_r\}", r"C_{n_{\\delta_r}}", t)
    t = re.sub(r"C_\{n_\\beta\}", r"C_{n_\\beta}", t)
    t = re.sub(r"V_c_\{max\}", r"V_{c,\\max}", t)
    t = re.sub(r"C_F_m(?![0-9A-Za-z_])", r"C_{F,m}", t)
    t = re.sub(r"C_F_p(?![0-9A-Za-z_])", r"C_{F,p}", t)
    t = re.sub(r"\(C_\{n_\\beta\}\)_\{vertical\\_tail\}", r"(C_{n_\\beta})_{\\text{vertical tail}}", t)
    t = re.sub(r"V_\\inf", r"V_{\\infty}", t)
    t = re.sub(r"p_\\inf", r"p_{\\infty}", t)
    t = re.sub(r"\\rho_\\inf", r"\\rho_{\\infty}", t)
    t = re.sub(r"c_\\bar\\b", r"\\bar{c}", t)
    t = re.sub(r"c\\_\\bar", r"\\bar{c}", t)
    t = re.sub(r"c_\\bar(?![a-zA-Z])", r"\\bar{c}", t)
    t = re.sub(r"\\partial2w/\\partialx2", r"\\partial^2 w/\\partial x^2", t)
    t = re.sub(r"\\partialx\\b", r"\\partial x", t)
    t = re.sub(r"\\nWhere", r" \\text{Where: } ", t)
    t = t.replace("\\cdot  abla", "\\cdot \\nabla")
    t = t.replace("(\\mathbf{A} \\cdot  abla)", "(\\mathbf{A} \\cdot \\nabla)")
    t = t.replace("(\\mathbf{a} \\cdot  abla)", "(\\mathbf{a} \\cdot \\nabla)")
    t = t.replace("(\\boldsymbol{\\omega} \\cdot  abla)", "(\\boldsymbol{\\omega} \\cdot \\nabla)")
    t = t.replace("(\\mathbf{V} \\cdot  abla)", "(\\mathbf{V} \\cdot \\nabla)")
    t = re.sub(
        r"\\frac\{\\partial (\\mathbf\{[A-Za-z]\})\{\\partial ([a-z])\}",
        r"\\frac{\\partial \1}{\\partial \2}",
        t,
    )
    t = re.sub(
        r"\\frac\{\\partial (\\mathbf\{[A-Za-z]\})\{(\\partial [^}]+)\}",
        r"\\frac{\\partial \1}{\2}",
        t,
    )
    t = re.sub(r"\\frac\{D(\\mathbf\{[A-Za-z]\})\{Dt\}", r"\\frac{D\1}{Dt}", t)
    t = re.sub(r"\\frac\{d(\\mathbf\{[A-Za-z]\})\{d\\theta\}", r"\\frac{d\1}{d\\theta}", t)
    t = re.sub(
        r"\\frac\{\\mathbf\{([A-Za-z])\} \\cdot \\mathbf\{([A-Za-z])\}\{\|",
        r"\\frac{\\mathbf{\1} \\cdot \\mathbf{\2}}{|",
        t,
    )
    t = re.sub(r"\\dot\{\\mathbf\{x\} =", r"\\dot{\\mathbf{x}} =", t)
    t = re.sub(
        r"\\text\{proj\}\\_\{\\mathbf\{b\}\(\\mathbf\{a\}\) = \\frac\{\\mathbf\{a\} \\cdot \\mathbf\{b\}\{\|",
        r"\\text{proj}_{\\mathbf{b}}(\\mathbf{a}) = \\frac{\\mathbf{a} \\cdot \\mathbf{b}}{|",
        t,
    )
    t = re.sub(
        r"\\hat\{n\} = \\frac\{\\mathbf\{v\}\{\|\\mathbf\{v\}\|\}",
        r"\\hat{n} = \\frac{\\mathbf{v}}{|\\mathbf{v}|}",
        t,
    )
    t = re.sub(
        r"\\text\{Unit vector in direction of \} \\mathbf\{A\} = \\frac\{\\mathbf\{A\}\{\|",
        r"\\text{Unit vector in direction of } \\mathbf{A} = \\frac{\\mathbf{A}}{|",
        t,
    )
    t = re.sub(
        r"\\hat\{u\} = \\frac\{\\mathbf\{v\}\{\|\\mathbf\{v\}\|\}",
        r"\\hat{u} = \\frac{\\mathbf{v}}{|\\mathbf{v}|}",
        t,
    )
    t = re.sub(
        r"d\\mathbf\{s\} = \\frac\{d\\mathbf\{r\}\{d\\theta\} d\\theta",
        r"d\\mathbf{s} = \\frac{d\\mathbf{r}}{d\\theta} d\\theta",
        t,
    )
    t = re.sub(r"\\hat\{\\mathbf\{([ijk])\} \+", r"\\hat{\\mathbf{\1}} +", t)
    t = re.sub(r"-\\hat\{\\mathbf\{([ijk])\} \+", r"-\\hat{\\mathbf{\1}} +", t)
    t = re.sub(
        r"\\text\{Stoichiometric Air-to-Fuel Ratio \}\(\\text\{AFR\}\\_\{\\text\{stoic\}\}\) = \\frac\{1\}\{\\text\{f_stoic\}\}",
        r"\\text{Stoichiometric Air-to-Fuel Ratio }(\\text{AFR}_{\\text{stoic}}) = \\frac{1}{\\text{f}_{\\text{stoic}}}",
        t,
    )
    t = re.sub(
        r"C_N_total = C_N_beta \* beta \+ C_N_delta_R \* delta_R = 0",
        r"C_{N,\\text{total}} = C_{N_\\beta} \\beta + C_{N_{\\delta_R}} \\delta_R = 0",
        t,
    )
    t = re.sub(r"(?<![A-Za-z0-9_])C_N_beta(?![A-Za-z0-9_])", r"C_{N_\\beta}", t)
    t = re.sub(r"(?<![A-Za-z0-9_])C_N_delta_R(?![A-Za-z0-9_])", r"C_{N_{\\delta_R}}", t)
    t = re.sub(r"\\frac\{1\}\{\\text\{f_stoic\}\}", r"\\frac{1}{\\text{f}_{\\text{stoic}}}", t)
    t = t.replace(
        r"\rho V^2 = 1.22 \times (90)^2 = 9882 \ \text{kg/(m}\cdot\text{ s^2)}",
        r"\rho V^2 = 1.22 \times (90)^2 = 9882\ \text{kg/(m}\cdot\text{s)}^2",
    )
    t = re.sub(
        r"V_\{max\} = \\sqrt\{1407000 \\text\{ m\^\{2\}/s\^\{2\}\}\}",
        r"V_{max} = \\sqrt{1407000}\\,\\text{m}^{2}/\\text{s}^{2}",
        t,
    )
    t = re.sub(
        r"\\frac\{dC_\{m,\\mathrm\{cg\}\}\{d\\alpha_a\}",
        r"\\frac{dC_{m,\\mathrm{cg}}}{d\\alpha_a}",
        t,
    )
    t = re.sub(
        r"\\frac\{dC_\{m,\\mathrm\{cg\}\}\{d\\alpha_a\} < 0",
        r"\\frac{dC_{m,\\mathrm{cg}}}{d\\alpha_a} < 0",
        t,
    )
    t = re.sub(
        r"C_\{m,\\mathrm\{cg\}\}\(\\alpha_\{a,e\}\) = 0",
        r"C_{m,\\mathrm{cg}}(\\alpha_{a,e}) = 0",
        t,
    )
    t = re.sub(
        r"C_\{m,\\mathrm\{cg\}\(\\alpha_\{a,e\}\) = 0",
        r"C_{m,\\mathrm{cg}}(\\alpha_{a,e}) = 0",
        t,
    )
    t = t.replace(
        r"\text{proj}\_{\mathbf{b}(\mathbf{a}) = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{b}|^2} \mathbf{b}",
        r"\text{proj}_{\mathbf{b}}(\mathbf{a}) = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{b}|^2} \mathbf{b}",
    )
    t = t.replace("\\text{proj}\\_{\\mathbf{b}}", "\\text{proj}_{\\mathbf{b}}")
    t = t.replace("M^2$$2.", "M^2$\n\n2.")
    t = t.replace("given condition$(", "given condition $ (")
    t = t.replace("Let$(", "Let $ (")
    t = t.replace("$M_A$and$M_B$", r"$M_A$ and $M_B$")
    t = t.replace("Therefore,$", "Therefore, $")
    t = t.replace("For location A:$", "For location A: $")
    t = t.replace("For location B:$", "For location B: $")
    t = t.replace("B:$$", "B:\n\n$$")
    t = t.replace("relation:$$", "relation:\n\n$$")
    t = t.replace("equation for B:$$", "equation for B:\n\n$$")
    t = t.replace("derived relation:$$", "derived relation:\n\n$$")
    t = t.replace("V_{max} = \\sqrt{1407000 \\text{ m^{2}/s^{2}}}", "V_{max} = \\sqrt{1407000 \\,\\text{m}^2/\\text{s}^2}")
    t = t.replace(
        "V_{max} = \\sqrt{1407000 \\text{ m\\textsuperscript{2}/s\\textsuperscript{2}}}",
        "V_{max} = \\sqrt{1407000 \\,\\text{m}^2/\\text{s}^2}",
    )
    t = t.replace(
        r"$V_{max} = \sqrt{1407000 \text{ m^{2}/s^{2}}}$",
        r"$V_{max} = \sqrt{1407000 \,\text{m}^2/\text{s}^2}$",
    )
    t = t.replace(
        r"$\frac{dC\_{m,\mathrm{cg}}{d\alpha_a} < 0$",
        r"$\frac{dC_{m,\mathrm{cg}}}{d\alpha_a} < 0$",
    )
    t = t.replace(
        r"$C\_{m,\mathrm{cg}}(\alpha\_{a,e}) = 0$",
        r"$C_{m,\mathrm{cg}}(\alpha_{a,e}) = 0$",
    )
    t = t.replace(
        r"$C_{m,\mathrm{cg}(\alpha_{a,e}) = 0$",
        r"$C_{m,\mathrm{cg}}(\alpha_{a,e}) = 0$",
    )
    t = t.replace(",\\mathrm{cg}(\\alpha", ",\\mathrm{cg}}(\\alpha")
    t = t.replace(
        "dS = |\\frac{\\partial \\mathbf{r}{\\partial \\phi} \\times \\frac{\\partial \\mathbf{r}{\\partial \\theta}|",
        "dS = \\left|\\frac{\\partial \\mathbf{r}}{\\partial \\phi} \\times \\frac{\\partial \\mathbf{r}}{\\partial \\theta}\\right|",
    )
    t = t.replace("\\zeta =  abla \\times", "\\zeta = \\nabla \\times")
    t = re.sub(r"\\hat\{\\mathbf\{([ijk])\}(?!\})", r"\\hat{\\mathbf{\1}}", t)
    t = t.replace("[M]\\ddot{\\mathbf{x} + [K]\\mathbf{x}", "[M]\\ddot{\\mathbf{x}} + [K]\\mathbf{x}")
    t = t.replace("[M] \\ddot{\\mathbf{x} + [K] \\mathbf{x}", "[M] \\ddot{\\mathbf{x}} + [K] \\mathbf{x}")
    t = re.sub(r"\\frac\{d\\mathbf\{A\}\{dt\}\|_\{inertial\}", r"\\frac{d\\mathbf{A}}{dt}\\big|_{\\text{inertial}}", t)
    t = re.sub(r"\\frac\{d\\mathbf\{A\}\{dt\}\|_\{rot\}", r"\\frac{d\\mathbf{A}}{dt}\\big|_{\\text{rot}}", t)
    t = t.replace(
        "\\frac{d\\mathbf{A}{dt}\\big|_{\\text{inertial}}",
        "\\frac{d\\mathbf{A}}{dt}\\big|_{\\text{inertial}}",
    )
    t = t.replace(
        "\\frac{d\\mathbf{A}{dt}\\big|_{\\text{rot}}",
        "\\frac{d\\mathbf{A}}{dt}\\big|_{\\text{rot}}",
    )
    t = re.sub(
        r" \+ \\boldsymbol\{\\omega\} \\times \\mathbf\{A\}",
        r"+ \\boldsymbol{\\omega} \\times \\mathbf{A}",
        t,
    )
    t = re.sub(r"\*\*([^*]{2,120})\*\*", r"\1", t)
    t = t.replace("\\minus", "-")
    t = t.replace("Up\\-Away, Down\\-Towards", r"Up-Away, Down-Towards")
    t = re.sub(r"\\textsuperscript\{2\}", r"^{2}", t)
    t = re.sub(r"m/s\\textsuperscript\{2\}", r"m/s^{2}", t)
    t = re.sub(r"g = 9\.81 m/s\\textsuperscript\{2\}", r"g = 9.81\\ \\text{m/s}^{2}", t)
    t = re.sub(r"M\\textsubscript\{\\infty\}", r"M_{\\infty}", t)
    t = re.sub(r"M\\\\textsubscript\{\\\{\\\\infty\\\}\}", r"M_{\\infty}", t)
    t = re.sub(r"M\\textsubscript\{\\infty\}", r"M_{\\infty}", t)
    t = re.sub(
        r"\\frac\{P\\_\{0,2\}\}\{P\\_\{0,1\}\}\\_\\text\{oblique shocks\}\s*>\s*"
        r"\\frac\{P\\_\{0,2\}\}\{P\\_\{0,1\}\}\\_\\text\{normal shock at M_1\}",
        r"\\frac{P_{0,2}}{P_{0,1}}\\bigg|_{\\text{oblique}} > \\frac{P_{0,2}}{P_{0,1}}\\bigg|_{\\text{normal},\\, M_1}",
        t,
    )
    t = re.sub(
        r"\\text\{f_([a-zA-Z0-9_]+)\}(?=[^\}])",
        lambda m: f"\\text{{f}}_{{\\text{{{m.group(1)}}}}}",
        t,
    )
    t = re.sub(
        r"\\text\{Stoichiometric Air-to-Fuel Ratio \(AFR_stoic\)\}",
        r"\\text{Stoichiometric Air-to-Fuel Ratio }(\\text{AFR}_{\\text{stoic}})",
        t,
    )
    t = re.sub(
        r"\\phi = \\frac\{\\text\{f_actual\}\}\{\\text\{f_stoic\}\}",
        r"\\phi = \\frac{\\text{f}_{\\text{actual}}}{\\text{f}_{\\text{stoic}}}",
        t,
    )
    t = re.sub(
        r"\\text\{f_stoic\} = \\frac\{\\dot\{m\}_f\}\{\\dot\{m\}_a\} \\Big\|\\_\{\\text\{stoichiometric\}\}\}",
        r"\\text{f}_{\\text{stoic}} = \\frac{\\dot{m}_f}{\\dot{m}_a} \\Big|_{\\text{stoichiometric}}",
        t,
    )
    lap = (
        "L\\{{a \\cdot g(t) + b \\cdot h(t)}\\} = a \\cdot L\\{{g(t)}\\} + b \\cdot L\\{{h(t)}\\}}"
    )
    lap_fix = (
        "L\\left\\{a \\cdot g(t) + b \\cdot h(t)\\right\\} = a \\cdot L\\left\\{g(t)\\right\\} + "
        "b \\cdot L\\left\\{h(t)\\right\\}"
    )
    t = t.replace(lap, lap_fix)
    t = re.sub(r"Nozzle exit velocity \(V_\{s1\}\)", r"Nozzle exit velocity (V_{s1})", t)
    s_trunc = "V\\_{s1"
    if t.strip() == s_trunc or t.strip() == "V_{s1":
        t = "V_{s1}"
    t = re.sub(r"\$\$([0-9]+\.)", r"$$\n\n\1", t)
    t = re.sub(r"\$\$([A-Za-z])", r"$$\n\n\1", t)
    t = re.sub(r"condition\$\(", r"condition $(", t)
    t = re.sub(r"Let\$\(", r"Let $(", t)
    t = t.replace("M^2$$2.", "M^2$$\n\n2.")
    t = re.sub(r"between\$M_A\$and\$M_B\$", r"between $M_A$ and $M_B$", t)
    t = re.sub(r"equation for B:\$\$\\frac", r"equation for B:\n\n$$\\frac", t)
    t = re.sub(r"derived relation:\$\$\\frac", r"derived relation:\n\n$$\\frac", t)
    t = re.sub(r":\$\(", r": $(", t)
    t = re.sub(r"for A:\$\(", r"for A: $(", t)
    t = re.sub(r"B:\$\(", r"B: $(", t)
    t = re.sub(r"B:\$\(", r"B: $(", t)
    t = re.sub(r"\$\$This", r"$$\n\nThis", t)
    t = re.sub(r"M\^2\$\$2\.", r"M^2$$\n\n2.", t)
    t = re.sub(r"\\mathbf\{A\} \\times \\mathbf\{B\} = \\begin\{vmatrix\}", r"\\mathbf{A} \\times \\mathbf{B} = \\begin{vmatrix}", t)
    t = re.sub(
        r"div\(grad \\\(\\phi\\\)\)=\\\(\\nabla\^2\\phi\\\)",
        r"\\operatorname{div}(\\operatorname{grad}\\phi)=\\nabla^2\\phi",
        t,
    )
    t = re.sub(r"Sideslip Angle \(\\\(\\beta\\\)\)", r"Sideslip Angle ($\\beta$)", t)
    t = re.sub(r"\* \(l_v / b\)", r"\\cdot (l_v / b)", t)
    t = re.sub(r"\(dC_Y_v / d\(\\beta\)\)", r"(\\partial C_{Y_v}/\\partial\\beta)", t)
    t = re.sub(r"\(\\beta\)\)", r"(\\beta)", t)
    for _ in range(4):
        t2 = re.sub(r"\\\(([^()]*?)\\\)", r"\1", t)
        if t2 == t:
            break
        t = t2
    t = re.sub(r"([^\n])\\n(?=[A-Za-z])", r"\1 ", t)
    t = re.sub(r"\\n\\frac", r" \\frac", t)
    t = re.sub(r"\\nTurn", r" \\text{Turn}", t)
    t = re.sub(r":\\n-", r":; ", t)
    t = re.sub(r"\\n-", r"; ", t)
    t = re.sub(
        r"\\text\{Station-Keeping \\, \\Delta V\}",
        r"\\text{Station-Keeping}\\,\\Delta V",
        t,
    )
    t = re.sub(r"(Turn Rate:[^\n]+)\\n\s*Turn Radius:", r"\1 \\quad \\text{Turn Radius:}", t)
    t = t.replace("= 0 \\n\\frac{", "= 0 \\\\ \\frac{")
    t = re.sub(
        r"\\frac\{\\partial \\sigma\\_\{xx\}\}\{\\partial x\} \+ \\frac\{\\partial \\tau\\_\{xy\}\}\{\\partial y\} = 0 \\n",
        r"\\frac{\\partial \\sigma_{xx}}{\\partial x} + \\frac{\\partial \\tau_{xy}}{\\partial y} = 0 \\\\ ",
        t,
    )
    t = re.sub(
        r"\\nabla p = \\frac\{\{\\partial p\}\}\{\{\\partial x\}\}\\mathbf\{i\} \+ \\frac\{\{\\partial p\}\}\{\{\\partial y\}\}\\mathbf\{j\}\} \+ \\frac\{\{\\partial p\}\}\{\{\\partial z\}\}\\mathbf\{k\}",
        r"\\nabla p = \\frac{\\partial p}{\\partial x}\\mathbf{i} + \\frac{\\partial p}{\\partial y}\\mathbf{j} + \\frac{\\partial p}{\\partial z}\\mathbf{k}",
        t,
    )
    t = re.sub(
        r"V_2 = \\sqrt\{\\frac\{2\(p_1 - p_2\)\}\{\\rho \\left\[1 - \\left\(\\frac\{A_2\}\{A_1\}\right\)\^2\\right\]\}\}",
        r"V_2 = \\sqrt{\\frac{2(p_1 - p_2)}{\\rho \\left[1 - \\left(\\frac{A_2}{A_1}\\right)^2\\right]}}",
        t,
    )
    t = re.sub(
        r"\\theta = \\int_0\^\\delta \\frac\{u\(y\)\}\{U\} \\left\(1 - \\frac\{u\(y\)\}\{U\}\right\) dy",
        r"\\theta = \\int_0^\\delta \\frac{u(y)}{U} \\left(1 - \\frac{u(y)}{U}\\right) dy",
        t,
    )
    t = re.sub(
        r"\\mu = \\mu_0 \\left\(\\frac\{T\}\{T_0\}\right\)\^\{3/2\} \\left\(\\frac\{T_0 \+ S\}\{T \+ S\}\\right\)",
        r"\\mu = \\mu_0 \\left(\\frac{T}{T_0}\\right)^{3/2} \\left(\\frac{T_0 + S}{T + S}\\right)",
        t,
    )
    t = re.sub(
        r"\\frac\{u\(y\)\}\{U\\_\\infty\} = \\frac\{3y\}\{2\\delta\} - \\frac\{1\}\{2\}\\left\(\\frac\{y\}\{\\delta\}\\right\)\^3",
        r"\\frac{u(y)}{U_\\infty} = \\frac{3y}{2\\delta} - \\frac{1}{2}\\left(\\frac{y}{\\delta}\\right)^3",
        t,
    )
    for _ in range(12):
        t2 = re.sub(r"(?<=[A-Za-z0-9])\\_\{([^}]*)\}", r"_{\1}", t)
        if t2 == t:
            break
        t = t2
    t = re.sub(r"\\dot\{\\mathbf\{([ux])\}\(([^)]*)\)", r"\\dot{\\mathbf{\1}}(\2)", t)
    t = re.sub(r"\\frac\{\\mathbf\{([rN])\}\{", r"\\frac{\\mathbf{\1}}{", t)
    t = re.sub(
        r"\\frac\{2\\mathbf\{i\} - 4\\mathbf\{j\}\{2",
        r"\\frac{2\\mathbf{i} - 4\\mathbf{j}}{2",
        t,
    )
    t = t.replace(
        "[M] \\ddot{\\mathbf{x} + [K] \\mathbf{x} = 0",
        "[M] \\ddot{\\mathbf{x}} + [K] \\mathbf{x} = 0",
    )
    t = re.sub(r"\\dot\{\\mathbf\{x\}\(0\)", r"\\dot{\\mathbf{x}}(0)", t)
    t = re.sub(
        r"B_i = \(\\mathbf\{\\phi\}_i\^T \\mathbf\{M\} \\dot\{\\mathbf\{u\}\(0\)\)\)",
        r"B_i = (\\mathbf{\\phi}_i^T \\mathbf{M} \\dot{\\mathbf{u}}(0))",
        t,
    )
    t = _strip_trailing_spurious_backslash(t)
    return t


def _strip_trailing_spurious_backslash(t: str) -> str:
    """Remove trailing LaTeX linebreak `\\\\` or lone `\\` that KaTeX rejects at EOF."""
    u = t.rstrip()
    while u.endswith("\\\\"):
        u = u[:-2].rstrip()
    if len(u) >= 2 and u.endswith("\\") and not u.endswith("\\\\"):
        tail = u[:-1]
        if re.search(r"[0-9A-Za-z\)\]\}]$", tail):
            u = tail.rstrip()
    return u


def auto_wrap_pure_mathish_line(s: str, enabled: bool) -> str:
    """
    If there is no `$` but the trimmed line clearly looks like a formula, wrap once.
    Conservative: mostly ascii math tokens + backslash commands, short lines.
    """
    if not enabled:
        return s
    t = s.strip()
    if not t or "$" in t or "\\[" in t or "\\]" in t or "```" in t:
        return s
    if not _MATHISH_CMD.search(t):
        return s
    if len(t) > 400:
        return s
    # Heavier prose heuristics (avoid wrapping explanations / hints)
    if _PROSE_HINT.search(t):
        return s
    if t.count(" ") > 2:
        return s
    if re.fullmatch(r"[\s0-9A-Za-z\.,'\+\-\*/=\\()\[\]_{}^:|<>]+", t) is None:
        return s
    if t.startswith("$") and t.endswith("$"):
        return s
    return f"${t}$"


def fix_string(
    s: str,
    *,
    auto_wrap: bool,
) -> str:
    if not isinstance(s, str):
        return s
    chain: list[Callable[[str], str]] = [
        fix_unicode_symbols,
        fix_katex_compatibility,
        strip_invalid_latex_declarations,
        expand_frac_shorthand,
        normalize_sqrt,
        lambda x: process_mixed_dollar_string(x) if "$" in x else x,
        # spacing-like cleanup outside dollars for common `x ^ 2` without dollars
        lambda x: re.sub(
            r"(?<![\w\\])([A-Za-z0-9])\s+\^\s+\{",
            r"\1^{",
            x,
        ),
        lambda x: re.sub(
            r"(?<![\w\\])([A-Za-z0-9])\s+\^\s+([0-9A-Za-z])",
            r"\1^\2",
            x,
        ),
        escape_percent_unless_command,
        escape_ampersand_outside_alignment_dummy,
        escape_unescaped_underscores_in_text_runs_between_dollars,
        lambda x: auto_wrap_pure_mathish_line(x, auto_wrap),
        _strip_trailing_spurious_backslash,
    ]
    out = s
    for fn in chain:
        out = fn(out)
    return out


def walk_json_strings(
    obj: Any,
    *,
    auto_wrap: bool,
) -> Any:
    if isinstance(obj, str):
        return fix_string(obj, auto_wrap=auto_wrap)
    if isinstance(obj, dict):
        return {k: walk_json_strings(v, auto_wrap=auto_wrap) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk_json_strings(v, auto_wrap=auto_wrap) for v in obj]
    return obj


def apply_full_pipeline(obj: Any, *, auto_wrap: bool = True) -> Any:
    """Rename corrupt JSON keys, collapse JSON escaping, then string normalization."""
    fixed = fix_corrupted_dict_keys(obj)
    fixed = fix_double_backslashes(fixed)
    return walk_json_strings(fixed, auto_wrap=auto_wrap)

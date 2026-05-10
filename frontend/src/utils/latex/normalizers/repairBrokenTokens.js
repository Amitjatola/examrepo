/**
 * Some option payloads lose backslashes/braces (e.g. "dfracomega4 mathrmrad s^-1").
 * Rebuild command prefixes so downstream math wrapping can render with KaTeX.
 */
export const repairBrokenTokens = (raw) => {
    const s0 = String(raw ?? '')
    if (!s0) return s0
    if (/\$/.test(s0)) return s0

    const hasFractionWord = /\b(dfrac|frac|tfrac)\b/i.test(s0)
    const hasMathWord = /\b(mathrm|omega|theta|alpha|beta|gamma|delta|pi|lambda|mu|phi)\b/i.test(s0)
    if (!hasFractionWord && !hasMathWord) return s0

    let s = s0
    s = s.replace(
        /\b(dfrac|frac|tfrac|sqrt|mathrm|text|sin|cos|tan|log|ln|exp|omega|theta|alpha|beta|gamma|delta|pi|lambda|mu|phi)\b/g,
        '\\$1'
    )
    s = s.replace(/\\(dfrac|frac|tfrac)\s*\\([a-zA-Z]+)\s*([0-9]+(?:\.[0-9]+)?)/g, '\\$1{\\$2}{$3}')
    s = s.replace(/\\(dfrac|frac|tfrac)\s*\\([a-zA-Z]+)\s*\\([a-zA-Z]+)/g, '\\$1{\\$2}{\\$3}')
    s = s.replace(/\\mathrm\s*([a-zA-Z]+)/g, '\\mathrm{$1}')
    return s
}

/**
 * Legacy MCQ payloads sometimes insert a bogus `$` after a digit before "and/or/&",
 * e.g. `0$ and $\\sqrt{k}{m}` breaks `$...$` pairing and leaves TeX bare.
 * Rewrites to `0 and $\\sqrt{k}{m}` when the delimiter after `and` starts real TeX (`\`).
 */

const STRAY_DOLLAR_BEFORE_CONJ_RE =
    /(?<![0-9.])(?<![_^])(\d)\$\s*(?:,\s*)?(\band\b|\bor\b|&)\s*\$(?=\\)/gi

export const fixStrayDollarAfterDigit = (raw) => {
    const s = String(raw ?? '')
    if (!/\d\$[\s\S]*?\$\s*\\/s.test(s)) return s
    return s.replace(STRAY_DOLLAR_BEFORE_CONJ_RE, (_m, digit, conj) => `${digit} ${conj} $`)
}

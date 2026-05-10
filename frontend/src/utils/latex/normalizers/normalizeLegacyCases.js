import { TEXT_CMD_MARK } from '../constants.js'

/**
 * Legacy DB strings: leading \text{prose} then raw \frac{u}{U}=\begin{cases} ... row break_missing ...
 */
const stripFirstTextBraceProsePrefix = (s) => {
    const t = String(s ?? '').trimStart()
    if (!t.startsWith(TEXT_CMD_MARK)) return s
    const innerStart = TEXT_CMD_MARK.length
    let j = innerStart
    let depth = 1
    while (j < t.length && depth > 0) {
        const ch = t[j]
        if (ch === '{') depth += 1
        else if (ch === '}') depth -= 1
        j += 1
    }
    if (depth !== 0) return s
    const inner = t.slice(innerStart, j - 1)
    let rest = t.slice(j)
    rest = rest.replace(/^\s*\\\s*/, ' ')
    return `${inner.trimEnd()} ${rest.trimStart()}`
}

export const normalizeLegacyCases = (raw) => {
    let s = String(raw ?? '')
    if (!s.includes('\\begin{cases}')) return raw

    const t0 = s.trimStart()
    const looksLegacy =
        t0.startsWith(TEXT_CMD_MARK) ||
        s.includes('\\\\text{') ||
        /\\delta\s*\\\s+1/.test(s)

    if (!looksLegacy) return raw

    if (t0.startsWith(TEXT_CMD_MARK)) s = stripFirstTextBraceProsePrefix(s)

    s = s.replace(/\\\\text\{/g, '\\text{')

    s = s.replace(/(\\delta)\s*\\\s+1(\s*&)/g, '$1 \\\\ 1$2')

    if (!/\$\$[\s\S]*\\begin\{cases\}/.test(s) && !/\\\[[\s\S]*\\begin\{cases\}/.test(s)) {
        // Replacement: each `$$` in a string inserts one `$`; use `$$$$` for literal `$$`.
        s = s.replace(/((?:\\frac|\\dfrac)\{u\}\{U\}\s*=[\s\S]*?\\end\{cases\})/g, '$$$$$1$$$$')
    }

    return s
}

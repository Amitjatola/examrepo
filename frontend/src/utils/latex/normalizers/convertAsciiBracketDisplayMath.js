/**
 * Some stems use "[" ... "]" for multi-line expressions instead of $$ or \[.
 * When the interior is clearly TeX (\sigma, \tau, etc.), wrap as display math $$...$$ so KaTeX runs.
 */

const HAS_DISPLAY_TEX_SIGNAL =
    /\\(?:sigma|tau|varepsilon)(?![a-z])|\\(?:quad|ldots|cdots|dots|cdot|times|partial|nabla)\b|\\begin\{[a-zA-Z*]+\}/i

/** Inner must read as math, not prose like "[see below]" */
const bracketInnerLooksLikeTex = (inner) => {
    const t = String(inner || '').trim()
    if (t.length < 3 || !/^[\s\S]*\\[a-zA-Z]+[\s\S]*$/.test(t)) return false
    if (!HAS_DISPLAY_TEX_SIGNAL.test(t)) return false
    /** Skip markdown-style links "[label](http..." */
    if (/\]\s*\(\s*https?:\/\//m.test(inner)) return false
    return true
}

export const convertAsciiBracketDisplayMath = (raw) => {
    const s = String(raw ?? '')
    if (!s.includes('[') || !/\\(?:sigma|tau|varepsilon)(?![a-z])|\\begin\{|\s\\quad/.test(s)) return s

    let out = ''
    let i = 0
    while (i < s.length) {
        const open = s.indexOf('[', i)
        if (open === -1) {
            out += s.slice(i)
            break
        }
        out += s.slice(i, open)
        const innerStart = open + 1
        let depth = 0
        let j = innerStart
        while (j < s.length) {
            const ch = s[j]
            if (ch === '{') depth += 1
            else if (ch === '}') depth = Math.max(0, depth - 1)
            else if (ch === ']' && depth === 0) break
            j += 1
        }
        if (j >= s.length) {
            out += s[open]
            i = open + 1
            continue
        }
        const inner = s.slice(innerStart, j)
        if (bracketInnerLooksLikeTex(inner)) {
            out += `$$${inner.trim()}$$`
        } else {
            out += s.slice(open, j + 1)
        }
        i = j + 1
    }
    return out
}

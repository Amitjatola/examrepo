import { MAX_ASSIGNMENT_LIST_LENGTH } from '../constants.js'

/**
 * Legacy rows: comma-separated assignment list with TeX but no $...$.
 */
export const wrapBareAssignmentList = (raw) => {
    const s0 = String(raw ?? '')
    const s = s0.trim()
    if (!s) return s0
    if (/\$|\\\[/.test(s)) return s0
    if (s.length > MAX_ASSIGNMENT_LIST_LENGTH) return s0
    if (/[.!?][\s\n][A-Za-z]/.test(s)) return s0
    const eqCount = (s.match(/=/g) || []).length
    if (eqCount < 2) return s0
    const hasLatexCmd = /\\[a-zA-Z]+/.test(s)
    const hasSub = /_\{/.test(s)
    if (!hasLatexCmd && !hasSub) return s0

    let t = s.replace(/\bV\{exit\}/g, 'V_{\\text{exit}}')
    t = t.replace(/\b([A-Za-z])\{([a-z]{1,12})\}(?=\s*[=,)])/g, (_m, a, b) => `${a}_{\\text{${b}}}`)
    return `$${t}$`
}

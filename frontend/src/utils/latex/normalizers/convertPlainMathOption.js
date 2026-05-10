import {
    MAX_PLAIN_MATH_OPTION_LENGTH,
    MAX_PLAIN_MATH_WORDS,
    PLAIN_MATH_KEYWORD_RE,
    SPELLED_WORD_TO_LATEX
} from '../constants.js'

const inlineSpelledMathTokens = (src) => {
    let out = src.replace(/\bsqrt\(([^)]+)\)/g, '$\\sqrt{$1}$')
    for (const [word, latex] of Object.entries(SPELLED_WORD_TO_LATEX)) {
        const re = new RegExp(`\\b${word}\\b`, 'g')
        out = out.replace(re, `$${latex}$`)
    }
    return out
}

/**
 * Short option strings stored as plain-text math without LaTeX markup.
 */
export const convertPlainMathOption = (raw) => {
    const s0 = String(raw ?? '')
    const s = s0.trim()
    if (!s || s.length > MAX_PLAIN_MATH_OPTION_LENGTH) return s0
    if (/\$|\\[a-zA-Z]/.test(s)) return s0
    if (/[.!?]\s+[A-Z]/.test(s)) return s0
    const words = s.split(/\s+/)
    if (words.length > MAX_PLAIN_MATH_WORDS) return s0
    const hasMathKeyword = PLAIN_MATH_KEYWORD_RE.test(s)
    const hasMathOp = /[/^*=<>]/.test(s) || /\d+\s+[a-zA-Z]{1,4}\b/.test(s)
    if (!hasMathKeyword && !hasMathOp) return s0

    if (hasMathKeyword && !hasMathOp) {
        return inlineSpelledMathTokens(s)
    }

    if (hasMathKeyword && (words.length > 5 || (words.length >= 4 && /\b(the|a|an)\b/i.test(s)))) {
        return inlineSpelledMathTokens(s)
    }

    if (hasMathOp && /\bdeg\b/i.test(s)) {
        const chunks = s.split(/\s+and\s+/i).map((c) => c.trim()).filter(Boolean)
        const chunkToMath = (chunk) => {
            const p = chunk.replace(/\bdeg\b/gi, '^\\circ').replace(/\s+/g, '')
            return `$${p}$`
        }
        return chunks.map(chunkToMath).join(' and ')
    }

    let t = s.replace(/\bsqrt\(([^)]+)\)/g, '\\sqrt{$1}')
    for (const [word, latex] of Object.entries(SPELLED_WORD_TO_LATEX)) {
        const re = new RegExp(`\\b${word}\\b`, 'g')
        t = t.replace(re, latex)
    }
    t = t.replace(/\^(\d+)/g, '^{$1}')
    t = t.replace(/\^([a-zA-Z])/g, '^{$1}')
    return `$${t}$`
}

import {
    DOLLAR_COUNT_ABORT_UNWRAP,
    HEAD_MIN_LENGTH_THRESHOLD,
    HEAD_PROSE_WORD_THRESHOLD,
    MID_WORDS_PR_THRESHOLD,
    MID_WORDS_SP_THRESHOLD,
    TEXT_CMD_MARK
} from '../constants.js'

/**
 * Legacy DB strings interleave \text{English} with bare TeX and no $ delimiters.
 */
export const unwrapAlternatingText = (raw) => {
    const s = String(raw ?? '')
    if (!s.includes(TEXT_CMD_MARK)) return s

    const dollarCount = (s.match(/\$/g) || []).length
    const t0 = s.trimStart()
    if (dollarCount >= DOLLAR_COUNT_ABORT_UNWRAP || /^\\\[[\s\S]/.test(t0) || t0.startsWith('$$')) return s

    const proseWordishCount = (t) => {
        const cleaned = String(t || '')
            .replace(/\\[a-zA-Z]+/g, ' ')
            .replace(/\\./g, ' ')
            .replace(/[{}_^=+\-*/()<>.,;:!]/g, ' ')
            .replace(/\d+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
        return cleaned ? cleaned.split(' ').filter((w) => w.length > 1).length : 0
    }

    const firstMark = s.indexOf(TEXT_CMD_MARK)
    if (firstMark > 0) {
        const head = s.slice(0, firstMark).trim()
        const headWords = proseWordishCount(head)
        if (headWords >= HEAD_PROSE_WORD_THRESHOLD || head.length >= HEAD_MIN_LENGTH_THRESHOLD) return s
    }

    const out = []
    let i = 0

    while (i < s.length) {
        const k = s.indexOf(TEXT_CMD_MARK, i)
        if (k === -1) {
            const tail = s.slice(i).trim().replace(/^,\s*/, '')
            if (tail) out.push({ k: 'm', v: tail })
            break
        }

        if (k > i) {
            const mid = s.slice(i, k).trim().replace(/^,\s*/, '')
            if (mid) {
                const midWordsSp = mid.split(/\s+/).filter(Boolean).length
                const midWordsPr = proseWordishCount(mid)
                if (midWordsSp > MID_WORDS_SP_THRESHOLD || midWordsPr > MID_WORDS_PR_THRESHOLD) return s
                out.push({ k: 'm', v: mid })
            }
        }

        const innerStart = k + TEXT_CMD_MARK.length
        if (innerStart > s.length) return s

        let j = innerStart
        let depth = 1
        while (j < s.length && depth > 0) {
            const ch = s[j]
            if (ch === '{') depth += 1
            else if (ch === '}') depth -= 1
            j += 1
        }
        if (depth !== 0) return s

        out.push({ k: 't', v: s.slice(innerStart, j - 1) })
        i = j
    }

    return out.map((p) => (p.k === 't' ? p.v : `$${p.v}$`)).join('')
}

import { KNOWN_MATH_CMDS_RE, MATH_ZONE_SPLIT_RE } from '../constants.js'

/**
 * Scan prose for inline math with \commands and wrap in $...$.
 */
export const wrapBareLatexInProse = (fragment) => {
    if (!fragment || /\$/.test(fragment)) return fragment
    if (!/\\[a-zA-Z]/.test(fragment)) return fragment

    const isLetter = (ch) => /[a-zA-Z]/.test(ch)

    let result = ''
    let i = 0

    while (i < fragment.length) {
        let bs = -1
        for (let k = i; k < fragment.length; k++) {
            if (fragment[k] === '\\' && k + 1 < fragment.length && isLetter(fragment[k + 1])) {
                let ce = k + 1
                while (ce < fragment.length && isLetter(fragment[ce])) ce++
                if (KNOWN_MATH_CMDS_RE.test(fragment.slice(k + 1, ce))) {
                    bs = k
                    break
                }
            }
        }
        if (bs === -1) {
            result += fragment.slice(i)
            break
        }

        let left = bs
        const before = fragment.slice(i, bs)
        const leadMatch = before.match(
            /([A-Za-z0-9](?:[_^]\{[^{}]*\}|[_^][A-Za-z0-9])?\s*[=<>]\s*(?:[0-9]+\s*)?)$/
        )
        if (leadMatch) {
            left = bs - leadMatch[0].length
        }
        result += fragment.slice(i, left)

        let j = left
        while (j < fragment.length) {
            const ch = fragment[j]
            if (ch === '\\' && j + 1 < fragment.length && isLetter(fragment[j + 1])) {
                j++
                while (j < fragment.length && isLetter(fragment[j])) j++
                while (j < fragment.length) {
                    let ws = j
                    while (ws < fragment.length && fragment[ws] === ' ') ws++
                    if (ws < fragment.length && fragment[ws] === '{') {
                        j = ws + 1
                        let d = 1
                        while (j < fragment.length && d > 0) {
                            if (fragment[j] === '{') d++
                            else if (fragment[j] === '}') d--
                            j++
                        }
                    } else break
                }
                if (j < fragment.length && /[_^]/.test(fragment[j])) {
                    j++
                    if (j < fragment.length && fragment[j] === '{') {
                        j++
                        let d = 1
                        while (j < fragment.length && d > 0) {
                            if (fragment[j] === '{') d++
                            else if (fragment[j] === '}') d--
                            j++
                        }
                    } else if (j < fragment.length && /[a-zA-Z0-9]/.test(fragment[j])) j++
                }
            } else if (ch === '\\' && j + 1 < fragment.length && /[,;!]/.test(fragment[j + 1])) {
                j += 2
            } else if (/[=<>\/+\-*()]/.test(ch)) {
                j++
            } else if (/[0-9]/.test(ch)) {
                while (j < fragment.length && /[0-9.]/.test(fragment[j])) j++
            } else if (isLetter(ch)) {
                let we = j
                while (we < fragment.length && isLetter(fragment[we])) we++
                if (we - j === 1) {
                    j = we
                    if (j < fragment.length && /[_^]/.test(fragment[j])) {
                        j++
                        if (j < fragment.length && fragment[j] === '{') {
                            j++
                            let d = 1
                            while (j < fragment.length && d > 0) {
                                if (fragment[j] === '{') d++
                                else if (fragment[j] === '}') d--
                                j++
                            }
                        } else if (j < fragment.length && /[a-zA-Z0-9]/.test(fragment[j])) j++
                    }
                } else break
            } else if (ch === '_' || ch === '^') {
                j++
                if (j < fragment.length && fragment[j] === '{') {
                    j++
                    let d = 1
                    while (j < fragment.length && d > 0) {
                        if (fragment[j] === '{') d++
                        else if (fragment[j] === '}') d--
                        j++
                    }
                } else if (j < fragment.length && /[a-zA-Z0-9]/.test(fragment[j])) j++
            } else if (ch === ' ') {
                let ws = j
                while (ws < fragment.length && fragment[ws] === ' ') ws++
                if (ws >= fragment.length) break
                const nx = fragment[ws]
                if (
                    nx === '\\' &&
                    ws + 1 < fragment.length &&
                    (isLetter(fragment[ws + 1]) || /[,;!]/.test(fragment[ws + 1]))
                ) {
                    j = ws
                } else if (/[=<>\/+\-*()_^0-9]/.test(nx)) {
                    j = ws
                } else if (isLetter(nx)) {
                    let we2 = ws
                    while (we2 < fragment.length && isLetter(fragment[we2])) we2++
                    if (we2 - ws === 1 && we2 < fragment.length && /[_^=<>\/+\-*\\]/.test(fragment[we2])) {
                        j = ws
                    } else break
                } else break
            } else break
        }

        const mathExpr = fragment.slice(left, j).replace(/[\s,.;:]+$/, '')
        const trailing = fragment.slice(left + mathExpr.length, j)
        if (mathExpr && /\\[a-zA-Z]/.test(mathExpr)) {
            result += `$${mathExpr}$${trailing}`
        } else {
            result += fragment.slice(left, j)
        }
        i = j
    }
    return result
}

/** Process non-math-zone pieces with a transform (fresh regex per call — avoids global lastIndex issues). */
export const processNonZonePieces = (text, fn) => {
    const zoneRe = new RegExp(MATH_ZONE_SPLIT_RE.source, MATH_ZONE_SPLIT_RE.flags)
    return text.split(zoneRe).map((piece) => {
        if (!piece) return piece
        if (/^\$\$[\s\S]*\$\$$/.test(piece)) return piece
        if (/^\\\[[\s\S]*\\\]$/.test(piece)) return piece
        if (/^\$[\s\S]*\$$/.test(piece) && !piece.startsWith('$$')) return piece
        if (/^\\\([\s\S]*\\\)$/.test(piece)) return piece
        return fn(piece)
    }).join('')
}

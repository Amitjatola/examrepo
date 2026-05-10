import { processNonZonePieces, wrapBareLatexInProse } from './wrapBareLatexInProse.js'

/**
 * Wrap bare LaTeX fragments (\text{...}, \underline{...}) outside math zones.
 */
export const wrapBareMathCommands = (raw) => {
    const s = String(raw ?? '')
    const blankTextToRule = (fragment) =>
        fragment
            .replace(/\\text\s*\{\s*((?:(?:\\_)|_){2,})\s*\}/g, '$\\underline{\\hspace{3em}}$')
            .replace(/\\text\s*\{([^{}]*)\}/g, (_m, inner) => {
                const wordCount = inner.trim().split(/\s+/).filter(Boolean).length
                if (wordCount > 4) return inner
                const t = fragment.trim()
                if (/^\$[\s\S]*\$$/.test(t) && !t.startsWith('$$')) {
                    return `\\text{${inner}}`
                }
                return `$\\text{${inner}}$`
            })
            .replace(/\\underline\s*\{([^{}]*)\}/g, '$\\underline{$1}$')

    const afterBareWrap = processNonZonePieces(s, wrapBareLatexInProse)
    return processNonZonePieces(afterBareWrap, blankTextToRule)
}

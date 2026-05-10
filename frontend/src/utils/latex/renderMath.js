import katex from 'katex'
import { normalizeCommonLatexTypos } from './sanitize.js'

export const renderMathToHtml = (math, isDisplayMode) => {
    try {
        const isDev = typeof import.meta !== 'undefined' && import.meta.env?.DEV
        return katex.renderToString(normalizeCommonLatexTypos(math), {
            displayMode: isDisplayMode,
            throwOnError: Boolean(isDev),
            output: 'html',
            strict: false,
            trust: true
        })
    } catch (e) {
        console.error('KaTeX Error:', e)
        return math
    }
}

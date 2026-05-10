import { describe, expect, it } from 'vitest'
import { normalizeCommonLatexTypos, normalizePlainTextLatexTokens } from '../sanitize.js'

describe('sanitize', () => {
    it('converts tabular to array in math', () => {
        expect(normalizeCommonLatexTypos('\\begin{tabular}{|c|}\\hline a\\end{tabular}')).toContain(
            '\\begin{array}'
        )
    })

    it('unwraps prose \\text in plain path', () => {
        expect(normalizePlainTextLatexTokens('\\text{Hello}')).toBe('Hello')
    })
})

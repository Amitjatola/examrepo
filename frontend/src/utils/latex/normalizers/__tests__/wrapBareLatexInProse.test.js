import { describe, expect, it } from 'vitest'
import { wrapBareLatexInProse } from '../wrapBareLatexInProse.js'

describe('wrapBareLatexInProse', () => {
    it('wraps bare frac in prose', () => {
        const out = wrapBareLatexInProse('see \\frac{a}{b} now')
        expect(out).toContain('$\\frac{a}{b}$')
    })

    it('no-ops when dollars exist', () => {
        expect(wrapBareLatexInProse('$x$')).toBe('$x$')
    })
})

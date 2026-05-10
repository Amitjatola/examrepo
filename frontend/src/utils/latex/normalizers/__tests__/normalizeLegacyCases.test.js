import { describe, expect, it } from 'vitest'
import { normalizeLegacyCases } from '../normalizeLegacyCases.js'

describe('normalizeLegacyCases', () => {
    it('no-ops when cases absent', () => {
        expect(normalizeLegacyCases('plain')).toBe('plain')
    })

    it('wraps u/U legacy cases block in $$ when flagged by delta-row typo', () => {
        const raw =
            '\\frac{u}{U}=\\begin{cases} y \\le \\delta \\ 1 & y>\\delta \\end{cases}'
        const out = normalizeLegacyCases(raw)
        expect(out).toContain('$$')
        expect(out).toContain('\\begin{cases}')
    })
})

import { describe, expect, it } from 'vitest'
import { repairBrokenTokens } from '../repairBrokenTokens.js'

describe('repairBrokenTokens', () => {
    it('returns unchanged when dollars present', () => {
        expect(repairBrokenTokens('$\\omega$')).toBe('$\\omega$')
    })

    it('prepends backslashes and wraps frac arguments', () => {
        expect(repairBrokenTokens('dfrac omega 4')).toBe('\\dfrac{\\omega}{4}')
    })

    it('wraps frac arguments when digits follow', () => {
        expect(repairBrokenTokens('dfrac omega 4')).toMatch(/\\dfrac\{\\omega\}\{4\}/)
    })
})

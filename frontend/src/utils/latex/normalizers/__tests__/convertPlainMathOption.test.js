import { describe, expect, it } from 'vitest'
import { convertPlainMathOption } from '../convertPlainMathOption.js'

describe('convertPlainMathOption', () => {
    it('wraps sqrt pi style plain math', () => {
        const out = convertPlainMathOption('sqrt(2) pi v / g')
        expect(out).toContain('$')
        expect(out).toContain('\\sqrt')
    })

    it('no-ops long strings', () => {
        const long = 'a'.repeat(100)
        expect(convertPlainMathOption(long)).toBe(long.trim())
    })

    it('handles deg with and', () => {
        const out = convertPlainMathOption('> 20 deg and < 30 deg')
        expect(out).toContain('and')
        expect(out).toMatch(/\^\\circ/)
    })
})

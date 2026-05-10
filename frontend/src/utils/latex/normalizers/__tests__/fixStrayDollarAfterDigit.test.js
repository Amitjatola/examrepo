import { describe, expect, it } from 'vitest'
import { fixStrayDollarAfterDigit } from '../fixStrayDollarAfterDigit.js'
import { normalize } from '../../pipeline.js'

describe('fixStrayDollarAfterDigit', () => {
    it('repairs GATE-style "0$ and $\\sqrt..." options', () => {
        const input =
            String.raw`0$ and $\sqrt{\dfrac{k(m_1+m_2)}{m_1 m_2}}$`
        const out = fixStrayDollarAfterDigit(input)
        expect(out).toBe(
            String.raw`0 and $\sqrt{\dfrac{k(m_1+m_2)}{m_1 m_2}}$`
        )
    })

    it('supports "or" and ampersand', () => {
        expect(
            fixStrayDollarAfterDigit(String.raw`0$ or $\alpha$`)
        ).toBe(String.raw`0 or $\alpha$`)
        expect(
            fixStrayDollarAfterDigit(String.raw`0$ & $\beta$`)
        ).toBe(String.raw`0 & $\beta$`)
    })

    it('does not change money-ish "5$ and $10" (second $ not TeX)', () => {
        const s = '5$ and $10'
        expect(fixStrayDollarAfterDigit(s)).toBe(s)
    })

    it('does not strip subscript digit before$', () => {
        const s = String.raw`x_1$ and $\omega$`
        expect(fixStrayDollarAfterDigit(s)).toBe(s)
    })

    it('does not rewrite multi-digit endings like 10$', () => {
        const s = String.raw`10$ and $\pi$`
        expect(fixStrayDollarAfterDigit(s)).toBe(s)
    })

    it('runs in normalize() pipeline before delimiter split', () => {
        const input =
            String.raw`0$ and $\sqrt{\dfrac{k(m_1+m_2)}{m_1 m_2}}$`
        const out = normalize(input)
        expect(out).not.toContain('0$ and')
        expect(out).toContain(String.raw`\sqrt`)
    })
})

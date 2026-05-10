import { describe, expect, it } from 'vitest'
import { unwrapAlternatingText } from '../unwrapAlternatingText.js'

describe('unwrapAlternatingText', () => {
    it('no-ops without text marker', () => {
        expect(unwrapAlternatingText('x = 1')).toBe('x = 1')
    })

    it('unwraps short alternating \\text/TeX legacy payloads', () => {
        const raw = '\\text{mass } M \\text{ and stiffness } k'
        const out = unwrapAlternatingText(raw)
        expect(out).toContain('mass')
        expect(out).toContain('$M$')
    })
})

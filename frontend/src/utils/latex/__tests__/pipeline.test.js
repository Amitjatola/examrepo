import { describe, expect, it } from 'vitest'
import { normalize } from '../pipeline.js'

describe('pipeline', () => {
    it('chains repair + optional wrapping', () => {
        const out = normalize('dfrac omega 4')
        expect(out).toContain('omega')
    })

    it('treats full plain string round-trip', () => {
        expect(normalize('')).toBe('')
    })
})

import { describe, expect, it } from 'vitest'
import { ClassifyStrategy, analyzeNormalizedLatex, isLikelySentenceWrappedAsMath } from '../classify.js'

describe('classify', () => {
    it('marks delimited math', () => {
        const meta = analyzeNormalizedLatex('$x^2$')
        expect(meta.hasMathDelimiters).toBe(true)
        expect(meta.strategy).toBe(ClassifyStrategy.Delimited)
    })

    it('detects sentence masquerading as math', () => {
        expect(isLikelySentenceWrappedAsMath('If we know this, then it follows, etc.')).toBe(true)
    })

    it('rejects strong LaTeX as sentence-math', () => {
        expect(isLikelySentenceWrappedAsMath('\\dfrac{1}{2}\\mathrm{m}')).toBe(false)
    })
})

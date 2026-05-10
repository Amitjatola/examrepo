import { describe, expect, it } from 'vitest'
import { convertAsciiBracketDisplayMath } from '../convertAsciiBracketDisplayMath.js'
import { convertParentheticalNumericTextUnit } from '../convertParentheticalNumericTextUnit.js'
import { normalize } from '../../pipeline.js'

const gateStemSnippet = `
A batch yields at (330 ,\\text{MN/m}^2). Stress:

[
\\sigma_x = 140 ,\\text{MN/m}^2,\\quad
\\sigma_y = -70 ,\\text{MN/m}^2,\\quad
\\sigma_z = 0,
]
[
\\tau_{xy} = x ,\\text{MN/m}^2,\\quad
\\tau_{yz} = 0,\\quad
\\tau_{zx} = 0
]

The value of (x) is _____.
`

describe('convertAsciiBracketDisplayMath', () => {
    it('wraps [ \\sigma … ] blocks as $$ display math', () => {
        const out = convertAsciiBracketDisplayMath(gateStemSnippet)
        expect(out).toContain('$$')
        expect(out).toContain(String.raw`\sigma_x`)
        expect(out.match(/\$\$/g)?.length ?? 0).toBeGreaterThanOrEqual(4)
        expect(out).not.toMatch(/\[\s*\\\s*sigma/s)
    })

    it('does not wrap plain prose brackets', () => {
        expect(convertAsciiBracketDisplayMath('[approximation omitted]')).toBe('[approximation omitted]')
    })
})

describe('convertParentheticalNumericTextUnit', () => {
    it('unwraps numeric \\text units into inline math', () => {
        expect(convertParentheticalNumericTextUnit(String.raw`(330 ,\text{MN/m}^2)`)).toBe(
            String.raw`$330\,\text{MN/m}^2$`
        )
    })

    it('leaves symbolic (x) alone', () => {
        expect(convertParentheticalNumericTextUnit('The value of (x)')).toBe('The value of (x)')
    })
})

describe('pipeline + Von Mises style stem', () => {
    it('normalize() yields $$ zones and inline unit math', () => {
        const out = normalize(gateStemSnippet.trim())
        expect(out).toContain(String.raw`$330\,\text{MN/m}^2$`)
        expect(out).toMatch(/\$\$/s)
        expect(out).toContain(String.raw`\sigma_x`)
        expect(out).toContain(String.raw`\tau_{xy}`)
    })
})

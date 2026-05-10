import { describe, expect, it } from 'vitest'
import { wrapBareMathCommands } from '../wrapBareMathCommands.js'

describe('wrapBareMathCommands', () => {
    it('wraps short \\text outside math zones', () => {
        const out = wrapBareMathCommands('Value is \\text{Pa} units')
        expect(out).toContain('$\\text{Pa}$')
    })

    it('does not double-wrap inline math for short text', () => {
        const out = wrapBareMathCommands('$\\theta(0)=0$ and $\\theta(L)=0$')
        expect(out).not.toMatch(/\$\$\\text/)
    })
})

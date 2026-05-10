import { describe, expect, it } from 'vitest'
import { wrapBareAssignmentList } from '../wrapBareAssignmentList.js'

describe('wrapBareAssignmentList', () => {
    it('wraps multi-assignment tech strings', () => {
        const raw = 'V_{in} = 180, \\dot{m}_{air} = 94'
        const out = wrapBareAssignmentList(raw)
        expect(out.startsWith('$')).toBe(true)
        expect(out.endsWith('$')).toBe(true)
    })

    it('no-ops single equals', () => {
        expect(wrapBareAssignmentList('x = 1')).toBe('x = 1')
    })
})

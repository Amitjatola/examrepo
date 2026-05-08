/**
 * Normalize tier_1_core_research.formulas_principles into display blocks (shared by FormulaSheetPrint + CheatSheetPage).
 */

/**
 * @param {Record<string, unknown>} [tier1]
 * @returns {{ key: string, title: string, body: string }[]}
 */
export const extractFormulaBlocksFromTier1 = (tier1) => {
    const t = tier1 && typeof tier1 === 'object' ? tier1 : {}
    const raw = t.formulas_principles
    const formulas = Array.isArray(raw) ? raw : raw ? [raw] : []

    return formulas
        .map((item, idx) => {
            if (item == null) return null
            if (typeof item === 'string') {
                return { key: `s-${idx}`, title: `Formula ${idx + 1}`, body: item }
            }
            const title = item.name || item.title || `Principle ${idx + 1}`
            const body = item.formula || item.description || item.text || ''
            if (!body && !title) return null
            return { key: `o-${idx}`, title, body: typeof body === 'string' ? body : JSON.stringify(body) }
        })
        .filter(Boolean)
}

/**
 * Stable key for deduplication across questions (whitespace-collapsed lower-case title|body).
 */
export const formulaBlockDedupeKey = (title, body) => {
    const t = String(title || '').trim().replace(/\s+/g, ' ').toLowerCase()
    const b = String(body || '').trim().replace(/\s+/g, ' ').toLowerCase()
    return `${t}|${b}`
}

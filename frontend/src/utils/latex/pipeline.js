import { convertAsciiBracketDisplayMath } from './normalizers/convertAsciiBracketDisplayMath.js'
import { convertParentheticalNumericTextUnit } from './normalizers/convertParentheticalNumericTextUnit.js'
import { convertPlainMathOption } from './normalizers/convertPlainMathOption.js'
import { fixStrayDollarAfterDigit } from './normalizers/fixStrayDollarAfterDigit.js'
import { normalizeLegacyCases } from './normalizers/normalizeLegacyCases.js'
import { repairBrokenTokens } from './normalizers/repairBrokenTokens.js'
import { unwrapAlternatingText } from './normalizers/unwrapAlternatingText.js'
import { wrapBareAssignmentList } from './normalizers/wrapBareAssignmentList.js'
import { wrapBareMathCommands } from './normalizers/wrapBareMathCommands.js'

/**
 * Ordered legacy normalizers. Append new steps at the end (Open/Closed).
 * Order mirrors historical LatexRenderer behavior.
 */
const normalizers = [
    fixStrayDollarAfterDigit,
    convertAsciiBracketDisplayMath,
    convertParentheticalNumericTextUnit,
    repairBrokenTokens,
    normalizeLegacyCases,
    unwrapAlternatingText,
    convertPlainMathOption,
    wrapBareAssignmentList,
    wrapBareMathCommands
]

export const normalize = (raw) => normalizers.reduce((text, fn) => fn(text), String(raw ?? ''))

export { normalizers }

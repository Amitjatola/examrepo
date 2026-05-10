/**
 * Shared regex + thresholds for legacy LaTeX normalization (LatexRenderer pipeline).
 */

/** Marker for \text{...} blocks */
export const TEXT_CMD_MARK = '\\text{'

/** Split capture: $$...$$ | \[...\] | $...$ | \(...\) — non-greedy inner match */
export const MATH_ZONE_SPLIT_RE =
    /(\$\$[\s\S]*?\$\$)|(\\\[[\s\S]*?\\\])|(\$[\s\S]*?\$)|(\\\([\s\S]*?\\\))/g

/** Alias (plan name): math-zone splitter with capture groups */
export const MATH_ZONE_RE = MATH_ZONE_SPLIT_RE

/** Whether the string already contains math delimiters */
export const HAS_MATH_DELIMITERS_RE =
    /\$\$[\s\S]*?\$\$|\$[\s\S]*?\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)/

/** Fresh splitter for String.split — avoids shared /g RegExp lastIndex hazards */
export const createMathZoneSplitRegex = () =>
    new RegExp(MATH_ZONE_SPLIT_RE.source, MATH_ZONE_SPLIT_RE.flags)

/**
 * Commands considered "math" when scanning prose to wrap bare \command islands.
 * Must match full command name after backslash (see wrapBareLatexInProse).
 */
export const KNOWN_MATH_CMDS_RE =
    /^(frac|dfrac|tfrac|sqrt|omega|pi|alpha|beta|gamma|delta|theta|sigma|lambda|mu|rho|phi|epsilon|infty|approx|leq|geq|neq|times|cdot|dot|hat|bar|vec|tilde|overline|mathrm|mathbf|text|sin|cos|tan|log|ln|exp|lim|sum|int|partial|nabla|pm|mp|left|right|Big|big|quad|qquad)$/

/** Spelled English math words → LaTeX (no delimiters) for convertPlainMathOption */
export const SPELLED_WORD_TO_LATEX = Object.freeze({
    pi: '\\pi',
    inf: '\\infty',
    alpha: '\\alpha',
    beta: '\\beta',
    gamma: '\\gamma',
    delta: '\\delta',
    theta: '\\theta',
    omega: '\\omega',
    sigma: '\\sigma',
    lambda: '\\lambda',
    mu: '\\mu',
    rho: '\\rho',
    phi: '\\phi',
    epsilon: '\\epsilon',
    sin: '\\sin',
    cos: '\\cos',
    tan: '\\tan',
    log: '\\log',
    ln: '\\ln',
    exp: '\\exp'
})

/** Regex for plain-math keyword detection (matches convertPlainMathOption) */
export const PLAIN_MATH_KEYWORD_RE =
    /\b(pi|sqrt|sin|cos|tan|log|ln|exp|inf|alpha|beta|gamma|delta|theta|omega|sigma|lambda|mu|rho|phi|epsilon)\b/i

export const MAX_PLAIN_MATH_OPTION_LENGTH = 80
export const MAX_PLAIN_MATH_WORDS = 12
export const MAX_ASSIGNMENT_LIST_LENGTH = 320
export const HEAD_PROSE_WORD_THRESHOLD = 5
export const HEAD_MIN_LENGTH_THRESHOLD = 42
export const MID_WORDS_SP_THRESHOLD = 10
export const MID_WORDS_PR_THRESHOLD = 8
export const DOLLAR_COUNT_ABORT_UNWRAP = 4
export const AUTO_WRAP_MAX_CHARS = 120
export const AUTO_WRAP_MAX_WORDS = 12
export const EQUATION_LIKE_MAX_CHARS = 220
export const EQUATION_LIKE_MAX_TOKEN_WORDS = 14
export const EQUATION_LIKE_MIN_OPS = 6
export const FULL_LATEX_MIN_COMMANDS = 3

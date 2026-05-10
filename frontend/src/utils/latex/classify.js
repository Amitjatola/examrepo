import {
    AUTO_WRAP_MAX_CHARS,
    AUTO_WRAP_MAX_WORDS,
    EQUATION_LIKE_MAX_CHARS,
    EQUATION_LIKE_MAX_TOKEN_WORDS,
    EQUATION_LIKE_MIN_OPS,
    FULL_LATEX_MIN_COMMANDS,
    HAS_MATH_DELIMITERS_RE
} from './constants.js'

/**
 * Legacy: long English accidentally wrapped in $...$ — render as markdown prose instead of KaTeX.
 */
export const isLikelySentenceWrappedAsMath = (value) => {
    const raw = String(value || '')
    const strongMathSignal =
        /\\(mathcal|mathrm|mathbf|mathit|textrm|frac|dfrac|tfrac|sqrt|left|right|sum|int|partial|nabla|cdot|times|infty|approx|leq|geq|neq|pm|mp|sigma|tau|Omega|omega|alpha|beta|gamma|delta|theta|lambda|mu|rho|phi|epsilon|pi|sin|cos|tan|log|ln|exp|begin\{)/.test(
            raw
        )
    if (strongMathSignal) return false

    const hasGreekCommand = /\\(alpha|beta|gamma|delta|theta|omega|sigma|lambda|mu|rho|phi|epsilon)\b/.test(raw)
    const hasMathOperators = /[=+\-*/^_{}<>]/.test(raw)

    const cleaned = String(value || '')
        .replace(/\\[a-zA-Z]+/g, ' ')
        .replace(/[{}_^$=()+\-*/[\]<>]/g, ' ')
        .replace(/\d+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
    const words = cleaned ? cleaned.split(' ').filter((w) => w.length > 1) : []

    if (hasGreekCommand && !hasMathOperators && words.length >= 2) return true

    const hasSentenceSignal = /[,.]|\\text\{|\bif\b|\bthen\b|\bmatrix\b/i.test(raw)
    return words.length >= 7 && hasSentenceSignal
}

/** Strategy labels for how normalized text should be wrapped before delimiter split (Open/Closed extension point). */
export const ClassifyStrategy = Object.freeze({
    Delimited: 'delimited',
    BareEquation: 'bare-equation',
    FullLatex: 'full-latex',
    ShortMath: 'short-math',
    Prose: 'prose'
})

/**
 * Heuristics for auto-wrapping undelimited math and environment detection.
 * Mirrors legacy LatexRenderer inline logic (preserve behavior byte-for-byte).
 */
export const analyzeNormalizedLatex = (normalizedText) => {
    const hasMathDelimiters = HAS_MATH_DELIMITERS_RE.test(normalizedText)
    const hasLatexLikeSyntax =
        /\\[a-zA-Z]+|[_^]|\\\(|\\\)|\\\[|\\\]/.test(normalizedText)
    const hasLatexEnvironment = /\\begin\{[a-zA-Z*]+\}[\s\S]*?\\end\{[a-zA-Z*]+\}/.test(normalizedText)
    const latexCommandCount = (normalizedText.match(/\\[a-zA-Z]+/g) || []).length
    const wordCount = normalizedText.trim().split(/\s+/).filter(Boolean).length
    const hasSentenceLikePunctuation = /[.!?]\s+[A-Z]/.test(normalizedText)
    const plainTextWithoutLatex = normalizedText
        .replace(/\\[a-zA-Z]+/g, ' ')
        .replace(/[{}_^$=()+\-*/[\],.:;<>]/g, ' ')
        .replace(/\d+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
    const plainWordCount = plainTextWithoutLatex
        ? plainTextWithoutLatex.split(' ').filter((w) => w.length > 1).length
        : 0
    const isLikelyProseWithMath = plainWordCount >= 4
    const operatorMatchCount = (normalizedText.match(/[=+\-/*^()]/g) || []).length
    const tokenLikeWordCount = (normalizedText.match(/[A-Za-z]+/g) || []).length
    const isEquationLikeWithoutDelimiters =
        !hasMathDelimiters &&
        operatorMatchCount >= EQUATION_LIKE_MIN_OPS &&
        tokenLikeWordCount <= EQUATION_LIKE_MAX_TOKEN_WORDS &&
        normalizedText.length <= EQUATION_LIKE_MAX_CHARS
    const appearsAsFullLatexExpression =
        !hasMathDelimiters &&
        latexCommandCount >= FULL_LATEX_MIN_COMMANDS &&
        normalizedText.trim().startsWith('\\')
    const shouldAutoWrapWholeMath =
        isEquationLikeWithoutDelimiters ||
        appearsAsFullLatexExpression ||
        (!hasMathDelimiters &&
            hasLatexLikeSyntax &&
            wordCount <= AUTO_WRAP_MAX_WORDS &&
            normalizedText.length <= AUTO_WRAP_MAX_CHARS &&
            !hasSentenceLikePunctuation &&
            !isLikelyProseWithMath)

    let strategy = ClassifyStrategy.Prose
    if (hasMathDelimiters) {
        strategy = ClassifyStrategy.Delimited
    } else if (isEquationLikeWithoutDelimiters) {
        strategy = ClassifyStrategy.BareEquation
    } else if (appearsAsFullLatexExpression) {
        strategy = ClassifyStrategy.FullLatex
    } else if (shouldAutoWrapWholeMath) {
        strategy = ClassifyStrategy.ShortMath
    }

    return {
        hasMathDelimiters,
        hasLatexLikeSyntax,
        hasLatexEnvironment,
        latexCommandCount,
        wordCount,
        hasSentenceLikePunctuation,
        plainWordCount,
        isLikelyProseWithMath,
        operatorMatchCount,
        tokenLikeWordCount,
        isEquationLikeWithoutDelimiters,
        appearsAsFullLatexExpression,
        shouldAutoWrapWholeMath,
        strategy
    }
}

/** @deprecated Use analyzeNormalizedLatex(normalizedText).strategy — kept for explicit call-sites/tests */
export const classifyContent = (normalizedText) => analyzeNormalizedLatex(normalizedText).strategy

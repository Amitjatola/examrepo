/**
 * Many legacy rows store a short, delimiter-free LaTeX fragment in `question_text_latex` (e.g. "V_{in} = 180, \\dot{m}_{air} = 94...")
 * while the readable prose lives in `question_text`. The UI must not prefer that fragment over the full stem.
 *
 * When `question_text_latex` is upgraded to a full prose+math stem, it is usually longer and/or sentence-complete — then we show it.
 */
export const selectQuestionStemText = (question) => {
    const plain = typeof question?.question_text === 'string' ? question.question_text.trim() : ''
    const latex = typeof question?.question_text_latex === 'string' ? question.question_text_latex.trim() : ''

    if (!latex) return plain || 'No question text available.'
    if (!plain) return latex

    const plainHasSentenceEnd = /[.!?][\s\n]/.test(plain)
    const latexHasSentenceEnd = /[.!?][\s\n]/.test(latex)

    const latexLooksLikeShortNumericFragment =
        plain.length >= 50 &&
        latex.length < Math.min(plain.length * 0.75, 280) &&
        (!latexHasSentenceEnd || latex.length + 35 < plain.length)

    if (latexLooksLikeShortNumericFragment && plainHasSentenceEnd) return plain

    return latex
}

import React, { useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import 'katex/dist/katex.min.css'
import { analyzeNormalizedLatex, isLikelySentenceWrappedAsMath } from '../utils/latex/classify.js'
import { createMathZoneSplitRegex } from '../utils/latex/constants.js'
import { normalize } from '../utils/latex/pipeline.js'
import { renderMathToHtml } from '../utils/latex/renderMath.js'
import { normalizePlainTextLatexTokens } from '../utils/latex/sanitize.js'

const LatexRenderer = ({ text, block = false, inline = false }) => {
    const inlineMathClass = inline
        ? 'inline align-middle mx-0.5 text-inherit [&_.katex]:text-inherit [&_.katex-display]:!inline'
        : 'inline-block mx-0.5 align-baseline text-inherit [&_.katex]:text-inherit'

    const { normalizedText, hasMathDelimiters, hasLatexEnvironment, shouldAutoWrapWholeMath } =
        useMemo(() => {
            const normalizedText = normalize(String(text ?? ''))
            const meta = analyzeNormalizedLatex(normalizedText)
            return { normalizedText, ...meta }
        }, [text])

    if (!text) return null

    const withWrappedEnvironments =
        !hasMathDelimiters && hasLatexEnvironment
            ? normalizedText.replace(
                  /(\\begin\{[a-zA-Z*]+\}[\s\S]*?\\end\{[a-zA-Z*]+\})/g,
                  (_m, envBlock) => `$$${envBlock}$$`
              )
            : normalizedText

    const safeText = shouldAutoWrapWholeMath ? `$${withWrappedEnvironments}$` : withWrappedEnvironments
    const splitRe = createMathZoneSplitRegex()
    const parts = safeText.split(splitRe)

    return (
        <span className={block ? 'block w-full' : ''}>
            {parts.map((part, index) => {
                if (!part) return null

                if (
                    (part.startsWith('$$') && part.endsWith('$$') && part.length >= 4) ||
                    (part.startsWith('\\[') && part.endsWith('\\]') && part.length >= 4)
                ) {
                    const math = part.slice(2, -2)
                    const html = renderMathToHtml(math, true)
                    return (
                        <span
                            key={index}
                            className="block my-4 text-center overflow-x-auto max-w-full"
                            dangerouslySetInnerHTML={{ __html: html }}
                        />
                    )
                }
                if (
                    (part.startsWith('$') && part.endsWith('$') && part.length >= 2) ||
                    (part.startsWith('\\(') && part.endsWith('\\)') && part.length >= 4)
                ) {
                    const math = part.startsWith('$') ? part.slice(1, -1) : part.slice(2, -2)
                    if (isLikelySentenceWrappedAsMath(math)) {
                        return (
                            <span key={index} className="inline">
                                <ReactMarkdown components={{ p: 'span' }}>
                                    {normalizePlainTextLatexTokens(math)}
                                </ReactMarkdown>
                            </span>
                        )
                    }
                    const html = renderMathToHtml(math, false)
                    return (
                        <span
                            key={index}
                            className={inlineMathClass}
                            dangerouslySetInnerHTML={{ __html: html }}
                        />
                    )
                }
                return (
                    <span key={index} className="inline">
                        <ReactMarkdown components={{ p: 'span' }}>
                            {normalizePlainTextLatexTokens(part)}
                        </ReactMarkdown>
                    </span>
                )
            })}
        </span>
    )
}

export default React.memo(LatexRenderer)

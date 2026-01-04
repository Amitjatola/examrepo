import React from 'react';
import ReactMarkdown from 'react-markdown';
import katex from 'katex';
import 'katex/dist/katex.min.css';

const LatexRenderer = ({ text, block = false, inline = false }) => {
    if (!text) return null;

    // Helper to render math string using katex
    const renderMath = (math, isDisplayMode) => {
        try {
            return katex.renderToString(math, {
                displayMode: isDisplayMode,
                throwOnError: false,
                output: 'html',
                strict: false,
                trust: true
            });
        } catch (e) {
            console.error("KaTeX Error:", e);
            return math;
        }
    };

    // Regex to split text by delimiters: $$...$$ or $...$
    // Capture groups: 1=$$block$$, 2=$inline$
    const regex = /(\$\$[\s\S]*?\$\$)|(\$[\s\S]*?\$)/g;

    const parts = text.split(regex);

    return (
        <span className={block ? "block w-full" : ""}>
            {parts.map((part, index) => {
                if (!part) return null;

                if (part.startsWith('$$') && part.endsWith('$$') && part.length >= 4) {
                    // Block math
                    const math = part.slice(2, -2);
                    const html = renderMath(math, true);
                    return <span key={index} className="block my-4 text-center" dangerouslySetInnerHTML={{ __html: html }} />;
                } else if (part.startsWith('$') && part.endsWith('$') && part.length >= 2) {
                    // Inline math
                    const math = part.slice(1, -1);
                    const html = renderMath(math, false);
                    return <span key={index} dangerouslySetInnerHTML={{ __html: html }} />;
                } else {
                    // Regular markdown text
                    return (
                        <span key={index} className="inline">
                            <ReactMarkdown components={{ p: 'span' }}>{part}</ReactMarkdown>
                        </span>
                    );
                }
            })}
        </span>
    );
};

export default LatexRenderer;

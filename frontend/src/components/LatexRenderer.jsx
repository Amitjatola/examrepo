import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

/**
 * Preprocesses text to ensure LaTeX patterns are wrapped in $ delimiters.
 * This handles cases where the database stores LaTeX without $ wrappers.
 */
const preprocessLatex = (text) => {
    if (!text) return '';

    // Already has $ delimiters, return as-is
    if (text.includes('$')) return text;

    // Check if text contains any LaTeX commands (starts with \)
    if (!text.includes('\\')) return text;

    // For short text that is primarily LaTeX (like answer options), wrap the whole thing
    // Examples: "\frac{d^2y}{dx^2} + y = 0" or "\left(\frac{dy}{dx}\right)^2"
    const trimmed = text.trim();

    // Check if the text starts with a LaTeX command - likely an equation
    if (trimmed.startsWith('\\')) {
        return `$${text}$`;
    }

    // For longer mixed content, wrap individual LaTeX segments
    let processed = text;

    // Match block environments and wrap with $
    const blockPattern = /\\begin\{(bmatrix|pmatrix|vmatrix|matrix|cases|aligned|align|equation|array)\}[\s\S]*?\\end\{\1\}/g;
    processed = processed.replace(blockPattern, (match) => `$${match}$`);

    // Match complete LaTeX expressions that aren't already wrapped
    // This handles: \frac{...}{...}, \sqrt{...}, \left(...\right), Greek letters, etc.

    // Pattern 1: \command{...}{...} or \command{...} patterns
    const commandPattern = /\\[a-zA-Z]+(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\})+/g;
    processed = processed.replace(commandPattern, (match, offset) => {
        // Check if already inside $ delimiters
        const before = processed.substring(0, offset);
        const dollarCount = (before.match(/\$/g) || []).length;
        if (dollarCount % 2 === 1) return match;
        return `$${match}$`;
    });

    // Pattern 2: Simple commands like \cdot, \times, \lambda, etc.
    const simpleCommands = /\\(cdot|times|div|pm|mp|leq|geq|neq|approx|equiv|infty|partial|nabla|lambda|alpha|beta|gamma|delta|theta|phi|psi|omega|pi|sigma|mu|epsilon|det)\b/g;
    processed = processed.replace(simpleCommands, (match, offset) => {
        const before = processed.substring(0, offset);
        const dollarCount = (before.match(/\$/g) || []).length;
        if (dollarCount % 2 === 1) return match;
        return `$${match}$`;
    });

    // Pattern 3: \left and \right with matching delimiters - need to find pairs
    if (processed.includes('\\left') || processed.includes('\\right')) {
        // Find \left...\right pairs and wrap them
        const leftRightPattern = /\\left[(\[{|][\s\S]*?\\right[)\]}|]/g;
        processed = processed.replace(leftRightPattern, (match, offset) => {
            const before = processed.substring(0, offset);
            const dollarCount = (before.match(/\$/g) || []).length;
            if (dollarCount % 2 === 1) return match;
            return `$${match}$`;
        });
    }

    // Clean up any adjacent $ delimiters that we might have created ($$)
    processed = processed.replace(/\$\$/g, '$ $');

    return processed;
};

const LatexRenderer = ({ text, className = '' }) => {
    if (!text) return null;

    const processedText = preprocessLatex(text);

    return (
        <div className={`markdown-body ${className}`}>
            <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                    // Override default element styling if needed
                    p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                    a: ({ node, ...props }) => <a className="text-blue-600 hover:underline" {...props} />,
                    ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-4" {...props} />,
                    ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-4" {...props} />,
                    li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                    h1: ({ node, ...props }) => <h1 className="text-xl font-bold mb-3" {...props} />,
                    h2: ({ node, ...props }) => <h2 className="text-lg font-bold mb-2" {...props} />,
                    h3: ({ node, ...props }) => <h3 className="text-base font-bold mb-2" {...props} />,
                    blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-gray-200 pl-4 my-4 italic" {...props} />,
                }}
            >
                {processedText}
            </ReactMarkdown>
        </div>
    );
};

export default LatexRenderer;

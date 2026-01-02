
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

const LatexRenderer = ({ text, block = false, inline = false }) => {
    if (!text) return null;

    // Sanitize and prepare text
    // Ensure all backslashes are properly escaped if needed, though raw string from API usually fine

    // If inline forced, wrap in $...$ if not already
    let content = text;

    // Simple heuristic: if text doesn't look like markdown/latex, just render it?
    // But we want to support mixed content.

    return (
        <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={{
                p: ({ node, ...props }) => inline ? <span {...props} /> : <p className="mb-4" {...props} />
            }}
        >
            {content}
        </ReactMarkdown>
    );
};

export default LatexRenderer;

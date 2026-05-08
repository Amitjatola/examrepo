import React from 'react';
import ReactMarkdown from 'react-markdown';
import katex from 'katex';
import 'katex/dist/katex.min.css';

const TEXT_CMD_MARK = '\\text{';

/**
 * Legacy DB strings interleave \\text{English} with bare TeX (C_p, \\Phi, \\frac) and no $ delimiters.
 * Unwrap \\text{...} to plain prose and wrap each interstitial TeX snippet as $...$ so KaTeX runs.
 */
const unwrapAlternatingTextLatex = (raw) => {
    const s = String(raw ?? '');
    if (!s.includes(TEXT_CMD_MARK)) return s;

    const dollarCount = (s.match(/\$/g) || []).length;
    const t0 = s.trimStart();
    if (dollarCount >= 4 || /^\\\[[\s\S]/.test(t0) || t0.startsWith('$$')) return s;

    /** Word count for actual Latin prose tokens (not TeX commands or math punctuation). */
    const proseWordishCount = (t) => {
        const cleaned = String(t || '')
            .replace(/\\[a-zA-Z]+/g, ' ')
            .replace(/\\./g, ' ')
            .replace(/[{}_^=+\-*/()<>.,;:!]/g, ' ')
            .replace(/\d+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
        return cleaned ? cleaned.split(' ').filter((w) => w.length > 1).length : 0;
    };

    const firstMark = s.indexOf(TEXT_CMD_MARK);
    if (firstMark > 0) {
        const head = s.slice(0, firstMark).trim();
        const headWords = proseWordishCount(head);
        // English stem with \\text{km}, \\text{bar} for units — interstitials are prose, not math.
        if (headWords >= 5 || head.length >= 42) return s;
    }

    const out = [];
    let i = 0;

    while (i < s.length) {
        const k = s.indexOf(TEXT_CMD_MARK, i);
        if (k === -1) {
            const tail = s.slice(i).trim().replace(/^,\s*/, '');
            if (tail) out.push({ k: 'm', v: tail });
            break;
        }

        if (k > i) {
            const mid = s.slice(i, k).trim().replace(/^,\s*/, '');
            if (mid) {
                const midWordsSp = mid.split(/\s+/).filter(Boolean).length;
                const midWordsPr = proseWordishCount(mid);
                // Long clause between \\text{...} blocks: prose + inline units, not legacy bare-math chunks.
                if (midWordsSp > 10 || midWordsPr > 8) return s;
                out.push({ k: 'm', v: mid });
            }
        }

        const innerStart = k + TEXT_CMD_MARK.length;
        if (innerStart > s.length) return s;

        let j = innerStart;
        let depth = 1;
        while (j < s.length && depth > 0) {
            const ch = s[j];
            if (ch === '{') depth += 1;
            else if (ch === '}') depth -= 1;
            j += 1;
        }
        if (depth !== 0) return s;

        out.push({ k: 't', v: s.slice(innerStart, j - 1) });
        i = j;
    }

    return out.map((p) => (p.k === 't' ? p.v : `$${p.v}$`)).join('');
};

/**
 * Short option strings stored as plain-text math (e.g. "sqrt(2) pi v / g") without any LaTeX markup.
 * Convert known math keywords to TeX and wrap as $...$. Only fires on short, non-prose, delimiter-free strings.
 */
const convertPlainMathOption = (raw) => {
    const s0 = String(raw ?? '');
    const s = s0.trim();
    if (!s || s.length > 80) return s0;
    if (/\$|\\[a-zA-Z]/.test(s)) return s0;
    if (/[.!?]\s+[A-Z]/.test(s)) return s0;
    const words = s.split(/\s+/);
    if (words.length > 12) return s0;
    const hasMathKeyword = /\b(pi|sqrt|sin|cos|tan|log|ln|exp|inf|alpha|beta|gamma|delta|theta|omega|sigma|lambda|mu|rho|phi|epsilon)\b/i.test(s);
    // Do not use `\d+\s*[a-z]` — it matches the first letter after a number (e.g. "2412 airfoil" -> "2412 a")
    // and wrongly wraps full prose stems in math mode. Only treat digit+token as math when the token is short (units).
    const hasMathOp = /[/^*=<>]/.test(s) || /\d+\s+[a-zA-Z]{1,4}\b/.test(s);
    if (!hasMathKeyword && !hasMathOp) return s0;

    let t = s;
    t = t.replace(/\bsqrt\(([^)]+)\)/g, '\\sqrt{$1}');
    t = t.replace(/\bpi\b/g, '\\pi');
    t = t.replace(/\binf\b/g, '\\infty');
    t = t.replace(/\balpha\b/g, '\\alpha');
    t = t.replace(/\bbeta\b/g, '\\beta');
    t = t.replace(/\bgamma\b/g, '\\gamma');
    t = t.replace(/\bdelta\b/g, '\\delta');
    t = t.replace(/\btheta\b/g, '\\theta');
    t = t.replace(/\bomega\b/g, '\\omega');
    t = t.replace(/\bsigma\b/g, '\\sigma');
    t = t.replace(/\blambda\b/g, '\\lambda');
    t = t.replace(/\bmu\b/g, '\\mu');
    t = t.replace(/\brho\b/g, '\\rho');
    t = t.replace(/\bphi\b/g, '\\phi');
    t = t.replace(/\bepsilon\b/g, '\\epsilon');
    t = t.replace(/\bsin\b/g, '\\sin');
    t = t.replace(/\bcos\b/g, '\\cos');
    t = t.replace(/\btan\b/g, '\\tan');
    t = t.replace(/\blog\b/g, '\\log');
    t = t.replace(/\bln\b/g, '\\ln');
    t = t.replace(/\bexp\b/g, '\\exp');
    t = t.replace(/\^(\d+)/g, '^{$1}');
    t = t.replace(/\^([a-zA-Z])/g, '^{$1}');
    return `$${t}$`;
};

/**
 * Legacy rows sometimes store only a comma-separated assignment list with TeX commands but no $...$.
 * Wrap as one inline math chunk so KaTeX runs (e.g. V_{in}, \\dot{m}_{air}).
 */
const wrapLegacyBareAssignmentList = (raw) => {
    const s0 = String(raw ?? '');
    const s = s0.trim();
    if (!s) return s0;
    if (/\$|\\\[/.test(s)) return s0;
    if (s.length > 320) return s0;
    if (/[.!?][\s\n][A-Za-z]/.test(s)) return s0;
    const eqCount = (s.match(/=/g) || []).length;
    if (eqCount < 2) return s0;
    const hasLatexCmd = /\\[a-zA-Z]+/.test(s);
    const hasSub = /_\{/.test(s);
    if (!hasLatexCmd && !hasSub) return s0;

    let t = s.replace(/\bV\{exit\}/g, 'V_{\\text{exit}}');
    t = t.replace(/\b([A-Za-z])\{([a-z]{1,12})\}(?=\s*[=,)])/g, (_m, a, b) => `${a}_{\\text{${b}}}`);
    return `$${t}$`;
};

/**
 * Scan prose text for inline math expressions containing \commands and wrap them in $...$.
 * Handles patterns like: \omega_p \approx \sqrt{2}\,g/V  or  T = 2\pi/\omega_p
 */
const wrapBareLatexInProse = (fragment) => {
    if (!fragment || /\$/.test(fragment)) return fragment;
    if (!/\\[a-zA-Z]/.test(fragment)) return fragment;

    const isLetter = (ch) => /[a-zA-Z]/.test(ch);
    const knownMathCmds = /^(frac|dfrac|tfrac|sqrt|omega|pi|alpha|beta|gamma|delta|theta|sigma|lambda|mu|rho|phi|epsilon|infty|approx|leq|geq|neq|times|cdot|dot|hat|bar|vec|tilde|overline|mathrm|mathbf|text|sin|cos|tan|log|ln|exp|lim|sum|int|partial|nabla|pm|mp|left|right|Big|big|quad|qquad)$/;

    let result = '';
    let i = 0;

    while (i < fragment.length) {
        let bs = -1;
        for (let k = i; k < fragment.length; k++) {
            if (fragment[k] === '\\' && k + 1 < fragment.length && isLetter(fragment[k + 1])) {
                let ce = k + 1;
                while (ce < fragment.length && isLetter(fragment[ce])) ce++;
                if (knownMathCmds.test(fragment.slice(k + 1, ce))) { bs = k; break; }
            }
        }
        if (bs === -1) { result += fragment.slice(i); break; }

        let left = bs;
        const before = fragment.slice(i, bs);
        const leadMatch = before.match(/([A-Za-z0-9](?:[_^]\{[^{}]*\}|[_^][A-Za-z0-9])?\s*[=<>]\s*(?:[0-9]+\s*)?)$/);
        if (leadMatch) { left = bs - leadMatch[0].length; }
        result += fragment.slice(i, left);

        let j = left;
        while (j < fragment.length) {
            const ch = fragment[j];
            if (ch === '\\' && j + 1 < fragment.length && isLetter(fragment[j + 1])) {
                j++;
                while (j < fragment.length && isLetter(fragment[j])) j++;
                while (j < fragment.length) {
                    let ws = j; while (ws < fragment.length && fragment[ws] === ' ') ws++;
                    if (ws < fragment.length && fragment[ws] === '{') {
                        j = ws + 1; let d = 1;
                        while (j < fragment.length && d > 0) { if (fragment[j] === '{') d++; else if (fragment[j] === '}') d--; j++; }
                    } else break;
                }
                if (j < fragment.length && /[_^]/.test(fragment[j])) {
                    j++;
                    if (j < fragment.length && fragment[j] === '{') {
                        j++; let d = 1;
                        while (j < fragment.length && d > 0) { if (fragment[j] === '{') d++; else if (fragment[j] === '}') d--; j++; }
                    } else if (j < fragment.length && /[a-zA-Z0-9]/.test(fragment[j])) j++;
                }
            } else if (ch === '\\' && j + 1 < fragment.length && /[,;!]/.test(fragment[j + 1])) {
                j += 2;
            } else if (/[=<>\/+\-*()]/.test(ch)) {
                j++;
            } else if (/[0-9]/.test(ch)) {
                while (j < fragment.length && /[0-9.]/.test(fragment[j])) j++;
            } else if (isLetter(ch)) {
                let we = j; while (we < fragment.length && isLetter(fragment[we])) we++;
                if (we - j === 1) {
                    j = we;
                    if (j < fragment.length && /[_^]/.test(fragment[j])) {
                        j++;
                        if (j < fragment.length && fragment[j] === '{') {
                            j++; let d = 1;
                            while (j < fragment.length && d > 0) { if (fragment[j] === '{') d++; else if (fragment[j] === '}') d--; j++; }
                        } else if (j < fragment.length && /[a-zA-Z0-9]/.test(fragment[j])) j++;
                    }
                } else break;
            } else if (ch === '_' || ch === '^') {
                j++;
                if (j < fragment.length && fragment[j] === '{') {
                    j++; let d = 1;
                    while (j < fragment.length && d > 0) { if (fragment[j] === '{') d++; else if (fragment[j] === '}') d--; j++; }
                } else if (j < fragment.length && /[a-zA-Z0-9]/.test(fragment[j])) j++;
            } else if (ch === ' ') {
                let ws = j; while (ws < fragment.length && fragment[ws] === ' ') ws++;
                if (ws >= fragment.length) break;
                const nx = fragment[ws];
                if (nx === '\\' && ws + 1 < fragment.length && (isLetter(fragment[ws + 1]) || /[,;!]/.test(fragment[ws + 1]))) { j = ws; }
                else if (/[=<>\/+\-*()_^0-9]/.test(nx)) { j = ws; }
                else if (isLetter(nx)) {
                    let we2 = ws; while (we2 < fragment.length && isLetter(fragment[we2])) we2++;
                    if (we2 - ws === 1 && we2 < fragment.length && /[_^=<>\/+\-*\\]/.test(fragment[we2])) { j = ws; }
                    else break;
                } else break;
            } else break;
        }

        const mathExpr = fragment.slice(left, j).replace(/[\s,.;:]+$/, '');
        const trailing = fragment.slice(left + mathExpr.length, j);
        if (mathExpr && /\\[a-zA-Z]/.test(mathExpr)) {
            result += `$${mathExpr}$${trailing}`;
        } else {
            result += fragment.slice(left, j);
        }
        i = j;
    }
    return result;
};

/** Process non-math-zone pieces of text with a given transform function. */
const processNonZonePieces = (text, fn) => {
    const zoneRe = /(\$\$[\s\S]*?\$\$)|(\\\[[\s\S]*?\\\])|(\$[\s\S]*?\$)|(\\\([\s\S]*?\\\))/g;
    return text.split(zoneRe).map((piece) => {
        if (!piece) return piece;
        if (/^\$\$[\s\S]*\$\$$/.test(piece)) return piece;
        if (/^\\\[[\s\S]*\\\]$/.test(piece)) return piece;
        if (/^\$[\s\S]*\$$/.test(piece) && !piece.startsWith('$$')) return piece;
        if (/^\\\([\s\S]*\\\)$/.test(piece)) return piece;
        return fn(piece);
    }).join('');
};

/**
 * Wrap bare LaTeX fragments that only make sense inside math mode (e.g. \text{...}, \underline{...})
 * when they appear outside $...$, $$...$$, \[...\], \(...\). Prevents raw "\text{...}" in prose.
 */
const wrapBareMathOnlyCommands = (raw) => {
    const s = String(raw ?? '');
    const blankTextToRule = (fragment) =>
        fragment
            .replace(/\\text\s*\{\s*((?:(?:\\_)|_){2,})\s*\}/g, '$\\underline{\\hspace{3em}}$')
            .replace(/\\text\s*\{([^{}]*)\}/g, (_m, inner) => {
                const wordCount = inner.trim().split(/\s+/).filter(Boolean).length;
                if (wordCount > 4) return inner;
                return `$\\text{${inner}}$`;
            })
            .replace(/\\underline\s*\{([^{}]*)\}/g, '$\\underline{$1}$');

    const afterBareWrap = processNonZonePieces(s, wrapBareLatexInProse);
    return processNonZonePieces(afterBareWrap, blankTextToRule);
};

const LatexRenderer = ({ text, block = false, inline = false }) => {
    const inlineMathClass = inline
        ? 'inline align-middle mx-0.5 text-inherit [&_.katex]:text-inherit [&_.katex-display]:!inline'
        : 'inline-block mx-0.5 align-baseline text-inherit [&_.katex]:text-inherit';
    if (!text) return null;
    const normalizedText = wrapBareMathOnlyCommands(wrapLegacyBareAssignmentList(convertPlainMathOption(unwrapAlternatingTextLatex(String(text)))));

    const hasMathDelimiters = /\$\$[\s\S]*?\$\$|\$[\s\S]*?\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)/.test(normalizedText);
    const hasLatexLikeSyntax = /\\[a-zA-Z]+|[_^]|\\\(|\\\)|\\\[|\\\]/.test(normalizedText);
    const hasLatexEnvironment = /\\begin\{[a-zA-Z*]+\}[\s\S]*?\\end\{[a-zA-Z*]+\}/.test(normalizedText);
    const latexCommandCount = (normalizedText.match(/\\[a-zA-Z]+/g) || []).length;
    const wordCount = normalizedText.trim().split(/\s+/).filter(Boolean).length;
    const hasSentenceLikePunctuation = /[.!?]\s+[A-Z]/.test(normalizedText);
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
        operatorMatchCount >= 6 &&
        tokenLikeWordCount <= 14 &&
        normalizedText.length <= 220
    const appearsAsFullLatexExpression =
        !hasMathDelimiters &&
        latexCommandCount >= 3 &&
        normalizedText.trim().startsWith('\\');
    const shouldAutoWrapWholeMath =
        isEquationLikeWithoutDelimiters ||
        appearsAsFullLatexExpression ||
        (
            !hasMathDelimiters &&
            hasLatexLikeSyntax &&
            wordCount <= 12 &&
            normalizedText.length <= 120 &&
            !hasSentenceLikePunctuation &&
            !isLikelyProseWithMath
        );

    const normalizeCommonLatexTypos = (math) =>
        math
            // Fill-in blanks: \text{\_\_\_} / \text{___} often fails KaTeX or reads as subscripts
            .replace(/\\text\s*\{\s*((?:(?:\\_)|_){2,})\s*\}/g, '\\underline{\\hspace{3em}}')
            // Common malformed payload pattern from backend: \dot(m) -> \dot{m}
            .replace(/\\dot\s*\(\s*([a-zA-Z0-9]+)\s*\)/g, '\\dot{$1}')
            // Another malformed payload pattern: \text(foo) -> \text{foo}
            .replace(/\\text\s*\(([^()]+)\)/g, '\\text{$1}')
            // Fix malformed table/cases separators from dirty payloads: "\&" -> "&"
            .replace(/\\&/g, '&')
            // Do not rewrite `\ ` (backslash + space): it is valid TeX spacing before \mathrm/\text.
            // Replacing it with `\\` inserts line breaks in KaTeX and splits values from units.
            // Normalize escaped underscores in plain latex contexts
            .replace(/\\_/g, '_');

    const normalizePlainTextLatexTokens = (value) =>
        value
            // Underscore-only \text{...} leaked into prose — show a blank line
            .replace(/\\text\s*\{\s*((?:(?:\\_)|_){2,})\s*\}/g, '________')
            // Render common fraction latex that appears outside $...$ as readable text
            .replace(/\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}/g, '($1)/($2)')
            .replace(/\\dfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}/g, '($1)/($2)')
            .replace(/\\tfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}/g, '($1)/($2)')
            .replace(/\\ldots/g, '…')
            // Improve readability for latex operators that appear in prose without $...$
            .replace(/\\times/g, '×')
            .replace(/\\cdot/g, '·')
            .replace(/\\leq/g, '≤')
            .replace(/\\geq/g, '≥')
            .replace(/\\neq/g, '≠')
            // Common greek symbols in solution prose
            .replace(/\\lambda/g, 'λ')
            .replace(/\\mu/g, 'μ')
            .replace(/\\theta/g, 'θ')
            .replace(/\\omega/g, 'ω')
            .replace(/\\alpha/g, 'α')
            .replace(/\\beta/g, 'β')
            .replace(/\\gamma/g, 'γ')
            .replace(/\\delta/g, 'δ')
            .replace(/\\bar\{([A-Za-zα-ωΑ-Ω])\}/g, '$1̄')
            .replace(/\\pi/g, 'π')
            .replace(/\bpi\s*\/\s*(\d+)\b/g, 'π/$1')
            // Common escaped text artifacts
            .replace(/\\_/g, '_');

    const isLikelySentenceWrappedAsMath = (value) => {
        const raw = String(value || '')
        const strongMathSignal = /\\(mathcal|frac|dfrac|tfrac|left|right|sum|int|partial|nabla|cdot|times|begin\{)/.test(raw)
        if (strongMathSignal) return false

        const cleaned = String(value || '')
            .replace(/\\[a-zA-Z]+/g, ' ')
            .replace(/[{}_^$=()+\-*/[\]<>]/g, ' ')
            .replace(/\d+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
        const words = cleaned ? cleaned.split(' ').filter((w) => w.length > 1) : []
        const hasSentenceSignal = /[,.]|\\text\{|\bif\b|\bthen\b|\bmatrix\b/i.test(raw)
        return words.length >= 7 && hasSentenceSignal
    }

    // Helper to render math string using katex
    const renderMath = (math, isDisplayMode) => {
        try {
            const isDev = typeof import.meta !== 'undefined' && import.meta.env?.DEV;
            return katex.renderToString(normalizeCommonLatexTypos(math), {
                displayMode: isDisplayMode,
                throwOnError: Boolean(isDev),
                output: 'html',
                strict: false,
                trust: true
            });
        } catch (e) {
            console.error("KaTeX Error:", e);
            return math;
        }
    };

    // Regex to split text by delimiters: $$...$$, \[...\], $...$, or \(...\)
    // Capture groups: 1=$$block$$, 2=\[block\], 3=$inline$, 4=\(inline\)
    const regex = /(\$\$[\s\S]*?\$\$)|(\\\[[\s\S]*?\\\])|(\$[\s\S]*?\$)|(\\\([\s\S]*?\\\))/g;

    // Wrap bare LaTeX environment fragments (e.g. \begin{cases}...\end{cases}) without forcing whole prose into math mode.
    const withWrappedEnvironments = !hasMathDelimiters && hasLatexEnvironment
        ? normalizedText.replace(
            /(\\begin\{[a-zA-Z*]+\}[\s\S]*?\\end\{[a-zA-Z*]+\})/g,
            (_m, envBlock) => `$$${envBlock}$$`
        )
        : normalizedText;

    // Fallback only for short/full-latex payloads, otherwise preserve normal text spacing.
    const safeText = shouldAutoWrapWholeMath ? `$${withWrappedEnvironments}$` : withWrappedEnvironments;
    const parts = safeText.split(regex);

    return (
        <span className={block ? "block w-full" : ""}>
            {parts.map((part, index) => {
                if (!part) return null;

                if (
                    (part.startsWith('$$') && part.endsWith('$$') && part.length >= 4) ||
                    (part.startsWith('\\[') && part.endsWith('\\]') && part.length >= 4)
                ) {
                    // Block math
                    const math = part.slice(2, -2);
                    const html = renderMath(math, true);
                    return <span key={index} className="block my-4 text-center" dangerouslySetInnerHTML={{ __html: html }} />;
                } else if (
                    (part.startsWith('$') && part.endsWith('$') && part.length >= 2) ||
                    (part.startsWith('\\(') && part.endsWith('\\)') && part.length >= 4)
                ) {
                    // Inline math — small horizontal gap so prose does not touch formulas
                    const math = part.startsWith('$') ? part.slice(1, -1) : part.slice(2, -2);
                    if (isLikelySentenceWrappedAsMath(math)) {
                        return (
                            <span key={index} className="inline">
                                <ReactMarkdown components={{ p: 'span' }}>
                                    {normalizePlainTextLatexTokens(math)}
                                </ReactMarkdown>
                            </span>
                        );
                    }
                    const html = renderMath(math, false);
                    return (
                        <span
                            key={index}
                            className={inlineMathClass}
                            dangerouslySetInnerHTML={{ __html: html }}
                        />
                    );
                } else {
                    // Regular markdown text
                    return (
                        <span key={index} className="inline">
                            <ReactMarkdown components={{ p: 'span' }}>
                                {normalizePlainTextLatexTokens(part)}
                            </ReactMarkdown>
                        </span>
                    );
                }
            })}
        </span>
    );
};

export default LatexRenderer;

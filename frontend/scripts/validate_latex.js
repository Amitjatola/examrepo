import fs from 'fs';
import katex from 'katex';

const API_URL = 'http://localhost:8000/api/v1';

async function fetchAllQuestions() {
    console.log('Fetching questions from API...');
    let allQuestions = [];
    let page = 1;
    let hasMore = true;

    while (hasMore) {
        try {
            const response = await fetch(`${API_URL}/search?page=${page}&page_size=100`);
            if (!response.ok) {
                console.error(`API returned status: ${response.status} on page ${page}`);
                break;
            }
            const data = await response.json();
            if (data.questions && data.questions.length > 0) {
                allQuestions = allQuestions.concat(data.questions);
                page++;
                if (data.questions.length < 100) {
                    hasMore = false;
                }
            } else {
                hasMore = false;
            }
        } catch (error) {
            console.error(`Failed to fetch questions on page ${page}:`, error);
            hasMore = false;
        }
    }
    console.log(`Successfully fetched ${allQuestions.length} questions.`);
    return allQuestions;
}

// Helper to safely extract all text from nested objects/arrays (like 'options')
function extractAllText(obj) {
    if (typeof obj === 'string') return [obj];
    if (Array.isArray(obj)) return obj.flatMap(extractAllText);
    if (obj !== null && typeof obj === 'object') return Object.values(obj).flatMap(extractAllText);
    return [];
}

function extractLatex(text) {
    if (!text) return [];

    // DEFINED LOCALLY: Prevents the lastIndex state bug across multiple function calls
    const localLatexRegex = /(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/g;
    const matches = [];
    let match;

    while ((match = localLatexRegex.exec(text)) !== null) {
        let original = match[0];
        let latex = original;

        // Strip delimiters
        if (latex.startsWith('$$') && latex.endsWith('$$')) {
            latex = latex.substring(2, latex.length - 2);
        } else if (latex.startsWith('$') && latex.endsWith('$')) {
            latex = latex.substring(1, latex.length - 1);
        }

        // LINE-BY-LINE TRACKING: Calculate line number based on index
        const textUpToMatch = text.substring(0, match.index);
        const lineNumber = (textUpToMatch.match(/\n/g) || []).length + 1;

        matches.push({
            original: original,
            latex: latex.trim(),
            lineNumber: lineNumber
        });
    }
    return matches;
}

// Comprehensive backslash fixer for common API escaping issues
function attemptAutoFix(latexString) {
    return latexString
        // Replace double backslashes followed by a letter with a single backslash
        .replace(/\\\\([A-Za-z])/g, '\\$1')
        // Catch common commands that often get mangled
        .replace(/\\\\(begin|end|text|frac|sqrt|left|right|sin|cos|tan|theta|alpha|beta|gamma|infty|circ|pi|mu|rho)/g, '\\$1');
}

async function validateLatex() {
    const questions = await fetchAllQuestions();
    if (questions.length === 0) {
        console.log('No questions found to validate.');
        return;
    }

    console.log(`Validating LaTeX for ${questions.length} questions...`);
    const brokenItems = [];
    let totalEquationsProcessed = 0;

    questions.forEach(q => {
        // Safely extract text fields without using JSON.stringify
        const fieldsToSearch = [
            { name: 'question_text', texts: extractAllText(q.question_text) },
            { name: 'question_text_latex', texts: extractAllText(q.question_text_latex) },
            { name: 'explanation', texts: extractAllText(q.explanation) },
            { name: 'options', texts: extractAllText(q.options) }
        ];

        fieldsToSearch.forEach(field => {
            field.texts.forEach(textSegment => {
                const latexBlocks = extractLatex(textSegment);

                latexBlocks.forEach(block => {
                    totalEquationsProcessed++;
                    try {
                        // Dry run render
                        katex.renderToString(block.latex, {
                            throwOnError: true,
                            displayMode: block.original.startsWith('$$')
                        });
                    } catch (error) {
                        let suggestedFix = null;

                        // Attempt auto-fix
                        try {
                            const fixedLatex = attemptAutoFix(block.latex);
                            katex.renderToString(fixedLatex, {
                                throwOnError: true,
                                displayMode: block.original.startsWith('$$')
                            });
                            suggestedFix = fixedLatex;
                        } catch (fixError) {
                            // Fix failed, leave as null
                        }

                        brokenItems.push({
                            question_id: q.question_id,
                            field: field.name,
                            line: block.lineNumber,
                            original_string: block.original,
                            error: error.message,
                            suggested_fix: suggestedFix
                        });
                    }
                });
            });
        });
    });

    console.log(`\nProcessed a total of ${totalEquationsProcessed} LaTeX equations.`);

    if (brokenItems.length > 0) {
        console.log(`Found ${brokenItems.length} broken LaTeX strings. Writing to broken_latex.log...`);

        const logContent = brokenItems.map(item =>
            `Question ID: ${item.question_id}\n` +
            `Field: ${item.field} (Line ${item.line})\n` +
            `Error: ${item.error}\n` +
            `Broken LaTeX:\n${item.original_string}\n` +
            (item.suggested_fix ? `Suggested Fix:\n$${item.suggested_fix}$\n` : `Suggested Fix: None\n`) +
            `--------------------------------------------------\n`
        ).join('\n');

        fs.writeFileSync('broken_latex.log', logContent);
        console.log('Done.');
    } else {
        console.log('All LaTeX strings are valid!');
        fs.writeFileSync('broken_latex.log', `Checked ${totalEquationsProcessed} equations. All valid!\n`);
    }
}

validateLatex();
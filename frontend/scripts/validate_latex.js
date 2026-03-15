import fs from 'fs';
import katex from 'katex';

const API_URL = 'http://localhost:8000/api/v1';

// Regex to find LaTeX blocks ($...$ or $$...$$)
const latexRegex = /(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/g;

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
                // Check if we've reached the end
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

function extractLatex(text) {
    if (!text) return [];
    const matches = [];
    let match;
    while ((match = latexRegex.exec(text)) !== null) {
        // Remove the outer $ or $$ delimiters for katex rendering
        let latex = match[0];
        if (latex.startsWith('$$') && latex.endsWith('$$')) {
            latex = latex.substring(2, latex.length - 2);
        } else if (latex.startsWith('$') && latex.endsWith('$')) {
            latex = latex.substring(1, latex.length - 1);
        }
        matches.push({ original: match[0], latex: latex.trim() });
    }
    return matches;
}

async function validateLatex() {
    const questions = await fetchAllQuestions();
    if (questions.length === 0) {
        console.log('No questions found to validate.');
        return;
    }

    console.log(`Validating LaTeX for ${questions.length} questions...`);
    const brokenItems = [];

    questions.forEach(q => {
        const fieldsToSearch = [
            { name: 'question_text', text: q.question_text },
            { name: 'question_text_latex', text: q.question_text_latex },
            { name: 'explanation', text: typeof q.explanation === 'string' ? q.explanation : JSON.stringify(q.explanation) },
            { name: 'options', text: typeof q.options === 'string' ? q.options : JSON.stringify(q.options) }
        ];

        fieldsToSearch.forEach(field => {
            const latexBlocks = extractLatex(field.text);
            
            latexBlocks.forEach(block => {
                try {
                    // Dry run render
                    katex.renderToString(block.latex, {
                        throwOnError: true,
                        displayMode: block.original.startsWith('$$')
                    });
                } catch (error) {
                    let suggestedFix = null;
                    
                    // Attempt an auto-fix: Many errors are due to double-escaped backslashes (\\circ instead of \circ).
                    // Or newline issues. Let's try replacing \\ with \ where it might be a command.
                    // Except for \\\\ which might be intended for newline. 
                    try {
                        let fixedLatex = block.latex
                            .replace(/\\\\([A-Za-z])/g, '\\$1') // Change \\circ to \circ, \\infty to \infty
                            .replace(/\\\\begin/g, '\\begin')
                            .replace(/\\\\end/g, '\\end')
                            .replace(/\\\\text/g, '\\text')
                            .replace(/\\\\frac/g, '\\frac')
                            .replace(/\\\\sqrt/g, '\\sqrt')
                            .replace(/\\\\left/g, '\\left')
                            .replace(/\\\\right/g, '\\right')
                            .replace(/\\\\sin/g, '\\sin')
                            .replace(/\\\\cos/g, '\\cos')
                            .replace(/\\\\tan/g, '\\tan')
                            .replace(/\\\\theta/g, '\\theta')
                            .replace(/\\\\alpha/g, '\\alpha')
                            .replace(/\\\\beta/g, '\\beta')
                            .replace(/\\\\gamma/g, '\\gamma')
                            .replace(/\\\\infty/g, '\\infty')
                            .replace(/\\\\circ/g, '\\circ')
                            .replace(/\\\\pi/g, '\\pi')
                            .replace(/\\\\mu/g, '\\mu')
                            .replace(/\\\\rho/g, '\\rho');

                        katex.renderToString(fixedLatex, {
                            throwOnError: true,
                            displayMode: block.original.startsWith('$$')
                        });
                        suggestedFix = fixedLatex;
                    } catch (fixError) {
                        // If it still fails, just leave suggestedFix as null
                    }

                    brokenItems.push({
                        question_id: q.question_id,
                        field: field.name,
                        original_string: block.original,
                        latex_content: block.latex,
                        error: error.message,
                        suggested_fix: suggestedFix
                    });
                }
            });
        });
    });

    if (brokenItems.length > 0) {
        console.log(`Found ${brokenItems.length} broken LaTeX strings. Writing to broken_latex.log...`);
        const logContent = brokenItems.map(item => 
            `Question ID: ${item.question_id}\n` +
            `Field: ${item.field}\n` +
            `Error: ${item.error}\n` +
            `Broken LaTeX:\n${item.original_string}\n` +
            (item.suggested_fix ? `Suggested Fix:\n$${item.suggested_fix}$\n` : `Suggested Fix: None\n`) +
            `--------------------------------------------------\n`
        ).join('\n');
        
        fs.writeFileSync('broken_latex.log', logContent);
        console.log('Done.');
    } else {
        console.log('All LaTeX strings are valid!');
        fs.writeFileSync('broken_latex.log', 'All LaTeX strings are valid!\n');
    }
}

validateLatex();

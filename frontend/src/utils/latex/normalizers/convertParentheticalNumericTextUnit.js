/**
 * Unwraps "(330 ,\\text{MN/m}^2)" style units into inline math so KaTeX runs.
 * Only matches a numeric head to avoid "(x)" placeholders.
 */

export const convertParentheticalNumericTextUnit = (raw) =>
    String(raw ?? '').replace(
        /\(\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*(\\text\{[^}]+\}(?:\s*\^(?:\{[^}]+\}|[0-9A-Za-z]+))?)\s*\)/g,
        (_full, num, tex) => `$${num}\\,${tex}$`
    )

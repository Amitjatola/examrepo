#!/usr/bin/env node
/**
 * Reads Playwright JSON output (`e2e-results/test-results.json`) and writes
 * `e2e-reports/E2E_BUG_REPORT_FOR_CURSOR.md` — structured for AI/code assistants.
 *
 * Usage (from frontend/): npm run test:e2e && npm run test:e2e:bugs
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const jsonPath = path.join(root, 'e2e-results', 'test-results.json')
const outDir = path.join(root, 'e2e-reports')
const outFile = path.join(outDir, 'E2E_BUG_REPORT_FOR_CURSOR.md')

const walkSuite = (suite, prefix, failures) => {
  const parts = [prefix, suite.title].filter(Boolean)
  const suitePath = parts.join(' > ')
  const file = suite.file || ''

  for (const spec of suite.specs || []) {
    const specFile = spec.file || file
    for (const test of spec.tests || []) {
      for (const res of test.results || []) {
        if (res.status === 'failed' || res.status === 'timedOut') {
          const err = res.error || {}
          failures.push({
            suitePath,
            specTitle: spec.title || test.projectName || 'test',
            file: specFile,
            line: spec.line,
            column: spec.column,
            status: res.status,
            message: err.message || String(err.value || res.status),
            stack: err.stack || '',
          })
        }
      }
    }
  }

  for (const child of suite.suites || []) {
    walkSuite(child, suitePath || prefix, failures)
  }
}

const main = () => {
  if (!fs.existsSync(jsonPath)) {
    fs.mkdirSync(outDir, { recursive: true })
    const stub = `# E2E bug report (Cursor-ready)

**Status:** No JSON results found.

Run from \`frontend/\`:

\`\`\`bash
npm run test:e2e && npm run test:e2e:bugs
\`\`\`

Expected input: \`e2e-results/test-results.json\` (Playwright JSON reporter).
`
    fs.writeFileSync(outFile, stub, 'utf8')
    console.warn(`[e2e-bugs] Missing ${jsonPath}; wrote placeholder ${outFile}`)
    process.exit(0)
    return
  }

  const raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'))
  const failures = []
  for (const suite of raw.suites || []) {
    walkSuite(suite, '', failures)
  }

  const stats = raw.stats || {}
  const lines = []
  lines.push('# E2E bug report for Cursor')
  lines.push('')
  lines.push('Use this file as **single context** for fixing UI/regression bugs found by Playwright.')
  lines.push('')
  lines.push('## Run metadata')
  lines.push('')
  lines.push(`- **Generated:** ${new Date().toISOString()}`)
  lines.push(`- **Playwright stats:** ${JSON.stringify(stats)}`)
  lines.push(`- **Source:** \`feature.md\` website map + critical flows (landing, sidebar, premium, year/mock exam, search).`)
  lines.push('')
  lines.push('## How to fix (for assistants)')
  lines.push('')
  lines.push('1. Open the **file** under **Primary location**.')
  lines.push('2. Reproduce locally: \`cd frontend && npm run test:e2e -- --headed <optional grep>\`.')
  lines.push('3. Cross-check **feature.md** → *Where features live* table for intended \`MainContent\` \`view\`.')
  lines.push('4. Prefer accessibility-focused selectors (\`getByRole\`, labels); avoid brittle CSS.')
  lines.push('')
  if (!failures.length) {
    lines.push('## Failures')
    lines.push('')
    lines.push('_None — all E2E tests passed._')
    lines.push('')
  } else {
    lines.push('## Failures (fix in order)')
    lines.push('')
    failures.forEach((f, i) => {
      const id = String(i + 1).padStart(3, '0')
      lines.push(`### BUG-${id}`)
      lines.push('')
      lines.push(`- **Severity:** unknown (set manually — blocker / major / minor)`)
      lines.push(`- **Suite path:** ${f.suitePath || '(root)'}`)
      lines.push(`- **Test / spec:** ${f.specTitle}`)
      lines.push(`- **Primary location:** \`${f.file}\`${f.line != null ? ` (line ~${f.line})` : ''}`)
      lines.push(`- **Playwright status:** ${f.status}`)
      lines.push('- **Observed (error message):**')
      lines.push('')
      lines.push('```')
      lines.push((f.message || '').trim() || '(no message)')
      lines.push('```')
      if (f.stack) {
        lines.push('- **Stack (trimmed):**')
        lines.push('')
        lines.push('```')
        lines.push(f.stack.split('\n').slice(0, 25).join('\n'))
        lines.push('```')
      }
      lines.push('- **Expected:** Test assertion should pass — compare with **feature.md** behavior for that surface.')
      lines.push('- **Suggested owners:** `frontend/src/components/MainContent.jsx`, related view component, or API if search/auth.')
      lines.push('')
    })
  }

  fs.mkdirSync(outDir, { recursive: true })
  fs.writeFileSync(outFile, lines.join('\n'), 'utf8')
  console.log(`[e2e-bugs] Wrote ${outFile} (${failures.length} failure(s))`)
}

main()

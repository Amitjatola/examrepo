/**
 * Validate one LaTeX expression via KaTeX (no network).
 * Reads UTF-8 expression from stdin; prints "OK" or writes error to stderr and exits 1.
 *
 * Environment:
 *   KATEX_PKG_DIR — absolute path to the `katex` npm package root
 *                   (e.g. repo/frontend/node_modules/katex)
 */
'use strict'

const fs = require('fs')
const path = require('path')

const pkgDir = process.env.KATEX_PKG_DIR
if (!pkgDir) {
  console.error('KATEX_PKG_DIR is not set')
  process.exit(2)
}

const katexMain = path.join(pkgDir, 'dist', 'katex.js')
if (!fs.existsSync(katexMain)) {
  console.error('Missing KaTeX bundle at', katexMain)
  process.exit(2)
}

const katex = require(katexMain)

const expr = fs.readFileSync(0, 'utf8').trimEnd()
if (!expr.length) {
  console.error('empty stdin')
  process.exit(2)
}
try {
  katex.renderToString(expr, { throwOnError: true, output: 'html', strict: 'warn' })
  process.stdout.write('OK\n')
} catch (e) {
  console.error(String(e && e.message ? e.message : e))
  process.exit(1)
}

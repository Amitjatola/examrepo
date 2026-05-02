/**
 * Batch KaTeX validation: read JSON Lines from stdin, one object per line:
 *   {"id":0,"tex":"x^2"}
 * Print one result line per input:
 *   {"id":0,"ok":true}  or  {"id":0,"ok":false,"error":"..."}
 * KATEX_PKG_DIR must point at the katex package root (see validate_latex.py).
 */
'use strict'

const fs = require('fs')
const path = require('path')
const readline = require('readline')

const pkgDir = process.env.KATEX_PKG_DIR
if (!pkgDir) {
  console.error('KATEX_PKG_DIR is not set')
  process.exit(2)
}
const katexMain = path.join(pkgDir, 'dist', 'katex.js')
if (!fs.existsSync(katexMain)) {
  console.error('Missing', katexMain)
  process.exit(2)
}
const katex = require(katexMain)

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity })

const handleLine = (line) => {
  const trimmed = line.trim()
  if (!trimmed) {
    return
  }
  let row
  try {
    row = JSON.parse(trimmed)
  } catch (e) {
    process.stdout.write(
      JSON.stringify({ id: null, ok: false, error: 'json parse: ' + String(e.message) }) + '\n',
    )
    return
  }
  const id = row.id
  const tex = row.tex
  if (typeof tex !== 'string' || !tex.length) {
    process.stdout.write(JSON.stringify({ id, ok: true, skip: true }) + '\n')
    return
  }
  try {
    katex.renderToString(tex, { throwOnError: true, output: 'html', strict: 'warn' })
    process.stdout.write(JSON.stringify({ id, ok: true }) + '\n')
  } catch (e) {
    process.stdout.write(
      JSON.stringify({ id, ok: false, error: String(e && e.message ? e.message : e) }) + '\n',
    )
  }
}

rl.on('line', handleLine)
rl.on('close', () => process.exit(0))

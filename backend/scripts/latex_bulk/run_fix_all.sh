#!/usr/bin/env bash
# Fix LaTeX for all question JSON under QUESTIONS_ROOT (folder-per-question layout).
# Repo root on this machine — edit AEROGATE if your clone path differs.
set -euo pipefail

AEROGATE="/Users/amitjatola/.gemini/antigravity/scratch/aerogate"
LB="$AEROGATE/backend/scripts/latex_bulk"

# Default: bundled sample tree. Override to your export folder, e.g.:
#   export QUESTIONS_ROOT="$AEROGATE/frontend/output"
#   export QUESTIONS_ROOT="/Volumes/external/gate_questions"
QUESTIONS_ROOT="${QUESTIONS_ROOT:-$LB/samples/year_layout}"

OUT_ROOT="${OUT_ROOT:-$LB/out/latex_cleaned}"
REPORT="${REPORT:-$LB/out/all_katex_failures.log}"
SUMMARY="${SUMMARY:-$LB/out/all_folder_summary.json}"

echo "AEROGATE=$AEROGATE"
echo "QUESTIONS_ROOT=$QUESTIONS_ROOT"
echo "OUT_ROOT=$OUT_ROOT"

cd "$AEROGATE/frontend"
npm install

cd "$LB"
python3 process_question_folder.py \
  --root "$QUESTIONS_ROOT" \
  --output-root "$OUT_ROOT" \
  --report "$REPORT" \
  --summary-json "$SUMMARY"

echo "Done. Cleaned JSON under: $OUT_ROOT"
echo "Summary: $SUMMARY"
echo "KaTeX failures (if any): $REPORT"

# LaTeX bulk cleanup + KaTeX validation

Deterministic, offline batch tooling for question JSON (no AI, no paid APIs).

## What it does

- **`latex_fixers.py`**: string + JSON-tree transforms (fractions, spacing, `\\\\` → `\\`, `%`/`&`/`_` hygiene, conservative `$...$` wrapping).
- **`process_json.py`**: reads a JSON export (`[...]` or `{ "questions": [...] }`), writes cleaned JSON + optional flattened CSV for spreadsheets.
- **`process_question_folder.py`**: walks **one `.json` file per question** (same folder pattern as `backend/scripts/import_questions.py`: `<root>/<YEAR>/*.json` or nested dirs), runs cleanup + KaTeX per file, writes results, then moves on. Aggregates failures with `file=relative/path.json` in the report.
- **`validate_latex.py` + `validate_katex.cjs`**: extracts math fragments from every string field and runs **KaTeX** (`throwOnError: true`) via `frontend/node_modules/katex/dist/katex.js`. Writes a failure log with **question_id / JSON path / fragment / error**.

> **Honest scope:** no automated pipeline can mathematically guarantee “100% fixes” for ambiguous mixed text/math without human rules. This toolkit maximizes **batch coverage**, then **surfaces** what KaTeX still rejects.

## Requirements

- Python **3.10+** (stdlib only for cleanup/validation driver).
- **Node 18+** and **`katex`** installed from the repo app (see below). Do **not** run `npm install KaTeX` as a package name — the dependency is **`katex`** (lowercase) in `frontend/package.json`.

### Install Node deps (safe copy-paste)

Run **one command per line**. Do not paste `# …` comments on the same line as `npm install` (some terminals/tools forward `#` to npm and you get `EINVALIDTAGNAME`).

```bash
cd path/to/aerogate/frontend
npm install
```

### One-shot (this repo clone — absolute paths)

Copy-paste exactly:

```bash
chmod +x /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/run_fix_all.sh
/Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/run_fix_all.sh
```

By default this processes **`samples/year_layout`** and writes to **`out/latex_cleaned/`**. To use your real export folder:

```bash
export QUESTIONS_ROOT="/Users/amitjatola/.gemini/antigravity/scratch/aerogate/frontend/output"
export OUT_ROOT="/Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/out/latex_cleaned"
/Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/run_fix_all.sh
```

(Create `frontend/output` with your `YEAR/*.json` tree if needed.)

Equivalent manual commands:

```bash
cd /Users/amitjatola/.gemini/antigravity/scratch/aerogate/frontend
npm install

cd /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk
mkdir -p out/latex_cleaned
python3 process_question_folder.py \
  --root /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/samples/year_layout \
  --output-root /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/out/latex_cleaned \
  --report /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/out/all_katex_failures.log \
  --summary-json /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend/scripts/latex_bulk/out/all_folder_summary.json
```

## Run cleanup (JSON + CSV)

From this directory:

```bash
cd backend/scripts/latex_bulk
mkdir -p out
python3 process_json.py \
  -i samples/input_sample.json \
  -o out/cleaned.json \
  --csv out/cleaned.csv
```

Optional: disable heuristic auto-wrapping of “math-looking” lines:

```bash
python3 process_json.py -i samples/input_sample.json -o out/cleaned.json --no-auto-wrap
```

**DB workflow:** export `questions` (or the rich JSON columns) to `export.json`, run the script, inspect `out/cleaned.csv`, then import/UPDATE via your migration tool or SQL.

## Per-question folder (`q1.json` trees)

**Replace placeholders** like `/path/to/frontend/output` with the real directory on your machine (for this project, imports often use `frontend/output` **if that folder exists** on your machine).

**Copy-paste: smoke test (works in a fresh clone)**

```bash
cd path/to/aerogate/backend/scripts/latex_bulk
python3 process_question_folder.py \
  --root samples/year_layout \
  --output-root out/demo_cleaned
```

**Your real data** (parallel output tree first, then review and swap paths as needed):

```bash
cd path/to/aerogate/backend/scripts/latex_bulk
python3 process_question_folder.py \
  --root ../../frontend/output \
  --output-root ../../frontend/output_latex_cleaned
```

Paths are relative to `latex_bulk`; adjust if your question tree lives elsewhere.

**In-place overwrite** (only after you trust the cleaned files)

```bash
python3 process_question_folder.py --root ../../frontend/output
```

**Every `*.json` under a root** (no `YEAR/` subfolders)

```bash
python3 process_question_folder.py --root /absolute/path/to/questions --scan recursive --output-root /absolute/path/to/questions_cleaned
```

**If you see `command not found: #`** — you pasted a line that starts with `#` as a shell command. In docs, lines starting with `#` are comments: skip them or type the real commands only.

Each file may be either one **object** `{ ... }` or a **one-element list** `[ { ... } ]` (both round-trip the same shape after processing).

Outputs:

- **`--summary-json`** (default `out/folder_run_summary.json`) — per file: `question_id`, `written`, `katex_failures`, load/processing `error`.
- **`--report`** — KaTeX failures; lines include `file=2024/Q01.json` when applicable.

Useful flags: `--dry-run`, `--no-validate`, `--no-auto-wrap`, `--strict` (exit `1` if any KaTeX fragment fails).

Sample: `samples/year_layout/2024/SAMPLE_Q1.json`.

## Run KaTeX validation

```bash
cd backend/scripts/latex_bulk
python3 validate_latex.py -i out/cleaned.json --report out/katex_failures.log
echo $?
```

- Exit code **0** → no failures recorded.
- Exit code **1** → see `out/katex_failures.log` for `(question_id, JSON path, fragment, KaTeX error)`.

The validator runs `node validate_katex.cjs` with **`KATEX_PKG_DIR`** pointing at `frontend/node_modules/katex` (no global `npm install -g` needed).

## Sample

- Input: `samples/input_sample.json`
- After processing, open `out/cleaned.json` and compare `tier_1_core_research.explanation` strings (fractions, `%`, `x^2` spacing).

## Fix LaTeX when data lives in **PostgreSQL** (not JSON files)

Questions are stored in table `questions` with **text** columns (`question_text`, `question_text_latex`, …) and **JSON** columns (`options`, `tier_0_classification` … `tier_4_metadata`). LaTeX appears across those fields.

### Recommended approach

1. **Backup** the `questions` table (requires `pg_dump` and `DATABASE_URL` in `backend/.env`):

```bash
cd /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend
./scripts/latex_bulk/backup_questions_table.sh
```

Writes `backend/backups/questions_table_<timestamp>.sql` (override directory with `BACKUP_DIR=/path`).

2. **Stop app traffic** to the DB while you run a bulk update, *or* run in a maintenance window.
3. **Use the in-DB script** (same `latex_fixers` as file pipelines). From **`backend/`**:

```bash
cd /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend
PYTHONPATH=. python scripts/latex_bulk/fix_questions_in_db.py --dry-run --limit 20
```

Inspect counts; then:

```bash
PYTHONPATH=. python scripts/latex_bulk/fix_questions_in_db.py
```

- By default the script **refreshes `search_content` and `embedding`** via `QuestionRepository._prepare_search_data` so search stays aligned with fixed text (embedding call can be slow for huge tables).
- Faster pass without reranking vectors:

```bash
PYTHONPATH=. python scripts/latex_bulk/fix_questions_in_db.py --skip-embedding
```

(Then run your existing **reindex** job if you have one, e.g. `scripts/reindex_questions.py`.)

4. **Legacy backslash-only repair** in DB (`tier_1` double-escaped `\\`): see **`backend/fix_latex.py`** — orthogonal; run before or after depending on whether raw dumps still contain `\\\\`.

5. **Validate a DB slice with KaTeX** (optional): `export_questions_for_validation.py` writes a JSON array; `validate_latex.py` checks fragments and **ignores `image_metadata.path`** (Windows-style paths are not math).

```bash
cd /Users/amitjatola/.gemini/antigravity/scratch/aerogate/backend
PYTHONPATH=. python scripts/latex_bulk/export_questions_for_validation.py --limit 30 -o scripts/latex_bulk/out/db_slice.json
cd scripts/latex_bulk
python3 validate_latex.py -i out/db_slice.json --report out/katex_db_slice.log
```

### Alternative: export → fix files → re-import

If you prefer not to touch production rows directly: export rows to JSON / folder-per-question → run **`process_question_folder.py`** or **`process_json.py`** → bulk import via your existing **`import_questions`** / migration tooling.

## Notes

- If your export double-escaped LaTeX (`\\\\frac`), the pipeline normalizes to `\frac` before other rules (see also legacy `backend/fix_latex.py` for DB-only backslash repair).
- CSV columns mirror common Aerogate fields; nested tiers are **JSON strings** in cells (`tier_1_core_research`, …).

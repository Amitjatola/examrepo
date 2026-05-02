#!/usr/bin/env python3
"""
Iterate per-question JSON files in a directory tree (same layout as `import_questions.py`):
  <root>/<YEAR>/*.json
  <root>/<YEAR>/<subdir>/*.json

For each file: load → apply LaTeX cleanup → validate with KaTeX → write output → next file.

Examples:
  python process_question_folder.py --root /path/to/frontend/output
  python process_question_folder.py --root ./data --scan recursive --output-root ./data_cleaned
  python process_question_folder.py --root ./out --dry-run --no-validate
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from latex_fixers import apply_full_pipeline

from validate_latex import (
    collect_failures_for_record,
    find_repo_root,
    write_failure_report,
)

ScanMode = Literal["import-layout", "recursive"]


@dataclass
class FileResult:
    path: str
    question_id: str
    written: bool
    katex_failures: int
    error: str | None = None


def discover_json_files(root: Path, scan: ScanMode) -> list[Path]:
    if not root.is_dir():
        return []
    if scan == "recursive":
        return sorted(p for p in root.rglob("*.json") if p.is_file())
    out: list[Path] = []
    for year_dir in sorted(root.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        for item in year_dir.iterdir():
            if item.is_file() and item.suffix == ".json":
                out.append(item)
            elif item.is_dir():
                for sub in item.iterdir():
                    if sub.is_file() and sub.suffix == ".json":
                        out.append(sub)
    return sorted(out)


def load_question_object(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Return (question_dict, meta) where meta records how to serialize back.
    meta: { "wrap": "dict" | "list" }
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw, {"wrap": "dict"}
    if isinstance(raw, list):
        if len(raw) == 1 and isinstance(raw[0], dict):
            return raw[0], {"wrap": "list"}
        raise ValueError(f"{path}: expected a single dict or a one-element list of dicts")
    raise ValueError(f"{path}: unsupported JSON root type {type(raw).__name__}")


def serialize_payload(data: dict[str, Any], meta: dict[str, Any]) -> Any:
    if meta.get("wrap") == "list":
        return [data]
    return data


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Per-file LaTeX cleanup + KaTeX validation for question JSON trees",
    )
    ap.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Folder containing per-question .json (see --scan)",
    )
    ap.add_argument(
        "--scan",
        choices=("import-layout", "recursive"),
        default="import-layout",
        help="import-layout: <root>/<YEAR>/*.json (matches import_questions.py). "
        "recursive: **/*.json under root.",
    )
    ap.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="If set, writes under this root preserving relative paths from --root. "
        "If omitted, overwrites each input file in place.",
    )
    ap.add_argument("--dry-run", action="store_true", help="Do not write files")
    ap.add_argument("--no-validate", action="store_true", help="Skip KaTeX checks")
    ap.add_argument("--no-auto-wrap", action="store_true", help="See latex_fixers auto_wrap")
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("out/folder_katex_failures.log"),
        help="Aggregated KaTeX failure log for all files",
    )
    ap.add_argument(
        "--summary-json",
        type=Path,
        default=Path("out/folder_run_summary.json"),
        help="Machine-readable run summary",
    )
    ap.add_argument("--node", default="node")
    ap.add_argument("--validator", type=Path, default=None)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any KaTeX failures (default: exit 0, still log failures)",
    )
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    sample_root = here / "samples/year_layout"
    validator = args.validator or (here / "validate_katex.cjs")
    if not args.no_validate:
        if not validator.is_file():
            print(f"Missing {validator}", file=sys.stderr)
            return 2
        repo = find_repo_root(here)
        fe = repo / "frontend"
        if not (fe / "node_modules" / "katex").is_dir():
            print("Run: cd frontend && npm install  (needs katex)", file=sys.stderr)
            return 2
    else:
        fe = find_repo_root(here) / "frontend"

    root_resolved = args.root.expanduser().resolve()
    if not root_resolved.is_dir():
        print(
            "ERROR: --root is not an existing directory:\n"
            f"  {root_resolved}\n\n"
            "Docs often use placeholders like /path/to/frontend/output — replace those with your real folder.\n"
            "Quick smoke test from this repo:\n"
            f"  python3 process_question_folder.py --root {sample_root} --output-root {here / 'out' / 'demo_cleaned'}",
            file=sys.stderr,
        )
        return 2

    files = discover_json_files(root_resolved, args.scan)  # type: ignore[arg-type]
    if not files:
        hint = ""
        if args.scan == "import-layout":
            hint = (
                "\nHint: import-layout only looks under <root>/<YEAR>/ with YEAR = digits (e.g. 2024). "
                "If your tree is flatter, use --scan recursive."
                f"\nTry the bundled sample: --root {sample_root}"
            )
        print(
            f"No .json files found under {root_resolved} (scan={args.scan}).{hint}",
            file=sys.stderr,
        )
        return 2

    all_failures: list = []
    results: list[FileResult] = []
    file_index = 0

    for path in files:
        rel = path.resolve().relative_to(root_resolved)
        err_msg: str | None = None
        written = False
        k_fail = 0
        qid = path.stem

        try:
            obj, meta = load_question_object(path)
            qid = str(obj.get("question_id") or path.stem)
            cleaned = apply_full_pipeline(obj, auto_wrap=not args.no_auto_wrap)

            if not args.no_validate:
                fails = collect_failures_for_record(
                    cleaned,
                    record_index=file_index,
                    node_exe=args.node,
                    validator=validator,
                    frontend_dir=fe,
                    source_file=str(rel).replace("\\", "/"),
                )
                k_fail = len(fails)
                all_failures.extend(fails)

            if not args.dry_run:
                out_path = (
                    args.output_root.resolve() / rel
                    if args.output_root
                    else path.resolve()
                )
                out_path.parent.mkdir(parents=True, exist_ok=True)
                payload = serialize_payload(cleaned, meta)
                out_path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                written = True
            else:
                written = False

        except Exception as e:  # noqa: BLE001 — batch tool: keep going
            err_msg = str(e)
            k_fail = 0

        results.append(
            FileResult(
                path=str(rel),
                question_id=qid,
                written=written,
                katex_failures=k_fail,
                error=err_msg,
            ),
        )
        file_index += 1

    if not args.no_validate and all_failures:
        write_failure_report(args.report, all_failures)

    summary = {
        "root": str(root_resolved),
        "scan": args.scan,
        "files_seen": len(files),
        "dry_run": args.dry_run,
        "output_root": str(args.output_root.resolve()) if args.output_root else None,
        "katex_failure_count": len(all_failures),
        "files_with_errors": sum(1 for r in results if r.error),
        "results": [asdict(r) for r in results],
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(
        f"Files: {len(files)} | written: {sum(1 for r in results if r.written)} | "
        f"load/processing errors: {sum(1 for r in results if r.error)} | "
        f"KaTeX fragment failures: {len(all_failures)}",
    )
    print(f"Summary: {args.summary_json}")
    if not args.no_validate:
        print(f"Failures log: {args.report if all_failures else '(none)'}")

    if args.strict and all_failures:
        return 1
    if any(r.error for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

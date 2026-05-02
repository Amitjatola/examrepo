#!/usr/bin/env python3
"""
Validate LaTeX fragments with KaTeX (Node). Logs failing (question_id, json path, error).

Requires:
  - Node 18+
  - `npm install` in repo `frontend/` (`katex` dependency)

Example:
  python validate_latex.py -i samples/input_sample.json --report latex_failures.log
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Failure:
    record_index: int
    record_key: str
    path: str
    fragment: str
    error: str
    source_file: str | None = None


_DISPLAY_DOLLAR = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
_INLINE_DOLLAR = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL)
_PARENS = re.compile(r"\\\((.+?)\\\)", re.DOTALL)
_BRACK = re.compile(r"\\\[(.+?)\\\]", re.DOTALL)
_PROSE_FOR_VALIDATE = re.compile(
    r"\b(first|second|then|when|note|use|constants|compute|risk|done|unescaped|the|and|for|with|from|into|"
    r"that|this|are|was|were|comment|half|value|question|answer|option|step|therefore|hence)\b",
    re.I,
)


def extract_latex_fragments(text: str) -> list[str]:
    """Pull plausible math spans from a mixed string."""
    if not text or not isinstance(text, str):
        return []
    frags: list[str] = []
    for rx in (_DISPLAY_DOLLAR, _INLINE_DOLLAR, _PARENS, _BRACK):
        frags.extend(m.group(1).strip() for m in rx.finditer(text) if m.group(1).strip())
    stripped = text.strip()
    if "\\" in stripped and "$" not in stripped and len(frags) == 0:
        if not _PROSE_FOR_VALIDATE.search(stripped):
            frags.append(stripped)
    dedup: list[str] = []
    for f in frags:
        if f not in dedup:
            dedup.append(f)
    return dedup


def find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "frontend" / "package.json").is_file():
            return p
    raise FileNotFoundError("Could not locate repo root (missing frontend/package.json)")


def katex_check(
    fragment: str,
    node_exe: str,
    validator: Path,
    *,
    module_dir: Path,
) -> str | None:
    """Return error message if invalid; None if OK."""
    proc = subprocess.run(
        [node_exe, str(validator)],
        input=(fragment + "\n").encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(module_dir),
        env={**os.environ, "KATEX_PKG_DIR": str(module_dir / "node_modules" / "katex")},
    )
    if proc.returncode == 0:
        return None
    err = proc.stderr.decode("utf-8", errors="replace").strip()
    if not err:
        err = proc.stdout.decode("utf-8", errors="replace").strip() or f"exit {proc.returncode}"
    return err


def walk_string_fields(obj: Any, base_path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(obj, str):
        yield base_path or "$", obj
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{base_path}.{k}" if base_path else str(k)
            yield from walk_string_fields(v, p)
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{base_path}[{i}]"
            yield from walk_string_fields(v, p)


def load_records(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("questions"), list):
        return [x for x in data["questions"] if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    raise ValueError("Unsupported JSON structure for records")


def record_key(rec: dict[str, Any], idx: int) -> str:
    return str(rec.get("question_id") or rec.get("id") or f"row_{idx}")


def _skip_string_for_katex_validation(json_path: str, s: str) -> bool:
    """File paths use backslashes; do not send them to KaTeX."""
    if "image_metadata" in json_path and json_path.endswith("path"):
        return True
    if isinstance(s, str) and ("\\raw_images\\" in s or "/raw_images/" in s or "\\\\raw_images\\\\" in s):
        return True
    if json_path.endswith(".Path") or json_path.endswith("Path"):
        return True
    if "image)" in json_path or "4-3)" in json_path:
        return True
    return False


def collect_failures_for_record(
    rec: dict[str, Any],
    *,
    record_index: int,
    node_exe: str,
    validator: Path,
    frontend_dir: Path,
    source_file: str | None = None,
) -> list[Failure]:
    """Run KaTeX on all extracted fragments for one question dict."""
    failures: list[Failure] = []
    for json_path, s in walk_string_fields(rec):
        if _skip_string_for_katex_validation(json_path, s):
            continue
        for frag in extract_latex_fragments(s):
            err = katex_check(frag, node_exe, validator, module_dir=frontend_dir)
            if err:
                failures.append(
                    Failure(
                        record_index=record_index,
                        record_key=record_key(rec, record_index),
                        path=json_path,
                        fragment=frag[:500],
                        error=err,
                        source_file=source_file,
                    ),
                )
    return failures


def _collect_fragment_jobs(records: list[dict[str, Any]]) -> list[tuple[int, str, str, str]]:
    """(record_index, record_key, json_path, fragment) in order."""
    jobs: list[tuple[int, str, str, str]] = []
    for idx, rec in enumerate(records):
        rk = record_key(rec, idx)
        for json_path, s in walk_string_fields(rec):
            if _skip_string_for_katex_validation(json_path, s):
                continue
            for frag in extract_latex_fragments(s):
                jobs.append((idx, rk, json_path, frag))
    return jobs


def collect_failures_batch(
    records: list[dict[str, Any]],
    *,
    node_exe: str,
    validator_jsonl: Path,
    frontend_dir: Path,
) -> list[Failure]:
    """Single Node process + KaTeX load; one JSON line per fragment."""
    jobs = _collect_fragment_jobs(records)
    failures: list[Failure] = []
    if not jobs:
        return failures

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".jsonl",
        delete=False,
    ) as tmp:
        for i, (_idx, _rk, _jp, frag) in enumerate(jobs):
            tmp.write(json.dumps({"id": i, "tex": frag}, ensure_ascii=False) + "\n")
        tmp_path = Path(tmp.name)

    try:
        proc = subprocess.run(
            [node_exe, str(validator_jsonl)],
            input=tmp_path.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(frontend_dir),
            env={**os.environ, "KATEX_PKG_DIR": str(frontend_dir / "node_modules" / "katex")},
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        print(f"batch validator failed: {err or proc.stdout.decode('utf-8', errors='replace')}", file=sys.stderr)
        return [
            Failure(
                record_index=-1,
                record_key="batch",
                path="validator",
                fragment="",
                error=err or f"exit {proc.returncode}",
                source_file=None,
            ),
        ]

    for line in proc.stdout.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("skip"):
            continue
        if row.get("ok"):
            continue
        fid = row.get("id")
        if not isinstance(fid, int) or fid < 0 or fid >= len(jobs):
            continue
        idx, rk, jp, frag = jobs[fid]
        failures.append(
            Failure(
                record_index=idx,
                record_key=rk,
                path=jp,
                fragment=(frag[:500] if isinstance(frag, str) else ""),
                error=str(row.get("error", "KaTeX error")),
                source_file=None,
            ),
        )
    return failures


def write_failure_report(report_path: Path, failures: list[Failure]) -> None:
    lines: list[str] = []
    for f in failures:
        file_b = f"file={f.source_file}\t" if f.source_file else ""
        lines.append(
            f"{file_b}index={f.record_index}\tquestion_id={f.record_key}\tpath={f.path}",
        )
        lines.append(f"  fragment={json.dumps(f.fragment, ensure_ascii=False)[:800]}")
        lines.append(f"  error={f.error}")
        lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate LaTeX via KaTeX; log failures")
    ap.add_argument("-i", "--input", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("latex_katex_failures.log"))
    ap.add_argument("--node", default="node", help="Node binary (default: node)")
    ap.add_argument(
        "--validator",
        type=Path,
        default=None,
        help="Path to validate_katex.cjs (per-fragment mode only)",
    )
    ap.add_argument(
        "--batch",
        action="store_true",
        help="Fast path: one Node process (validate_katex_jsonl.cjs) for all fragments (recommended for large exports)",
    )
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    validator = args.validator or (here / "validate_katex.cjs")
    validator_jsonl = here / "validate_katex_jsonl.cjs"

    repo = find_repo_root(here)
    fe = repo / "frontend"
    if not (fe / "node_modules" / "katex").is_dir():
        print(
            "Install KaTeX in frontend first: cd frontend && npm install",
            file=sys.stderr,
        )
        return 2

    records = load_records(args.input)
    failures: list[Failure] = []

    use_batch = args.batch or len(records) >= 100
    if use_batch:
        if not validator_jsonl.is_file():
            print(f"Missing {validator_jsonl}", file=sys.stderr)
            return 2
        failures.extend(
            collect_failures_batch(
                records,
                node_exe=args.node,
                validator_jsonl=validator_jsonl,
                frontend_dir=fe,
            ),
        )
    else:
        if not validator.is_file():
            print(f"Missing {validator}", file=sys.stderr)
            return 2
        for idx, rec in enumerate(records):
            failures.extend(
                collect_failures_for_record(
                    rec,
                    record_index=idx,
                    node_exe=args.node,
                    validator=validator,
                    frontend_dir=fe,
                ),
            )

    jobs_n = len(_collect_fragment_jobs(records))
    write_failure_report(args.report, failures)
    print(
        f"Records: {len(records)}; fragments_checked: {jobs_n}; KaTeX failures: {len(failures)}; "
        f"batch={use_batch}; report: {args.report}",
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

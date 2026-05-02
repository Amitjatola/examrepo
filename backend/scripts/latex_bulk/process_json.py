#!/usr/bin/env python3
"""
Bulk-clean question JSON (recursive LaTeX fixes) and export JSON + CSV.

Examples:
  python process_json.py -i samples/input_sample.json -o out/cleaned.json --csv out/cleaned.csv
  python process_json.py -i export.json -o export_cleaned.json --csv export_cleaned.csv --no-auto-wrap
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable

from latex_fixers import apply_full_pipeline


def load_records_and_wrapper(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)], None
    if isinstance(data, dict):
        if "questions" in data and isinstance(data["questions"], list):
            recs = [x for x in data["questions"] if isinstance(x, dict)]
            return recs, data
        return [data], None
    raise ValueError("Top-level JSON must be a list of objects or an object with key 'questions'")


def flatten_record_for_csv(rec: dict[str, Any]) -> dict[str, str]:
    """
    Flatten Aerogate-style fields to CSV cells (JSON in cells for tiers/options).
    """
    out: dict[str, str] = {}
    out["question_id"] = str(rec.get("question_id", ""))
    out["id"] = str(rec.get("id", ""))

    scalar_keys = (
        "question_text",
        "question_text_latex",
        "exam_name",
        "subject",
        "question_type",
        "answer_key",
    )
    for k in scalar_keys:
        v = rec.get(k)
        out[k] = "" if v is None else str(v)

    for k in ("year", "question_number", "marks", "negative_marks"):
        v = rec.get(k)
        out[k] = "" if v is None else str(v)

    json_keys = (
        "options",
        "image_metadata",
        "tier_0_classification",
        "tier_1_core_research",
        "tier_2_student_learning",
        "tier_3_enhanced_learning",
        "tier_4_metadata",
    )
    for k in json_keys:
        v = rec.get(k)
        if v is None:
            out[k] = ""
        elif isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = str(v)

    known = {
        "question_id",
        "id",
        *scalar_keys,
        *json_keys,
        "year",
        "question_number",
        "marks",
        "negative_marks",
    }
    extra = {k: v for k, v in rec.items() if k not in known}
    if extra:
        out["__extra_json__"] = json.dumps(extra, ensure_ascii=False)
    return out


def write_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    p = argparse.ArgumentParser(description="Bulk LaTeX cleanup for question JSON + CSV export")
    p.add_argument("-i", "--input", required=True, type=Path, help="Input .json path")
    p.add_argument("-o", "--output-json", required=True, type=Path, help="Output cleaned .json")
    p.add_argument("--csv", type=Path, default=None, help="Optional output .csv (flattened columns)")
    p.add_argument("--no-auto-wrap", action="store_true", help="Disable heuristic $...$ wrapping for mathish lines")
    args = p.parse_args()

    records, wrapper = load_records_and_wrapper(args.input)
    cleaned = [apply_full_pipeline(rec, auto_wrap=not args.no_auto_wrap) for rec in records]

    if wrapper is not None:
        payload: Any = {**wrapper, "questions": cleaned}
    else:
        payload = cleaned

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.csv:
        csv_rows = [flatten_record_for_csv(r) for r in cleaned]
        write_csv(args.csv, csv_rows)

    print(
        f"Processed {len(cleaned)} records → {args.output_json}"
        + (f", {args.csv}" if args.csv else ""),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

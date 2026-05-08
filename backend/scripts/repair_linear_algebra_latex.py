"""
Bulk-fix LaTeX-heavy content for Linear Algebra topic questions.

Usage (from repo root):
  export DATABASE_URL='postgresql+asyncpg://...'
  python backend/scripts/repair_linear_algebra_latex.py
"""

import asyncio
import json
import re
from copy import deepcopy
from datetime import datetime
from typing import Any

from sqlalchemy import text

from app.core.database import engine


TOPIC_NAME = "Linear Algebra"


def _sanitize_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    s = value.replace("\r\n", "\n").strip()

    # Frequent malformed LaTeX patterns seen in this dataset
    s = re.sub(r"\\dot\s*\(\s*([A-Za-z0-9]+)\s*\)", r"\\dot{\1}", s)
    s = re.sub(r"\\text\s*\(([^()]+)\)", r"\\text{\1}", s)
    s = s.replace(r"\&", "&")
    s = s.replace(r"\_", "_")

    # Fix row-separator style inside environment payloads: "\ " -> "\\ "
    def _fix_env(match: re.Match) -> str:
        env = match.group(1)
        body = match.group(2)
        body = re.sub(r"\\\s+", r"\\\\ ", body)
        return f"\\begin{{{env}}}{body}\\end{{{env}}}"

    s = re.sub(
        r"\\begin\{(bmatrix|pmatrix|vmatrix|cases)\}([\s\S]*?)\\end\{\1\}",
        _fix_env,
        s,
    )

    return s


def _latex_tokenize(value: str) -> str:
    token_map = {
        r"\blambda\b": r"\\lambda",
        r"\balpha\b": r"\\alpha",
        r"\bbeta\b": r"\\beta",
        r"\bgamma\b": r"\\gamma",
        r"\btheta\b": r"\\theta",
        r"\bomega\b": r"\\omega",
        r"\bmu\b": r"\\mu",
        r"\bpi\b": r"\\pi",
    }
    out = value
    for pattern, repl in token_map.items():
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def _sanitize_option(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    s = _sanitize_text(value)

    if "$" in s:
        return s

    looks_formula_like = bool(
        re.search(r"[\\^_/]|(?:\bpi\b|\blambda\b|\balpha\b)|\d+\s*/\s*\d+", s, flags=re.IGNORECASE)
    )

    has_long_prose = len(re.findall(r"[A-Za-z]+", s)) >= 7

    if looks_formula_like and not has_long_prose:
        s = _latex_tokenize(s)
        return f"${s}$"

    return s


def _clean_steps(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in items:
        if not isinstance(raw, str):
            continue
        s = _sanitize_text(raw)
        if not s or s.lower() == "none":
            continue
        key = re.sub(r"^step\s*\d+\s*:\s*", "", s, flags=re.IGNORECASE)
        key = re.sub(r"\s+", " ", key).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(s)
    return cleaned


def _sanitize_tier1(t1: Any) -> dict:
    src = deepcopy(t1) if isinstance(t1, dict) else {}

    av = src.setdefault("answer_validation", {})
    av["reasoning"] = _sanitize_text(av.get("reasoning"))

    exp = src.setdefault("explanation", {})
    exp["step_by_step"] = _clean_steps(exp.get("step_by_step"))
    formulas = exp.get("formulas_used")
    if isinstance(formulas, list):
        exp["formulas_used"] = [_sanitize_text(x) for x in formulas if isinstance(x, str) and x.strip()]
    else:
        exp["formulas_used"] = []

    sbs = src.setdefault("step_by_step_solution", {})
    sbs["solution_path"] = _sanitize_text(sbs.get("solution_path"))
    key_insights = sbs.get("key_insights")
    if isinstance(key_insights, list):
        sbs["key_insights"] = [_sanitize_text(x) for x in key_insights if isinstance(x, str) and x.strip()]
    else:
        sbs["key_insights"] = []
    if not sbs.get("total_steps"):
        sbs["total_steps"] = len(exp["step_by_step"])

    hints = src.get("hints")
    if isinstance(hints, list):
        src["hints"] = [_sanitize_text(x) for x in hints if isinstance(x, str) and x.strip() and x.strip().lower() != "none"]
    else:
        src["hints"] = []

    return src


async def main() -> None:
    async with engine.begin() as conn:
        rows = (
            await conn.execute(
                text(
                    """
                    SELECT
                      question_id,
                      question_text,
                      question_text_latex,
                      options,
                      tier_1_core_research
                    FROM questions
                    WHERE lower(coalesce(tier_1_core_research->'hierarchical_tags'->'topic'->>'name', '')) LIKE :topic
                    ORDER BY question_id
                    """
                ),
                {"topic": f"%{TOPIC_NAME.lower()}%"},
            )
        ).fetchall()

        if not rows:
            raise SystemExit(f"No questions found for topic: {TOPIC_NAME}")

        patched = 0
        for row in rows:
            qid = row[0]
            qt = row[1]
            qtl = row[2]
            options = row[3]
            t1 = row[4]

            new_qt = _sanitize_text(qt)
            new_qtl_base = qtl if isinstance(qtl, str) and qtl.strip() else qt
            new_qtl = _sanitize_text(new_qtl_base)

            if isinstance(options, dict):
                new_opts = {k: _sanitize_option(v) for k, v in options.items()}
            else:
                new_opts = options

            new_t1 = _sanitize_tier1(t1)

            await conn.execute(
                text(
                    """
                    UPDATE questions
                    SET question_text = :qt,
                        question_text_latex = :qtl,
                        options = CAST(:opts AS jsonb),
                        tier_1_core_research = CAST(:t1 AS jsonb),
                        updated_at = :updated_at
                    WHERE question_id = :qid
                    """
                ),
                {
                    "qid": qid,
                    "qt": new_qt,
                    "qtl": new_qtl,
                    "opts": json.dumps(new_opts) if new_opts is not None else None,
                    "t1": json.dumps(new_t1),
                    "updated_at": datetime.utcnow(),
                },
            )
            patched += 1

    print(f"Patched {patched} questions in topic '{TOPIC_NAME}'.")


if __name__ == "__main__":
    asyncio.run(main())

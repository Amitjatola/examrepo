"""
Fix MCQ option LaTeX for GATE_2009_AE_Q11 (propellant classification).

Raw N_2O_4 / LH_2 in plain text does not render; wrap formulas for KaTeX.

Usage:

  From repo root (directory that contains the ``backend/`` folder)::

    PYTHONPATH=backend python backend/patch_gate_2009_ae_q11_options_latex.py --json

  From inside ``backend/`` (note: no ``backend/`` prefix on the script path)::

    PYTHONPATH=. python patch_gate_2009_ae_q11_options_latex.py --json

  With a custom JSON export (use a real path on your machine, not ``/path/to/...``)::

    PYTHONPATH=backend python backend/patch_gate_2009_ae_q11_options_latex.py --json ~/data/my_questions.json

  Postgres (needs valid ``DATABASE_URL`` in ``backend/.env``)::

    PYTHONPATH=backend python backend/patch_gate_2009_ae_q11_options_latex.py

Database URL example:
  DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/aerogate
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

PUBLIC_ID = "GATE_2009_AE_Q11"

DEFAULT_JSON = Path(__file__).resolve().parent / "scripts/latex_bulk/out/db_all_questions.json"

# Class labels stay plain (ES), (SC), (C), (CG); chemistry uses \mathrm / \text.
OPTIONS = {
    "A": (
        r"$\mathrm{N_2O_4}\text{-UDMH}$ (ES), $\text{LOX-RP1}$ (C), $\text{LOX-}\mathrm{LH_2}$ (C), "
        r"$\mathrm{N_2}$ (C)"
    ),
    "B": (
        r"$\mathrm{N_2O_4}\text{-UDMH}$ (SC), $\text{LOX-RP1}$ (SC), $\text{LOX-}\mathrm{LH_2}$ (C), "
        r"$\mathrm{N_2}$ (C)"
    ),
    "C": (
        r"$\mathrm{N_2O_4}\text{-UDMH}$ (ES), $\text{LOX-RP1}$ (SC), $\text{LOX-}\mathrm{LH_2}$ (C), "
        r"$\mathrm{N_2}$ (CG)"
    ),
    "D": (
        r"$\mathrm{N_2O_4}\text{-UDMH}$ (ES), $\text{LOX-RP1}$ (C), $\text{LOX-}\mathrm{LH_2}$ (C), "
        r"$\mathrm{N_2}$ (CG)"
    ),
}


def patch_json_file(path: Path) -> None:
    if not path.is_file():
        hint = ""
        if "path/to" in str(path).lower() or str(path).startswith("/path/"):
            hint = (
                '\n(That path was an example placeholder. Use --json alone for the repo default '
                f"file, or pass a real path. Default is:\n  {DEFAULT_JSON}\n)"
            )
        raise SystemExit(f"JSON file not found: {path}{hint}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected a JSON array of questions in {path}")

    found = False
    for q in data:
        if isinstance(q, dict) and q.get("question_id") == PUBLIC_ID:
            q["options"] = dict(OPTIONS)
            found = True
            break

    if not found:
        raise SystemExit(f"Question not found in JSON: {PUBLIC_ID}")

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("patched options in", path)


async def patch_database() -> None:
    from app.core.database import engine

    opts_json = json.dumps(OPTIONS, ensure_ascii=False)
    async with engine.begin() as conn:
        res = await conn.execute(
            text("SELECT 1 FROM questions WHERE question_id=:q LIMIT 1"),
            {"q": PUBLIC_ID},
        )
        if res.fetchone() is None:
            raise SystemExit(f"Question not in database: {PUBLIC_ID}")

        await conn.execute(
            text(
                "UPDATE questions SET options=CAST(:opts AS jsonb), updated_at=:u "
                "WHERE question_id=:q"
            ),
            {"opts": opts_json, "u": datetime.utcnow(), "q": PUBLIC_ID},
        )

    print("patched options in database for", PUBLIC_ID)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        nargs="?",
        const="__default__",
        default=None,
        metavar="PATH",
        help=(
            "Patch a JSON question export instead of Postgres. "
            "Omit PATH to use the repo bulk file: scripts/latex_bulk/out/db_all_questions.json "
            "(under backend/). Pass a real filesystem path; do not use a literal /path/to/... example."
        ),
    )
    args = parser.parse_args()

    if args.json is not None:
        path = DEFAULT_JSON if args.json == "__default__" else Path(args.json)
        patch_json_file(path)
        return

    try:
        asyncio.run(patch_database())
    except OSError as e:
        print("Database connection failed:", e, file=sys.stderr)
        _print_db_hint()
        raise SystemExit(1) from e
    except Exception as e:
        err = str(e).lower()
        if "does not exist" in err or "authentication" in err or "password" in err or "connection refused" in err:
            print("Database patch failed:", e, file=sys.stderr)
            _print_db_hint()
            print(
                f"\nOr skip the DB and patch the bulk export:\n"
                f"  PYTHONPATH=backend python backend/patch_gate_2009_ae_q11_options_latex.py --json\n",
                file=sys.stderr,
            )
            raise SystemExit(1) from e
        raise


def _print_db_hint() -> None:
    print(
        "\nFix DATABASE_URL in backend/.env (or env) so the Postgres user exists.\n"
        "Example: postgresql+asyncpg://YOUR_USERNAME@localhost:5432/YOUR_DATABASE\n"
        "Avoid placeholder URLs with user literal \"user\" unless that role exists.\n",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

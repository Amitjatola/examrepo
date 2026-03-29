"""
Fix double-escaped LaTeX backslashes in the database.

The root cause: JSON data was stored with double-escaped backslashes (\\\\)
instead of single backslashes (\\). This breaks KaTeX rendering on the frontend.

This script converts all occurrences of \\\\ -> \\ in the tier_1_core_research
JSON column (which contains the explanation field with LaTeX).

Usage:
    cd backend
    source venv/bin/activate
    python fix_latex.py
"""

import asyncio
import json
import re
from sqlalchemy import text
from app.core.database import engine


def fix_double_backslashes(obj):
    """Recursively fix double-escaped backslashes in a JSON-compatible object."""
    if isinstance(obj, str):
        # Replace \\\\ (double-escaped) with \\ (single-escaped)
        # In Python string terms: '\\\\' (literal \\) -> '\\' (literal \)
        return obj.replace('\\\\', '\\')
    elif isinstance(obj, dict):
        return {k: fix_double_backslashes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_double_backslashes(item) for item in obj]
    return obj


async def main():
    print("=" * 60)
    print("LaTeX Double-Backslash Fix Script")
    print("=" * 60)
    
    async with engine.begin() as conn:
        # Fetch all questions that have tier_1_core_research
        result = await conn.execute(
            text("SELECT id, question_id, tier_1_core_research FROM questions WHERE tier_1_core_research IS NOT NULL")
        )
        rows = result.fetchall()
        print(f"\nFound {len(rows)} questions with tier_1_core_research data.")
        
        fixed_count = 0
        for row in rows:
            db_id, question_id, tier1_data = row
            
            if tier1_data is None:
                continue
            
            # Convert to string for comparison
            original_json_str = json.dumps(tier1_data)
            
            # Check if it contains double-backslashes
            if '\\\\' not in original_json_str:
                continue
            
            # Fix the data
            fixed_data = fix_double_backslashes(tier1_data)
            
            # Verify the fix actually changed something
            fixed_json_str = json.dumps(fixed_data)
            if original_json_str == fixed_json_str:
                continue
            
            # Update the row
            await conn.execute(
                text("UPDATE questions SET tier_1_core_research = :data WHERE id = :id"),
                {"data": json.dumps(fixed_data), "id": str(db_id)}
            )
            fixed_count += 1
            
            if fixed_count <= 5:
                print(f"  ✓ Fixed: {question_id}")
            elif fixed_count == 6:
                print(f"  ... (showing first 5, continuing in background)")
        
        print(f"\n{'=' * 60}")
        print(f"DONE: Fixed {fixed_count} questions out of {len(rows)} total.")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())

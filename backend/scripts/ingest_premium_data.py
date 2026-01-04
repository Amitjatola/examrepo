import asyncio
import json
import sys
import os
from pathlib import Path
from typing import List

# Add backend directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from sqlmodel import select
from app.core.database import get_session_context
from app.domains.questions.models import Question

async def ingest_file(session, file_path: Path):
    """Reads a single JSON file and updates the matching question in the DB."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {file_path}")
        return
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    # Handle if the file contains a list or a single object
    if isinstance(data, list):
        items = data
    else:
        items = [data]

    for item in items:
        q_id = item.get("question_id")
        if not q_id:
            continue

        # Check if question exists
        statement = select(Question).where(Question.question_id == q_id)
        result = await session.execute(statement)
        question = result.scalar_one_or_none()

        if not question:
            # Silent skip or verbose? Let's be verbose but concise
            # print(f"  [SKIP] {q_id} not in DB.")
            continue

        updated = False
        if "tier_0_classification" in item:
            question.tier_0_classification = item["tier_0_classification"]
            updated = True
        
        if "tier_1_core_research" in item:
            question.tier_1_core_research = item["tier_1_core_research"]
            updated = True
        
        if "tier_2_student_learning" in item:
            question.tier_2_student_learning = item["tier_2_student_learning"]
            updated = True
            
        if "tier_3_enhanced_learning" in item:
            question.tier_3_enhanced_learning = item["tier_3_enhanced_learning"]
            updated = True
            
        if "tier_4_metadata" in item:
            question.tier_4_metadata = item["tier_4_metadata"]
            updated = True
        elif "tier_4_metadata_and_future" in item:
             question.tier_4_metadata = item["tier_4_metadata_and_future"]
             updated = True

        if updated:
            session.add(question)
            print(f"  [OK] Updated {q_id}")

async def traverse_and_ingest(root_dir: str):
    """
    Recursively finds all .json files in root_dir and ingests them.
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory not found at {root_dir}")
        return

    print(f"Scanning {root_dir}...")
    json_files = list(root_path.rglob("*.json"))
    print(f"Found {len(json_files)} JSON files to process.")

    async with get_session_context() as session:
        for i, file_path in enumerate(json_files):
            # Print progress every 10 files
            if i % 10 == 0:
                print(f"Processing {i}/{len(json_files)}...")
            
            await ingest_file(session, file_path)
        
        print("Committing changes...")
        await session.commit()
    
    print("Ingestion complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/scripts/ingest_premium_data.py <directory_path>")
        sys.exit(1)
    
    dir_path = sys.argv[1]
    asyncio.run(traverse_and_ingest(dir_path))

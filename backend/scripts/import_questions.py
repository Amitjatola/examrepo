#!/usr/bin/env python3
"""
Bulk import script for questions from frontend/output folder.
Skips questions that already exist in the database.
"""
import os
import json
import requests
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"
OUTPUT_DIR = Path("/Users/amitjatola/.gemini/antigravity/scratch/aerogate/frontend/output")

def import_question(json_path: Path) -> dict:
    """Import a single question from a JSON file."""
    question_id = json_path.stem
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Wrap in a list for the bulk import endpoint
        response = requests.post(
            f"{API_BASE}/questions/import/bulk",
            files={"file": (json_path.name, json.dumps([data]), "application/json")}
        )
        
        if response.status_code == 200:
            return {"status": "success", "question_id": question_id}
        else:
            return {"status": "error", "question_id": question_id, "error": response.text}
    except Exception as e:
        return {"status": "error", "question_id": question_id, "error": str(e)}


def find_all_json_files(base_dir: Path) -> list:
    """Find all question JSON files in the output directory."""
    json_files = []
    for year_dir in base_dir.iterdir():
        if year_dir.is_dir() and year_dir.name.isdigit():
            # Check for direct JSON files
            for item in year_dir.iterdir():
                if item.is_file() and item.suffix == '.json':
                    json_files.append(item)
                elif item.is_dir():
                    # Check inside question subdirectory
                    for subitem in item.iterdir():
                        if subitem.is_file() and subitem.suffix == '.json':
                            json_files.append(subitem)
    return json_files


def main():
    print(f"Searching for questions in {OUTPUT_DIR}")
    
    json_files = find_all_json_files(OUTPUT_DIR)
    print(f"Found {len(json_files)} question files")
    
    results = {"success": 0, "skipped": 0, "error": 0}
    errors = []
    
    for json_file in sorted(json_files):
        result = import_question(json_file)
        results[result["status"]] += 1
        
        if result["status"] == "success":
            print(f"✓ Imported: {result['question_id']}")
        elif result["status"] == "skipped":
            print(f"→ Skipped: {result['question_id']} ({result.get('reason', '')})")
        else:
            print(f"✗ Error: {result['question_id']} - {result.get('error', '')}")
            errors.append(result)
    
    print("\n" + "="*50)
    print(f"Import Summary:")
    print(f"  Success: {results['success']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors:  {results['error']}")
    
    if errors:
        print("\nFailed imports:")
        for e in errors:
            print(f"  - {e['question_id']}: {e.get('error', '')[:100]}")


if __name__ == "__main__":
    main()

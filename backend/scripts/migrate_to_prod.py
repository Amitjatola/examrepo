#!/usr/bin/env python3
"""
Script to migrate local question data to the production API.
Uploads JSON files from frontend/output to the remote API.
"""
import os
import json
import sys
from pathlib import Path
import time

try:
    import requests
except ImportError:
    print("Error: 'requests' library is missing.")
    print("Please install it: pip install requests")
    sys.exit(1)

# PRODUCTION CONFIGURATION
# Default to AWS App Runner URL if set, or passed as argument
if len(sys.argv) > 1:
    API_BASE = sys.argv[1]
else:
    API_BASE = os.getenv("API_URL", "https://api.qbt.world/api/v1") 

DATA_DIR = Path("/Users/amitjatola/.gemini/antigravity/scratch/aerogate/frontend/output")

print(f"Targeting API: {API_BASE}")

def import_question(json_path: Path) -> dict:
    """Import a single question from a JSON file."""
    question_id = json_path.stem
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # The bulk import endpoint expects a list of questions
        files = {
            "file": (json_path.name, json.dumps([data]), "application/json")
        }
        
        response = requests.post(
            f"{API_BASE}/questions/import/bulk",
            files=files,
            timeout=120  # Longer timeout for remote server (Embeddings can be slow)
        )
        
        if response.status_code == 200:
            return {"status": "success", "question_id": question_id}
        elif response.status_code == 409: # Conflict/Duplicate
             return {"status": "skipped", "question_id": question_id, "reason": "Already exists"}
        else:
            return {"status": "error", "question_id": question_id, "error": f"{response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"status": "error", "question_id": question_id, "error": str(e)}

def find_all_json_files(base_dir: Path) -> list:
    """Find all question JSON files in the output directory."""
    json_files = []
    if not base_dir.exists():
        print(f"Error: Data directory not found: {base_dir}")
        return []
        
    for year_dir in base_dir.iterdir():
        if year_dir.is_dir() and year_dir.name.isdigit():
            for item in year_dir.iterdir():
                if item.is_file() and item.suffix == '.json':
                    json_files.append(item)
                elif item.is_dir():
                    for subitem in item.iterdir():
                        if subitem.is_file() and subitem.suffix == '.json':
                            json_files.append(subitem)
    return json_files

def main():
    print(f"🚀 Starting migration to: {API_BASE}")
    print(f"📂 Reading data from: {DATA_DIR}")
    
    # Check if API is healthy first
    try:
        health = requests.get(f"https://examrepo-production.up.railway.app/health", timeout=10)
        if health.status_code != 200:
            print("⚠️ API Health check failed. Is the backend running?")
            # Proceed anyway as health check path might vary
    except Exception as e:
        print(f"⚠️ Warning: Could not reach API root: {e}")
        print("Trying to upload directly...")

    json_files = find_all_json_files(DATA_DIR)
    total_files = len(json_files)
    print(f"Found {total_files} question files to process")
    
    if total_files == 0:
        print("No files found. Exiting.")
        return

    results = {"success": 0, "skipped": 0, "error": 0}
    errors = []
    
    start_time = time.time()
    
    for i, json_file in enumerate(sorted(json_files)):
        print(f"Processing {i+1}/{total_files}: {json_file.stem}...", end="\r")
        result = import_question(json_file)
        results[result["status"]] += 1
        
        if result["status"] == "error":
            print(f"\n✗ Error {result['question_id']}: {result.get('error')}")
            errors.append(result)
        elif result["status"] == "success":
             # Optional: print success for every file or just show progress
             pass
        
        # Tiny sleep to avoid overwhelming the server slightly
        time.sleep(0.05)
    
    duration = time.time() - start_time
    print(f"\n\n{'='*50}")
    print(f"Migration Complete in {duration:.2f}s")
    print(f"  ✅ Success: {results['success']}")
    print(f"  ⏭️ Skipped: {results['skipped']}")
    print(f"  ❌ Errors:  {results['error']}")
    
    if errors:
        print("\nUsing incorrect API URL or Server Error likely if all failed.")
        print(f"First error: {errors[0]}")

if __name__ == "__main__":
    main()

import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Connect to MongoDB Atlas
load_dotenv()
CONNECTION_STRING = os.environ.get("CONNECTION_STRING")

if not CONNECTION_STRING:
    print("Error: CONNECTION_STRING not found in .env")
    exit(1)

client = MongoClient(CONNECTION_STRING)
db = client['search_engine_db']

# 2. Read courses_data.json
file_path = "courses_data.json"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read().replace("\u00a0", " ")  # strip invisible non-breaking spaces
        courses = json.loads(raw)
except Exception as e:
    print(f"Error reading {file_path}: {e}")
    exit(1)

# 3. Standardize keys for Flask templates and quiz grading
for course in courses:
    # Ensure standard 'title' key
    if "course_title" in course and "title" not in course:
        course["title"] = course.pop("course_title")
    course.pop("title_keyword", None)

    # Standardize both answer keys for app.py
    for ch in course.get("chapters", []):
        for q in ch.get("quiz", []):
            val = q.get("correct_answer") or q.get("answer")
            q["answer"] = val
            q["correct_answer"] = val

# 4. Insert freshly cleaned courses
db.courses.delete_many({})  # Safety wipe so no duplicates exist
result = db.courses.insert_many(courses)

print(f"\nSuccessfully inserted {len(result.inserted_ids)} courses into MongoDB Atlas:")
for c in courses:
    print(f"  ✓ {c.get('title')} ({len(c.get('chapters', []))} chapters)")
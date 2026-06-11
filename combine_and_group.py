import json
import glob
import os
from collections import defaultdict


DATASET_DIR = "datasets"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_all_sections():
    all_sections = []
    seen_ids = set()

    files = sorted(glob.glob(f"{DATASET_DIR}/*.json"))

    print(f"Found {len(files)} dataset files")

    for filename in files:
        print("Reading", filename)

        with open(filename, "r", encoding="utf-8") as f:
            sections = json.load(f)

        for section in sections:
            section_id = section.get("id")

            if not section_id:
                continue

            # Avoid duplicates across multiple captures
            if section_id in seen_ids:
                continue

            seen_ids.add(section_id)
            all_sections.append(section)

    return all_sections


def group_by_course(sections):
    courses = {}

    for section in sections:
        course_code = section["courseCode"]
        section_type = section.get("type") or "Unknown"

        if course_code not in courses:
            courses[course_code] = {
                "courseCode": course_code,
                "title": section.get("title"),
                "credits": section.get("credits"),
                "components": defaultdict(list),
            }

        # Some courses may have inconsistent credits/title in weird edge cases.
        # Keep the first one for now.

        section_data = {
            "id": section["id"],
            "section": section["section"],
            "type": section_type,
            "status": section.get("status"),
            "deliveryMode": section.get("deliveryMode"),
            "meetings": section.get("meetings", []),
        }

        courses[course_code]["components"][section_type].append(section_data)

    # Convert defaultdict to normal dict for JSON output
    for course in courses.values():
        course["components"] = dict(course["components"])

    return courses


def main():
    all_sections = load_all_sections()

    print()
    print(f"Total unique sections: {len(all_sections)}")

    courses_grouped = group_by_course(all_sections)

    print(f"Total unique courses: {len(courses_grouped)}")

    # 1. Raw flat section dataset
    with open(f"{OUTPUT_DIR}/all_sections.json", "w", encoding="utf-8") as f:
        json.dump(all_sections, f, indent=2, ensure_ascii=False)

    # 2. Course-first grouped dataset
    with open(f"{OUTPUT_DIR}/courses_grouped.json", "w", encoding="utf-8") as f:
        json.dump(courses_grouped, f, indent=2, ensure_ascii=False)

    print()
    print(f"Saved {OUTPUT_DIR}/all_sections.json")
    print(f"Saved {OUTPUT_DIR}/courses_grouped.json")


if __name__ == "__main__":
    main()
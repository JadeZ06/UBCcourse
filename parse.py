import json
import re
import glob
import os


DAY_MAP = {
    "Mon": 1,
    "Tue": 2,
    "Wed": 3,
    "Thu": 4,
    "Fri": 5,
    "Sat": 6,
    "Sun": 7,
}


def convert_time_to_minutes(time_str):
    time_str = time_str.strip().lower()

    m = re.match(r"(\d+):(\d+)\s*(a\.m\.|p\.m\.)", time_str)

    if not m:
        raise ValueError(f"Invalid time: {time_str}")

    hour = int(m.group(1))
    minute = int(m.group(2))
    ampm = m.group(3)

    if ampm == "p.m." and hour != 12:
        hour += 12

    if ampm == "a.m." and hour == 12:
        hour = 0

    return hour * 60 + minute


def get_list_items(data):
    # page_0.json usually looks like:
    # data["children"][0]["listItems"]
    #
    # pagination pages may look like:
    # data["body"]["children"][0]["listItems"]

    if "body" in data:
        data = data["body"]

    return data["children"][0]["listItems"]


def get_subtitle_text(item, label):
    for sub in item.get("subtitles", []):
        if sub.get("label") == label:
            instances = sub.get("instances", [])
            if instances:
                return instances[0].get("text")
    return None


def get_credits(item):
    for sub in item.get("subtitles", []):
        value = sub.get("value", "")

        if "Credits" in value:
            return int(float(value.split()[0]))

    return None


def parse_course_title(course_text):
    # Example:
    # CPSC_V 100-101 - Computational Thinking

    left, title = course_text.split(" - ", 1)
    course_code, section = left.rsplit("-", 1)

    return course_code, section, title


def parse_meeting_detail(detail):
    # Example:
    # UBCV | West Mall Swing Space Building (SWNG) | Floor: 2 | Room: 222 | Mon Wed Fri | 2:00 p.m. - 3:00 p.m. | 2026-09-09 - 2026-12-07

    parts = [p.strip() for p in detail.split("|")]

    if len(parts) < 7:
        return None

    building_part = parts[1]
    room_part = parts[3]
    days_part = parts[4]
    time_part = parts[5]
    date_part = parts[6]

    building_match = re.search(r"\((.*?)\)", building_part)

    building = (
        building_match.group(1)
        if building_match
        else building_part
    )

    room = room_part.replace("Room:", "").strip()

    days = [
        DAY_MAP[d]
        for d in days_part.split()
        if d in DAY_MAP
    ]

    start_raw, end_raw = time_part.split(" - ")

    start_date, end_date = date_part.split(" - ")

    return {
        "days": days,
        "startMinute": convert_time_to_minutes(start_raw),
        "endMinute": convert_time_to_minutes(end_raw),
        "building": building,
        "room": room,
        "startDate": start_date,
        "endDate": end_date,
    }


def parse_item(item):
    course_text = item["title"]["instances"][0]["text"]

    course_code, section, title = parse_course_title(course_text)

    course_type = get_subtitle_text(item, "Instructional Format")
    status = get_subtitle_text(item, "Section Status")
    delivery_mode = get_subtitle_text(item, "Delivery Mode")
    credits = get_credits(item)

    meetings = []

    for field in item.get("detailResultFields", []):
        if field.get("label") != "Section Details":
            continue

        for instance in field.get("instances", []):
            detail = instance.get("text", "")
            meeting = parse_meeting_detail(detail)

            if meeting:
                meetings.append(meeting)

    return {
        "id": f"{course_code}-{section}",
        "courseCode": course_code,
        "section": section,
        "title": title,
        "type": course_type,
        "status": status,
        "deliveryMode": delivery_mode,
        "credits": credits,
        "meetings": meetings,
    }


all_courses = []
seen_ids = set()

files = sorted(
    glob.glob("responses/*.json"),
    key=lambda x: int(re.search(r"page_(\d+)", x).group(1))
)

for filename in files:
    print("Reading", filename)

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = get_list_items(data)

    for item in items:
        course = parse_item(item)

        # avoid duplicates if a page was captured twice
        if course["id"] not in seen_ids:
            all_courses.append(course)
            seen_ids.add(course["id"])


os.makedirs("output", exist_ok=True)

with open("output/courses.json", "w", encoding="utf-8") as f:
    json.dump(all_courses, f, indent=2, ensure_ascii=False)

print()
print(f"Saved {len(all_courses)} courses to output/courses.json")
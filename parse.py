import json
import re


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

    m = re.match(
        r"(\d+):(\d+)\s*(a\.m\.|p\.m\.)",
        time_str
    )

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


with open("search.json", encoding="utf-8") as f:
    data = json.load(f)

courses = []

for item in data["children"][0]["listItems"]:

    # -------------------------
    # Course title
    # -------------------------

    course_text = item["title"]["instances"][0]["text"]

    # Example:
    # CPSC_V 110-101 - Computation, Programs, and Programming

    left, title = course_text.split(" - ", 1)

    course_code, section = left.rsplit("-", 1)

    # -------------------------
    # Type
    # -------------------------

    course_type = (
        item["subtitles"][0]
        ["instances"][0]
        ["text"]
    )

    # -------------------------
    # Credits
    # -------------------------

    credits = None

    for sub in item["subtitles"]:

        if (
            sub["widget"] == "text"
            and "Credits" in sub.get("value", "")
        ):
            credits = int(
                sub["value"].split()[0]
            )

    # -------------------------
    # Meetings
    # -------------------------

    meetings = []

    for field in item["detailResultFields"]:

        if field.get("label") != "Section Details":
            continue

        for meeting in field["instances"]:

            detail = meeting["text"]

            parts = [
                p.strip()
                for p in detail.split("|")
            ]

            if len(parts) < 7:
                continue

            building_part = parts[1]
            room_part = parts[3]
            days_part = parts[4]
            time_part = parts[5]

            building_match = re.search(
                r"\((.*?)\)",
                building_part
            )

            building = (
                building_match.group(1)
                if building_match
                else building_part
            )

            room = (
                room_part
                .replace("Room:", "")
                .strip()
            )

            days = [
                DAY_MAP[d]
                for d in days_part.split()
                if d in DAY_MAP
            ]

            start_raw, end_raw = (
                time_part.split(" - ")
            )

            meetings.append({
                "days": days,
                "startMinute":
                    convert_time_to_minutes(
                        start_raw
                    ),
                "endMinute":
                    convert_time_to_minutes(
                        end_raw
                    ),
                "building": building,
                "room": room
            })

    courses.append({
        "id": f"{course_code}-{section}",
        "courseCode": course_code,
        "section": section,
        "title": title,
        "type": course_type,
        "credits": credits,
        "meetings": meetings
    })

with open(
    "courses.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        courses,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Saved {len(courses)} sections"
)
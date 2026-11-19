#!/usr/bin/env python3
"""
CourseStack push script - CPSA Module B VLANs and Wireless lesson + quiz v1
Creates a new chapter "Module B - VLANs and Wireless" and pushes the lesson into it.
Run: python coursestack_push_cpsa_b_vlans_wireless_v1.py
"""

import uuid
import requests

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
BASE_URL  = "https://app.coursestack.com"
PAGE_URL  = "https://heaps1345.github.io/mca-activites/cpsa/module-b/cpsa_b_vlans_wireless_v1.html"

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})


def text_item(md):
    return {"type": "text", "id": str(uuid.uuid4()), "markdown": md}

def embed_item(url):
    return {"type": "iframe", "id": str(uuid.uuid4()), "url": url, "aspect_width": 16, "aspect_height": 9}

def create_chapter(name):
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/chapters", json={"name": name})
    r.raise_for_status()
    data = r.json()
    ch = data.get("chapter", data.get("data", data))
    return (ch if isinstance(ch, dict) else data).get("id") or data.get("id")

def create_lesson(name, chapter_id):
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/lessons", json={"name": name, "type": "lesson", "chapter_id": chapter_id})
    r.raise_for_status()
    data = r.json()
    lesson = data.get("lesson", data)
    return (lesson if isinstance(lesson, dict) else data).get("id") or data.get("id")

def push_content(lesson_id, items):
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/lessons/{lesson_id}", json={"content": {"type": "lesson", "id": str(uuid.uuid4()), "items": items}})
    r.raise_for_status()


def main():
    print("Creating chapter...")
    chapter_id = create_chapter("Module B - VLANs and Wireless")
    print(f"  Chapter ID: {chapter_id}")

    print("Creating lesson...")
    lesson_id = create_lesson("VLANs and Wireless - Lesson and Quiz", chapter_id)
    print(f"  Lesson ID: {lesson_id}")

    print("Pushing content...")
    push_content(lesson_id, [
        text_item(
            r"A combined lesson and knowledge check covering VLAN hopping attacks "
            r"(double-tagging and switch spoofing) and wireless encryption weaknesses "
            r"(WEP, WPA2-PSK, WPS). Includes a 15-question quiz with progress saving."
        ),
        embed_item(PAGE_URL),
    ])

    print(f"\nDone.")
    print(f"  Course:  {BASE_URL}/courses/{COURSE_ID}")
    print(f"  Chapter: {chapter_id}")
    print(f"  Lesson:  {lesson_id}")


if __name__ == "__main__":
    main()

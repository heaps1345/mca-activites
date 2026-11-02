#!/usr/bin/env python3
"""
CourseStack push script - Module A Instructor Slides lesson
Adds a single lesson to the Module A chapter containing the 27-slide HTML deck.

Run locally on Windows (container proxy blocks app.coursestack.com):
    python3 coursestack_push_module_a_slides_v1.py

Requirements:
    pip install requests
"""

import uuid
import time
import requests

API_KEY    = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
COURSE_ID  = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
BASE_URL   = "https://app.coursestack.com"
CHAPTER_ID = "4990d041-f15b-42e8-9e7d-11975f19264b"   # Module A: Soft Skills

SLIDES_URL = (
    "https://heaps1345.github.io/mca-activites/cpsa/module-a/"
    "syntex_instructor_slides_v1.html"
)

LESSON_NAME = "Module A: Instructor Slides (A1-A5)"

INTRO = (
    "27-slide instructor presentation covering all five Module A topics: "
    "A1 Penetration Testing Lifecycle, A2 UK Legal Framework, A3 Scoping and Engagement Types, "
    "A4 Risk Management and CVSS v3.1, and A5 Professional Reporting. "
    "Each topic follows the format: content -> real-world analogy -> demo callout -> lab callout. "
    "Use arrow keys or swipe to navigate. Press F for fullscreen."
)

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})


def text_item(markdown_text):
    return {"type": "text", "id": str(uuid.uuid4()), "markdown": markdown_text}


def embed_item(url):
    return {
        "type": "iframe",
        "id": str(uuid.uuid4()),
        "url": url,
        "aspect_width": 16,
        "aspect_height": 9,
    }


def create_lesson(name, chapter_id):
    payload = {"name": name, "type": "lesson", "chapter_id": chapter_id}
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/lessons", json=payload)
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    data = r.json()
    return data.get("lesson", data).get("id") or data.get("id")


def push_lesson_content(lesson_id, items):
    content = {
        "content": {
            "type": "lesson",
            "id": str(uuid.uuid4()),
            "items": items,
        }
    }
    r = session.post(
        f"{BASE_URL}/api/content/{COURSE_ID}/lessons/{lesson_id}",
        json=content,
    )
    if not r.ok:
        print(f"  CONTENT ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()


def main():
    print(f"Pushing '{LESSON_NAME}' to chapter {CHAPTER_ID}...\n")

    items = [
        text_item(INTRO),
        embed_item(SLIDES_URL),
        text_item(f"[Open slides in new tab]({SLIDES_URL})"),
    ]

    print(f"  Creating lesson...")
    lesson_id = create_lesson(LESSON_NAME, CHAPTER_ID)
    time.sleep(0.5)
    print(f"    Created -> {lesson_id}")

    print(f"  Pushing content...")
    push_lesson_content(lesson_id, items)
    time.sleep(0.5)
    print(f"    Content pushed OK")

    print(f"\nDone. Lesson ID: {lesson_id}")


if __name__ == "__main__":
    main()

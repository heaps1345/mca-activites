#!/usr/bin/env python3
"""
CourseStack push script - CPSA Module B TCP Packets lesson + quiz v1
Creates a new chapter "Module B - TCP Packets" and pushes the lesson into it.
Run: python coursestack_push_cpsa_b_tcp_v1.py
"""

import uuid
import time
import requests

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
BASE_URL  = "https://app.coursestack.com"
PAGE_URL  = "https://heaps1345.github.io/mca-activites/cpsa/module-b/cpsa_b_tcp_packets_v1.html"

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
    chapter_id = create_chapter("Module B - TCP Packets")
    print(f"  Chapter ID: {chapter_id}")
    time.sleep(0.5)

    print("Creating lesson...")
    lesson_id = create_lesson("TCP Packets - Lesson and Quiz", chapter_id)
    time.sleep(0.5)

    intro = (
        r"A combined lesson and knowledge check covering TCP header structure, "
        r"the six TCP flags (SYN, ACK, FIN, RST, PSH, URG) and their pentest context, "
        r"the three-way handshake mechanics, nmap scan types and the flags they use, "
        r"TCP sequence numbers, ISN predictability, and session hijacking.\n\n"
        r"15 questions covering flags, handshake steps, scan types, and sequence numbers. "
        r"Progress is saved automatically."
    )
    push_content(lesson_id, [
        text_item(intro),
        embed_item(PAGE_URL),
        text_item(f"[Open in new tab]({PAGE_URL})"),
    ])

    print(f"  Lesson ID: {lesson_id}")
    print(f"\nDone. Lesson live at: {PAGE_URL}")
    print(f"Course: https://app.coursestack.com/courses/{COURSE_ID}")


if __name__ == "__main__":
    main()

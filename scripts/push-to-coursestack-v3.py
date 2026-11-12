#!/usr/bin/env python3
"""
push-to-coursestack-v2.py
Pushes Module B foundational labs (B1-A, B2-A, B3-A) to the CPSA course.

These are the NEW zero-experience Kali CLI / networking labs that sit BEFORE
the existing B4+ labs in the course.

Usage (Windows):
  python push-to-coursestack-v2.py

If you do not know the Module B chapter ID, run with --list-chapters to
print all chapter names and IDs for the CPSA course, then set CHAPTER_ID below.

  python push-to-coursestack-v2.py --list-chapters
"""

import sys
import uuid
import time
import requests

API_KEY    = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
COURSE_ID  = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
BASE_URL   = "https://app.coursestack.com"
GITHUB_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-b"

# ------------------------------------------------------------------
# SET THIS to the Module B chapter ID before running.
# Run with --list-chapters if you don't know it.
# If left empty the script will create a NEW "Module B - Foundational Labs" chapter.
# ------------------------------------------------------------------
CHAPTER_ID = ""

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

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
    lesson = data.get("lesson", data)
    if isinstance(lesson, dict):
        return lesson.get("id") or data.get("id")
    return data.get("id")


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


def make_lesson(name, chapter_id, items):
    print(f"  Creating: {name}")
    lesson_id = create_lesson(name, chapter_id)
    time.sleep(0.5)
    push_lesson_content(lesson_id, items)
    time.sleep(0.5)
    print(f"    OK -> {lesson_id}")


def create_chapter(name, description=""):
    payload = {"name": name, "description": description}
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/chapters", json=payload)
    if not r.ok:
        print(f"  CHAPTER ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    data = r.json()
    chapter = data.get("chapter", data.get("data", data))
    if isinstance(chapter, dict):
        chapter_id = chapter.get("id") or data.get("id")
    else:
        chapter_id = data.get("id")
    print(f"  New chapter created: {chapter_id}")
    return chapter_id


def list_chapters():
    r = session.get(f"{BASE_URL}/api/content/{COURSE_ID}")
    if not r.ok:
        print(f"ERROR {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    data = r.json()
    # chapters may be nested under 'content', 'chapters', or top-level list
    items = data.get("content", data.get("chapters", data if isinstance(data, list) else []))
    if isinstance(items, dict):
        items = items.get("chapters", [])
    print(f"\nChapters in CPSA course ({COURSE_ID}):\n")
    for ch in items:
        print(f"  {ch.get('id')}  |  {ch.get('name', ch.get('title', '???'))}")
    print()


# ------------------------------------------------------------------
# Labs to push
# ------------------------------------------------------------------

LABS = [
    {
        "title": "Lab B1-A: Kali CLI Networking Orientation",
        "slug": "lab-b1a-cli-networking-v1.html",
        "intro": (
            "Think of this lab as checking your own driving licence and reading the road signs before "
            "you set off on a journey. Before you can probe a target network you need to know exactly "
            "where YOUR machine sits - its IP address, its gateway, its DNS server. A pen tester who "
            "does not know their own network configuration is like a safecracker who forgot to bring "
            "their stethoscope.\n\n"
            "In this lab you will use `ip a`, `ip r`, `ping`, `traceroute`, `nslookup`, `dig` and `ss` "
            "to map your own Kali machine's network setup from the command line. Every one of these "
            "commands comes up on the CPSA exam - and every one of them is something you will reach "
            "for on every real engagement."
        ),
    },
    {
        "title": "Lab B2-A: Passive Network Reconnaissance",
        "slug": "lab-b2a-network-recon-v1.html",
        "intro": (
            "Imagine sitting in a coffee shop and working out who is in the room just by listening - "
            "without asking anyone a single question. That is passive reconnaissance. You are gathering "
            "intelligence from traffic that is already flowing around you, leaving no footprint on the "
            "target whatsoever.\n\n"
            "In this lab you will use `arp`, `ip neigh`, `/etc/hosts` and Wireshark to pull MAC "
            "addresses, identify live hosts and read OS fingerprinting clues out of ICMP TTL values - "
            "all without sending a single active probe. The CPSA exam loves TTL-based OS fingerprinting: "
            "Linux returns 64, Windows returns 128, Cisco returns 255. By the end of this lab you will "
            "be able to spot an OS from a packet capture alone."
        ),
    },
    {
        "title": "Lab B3-A: Protocol-Level Service Enumeration",
        "slug": "lab-b3a-service-enumeration-v1.html",
        "intro": (
            "Nmap tells you a port is open. This lab teaches you what to actually DO with it. "
            "Think of Nmap as a burglar alarm detector - it tells you which doors exist. This lab "
            "teaches you to pick the locks. Each protocol has its own native query language and its "
            "own class of misconfiguration, and CPSA expects you to know them all.\n\n"
            "You will work through four protocols used in almost every real-world internal assessment: "
            "DNS (including a zone transfer attempt that dumps the entire internal namespace in one "
            "command), SMB null sessions, LDAP anonymous binds and SNMP default community strings. "
            "The target IP is assigned by your instructor - fill it in at the top of the lab before "
            "you start."
        ),
    },
]


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    if "--list-chapters" in sys.argv:
        list_chapters()
        return

    chapter_id = CHAPTER_ID.strip()

    if not chapter_id:
        print("CHAPTER_ID not set - creating a new chapter...")
        chapter_id = create_chapter(
            "Module B - Foundational Labs",
            "Zero-experience Kali CLI and networking labs for CREST CPSA Module B"
        )
        time.sleep(1)
        print(f"\n*** SAVE THIS CHAPTER ID for future scripts: {chapter_id} ***\n")
    else:
        print(f"Using existing chapter: {chapter_id}")

    print(f"\nPushing {len(LABS)} labs to chapter {chapter_id}...\n")

    for lab in LABS:
        lab_url = f"{GITHUB_BASE}/{lab['slug']}"
        items = [
            text_item(lab["intro"]),
            embed_item(lab_url),
            text_item(f"[Open lab in new tab]({lab_url})"),
        ]
        make_lesson(lab["title"], chapter_id, items)

    print(f"\nDone. {len(LABS)} lessons created.")
    print(f"Course: https://app.coursestack.com/courses/{COURSE_ID}")


if __name__ == "__main__":
    main()

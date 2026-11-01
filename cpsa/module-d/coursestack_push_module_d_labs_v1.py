"""
coursestack_push_module_d_labs_v1.py
--------------------------------------
Pushes Module D lab lessons to CourseStack.
Each lab lesson contains an iframe embed pointing to the GitHub Pages URL.

Course: b9d920c3-4a8e-4227-af24-3c5f32fc7350
Chapter: Module 04 - Networking Equipment  (finds existing, does not recreate)

Run on Windows:
  Invoke-WebRequest -Uri "https://raw.githubusercontent.com/heaps1345/mca-activites/main/cpsa/module-d/coursestack_push_module_d_labs_v1.py" -OutFile "coursestack_push_module_d_labs_v1.py"
  python coursestack_push_module_d_labs_v1.py

Lab lessons created:
  D-LAB-01  Lab D1-A: SNMP Enumeration
  D-LAB-02  Lab D2-A: Wireshark Packet Capture
  D-LAB-03  Lab D3-A: ARP Spoofing - Layer 2 MITM
"""

import requests
import json
import uuid
import time

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------
API_KEY   = "YOUR_API_KEY_HERE"   # replace with actual key
BASE_URL  = "https://app.coursestack.com"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
GITHUB_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-d"

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})

# -----------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------

def get_chapters():
    r = session.get(f"{BASE_URL}/api/content/{COURSE_ID}/chapters")
    r.raise_for_status()
    return r.json()

def create_lesson(chapter_id, title):
    payload = {"title": title, "chapter_id": chapter_id}
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/lessons", json=payload)
    r.raise_for_status()
    return r.json()

def push_lesson_content(lesson_id, items):
    content = {
        "content": {
            "type": "lesson",
            "id": str(uuid.uuid4()),
            "items": items
        }
    }
    r = session.post(
        f"{BASE_URL}/api/content/{COURSE_ID}/lessons/{lesson_id}",
        json=content
    )
    r.raise_for_status()
    return r.json()

def text_item(markdown_text):
    return {"type": "text", "id": str(uuid.uuid4()), "content": markdown_text}

def embed_item(url, title=""):
    return {
        "type": "embed",
        "id": str(uuid.uuid4()),
        "url": url,
        "title": title
    }

def make_lesson(chapter_id, title, items):
    print(f"  Creating lesson: {title}")
    lesson = create_lesson(chapter_id, title)
    lesson_id = lesson.get("id") or lesson.get("lesson", {}).get("id")
    time.sleep(0.5)
    push_lesson_content(lesson_id, items)
    time.sleep(0.5)
    print(f"    Done -> {lesson_id}")
    return lesson_id

# -----------------------------------------------------------------------
# CHAPTER - find existing Module D chapter (created by theory script)
# -----------------------------------------------------------------------

def find_chapter():
    chapters = get_chapters()
    target_title = "Module 04 - Networking Equipment"
    chapter_list = chapters if isinstance(chapters, list) else chapters.get("chapters", [])
    for ch in chapter_list:
        if target_title.lower() in ch.get("title", "").lower():
            print(f"Found chapter: {ch['title']} ({ch['id']})")
            return ch["id"]
    raise RuntimeError(
        f"Chapter '{target_title}' not found. "
        "Run coursestack_push_module_d_theory_v1.py first to create it."
    )

# -----------------------------------------------------------------------
# LAB LESSONS
# -----------------------------------------------------------------------

LABS = [
    (
        "D-LAB-01  Lab D1-A: SNMP Enumeration",
        f"{GITHUB_BASE}/lab-d1a-snmp-enumeration-v1.html",
        "Lab D1-A: SNMP Enumeration",
        """\
## Lab D1-A - SNMP Enumeration

**Target:** SYNTEX-LNX01  |  **Duration:** 25-30 minutes  |  **Difficulty:** Intermediate

This lab covers active enumeration of SNMP services using nmap, snmpwalk, snmpget, \
and onesixtyone. You will extract system information, running processes, and attempt \
community string brute-forcing against the SYNTEX-LNX01 Ubuntu target.

**Tools used:** nmap, snmpwalk, snmpget, onesixtyone

**Syllabus area:** D1 - Management Protocols

The interactive lab guide is embedded below. Complete all steps and answer the \
confirmation questions before marking this lesson complete.
"""
    ),
    (
        "D-LAB-02  Lab D2-A: Wireshark Packet Capture",
        f"{GITHUB_BASE}/lab-d2a-wireshark-packet-capture-v1.html",
        "Lab D2-A: Wireshark Packet Capture",
        """\
## Lab D2-A - Wireshark Packet Capture

**Targets:** SYNTEX-LNX01 (HTTP), SYNTEX-WIN01 (FTP)  |  **Duration:** 35-40 minutes  |  **Difficulty:** Intermediate

This lab covers live packet capture and offline analysis using Wireshark and tcpdump. \
You will capture HTTP login traffic, apply display filters, use Follow TCP Stream, \
capture FTP credentials with tcpdump, and analyse protocol distribution using \
Statistics > Protocol Hierarchy.

**Tools used:** Wireshark, tcpdump, curl

**Syllabus area:** D2 - Packet Capture Analysis

The interactive lab guide is embedded below. Complete all steps and answer the \
confirmation questions before marking this lesson complete.
"""
    ),
    (
        "D-LAB-03  Lab D3-A: ARP Spoofing - Layer 2 MITM",
        f"{GITHUB_BASE}/lab-d3a-arp-spoofing-mitm-v1.html",
        "Lab D3-A: ARP Spoofing - Layer 2 MITM",
        """\
## Lab D3-A - ARP Spoofing - Layer 2 MITM

**Target:** SYNTEX-WIN01 + Lab Gateway  |  **Duration:** 40 minutes  |  **Difficulty:** Advanced

This lab demonstrates a full Layer 2 Man-in-the-Middle attack using arpspoof from the \
dsniff suite. You will enable IP forwarding, poison both the victim and gateway ARP \
caches simultaneously, verify the MITM position with Wireshark, and cleanly restore \
the network on completion.

**Tools used:** arpspoof (dsniff), Wireshark, ip, arp

**Syllabus area:** D3 - ARP Spoofing

**Important:** Always enable IP forwarding before running arpspoof. Always clean up \
when done. Only run this lab in your isolated SYNTEX environment.

The interactive lab guide is embedded below. Complete all steps and answer the \
confirmation questions before marking this lesson complete.
"""
    ),
]

# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------

def main():
    print("CourseStack - Module D Labs Push")
    print("=" * 40)

    chapter_id = find_chapter()

    for lesson_title, lab_url, embed_title, intro_markdown in LABS:
        items = [
            text_item(intro_markdown),
            embed_item(lab_url, embed_title),
        ]
        make_lesson(chapter_id, lesson_title, items)

    print()
    print("All Module D lab lessons pushed successfully.")
    print()
    print("Lab URLs live at:")
    print(f"  {GITHUB_BASE}/lab-d1a-snmp-enumeration-v1.html")
    print(f"  {GITHUB_BASE}/lab-d2a-wireshark-packet-capture-v1.html")
    print(f"  {GITHUB_BASE}/lab-d3a-arp-spoofing-mitm-v1.html")


if __name__ == "__main__":
    main()

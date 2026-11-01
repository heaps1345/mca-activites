"""
coursestack_push_module_d_labs_v2.py
--------------------------------------
Pushes Module D lab lessons to CourseStack.
v2 - fixes API field names (name/type instead of title, type required)
     hardcodes chapter ID

Course: b9d920c3-4a8e-4227-af24-3c5f32fc7350
Chapter ID: 7d68c2cc-003d-4cde-90f6-b780ac86660e  (Module 04 - Networking Equipment)

Run on Windows:
  del coursestack_push_module_d_labs_v2.py
  curl.exe -L "https://raw.githubusercontent.com/heaps1345/mca-activites/main/cpsa/module-d/coursestack_push_module_d_labs_v2.py" -o coursestack_push_module_d_labs_v2.py
  python coursestack_push_module_d_labs_v2.py

Lab lessons created:
  D-LAB-01  Lab D1-A: SNMP Enumeration
  D-LAB-02  Lab D2-A: Wireshark Packet Capture
  D-LAB-03  Lab D3-A: ARP Spoofing - Layer 2 MITM
"""

import requests
import uuid
import time

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------
API_KEY    = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE_URL   = "https://app.coursestack.com"
COURSE_ID  = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
CHAPTER_ID = "7d68c2cc-003d-4cde-90f6-b780ac86660e"
GITHUB_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-d"

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})

# -----------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------

def create_lesson(name):
    payload = {"name": name, "type": "lesson", "chapter_id": CHAPTER_ID}
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
            "items": items
        }
    }
    r = session.post(
        f"{BASE_URL}/api/content/{COURSE_ID}/lessons/{lesson_id}",
        json=content
    )
    if not r.ok:
        print(f"  CONTENT ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()

def text_item(markdown_text):
    return {"type": "text", "id": str(uuid.uuid4()), "markdown": markdown_text}

def embed_item(url, title=""):
    return {
        "type": "iframe",
        "id": str(uuid.uuid4()),
        "url": url,
        "title": title
    }

def make_lesson(name, items):
    print(f"  Creating: {name}")
    lesson_id = create_lesson(name)
    time.sleep(0.5)
    push_lesson_content(lesson_id, items)
    time.sleep(0.5)
    print(f"    OK -> {lesson_id}")

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
    print("=" * 60)
    print("CourseStack Module D Labs Push - v2")
    print(f"Course:  {COURSE_ID}")
    print(f"Chapter: {CHAPTER_ID}")
    print("=" * 60)
    print()

    for lesson_name, lab_url, embed_title, intro_markdown in LABS:
        items = [
            text_item(intro_markdown),
            embed_item(lab_url, embed_title),
        ]
        make_lesson(lesson_name, items)

    print()
    print("=" * 60)
    print("All Module D lab lessons pushed successfully.")
    print()
    print("Lab URLs:")
    print(f"  {GITHUB_BASE}/lab-d1a-snmp-enumeration-v1.html")
    print(f"  {GITHUB_BASE}/lab-d2a-wireshark-packet-capture-v1.html")
    print(f"  {GITHUB_BASE}/lab-d3a-arp-spoofing-mitm-v1.html")
    print("=" * 60)


if __name__ == "__main__":
    main()

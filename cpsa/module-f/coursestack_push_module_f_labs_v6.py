#!/usr/bin/env python3
"""
CourseStack push script - Module F labs (all 8)
Run AFTER coursestack_push_module_f_theory_v1.py
Chapter ID is already set below.
"""

import uuid
import time
import requests

API_KEY = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
BASE_URL = "https://app.coursestack.com"
GITHUB_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-f"
CHAPTER_ID = "643abf9f-81d1-480c-a4b9-cfebe9198935"

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


def make_lesson(name, chapter_id, items):
    print(f"  Creating: {name}")
    lesson_id = create_lesson(name, chapter_id)
    time.sleep(0.5)
    push_lesson_content(lesson_id, items)
    time.sleep(0.5)
    print(f"    OK -> {lesson_id}")


LABS = [
    {
        "title": "Lab F1-A: User Enumeration",
        "slug": "lab-f1a-user-enumeration-v1.html",
        "intro": (
            "In this lab you will enumerate user accounts and information from SYNTEX-LNX01 "
            "using finger, SMTP VRFY, and system file inspection."
        ),
    },
    {
        "title": "Lab F3-A: FTP & NFS Assessment",
        "slug": "lab-f3a-ftp-nfs-assessment-v1.html",
        "intro": (
            "Assess the FTP and NFS services on SYNTEX-LNX01. You will identify anonymous FTP access, "
            "misconfigured NFS exports, and retrieve sensitive files from both services."
        ),
    },
    {
        "title": "Lab F5-A: SSH Post-Exploitation",
        "slug": "lab-f5a-ssh-post-exploitation-v1.html",
        "intro": (
            "Following SSH access to SYNTEX-LNX01, perform post-exploitation enumeration including "
            "local users, sudo rights, network configuration, and installed services."
        ),
    },
    {
        "title": "Lab F4-A: SNMP Enumeration",
        "slug": "lab-f4a-snmp-enumeration-v1.html",
        "intro": (
            "Enumerate SNMP on SYNTEX-LNX01 using community string brute-forcing and MIB walking. "
            "You will extract process lists, network interfaces, and system information via UDP 161."
        ),
    },
    {
        "title": "Lab F5-B: SMB Assessment",
        "slug": "lab-f5a-smb-assessment-v1.html",
        "intro": (
            "Assess the Samba service on SYNTEX-LNX01. You will detect SMBv1, enumerate shares with "
            "enum4linux, access the finance share as guest, and retrieve credentials from a budget file."
        ),
    },
    {
        "title": "Lab F6-A: Web Service Assessment",
        "slug": "lab-f6a-web-assessment-v1.html",
        "intro": (
            "Assess the Apache web service on SYNTEX-LNX01. You will identify version disclosure, "
            "directory listing, exposed configuration files, phpinfo(), and missing security headers."
        ),
    },
    {
        "title": "Lab F7-A: TLS/SSL Assessment",
        "slug": "lab-f7a-tls-assessment-v1.html",
        "intro": (
            "Assess the TLS/SSL configuration on SYNTEX-LNX01 port 443 using sslscan, testssl.sh, "
            "and OpenSSL. You will identify legacy protocol versions, weak ciphers, and certificate issues."
        ),
    },
    {
        "title": "Lab F8-A: Linux Privilege Escalation",
        "slug": "lab-f8a-privilege-escalation-v1.html",
        "intro": (
            "Identify and understand three privilege escalation paths on SYNTEX-LNX01: a world-writable "
            "root cron script, a vulnerable SUID binary, and Docker group membership."
        ),
    },
]


def main():
    print(f"Pushing {len(LABS)} Module F lab lessons to chapter {CHAPTER_ID}...\n")
    for lab in LABS:
        lab_url = f"{GITHUB_BASE}/{lab['slug']}"
        items = [
            text_item(lab["intro"]),
            embed_item(lab_url),
            text_item(f"[Open lab in new tab]({lab_url})"),
        ]
        make_lesson(lab["title"], CHAPTER_ID, items)
    print(f"\nDone. {len(LABS)} lessons created.")


if __name__ == "__main__":
    main()

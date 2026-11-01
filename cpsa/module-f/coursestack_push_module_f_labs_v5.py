"""
coursestack_push_module_f_labs_v5.py
--------------------------------------
Pushes Module F lab lessons to CourseStack.

Module F: Linux / Unix Security Assessment
Three labs: F1-A User Enumeration, F3-A FTP/NFS Assessment, F5-A SSH/Post-Exploitation

Course: b9d920c3-4a8e-4227-af24-3c5f32fc7350

NOTE: This script requires the Module F chapter to already exist.
      Run coursestack_push_module_f_theory_v1.py first, then paste the
      printed Chapter ID into CHAPTER_ID below.

Run on Windows:
  python coursestack_push_module_f_labs_v5.py

Lab lessons created:
  F-LAB-01  Lab F1-A: User Enumeration
  F-LAB-02  Lab F3-A: FTP and NFS Assessment
  F-LAB-03  Lab F5-A: SSH Assessment and Post-Exploitation
"""

import requests
import uuid
import time

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------
API_KEY     = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE_URL    = "https://app.coursestack.com"
COURSE_ID   = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"

# Paste the Chapter ID printed by coursestack_push_module_f_theory_v1.py here:
CHAPTER_ID  = "PASTE_MODULE_F_CHAPTER_ID_HERE"

GITHUB_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-f"

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

def embed_item(url):
    return {
        "type": "iframe",
        "id": str(uuid.uuid4()),
        "url": url,
        "aspect_width": 16,
        "aspect_height": 9,
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
        "F-LAB-01  Lab F1-A: User Enumeration",
        f"{GITHUB_BASE}/lab-f1a-user-enumeration-v1.html",
        """\
## Lab F1-A - User Enumeration

**Target:** SYNTEX-LNX01  |  **Duration:** 25-30 minutes  |  **Difficulty:** Intermediate

This lab covers active user enumeration against a Linux target using rusers, rwho, finger
daemon (port 79), and SMTP VRFY/RCPT TO. You will compile a confirmed username list from
multiple sources and practice banner grabbing FTP, SMTP, and SSH pre-authentication.

**Tools used:** rusers, finger, smtp-user-enum, nmap, nc, telnet

**Syllabus area:** F1 - User Enumeration

The interactive lab guide is embedded below. Complete all steps and answer the
confirmation questions before marking this lesson complete.
""",
    ),
    (
        "F-LAB-02  Lab F3-A: FTP and NFS Assessment",
        f"{GITHUB_BASE}/lab-f3a-ftp-nfs-assessment-v1.html",
        """\
## Lab F3-A - FTP and NFS Assessment

**Target:** SYNTEX-LNX01  |  **Duration:** 35-40 minutes  |  **Difficulty:** Intermediate

This lab covers anonymous FTP access testing, write permission assessment, web root
overlap analysis, and full NFS export enumeration including UID/GID spoofing and
no_root_squash exploitation. Reversion of all test artefacts is required.

**Tools used:** nmap, ftp, nc, showmount, rpcinfo, mount

**Syllabus areas:** F3 FTP, F5 NFS

**Important:** All test artefacts (write-test.txt, SUID binaries, test users) must be
removed and confirmed before marking this lab complete.

The interactive lab guide is embedded below. Complete all steps and answer the
confirmation questions before marking this lesson complete.
""",
    ),
    (
        "F-LAB-03  Lab F5-A: SSH Assessment and Post-Exploitation",
        f"{GITHUB_BASE}/lab-f5a-ssh-post-exploitation-v1.html",
        """\
## Lab F5-A - SSH Assessment and Post-Exploitation

**Target:** SYNTEX-LNX01  |  **Duration:** 40-45 minutes  |  **Difficulty:** Advanced

This lab covers SSH banner analysis and protocol version identification, authentication
method enumeration, password hash extraction and offline cracking workflow, patch-level
assessment against kernel CVEs, and full reversion documentation to CPSA reporting
standard.

**Tools used:** nmap, nc, john, hashcat, apt/dpkg, searchsploit

**Syllabus areas:** F5-F9 Network Services, F6 Post-Exploitation and Reporting

**Important:** Hash cracking must be performed on your analysis host only. Never run
John or Hashcat on the target system.

The interactive lab guide is embedded below. Complete all steps and answer the
confirmation questions before marking this lesson complete.
""",
    ),
]

# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------

def main():
    if CHAPTER_ID == "PASTE_MODULE_F_CHAPTER_ID_HERE":
        print("=" * 60)
        print("ERROR: CHAPTER_ID not set.")
        print()
        print("  1. Run coursestack_push_module_f_theory_v1.py first")
        print("  2. Copy the Chapter ID it prints at the end")
        print("  3. Paste it into CHAPTER_ID at the top of this file")
        print("  4. Run this script again")
        print("=" * 60)
        return

    print("=" * 60)
    print("CourseStack Module F Labs Push - v5")
    print(f"Course:  {COURSE_ID}")
    print(f"Chapter: {CHAPTER_ID}")
    print("=" * 60)
    print()

    for lesson_name, lab_url, intro_markdown in LABS:
        items = [
            text_item(intro_markdown),
            embed_item(lab_url),
        ]
        make_lesson(lesson_name, items)

    print()
    print("=" * 60)
    print("All Module F lab lessons pushed successfully.")
    print()
    print("Lab URLs (GitHub Pages):")
    for _, url, _ in LABS:
        print(f"  {url}")
    print("=" * 60)


if __name__ == "__main__":
    main()

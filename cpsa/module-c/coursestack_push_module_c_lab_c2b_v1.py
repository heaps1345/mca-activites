"""
CourseStack - Add Lab C2-B (DNS Zone Transfer) to Module C  v1
Finds the existing Module C Labs chapter (or creates it) and
adds a single lesson embedding the lab HTML via GitHub Pages.

Run from Kali or any machine with internet access:
  pip install requests
  python3 coursestack_push_module_c_lab_c2b_v1.py
"""

import requests
import uuid
import time
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"

# GitHub Pages URL for the new lab
LAB_URL  = "https://heaps1345.github.io/mca-activites/cpsa/module-c/lab-c2b-dns-zone-transfer-v1.html"
LAB_NAME = "Lab C2-B - DNS Zone Transfer (Live AXFR)"

# If you already know the Module C chapter ID, paste it here to skip creation.
# Leave as None to auto-detect or create.
MODULE_C_CHAPTER_ID = None

HEADERS = {"Content-Type": "application/json"}


def uid():
    return str(uuid.uuid4()).replace("-", "")


def api_get(path):
    url = f"{BASE}{path}"
    r = requests.get(url, auth=auth, headers=HEADERS, timeout=20)
    try:
        data = r.json()
    except Exception:
        data = {}
    return r.status_code, data


def api_post(path, payload):
    url = f"{BASE}{path}"
    r = requests.post(url, auth=auth, headers=HEADERS, json=payload, timeout=20)
    try:
        data = r.json()
    except Exception:
        data = {}
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
    return r.status_code, data


def find_or_create_chapter():
    """Look for an existing Module C Labs chapter, else create it."""
    print("[*] Fetching existing chapters...")
    status, data = api_get(f"/api/content/{COURSE_ID}/chapters")
    chapters = []
    if isinstance(data, list):
        chapters = data
    elif isinstance(data, dict):
        chapters = data.get("chapters") or data.get("data") or []

    for ch in chapters:
        name = (ch.get("name") or "").lower()
        if "module c" in name and ("lab" in name or "labs" in name):
            cid = ch.get("id")
            print(f"  Found existing chapter: '{ch.get('name')}' (id={cid})")
            return cid

    # Not found - create it
    print("  No Module C Labs chapter found - creating...")
    status, data = api_post(
        f"/api/content/{COURSE_ID}/chapters",
        {
            "name": "Module C - Hands-On Labs",
            "description": "Practical lab exercises covering CREST CPSA Module C: Background Information Gathering and Open Source Intelligence"
        }
    )
    chapter_obj = data.get("chapter") or data.get("data") or data
    if isinstance(chapter_obj, dict):
        cid = chapter_obj.get("id")
    else:
        cid = None
    print(f"  Created chapter (id={cid})")
    return cid


def create_lesson(chapter_id, name):
    print(f"  [lesson] {name}")
    payload = {"name": name, "chapter_id": chapter_id, "type": "lesson"}
    status, data = api_post(f"/api/content/{COURSE_ID}/lessons", payload)
    lesson_obj = data.get("lesson") or data.get("data") or data
    if isinstance(lesson_obj, dict):
        lesson_id = lesson_obj.get("id")
    else:
        lesson_id = None
    print(f"    status={status}  lesson_id={lesson_id}")
    return lesson_id


def set_lesson_content(lesson_id, iframe_url):
    content_block = {
        "id": uid(),
        "type": "embed",
        "data": {
            "url": iframe_url,
            "height": 900
        }
    }
    payload = {"content": [content_block]}
    status, data = api_post(
        f"/api/content/{COURSE_ID}/lessons/{lesson_id}",
        payload
    )
    print(f"    content status={status}")
    return status


def main():
    print("=== CourseStack: Add Module C Lab C2-B ===")

    chapter_id = MODULE_C_CHAPTER_ID or find_or_create_chapter()
    if not chapter_id:
        print("FATAL: could not find or create Module C chapter. Aborting.")
        return

    time.sleep(1)
    lesson_id = create_lesson(chapter_id, LAB_NAME)
    if lesson_id:
        time.sleep(0.5)
        set_lesson_content(lesson_id, LAB_URL)

    print("\n=== Done ===")
    print(f"Course: https://app.coursestack.com/courses/{COURSE_ID}")
    print(f"Lab URL: {LAB_URL}")


if __name__ == "__main__":
    main()

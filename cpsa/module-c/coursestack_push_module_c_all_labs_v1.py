"""
CourseStack - Push ALL Module C Labs to CPSA course  v1
Finds or creates the Module C Hands-On Labs chapter and adds
all 7 lab lessons, each embedding the GitHub Pages lab HTML.

Run on Windows/Kali with internet access:
  pip install requests
  python coursestack_push_module_c_all_labs_v1.py

Labs pushed:
  Lab C1-A  WHOIS and RIRs
  Lab C2-A  DNS Enumeration
  Lab C2-B  DNS Zone Transfer (Live AXFR)
  Lab C3-A  Web Recon
  Lab C4-A  Google Hacking
  Lab C5-A  Email Headers
  Lab C6-A  OSINT Sources
"""

import requests
import uuid
import time
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"

GITHUB_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-c"

LABS = [
    ("Lab C1-A - WHOIS and RIRs",                  f"{GITHUB_BASE}/lab-c1a-whois-rirs-v1.html"),
    ("Lab C2-A - DNS Enumeration",                  f"{GITHUB_BASE}/lab-c2a-dns-enumeration-v1.html"),
    ("Lab C2-B - DNS Zone Transfer (Live AXFR)",    f"{GITHUB_BASE}/lab-c2b-dns-zone-transfer-v1.html"),
    ("Lab C3-A - Web Recon",                        f"{GITHUB_BASE}/lab-c3a-web-recon-v1.html"),
    ("Lab C4-A - Google Hacking",                   f"{GITHUB_BASE}/lab-c4a-google-hacking-v1.html"),
    ("Lab C5-A - Email Headers",                    f"{GITHUB_BASE}/lab-c5a-email-headers-v1.html"),
    ("Lab C6-A - OSINT Sources",                    f"{GITHUB_BASE}/lab-c6a-osint-sources-v1.html"),
]

# If you already know the Module C chapter ID, paste it here to skip detection.
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
    """POST full content object - confirmed working pattern from SC-300 / Module A v6."""
    payload = {
        "content": {
            "type": "lesson",
            "id": uid(),
            "items": [
                {
                    "id": uid(),
                    "type": "iframe",
                    "url": iframe_url,
                    "aspect_height": 9,
                    "aspect_width": 16
                }
            ]
        }
    }
    status, data = api_post(
        f"/api/content/{COURSE_ID}/lessons/{lesson_id}",
        payload
    )
    print(f"    content status={status}")
    return status


def main():
    print("=" * 55)
    print("CourseStack: Push ALL Module C Labs")
    print(f"Course ID: {COURSE_ID}")
    print(f"Labs to push: {len(LABS)}")
    print("=" * 55)

    chapter_id = MODULE_C_CHAPTER_ID or find_or_create_chapter()
    if not chapter_id:
        print("FATAL: could not find or create Module C chapter. Aborting.")
        return

    print(f"\n[*] Chapter ID: {chapter_id}")
    print("[*] Creating lessons...\n")

    results = []
    for name, url in LABS:
        lesson_id = create_lesson(chapter_id, name)
        if lesson_id:
            time.sleep(0.5)
            status = set_lesson_content(lesson_id, url)
            results.append((name, lesson_id, status, url))
        else:
            results.append((name, None, None, url))
        time.sleep(0.5)

    print("\n" + "=" * 55)
    print("Results summary:")
    for name, lid, status, url in results:
        ok = "OK" if status == 200 else f"FAILED ({status})"
        print(f"  {ok}  {name}")
    print("\nCourse editor:")
    print(f"  https://app.coursestack.com/courses/{COURSE_ID}")
    print("=" * 55)


if __name__ == "__main__":
    main()

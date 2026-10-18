"""
CourseStack - Push Module B Labs to CPSA course  v1
Creates a "Module B - Labs" chapter with one lesson per hands-on lab.
Each lesson embeds the GitHub Pages URL as an iframe.

Labs:
  B4-A  Network Sweeping
  B4-B  Route Mapping
  B4-C  Port Scanning
  B5-A  Tool Output Analysis
  B8-A  OS Fingerprinting
  B9-A  Banner Grabbing and Service Identification
  B13-A Linux Privilege Escalation - SUID, Cron and Sudo
  B13-B Linux Privilege Escalation via NFS no_root_squash
  B14-A Process and Socket Enumeration
  B14-B Windows Privilege Escalation - Services and Registry
"""

import requests
import uuid
import time
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"

GH_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-b"

LABS = [
    ("Lab B4-A - Network Sweeping",                        "lab-b4a-network-sweeping-v1.html"),
    ("Lab B4-B - Route Mapping",                           "lab-b4b-route-mapping-v1.html"),
    ("Lab B4-C - Port Scanning",                           "lab-b4c-port-scanning-v1.html"),
    ("Lab B5-A - Tool Output Analysis",                    "lab-b5a-tool-output-v1.html"),
    ("Lab B8-A - OS Fingerprinting",                       "lab-b8a-os-fingerprinting-v1.html"),
    ("Lab B9-A - Banner Grabbing and Service ID",          "lab-b9a-banner-grabbing-v1.html"),
    ("Lab B13-A - Linux Privilege Escalation",             "lab-b13a-linux-privesc-v1.html"),
    ("Lab B13-B - Linux Privilege Escalation via NFS",     "lab-b13b-linux-privesc-nfs-v1.html"),
    ("Lab B14-A - Process and Socket Enumeration",         "lab-b14a-process-socket-enum-v1.html"),
    ("Lab B14-B - Windows Privilege Escalation",           "lab-b14b-windows-privesc-v1.html"),
]

HEADERS = {"Content-Type": "application/json"}


def uid():
    return str(uuid.uuid4()).replace("-", "")


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


def create_chapter(name, description=""):
    print(f"\n[chapter] {name}")
    status, data = api_post(
        f"/api/content/{COURSE_ID}/chapters",
        {"name": name, "description": description}
    )
    chapter_id = None
    if isinstance(data, dict):
        chapter_id = (data.get("chapter") or data.get("data") or data).get("id") or data.get("id")
    print(f"  status={status}  chapter_id={chapter_id}")
    return chapter_id


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
    print("=== CourseStack: Push Module B Labs ===")

    chapter_id = create_chapter(
        "Module B - Hands-On Labs",
        "Practical lab exercises covering CREST CPSA Module B: Core Technical Skills"
    )
    if not chapter_id:
        print("FATAL: could not create chapter. Aborting.")
        return

    time.sleep(1)

    for lesson_name, filename in LABS:
        url = f"{GH_BASE}/{filename}"
        lesson_id = create_lesson(chapter_id, lesson_name)
        if lesson_id:
            time.sleep(0.5)
            set_lesson_content(lesson_id, url)
        time.sleep(0.5)

    print("\n=== Done ===")
    print(f"Chapter ID: {chapter_id}")
    print(f"Course: https://app.coursestack.com/courses/{COURSE_ID}")


if __name__ == "__main__":
    main()

"""
CourseStack - Patch Module B lesson content  v1
Lessons already exist. This script pushes the iframe content to each one.
Uses the correct payload shape: {"content": {"type":"lesson","id":"...","items":[...]}}
"""

import requests
import uuid
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
HEADERS   = {"Content-Type": "application/json"}

GH_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-b"

# Lesson IDs from the first run
LESSONS = [
    ("1c337e35-21dd-4fa7-bab0-e65d5ceed997", "lab-b4a-network-sweeping-v1.html",        "Lab B4-A - Network Sweeping"),
    ("b16790fe-9668-4cd0-977c-9d9a6457c439", "lab-b4b-route-mapping-v1.html",            "Lab B4-B - Route Mapping"),
    ("f83ac7d3-5e3f-47e4-a718-83cb41a10ad4", "lab-b4c-port-scanning-v1.html",            "Lab B4-C - Port Scanning"),
    ("07695254-de1c-442a-8330-27f9918330cf", "lab-b5a-tool-output-v1.html",              "Lab B5-A - Tool Output Analysis"),
    ("a8813d7e-47d4-4b29-93f8-3d4628e32ced", "lab-b8a-os-fingerprinting-v1.html",        "Lab B8-A - OS Fingerprinting"),
    ("bc5997c7-fb8e-4ad1-91f3-c685d6282634", "lab-b9a-banner-grabbing-v1.html",          "Lab B9-A - Banner Grabbing"),
    ("09d215ee-979a-430c-821e-af8fb8e0b27c", "lab-b13a-linux-privesc-v1.html",           "Lab B13-A - Linux Privilege Escalation"),
    ("572e93ad-181a-477f-842a-ed92ace5e6e2", "lab-b13b-linux-privesc-nfs-v1.html",       "Lab B13-B - Linux Privesc via NFS"),
    ("33b22095-0c08-4de6-b129-42b2f4daf272", "lab-b14a-process-socket-enum-v1.html",     "Lab B14-A - Process and Socket Enumeration"),
    ("9fdd3538-3741-45a2-8429-d50cc76108a1", "lab-b14b-windows-privesc-v1.html",         "Lab B14-B - Windows Privilege Escalation"),
]


def uid():
    return str(uuid.uuid4()).replace("-", "")


def push_content(lesson_id, lesson_name, iframe_url):
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
    url = f"{BASE}/api/content/{COURSE_ID}/lessons/{lesson_id}"
    r = requests.post(url, auth=auth, headers=HEADERS, json=payload, timeout=20)
    if r.ok:
        print(f"  OK  {lesson_name}")
    else:
        print(f"  ERR {r.status_code} - {lesson_name}: {r.text[:200]}")
    return r.status_code


def main():
    print("=== Patching Module B lesson content ===\n")
    ok = 0
    for lesson_id, filename, name in LESSONS:
        iframe_url = f"{GH_BASE}/{filename}"
        status = push_content(lesson_id, name, iframe_url)
        if status == 200:
            ok += 1
    print(f"\n=== Done: {ok}/{len(LESSONS)} lessons updated ===")


if __name__ == "__main__":
    main()

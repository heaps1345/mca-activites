"""
Push CPSA Module B - VLANs and Wireless lesson to CourseStack.
Run locally on Windows - proxy blocks outbound to app.coursestack.com from cloud.
"""

import requests

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
BASE_URL  = "https://app.coursestack.com"

LESSON_URL = "https://heaps1345.github.io/mca-activites/cpsa/module-b/cpsa_b_vlans_wireless_v1.html"

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})


def create_chapter():
    r = session.post(
        f"{BASE_URL}/api/v1/courses/{COURSE_ID}/chapters",
        json={"title": "Module B - VLANs and Wireless"}
    )
    r.raise_for_status()
    chapter_id = r.json()["id"]
    print(f"[+] Chapter created: {chapter_id}")
    return chapter_id


def create_lesson(chapter_id):
    payload = {
        "title": "VLANs and Wireless - Lesson and Quiz",
        "chapterId": chapter_id,
        "type": "text",
        "content": r"""## VLANs and Wireless

This lesson covers VLAN hopping attacks and wireless encryption weaknesses for CREST CPSA Module B.

**Topics covered:**
- What is a VLAN and why segmentation matters
- VLAN double-tagging attack - how it works and how to defend
- Switch spoofing via DTP - exploiting auto-negotiation
- Wireless encryption status - WEP, WPA2-PSK, WPA3, WPS
- Breaking WEP with aircrack-ng (IV weakness)
- Breaking WPA2-PSK via 4-way handshake capture and offline cracking
- Breaking WPS via split PIN brute-force (Reaver/Bully)
- 15-question quiz with progress saved between sessions

<iframe src="{url}" width="100%" height="900" frameborder="0" allowfullscreen style="border-radius:8px;"></iframe>
""".replace("{url}", LESSON_URL)
    }
    r = session.post(
        f"{BASE_URL}/api/v1/courses/{COURSE_ID}/lessons",
        json=payload
    )
    r.raise_for_status()
    lesson_id = r.json()["id"]
    print(f"[+] Lesson created: {lesson_id}")
    return lesson_id


if __name__ == "__main__":
    print("[*] Pushing VLANs and Wireless lesson to CourseStack...")
    chapter_id = create_chapter()
    lesson_id  = create_lesson(chapter_id)
    print(f"\n[+] Done.")
    print(f"    Course:  {BASE_URL}/courses/{COURSE_ID}")
    print(f"    Chapter: {chapter_id}")
    print(f"    Lesson:  {lesson_id}")

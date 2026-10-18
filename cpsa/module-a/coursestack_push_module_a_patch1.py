"""
CourseStack - Module A Patch 1
Adds:
  - A-07: Professional Ethics and Independence (new lesson)
  - Updates Module A Knowledge Check to 10 questions (adds 5 ethics MCQs)

Run AFTER the main v6 deploy. Requires the correct lesson IDs from that run.
Update CHAPTER_ID and KC_LESSON_ID below before running.
"""

import requests
import uuid
import time
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"

# -------------------------------------------------------
# UPDATE THESE after running v6 - get from v6 output
# -------------------------------------------------------
CHAPTER_ID    = "PASTE_CHAPTER_ID_HERE"
KC_LESSON_ID  = "PASTE_KC_LESSON_ID_HERE"
# -------------------------------------------------------

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
        print(f"  ERROR {r.status_code}: {r.text[:400]}")
    return r.status_code, data


def create_lesson(chapter_id, name, passing_percent=None):
    print(f"  [lesson] {name}")
    payload = {"name": name, "chapter_id": chapter_id, "type": "lesson"}
    if passing_percent is not None:
        payload["passing_percent"] = passing_percent
    status, data = api_post(f"/api/content/{COURSE_ID}/lessons", payload)
    lesson_obj = data.get("lesson") or data.get("data") or data
    lesson_id = lesson_obj.get("id") if isinstance(lesson_obj, dict) else data.get("id")
    print(f"    status={status}  lesson_id={lesson_id}")
    return lesson_id


def push_content(lesson_id, items):
    status, data = api_post(
        f"/api/content/{COURSE_ID}/lessons/{lesson_id}",
        {"content": {"type": "lesson", "id": uid(), "items": items}}
    )
    print(f"    push_content -> {status}")
    return status


def make_text(markdown):
    return {"id": uid(), "type": "text", "markdown": markdown}


def make_mcq(question, answers):
    return {
        "id": uid(),
        "type": "question-multiple-choice",
        "question": question,
        "answers": [{"id": uid(), **a} for a in answers],
    }


# -------------------------------------------------------
# A-07 content
# -------------------------------------------------------

ETHICS_MD = """## A7 - Professional Ethics and Independence

### Why Ethics Matter in Penetration Testing

A penetration tester has privileged access to systems, data, and vulnerabilities that could cause serious harm if misused or misreported. Professional ethics and independence are not optional extras - they are the foundation of a credible assessment and a requirement of the CREST Code of Conduct.

### The Independence Principle

Your report must reflect what you found, not what the client wants to hear. A tester who modifies findings under client pressure:

- Produces a false picture of the organisation's security posture
- Leaves real risks unmitigated
- Exposes the client's customers, staff, and partners to harm
- Breaches the CREST Code of Conduct
- May expose themselves to professional and legal liability

### Common Pressure Scenarios

**"Can you downgrade this finding? The board presentation is next week."**
No. Severity ratings are based on CVSS scores and technical evidence, not on the timing of board meetings. If the finding is Critical, it is Critical.

**"We're going through a PCI audit next month - can this just not appear in the report?"**
No. Omitting findings from a compliance-driven assessment could constitute fraud and directly harms the organisation's customers.

**"We've already patched it - can you just mark it as remediated?"**
Only if you can verify the patch. You must re-test or note that remediation was client-asserted and unverified.

**"The finding description makes us look bad - can you soften the language?"**
Clarity is not optional. Technical readers need precise descriptions. You can ensure language is professional and factual, but you cannot obscure the nature or impact of a vulnerability.

### The Right Response to Pressure

1. **Listen and acknowledge** - understand the concern without agreeing to change anything
2. **Explain your obligation** - your report is a professional document and your name is on it
3. **Document the request** - record that the client asked for a modification and that you declined
4. **Escalate if needed** - if employed by a firm, inform your line manager immediately
5. **Walk away if necessary** - if a client insists on falsification, withdraw from the engagement

### CREST Code of Conduct

CREST-certified testers are bound by the CREST Code of Conduct, which requires:

- **Integrity** - honest reporting of findings without omission or distortion
- **Objectivity** - assessments based on evidence, not on client relationships or commercial pressure
- **Confidentiality** - all data and findings handled securely and disclosed only to authorised parties
- **Competence** - only undertaking work within your area of expertise

Breaching the Code of Conduct can result in loss of CREST certification.

### What You Can Legitimately Do

- Correct factual errors (wrong IP address, wrong service version)
- Improve clarity or professionalism of language without changing meaning
- Add context the client provides that changes the technical picture (e.g. a compensating control you were not aware of)
- Mark a finding as remediated after successful re-test verification

### Syntex Application

If Sarah Chen (Syntex CEO) contacted you after receiving the draft report and asked you to remove the Kerberoasting finding because "it will cause panic with investors" - the correct response is to decline, document the request, and submit the report as written. The finding is real, evidenced, and Critical. Omitting it would be unethical and potentially fraudulent given Syntex's PCI DSS obligations.
"""


# -------------------------------------------------------
# All 10 knowledge check questions
# -------------------------------------------------------

ALL_KC_QUESTIONS = [
    # Original 5
    {
        "question": "Which document in an engagement pack provides legal authorisation for the penetration test and constitutes a defence under the Computer Misuse Act 1990?",
        "answers": [
            {"answer": "Scope of Work", "correct": False},
            {"answer": "Rules of Engagement", "correct": False},
            {"answer": "Permission to Test Letter", "correct": True},
            {"answer": "Client Brief", "correct": False},
        ],
    },
    {
        "question": "A vulnerability is exploitable over the network with no authentication required. It results in full compromise of the target system only. What is the CVSS v3.1 vector string?",
        "answers": [
            {"answer": "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "correct": True},
            {"answer": "AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H", "correct": False},
            {"answer": "AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "correct": False},
            {"answer": "AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H", "correct": False},
        ],
    },
    {
        "question": "Kerberoasting is scored at CVSS 9.9 rather than 9.8. Which metric difference accounts for the higher score?",
        "answers": [
            {"answer": "Attack Complexity is Low rather than High", "correct": False},
            {"answer": "Scope is Changed rather than Unchanged", "correct": True},
            {"answer": "Privileges Required is None rather than Low", "correct": False},
            {"answer": "Attack Vector is Network rather than Adjacent", "correct": False},
        ],
    },
    {
        "question": "Which PCI DSS v4.0 requirement mandates annual penetration testing for organisations that process card data?",
        "answers": [
            {"answer": "Req 6.3", "correct": False},
            {"answer": "Req 8.2", "correct": False},
            {"answer": "Req 11.3", "correct": True},
            {"answer": "Req 4.2.1", "correct": False},
        ],
    },
    {
        "question": "Which phase of the penetration testing lifecycle must be completed before any active scanning or testing begins?",
        "answers": [
            {"answer": "Reconnaissance", "correct": False},
            {"answer": "Reporting", "correct": False},
            {"answer": "Pre-engagement and Authorisation", "correct": True},
            {"answer": "Scanning and Enumeration", "correct": False},
        ],
    },
    # New ethics questions
    {
        "question": "A client contacts you after receiving the draft report and asks you to downgrade a Critical finding to Medium because the board presentation is next week. What is the correct response?",
        "answers": [
            {"answer": "Downgrade it - the client relationship is important", "correct": False},
            {"answer": "Decline, document the request, and submit the report as written", "correct": True},
            {"answer": "Add a note explaining the timing issue and downgrade temporarily", "correct": False},
            {"answer": "Remove the finding and add it to a separate confidential annex", "correct": False},
        ],
    },
    {
        "question": "A client tells you they have already patched a High severity finding before the report is issued and asks you to mark it as remediated. What should you do?",
        "answers": [
            {"answer": "Mark it as remediated - the client has confirmed the fix", "correct": False},
            {"answer": "Remove the finding entirely as it no longer applies", "correct": False},
            {"answer": "Re-test to verify or note it as client-asserted and unverified", "correct": True},
            {"answer": "Downgrade it to Low severity to reflect the reduced risk", "correct": False},
        ],
    },
    {
        "question": "Which of the following is a legitimate reason to modify a finding after the draft report has been issued?",
        "answers": [
            {"answer": "The client is undergoing a PCI audit and the finding would cause a failure", "correct": False},
            {"answer": "The client's CEO has asked for softer language throughout the report", "correct": False},
            {"answer": "You identified a factual error - the finding affected the wrong IP address", "correct": True},
            {"answer": "The client's investor presentation is scheduled for the following week", "correct": False},
        ],
    },
    {
        "question": "Under the CREST Code of Conduct, which principle requires that a tester's assessment is based on evidence rather than on commercial or relationship pressure?",
        "answers": [
            {"answer": "Confidentiality", "correct": False},
            {"answer": "Competence", "correct": False},
            {"answer": "Integrity", "correct": False},
            {"answer": "Objectivity", "correct": True},
        ],
    },
    {
        "question": "A client asks you to omit a Critical finding from a compliance assessment because they are going through a PCI audit next month. What is the most serious risk of complying with this request?",
        "answers": [
            {"answer": "The report will be shorter than expected", "correct": False},
            {"answer": "It could constitute fraud and leave real risk unmitigated, harming the client's customers", "correct": True},
            {"answer": "The CVSS score average will be lower", "correct": False},
            {"answer": "The client may receive a lower overall risk rating than deserved", "correct": False},
        ],
    },
]


def main():
    print("=" * 60)
    print("Module A Patch 1 - Ethics lesson + 10-question KC")
    print("=" * 60)

    if CHAPTER_ID == "PASTE_CHAPTER_ID_HERE":
        print("\nERROR: Update CHAPTER_ID and KC_LESSON_ID at the top of this script first.")
        return

    # Add A-07 ethics lesson
    print("\n--- Adding A-07: Professional Ethics ---")
    ethics_id = create_lesson(CHAPTER_ID, "A-07: Professional Ethics and Independence")
    if ethics_id:
        push_content(ethics_id, [make_text(ETHICS_MD)])
    time.sleep(0.3)

    # Update knowledge check with all 10 questions
    print("\n--- Updating Knowledge Check (10 questions) ---")
    items = [make_text(
        "## Module A Knowledge Check\n\n"
        "Answer all ten questions. A score of 70% or above is required to complete Module A.\n\n"
        "The questions cover: penetration testing lifecycle, engagement pack documents, "
        "CVSS v3.1 scoring, compliance frameworks, and professional ethics."
    )]
    for q in ALL_KC_QUESTIONS:
        items.append(make_mcq(q["question"], q["answers"]))
    push_content(KC_LESSON_ID, items)

    print("\n" + "=" * 60)
    print("Patch 1 complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()

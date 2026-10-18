"""
CourseStack - Push Module A (Soft Skills) to CPSA course  v6
Fixed: use POST /api/content/{course_id}/lessons/{lesson_id} with full
       content object (same pattern confirmed working in SC-300 course).
       Items endpoint does not exist - content goes in the lesson body.

Lesson plan:
  A-01  Introduction and Scenario        (text)
  A-02  Penetration Testing Lifecycle    (text)
  A-03  Engagement Packs                 (text)
  A-04  Pentest Report Writing           (text)
  A-05  CVSS v3.1 Scoring               (text)
  A-06  Compliance Mapping              (text)
  Lab A1  Engagement Pack Review        (iframe)
  Lab A2  Model Answer Report           (iframe)
  Lab A3  Student Report Template       (iframe)
  Lab A4  CVSS Scoring Worksheet        (iframe)
  Module A: Knowledge Check             (text + MCQs)
"""

import requests
import uuid
import time
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"

ARTIFACT_ENGAGEMENT_PACK = "https://heaps1345.github.io/mca-activites/cpsa/module-a/syntex_engagement_pack_v1.html"
ARTIFACT_FINDINGS_REPORT = "https://heaps1345.github.io/mca-activites/cpsa/module-a/syntex_findings_report_v1.html"
ARTIFACT_STUDENT_REPORT  = "https://heaps1345.github.io/mca-activites/cpsa/module-a/syntex_student_report_v1.html"
ARTIFACT_CVSS_WORKSHEET  = "https://heaps1345.github.io/mca-activites/cpsa/module-a/syntex_cvss_worksheet_v1.html"

HEADERS = {"Content-Type": "application/json"}


def uid():
    return str(uuid.uuid4()).replace("-", "")


# -------------------------------------------------------
# API helpers
# -------------------------------------------------------

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


def create_lesson(chapter_id, name, passing_percent=None):
    print(f"  [lesson] {name}")
    payload = {"name": name, "chapter_id": chapter_id, "type": "lesson"}
    if passing_percent is not None:
        payload["passing_percent"] = passing_percent
    status, data = api_post(f"/api/content/{COURSE_ID}/lessons", payload)

    lesson_obj = data.get("lesson") or data.get("data") or data
    if isinstance(lesson_obj, dict):
        lesson_id = lesson_obj.get("id")
    else:
        lesson_id = None

    # fetch to confirm id if missing
    if not lesson_id:
        lesson_id = data.get("id")

    print(f"    status={status}  lesson_id={lesson_id}")
    return lesson_id


def push_content(lesson_id, items):
    """POST full content object to lesson - the working pattern from SC-300."""
    status, data = api_post(
        f"/api/content/{COURSE_ID}/lessons/{lesson_id}",
        {"content": {"type": "lesson", "id": uid(), "items": items}}
    )
    print(f"    push_content -> {status}")
    return status


def make_text(markdown):
    return {"id": uid(), "type": "text", "markdown": markdown}


def make_iframe(url, title=""):
    return {"id": uid(), "type": "iframe", "url": url, "aspect_height": 9, "aspect_width": 16}


def make_mcq(question, answers, explanation=""):
    answers_with_ids = [{"id": uid(), **a} for a in answers]
    return {
        "id": uid(),
        "type": "question-multiple-choice",
        "question": question,
        "answers": answers_with_ids,
    }


# -------------------------------------------------------
# Lesson content
# -------------------------------------------------------

INTRO_MD = """## Module A - Soft Skills: Syntex Solutions Ltd Scenario

Welcome to Module A of the MCA CREST CPSA course. This module covers the professional and procedural skills required of a practitioner - the foundation that every technical assessment is built on.

### Scenario Context

Throughout this module you will work with a fictional client: **Syntex Solutions Ltd** - a UK-based fintech company processing card payments, regulated under PCI DSS v4.0, UK GDPR and FCA SYSC.

You have been engaged to conduct a **grey box penetration test** against two target systems:

- **SYNTEX-DC01** - Windows Server 2016 Active Directory Domain Controller (10.0.29.131)
- **SYNTEX-LNX01** - Ubuntu 20.04 LTS web server (10.1.53.39)

Starting credentials have been supplied: `jsmith / Password1`

### Module A Objectives

By the end of this module you will be able to:

- Describe all phases of the penetration testing lifecycle
- Identify and explain the purpose of each document in an engagement pack
- Structure a pentest report for both executive and technical audiences
- Calculate CVSS v3.1 base scores and justify severity ratings
- Map technical findings to regulatory obligations (PCI DSS, UK GDPR, FCA SYSC, CMA)

### Module A Labs

| Lab | Title | Format |
|-----|-------|--------|
| Lab A1 | Engagement Pack Review | Interactive document review |
| Lab A2 | Model Answer Report | Annotated findings report |
| Lab A3 | Student Report Template | Fillable HTML form |
| Lab A4 | CVSS Scoring Worksheet | Interactive calculator |
"""

PT_LIFECYCLE_MD = """## A1 - Penetration Testing Lifecycle

### Overview

A penetration test is not an ad-hoc activity. Every professional engagement follows a defined lifecycle that ensures legal authorisation, consistent methodology, and actionable outputs.

### The Seven Phases

**1. Scoping and Engagement**
The client defines what is to be tested, the testing approach (black/grey/white box), timeframe, and budget. The scope document must be agreed and signed before any work begins.

**2. Pre-engagement and Authorisation**
Legal documents are prepared and signed:
- Permission to Test Letter (legal cover under Computer Misuse Act 1990 s.1)
- Scope of Work (target IPs, exclusions, permitted techniques)
- Rules of Engagement (testing hours, prohibited actions, escalation contacts)

**3. Reconnaissance and Information Gathering**
Passive and active intelligence gathering about the target environment. OSINT, DNS enumeration, service discovery.

**4. Scanning and Enumeration**
Active network scanning, port scanning, service version detection, vulnerability scanning.

**5. Exploitation and Post-Exploitation**
Controlled exploitation of vulnerabilities to demonstrate impact. Evidence captured at each stage.

**6. Reporting**
All findings documented with evidence, CVSS scores, and remediation guidance. Separate executive and technical sections.

**7. Debrief and Closure**
Results presented to the client. Remediation verified if a re-test is in scope. All test data securely deleted.

### Why the Lifecycle Matters

Testing without written authorisation is an offence under Computer Misuse Act 1990 s.1. The engagement pack documents are not bureaucracy - they are legal protection for both the tester and the client.

### Syntex Application

For the Syntex engagement:
- Permission to Test Letter is signed by CEO **Sarah Chen**
- Testing hours: 09:00-17:00 Monday-Friday
- No denial-of-service testing against payment processing services
- Emergency contact: Mark Harris CTO +44 7700 900123
"""

ENGAGEMENT_PACKS_MD = """## A2 - Engagement Packs

### What is an Engagement Pack?

An engagement pack is the complete set of documents that authorise, define, and govern a penetration test. Every professional engagement requires all six documents before testing begins.

### The Six Documents

**1. Client Brief**
Provides business context: what the organisation does, its regulatory obligations, the drivers for commissioning the assessment, and key stakeholder contacts.

**2. Scope of Work**
Precisely defines the technical scope: target IP addresses and ranges, systems explicitly excluded, types of testing permitted, and any technical constraints.

**3. Rules of Engagement**
Operational constraints: permitted testing hours, prohibited techniques (e.g. DoS), required evidence capture standards, and emergency escalation procedures.

**4. Permission to Test Letter**
The legal cornerstone. A formal letter signed by the asset owner authorising the assessment. Provides a s.1 Computer Misuse Act 1990 defence. Must be obtained before any active testing.

**5. Supplied Credentials**
For grey box engagements: the starting credentials provided by the client, the account level, and any caveats on their use.

**6. Network Overview**
Technical context: IP addressing, subnet layout, key services by host, and a logical/physical network diagram.

### Common Exam Questions

- Which document provides legal authorisation for the test? **Permission to Test Letter**
- What Act governs unauthorised computer access in the UK? **Computer Misuse Act 1990**
- What section makes unauthorised access an offence? **Section 1**

### Syntex Engagement Pack

The Syntex engagement pack is available in Lab A1. Work through it and answer the review questions before proceeding.
"""

REPORT_WRITING_MD = """## A3 - Pentest Report Writing

### Report Structure

A professional penetration test report contains seven sections:

1. **Cover Page and Metadata** - Client name, engagement type, date, version, classification, consultant name
2. **Executive Summary** - Non-technical overview: what was tested, overall risk rating, headline findings, business impact
3. **Risk Summary Table** - All findings tabulated with ID, title, severity, CVSS score, and remediation status
4. **Scope and Methodology** - Targets tested, testing approach, tools used, any limitations encountered
5. **Technical Findings** - Each finding in full: title, severity, CVSS, description, evidence, remediation
6. **Compliance Impact** - Regulatory mapping showing which findings breach specific framework requirements
7. **Remediation Roadmap** - Prioritised action plan with immediate, short-term, and long-term recommendations

### Writing for Two Audiences

**Executive Summary** (read by the CEO/CTO):
- No technical jargon
- Business risk framing: "customer card data is at risk"
- Severity counts and overall risk rating
- Regulatory implications
- Maximum one page

**Technical Findings** (read by the sysadmin team):
- Precise tool names, CVE IDs, exact commands
- Screenshots and command output as evidence
- CVSS vector string for reproducibility
- File paths and config changes in remediation
- Sufficient detail to reproduce and verify the fix

### Finding Format

Every technical finding must include:
- **ID** - Sequential reference (e.g. F-01)
- **Title** - Concise description of the vulnerability
- **Severity** - Critical / High / Medium / Low / Informational
- **CVSS v3.1 Score** - Numeric score and vector string
- **Description** - What the vulnerability is and why it matters
- **Evidence** - Screenshot or command output proving exploitability
- **Remediation** - Specific, actionable fix guidance

### Syntex Report

The model answer report for the Syntex engagement (18 findings, 3 Critical / 7 High / 6 Medium / 2 Low) is available in Lab A2. The fillable student template is in Lab A3.
"""

CVSS_MD = """## A4 - CVSS v3.1 Scoring

### What is CVSS?

The Common Vulnerability Scoring System (CVSS) v3.1 is the industry-standard framework for rating the severity of security vulnerabilities. It produces a numeric score from 0.0 to 10.0 and a corresponding severity band.

### The Eight Base Metrics

**Exploitability Metrics** (how easy is it to exploit?):

| Metric | Abbreviation | Values |
|--------|-------------|--------|
| Attack Vector | AV | Network (N), Adjacent (A), Local (L), Physical (P) |
| Attack Complexity | AC | Low (L), High (H) |
| Privileges Required | PR | None (N), Low (L), High (H) |
| User Interaction | UI | None (N), Required (R) |

**Impact Metrics** (what damage does exploitation cause?):

| Metric | Abbreviation | Values |
|--------|-------------|--------|
| Scope | S | Unchanged (U), Changed (C) |
| Confidentiality | C | None (N), Low (L), High (H) |
| Integrity | I | None (N), Low (L), High (H) |
| Availability | A | None (N), Low (L), High (H) |

### Score Ranges

| Score | Severity |
|-------|----------|
| 0.0 | None |
| 0.1 - 3.9 | Low |
| 4.0 - 6.9 | Medium |
| 7.0 - 8.9 | High |
| 9.0 - 10.0 | Critical |

### The Scope Metric

Scope is the metric candidates most commonly get wrong. It describes whether exploitation of the vulnerable component can impact components beyond it:

- **Scope Unchanged (S:U)** - impact stays within the vulnerable component
- **Scope Changed (S:C)** - impact extends to other components (e.g. Kerberoasting on a domain controller affects all domain-joined systems)

When Scope is Changed, the Privileges Required weighting increases, often raising the score significantly.

### CVSS Vector String

The complete vector string encodes all eight metric values:

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H = 9.8 Critical`

### Lab A4 - CVSS Scoring Worksheet

Practice calculating scores for six Syntex findings using the interactive calculator. Compare your results to the model answers.
"""

COMPLIANCE_MD = """## A5 - Compliance Mapping

### Why Compliance Matters for Pentesters

A penetration tester working with regulated clients must understand which findings breach specific regulatory requirements. This shapes the prioritisation of the risk summary table and the executive summary narrative.

### Four Frameworks Relevant to Syntex

**PCI DSS v4.0** (Payment Card Industry Data Security Standard)
Syntex processes card payments - PCI DSS compliance is mandatory.

- Req 6.3: Protect all system components from known vulnerabilities
- Req 8.2: Unique user IDs and strong password requirements
- Req 11.3: Annual internal and external penetration testing
- Req 4.2.1: Strong cryptography for data in transit

**UK GDPR / Data Protection Act 2018**
Syntex holds customer personally identifiable information (PII).

- Art 5(1)(f): Security of personal data processing (integrity and confidentiality)
- Art 32: Technical and organisational measures to ensure data security
- Art 33: 72-hour breach notification requirement

**FCA SYSC** (Senior Management Arrangements, Systems and Controls)
Syntex is FCA-regulated as a payment processing firm.

- SYSC 8: Outsourcing and third-party risk management
- SYSC 15A: Operational resilience - impact tolerances
- PS21/3: Operational resilience rules for UK financial firms

**Computer Misuse Act 1990**
Governs the test itself, not the findings. The Permission to Test Letter provides the s.1 defence.

### Mapping Findings to Frameworks

| Finding | PCI DSS | UK GDPR | FCA SYSC |
|---------|---------|---------|----------|
| Kerberoasting (Critical) | Req 8.2, 6.3 | Art 32 | SYSC 15A |
| Weak SSH Root Password (Critical) | Req 8.2, 11.3 | Art 32, 5(1)(f) | SYSC 15A |
| Apache Struts RCE (Critical) | Req 6.3, 11.3 | Art 32, 33 | SYSC 8 |
| Cleartext FTP Credentials (High) | Req 8.2, 4.2 | Art 32, 25 | SYSC 8 |
| Outdated SSL/TLS (High) | Req 4.2.1 | Art 32 | SYSC 15A |

### CREST CPSA Exam Tip

You will not be asked to memorise every PCI DSS requirement number. You will be expected to know:
- That PCI DSS Req 11.3 mandates penetration testing
- That UK GDPR Art 32 requires technical security measures
- That CMA 1990 s.1 governs authorisation for the test itself
"""

KNOWLEDGE_CHECK_QUESTIONS = [
    {
        "question": "Which document in an engagement pack provides legal authorisation for the penetration test and constitutes a defence under the Computer Misuse Act 1990?",
        "answers": [
            {"answer": "Scope of Work", "correct": False},
            {"answer": "Rules of Engagement", "correct": False},
            {"answer": "Permission to Test Letter", "correct": True},
            {"answer": "Client Brief", "correct": False},
        ],
        "explanation": "The Permission to Test Letter, signed by the asset owner, provides a s.1 Computer Misuse Act 1990 defence. Without it, accessing computer systems is a criminal offence regardless of the tester's intent."
    },
    {
        "question": "A vulnerability is exploitable over the network with no authentication required. It results in full compromise of the target system only. What is the CVSS v3.1 vector string?",
        "answers": [
            {"answer": "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "correct": True},
            {"answer": "AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H", "correct": False},
            {"answer": "AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "correct": False},
            {"answer": "AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H", "correct": False},
        ],
        "explanation": "Network-based (AV:N), Low complexity (AC:L), No privileges (PR:N), No user interaction (UI:N), Scope Unchanged (S:U - only the target system is impacted), High CIA impact = 9.8 Critical."
    },
    {
        "question": "Kerberoasting is scored at CVSS 9.9 rather than 9.8. Which metric difference accounts for the higher score?",
        "answers": [
            {"answer": "Attack Complexity is Low rather than High", "correct": False},
            {"answer": "Scope is Changed rather than Unchanged", "correct": True},
            {"answer": "Privileges Required is None rather than Low", "correct": False},
            {"answer": "Attack Vector is Network rather than Adjacent", "correct": False},
        ],
        "explanation": "Kerberoasting on an Active Directory domain controller has Scope Changed (S:C) because compromising service account credentials impacts all domain-joined systems, not just the DC."
    },
    {
        "question": "Which PCI DSS v4.0 requirement mandates annual penetration testing for organisations that process card data?",
        "answers": [
            {"answer": "Req 6.3", "correct": False},
            {"answer": "Req 8.2", "correct": False},
            {"answer": "Req 11.3", "correct": True},
            {"answer": "Req 4.2.1", "correct": False},
        ],
        "explanation": "PCI DSS v4.0 Requirement 11.3 mandates annual internal and external penetration testing for all systems in the cardholder data environment."
    },
    {
        "question": "Which phase of the penetration testing lifecycle must be completed before any active scanning or testing begins?",
        "answers": [
            {"answer": "Reconnaissance", "correct": False},
            {"answer": "Reporting", "correct": False},
            {"answer": "Pre-engagement and Authorisation", "correct": True},
            {"answer": "Scanning and Enumeration", "correct": False},
        ],
        "explanation": "Pre-engagement and Authorisation must be completed first. The Permission to Test Letter must be signed before any active testing. Passive OSINT may be conducted before this, but port scanning requires written authorisation."
    },
]


# -------------------------------------------------------
# Main deployment
# -------------------------------------------------------

def main():
    print("=" * 60)
    print("CourseStack Module A Push v6 - CPSA Course")
    print(f"Course ID: {COURSE_ID}")
    print("=" * 60)

    chapter_id = create_chapter(
        "Module A: Soft Skills",
        "PT lifecycle, engagement packs, report writing, CVSS scoring and compliance mapping. Scenario: Syntex Solutions Ltd."
    )
    if not chapter_id:
        print("\nFATAL: Could not create chapter. Aborting.")
        return

    time.sleep(0.5)

    # Theory lessons
    theory_lessons = [
        ("A-01: Introduction and Scenario",     INTRO_MD),
        ("A-02: Penetration Testing Lifecycle",  PT_LIFECYCLE_MD),
        ("A-03: Engagement Packs",               ENGAGEMENT_PACKS_MD),
        ("A-04: Pentest Report Writing",         REPORT_WRITING_MD),
        ("A-05: CVSS v3.1 Scoring",              CVSS_MD),
        ("A-06: Compliance Mapping",             COMPLIANCE_MD),
    ]

    print("\n--- Theory Lessons ---")
    for name, content in theory_lessons:
        lesson_id = create_lesson(chapter_id, name)
        if lesson_id:
            push_content(lesson_id, [make_text(content)])
        time.sleep(0.3)

    # Lab lessons
    lab_lessons = [
        ("Lab A1: Engagement Pack Review",  ARTIFACT_ENGAGEMENT_PACK, "Syntex Engagement Pack"),
        ("Lab A2: Model Answer Report",     ARTIFACT_FINDINGS_REPORT, "Syntex Findings Report"),
        ("Lab A3: Student Report Template", ARTIFACT_STUDENT_REPORT,  "Student Report Template"),
        ("Lab A4: CVSS Scoring Worksheet",  ARTIFACT_CVSS_WORKSHEET,  "CVSS Scoring Worksheet"),
    ]

    print("\n--- Lab Lessons ---")
    for name, url, title in lab_lessons:
        lesson_id = create_lesson(chapter_id, name)
        if lesson_id:
            push_content(lesson_id, [make_iframe(url, title)])
        time.sleep(0.3)

    # Knowledge check
    print("\n--- Knowledge Check ---")
    kc_id = create_lesson(chapter_id, "Module A: Knowledge Check", passing_percent=70)
    if kc_id:
        items = [make_text("## Module A Knowledge Check\n\nAnswer all five questions. A score of 70% or above is required to complete Module A.\n\nThe questions cover: penetration testing lifecycle, engagement pack documents, CVSS v3.1 scoring, and compliance frameworks.")]
        for q in KNOWLEDGE_CHECK_QUESTIONS:
            items.append(make_mcq(q["question"], q["answers"], q["explanation"]))
        push_content(kc_id, items)

    print("\n" + "=" * 60)
    print("Module A deployment complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()

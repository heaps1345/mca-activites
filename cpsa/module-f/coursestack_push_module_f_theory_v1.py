"""
coursestack_push_module_f_theory_v1.py
--------------------------------------
Pushes Module F theory lessons and knowledge check to CourseStack.

Module F: Linux / Unix Security Assessment
Sections: F1 User Enumeration, F2 Unix Vulnerabilities, F3 FTP,
          F4 Sendmail / SMTP, F5-F9 Network Services, F6 Post-Exploitation

Course: b9d920c3-4a8e-4227-af24-3c5f32fc7350

Run on Windows:
  python coursestack_push_module_f_theory_v1.py

Lessons created:
  F-01  F1: User Enumeration
  F-02  F2: Unix Vulnerabilities
  F-03  F3: FTP
  F-04  F4: Sendmail and SMTP
  F-05  F5-F9: Network Services
  F-06  F6: Post-Exploitation and Reporting
  F-KC  Module F Knowledge Check
"""

import requests
import uuid
import time

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------
API_KEY   = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE_URL  = "https://app.coursestack.com"
COURSE_ID = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})

# -----------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------

def create_chapter(name):
    payload = {"name": name}
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/chapters", json=payload)
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    data = r.json()
    chapter_id = data.get("chapter", data).get("id") or data.get("id")
    print(f"  Chapter created -> {chapter_id}")
    return chapter_id

def create_lesson(name, chapter_id):
    payload = {"name": name, "type": "lesson", "chapter_id": chapter_id}
    r = session.post(f"{BASE_URL}/api/content/{COURSE_ID}/lessons", json=payload)
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    data = r.json()
    return data.get("lesson", data).get("id") or data.get("id")

def push_lesson_content(lesson_id, items):
    content = {
        "content": {
            "type": "lesson",
            "id": str(uuid.uuid4()),
            "items": items
        }
    }
    r = session.post(
        f"{BASE_URL}/api/content/{COURSE_ID}/lessons/{lesson_id}",
        json=content
    )
    if not r.ok:
        print(f"  CONTENT ERROR {r.status_code}: {r.text[:300]}")
        r.raise_for_status()

def text_item(markdown_text):
    return {"type": "text", "id": str(uuid.uuid4()), "markdown": markdown_text}

def make_lesson(name, chapter_id, items):
    print(f"  Creating: {name}")
    lesson_id = create_lesson(name, chapter_id)
    time.sleep(0.5)
    push_lesson_content(lesson_id, items)
    time.sleep(0.5)
    print(f"    OK -> {lesson_id}")

# -----------------------------------------------------------------------
# LESSON CONTENT
# -----------------------------------------------------------------------

LESSON_F1 = text_item("""\
## F1 - User Enumeration

Before attempting a single exploit against a Linux/Unix host, the professional
penetration tester builds a complete picture of who is on the system. User
enumeration reduces the brute-force search space from millions of possible
usernames down to dozens of confirmed accounts and reveals the application
stack through service accounts such as `www-data`, `postgres`, and `oracle`.

On the Syntex Solutions engagement the Linux targets share the same flat
network as the Windows domain. Usernames discovered here may map directly
to Active Directory accounts you already own.

---

### Why User Enumeration Matters

| Goal | Detail |
|------|--------|
| **Valid Usernames** | Reduce brute-force search space from millions to dozens |
| **Service Accounts** | Reveal the application stack: www-data, postgres, oracle |
| **Trust Mapping** | Cross-reference Linux users against AD accounts already harvested |
| **Privilege Targets** | Identify root, sudo users, and administrative accounts |

> **Operator Takeaway:** User enumeration is reconnaissance, not exploitation.
> Document every identified username as evidence before moving to attack phase.

---

### Enumeration Techniques Overview

**rusers / rwho**
RPC-based services that broadcast logged-in user lists. Require `rusersd`/`rwhod`
running on the target. Port 513 (UDP/TCP).

**finger daemon**
Port 79. Returns user details from `/etc/passwd` including full name, home
directory, login shell, and `.plan` file contents.

**SMTP VRFY / EXPN**
Sendmail commands that validate usernames and expand mailing list aliases.
Common on legacy Solaris and unpatched Linux mail hosts.

**Banner Grabbing**
`nc` / `telnet` to service ports. FTP, SSH, and SMTP banners reveal OS,
daemon version, and sometimes host identity.

---

### rusers / rwho / finger - Commands

**rusers - Remote User Listing**
```
rusers -al 10.10.10.50    # -a: show all users including idle, -l: long listing
rusers 10.10.10.0/24      # Sweep entire subnet
```

**rwho - Local Network Broadcast**
```
rwho    # Lists users on hosts running rwhod (passive - listens for UDP broadcasts)
```

**finger - Port 79**
```
nc -vn 10.10.10.50 79     # Banner grab
finger @10.10.10.50       # List all users
finger root@10.10.10.50   # Specific user
finger @internal@external  # Bounce attack
```

**Example finger output (syntex.local)**
```
Login: jsmith          Name: John Smith
Directory: /home/jsmith  Shell: /bin/bash
Last login Mon Oct 21 09:14 on pts/0
No Plan.

Login: www-data        Name: Web Daemon
Directory: /var/www    Shell: /usr/sbin/nologin
```

> **Operator Takeaway:** finger reads `/etc/passwd` directly. Every field it
> returns is intelligence. Home dirs reveal mount points; shell fields reveal
> service vs. interactive accounts.
""")

LESSON_F2 = text_item("""\
## F2 - Unix Vulnerabilities

With a user list in hand, the next phase is identifying exploitable conditions
on the target. This section covers public exploit research, the important
operational differences between Solaris and Linux, the full remote-exploit-to-root
chain, and the post-exploitation workflow required by the CREST CPSA syllabus.

---

### Public Exploit Research

A five-step methodology for finding and safely applying public exploits:

**01 - Identify the OS and Version**
```
uname -a
cat /etc/issue
cat /etc/os-release
```
Banner grabbing also reveals version information pre-authentication.

**02 - Identify Running Services and Versions**
```
nmap -sV 10.10.10.50
```
Combine with banner grabs and daemon config files for exact version strings.

**03 - Search Exploit-DB / Searchsploit**
```
searchsploit "linux kernel 3.13"
searchsploit -x 37292    # Examine exploit code before running
searchsploit --cve 2021-4034
```
Match kernel and service versions to known CVEs.
Additional resources: Exploit-DB, NVD (nvd.nist.gov), VulnDB, PacketStorm, GitHub PoC repos.

**04 - Evaluate Exploit Reliability**
Read the exploit notes, rank, and tested platforms. Check the kernel patch level
and compile flags - a patch-level mismatch is the difference between root and a
crashed process.

**05 - Stage and Test in Lab First**
Never run unreviewed exploit code directly on a live target.

> **Operator Takeaway:** CVE number alone is not enough. Check the target kernel
> patch level and compile flags - a patch-level mismatch is the difference between
> root and a crashed process.

---

### Solaris vs Linux - What Differs on an Engagement

| Oracle Solaris | Linux |
|---|---|
| Legacy services enabled by default (rusers, rwho, finger, rsh, rlogin) | Legacy services disabled by default - must be explicitly enabled |
| SMTP VRFY/EXPN frequently enabled and unfiltered | Kernel exploits: Dirty COW (CVE-2016-5195), PwnKit (CVE-2021-4034), Dirty Pipe (CVE-2022-0847) |
| Solaris-specific kernel and RPC exploits on Exploit-DB | apt/yum show installed vs available - gap = attack surface |
| /etc/shadow may use crypt(3) DES on older Solaris | /etc/shadow uses SHA-512 ($6$) or yescrypt ($y$) on modern distros |

> **Identify the exact OS first. The exploit pool changes completely.**

---

### Remote Exploit to Root - The Chain

1. **Enumerate** - OS, kernel, running services, daemon versions
2. **Research** - searchsploit / Exploit-DB match to version
3. **Lab Test** - Verify in controlled environment before engagement use
4. **Exploit** - Remote exploit code to initial foothold or direct root
5. **Escalate** - Local privilege escalation if initial access is unprivileged

> **Operator Takeaway:** On the Syntex Solutions engagement, document every step
> of the chain with timestamps and evidence references. An undocumented root shell
> is professionally worthless.

---

### Post-Exploitation Workflow

**01 - Exfiltrate Password Hashes**
```
cat /etc/shadow               # Requires root
unshadow /etc/passwd /etc/shadow > hashes.txt
```

**02 - Crack Offline**
```
john --wordlist=rockyou.txt hashes.txt
hashcat -m 1800 hashes.txt wordlist.txt    # -m 1800 = SHA-512 ($6$)
```
John the Ripper or Hashcat - never crack on target. Protect client data.

**03 - Check Patch Levels**
```
uname -a
uname -r
rpm -qa --last | head -20
dpkg -l | grep -i "linux-image"
```

**04 - Derive Missing Patches**
Cross-reference installed packages against CVE feeds to identify unpatched risk.

**05 - Reversion**
Remove dropped files, restore config changes, kill implanted processes.

> **Operator Takeaway:** Reversion is not optional. The CREST CPSA syllabus
> explicitly requires it. Document the pre-engagement state and confirm
> restoration before scope close.
""")

LESSON_F3 = text_item("""\
## F3 - FTP

FTP (File Transfer Protocol) runs on port 21 and is one of the most commonly
misconfigured services on legacy Linux infrastructure. The CREST CPSA syllabus
requires testers to assess access control weaknesses, anonymous access exposure,
and write permission risks.

---

### Identification

```
nmap -sV -p 21 10.10.10.0/24
nc -vn 10.10.10.50 21              # Grab banner
ftp 10.10.10.50
# At prompt: try anonymous / anonymous
```

**Nmap script checks**
```
nmap -p 21 --script ftp-anon 10.10.10.50
nmap -p 21 --script ftp-syst 10.10.10.50
```

---

### Anonymous Access - What to Do With It

When anonymous FTP is open, your investigation follows three steps:

**List Directory Contents**
Browse for config files, backups, credentials, and scripts. Anything left in
the FTP root was put there by someone. It is all intelligence.

**Check for Write Access**
```
ftp> put testfile.txt
```
PUT a test file. Write access to the web root is a critical finding. Immediately
document with a before/after directory listing.

**Pivot to Web**
If the FTP root overlaps with the web root (`/var/www`), a webshell upload
becomes achievable. Verify the overlap first before escalating severity.

---

### FTP Write Access - Risk Classification

| Risk | What It Enables |
|------|----------------|
| **Webshell Upload** | Write to `/var/www` leads to code execution via HTTP |
| **Cron Job Hijack** | Write to a script called by root cron leads to privilege escalation |
| **Configuration Replacement** | Overwrite daemon configs to change service behaviour |
| **FTP Bounce Attack** | Use the PORT command to proxy through the FTP server to scan internal hosts |

> **Operator Takeaway:** Anonymous FTP with write access to a web root is a
> Critical finding. Document with directory listing, PUT test, and HTTP request
> demonstrating access - before and after screenshots.
""")

LESSON_F4 = text_item("""\
## F4 - Sendmail and SMTP

SMTP (Simple Mail Transfer Protocol) runs on port 25. The CREST CPSA syllabus
covers two distinct attack surfaces: username discovery via VRFY/EXPN commands,
and mail relaying abuse where an open relay can be used for phishing or
internal spoofing.

---

### SMTP VRFY and EXPN - Username Discovery

**Manual Enumeration via Telnet**
```
telnet 10.10.10.60 25
220 mail.syntex.local ESMTP Sendmail 8.9.3

HELO attacker
250 mail.syntex.local Hello [10.10.10.5]

VRFY root
250 Super-User <root@syntex.local>

VRFY jsmith
250 John Smith <jsmith@syntex.local>

VRFY nobody
550 nobody... User unknown

EXPN admins
250 root <root@syntex.local>
250 sysadmin <sysadmin@syntex.local>
```

Response codes: 250/251/252 = valid user | 550 = unknown

**Automated - smtp-user-enum**
```
# VRFY mode (default)
smtp-user-enum -M VRFY \
  -U /usr/share/seclists/Usernames/Names/names.txt \
  -t 10.10.10.60

# EXPN mode (mailing list expansion)
smtp-user-enum -M EXPN \
  -U users.txt -t 10.10.10.60

# RCPT TO mode - use when VRFY/EXPN disabled
smtp-user-enum -M RCPT \
  -U users.txt -t 10.10.10.60 \
  -f test@example.com

# Nmap NSE
nmap -p 25 --script smtp-enum-users \
  --script-args smtp-enum-users.methods={VRFY,EXPN,RCPT} \
  10.10.10.60
```

> **Operator Takeaway:** VRFY and EXPN are often disabled on modern Sendmail.
> Always fall back to RCPT TO - it is the hardest to disable without breaking
> mail delivery.

---

### Mail Relaying - Open Relay Testing

An open relay is an SMTP server that will forward mail for any sender to any
recipient, not just its own domain. Historically common; now exploited for
spam and phishing.

**Why It Matters on an Engagement**

- **Phishing Infrastructure:** An attacker can send spoofed mail appearing to
  come from Syntex Solutions' own mail server.
- **Internal Spoof:** Relay mail internally to targets inside the corporate
  network, bypassing external spam filters.
- **Reputation Damage:** If abused post-engagement, the client IP is blacklisted
  with potential business impact beyond the test.

**Testing for Open Relay**
```
telnet 10.10.10.60 25
HELO attacker.external.com
MAIL FROM:<evil@attacker.com>
RCPT TO:<victim@external-domain.com>
DATA
Subject: Relay Test
This is a relay test.
.

# 250 OK = OPEN RELAY (critical finding)
# 550/554 = relay denied (expected behaviour)
```

**Automated check**
```
nmap -p 25 --script smtp-open-relay 10.10.10.60
```

> **Operator Takeaway:** Open relay is typically a **High** severity finding.
> Document the exact SMTP transcript as evidence - message accepted or rejected
> - not just the nmap script output.
""")

LESSON_F5 = text_item("""\
## F5-F9 - Network Services

The Syntex Solutions Linux infrastructure runs several network services that
carry significant attack surface: NFS (file sharing), the Berkeley R* suite
(legacy trust), X11 (display), RPC (portmapper), and SSH. Each has specific
enumeration commands and exploitation paths the CREST CPSA syllabus covers.

---

### NFS - Network File System

**Enumeration**
```
showmount -e 10.10.10.70
# Export list for 10.10.10.70:
# /home      *
# /var/backups  10.10.10.0/24

mkdir /tmp/nfs-mount
mount -t nfs 10.10.10.70:/home /tmp/nfs-mount -nolock
```

**Security Levels**

- **Host-level security:** `/etc/exports` restricts which hosts can mount.
  An asterisk (`*`) means any host can mount - critical misconfiguration.
- **File-level security:** Enforced by UID/GID. The NFS server trusts the
  client's user identity.

**UID/GID Manipulation Attack**
```
# If file owned by UID 1103 on target:
useradd -u 1103 syntex-user
su syntex-user
ls /tmp/nfs-mount/restricted/
# Access granted - UID matched
```

**Root Squashing - Know the Options**

| Option | Behaviour |
|--------|-----------|
| `root_squash` (SECURE) | UID 0 mapped to nobody (UID 65534). Root on client is not root on server. |
| `no_root_squash` (DANGEROUS) | Root on client IS root on server. Create SUID shell. |
| `nosuid` / `noexec` | Prevent execution of SUID binaries and scripts from mounted share. |

> **Operator Takeaway:** `no_root_squash` on a world-mountable NFS share is a
> direct path to root. Check `/etc/exports` on every Linux host in scope.

---

### R* Services - Trust Relationship Abuse

The Berkeley R* suite provides remote login and execution without modern
authentication. All traffic transmitted unencrypted.

| Service | Port | Description |
|---------|------|-------------|
| rlogin | 513 | Remote login - no password if trust configured |
| rsh | 514 | Remote shell execution - no authentication if trusted |
| rexec | 512 | Remote exec - requires username/password |
| rwho / rcp | - | Remote who / remote copy - used for enumeration |

**Trust Configuration Files**
```
# /etc/hosts.equiv - system-wide trust
# Format: [+|-] [hostname] [username]
+                         # ALL hosts trusted (catastrophic)
trusted-host.syntex.local
+web01                    # Trust specific host

# ~/.rhosts - user-level trust
web01.syntex.local jsmith  # jsmith@web01 trusted
+                          # Trust all (if present = critical)
```

**Exploitation**
```
rlogin -l root 10.10.10.80
# If .rhosts or hosts.equiv allows - no password

rsh 10.10.10.80 -l jsmith "id; cat /etc/shadow"
```

> **Operator Takeaway:** A `+` in `/etc/hosts.equiv` trusts every host on the
> internet. If found, this is a Critical finding. The `.rhosts` file is per-user
> - check home directories after initial access.

---

### X11 - X Windows (Port 6000+)

X11 is the display protocol for Unix graphical environments. Misconfigured
X access control allows any host to connect and capture keystrokes or screenshots.

**Access Control Methods**
- `xhost` controls which hosts can connect. `xhost +` disables all access control.
- `xauth` uses a magic cookie stored in `~/.Xauthority` for per-user auth.

**Enumeration and Abuse**
```
nmap -sV -p 6000-6010 10.10.10.0/24
xdpyinfo -display 10.10.10.80:0    # Check access
# If open:
xwd -root -display 10.10.10.80:0   # Screenshot of entire X display
```

---

### RPC - Remote Procedure Call

RPC runs on port 111 (portmapper). Enumerate it first on any host with
port 111 open - it maps the entire RPC service landscape in one query.

```
rpcinfo -p 10.10.10.70
# program vers proto  port  service
# 100000   4   tcp    111   portmapper
# 100003   3   tcp   2049   nfs
# 100005   3   tcp  20048   mountd
# 100024   1   tcp  41259   status

nmap -sV -p 111 --script rpcinfo 10.10.10.70
```

**Common RPC Services to Target**

| RPC Program | Description |
|-------------|-------------|
| NFS (100003) | See NFS section above. Most common RPC target. |
| mountd (100005) | Handles mount requests - identify export list. |
| statd / lockd | Historically vulnerable - check Exploit-DB for version-specific issues. |

---

### SSH - Version Fingerprinting and Auth Mechanisms

**Version Fingerprinting**
```
nc -vn 10.10.10.50 22
# SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7

nmap -sV -p 22 10.10.10.50
nmap -p 22 --script ssh2-enum-algos 10.10.10.50
nmap -p 22 --script ssh-auth-methods \
  --script-args="ssh.user=root" 10.10.10.50
```

**SSHv1 vs SSHv2**

| Version | Status |
|---------|--------|
| SSH Version 1 | Deprecated / Dangerous. Vulnerable to MITM, session hijacking, and protocol-level attacks. If found: Critical. |
| SSH Version 2 | Current standard. Diffie-Hellman key exchange, MAC integrity checks, no shared-secret session ID flaw. |

**Authentication Mechanisms**

| Mechanism | Tester Notes |
|-----------|-------------|
| Password Authentication | Susceptible to brute-force. Check MaxAuthTries, PasswordAuthentication in sshd_config. |
| Public Key Authentication | Check `~/.ssh/authorized_keys` - may contain attacker-controllable keys post-compromise. |
| Keyboard-Interactive | Used for PAM, OTP. May fall back to password depending on PAM config. |
| GSSAPI / Kerberos | Domain-integrated SSH. Previously compromised Kerberos tickets may apply. |

> **Operator Takeaway:** SSHv1 anywhere on the Syntex Solutions estate is a
> standalone Critical. Banner grab every SSH port - version is exposed
> pre-authentication, no credentials required.
""")

LESSON_F6 = text_item("""\
## F6 - Post-Exploitation and Reporting

The final phase of the Linux assessment covers three mandatory activities:
password hash extraction and offline cracking, patch-level assessment, and
full reversion of the target systems. The section closes with the CREST CPSA
reporting standard for Linux findings.

---

### Password Hash Extraction and Offline Cracking

**Hash Extraction - Linux**
```
# Requires root / sudo
cat /etc/shadow
# jsmith:$6$rounds=5000$salt$hash...:19200:0:99999:7:::
# root:$6$rounds=5000$...

# Combine passwd + shadow for John
unshadow /etc/passwd /etc/shadow > combined.txt

# Identify hash format
hashid '$6$rounds=5000$...'
# SHA-512 crypt = hashcat mode 1800
```

**Hash Types - Know These for CPSA**

| Format | Algorithm | Hashcat Mode |
|--------|-----------|-------------|
| `$1$` | MD5 crypt | 500 (legacy Linux) |
| `$5$` | SHA-256 crypt | 7400 |
| `$6$` | SHA-512 crypt | 1800 (most common modern Linux) |

**Offline Cracking - Analysis Host Only**
```
# John the Ripper
john --wordlist=/usr/share/wordlists/rockyou.txt combined.txt
john --rules combined.txt    # With mangling rules
john --show combined.txt     # Display cracked

# Hashcat
hashcat -m 1800 hashes.txt /usr/share/wordlists/rockyou.txt
hashcat -m 1800 hashes.txt /usr/share/wordlists/rockyou.txt -r best64.rule
hashcat -m 1800 --show hashes.txt
```

> **Operator Takeaway:** Never crack hashes on the target system. Copy
> `/etc/shadow` to your analysis host via documented, auditable transfer.
> Log the hash file itself as evidence - it IS the finding.

---

### Patch Assessment and Reversion

**Identifying Missing Patches**
```
# Kernel version
uname -r
uname -a

# Debian / Ubuntu
dpkg -l | grep "linux-image"
apt list --upgradable 2>/dev/null

# RHEL / CentOS
rpm -qa --last | head -30
yum check-update 2>/dev/null
```
Cross-reference against nvd.nist.gov, ubuntu.com/security/cves, or
access.redhat.com/security to identify CVEs with available patches.

> **Operator Takeaway:** The patch-level delta between installed and available
> IS the finding. A kernel 6 months behind its stable release is not an
> assumption of risk - it is a documented vulnerability window.

**Reversion - Why and How**

| Step | Action |
|------|--------|
| 01 - Document pre-engagement state | Screenshot/log all files you plan to touch before touching them |
| 02 - Remove all dropped artifacts | Exploits, payloads, shells, test files, listening processes |
| 03 - Restore modified configs | Return any changed configuration files to original state |
| 04 - Kill all implanted processes | No persistent backdoors left running after scope close |
| 05 - Confirm and document | Record reversion steps with timestamps - this goes in the report |

---

### What Goes in the CPSA Report

For each Linux finding, document six elements:

| Element | Example |
|---------|---------|
| **1 - Title / Summary** | "NFS no_root_squash on 10.10.10.70 - Direct Root Access" |
| **2 - Evidence** | /etc/exports content, mount commands, UID manipulation steps with output |
| **3 - Technical Analysis** | Why the misconfiguration is exploitable and what the attack path is |
| **4 - Impact / Risk** | Confidentiality, integrity, availability - specific to Syntex Solutions data |
| **5 - Recommendation** | Specific, actionable remediation - not "apply patches" |
| **6 - Reversion Confirmation** | Timestamp and description of restored state |

**Module F Reporting Checklist**

- User enumeration evidence (raw output from rusers, finger, SMTP VRFY - timestamped)
- Exploit chain documented (every command, every step, evidence reference per action)
- Hashes logged as evidence (hash file stored securely - not in version control)
- Patch delta documented (installed vs available versions, specific CVEs identified)
- Reversion confirmed (written record of what was placed, what was removed)

> **Operator Takeaway:** The CPSA exam tests whether you understand what to look
> for and why. The report tests whether you found it and whether you can
> communicate impact. Both matter.
""")

KC_ITEMS = [
    text_item("""\
## Module F - Knowledge Check

Test your understanding of Linux/Unix Security Assessment before moving to the labs.
Answer each question, then check your reasoning against the explanations below.

---

### Q1 - SMTP Fallback

VRFY and EXPN are disabled on a target's Sendmail server. Which enumeration
method should you fall back to?

A) Banner grabbing only
B) RCPT TO mode with smtp-user-enum
C) Skip SMTP enumeration entirely
D) Connect directly to port 993

**Answer: B**

RCPT TO works by attempting to address mail to each username. The server must
accept or reject the recipient for mail to function at all - this makes RCPT TO
nearly impossible to disable without breaking mail delivery. It is the most
reliable fallback when VRFY and EXPN are hardened.

---

### Q2 - NFS no_root_squash

You mount an NFS share and find it is exported with `no_root_squash`. What
can you do as root on your attacker machine?

A) Read files owned by UID 0 only
B) Write files but not execute them
C) Act as root on the NFS server's filesystem
D) Nothing - the share is still protected by file permissions

**Answer: C**

With `no_root_squash`, the NFS server trusts your UID 0 as root. You can read
`/etc/shadow`, create SUID binaries, and modify any file on the export. This is
a direct path to root-level access on the remote host and is classified as Critical.

---

### Q3 - SSH Version Finding

During a banner grab you see: `SSH-1.99-OpenSSH_3.9p1`. What severity do you
assign and why?

A) Informational - older SSH versions are still functional
B) Low - version is old but not exploitable without credentials
C) Critical - SSHv1 support is a standalone critical finding
D) Medium - document and recommend upgrade at next maintenance window

**Answer: C**

SSH-1.99 means the server supports both SSHv1 and SSHv2. SSHv1 is vulnerable
to MITM attacks, session hijacking, and protocol-level cryptographic weaknesses.
The CREST CPSA syllabus treats SSHv1 anywhere on a production network as a
standalone Critical regardless of whether active exploitation is attempted.

---

### Q4 - Hash Cracking Location

After gaining root on SYNTEX-LNX01 you extract `/etc/shadow`. Where do you
crack the hashes?

A) On SYNTEX-LNX01 using John the Ripper
B) On SYNTEX-WIN01 to spread compute load
C) On your analysis host only, never on the target
D) Upload to an online cracking service for speed

**Answer: C**

Hash cracking must happen on your analysis host only. Running John or Hashcat
on the target consumes CPU, generates process noise, and risks alerting defenders.
Uploading client password hashes to a third-party service violates professional
standards and likely breaches engagement rules of engagement.

---

### Q5 - Reversion Evidence

Which of the following is NOT sufficient as reversion confirmation in a CPSA report?

A) Screenshot of the original `/etc/exports` taken before modification
B) A timestamped log showing the test file was removed from the FTP root
C) A verbal assurance from the tester that all changes were reversed
D) Before/after directory listing showing the dropped binary was removed

**Answer: C**

Verbal assurance has no evidentiary value. The CREST CPSA standard requires
documented, timestamped confirmation of reversion. Every file dropped, config
changed, or process started must have a corresponding removal log with timestamps.
This documentation goes directly into the report.

---

### Q6 - /etc/hosts.equiv Misconfiguration

You find `/etc/hosts.equiv` on SYNTEX-LNX01 containing a single `+` character.
What does this mean?

A) All local users are trusted for passwordless login
B) Every host on the internet is trusted for passwordless login as any user
C) Only hosts in the syntex.local domain are trusted
D) The file is empty and has no effect

**Answer: B**

A lone `+` in `/etc/hosts.equiv` grants every host on the internet the ability
to log in without a password. This is a Critical finding. Combined with a
username list from rusers or finger, it allows immediate root-level access from
any host on the network without credentials.
"""),
]

# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------

def main():
    print("=" * 60)
    print("CourseStack Module F Theory Push - v1")
    print(f"Course: {COURSE_ID}")
    print("=" * 60)
    print()

    # Create chapter
    print("Creating chapter: Module 06 - Linux / Unix Security Assessment")
    chapter_id = create_chapter("Module 06 - Linux / Unix Security Assessment")
    time.sleep(1)

    # Theory lessons
    lessons = [
        ("F-01  F1: User Enumeration",       [LESSON_F1]),
        ("F-02  F2: Unix Vulnerabilities",   [LESSON_F2]),
        ("F-03  F3: FTP",                    [LESSON_F3]),
        ("F-04  F4: Sendmail and SMTP",      [LESSON_F4]),
        ("F-05  F5-F9: Network Services",    [LESSON_F5]),
        ("F-06  F6: Post-Exploitation and Reporting", [LESSON_F6]),
        ("F-KC  Module F Knowledge Check",   KC_ITEMS),
    ]

    print()
    for name, items in lessons:
        make_lesson(name, chapter_id, items)

    print()
    print("=" * 60)
    print("All Module F theory lessons pushed successfully.")
    print(f"Chapter ID: {chapter_id}")
    print("=" * 60)


if __name__ == "__main__":
    main()

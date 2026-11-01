"""
coursestack_push_module_d_theory_v2.py
---------------------------------------
Pushes Module D theory lessons + knowledge check to CourseStack.
v2 - fixes API field names (name/type instead of title, type required)
     hardcodes chapter ID to avoid chapter lookup issues

Course: b9d920c3-4a8e-4227-af24-3c5f32fc7350
Chapter ID: 7d68c2cc-003d-4cde-90f6-b780ac86660e  (Module 04 - Networking Equipment)
"""

import requests
import uuid
import time

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------
API_KEY    = "sk_5e9fde21e45324530a735286f8e28bcecf3e9df298ab37ec016833ed57c4f2e52b215010e457e6f3de80c070d3161ff5"
BASE_URL   = "https://app.coursestack.com"
COURSE_ID  = "b9d920c3-4a8e-4227-af24-3c5f32fc7350"
CHAPTER_ID = "7d68c2cc-003d-4cde-90f6-b780ac86660e"

session = requests.Session()
session.auth = (API_KEY, "")
session.headers.update({"Content-Type": "application/json"})

# -----------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------

def create_lesson(name):
    payload = {"name": name, "type": "lesson", "chapter_id": CHAPTER_ID}
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
    return {"type": "text", "id": str(uuid.uuid4()), "content": markdown_text}

def make_lesson(name, items):
    print(f"  Creating: {name}")
    lesson_id = create_lesson(name)
    time.sleep(0.5)
    push_lesson_content(lesson_id, items)
    time.sleep(0.5)
    print(f"    OK -> {lesson_id}")

# -----------------------------------------------------------------------
# LESSONS
# -----------------------------------------------------------------------

LESSONS = [

("D-01  Management Protocols - Risk Overview", [text_item("""# Management Protocols - Risk Overview

Networking equipment (routers, switches, firewalls) is managed remotely using a range of protocols. Many of these protocols were designed before security was a priority, making them dangerous if left at default settings.

## Protocol Risk Table

| Protocol | Port | Risk | Attack Surface |
|---|---|---|---|
| Telnet | TCP 23 | **CRITICAL** | All traffic sent in cleartext. Passwords captured with Wireshark or tcpdump. |
| SNMP v1/v2c | UDP 161/162 | **HIGH** | Community strings transmitted in cleartext. Default strings: `public` (read-only) and `private` (read-write). |
| SNMP v3 | UDP 161/162 | LOW | Authentication + encryption. Still audit cipher and auth configuration. |
| SSH v1 | TCP 22 | **HIGH** | Protocol-level weaknesses. Disable, use SSH v2 only. |
| SSH v2 | TCP 22 | LOW | Audit weak ciphers, password auth vs key auth. |
| TFTP | UDP 69 | **HIGH** | No authentication. May expose device configs or allow firmware upload. |
| NTP | UDP 123 | MEDIUM | Amplification DDoS, time manipulation. |
| HTTP (mgmt) | TCP 80 | **HIGH** | Management credentials sent in cleartext. HTTPS only. |

## Key Takeaway

Before testing any network device, enumerate which management protocols are running. Protocols rated HIGH or CRITICAL are almost always exploitable without needing to touch application-layer vulnerabilities.
""")]),

("D-02  SNMP - The Attacker's View", [text_item("""# SNMP - The Attacker's View

SNMP (Simple Network Management Protocol) can expose an entire device configuration: routing tables, interfaces, ARP cache, running processes. The condition is simple - the community string must be known.

**Default community strings to always test:** `public` (read-only) and `private` (read-write, critical if available).

## Attack Commands

**Discover SNMP on a network:**
```
nmap -sU -p 161 --script snmp-info 192.168.1.0/24
```

**Walk the entire MIB tree (dump all SNMP data):**
```
snmpwalk -v2c -c public 192.168.1.1
```

**Get specific OIDs:**
```
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.5.0
```

**Brute force community strings:**
```
onesixtyone -c /usr/share/wordlists/snmp.txt 192.168.1.1
```

## What You Can Retrieve

| OID Branch | Data |
|---|---|
| `1.3.6.1.2.1.1` | System info (hostname, OS, uptime) |
| `1.3.6.1.2.1.2` | Interface list and MAC addresses |
| `1.3.6.1.2.1.4.20` | IP address table |
| `1.3.6.1.2.1.11` | SNMP statistics |

## Remember

> SNMPv1/v2c = community strings in cleartext.
> SNMPv3 = encrypted and authenticated - still audit the configuration.
""")]),

("D-03  Packet Capture Analysis - Wireshark", [text_item("""# Packet Capture Analysis - Wireshark

Wireshark is the primary tool for packet capture and traffic analysis during network assessments. Understanding the two filter types is essential before you start any capture.

## Two Filter Types

| Filter Type | When Applied | Syntax | Example |
|---|---|---|---|
| Capture filter | During capture - limits what is recorded | BPF syntax | `tcp port 80` |
| Display filter | After capture - filters the view only | Wireshark syntax | `http.request.method == "POST"` |

> Capture filters reduce file size. Display filters let you analyse a full capture flexibly.

## Essential Wireshark Display Filters

| Filter | What It Shows |
|---|---|
| `http` | All HTTP traffic |
| `http.request.method == "POST"` | POST requests - look for credentials |
| `tcp.port == 445` | SMB traffic |
| `dns` | All DNS queries and responses |
| `ftp` | FTP control channel (cleartext credentials) |
| `telnet` | Entire Telnet session (all cleartext) |
| `arp` | ARP traffic - spot ARP poisoning |
| `smtp` | Email traffic |

## Practical Workflow

1. Start Wireshark on the correct interface
2. Apply a capture filter if you only want specific traffic (e.g. `host 192.168.1.50`)
3. Trigger the target action (login, file transfer, etc.)
4. Stop capture
5. Apply display filters to isolate credentials or interesting traffic
6. Use **Follow TCP Stream** to reconstruct the full conversation
""")]),

("D-04  Wireshark Core Techniques & tcpdump", [text_item("""# Wireshark Core Techniques & tcpdump

## Three Essential Wireshark Techniques

### 1. Follow TCP Stream
Right-click any packet, choose **Follow > TCP Stream**. This reconstructs the full application-layer conversation. You can read HTTP sessions, FTP credentials, and Telnet sessions in plain text.

### 2. Statistics > Protocol Hierarchy
Gives an overview of every protocol in the capture. Instantly shows whether HTTP, FTP, or Telnet (cleartext protocols) are in use - critical for a quick assessment of what is running on the network.

### 3. Statistics > Conversations
Shows all communication pairs and byte counts. Identifies the most active hosts quickly - useful for spotting data exfiltration or unusual lateral movement.

## tcpdump - Command Line Capture

When you do not have a GUI or are working on a Linux target, `tcpdump` is your tool.

**Capture all traffic on eth0:**
```
tcpdump -i eth0 -w capture.pcap
```

**Capture traffic to/from a specific host:**
```
tcpdump -i eth0 host 192.168.1.100 -w host.pcap
```

**Capture only HTTP traffic:**
```
tcpdump -i eth0 tcp port 80 -w http.pcap
```

**Read a saved pcap file:**
```
tcpdump -r capture.pcap
```

> Capture with tcpdump on a remote host, transfer the .pcap file to your machine, then analyse in Wireshark for the best of both tools.
""")]),

("D-05  ARP Spoofing - Layer 2 MITM", [text_item("""# ARP Spoofing - Layer 2 MITM

ARP (Address Resolution Protocol) maps IP addresses to MAC addresses on a local network segment. **ARP has no authentication** - anyone can send ARP replies claiming any IP/MAC mapping.

## How an ARP Spoofing Attack Works

An attacker positions themselves between a victim and the gateway by sending two streams of forged ARP replies simultaneously.

| Step | Action | ARP Reply Sent |
|---|---|---|
| 1. Poison victim | Tell victim that gateway IP is at attacker MAC | "Gateway (192.168.1.1) is at MY MAC" |
| 2. Poison gateway | Tell gateway that victim IP is at attacker MAC | "Victim (192.168.1.50) is at MY MAC" |
| 3. MITM achieved | All victim traffic flows through the attacker | Attacker forwards packets to maintain connectivity |

## Commands

**Enable IP forwarding (so traffic passes through):**
```
echo 1 > /proc/sys/net/ipv4/ip_forward
```

**Poison victim's ARP cache:**
```
arpspoof -i eth0 -t 192.168.1.50 192.168.1.1
```

**Poison gateway's ARP cache:**
```
arpspoof -i eth0 -t 192.168.1.1 192.168.1.50
```

Run both arpspoof commands simultaneously in separate terminals.

## What You Can Intercept

Once positioned as MITM, combine with Wireshark or tcpdump to capture:
- HTTP credentials
- Telnet sessions
- FTP credentials
- SMB authentication hashes (pass to Responder)

## Defence

**Dynamic ARP Inspection (DAI)** on managed switches validates ARP packets against the DHCP snooping binding table, dropping spoofed ARP replies.
""")]),

("D-06  DHCP Starvation & STP Root Bridge Attack", [text_item("""# DHCP Starvation & STP Root Bridge Attack

## DHCP Starvation

An attacker sends thousands of DHCP DISCOVER requests with spoofed source MAC addresses, exhausting the DHCP server's IP address pool. Legitimate clients then cannot obtain addresses - a network Denial of Service.

**Tool:** `dhcpig`, `Yersinia`

**Defence:** DHCP snooping on switch ports limits DHCP requests per port.

## DHCP Spoofing (Rogue DHCP)

After exhausting the pool with starvation, the attacker runs a rogue DHCP server that responds first to new DISCOVER requests. The attacker sets themselves as the default gateway and DNS server, achieving full MITM on all new clients.

**Tool:** `Yersinia`

**Defence:** DHCP snooping designates trusted ports (only those connected to real DHCP servers) and drops offers from untrusted ports.

## STP Root Bridge Attack

Spanning Tree Protocol (STP) prevents loops by electing a **root bridge** based on the lowest bridge priority. An attacker injects Bridge Protocol Data Units (BPDUs) with **priority 0**, causing all switches to elect the attacker's host as root bridge. All traffic then flows through the attacker.

**Tool:** `Yersinia`

```
yersinia -G
```

**Defences:**

| Defence | Placement | Effect |
|---|---|---|
| BPDU Guard | Access ports (endpoints) | Shuts down port if it receives any BPDU |
| Root Guard | Uplinks / distribution ports | Prevents port from becoming root port |

## Protocol Attacks Quick Reference

| Protocol | Attack | Tool | Defence |
|---|---|---|---|
| ARP | ARP spoofing / poisoning (MITM) | arpspoof, Ettercap, Bettercap | Dynamic ARP Inspection (DAI) |
| DHCP | Starvation (DoS) / Rogue server | dhcpig, Yersinia | DHCP snooping |
| STP | Root bridge election attack | Yersinia | BPDU Guard, Root Guard |
""")]),

("D-07  VoIP & Wireless Security", [text_item("""# VoIP & Wireless Security

## VoIP / SIP Attacks

SIP (Session Initiation Protocol) is the signalling protocol behind most enterprise VoIP. It runs over UDP/TCP port 5060. Without authentication or encryption, SIP is highly vulnerable.

| Attack | Tool | Description |
|---|---|---|
| SIP enumeration | `svmap` | Discover SIP devices on network |
| Extension enumeration | `svwar` | Enumerate valid extensions |
| Credential brute force | `svcrack` | Brute force SIP credentials |
| RTP eavesdropping | Wireshark | Capture unencrypted voice streams |

**SIPvicious suite commands:**
```
svmap 192.168.1.0/24
svwar -e100-300 192.168.1.100
svcrack -u100 192.168.1.100
```

**Defence:** SRTP (encrypted voice), SIP authentication, Session Border Controller (SBC)

## 802.11 Wireless Attacks

| Attack | Tool | Target |
|---|---|---|
| Deauthentication | `aireplay-ng` | Force client disconnect, capture 4-way handshake |
| WPA2 handshake crack | `aircrack-ng` | Offline dictionary attack against captured handshake |
| PMKID attack | `hcxdumptool` | Crack WPA2 without client present |
| Evil Twin / Rogue AP | `hostapd-wpe` | Capture client credentials |
| WPS PIN brute force | `reaver`, `bully` | Max ~11,000 tries against WPS |

**Capturing a WPA2 handshake:**
```
airmon-ng start wlan0
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon
aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF wlan0mon
aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap
```

**Defence:** WPA3, 802.11w (PMF - Protected Management Frames), WIDS (Wireless Intrusion Detection)
""")]),

("D-KC  Module D - Knowledge Check", [text_item("""# Module D - Knowledge Check

Test your understanding of networking equipment security.

---

**Question 1 - SNMP Default Community String**

An SNMP v2c service is running on a network device. The administrator has not changed the default configuration. What is the read-only community string?

> **Answer:** `public`
>
> The read-only default is `public`. The read-write default is `private`. Always test both. If `private` is accessible, you can write to the device MIB - potentially modifying routing tables or interface configurations.

---

**Question 2 - Gratuitous ARP Attack**

An attacker sends gratuitous ARP replies continuously, mapping the gateway IP address to their own MAC address. What attack is this?

> **Answer:** ARP cache poisoning / ARP spoofing - Layer 2 MITM
>
> Because ARP has no authentication, any host can claim any IP/MAC mapping. Once the victim's ARP cache is poisoned, all traffic intended for the gateway passes through the attacker.

---

**Question 3 - Wireshark POST Filter**

You have captured network traffic and want to display only HTTP POST requests in Wireshark. What display filter do you apply?

> **Answer:** `http.request.method == "POST"`
>
> Remember: this is a display filter (Wireshark syntax), not a capture filter (BPF syntax). It works on a saved pcap file and does not affect what was recorded.

---

**Question 4 - STP Root Bridge Defence**

An attacker is sending BPDUs with priority 0 from a host connected to an access switch port, causing it to win the root bridge election. What switch feature stops this?

> **Answer:** BPDU Guard on the access port
>
> BPDU Guard shuts down any port that receives a BPDU. Because end-user devices should never send BPDUs, enabling it on access ports immediately kills the attack. Root Guard (on uplinks) prevents an existing port from becoming a root port.

---

**Question 5 - Replacing Telnet**

A legacy managed switch uses Telnet for remote management. You have been asked to identify the secure replacement. What protocol should be configured?

> **Answer:** SSH v2
>
> SSH v2 provides encrypted, authenticated remote management. SSH v1 has known protocol-level weaknesses and should be disabled. Once SSH v2 is in place, the Telnet service should be disabled entirely.

---

**Question 6 - DHCP Starvation vs Rogue DHCP**

What is the difference between a DHCP starvation attack and a DHCP spoofing attack?

> **Answer:** Starvation exhausts the IP pool (DoS). Spoofing/Rogue DHCP provides a malicious DHCP response after the pool is exhausted, setting the attacker as the default gateway (MITM). The two attacks are often chained together.

---

**Question 7 - WPA2 Handshake Capture**

You are assessing a WPA2 wireless network. No clients are currently connected. Which tool and technique lets you capture a usable WPA2 handshake without waiting for a client to naturally authenticate?

> **Answer:** `hcxdumptool` using the PMKID attack
>
> The PMKID is broadcast by the access point and can be captured without requiring a client handshake. `hcxdumptool` captures the PMKID, which can then be cracked offline with `hashcat`. If clients are present, `aireplay-ng` deauthentication forces a reconnect that produces the 4-way handshake.
""")]),

]

# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------

def main():
    print("=" * 60)
    print("CourseStack Module D Theory Push - v2")
    print(f"Course:  {COURSE_ID}")
    print(f"Chapter: {CHAPTER_ID}")
    print("=" * 60)
    print()

    for name, items in LESSONS:
        make_lesson(name, items)

    print()
    print("=" * 60)
    print("All Module D lessons created successfully.")
    print("=" * 60)

if __name__ == "__main__":
    main()

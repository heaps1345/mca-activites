#!/usr/bin/env bash
# push-to-coursestack-v1.sh
# Pushes MCA Module B lab HTML files to CourseStack
# Usage: ./push-to-coursestack-v1.sh [--dry-run]
#
# SETUP: Fill in the variables in the CONFIGURATION section below before running.

set -euo pipefail

# ============================================================
# CONFIGURATION - fill these in before running
# ============================================================

COURSESTACK_API_URL="https://your-coursestack-instance/api"   # Base API URL
COURSESTACK_API_KEY=""                                          # Your API key / token
COURSESTACK_COURSE_ID=""                                        # Course ID for CREST CPSA
COURSESTACK_MODULE_ID=""                                        # Module ID for Module B

LAB_DIR="$(cd "$(dirname "$0")/.." && pwd)/cpsa/module-b"      # Path to lab files

# ============================================================
# DO NOT EDIT BELOW THIS LINE
# ============================================================

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[DRY RUN] No files will be uploaded."
fi

# Check dependencies
for cmd in curl jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: $cmd is required but not installed." >&2
    exit 1
  fi
done

# Validate config
if [[ -z "$COURSESTACK_API_KEY" ]]; then
  echo "Error: COURSESTACK_API_KEY is not set. Edit this script and add your API key." >&2
  exit 1
fi
if [[ -z "$COURSESTACK_COURSE_ID" ]]; then
  echo "Error: COURSESTACK_COURSE_ID is not set." >&2
  exit 1
fi

# Labs to push - in order
LABS=(
  "lab-b1a-cli-networking-v1.html"
  "lab-b2a-network-recon-v1.html"
  "lab-b3a-service-enumeration-v1.html"
  "lab-b4a-network-sweeping-v1.html"
  "lab-b4b-route-mapping-v1.html"
  "lab-b4c-port-scanning-v1.html"
  "lab-b5a-tool-output-v1.html"
  "lab-b8a-os-fingerprinting-v1.html"
  "lab-b9a-banner-grabbing-v1.html"
  "lab-b13a-linux-privesc-v1.html"
  "lab-b13b-linux-privesc-nfs-v1.html"
  "lab-b14a-process-socket-enum-v1.html"
  "lab-b14b-windows-privesc-v1.html"
)

echo "======================================"
echo " MCA CourseStack Lab Push"
echo " Course ID : $COURSESTACK_COURSE_ID"
echo " Lab dir   : $LAB_DIR"
echo " Labs      : ${#LABS[@]}"
echo "======================================"
echo ""

PASS=0
FAIL=0
SKIP=0

for LAB in "${LABS[@]}"; do
  FILE="$LAB_DIR/$LAB"

  if [[ ! -f "$FILE" ]]; then
    echo "  [SKIP] $LAB - file not found"
    ((SKIP++)) || true
    continue
  fi

  if $DRY_RUN; then
    echo "  [DRY]  $LAB - would upload $(wc -c < "$FILE") bytes"
    ((PASS++)) || true
    continue
  fi

  echo -n "  [PUSH] $LAB ... "

  HTTP_STATUS=$(curl -s -o /tmp/cs_response.json -w "%{http_code}" \
    -X POST "$COURSESTACK_API_URL/courses/$COURSESTACK_COURSE_ID/labs" \
    -H "Authorization: Bearer $COURSESTACK_API_KEY" \
    -H "Content-Type: multipart/form-data" \
    -F "module_id=$COURSESTACK_MODULE_ID" \
    -F "file=@$FILE;type=text/html" \
    -F "filename=$LAB")

  if [[ "$HTTP_STATUS" == "200" ]] || [[ "$HTTP_STATUS" == "201" ]]; then
    echo "OK ($HTTP_STATUS)"
    ((PASS++)) || true
  else
    echo "FAILED ($HTTP_STATUS)"
    echo "    Response: $(cat /tmp/cs_response.json)"
    ((FAIL++)) || true
  fi
done

echo ""
echo "======================================"
echo " Done: $PASS pushed, $FAIL failed, $SKIP skipped"
echo "======================================"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi

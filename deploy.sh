#!/usr/bin/env bash
# Copy the files in site/ into the web container through the Proxmox host, then check it serves.
# Settings come from config.env next to this script (copy config.example.env; it is gitignored).
set -euo pipefail
cd "$(dirname "$0")"
[ -f config.env ] || { echo "config.env missing: copy config.example.env and fill it in" >&2; exit 1; }
# shellcheck disable=SC1091
source config.env
SSH=${SSH:-ssh}
SCP=${SCP:-scp}
: "${PVE_HOST:?}" "${SITE_CT:?}"
SITE_ROOT=${SITE_ROOT:-/var/www/homelab}

# Every file in site/ (index.html, og.png, ...). stats.json is pushed by the host's timer, not from here.
FILES=(site/*)
"$SSH" -o BatchMode=yes "$PVE_HOST" "mkdir -p /tmp/homelab-site-deploy"
"$SCP" -o BatchMode=yes "${FILES[@]}" "$PVE_HOST:/tmp/homelab-site-deploy/"
"$SSH" -o BatchMode=yes "$PVE_HOST" "cd /tmp/homelab-site-deploy && for f in *; do pct push $SITE_CT \"\$f\" \"$SITE_ROOT/\$f\" --perms 644 || exit 1; done; cd / && rm -rf /tmp/homelab-site-deploy"

if [ -n "${CHECK_CT:-}" ] && [ -n "${SITE_URL_INTERNAL:-}" ]; then
  "$SSH" -o BatchMode=yes "$PVE_HOST" \
    "pct exec $CHECK_CT -- curl -s -o /dev/null -w 'served: HTTP %{http_code}, %{size_download} bytes\n' $SITE_URL_INTERNAL"
fi

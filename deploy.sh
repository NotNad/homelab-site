#!/usr/bin/env bash
# Copy site/index.html into the web container through the Proxmox host, then check it serves.
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

"$SCP" -o BatchMode=yes site/index.html "$PVE_HOST:/tmp/homelab-site-index.html"
"$SSH" -o BatchMode=yes "$PVE_HOST" "pct push $SITE_CT /tmp/homelab-site-index.html $SITE_ROOT/index.html --perms 644 && rm -f /tmp/homelab-site-index.html"

if [ -n "${CHECK_CT:-}" ] && [ -n "${SITE_URL_INTERNAL:-}" ]; then
  "$SSH" -o BatchMode=yes "$PVE_HOST" \
    "pct exec $CHECK_CT -- curl -s -o /dev/null -w 'served: HTTP %{http_code}, %{size_download} bytes\n' $SITE_URL_INTERNAL"
fi

# Homelab website

The source of **[lab.hyperyder.com](https://lab.hyperyder.com)**, a public tour of my homelab: a segmented network, a Proxmox host sharing one RTX 3090 across five workloads, ZFS storage, nightly backups, and a self-hosted AI agent locked down to least privilege.

The page is served from the lab itself. This repo is how it's built, hosted and kept safe.

## How it's hosted

```
visitor ──HTTPS──▶ Cloudflare ──tunnel (outbound-only)──▶ cloudflared ──HTTP──▶ nginx
                                                          └──────── DMZ VLAN ────────┘
```

- **One static file.** `site/index.html` holds all the HTML, CSS and JavaScript, with no build step and no third-party requests (no CDNs, fonts or analytics). There's no server-side code, database, login or form.
- **No open ports.** The site is published through a Cloudflare Tunnel: the connector dials out, so the router forwards nothing and the home IP stays hidden.
- **Isolated container.** nginx runs in a small unprivileged LXC container (root inside maps to an unprivileged user on the host) on a DMZ VLAN that can't start connections into the internal network. SSH is disabled inside it, and security updates install automatically.
- **Locked-down nginx** ([`nginx/homelab.conf`](nginx/homelab.conf)): GET/HEAD only, no version banner, dotfiles denied. A strict Content Security Policy (`default-src 'none'`) blocks scripts and requests to other sites, and framing and forms are disabled.

## Live stats without a network path

The "Lab right now" strip shows hourly, aggregate numbers: service uptime, guests running, backup streak, media library size, local LLM requests, and the last security patch.

```
Proxmox host (hourly systemd timer)
  ├─ reads Proxmox, the backup task log, Uptime Kuma's database (read-only), Ollama's log
  ├─ writes stats.json
  └─ pct push ──▶ web container   (a file copy through the hypervisor, not the network)
```

The web container never talks to the rest of the lab, and no API or status endpoint is exposed. If the timer stops, the page keeps the last numbers and marks them stale.

What's left out matters as much as what's shown. There's no per-service status, no versions or boot times (they reveal patch level), and no live GPU, game or network activity (it reveals when someone is home).

- [`stats/homelab-site-stats`](stats/homelab-site-stats): the collector (Python, standard library only).
- [`stats/kuma-uptime.js`](stats/kuma-uptime.js): 30-day uptime from Uptime Kuma's SQLite database, opened read-only.
- [`stats/homelab-site-stats.timer`](stats/homelab-site-stats.timer): runs it hourly.
- [`stats/stats.example.json`](stats/stats.example.json): what the page receives.

## Using it

1. Copy `config.example.env` to `config.env` (gitignored) and fill in your container IDs.
2. On the Proxmox host, install the stats pieces:
   ```bash
   install -m 755 stats/homelab-site-stats /usr/local/sbin/
   install -m 644 stats/homelab-site-stats.service stats/homelab-site-stats.timer /etc/systemd/system/
   # Put the stats lines from config.env (SITE_CT onwards) in /etc/homelab-site-stats.conf.
   # If you use Uptime Kuma, copy stats/kuma-uptime.js into its container at /usr/local/lib/site-stats/.
   systemctl daemon-reload && systemctl enable --now homelab-site-stats.timer
   ```
3. Put `nginx/homelab.conf` in the web container and reload nginx.
4. Deploy the page from your workstation with `./deploy.sh`.

Each stat source is optional. Leave its setting empty and the page hides that tile.

## Content rules

The page describes the design, not the map. It has no IPs, subnets, hostnames, port numbers, firewall-rule details, or known weak spots. Keep it that way in any edit.

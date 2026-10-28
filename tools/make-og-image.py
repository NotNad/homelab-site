# Renders site/og.png, the 1200x627 link-preview card. Needs Pillow; font paths are for Windows.
# Usage: python tools/make-og-image.py site/og.png
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 627
BG, SURF, BORDER = "#0d1117", "#151b23", "#2a3441"
TEXT, MUTED, ACCENT = "#e6edf3", "#9aa6b4", "#60a5fa"
ZONES = ["#4ade80", "#60a5fa", "#fb923c", "#c084fc", "#94a3b8"]
F = "C:/Windows/Fonts/"
sans_b = lambda s: ImageFont.truetype(F + "segoeuib.ttf", s)
sans = lambda s: ImageFont.truetype(F + "segoeui.ttf", s)
mono_b = lambda s: ImageFont.truetype(F + "consolab.ttf", s)
mono = lambda s: ImageFont.truetype(F + "consola.ttf", s)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
X = 72

# zone colour bar along the top
seg = W / len(ZONES)
for i, c in enumerate(ZONES):
    d.rectangle([int(i * seg), 0, int((i + 1) * seg), 8], fill=c)

d.text((X, 70), "SELF-HOSTED  ·  BUILT AND RUN AT HOME", font=mono_b(22), fill=ACCENT)
d.text((X, 104), "Dan's Homelab", font=sans_b(84), fill=TEXT)
sub = ["Segmented network, Proxmox virtualisation, one RTX 3090 shared",
       "by AI, media and gaming, ZFS storage, and a hardened AI agent."]
for i, line in enumerate(sub):
    d.text((X, 222 + i * 40), line, font=sans(30), fill=MUTED)

stats = [("22 + 2", "containers + VMs"), ("5", "network zones"), ("1 GPU", "shared by 5 workloads"), ("27 TB", "ZFS storage")]
gap, top, bh = 20, 340, 132
bw = (W - 2 * X - gap * (len(stats) - 1)) / len(stats)
for i, (v, l) in enumerate(stats):
    x0 = X + i * (bw + gap)
    d.rounded_rectangle([x0, top, x0 + bw, top + bh], radius=14, fill=SURF, outline=BORDER, width=2)
    d.text((x0 + 22, top + 20), v, font=mono_b(44), fill=TEXT)
    d.text((x0 + 22, top + 82), l, font=sans(22), fill=MUTED)

# footer
d.ellipse([X, 532, X + 14, 546], fill=ZONES[0])
d.text((X + 26, 524), "Live from the rack", font=sans(24), fill=MUTED)
url = "lab.hyperyder.com"
uw = d.textlength(url, font=mono_b(28))
d.text((W - X - uw, 521), url, font=mono_b(28), fill=ACCENT)

img.save(sys.argv[1], optimize=True)
print("saved", sys.argv[1])

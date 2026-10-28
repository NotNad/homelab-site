# Renders the PNG/ICO favicons from the same shapes as site/favicon.svg. Needs Pillow.
# Usage: python tools/make-favicons.py site
import os, sys
from PIL import Image, ImageDraw

BG, UNIT, EDGE = "#0d1117", "#1d2530", "#3a4656"
LEDS = ["#4ade80", "#60a5fa", "#fb923c"]


def draw(size, ss=8):
    """Draw on a 64-unit grid at size*ss pixels, then downsample for smooth edges."""
    px = size * ss
    k = px / 64
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = lambda *v: [round(x * k) for x in v]
    d.rounded_rectangle(s(0, 0, 64, 64), radius=round(14 * k), fill=BG)
    for y in (11, 26, 41):
        d.rounded_rectangle(s(10, y, 54, y + 12), radius=round(3 * k), fill=UNIT, outline=EDGE, width=max(1, round(2 * k)))
        d.rounded_rectangle(s(16, y + 5, 34, y + 7), radius=round(1 * k), fill=EDGE)
    for y, c in zip((17, 32, 47), LEDS):
        d.ellipse(s(46 - 3.5, y - 3.5, 46 + 3.5, y + 3.5), fill=c)
    return img.resize((size, size), Image.LANCZOS)


out = sys.argv[1]
draw(180).convert("RGB").save(os.path.join(out, "apple-touch-icon.png"), optimize=True)  # iOS: no transparency
draw(32).save(os.path.join(out, "favicon-32.png"), optimize=True)
draw(48).save(os.path.join(out, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
print("wrote apple-touch-icon.png, favicon-32.png, favicon.ico")

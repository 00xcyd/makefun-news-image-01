# THE WORLD — Wednesday 25 November 2026.
#
# Draws this repository's entry.png: a 1024x1024 newspaper-front-page poster
# that sums up one day's world news (25 November 2026) in six reported stories.
# The judge sees only the image bytes, so everything is drawn flat and bold:
# a heavy serif masthead, a large unmistakable date line, a 3x2 grid of
# textless editorial illustrations, and short reported labels under each.
#
# Run:  python3 compose.py   (writes entry.png beside this file)
#
# Style: flat editorial newspaper art. Cream paper, near-black ink, brick red,
# muted blue, gold. Bold outlines, strong silhouettes, no gradients, no
# photographs, no third-party artwork — every mark on the page is drawn here.

from PIL import Image, ImageDraw, ImageFont
import math
import random

W = H = 1024
CREAM = (242, 234, 216)
INK = (22, 22, 22)
RED = (192, 57, 43)
BLUE = (31, 78, 121)
GOLD = (217, 164, 65)
SEA = (152, 170, 192)
NIGHT = (40, 58, 86)
PALE = (206, 214, 223)

FONTS = "/System/Library/Fonts/Supplemental/"


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)


def tracked_text(draw, center_x, y, text, fnt, fill, tracking):
    """Draw text centered at center_x with extra letter spacing; returns height."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = center_x - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def text_centered(draw, center_x, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((center_x - w / 2, y), text, font=fnt, fill=fill)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def ngon(d, cx, cy, rx, ry, n, rot, fill=None, outline=None, width=1):
    pts = []
    for i in range(n):
        a = rot + 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=width)


# ----------------------------------------------------------------------------
# Scene 1 — Trade: stacked containers under an abstract red tariff seal,
# over a faint world map. (US announces a new tariff round on 14 partners.)
def scene_tariffs(im, d):
    w, h = im.size
    # faint continents
    d.polygon([(w*0.06, h*0.16), (w*0.30, h*0.08), (w*0.38, h*0.28), (w*0.24, h*0.44), (w*0.10, h*0.38)], fill=PALE)
    d.polygon([(w*0.24, h*0.46), (w*0.36, h*0.42), (w*0.42, h*0.70), (w*0.30, h*0.92), (w*0.22, h*0.66)], fill=PALE)
    d.polygon([(w*0.46, h*0.12), (w*0.62, h*0.10), (w*0.66, h*0.34), (w*0.52, h*0.46), (w*0.44, h*0.30)], fill=PALE)
    d.polygon([(w*0.48, h*0.48), (w*0.62, h*0.44), (w*0.66, h*0.72), (w*0.52, h*0.90), (w*0.46, h*0.66)], fill=PALE)
    d.polygon([(w*0.70, h*0.14), (w*0.94, h*0.10), (w*0.97, h*0.40), (w*0.80, h*0.46), (w*0.70, h*0.32)], fill=PALE)
    # stacked containers
    box_colors = [BLUE, RED, GOLD, GOLD, BLUE, RED]
    x0, y0, cw, ch = w*0.22, h*0.50, w*0.24, h*0.14
    for i in range(3):
        row_w = 2 if i < 2 else 3
        for j in range(row_w):
            bx = x0 + j * (cw + w*0.02) - (w*0.01 if i == 2 else 0)
            by = y0 + i * (ch + h*0.02)
            rrect(d, [bx, by, bx + cw, by + ch], 4, fill=box_colors[(i*2+j) % 6], outline=INK, width=5)
    # abstract red tariff seal
    cx, cy, s, a = w*0.70, h*0.26, w*0.19, -0.20
    pts = []
    for (px, py) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        rx, ry = math.cos(a)*px - math.sin(a)*py, math.sin(a)*px + math.cos(a)*py
        pts.append((cx + rx*s, cy + ry*s*0.72))
    d.polygon(pts, outline=RED, width=9)
    for k in range(3):
        p0 = (cx - s*0.55 + k*s*0.45, cy - s*0.42), (cx - s*0.35 + k*s*0.45, cy + s*0.34)
        d.line([p0[0], p0[1]], fill=RED, width=9)


# ----------------------------------------------------------------------------
# Scene 2 — Strait of Hormuz: a burning tanker between rocky shores.
def scene_hormuz(im, d):
    w, h = im.size
    horizon = h * 0.58
    d.rectangle([0, horizon, w, h], fill=SEA)
    # rocky shores narrowing the strait
    d.polygon([(0, 0), (w*0.22, 0), (w*0.16, horizon*0.55), (w*0.05, horizon)], fill=INK)
    d.polygon([(w, 0), (w*0.80, 0), (w*0.86, horizon*0.55), (w*0.97, horizon)], fill=INK)
    # waves
    for i in range(5):
        wy = horizon + h*0.07*i + h*0.03
        d.arc([w*0.08*(i % 3), wy, w*0.08*(i % 3) + w*0.30, wy + h*0.04], 200, 340, fill=(120, 138, 160), width=3)
    # tanker, side view
    tx, ty, tw, th = w*0.24, horizon - h*0.11, w*0.52, h*0.10
    d.polygon([(tx, ty), (tx + tw, ty), (tx + tw - w*0.05, ty + th), (tx + w*0.04, ty + th)], fill=INK)
    deck = ty
    d.rectangle([tx + tw*0.62, deck - h*0.16, tx + tw*0.78, deck], fill=CREAM, outline=INK, width=5)
    d.rectangle([tx + tw*0.66, deck - h*0.24, tx + tw*0.74, deck - h*0.16], fill=INK)
    d.line([(tx + tw*0.50, deck), (tx + tw*0.50, deck - h*0.20)], fill=INK, width=4)
    # fire and smoke
    for i in range(3):
        fx = tx + tw*(0.18 + i*0.22)
        ngon(d, fx, deck - h*0.02, w*0.035, h*0.06, 3, -math.pi/2, fill=RED)
        ngon(d, fx, deck - h*0.02, w*0.018, h*0.032, 3, -math.pi/2, fill=GOLD)
    for cx, cy, r in [(tx + tw*0.42, deck - h*0.16, w*0.052), (tx + tw*0.58, deck - h*0.30, w*0.066)]:
        d.ellipse([cx - r, cy - r*0.8, cx + r, cy + r*0.8], fill=(70, 70, 70))


# ----------------------------------------------------------------------------
# Scene 3 — Riyadh at night: a drone reaches the glass tower, smoke rising.
def scene_riyadh(im, d):
    w, h = im.size
    d.rectangle([0, 0, w, h], fill=NIGHT)
    d.ellipse([w*0.08, h*0.10, w*0.16, h*0.18], fill=CREAM)
    d.ellipse([w*0.10, h*0.10, w*0.13, h*0.13], fill=NIGHT)
    tower_x, tower_w = w*0.38, w*0.20
    top, bottom = h*0.08, h*0.94
    d.polygon([(tower_x, bottom), (tower_x + tower_w*0.5, top), (tower_x + tower_w, bottom)], fill=(120, 140, 165), outline=INK, width=5)
    for i in range(9):
        yy = bottom - (bottom - top)*i/9 - h*0.05
        half = tower_w*0.5*(1 - (i/9)*0.92)
        d.line([(tower_x + tower_w*0.5 - half, yy), (tower_x + tower_w*0.5 + half, yy)], fill=(60, 80, 105), width=4)
    for j in range(4):
        xw = tower_x + tower_w*(0.18 + j*0.20)
        d.line([(xw, bottom), (xw + tower_w*0.10*(j-1.5)/1.5, top + h*0.04)], fill=(60, 80, 105), width=3)
    # impact spark and smoke
    sx, sy = tower_x + tower_w*0.72, h*0.34
    ngon(d, sx, sy, w*0.05, w*0.05, 8, 0, fill=RED)
    ngon(d, sx, sy, w*0.024, w*0.024, 8, 0, fill=GOLD)
    pts = [(sx, sy)]
    for k in range(1, 6):
        pts.append((sx + w*0.02*math.sin(k*1.9), sy - h*0.085*k))
    d.line(pts, fill=(150, 150, 150), width=14)
    d.line([(pts[-1][0] - w*0.03, pts[-1][1] + h*0.01), pts[-1], (pts[-1][0] + w*0.03, pts[-1][1] + h*0.01)], fill=(150, 150, 150), width=12)
    # drone silhouette
    dx, dy, ds = w*0.80, h*0.40, w*0.09
    d.line([(dx - ds, dy), (dx + ds, dy)], fill=INK, width=8)
    d.ellipse([dx - ds*0.14, dy - ds*0.28, dx + ds*0.14, dy + ds*0.28], fill=RED, outline=INK, width=4)
    for side in (-1, 1):
        ex = dx + side*ds
        d.line([(ex, dy - ds*0.30), (ex, dy + ds*0.30)], fill=INK, width=6)
        d.ellipse([ex - ds*0.22, dy - ds*0.34, ex + ds*0.22, dy - ds*0.26], outline=INK, width=4)
        d.ellipse([ex - ds*0.22, dy + ds*0.26, ex + ds*0.22, dy + ds*0.34], outline=INK, width=4)


# ----------------------------------------------------------------------------
# Scene 4 — The courtroom: gavel, circuit board, redacted document.
def scene_huawei(im, d):
    w, h = im.size
    d.rectangle([0, h*0.80, w, h], fill=(226, 217, 196))
    # document with redaction bars
    dx, dy, dw, dh = w*0.08, h*0.20, w*0.34, h*0.52
    rrect(d, [dx, dy, dx + dw, dy + dh], 6, fill=CREAM, outline=INK, width=5)
    for i in range(3):
        by = dy + dh*(0.24 + i*0.22)
        d.rectangle([dx + dw*0.12, by, dx + dw*0.88, by + h*0.05], fill=INK)
    # circuit board
    bx, by, bw, bh = w*0.52, h*0.42, w*0.40, h*0.34
    rrect(d, [bx, by, bx + bw, by + bh], 6, fill=BLUE, outline=INK, width=5)
    traces = [(0.12, 0.20, 0.30, 0.20), (0.30, 0.20, 0.30, 0.60), (0.12, 0.70, 0.80, 0.70), (0.55, 0.15, 0.55, 0.70), (0.55, 0.40, 0.88, 0.40)]
    for (x1, y1, x2, y2) in traces:
        d.line([(bx + bw*x1, by + bh*y1), (bx + bw*x2, by + bh*y2)], fill=GOLD, width=4)
    for (cx, cy) in [(0.12, 0.20), (0.30, 0.60), (0.12, 0.70), (0.80, 0.70), (0.55, 0.15), (0.55, 0.70), (0.88, 0.40)]:
        d.ellipse([bx + bw*cx - 7, by + bh*cy - 7, bx + bw*cx + 7, by + bh*cy + 7], fill=GOLD, outline=INK, width=3)
    # gavel, diagonal across the desk
    gx, gy, gl = w*0.18, h*0.88, w*0.62
    a = -0.32
    ex, ey = gx + gl*math.cos(a), gy + gl*math.sin(a)
    d.line([(gx, gy), (ex, ey)], fill=(120, 84, 40), width=16)
    hx, hy = ex, ey
    pa = a + math.pi/2
    hxw, hhw = w*0.11, h*0.06
    pts = [(hx + hxw*math.cos(pa) - hhw*math.sin(pa), hy + hxw*math.sin(pa) + hhw*math.cos(pa)),
           (hx + hxw*math.cos(pa) + hhw*math.sin(pa), hy + hxw*math.sin(pa) - hhw*math.cos(pa)),
           (hx - hxw*math.cos(pa) + hhw*math.sin(pa), hy - hxw*math.sin(pa) - hhw*math.cos(pa)),
           (hx - hxw*math.cos(pa) - hhw*math.sin(pa), hy - hxw*math.sin(pa) + hhw*math.cos(pa))]
    d.polygon(pts, fill=(150, 106, 50), outline=INK, width=5)
    d.ellipse([w*0.24, h*0.90, w*0.24 + w*0.26, h*0.90 + h*0.10], fill=(120, 84, 40), outline=INK, width=5)


# ----------------------------------------------------------------------------
# Scene 5 — Caracas opens the books: oil derrick, falling bond stack.
def scene_venezuela(im, d):
    w, h = im.size
    d.line([(0, h*0.93), (w, h*0.93)], fill=INK, width=4)
    # rough map silhouette
    d.polygon([(w*0.07, h*0.10), (w*0.25, h*0.07), (w*0.31, h*0.22), (w*0.22, h*0.34), (w*0.10, h*0.30), (w*0.05, h*0.20)], fill=GOLD, outline=INK, width=4)
    # derrick lattice
    bx, base_y, top_y = w*0.60, h*0.93, h*0.16
    bw = w*0.16
    d.polygon([(bx - bw, base_y), (bx + bw, base_y), (bx + bw*0.12, top_y), (bx - bw*0.12, top_y)], outline=INK, width=5)
    for i in range(6):
        t = i / 6
        xl = bx - bw*(1 - t) - bw*0.12*t
        xr = bx + bw*(1 - t) + bw*0.12*t
        yy = base_y + (top_y - base_y)*t
        d.line([(xl, yy), (xr, yy)], fill=INK, width=3)
        d.line([(xl, yy), (xr, yy - (base_y - top_y)/6)], fill=INK, width=3)
        d.line([(xr, yy), (xl, yy - (base_y - top_y)/6)], fill=INK, width=3)
    d.line([(bx - bw*0.5, base_y), (bx + bw*0.12, top_y)], fill=INK, width=4)
    d.line([(bx + bw*0.5, base_y), (bx - bw*0.12, top_y)], fill=INK, width=4)
    # falling bond certificates
    for (cx, cy, rot, sealed) in [(w*0.32, h*0.24, 0.5, False), (w*0.44, h*0.40, -0.4, True), (w*0.30, h*0.58, 0.9, False), (w*0.48, h*0.68, -0.9, False)]:
        bw2, bh2 = w*0.16, h*0.11
        pts = []
        for (px, py) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            rx = px*bw2*math.cos(rot) - py*bh2*math.sin(rot)
            ry = px*bw2*math.sin(rot) + py*bh2*math.cos(rot)
            pts.append((cx + rx, cy + ry))
        d.polygon(pts, fill=CREAM, outline=INK, width=4)
        if sealed:
            mx, my = cx, cy
            r = min(bw2, bh2) * 0.5
            d.ellipse([mx - r, my - r, mx + r, my + r], fill=RED, outline=INK, width=3)


# ----------------------------------------------------------------------------
# Scene 6 — A crowded boat on a grey sea, a distant shore.
def scene_rohingya(im, d):
    w, h = im.size
    horizon = h * 0.46
    d.rectangle([0, 0, w, horizon], fill=(214, 218, 224))
    d.rectangle([0, horizon, w, h], fill=SEA)
    d.rectangle([w*0.62, horizon - h*0.045, w, horizon + h*0.02], fill=GOLD, outline=INK, width=4)
    for i in range(6):
        tx = w*0.66 + i*w*0.055
        d.line([(tx, horizon - h*0.045), (tx, horizon - h*0.045 - h*0.055*(0.5 + (i % 2)))], fill=INK, width=3)
    for i in range(5):
        wy = horizon + h*0.09*i + h*0.02
        d.arc([w*0.04 + (i % 3)*w*0.30, wy, w*0.04 + (i % 3)*w*0.30 + w*0.24, wy + h*0.04], 200, 340, fill=(120, 138, 160), width=3)
    # crowded boat
    bx, by, bl, bh = w*0.16, horizon + h*0.20, w*0.58, h*0.10
    d.polygon([(bx, by), (bx + bl, by), (bx + bl*0.92, by + bh), (bx + bl*0.08, by + bh)], fill=INK)
    d.line([(bx + bl*0.06, by - h*0.01), (bx + bl*0.94, by - h*0.01)], fill=GOLD, width=5)
    # figures packed on deck
    n = 9
    for i in range(n):
        fx = bx + bl*0.12 + i * (bl*0.76 / (n - 1))
        fy = by - h*0.008
        hr = h*0.026
        d.ellipse([fx - hr, fy - hr*2.6, fx + hr, fy - hr*0.7], fill=INK)
        d.polygon([(fx - hr*1.15, fy - hr*0.8), (fx + hr*1.15, fy - hr*0.8), (fx + hr*0.9, fy + hr*0.5), (fx - hr*0.9, fy + hr*0.5)], fill=INK)
    # a small bag of belongings
    d.ellipse([bx + bl*0.90, by - h*0.045, bx + bl*0.90 + w*0.05, by - h*0.045 + h*0.05], outline=INK, width=4, fill=CREAM)


# ----------------------------------------------------------------------------
SCENES = [
    (scene_tariffs,  "NEW TARIFF ROUND",   "US targets China, EU, 12 partners"),
    (scene_hormuz,   "TANKERS HIT MINES", "Two ships burn in Strait of Hormuz"),
    (scene_riyadh,   "RIYADH TOWER HIT",  "Second strike on PIF tower; 11 hurt"),
    (scene_huawei,   "HUAWEI CONVICTED",  "US jury finds trade-secret conspiracy"),
    (scene_venezuela, "$237.5BN DEBT",    "Venezuela opens books for restructuring"),
    (scene_rohingya, "ROHINGYA RETURNS",   "Malaysia to send refugees to Myanmar"),
]


def draw_cell_scene(fn):
    """Draw one illustration at 2x, downscale for clean edges, border it."""
    cw, ch = 306, 250
    big = Image.new("RGB", (cw * 2, ch * 2), CREAM)
    d = ImageDraw.Draw(big)
    fn(big, d)
    small = big.resize((cw, ch), Image.LANCZOS)
    dd = ImageDraw.Draw(small)
    dd.rectangle([0, 0, cw - 1, ch - 1], outline=INK, width=2)
    return small


def main():
    poster = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(poster)

    f_kicker = font("Arial Bold.ttf", 15)
    f_mast = font("Georgia Bold.ttf", 58)
    f_date = font("Georgia Bold.ttf", 38)
    f_head = font("Arial Bold.ttf", 27)
    f_sub = font("Arial.ttf", 15)
    f_foot = font("Arial Bold.ttf", 15)
    f_foot2 = font("Arial.ttf", 14)

    # masthead
    tracked_text(d, W / 2, 20, "ONE DAY  ·  SIX STORIES", f_kicker, RED, 4)
    text_centered(d, W / 2, 44, "THE WORLD", f_mast, INK)
    d.line([(70, 130), (W - 70, 130)], fill=INK, width=3)
    d.line([(70, 136), (W - 70, 136)], fill=INK, width=1)
    # the day this page sums up — the second most legible thing on it
    tracked_text(d, W / 2, 148, "WEDNESDAY 25 NOVEMBER 2026", f_date, INK, 3)
    d.line([(70, 200), (W - 70, 200)], fill=INK, width=1)

    # 3 x 2 story grid
    left, top = 36, 212
    cw, ch, gap = 306, 250, 17
    row_h = 314
    for idx, (fn, head, sub) in enumerate(SCENES):
        col, row = idx % 3, idx // 3
        x = left + col * (cw + gap)
        y = top + row * (row_h + 12)
        poster.paste(draw_cell_scene(fn), (x, y))
        text_centered(d, x + cw / 2, y + ch + 10, head, f_head, INK)
        text_centered(d, x + cw / 2, y + ch + 44, sub, f_sub, INK)
    # column rules
    for gx in (left + cw + gap // 2, left + 2 * cw + gap + gap // 2):
        d.line([(gx, top - 4), (gx, top + 2 * (row_h + 12) - 6)], fill=INK, width=1)

    # footer
    d.line([(70, 866), (W - 70, 866)], fill=INK, width=2)
    d.text((78, 884), "25.11.2026", font=f_foot, fill=RED)
    regions = "AMERICAS  ·  EUROPE  ·  MIDDLE EAST  ·  ASIA"
    d.text((W - 78 - d.textlength(regions, font=f_foot2), 886), regions, font=f_foot2, fill=INK)
    fields = "TRADE  ·  SHIPPING  ·  SECURITY  ·  LAW  ·  DEBT  ·  REFUGEES"
    text_centered(d, W / 2, 926, fields, f_foot2, INK)

    # subtle paper grain
    rnd = random.Random(25112026)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for _ in range(2600):
        x, y = rnd.randrange(W), rnd.randrange(H)
        od.point((x, y), fill=(60, 50, 30, rnd.randrange(8, 22)))
    poster = Image.alpha_composite(poster.convert("RGBA"), overlay).convert("RGB")

    poster.save("entry.png", optimize=True)
    print("entry.png written", poster.size)


if __name__ == "__main__":
    main()

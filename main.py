#!/usr/bin/env python3
"""The World in One Page -- 21 November 2026 (candidate B: hero-led).

Draws a one-page newspaper front page summing up the world's news of
Saturday 21 November 2026, and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png).

Deterministic: no network, no randomness, no timestamps in the image.
If Pillow is unavailable, falls back to copying the bundled artwork.png
(byte-identical to what this program draws with Pillow).

Stories (all reported 20-21 November 2026, AP / Reuters / BBC / CNN):
  1. Russian missiles and a drone land in Poland; NATO calls it a
     "grave violation", Poland calls it a deliberate provocation.
  2. S&P 500 falls ~3.7% into correction as AI shares plunge.
  3. World Court finds Myanmar committed genocide against the Rohingya
     -- the first time the ICJ has held a state responsible.
  4. UK and EU sign deals on food trade, carbon markets, youth mobility.
  5. Trump, Xi and Putin's first trilateral summit ends with few
     concrete results.
  6. COP31 climate talks deadlocked over fossil fuels and finance.
  7. Cyclone Akvan slams India's east coast; 300,000 evacuated.
"""

import os
import shutil
import sys

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
NAVY = (22, 40, 63)
NAVY2 = (31, 55, 84)
RED = (179, 39, 30)
RED_LT = (255, 120, 100)
GOLD = (201, 162, 39)
GOLD_LT = (232, 193, 90)
GREY = (90, 90, 86)
WHITE = (255, 255, 255)
BLUE = (43, 96, 158)


def _fonts_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "fonts")


def load_font(name, size):
    """Load a bundled DejaVu font, else a system copy, else default."""
    from PIL import ImageFont

    cands = [
        os.path.join(_fonts_dir(), name),
        os.path.join("/usr/share/fonts/truetype/dejavu", name),
    ]
    for path in cands:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, lines, font, fill, leading=None):
    """Draw lines; returns y after the last line."""
    if leading is None:
        leading = int(font.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def dashed_line(draw, p0, p1, fill, width=2, dash=7, gap=5):
    """Draw a dashed straight line between two points."""
    import math

    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    dx, dy = (x1 - x0) / dist, (y1 - y0) / dist
    pos = 0.0
    while pos < dist:
        end = min(pos + dash, dist)
        draw.line(
            [(x0 + dx * pos, y0 + dy * pos), (x0 + dx * end, y0 + dy * end)],
            fill=fill,
            width=width,
        )
        pos = end + gap


def draw_poland_map(draw, box):
    """Stylised map panel: Poland, three impact sites, NATO jets."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY2, outline=INK, width=2)
    # Simplified Poland silhouette (normalised coords in the box).
    poly = [
        (0.16, 0.30), (0.34, 0.14), (0.52, 0.18), (0.70, 0.10),
        (0.88, 0.22), (0.84, 0.42), (0.92, 0.56), (0.80, 0.72),
        (0.62, 0.88), (0.42, 0.84), (0.26, 0.68), (0.10, 0.48),
    ]
    pts = [(x0 + px * (x1 - x0), y0 + py * (y1 - y0)) for px, py in poly]
    draw.polygon(pts, fill=(74, 116, 158), outline=(220, 225, 230))
    # Ukraine hint, bottom right.
    draw.text((x0 + 0.60 * (x1 - x0), y0 + 0.90 * (y1 - y0)),
              "UKRAINE", font=FONT_SM, fill=(150, 170, 195))
    draw.text((x0 + 0.30 * (x1 - x0), y0 + 0.42 * (y1 - y0)),
              "POLAND", font=FONT_MD, fill=WHITE)
    # Incoming tracks from the south-east.
    sites = [(0.62, 0.55), (0.74, 0.66), (0.52, 0.70)]
    for sx, sy in sites:
        px, py = x0 + sx * (x1 - x0), y0 + sy * (y1 - y0)
        dashed_line(draw, (x1 - 8, y1 - 6), (px, py), (255, 120, 100), 2)
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                     outline=WHITE, width=2)
    draw.text((x0 + 10, y0 + 8), "3 IMPACT SITES", font=FONT_SM,
              fill=GOLD_LT)
    draw.text((x0 + 10, y1 - 26), "NATO JETS SCRAMBLED", font=FONT_SM,
              fill=WHITE)


def draw_market_chart(draw, box):
    """Small red plunging line chart inside a panel box."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(255, 255, 255), outline=(200, 200, 195))
    pts = [
        (0.06, 0.30), (0.16, 0.34), (0.26, 0.28), (0.36, 0.46),
        (0.46, 0.42), (0.56, 0.62), (0.66, 0.58), (0.76, 0.80),
        (0.86, 0.76), (0.95, 0.94),
    ]
    xy = [(x0 + px * (x1 - x0), y0 + py * (y1 - y0)) for px, py in pts]
    draw.line(xy, fill=RED, width=3, joint="curve")
    draw.ellipse([xy[-1][0] - 4, xy[-1][1] - 4, xy[-1][0] + 4, xy[-1][1] + 4],
                 fill=RED)
    label = "S&P 500  -3.7%"
    lw = draw.textlength(label, font=FONT_SM_B)
    draw.rectangle([x0 + 4, y0 + 3, x0 + lw + 12, y0 + 22], fill=WHITE)
    draw.text((x0 + 8, y0 + 4), label, font=FONT_SM_B, fill=RED)


def draw_scales(draw, cx, cy, s, fill):
    """Simple scales-of-justice glyph centred at (cx, cy), size s."""
    draw.line([(cx, cy - s, ), (cx, cy + s)], fill=fill, width=3)
    draw.line([(cx - s, cy - s * 0.55), (cx + s, cy - s * 0.55)],
              fill=fill, width=3)
    for sign in (-1, 1):
        px = cx + sign * s * 0.8
        draw.line([(cx + sign * s * 0.8, cy - s * 0.55), (px, cy)],
                  fill=fill, width=2)
        draw.arc([px - s * 0.32, cy - s * 0.28, px + s * 0.32, cy + s * 0.28],
                 start=0, end=180, fill=fill, width=2)
        draw.line([(px - s * 0.32, cy), (px + s * 0.32, cy)], fill=fill,
                  width=2)
    draw.ellipse([cx - 4, cy - s - 4, cx + 4, cy - s + 4], fill=fill)


def draw_flags_trio(draw, x, y, w, h):
    """US / China / Russia mini flags in a row."""
    fw = (w - 16) // 3
    # USA: stripes + canton.
    draw.rectangle([x, y, x + fw, y + h], fill=WHITE, outline=INK)
    for i in range(7):
        if i % 2 == 0:
            draw.rectangle([x, y + i * h // 7, x + fw,
                            y + (i + 1) * h // 7], fill=RED)
    draw.rectangle([x, y, x + fw * 2 // 5, y + h * 4 // 7], fill=NAVY)
    # China: red field, yellow stars.
    cx = x + fw + 8
    draw.rectangle([cx, y, cx + fw, y + h], fill=(222, 41, 16), outline=INK)
    draw.text((cx + 6, y + 2), "*", font=FONT_MD, fill=(255, 222, 0))
    # Russia: white / blue / red tricolour.
    rx = x + 2 * (fw + 8)
    draw.rectangle([rx, y, rx + fw, y + h // 3], fill=WHITE, outline=INK)
    draw.rectangle([rx, y + h // 3, rx + fw, y + 2 * h // 3], fill=BLUE)
    draw.rectangle([rx, y + 2 * h // 3, rx + fw, y + h], fill=RED)


def draw_eu_uk(draw, x, y, w, h):
    """EU circle-of-stars and a simplified Union Jack, side by side."""
    import math

    fw = (w - 12) // 2
    # EU flag.
    draw.rectangle([x, y, x + fw, y + h], fill=(0, 51, 153), outline=INK)
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        sx = x + fw / 2 + math.cos(a) * fw * 0.30
        sy = y + h / 2 + math.sin(a) * h * 0.30
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    # Union Jack (simplified: navy, white cross, red cross).
    ux = x + fw + 12
    draw.rectangle([ux, y, ux + fw, y + h], fill=NAVY, outline=INK)
    draw.rectangle([ux, y + h // 3, ux + fw, y + 2 * h // 3], fill=WHITE)
    draw.rectangle([ux + fw // 3, y, ux + 2 * fw // 3, y + h], fill=WHITE)
    draw.rectangle([ux, y + h * 11 // 24, ux + fw, y + h * 13 // 24],
                   fill=RED)
    draw.rectangle([ux + fw * 11 // 24, y, ux + fw * 13 // 24, y + h],
                   fill=RED)


def draw_globe(draw, cx, cy, r):
    """Small globe with a red deadlock slash."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 180, 210),
                 outline=NAVY, width=2)
    draw.ellipse([cx - r * 0.55, cy - r * 0.6, cx - r * 0.05, cy - r * 0.1],
                 fill=(90, 160, 90))
    draw.ellipse([cx + r * 0.1, cy + r * 0.15, cx + r * 0.6, cy + r * 0.6],
                 fill=(90, 160, 90))
    draw.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED, width=4)


def draw_cyclone(draw, cx, cy, r, fill):
    """Spiral glyph for the cyclone strip."""
    import math

    for k in range(3):
        pts = []
        for t in range(0, 181, 6):
            a = math.radians(t + k * 40)
            rr = r * (0.25 + 0.75 * t / 180.0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        draw.line(pts, fill=fill, width=3, joint="curve")


def build_image():
    from PIL import Image, ImageDraw

    global FONT_SM, FONT_SM_B, FONT_MD, FONT_BODY, FONT_HEAD, FONT_TITLE
    global FONT_KICK, FONT_DATE, FONT_HEAD_SM

    FONT_SM = load_font("DejaVuSans.ttf", 15)
    FONT_SM_B = load_font("DejaVuSans-Bold.ttf", 16)
    FONT_MD = load_font("DejaVuSans-Bold.ttf", 20)
    FONT_BODY = load_font("DejaVuSans.ttf", 20)
    FONT_HEAD = load_font("DejaVuSerif-Bold.ttf", 34)
    FONT_HEAD_SM = load_font("DejaVuSerif-Bold.ttf", 30)
    FONT_TITLE = load_font("DejaVuSerif-Bold.ttf", 52)
    FONT_KICK = load_font("DejaVuSans-Bold.ttf", 17)
    FONT_DATE = load_font("DejaVuSans-Bold.ttf", 20)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28  # margin

    # ---- Masthead ----
    d.rectangle([0, 0, W, 118], fill=NAVY)
    title = "THE WORLD IN ONE PAGE"
    tw = d.textlength(title, font=FONT_TITLE)
    d.text(((W - tw) / 2, 14), title, font=FONT_TITLE, fill=WHITE)
    d.rectangle([M, 82, W - M, 84], fill=GOLD)
    date_line = "SATURDAY, 21 NOVEMBER 2026  ·  THE DAY'S WORLD NEWS IN ONE IMAGE"
    tw = d.textlength(date_line, font=FONT_DATE)
    d.text(((W - tw) / 2, 90), date_line, font=FONT_DATE, fill=GOLD_LT)

    # ---- Hero: Poland lead, dark band with big map ----
    y = 132
    d.rectangle([M, y, W - M, y + 338], fill=NAVY, outline=INK, width=2)
    draw_poland_map(d, (M + 14, y + 14, 600, y + 324))
    tx = 624
    d.text((tx, y + 22), "LEAD  ·  NATO ON ALERT", font=FONT_KICK,
           fill=RED_LT)
    d.text((tx, y + 52), "RUSSIAN MISSILES", font=FONT_HEAD_SM, fill=WHITE)
    d.text((tx, y + 90), "LAND IN POLAND", font=FONT_HEAD_SM, fill=WHITE)
    deck = ("Two missiles and a suspected drone came down in south-east "
            "Poland during a huge Russian attack on Ukraine. NATO calls it "
            "a \u201cgrave violation\u201d; Warsaw calls it a deliberate "
            "provocation. No one was hurt in Poland.")
    lines = wrap(d, deck, FONT_BODY, 340)
    draw_text_block(d, tx, y + 142, lines, FONT_BODY,
                    (225, 232, 240))

    # ---- Row 1: markets / ICJ / UK-EU ----
    y = 484
    pw, gap = 312, 16
    # Markets
    x = M
    d.rectangle([x, y, x + pw, y + 206], fill=WHITE, outline=INK, width=2)
    d.text((x + 14, y + 12), "MARKETS", font=FONT_KICK, fill=RED)
    d.text((x + 14, y + 40), "WALL ST SLUMPS", font=FONT_HEAD_SM, fill=INK)
    lines = wrap(d, "S&P 500 falls about 3.7% into correction as AI shares "
                 "plunge.", FONT_BODY, pw - 28)
    draw_text_block(d, x + 14, y + 84, lines, FONT_BODY, INK)
    draw_market_chart(d, (x + 14, y + 164, x + pw - 14, y + 192))
    # ICJ
    x = M + pw + gap
    d.rectangle([x, y, x + pw, y + 206], fill=WHITE, outline=INK, width=2)
    d.text((x + 14, y + 12), "JUSTICE  ·  WORLD COURT", font=FONT_KICK,
           fill=RED)
    d.text((x + 14, y + 40), "MYANMAR", font=FONT_HEAD_SM, fill=INK)
    d.text((x + 14, y + 74), "COMMITTED", font=FONT_HEAD_SM, fill=INK)
    d.text((x + 14, y + 108), "GENOCIDE", font=FONT_HEAD_SM, fill=INK)
    lines = wrap(d, "First time the ICJ has held a state responsible.",
                 FONT_BODY, pw - 28)
    draw_text_block(d, x + 14, y + 142, lines, FONT_BODY, INK)
    draw_scales(d, x + pw - 44, y + 52, 22, NAVY)
    # UK-EU
    x = M + 2 * (pw + gap)
    d.rectangle([x, y, x + pw, y + 206], fill=WHITE, outline=INK, width=2)
    d.text((x + 14, y + 12), "DIPLOMACY  ·  BRUSSELS", font=FONT_KICK,
           fill=RED)
    lines = wrap(d, "UK AND EU SIGN NEW DEALS", FONT_MD, pw - 28)
    draw_text_block(d, x + 14, y + 40, lines, FONT_MD, INK)
    draw_eu_uk(d, x + 14, y + 104, pw - 28, 34)
    lines = wrap(d, "Food trade, carbon markets and youth mobility agreed.",
                 FONT_BODY, pw - 28)
    draw_text_block(d, x + 14, y + 152, lines, FONT_BODY, INK)

    # ---- Row 2: summit / COP31 / cyclone ----
    y = 704
    # Summit
    x = M
    d.rectangle([x, y, x + pw, y + 206], fill=WHITE, outline=INK, width=2)
    d.text((x + 14, y + 12), "SUMMIT  ·  SHENZHEN", font=FONT_KICK,
           fill=RED)
    lines = wrap(d, "TRUMP, XI AND PUTIN MEET", FONT_MD, pw - 28)
    draw_text_block(d, x + 14, y + 40, lines, FONT_MD, INK)
    draw_flags_trio(d, x + 14, y + 104, pw - 28, 34)
    lines = wrap(d, "First trilateral summit ends with few concrete results.",
                 FONT_BODY, pw - 28)
    draw_text_block(d, x + 14, y + 152, lines, FONT_BODY, INK)
    # COP31
    x = M + pw + gap
    d.rectangle([x, y, x + pw, y + 206], fill=WHITE, outline=INK, width=2)
    d.text((x + 14, y + 12), "CLIMATE  ·  COP31", font=FONT_KICK, fill=RED)
    lines = wrap(d, "CLIMATE TALKS DEADLOCKED", FONT_MD, pw - 28)
    draw_text_block(d, x + 14, y + 40, lines, FONT_MD, INK)
    draw_globe(d, x + 40, y + 122, 24)
    lines = wrap(d, "Talks stall over fossil fuels and climate finance.",
                 FONT_BODY, 196)
    draw_text_block(d, x + 76, y + 102, lines, FONT_BODY, INK)
    # Cyclone card
    x = M + 2 * (pw + gap)
    d.rectangle([x, y, x + pw, y + 206], fill=BLUE, outline=INK, width=2)
    d.text((x + 14, y + 12), "WEATHER  ·  INDIA", font=FONT_KICK,
           fill=(255, 255, 255))
    lines = wrap(d, "CYCLONE AKVAN SLAMS EAST COAST", FONT_MD, pw - 28)
    draw_text_block(d, x + 14, y + 40, lines, FONT_MD, WHITE)
    draw_cyclone(d, x + 44, y + 122, 24, WHITE)
    lines = wrap(d, "Storm crosses Odisha; 300,000 evacuated.",
                 FONT_BODY, 210)
    draw_text_block(d, x + 76, y + 102, lines, FONT_BODY,
                    (220, 232, 245))

    # ---- Footer ticker ----
    y = 924
    d.rectangle([M, y, W - M, y + 46], fill=NAVY)
    tick = ("ALSO TODAY:  US court voids 2022 spending bill  ·  "
            "Trump: Iran wants a deal  ·  India launches H5N1 vaccine")
    tfont = FONT_SM
    while d.textlength(tick, font=tfont) > W - 2 * M - 16 and tfont.size > 11:
        tfont = load_font("DejaVuSans.ttf", tfont.size - 1)
    tw = d.textlength(tick, font=tfont)
    d.text(((W - tw) / 2, y + 14), tick, font=tfont, fill=WHITE)
    src = "Reported 20\u201321 November 2026  ·  Sources: AP, Reuters, BBC, CNN, Le Monde"
    tw = d.textlength(src, font=FONT_SM)
    d.text(((W - tw) / 2, 984), src, font=FONT_SM, fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        from PIL import Image  # noqa: F401

        img = build_image()
        img.save(out_path, "PNG")
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        bundled = os.path.join(here, "artwork.png")
        if not os.path.exists(bundled):
            sys.stderr.write("Pillow missing and no bundled artwork.png\n")
            raise
        shutil.copyfile(bundled, out_path)


if __name__ == "__main__":
    main()

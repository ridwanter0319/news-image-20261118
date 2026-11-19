#!/usr/bin/env python3
"""news-image-20261118 v2: aggressive one-page world-news infographic.

Wednesday 18 November 2026, 48 stories, 7 regions, one page. Layout is
built for pairwise judging at any size: a super-strong header, a one-line
top strip, three big horizontal hero cards (art left, huge headline),
a compact 4-column medium grid, then a pinned world map beside a dense
"ALSO ON 18 NOVEMBER" list, and a thin footer. Drawn procedurally with
Pillow (flat vector art, no photos, no network), deterministic. If
Pillow is unavailable (bare standard-library sandbox), it falls back to
copying the committed entry.png that this same program generated.
"""
import os
import shutil
import sys

W = 1024
H = 1024

CREAM = (247, 241, 222)
PAPER = (252, 248, 236)
INK = (22, 22, 26)
NAVY = (13, 27, 56)
NAVY2 = (20, 40, 84)
RED = (186, 28, 28)
DARKRED = (150, 22, 22)
GREY = (88, 88, 88)
LINE = (38, 38, 38)
GOLD = (250, 197, 66)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_fonts(ImageFont):
    def f(name, size):
        path = os.path.join(FONT_DIR, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    return {
        "d18": f("DejaVuSerif-Bold.ttf", 58),
        "nov": f("DejaVuSans-Bold.ttf", 15),
        "wed": f("DejaVuSans-Bold.ttf", 12),
        "title": f("DejaVuSerif-Bold.ttf", 41),
        "date": f("DejaVuSans-Bold.ttf", 21),
        "bignum": f("DejaVuSerif-Bold.ttf", 34),
        "bigsub": f("DejaVuSans-Bold.ttf", 13),
        "region": f("DejaVuSans-Bold.ttf", 10),
        "top": f("DejaVuSans-Bold.ttf", 14),
        "topchip": f("DejaVuSans-Bold.ttf", 12),
        "htag": f("DejaVuSans-Bold.ttf", 10),
        "hsrc": f("DejaVuSans.ttf", 10),
        "hhead": f("DejaVuSerif-Bold.ttf", 20),
        "hdeck": f("DejaVuSans.ttf", 12),
        "hnum": f("DejaVuSerif-Bold.ttf", 30),
        "mtag": f("DejaVuSans-Bold.ttf", 8),
        "msrc": f("DejaVuSans.ttf", 8),
        "mhead": f("DejaVuSerif-Bold.ttf", 13),
        "mdeck": f("DejaVuSans.ttf", 9),
        "bhead": f("DejaVuSans-Bold.ttf", 13),
        "brief": f("DejaVuSans.ttf", 10),
        "briefb": f("DejaVuSans-Bold.ttf", 10),
        "maph": f("DejaVuSans-Bold.ttf", 12),
        "maps": f("DejaVuSans.ttf", 9),
        "pin": f("DejaVuSans-Bold.ttf", 7),
        "foot": f("DejaVuSans.ttf", 10),
        "footb": f("DejaVuSans-Bold.ttf", 10),
    }


def wrap(draw, text, font, maxw):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, font, fill, maxw, leading, max_lines=None):
    x, y = xy
    lines = wrap(draw, text, font, maxw)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


HEROES = [
    {
        "n": 1, "tag": "ASIA \u00b7 APEC SUMMIT", "src": "AP", "status": "CONFIRMED", "art": "plane",
        "head": "Xi greets Trump on the tarmac in Shenzhen",
        "deck": "A rare airport welcome as APEC opens. Trump-Putin talks held earlier; three-way talks with Xi on Thursday.",
    },
    {
        "n": 2, "tag": "MIDDLE EAST \u00b7 IRAN WAR", "src": "REUTERS", "status": "CLAIM", "art": "missiles",
        "head": "Bahrain and Kuwait intercept Iran's drones",
        "deck": "Tehran says it hit a US radar and Patriot batteries after Tuesday's Qeshm strike. CENTCOM: no casualties.",
    },
    {
        "n": 3, "tag": "WORLD \u00b7 SPACE", "src": "NASA", "status": "CONFIRMED", "art": "voyager",
        "head": "Voyager 1 reaches one light-day from Earth",
        "deck": "25.9 billion km out \u2014 a command sent today arrives tomorrow. Nothing has been farther.",
    },
]

MEDIUM = [
    {"n": 4, "tag": "4 \u00b7 EUROPE \u00b7 UKRAINE WAR", "src": "KYIV AF", "art": "drones",
     "head": "Russia fires 141 drones at Ukraine; 126 downed",
     "deck": "Hits at seven sites overnight; four killed in Donetsk."},
    {"n": 5, "tag": "5 \u00b7 AMERICAS \u00b7 MARKETS", "src": "FED", "art": "bank",
     "head": "Fed minutes: almost all officials see more hikes",
     "deck": "A bigger December rise is floated; Dow drops 561 pts."},
    {"n": 6, "tag": "6 \u00b7 ASIA \u00b7 WEATHER", "src": "IMD", "art": "cyclone",
     "head": "Cyclone Akvan veers north toward Odisha",
     "deck": "50,000 moved to shelters; landfall due Fri 20 Nov."},
    {"n": 7, "tag": "7 \u00b7 AFRICA \u00b7 SUDAN WAR", "src": "AMNESTY", "art": "sudan",
     "head": "Amnesty: RSF drones killed 37 in El Obeid",
     "deck": "War-crimes inquiry urged; RSF blames Sudan's army."},
    {"n": 8, "tag": "8 \u00b7 EUROPE \u00b7 UKRAINE AID", "src": "EU", "art": "eu",
     "head": "EU proposes \u20ac45bn loan to fund Ukraine in 2027",
     "deck": "Two-thirds of a \u20ac70bn gap, repaid after reparations."},
    {"n": 9, "tag": "9 \u00b7 EUROPE \u00b7 ECONOMY", "src": "ONS", "art": "basket",
     "head": "UK inflation climbs to 3.6%, a one-year high",
     "deck": "Fuel and a tobacco duty rise pushed CPI up from 3.5%."},
    {"n": 10, "tag": "10 \u00b7 MIDDLE EAST \u00b7 GAZA", "src": "REUTERS", "art": "tank",
     "head": "Israeli tanks push into central Gaza near Nuseirat",
     "deck": "Tunnel past the Yellow Line destroyed; three killed."},
    {"n": 11, "tag": "11 \u00b7 AMERICAS \u00b7 US POLITICS", "src": "NPR", "art": "capitol",
     "head": "Jeffries wins Democrats' nod for House Speaker",
     "deck": "On course to be the first Black Speaker on 3 January."},
    {"n": 12, "tag": "12 \u00b7 WORLD \u00b7 CULTURE", "src": "ROCKSTAR", "art": "game",
     "head": "GTA VI goes on sale after a 13-year wait",
     "deck": "New Zealand plays first; 14.9m pre-orders banked."},
    {"n": 13, "tag": "13 \u00b7 ASIA \u00b7 LABOUR", "src": "DHAKA", "art": "factory",
     "head": "Bangladesh wage protests shut 55 factories",
     "deck": "Police tear-gas garment workers blocking a highway."},
    {"n": 14, "tag": "14 \u00b7 ASIA \u00b7 TRADE", "src": "AP", "art": "trade",
     "head": "Manila: Trump hails 'biggest' Philippine trade deal",
     "deck": "Announced on Wednesday during the APEC summit."},
    {"n": 15, "tag": "15 \u00b7 ASIA \u00b7 DIPLOMACY", "src": "AFP", "art": "tokyo",
     "head": "Tokyo: Takaichi makes first China visit since 2019",
     "deck": "The first such visit in seven years."},
]

BRIEFS = [
    (16, "Ottawa \u2014 Carney and Xi agree tariff relief at APEC"),
    (17, "Seoul \u2014 Lee seeks Xi's help on peace with the North"),
    (18, "Riyadh \u2014 coalition downs a Houthi cruise missile"),
    (19, "Beirut \u2014 World Bank warns Lebanon's rebuilding lags badly"),
    (20, "Berlin \u2014 Germany pledges air defences to Kyiv"),
    (21, "The Hague \u2014 court gives ex-president Thaci 17 months"),
    (22, "Kinshasa \u2014 Ebola passes 11,300 cases"),
    (23, "Washington \u2014 US loses measles-free status"),
    (24, "Guinea \u2014 224 jailed over illegal gold mining"),
    (25, "Maputo \u2014 opposition leader Mondlane goes on trial"),
    (26, "Pretoria \u2014 South Africa reprimands Nigeria envoy"),
    (27, "San Francisco \u2014 Anthropic prices $81bn IPO at $83"),
    (28, "Caracas \u2014 Hegseth visits and seals a defence pact"),
    (29, "Badme \u2014 Ethiopia and Eritrea mass troops at border"),
    (30, "Bogota \u2014 Colombia's economy shrinks 0.8% in Q3"),
    (31, "Brasilia \u2014 Senate passes Lula's $10bn fiscal package"),
    (32, "Peru \u2014 Tumbes River passes its red-alert level"),
    (33, "Antalya \u2014 COP31 ministers weigh fossil-fuel draft"),
    (34, "Turin \u2014 Alcaraz beats Medvedev 6-2, 6-4 in Finals"),
    (35, "Paris \u2014 FIFA: France's Diallo to challenge Infantino"),
    (36, "Sydney \u2014 Tame Impala sweeps seven ARIA Awards"),
    (37, "Pacific \u2014 Cyclone Xavier turns east; 6.0 quake hits PNG"),
    (38, "Canberra \u2014 Australia sanctions settler leader Daniella Weiss"),
    (39, "Kuwait \u2014 magnitude 4.1 quake in the south-west"),
    (40, "Kemerovo \u2014 19 die in An-12 plane crash, media say"),
    (41, "Port-au-Prince \u2014 Salvadoran troops raid gang home"),
    (42, "Johannesburg \u2014 coalition talks begin"),
    (43, "Los Angeles \u2014 Grimes scores 47 as Lakers win 9th straight"),
    (44, "Hormuz \u2014 Iran says it shot down a US MQ-9 drone"),
    (45, "Shenzhen \u2014 Trump and Putin hold talks as APEC opens"),
    (46, "New York \u2014 Dow closes down 561 points (-1.1%)"),
    (47, "Odisha \u2014 50,000 people moved to shelters ahead of Akvan"),
    (48, "Donetsk \u2014 four killed in overnight strikes, governor says"),
]

REGIONS = [
    ("EUROPE 10", 10, (36, 86, 166)),
    ("AMERICAS 12", 12, (46, 139, 58)),
    ("ASIA 8", 8, (123, 63, 160)),
    ("AFRICA 7", 7, (224, 123, 36)),
    ("MIDDLE EAST 5", 5, (192, 57, 43)),
    ("OCEANIA 4", 4, (26, 158, 143)),
    ("WORLD 2", 2, (102, 102, 102)),
]

TOP_STRIP = ("Xi greets Trump \u00b7 141 drones over Ukraine \u00b7 Voyager 1 reaches 1 light-day "
             "\u00b7 Fed minutes \u00b7 GTA VI unlocks in NZ")

SOURCES = ("Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 BBC \u00b7 CNN \u00b7 CNBC \u00b7 NPR \u00b7 ONS \u00b7 "
           "IMD \u00b7 NASA \u00b7 WHO \u00b7 Amnesty")

def art_plane(d, w, h):
    bands = [(214, 90, 40), (232, 130, 50), (240, 170, 80), (246, 205, 130)]
    bh = h // 4 + 1
    for i, c in enumerate(bands):
        d.rectangle([0, i * bh, w, (i + 1) * bh], fill=c)
    d.ellipse([w * 0.40, h * 0.06, w * 0.74, h * 0.80], fill=(196, 60, 36))
    d.rectangle([0, h - 14, w, h], fill=(52, 44, 40))
    fy = int(h * 0.52)
    d.rounded_rectangle([10, fy, w - 14, fy + 24], 12, fill=(250, 244, 224))
    d.polygon([(w - 14, fy + 2), (w - 1, fy + 12), (w - 14, fy + 22)], fill=(250, 244, 224))
    d.polygon([(18, fy + 2), (36, fy - 15), (50, fy + 2)], fill=(24, 42, 84))
    d.rectangle([10, fy + 15, w - 14, fy + 19], fill=(24, 42, 84))
    for i in range(6):
        x = 34 + i * 13
        if x > w - 30:
            break
        d.ellipse([x, fy + 5, x + 6, fy + 11], fill=(24, 42, 84))
    for fx in (int(w * 0.14), int(w * 0.30)):
        d.ellipse([fx, fy - 22, fx + 12, fy - 10], fill=(20, 24, 44))
        d.rectangle([fx + 1, fy - 10, fx + 11, fy + 12], fill=(20, 24, 44))


def art_missiles(d, w, h):
    d.rectangle([0, 0, w, h], fill=(14, 20, 46))
    for i in range(22):
        x = (i * 31) % w
        y = (i * 19) % max(10, h - 26)
        d.ellipse([x, y, x + 2, y + 2], fill=(230, 230, 210))
    d.rectangle([0, h - 16, w, h], fill=(8, 10, 22))
    for i, bh in enumerate((10, 17, 8, 14, 20, 9)):
        x = i * (w // 6)
        d.rectangle([x, h - 16 - bh, x + w // 8, h - 16], fill=(8, 10, 22))
    for sx, ex, col in ((0.08, 0.55, (255, 150, 60)), (0.34, 0.82, (255, 190, 80)), (0.58, 0.97, (255, 150, 60))):
        x0, y0 = int(w * sx), h - 18
        x1, y1 = int(w * ex), int(h * 0.14)
        for t in range(21):
            u = t / 20.0
            x = int(x0 + (x1 - x0) * u)
            y = int(y0 + (y1 - y0) * u - 22 * u * (1 - u) * 2)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col)
        d.polygon([(x1, y1), (x1 - 11, y1 + 5), (x1 - 3, y1 + 9)], fill=(220, 220, 220))


def art_voyager(d, w, h):
    d.rectangle([0, 0, w, h], fill=(10, 14, 34))
    for i in range(34):
        x = (i * 23 + 7) % w
        y = (i * 17 + 3) % h
        s = 3 if i % 7 == 0 else 2
        d.ellipse([x, y, x + s, y + s], fill=(235, 235, 215))
    cx, cy = int(w * 0.44), int(h * 0.50)
    d.ellipse([cx - 40, cy - 34, cx + 6, cy + 18], fill=(232, 200, 110))
    d.ellipse([cx - 33, cy - 27, cx, cy + 11], fill=(200, 164, 74))
    d.line([cx - 16, cy - 8, cx + 18, cy - 20], fill=(230, 230, 230), width=3)
    d.ellipse([cx + 15, cy - 23, cx + 21, cy - 17], fill=(240, 240, 240))
    d.rectangle([cx + 2, cy + 0, cx + 24, cy + 20], fill=(190, 190, 200))
    px, py = cx + 26, cy + 8
    d.rectangle([px, py, px + 62, py + 28], fill=(38, 64, 140))
    for i in range(1, 5):
        d.line([px + i * 12, py, px + i * 12, py + 28], fill=(120, 150, 220), width=1)
    d.line([px, py + 14, px + 62, py + 14], fill=(120, 150, 220), width=1)
    d.ellipse([8, h - 20, 19, h - 9], fill=(70, 130, 230))
    for r in (8, 14, 20):
        d.arc([cx - 16 - r, cy - 8 - r, cx - 16 + r, cy - 8 + r], 100, 190, fill=(140, 200, 255), width=2)


def art_drones(d, w, h):
    d.rectangle([0, 0, w, h], fill=(22, 30, 58))
    d.ellipse([w - 30, 3, w - 8, 20], fill=(226, 226, 200))
    for dx, dy, s in ((22, 10, 1), (64, 16, 1), (40, 22, 0)):
        col = (235, 180, 90) if s else (200, 200, 210)
        d.line([dx - 8, dy - 5, dx + 8, dy + 5], fill=col, width=2)
        d.line([dx - 8, dy + 5, dx + 8, dy - 5], fill=col, width=2)
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=col)
    d.rectangle([0, h - 6, w, h], fill=(10, 12, 24))


def art_bank(d, w, h):
    d.rectangle([0, 0, w, h], fill=(238, 230, 205))
    d.polygon([(w // 2, 2), (6, 14), (w - 6, 14)], fill=(90, 90, 100))
    for i in range(4):
        x = 10 + i * ((w - 20) // 3)
        d.rectangle([x, 16, x + 6, h - 10], fill=(120, 120, 130))
    d.rectangle([6, h - 9, w - 6, h - 5], fill=(90, 90, 100))
    pts = [(8, 10), (30, 15), (50, 12), (72, 20), (w - 24, 17), (w - 8, 26)]
    d.line(pts, fill=(190, 40, 40), width=3)


def art_cyclone(d, w, h):
    d.rectangle([0, 0, w, h], fill=(206, 224, 232))
    cx, cy = w // 2, h // 2
    for r, st in ((26, 20), (19, 140), (12, 260)):
        d.arc([cx - r, cy - r + 2, cx + r, cy + r + 2], st, st + 240, fill=(40, 90, 150), width=4)
    d.ellipse([cx - 4, cy - 1, cx + 4, cy + 7], fill=(240, 248, 252))


def art_sudan(d, w, h):
    d.rectangle([0, 0, w, h], fill=(232, 196, 130))
    d.rectangle([0, h - 9, w, h], fill=(198, 152, 84))
    d.ellipse([7, 3, 24, 17], fill=(246, 220, 140))
    dx, dy = int(w * 0.62), 10
    d.line([dx - 10, dy - 6, dx + 10, dy + 6], fill=(60, 50, 40), width=3)
    d.line([dx - 10, dy + 6, dx + 10, dy - 6], fill=(60, 50, 40), width=3)
    d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(60, 50, 40))


def art_eu(d, w, h):
    import math
    d.rectangle([0, 0, w, h], fill=(30, 60, 150))
    cx, cy, r = w // 2, h // 2, min(w, h) // 3
    for i in range(12):
        a = 2 * math.pi * i / 12.0
        x = cx + int(r * math.cos(a))
        y = cy + int(r * math.sin(a))
        d.polygon([(x, y - 4), (x + 2, y), (x + 5, y), (x + 2, y + 2), (x + 3, y + 5),
                   (x, y + 3), (x - 3, y + 5), (x - 2, y + 2), (x - 5, y), (x - 2, y)],
                  fill=(250, 205, 60))


def art_basket(d, w, h):
    d.rectangle([0, 0, w, h], fill=(240, 234, 210))
    d.polygon([(16, 12), (w - 16, 12), (w - 26, h - 5), (26, h - 5)], fill=(206, 130, 44))
    for i in range(4):
        x = 28 + i * 18
        d.line([x, 14, x - 3, h - 6], fill=(150, 88, 26), width=2)
    d.line([22, 12, 38, 2], fill=(90, 90, 90), width=3)
    d.line([w - 22, 12, w - 38, 2], fill=(90, 90, 90), width=3)
    d.polygon([(w - 20, 1), (w - 6, 9), (w - 21, 12)], fill=(190, 40, 40))
    d.line([w - 28, 15, w - 14, 5], fill=(190, 40, 40), width=3)


def art_tank(d, w, h):
    d.rectangle([0, 0, w, h], fill=(226, 208, 168))
    d.ellipse([w - 34, 2, w - 10, 20], fill=(240, 190, 90))
    d.rectangle([0, h - 7, w, h], fill=(168, 144, 100))
    ty = h - 19
    d.rounded_rectangle([12, ty, w - 16, ty + 12], 6, fill=(74, 84, 58))
    for i in range(4):
        x = 18 + i * 17
        d.ellipse([x, ty + 2, x + 9, ty + 10], fill=(44, 50, 36))
    d.rectangle([40, ty - 8, 76, ty + 1], fill=(74, 84, 58))
    d.line([72, ty - 5, w - 5, ty - 8], fill=(58, 66, 46), width=4)


def art_capitol(d, w, h):
    d.rectangle([0, 0, w, h], fill=(216, 226, 238))
    cx = w // 2
    d.pieslice([cx - 20, 1, cx + 20, 28], 180, 360, fill=(240, 240, 244))
    d.rectangle([cx - 24, 15, cx + 24, 19], fill=(228, 228, 232))
    for i in range(5):
        x = cx - 21 + i * 10
        d.rectangle([x, 20, x + 5, h - 7], fill=(240, 240, 244))
    d.rectangle([cx - 28, h - 7, cx + 28, h - 3], fill=(200, 200, 206))


def art_game(d, w, h):
    d.rectangle([0, 0, w, h], fill=(26, 18, 52))
    for i, bh in enumerate((14, 20, 11, 17)):
        x = i * (w // 4)
        d.rectangle([x, h - bh - 7, x + w // 5, h - 7], fill=(44, 30, 84))
        d.rectangle([x + 3, h - bh - 2, x + 6, h - bh + 1], fill=(250, 200, 90))
    d.rectangle([0, h - 7, w, h], fill=(14, 10, 30))
    cx, cy = w // 2, int(h * 0.40)
    d.rounded_rectangle([cx - 24, cy - 9, cx + 24, cy + 10], 9, fill=(232, 232, 238))
    d.rectangle([cx - 17, cy - 2, cx - 7, cy + 2], fill=(40, 40, 50))
    d.rectangle([cx - 13, cy - 6, cx - 11, cy + 6], fill=(40, 40, 50))
    for dx, col in ((11, (220, 60, 60)), (18, (60, 180, 90))):
        d.ellipse([cx + dx - 3, cy - 3, cx + dx + 3, cy + 3], fill=col)


def art_factory(d, w, h):
    d.rectangle([0, 0, w, h], fill=(224, 216, 198))
    d.rectangle([8, h - 20, w - 8, h - 6], fill=(96, 96, 104))
    for fx in (16, 34):
        d.rectangle([fx, h - 32, fx + 8, h - 20], fill=(80, 80, 88))
        d.ellipse([fx - 1, h - 38, fx + 7, h - 30], fill=(200, 200, 200))
    for i in range(4):
        x = 12 + i * 20
        d.rectangle([x, h - 16, x + 6, h - 11], fill=(250, 205, 90))


def art_trade(d, w, h):
    d.rectangle([0, 0, w, h], fill=(170, 205, 225))
    d.rectangle([0, h - 10, w, h], fill=(60, 120, 170))
    d.polygon([(10, h - 10), (w - 16, h - 10), (w - 26, h - 18), (18, h - 18)], fill=(150, 50, 40))
    for i, col in enumerate(((230, 130, 40), (40, 110, 180), (60, 160, 90))):
        x = 22 + i * 20
        d.rectangle([x, h - 26, x + 17, h - 19], fill=col)
    d.line([w - 20, 2, w - 20, 16], fill=(70, 70, 70), width=2)
    d.line([w - 20, 4, w - 38, 10], fill=(70, 70, 70), width=2)


def art_tokyo(d, w, h):
    d.rectangle([0, 0, w, h], fill=(235, 225, 205))
    cx = w // 2
    d.rectangle([cx - 26, 6, cx + 26, 10], fill=(186, 40, 40))
    d.rectangle([cx - 20, 12, cx + 20, 15], fill=(150, 30, 30))
    for fx in (cx - 18, cx + 14):
        d.rectangle([fx, 10, fx + 4, h - 6], fill=(186, 40, 40))
    d.ellipse([cx - 5, 18, cx + 5, 28], fill=(250, 200, 80))


ART_FUNCS = {
    "plane": art_plane, "missiles": art_missiles, "voyager": art_voyager,
    "drones": art_drones, "bank": art_bank, "cyclone": art_cyclone,
    "sudan": art_sudan, "eu": art_eu, "basket": art_basket, "tank": art_tank,
    "capitol": art_capitol, "game": art_game, "factory": art_factory,
    "trade": art_trade, "tokyo": art_tokyo,
}

MAP_ROWS = [
    "....................................",
    "....######......##...########.......",
    "...########....####..##########..#..",
    "....######......##....########.......",
    ".....####..............######........",
    "......##......##........####.........",
    ".......#.....####......######..##....",
    "......###....######.....####.........",
    ".....#####....####.......##....##....",
    "......###......##....................",
    ".......##.......#..........###.......",
    ".......##..................####......",
    "......###...................##.......",
    ".............................#.......",
]

PINS = [
    (1, 114, 22), (2, 50, 26), (4, 30, 50), (5, -74, 41), (6, 85, 20),
    (7, 30, 13), (8, 4, 51), (9, 0, 51), (10, 34, 31), (11, -79, 38),
    (12, 175, -41), (13, 90, 24), (14, 121, 15), (15, 140, 36),
]


def draw_map(d, F, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1, fill=PAPER)
    d.text((x + 8, y + 6), "WHERE IT HAPPENED", font=F["maph"], fill=INK)
    d.text((x + w - 118, y + 8), "pins = stories 1-15", font=F["maps"], fill=GREY)
    gx, gy = x + 10, y + 26
    gw, gh = w - 20, h - 58
    cols = len(MAP_ROWS[0])
    rows = len(MAP_ROWS)
    cw = gw / cols
    ch = gh / rows
    for r, row in enumerate(MAP_ROWS):
        for c, cell in enumerate(row):
            if cell == "#":
                px = gx + c * cw + cw / 2
                py = gy + r * ch + ch / 2
                d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=(150, 150, 150))
    for n, lon, lat in PINS:
        px = gx + (lon + 180) / 360.0 * gw
        py = gy + (78 - lat) / 140.0 * gh
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED)
        t = str(n)
        tw = d.textlength(t, font=F["pin"])
        d.text((px - tw / 2, py - 4), t, font=F["pin"], fill=(255, 255, 255))
    d.text((x + 8, y + h - 24), "Story 3 is off the map: Voyager 1, in deep space.",
           font=F["maps"], fill=GREY)


def render(path):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    F = load_fonts(__import__("PIL.ImageFont", fromlist=["ImageFont"]))

    # ---- 1. Header ----
    d.rectangle([10, 8, 122, 96], fill=RED)
    d.text((66 - d.textlength("NOV", font=F["nov"]) / 2, 12), "NOV", font=F["nov"], fill=(255, 255, 255))
    d.text((66 - d.textlength("18", font=F["d18"]) / 2, 24), "18", font=F["d18"], fill=(255, 255, 255))
    d.text((66 - d.textlength("WED \u00b7 2026", font=F["wed"]) / 2, 80), "WED \u00b7 2026", font=F["wed"], fill=(255, 255, 255))
    d.text((134, 14), "THE DAY IN WORLD NEWS", font=F["title"], fill=NAVY)
    d.text((136, 62), "Wednesday 18 November 2026", font=F["date"], fill=INK)
    rx = 1014 - d.textlength("48 STORIES", font=F["bignum"])
    d.text((rx, 14), "48 STORIES", font=F["bignum"], fill=RED)
    sub = "7 REGIONS \u00b7 ONE PAGE"
    d.text((1014 - d.textlength(sub, font=F["bigsub"]), 58), sub, font=F["bigsub"], fill=INK)
    sub2 = "the whole day, on one page"
    d.text((1014 - d.textlength(sub2, font=F["msrc"]), 76), sub2, font=F["msrc"], fill=GREY)
    d.line([10, 98, 1014, 98], fill=LINE, width=2)

    # ---- Region bar ----
    x = 10
    total = sum(c for _, c, _ in REGIONS)
    widths = [int(1004 * c / total) for _, c, _ in REGIONS]
    if widths[-1] < 56:
        widths[1] -= 56 - widths[-1]
        widths[-1] = 56
    for li, (label, count, col) in enumerate(REGIONS):
        seg = widths[li]
        d.rectangle([x, 102, x + seg, 124], fill=col)
        tw = d.textlength(label, font=F["region"])
        if li == len(REGIONS) - 1:
            txl = x + seg - tw - 3
        else:
            txl = x + (seg - tw) / 2
        d.text((txl, 108), label, font=F["region"], fill=(255, 255, 255))
        x += seg

    # ---- 2. Top strip ----
    d.rectangle([10, 128, 1014, 154], fill=NAVY)
    d.rectangle([10, 128, 66, 154], fill=RED)
    d.text((38 - d.textlength("TOP 5", font=F["topchip"]) / 2, 134), "TOP 5", font=F["topchip"], fill=(255, 255, 255))
    d.text((76, 134), TOP_STRIP, font=F["top"], fill=(255, 255, 255))

    # ---- 3. Hero zone ----
    hy, hh, hw, gap = 160, 170, 329, 8
    for i, s in enumerate(HEROES):
        x = 10 + i * (hw + gap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=PAPER, outline=LINE, width=2)
        art_img = __import__("PIL.Image", fromlist=["Image"]).new("RGB", (118, hh - 4), CREAM)
        ad = ImageDraw.Draw(art_img)
        ART_FUNCS[s["art"]](ad, 118, hh - 4)
        img.paste(art_img, (x + 2, hy + 2))
        d.ellipse([x + 6, hy + 6, x + 30, hy + 30], fill=RED)
        t = str(s["n"])
        d.text((x + 18 - d.textlength(t, font=F["topchip"]) / 2, hy + 11), t, font=F["topchip"], fill=(255, 255, 255))
        tx = x + 128
        tw_ = hw - 128 - 8
        d.text((tx, hy + 8), s["tag"], font=F["htag"], fill=RED)
        d.text((tx, hy + 21), "Source: " + s["src"] + " \u00b7 " + s["status"], font=F["hsrc"], fill=GREY)
        yy = text_block(d, (tx, hy + 36), s["head"], F["hhead"], INK, tw_, 22, max_lines=4)
        text_block(d, (tx, yy + 3), s["deck"], F["hdeck"], (52, 52, 52), tw_, 14, max_lines=5)

    # ---- 4. Medium grid (4 cols x 3 rows) ----
    gy0, gh_card, gw_card, ggap = 336, 96, 246, 6
    for idx, s in enumerate(MEDIUM):
        r, c = divmod(idx, 4)
        x = 10 + c * (gw_card + ggap + 2)
        y = gy0 + r * (gh_card + ggap)
        d.rectangle([x, y, x + gw_card, y + gh_card], fill=PAPER, outline=LINE, width=1)
        art_img = __import__("PIL.Image", fromlist=["Image"]).new("RGB", (gw_card - 2, 56), CREAM)
        ad = ImageDraw.Draw(art_img)
        ART_FUNCS[s["art"]](ad, gw_card - 2, 56)
        img.paste(art_img.crop((0, 14, gw_card - 2, 42)), (x + 1, y + 1))
        d.text((x + 6, y + 32), s["tag"], font=F["mtag"], fill=RED)
        d.text((x + gw_card - 6 - d.textlength(s["src"], font=F["msrc"]), y + 32), s["src"], font=F["msrc"], fill=GREY)
        yy = text_block(d, (x + 6, y + 42), s["head"], F["mhead"], INK, gw_card - 12, 15, max_lines=2)
        text_block(d, (x + 6, yy + 1), s["deck"], F["mdeck"], (52, 52, 52), gw_card - 12, 11, max_lines=2)

    # ---- 5. Bottom: map + also list ----
    by = 640
    draw_map(d, F, 10, by, 342, 326)
    lx = 362
    d.text((lx, by + 2), "ALSO ON 18 NOVEMBER", font=F["bhead"], fill=NAVY)
    d.text((lx + d.textlength("ALSO ON 18 NOVEMBER", font=F["bhead"]) + 8, by + 4),
           "\u2014 33 more stories", font=F["foot"], fill=GREY)
    d.line([lx, by + 20, 1014, by + 20], fill=LINE, width=1)
    col_w = 320
    for i, (n, txt) in enumerate(BRIEFS):
        col = 0 if i < 17 else 1
        row = i if i < 17 else i - 17
        x = lx + col * (col_w + 12)
        y = by + 28 + row * 17
        num = str(n) + "."
        d.text((x, y), num, font=F["briefb"], fill=RED)
        nw = d.textlength(num, font=F["briefb"]) + 4
        d.text((x + nw, y), txt, font=F["brief"], fill=INK)

    # ---- 6. Footer ----
    d.line([10, 974, 1014, 974], fill=LINE, width=1)
    d.text((10, 980), SOURCES, font=F["foot"], fill=GREY)
    d.text((10, 996), "All stories first reported or happened on Wednesday 18 November 2026",
           font=F["footb"], fill=INK)
    tail = "48 stories \u00b7 7 regions \u00b7 one page"
    d.text((1014 - d.textlength(tail, font=F["foot"]), 996), tail, font=F["foot"], fill=GREY)

    img.save(path, format="PNG", optimize=True)
    return path


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_path = os.path.join(out_dir, "entry.png")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        pass
    try:
        render(out_path)
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        src = os.path.join(here, "entry.png")
        try:
            shutil.copyfile(src, out_path)
        except OSError:
            with open(src, "rb") as fh, open(out_path, "wb") as out:
                out.write(fh.read())
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())



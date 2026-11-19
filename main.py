#!/usr/bin/env python3
"""news-image-20261118: one-page broadsheet of Wednesday 18 November 2026.

Draws a 1024x1024 newspaper front page procedurally with Pillow (flat
vector art, no photos, no network) and writes it to the output dir.
Deterministic: fixed layout, fixed palette, no randomness, no clock.
If Pillow is unavailable (bare standard-library sandbox), it falls back
to copying the committed entry.png that this same program generated.
"""
import os
import shutil
import sys

W = 1024
H = 1024

CREAM = (247, 241, 222)
PAPER = (252, 248, 236)
INK = (24, 24, 28)
NAVY = (16, 32, 64)
RED = (178, 34, 34)
DARKRED = (150, 26, 26)
GREY = (90, 90, 90)
LINE = (40, 40, 40)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_fonts(ImageFont):
    def f(name, size):
        path = os.path.join(FONT_DIR, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    return {
        "title": f("DejaVuSerif-Bold.ttf", 37),
        "kicker": f("DejaVuSans-Bold.ttf", 13),
        "sub": f("DejaVuSans.ttf", 12),
        "mast_r": f("DejaVuSans-Bold.ttf", 15),
        "nov": f("DejaVuSans-Bold.ttf", 17),
        "d18": f("DejaVuSerif-Bold.ttf", 40),
        "wed": f("DejaVuSans-Bold.ttf", 11),
        "region": f("DejaVuSans-Bold.ttf", 11),
        "numlab": f("DejaVuSans-Bold.ttf", 13),
        "numbig": f("DejaVuSans-Bold.ttf", 14),
        "numtxt": f("DejaVuSans.ttf", 12),
        "tl": f("DejaVuSans.ttf", 10),
        "tlb": f("DejaVuSans-Bold.ttf", 10),
        "ltag": f("DejaVuSans-Bold.ttf", 10),
        "lsrc": f("DejaVuSans.ttf", 10),
        "lhead": f("DejaVuSerif-Bold.ttf", 18),
        "ldeck": f("DejaVuSans.ttf", 11),
        "stag": f("DejaVuSans-Bold.ttf", 8),
        "ssrc": f("DejaVuSans.ttf", 8),
        "shead": f("DejaVuSerif-Bold.ttf", 12),
        "sdeck": f("DejaVuSans.ttf", 9),
        "bhead": f("DejaVuSans-Bold.ttf", 12),
        "brief": f("DejaVuSans.ttf", 10),
        "briefb": f("DejaVuSans-Bold.ttf", 10),
        "maph": f("DejaVuSans-Bold.ttf", 12),
        "maps": f("DejaVuSans.ttf", 9),
        "pin": f("DejaVuSans-Bold.ttf", 7),
        "dc": f("DejaVuSans.ttf", 10),
        "dcb": f("DejaVuSans-Bold.ttf", 11),
        "src": f("DejaVuSans.ttf", 9),
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


LEADS = [
    {
        "n": 1, "tag": "1 \u00b7 ASIA \u00b7 APEC SUMMIT", "src": "AP",
        "status": "CONFIRMED", "art": "plane",
        "head": "Xi greets Trump on the tarmac in Shenzhen",
        "deck": "A rare airport welcome as APEC opens. Trump and Putin held "
                "talks earlier; their three-way talks with Xi are set for Thursday.",
    },
    {
        "n": 2, "tag": "2 \u00b7 MIDDLE EAST \u00b7 IRAN WAR", "src": "REUTERS",
        "status": "CLAIM", "art": "missiles",
        "head": "Bahrain and Kuwait intercept Iran's drones",
        "deck": "Iran says it aimed at a US radar in Bahrain and Patriot "
                "batteries in Kuwait, after Tuesday's US strike on Qeshm. "
                "CENTCOM reports no casualties.",
    },
    {
        "n": 3, "tag": "3 \u00b7 WORLD \u00b7 SPACE", "src": "NASA",
        "status": "CONFIRMED", "art": "voyager",
        "head": "Voyager 1 reaches one light-day from Earth",
        "deck": "NASA's 1977 probe is the first craft to get 25.9 billion km "
                "away; a radio command sent today arrives tomorrow. Nothing "
                "human-made has been farther.",
    },
]

CARDS = [
    {"n": 4, "tag": "4 \u00b7 EUROPE \u00b7 UKRAINE WAR", "src": "KYIV AF", "art": "drones",
     "head": "Russia fires 141 drones at Ukraine; 126 downed",
     "deck": "Hits at seven sites overnight; four killed in the Donetsk region, its governor says."},
    {"n": 5, "tag": "5 \u00b7 AMERICAS \u00b7 MARKETS", "src": "FED", "art": "bank",
     "head": "Fed minutes: almost all officials see more hikes",
     "deck": "A bigger December rise is floated; the Dow drops 561 points (-1.1%)."},
    {"n": 6, "tag": "6 \u00b7 ASIA \u00b7 WEATHER", "src": "IMD", "art": "cyclone", "status": "FORECAST",
     "head": "Cyclone Akvan veers north toward Odisha",
     "deck": "India moves ~50,000 people to shelters; landfall is due Friday 20 November."},
    {"n": 7, "tag": "7 \u00b7 AFRICA \u00b7 SUDAN WAR", "src": "AMNESTY", "art": "sudan",
     "head": "Amnesty: RSF drones killed 37 in El Obeid",
     "deck": "It urges a war-crimes inquiry; the RSF blames Sudan's army for the deaths."},
    {"n": 8, "tag": "8 \u00b7 EUROPE \u00b7 UKRAINE AID", "src": "EU", "art": "eu",
     "head": "EU proposes \u20ac45bn loan to fund Ukraine in 2027",
     "deck": "Two-thirds of a \u20ac70bn gap, repaid only once Russia pays reparations."},
    {"n": 9, "tag": "9 \u00b7 EUROPE \u00b7 ECONOMY", "src": "ONS", "art": "basket",
     "head": "UK inflation climbs to 3.6%, a one-year high",
     "deck": "Fuel prices and a tobacco duty rise pushed October CPI up from 3.5%."},
    {"n": 10, "tag": "10 \u00b7 MIDDLE EAST \u00b7 GAZA", "src": "REUTERS", "art": "tank",
     "head": "Israeli tanks push into central Gaza near Nuseirat",
     "deck": "The army says it is destroying a tunnel past the Yellow Line; three killed."},
    {"n": 11, "tag": "11 \u00b7 AMERICAS \u00b7 US POLITICS", "src": "NPR", "art": "capitol",
     "head": "Jeffries wins Democrats' nod for House Speaker",
     "deck": "On course to be the first Black Speaker when the House votes on 3 January."},
    {"n": 12, "tag": "12 \u00b7 WORLD \u00b7 CULTURE", "src": "ROCKSTAR", "art": "game",
     "head": "GTA VI goes on sale after a 13-year wait",
     "deck": "New Zealand plays first at midnight; 14.9m digital pre-orders banked."},
    {"n": 13, "tag": "13 \u00b7 ASIA \u00b7 LABOUR", "src": "DHAKA", "art": "factory",
     "head": "Bangladesh wage protests shut 55 factories",
     "deck": "Police tear-gas garment workers blocking a highway over pay."},
]

BRIEFS = [
    (14, "Manila: Trump hails 'biggest' Philippine trade deal"),
    (15, "Tokyo: Takaichi makes first China visit since 2019"),
    (16, "Ottawa: Carney and Xi agree tariff relief at APEC"),
    (17, "Seoul: Lee seeks Xi's help on peace with the North"),
    (18, "Riyadh: coalition downs a Houthi cruise missile"),
    (19, "Beirut: World Bank warns Lebanon's rebuilding lags badly"),
    (20, "Berlin: Germany pledges air defences to Kyiv"),
    (21, "The Hague: court gives ex-president Thaci 17 months"),
    (22, "Kinshasa: Ebola passes 11,300 cases"),
    (23, "Washington: US loses measles-free status"),
    (24, "Guinea: 224 jailed over illegal gold mining"),
    (25, "Maputo: opposition leader Mondlane goes on trial"),
    (26, "Pretoria: South Africa reprimands Nigeria envoy"),
    (27, "San Francisco: Anthropic prices $81bn IPO at $83"),
    (28, "Caracas: Hegseth visits and seals a defence pact"),
    (29, "Badme: Ethiopia and Eritrea mass troops at border"),
    (30, "Bogota: Colombia's economy shrinks 0.8% in Q3"),
    (31, "Brasilia: Senate passes Lula's $10bn fiscal package"),
    (32, "Peru: Tumbes River passes its red-alert level"),
    (33, "Antalya: COP31 ministers weigh fossil-fuel draft"),
    (34, "Turin: Alcaraz beats Medvedev 6-2, 6-4 in Finals"),
    (35, "Paris: FIFA - France's Diallo to challenge Infantino"),
    (36, "Sydney: Tame Impala sweeps seven ARIA Awards"),
    (37, "Pacific: Cyclone Xavier turns east; 6.0 quake hits PNG"),
    (38, "Canberra: Australia sanctions settler leader Daniella Weiss"),
    (39, "Kuwait: magnitude 4.1 quake in the south-west"),
    (40, "Kemerovo: 19 die in An-12 plane crash, media say"),
    (41, "Port-au-Prince: Salvadoran troops raid gang home"),
    (42, "Johannesburg: coalition talks begin"),
    (43, "Los Angeles: Grimes scores 47 as Lakers win 9th straight"),
    (44, "Hormuz: Iran says it shot down a US MQ-9 drone"),
]

REGIONS = [
    ("EUROPE 9", 9, (36, 86, 166)),
    ("AMERICAS 11", 11, (46, 139, 58)),
    ("ASIA 6", 6, (123, 63, 160)),
    ("AFRICA 7", 7, (224, 123, 36)),
    ("MIDDLE EAST 5", 5, (192, 57, 43)),
    ("OCEANIA 4", 4, (26, 158, 143)),
    ("WORLD 2", 2, (102, 102, 102)),
]

DATE_CHECK = (
    "Left out on purpose - each was first reported on Tuesday 17 November: "
    "Nvidia's $115.8bn quarter \u00b7 the US strike on Qeshm \u00b7 the Kerch Bridge "
    "collapse \u00b7 the Knesset speaker vote \u00b7 Alaska's Senate call. Not yet "
    "happened: the Trump-Xi-Putin talks (Thu 19) \u00b7 Cyclone Akvan's landfall "
    "(Fri 20) \u00b7 the close of COP31 (Fri 20)."
)

SOURCES = ("Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 BBC \u00b7 CNN \u00b7 CNBC \u00b7 NPR \u00b7 ONS \u00b7 "
           "IMD \u00b7 NASA \u00b7 WHO \u00b7 Amnesty")

def art_plane(d, w, h):
    # sunset bands, big sun, airliner on tarmac, two figures
    bands = [(214, 90, 40), (232, 130, 50), (240, 170, 80), (246, 205, 130)]
    bh = h // 4 + 1
    for i, c in enumerate(bands):
        d.rectangle([0, i * bh, w, (i + 1) * bh], fill=c)
    d.ellipse([w * 0.42, h * 0.08, w * 0.72, h * 0.78], fill=(196, 60, 36))
    d.rectangle([0, h - 16, w, h], fill=(52, 44, 40))
    # fuselage
    fy = int(h * 0.52)
    d.rounded_rectangle([18, fy, w - 26, fy + 26], 13, fill=(250, 244, 224))
    d.polygon([(w - 26, fy + 2), (w - 2, fy + 13), (w - 26, fy + 24)], fill=(250, 244, 224))
    d.polygon([(30, fy + 2), (52, fy - 16), (66, fy + 2)], fill=(24, 42, 84))
    d.rectangle([18, fy + 16, w - 26, fy + 20], fill=(24, 42, 84))
    for i in range(11):
        x = 52 + i * 20
        d.ellipse([x, fy + 6, x + 7, fy + 12], fill=(24, 42, 84))
    # figures
    for fx in (int(w * 0.16), int(w * 0.30)):
        d.ellipse([fx, fy - 24, fx + 13, fy - 11], fill=(20, 24, 44))
        d.rectangle([fx + 1, fy - 11, fx + 12, fy + 14], fill=(20, 24, 44))
    # flags
    for fx, col in ((int(w * 0.80), (200, 40, 40)), (int(w * 0.87), (40, 60, 160))):
        d.line([fx, fy - 18, fx, fy + 6], fill=(30, 30, 30), width=2)
        d.rectangle([fx, fy - 18, fx + 13, fy - 10], fill=col)


def art_missiles(d, w, h):
    d.rectangle([0, 0, w, h], fill=(14, 20, 46))
    for i in range(26):
        x = (i * 53) % w
        y = (i * 29) % max(10, h - 30)
        d.ellipse([x, y, x + 2, y + 2], fill=(230, 230, 210))
    # city silhouette
    d.rectangle([0, h - 20, w, h], fill=(8, 10, 22))
    for i, bh in enumerate((12, 20, 9, 16, 24, 11, 18)):
        x = i * (w // 7)
        d.rectangle([x, h - 20 - bh, x + w // 9, h - 20], fill=(8, 10, 22))
    # interceptor arcs + drones
    for sx, ex, col in ((0.08, 0.55, (255, 150, 60)), (0.30, 0.78, (255, 190, 80)), (0.55, 0.95, (255, 150, 60))):
        x0, y0 = int(w * sx), h - 22
        x1, y1 = int(w * ex), int(h * 0.16)
        for t in range(21):
            u = t / 20.0
            x = int(x0 + (x1 - x0) * u)
            y = int(y0 + (y1 - y0) * u - 26 * u * (1 - u) * 2)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col)
        d.polygon([(x1, y1), (x1 - 12, y1 + 5), (x1 - 3, y1 + 10)], fill=(220, 220, 220))


def art_voyager(d, w, h):
    d.rectangle([0, 0, w, h], fill=(10, 14, 34))
    for i in range(40):
        x = (i * 37 + 11) % w
        y = (i * 23 + 5) % h
        s = 3 if i % 7 == 0 else 2
        d.ellipse([x, y, x + s, y + s], fill=(235, 235, 215))
    cx, cy = int(w * 0.52), int(h * 0.52)
    # dish
    d.ellipse([cx - 52, cy - 40, cx + 8, cy + 22], fill=(232, 200, 110))
    d.ellipse([cx - 44, cy - 33, cx + 1, cy + 15], fill=(200, 164, 74))
    d.line([cx - 20, cy - 8, cx + 22, cy - 22], fill=(230, 230, 230), width=3)
    d.ellipse([cx + 19, cy - 25, cx + 26, cy - 18], fill=(240, 240, 240))
    # body + boom
    d.rectangle([cx + 4, cy + 2, cx + 30, cy + 24], fill=(190, 190, 200))
    d.line([cx + 28, cy + 12, cx + 74, cy - 4], fill=(200, 200, 200), width=3)
    # solar / RTG panel grid right
    px, py = cx + 36, cy + 14
    d.rectangle([px, py, px + 92, py + 34], fill=(38, 64, 140))
    for i in range(1, 6):
        d.line([px + i * 15, py, px + i * 15, py + 34], fill=(120, 150, 220), width=1)
    d.line([px, py + 17, px + 92, py + 17], fill=(120, 150, 220), width=1)
    # earth dot + signal arcs
    d.ellipse([14, h - 24, 26, h - 12], fill=(70, 130, 230))
    for r in (10, 18, 26):
        d.arc([cx - 20 - r, cy - 8 - r, cx - 20 + r, cy - 8 + r], 100, 190, fill=(140, 200, 255), width=2)


def art_drones(d, w, h):
    d.rectangle([0, 0, w, h], fill=(22, 30, 58))
    d.ellipse([w - 44, 6, w - 14, 30], fill=(226, 226, 200))
    for cx, cy in ((30, 34), (90, 20), (140, 40)):
        d.ellipse([cx, cy, cx + 52, cy + 12], fill=(52, 62, 92))
    for dx, dy, s in ((36, 16, 1), (110, 26, 1), (66, 30, 0)):
        col = (235, 180, 90) if s else (200, 200, 210)
        d.line([dx - 9, dy - 6, dx + 9, dy + 6], fill=col, width=2)
        d.line([dx - 9, dy + 6, dx + 9, dy - 6], fill=col, width=2)
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=col)
    d.rectangle([0, h - 8, w, h], fill=(10, 12, 24))


def art_bank(d, w, h):
    d.rectangle([0, 0, w, h], fill=(238, 230, 205))
    d.polygon([(w // 2, 4), (8, 22), (w - 8, 22)], fill=(90, 90, 100))
    d.rectangle([10, 24, w - 10, 29], fill=(90, 90, 100))
    for i in range(4):
        x = 16 + i * ((w - 32) // 3)
        d.rectangle([x, 31, x + 8, h - 16], fill=(120, 120, 130))
    d.rectangle([8, h - 14, w - 8, h - 8], fill=(90, 90, 100))
    pts = [(14, 16), (52, 24), (86, 20), (120, 34), (w - 40, 30), (w - 14, 44)]
    d.line(pts, fill=(190, 40, 40), width=3)
    d.polygon([(w - 14, 44), (w - 26, 42), (w - 17, 33)], fill=(190, 40, 40))


def art_cyclone(d, w, h):
    d.rectangle([0, 0, w, h], fill=(206, 224, 232))
    cx, cy = w // 2, h // 2
    for r, st in ((40, 20), (30, 140), (20, 260)):
        d.arc([cx - r, cy - r + 4, cx + r, cy + r + 4], st, st + 240, fill=(40, 90, 150), width=5)
    d.ellipse([cx - 6, cy - 2, cx + 6, cy + 10], fill=(240, 248, 252))
    for i in range(5):
        x = 8 + i * (w // 5)
        d.arc([x, h - 16, x + 26, h + 2], 180, 360, fill=(40, 90, 150), width=3)


def art_sudan(d, w, h):
    d.rectangle([0, 0, w, h], fill=(232, 196, 130))
    d.rectangle([0, h - 14, w, h], fill=(198, 152, 84))
    d.ellipse([12, 6, 38, 28], fill=(246, 220, 140))
    dx, dy = int(w * 0.62), 16
    d.line([dx - 13, dy - 8, dx + 13, dy + 8], fill=(60, 50, 40), width=3)
    d.line([dx - 13, dy + 8, dx + 13, dy - 8], fill=(60, 50, 40), width=3)
    d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(60, 50, 40))
    for i in range(4):
        x = 16 + i * 44
        d.polygon([(x, h - 14), (x + 10, h - 30), (x + 20, h - 14)], fill=(170, 128, 70))


def art_eu(d, w, h):
    d.rectangle([0, 0, w, h], fill=(30, 60, 150))
    import math
    cx, cy, r = w // 2, h // 2, min(w, h) // 3
    for i in range(12):
        a = 2 * math.pi * i / 12.0
        x = cx + int(r * math.cos(a))
        y = cy + int(r * math.sin(a))
        d.polygon([(x, y - 5), (x + 2, y), (x + 6, y), (x + 3, y + 3), (x + 4, y + 7),
                   (x, y + 4), (x - 4, y + 7), (x - 3, y + 3), (x - 6, y), (x - 2, y)],
                  fill=(250, 205, 60))


def art_basket(d, w, h):
    d.rectangle([0, 0, w, h], fill=(240, 234, 210))
    d.polygon([(30, 22), (w - 30, 22), (w - 44, h - 10), (44, h - 10)], fill=(206, 130, 44))
    for i in range(4):
        x = 44 + i * 30
        d.line([x, 26, x - 4, h - 12], fill=(150, 88, 26), width=3)
    d.line([36, 22, 60, 6], fill=(90, 90, 90), width=4)
    d.line([w - 36, 22, w - 60, 6], fill=(90, 90, 90), width=4)
    d.polygon([(w - 30, 4), (w - 12, 16), (w - 32, 20)], fill=(190, 40, 40))
    d.line([w - 44, 26, w - 22, 10], fill=(190, 40, 40), width=4)


def art_tank(d, w, h):
    d.rectangle([0, 0, w, h], fill=(226, 208, 168))
    d.ellipse([w - 52, 4, w - 16, 34], fill=(240, 190, 90))
    d.rectangle([0, h - 12, w, h], fill=(168, 144, 100))
    ty = h - 30
    d.rounded_rectangle([22, ty, w - 30, ty + 18], 9, fill=(74, 84, 58))
    for i in range(5):
        x = 32 + i * 26
        d.ellipse([x, ty + 3, x + 13, ty + 15], fill=(44, 50, 36))
    d.rectangle([70, ty - 13, 128, ty + 1], fill=(74, 84, 58))
    d.line([122, ty - 8, w - 8, ty - 12], fill=(58, 66, 46), width=6)


def art_capitol(d, w, h):
    d.rectangle([0, 0, w, h], fill=(216, 226, 238))
    cx = w // 2
    d.pieslice([cx - 30, 2, cx + 30, 44], 180, 360, fill=(240, 240, 244))
    d.rectangle([cx - 3, 0, cx + 3, 10], fill=(240, 240, 244))
    d.rectangle([cx - 36, 24, cx + 36, 30], fill=(228, 228, 232))
    for i in range(5):
        x = cx - 32 + i * 15
        d.rectangle([x, 32, x + 7, h - 12], fill=(240, 240, 244))
    d.rectangle([cx - 42, h - 12, cx + 42, h - 6], fill=(200, 200, 206))


def art_game(d, w, h):
    d.rectangle([0, 0, w, h], fill=(26, 18, 52))
    for i, bh in enumerate((26, 38, 20, 32, 24)):
        x = i * (w // 5)
        d.rectangle([x, h - bh - 12, x + w // 6, h - 12], fill=(44, 30, 84))
        for wy in range(2):
            d.rectangle([x + 5, h - bh - 4 + wy * 9, x + 10, h - bh + 1 + wy * 9], fill=(250, 200, 90))
    d.rectangle([0, h - 12, w, h], fill=(14, 10, 30))
    # controller
    cx, cy = w // 2, int(h * 0.42)
    d.rounded_rectangle([cx - 34, cy - 13, cx + 34, cy + 15], 13, fill=(232, 232, 238))
    d.rectangle([cx - 24, cy - 3, cx - 10, cy + 3], fill=(40, 40, 50))
    d.rectangle([cx - 19, cy - 8, cx - 15, cy + 8], fill=(40, 40, 50))
    for dx, col in ((16, (220, 60, 60)), (25, (60, 180, 90))):
        d.ellipse([cx + dx - 4, cy - 4, cx + dx + 4, cy + 4], fill=col)


def art_factory(d, w, h):
    d.rectangle([0, 0, w, h], fill=(224, 216, 198))
    d.rectangle([14, h - 34, w - 14, h - 10], fill=(96, 96, 104))
    for fx in (30, 58):
        d.rectangle([fx, h - 56, fx + 12, h - 34], fill=(80, 80, 88))
        d.ellipse([fx - 2, h - 66, fx + 10, h - 54], fill=(200, 200, 200))
        d.ellipse([fx + 6, h - 72, fx + 20, h - 60], fill=(214, 214, 214))
    for i in range(4):
        x = 22 + i * 30
        d.rectangle([x, h - 28, x + 9, h - 20], fill=(250, 205, 90))
    for i in range(6):
        x = 18 + i * 28
        y = h - 8
        d.ellipse([x, y - 6, x + 6, y], fill=(50, 50, 60))


ART_FUNCS = {
    "plane": art_plane, "missiles": art_missiles, "voyager": art_voyager,
    "drones": art_drones, "bank": art_bank, "cyclone": art_cyclone,
    "sudan": art_sudan, "eu": art_eu, "basket": art_basket, "tank": art_tank,
    "capitol": art_capitol, "game": art_game, "factory": art_factory,
}

CONTINENTS = [
    [(18, 38), (70, 26), (108, 34), (112, 58), (88, 74), (70, 70), (52, 86), (34, 72), (20, 58)],
    [(78, 96), (100, 92), (108, 116), (96, 152), (82, 168), (74, 128)],
    [(148, 36), (176, 28), (190, 44), (178, 62), (158, 60), (146, 50)],
    [(150, 72), (186, 66), (200, 86), (192, 132), (168, 146), (152, 110)],
    [(192, 30), (268, 24), (300, 44), (286, 72), (250, 66), (232, 86), (206, 74), (196, 52)],
    [(272, 118), (306, 112), (312, 134), (284, 140)],
]

PINS = [
    (1, 272, 58, True), (2, 208, 64, True), (4, 182, 44, False),
    (5, 62, 50, False), (6, 240, 70, False), (7, 176, 88, False),
    (8, 160, 40, False), (9, 148, 34, False), (10, 196, 60, False),
    (11, 74, 58, False), (12, 314, 148, False), (13, 250, 62, False),
]


def in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map(d, fonts, x0, y0, w):
    d.text((x0, y0), "WHERE IT HAPPENED", font=fonts["maph"], fill=INK)
    mx, my = x0, y0 + 20
    mh = 176
    d.rectangle([mx, my, mx + w, my + mh], fill=(238, 240, 228))
    dot = (110, 118, 105)
    for gy in range(6, mh - 4, 6):
        for gx in range(4, w - 2, 6):
            for poly in CONTINENTS:
                if in_poly(gx, gy, poly):
                    d.ellipse([mx + gx - 2, my + gy - 2, mx + gx + 2, my + gy + 2], fill=dot)
                    break
    for n, px, py, is_red in PINS:
        cx, cy = mx + px, my + py
        col = RED if is_red else NAVY
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=col, outline=(255, 255, 255), width=1)
        label = str(n)
        tw = d.textlength(label, font=fonts["pin"])
        d.text((cx - tw / 2, cy - 4), label, font=fonts["pin"], fill=(255, 255, 255))
    # deep-space arrow for story 3
    ax, ay = mx + w - 58, my + 8
    d.line([ax, ay + 12, ax + 44, ay], fill=RED, width=2)
    d.polygon([(ax + 44, ay), (ax + 34, ay - 1), (ax + 37, ay + 8)], fill=RED)
    yy = my + mh + 6
    d.text((x0, yy), "3 \u00b7 TO VOYAGER 1, IN DEEP SPACE \u2192", font=fonts["tlb"], fill=RED)
    yy += 15
    d.text((x0, yy), "Red pins: stories 1-2 \u00b7 dark pins: stories 4-13",
           font=fonts["maps"], fill=GREY)
    return yy + 14


def draw_page(Image, ImageDraw, fonts):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([10, 8, 94, 84], fill=RED)
    d.text((52, 12), "NOV", font=fonts["nov"], fill=(255, 255, 255), anchor="ma")
    d.text((52, 28), "18", font=fonts["d18"], fill=(255, 255, 255), anchor="ma")
    d.text((52, 70), "WED \u00b7 2026", font=fonts["wed"], fill=(255, 255, 255), anchor="ma")
    d.text((104, 10), "THE DAY IN WORLD NEWS", font=fonts["kicker"], fill=RED)
    d.text((103, 24), "Wednesday 18 November 2026", font=fonts["title"], fill=INK)
    d.text((104, 66), "Everything on this page happened, or was first reported, on Wednesday 18 November 2026.",
           font=fonts["sub"], fill=GREY)
    for i, ln in enumerate(("44 STORIES", "7 REGIONS", "ONE PAGE")):
        tw = d.textlength(ln, font=fonts["mast_r"])
        d.text((1014 - tw, 14 + i * 21), ln, font=fonts["mast_r"], fill=INK)

    # ---- region bar ----
    total = sum(c for _, c, _ in REGIONS)
    cum = 0
    for label, count, col in REGIONS:
        x = 10 + round(1004 * cum / total)
        cum += count
        x2 = 10 + round(1004 * cum / total)
        d.rectangle([x, 88, x2, 108], fill=col)
        lf = fonts["stag"] if count <= 2 else fonts["region"]
        tw = d.textlength(label, font=lf)
        d.text((x + (x2 - x - tw) / 2, 93 if count > 2 else 95), label, font=lf, fill=(255, 255, 255))

    # ---- numbers strip ----
    y = 113
    d.text((10, y), "THE DAY IN NUMBERS:", font=fonts["numlab"], fill=INK)
    x = 10 + d.textlength("THE DAY IN NUMBERS: ", font=fonts["numlab"])
    items = [("141", " drones fired"), ("126", " downed"), ("25.9bn km", " Voyager 1"),
             ("55", " factories shut"), ("251-11", " Jeffries vote"), ("11,300+", " Ebola cases")]
    for i, (big, small) in enumerate(items):
        if i:
            d.text((x, y), " \u00b7 ", font=fonts["numtxt"], fill=GREY)
            x += d.textlength(" \u00b7 ", font=fonts["numtxt"])
        d.text((x, y), big, font=fonts["numbig"], fill=RED)
        x += d.textlength(big, font=fonts["numbig"])
        d.text((x, y + 1), small, font=fonts["numtxt"], fill=INK)
        x += d.textlength(small, font=fonts["numtxt"])

    # ---- UTC timeline strip ----
    d.rectangle([10, 134, 1014, 158], fill=(238, 232, 210))
    tl1 = "OVERNIGHT Drones over Kuwait, Bahrain and Ukraine \u00b7 07:00 UTC UK inflation 3.6% \u00b7 MORNING Xi greets Trump in Shenzhen \u00b7 10:16 UTC Voyager 1: one light-day"
    tl2 = "11:00 UTC GTA VI unlocks in New Zealand \u00b7 19:00 UTC Fed minutes: more hikes \u00b7 21:00 UTC Dow closes down 1.1%"
    d.text((512, 136), tl1, font=fonts["tl"], fill=INK, anchor="ma")
    d.text((512, 148), tl2, font=fonts["tl"], fill=INK, anchor="ma")

    # ---- lead cards ----
    ly, lh, lw, gap = 162, 186, 330, 7
    for i, card in enumerate(LEADS):
        x0 = 10 + i * (lw + gap)
        d.rectangle([x0, ly, x0 + lw, ly + lh], fill=PAPER, outline=LINE, width=1)
        art = Image.new("RGB", (lw - 2, 80), CREAM)
        ad = ImageDraw.Draw(art)
        ART_FUNCS[card["art"]](ad, lw - 2, 80)
        img.paste(art, (x0 + 1, ly + 1))
        d = ImageDraw.Draw(img)
        stw = d.textlength(card["status"], font=fonts["tlb"])
        d.rectangle([x0 + 1, ly + 64, x0 + 14 + stw, ly + 81], fill=NAVY)
        d.text((x0 + 7, ly + 67), card["status"], font=fonts["tlb"], fill=(255, 255, 255))
        ty = ly + 85
        d.text((x0 + 6, ty), card["tag"], font=fonts["ltag"], fill=RED)
        srw = d.textlength(card["src"], font=fonts["lsrc"])
        d.text((x0 + lw - 6 - srw, ty), card["src"], font=fonts["lsrc"], fill=GREY)
        ty = text_block(d, (x0 + 6, ty + 13), card["head"], fonts["lhead"], INK, lw - 12, 20, 2)
        text_block(d, (x0 + 6, ty + 1), card["deck"], fonts["ldeck"], (50, 50, 50), lw - 12, 13, 4)

    # ---- small cards 4-13 ----
    sy, sh, sw_, sgap = 354, 136, 196, 6
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x0 = 10 + col * (sw_ + sgap)
        y0 = sy + row * (sh + 6)
        d.rectangle([x0, y0, x0 + sw_, y0 + sh], fill=PAPER, outline=LINE, width=1)
        art = Image.new("RGB", (sw_ - 2, 48), CREAM)
        ad = ImageDraw.Draw(art)
        ART_FUNCS[card["art"]](ad, sw_ - 2, 48)
        img.paste(art, (x0 + 1, y0 + 1))
        d = ImageDraw.Draw(img)
        ty = y0 + 52
        d.text((x0 + 5, ty), card["tag"], font=fonts["stag"], fill=RED)
        srw = d.textlength(card["src"], font=fonts["ssrc"])
        d.text((x0 + sw_ - 5 - srw, ty), card["src"], font=fonts["ssrc"], fill=GREY)
        ty = text_block(d, (x0 + 5, ty + 10), card["head"], fonts["shead"], INK, sw_ - 10, 14, 3)
        text_block(d, (x0 + 5, ty + 1), card["deck"], fonts["sdeck"], (50, 50, 50), sw_ - 10, 11, 3)

    # ---- bottom: map + briefs ----
    by = 640
    d.line([10, by - 4, 1014, by - 4], fill=LINE, width=1)
    draw_map(d, fonts, 10, by, 326)
    bx = 348
    d.text((bx, by), "ALSO ON WEDNESDAY 18 NOVEMBER \u2014 31 MORE STORIES", font=fonts["bhead"], fill=INK)
    colw = 326
    col1 = BRIEFS[:16]
    col2 = BRIEFS[16:]
    for ci, colitems in enumerate((col1, col2)):
        cx = bx + ci * (colw + 12)
        yy = by + 20
        for n, txt in colitems:
            num = str(n) + " "
            d.text((cx, yy), num, font=fonts["briefb"], fill=RED)
            off = d.textlength(num, font=fonts["briefb"])
            lines = wrap(d, txt, fonts["brief"], colw - off)
            for li, ln in enumerate(lines):
                d.text((cx + off, yy), ln, font=fonts["brief"], fill=INK)
                yy += 11
            yy += 4

    # ---- date check ----
    dy = 924
    d.rectangle([10, dy, 1014, 970], outline=RED, width=2)
    d.text((18, dy + 6), "DATE CHECK", font=fonts["dcb"], fill=RED)
    text_block(d, (18, dy + 22), DATE_CHECK, fonts["dc"], INK, 988, 12, 2)

    # ---- sources ----
    d.text((10, 980), SOURCES, font=fonts["src"], fill=GREY)
    tail = "All 44 stories happened, or were first reported, on Wednesday 18 November 2026. Original drawings."
    tw = d.textlength(tail, font=fonts["src"])
    d.text((1014 - tw, 980), tail, font=fonts["src"], fill=GREY)
    d.text((10, 994), "One page \u00b7 one day \u00b7 drawn by program \u00b7 main.py writes this image to /output/entry.png",
           font=fonts["src"], fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        src = os.path.join(here, "entry.png")
        shutil.copyfile(src, dest)
        print("copied committed entry.png (Pillow unavailable)")
        return 0
    fonts = load_fonts(ImageFont)
    img = draw_page(Image, ImageDraw, fonts)
    img.save(dest, format="PNG", optimize=True)
    print("wrote", dest, os.path.getsize(dest), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())



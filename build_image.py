#!/usr/bin/env python3
"""Draw the news-image-20261119 v3 poster (1024x1024, RGB PNG).

v3 = master-prompt-v3 (rank-2 style). The main correction from v2.1:
  - NO thick card borders (v2.1 had 3 px outlines + 2 px art frames).
  - NO red verified-number strips under articles.
  - NO region band.
  - Only hairline 1-2 px rules between articles; illustrations sit
    directly in the article area with no frame; generous cream space.
  - Every card has a real 2-4 line dark description (never red).
  - Masthead like rank 2: "THE WORLD IN ONE PICTURE" + huge serif
    date + italic red strapline + six-column number band on cream.
  - 3 heroes + 10 mids + 21 briefs = 34 stories, map + DATE CHECK.

Stories: master-prompt-v3 + facts-v2-verified.md. M4 uses VERDICT
wording -- the ICJ judgment was confirmed at build time (UN News,
Reuters, CNN, Le Monde, 19 Nov): Myanmar found responsible for
genocide against the Rohingya, first time the Court held a state
accountable, ruling final. M13 is Ruto (verified v2 Africa slot).
Numbers printed: $81.3bn, 13 years, 11:00 UTC, 200,000+, 120-130
km/h, 2019 -- all from the master prompt / verified facts. The
rank-2 poster's conflicting figures were NOT copied ($120bn COP31,
700,000+ Rohingya, 50,000 Odisha, 551,864 Suneung).

Art: 13 NEW flat editorial vector illustrations + new world map,
generated as 4 contact sheets (v3-illustrations/) in one consistent
style, cropped by prepare_art_v3.py into the embedded ZIP in
img_part1/2/3.py (single-line base64). The build is fully
deterministic: same bytes on every run, no network, no clock, no
randomness.

Usage: python3 build_image.py [out_path]  (default /output/entry.png)
"""
import base64
import io
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PAGE_W, PAGE_H = 1024, 1024
MARGIN = 24
CONTENT_W = PAGE_W - 2 * MARGIN  # 976

# ---- palette (exact, from the master prompt) ----
PAPER = (244, 237, 224)
INK = (21, 21, 21)
RULE = (43, 43, 43)
NAVY = (18, 35, 74)
RED = (179, 38, 30)
GREY = (90, 86, 78)
LIGHT_GREY = (150, 146, 138)
REGION = {
    "Europe": (46, 94, 170),
    "Americas": (46, 125, 79),
    "Asia-Pacific": (200, 69, 45),
    "Middle East": (199, 122, 31),
    "Africa": (138, 106, 16),
    "Oceania": (122, 63, 160),
    "World": (74, 85, 96),
}

# ---- v3 geometry ----
TOP_Y = 8
DATE_Y = 26
DATE_MAX = 60
STRAP_Y = 96
BAND_RULE_Y = 116
BAND_Y = 118
BAND_H = 36
BAND_RULE2_Y = 158
HERO_Y = 166
HERO_W = 320
HERO_GAP = 8
HERO_ART_W, HERO_ART_H = 308, 104
MID_W = 192
MID_CGAP = 4
MID_RGAP = 3
MID_ART_W, MID_ART_H = 180, 54
MAP_W, MAP_H = 280, 120
MAP_COL_W = 330


# ---- fonts ----
def _pick(names):
    for name in names:
        for root in ("/usr/share/fonts", "/usr/local/share/fonts"):
            hits = sorted(Path(root).rglob(name))
            if hits:
                return str(hits[0])
    return None


SERIF_B = _pick(["NotoSerifCondensed-Bold.ttf", "NotoSerif-Bold.ttf",
                 "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"])
SERIF = _pick(["NotoSerifCondensed-Regular.ttf", "NotoSerif-Regular.ttf",
               "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"])
SERIF_I = _pick(["NotoSerifCondensed-Italic.ttf", "NotoSerif-Italic.ttf",
                 "DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf"])
SANS_B = _pick(["NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf",
                "LiberationSans-Bold.ttf"])
SANS = _pick(["NotoSans-Regular.ttf", "DejaVuSans.ttf",
              "LiberationSans-Regular.ttf"])


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, path, start_size, max_w, min_size=10):
    """Largest size <= start_size at which text fits max_w."""
    size = start_size
    while size > min_size and text_w(draw, text, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


# ---- story data ----
# "pin" is (fx, fy) on the map image, 0..1 (estimated from the v3 map
# crop; verified visually on the render).
HEROES = [
    dict(n=1, place="SHENZHEN, CHINA", cat="DIPLOMACY",
         region="Asia-Pacific", art="h1",
         head="Trump, Xi and Putin hold first three-way summit",
         desc=("The three nuclear powers meet in Shenzhen during the "
               "APEC gathering, with nuclear arms control among "
               "Washington's priorities. The outcome remains "
               "unconfirmed."),
         pin=(0.80, 0.36)),
    dict(n=2, place="WORLDWIDE", cat="GAMES", region="World", art="h2",
         head="GTA VI arrives after a 13-year wait",
         desc=("Rockstar's sequel unlocks at local midnight, with New "
               "Zealand among the first markets to receive the game "
               "- the follow-up to GTA V, from 2013."),
         pin=(0.94, 0.80)),
    dict(n=3, place="NEW YORK", cat="MARKETS", region="Americas",
         art="h3",
         head="Anthropic starts trading on Nasdaq as ANT",
         desc=("Anthropic begins public trading after pricing its "
               "shares at $83, above the $70-78 range. The offering "
               "raised about $81.3bn; first trades begin Thursday."),
         pin=(0.205, 0.30)),
]

MIDS = [
    dict(n=4, place="THE HAGUE", cat="LAW", region="Europe", art="m1",
         head="World Court rules on Rohingya genocide case",
         desc=("The World Court finds Myanmar guilty of genocide "
               "against the Rohingya. The ruling is final."),
         pin=(0.455, 0.25)),
    dict(n=5, place="ODISHA", cat="STORM", region="Asia-Pacific",
         art="m2",
         head="Cyclone Akvan bears down on India's east coast",
         desc=("Odisha plans evacuations of more than 200,000 people. "
               "Forecast winds are 120-130 km/h."),
         pin=(0.70, 0.50)),
    dict(n=6, place="ANTALYA", cat="CLIMATE", region="World", art="m3",
         head="COP31 enters its final 48 hours",
         desc=("Final stage: ministers work through unresolved issues; "
               "a finance target stays in play."),
         pin=(0.50, 0.38)),
    dict(n=7, place="KYIV", cat="WAR", region="Europe", art="m4",
         head="Ukraine watches Shenzhen from the sidelines",
         desc=("Not on the summit agenda, Kyiv watches the talks "
               "closely on the war and security."),
         pin=(0.545, 0.26)),
    dict(n=8, place="SHENZHEN", cat="TRADE", region="Asia-Pacific",
         art="m5",
         head="APEC leaders gather in Shenzhen",
         desc=("Pacific economies meet in Shenzhen, with trade and "
               "economic cooperation at the centre."),
         pin=(0.84, 0.48)),
    dict(n=9, place="SOUTH FLORIDA", cat="WEATHER", region="Americas",
         art="m6",
         head="Flooded Florida braces for still more rain",
         desc=("Heavy rain floods roads across South Florida, and a "
               "synagogue roof collapses."),
         pin=(0.27, 0.52)),
    dict(n=10, place="JERUSALEM", cat="POLITICS", region="Middle East",
         art="m7",
         head="Israel pauses E1 settlement contract process",
         desc=("Israel's attorney general pauses the E1 settlement "
               "contract process in Jerusalem."),
         pin=(0.575, 0.46)),
    dict(n=11, place="WASHINGTON", cat="POLITICS", region="Americas",
         art="m8",
         head="Lawmakers urge Trump to press Xi on detainees",
         desc=("U.S. lawmakers want the detained Americans raised "
               "with Trump and Xi in their discussions."),
         pin=(0.235, 0.40)),
    dict(n=12, place="RIYADH", cat="HORMUZ", region="Middle East",
         art="m9",
         head="Missile aimed at Riyadh; tanker hit near Oman",
         desc=("A missile aimed at Riyadh was intercepted; a tanker "
               "was hit near Khasab, Oman."),
         pin=(0.625, 0.55)),
    dict(n=13, place="NAIROBI", cat="POLITICS", region="Africa",
         art="m10",
         head="Ruto gives State of the Nation address",
         desc=("Kenya's president addresses parliament in Nairobi for "
               "the State of the Nation address."),
         pin=(0.53, 0.60)),
]

# (number, place, text, region) -- the 21 verified v2 briefs, unchanged
BRIEFS = [
    (14, "US–PHILIPPINES", "eye $2bn+ loan deal", "Asia-Pacific"),
    (15, "PANAMA", "2nd arrest in reporter attack", "Americas"),
    (16, "KHASAB", "tanker hit off Oman; crew safe", "Middle East"),
    (17, "WASHINGTON", "US sanctions 3 over Hezbollah links", "Americas"),
    (18, "ESTONIA", "to close Russia crossings", "Europe"),
    (19, "PRAGUE", "mass protest over media law", "Europe"),
    (20, "SPAIN", "strike disrupts ports, plants", "Europe"),
    (21, "HOLLYWOOD", "actor Stacy Keach dies, aged 85", "Americas"),
    (22, "TOKYO", "India, Japan hold 2+2 defence talks", "Asia-Pacific"),
    (23, "NEW DELHI", "Sindhu back in badminton top 5", "Asia-Pacific"),
    (24, "DELHI", "schools reopen as smog eases", "Asia-Pacific"),
    (25, "VIENNA", "IAEA: N. Korea expanding enrichment", "Asia-Pacific"),
    (26, "CARACAS", "US cites $12bn Venezuela revenue", "Americas"),
    (27, "GAZA", "4 nations: let aid reach flooded Gaza", "Middle East"),
    (28, "SANA'A", "coalition hits Houthi sites", "Middle East"),
    (29, "SHENZHEN", "Carney meets Trump; talks continue", "Asia-Pacific"),
    (30, "WELLINGTON", "India bowl first in NZ Test", "Oceania"),
    (31, "NAIROBI", "opposition holds reform forum", "Africa"),
    (32, "SAN JOSE", "Logitech marks GTA launch", "Americas"),
    (33, "PARIS", "France under 300+ weather alerts", "Europe"),
    (34, "KUMAMOTO", "strong quake shakes SW Japan", "Asia-Pacific"),
]

NUMBER_BAND = [
    ("$81.3BN", "RAISED BY ANTHROPIC"),
    ("13 YEARS", "SINCE GTA V"),
    ("11:00 UTC", "GTA VI NZ UNLOCK"),
    ("200,000+", "ODISHA EVACUATIONS"),
    ("120–130 KM/H", "AKVAN FORECAST WINDS"),
    ("2019", "CASE FILED"),
]

DATE_CHECK = ("DATE CHECK — left off on purpose because they broke "
              "before Thursday: Peltola's Alaska win (17) · "
              "Canada–China deal (17) · Kerch Bridge (16–17) · "
              "Duckett's 133 (18) · Van Gogh $190.4m (Wed night) · "
              "settler sanctions (17–18) · Iran drones (17–18) · EU "
              "€45bn loan · Jeffries Speaker · Voyager 1 · Bangladesh "
              "535 · Pew projection · COP31 draft (Mon)")

FOOTER = ("Every story on this page happened or was first reported on "
          "Thursday 19 November 2026, in any time zone.")


# ---- artwork ----
def load_art():
    art = {}
    for part in (1, 2, 3):
        src = (HERE / f"img_part{part}.py").read_text()
        ns = {}
        exec(compile(src, f"img_part{part}.py", "exec"), ns)
        zf = zipfile.ZipFile(io.BytesIO(base64.b64decode(ns["DATA"])))
        for name in zf.namelist():
            art[name[:-4]] = Image.open(io.BytesIO(zf.read(name))).convert("RGB")
    return art


# ---- drawing ----
def draw_chip(d, x, y, n, label, size):
    """Red circled number + red caps label (rank-2 style)."""
    r = 7 if size >= 11 else 6
    cx, cy = x + r, y + r
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    num_f = font(SANS_B, 9 if size >= 11 else 8)
    t = str(n)
    d.text((cx - text_w(d, t, num_f) / 2, cy - 6),
           t, font=num_f, fill=(255, 255, 255))
    lab_f = font(SANS_B, size)
    d.text((x + 2 * r + 5, y + (2 * r - size) // 2 + 1),
           label, font=lab_f, fill=RED)


def article_height(d, story, w, hero):
    """Height of one article (art + chip + headline + desc)."""
    tw = w - 12
    head_f = font(SERIF_B, 24 if hero else 14)
    head_lh = 28 if hero else 17
    head_lines = wrap(d, story["head"], head_f, tw)
    desc_f = font(SANS, 12 if hero else 11)
    desc_lh = 15 if hero else 13
    desc_lines = wrap(d, story["desc"], desc_f, tw)
    art_h = HERO_ART_H if hero else MID_ART_H
    chip_h = 14 if hero else 12
    return (art_h + 5 + chip_h + 3 + len(head_lines) * head_lh
            + 3 + len(desc_lines) * desc_lh + 6), head_lines, desc_lines


def draw_article(d, page, art, story, x, y, w, hero):
    """One article: art on top (NO frame), chip, headline, desc."""
    aw = HERO_ART_W if hero else MID_ART_W
    ah = HERO_ART_H if hero else MID_ART_H
    ax = x + 6
    img = art[story["art"]]
    if img.size != (aw, ah):
        img = img.resize((aw, ah), Image.LANCZOS)
    page.paste(img, (ax, y))
    cy = y + ah + 5
    chip_size = 11 if hero else 9
    draw_chip(d, x + 6, cy, story["n"],
              f"{story['place']} · {story['cat']}", chip_size)
    hy = cy + (14 if hero else 12) + 3
    tw = w - 12
    head_f = font(SERIF_B, 24 if hero else 14)
    head_lh = 28 if hero else 17
    head_lines = wrap(d, story["head"], head_f, tw)
    for line in head_lines:
        d.text((x + 6, hy), line, font=head_f, fill=INK)
        hy += head_lh
    desc_f = font(SANS, 12 if hero else 11)
    desc_lh = 15 if hero else 13
    hy += 3
    for line in wrap(d, story["desc"], desc_f, tw):
        d.text((x + 6, hy), line, font=desc_f, fill=INK)
        hy += desc_lh
    return hy


def build(out_path):
    art = load_art()
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)

    # ---- one thin outer rule near the page edges ----
    d.rectangle([5, 5, PAGE_W - 6, PAGE_H - 6], outline=RULE, width=1)

    # ---- masthead top line (rank-2 style) ----
    top_f = font(SANS_B, 11)
    d.text((MARGIN, TOP_Y), "THE WORLD IN ONE PICTURE",
           font=top_f, fill=RED)
    total = len(HEROES) + len(MIDS) + len(BRIEFS)
    right_txt = f"{total} STORIES · EVERY ONE FROM THURSDAY 19 NOVEMBER 2026"
    d.text((PAGE_W - MARGIN - text_w(d, right_txt, top_f), TOP_Y),
           right_txt, font=top_f, fill=GREY)

    # ---- big serif date, auto-fitted ----
    date_txt = "Thursday 19 November 2026"
    date_f = fit_font(d, date_txt, SERIF_B, DATE_MAX, CONTENT_W)
    d.text(((PAGE_W - text_w(d, date_txt, date_f)) / 2, DATE_Y),
           date_txt, font=date_f, fill=INK)

    # ---- italic red strapline ----
    strap = ("Three leaders meet in Shenzhen · GTA VI unlocks worldwide "
             "· A record IPO starts trading · The World Court rules on "
             "the Rohingya")
    strap_f = font(SERIF_I, 13)
    d.text(((PAGE_W - text_w(d, strap, strap_f)) / 2, STRAP_Y),
           strap, font=strap_f, fill=RED)

    # ---- number band: navy figures on cream, thin dividers ----
    d.line([(MARGIN, BAND_RULE_Y), (PAGE_W - MARGIN, BAND_RULE_Y)],
           fill=RULE, width=1)
    cell_w = CONTENT_W / len(NUMBER_BAND)
    num_f = font(SANS_B, 19)
    num_lab_f = font(SANS, 9)
    for i, (num, lab) in enumerate(NUMBER_BAND):
        cx = MARGIN + i * cell_w
        d.text((cx + (cell_w - text_w(d, num, num_f)) / 2, BAND_Y + 3),
               num, font=num_f, fill=NAVY)
        d.text((cx + (cell_w - text_w(d, lab, num_lab_f)) / 2, BAND_Y + 25),
               lab, font=num_lab_f, fill=GREY)
        if i:
            d.line([(cx, BAND_Y + 4), (cx, BAND_Y + BAND_H - 4)],
                   fill=LIGHT_GREY, width=1)
    d.line([(MARGIN, BAND_RULE2_Y), (PAGE_W - MARGIN, BAND_RULE2_Y)],
           fill=RULE, width=2)
    d.line([(MARGIN, BAND_RULE2_Y + 3), (PAGE_W - MARGIN, BAND_RULE2_Y + 3)],
           fill=RULE, width=1)

    # ---- heroes: measure, then draw (art top, no frames) ----
    hero_h = max(article_height(d, s, HERO_W, True)[0] for s in HEROES)
    for i, story in enumerate(HEROES):
        hx = MARGIN + i * (HERO_W + HERO_GAP)
        draw_article(d, page, art, story, hx, HERO_Y, HERO_W, True)
        if i:
            gx = MARGIN + i * (HERO_W + HERO_GAP) - HERO_GAP // 2
            d.line([(gx, HERO_Y), (gx, HERO_Y + hero_h)],
                   fill=LIGHT_GREY, width=1)
    hero_end = HERO_Y + hero_h
    d.line([(MARGIN, hero_end + 4), (PAGE_W - MARGIN, hero_end + 4)],
           fill=RULE, width=1)

    # ---- mids, 5 x 2 ----
    mid_h = max(article_height(d, s, MID_W, False)[0] for s in MIDS)
    mid_y0 = hero_end + 9
    for i, story in enumerate(MIDS):
        row, col = divmod(i, 5)
        mx = MARGIN + col * (MID_W + MID_CGAP)
        my = mid_y0 + row * (mid_h + MID_RGAP)
        draw_article(d, page, art, story, mx, my, MID_W, False)
        if col:
            gx = MARGIN + col * (MID_W + MID_CGAP) - MID_CGAP // 2
            d.line([(gx, my), (gx, my + mid_h)], fill=LIGHT_GREY, width=1)
    mid_end = mid_y0 + 2 * mid_h + MID_RGAP
    d.line([(MARGIN, mid_end + 4), (PAGE_W - MARGIN, mid_end + 4)],
           fill=RULE, width=1)

    # ---- map + briefs ----
    sec_y = mid_end + 7
    sec_f = font(SANS_B, 12)
    d.text((MARGIN, sec_y), "WHERE IT HAPPENED", font=sec_f, fill=INK)
    d.text((MARGIN + 176, sec_y), "NUMBERED = CARDS · DOTS = BRIEFS",
           font=font(SANS_B, 9), fill=GREY)
    bx0 = MARGIN + 350
    d.text((bx0, sec_y), "ALSO ON THURSDAY 19 NOVEMBER", font=sec_f,
           fill=INK)
    d.line([(MARGIN, sec_y + 15), (PAGE_W - MARGIN, sec_y + 15)],
           fill=RULE, width=1)
    map_y = sec_y + 19
    map_img = art["map"]
    if map_img.size != (MAP_W, MAP_H):
        map_img = map_img.resize((MAP_W, MAP_H), Image.LANCZOS)
    map_x = MARGIN + (MAP_COL_W - MAP_W) // 2
    page.paste(map_img, (map_x, map_y))
    # numbered pins 1-13
    for story in HEROES + MIDS:
        fx, fy = story["pin"]
        px = map_x + int(fx * MAP_W)
        py = map_y + int(fy * MAP_H)
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r],
                  fill=(255, 255, 255), outline=RED, width=2)
        num_f = font(SANS_B, 10)
        t = str(story["n"])
        d.text((px - text_w(d, t, num_f) / 2, py - 6),
               t, font=num_f, fill=RED)
    # legend: pin counts only, one line, computed from the pin data
    pin_counts = {}
    for s in HEROES + MIDS:
        pin_counts[s["region"]] = pin_counts.get(s["region"], 0) + 1
    order = ["Europe", "Americas", "Asia-Pacific", "Middle East",
             "Africa", "World"]
    short = {"Europe": "EUROPE", "Americas": "THE AMERICAS",
             "Asia-Pacific": "ASIA-PACIFIC", "Middle East": "MIDEAST",
             "Africa": "AFRICA", "World": "WORLD"}
    leg = " · ".join(f"{short[r]} {pin_counts.get(r, 0)}" for r in order)
    leg_y = map_y + MAP_H + 5
    d.text((MARGIN, leg_y), leg, font=font(SANS_B, 9), fill=INK)

    # briefs, two columns
    bw = 305
    col1 = BRIEFS[:11]
    col2 = BRIEFS[11:]
    brief_f = font(SANS, 11)
    for col_i, col in enumerate((col1, col2)):
        cx = bx0 + col_i * (bw + 20)
        cy = sec_y + 23
        for n, place, text, _region in col:
            line = f"{n} — {place}: {text}"
            fnt = brief_f
            while text_w(d, line, fnt) > bw and fnt.size > 9:
                fnt = font(SANS, fnt.size - 1)
            d.text((cx, cy), "•  " + line, font=fnt, fill=INK)
            cy += 14
    brief_end = sec_y + 23 + 11 * 15

    # ---- date check + footer ----
    dc_y = max(leg_y + 16, brief_end + 4)
    dc_lines = wrap(d, DATE_CHECK, font(SANS_B, 9), CONTENT_W - 12)
    dc_h = 4 + len(dc_lines) * 12 + 3
    d.rectangle([MARGIN, dc_y, PAGE_W - MARGIN - 1, dc_y + dc_h - 1],
                outline=RED, width=1)
    for i, line in enumerate(dc_lines):
        d.text((MARGIN + 6, dc_y + 4 + i * 12), line,
               font=font(SANS_B, 9), fill=RED)
    foot_f = font(SANS, 9)
    foot_y = dc_y + dc_h + 3
    d.text(((PAGE_W - text_w(d, FOOTER, foot_f)) / 2, foot_y),
           FOOTER, font=foot_f, fill=GREY)

    print(f"layout: hero_h={hero_h} mid_h={mid_h} hero_end={hero_end} "
          f"mid_end={mid_end} sec_y={sec_y} map_y={map_y} "
          f"leg_y={leg_y} brief_end={brief_end} dc_y={dc_y} "
          f"dc_lines={len(dc_lines)} foot_y={foot_y} "
          f"page_bottom={foot_y + 10}")
    if foot_y + 10 > PAGE_H - 6:
        print("WARNING: content overflows the page!")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    build(target)
    print(f"wrote {target}")

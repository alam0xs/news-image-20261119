#!/usr/bin/env python3
"""Draw the news-image-20261119 v2.1 poster (1024x1024, RGB PNG).

v2.1 = v2 with BIGGER pictures (Ivan: "masih banyak ruang kosong,
bisa agak dibesarkan sedikit lagi gambar gambar nya"). Nothing about
the stories changed: same 34 stories, same headlines, numbers,
bands, masthead text, palette, borders, pins, DATE CHECK and footer.

What grew (display size, before -> after):
  hero art  308x88  -> 308x116  (+32%)
  mid art   180x38  -> 180x64   (+68%; now a picture, not a strip)
  world map 272x150 -> 280x155  (fills more of its column)
The cards grew with the art, and the header was tightened a little
(title 68 -> 64 px, bands slightly shorter) so everything still
fits on the one page with nothing clipped or overlapping.

Art was re-cropped for v2.1 (see prepare_art_v2.1.py): the v2 crops
were short strips, and stretching them to the new sizes would have
distorted the scenes. The new crops come from the same ChatGPT
sources at (near) the display aspect, so they stay sharp. Two
content fixes ride along: m10 Nairobi now shows the domed
parliament + skyline (v2's crop accidentally showed the quake
street), and h3 uses poster1's full chart panel (building + A +
ticker) instead of poster3's thin chart strip.

Layout follows the ChatGPT v2 design (poster3): single-line serif
masthead, region band + number band, 3 hero cards + 10 mid cards,
each with a clear border (3 px card outline + 2 px art frame), a
dotted world map with numbered pins, two brief columns, a DATE
CHECK box and a footer.

Artwork comes from the embedded ZIPs in img_part1/2/3.py (each a
single-line base64 string). The build is fully deterministic: same
bytes on every run, no network, no clock, no randomness.

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

# ---- palette (from the Claude brief) ----
PAPER = (244, 237, 224)
INK = (21, 21, 21)
RULE = (43, 43, 43)
NAVY = (18, 35, 74)
RED = (179, 38, 30)
GREY = (90, 86, 78)
REGION = {
    "Europe": (46, 94, 170),
    "Americas": (46, 125, 79),
    "Asia-Pacific": (200, 69, 45),
    "Middle East": (199, 122, 31),
    "Africa": (138, 106, 16),
    "Oceania": (122, 63, 160),
    "World": (74, 85, 96),
}
REGION_SHORT = {
    "Europe": "EUROPE",
    "Americas": "THE AMERICAS",
    "Asia-Pacific": "ASIA-PACIFIC",
    "Middle East": "MIDEAST",
    "Africa": "AFRICA",
    "Oceania": "OCEANIA",
    "World": "WORLD",
}

# ---- v2.1 geometry ----
# header (tightened a touch so the bigger pictures fit)
STRIP_Y = 6
STRIP_RULE_Y = 19
TITLE_Y = 23
TITLE_START = 64          # auto-fit caps at 64 px here
SUB_Y = 98
SUB_SIZE = 13
REGION_Y = 115
REGION_H = 16
REGION_LAB_Y = 133
NUM_Y = 142
NUM_H = 34
RULE1_Y = 180
RULE2_Y = 183
# heroes: art 308x116 (was 308x88)
HERO_Y = 187
HERO_H = 236
HERO_W = 320
HERO_GAP = 8
HERO_CHIP_H = 17
HERO_ART_H = 116
# mids: art 180x64 (was 180x38)
MID_W = 192
MID_H = 170
MID_CGAP = 4
MID_RGAP = 4
MID_CHIP_H = 12
MID_ART_H = 64
GAP_HM = 4
GAP_MB = 4
# map: shown 280x155 (was 272x150), same 270x150 crop
MAP_W, MAP_H = 280, 155
MAP_COL_W = 330
DATE_CHECK_Y = 975


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
# region is one of REGION keys. "band" is the verified-number strip
# (None = no band). "pin" is (fx, fy) on the map image, 0..1.
HEROES = [
    dict(n=1, place="SHENZHEN", cat="SUMMIT", region="Asia-Pacific",
         art="h1",
         head="Trump, Xi and Putin hold first three-way summit",
         ctx="Nuclear arms control tops the agenda",
         band=None,
         pin=(0.83, 0.52)),
    dict(n=2, place="NEW YORK", cat="GAMES", region="World",
         art="h2",
         head="GTA VI arrives after a 13-year wait",
         ctx="PS5 and Xbox Series X|S; New Zealand played first",
         band="FIRST UNLOCK 11:00 UTC",
         pin=(0.97, 0.88)),
    dict(n=3, place="NASDAQ", cat="MARKETS", region="Americas",
         art="h3",
         head="Anthropic debuts in the biggest IPO on record",
         ctx="Priced $83, above its range; first trade pending",
         band="$83 · $81.3BN RAISED",
         pin=(0.20, 0.34)),
]

MIDS = [
    dict(n=4, place="THE HAGUE", cat="LAW", region="Europe",
         art="m1",
         head="Court reads Rohingya genocide judgment",
         ctx="Gambia v. Myanmar; verdict day in The Hague",
         band="CASE FILED NOV 2019",
         pin=(0.47, 0.28)),
    dict(n=5, place="ODISHA", cat="STORM", region="Asia-Pacific",
         art="m2",
         head="Cyclone Akvan bears down on east India",
         ctx="Odisha to evacuate 200,000+",
         band="120–130 KM/H",
         pin=(0.72, 0.55)),
    dict(n=6, place="ANTALYA", cat="CLIMATE", region="World",
         art="m3",
         head="COP31 enters its final 48 hours",
         ctx="Ministers take over the text; 21 issues open",
         band="21 ISSUES",
         pin=(0.55, 0.38)),
    dict(n=7, place="KYIV", cat="WAR", region="Europe",
         art="m4",
         head="Ukraine watches Shenzhen from the sidelines",
         ctx="Kyiv urges Trump and Xi to press Putin",
         band=None,
         pin=(0.53, 0.30)),
    dict(n=8, place="SHENZHEN", cat="TRADE", region="Asia-Pacific",
         art="m5",
         head="APEC leaders gather in Shenzhen",
         ctx="Xi pledges $20m; 21 economies seek a declaration",
         band="$20M PLEDGED",
         pin=(0.89, 0.60)),
    dict(n=9, place="FLORIDA", cat="WEATHER", region="Americas",
         art="m6",
         head="Flooded Florida braces for still more rain",
         ctx="Heavy rain floods roads; synagogue roof collapses",
         band=None,
         pin=(0.11, 0.53)),
    dict(n=10, place="JERUSALEM", cat="POLITICS", region="Middle East",
         art="m7",
         head="Israel pauses E1 settlement contract",
         ctx="Attorney general halts process in Jerusalem",
         band=None,
         pin=(0.56, 0.49)),
    dict(n=11, place="WASHINGTON", cat="POLITICS", region="Americas",
         art="m8",
         head="Lawmakers urge Trump to press Xi on detainees",
         ctx="Americans held in China raised in Washington",
         band=None,
         pin=(0.14, 0.42)),
    dict(n=12, place="IRAN", cat="CONFLICT", region="Middle East",
         art="m9",
         head="Trump reportedly weighs Iran strikes",
         ctx="Netanyahu said to seek 4- to 7-day campaign",
         band="4–7 DAYS",
         pin=(0.62, 0.43)),
    dict(n=13, place="NAIROBI", cat="POLITICS", region="Africa",
         art="m10",
         head="Ruto gives State of the Nation address",
         ctx="Kenya's president speaks to parliament",
         band=None,
         pin=(0.55, 0.62)),
]

# (number, place, text, region) -- verified 19 Nov items, one line each
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
    ("$83", "ANT IPO PRICE"),
    ("$81.3BN", "RAISED BY ANTHROPIC"),
    ("11:00 UTC", "GTA VI NZ UNLOCK"),
    ("200,000+", "ODISHA EVACUATIONS"),
    ("120–130 KM/H", "AKVAN WIND SPEED"),
    ("21 ISSUES", "OPEN AT COP31"),
]

DATE_CHECK = ("DATE CHECK — FIRST REPORTED 17–18 NOV, SO NOT ON THIS PAGE "
              "AS NEWS: Peltola's Alaska win (17) · Canada–China deal "
              "(17) · Kerch Bridge (16–17) · Duckett's 133 (18) · Van "
              "Gogh $190.4m (Wed night) · settler sanctions (17–18) · "
              "Iran drones (17–18) · EU €45bn loan · Jeffries Speaker · "
              "Voyager 1 · Bangladesh 535 · Pew projection · COP31 draft "
              "(Mon)")

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
def draw_card(d, page, art, story, x, y, w, h, hero):
    """One bordered picture card. Returns nothing; draws in place."""
    # strong card outline + framed art panel (Ivan's v2 fix, kept)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=3)
    colour = REGION[story["region"]]
    chip_h = HERO_CHIP_H if hero else MID_CHIP_H
    chip_font = font(SANS_B, 11 if hero else 9)
    d.rectangle([x + 3, y + 3, x + w - 4, y + 3 + chip_h - 1], fill=colour)
    chip_txt = f"{story['n']} · {story['place']} · {story['cat']}"
    if hero:
        d.text((x + 8, y + 3 + (chip_h - 11) // 2),
               chip_txt, font=chip_font, fill=(255, 255, 255))
    else:
        d.text((x + 8, y + 4), chip_txt, font=chip_font,
               fill=(255, 255, 255))
    ax, ay = x + 6, y + 3 + chip_h + 4
    aw = w - 12
    ah = HERO_ART_H if hero else MID_ART_H
    img = art[story["art"]]
    if img.size != (aw, ah):
        img = img.resize((aw, ah), Image.LANCZOS)
    page.paste(img, (ax, ay))
    d.rectangle([ax, ay, ax + aw - 1, ay + ah - 1], outline=INK, width=2)
    tx = x + 8
    tw = w - 16
    hy = ay + ah + 6
    head_f = font(SERIF_B, 22 if hero else 14)
    head_lh = 26 if hero else 17
    head_lines = wrap(d, story["head"], head_f, tw)
    for line in head_lines[:3]:
        d.text((tx, hy), line, font=head_f, fill=INK)
        hy += head_lh
    ctx_f = font(SANS, 11)
    ctx_lh = 14 if hero else 13
    for line in wrap(d, story["ctx"], ctx_f, tw)[:2]:
        d.text((tx, hy), line, font=ctx_f, fill=INK)
        hy += ctx_lh
    if story["band"]:
        band_f = font(SANS_B, 13 if hero else 11)
        d.text((tx, y + h - 20 if hero else y + h - 17),
               story["band"], font=band_f, fill=RED)


def build(out_path):
    art = load_art()
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)

    # ---- masthead strip ----
    strip_f = font(SANS_B, 10)
    d.text((MARGIN, STRIP_Y), "THE WORLD IN ONE PICTURE",
           font=strip_f, fill=GREY)
    mid_txt = "EVERY STORY FROM ONE DAY"
    d.text(((PAGE_W - text_w(d, mid_txt, strip_f)) / 2, STRIP_Y),
           mid_txt, font=strip_f, fill=GREY)
    right_txt = "NO. 3 · ONE PAGE"
    d.text((PAGE_W - MARGIN - text_w(d, right_txt, strip_f), STRIP_Y),
           right_txt, font=strip_f, fill=GREY)
    d.line([(MARGIN, STRIP_RULE_Y), (PAGE_W - MARGIN, STRIP_RULE_Y)],
           fill=RULE, width=1)

    # ---- neat one-line title, auto-fitted (rank-1 style) ----
    date_txt = "Thursday 19 November 2026"
    date_f = fit_font(d, date_txt, SERIF_B, TITLE_START, CONTENT_W)
    d.text(((PAGE_W - text_w(d, date_txt, date_f)) / 2, TITLE_Y),
           date_txt, font=date_f, fill=INK)

    # ---- subline ----
    total = len(HEROES) + len(MIDS) + len(BRIEFS)
    sub_f = font(SERIF, SUB_SIZE)
    sub_lead = f"{total} stories from one day — "
    sub_rest = ("a first three-way summit, GTA VI's release day, the "
                "biggest IPO ever, a genocide judgment, a cyclone")
    lead_w = text_w(d, sub_lead, sub_f)
    rest_w = text_w(d, sub_rest, sub_f)
    sx = (PAGE_W - lead_w - rest_w) / 2
    d.text((sx, SUB_Y), sub_lead, font=sub_f, fill=RED)
    d.text((sx + lead_w, SUB_Y), sub_rest, font=sub_f, fill=INK)

    # ---- region band (counts computed from the data) ----
    all_stories = HEROES + MIDS + [
        dict(region=r) for (_, _, _, r) in BRIEFS]
    counts = {}
    for s in all_stories:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    order = ["Europe", "Americas", "Asia-Pacific", "Middle East",
             "Africa", "Oceania", "World"]
    widths = {}
    for r in order:
        min_w = 72 if r == "Oceania" else 64
        widths[r] = max(int(counts.get(r, 0) / total * CONTENT_W), min_w)
    widths["Asia-Pacific"] -= sum(widths.values()) - CONTENT_W
    bx, by, bh = MARGIN, REGION_Y, REGION_H
    band_f = font(SANS_B, 10)
    for r in order:
        w = widths[r]
        d.rectangle([bx, by, bx + w - 1, by + bh - 1], fill=REGION[r])
        label = f"{REGION_SHORT[r]} {counts.get(r, 0)}"
        if text_w(d, label, band_f) <= w - 8:
            d.text((bx + (w - text_w(d, label, band_f)) / 2, by + 3),
                   label, font=band_f, fill=(255, 255, 255))
        bx += w
    lab_f = font(SANS, 8)
    lab = "STORIES BY REGION — COUNTED FROM THIS PAGE"
    d.text(((PAGE_W - text_w(d, lab, lab_f)) / 2, REGION_LAB_Y),
           lab, font=lab_f, fill=GREY)

    # ---- number band ----
    nb_y, nb_h = NUM_Y, NUM_H
    d.rectangle([MARGIN, nb_y, PAGE_W - MARGIN - 1, nb_y + nb_h - 1],
                fill=NAVY)
    cell_w = CONTENT_W / len(NUMBER_BAND)
    num_f = font(SANS_B, 19)
    num_lab_f = font(SANS, 9)
    for i, (num, lab) in enumerate(NUMBER_BAND):
        cx = MARGIN + i * cell_w
        d.text((cx + (cell_w - text_w(d, num, num_f)) / 2, nb_y + 3),
               num, font=num_f, fill=(255, 255, 255))
        d.text((cx + (cell_w - text_w(d, lab, num_lab_f)) / 2, nb_y + 22),
               lab, font=num_lab_f, fill=(200, 205, 215))
        if i:
            d.line([(cx, nb_y + 4), (cx, nb_y + nb_h - 4)],
                   fill=(255, 255, 255), width=1)
    # double rule
    d.line([(MARGIN, RULE1_Y), (PAGE_W - MARGIN, RULE1_Y)], fill=RULE, width=2)
    d.line([(MARGIN, RULE2_Y), (PAGE_W - MARGIN, RULE2_Y)], fill=RULE, width=1)

    # ---- heroes (bigger art: 308x116) ----
    for i, story in enumerate(HEROES):
        hx = MARGIN + i * (HERO_W + HERO_GAP)
        draw_card(d, page, art, story, hx, HERO_Y, HERO_W, HERO_H, True)

    # ---- mids, 5 x 2 (bigger art: 180x64) ----
    mid_y0 = HERO_Y + HERO_H + GAP_HM
    for i, story in enumerate(MIDS):
        row, col = divmod(i, 5)
        mx = MARGIN + col * (MID_W + MID_CGAP)
        my = mid_y0 + row * (MID_H + MID_RGAP)
        draw_card(d, page, art, story, mx, my, MID_W, MID_H, False)

    # ---- map + briefs ----
    sec_y = mid_y0 + 2 * MID_H + MID_RGAP + GAP_MB
    map_img = art["map"]
    if map_img.size != (MAP_W, MAP_H):
        map_img = map_img.resize((MAP_W, MAP_H), Image.LANCZOS)
    map_x = MARGIN + (MAP_COL_W - MAP_W) // 2
    sec_f = font(SANS_B, 12)
    d.text((MARGIN, sec_y), "WHERE IT HAPPENED", font=sec_f, fill=INK)
    d.text((MARGIN + 176, sec_y), "NUMBERED = CARDS · DOTS = BRIEFS",
           font=font(SANS_B, 9), fill=GREY)
    d.line([(MARGIN, sec_y + 14), (MARGIN + MAP_COL_W, sec_y + 14)],
           fill=RULE, width=1)
    map_y = sec_y + 18
    page.paste(map_img, (map_x, map_y))
    d.rectangle([map_x, map_y, map_x + MAP_W - 1,
                 map_y + MAP_H - 1], outline=INK, width=2)
    # numbered pins 1-13 (fractions are of the map image, so they
    # stay right when the map is shown bigger)
    pin_counts = {}
    for s in HEROES + MIDS:
        pin_counts[s["region"]] = pin_counts.get(s["region"], 0) + 1
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
    # legend: pin counts only, two deliberate lines (never split mid-item);
    # counts computed from the pin data, never typed by hand
    leg_y = map_y + MAP_H + 6
    leg_f = font(SANS_B, 10)
    leg_lines = [
        " · ".join(f"{REGION_SHORT[r]} {pin_counts.get(r, 0)}"
                   for r in ("Europe", "Americas", "Asia-Pacific")),
        " · ".join(f"{REGION_SHORT[r]} {pin_counts.get(r, 0)}"
                   for r in ("Middle East", "Africa", "World")),
    ]
    for line in leg_lines:
        d.text((MARGIN, leg_y), line, font=leg_f, fill=INK)
        leg_y += 12

    # briefs, two columns
    bx0 = MARGIN + 350
    bw = 305
    d.text((bx0, sec_y), "MORE FROM THURSDAY", font=sec_f, fill=INK)
    d.line([(bx0, sec_y + 14), (PAGE_W - MARGIN, sec_y + 14)],
           fill=RULE, width=1)
    col1 = BRIEFS[:11]
    col2 = BRIEFS[11:]
    brief_f = font(SANS, 11)
    for col_i, col in enumerate((col1, col2)):
        cx = bx0 + col_i * (bw + 20)
        cy = sec_y + 22
        for n, place, text, _region in col:
            line = f"{n} — {place}: {text}"
            fnt = brief_f
            while text_w(d, line, fnt) > bw and fnt.size > 9:
                fnt = font(SANS, fnt.size - 1)
            d.text((cx, cy), "•  " + line, font=fnt, fill=INK)
            cy += 16

    # ---- date check + footer ----
    dc_y = DATE_CHECK_Y
    dc_lines = wrap(d, DATE_CHECK, font(SANS_B, 9), CONTENT_W - 12)
    dc_h = 6 + len(dc_lines) * 12 + 4
    d.rectangle([MARGIN, dc_y, PAGE_W - MARGIN - 1, dc_y + dc_h - 1],
                outline=RED, width=1)
    for i, line in enumerate(dc_lines):
        d.text((MARGIN + 6, dc_y + 4 + i * 12), line,
               font=font(SANS_B, 9), fill=RED)
    foot_f = font(SANS, 9)
    d.text(((PAGE_W - text_w(d, FOOTER, foot_f)) / 2, dc_y + dc_h + 4),
           FOOTER, font=foot_f, fill=GREY)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    build(target)
    print(f"wrote {target}")

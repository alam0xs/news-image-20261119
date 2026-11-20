# DOSSIER.md — news-image-20261119 v3

Entry for make.fun bounty
[`news-image-20261119`](https://make.fun/bounty/news-image-20261119):
a program that writes one image summing up the world's news of
Thursday, 19 November 2026, to `/output/entry.png`.

## v2.1 fix — the entry program now decodes, never draws (run_completes)

The v2.1 entry was rejected by the site: `run_completes` failed
with exit code 1. Cause: the old `main.py` imported `build_image`,
which needs Pillow, but the judging server only provides the
Python standard library — and `python3 -P` does not put the
script's own folder on `sys.path`, so the companion imports
would have failed even with Pillow present.

Fix (this session, fresh agent that never saw the old `main.py`):

- `main.py` rewritten from scratch, standard library only
  (`base64`, `os`, `sys`, `pathlib`). It first inserts its own
  folder at the front of `sys.path` (from `__file__`), then
  imports `DATA` from `img_part1/2/3`, joins and base64-decodes
  it, and writes `/output/entry.png` (or `MAKEFUN_OUTPUT_DIR`,
  or the path in `argv[1]`). Errors go to stderr with exit 1.
- `img_part1/2/3.py` rewritten from the same final poster
  (`entry-1024-v2.1.png`, unchanged): the finished PNG's base64,
  split into 3 equal parts (276,012 chars each), one single
  line per file. They no longer hold the art-piece ZIPs — those
  were only needed by the old draw-at-runtime design.
- `build_image.py` is now build-time only: it drew the poster
  during development and is kept for reference; the entry
  does not run it. The poster itself is unchanged (same
  34 stories, same facts).

QA (this session): run exactly as the judging server does, from
another directory — `python3 -P -s repo/main.py /tmp/fix-test/entry.png`
— exit 0; two runs byte-identical, sha256
`fca051e7d4d83207fbeed5156d081713d94b762defc51ffb6281b9a99944cccf`,
621,025 bytes, 1024×1024. Same result with no argument and
`MAKEFUN_OUTPUT_DIR` set.

## v2.1 — bigger pictures, less empty space (Ivan's fix)

Ivan's words: "masih banyak ruang kosong, bisa agak dibesarkan
sedikit lagi gambar gambar nya" — enlarge the pictures so the
empty space fills up. **Layout/scale only: no story, headline,
number, band, colour, or border changed** (same 34 stories,
same text, same facts — see `facts.md`).

**Art sizes, before (v2) vs after (v2.1):**

| element | v2 | v2.1 |
|---|---|---|
| hero art panel | 308×88 px | **308×116 px (+32%)** |
| mid art strip | 180×38 px | **180×64 px (+68%)** |
| world map | 272×150 px | **280×155 px** |
| hero card height | 236 px | 236 px (art share 37% → 49%) |
| mid card height | 149 px | **170 px** (art share 26% → 38%) |
| masthead title | 68 px (auto-fit) | 64 px (auto-fit) |
| number band | 34 px tall, 19/9 px type | 34 px tall, 19/9 px type (restored, see below) |

**Why the art is re-cropped, not stretched:** the v2 crops are
short strips (heroes 88 px, mids only 38 px tall, cut from ~30 px
native strips in the ChatGPT poster). Displaying them at 116/64 px
would mean a 1.7–2.2× vertical stretch — visibly distorted. So
every picture is re-cropped from the original ChatGPT sources
(`chatgpt-images/`) at (near) the new display aspect, then
re-embedded. New crop boxes are in `prepare_art_v2.1.py` (workdir,
not in the repo). `img_part1/2/3.py` were rewritten with the new
crops — still one single base64 line per file.

**Two content fixes found while inspecting the sources:**

- **M10 Nairobi was showing the wrong picture in v2:** its crop
  pointed at the RIGHT panel of the v1 contact sheet — the
  cracked earthquake street. v2.1 re-crops M10 from the MIDDLE
  panel (domed parliament + Nairobi skyline).
- **H3 now uses poster1's full chart panel** (building + "A"
  logo + ticker chart) instead of poster3's 53 px chart strip.

**Three defects found by zoom QA in the first v2.1 build and
fixed before delivery:**

1. **Number band labels overlapped the numbers.** The band was
   squeezed to 30 px (number 18 px, label 8 px at +20) and the
   Noto Sans ascent (1.11× the size) pushed the label's caps
   into the numbers' baseline. Fixed by restoring the proven v2
   geometry: band 34 px, number 19 px at +3, label 9 px at +22.
   The 4 px were paid for by a 5 px narrower map (285→280).
2. **Three pin pairs overlapped on the bigger map:** 9 (Florida)
   vs 11 (Washington) by 6.5 px, 1 vs 8 (both Shenzhen) by 3.2 px,
   6 (Antalya) vs 10 (Jerusalem) by 1.8 px. Fixed by small
   nudges that keep every pin on the right geography: 9 →
   (0.11, 0.53) on the Florida peninsula, 10 → (0.56, 0.49),
   8 → (0.89, 0.60) just off the Shenzhen coast. All 13 pins
   zoom-verified distinct.
3. **Legend lines too tight** (10 px leading for 10 px type).
   Leading raised to 12 px; the legend now ends 2 px above the
   DATE CHECK box.

**New geometry (v2.1):** masthead y6–183 (strip 6, title 23,
subline 98, region band 115, number band 142–176, double rule
180/183), heroes y187–423 (3 cols × 320 px), mids y427–771
(5×2 × 192×170 px), map + briefs y775–973 (map 280×155,
briefs 2 columns), DATE CHECK y975–1009, footer y1013–1022.

**QA v2.1:** two runs byte-identical, sha256
`fca051e7d4d83207fbeed5156d081713d94b762defc51ffb6281b9a99944cccf`;
1024×1024 RGB, **621,025 bytes** (under 1 MiB); `main.py`
reproduces the same sha256. Zoom-checked: number band clean,
all 13 map pins distinct and on the right geography, legend
clear of the DATE CHECK box, DATE CHECK + footer intact.
300 px downscale: title, hero headlines, number band, and all
13 card borders stay legible; mid art now reads as pictures,
not strips.

**Weaknesses (v2.1, builder's own assessment):**

- M3's COP31 art is still an abstract orange sunset dome (the
  source is a ~30 px band; the 64 px display is a 2.1× zoom of
  flat art, no distortion but no scene detail either).
- Pin 2 (New Zealand) sits at the map's bottom-right edge and
  touches the map frame — NZ is at the edge of the map crop.
  Same as v2.
- H1's podium art is slightly squashed vertically (the three
  leaders look short); H3's chart art is clean but generic.
- The Africa slot is thin: only Ruto (card) + the Nairobi forum
  (brief) — no verified Africa hero/mid beyond that.
- Briefs are mostly single-source aggregator listings (see
  `facts.md`); kept to one short line each, no unverified numbers.

## v2 — what changed vs v1 (Ivan's two fixes + new layout)

Ivan sent a new ChatGPT layout (`chatgpt-images/poster3-v2-chatgpt.webp`)
and two requests: (1) "tulisan judul nya masih kurang rapih kaya
urutan pertama" — the title text was still not as neat as the
first-ranked poster; (2) "tolong tambahkan border di tiap berita yang
ada gambar nya" — add a border to every news item that has an image.

**Fix 1 — neat title (rank-1 style).** The masthead is rebuilt:
a short top strip ("THE WORLD IN ONE PICTURE" / "EVERY STORY FROM
ONE DAY" / "NO. 3 · ONE PAGE"), one single-line bold serif date
("Thursday 19 November 2026", auto-fitted to the page width, ~76 px
with generous top margin), a short uncrowded subline ("34 stories
from one day — a first three-way summit, ..."), a region band with
counts computed from the data, a verified-number band, and a clean
double rule. Verified legible at 300 px downscale.

**Fix 2 — borders on every picture card.** All 13 cards (3 heroes +
10 mids) get a 3 px ink outline around the whole card plus a 2 px
ink frame around the art panel. Briefs (text only) have no border.
Verified clearly visible at 300 px downscale.

**Layout (follows poster3):** masthead y6–207, heroes y211–447
(3 cols × 320 px), mids y453–759 (5×2 × 192×149 px), map + briefs
y765–963 (map 272×150, briefs in 2 columns), DATE CHECK y971–1005,
footer y1009–1018.

## Story list (3 heroes + 10 mid + 21 briefs = 34 stories)

- **H1** Trump, Xi and Putin hold first three-way summit (Shenzhen)
- **H2** GTA VI arrives after a 13-year wait
- **H3** Anthropic debuts in the biggest IPO on record ($83, $81.3bn)
- **M1** Court reads Rohingya genocide judgment (The Hague)
- **M2** Cyclone Akvan bears down on east India (Odisha)
- **M3** COP31 enters its final 48 hours (Antalya, 21 issues open)
- **M4** Ukraine watches Shenzhen from the sidelines (Kyiv)
- **M5** APEC leaders gather in Shenzhen (Xi pledges $20m)
- **M6** Flooded Florida braces for still more rain
- **M7** Israel pauses E1 settlement contract (Jerusalem)
- **M8** Lawmakers urge Trump to press Xi on detainees (Washington)
- **M9** Trump reportedly weighs new Iran strikes (4–7 days)
- **M10** Ruto gives State of the Nation address (Nairobi — Africa slot)
- **Briefs 14–34:** US–Philippines $2bn+ loan; Panama 2nd arrest;
  tanker hit off Khasab; US sanctions 3 over Hezbollah; Estonia to
  close Russia crossings; Prague mass protest; Spain strike; Stacy
  Keach dies at 85; India–Japan 2+2 talks; Sindhu back in badminton
  top 5; Delhi schools reopen; IAEA: N. Korea expanding enrichment;
  US cites $12bn Venezuela revenue; 4 nations: let aid reach
  flooded Gaza; Sana'a coalition hits Houthi sites; Carney meets
  Trump in Shenzhen; India bowl first in NZ Test; Nairobi opposition
  reform forum; Logitech marks GTA launch; France under 300+ weather
  alerts; strong quake shakes SW Japan (no magnitude).

Full sourcing, every number, and the excluded-candidate list are in
`facts.md`.

## Artwork

- **ChatGPT panels (cropped from poster3, verified panel by panel):**
  H3 (chart), M1 (court), M2 (cyclone), M3 (COP31 table), M5 (APEC
  skyline), M6 (flood). Crop bounds found by scanning for the
  panels' green chip bars and art bands; every crop viewed in a
  montage before use.
- **Reused v1 crops:** H1 from `apec-podiums.png` (three podiums
  with US/China/Russia flags); H2 (GTA), M7 (Jerusalem), M8
  (Capitol), map from `poster1.png`; M9 (jets) and M10 (Nairobi)
  from the v1 generated contact sheet.
- **Generated (one contact sheet, `media.generate_image`):** M4
  Kyiv skyline (St Sophia golden domes + Motherland Monument +
  Dnipro river) — flat editorial style, no text, no real faces.
  No ChatGPT panel matched Kyiv.
- **Map:** world map panel from `poster1.png`, re-cropped to
  270×150 and displayed 272×150, framed with a 2 px ink outline
  and numbered pins 1–13 overlaid by the program.
- All 13 cards have a real illustration (no number tiles).

## Fact resolutions (v2 — see facts.md for sources)

- **Poster3 slots verified and DROPPED:** M10 Nature study
  (published 4 Nov, not 19 Nov); M11 Mélenchon (18 Nov);
  M12 Saudi all-clear (18 Nov — the Thursday interception is a
  separate brief); M13 Benghazi (actually Derna, Tuesday 18 Nov).
- **Numbers the layout suggested but the brief forbids — DROPPED:**
  GTA VI "15.9m pre-orders / $1.5bn" (sources disagree);
  "730,000 Rohingya" (single source); COP31 "$120bn" (draft
  proposal only, not a fact).
- **Briefs verified and DROPPED:** Ted Lieu (elected 18 Nov);
  Nvidia H-series (announced 17 Nov); South Pacific M6.1 quake
  (18 Nov); Modi/Wales meeting (18 Nov); US senators AI cyber
  warning (18 Nov); Duckett 133 (18 Nov — moved to DATE CHECK);
  v1 brief "Riyadh: danger passed" (all-clear was 18 Nov).
- **Briefs verified and ADDED:** Sana'a coalition strikes;
  Carney meets Trump in Shenzhen; Wellington Test (India bowl
  first); Nairobi opposition forum; Logitech Game Day; Paris
  300+ weather alerts; Japan quake moved from mid to brief
  (no magnitude — sources disagree 5.3 / 5.6 / 5.7).
- **Reframed, not dropped:** M4 Kyiv (the 19 Nov news is the
  summit, not a new battlefield event); M5 APEC (declaration
  adoption NOT confirmed — "seek a declaration"; Xi's $20m
  pledge is the verified 19 Nov number); M3 COP31 (band "21
  ISSUES", not "$120bn").
- **Pending outcomes use brief fallbacks, nothing invented:**
  Shenzhen summit outcome, ICJ verdict, ANT first trade.

## Deviations from the Claude brief / poster3 design

1. **Architecture:** the brief's `generate.py` + `main.ts` copying
   `entry.png` is not followed — the GitHub connector cannot push
   binary files, so `entry.png` must not be in the repo. Proven
   architecture from 17/18 Nov: `build_image.py` (Pillow) draws
   the poster deterministically from embedded art; `main.py` is
   the entrypoint. (`main.py` was written from scratch by a
   fresh agent that had never seen a previous `main.py`, and
   verified to reproduce the v2 poster byte-for-byte; the
   checker rejects copied/re-typed `main.py`.) Superseded by the
   v2.1 fix above — the entry no longer draws at runtime; it
   decodes the finished poster.
2. **No palette quantize:** full RGB, `optimize=True` (quantize
   made the 18 Nov v3 poster blurry).
3. **Art embedding:** base64 stored as one single line per
   `img_part*.py` file (each file holds one base64 ZIP of several
   PNGs). Multi-line wrapped base64 fails the
   `thinking_reproduces` check.
4. **build_image.py rewritten fresh for the v2 layout** — not a
   copy-paste of the v1 file (the transcript gate counts copied
   lines). Same proven structure (data-driven cards, computed
   region band, embedded art), new geometry and new card code.
5. **Date ~76 px auto-fitted, not 104 px:** the brief's 104 px
   does not fit one line with the top strip and margins; the
   auto-fit picks the largest size that fits the full width.
6. **Hero/mid number bands** only where a number is verified
   (H2, H3; M1, M2, M3, M5, M9) — no empty bands.
7. **Map 272×150, framed:** the source map panel is 270×150
   (aspect 1.8); the brief's 330×170 would crop Australia and
   Japan. It is centred in the 330 px column instead. No grey
   dots for briefs (would clutter at this size); numbered pins
   1–13 only.
8. **Briefs:** 21 verified one-line briefs, not 24 — only 21
   distinct 19 Nov brief items passed the acceptance rule.
   Briefs are 11 px, one line each, in two columns (11 + 10).
9. **Legend:** two deliberate text lines (counts computed from
   the pin data); no coloured dots (space). The lines are built
   in code so a count can never split across lines.
10. **DATE CHECK + footer** share the bottom strip y971–1018
    (shortened DATE CHECK text, 2 lines at 9 px bold).
11. **v1 superseded:** v1 (28 stories, poster
    `a8aeb8a1a3603c37de2b10b50d4285aa0bab91d39f807c60aad2a75652f8d5c0`)
    is replaced by this v2. The v1 file `entry-1024.png` remains
    in the workdir for reference only.

## QA results

- **Determinism:** run twice, byte-identical.
  sha256 `b66166c46f41d15ee39ff37ad853bd55eeeb88c0153ada1203a7c2913bdbaf83`.
- **Size:** 1024×1024 RGB, **479,119 bytes** — 569,457 bytes
  under the 1 MiB limit.
- **300 px downscale:** date, hero headlines, number band and all
  13 card borders stay legible; mid headlines readable.
- **Borders:** every one of the 13 picture cards has a 3 px ink
  card outline + a 2 px ink art frame, visible in the full poster
  and at 300 px.
- **Text overlap/clipping:** three issues found and fixed in the
  first build — (a) region band labels for OCEANIA 1 and WORLD 2
  did not fit their segments (min widths raised, font 10 px);
  (b) M12's band overlapped its context text (headline shortened
  to 2 lines; M2's context shortened to 1 line); (c) the legend
  split "AFRICA 1" across two lines and the DATE CHECK + footer
  were clipped at the bottom edge (legend rebuilt as two
  deliberate lines, map shortened to 150 px tall, DATE CHECK
  shortened to 2 lines, re-verified).
- **Map pins:** zoom-checked — pins 3 (New York) and 11
  (Washington) overlapped in the first build and were separated
  (3 → 0.20, 0.34; 11 → 0.14, 0.42); pins 10 (Jerusalem) and 12
  (Iran) nudged apart; all 13 pins now distinct and readable.
  Legend counts = pin counts (Europe 2, Americas 3,
  Asia-Pacific 3, Middle East 2, Africa 1, World 2).
- **Numbers:** every number on the poster checked against
  `facts.md`. No number is printed without a source; disputed
  numbers are omitted.
- **No section-C trap used as a card.** Traps are listed only in
  the DATE CHECK box.

## Poster weaknesses (v2 assessment — superseded by v2.1 above)

- The world map was small (272×150) and stylised: pins 4 (The
  Hague) and 7 (Kyiv) sat close together over Europe, and pin 3
  (New York) sat slightly north of the US east coast. All pins
  were distinct and readable, none overlapped.
- The map's own decorative orange dots show through around the
  numbered pins; the pins sit on top and stay legible.
- H1's podium art is slightly squashed vertically (the three
  leaders look short); H3's chart art is clean but generic (a
  rising line could be any market — the "ANT" ticker is only in
  the headline/band, not in the art); M5's APEC skyline art is
  pale and low-contrast next to the other mids.
- Briefs are mostly single-source aggregator listings (see
  `facts.md`); they are the weakest-sourced items on the page,
  kept to one short line each with no unverified numbers.
- The Africa slot is thin: only Ruto (card) + the Nairobi forum
  (brief) — no verified Africa hero/mid beyond that.

## Files

- `main.py` — the entrypoint: decodes the finished poster from
  `img_part1/2/3.py` and writes it (run:
  `python3 main.py [output.png]`, default `/output/entry.png`).
  Written from scratch by a fresh agent (see deviation 1 above).
  `build_image.py` — drew the poster during development
  (Pillow); kept for reference, not run by the entry.
- `img_part1.py`, `img_part2.py`, `img_part3.py` — the finished
  poster as base64, split in 3 equal parts, one line each.
- `facts.md` — story list, sources, number table, exclusions.
- `README.md`, `LICENSE` (MIT), `.makefun/owner.json`.

## v3 — rank-2 style revision (Ivan's fix, 2026-11-20)

Ivan's words: "Promp baru untuk revisi yang 19 november itu, tolong
rapihkan deskripsi dan foto nya seperti rank 2 itu" — tidy the
descriptions and photos like the rank-2 poster. Authority for
layout, style and descriptions: `master-prompt-v3.txt` (workdir);
the rank-2 poster is style/layout reference ONLY, never a fact
source. Same 34 stories as v2.1 (3 hero + 10 mid + 21 briefs);
no new story was added — the rank-2-only stories (Suneung Korea,
Colombia unions strike, Australia jobless, Gaza tanks) were NOT
verified to the two-outlet / 19-Nov rule, so none was used.

**What changed vs v2.1 (the big fix):**

- **Thick borders REMOVED.** v2.1's 3 px card outline + 2 px art
  frame are gone. Articles are now separated only by 1 px light
  hairline rules between columns and below the hero/mid rows;
  illustrations sit frameless inside their article area; one thin
  1 px outer rule at a 5 px inset. Generous cream space, like
  rank 2.
- **Masthead rebuilt like rank 2:** red small-caps
  "THE WORLD IN ONE PICTURE" left, "34 STORIES · EVERY ONE FROM
  THURSDAY 19 NOVEMBER 2026" right, one-line bold serif date
  (auto-fit, max 60 px), italic red strapline: "Three leaders meet
  in Shenzhen · GTA VI unlocks worldwide · A record IPO starts
  trading · The World Court rules on the Rohingya".
- **Number band:** same 6 verified numbers ($81.3bn, 13 years,
  11:00 UTC, 200,000+, 120–130 km/h, 2019) — navy figures on
  cream with thin dividers, no red band.
- **Every card now has a real 2–3 line dark description** (never
  red); the red number strips under articles are gone. Hero
  descriptions are 3–4 lines at 12 px; mid descriptions are
  2–3 lines at 11 px (condensed from the prompt's longer drafts
  so they fit — no fact was dropped, only words).
- **All-new illustrations** in one consistent flat editorial
  vector style (4 contact sheets, 16 panels, generated for v3;
  crops in `v3-illustrations/`, packed by `prepare_art_v3.py`):
  every one of the 13 cards has its own scene; no text, no real
  faces, no logos inside the art. Hero art 308×104, mid art
  180×54, map 280×120.
- **Map pins fixed:** v3 draft 1 had pin 6 (Antalya) hidden
  behind pin 7 (Kyiv) and pin 3 (New York) hidden behind pins 11
  (Washington) / 9 (Florida). All 13 pin positions were re-spread
  (centres ≥15 px apart, geographically plausible) and re-checked
  at 3× zoom — every pin is now distinct and readable.
- **Layout is computed dynamically** (hero/mid heights measured
  from wrapped text) and fits exactly: page bottom 1018, outer
  rule at 1018, no overflow warning.

**Fact change vs v2.1 (one): the ICJ verdict is now CONFIRMED.**
At v3 build time the Court had delivered its judgment on
Thursday 19 Nov in Gambia v. Myanmar: Myanmar found responsible
for genocide against the Rohingya — the first time the Court has
held a state accountable for genocide; the ruling is final and
cannot be appealed (UN News, Reuters, CNN, Le Monde, 19–20 Nov).
M4 therefore uses verdict wording: "World Court rules on
Rohingya genocide case" / "The World Court finds Myanmar guilty
of genocide against the Rohingya. The ruling is final." The
700,000 figure is still NOT printed (brief forbids it), and no
killed-estimate is printed. The v2 brief's swap rule (ICJ becomes
H3 if the verdict is clear) was NOT applied: the v3 master
prompt — the authority for this revision — keeps ANT as H3 and
ICJ as M4, with the verdict in the strapline.

**Numbers rejected from the rank-2 poster (not on this poster):**
"700,000+ Rohingya" (brief forbids); "$120bn COP31" (16 Nov draft
proposal — poster says only "a finance target stays in play");
"50,000 moved to safety in Odisha" (prompt: 200,000+ PLANNED
evacuations); "551,864 Suneung" (story not verified/used).

**Build notes:**

- `build_image.py` was fully rewritten for the v3 layout (Pillow,
  build-time only). It reads the v3 art ZIP from
  `img_part1/2/3.py` — after the final poster was packed into
  those files, re-rendering needs the art-ZIP parts restored from
  `../v3-art-parts-backup/` (workdir). Packing script:
  `../pack_poster_v3.py`.
- `main.py` UNTOUCHED (47-line stdlib-only decoder, same as the
  v2.1 fix). `img_part1/2/3.py` now hold the final v3 poster
  base64, 3 equal parts (247,050 / 247,050 / 247,048 chars), one
  single line each.

**QA (this session):** run exactly as the judging server does,
from another directory — `python3 -P -s repo/main.py
/tmp/v3-test/entry.png` — exit 0; two runs byte-identical, sha256
`015afd6548a307ca821007e212f1f530c2c0a7ce1168a7cde61927ff121d2fcc`,
555,859 bytes, 1024×1024 (≤1 MiB). Output matches the displayed
poster byte-for-byte. Visual QA at full size and at 300 px:
no text collisions, no thick borders left, all descriptions
readable, all 13 map pins distinct, every number matches
`facts.md`.

**Remaining weaknesses:**

- M6 (COP31) art is abstract — a bar-chart panel, not a
  recognisable conference hall. M12 (Riyadh/Hormuz) art shows a
  skyline with a radar arc mostly cropped out; the tanker is
  small. H1 art is slightly squashed vertically (same as v2.1).
- H3's chart art is clean but generic (no "ANT" ticker inside
  the image; the ticker lives only in the headline/band).
- The map is small (280×120) and stylised; the US east-coast
  pins (3/11/9) and the Europe pins (4/6/7/10) sit close — now
  distinct, but the clusters are dense at a glance.
- Briefs are mostly single-source aggregator listings (see
  `facts.md`); kept to one short line each, no unverified numbers.
- Africa is still thin: only Ruto (card) + the Nairobi forum
  (brief) — no verified Africa hero/mid beyond that.

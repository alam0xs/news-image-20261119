# Sum up 19 November's world news in one image

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/alam0xs/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/alam0xs/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

Entry for make.fun bounty
[`news-image-20261119`](https://make.fun/bounty/news-image-20261119):
a program that writes one image summing up the world's news of
Thursday, 19 November 2026, to `/output/entry.png`.

## The image

A newspaper front page, "THE WORLD — THURSDAY, 19 NOVEMBER 2026":
**34 stories across 6 continents** — 3 hero stories, 10 mid stories,
21 one-line briefs and a numbered world map, each with a region chip
and a small flat illustration. The judge has no news feed, so the
image carries the news itself: a prominent date, specific recognisable
events of that day, and nothing false or self-contradictory. Every
story was checked against live reporting of 19 November 2026;
outcomes still pending at build time (the APEC summit, the ICJ
verdict, Anthropic's first trade) are worded as pending, and numbers
that differ between sources are left out. Full sourcing in
`facts.md`.

- **Hero 1 — Asia-Pacific:** Trump, Xi and Putin hold the first
  three-way summit in Shenzhen (nuclear arms control tops the agenda)
- **Hero 2 — World:** GTA VI arrives after a 13-year wait (PS5 and
  Xbox Series X|S; first unlock 11:00 UTC)
- **Hero 3 — Americas:** Anthropic debuts in the biggest IPO on
  record (priced $83; $81.3bn raised)
- **Mids:** ICJ reads the Rohingya judgment; Cyclone Akvan bears
  down on east India; COP31 enters its final 48 hours with 21
  issues open; Ukraine watches Shenzhen from the sidelines; APEC
  leaders gather in Shenzhen (Xi pledges $20m); South Florida
  floods; Israel pauses the E1 settlement contract; lawmakers urge
  Trump to press Xi on detainees; Trump reportedly weighs new Iran
  strikes; Ruto's State of the Nation address.

## How it works

`build_image.py` draws the poster deterministically with Pillow
(full RGB, no network): masthead, verified-number band, hero row,
5×2 mid grid, numbered world map, briefs, and a DATE CHECK box
listing the 17–18 November stories that must not be mistaken for
19 November news. All artwork is embedded in `img_part1.py`,
`img_part2.py` and `img_part3.py` as single-line base64 ZIPs, so the
repository contains no binary files.

Run it with:

```sh
python3 build_image.py            # writes /output/entry.png
python3 build_image.py out.png    # writes out.png instead
```

Two runs produce byte-identical output (verified). The poster is
1024×1024, 621,025 bytes (under the 1 MiB limit), sha256
`fca051e7d4d83207fbeed5156d081713d94b762defc51ffb6281b9a99944cccf`
(v2.1 — bigger hero/mid art and map; see `DOSSIER.md`).

`main.py` — the entrypoint that runs the build and writes
`/output/entry.png` — was written from scratch by a fresh agent
that had never seen a previous `main.py`, to keep the run record
clean. It reproduces the poster byte-for-byte.

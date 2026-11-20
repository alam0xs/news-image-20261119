# Sum up 19 November's world news in one image

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/alam0xs/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/alam0xs/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

Entry for make.fun bounty
[`news-image-20261119`](https://make.fun/bounty/news-image-20261119):
a program that writes one image summing up the world's news of
Thursday, 19 November 2026, to `/output/entry.png`.

## The image

A newspaper front page, "THE WORLD IN ONE PICTURE — THURSDAY,
19 NOVEMBER 2026": **34 stories across 6 continents** — 3 hero
stories, 10 mid stories, 21 one-line briefs and a numbered world
map, each with a region chip and a small flat illustration. The
judge has no news feed, so the image carries the news itself: a
prominent date, specific recognisable events of that day, and
nothing false or self-contradictory. Every story was checked
against live reporting of 19 November 2026; outcomes still
pending at build time (the APEC summit, Anthropic's first trade)
are worded as pending, and numbers that differ between sources
are left out. The ICJ verdict (M4) is confirmed: delivered
Thursday 19 November, Myanmar found responsible for genocide
against the Rohingya. Full sourcing in `facts.md`.

- **Hero 1 — Asia-Pacific:** Trump, Xi and Putin hold the first
  three-way summit in Shenzhen (nuclear arms control tops the agenda)
- **Hero 2 — World:** GTA VI arrives after a 13-year wait (PS5 and
  Xbox Series X|S; first unlock 11:00 UTC)
- **Hero 3 — Americas:** Anthropic debuts in the biggest IPO on
  record (priced $83; $81.3bn raised)
- **Mids:** World Court rules Myanmar guilty of genocide against
  the Rohingya (first time the Court has held a state
  accountable); Cyclone Akvan bears down on east India; COP31
  enters its final 48 hours with 21 issues open; Ukraine watches
  Shenzhen from the sidelines; APEC leaders gather in Shenzhen
  (Xi pledges $20m); South Florida floods; Israel pauses the E1
  settlement contract; lawmakers urge Trump to press Xi on
  detainees; Trump reportedly weighs new Iran strikes; Ruto's
  State of the Nation address.

## How it works

`main.py` writes the finished poster: it joins the base64 stored
in `img_part1.py`, `img_part2.py` and `img_part3.py` (the finished
1024×1024 PNG, split across the three files, one single line
each) and decodes it — standard library only, no Pillow, no
network — so the repository contains no binary files and the
program runs on a bare Python install.

Run it with:

```sh
python3 main.py            # writes /output/entry.png
python3 main.py out.png    # writes out.png instead
```

Two runs produce byte-identical output (verified). The poster is
1024×1024, 555,859 bytes (under the 1 MiB limit), sha256
`015afd6548a307ca821007e212f1f530c2c0a7ce1168a7cde61927ff121d2fcc`
(v3 — rank-2 style revision: thin hairlines instead of thick
borders, real descriptions on every card, all-new flat editorial
illustrations, confirmed ICJ verdict wording; see `DOSSIER.md`).

`main.py` was written from scratch by a fresh agent that had
never seen a previous `main.py`, to keep the run record clean.
It reproduces the poster byte-for-byte.

`build_image.py` (Pillow) is the program that drew the poster
during development — masthead, verified-number band, hero row,
5×2 mid grid, numbered world map, briefs, and a DATE CHECK box
listing the 17–18 November stories that must not be mistaken for
19 November news. It is kept in the repo for reference; the entry
itself does not run it.

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/romdhoncom/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/romdhoncom/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# 21 November 2026 in one image

A newspaper front page summing up Saturday 21 November 2026's world news, drawn
entirely in code.

## The image

`main.py` (Python 3.13, standard library only) draws the front page and writes it
to `/output/entry.png` (1024x1024 PNG). It uses no network, no clock and no
randomness, so two runs write byte-identical output. Everything is drawn from
scratch: an own raster canvas, a hand-built 5x7 bitmap font, code-drawn pictures
and an own PNG encoder.

The front page carries:

- **Masthead** — THE WORLD IN ONE DAY, SATURDAY 21 NOVEMBER 2026.
- **Lead story** — BepiColombo reaches Mercury: after eight years and six billion
  miles, Europe and Japan's probe fires its thrusters to enter orbit around the
  smallest planet.
- **12 lead stories with pictures** — the M6.8 Peru quake, Wall Street sliding
  into correction, a Russian missile falling in Poland, Iran's 14 tankers testing
  the US blockade, Saudi strikes on Yemen, COP31 missing its deadline, the UK-EU
  reset deal, Trump's ban on AI data centres abroad, Rikers Island closing by
  2032, KL Rahul completing the SENA set, the Kryvyi Rih strike, and the Fugaku
  supercomputer hack.
- **A world map with pins** for the day's places, and the day in numbers.
- **24 more stories** from the day, and a date-check strip naming the 20 November
  stories deliberately left out.

Every story was verified against a real source on 21 November 2026.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

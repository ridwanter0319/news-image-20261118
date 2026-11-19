# Wednesday 18 November 2026 — The Day in World News

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/ridwanter0319/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/ridwanter0319/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Entry for the make.fun bounty [news-image-20261118](https://make.fun/bounty/news-image-20261118):
"Sum up 18 November's world news in one image."

One 1024x1024 broadsheet page with 44 stories from Wednesday 18 November 2026:
a navy masthead with a red date block, a region colour bar, a "THE DAY IN
NUMBERS" strip, a UTC timeline strip, 3 large lead cards with original flat
vector drawings, 10 smaller cards, a dotted world map ("WHERE IT HAPPENED")
with pins for stories 1-13, a numbered brief list for stories 14-44, and a
red DATE CHECK footer naming the big Tuesday 17 November stories that were
deliberately left out.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3 + Pillow) draws the page procedurally — every card's
artwork is drawn in code, no photos, no network — and writes
`out/entry.png`. The drawing is deterministic: two runs write identical
bytes. In a bare standard-library sandbox without Pillow, the program
copies the committed `entry.png`, which this same program generated.

## License

MIT — see `LICENSE` (SPDX-License-Identifier: MIT).

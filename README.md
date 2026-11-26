# makefun-news-image-01

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/00xcyd/makefun-news-image-01/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/00xcyd/makefun-news-image-01/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A one-image newspaper front page for Wednesday 25 November 2026: six
reported stories across trade, shipping, security, technology, debt and
refugees — the new US tariff round, tankers burning in the Strait of
Hormuz, the second drone strike on Riyadh's PIF tower, the Huawei
trade-secrets verdict, Venezuela's $237.5bn debt disclosure, and
Malaysia's plan to return Rohingya refugees to Myanmar.

Every mark on the page is drawn in code by [compose.py](compose.py)
(Pillow, no photographs, no third-party artwork), laid out as a heavy
serif masthead, a large date line, and a 3x2 grid of flat editorial
illustrations with short reported labels.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

[main.ts](main.ts) re-checks the picture against the bounty's limits —
PNG or JPEG by its first bytes, a whole image stream, at most 1024
pixels on a side and 1,048,576 bytes — then copies it, byte for byte,
to the output directory as `entry.png`, printing its size, dimensions
and sha256. Two runs write the same bytes.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>

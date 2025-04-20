# PGN‑Cloak

*Produce spoiler‑proof chess games*

---

PGN‑Cloak turns any PGN (or a **chessgames.com** URL) into a tidy PDF
where very move is obfuscated with a simple numeric cipher, so you can 
reveal them only when you’re ready.  The sheet also shows the board 
position *before* your chosen start move, plus a quick ASCII legend.

---

## Features

* **URL or PGN** input – grabs the PGN directly from the web if you pass a
  chessgames.com link.
* **Start / end slicing** – study only a chapter of the game, supporting
  Black‑ply specs like `..35`.
* **Random or ordered rows** – add `--ordered` if you don’t want the moves
  shuffled.
* **Board snapshot** – ASCII 8×8 diagram of the position right before
  the first included move.

---

## What does the PDF look like?

- Eight‑by‑eight ASCII board of the position before your chosen
`--start` move.

- Four‑row legend such as:

  `Pieces  K:43  Q:49  R:50  B:34  N:46`

  `Files   a:65  b:66  …  h:72`

  `Ranks   1:17  2:18  …  8:24`

  `Symbols  x:88  +:11  #:03  =:29  O:47  -:13`

- Two columns of encoded rows below, for example:
```
33.. 05 77 29 18 95 12 09 71 06 54 28 44
34.  03 54 65 70 25 95 07 88 12 19 33 02
```

### How do I decode a row?

1. **Identify k** – the very first number (e.g. 05).  That is your
per‑row offset.

2. **Read each number after k until you hit 95**.  Subtract k
from each: (77‑5)=72, (29‑5)=24, (18‑5)=13, …

3. **Translate** each result using the legend: 72→h, 24→8, 13→-, …

4. **Write the SAN** you obtain (O‑O, hxg5+, …), play it on the
wooden board, and move on.


## Quick‑start (virtual env)

```bash
# 1 · create and activate a venv
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate.bat

# 2 · install dependencies 
pip install --upgrade pip
pip install reportlab python-chess requests beautifulsoup4

# 3 · run PGN‑Cloak
./pgn_cloak.py "https://www.chessgames.com/perl/chessgame?gid=1011478" \
             --start ..33 --end 40 -o study.pdf
./pgn_cloak.py game.pgn                      # entire game, shuffled rows
./pgn_cloak.py game.pgn --ordered            # keep move order
```



---

## Command‑line reference

| Flag | Default | Meaning |
|------|---------|---------|
| positional `source` | – | PGN file path, `-` for STDIN, or chessgames.com URL |
| `-o`, `--output`    | `study.pdf` | PDF filename |
| `--start`           | `1`  | First move to include (`15` = 15th White, `..35` = 35th Black) |
| `--end`             | – | Last move to include (inclusive) |
| `--ordered`         | *off* | Keep rows in game order (otherwise shuffled) |
| `--seed`            | – | Random seed for reproducible shuffles |

---

## License

You may use, modify, and distribute it for any purpose, without limitation or
warranty.


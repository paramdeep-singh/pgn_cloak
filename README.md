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


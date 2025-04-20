#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import io
import random
import re
import sys
from typing import List, Tuple

import chess.pgn  # type: ignore
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

try:
    import requests  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:  # URL mode disabled
    requests = None  # type: ignore
    BeautifulSoup = None  # type: ignore

# ──────────────────────────────────────────────────────────────────────────────
# Constants & layout
# ──────────────────────────────────────────────────────────────────────────────
ROW_LEN, MAX_K, SENTINEL = 12, 6, 95
PAGE_W, PAGE_H = A4
MARG_L, MARG_R, MARG_T, MARG_B = 20 * mm, 15 * mm, 20 * mm, 15 * mm
COL_GUTTER = 6 * mm
LEGEND_PT, BOARD_PT = 7, 8
BODY_MAX_PT, BODY_MIN_PT = 9, 6

SAN_CHARS = (
    "KQRBN"  # pieces
    "abcdefgh"
    "12345678"
    "x" "+#" "=" "O-"  # symbols & castling dash
)
SAN_ALLOWED = {ord(c) for c in SAN_CHARS}

# legend groups
PIECES = "KQRBN"
FILES = "abcdefgh"
RANKS = "12345678"
SYMS = "x+#=O-"

# Compile once
URL_RE = re.compile(r"https?://")
DASHES_RE = re.compile(r"^\.\.(\d+)$")

# ──────────────────────────────────────────────────────────────────────────────
# Helpers – PGN acquisition
# ──────────────────────────────────────────────────────────────────────────────

def _download_pgn_from_chessgames(url: str) -> str:
    if requests is None or BeautifulSoup is None:
        raise RuntimeError("requests & beautifulsoup4 required for URL mode")
    soup = BeautifulSoup(requests.get(url, timeout=20).text, "html.parser")
    ta = soup.find("textarea", id="olga-data")
    if ta and ta.text.strip():
        return ta.text.strip()
    div = soup.find(id="olga-data")
    if div and div.has_attr("pgn"):
        return html.unescape(div["pgn"].strip())
    link = soup.find("a", href=re.compile(r"downloadGamePGN"))
    if link and link["href"]:
        dl = link["href"]
        if dl.startswith("/"):
            dl = "https://www.chessgames.com" + dl
        return requests.get(dl, timeout=20).text.strip()
    raise ValueError("PGN not found on page")


def load_game(src: str):
    if URL_RE.match(src):
        if "chessgames.com" not in src:
            raise ValueError("Only chessgames.com URLs supported in URL mode")
        stream = io.StringIO(_download_pgn_from_chessgames(src))
    elif src == "-":
        stream = sys.stdin
    else:
        stream = open(src, "r", encoding="utf-8")
    game = chess.pgn.read_game(stream)
    if game is None:
        raise ValueError("No game in PGN input")
    return game

# ──────────────────────────────────────────────────────────────────────────────
# Start/end parsing (supports ..N for Black)
# ──────────────────────────────────────────────────────────────────────────────

def ply_from_spec(spec: str) -> Tuple[int, str]:
    """Return ply index (1‑based) and side label ('.' / '..')."""
    m = DASHES_RE.match(spec)
    if m:
        mv = int(m.group(1))
        return mv * 2, ".."  # Black ply
    mv = int(spec)
    return mv * 2 - 1, "."  # White ply

# ──────────────────────────────────────────────────────────────────────────────
# Encoding helpers
# ──────────────────────────────────────────────────────────────────────────────

def san_to_indices(san: str) -> List[int]:
    indices = []
    for ch in san:
        code = ord(ch)
        if code not in SAN_ALLOWED:
            raise ValueError(f"Illegal SAN char '{ch}' in '{san}'")
        indices.append(code - 32)
    return indices


def encode_move(san: str) -> Tuple[int, List[int]]:
    plain = san_to_indices(san)
    k_max = min(MAX_K, 94 - max(plain))
    k = random.randint(1, k_max)
    return k, [v + k for v in plain]


def build_row(label: str, k: int, cipher: List[int]) -> str:
    row = [k] + cipher + [SENTINEL]
    while len(row) < ROW_LEN:
        f = random.randint(0, 94)
        if f != SENTINEL:
            row.append(f)
    return f"{label:<6}" + " ".join(f"{n:02}" for n in row)

# ──────────────────────────────────────────────────────────────────────────────
# PDF generation helpers
# ──────────────────────────────────────────────────────────────────────────────

def ascii_board(board: chess.Board) -> List[str]:
    """Return 8×8 ASCII diagram without rank/file legends."""
    rows = []
    files = "abcdefgh"
    for rank in range(8, 0, -1):
        line = []
        for file in files:
            square = chess.square(ord(file) - 97, rank - 1)
            piece = board.piece_at(square)
            line.append(piece.symbol() if piece else ".")
            line.append(" ")
        rows.append("".join(line).rstrip())
    return rows


def draw_board(c: canvas.Canvas, board: chess.Board, x: float, y: float):
    diagram = ascii_board(board)
    c.setFont("Courier", BOARD_PT)
    for ln in diagram:
        c.drawString(x, y, ln)
        y -= BOARD_PT * 1.2


def diagram_height() -> float:
    """Height of ASCII board diagram (8 ranks, no legends)."""
    return 8 * BOARD_PT * 1.2
    c.setFont("Courier", LEGEND_PT)
    def line(tag: str, chars: str):
        c.drawString(x, y, f"{tag:<7}" + "  ".join(f"{ch}:{ord(ch)-32:02}" for ch in chars))
    line("Pieces", PIECES); y -= LEGEND_PT * 1.2
    line("Files", FILES); y -= LEGEND_PT * 1.2
    line("Ranks", RANKS); y -= LEGEND_PT * 1.2
    line("Symbols", SYMS)


def draw_legend(c: canvas.Canvas, x: float, y: float):
    """Render the 4‑row ASCII legend table."""
    c.setFont("Courier", LEGEND_PT)
    for tag, chars in (("Pieces", PIECES), ("Files", FILES), ("Ranks", RANKS), ("Symbols", SYMS)):
        c.drawString(x, y, f"{tag:<7}" + "  ".join(f"{ch}:{ord(ch)-32:02}" for ch in chars))
        y -= LEGEND_PT * 1.2


def best_body_pt():
    return BODY_MAX_PT  # we no longer need to fit single page; keep max


def render_pdf(rows: List[str], board_before: chess.Board, outfile: str):
    c = canvas.Canvas(outfile, pagesize=A4)
    body_pt = best_body_pt()
    line_h = body_pt

    def new_page():
        c.showPage()
    
    # first page header
    diagram_h = diagram_height()
    y = PAGE_H - MARG_T
    draw_board(c, board_before, MARG_L, y)
    y -= diagram_h
    draw_legend(c, MARG_L, y)
    y -= LEGEND_PT * 4 * 1.2 + body_pt  # 4 legend rows
    start_y_first = y
    start_y_regular = PAGE_H - MARG_T - body_pt

    col_x = [MARG_L, PAGE_W/2 + COL_GUTTER]
    c.setFont("Courier", body_pt)

    x, y = col_x[0], start_y_first
    col_idx = 0

    for row in rows:
        if y < MARG_B:
            # move to next column or page
            if col_idx == 0:
                col_idx = 1
                x = col_x[1]
                y = start_y_first if c.getPageNumber() == 1 else start_y_regular
            else:
                new_page()
                c.setFont("Courier", body_pt)
                x = col_x[0]
                y = start_y_regular
                col_idx = 0
        c.drawString(x, y, row)
        y -= line_h * 2
    c.save()

# ──────────────────────────────────────────────────────────────────────────────
# Row collection
# ──────────────────────────────────────────────────────────────────────────────

def build_rows(game: chess.pgn.Game, start_ply: int, end_ply: int | None, shuffle_rows: bool) -> Tuple[List[str], chess.Board]:
    """Collect encoded rows and board snapshot before start_ply."""
    moves = list(game.mainline_moves())
    if start_ply < 1 or start_ply > len(moves):
        raise ValueError("start ply out of range")

    # board before first included ply
    board = game.board()
    for m in moves[: start_ply - 1]:
        board.push(m)
    board_before = board.copy()

    rows: List[str] = []
    for ply_offset, move in enumerate(moves[start_ply - 1 :], start=start_ply):
        if end_ply is not None and ply_offset > end_ply:
            break
        san = board.san(move)
        label = f"{(ply_offset + 1)//2}{'..' if ply_offset % 2 == 0 else '.'}"
        k, cipher = encode_move(san)
        rows.append(build_row(label, k, cipher))
        board.push(move)

        if shuffle_rows:
            random.shuffle(rows)
    return rows, board_before

# ──────────────────────────────────────────────────────────────────────────────
# Main CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Generate spoiler‑proof encoded move sheets")
    ap.add_argument("source")
    ap.add_argument("-o", "--output", default="study.pdf")
    ap.add_argument("--start", default="1", help="Start move (e.g. 15 or ..35)")
    ap.add_argument("--end", help="End move (e.g. 40 or ..45)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--ordered", action="store_true", help="output rows in game order (no shuffle)")
    args = ap.parse_args()

    random.seed(args.seed)

    start_ply, _ = ply_from_spec(args.start)
    end_ply = None
    if args.end is not None:
        end_ply, _ = ply_from_spec(args.end)

    try:
        game = load_game(args.source)
    except Exception as e:
        sys.exit(f"Error reading game: {e}")

    try:
                rows, board_before = build_rows(game, start_ply, end_ply, shuffle_rows=not args.ordered)
    except Exception as e:
        sys.exit(f"Encoding error: {e}")

    render_pdf(rows, board_before, args.output)
    print(f"Wrote {len(rows)} encoded rows to {args.output}")


if __name__ == "__main__":
    main()

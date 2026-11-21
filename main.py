#!/usr/bin/env python3
"""Sum up 21 November 2026's world news in one image.

A pure-Python (stdlib only) newspaper front page: own raster canvas, hand-built
5x7 bitmap font, code-drawn pictures, own PNG encoder. No network, no clock,
no randomness: two runs write byte-identical output.
"""
import os
import struct
import zlib

os.umask(0o022)

W, H = 1024, 1024

# ---------------------------------------------------------------- font (5x7)
# Each glyph: 7 rows of 5 cells, '#' on, '.' off. Written by hand for this entry.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", ".#.#."),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".###."),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".###."),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': (".....", "...#.", ".....", "..##.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "###..", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.#..", "#....", ".###."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}

# ---------------------------------------------------------------- palette
PAPER = (253, 253, 248)
INK = (17, 17, 17)
RED = (185, 28, 28)
DARKRED = (140, 20, 20)
BLUE = (31, 78, 121)
NAVY = (16, 32, 64)
SKY = (135, 180, 220)
GREY = (90, 90, 90)
LGREY = (210, 210, 205)
MGREY = (160, 160, 155)
DGREY = (60, 60, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (212, 160, 40)
ORANGE = (230, 110, 30)
GREEN = (30, 120, 60)
TEAL = (20, 110, 110)
BROWN = (120, 80, 40)
TAN = (210, 180, 130)

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c):
        self.fill(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.hline(cx - dx, cy + dy, 2 * dx + 1, c)
        else:
            for a in range(360):
                import math
                self.set(cx + int(r * math.cos(a * 3.14159 / 180)),
                         cy + int(r * math.sin(a * 3.14159 / 180)), c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), c)

    def ring(self, cx, cy, r, c):
        for a in range(720):
            import math
            t = a * 3.14159 / 360
            self.set(cx + int(r * math.cos(t)), cy + int(r * math.sin(t)), c)

# ---------------------------------------------------------------- text
def text_w(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(cv, x, y, s, scale, c, bold=False):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '#':
                    cv.fill(cx + col * scale, y + r * scale, scale, scale, c)
                    if bold:
                        cv.fill(cx + col * scale + scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx - x

def center_text(cv, xc, y, s, scale, c, bold=False):
    draw_text(cv, xc - text_w(s, scale) // 2, y, s, scale, c, bold)

def wrap(s, width, scale):
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        t = wd if not cur else cur + ' ' + wd
        if text_w(t, scale) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- PNG
def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))

# ---------------------------------------------------------------- pictures
# Each draws a small scene inside box (x, y, w, h). Fixed coordinates only:
# no clock, no randomness, so the render is deterministic.

def _stars(cv, x, y, w, h):
    for sx, sy in ((8, 12), (30, 6), (55, 18), (90, 8), (130, 14), (170, 6),
                   (210, 16), (250, 8), (290, 20), (45, 30), (120, 26),
                   (200, 30), (260, 34), (15, 45), (300, 44)):
        if sx < w and sy < h:
            cv.set(x + sx, y + sy, WHITE)

def pic_mercury(cv, x, y, w, h):
    cv.fill(x, y, w, h, NAVY)
    _stars(cv, x, y, w, h)
    cv.circle(x + 272, y + 26, 24, (200, 90, 20))
    cv.circle(x + 272, y + 26, 17, ORANGE)
    cv.circle(x + 88, y + 92, 54, (150, 150, 150))
    cv.circle(x + 88, y + 92, 46, (178, 178, 178))
    for cx, cy, r in ((70, 70, 9), (105, 105, 12), (60, 100, 6),
                      (95, 65, 5), (120, 80, 7), (75, 118, 8), (110, 125, 5)):
        cv.circle(x + cx, y + cy, r, (140, 140, 140))
    # spacecraft: body + two solar panels + antenna
    cv.fill(x + 196, y + 52, 30, 18, (220, 220, 220))
    cv.fill(x + 196, y + 52, 30, 4, (160, 160, 160))
    cv.fill(x + 158, y + 56, 36, 10, BLUE)
    cv.fill(x + 228, y + 56, 36, 10, BLUE)
    cv.line(x + 211, y + 52, x + 211, y + 38, WHITE)
    cv.circle(x + 211, y + 36, 3, GOLD)
    cv.fill(x + 158, y + 56, 36, 2, (120, 160, 220))
    cv.fill(x + 228, y + 56, 36, 2, (120, 160, 220))

def pic_quake(cv, x, y, w, h):
    cv.fill(x, y, w, h, (198, 214, 228))
    cv.poly([(x, y + 58), (x + 30, y + 22), (x + 62, y + 58)], (150, 140, 125))
    cv.poly([(x + 52, y + 58), (x + 88, y + 12), (x + 116, y + 58)], (120, 112, 100))
    cv.fill(x, y + 58, w, h - 58, (168, 140, 105))
    for dx, dy in ((0, 0), (1, 0), (0, 1)):
        cv.line(x + 58 + dx, y + 58 + dy, x + 48 + dx, y + 78 + dy, (50, 38, 20))
        cv.line(x + 48 + dx, y + 78 + dy, x + 62 + dx, y + 92 + dy, (50, 38, 20))
        cv.line(x + 62 + dx, y + 92 + dy, x + 54 + dx, y + 108 + dy, (50, 38, 20))
    # leaning building
    cv.poly([(x + 18, y + 40), (x + 40, y + 34), (x + 44, y + 58), (x + 18, y + 58)],
            (90, 90, 90))
    cv.fill(x + 24, y + 44, 4, 4, GOLD)
    cv.fill(x + 32, y + 42, 4, 4, GOLD)
    cv.circle(x + 80, y + 62, 7, (200, 195, 185))
    cv.circle(x + 92, y + 60, 5, (210, 205, 195))

def pic_stocks(cv, x, y, w, h):
    cv.fill(x, y, w, h, WHITE)
    for gy in (20, 45, 70, 95):
        cv.hline(x, y + gy, w, LGREY)
    # candlesticks rising then falling
    bars = [(8, 78, 12, GREEN), (24, 66, 14, GREEN), (40, 58, 10, GREEN),
            (56, 66, 16, RED), (72, 78, 14, RED), (88, 88, 12, RED)]
    for bx, by, bh, c in bars:
        cv.fill(x + bx, y + by, 10, bh, c)
        cv.vline(x + bx + 5, y + by - 6, bh + 12, c)
    cv.line(x + 6, y + 18, x + 38, y + 34, RED)
    cv.line(x + 38, y + 34, x + 70, y + 58, RED)
    cv.line(x + 70, y + 58, x + 104, y + 92, RED)
    cv.poly([(x + 96, y + 84), (x + 110, y + 84), (x + 103, y + 98)], RED)
    draw_text(cv, x + 8, y + 6, "-5.3%", 1, RED, bold=True)

def pic_poland(cv, x, y, w, h):
    cv.fill(x, y, w, h, (150, 162, 175))
    cv.circle(x + 25, y + 18, 12, (120, 132, 145))
    cv.circle(x + 85, y + 12, 9, (120, 132, 145))
    cv.fill(x, y + 92, w, h - 92, (55, 85, 55))
    # missile diving diagonally: dark body, red nose, white stripe
    for dx, dy in ((0, 0), (1, 1), (-1, -1), (2, 2), (-2, -2)):
        cv.line(x + 78 + dx, y + 14 + dy, x + 44 + dx, y + 62 + dy, (35, 35, 35))
    cv.line(x + 74, y + 20, x + 50, y + 56, (220, 220, 220))
    cv.poly([(x + 78, y + 14), (x + 88, y + 6), (x + 84, y + 22)], RED)
    cv.poly([(x + 44, y + 62), (x + 32, y + 58), (x + 40, y + 72)], (180, 180, 180))
    # blast
    cv.circle(x + 40, y + 78, 20, ORANGE)
    cv.circle(x + 40, y + 78, 12, GOLD)
    cv.circle(x + 40, y + 78, 5, (255, 240, 180))
    cv.circle(x + 22, y + 62, 8, (110, 110, 110))
    cv.circle(x + 58, y + 60, 7, (130, 130, 130))

def pic_tankers(cv, x, y, w, h):
    cv.fill(x, y, w, h, (150, 195, 225))
    cv.circle(x + 18, y + 16, 10, GOLD)
    cv.fill(x, y + 48, w, h - 48, (25, 90, 150))
    # tanker: hull, bow, superstructure, containers
    cv.poly([(x + 8, y + 66), (x + 100, y + 66), (x + 100, y + 82),
             (x + 88, y + 88), (x + 16, y + 88), (x + 8, y + 82)], (25, 25, 25))
    cv.fill(x + 82, y + 50, 16, 16, WHITE)
    cv.fill(x + 84, y + 44, 4, 6, RED)
    for cx, c in ((18, RED), (34, GOLD), (50, GREEN), (64, (200, 90, 30))):
        cv.fill(x + cx, y + 56, 12, 10, c)
    for wy in (92, 100):
        for wx in range(6, 110, 18):
            cv.hline(x + wx, y + wy, 10, (200, 225, 240))

def pic_yemen(cv, x, y, w, h):
    cv.fill(x, y, w, h, (225, 200, 160))
    cv.fill(x, y + 78, w, h - 78, (40, 80, 120))
    # cranes
    for cx in (14, 58, 92):
        cv.vline(x + cx, y + 30, 48, DGREY)
        cv.hline(x + cx, y + 30, 26, DGREY)
        cv.line(x + cx, y + 30, x + cx + 12, y + 48, DGREY)
    # containers
    for cx, cy, c in ((20, 66, RED), (34, 66, BLUE), (48, 66, GOLD),
                      (66, 66, GREEN), (80, 66, RED), (27, 54, GOLD)):
        cv.fill(x + cx, y + cy, 12, 12, c)
    # blast + smoke
    cv.circle(x + 88, y + 58, 12, ORANGE)
    cv.circle(x + 88, y + 58, 6, GOLD)
    cv.circle(x + 84, y + 40, 9, (110, 110, 110))
    cv.circle(x + 76, y + 26, 7, (130, 130, 130))
    cv.circle(x + 94, y + 30, 6, (150, 150, 150))

def pic_cop31(cv, x, y, w, h):
    cv.fill(x, y, w, h, (210, 228, 210))
    cv.circle(x + 40, y + 52, 34, (40, 110, 190))
    cv.circle(x + 30, y + 42, 12, GREEN)
    cv.circle(x + 52, y + 62, 10, GREEN)
    cv.circle(x + 46, y + 34, 6, GREEN)
    # thermometer
    cv.fill(x + 88, y + 18, 14, 62, WHITE)
    cv.circle(x + 95, y + 18, 7, WHITE)
    cv.circle(x + 95, y + 86, 12, RED)
    cv.fill(x + 92, y + 44, 6, 38, RED)
    cv.fill(x + 90, y + 30, 10, 2, RED)
    draw_text(cv, x + 82, y + 98, "1.5C", 1, DARKRED, bold=True)

def pic_ukeu(cv, x, y, w, h):
    cv.fill(x, y, w, h, WHITE)
    # Union Jack (simplified): blue, white diagonals, red cross
    cv.fill(x + 6, y + 8, 48, 34, (0, 40, 110))
    cv.line(x + 6, y + 8, x + 54, y + 42, WHITE)
    cv.line(x + 54, y + 8, x + 6, y + 42, WHITE)
    cv.fill(x + 27, y + 8, 6, 34, WHITE)
    cv.fill(x + 6, y + 22, 48, 6, WHITE)
    cv.fill(x + 29, y + 8, 3, 34, RED)
    cv.fill(x + 6, y + 24, 48, 3, RED)
    # EU flag: blue, ring of yellow stars
    cv.fill(x + 62, y + 8, 48, 34, (0, 40, 110))
    for k in range(12):
        import math
        a = k * 3.14159 / 6
        cv.set(x + 86 + int(11 * math.cos(a)), y + 25 + int(11 * math.sin(a)), GOLD)
        cv.set(x + 87 + int(11 * math.cos(a)), y + 25 + int(11 * math.sin(a)), GOLD)
    # green tick
    cv.circle(x + 58, y + 82, 16, GREEN)
    cv.line(x + 50, y + 82, x + 56, y + 88, WHITE)
    cv.line(x + 56, y + 88, x + 68, y + 74, WHITE)

def pic_datacentre(cv, x, y, w, h):
    cv.fill(x, y, w, h, (35, 40, 50))
    for rx in (8, 44, 80):
        cv.fill(x + rx, y + 22, 28, 76, (15, 18, 25))
        for ry in range(28, 92, 10):
            for lx, c in ((4, GREEN), (12, GOLD), (20, RED)):
                cv.fill(x + rx + lx, y + ry, 4, 3, c)
    # prohibition ring over a small globe
    cv.circle(x + 96, y + 14, 11, (40, 110, 190))
    cv.circle(x + 93, y + 11, 4, GREEN)
    cv.ring(x + 96, y + 14, 14, RED)
    cv.line(x + 86, y + 24, x + 106, y + 4, RED)
    cv.line(x + 87, y + 25, x + 107, y + 5, RED)

def pic_rikers(cv, x, y, w, h):
    cv.fill(x, y, w, h, (200, 210, 225))
    for bx, bh in ((4, 46), (20, 62), (38, 54), (58, 72), (78, 58), (96, 44)):
        cv.fill(x + bx, y + 108 - bh, 14, bh, (70, 78, 90))
        cv.fill(x + bx + 3, y + 108 - bh + 6, 3, 3, GOLD)
        cv.fill(x + bx + 3, y + 108 - bh + 16, 3, 3, GOLD)
    for bx in range(0, w, 26):
        cv.fill(x + bx, y, 4, h, (20, 20, 20))
    draw_text(cv, x + 8, y + 94, "2032", 1, WHITE, bold=True)

def pic_rahul(cv, x, y, w, h):
    cv.fill(x, y, w, h, (60, 140, 70))
    cv.fill(x, y + 44, w, 34, (205, 175, 120))
    # stumps + bails
    for sx in (46, 54, 62):
        cv.fill(x + sx, y + 52, 4, 20, GOLD)
    cv.fill(x + 46, y + 49, 20, 3, GOLD)
    # bat
    cv.poly([(x + 74, y + 40), (x + 82, y + 44), (x + 66, y + 76), (x + 58, y + 72)],
            (150, 105, 60))
    cv.fill(x + 76, y + 36, 5, 8, (120, 85, 50))
    # ball
    cv.circle(x + 92, y + 84, 7, RED)
    cv.line(x + 87, y + 80, x + 97, y + 88, WHITE)

def pic_kryvyi(cv, x, y, w, h):
    cv.fill(x, y, w, 40, (235, 170, 110))
    cv.fill(x, y + 40, w, 28, (200, 120, 80))
    cv.fill(x, y + 68, w, h - 68, (50, 50, 55))
    for bx, bh in ((6, 34), (24, 48), (44, 40), (66, 56), (88, 42)):
        cv.fill(x + bx, y + 108 - bh, 16, bh, (25, 25, 30))
    cv.circle(x + 76, y + 40, 14, ORANGE)
    cv.circle(x + 76, y + 40, 7, GOLD)
    cv.circle(x + 66, y + 24, 8, (120, 120, 120))
    cv.circle(x + 88, y + 22, 6, (140, 140, 140))
    cv.line(x + 20, y + 12, x + 52, y + 34, WHITE)
    cv.circle(x + 20, y + 12, 2, WHITE)

def pic_fugaku(cv, x, y, w, h):
    cv.fill(x, y, w, h, (20, 22, 30))
    for rx in (6, 40, 74):
        cv.fill(x + rx, y + 14, 28, 78, (10, 12, 18))
        for ry in range(20, 86, 8):
            for lx, c in ((4, GREEN), (11, (0, 180, 220)), (18, GOLD)):
                cv.fill(x + rx + lx, y + ry, 4, 3, c)
    cv.poly([(x + 96, y + 62), (x + 82, y + 92), (x + 110, y + 92)], RED)
    cv.fill(x + 94, y + 74, 4, 10, WHITE)
    cv.fill(x + 94, y + 87, 4, 4, WHITE)

# ---------------------------------------------------------------- world map
MAP_PINS = [
    ("LIMA", 160, 74), ("NEW YORK", 165, 29), ("WASHINGTON", 150, 34),
    ("WARSAW", 329, 19), ("BRUSSELS", 300, 20), ("ANTALYA", 346, 32),
    ("KRYVYI RIH", 350, 23), ("KHARG", 379, 39), ("HODEIDAH", 367, 51),
    ("DELHI", 425, 39), ("KOBE", 525, 34), ("WELLINGTON", 594, 98),
    ("LOS ANGELES", 88, 33), ("LAS VEGAS", 100, 40),
]

def pic_map(cv, x, y, w, h):
    cv.fill(x, y, w, h, (170, 205, 230))
    for gx in range(0, w, 62):
        cv.vline(x + gx, y, h, (150, 188, 215))
    for gy in range(0, h, 27):
        cv.hline(x, y + gy, w, (150, 188, 215))
    land = (135, 165, 135)
    cv.poly([(x + 60, y + 18), (x + 110, y + 12), (x + 150, y + 18),
             (x + 170, y + 30), (x + 160, y + 45), (x + 140, y + 55),
             (x + 110, y + 60), (x + 80, y + 55), (x + 55, y + 40),
             (x + 50, y + 25)], land)
    cv.poly([(x + 185, y + 8), (x + 205, y + 6), (x + 210, y + 14),
             (x + 195, y + 18)], land)
    cv.poly([(x + 165, y + 62), (x + 185, y + 60), (x + 200, y + 70),
             (x + 195, y + 90), (x + 185, y + 105), (x + 175, y + 95),
             (x + 165, y + 78)], land)
    cv.poly([(x + 300, y + 15), (x + 330, y + 12), (x + 345, y + 18),
             (x + 335, y + 30), (x + 315, y + 32), (x + 300, y + 25)], land)
    cv.poly([(x + 300, y + 38), (x + 340, y + 36), (x + 355, y + 48),
             (x + 350, y + 70), (x + 335, y + 88), (x + 320, y + 80),
             (x + 305, y + 60), (x + 298, y + 48)], land)
    cv.poly([(x + 350, y + 12), (x + 420, y + 8), (x + 500, y + 12),
             (x + 560, y + 20), (x + 575, y + 30), (x + 540, y + 45),
             (x + 500, y + 55), (x + 460, y + 60), (x + 420, y + 55),
             (x + 380, y + 45), (x + 350, y + 30)], land)
    cv.poly([(x + 470, y + 65), (x + 490, y + 62), (x + 505, y + 68),
             (x + 490, y + 75)], land)
    cv.poly([(x + 505, y + 78), (x + 545, y + 75), (x + 560, y + 82),
             (x + 545, y + 95), (x + 515, y + 95), (x + 500, y + 86)], land)
    for name, px, py in MAP_PINS:
        cv.circle(x + px, y + py, 4, RED)
        cv.circle(x + px, y + py, 2, WHITE)

# ---------------------------------------------------------------- layout
M = 14            # side margin
CW = 996          # content width
COLW = 324        # lead column width
COLX = (M, M + COLW + 12, M + 2 * COLW + 24)

LEADS = [
    ("QUAKE - PERU", "M6.8 QUAKE SHAKES PERU",
     "Junin tremor felt in Lima; no casualties reported at first.", pic_quake),
    ("MARKETS - NEW YORK", "STOCKS SLIDE INTO CORRECTION",
     "S&P 500 -3.7%, Nasdaq -5.3%; SEC examines Nvidia as shares fall 13.8%.",
     pic_stocks),
    ("WAR - POLAND", "MISSILE FALLS IN POLAND",
     "Two missiles and a drone down; Warsaw calls it a deliberate provocation.",
     pic_poland),
    ("GULF STANDOFF", "14 TANKERS TEST BLOCKADE",
     "Iran masses ships at Kharg; Tehran vows to break the US blockade.",
     pic_tankers),
    ("WAR - YEMEN", "SAUDI STRIKES POUND YEMEN",
     "Coalition hits Hodeidah port and Sanaa; Houthis warn airlines off Saudi skies.",
     pic_yemen),
    ("CLIMATE - ANTALYA", "COP31 MISSES DEADLINE",
     "Talks run into overtime; draft still has no mention of fossil fuels.",
     pic_cop31),
    ("EUROPE - BRUSSELS", "UK AND EU SEAL RESET DEAL",
     "Food checks scrapped, carbon markets linked, youth scheme for 100,000.",
     pic_ukeu),
    ("TECH - WASHINGTON", "TRUMP: NO DATA CENTRES ABROAD",
     "'Tremendous tax' threatened on US firms building data centres overseas.",
     pic_datacentre),
    ("NEW YORK", "RIKERS TO CLOSE BY 2032",
     "Mayor Mamdani unveils plan to shut the jail complex by 2032.", pic_rikers),
    ("CRICKET - WELLINGTON", "RAHUL COMPLETES SENA SET",
     "First Indian opener with Test hundreds in all four SENA countries.",
     pic_rahul),
    ("WAR - UKRAINE", "KRYVYI RIH HIT: 2 DEAD",
     "Russian strike kills two and wounds 42, including four children.",
     pic_kryvyi),
    ("TECH - JAPAN", "FUGAKU SUPERCOMPUTER HACKED",
     "Japan's top supercomputer hit by suspected cyberattack; RIKEN halts work.",
     pic_fugaku),
]

MORE = [
    ("Zelensky:", " meets generals on repairs after barrage"),
    ("Palisades arson:", " LA jury convicts Rinderknecht"),
    ("Las Vegas GP:", " Russell, Verstappen collide"),
    ("India shares:", " record Rs 1.22 lakh crore inflow"),
    ("Nepal PM:", " heads to Delhi for first foreign trip"),
    ("Myanmar:", " calls ICJ genocide ruling 'unfair'"),
    ("GTA 6 PC scam:", " $200 malware kit targets fans"),
    ("White House:", " removes cyber-security chief"),
    ("NSA network:", " classified system down, sources say"),
    ("Florida floods:", " deluge shifts north as rivers rise"),
    ("Tools recall:", " 229,000 in battery scare"),
    ("Sikh plot:", " Indian jailed 19 years in US case"),
    ("Deepathoon:", " top court allows lamp, one time"),
    ("Manipur liquor:", " spurious drink kills 11"),
    ("Alcaraz:", " brushes off injury to beat Cobolli"),
    ("Cummins:", " keeps Cricket Australia backing"),
    ("Luckey:", " plans island to last 1,000 years"),
    ("Kane:", " out three months with ankle injury"),
    ("Trump, Xi:", " humans stay in charge of AI arms"),
    ("Argentina:", " Senate backs disability law"),
    ("Cyclone Akvan:", " rain returns to Tamil Nadu"),
    ("AMD Lux:", " supercomputer opens for science"),
    ("Navy chief:", " senators grill him on Iran costs"),
    ("FDA nominee:", " Trump pulls pick before vote"),
]

NUMBERS = [
    ("6.8", "Peru quake magnitude"),
    ("-5.3%", "Nasdaq, Friday"),
    ("14", "tankers at Kharg"),
    ("100,000", "youth visas a year"),
    ("19:24 CET", "BepiColombo insertion"),
    ("2032", "Rikers Island closes"),
]

STRIP = ("YESTERDAY, 20 NOV - LEFT OUT ON PURPOSE: KYIV BARRAGE | ASIA ROUT | "
         "GTA VI $3.8BN | SYDNEY CHARGE | SENEGAL BOAT | TOKYO RALLY | "
         "PETE ROSE PARDON | DENMARK PLOT")


def border(cv, x, y, w, h, c=INK):
    cv.hline(x, y, w, c)
    cv.hline(x, y + h - 1, w, c)
    cv.vline(x, y, h, c)
    cv.vline(x + w - 1, y, h, c)


def draw():
    cv = Canvas(W, H)
    # ---- masthead
    center_text(cv, W // 2, 10, "THE WORLD IN ONE DAY", 5, INK, bold=True)
    cv.hline(M, 52, CW, INK)
    cv.hline(M, 54, CW, INK)
    draw_text(cv, M, 59, "No. 325", 1, GREY)
    center_text(cv, W // 2, 58, "SATURDAY 21 NOVEMBER 2026", 2, RED, bold=True)
    s = "WORLD TELEVISION DAY"
    draw_text(cv, W - M - text_w(s, 1), 59, s, 1, GREY)
    cv.hline(M, 76, CW, INK)
    # ---- hero: BepiColombo
    hy = 82
    pic_mercury(cv, M, hy, 316, 148)
    border(cv, M, hy, 316, 148)
    tx = 344
    draw_text(cv, tx, hy + 4, "SPACE - MERCURY", 1, RED, bold=True)
    draw_text(cv, tx, hy + 18, "BEPICOLOMBO REACHES MERCURY", 3, INK, bold=True)
    y = hy + 47
    for ln in wrap("After eight years and six billion miles, Europe and Japan's "
                   "BepiColombo fires its thrusters tonight to enter orbit around "
                   "Mercury - only the second craft ever to do so.", 666, 1):
        draw_text(cv, tx, y, ln, 1, INK)
        y += 9
    y += 3
    for ln in wrap("Its two orbiters will map the smallest planet and probe its "
                   "magnetic field. Science begins in April 2027.", 666, 1):
        draw_text(cv, tx, y, ln, 1, INK)
        y += 9
    cv.hline(tx, hy + 110, 666, LGREY)
    draw_text(cv, tx, hy + 116,
              "INSERTION 19:24 CET | TWO ORBITERS | 8 YEARS, 6BN MILES", 1,
              DARKRED, bold=True)
    draw_text(cv, tx, hy + 128,
              "MPO AND MIO SEPARATE 9-10 DEC | SCIENCE FROM APRIL 2027", 1,
              INK, bold=True)
    # ---- lead grid: 3 columns x 4 rows
    rows_y = (237, 361, 485, 609)
    for i, (kick, head, deck, pic) in enumerate(LEADS):
        col, row = i % 3, i // 3
        x, y = COLX[col], rows_y[row]
        pic(cv, x, y, 116, 108)
        border(cv, x, y, 116, 108)
        tx2 = x + 124
        draw_text(cv, tx2, y + 2, kick, 1, RED, bold=True)
        yy = y + 14
        for ln in wrap(head, 200, 2):
            draw_text(cv, tx2, yy, ln, 2, INK, bold=True)
            yy += 15
        yy += 4
        for ln in wrap(deck, 200, 1):
            draw_text(cv, tx2, yy, ln, 1, INK)
            yy += 9
    # ---- map band
    my = 733
    draw_text(cv, M, my, "THE DAY ON THE MAP", 1, INK, bold=True)
    draw_text(cv, 646, my, "THE DAY IN NUMBERS", 1, RED, bold=True)
    cv.hline(M, my + 11, CW, INK)
    pic_map(cv, M, my + 16, 620, 104)
    border(cv, M, my + 16, 620, 104)
    ny = my + 16
    for num, lab in NUMBERS:
        draw_text(cv, 646, ny + 2, num, 2, DARKRED, bold=True)
        draw_text(cv, 646 + 118, ny + 4, lab, 1, INK)
        ny += 17
    draw_text(cv, M, my + 124,
              "PINNED: LIMA - NEW YORK - WASHINGTON - WARSAW - BRUSSELS - "
              "ANTALYA - KRYVYI RIH", 1, GREY)
    draw_text(cv, M, my + 133,
              "KHARG - HODEIDAH - DELHI - KOBE - LOS ANGELES - LAS VEGAS - "
              "WELLINGTON", 1, GREY)
    # ---- more from the day
    oy = 881
    draw_text(cv, M, oy, "MORE FROM THE DAY", 1, INK, bold=True)
    cv.hline(M, oy + 11, CW, INK)
    for i, (b, rest) in enumerate(MORE):
        col, row = i // 8, i % 8
        x = COLX[col]
        y = oy + 16 + row * 12
        w1 = draw_text(cv, x, y, b, 1, INK, bold=True)
        draw_text(cv, x + w1, y, rest, 1, INK)
    # ---- date-check strip
    sy = 996
    cv.fill(M, sy, CW, 22, BLACK)
    center_text(cv, W // 2, sy + 7, STRIP, 1, WHITE)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = draw()
    data = png_bytes(cv)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)


if __name__ == "__main__":
    main()

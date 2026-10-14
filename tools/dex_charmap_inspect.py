#!/usr/bin/env python3
"""
Inspect gfx/pokedex/characters.interleave.png to see which character slots
(0x00..0xFF) are used vs blank, and render an annotated overview.

The file is 128x256 = 16 cols x 32 rows of 8x8 tiles.
Each character = 2 stacked tiles (top + bottom) = 16 pixels tall.
Character N lives at PNG col (N % 16), PNG rows (N // 16) * 2 and *2 + 1.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "gfx" / "pokedex" / "characters.interleave.png"
OUT = REPO / "tools" / "out_dex_charmap_inspect.png"


def main() -> None:
    im = Image.open(SRC).convert("L")
    w, h = im.size
    assert (w, h) == (128, 256), f"unexpected size {w}x{h}"
    px = im.load()

    # Determine blank slots
    blanks: list[int] = []
    used: list[int] = []
    for ci in range(256):
        col = ci % 16
        row = ci // 16
        x0, y0 = col * 8, row * 16
        # Check the 8x16 box for any non-white pixel
        has_ink = False
        for y in range(y0, y0 + 16):
            for x in range(x0, x0 + 8):
                if px[x, y] < 0xF0:  # not white
                    has_ink = True
                    break
            if has_ink:
                break
        (used if has_ink else blanks).append(ci)

    print(f"Used   : {len(used)} slots")
    print(f"Blank  : {len(blanks)} slots")
    print()
    print("Blank slot ranges (hex):")
    # group consecutive
    groups: list[tuple[int, int]] = []
    s = blanks[0] if blanks else None
    prev = s
    for b in blanks[1:]:
        if b == prev + 1:
            prev = b
            continue
        groups.append((s, prev))
        s = b
        prev = b
    if s is not None:
        groups.append((s, prev))
    for lo, hi in groups:
        if lo == hi:
            print(f"  ${lo:02X}")
        else:
            print(f"  ${lo:02X}-${hi:02X}  ({hi - lo + 1} slots)")

    # Render annotated overview at 4x zoom with grid + slot IDs
    scale = 4
    overview = im.resize((w * scale, h * scale), Image.NEAREST).convert("RGB")
    draw = ImageDraw.Draw(overview)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
    for ci in range(256):
        col = ci % 16
        row = ci // 16
        x0, y0 = col * 8 * scale, row * 16 * scale
        x1, y1 = x0 + 8 * scale, y0 + 16 * scale
        color = (255, 0, 0) if ci in blanks else (0, 128, 0)
        draw.rectangle([x0, y0, x1 - 1, y1 - 1], outline=color)
        draw.text((x0 + 2, y0 + 1), f"{ci:02X}", fill=color, font=font)
    overview.save(OUT)
    print(f"\nWrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()

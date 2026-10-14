#!/usr/bin/env python3
"""Extract per-slot 8x16 character preview rows from characters.interleave.png.

Renders the contents of slot IDs in a horizontal strip, each labeled
with its hex ID, so we can identify which letter is at which slot.
"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "gfx" / "pokedex" / "characters.interleave.png"


def main() -> None:
    rows = [
        ("00-1F", list(range(0x00, 0x20))),
        ("20-3F", list(range(0x20, 0x40))),
        ("40-5F", list(range(0x40, 0x60))),
        ("60-7F", list(range(0x60, 0x80))),
        ("80-9F", list(range(0x80, 0xA0))),
        ("A0-BF", list(range(0xA0, 0xC0))),
        ("C0-DF", list(range(0xC0, 0xE0))),
        ("E0-FF", list(range(0xE0, 0x100))),
    ]
    im = Image.open(SRC).convert("L")
    px = im.load()
    scale = 5
    pad = 14  # space for label
    cell_w = 8 * scale
    cell_h = 16 * scale + pad
    for name, slots in rows:
        out = Image.new("RGB", (cell_w * len(slots), cell_h), "white")
        d = ImageDraw.Draw(out)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 10)
        except Exception:
            font = ImageFont.load_default()
        for i, sl in enumerate(slots):
            col = sl % 16
            row = sl // 16
            x0, y0 = col * 8, row * 16
            tile = im.crop((x0, y0, x0 + 8, y0 + 16)).resize((cell_w, 16 * scale), Image.NEAREST)
            out.paste(tile, (i * cell_w, pad))
            d.text((i * cell_w + 1, 1), f"{sl:02X}", fill="red", font=font)
        path = REPO / "tools" / f"out_dex_slots_{name}.png"
        out.save(path)
        print(f"wrote {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Extract EU titlescreen data (tilemap / bgattr / palettes / tile gfx) for all 5 EU languages.

The EU Pokemon Pinball ROM contains a 5-entry language table for the titlescreen
fade-in load list. Each entry references a different tilemap, bgattr, palettes and
tile-gfx region. Language order in Nintendo EU releases of that era is
EN, FR, DE, ES, IT — match #2 (FR) has been confirmed visually via bank_46.png.

For each language, this script saves:
    eu_reference/<lang>/titlescreen/titlescreen.map           (1024 B)
    eu_reference/<lang>/titlescreen/titlescreen.bgattr        (576 B)
    eu_reference/<lang>/titlescreen/titlescreen_palettes.bin  (128 B)
    eu_reference/<lang>/titlescreen/titlescreen_fade_in.2bpp  (0x1800 B, GBC tiles)
    eu_reference/<lang>/titlescreen/titlescreen.2bpp          (0x1800 B, GB tiles)
    eu_reference/<lang>/titlescreen/titlescreen_fade_in.png   (rendered preview)
    eu_reference/<lang>/titlescreen/titlescreen.png           (rendered preview)
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
EU_ROM = (REPO / "PokemonPinballEurope.gbc").read_bytes()

# Language order in the EU Pokemon Pinball ROM (verified by rendering tile previews)
LANGUAGES = ["en", "fr", "de", "it", "es"]

# The 5 titlescreen entries form a contiguous table starting at 0xc06b.
# Each entry is 46 bytes: 7B GB-tiles + 7B GB-tilemap + 2B FF + 7B GBC-tiles +
# 7B GBC-tilemap + 7B GBC-bgattr + 7B GBC-palettes + 2B FF.
import struct
TABLE_START = 0xc06b
ENTRY_SIZE  = 46

# Field offsets within each entry (each VIDEO_DATA item = 7 bytes: addr(2) bank(1) dest(2) size(2))
FIELDS = [
    ("gb_tiles",     0,  0x1800),
    ("gb_tilemap",   7,  0x400),   # full 32x32 tilemap; only $240 are loaded but file on disk is 0x400
    # 14..15: FF FF terminator
    ("gbc_tiles",    16, 0x1800),
    ("gbc_tilemap",  23, 0x400),   # full 32x32 tilemap
    ("gbc_bgattr",   30, 0x240),   # bgattr is only $240 (matches load size and on-disk size)
    ("gbc_palettes", 37, 0x80),
    # 44..45: FF FF terminator
]

def addr_bank_to_file(addr: int, bank: int) -> int:
    return (bank * 0x4000) + (addr - 0x4000) if bank else addr

def parse_entry(rom: bytes, entry_off: int) -> dict:
    """Read pointer+bank+size from one 46-byte language entry."""
    out = {}
    for name, fld_off, size in FIELDS:
        base = entry_off + fld_off
        addr = rom[base] | (rom[base+1] << 8)
        bank = rom[base+2]
        out[name] = {"file": addr_bank_to_file(addr, bank), "size": size, "bank": bank, "addr": addr}
    return out

def twobpp_to_png(data: bytes, tiles_wide: int = 32) -> Image.Image:
    """Render flat 2bpp stream as grayscale PNG, laid out tiles_wide tiles per row."""
    tile_count = len(data) // 16
    tiles_high = (tile_count + tiles_wide - 1) // tiles_wide
    palette = [0xFF, 0xAA, 0x55, 0x00]
    im = Image.new("L", (tiles_wide * 8, tiles_high * 8))
    px = im.load()
    for ti in range(tile_count):
        row_t, col_t = ti // tiles_wide, ti % tiles_wide
        tile = data[ti*16:ti*16+16]
        for row in range(8):
            lo, hi = tile[row*2], tile[row*2+1]
            for col in range(8):
                bit = 7 - col
                val = ((lo >> bit) & 1) | (((hi >> bit) & 1) << 1)
                px[col_t*8 + col, row_t*8 + row] = palette[val]
    return im

def main():
    print("Extracting EU titlescreen data for each language:")
    for i, lang in enumerate(LANGUAGES):
        entry_off = TABLE_START + i * ENTRY_SIZE
        fields = parse_entry(EU_ROM, entry_off)
        out_dir = REPO / f"eu_reference/{lang}/titlescreen"
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n  [{lang}] table entry @ {entry_off:#x}")
        # Save each binary
        for name, info in fields.items():
            data = EU_ROM[info["file"]:info["file"] + info["size"]]
            ext = {"gb_tiles": "2bpp", "gbc_tiles": "2bpp",
                   "gb_tilemap": "map", "gbc_tilemap": "map",
                   "gbc_bgattr": "bgattr", "gbc_palettes": "bin"}[name]
            fname_map = {
                "gb_tiles":     "titlescreen.2bpp",
                "gb_tilemap":   "titlescreen_gb.map",
                "gbc_tiles":    "titlescreen_fade_in.2bpp",
                "gbc_tilemap":  "titlescreen.map",
                "gbc_bgattr":   "titlescreen.bgattr",
                "gbc_palettes": "titlescreen_palettes.bin",
            }
            (out_dir / fname_map[name]).write_bytes(data)
            print(f"    {name:14s} bank {info['bank']:#04x} file {info['file']:#x} size {info['size']:#x}")

        # Render preview PNGs of tile sheets
        gb_data  = EU_ROM[fields["gb_tiles"]["file"]:fields["gb_tiles"]["file"]+fields["gb_tiles"]["size"]]
        gbc_data = EU_ROM[fields["gbc_tiles"]["file"]:fields["gbc_tiles"]["file"]+fields["gbc_tiles"]["size"]]
        twobpp_to_png(gb_data).save(out_dir / "titlescreen.png")
        twobpp_to_png(gbc_data).save(out_dir / "titlescreen_fade_in.png")

    print("\nDone. Check the rendered PNGs to confirm the language order (en/fr/de/es/it).")

if __name__ == "__main__":
    main()

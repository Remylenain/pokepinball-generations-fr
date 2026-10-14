#!/usr/bin/env python3
"""Verify EU ROM layout for titlescreen data, then dump EU tilemap/bgattr/palettes.

Strategy:
 1. Confirm US ROM bytes at offset 0xc5800 match gfx/tilemaps/titlescreen.map (1024 B).
 2. Confirm US ROM bytes at offset 0xc5c00 match gfx/bgattr/titlescreen.bgattr (576 B).
 3. If both match, EU layout is almost certainly identical (same engine, same 2 MB size).
    Dump EU bytes at the same offsets into eu_reference/fr/.
 4. Compare US vs EU tilemap byte-by-byte to confirm there ARE differences (localization).
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
US_ROM = REPO / "PinballGenerations.gbc"
EU_ROM = REPO / "PokemonPinballEurope.gbc"
US_TILEMAP = REPO / "gfx/tilemaps/titlescreen.map"
US_BGATTR  = REPO / "gfx/bgattr/titlescreen.bgattr"

# Symbol addresses from main.asm
OFF_TILEMAP   = 0xc5800
LEN_TILEMAP   = 1024            # 1024 bytes
OFF_BGATTR    = 0xc5c00
LEN_BGATTR    = 576             # 576 bytes
OFF_PALETTES  = 0xdcf80
LEN_PALETTES  = 0x80            # 128 bytes (TitlescreenPalettes block: 8 BG + 8 OBJ palettes × 8 bytes)

OUT_DIR = REPO / "eu_reference/fr/titlescreen"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def read(rom_path: Path, off: int, length: int) -> bytes:
    with rom_path.open("rb") as f:
        f.seek(off)
        return f.read(length)


def check_match(label: str, rom_bytes: bytes, expected: bytes) -> bool:
    ok = rom_bytes == expected
    print(f"[{label}] US ROM @ 0x{OFF_TILEMAP:x}: {'MATCH' if ok else 'MISMATCH'} (len rom={len(rom_bytes)}, expected={len(expected)})")
    return ok


def diff_count(a: bytes, b: bytes) -> int:
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] != b[i]) + abs(len(a) - len(b))


def main() -> int:
    us_tilemap_disk = US_TILEMAP.read_bytes()
    us_bgattr_disk  = US_BGATTR.read_bytes()

    us_tilemap_rom = read(US_ROM, OFF_TILEMAP, LEN_TILEMAP)
    us_bgattr_rom  = read(US_ROM, OFF_BGATTR,  LEN_BGATTR)
    us_palettes_rom = read(US_ROM, OFF_PALETTES, LEN_PALETTES)

    print(f"== Sanity check: US ROM bytes vs on-disk gfx files ==")
    ok_t = us_tilemap_rom == us_tilemap_disk
    ok_b = us_bgattr_rom  == us_bgattr_disk
    print(f"  tilemap : {'MATCH' if ok_t else 'MISMATCH'}")
    print(f"  bgattr  : {'MATCH' if ok_b else 'MISMATCH'}")
    if not (ok_t and ok_b):
        print("  -> US ROM offsets are NOT what we expected. Aborting.")
        return 1
    print("  -> Layout confirmed for US ROM.")

    eu_tilemap = read(EU_ROM, OFF_TILEMAP, LEN_TILEMAP)
    eu_bgattr  = read(EU_ROM, OFF_BGATTR,  LEN_BGATTR)
    eu_palettes = read(EU_ROM, OFF_PALETTES, LEN_PALETTES)

    print(f"\n== EU vs US comparison at same offsets ==")
    print(f"  tilemap  : {diff_count(us_tilemap_rom, eu_tilemap)} bytes differ out of {LEN_TILEMAP}")
    print(f"  bgattr   : {diff_count(us_bgattr_rom,  eu_bgattr)} bytes differ out of {LEN_BGATTR}")
    print(f"  palettes : {diff_count(us_palettes_rom, eu_palettes)} bytes differ out of {LEN_PALETTES}")

    (OUT_DIR / "titlescreen.map").write_bytes(eu_tilemap)
    (OUT_DIR / "titlescreen.bgattr").write_bytes(eu_bgattr)
    (OUT_DIR / "titlescreen_palettes.bin").write_bytes(eu_palettes)
    print(f"\nWrote EU dumps to {OUT_DIR.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

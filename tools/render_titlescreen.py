#!/usr/bin/env python3
"""Render the GBC titlescreen from tilemap + bgattr + palettes + tile data into a PNG."""
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parent.parent

def render(tiles_2bpp: bytes, tilemap: bytes, bgattr: bytes, palettes: bytes,
           cols=20, rows=18, tmap_stride=32) -> Image.Image:
    """Render cols×rows tiles into an 8*cols × 8*rows RGB image.

    tilemap byte = tile index in the bgattr-selected VRAM bank.
    bgattr byte: bits 0-2 = BG palette index, bit 3 = VRAM bank,
                 bit 5 = X-flip, bit 6 = Y-flip.
    palettes = 8 BG palettes × 4 colors × 2 bytes (GBC BGR15 LE).
    """
    def pal_to_rgb(pidx: int, cidx: int):
        off = pidx*8 + cidx*2
        lo, hi = palettes[off], palettes[off+1]
        v = lo | (hi << 8)
        r = (v & 0x1f) * 255 // 31
        g = ((v >> 5) & 0x1f) * 255 // 31
        b = ((v >> 10) & 0x1f) * 255 // 31
        return (r, g, b)

    def decode_tile(idx: int, bank: int):
        """Return 8x8 list of 4-color indices for tile."""
        base = (bank * 256 + idx) * 16
        tile = tiles_2bpp[base:base+16]
        out = [[0]*8 for _ in range(8)]
        for row in range(8):
            lo, hi = tile[row*2], tile[row*2+1]
            for col in range(8):
                bit = 7 - col
                out[row][col] = ((lo >> bit) & 1) | (((hi >> bit) & 1) << 1)
        return out

    im = Image.new("RGB", (cols*8, rows*8))
    px = im.load()
    for ty in range(rows):
        for tx in range(cols):
            tmidx = ty*tmap_stride + tx
            tile_idx = tilemap[tmidx]
            attr = bgattr[tmidx]
            pidx = attr & 7
            bank = (attr >> 3) & 1
            xflip = (attr >> 5) & 1
            yflip = (attr >> 6) & 1
            tile = decode_tile(tile_idx, bank)
            for r in range(8):
                for c in range(8):
                    sr = 7 - r if yflip else r
                    sc = 7 - c if xflip else c
                    cidx = tile[sr][sc]
                    px[tx*8+c, ty*8+r] = pal_to_rgb(pidx, cidx)
    return im

def main():
    fr = REPO / "eu_reference/fr/titlescreen"
    # Use freshly built ROM bytes (sanity: re-extract from PinballGenerations.gbc directly)
    rom = (REPO / "PinballGenerations.gbc").read_bytes()
    tiles_built = rom[0x2b*0x4000 : 0x2b*0x4000 + 0x1800]
    tilemap_built = rom[0x31*0x4000 + 0x1400 : 0x31*0x4000 + 0x1400 + 0x240]
    bgattr_built = rom[0x31*0x4000 + 0x1800 : 0x31*0x4000 + 0x1800 + 0x240]
    pal_built = rom[0x37*0x4000 + 0x1188 : 0x37*0x4000 + 0x1188 + 0x80]

    # The tilemap stride is 18 since only the visible area (20×18) is loaded — wait, need to check.
    # Actually load size is 0x240 = 576 bytes which fits 18×32, but if only 20×18 visible loaded, it's 360 bytes.
    # 0x240 = 576 — that matches 18*32, suggesting full 32-col tilemap rows loaded.
    # But $240 = 0x240 = 576 also = 32×18.
    # Hmm but VIDEO_DATA_TILEMAP TitlescreenTilemap, vBGMap, $240 — loads 576 bytes to vBGMap (VRAM tilemap area).
    # VRAM tilemap is 32 cols wide so 576/32 = 18 rows. OK so stride is 32, full 18 rows.
    img = render(tiles_built, tilemap_built, bgattr_built, pal_built, cols=20, rows=18, tmap_stride=32)
    out = REPO / "_debug/rendered_titlescreen_from_built_rom.png"
    img.save(out)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()

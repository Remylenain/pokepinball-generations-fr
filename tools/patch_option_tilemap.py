#!/usr/bin/env python3
"""Patch option_menu.map and option_menu_2.map after rumble_text and bgm_se_text grew.

Changes:
- rumble_text PNG: 48x8 (6 tiles) -> 64x8 (8 tiles)   [+2 tiles]
- bgm_se_text PNG: 24x40 (15 tiles) -> 32x40 (20 tiles) [+5 tiles, at end of load]

Tile-index shift logic:
- The BG tile data is in signed addressing ($8800-$97FF, LCDC bit 4 = 0).
- A tilemap byte X represents load-tile T where:
    T = X            if X >= 0x80 (signed negative half, $8800-$8FFF)
    T = X + 0x100    if X <  0x80 (signed positive half, $9000-$97FF)
- rumble_text grew by 2 tiles starting at load tile 0xa5. Every reference to
  load tile T >= 0xab needs to shift to T+2 (because everything after rumble
  in the load moved by 2 tiles).
- bgm_se_text is at the END of the load, so its growth shifts nothing.

New label slots in the tilemap:
- VIBRATION (row 3, BG): cols 3..10 -> tiles a5..ac (was a5..aa)
- MUSIQUE   (row 11, BG): cols 3..6 -> tiles 33,34,35,36 (new bgm_se tiles 0..3)
- EFFETS    (row 13, BG): cols 3..6 -> tiles 37,38,39,3a (new bgm_se tiles 4..7)
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
W = 32                 # tilemap stride
SHIFT_THRESHOLD = 0xab  # load tile T below this is unchanged
SHIFT_AMOUNT = 2

def byte_to_tile(x: int) -> int:
    return x if x >= 0x80 else x + 0x100

def tile_to_byte(t: int) -> int:
    return t if t < 0x100 else t - 0x100

def shift_byte(x: int) -> int:
    t = byte_to_tile(x)
    if t >= SHIFT_THRESHOLD:
        t += SHIFT_AMOUNT
    return tile_to_byte(t) & 0xff

def patch_tilemap(path: Path, position_overrides: dict[tuple[int,int], list[int]]):
    """Apply shift to every byte, then overwrite specific positions for new labels.

    position_overrides: {(row, col_start): [byte, byte, ...]}
    """
    data = bytearray(path.read_bytes())
    # 1) Shift all bytes referencing tiles >= 0xab.
    for i in range(len(data)):
        data[i] = shift_byte(data[i])
    # 2) Apply overrides.
    for (row, col_start), new_bytes in position_overrides.items():
        for k, b in enumerate(new_bytes):
            data[row * W + col_start + k] = b
    path.write_bytes(bytes(data))

def main():
    # option_menu.map = BG layer (vBGMap). Holds RUMBLE/KEY CO/SOUND TEST/BGM/SE positions.
    bg_overrides = {
        # VIBRATION at row 3 — extend cols 9..10 with new tiles ab,ac
        (3,  9):  [0xab, 0xac],
        # MUSIQUE at row 11 — cols 3..6 (was 3..5)
        (11, 3):  [0x33, 0x34, 0x35, 0x36],
        # EFFETS  at row 13 — cols 3..6 (was 3..4)
        (13, 3):  [0x37, 0x38, 0x39, 0x3a],
        # Clear col 5 of row 13 in case the shift left a tile there from old "35".
        # (Shifting 0x35 -> 0x37, which now is overwritten by the override above.)
    }
    patch_tilemap(REPO / "gfx/tilemaps/option_menu.map", bg_overrides)
    print("patched option_menu.map (BG layer)")

    # option_menu_2.map = Window layer (vBGWin). Used for the KeyConfig sub-screen;
    # the options screen itself doesn't show the window (LCDC bit 5 = 0). Still apply
    # the shift so KeyConfig stays correct.
    patch_tilemap(REPO / "gfx/tilemaps/option_menu_2.map", {})
    print("patched option_menu_2.map (Window layer)")

    # option_menu_3.map and option_menu_4.map are bgattr maps (palette/bank bits per tile),
    # not tile indices. They do not need shifting. We could optionally set the bgattr for
    # the new VIBRATION/MUSIQUE/EFFETS tiles, but keeping them at the default (palette 0)
    # matches the surrounding background.

if __name__ == "__main__":
    main()

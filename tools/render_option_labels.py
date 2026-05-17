#!/usr/bin/env python3
"""Render FR option-menu label PNGs to match dimensions of existing US PNGs.

Two bitmap fonts defined inline:
- WIDE: 8x8 bold caps (matches existing project labels RUMBLE/SOUND TEST/etc)
- NARROW: variable-width compact caps + 1-px gap (matches EU FR MUSIQUE/EFFETS)
"""
from PIL import Image
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# WIDE font: 8x8 bold caps. Each glyph is 8 rows of 8 chars ('#'=fg, '.'=bg).
WIDE = {
    'A': [
        ".######.",
        "##....##",
        "##....##",
        "########",
        "########",
        "##....##",
        "##....##",
        "........",
    ],
    'C': [
        ".######.",
        "##....##",
        "##......",
        "##......",
        "##......",
        "##....##",
        ".######.",
        "........",
    ],
    'E': [
        "########",
        "##......",
        "##......",
        "#####...",
        "#####...",
        "##......",
        "########",
        "........",
    ],
    'F': [
        "########",
        "##......",
        "##......",
        "######..",
        "######..",
        "##......",
        "##......",
        "........",
    ],
    'G': [
        ".######.",
        "##....##",
        "##......",
        "##..####",
        "##....##",
        "##....##",
        ".######.",
        "........",
    ],
    'I': [
        "########",
        "...##...",
        "...##...",
        "...##...",
        "...##...",
        "...##...",
        "########",
        "........",
    ],
    'N': [
        "##....##",
        "###...##",
        "####..##",
        "##.##.##",
        "##..####",
        "##...###",
        "##....##",
        "........",
    ],
    'O': [
        ".######.",
        "##....##",
        "##....##",
        "##....##",
        "##....##",
        "##....##",
        ".######.",
        "........",
    ],
    'S': [
        ".######.",
        "##....##",
        "##......",
        ".######.",
        "......##",
        "##....##",
        ".######.",
        "........",
    ],
    'T': [
        "########",
        "...##...",
        "...##...",
        "...##...",
        "...##...",
        "...##...",
        "...##...",
        "........",
    ],
    '.': [
        "........",
        "........",
        "........",
        "........",
        "........",
        "...##...",
        "...##...",
        "........",
    ],
    ' ': [
        "........",
    ] * 8,
}

# NARROW font: variable-width, each entry is (width, rows). Glyph followed by 1px gap.
def G(w, *rows):
    return (w, list(rows))

NARROW = {
    'A': G(4,
        ".##.",
        "#..#",
        "#..#",
        "####",
        "####",
        "#..#",
        "#..#",
        "....",
    ),
    'B': G(3,
        "##.",
        "#.#",
        "#.#",
        "##.",
        "##.",
        "#.#",
        "##.",
        "...",
    ),
    'E': G(3,
        "###",
        "#..",
        "#..",
        "##.",
        "##.",
        "#..",
        "###",
        "...",
    ),
    'F': G(3,
        "###",
        "#..",
        "#..",
        "##.",
        "##.",
        "#..",
        "#..",
        "...",
    ),
    'I': G(1,
        "#",
        "#",
        "#",
        "#",
        "#",
        "#",
        "#",
        ".",
    ),
    'M': G(5,
        "#...#",
        "##.##",
        "##.##",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
        ".....",
    ),
    'N': G(4,
        "#..#",
        "##.#",
        "##.#",
        "#.##",
        "#.##",
        "#..#",
        "#..#",
        "....",
    ),
    'O': G(3,
        ".#.",
        "#.#",
        "#.#",
        "#.#",
        "#.#",
        "#.#",
        ".#.",
        "...",
    ),
    'Q': G(4,
        ".##.",
        "#..#",
        "#..#",
        "#..#",
        "#.##",
        "#..#",
        ".###",
        "....",
    ),
    'R': G(3,
        "##.",
        "#.#",
        "#.#",
        "##.",
        "#.#",
        "#.#",
        "#.#",
        "...",
    ),
    'S': G(3,
        ".##",
        "#..",
        "#..",
        ".#.",
        "..#",
        "..#",
        "##.",
        "...",
    ),
    'T': G(3,
        "###",
        ".#.",
        ".#.",
        ".#.",
        ".#.",
        ".#.",
        ".#.",
        "...",
    ),
    'U': G(3,
        "#.#",
        "#.#",
        "#.#",
        "#.#",
        "#.#",
        "#.#",
        ".#.",
        "...",
    ),
    'V': G(3,
        "#.#",
        "#.#",
        "#.#",
        "#.#",
        "#.#",
        ".#.",
        ".#.",
        "...",
    ),
    ' ': G(2,
        "..",
    ) * 8,
}


def render_wide(text: str, width: int, height: int = 8) -> Image.Image:
    im = Image.new("L", (width, height), 0)
    px = im.load()
    x = 0
    for ch in text:
        rows = WIDE[ch]
        for r, row in enumerate(rows[:height]):
            for c, p in enumerate(row[:8]):
                if x + c < width and p == '#':
                    px[x + c, r] = 255
        x += 8
        if x >= width:
            break
    return im


def render_narrow(text: str, width: int, height: int = 8, gap: int = 0) -> Image.Image:
    im = Image.new("L", (width, height), 0)
    px = im.load()
    x = 0
    for ch in text:
        w, rows = NARROW[ch]
        for r, row in enumerate(rows[:height]):
            for c, p in enumerate(row[:w]):
                if x + c < width and p == '#':
                    px[x + c, r] = 255
        x += w + gap
        if x >= width:
            break
    return im


def total_width_narrow(text: str, gap: int = 0) -> int:
    return sum(NARROW[ch][0] for ch in text) + (len(text) - 1) * gap


def main():
    out = REPO / "gfx/option_menu"

    # VIBRATION (9 chars) — narrow font with 1px gap
    print(f'  VIBRATION narrow width = {total_width_narrow("VIBRATION")} px (target 48)')
    img = Image.new("L", (48, 8), 0)
    inner = render_narrow("VIBRATION", width=44, gap=1)  # add gap for readability since we have room
    img.paste(inner, (2, 0))
    img.save(out / "rumble_text.png")
    print(f"  -> rumble_text.png  (48x8)")

    # CONFIG. split as "CONFI" + "G." across two existing PNGs (40+24 = 64px width)
    img = render_wide("CONFI", width=40)
    img.save(out / "key_co_text.png")
    print("  -> key_co_text.png  (CONFI wide, 40x8)")

    img = render_wide("G.", width=24)
    img.save(out / "nfig_text.png")
    print("  -> nfig_text.png    (G. wide, 24x8)")

    # TEST SON (8 chars incl space) wide font: 64 px in 72 available
    img = render_wide("TEST SON", width=72)
    img.save(out / "sound_test_text.png")
    print("  -> sound_test_text.png (TEST SON wide, 72x8)")

    # bgm_se_text.png left untouched: 24x8 is too narrow to fit MUSIQUE (7 chars) or
    # EFFETS (6 chars) without the narrow font collapsing into an illegible blur. BGM/SE
    # are universally understood gaming acronyms — keeping them.


if __name__ == "__main__":
    main()

# EU ROM reference assets

Extracted from the official multilingual European ROM:
`Pokemon Pinball (Europe) (En,Fr,De,Es,It) (SGB Enhanced).gbc` (renamed `PokemonPinballEurope.gbc`).

## Directory layout

```
eu_reference/
├── README.md                         (this file)
├── banks/                            full per-bank dumps (128 PNGs)
│   └── bank_00.png … bank_7f.png     each bank rendered as 128×512 px 2bpp
├── by_asset/                         EU equivalents of our gfx/ files
│   ├── copyright_text.{2bpp,png}
│   ├── titlescreen/titlescreen.{2bpp,png}
│   ├── pokedex/pokedex_initial.{2bpp,png}
│   ├── high_scores/high_scores_base_gameboy_*.{2bpp,png}
│   ├── option_menu/{bgm_se,sound_test,arrow}.{2bpp,png}
│   ├── key_config/{ball_start,reset,icons}_text.{2bpp,png}
│   ├── billboard/                     EU map labels, slot graphics, silhouettes
│   └── stage/                         EU per-stage bases (gameboy / gameboycolor)
├── eu_bank02_font.{png,2bpp}          full multilingual font (Latin-1, ASCII, ♂/♀, etc.)
├── eu_bank02_font_labeled.png         same with tile-ID overlay for navigation
├── eu_french_accent_tiles.{png,2bpp}  top-half tiles for FR accents (à, è, é, ê, …)
├── eu_french_accent_complete.png      same accents with top+bottom halves stacked
├── eu_pokedex_initial.png             EU Pokédex layout (≈ identical to US, 2 tiles differ)
├── eu_pokemon_names.txt               official FR Pokémon names (Gen 1-2; EU pre-dates Gen 3)
└── eu_fr_strings.txt                  every FR/DE/IT/ES UI string from the ROM
```

## How `by_asset/` was produced

For each `.2bpp` file under our `gfx/` tree, we searched the EU ROM for a 64-byte signature.
Results:

| Outcome                          | Count |
|----------------------------------|-------|
| EU bytes differ → extracted PNG  | 98    |
| Bytes identical in US & EU       | 524   |
| Not found / sparse / interleaved | 493   |

The 98 extracted are the *language- or region-specific* assets: title screen, copyright text, high-score screens, options/key-config text, map labels (`VERMILION : …`), slot machine billboards, and per-stage gameboy/gameboycolor base layers (often identical across stages, hence repeated offsets).

The "not found" set is mostly Gen 3 content (Hoenn maps, new sprites added by the *pinball-generations* hack — they obviously don't exist in the official EU ROM), interleaved fonts (the binary search doesn't see them through the interleave step), and compressed assets.

## Tile-layout notes

- Latin-1 codepoint → EU font tile-ID: `tile = codepoint + 0x1D0`.
  Example: `é` (U+00E9) → tile `0x2B9` (top half) + tile `0x2C9` (bottom half, +16 = next row in the 16-wide layout).

- The dex font renders each character as **two stacked 8×8 tiles** (top half + bottom half). The bottom halves of accented letters are typically identical to the unaccented equivalents — only the top halves carry the accent mark.

## How to integrate

To add French accents to the dex display:

1. Pick free byte values in `charmap.asm` (e.g. `$01`-`$0C`, skipping `$0D` which is the linebreak).
2. Add `charmap "è", $XX` etc. for each accent.
3. Edit `gfx/pokedex/characters.interleave.png` to insert accent top/bottom tiles at source positions matching the chosen output tile IDs (use the `interleave()` formula in `tools/gfx.c`).
4. Re-add accents to the FR text files. A find/replace `etre → être`, `tres → très`, etc. works for most cases.

To replace `lb` → `kg` and `'` → `.` for the metric Pokédex:

1. Find the `lb` and `'` tiles in `gfx/pokedex/characters.interleave.png` (output tiles `$70`, `$72`, `$83`).
2. Copy the corresponding glyphs from `eu_bank02_font.png` (you'll find a `kg` digraph and `m` suffix in the multilingual font).
3. Or just draw a `.` directly into tile `$72` and a `kg` into tile `$83` — they're 8×8 each.

The raw tile data needed for accents is in `eu_french_accent_tiles.2bpp`.

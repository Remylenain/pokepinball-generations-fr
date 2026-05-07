# EU ROM reference assets

Extracted from the official multilingual European ROM:
`Pokemon Pinball (Europe) (En,Fr,De,Es,It) (SGB Enhanced).gbc` (renamed `PokemonPinballEurope.gbc`).

## Files

- **`eu_pokedex_initial.png`** (128x192 2bpp) — EU equivalent of `gfx/pokedex/pokedex_initial.png`. Differs from US in only 2 tiles (`0x14B`, `0x14D`).

- **`eu_bank02_font.png`** (256x256 2bpp, 16KB raw) — Full multilingual font from EU bank `02`. Contains ASCII, full Latin-1 accent set, ♂/♀, etc. Drop-in compatible 2bpp PNG.

- **`eu_bank02_font_labeled.png`** — same font with tile-ID labels overlaid for navigation.

- **`eu_french_accent_tiles.png`** + **`.2bpp`** — Just the FR-relevant accent top-half tiles, side by side with their tile IDs.

- **`eu_french_accent_complete.png`** — Same accents but showing top **and** bottom halves stacked (because each glyph spans 2 vertical tiles in this engine).

- **`eu_pokemon_names.txt`** — Official FR Pokémon names extracted from EU ROM (Gen 1-2 only; EU pre-dates Gen 3). Aligns with our existing translations.

- **`eu_fr_strings.txt`** — All FR/DE/IT/ES UI strings from EU ROM. Useful for cross-checking translation choices.

## Tile-layout notes

- Latin-1 codepoint → EU font tile-ID: `tile = codepoint + 0x1D0`.
  Example: `é` (U+00E9) → tile `0x2B9` (top half) + tile `0x2C9` (bottom half, +16 = next row in the 16-wide layout).

- The dex font in this engine renders each character as **two stacked 8×8 tiles** (top half + bottom half). The bottom halves of accented letters are typically identical to the unaccented equivalents — only the top halves carry the accent mark.

## How to use

To add French accents to the dex display:

1. Pick free byte values in `charmap.asm` (e.g. `$01`-`$0C`, skipping `$0D` which is the linebreak).
2. Add `charmap "è", $XX` etc. for each accent.
3. Edit `gfx/pokedex/characters.interleave.png` to insert accent top/bottom tiles at source positions matching the chosen output tile IDs (use the `interleave()` formula in `tools/gfx.c`: source row 2K → output even tiles 32K..30+32K, source row 2K+1 → output odd tiles 1+32K..31+32K).
4. Re-add accents to the FR text files (descriptions, scrolling text…). A simple find/replace by reverse-converting "etre" → "être" etc. works for most cases.

The raw tile data needed is in `eu_french_accent_tiles.2bpp`.

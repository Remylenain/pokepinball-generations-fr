#!/usr/bin/env python3
"""
Extract EU-ROM equivalents of every gfx/ asset.

For each `.2bpp`/`.png` pair under `gfx/` (excluding `gfx/eu_reference/`):

1. Read the US bytes (`.2bpp`) and original render dimensions (from `.png`).
2. Search the EU ROM for ALL exact byte-matches of the US asset:
   - 1 match  → shared asset (same data in both ROMs). Saved under
                `eu_reference/shared/<path>.png`.
   - >1 match → still shared but stored multiple times. Same destination.
   - 0 match  → language-specific (or hack-only Gen-3 content, or compressed).
                We then scan for partial matches and extract every plausible
                variant at native and US dimensions.
3. For language-specific assets, we have no programmatic label table, so we
   tag each extracted candidate with `_bank<XX>_offs<YYYY>` and let manual
   inspection assign the correct language. A `MANIFEST.tsv` documents every
   extraction with bank/offset/dimensions, plus tentative language guesses
   based on known bank-range heuristics observed in the EU ROM.

Outputs:
    eu_reference/shared/...                 PNGs identical across US/EU
    eu_reference/candidates/<asset>/...     Per-asset candidate extractions
    eu_reference/en/...                     Promoted English versions (manual)
    eu_reference/fr/...                     Promoted French versions (manual)
    eu_reference/MANIFEST.tsv               Index of every extraction
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
GFX = REPO / "gfx"
EU_ROM_PATH = REPO / "PokemonPinballEurope.gbc"
US_ROM_PATH = REPO / "PinballGenerations.gbc"
OUT = REPO / "eu_reference"

BANK_SIZE = 0x4000  # 16 KiB


def png_dims(png_path: Path) -> tuple[int, int]:
    with Image.open(png_path) as im:
        return im.size


def twobpp_to_png_bytes(data: bytes, width: int, height: int) -> Image.Image:
    """Render a flat .2bpp tile stream as a width×height PIL image.

    GB tiles are 8×8 px, 16 bytes each, stored row-by-row.  An image of
    width×height pixels is rendered as (width//8) × (height//8) tiles laid
    out left-to-right, top-to-bottom.
    """
    if width % 8 or height % 8:
        raise ValueError(f"Dimensions must be multiples of 8: got {width}x{height}")
    tw, th = width // 8, height // 8
    needed = tw * th * 16
    if len(data) < needed:
        data = data + b"\x00" * (needed - len(data))
    palette = [0xFF, 0xAA, 0x55, 0x00]  # white, light gray, dark gray, black
    im = Image.new("L", (width, height))
    px = im.load()
    for ti in range(th):
        for tj in range(tw):
            tile = data[(ti * tw + tj) * 16 : (ti * tw + tj) * 16 + 16]
            for row in range(8):
                lo = tile[row * 2]
                hi = tile[row * 2 + 1]
                for col in range(8):
                    bit = 7 - col
                    val = ((lo >> bit) & 1) | (((hi >> bit) & 1) << 1)
                    px[tj * 8 + col, ti * 8 + row] = palette[val]
    return im


def png_to_twobpp(png_path: Path) -> bytes:
    """Convert a 2-bit grayscale PNG back to flat .2bpp tile bytes.

    Used for the *.png files in gfx/ that may not have an accompanying .2bpp.
    """
    im = Image.open(png_path).convert("L")
    w, h = im.size
    if w % 8 or h % 8:
        raise ValueError(f"Dimensions must be multiples of 8: got {w}x{h}")
    tw, th = w // 8, h // 8
    px = im.load()
    out = bytearray()
    quantize = {0xFF: 0, 0xAA: 1, 0x55: 2, 0x00: 3}
    for ti in range(th):
        for tj in range(tw):
            for row in range(8):
                lo = 0
                hi = 0
                for col in range(8):
                    g = px[tj * 8 + col, ti * 8 + row]
                    # nearest of {0xFF,0xAA,0x55,0x00}
                    v = min(quantize, key=lambda k: abs(k - g))
                    val = quantize[v]
                    bit = 7 - col
                    lo |= (val & 1) << bit
                    hi |= ((val >> 1) & 1) << bit
                out.append(lo)
                out.append(hi)
    return bytes(out)


def find_all(haystack: bytes, needle: bytes, max_results: int = 32) -> list[int]:
    out: list[int] = []
    start = 0
    while len(out) < max_results:
        i = haystack.find(needle, start)
        if i == -1:
            break
        out.append(i)
        start = i + 1
    return out


def bank_of(offset: int) -> int:
    return offset // BANK_SIZE


def collect_assets() -> list[tuple[Path, Path, tuple[int, int]]]:
    """Walk gfx/ and return (png_path, asset_bytes_source, (w, h)) entries.

    `asset_bytes_source` is the .2bpp path if present, else the .png itself
    (so callers must convert).
    """
    assets: list[tuple[Path, Path, tuple[int, int]]] = []
    for png in sorted(GFX.rglob("*.png")):
        if "eu_reference" in png.parts:
            continue
        bpp = png.with_suffix(".2bpp")
        src = bpp if bpp.exists() else png
        try:
            assets.append((png, src, png_dims(png)))
        except Exception as e:
            print(f"!! could not read {png}: {e}", file=sys.stderr)
    return assets


def load_us_bytes(src: Path) -> bytes:
    if src.suffix == ".2bpp":
        return src.read_bytes()
    return png_to_twobpp(src)


def relpath_from_gfx(png: Path) -> Path:
    return png.relative_to(GFX)


def main() -> int:
    if not EU_ROM_PATH.exists():
        print(f"Missing {EU_ROM_PATH}", file=sys.stderr)
        return 1
    eu = EU_ROM_PATH.read_bytes()

    OUT.mkdir(exist_ok=True)
    (OUT / "shared").mkdir(exist_ok=True)
    (OUT / "candidates").mkdir(exist_ok=True)
    (OUT / "en").mkdir(exist_ok=True)
    (OUT / "fr").mkdir(exist_ok=True)

    assets = collect_assets()
    print(f"Scanning {len(assets)} gfx assets against EU ROM ({len(eu):,} bytes)…")

    manifest: list[str] = [
        "rel_path\twidth\theight\tus_bytes\tstatus\teu_offsets\tnotes"
    ]
    n_shared = n_lang = n_missing = 0

    for png, src, (w, h) in assets:
        rel = relpath_from_gfx(png)
        try:
            us = load_us_bytes(src)
        except Exception as e:
            print(f"!! skip {rel}: {e}", file=sys.stderr)
            manifest.append(f"{rel}\t{w}\t{h}\t-\tERROR\t-\t{e}")
            continue

        n = len(us)
        # 1. Full match → shared
        full_matches = find_all(eu, us, max_results=4)
        if full_matches:
            dest = OUT / "shared" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            twobpp_to_png_bytes(us, w, h).save(dest)
            n_shared += 1
            manifest.append(
                f"{rel}\t{w}\t{h}\t{n}\tshared\t"
                + ",".join(f"{o:06x}" for o in full_matches)
                + "\t"
            )
            continue

        # 2. Partial signature search.  Require at least 64-byte sig (= 4 tiles
        # of distinct data) to avoid spurious matches against short repeating
        # patterns that exist all over the ROM.
        candidates: list[int] = []
        sig_len = 0
        for try_len in (min(n, 256), min(n, 128), 64):
            if try_len < 64 or try_len > n:
                continue
            sig = us[:try_len]
            # Discard low-entropy signatures (mostly zeros / repeated bytes).
            if len(set(sig)) < 6:
                continue
            hits = find_all(eu, sig, max_results=8)
            if hits:
                candidates = hits
                sig_len = try_len
                break

        if not candidates:
            n_missing += 1
            manifest.append(f"{rel}\t{w}\t{h}\t{n}\tmissing\t-\t")
            continue

        n_lang += 1
        cand_dir = OUT / "candidates" / rel.parent / rel.stem
        cand_dir.mkdir(parents=True, exist_ok=True)

        # Expand candidates: for each direct hit, also extract from the same
        # in-bank offset in banks N-3..N+3.  EU stores per-language tile data
        # in parallel banks, so adjacent banks at the same offset often hold
        # the other language variants.  These are marked "_par" for parallel.
        # Only expand parallel banks for small assets (text-style); for large
        # ones the bytes vary too much within a bank to be useful.
        expanded: list[tuple[int, bool]] = [(o, False) for o in candidates]
        seen_offsets = set(candidates)
        if n <= 512:  # roughly 32 tiles or less
            for off in candidates:
                bank = bank_of(off)
                bank_off = off & (BANK_SIZE - 1)
                for delta in (-3, -2, -1, 1, 2, 3):
                    pb = bank + delta
                    if pb < 0 or pb * BANK_SIZE >= len(eu):
                        continue
                    p_off = pb * BANK_SIZE + bank_off
                    if p_off in seen_offsets:
                        continue
                    # Require non-empty, non-monochrome region
                    region = eu[p_off : p_off + min(n, 64)]
                    if len(set(region)) < 4:
                        continue
                    expanded.append((p_off, True))
                    seen_offsets.add(p_off)

        offsets_str: list[str] = []
        for off, is_par in expanded:
            blob = eu[off : off + n]
            if len(blob) < n:
                blob = blob + b"\x00" * (n - len(blob))
            bank = bank_of(off)
            bank_off = off & (BANK_SIZE - 1)
            tag = "par" if is_par else "hit"
            name = f"bank{bank:02x}_offs{bank_off:04x}_{tag}.png"
            try:
                twobpp_to_png_bytes(blob, w, h).save(cand_dir / name)
            except Exception as e:
                print(f"  !! render fail {rel} @ {off:x}: {e}", file=sys.stderr)
                continue
            offsets_str.append(f"{off:06x}{'*' if is_par else ''}")
        manifest.append(
            f"{rel}\t{w}\t{h}\t{n}\tlang_specific(sig={sig_len})\t"
            + ",".join(offsets_str)
            + "\t* = parallel-bank speculation"
        )

    (OUT / "MANIFEST.tsv").write_text("\n".join(manifest) + "\n")
    print(f"\nDone. shared={n_shared}  language-specific={n_lang}  missing={n_missing}")
    print(f"Wrote {OUT / 'MANIFEST.tsv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

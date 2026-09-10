#!/usr/bin/env python3
"""Render pinball stage fields exactly as in-game by AUTO-PARSING the video-data
blocks in data/stage_base_gfx.asm (2 VRAM banks + attr map + retinted palettes).

Outputs (in _debug/):
  <region>_full.png        colorized top+bottom stitched (comparison screen, 20x18 each)
  <region>_<half>_edit.png 4-gray editable sheet (32x32) for reskin
  <region>_<half>_side.json per-cell metadata for lossless re-cut
"""
import re, json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GBGFX = os.path.join(ROOT, 'data/stage_base_gfx.asm')
PALASM = os.path.join(ROOT, 'data/stage_palettes.asm')
MAIN = os.path.join(ROOT, 'main.asm')

VRAM = {'vTilesOB': 0x8000, 'vTilesSH': 0x8800, 'vTilesBG': 0x9000,
        'vBGMap': 0x9800, 'vBGWin': 0x9c00}
WIN_BASE = 0x8800            # BG-addressable window start ($8800 signed mode)
WIN_N = 256                 # tiles in $8800-$97FF

# ---- label -> INCBIN file (gfx + tilemaps) ----
def incbin_map():
    m = {}
    lines = open(MAIN).read().split('\n')
    for i, l in enumerate(lines):
        lm = re.match(r'^([A-Za-z0-9_]+):', l)
        if lm:
            # find INCBIN within next couple of lines
            for j in range(i, min(i+3, len(lines))):
                im = re.search(r'INCBIN\s+"([^"]+)"', lines[j])
                if im:
                    m[lm.group(1)] = im.group(1); break
    return m
INCBIN = incbin_map()

def eval_dest(expr):
    expr = expr.strip()
    for k, v in VRAM.items():
        expr = expr.replace(k, str(v))
    expr = re.sub(r'\$([0-9A-Fa-f]+)', lambda m: str(int(m.group(1), 16)), expr)
    return eval(expr, {'__builtins__': {}}, {})

# ---- parse one field block ----
def parse_block(name):
    txt = open(GBGFX).read().split('\n')
    start = next(i for i, l in enumerate(txt) if l.startswith(name + ':'))
    tiles = []; tilemap = attrmap = pallabel = None
    for l in txt[start+1:]:
        if re.search(r'db\s+\$FF', l): break
        m = re.match(r'\s*VIDEO_DATA_TILES(_BANK2)?\s+([A-Za-z0-9_]+)\s*,\s*([^,]+),\s*(\$?\w+)', l)
        if m:
            bank = 1 if m.group(1) else 0
            tiles.append((bank, m.group(2).strip(), eval_dest(m.group(3)), eval_dest(m.group(4))))
            continue
        m = re.match(r'\s*VIDEO_DATA_TILEMAP\s+([A-Za-z0-9_]+)', l)
        if m: tilemap = m.group(1); continue
        m = re.match(r'\s*VIDEO_DATA_TILEMAP_BANK2\s+([A-Za-z0-9_]+)', l)
        if m: attrmap = m.group(1); continue
        m = re.match(r'\s*VIDEO_DATA_PALETTES\s+([A-Za-z0-9_]+)', l)
        if m: pallabel = m.group(1); continue
    return tiles, tilemap, attrmap, pallabel

# ---- 2bpp + palettes ----
def read_2bpp(path):
    data = open(os.path.join(ROOT, path), 'rb').read()
    out = []
    for t in range(len(data)//16):
        tile = []
        for y in range(8):
            lo, hi = data[t*16+y*2], data[t*16+y*2+1]
            tile.append([((hi>>(7-x))&1)<<1 | ((lo>>(7-x))&1) for x in range(8)])
        out.append(tile)
    return out

def parse_palettes(prefix):
    store = {}; cur = None; cols = []
    lab = re.compile(r'^([A-Za-z0-9_]+):')
    rgb = re.compile(r'RGB\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')
    for l in open(PALASM):
        m = lab.match(l)
        if m:
            if cur and len(cols) == 4: store[cur] = cols
            cur = m.group(1); cols = []; continue
        mm = rgb.search(l)
        if mm and cur and len(cols) < 4:
            cols.append(tuple(int(x)*255//31 for x in mm.groups()))
    if cur and len(cols) == 4: store[cur] = cols
    pal = {}
    for n in range(8):
        nm = f"{prefix}BGPalette{n}"
        if nm not in store and n == 3: nm = f"{prefix}BGPalette3Unlit"
        pal[n] = store[nm]
    return pal

def build_window(tiles_lines, bank):
    win = [[[0]*8 for _ in range(8)] for _ in range(WIN_N)]
    for b, label, dest, size in tiles_lines:
        if b != bank: continue
        if dest < WIN_BASE or dest >= WIN_BASE + WIN_N*16: continue
        off = (dest - WIN_BASE)//16
        if label not in INCBIN: continue
        ts = read_2bpp(INCBIN[label])[:size//16]
        for i, t in enumerate(ts):
            if 0 <= off+i < WIN_N: win[off+i] = t
    return win

def flip(t, xf, yf):
    r = [row[:] for row in t]
    if xf: r = [row[::-1] for row in r]
    if yf: r = r[::-1]
    return r

GRAY = [(255,255,255),(170,170,170),(85,85,85),(0,0,0)]

def render_block(name, tilemap_patch=None):
    """tilemap_patch : {offset depuis vBGMap: octet de tuile} pour simuler un
    etat de jeu. La tilemap de certaines zones est reecrite a l'execution selon
    wStageCollisionState ; sans ce patch on ne voit que l'etat au chargement."""
    tiles_lines, tmlabel, atlabel, pallabel = parse_block(name)
    bank0 = build_window(tiles_lines, 0)
    bank1 = build_window(tiles_lines, 1)
    pal = parse_palettes(pallabel[:-len('Palettes')])
    tmap = bytearray(open(os.path.join(ROOT, INCBIN[tmlabel]), 'rb').read())
    amap = open(os.path.join(ROOT, INCBIN[atlabel]), 'rb').read()
    for off, tile in (tilemap_patch or {}).items():
        if 0 <= off < len(tmap):
            tmap[off] = tile
    col = Image.new('RGB', (256, 256)); edit = Image.new('RGB', (256, 256))
    cp, ep = col.load(), edit.load(); side = []
    for r in range(32):
        for c in range(32):
            idx = r*32+c; b = tmap[idx]; attr = amap[idx]
            p = attr & 7; vb = (attr>>3)&1; xf = (attr>>5)&1; yf = (attr>>6)&1
            w = (b + 0x80) & 0xFF
            t = flip((bank1 if vb else bank0)[w], xf, yf)
            pc = pal[p]
            for y in range(8):
                for x in range(8):
                    v = t[y][x]
                    cp[c*8+x, r*8+y] = pc[v]; ep[c*8+x, r*8+y] = GRAY[v]
            side.append({'r':r,'c':c,'byte':b,'attr':attr,'win':w,'bank':vb,'xf':xf,'yf':yf,'pal':p})
    return col, edit, side

OUT = os.path.join(ROOT, '_work')
REGIONS = ['Red', 'Blue', 'Gold', 'Silver', 'Ruby', 'Sapphire']

def crop_screen(img):  # visible 20x18 tiles = 160x144
    return img.crop((0, 0, 160, 144))

if __name__ == '__main__':
    EDIT_FIELDS = [('Ruby','Top'),('Ruby','Bottom'),('Sapphire','Top'),('Sapphire','Bottom')]
    for region in REGIONS:
        halves = {}
        for half in ['Top', 'Bottom']:
            name = f"Stage{region}Field{half}Gfx_GameBoyColor"
            col, edit, side = render_block(name)
            halves[half] = col
            if (region, half) in EDIT_FIELDS:
                tag = f"{region.lower()}_{half.lower()}"
                edit.save(f"{OUT}/{tag}_edit.png")
                json.dump(side, open(f"{OUT}/{tag}_side.json", 'w'))
        # stitched full-table comparison screen (top over bottom)
        full = Image.new('RGB', (160, 288))
        full.paste(crop_screen(halves['Top']), (0, 0))
        full.paste(crop_screen(halves['Bottom']), (0, 144))
        full.resize((480, 864), Image.NEAREST).save(f"{OUT}/{region.lower()}_full.png")
        print(f"{region}: full table + edits done")

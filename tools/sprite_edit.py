#!/usr/bin/env python3
"""Editeur de sprites de plateau (Pokemon Pinball Generations).

Sort un Pokemon d'un plateau sous forme d'une seule planche PNG, en vraies
couleurs, prete a redessiner dans n'importe quel editeur d'images. Puis la
redecoupe et la reecrit dans les bons fichiers sources.

  list <table>
      Les creatures REELLEMENT dessinees par ce plateau. Chaque table a son
      casting : Rouge/Or/Rubis ont ditto, voltorb, staryu, bellsprout, spinner ;
      Bleu/Argent/Saphir ont cloyster, shellder, slowpoke, spinner.

  export <table> <creature>
      _work/<table>_top_<creature>.png      <- la planche a redessiner
      _work/<table>_top_<creature>_x6.png   <- la meme en x6, pour regarder
      _work/<table>_top_<creature>.json     <- plan de decoupe (ne pas toucher)
      Cadres roses = les frames sprite. Cadres verts = la partie de la bestiole
      dessinee dans le FOND, avec une boite par etat du plateau.

  import <table> <creature>
      Redecoupe la planche et reecrit les gfx/stage/<table>_top/*.png.

  preview <table> <creature>
      Rend le plateau comme en jeu, un panneau par etat.

Options :
  --palette    (import) fabrique la palette A PARTIR du dessin et l'ecrit dans
               data/stage_palettes.asm, au lieu d'y ramener le dessin de force.
  --dry-run    (import) dit ce qu'il ferait sans rien ecrire.
  --force      (export) ecrase la planche en cours sans la sauvegarder.
  --bottom     travaille sur la moitie basse du plateau (aucune des six
               tables actuelles n'y a de creature).
  --scale=N    facteur de zoom de l'apercu (defaut 6).

Regles a respecter en dessinant :
  - ne pas changer la taille de l'image ;
  - rester dans les cadres ;
  - 3 couleurs opaques maximum par sprite, plus le transparent (limite
    materielle du Game Boy Color, elle ne se contourne pas) ;
  - dans les cadres verts la couleur 0 est opaque : en fond il n'y a pas de
    transparence.
"""

import json
import os
import re
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OAM_ASM = os.path.join(ROOT, 'data/oam_frames.asm')
GFX_ASM = os.path.join(ROOT, 'data/stage_base_gfx.asm')
PAL_ASM = os.path.join(ROOT, 'data/stage_palettes.asm')
MAIN_ASM = os.path.join(ROOT, 'main.asm')
WORK = os.path.join(ROOT, '_work')

VRAM = {'vTilesOB': 0x8000, 'vTilesSH': 0x8800, 'vTilesBG': 0x9000,
        'vBGMap': 0x9800, 'vBGWin': 0x9c00}

# Fonctions de dessin communes a tous les plateaux : ce ne sont pas des
# creatures du plateau et elles tapent dans des fichiers gfx partages.
NOT_CREATURES = {
    'timer', 'pinball', 'flippers', 'sprites', 'monsprite',
    'evolutionindicatorarrows', 'evolutiontrinket', 'animatedmon',
    'pikachusavers', 'slotglow', 'moncaptureanimation', 'saver',
}

# Suffixes de nom de fonction a retirer pour regrouper une meme creature
# (DrawBellsproutHead + DrawBellsproutBody = une seule bestiole).
NAME_SUFFIXES = ('sprites', 'sprite', 'head', 'body')

GUTTER = 8          # marge transparente entre deux frames dans la planche
CANON_GRAYS = [(255, 255, 255), (170, 170, 170), (85, 85, 85), (0, 0, 0)]


# --------------------------------------------------------------------------
# lecture des sources
# --------------------------------------------------------------------------

def incbin_map():
    """label asm -> chemin du fichier INCBIN."""
    out = {}
    lines = open(MAIN_ASM).read().split('\n')
    for i, l in enumerate(lines):
        m = re.match(r'^([A-Za-z0-9_]+):', l)
        if not m:
            continue
        for j in range(i, min(i + 3, len(lines))):
            im = re.search(r'INCBIN\s+"([^"]+)"', lines[j])
            if im:
                out[m.group(1)] = im.group(1)
                break
    return out


def eval_dest(expr):
    expr = expr.strip()
    for k, v in VRAM.items():
        expr = expr.replace(k, str(v))
    expr = re.sub(r'\$([0-9A-Fa-f]+)', lambda m: str(int(m.group(1), 16)), expr)
    return eval(expr, {'__builtins__': {}}, {})


def parse_oam_frames():
    """nom de frame -> [(dy, dx, tile, attr), ...] et table des ids."""
    frames, order = {}, []
    cur, ent = None, []
    for line in open(OAM_ASM):
        m = re.match(r'^([A-Za-z0-9_]+):', line)
        if m:
            if cur:
                frames[cur] = ent
            cur, ent = m.group(1), []
            continue
        if cur is None:
            continue
        if re.match(r'\s*db\s+\$80\b', line):
            frames[cur] = ent
            cur = None
            continue
        vals = re.findall(r'\$([0-9A-Fa-f]{2})', line)
        if len(vals) >= 4:
            ent.append(tuple(int(v, 16) for v in vals[:4]))
    if cur:
        frames[cur] = ent
    # table id -> nom (OAMDataPointers)
    inside = False
    for line in open(OAM_ASM):
        if line.startswith('OAMDataPointers:'):
            inside = True
            continue
        if inside:
            m = re.match(r'\s*dw\s+([A-Za-z0-9_]+)', line)
            if m:
                order.append(m.group(1))
            elif line.strip() and not line.startswith(';'):
                break
    return frames, order


def parse_pointer_tables():
    """{1: [nom de frame par id], 2: [...]} d'apres OAMDataPointers(2)."""
    tables, cur = {}, None
    for line in open(OAM_ASM):
        m = re.match(r'^OAMDataPointers(2?):', line)
        if m:
            cur = 2 if m.group(1) else 1
            tables[cur] = []
            continue
        if cur is None:
            continue
        m = re.match(r'\s*dw\s+([A-Za-z0-9_]+)', line)
        if m:
            tables[cur].append(m.group(1))
        elif line.strip() and not line.lstrip().startswith(';'):
            cur = None
    return tables


def field_creatures(field, raw=False):
    """Decouvre les creatures REELLEMENT dessinees par ce plateau.

    Chaque plateau a son propre casting : la famille Rouge (Rouge/Or/Rubis) a
    Metamorph, Voltorbe, Stari, Chetiflor ; la famille Bleue (Bleu/Argent/
    Saphir) a Kokiyas, Ramoloss, Crustabri. On lit donc le fichier de dessin
    du plateau au lieu de supposer.
    """
    path = os.path.join(
        ROOT, f'engine/pinball_game/draw_sprites/draw_{field.lower()}_field_sprites.asm')
    if not os.path.exists(path):
        die(f"fichier de dessin introuvable pour le plateau {field}")
    tables = parse_pointer_tables()
    lines = open(path).read().split('\n')

    # decoupe en sections : une fonction Draw* et les donnees qui la suivent
    sections, cur, buf = [], None, []
    for l in lines:
        m = re.match(r'^Draw([A-Za-z0-9]+?)(?:_[A-Za-z0-9]*(?:Field|Stage)[A-Za-z]*)?:', l)
        if m:
            if cur:
                sections.append((cur, buf))
            cur, buf = m.group(1), []
            continue
        if cur:
            buf.append(l)
    if cur:
        sections.append((cur, buf))

    out, rawout = {}, {}
    for name, body in sections:
        key = name.lower()
        for suf in NAME_SUFFIXES:
            if key.endswith(suf) and len(key) > len(suf):
                key = key[:-len(suf)]
                break
        if key in NOT_CREATURES or not key:
            continue
        which = 2 if any('LoadOAMData2' in l for l in body) else 1
        table = tables.get(which, [])
        ids, label = [], None
        for l in body:
            m = re.match(r'^([A-Za-z0-9_]+):', l)
            if m:
                label = m.group(1)
                continue
            if label is None:
                continue
            if not re.match(r'\s*db\s+\$', l):
                continue
            vals = [int(v, 16) for v in re.findall(r'\$([0-9A-Fa-f]{2})', l)]
            # Deux formes seulement sont fiables : un label *OAMIds*, ou une
            # ligne db explicitement commentee '; oam ids'. Surtout PAS les
            # AnimationData, dont le 2e octet est un numero de frame et non un
            # id OAM (ca donnait des sprites sans rapport).
            if 'OAMIds' in label:
                ids += vals
            elif re.search(r';.*oam ids', l, re.I):
                ids += vals
        frames = []
        for i in ids:
            if i < len(table) and table[i] not in frames:
                frames.append(table[i])
        if frames:
            out.setdefault(key, [])
            for f in frames:
                if f not in out[key]:
                    out[key].append(f)
            rawout.setdefault(key, [])
            rawout[key] += [table[i] for i in ids if i < len(table)]
    return rawout if raw else out


def variants_by_state(field, region_cells):
    """{etat de collision: ecritures de tilemap} d'apres la table 8x8.

    L'index d'une entree vaut etat_precedent * 8 + etat_courant ; toutes les
    transitions qui menent au meme etat ecrivent la meme chose, on garde donc
    une seule version par etat.
    """
    path = os.path.join(ROOT,
                        f'data/queued_tiledata/{field.lower()}_field/structures.asm')
    if not os.path.exists(path):
        return {}
    labels = parse_asm(path)
    tables = [l for l in labels if l.startswith('TileDataPointers_')]
    if not tables:
        return {}
    want = {VBGMAP + r * 32 + c for r, c in region_cells}
    out, conflicts_by_state = {}, {}
    for i, (_, expr) in enumerate(labels[tables[-1]]):
        v = ev(expr, labels)
        if not isinstance(v, str) or v not in labels:
            continue
        head = labels[v]
        if not head or head[0][0] != 'db':
            continue
        w = {}
        for _, e2 in head[1:]:
            sub2 = ev(e2, labels)
            if isinstance(sub2, str) and sub2 in labels:
                w.update(decode_chunk(sub2, labels))
        w = {a - VBGMAP: t for a, t in w.items() if a in want}
        if not w:
            continue
        # Une transition ne reecrit que ce qui differe entre l'etat de depart et
        # celui d'arrivee : il faut fusionner toutes celles qui menent au meme
        # etat pour obtenir sa tilemap complete.
        cur = i % 8
        acc = out.setdefault(cur, {})
        for a, t in w.items():
            if a in acc and acc[a] != t:
                conflicts_by_state.setdefault(cur, set()).add(a)
            acc[a] = t
    return out


def parse_video_block(field, half):
    """Retourne obj_owner[bank][tile 0..255] = (label, index dans le fichier)."""
    name = f"Stage{field}Field{half}Gfx_GameBoyColor"
    txt = open(GFX_ASM).read().split('\n')
    try:
        start = next(i for i, l in enumerate(txt) if l.startswith(name + ':'))
    except StopIteration:
        die(f"bloc {name} introuvable dans data/stage_base_gfx.asm")
    owner = [[None] * 256, [None] * 256]      # tuiles OBJ, $8000 + n*16
    owner_bg = [[None] * 256, [None] * 256]   # fenetre BG, $8800 + w*16
    pal_label = None
    for l in txt[start + 1:]:
        if re.search(r'db\s+\$FF', l):
            break
        m = re.match(r'\s*VIDEO_DATA_TILES(_BANK2)?\s+([A-Za-z0-9_]+)\s*,\s*([^,]+),\s*(\$?\w+)', l)
        if m:
            bank = 1 if m.group(1) else 0
            label, dest, size = m.group(2).strip(), eval_dest(m.group(3)), eval_dest(m.group(4))
            first = (dest - 0x8000) // 16          # index de tuile OBJ
            wfirst = (dest - 0x8800) // 16         # index dans la fenetre BG
            for i in range(size // 16):
                t = first + i
                if 0 <= t < 256:
                    owner[bank][t] = (label, i)     # le dernier ecrit gagne
                w = wfirst + i
                if 0 <= w < 256:
                    owner_bg[bank][w] = (label, i)
            continue
        m = re.match(r'\s*VIDEO_DATA_PALETTES\s+([A-Za-z0-9_]+)', l)
        if m:
            pal_label = m.group(1)
    return owner, owner_bg, pal_label


def parse_palettes(prefix, kind='OBJ'):
    store, cur, cols = {}, None, []
    for line in open(PAL_ASM):
        m = re.match(r'^([A-Za-z0-9_]+):', line)
        if m:
            if cur and len(cols) == 4:
                store[cur] = cols
            cur, cols = m.group(1), []
            continue
        mm = re.search(r'RGB\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', line)
        if mm and cur and len(cols) < 4:
            cols.append(tuple(int(x) * 255 // 31 for x in mm.groups()))
    if cur and len(cols) == 4:
        store[cur] = cols
    out = {}
    for n in range(8):
        key = f"{prefix}{kind}Palette{n}"
        if key not in store and n == 3:
            key = f"{prefix}{kind}Palette3Unlit"
        if key in store:
            out[n] = store[key]
    return out


# --------------------------------------------------------------------------
# tuiles <-> PNG
# --------------------------------------------------------------------------

def png_tiles(path):
    """Lit un PNG source et rend (liste de tuiles 8x8 d'indices, couleurs)."""
    im = Image.open(os.path.join(ROOT, path)).convert('RGB')
    colors = sorted((c for _, c in im.getcolors(1 << 24)),
                    key=lambda c: -(c[0] + c[1] + c[2]))
    while len(colors) < 4:                       # PNG a moins de 4 teintes
        for g in CANON_GRAYS:
            if g not in colors:
                colors.append(g)
                break
        colors.sort(key=lambda c: -(c[0] + c[1] + c[2]))
    idx = {c: i for i, c in enumerate(colors[:4])}
    px = im.load()
    tiles = []
    for ty in range(im.height // 8):
        for tx in range(im.width // 8):
            tiles.append([[idx[px[tx * 8 + x, ty * 8 + y]] for x in range(8)]
                          for y in range(8)])
    return tiles, colors[:4], (im.width // 8, im.height // 8)


def write_png_tiles(path, tiles, colors, grid):
    w, h = grid
    im = Image.new('RGB', (w * 8, h * 8))
    px = im.load()
    for i, t in enumerate(tiles):
        tx, ty = i % w, i // w
        for y in range(8):
            for x in range(8):
                px[tx * 8 + x, ty * 8 + y] = colors[t[y][x]]
    im.convert('RGBA').save(os.path.join(ROOT, path))


def verify_with_rgbgfx(path, tiles):
    """rgbgfx deduit l'index d'une couleur de sa luminosite : si le dessin
    n'utilise plus les 4 niveaux, tous les index glissent et les couleurs
    sortent fausses en jeu. On reconvertit pour de vrai et on compare."""
    import shutil
    import subprocess
    import tempfile
    if not shutil.which('rgbgfx'):
        return None
    with tempfile.NamedTemporaryFile(suffix='.2bpp', delete=False) as f:
        tmp = f.name
    try:
        r = subprocess.run(['rgbgfx', '-o', tmp, os.path.join(ROOT, path)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return f"rgbgfx refuse le fichier : {r.stderr.strip()}"
        data = open(tmp, 'rb').read()
        for i, want in enumerate(tiles):
            got = [[((data[i * 16 + y * 2 + 1] >> (7 - x) & 1) << 1) |
                    (data[i * 16 + y * 2] >> (7 - x) & 1) for x in range(8)]
                   for y in range(8)]
            if got != want:
                return (f"tuile {i} relue differemment apres conversion — "
                        f"le dessin n'utilise probablement plus les 4 niveaux "
                        f"de gris du fichier, ce qui decale les index")
        return None
    finally:
        os.unlink(tmp)


# --------------------------------------------------------------------------
# mise en planche
# --------------------------------------------------------------------------

def layout(frames, names):
    """Place chaque frame cote a cote. Rend (largeur, hauteur, boites)."""
    boxes, x = [], GUTTER
    height = 0
    for n in names:
        ent = frames[n]
        if not ent:
            die(f"frame OAM vide : {n}")
        minx = min(e[1] for e in ent)
        miny = min(e[0] for e in ent)
        w = max(e[1] for e in ent) - minx + 8
        h = max(e[0] for e in ent) - miny + 16
        boxes.append({'name': n, 'x': x, 'y': GUTTER, 'w': w, 'h': h,
                      'minx': minx, 'miny': miny})
        x += w + GUTTER
        height = max(height, h)
    return x, height + 2 * GUTTER, boxes


VBGMAP = 0x9800

# --------------------------------------------------------------------------
# variantes de tilemap : la partie fond d'une creature change selon l'etat
# --------------------------------------------------------------------------

def parse_asm(path):
    """label -> liste de ('db'|'dw', expression brute)."""
    out, cur = {}, None
    for line in open(path):
        line = line.split(';')[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):', line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, [])
            line = line[m.end():]
        if cur is None:
            continue
        m = re.match(r'\s*(db|dw)\s+(.*)', line)
        if m:
            kind = m.group(1)
            for e in split_args(m.group(2)):
                out[cur].append((kind, e.strip()))
    return out


def split_args(s):
    """Coupe sur les virgules de premier niveau."""
    parts, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur)
            cur = ''
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def ev(expr, labels):
    """Evalue une expression asm simple. Rend un int, ou le nom d'un label."""
    e = expr.strip()
    if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', e) and e in labels:
        return e
    m = re.match(r'Bank\(', e)
    if m:
        return 0
    e2 = re.sub(r'\$([0-9A-Fa-f]+)', lambda m: str(int(m.group(1), 16)), e)
    e2 = e2.replace('vBGMap', str(VBGMAP)).replace('vBGWin', '0x9c00')
    e2 = re.sub(r'\btile\b', '', e2)
    if re.search(r'[A-Za-z_]', e2):
        return e.strip()                      # label non resolu
    try:
        return int(eval(e2, {'__builtins__': {}}, {}))
    except Exception:
        return e.strip()


def flatten(label, labels):
    """Octets d'un label, les 'dw' vers un label restant symboliques."""
    out = []
    for kind, expr in labels.get(label, []):
        v = ev(expr, labels)
        if kind == 'db':
            out.append(v if isinstance(v, int) else 0)
        else:
            out.append(('ptr', v) if isinstance(v, str) else v & 0xFF)
            if isinstance(v, int):
                out.append((v >> 8) & 0xFF)
    return out


def decode_chunk(label, labels):
    """Rend les ecritures {adresse vBGMap: octet de tuile} d'un chunk."""
    by = flatten(label, labels)
    if not by or not isinstance(by[0], tuple):
        return {}
    func = by[0][1]
    d = by[1:]
    if not all(isinstance(x, int) for x in d):
        return {}
    w = {}
    if func.startswith('Func_1198'):
        # db total ; puis [ (n<<1)|start ][ dest lo ][ dest hi ][ start? ] ; 0
        i, c = 1, 0
        while i < len(d) and d[i] != 0:
            b = d[i]
            dest = d[i + 1] | (d[i + 2] << 8)
            i += 3
            n, has = b >> 1, b & 1
            if has:
                c = d[i]
                i += 1
            for k in range(n):
                w[dest + k] = (c + k) & 0xFF
            c = (c + n) & 0xFF
    elif func.startswith('LoadTileLists'):
        # db total ; puis [ n ][ dest lo ][ dest hi ][ n octets ] ; 0
        i = 1
        while i < len(d) and d[i] != 0:
            n = d[i]
            dest = d[i + 1] | (d[i + 2] << 8)
            i += 3
            for k in range(n):
                w[dest + k] = d[i + k]
            i += n
    return w


def variants(field, region_cells):
    """Toutes les tilemaps possibles pour les cellules donnees."""
    path = os.path.join(ROOT, f'data/queued_tiledata/{field.lower()}_field/structures.asm')
    if not os.path.exists(path):
        return []
    labels = parse_asm(path)
    tables = [l for l in labels if l.startswith('TileDataPointers_')]
    if not tables:
        return []
    table = tables[-1]                        # la seconde table est la version GBC
    want = {VBGMAP + r * 32 + c for r, c in region_cells}
    out = []
    for kind, expr in labels[table]:
        v = ev(expr, labels)
        if not isinstance(v, str) or v not in labels:
            continue
        # entete : db nombre de chunks ; puis dw pointeurs
        head = labels[v]
        if not head or head[0][0] != 'db':
            continue
        w = {}
        for k2, e2 in head[1:]:
            sub = ev(e2, labels)
            if isinstance(sub, str) and sub in labels:
                w.update(decode_chunk(sub, labels))
        w = {a: t for a, t in w.items() if a in want}
        if w and w not in out:
            out.append(w)
    return out




def bg_region(field, half, frames, names, margin_below=3):
    """Les cellules de FOND qui appartiennent a la creature.

    Une partie du Pokemon est dessinee dans le fond, pas en OAM (typiquement le
    bas de celui qui bloque le couloir de lancement). On la retrouve ainsi : on
    prend les cellules autour de l'emprise des sprites, et on ne garde que
    celles dont la palette BG ne sert **nulle part ailleurs** sur l'ecran. Une
    palette dediee a cette zone = des tuiles dediees a cet objet.
    """
    tag = f"stage_{field.lower()}_field_{half.lower()}_gameboycolor"
    base = os.path.join(ROOT, 'gfx/tilemaps', tag)
    if not os.path.exists(base + '.map'):
        return None
    tm = open(base + '.map', 'rb').read()
    am = open(base + '_2.map', 'rb').read()
    xs, ys = [], []
    for n in names:
        for dy, dx, tile, attr in frames[n]:
            xs += [dx - 8, dx - 1]
            ys += [dy, dy + 15]
    if not xs:
        return None
    c0, c1 = max(0, min(xs) // 8 - 1), min(19, max(xs) // 8 + 1)
    r0, r1 = max(0, min(ys) // 8 - 1), min(17, max(ys) // 8 + margin_below)
    cand = {(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)}
    pin = {am[r * 32 + c] & 7 for r, c in cand}
    pout = {am[r * 32 + c] & 7 for r in range(18) for c in range(20)
            if (r, c) not in cand}
    private = pin - pout
    sel = sorted((r, c) for r, c in cand if (am[r * 32 + c] & 7) in private)
    if not sel:
        return None
    rr = [r for r, _ in sel]
    cc = [c for _, c in sel]
    # La tilemap de cette zone est reecrite a chaque changement d'etat : le bas
    # de la bestiole n'a pas la meme hauteur selon qu'elle est au repos,
    # deployee ou retractee. On sort donc TOUTES les variantes, pas seulement
    # celle presente dans la tilemap statique.
    vs = variants(field, sel)
    static = {VBGMAP + r * 32 + c: tm[r * 32 + c] for r, c in sel}
    if static not in vs:
        vs.append(static)
    out = []
    for vi, v in enumerate(vs):
        cells = []
        for r, c in sel:
            a = VBGMAP + r * 32 + c
            if a not in v:
                continue
            attr = am[r * 32 + c]
            cells.append({'row': r, 'col': c, 'win': (v[a] + 0x80) & 0xFF,
                          'attr': attr, 'bank': (attr >> 3) & 1, 'pal': attr & 7})
        if cells:
            out.append(cells)
    return {'r0': min(rr), 'r1': max(rr), 'c0': min(cc), 'c1': max(cc),
            'pals': sorted(private), 'variants': out}


def check_overlaps(frames, names):
    """Deux tuiles d'une meme frame qui se recouvrent = decoupe ambigue."""
    bad = []
    for n in names:
        seen = []
        for dy, dx, tile, attr in frames[n]:
            for (py, px_, pt) in seen:
                if abs(dx - px_) < 8 and abs(dy - py) < 16:
                    bad.append((n, hex(pt), hex(tile)))
            seen.append((dy, dx, tile))
    return bad


# --------------------------------------------------------------------------
# commandes
# --------------------------------------------------------------------------

def die(msg):
    print(f"\n  ERREUR : {msg}\n", file=sys.stderr)
    sys.exit(1)


def resolve(field, half, names):
    global OWN_DIR
    OWN_DIR = f"gfx/stage/{field.lower()}_{half.lower()}/"
    frames, _ = parse_oam_frames()
    owner, owner_bg, pal_label = parse_video_block(field, half)
    prefix = pal_label[:-len('Palettes')]
    objpal = parse_palettes(prefix, 'OBJ')
    bgpal = parse_palettes(prefix, 'BG')
    incbin = incbin_map()
    for n in names:
        if n not in frames:
            die(f"frame OAM inconnue : {n}")
    return frames, owner, objpal, incbin, owner_bg, bgpal


OWN_DIR = None      # 'gfx/stage/<table>_<moitie>/' du plateau en cours


def tile_source(owner, incbin, bank, tile):
    """(chemin du PNG source, index de la tuile dans ce PNG) ou None.

    Refuse tout fichier hors du dossier du plateau : les gfx partages
    (gfx/stage/shared/, la bille...) servent a TOUTES les tables, y ecrire
    abimerait les autres. Ca arrive si on demande une creature de la moitie
    haute avec --bottom, par exemple.
    """
    o = owner[bank][tile]
    if o is None:
        return None
    label, i = o
    path = incbin.get(label)
    if path and path.endswith('.2bpp'):
        path = path[:-len('.2bpp')] + '.png'    # le PNG est la vraie source
    if path and OWN_DIR and OWN_DIR not in path:
        die(f"la tuile ${tile:02x} pointe vers {path}, qui n'appartient pas a ce\n"
            f"          plateau et sert a d'autres tables. Verifie la moitie "
            f"demandee (--bottom ?).")
    return path, i


def cmd_list(field, half):
    frames_all, owner, objpal, incbin, _, _ = resolve(field, half, [])
    creatures = field_creatures(field)
    if not creatures:
        die(f"aucune creature trouvee pour le plateau {field}")
    print(f"\nPlateau {field} / {half} — creatures reellement dessinees :\n")
    for key in sorted(creatures):
        names = creatures[key]
        files = set()
        for n in names:
            if n not in frames_all:
                continue
            for dy, dx, tile, attr in frames_all[n]:
                for t in (tile & 0xFE, (tile & 0xFE) + 1):
                    src = tile_source(owner, incbin, (attr >> 3) & 1, t)
                    if src and src[0]:
                        files.add(src[0])
        short = sorted(os.path.basename(f) for f in files)
        print(f"  {key:<12} {len(names)} frame(s)   {', '.join(short) or '?'}")
    print(f"\n  export : python3 tools/sprite_edit.py export {field.lower()} <nom>\n")


def cmd_export(field, half, key, names, scale, force=False):
    frames, owner, objpal, incbin, owner_bg, bgpal = resolve(field, half, names)
    over = check_overlaps(frames, names)
    if over:
        for n, a, b in over:
            print(f"  ATTENTION {n}: tuiles {a} et {b} se recouvrent")

    W, H, boxes = layout(frames, names)
    bgr = bg_region(field, half, frames, names)
    if bgr:
        bgw = (bgr['c1'] - bgr['c0'] + 1) * 8
        bgh = (bgr['r1'] - bgr['r0'] + 1) * 8
        bgr['w'], bgr['h'] = bgw, bgh
        bgr['x'], bgr['y'] = W + GUTTER, GUTTER
        W += GUTTER + len(bgr['variants']) * (bgw + GUTTER)
        H = max(H, bgh + 2 * GUTTER)
        # nommer les variantes : celle a le plus de tuiles distinctes est
        # l'etat deploye, celle qui en a le moins est le plateau nu
        counts = [len({c['win'] for c in v}) for v in bgr['variants']]
        bgr['labels'] = []
        for i, n in enumerate(counts):
            if n == max(counts):
                bgr['labels'].append('deploye')
            elif n == min(counts):
                bgr['labels'].append('retracte')
            else:
                bgr['labels'].append('au repos')
    sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    guide = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    entries = []
    files_used = set()

    for box in boxes:
        n = box['name']
        # ordre inverse : l'entree OAM la plus basse dessine par-dessus
        for order_i, (dy, dx, tile, attr) in reversed(list(enumerate(frames[n]))):
            bank = (attr >> 3) & 1
            pal = objpal.get(attr & 7, CANON_GRAYS)
            ox = box['x'] + dx - box['minx']
            oy = box['y'] + dy - box['miny']
            for k in (0, 1):
                t = (tile & 0xFE) + k
                src = tile_source(owner, incbin, bank, t)
                if not src or not src[0]:
                    die(f"tuile ${t:02x} (banque {bank}) : aucun fichier source "
                        f"dans le bloc video de {field} {half}")
                path, idx = src
                files_used.add(path)
                tiles, colors, grid = png_tiles(path)
                td = tiles[idx]
                if attr & 0x20:
                    td = [row[::-1] for row in td]
                if attr & 0x40:
                    td = td[::-1]
                for y in range(8):
                    for x in range(8):
                        v = td[y][x]
                        if v == 0:
                            continue            # couleur 0 = transparent (OBJ)
                        sheet.putpixel((ox + x, oy + y + k * 8), pal[v] + (255,))
            entries.append({'frame': n, 'i': order_i, 'x': ox, 'y': oy,
                            'tile': tile, 'attr': attr, 'bank': bank,
                            'pal': attr & 7})
        # cadre du guide
        for x in range(box['x'], box['x'] + box['w']):
            for y in (box['y'] - 1, box['y'] + box['h']):
                guide.putpixel((x, y), (255, 0, 128, 255))
        for y in range(box['y'], box['y'] + box['h']):
            for x in (box['x'] - 1, box['x'] + box['w']):
                guide.putpixel((x, y), (255, 0, 128, 255))

    if bgr:
        for vi, cells in enumerate(bgr['variants']):
            bx = bgr['x'] + vi * (bgw + GUTTER)
            for cell in cells:
                src = tile_source(owner_bg, incbin, cell['bank'], cell['win'])
                if not src or not src[0]:
                    die(f"cellule de fond ligne {cell['row']} colonne "
                        f"{cell['col']} : fenetre {cell['win']} sans source")
                path, idx = src
                files_used.add(path)
                tiles, colors, grid = png_tiles(path)
                td = tiles[idx]
                if cell['attr'] & 0x20:
                    td = [row[::-1] for row in td]
                if cell['attr'] & 0x40:
                    td = td[::-1]
                pal = bgpal.get(cell['pal'], CANON_GRAYS)
                ox = bx + (cell['col'] - bgr['c0']) * 8
                oy = bgr['y'] + (cell['row'] - bgr['r0']) * 8
                cell['x'], cell['y'] = ox, oy
                for y in range(8):
                    for x in range(8):
                        # en fond la couleur 0 est opaque, ce n'est pas du vide
                        sheet.putpixel((ox + x, oy + y), pal[td[y][x]] + (255,))
            for x in range(bx, bx + bgw):
                for y in (bgr['y'] - 1, bgr['y'] + bgh):
                    guide.putpixel((x, y), (0, 190, 90, 255))
            for y in range(bgr['y'], bgr['y'] + bgh):
                for x in (bx - 1, bx + bgw):
                    guide.putpixel((x, y), (0, 190, 90, 255))

    os.makedirs(WORK, exist_ok=True)
    tag = f"{field.lower()}_{half.lower()}_{key}"
    out_png = os.path.join(WORK, tag + '.png')
    # Ne jamais ecraser un dessin en cours sans prevenir : on compare a ce que
    # l'export produirait et on met de cote si ca differe.
    if os.path.exists(out_png) and not force:
        try:
            old_im = Image.open(out_png).convert('RGBA')
            # comparaison octet a octet : sur une image RGBA, getbbox() de
            # Pillow ne regarde que le canal alpha et raterait un changement
            # de couleur.
            differs = (old_im.size != sheet.size
                       or old_im.tobytes() != sheet.tobytes())
        except Exception:
            differs = True
        if differs:
            n = 1
            while os.path.exists(os.path.join(WORK, f"{tag}.sauvegarde{n}.png")):
                n += 1
            bak = os.path.join(WORK, f"{tag}.sauvegarde{n}.png")
            os.rename(out_png, bak)
            print(f"\n  Ton dessin en cours a ete mis de cote dans")
            print(f"    _work/{os.path.basename(bak)}")
            print(f"  (l'export repart des graphismes du jeu ; "
                  f"--force pour ecraser sans sauvegarde)")
    sheet.save(out_png)

    # version zoomee avec grille 8x16 + cadres, uniquement pour regarder
    big = sheet.resize((W * scale, H * scale), Image.NEAREST)
    bg = Image.new('RGBA', big.size, (255, 255, 255, 255))
    for by in range(0, big.height, 16):
        for bx in range(0, big.width, 16):
            if (bx // 16 + by // 16) % 2:
                for y in range(by, min(by + 16, big.height)):
                    for x in range(bx, min(bx + 16, big.width)):
                        bg.putpixel((x, y), (214, 214, 214, 255))
    bg.alpha_composite(big)
    gbig = guide.resize((W * scale, H * scale), Image.NEAREST)
    bg.alpha_composite(gbig)
    grid_col = (0, 128, 255, 90)
    ov = Image.new('RGBA', bg.size, (0, 0, 0, 0))
    for e in entries:
        for y in range(e['y'] * scale, (e['y'] + 16) * scale):
            for x in (e['x'] * scale, (e['x'] + 8) * scale - 1):
                if 0 <= x < ov.width and 0 <= y < ov.height:
                    ov.putpixel((x, y), grid_col)
        for x in range(e['x'] * scale, (e['x'] + 8) * scale):
            for y in (e['y'] * scale, (e['y'] + 16) * scale - 1):
                if 0 <= x < ov.width and 0 <= y < ov.height:
                    ov.putpixel((x, y), grid_col)
    bg.alpha_composite(ov)
    bg.convert('RGB').save(os.path.join(WORK, tag + f'_x{scale}.png'))

    json.dump({'field': field, 'half': half, 'key': key, 'names': names,
               'w': W, 'h': H, 'boxes': boxes, 'entries': entries, 'bg': bgr},
              open(os.path.join(WORK, tag + '.json'), 'w'), indent=1)

    print(f"\n  A REDESSINER  : _work/{tag}.png   ({W}x{H} px)")
    print(f"  a regarder    : _work/{tag}_x{scale}.png")
    print(f"\n  Frames incluses : {', '.join(names)}")
    print(f"  Fichiers qui seront reecrits a l'import :")
    for f in sorted(files_used):
        print(f"    {f}")
    pals = sorted({e['pal'] for e in entries})
    for p in pals:
        cols = objpal.get(p, [])
        print(f"  Palette OBJ {p} : couleur 0 = transparent, "
              f"puis {', '.join('#%02x%02x%02x' % c for c in cols[1:])}")
    if bgr:
        print(f"\n  Cadres VERTS a droite = la partie de la bestiole dessinee dans")
        print(f"  le FOND, pas en sprite (lignes {bgr['r0']}-{bgr['r1']}, "
              f"colonnes {bgr['c0']}-{bgr['c1']}).")
        print(f"  La tilemap de cette zone est reecrite a chaque changement d'etat,")
        print(f"  d'ou {len(bgr['variants'])} variantes a dessiner, dans l'ordre :")
        for i, lbl in enumerate(bgr['labels'], 1):
            print(f"    {i}. {lbl}")
        print(f"  Des cellules identiques d'une variante a l'autre partagent la meme")
        print(f"  tuile : dessine-les pareil, sinon la derniere l'emporte.")
        for p in bgr['pals']:
            cols = bgpal.get(p, [])
            print(f"  Palette BG {p} : {', '.join('#%02x%02x%02x' % c for c in cols)}"
                  f"   (ici la couleur 0 est opaque)")
        print(f"  Les zones laissees transparentes dans ce cadre ne t'appartiennent")
        print(f"  pas : n'y dessine rien, elles ne seront pas relues.")
    print(f"\n  Quand c'est fini :")
    print(f"    python3 tools/sprite_edit.py import {field.lower()} {key}\n")


def cmd_import(field, half, key, dry, set_palette=False):
    tag = f"{field.lower()}_{half.lower()}_{key}"
    jpath = os.path.join(WORK, tag + '.json')
    if not os.path.exists(jpath):
        die(f"_work/{tag}.json absent — lance d'abord la commande export")
    meta = json.load(open(jpath))
    frames, owner, objpal, incbin, owner_bg, bgpal = resolve(field, half, meta['names'])

    im = Image.open(os.path.join(WORK, tag + '.png')).convert('RGBA')
    W, H = meta['w'], meta['h']
    if im.size != (W, H):
        if im.width % W or im.height % H or im.width // W != im.height // H:
            die(f"taille inattendue {im.width}x{im.height} : il faut {W}x{H} "
                f"(ou un multiple entier exact)")
        k = im.width // W
        print(f"  image en x{k}, reduction automatique")
        small = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for y in range(H):
            for x in range(W):
                block = [im.getpixel((x * k + i, y * k + j))
                         for j in range(k) for i in range(k)]
                block = [p for p in block if p[3] >= 128] or [(0, 0, 0, 0)]
                small.putpixel((x, y), max(set(block), key=block.count))
        im = small
    px = im.load()

    if set_palette:
        # On fabrique la palette A PARTIR du dessin, au lieu d'y ramener le
        # dessin de force. C'est ce qui evite que deux verts proches partent
        # l'un sur l'or et l'autre sur le gris.
        _, pal_label = parse_video_block(field, half)[1:]
        prefix = pal_label[:-len('Palettes')]
        by_pal = {}
        for e in meta['entries']:
            d = by_pal.setdefault(e['pal'], {})
            for y in range(16):
                for x in range(8):
                    q = px[e['x'] + x, e['y'] + y]
                    if q[3] >= 128:
                        d[q[:3]] = d.get(q[:3], 0) + 1
        for pnum, colors in sorted(by_pal.items()):
            cols = derive_palette(colors)
            got = write_obj_palette(prefix, pnum, cols)
            if got is None:
                print(f"  palette OBJ {pnum} : bloc introuvable, ignoree")
                continue
            objpal[pnum] = [tuple(v * 255 // 31 for v in c) for c in got]
            print(f"  palette OBJ {pnum} deduite de ton dessin "
                  f"({len(colors)} teinte(s) -> 3) :")
            for i, c in enumerate(got[1:], 1):
                print(f"      couleur {i} : RGB {c[0]}, {c[1]}, {c[2]}")

    def snap(p, pal, opaque=False):
        if not opaque and p[3] < 128:
            return 0
        best, bd = (0, None) if opaque else (1, None)
        for i in ((0, 1, 2, 3) if opaque else (1, 2, 3)):
            c = pal[i]
            d = (c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2 + (c[2] - p[2]) ** 2
            if bd is None or d < bd:
                best, bd = i, d
        return best

    # tuile lue -> contenu, avec detection de conflit
    new_tiles = {}          # (bank, tile) -> matrice 8x8
    conflicts = []
    for e in meta['entries']:
        pal = objpal.get(e['pal'], CANON_GRAYS)
        for k in (0, 1):
            t = (e['tile'] & 0xFE) + k
            td = [[snap(px[e['x'] + x, e['y'] + y + k * 8], pal) for x in range(8)]
                  for y in range(8)]
            if e['attr'] & 0x40:
                td = td[::-1]
            if e['attr'] & 0x20:
                td = [row[::-1] for row in td]
            keyt = (e['bank'], t)
            if keyt in new_tiles and new_tiles[keyt] != td:
                conflicts.append((e['frame'], f"${t:02x}"))
            new_tiles[keyt] = td

    bg_tiles = {}           # (bank, fenetre) -> matrice 8x8
    for cells in (meta.get('bg') or {}).get('variants', []):
      for cell in cells:
        pal = bgpal.get(cell['pal'], CANON_GRAYS)
        td = [[snap(px[cell['x'] + x, cell['y'] + y], pal, opaque=True)
               for x in range(8)] for y in range(8)]
        if cell['attr'] & 0x40:
            td = td[::-1]
        if cell['attr'] & 0x20:
            td = [row[::-1] for row in td]
        keyb = (cell['bank'], cell['win'])
        if keyb in bg_tiles and bg_tiles[keyb] != td:
            conflicts.append(('fond', f"tuile partagee, fenetre {cell['win']}"))
        bg_tiles[keyb] = td

    if conflicts:
        print("\n  ATTENTION : une meme tuile recoit deux dessins differents")
        for f, t in sorted(set(conflicts)):
            print(f"    {f} tuile {t}")
        print("  -> c'est normal si deux frames partagent une tuile ;")
        print("     le dernier dessin l'emporte.\n")

    # regroupe par fichier source
    per_file = {}
    for (bank, t), td in new_tiles.items():
        src = tile_source(owner, incbin, bank, t)
        if not src or not src[0]:
            die(f"tuile ${t:02x} banque {bank} : pas de fichier source")
        per_file.setdefault(src[0], {})[src[1]] = td
    for (bank, w), td in bg_tiles.items():
        src = tile_source(owner_bg, incbin, bank, w)
        if not src or not src[0]:
            die(f"fenetre BG {w} banque {bank} : pas de fichier source")
        per_file.setdefault(src[0], {})[src[1]] = td

    total = 0
    bad = False
    for path, changes in sorted(per_file.items()):
        tiles, colors, grid = png_tiles(path)
        n = 0
        for idx, td in changes.items():
            if tiles[idx] != td:
                tiles[idx] = td
                n += 1
        total += n
        state = "inchange" if n == 0 else f"{n} tuile(s) modifiee(s)"
        print(f"  {path:<52} {state}")
        if n and not dry:
            write_png_tiles(path, tiles, colors, grid)
            err = verify_with_rgbgfx(path, tiles)
            if err:
                print(f"    /!\\ {err}")
                bad = True
            else:
                print("    verifie : rgbgfx relit exactement les memes tuiles")

    if dry:
        print(f"\n  --dry-run : rien n'a ete ecrit ({total} tuile(s) auraient change)\n")
    else:
        if bad:
            print("\n  Des couleurs risquent de sortir fausses en jeu — "
                  "verifie que ton dessin utilise bien les 3 teintes.\n")
        else:
            print(f"\n  {total} tuile(s) ecrite(s). Reconstruis la ROM avec  make\n")


def creature_origin(field, key):
    """Position ecran de l'objet, lue dans sa fonction Draw* (b-8, c-16)."""
    path = os.path.join(
        ROOT, f'engine/pinball_game/draw_sprites/draw_{field.lower()}_field_sprites.asm')
    txt = open(path).read()
    pat = (r'^Draw' + re.escape(key) + r'[A-Za-z0-9_]*:.*?\n\tld a, \$([0-9a-fA-F]{1,2})'
           r'\n\tld hl, hSCX.*?\n\tld a, \$([0-9a-fA-F]{1,2})\n\tld hl, hSCY')
    m = re.search(pat, txt, re.S | re.M | re.I)
    if not m:
        return None
    return int(m.group(1), 16) - 8, int(m.group(2), 16) - 16


def frame_image(frames, name, owner, objpal, incbin):
    """(image RGBA de la frame, dx mini, dy mini)."""
    ent = frames[name]
    minx = min(e[1] for e in ent)
    miny = min(e[0] for e in ent)
    w = max(e[1] for e in ent) - minx + 8
    h = max(e[0] for e in ent) - miny + 16
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for dy, dx, tile, attr in reversed(ent):
        pal = objpal.get(attr & 7, CANON_GRAYS)
        for k in (0, 1):
            src = tile_source(owner, incbin, (attr >> 3) & 1, (tile & 0xFE) + k)
            if not src or not src[0]:
                continue
            tiles, cols, grid = png_tiles(src[0])
            td = tiles[src[1]]
            if attr & 0x20:
                td = [r[::-1] for r in td]
            if attr & 0x40:
                td = td[::-1]
            for y in range(8):
                for x in range(8):
                    v = td[y][x]
                    if v:
                        im.putpixel((dx - minx + x, dy - miny + y + k * 8),
                                    pal[v] + (255,))
    return im, minx, miny


def derive_palette(colors_weighted):
    """Rend 3 couleurs 5 bits representant au mieux les couleurs fournies."""
    import itertools
    hist = [(n, c) for c, n in colors_weighted.items()]
    q = lambda c: tuple(min(31, round(v * 31 / 255)) * 255 // 31 for v in c)
    if len(hist) <= 3:
        out = [q(c) for _, c in hist]
        while len(out) < 3:                     # complete avec du noir
            for cand in ((0, 0, 0), (255, 255, 255), (128, 128, 128)):
                if cand not in out:
                    out.append(cand)
                    break
        return sorted(out, key=lambda c: -sum(c))
    cost = lambda pal: sum(n * min(sum((c[k] - p[k]) ** 2 for k in range(3))
                                   for p in pal) for n, c in hist)
    best = None
    for combo in itertools.combinations([c for _, c in hist], 3):
        pal = list(combo)
        for _ in range(40):                     # k-means pondere
            groups = {i: [] for i in range(3)}
            for n, c in hist:
                i = min(range(3), key=lambda i: sum((pal[i][k] - c[k]) ** 2
                                                    for k in range(3)))
                groups[i].append((n, c))
            new = []
            for i in range(3):
                g = groups[i] or [(1, pal[i])]
                tot = sum(n for n, _ in g)
                new.append(tuple(sum(n * c[k] for n, c in g) // tot for k in range(3)))
            if new == pal:
                break
            pal = new
        pal = [q(c) for c in pal]
        sc = cost(pal)
        if best is None or sc < best[0]:
            best = (sc, pal)
    return sorted(best[1], key=lambda c: -sum(c))


def write_obj_palette(prefix, n, cols):
    """Reecrit Stage<X>Field<Half>OBJPalette<n>, entree 0 laissee telle quelle."""
    label = f"{prefix}OBJPalette{n}"
    txt = open(PAL_ASM).read()
    m = re.search(rf'^({re.escape(label)}:[^\n]*\n)((?:\tRGB[^\n]*\n){{4}})',
                  txt, re.M)
    if not m:
        return None
    lines = m.group(2).rstrip('\n').split('\n')
    body = [lines[0]]                            # entree 0 = transparent
    for c in cols:
        body.append(f"\tRGB {c[0] * 31 // 255}, {c[1] * 31 // 255}, {c[2] * 31 // 255}")
    new = m.group(1) + '\n'.join(body) + '\n'
    open(PAL_ASM, 'w').write(txt[:m.start()] + new + txt[m.end():])
    return [tuple(int(v) for v in re.findall(r'\d+', l)) for l in body]


def cmd_preview(field, half, key, scale):
    """Rend le plateau tel qu'il sera en jeu, un panneau par etat."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import render_field as RF
    except ImportError:
        die("tools/render_field.py est introuvable")
    frames, owner, objpal, incbin, owner_bg, bgpal = resolve(field, half, [])
    raw = field_creatures(field, raw=True).get(key)
    if not raw:
        die(f"pas d'etats connus pour '{key}' sur le plateau {field}")
    names = sorted(set(raw))
    bgr = bg_region(field, half, frames, names)
    # On applique l'etat COMPLET, pas seulement les cellules de la bestiole :
    # le rail eclair et le toit des Voltorbe changent aussi selon l'etat.
    vbs = variants_by_state(field, [(r, c) for r in range(18) for c in range(20)])
    origin = creature_origin(field, key)
    if origin is None:
        die(f"position ecran introuvable pour '{key}'")

    # Certains etats n'ont qu'une reecriture partielle (voire aucune) : on prend
    # alors la tilemap complete d'un etat qui affiche la meme frame.
    full = max((len(w) for w in vbs.values()), default=0)
    seen, panels = [], []
    for st, fname in enumerate(raw):
        v = vbs.get(st)
        if vbs and (v is None or len(v) < full):
            for st2, f2 in enumerate(raw):
                if f2 == fname and st2 in vbs and len(vbs[st2]) == full:
                    v = vbs[st2]
                    break
        sig = (fname, tuple(sorted((v or {}).items())))
        if sig in seen:
            continue
        seen.append(sig)
        panels.append((st, fname, v))

    block = f"Stage{field}Field{half}Gfx_GameBoyColor"
    imgs = []
    for st, fname, v in panels:
        bg = RF.render_block(block, v)[0].crop((0, 0, 160, 144)).convert('RGBA')
        fim, minx, miny = frame_image(frames, fname, owner, objpal, incbin)
        bg.alpha_composite(fim, (origin[0] + minx, origin[1] + miny))
        imgs.append((f"etat {st} — {fname}", bg.convert('RGB')))

    from PIL import ImageDraw
    W = sum(160 * scale + 20 for _ in imgs) + 20
    out = Image.new('RGB', (W, 144 * scale + 40), (28, 28, 32))
    d = ImageDraw.Draw(out)
    x = 20
    for lbl, im in imgs:
        out.paste(im.resize((160 * scale, 144 * scale), Image.NEAREST), (x, 32))
        d.text((x, 12), lbl, fill=(255, 255, 255))
        x += 160 * scale + 20
    os.makedirs(WORK, exist_ok=True)
    tag = f"{field.lower()}_{half.lower()}_{key}_preview"
    out.save(os.path.join(WORK, tag + '.png'))
    print(f"\n  _work/{tag}.png  —  {len(imgs)} etat(s) rendus comme en jeu")
    for lbl, _ in imgs:
        print(f"    {lbl}")
    print()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(0)
    cmd, field = sys.argv[1], sys.argv[2].capitalize()
    half = 'Top'
    args = sys.argv[3:]
    if '--bottom' in args:
        half = 'Bottom'
        args.remove('--bottom')
    dry = '--dry-run' in args
    if dry:
        args.remove('--dry-run')
    force = '--force' in args
    if force:
        args.remove('--force')
    palette = '--palette' in args
    if palette:
        args.remove('--palette')
    scale = 6
    for a in list(args):
        if a.startswith('--scale='):
            scale = int(a.split('=')[1])
            args.remove(a)

    if cmd == 'list':
        cmd_list(field, half)
        return
    if not args:
        die("il manque le nom de la creature (ex : ditto)")
    key = args[0]
    creatures = field_creatures(field)
    if key in creatures:
        names = creatures[key]
    elif key.endswith('OAM'):
        names = [key]                      # nom de frame OAM donne a la main
    else:
        die(f"le plateau {field} n'a pas de '{key}'. Il a : "
            f"{', '.join(sorted(creatures))}\n"
            f"          (chaque plateau a son propre casting — "
            f"'list' te donne le sien)")
    if cmd == 'preview':
        cmd_preview(field, half, key, max(1, scale // 2))
    elif cmd == 'export':
        cmd_export(field, half, key, names, scale, force)
    elif cmd == 'import':
        cmd_import(field, half, key, dry, palette)
    else:
        die(f"commande inconnue : {cmd}")


if __name__ == '__main__':
    main()

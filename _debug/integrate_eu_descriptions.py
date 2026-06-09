#!/usr/bin/env python3
"""Replace the Gen-1 Pokédex descriptions in text/pokedex_descriptions_*.asm
with the official EU French text decoded from the user's EU ROM.
Text flows ROM -> project files (both the user's own assets)."""
import re, sys
sys.path.insert(0, '_debug')
from extract_eu_descriptions import decode, sentence_case, BASE

ROM = "PokemonPinballEurope.gbc"
FILES = [f"text/pokedex_descriptions_{i}.asm" for i in (1, 2, 3)]

# National dex #1..151 -> Generations description label (English spelling)
GEN1 = ("Bulbasaur Ivysaur Venusaur Charmander Charmeleon Charizard Squirtle "
 "Wartortle Blastoise Caterpie Metapod Butterfree Weedle Kakuna Beedrill Pidgey "
 "Pidgeotto Pidgeot Rattata Raticate Spearow Fearow Ekans Arbok Pikachu Raichu "
 "Sandshrew Sandslash NidoranF Nidorina Nidoqueen NidoranM Nidorino Nidoking "
 "Clefairy Clefable Vulpix Ninetales Jigglypuff Wigglytuff Zubat Golbat Oddish "
 "Gloom Vileplume Paras Parasect Venonat Venomoth Diglett Dugtrio Meowth Persian "
 "Psyduck Golduck Mankey Primeape Growlithe Arcanine Poliwag Poliwhirl Poliwrath "
 "Abra Kadabra Alakazam Machop Machoke Machamp Bellsprout Weepinbell Victreebell "
 "Tentacool Tentacruel Geodude Graveler Golem Ponyta Rapidash Slowpoke Slowbro "
 "Magnemite Magneton Farfetchd Doduo Dodrio Seel Dewgong Grimer Muk Shellder "
 "Cloyster Gastly Haunter Gengar Onix Drowzee Hypno Krabby Kingler Voltorb "
 "Electrode Exeggcute Exeggutor Cubone Marowak Hitmonlee Hitmonchan Lickitung "
 "Koffing Weezing Rhyhorn Rhydon Chansey Tangela Kangaskhan Horsea Seadra Goldeen "
 "Seaking Staryu Starmie MrMime Scyther Jynx Electabuzz Magmar Pinsir Tauros "
 "Magikarp Gyarados Lapras Ditto Eevee Vaporeon Jolteon Flareon Porygon Omanyte "
 "Omastar Kabuto Kabutops Aerodactyl Snorlax Articuno Zapdos Moltres Dratini "
 "Dragonair Dragonite Mewtwo Mew").split()
assert len(GEN1) == 151

# --- pixel widths: replicate Func_2957c char->glyph index, then CharacterWidths ---
def load_widths():
    L = open("data/vwf_character_widths.asm").read().split('\n')
    i = next(k for k, l in enumerate(L) if l.startswith('CharacterWidths:'))
    vals = []
    for l in L[i+1:]:
        m = re.match(r'\s*db \$([0-9a-fA-F]{2})', l)
        if m: vals.append(int(m.group(1), 16))
        if len(vals) == 256: break
    return vals
CW = load_widths()

ACC_GLYPH = {'è':0xfb,'ê':0xfc,'à':0xfd,'â':0xfe,'î':0xe7,'û':0xe8,'É':0xe9,
             'ô':0xa4,'ç':0xa5,'ï':0xa6,'ù':0xa7,'é':0xf9}
def glyph(ch):
    o = ord(ch)
    if ch == ' ': return 0
    if 0x30 <= o <= 0x39: return (o - 0x88) & 0xff
    if 0x41 <= o <= 0x5a: return (o - 0x8e) & 0xff
    if 0x61 <= o <= 0x7a: return (o - 0x94) & 0xff
    if ch == ',': return 0xf3
    if ch == '.': return 0xf4
    if ch == "'": return 0xfa
    if ch == '-': return 0xb2
    return ACC_GLYPH.get(ch)
def pxwidth(s):
    w = 0
    for ch in s:
        g = glyph(ch)
        w += CW[g] if g is not None else 6
    return w

# budget = widest existing dex line (so we never exceed the display)
def existing_budget():
    mx = 0
    for fn in FILES:
        for m in re.finditer(r'dex_(?:text|line) "([^"]*)"', open(fn).read()):
            mx = max(mx, pxwidth(m.group(1)))
    return mx
BUDGET = existing_budget()

def wrap(text):
    lines, cur = [], ""
    for word in text.split():
        cand = (cur + " " + word).strip()
        if pxwidth(cand) <= BUDGET:
            cur = cand
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines

def asm_block(label_line, lines):
    out = [label_line]
    out.append(f'\tdex_text "{lines[0]}"')
    for ln in lines[1:]:
        out.append(f'\tdex_line "{ln}"')
    out.append('\tdex_end')
    return '\n'.join(out)

def sc_lines(raw):
    """Sentence-case while PRESERVING the EU line breaks ($ff -> '\\n'),
    so the in-game wrapping matches the EU version exactly."""
    out, cap = [], True
    for ch in raw:
        if ch == '\n':
            out.append('\n'); continue
        c = ch.lower()
        if cap and c.isalpha():
            c = c.upper(); cap = False
        out.append(c)
        if ch == '.':
            cap = True
    return [ln.strip() for ln in ''.join(out).split('\n') if ln.strip()]


def main():
    d = open(ROM, 'rb').read()
    # decode EU national# -> list of sentence-cased lines (EU breaks preserved)
    eu = {}
    for idx in range(151):
        a = d[BASE+idx*2] | (d[BASE+idx*2+1] << 8)
        eu[idx+1] = sc_lines(decode(d, BASE+(a-0x4000)))
    # verify all labels present
    contents = {fn: open(fn).read() for fn in FILES}
    label_to_file = {}
    for fn, c in contents.items():
        for m in re.finditer(r'^(\w+)PokedexDescription:', c, re.M):
            label_to_file[m.group(1)] = fn
    missing = [GEN1[i] for i in range(151) if GEN1[i] not in label_to_file]
    if missing:
        print("LABELS INTROUVABLES:", missing); return 1
    # replace each block
    nrepl = 0
    for natnum in range(1, 152):
        label = GEN1[natnum-1]
        fn = label_to_file[label]
        c = contents[fn]
        lines = eu[natnum]
        pat = re.compile(r'^(' + label + r'PokedexDescription:[^\n]*)\n.*?\tdex_end',
                         re.M | re.S)
        new = asm_block(r'\1', lines)
        c2, n = pat.subn(new, c, count=1)
        if n != 1:
            print(f"ÉCHEC remplacement {label}"); return 1
        contents[fn] = c2; nrepl += 1
    for fn, c in contents.items():
        open(fn, 'w').write(c)
    print(f"budget largeur = {BUDGET}px | {nrepl} descriptions remplacées")

if __name__ == "__main__":
    sys.exit(main() or 0)

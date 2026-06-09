#!/usr/bin/env python3
"""Extract the official French Gen-1 Pokédex descriptions from the user's
Pokémon Pinball (Europe) ROM. Output is derived entirely from the ROM file.

EU description encoding (bank $7a):
  - pointer table at $1e8000: 151 entries, 2-byte LE bank-relative addresses
  - letters A-Z / a-z = ASCII
  - decorative drop-cap initial = uppercase ASCII - $20  (byte $21-$3a)
  - $fe = space   $ff = line break   $00 = end-of-entry
  - $0e = '.'  $0c = ','  $0d = '-'  $07 = apostrophe  $1a = ';'
  - $10-$19 = digits '0'-'9'
  - accents (uppercase): $ae=À $b0=Â $b5=Ç $b6=È $b7=É $b8=Ê
                         $bc=Î $bd=Ï $c2=Ô $c7=Ù $c9=Û
"""
import re, sys

ROM = "PokemonPinballEurope.gbc"
BANK = 0x7a
BASE = BANK * 0x4000          # 0x1e8000
NUM = 151

SP = {0xfe: ' ', 0xff: '\n', 0x07: "'", 0x0e: '.', 0x0c: ',', 0x0d: '-', 0x1a: ',',
      0xae: 'À', 0xb0: 'Â', 0xb5: 'Ç', 0xb6: 'È', 0xb7: 'É', 0xb8: 'Ê',
      0xbc: 'Î', 0xbd: 'Ï', 0xc2: 'Ô', 0xc7: 'Ù', 0xc9: 'Û'}
for k in range(0x10, 0x1a):
    SP[k] = chr(ord('0') + k - 0x10)


def decode(d, off):
    out = []
    i = off
    while True:
        b = d[i]; i += 1
        if b == 0x00:
            break
        if 0x41 <= b <= 0x5a or 0x61 <= b <= 0x7a:
            out.append(chr(b))                 # A-Z / a-z (ASCII)
        elif 0x21 <= b <= 0x3a:
            out.append(chr(b + 0x20))          # decorative drop-cap -> A-Z
        elif b in SP:
            out.append(SP[b])
        else:
            out.append(f'[{b:02x}]')           # should not happen
    return ''.join(out)


def sentence_case(t):
    """EU stores ALL CAPS; convert to French sentence case to match the
    Generations mixed-case display."""
    t = re.sub(r'\s+', ' ', t.replace('\n', ' ')).strip().lower()
    out, cap = [], True
    for ch in t:
        if cap and ch.isalpha():
            ch = ch.upper(); cap = False
        out.append(ch)
        if ch in '.':
            cap = True
    return ''.join(out)


def main():
    d = open(ROM, 'rb').read()
    raw_lines, sc_lines = [], []
    for idx in range(NUM):
        a = d[BASE + idx * 2] | (d[BASE + idx * 2 + 1] << 8)
        off = BASE + (a - 0x4000)
        raw = decode(d, off)
        natdex = idx + 1
        raw_lines.append(f"#{natdex:03d}\n{raw}\n")
        sc_lines.append(f"#{natdex:03d}: {sentence_case(raw)}")
    open("_debug/eu_fr_descriptions_raw.txt", "w").write("\n".join(raw_lines))
    open("_debug/eu_fr_descriptions_sentencecase.txt", "w").write("\n".join(sc_lines))
    unknown = sum(t.count('[') for t in sc_lines)
    print(f"Décodé {NUM} descriptions FR. Octets inconnus restants: {unknown}")
    print("Fichiers: _debug/eu_fr_descriptions_raw.txt (+ _sentencecase.txt)")


if __name__ == "__main__":
    main()

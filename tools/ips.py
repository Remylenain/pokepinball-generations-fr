#!/usr/bin/env python3
"""Creation et application de patches IPS.

    python ips.py create base.gbc cible.gbc sortie.ips
    python ips.py apply  base.gbc patch.ips sortie.gbc
    python ips.py info   patch.ips
    python ips.py verify base.gbc patch.ips attendu.gbc

Format IPS : "PATCH", puis des enregistrements
  offset (3 octets BE) + taille (2 octets BE) + donnees
  ou, si taille == 0 : offset + 0000 + taille_rle (2 octets BE) + octet repete
puis "EOF", et eventuellement 3 octets de troncature.
"""
import sys

EOF_OFFSET = 0x454F46  # "EOF" : un enregistrement ne peut pas commencer la
MAX_CHUNK = 0xFFFF
MIN_RLE = 9  # en dessous, le RLE ne fait pas gagner de place


def read(path):
    with open(path, "rb") as f:
        return f.read()


def diff_ranges(base, target):
    """Plages a ecrire dans le patch, fusionnees si separees par < 6 octets
    identiques (6 = cout d'un nouvel en-tete d'enregistrement).

    Au-dela de la taille de la base, TOUT est ecrit, y compris les octets nuls :
    les patchers etendent le fichier au fur et a mesure des ecritures, donc un
    octet nul omis en fin de fichier donnerait une ROM tronquee. Les longues
    plages de zeros partent en RLE, le cout reste negligeable."""
    common = min(len(base), len(target))
    ranges = []
    i = 0
    while i < common:
        if base[i] != target[i]:
            start = i
            gap = 0
            i += 1
            while i < common and gap < 6:
                if base[i] != target[i]:
                    gap = 0
                else:
                    gap += 1
                i += 1
            ranges.append((start, i - gap))
        else:
            i += 1
    if len(target) > common:
        if ranges and ranges[-1][1] >= common - 6:
            ranges[-1] = (ranges[-1][0], len(target))
        else:
            ranges.append((common, len(target)))
    return ranges


def create(base_path, target_path, out_path):
    base, target = read(base_path), read(target_path)
    if len(target) < len(base):
        sys.exit("cible plus courte que la base : troncature non geree")
    out = bytearray(b"PATCH")
    records = 0
    for start, end in diff_ranges(base, target):
        pos = start
        while pos < end:
            chunk_end = min(pos + MAX_CHUNK, end)
            data = target[pos:chunk_end]
            # RLE si un seul octet se repete assez longtemps
            run = 1
            while run < len(data) and data[run] == data[0]:
                run += 1
            if run >= MIN_RLE:
                out += pos.to_bytes(3, "big") + b"\x00\x00"
                out += run.to_bytes(2, "big") + data[:1]
                pos += run
            else:
                out += pos.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
                pos = chunk_end
            records += 1
            if pos == EOF_OFFSET:  # un offset "EOF" casserait le patch
                sys.exit("offset 0x454F46 atteint : cas non gere")
    out += b"EOF"
    with open(out_path, "wb") as f:
        f.write(out)
    print(f"{out_path} : {len(out)} octets, {records} enregistrements")


def apply(base_path, patch_path, out_path):
    rom = bytearray(read(base_path))
    p = read(patch_path)
    if p[:5] != b"PATCH":
        sys.exit("ce n'est pas un fichier IPS")
    i, applied = 5, 0
    while True:
        if p[i:i + 3] == b"EOF":
            break
        offset = int.from_bytes(p[i:i + 3], "big")
        size = int.from_bytes(p[i + 3:i + 5], "big")
        i += 5
        if size == 0:  # RLE
            rle_size = int.from_bytes(p[i:i + 2], "big")
            data = p[i + 2:i + 3] * rle_size
            i += 3
        else:
            data = p[i:i + size]
            i += size
        if offset + len(data) > len(rom):
            rom += bytes(offset + len(data) - len(rom))
        rom[offset:offset + len(data)] = data
        applied += 1
    with open(out_path, "wb") as f:
        f.write(rom)
    print(f"{out_path} : {len(rom)} octets, {applied} enregistrements appliques")


def verify(base_path, patch_path, expected_path):
    """Applique le patch en memoire et compare octet par octet au resultat attendu."""
    import hashlib
    rom = bytearray(read(base_path))
    p = read(patch_path)
    if p[:5] != b"PATCH":
        sys.exit("ce n'est pas un fichier IPS")
    i = 5
    while p[i:i + 3] != b"EOF":
        offset = int.from_bytes(p[i:i + 3], "big")
        size = int.from_bytes(p[i + 3:i + 5], "big")
        i += 5
        if size == 0:
            rle = int.from_bytes(p[i:i + 2], "big")
            data = p[i + 2:i + 3] * rle
            i += 3
        else:
            data = p[i:i + size]
            i += size
        if offset + len(data) > len(rom):
            rom += bytes(offset + len(data) - len(rom))
        rom[offset:offset + len(data)] = data
    expected = read(expected_path)
    if bytes(rom) != expected:
        bad = next(k for k in range(min(len(rom), len(expected)))
                   if rom[k] != expected[k]) if len(rom) == len(expected) else None
        sys.exit(f"ECHEC : le patch ne reproduit pas {expected_path}"
                 + (f" (1er ecart a 0x{bad:06X})" if bad is not None else
                    f" (tailles {len(rom)} vs {len(expected)})"))
    print(f"OK : base + patch == {expected_path} "
          f"({len(expected)} octets, sha1 {hashlib.sha1(expected).hexdigest()})")


def info(patch_path):
    p = read(patch_path)
    if p[:5] != b"PATCH":
        sys.exit("ce n'est pas un fichier IPS")
    i, n, lo, hi, total = 5, 0, None, 0, 0
    while p[i:i + 3] != b"EOF":
        offset = int.from_bytes(p[i:i + 3], "big")
        size = int.from_bytes(p[i + 3:i + 5], "big")
        i += 5
        length = size
        if size == 0:
            length = int.from_bytes(p[i:i + 2], "big")
            i += 3
        else:
            i += size
        lo = offset if lo is None else min(lo, offset)
        hi = max(hi, offset + length)
        total += length
        n += 1
    print(f"{n} enregistrements, octets ecrits {total}, "
          f"plage 0x{lo:06X}-0x{hi:06X} (taille ROM finale >= {hi})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "create" and len(sys.argv) == 5:
        create(*sys.argv[2:5])
    elif cmd == "apply" and len(sys.argv) == 5:
        apply(*sys.argv[2:5])
    elif cmd == "info" and len(sys.argv) == 3:
        info(sys.argv[2])
    elif cmd == "verify" and len(sys.argv) == 5:
        verify(*sys.argv[2:5])
    else:
        sys.exit(__doc__)

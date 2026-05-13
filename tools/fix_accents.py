#!/usr/bin/env python3
"""Apply targeted accent restorations to FR text source files.

Only SAFE whole-word replacements (low ambiguity in context).  Run twice
is idempotent.  Inspect the diff after running; nothing here uses sentence
context, so some edge cases may need manual correction.
"""
from __future__ import annotations
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Canonical FR Pokemon names: only entries where canonical FR has an accent.
# Lowercase 'é' inside all-caps follows the existing 'POKéMON' convention,
# since the font ships only that one accent glyph.
POKEDEX_MON_NAMES = {
    # Gen 1
    '"SALAMECHE @"' : '"SALAMèCHE @"',
    '"MELOFEE   @"' : '"MéLOFéE   @"',
    '"MELODELFE @"' : '"MéLODELFE @"',
    '"AEROMITE  @"' : '"AéROMITE  @"',
    '"FEROSINGE @"' : '"FéROSINGE @"',
    '"CHETIFLOR @"' : '"CHéTIFLOR @"',
    '"METAMORPH @"' : '"MéTAMORPH @"',
    '"EVOLI     @"' : '"éVOLI     @"',
    '"PTERA     @"' : '"PTéRA     @"',
    '"ELECTHOR  @"' : '"éLECTHOR  @"',
    # Gen 2
    '"HERICENDRE@"' : '"HéRICENDRE@"',
    '"DEMANTA   @"' : '"DéMANTA   @"',
    '"DEMOLOSSE @"' : '"DéMOLOSSE @"',
    '"DEBUGANT  @"' : '"DéBUGANT  @"',
    '"ECREMEUH  @"' : '"éCRéMEUH  @"',
    '"CELEBI    @"' : '"CéLéBI    @"',
    # Gen 3
    '"LINEON    @"' : '"LINéON    @"',
    '"HELEDELLE @"' : '"HéLéDELLE @"',
    '"TENEFIX   @"' : '"TéNéFIX   @"',
    '"MORPHEO   @"' : '"MORPHéO   @"',
    '"TERACLOPE @"' : '"TéRACLOPE @"',
    '"DEOXYS    @"' : '"DéOXYS    @"',
}

# Pokedex species names — only safe whole-word substitutions.
# Lowercase 'é' is used inside all-caps to follow the 'POKéMON' convention.
DEX_SPECIES_FIXES = {
    'dex_species "LEZARD"'      : 'dex_species "LéZARD"',
    'dex_species "TRES PIQUANT"': 'dex_species "TRèS PIQUANT"',
    'dex_species "FEROCE"'      : 'dex_species "FéROCE"',
    'dex_species "ENERGIE"'     : 'dex_species "éNERGIE"',
    'dex_species "ETOILE"'      : 'dex_species "éTOILE"',
    'dex_species "GENIE"'       : 'dex_species "GéNIE"',
    'dex_species "EPINE"'       : 'dex_species "éPINE"',
    'dex_species "EPEE"'        : 'dex_species "éPéE"',
    'dex_species "ELECTRIQUE"'  : 'dex_species "éLECTRIQUE"',
    'dex_species "MEDUSE"'      : 'dex_species "MéDUSE"',
    'dex_species "DEFENSE"'     : 'dex_species "DéFENSE"',
    'dex_species "EVOLUTION"'   : 'dex_species "éVOLUTION"',
    'dex_species "LUMIERE"'     : 'dex_species "LUMIèRE"',
    'dex_species "MYSTERIEUX"'  : 'dex_species "MYSTéRIEUX"',
    'dex_species "OBSCURITE"'   : 'dex_species "OBSCURITé"',
    'dex_species "SCARABEE"'    : 'dex_species "SCARABéE"',
    'dex_species "TETARD"'      : 'dex_species "TéTARD"',
    'dex_species "VENEPIC"'     : 'dex_species "VéNéPIC"',
    'dex_species "HUMANOIDE"'   : 'dex_species "HUMANOïDE"',
    'dex_species "CRETIN"'      : 'dex_species "CRéTIN"',
    'dex_species "DEGUEU"'      : 'dex_species "DéGUEU"',
    'dex_species "FEE"'         : 'dex_species "FéE"',
}

# Description-level fixes.  Applied only inside string-literal contents of
# db / dex_text / dex_line lines.  Each entry is (regex, replacement).
#
# Only patterns that are virtually unambiguous in context are kept.  In
# particular, NO "a" → "à" replacement except in fixed expressions: the
# verb "avoir" (il a, elle a, on a) is too common in Pokedex descriptions
# to risk grammatical corruption.  Same for "protege" which can be either
# verb "protège" or past participle "protégé".
DESCRIPTION_FIXES: list[tuple[str, str]] = [
    # --- Unambiguous whole-word accent restorations -----------------------
    (r"\bjusqu'a\b",      "jusqu'à"),
    (r"\bDeja\b",         "Déjà"),
    (r"\bdeja\b",         "déjà"),
    (r"\bTres\b",         "Très"),
    (r"\btres\b",         "très"),
    (r"\betre\b",         "être"),
    (r"\bEtre\b",         "Être"),
    (r"\bmeme\b",         "même"),
    (r"\bMeme\b",         "Même"),
    (r"\bmemes\b",        "mêmes"),
    (r"\bMemes\b",        "Mêmes"),
    (r"\bete\b",          "été"),
    (r"\bEte\b",          "Été"),
    (r"\bcreer\b",        "créer"),
    (r"\bcreature\b",     "créature"),
    (r"\bCreature\b",     "Créature"),
    (r"\bcreatures\b",    "créatures"),
    (r"\bdifferent\b",    "différent"),
    (r"\bdifferents\b",   "différents"),
    (r"\bdifferente\b",   "différente"),
    (r"\bdifferentes\b",  "différentes"),
    (r"\bespece\b",       "espèce"),
    (r"\bespeces\b",      "espèces"),
    (r"\bsiecle\b",       "siècle"),
    (r"\bsiecles\b",      "siècles"),
    (r"\bmatiere\b",      "matière"),
    (r"\bmatieres\b",     "matières"),
    (r"\benergie\b",      "énergie"),
    (r"\bEnergie\b",      "Énergie"),
    (r"\binteret\b",      "intérêt"),
    (r"\btete\b",         "tête"),
    (r"\bTete\b",         "Tête"),
    (r"\btetes\b",        "têtes"),
    (r"\bbete\b",         "bête"),
    (r"\bbetes\b",        "bêtes"),
    (r"\bmere\b",         "mère"),
    (r"\bMere\b",         "Mère"),
    (r"\bmeres\b",        "mères"),
    (r"\bpere\b",         "père"),
    (r"\bPere\b",         "Père"),
    (r"\bperes\b",        "pères"),
    (r"\bfrere\b",        "frère"),
    (r"\bfreres\b",       "frères"),
    (r"\bboite\b",        "boîte"),
    (r"\bboites\b",       "boîtes"),
    (r"\bfete\b",         "fête"),
    (r"\bFete\b",         "Fête"),
    (r"\bfetes\b",        "fêtes"),
    (r"\bforet\b",        "forêt"),
    (r"\bForet\b",        "Forêt"),
    (r"\bforets\b",       "forêts"),
    (r"\bnaitre\b",       "naître"),
    (r"\bconnaitre\b",    "connaître"),
    (r"\bapparait\b",     "apparaît"),
    (r"\bapparaitre\b",   "apparaître"),
    (r"\bdisparait\b",    "disparaît"),
    (r"\bIle\b",          "Île"),
    (r"\bpres\b",         "près"),
    (r"\bderriere\b",     "derrière"),
    (r"\bpremiere\b",     "première"),
    (r"\bPremiere\b",     "Première"),
    (r"\bpremieres\b",    "premières"),
    (r"\bderniere\b",     "dernière"),
    (r"\bDerniere\b",     "Dernière"),
    (r"\bdernieres\b",    "dernières"),
    (r"\bentiere\b",      "entière"),
    (r"\bentieres\b",     "entières"),
    (r"\bsysteme\b",      "système"),
    (r"\bsystemes\b",     "systèmes"),
    (r"\bextremement\b",  "extrêmement"),
    (r"\bextreme\b",      "extrême"),
    (r"\bextremes\b",     "extrêmes"),
    (r"\bcontrole\b",     "contrôle"),
    (r"\bcontroles\b",    "contrôles"),
    (r"\bcontroler\b",    "contrôler"),
    (r"\bage\b",          "âge"),
    (r"\bAge\b",          "Âge"),
    (r"\bages\b",         "âges"),
    (r"\bame\b",          "âme"),
    (r"\bames\b",         "âmes"),
    # --- Fixed adverbial / preposition expressions (always preposition) ---
    (r"\bla-bas\b",       "là-bas"),
    (r"\bla-haut\b",      "là-haut"),
    (r"\bd'ou\b",         "d'où"),
    (r"\bla ou\b",        "là où"),
    (r"\ba force\b",      "à force"),
    (r"\ba peine\b",      "à peine"),
    (r"\ba travers\b",    "à travers"),
    (r"\ba haute\b",      "à haute"),
    (r"\ba basse\b",      "à basse"),
    (r"\bpas a pas\b",    "pas à pas"),
    (r"\bface a face\b",  "face à face"),
    # Preposition "à" before a digit (e.g. "vit à 3000 mètres")
    (r"\ba (\d)",         r"à \1"),
    # Sentence-start "A la" / "A l'" is always preposition
    (r'((?:^|[.!?]\s|"\s*))A la\b', r"\1À la"),
    (r'((?:^|[.!?]\s|"\s*))A l\'',  r"\1À l'"),
]


def fix_with_dict(path: Path, mapping: dict[str, str]) -> bool:
    s = path.read_text()
    orig = s
    for old, new in mapping.items():
        s = s.replace(old, new)
    if s != orig:
        path.write_text(s)
        return True
    return False


def fix_dex_lines(path: Path) -> bool:
    s = path.read_text()
    orig = s
    pattern = re.compile(r'((?:db|dex_text|dex_line)\s+")([^"\n]*)(")', re.MULTILINE)

    def repl(m):
        body = m.group(2)
        for pat, rep in DESCRIPTION_FIXES:
            body = re.sub(pat, rep, body)
        return m.group(1) + body + m.group(3)

    s = pattern.sub(repl, s)
    if s != orig:
        path.write_text(s)
        return True
    return False


def main() -> None:
    pdx_names = REPO / "text" / "pokedex_mon_names.asm"
    if pdx_names.exists() and fix_with_dict(pdx_names, POKEDEX_MON_NAMES):
        print(f"updated {pdx_names.relative_to(REPO)}")

    pdx_species = REPO / "text" / "pokedex_species_names.asm"
    if pdx_species.exists() and fix_with_dict(pdx_species, DEX_SPECIES_FIXES):
        print(f"updated {pdx_species.relative_to(REPO)}")

    dex_files = [
        REPO / "text" / "pokedex_descriptions_1.asm",
        REPO / "text" / "pokedex_descriptions_2.asm",
        REPO / "text" / "pokedex_descriptions_3.asm",
        REPO / "text" / "scrolling_text.asm",
        REPO / "text" / "scrolling_text_map_names.asm",
    ]
    for p in dex_files:
        if p.exists() and fix_dex_lines(p):
            print(f"updated {p.relative_to(REPO)}")


if __name__ == "__main__":
    main()

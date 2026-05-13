# EU ROM reference

Assets extraits de la ROM officielle multilingue européenne
`Pokemon Pinball (Europe) (En,Fr,De,Es,It) (SGB Enhanced).gbc`
(renommée `PokemonPinballEurope.gbc` à la racine du repo).

Cette arborescence est **uniquement de la donnée de référence** : rien n'est
inclus dans la build. Le rôle est de fournir, pour chaque asset graphique de
`gfx/`, son équivalent dans l'ROM EU pour les ports multilingues.

## Structure

```
eu_reference/
├── README.md                       (ce fichier)
├── MANIFEST.tsv                    index de chaque asset gfx/ et son statut
│
├── banks/                          dumps par bank (128 PNG, 128×512 px chacun)
│   └── bank_00.png … bank_7f.png   utile pour repérer un asset visuellement
│
├── font/                           référence font multilingue
│   ├── eu_bank02_font.png          font complète extraite du bank 02
│   ├── eu_bank02_font_labeled.png  même chose avec tile-ID overlay
│   ├── eu_french_accent_tiles.png  tiles top-half pour les accents FR
│   ├── eu_french_accent_tiles.2bpp même chose en raw 2bpp
│   ├── eu_french_accent_complete.png accents stackés top+bottom
│   └── eu_pokedex_initial.png      layout Pokédex EU (≈ identique US, 2 tiles différents)
│
├── strings/                        texte extrait
│   ├── eu_fr_strings.txt           toutes les chaînes FR/DE/IT/ES UI
│   └── eu_pokemon_names.txt        noms officiels FR des Pokémon (Gen 1-2)
│
├── shared/                         assets identiques entre US et EU (614 fichiers)
│   └── <même chemin que gfx/>      copie PNG, utilisable telle quelle pour toute langue
│
├── candidates/                     assets dont les bytes diffèrent entre langues
│   └── <chemin gfx/>/<nom_asset>/
│       ├── bankXX_offsYYYY_hit.png  match direct du préfixe US dans l'EU ROM
│       └── bankXX_offsYYYY_par.png  extraction spéculative au même offset
│                                   dans un bank voisin (peut être une autre
│                                   langue ou de la donnée non-liée)
│
├── en/                             versions anglaises promues (à remplir manuellement)
└── fr/                             versions françaises promues (à remplir manuellement)
```

## MANIFEST.tsv

Index TSV de chaque asset de `gfx/` avec :

| colonne      | sens                                                              |
|--------------|-------------------------------------------------------------------|
| rel_path     | chemin relatif à `gfx/`                                           |
| width/height | dimensions du PNG source (= rendu attendu)                        |
| us_bytes     | taille du `.2bpp` US (octets)                                     |
| status       | `shared` (identique EU), `lang_specific(sig=N)` (différent), `missing` |
| eu_offsets   | offsets absolus dans `PokemonPinballEurope.gbc` (hex)             |
| notes        | `*` à côté d'un offset = bank-parallèle spéculatif                |

## Méthodologie d'extraction

Le script `tools/extract_eu_assets.py` parcourt chaque `.2bpp` (ou `.png` faute
de `.2bpp`) de `gfx/`, et pour chacun :

1. **Cherche un match exact des bytes US dans l'EU ROM**. Si trouvé →
   l'asset est `shared`, sauvegardé une fois dans `shared/<chemin>.png`.
2. **Sinon, signature search** sur les 64–256 premiers bytes. Chaque match
   donne un *candidate* dans `candidates/<chemin>/<asset>/bankXX_offsYYYY_hit.png`.
3. **Bank-parallel scan**. Pour chaque hit, on extrait aussi le même
   in-bank offset dans les banks voisins (±3). Les variantes par langue
   sont souvent stockées dans des banks adjacents (ex: BALL START en
   bank 0x46, BALL SPIELEN en bank 0x45). Marqués `_par`.
4. **Sinon** → `missing`. Soit l'asset est exclusif au hack
   (contenu Gen 3 : Hoenn, mons générations II/III absents de l'EU 1999),
   soit il est compressé/interleaved.

## Bilan de couverture

| Statut             | Nombre | Commentaire                                          |
|--------------------|-------:|------------------------------------------------------|
| shared             |    614 | Mêmes bytes dans US/hack et EU → utilisable direct  |
| language-specific  |     21 | Bytes différents, candidates extraites              |
| missing            |    487 | Gen 3 hack-only, ou compressé/interleaved          |

Les 487 *missing* sont attendus : pokepinball-generations ajoute énormément
de contenu Gen 3 (Hoenn, mons jamais vus dans l'EU originale). Pour ces
assets, l'EU ROM n'a tout simplement pas d'équivalent.

## Comment promouvoir un candidate vers `en/` ou `fr/`

Les `candidates/` contiennent toutes les versions trouvées sans étiquette de
langue (on n'a pas la table de labels de l'EU disasm). Inspection manuelle :

1. Ouvrir `candidates/<chemin>/<asset>/` et regarder chaque PNG.
2. Identifier la langue de chaque (ex : `BALL START` = EN, `BALL SPIELEN` = DE,
   `BALLE DEPART` = FR, etc).
3. Copier la version EN vers `en/<chemin>/<asset>.png` et FR vers
   `fr/<chemin>/<asset>.png`.

Pour la **variante reformatée aux dimensions US**, les `_hit` et `_par` sont
déjà rendus à la dimension du `.png` source de `gfx/`. C'est le format
canonique utilisable directement comme remplacement.

Pour la **variante native EU** (ex: `BALL SPIELEN` est en 24×24 dans
l'ROM EU, pas en 72×8), il faut re-extraire à la main avec un script court
en utilisant l'offset trouvé. Le bank 0x02 de l'ROM contient la font, et
les fichiers de référence dans `font/` aident à identifier les tile IDs.

## Liens utiles

- `font/eu_bank02_font_labeled.png` : pour identifier les tile IDs.
- Formule : pour une char ASCII de code `c`, son tile-ID dans la font EU
  est `c + 0x1E0`. Exemple : `'A'` (0x41) → tile `0x221`. Cela permet de
  chercher des séquences de tile-IDs dans le ROM pour localiser un texte
  donné toutes langues confondues.
- `strings/eu_fr_strings.txt` : toutes les chaînes FR/DE/IT/ES UI de la
  ROM EU (utile pour les dialogues, pas les graphiques).

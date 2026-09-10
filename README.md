# Pokémon Pinball Generations

Traduction en français de cette Rom Hack permettant l'ajout de tables et de Pokémon des générations >1.

This is a fan-made project based on the pokepinball disassembly.  It adds future-generation boards and Pokémon to the game, and it is featured on the [**Twitch Plays Pokemon**][tpp] stream.

To set up the repository, see [**INSTALL.md**](INSTALL.md).

Compiler la ROM :

```sh
make            # produit PinballGenerations.gbc
```

Les `.png` sont les sources : le `Makefile` régénère les `.2bpp` tout seul.


## Outils de plateau

Deux scripts pour travailler sur les tables sans manipuler les tuiles à la main.
Ils écrivent leurs sorties dans `_work/`, qui est ignoré par git. Ils ont besoin
de Python 3 et de Pillow (`pip install pillow`).

### `tools/sprite_edit.py` — éditer un Pokémon de plateau

Sort une créature sous forme d'une **seule planche PNG**, en vraies couleurs,
prête à redessiner dans n'importe quel éditeur d'images ; puis la redécoupe en
tuiles et la réécrit dans les bons fichiers sources.

```sh
python3 tools/sprite_edit.py list ruby              # le casting de cette table
python3 tools/sprite_edit.py export ruby voltorb    # -> _work/ruby_top_voltorb.png
#   ... tu redessines la planche ...
python3 tools/sprite_edit.py import ruby voltorb --palette
python3 tools/sprite_edit.py preview ruby voltorb   # contrôle sans émulateur
make
```

La planche contient :

* des **cadres roses** — les frames de sprite (OAM), avec la grille des tuiles 8×16 ;
* des **cadres verts** — la partie de la créature dessinée dans le *fond* et non
  en sprite, avec une boîte par état du plateau. Toutes les créatures n'en ont
  pas.

Options utiles :

| option | effet |
| --- | --- |
| `--palette` | à l'import, fabrique la palette **à partir du dessin** et l'écrit dans `data/stage_palettes.asm`, au lieu d'y ramener le dessin de force |
| `--dry-run` | à l'import, dit ce qu'il ferait sans rien écrire |
| `--force` | à l'export, écrase la planche en cours sans la sauvegarder |
| `--bottom` | travaille sur la moitié basse du plateau — aucune des six tables actuelles n'y a de créature, l'outil refuse alors proprement |
| `--scale=N` | facteur de zoom de l'aperçu (défaut 6) |

À savoir en dessinant :

* **3 couleurs opaques maximum par sprite**, plus le transparent. C'est une
  limite matérielle du Game Boy Color (une palette fait 4 entrées dont la 0 est
  toujours transparente), elle ne se contourne pas en agrandissant la palette.
* Le transparent laisse voir le fond : là où le plateau est blanc, ça fait une
  4ᵉ couleur gratuite.
* Inutile de dessiner en niveaux de gris. Une tuile ne stocke qu'un **index**
  de 0 à 3 ; c'est la palette qui décide des couleurs. Dessine dans les teintes
  que tu veux, puis `import --palette`.
* Dans les cadres verts, la couleur 0 est **opaque** : en fond il n'y a pas de
  transparence.
* Chaque table a son propre casting. Rouge/Or/Rubis ont `ditto`, `voltorb`,
  `staryu`, `bellsprout`, `spinner` ; Bleu/Argent/Saphir ont `cloyster`,
  `shellder`, `slowpoke`, `spinner`. Le code garde partout les noms d'origine de
  la table Rouge, seul le dessin change.

`export` ne détruit jamais un dessin en cours : s'il diffère de ce que le jeu
contient, il est mis de côté dans `_work/<nom>.sauvegardeN.png`.

### `tools/render_field.py` — rendre un plateau

Reconstruit un plateau exactement comme à l'écran, en lisant les blocs vidéo de
`data/stage_base_gfx.asm` (deux banques VRAM, carte d'attributs, palettes).

```sh
python3 tools/render_field.py
```

Écrit dans `_work/` :

* `<table>_full.png` — la table entière en couleurs, haut et bas assemblés, pour
  les six tables ;
* `<table>_<moitié>_edit.png` — la feuille 32×32 en 4 gris, pour une refonte du
  décor, et `<table>_<moitié>_side.json` — les métadonnées par cellule pour
  redécouper. Uniquement pour Rubis et Saphir (voir `EDIT_FIELDS` dans le script).

Il s'importe aussi comme module. `render_block(nom_du_bloc, tilemap_patch)`
accepte un dictionnaire `{offset depuis vBGMap: octet de tuile}` : c'est ce qui
permet de simuler un état de jeu, car la tilemap de certaines zones est réécrite
à l'exécution selon `wStageCollisionState`. Sans ce patch on ne voit que l'état
au chargement. `sprite_edit.py preview` s'en sert.


## See also

* Disassembly of [**Pokémon Pinball**][pokepinball]

[pokepinball]: https://github.com/pret/pokepinball
[tpp]: https://www.twitch.tv/twitchplayspokemon

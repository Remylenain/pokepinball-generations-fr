	charmap "@", $00
	charmap " ", $20
	charmap "!", $21
	charmap "♂", $24
	charmap "*", $2A
	charmap ",", $2C
	charmap "-", $2D
	charmap ".", $2E
	charmap "/", $2F
	charmap ":", $3A
	charmap "?", $3F
	charmap "é", $40
	charmap "♀", $5C
	charmap "`", $60

DEF chars EQUS "0123456789"
FOR x, STRLEN(#chars)
	charmap STRSLICE(#chars, x, x + 1), $30 + x
ENDR

REDEF chars EQUS "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FOR x, STRLEN(#chars)
	charmap STRSLICE(#chars, x, x + 1), $41 + x
ENDR

REDEF chars EQUS "abcdefghijklmnopqrstuvwxyz"
FOR x, STRLEN(#chars)
	charmap STRSLICE(#chars, x, x + 1), $61 + x
ENDR

; French accents: fall back to the closest unaccented base letter.
; The Pokedex/scrolling-text font only ships a glyph for é among the
; accents, so anything else is encoded as if the user had typed the
; base letter. Source files can use proper accented French, and the
; assembler folds them down here. CHARVAL("a") yields the value the base
; letter maps to above (RGBDS 1.0 replacement for the old `charmap "à", "a"`).
;
; Uppercase É chains to lowercase é so we still get the accented glyph
; in caps-only contexts (the dex name area is uppercase-only and a
; lowercase é is the closest thing to a real É we have).

	; Pokedex-description accents: these six have dedicated glyphs in the VWF
	; font (gfx/pokedex/characters.interleave.png) and are decoded by
	; Func_2957c (engine/pokedex.asm). They get unique low byte values that
	; ONLY the dex-description decoder recognises. They appear exclusively in
	; pokedex description text, so no other text engine ever sees these bytes.
	charmap "è", $01
	charmap "ê", $02
	charmap "à", $03
	charmap "î", $04
	charmap "û", $05
	charmap "â", $06
	charmap "É", $07
	charmap "ô", $08
	charmap "ç", $09
	charmap "ï", $0a
	charmap "ù", $0b

	; lowercase — fall back to base letter (no dedicated glyph anywhere)
	charmap "ä", CHARVAL("a")
	charmap "ë", CHARVAL("e")
	charmap "ö", CHARVAL("o")
	charmap "ü", CHARVAL("u")
	charmap "ÿ", CHARVAL("y")
	charmap "œ", CHARVAL("o")
	charmap "æ", CHARVAL("a")

	; uppercase
	charmap "À", CHARVAL("A")
	charmap "Â", CHARVAL("A")
	charmap "Ä", CHARVAL("A")
	charmap "È", CHARVAL("E")
	charmap "Ê", CHARVAL("E")
	charmap "Ë", CHARVAL("E")
	charmap "Î", CHARVAL("I")
	charmap "Ï", CHARVAL("I")
	charmap "Ô", CHARVAL("O")
	charmap "Ö", CHARVAL("O")
	charmap "Ù", CHARVAL("U")
	charmap "Û", CHARVAL("U")
	charmap "Ü", CHARVAL("U")
	charmap "Ÿ", CHARVAL("Y")
	charmap "Ç", CHARVAL("C")
	charmap "Œ", CHARVAL("O")
	charmap "Æ", CHARVAL("A")

	; apostrophes → backtick `, the only apostrophe glyph both the Pokedex
	; decoder (Func_2957c) and the bottom-banner font (PlaceText) recognize.
	; A straight ' (0x27) is otherwise unhandled: the dex decoder truncates
	; the text at it, and PlaceText silently drops it. Folding both the
	; straight and curly forms down to ` makes either one render correctly.
	charmap "'", CHARVAL("`")
	charmap "’", CHARVAL("`")

; "é"/"É" s'encodent en $40. Le Pokédex (police à largeur variable) a un glyph
; à cette tuile. Le bandeau bas (PlaceText) n'a pas de glyph $40, mais son
; moteur a été ajusté pour traiter $40 comme "e" → glyph é (voir PlaceText
; dans home/text.asm, .e_acute). Le jeu d'origine encodait "POKeMON" avec "e".

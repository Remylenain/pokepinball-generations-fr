	charmap "@", $00
	charmap "♂", $24
	charmap "é", $40
	charmap "♀", $5C

; French accents: fall back to the closest unaccented base letter.
; The Pokedex/scrolling-text font only ships a glyph for é among the
; accents, so anything else is encoded as if the user had typed the
; base letter. Source files can use proper accented French, and the
; assembler folds them down here.
;
; Uppercase É chains to lowercase é so we still get the accented glyph
; in caps-only contexts (the dex name area is uppercase-only and a
; lowercase é is the closest thing to a real É we have).

	; lowercase
	charmap "à", "a"
	charmap "â", "a"
	charmap "ä", "a"
	charmap "è", "e"
	charmap "ê", "e"
	charmap "ë", "e"
	charmap "î", "i"
	charmap "ï", "i"
	charmap "ô", "o"
	charmap "ö", "o"
	charmap "ù", "u"
	charmap "û", "u"
	charmap "ü", "u"
	charmap "ÿ", "y"
	charmap "ç", "c"
	charmap "œ", "o"
	charmap "æ", "a"

	; uppercase
	charmap "À", "A"
	charmap "Â", "A"
	charmap "Ä", "A"
	charmap "É", "é"
	charmap "È", "E"
	charmap "Ê", "E"
	charmap "Ë", "E"
	charmap "Î", "I"
	charmap "Ï", "I"
	charmap "Ô", "O"
	charmap "Ö", "O"
	charmap "Ù", "U"
	charmap "Û", "U"
	charmap "Ü", "U"
	charmap "Ÿ", "Y"
	charmap "Ç", "C"
	charmap "Œ", "O"
	charmap "Æ", "A"

	; curly apostrophe → straight apostrophe (renders as ` in the dex font)
	charmap "’", "`"

; "é"/"É" s'encodent en $40. Le Pokédex (police à largeur variable) a un glyph
; à cette tuile. Le bandeau bas (PlaceText) n'a pas de glyph $40, mais son
; moteur a été ajusté pour traiter $40 comme "e" → glyph é (voir PlaceText
; dans home/text.asm, .e_acute). Le jeu d'origine encodait "POKeMON" avec "e".

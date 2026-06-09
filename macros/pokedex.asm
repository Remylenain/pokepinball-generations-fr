MACRO dex_number
	db (((\1) / 100) % 10) + '0'
	db (((\1) / 10) % 10) + '0'
	db ((\1) % 10) + '0'
	db "@"
ENDM

; \1 = height in decimeters (e.g. 7 = 0.7m, 145 = 14.5m)
; The comma is baked into the background between the 2nd and 3rd digit slots,
; so we emit meters_tens, meters_ones, decimeter -> "XX,Y" (no macro point;
; the decimal sits where the old "." tile used to be). 5-byte field kept via
; a trailing terminator pad.
MACRO dex_height
	DEF meters_tens = (\1 / 100) % 10
	IF meters_tens == 0
		db " "
	ELSE
		db meters_tens + '0'
	ENDC
	db ((\1 / 10) % 10) + '0'
	db (\1 % 10) + '0'
	db "@"
	db "@"
ENDM

; \1 = weight in hectograms (e.g. 18 = 1.8 kg). One decimal place; the comma
; is baked into the background between the 3rd and 4th digit slots, so we emit
; 3 integer digits (space-padded) + 1 decimal digit -> "XXX,Y". Round weights
; show as "X,0". Layout: 4 digit tiles + "kg" tile (gfx tile $83).
MACRO dex_weight
	DEF whole = \1 / 10
	DEF deci = \1 % 10
	IF whole >= 100
		db ((whole / 100) % 10) + '0'
	ELSE
		db " "
	ENDC

	IF whole >= 10
		db ((whole / 10) % 10) + '0'
	ELSE
		db " "
	ENDC

	db (whole % 10) + '0'
	db deci + '0'
	db $00, $83
ENDM

MACRO dex_weight_decimal
	DEF x = (\1) * 10
	IF x >= 100
		db ((x / 100) % 10) + '0'
	ELSE
		db " "
	ENDC

	IF x >= 10
		db ((x / 100) % 10) + '0'
	ELSE
		db " "
	ENDC

	db (x % 10) + '0'
	db ((\2) % 10) + '0'
	db $00, $FC
ENDM

; \1 = species string
MACRO dex_species
	FOR I, STRLEN(\1)
		dex_species_char CHARVAL(STRSLICE(\1, I, I + 1))
	ENDR
	db "@"
ENDM

MACRO dex_species_char
	IF (\1) == ' '
		db $81, $40
	ELSE
		db $82, (\1) + $1F
	ENDC
ENDM

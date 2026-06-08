MACRO dex_number
	db (((\1) / 100) % 10) + '0'
	db (((\1) / 10) % 10) + '0'
	db ((\1) % 10) + '0'
	db "@"
ENDM

; \1 = height in decimeters (e.g. 7 = 0.7m, 145 = 14.5m)
; Display: 4 chars "XX.Y" with leading space if tens digit is 0
MACRO dex_height
	DEF meters_tens = (\1 / 100) % 10
	IF meters_tens == 0
		db " "
	ELSE
		db meters_tens + '0'
	ENDC
	db ((\1 / 10) % 10) + '0'
	db $72 ; "." (decimal point — gfx tile to update)
	db (\1 % 10) + '0'
	db "@"
ENDM

; \1 = weight in hectograms (e.g. 69 = 6.9 kg). Rounded to nearest integer kg.
; Display: 4 digits "XXXX" + "kg" tile (gfx tile $83 to update)
MACRO dex_weight
	DEF kg = (\1 + 5) / 10
	IF kg >= 1000
		db ((kg / 1000) % 10) + '0'
	ELSE
		db " "
	ENDC

	IF kg >= 100
		db ((kg / 100) % 10) + '0'
	ELSE
		db " "
	ENDC

	IF kg >= 10
		db ((kg / 10) % 10) + '0'
	ELSE
		db " "
	ENDC

	db (kg % 10) + '0'
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

DEF REGION_KANTO  EQU $0
DEF REGION_JOHTO  EQU $1
DEF REGION_HOENN  EQU $2

; Derniere region atteignable dans l'ecran de selection des tables.
; Mettre REGION_HOENN pour rouvrir les tables Rubis et Saphir : tout leur code
; et leurs donnees sont intacts, ils sont juste inaccessibles.
DEF LAST_SELECTABLE_REGION EQU REGION_JOHTO

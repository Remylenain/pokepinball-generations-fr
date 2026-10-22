BallSavedText:
	scrolling_text_normal 4, 20, 0, 16
	db "BILLE SAUVEE @"

ShootAgainText:
	scrolling_text_normal 4, 20, 0, 16
	db "SHOOT AGAIN @"

EndOfBallBonusText:
	; Offset 0 (FR "BILLE BONUS TERMINEE" = 20 cases, doit tenir tuiles 0-19).
	; L'offset 1 d'origine poussait le "E" final hors ecran. Conforme a la version EU.
	scrolling_text_normal 0, 20, 0, 21
	db "BILLE BONUS TERMINEE @"

FieldMultiplierText:
	scrolling_text_normal 1, 20, 0, 20
	db "MULTIPLICATEUR x0 @"

FieldMultiplierSpecialBonusText:
	scrolling_text_nopause 7, 51
	db "MULTIPLICATEUR BONUS SPECIAL @"

DigitsText1to8:
	scrolling_text 7, 51, 6, 20, 2, 15
	db "12345678 @"

BonusMultiplierText:
	scrolling_text_normal 0, 20, 0, 21
	db "MULTIPLIC. BONUS x0  @"

ExtraBallText:
	scrolling_text_normal 5, 20, 0, 16
	db "EXTRA BALL @"

ExtraBallSpecialBonusText:
	scrolling_text_nopause 7, 45
	db "EXTRA BALL BONUS SPECIAL @"

DigitsText1to9:
	scrolling_text 7, 45, 5, 20, 2, 15
	db "123456789 @"

LetsGetPokemonText:
	scrolling_text_normal 0, 20, 0, 21
	db "ATTRAPEZ LES POKEMON @"

PokemonRanAwayText:
	scrolling_text_normal 0, 20, 0, 21
	db "LE POKEMON S'ENFUIT @"

PokemonCaughtSpecialBonusText:
	scrolling_text_nopause 7, 49
	db "POKEMON ATTRAPE - BONUS SPECIAL @"

OneBillionText:
	scrolling_text 7, 46, 5, 20, 2, 19
	db "1.000.000.000 @"

HitText:
	; Offset 1 (FR "TOUCHE" = 6 lettres). A l'offset 4 d'origine ("HIT" = 3 lettres),
	; le mot debordait sur le score affiche a l'offset 8 (Data_2a2a) -> tronque.
	stationary_text 1, 0, 64
	db "TOUCHE @"

Data_2a2a:
	stationary_text 8, 1, 64

	db $00, $00 ; unused

FlippedText:
	stationary_text 2, 0, 64
	db "FLIP @"

CatchModeTileFlippedScoreStationaryTextHeader:
	stationary_text 10, 1, 64

	db $00, $00 ; unused

JackpotText:
	stationary_text 2, 0, 180
	db "JACKPOT @"

CatchModeJackpotScoreStationaryTextHeader:
	stationary_text 10, 1, 180

	db $00, $00 ; unused

YouGotAText:
	; Offset suffixe poussE A 35 (= durEe prEfixe) pour laisser 15 cases au
	; prEfixe "VOUS GAGNEZ UN " (FR plus long que "YOU GOT A "). Voir Data_2a79.
	scrolling_text_nopause 5, 35
	db "VOUS GAGNEZ UN @"

YouGotAnText:
	; Idem, voir Data_2a91 ("VOUS GAGNEZ UN " = 15 cases).
	scrolling_text_nopause 5, 35
	db "VOUS GAGNEZ UN @"

Data_2a79:
	; Offset de dEpart 35 (au lieu de 30) pour le prEfixe "VOUS GAGNEZ UN " (15 cases).
	scrolling_text 5, 35, 0, 20, 2, 17
	db "                 @"

Data_2a91:
	; Offset de dEpart 35 (au lieu de 31) pour le prEfixe "VOUS GAGNEZ UN " (15 cases).
	scrolling_text 5, 35, 0, 20, 2, 17
	db "                 @"

StartTrainingText:
	scrolling_text_normal 1, 20, 0, 19
	db "DEBUT ENTRAINEMENT @"

FindItemsText:
	scrolling_text_normal 3, 20, 0, 18
	db "TROUVER OBJETS @"

StartBreedingText:
	db $05, $54, $43, $14, $00, $37
	db "DEBUT ELEVAGE @"

EvolutionFailedText:
	scrolling_text_normal 0, 20, 0, 21
	db "ECHEC DE L'EVOLUTION @"

BreedingFailedText:
	db $05, $54, $42, $14, $00, $39
	db "ECHEC DE L'ELEVAGE @"

ItEvolvedIntoAText:
	scrolling_text_nopause 5, 38
	db "IL EVOLUE EN @"

EggHatchedIntoAText:
	db $05, $54, $00, $00, $00, $26
	db "IL ECLOT EN @"

ItEvolvedIntoAnText:
	scrolling_text_nopause 5, 39
	db "IL EVOLUE EN @"

EggHatchedIntoAnText:
	db $05, $54, $00, $00, $00, $27
	db "IL ECLOT EN @"

Data_2b1c:
	scrolling_text 5, 38, 0, 20, 2, 17
	db "                 @"

Data_2b34:
	scrolling_text 5, 39, 0, 20, 2, 17
	db "                 @"

EvolutionSpecialBonusText:
	scrolling_text_nopause 7, 44
	db "BONUS SPECIAL EVOLUTION @"

Data_2b6b:
	scrolling_text 7, 44, 6, 20, 2, 15
	db "12345678 @"

PokemonIsTiredText:
	scrolling_text_normal 2, 20, 0, 19
	db "POKEMON FATIGUE @"

ItemNotFoundText:
	scrolling_text_normal 2, 20, 0, 20
	db "OBJET NON TROUVE @"

KeepWalkingText:
	db $05, $54, $43, $14, $00, $35
	db "MARCHEZ @"

PokemonRecoveredText:
	scrolling_text_normal 3, 20, 0, 19
	db "POKEMON REPOSE @"

TryNextPlaceText:
	scrolling_text_normal 0, 20, 0, 21
	db "VOIR ENDROIT SUIVANT @"

YeahYouGotItText:
	scrolling_text_normal 6, 20, 0, 16
	db "SUPER ! @"

EvolutionTypeGetTextPointers:
	dw GetThunderStoneText
	dw GetMoonStoneText
	dw GetFireStoneText
	dw GetLeafStoneText
	dw GetWaterStoneText
	dw GetLinkCableText
	dw GetExperienceText
	dw GetSunStoneText
	dw TakeStepsText

GetExperienceText:
	scrolling_text_normal 1, 20, 0, 20
	db "GAGNER EXPERIENCE @"

GetFireStoneText:
	scrolling_text_normal 1, 20, 0, 20
	db "GAGNER PIERRE FEU @"

GetWaterStoneText:
	scrolling_text_normal 1, 20, 0, 20
	db "GAGNER PIERRE EAU @"

GetThunderStoneText:
	scrolling_text_normal 0, 20, 0, 21
	db "GAGNER PIERRE FOUDRE @"

GetLeafStoneText:
	scrolling_text_normal 0, 20, 0, 21
	db "GAGNER PIERRE PLANTE @"

GetMoonStoneText:
	scrolling_text_normal 1, 20, 0, 20
	db "GAGNER PIERRE LUNE @"

GetLinkCableText:
	scrolling_text_normal 2, 20, 0, 19
	db "AVOIR CABLE LINK @"

TakeStepsText:
	db $05, $54, $42, $14, $00, $38
	db "MARCHEZ BCP @"

GetSunStoneText:
	db $05, $54, $42, $14, $00, $38
	db "GAGNER P. SOLEIL @"

MapMoveFailedText:
	scrolling_text_normal 0, 20, 0, 20
	db "ECHEC DU DEPLACEMENT @"

ArrivedAtMapText:
	scrolling_text_nopause 5, 31
	db "ARRIVE A @"

StartFromMapText:
	; Comme scrolling_text_nopause 5, 31 mais offset de dEpart 19 (au lieu de 20)
	; pour laisser 12 cases au prEfixe "COMMENCER A " (FR plus long que "START FROM ").
	db 5, 19 + $40, 0, 0, 0, 31
	db "COMMENCER A @"

GoToDiglettStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIVEAU TAUPIQUEUR @"

GoToGengarStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIVEAU ECTOPLASMA @"

GoToMewtwoStageText:
	scrolling_text_normal 3, 20, 0, 18
	db "NIVEAU MEWTWO @"

GoToMeowthStageText:
	scrolling_text_normal 3, 20, 0, 18
	db "NIVEAU MIAOUSS @"

GoToSeelStageText:
	scrolling_text_normal 3, 20, 0, 17
	db "NIVEAU OTARIA @"

EndGengarStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIV ECTOPLASMA @"

EndMewtwoStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIVEAU MEWTWO @"

EndDiglettStageText:
	scrolling_text_normal 1, 20, 0, 21
	db "FIN NIV TAUPIQUEUR @"

EndMeowthStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIVEAU MIAOUSS @"

EndSeelStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIVEAU OTARIA @"

GengarStageClearedText:
	scrolling_text_normal 0, 20, 0, 21
	db "NIV ECTOPLASM REUSSI @"

MewtwoStageClearedText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIV MEWTWO REUSSI @"

DiglettStageClearedText:
	scrolling_text_normal 0, 20, 0, 21
	db "NIV TAUPIQU. REUSSI @"

MeowthStageClearedText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIV MIAOUSS REUSSI @"

SeelStageClearedText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIV OTARIA REUSSI @"

NumPokemonCaughtText:
	db "  0 POKEMON ATTRAPE@"

NumPokemonEvolvedText:
	db "  0 POKEMON EVOLUE@"

BellsproutCounterText:
	db "  0 CHETIFLOR@"

DugtrioCounterText:
	db "  0 TRIOPIKEUR@"

CaveShotCounterText:
	db "  0 TROUS@"

SpinnerTurnsCounterText:
	db "  0 TOURS ROULETTE@"

BonusPointsText:
	db " BONUS@"

SubtotalPointsText:
	db "SOUS-TOTAL@"

MultiplierPointsText:
	db " MULTIPLICATEUR@"

TotalPointsText:
	db " TOTAL@"

ScoreText:
	db " SCORE@"

GameOverText:
	db "     GAME OVER     @"

PsyduckCounterText:
	db "  0 PSYKOKWAK@"

PoliwagCounterText:
	db "  0 PTITARD@"

CloysterCounterText:
	db "  0 CRUSTABRI@"

SlowpokeCounterText:
	db "  0 RAMOLOSS@"

ReleasedBeastsText:
	db $05, $54, $42, $14, $00, $38
	db "BETES LIBEREES @"

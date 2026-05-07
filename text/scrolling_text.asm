BallSavedText:
	scrolling_text_normal 5, 20, 0, 16
	db "BALL GARDEE @"

ShootAgainText:
	scrolling_text_normal 4, 20, 0, 16
	db "RELANCEZ @"

EndOfBallBonusText:
	scrolling_text_normal 1, 20, 0, 19
	db "BONUS FIN DE BALLE @"

FieldMultiplierText:
	scrolling_text_normal 0, 20, 0, 20
	db "MULT. TERRAIN x0 @"

FieldMultiplierSpecialBonusText:
	scrolling_text_nopause 7, 51
	db "BONUS SPECIAL MULT. TERRAIN @"

DigitsText1to8:
	scrolling_text 7, 51, 6, 20, 2, 15
	db "12345678 @"

BonusMultiplierText:
	scrolling_text_normal 0, 20, 0, 21
	db "MULT. BONUS x0 @"

ExtraBallText:
	scrolling_text_normal 5, 20, 0, 16
	db "BALL BONUS @"

ExtraBallSpecialBonusText:
	scrolling_text_nopause 7, 45
	db "BONUS SPECIAL BALL @"

DigitsText1to9:
	scrolling_text 7, 45, 5, 20, 2, 15
	db "123456789 @"

LetsGetPokemonText:
	scrolling_text_normal 1, 20, 0, 19
	db "ATTRAPONS POKeMON @"

PokemonRanAwayText:
	scrolling_text_normal 2, 20, 0, 19
	db "POKeMON A FUI @"

PokemonCaughtSpecialBonusText:
	scrolling_text_nopause 7, 49
	db "BONUS SPECIAL CAPTURE @"

OneBillionText:
	scrolling_text 7, 46, 5, 20, 2, 19
	db "1.000.000.000 @"

HitText:
	stationary_text 4, 0, 64
	db "TOUCHE @"

Data_2a2a:
	stationary_text 8, 1, 64

	db $00, $00 ; unused

FlippedText:
	stationary_text 2, 0, 64
	db "FLIPPE @"

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
	scrolling_text_nopause 5, 30
	db "TU AS UN @"

YouGotAnText:
	scrolling_text_nopause 5, 31
	db "TU AS UN @"

Data_2a79:
	scrolling_text 5, 30, 0, 20, 2, 17
	db "                 @"

Data_2a91:
	scrolling_text 5, 31, 0, 20, 2, 17
	db "                 @"

StartTrainingText:
	scrolling_text_normal 3, 20, 0, 18
	db "DEBUT ENTRAIN. @"

FindItemsText:
	scrolling_text_normal 5, 20, 0, 16
	db "TROUVE OBJET @"

StartBreedingText:
	db $05, $54, $43, $14, $00, $37
	db "DEBUT ELEVAGE @"

EvolutionFailedText:
	scrolling_text_normal 2, 20, 0, 19
	db "EVOLUTION RATEE @"

BreedingFailedText:
	db $05, $54, $42, $14, $00, $39
	db "ELEVAGE RATE @"

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
	db "POKeMON FATIGUE @"

ItemNotFoundText:
	scrolling_text_normal 3, 20, 0, 18
	db "AUCUN OBJET @"

KeepWalkingText:
	db $05, $54, $43, $14, $00, $35
	db "MARCHEZ @"

PokemonRecoveredText:
	scrolling_text_normal 1, 20, 0, 19
	db "POKeMON SOIGNE @"

TryNextPlaceText:
	scrolling_text_normal 3, 20, 0, 18
	db "ALLEZ AILLEURS @"

YeahYouGotItText:
	scrolling_text_normal 2, 20, 0, 19
	db "OUI ! ATTRAPE @"

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
	scrolling_text_normal 3, 20, 0, 18
	db "GAGNE DE L'XP @"

GetFireStoneText:
	scrolling_text_normal 2, 20, 0, 19
	db "TROUVE P. FEU @"

GetWaterStoneText:
	scrolling_text_normal 1, 20, 0, 19
	db "TROUVE P. EAU @"

GetThunderStoneText:
	scrolling_text_normal 0, 20, 0, 20
	db "TROUVE P. FOUDRE @"

GetLeafStoneText:
	scrolling_text_normal 2, 20, 0, 19
	db "TROUVE P. PLANTE @"

GetMoonStoneText:
	scrolling_text_normal 2, 20, 0, 19
	db "TROUVE P. LUNE @"

GetLinkCableText:
	scrolling_text_normal 2, 20, 0, 19
	db "TROUVE C. LINK @"

TakeStepsText:
	db $05, $54, $42, $14, $00, $38
	db "MARCHEZ BCP @"

GetSunStoneText:
	db $05, $54, $42, $14, $00, $38
	db "TROUVE P. SOLEIL @"

MapMoveFailedText:
	scrolling_text_normal 2, 20, 0, 18
	db "VOYAGE RATE @"

ArrivedAtMapText:
	scrolling_text_nopause 5, 31
	db "ARRIVE A @"

StartFromMapText:
	scrolling_text_nopause 5, 31
	db "DEPART DE @"

GoToDiglettStageText:
	scrolling_text_normal 0, 20, 0, 20
	db "VERS STADE TAUPIQUEUR @"

GoToGengarStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "VERS STADE ECTOPLASMA @"

GoToMewtwoStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "VERS STADE MEWTWO @"

GoToMeowthStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "VERS STADE MIAOUSS @"

GoToSeelStageText:
	scrolling_text_normal 2, 20, 0, 19
	db "VERS STADE OTARIA @"

EndGengarStageText:
	scrolling_text_normal 2, 20, 0, 19
	db "FIN STADE ECTOPLASMA @"

EndMewtwoStageText:
	scrolling_text_normal 2, 20, 0, 19
	db "FIN STADE MEWTWO @"

EndDiglettStageText:
	scrolling_text_normal 1, 20, 0, 19
	db "FIN STADE TAUPIQUEUR @"

EndMeowthStageText:
	scrolling_text_normal 2, 20, 0, 19
	db "FIN STADE MIAOUSS @"

EndSeelStageText:
	scrolling_text_normal 3, 20, 0, 18
	db "FIN STADE OTARIA @"

GengarStageClearedText:
	scrolling_text_normal 0, 20, 0, 21
	db "STADE ECTOPLASMA REUSSI @"

MewtwoStageClearedText:
	scrolling_text_normal 0, 20, 0, 21
	db "STADE MEWTWO REUSSI @"

DiglettStageClearedText:
	scrolling_text_normal -1, 20, 0, 21
	db "STADE TAUPIQUEUR REUSSI @"

MeowthStageClearedText:
	scrolling_text_normal 0, 20, 0, 21
	db "STADE MIAOUSS REUSSI @"

SeelStageClearedText:
	scrolling_text_normal 1, 20, 0, 20
	db "STADE OTARIA REUSSI @"

NumPokemonCaughtText:
	db "  0 POKeMON CAPTURES@"

NumPokemonEvolvedText:
	db "  0 POKeMON EVOLUES@"

BellsproutCounterText:
	db "  0 CHETIFLOR@"

DugtrioCounterText:
	db "  0 TRIOPIKEUR@"

CaveShotCounterText:
	db "  0 TIRS GROTTE@"

SpinnerTurnsCounterText:
	db "  0 TOURS SPINNER@"

BonusPointsText:
	db " BONUS@"

SubtotalPointsText:
	db " SOUS-TOTAL@"

MultiplierPointsText:
	db " MULTIPLI.@"

TotalPointsText:
	db " TOTAL@"

ScoreText:
	db " SCORE@"

GameOverText:
	db "    PARTIE FINIE    @"

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

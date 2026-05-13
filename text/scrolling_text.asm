BallSavedText:
	scrolling_text_normal 5, 20, 0, 16
	db "BILLE SAUVÉE @"

ShootAgainText:
	scrolling_text_normal 4, 20, 0, 16
	db "SHOOT AGAIN @"

EndOfBallBonusText:
	scrolling_text_normal 1, 20, 0, 21
	db "BILLE BONUS TERMINÉE @"

FieldMultiplierText:
	scrolling_text_normal 0, 20, 0, 20
	db "MULTIPLICATEUR x0 @"

FieldMultiplierSpecialBonusText:
	scrolling_text_nopause 7, 51
	db "MULTIPLICATEUR BONUS SPÉCIAL @"

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
	db "EXTRA BALL BONUS SPÉCIAL @"

DigitsText1to9:
	scrolling_text 7, 45, 5, 20, 2, 15
	db "123456789 @"

LetsGetPokemonText:
	scrolling_text_normal 0, 20, 0, 21
	db "ATTRAPEZ LES POKÉMON @"

PokemonRanAwayText:
	scrolling_text_normal 1, 20, 0, 21
	db "LE POKÉMON S'ENFUIT @"

PokemonCaughtSpecialBonusText:
	scrolling_text_nopause 7, 49
	db "POKÉMON ATTRAPÉ - BONUS SPÉCIAL @"

OneBillionText:
	scrolling_text 7, 46, 5, 20, 2, 19
	db "1.000.000.000 @"

HitText:
	stationary_text 4, 0, 64
	db "TOUCHÉ @"

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
	scrolling_text_nopause 5, 30
	db "VOUS GAGNEZ UN @"

YouGotAnText:
	scrolling_text_nopause 5, 31
	db "VOUS GAGNEZ UN @"

Data_2a79:
	scrolling_text 5, 30, 0, 20, 2, 17
	db "                 @"

Data_2a91:
	scrolling_text 5, 31, 0, 20, 2, 17
	db "                 @"

StartTrainingText:
	scrolling_text_normal 2, 20, 0, 19
	db "DÉBUT ENTRAÎNEMENT @"

FindItemsText:
	scrolling_text_normal 3, 20, 0, 18
	db "TROUVER OBJETS @"

StartBreedingText:
	db $05, $54, $43, $14, $00, $37
	db "DÉBUT ÉLEVAGE @"

EvolutionFailedText:
	scrolling_text_normal 0, 20, 0, 21
	db "ÉCHEC DE L'ÉVOLUTION @"

BreedingFailedText:
	db $05, $54, $42, $14, $00, $39
	db "ÉCHEC DE L'ÉLEVAGE @"

ItEvolvedIntoAText:
	scrolling_text_nopause 5, 38
	db "IL ÉVOLUE EN @"

EggHatchedIntoAText:
	db $05, $54, $00, $00, $00, $26
	db "IL ÉCLOT EN @"

ItEvolvedIntoAnText:
	scrolling_text_nopause 5, 39
	db "IL ÉVOLUE EN @"

EggHatchedIntoAnText:
	db $05, $54, $00, $00, $00, $27
	db "IL ÉCLOT EN @"

Data_2b1c:
	scrolling_text 5, 38, 0, 20, 2, 17
	db "                 @"

Data_2b34:
	scrolling_text 5, 39, 0, 20, 2, 17
	db "                 @"

EvolutionSpecialBonusText:
	scrolling_text_nopause 7, 44
	db "BONUS SPÉCIAL ÉVOLUTION @"

Data_2b6b:
	scrolling_text 7, 44, 6, 20, 2, 15
	db "12345678 @"

PokemonIsTiredText:
	scrolling_text_normal 2, 20, 0, 19
	db "POKÉMON FATIGUÉ @"

ItemNotFoundText:
	scrolling_text_normal 1, 20, 0, 20
	db "OBJET NON TROUVÉ @"

KeepWalkingText:
	db $05, $54, $43, $14, $00, $35
	db "MARCHEZ @"

PokemonRecoveredText:
	scrolling_text_normal 2, 20, 0, 19
	db "POKÉMON REPOSÉ @"

TryNextPlaceText:
	scrolling_text_normal 0, 20, 0, 21
	db "VOIR ENDROIT SUIVANT @"

YeahYouGotItText:
	scrolling_text_normal 5, 20, 0, 16
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
	db "GAGNER EXPÉRIENCE @"

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
	db "AVOIR CÂBLE LINK @"

TakeStepsText:
	db $05, $54, $42, $14, $00, $38
	db "MARCHEZ BCP @"

GetSunStoneText:
	db $05, $54, $42, $14, $00, $38
	db "GAGNER P. SOLEIL @"

MapMoveFailedText:
	scrolling_text_normal 0, 20, 0, 20
	db "ÉCHEC DU DÉPLACEMENT @"

ArrivedAtMapText:
	scrolling_text_nopause 5, 31
	db "ARRIVÉ À @"

StartFromMapText:
	scrolling_text_nopause 5, 31
	db "COMMENCER À @"

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
	scrolling_text_normal 4, 20, 0, 17
	db "NIVEAU OTARIA @"

EndGengarStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIV ECTOPLASMA @"

EndMewtwoStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIVEAU MEWTWO @"

EndDiglettStageText:
	scrolling_text_normal 0, 20, 0, 21
	db "FIN NIV TAUPIQUEUR @"

EndMeowthStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIVEAU MIAOUSS @"

EndSeelStageText:
	scrolling_text_normal 1, 20, 0, 20
	db "FIN NIVEAU OTARIA @"

GengarStageClearedText:
	scrolling_text_normal 0, 20, 0, 21
	db "NIV ECTOPLASM RÉUSSI @"

MewtwoStageClearedText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIV MEWTWO RÉUSSI @"

DiglettStageClearedText:
	scrolling_text_normal 0, 20, 0, 21
	db "NIV TAUPIQU. RÉUSSI @"

MeowthStageClearedText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIV MIAOUSS RÉUSSI @"

SeelStageClearedText:
	scrolling_text_normal 1, 20, 0, 20
	db "NIV OTARIA RÉUSSI @"

NumPokemonCaughtText:
	db "  0 POKÉMON ATTRAPÉ@"

NumPokemonEvolvedText:
	db "  0 POKÉMON ÉVOLUÉ@"

BellsproutCounterText:
	db "  0 CHÉTIFLOR@"

DugtrioCounterText:
	db "  0 TRIOPIKEUR@"

CaveShotCounterText:
	db "  0 TROUS@"

SpinnerTurnsCounterText:
	db "  0 TOURS ROULETTE@"

BonusPointsText:
	db " BONUS@"

SubtotalPointsText:
	db " SOUS-TOTAL@"

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
	db "BÊTES LIBÉRÉES @"

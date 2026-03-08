// Copyright NeoNexusOne. All Rights Reserved.

#include "Core/EchoGameMode.h"
#include "Sound/EchoRippleManager.h"
#include "Player/EchoPawn.h"
#include "Core/EchoPlayerController.h"

AEchoGameMode::AEchoGameMode()
{
	RippleManager = CreateDefaultSubobject<UEchoRippleManager>(TEXT("RippleManager"));

	DefaultPawnClass = AEchoPawn::StaticClass();
	PlayerControllerClass = AEchoPlayerController::StaticClass();
}

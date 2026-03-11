// Copyright NeoNexusOne. All Rights Reserved.

#include "Core/EchoPlayerController.h"
#include "Core/EchoTypes.h"
#include "EnhancedInputSubsystems.h"

void AEchoPlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
		ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
	{
		if (DefaultMappingContext)
		{
			Subsystem->AddMappingContext(DefaultMappingContext, 0);
		}
	}

	// Lock cursor for free mouse look
	FInputModeGameOnly InputMode;
	SetInputMode(InputMode);
	bShowMouseCursor = false;

	// Clamp pitch to prevent camera flipping
	if (PlayerCameraManager)
	{
		PlayerCameraManager->ViewPitchMin = EchoDefaults::CameraPitchMin;
		PlayerCameraManager->ViewPitchMax = EchoDefaults::CameraPitchMax;
	}
}

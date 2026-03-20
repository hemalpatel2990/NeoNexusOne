// Copyright NeoNexusOne. All Rights Reserved.

#include "Core/EchoPlayerController.h"
#include "Core/EchoTypes.h"
#include "UI/EchoHUDWidget.h"
#include "Materials/MaterialParameterCollection.h"
#include "EnhancedInputSubsystems.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "AI/EchoEnemyPawn.h"
#include "EngineUtils.h"

DEFINE_LOG_CATEGORY_STATIC(LogEchoPC, Log, All);

void AEchoPlayerController::BeginPlay()
{
	Super::BeginPlay();

	// Enhanced Input setup
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

	// Load MPC reference
	GlobalSoundMPC = LoadObject<UMaterialParameterCollection>(nullptr,
		TEXT("/Game/EchoLocation/Materials/MPC_GlobalSound.MPC_GlobalSound"));

	// Create and display HUD widget
	if (HUDWidgetClass && IsLocalController())
	{
		HUDWidget = CreateWidget<UEchoHUDWidget>(this, HUDWidgetClass);
		if (HUDWidget)
		{
			HUDWidget->AddToViewport();
			HUDWidget->UpdateMapping(MappingProgress);
		}
	}
}

void AEchoPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);

	// --- Signal Decay ---
	if (CurrentSignal > 0.0f)
	{
		CurrentSignal = FMath::Max(0.0f,
			CurrentSignal - (DeltaTime / EchoDefaults::SignalDecayDuration));
	}

	// --- Enemy Proximity ---
	float ClosestDistSq = FMath::Square(EchoDefaults::MaxProximityRange + 1.0f);
	if (APawn* MyPawn = GetPawn())
	{
		const FVector MyLoc = MyPawn->GetActorLocation();
		for (TActorIterator<AEchoEnemyPawn> It(GetWorld()); It; ++It)
		{
			const float DistSq = FVector::DistSquared(MyLoc, It->GetActorLocation());
			if (DistSq < ClosestDistSq)
			{
				ClosestDistSq = DistSq;
			}
		}
	}
	const float ActualDist = FMath::Sqrt(ClosestDistSq);
	ProximityIntensity = FMath::Clamp(
		1.0f - (ActualDist / EchoDefaults::MaxProximityRange), 0.0f, 1.0f);

	// --- Update MPC for post-process interference material ---
	if (GlobalSoundMPC)
	{
		UKismetMaterialLibrary::SetScalarParameterValue(
			GetWorld(), GlobalSoundMPC,
			EchoMPCParams::SignalIntensity, CurrentSignal);
		UKismetMaterialLibrary::SetScalarParameterValue(
			GetWorld(), GlobalSoundMPC,
			EchoMPCParams::ProximityInterference, ProximityIntensity);
	}

	// --- Update HUD Widget ---
	if (HUDWidget)
	{
		HUDWidget->UpdateSignal(CurrentSignal);
	}
}

void AEchoPlayerController::ResetSignal()
{
	CurrentSignal = 1.0f;
	if (HUDWidget)
	{
		HUDWidget->TriggerPulse();
	}
}

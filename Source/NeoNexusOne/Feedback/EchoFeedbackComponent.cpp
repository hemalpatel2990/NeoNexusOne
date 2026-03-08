// Copyright NeoNexusOne. All Rights Reserved.

#include "Feedback/EchoFeedbackComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/ForceFeedbackEffect.h"

UEchoFeedbackComponent::UEchoFeedbackComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UEchoFeedbackComponent::PlayFeedback(EEchoMovementState State)
{
	APawn* OwnerPawn = Cast<APawn>(GetOwner());
	if (!OwnerPawn)
	{
		return;
	}

	APlayerController* PC = Cast<APlayerController>(OwnerPawn->GetController());
	if (!PC)
	{
		return;
	}

	TSubclassOf<UCameraShakeBase> ShakeClass = nullptr;
	UForceFeedbackEffect* ForceFeedback = nullptr;

	switch (State)
	{
	case EEchoMovementState::Drop:
		ShakeClass = DropShake;
		ForceFeedback = DropForceFeedback;
		break;

	case EEchoMovementState::SlamJump:
		ShakeClass = SlamShake;
		ForceFeedback = SlamForceFeedback;
		break;

	default:
		return;
	}

	if (ShakeClass)
	{
		PC->ClientStartCameraShake(ShakeClass);
	}

	if (ForceFeedback)
	{
		PC->ClientPlayForceFeedback(ForceFeedback);
	}
}

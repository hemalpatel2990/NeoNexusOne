// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Core/EchoTypes.h"
#include "EchoFeedbackComponent.generated.h"

class UCameraShakeBase;
class UForceFeedbackEffect;

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class ECHOLOCATION_API UEchoFeedbackComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UEchoFeedbackComponent();

	// --- Camera Shakes (set in Blueprint) ---

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Feedback")
	TSubclassOf<UCameraShakeBase> DropShake;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Feedback")
	TSubclassOf<UCameraShakeBase> SlamShake;

	// --- Force Feedback Effects (set in Blueprint) ---

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Feedback")
	TObjectPtr<UForceFeedbackEffect> DropForceFeedback;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Feedback")
	TObjectPtr<UForceFeedbackEffect> SlamForceFeedback;

	// --- API ---

	UFUNCTION(BlueprintCallable, Category = "Echo|Feedback")
	void PlayFeedback(EEchoMovementState State);
};

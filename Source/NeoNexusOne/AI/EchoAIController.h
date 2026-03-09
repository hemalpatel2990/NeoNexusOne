// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "Core/EchoTypes.h"
#include "EchoAIController.generated.h"

class UAIPerceptionComponent;
class UAISenseConfig_Hearing;

UCLASS()
class NEONEXUSONE_API AEchoAIController : public AAIController
{
	GENERATED_BODY()

public:
	AEchoAIController();

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;
	virtual void OnMoveCompleted(FAIRequestID RequestID, const FPathFollowingResult& Result) override;

private:
	UFUNCTION()
	void OnPerceptionUpdated(AActor* Actor, FAIStimulus Stimulus);

	void InvestigateLocation(const FVector& Location);
	void ReturnToSpawn();

	UPROPERTY(VisibleAnywhere, Category = "Echo|AI")
	TObjectPtr<UAIPerceptionComponent> AIPerceptionComp;

	UPROPERTY()
	TObjectPtr<UAISenseConfig_Hearing> HearingConfig;

	EEchoAIState CurrentState = EEchoAIState::Idle;
	FVector SpawnLocation = FVector::ZeroVector;
	float LingerTimer = 0.0f;
};

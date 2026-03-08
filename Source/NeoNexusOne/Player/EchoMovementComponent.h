// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PawnMovementComponent.h"
#include "Core/EchoTypes.h"
#include "EchoMovementComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnEchoImpact, EEchoMovementState, State, FVector, Location);

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NEONEXUSONE_API UEchoMovementComponent : public UPawnMovementComponent
{
	GENERATED_BODY()

public:
	UEchoMovementComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType,
		FActorComponentTickFunction* ThisTickFunction) override;

	// --- Tunable Properties ---

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Movement")
	float GlideSpeed = 600.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Movement")
	float HoverHeight = EchoDefaults::GlideHoverHeight;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Movement")
	float HoverInterpSpeed = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Movement")
	FVector SlamJumpImpulse = FVector(0.0f, 0.0f, 1200.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Movement")
	float GravityScale = 2.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Movement")
	float GroundTraceThreshold = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Movement")
	float SlamVelocityThreshold = 400.0f;

	// --- Delegates ---

	UPROPERTY(BlueprintAssignable, Category = "Echo|Movement")
	FOnEchoImpact OnEchoImpact;

	// --- Public API ---

	UFUNCTION(BlueprintCallable, Category = "Echo|Movement")
	void AddGlideInput(FVector2D Input);

	UFUNCTION(BlueprintCallable, Category = "Echo|Movement")
	void RequestSlamJump();

	UFUNCTION(BlueprintPure, Category = "Echo|Movement")
	EEchoMovementState GetMovementState() const { return CurrentState; }

private:
	EEchoMovementState CurrentState = EEchoMovementState::Idle;
	FVector CurrentVelocity = FVector::ZeroVector;
	FVector2D PendingInput = FVector2D::ZeroVector;

	bool CheckGroundContact(float& OutFloorZ) const;
	void HandleLanding(const FVector& ImpactLocation);
};
